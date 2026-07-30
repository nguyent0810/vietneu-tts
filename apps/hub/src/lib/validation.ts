import { z } from 'zod'

import { ApiError, ErrorCode, toApiError } from './errors'

/**
 * Giới hạn body của Vercel là 4.5 MB — vượt sẽ bị chặn ở tầng hạ tầng với
 * `FUNCTION_PAYLOAD_TOO_LARGE` (413) TRƯỚC KHI code chạy, nên client sẽ nhận
 * một lỗi không theo bảng phân loại của ta.
 *
 * Vì thế đặt trần thấp hơn hẳn (1 MB) và tự trả 413 theo đúng hợp đồng lỗi.
 * Gói bằng chứng phân tích là JSON text nên 1 MB là rất rộng rãi; payload lớn
 * hơn thế gần như chắc chắn là lỗi phía gọi.
 */
export const MAX_BODY_BYTES = 1_000_000

/** Mọi schema request đều phải `.strict()` — xem `parseBody`. */
export type StrictSchema<T> = z.ZodType<T, z.ZodTypeDef, unknown>

/**
 * Đọc và validate body JSON.
 *
 * Ba tầng kiểm tra theo đúng thứ tự, cố ý:
 *  1. Kích thước — trước khi tốn công parse.
 *  2. JSON hợp lệ — lỗi cú pháp trả MALFORMED_JSON, khác hẳn lỗi sai schema.
 *  3. Schema — trả VALIDATION_FAILED kèm đường dẫn trường lỗi (không kèm giá trị).
 */
export async function parseBody<T>(request: Request, schema: StrictSchema<T>): Promise<T> {
  const declared = request.headers.get('content-length')
  if (declared && Number(declared) > MAX_BODY_BYTES) {
    throw new ApiError(
      ErrorCode.PAYLOAD_TOO_LARGE,
      `Body vượt quá ${MAX_BODY_BYTES} byte.`,
    )
  }

  const raw = await request.text()
  // Kiểm lại theo kích thước THẬT: content-length có thể thiếu hoặc nói dối.
  if (Buffer.byteLength(raw, 'utf8') > MAX_BODY_BYTES) {
    throw new ApiError(ErrorCode.PAYLOAD_TOO_LARGE, `Body vượt quá ${MAX_BODY_BYTES} byte.`)
  }

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    throw new ApiError(ErrorCode.MALFORMED_JSON, 'Body không phải JSON hợp lệ.')
  }

  const result = schema.safeParse(parsed)
  if (!result.success) {
    throw toApiError(result.error)
  }
  return result.data
}

/** Validate query string theo cùng một đường lỗi với body. */
export function parseQuery<T>(url: URL, schema: StrictSchema<T>): T {
  const raw: Record<string, string> = {}
  for (const [key, value] of url.searchParams) raw[key] = value
  const result = schema.safeParse(raw)
  if (!result.success) throw toApiError(result.error)
  return result.data
}

// --- Kiểu dùng lại ----------------------------------------------------------

export const uuidSchema = z.string().uuid()
export const sha256Schema = z.string().regex(/^[0-9a-f]{64}$/, 'Phải là sha256 hex (64 ký tự).')
/** Ngày theo lịch báo cáo YouTube (YYYY-MM-DD), KHÔNG phải timestamp. */
export const isoDateSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Phải có dạng YYYY-MM-DD.')
export const channelLabelSchema = z.string().regex(/^[a-z][a-z0-9_]{1,62}$/)
/** ID video YouTube: 11 ký tự base64url. */
export const youtubeVideoIdSchema = z.string().regex(/^[A-Za-z0-9_-]{11}$/)
export const youtubeChannelIdSchema = z.string().regex(/^UC[A-Za-z0-9_-]{22}$/)

export const paginationSchema = z
  .object({
    limit: z.coerce.number().int().min(1).max(200).default(50),
    cursor: z.string().optional(),
  })
  .strict()

/**
 * Khoảng thời gian phân tích. Kiểm quan hệ start <= end ngay ở schema thay vì
 * để DB bắt: lỗi ở đây trả 400 kèm chỉ dẫn rõ ràng, còn để DB bắt thì thành 500
 * hoặc một lỗi ràng buộc khó hiểu với client.
 */
export const periodSchema = z
  .object({
    periodStart: isoDateSchema,
    periodEnd: isoDateSchema,
  })
  .strict()
  .refine((v) => v.periodStart <= v.periodEnd, {
    message: 'periodStart phải <= periodEnd.',
    path: ['periodStart'],
  })
