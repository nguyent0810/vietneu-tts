import { ZodError } from 'zod'

/**
 * Bảng phân loại lỗi API.
 *
 * Mã lỗi là hợp đồng ỔN ĐỊNH với client (CLI Python sinh từ OpenAPI): client
 * phân nhánh theo `code`, không theo `message`. Vì thế `message` được phép đổi
 * cách diễn đạt, còn `code` thì không — đổi `code` là breaking change.
 */
export const ErrorCode = {
  // 400
  VALIDATION_FAILED: 'VALIDATION_FAILED',
  MALFORMED_JSON: 'MALFORMED_JSON',
  UNSUPPORTED_SCHEMA_VERSION: 'UNSUPPORTED_SCHEMA_VERSION',
  // 401 / 403
  UNAUTHENTICATED: 'UNAUTHENTICATED',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_REVOKED: 'TOKEN_REVOKED',
  INSUFFICIENT_SCOPE: 'INSUFFICIENT_SCOPE',
  CAPABILITY_NOT_GRANTED: 'CAPABILITY_NOT_GRANTED',
  WORKER_CANNOT_APPROVE: 'WORKER_CANNOT_APPROVE',
  // 404 / 409
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  REVISION_FROZEN: 'REVISION_FROZEN',
  REVISION_NOT_FROZEN: 'REVISION_NOT_FROZEN',
  DUPLICATE_RUN_SEQUENCE: 'DUPLICATE_RUN_SEQUENCE',
  ITERATION_LIMIT_REACHED: 'ITERATION_LIMIT_REACHED',
  // 413 / 429
  PAYLOAD_TOO_LARGE: 'PAYLOAD_TOO_LARGE',
  RATE_LIMITED: 'RATE_LIMITED',
  // 5xx
  INTERNAL: 'INTERNAL',
  UPSTREAM_UNAVAILABLE: 'UPSTREAM_UNAVAILABLE',
} as const

export type ErrorCodeValue = (typeof ErrorCode)[keyof typeof ErrorCode]

const STATUS_BY_CODE: Record<ErrorCodeValue, number> = {
  VALIDATION_FAILED: 400,
  MALFORMED_JSON: 400,
  UNSUPPORTED_SCHEMA_VERSION: 400,
  UNAUTHENTICATED: 401,
  TOKEN_EXPIRED: 401,
  TOKEN_REVOKED: 401,
  INSUFFICIENT_SCOPE: 403,
  CAPABILITY_NOT_GRANTED: 403,
  WORKER_CANNOT_APPROVE: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  REVISION_FROZEN: 409,
  REVISION_NOT_FROZEN: 409,
  DUPLICATE_RUN_SEQUENCE: 409,
  ITERATION_LIMIT_REACHED: 409,
  PAYLOAD_TOO_LARGE: 413,
  RATE_LIMITED: 429,
  INTERNAL: 500,
  UPSTREAM_UNAVAILABLE: 503,
}

export interface ApiErrorBody {
  error: {
    code: ErrorCodeValue
    message: string
    details?: unknown
    requestId?: string
  }
}

export class ApiError extends Error {
  readonly code: ErrorCodeValue
  readonly status: number
  readonly details?: unknown
  /** Giây cho tới khi được thử lại — chỉ dùng với RATE_LIMITED. */
  readonly retryAfterSeconds?: number

  constructor(
    code: ErrorCodeValue,
    message: string,
    options: { details?: unknown; retryAfterSeconds?: number } = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = STATUS_BY_CODE[code]
    this.details = options.details
    this.retryAfterSeconds = options.retryAfterSeconds
  }

  toBody(requestId?: string): ApiErrorBody {
    return {
      error: {
        code: this.code,
        message: this.message,
        ...(this.details === undefined ? {} : { details: this.details }),
        ...(requestId ? { requestId } : {}),
      },
    }
  }
}

export function statusForCode(code: ErrorCodeValue): number {
  return STATUS_BY_CODE[code]
}

/**
 * Chuyển ZodError thành ApiError.
 *
 * Chỉ giữ `path` + `code` + `message` của Zod, KHÔNG giữ giá trị người dùng
 * gửi lên: nếu vọng lại giá trị thì một request chứa token/credential sẽ bị
 * ghi thẳng vào log lỗi.
 */
export function fromZodError(err: ZodError): ApiError {
  return new ApiError(ErrorCode.VALIDATION_FAILED, 'Payload không hợp lệ.', {
    details: err.issues.map((i) => ({
      path: i.path.join('.'),
      code: i.code,
      message: i.message,
    })),
  })
}

/**
 * Ánh xạ lỗi PostgreSQL sang mã API.
 *
 * Chỉ nhận diện các ràng buộc mà ta CỐ Ý dựa vào để bảo toàn dữ liệu; mọi thứ
 * khác trả về INTERNAL. Không đoán mò theo chuỗi message: message của Postgres
 * đổi giữa các phiên bản, còn `code`/`constraint` thì ổn định.
 */
export function fromDatabaseError(err: unknown): ApiError {
  const e = err as { code?: string; constraint?: string; message?: string }

  if (e?.code === '23505') {
    if (e.constraint === 'analysis_run_sequence_key') {
      return new ApiError(
        ErrorCode.DUPLICATE_RUN_SEQUENCE,
        'run_sequence đã tồn tại cho chủ thể và phiên bản thuật toán này.',
      )
    }
    return new ApiError(ErrorCode.CONFLICT, 'Bản ghi đã tồn tại.', {
      details: { constraint: e.constraint },
    })
  }

  if (e?.code === '23514') {
    if (e.constraint === 'llm_execution_iteration_bounds') {
      return new ApiError(
        ErrorCode.ITERATION_LIMIT_REACHED,
        'Đã đạt giới hạn 3 vòng tinh chỉnh cho gói phân tích này.',
      )
    }
    if (e.constraint === 'approval_decider_must_be_human') {
      return new ApiError(
        ErrorCode.WORKER_CANNOT_APPROVE,
        'Chỉ người dùng mới được phê duyệt; agent/worker không được phép.',
      )
    }
    return new ApiError(ErrorCode.VALIDATION_FAILED, 'Vi phạm ràng buộc dữ liệu.', {
      details: { constraint: e.constraint },
    })
  }

  // Trigger bất biến (revision/prompt đã FROZEN) dùng RAISE EXCEPTION mã P0001.
  if (e?.code === 'P0001' && e.message?.includes('IMMUTABLE_')) {
    return new ApiError(ErrorCode.REVISION_FROZEN, 'Bản ghi đã đóng băng, không thể sửa.')
  }

  if (e?.code === '23503') {
    return new ApiError(ErrorCode.NOT_FOUND, 'Bản ghi tham chiếu không tồn tại.', {
      details: { constraint: e.constraint },
    })
  }

  return new ApiError(ErrorCode.INTERNAL, 'Lỗi nội bộ.')
}

/** Chuẩn hoá mọi lỗi thành ApiError để route handler chỉ có một đường trả lỗi. */
export function toApiError(err: unknown): ApiError {
  if (err instanceof ApiError) return err
  if (err instanceof ZodError) return fromZodError(err)
  const e = err as { code?: string }
  if (typeof e?.code === 'string') return fromDatabaseError(err)
  return new ApiError(ErrorCode.INTERNAL, 'Lỗi nội bộ.')
}
