import { randomUUID } from 'node:crypto'

import { authenticateWorker, requireCapability, type WorkerCapability, type WorkerPrincipal } from './auth'
import { ApiError, ErrorCode, scrubSecrets, toApiError } from './errors'
import { consumeRateLimit } from './ratelimit'

/**
 * Vỏ bọc chung cho route handler: một đường vào, một đường ra lỗi.
 *
 * Mọi lỗi đều đi qua `toApiError` nên client luôn nhận đúng hình dạng
 * `{error:{code,message,requestId}}`. Không route nào được tự dựng phản hồi lỗi
 * riêng — nếu không, mã lỗi sẽ trôi khỏi hợp đồng đã công bố.
 */
export interface WorkerContext {
  principal: WorkerPrincipal
  requestId: string
}

export function jsonError(err: unknown, requestId: string): Response {
  const apiError = toApiError(err)
  const headers: Record<string, string> = { 'x-request-id': requestId }
  if (apiError.code === ErrorCode.RATE_LIMITED && apiError.retryAfterSeconds) {
    headers['retry-after'] = String(apiError.retryAfterSeconds)
  }

  if (apiError.status >= 500) {
    // Ghi log PHÍA SERVER kèm requestId. Trả 500 mà không log gì thì lỗi
    // production thành không thể chẩn đoán -- đúng tình huống đã gặp khi chạy
    // thật lần đầu. Nhưng chi tiết KHÔNG gửi ra client: message nội bộ có thể
    // chứa tên bảng, tên ràng buộc, hoặc mảnh connection string.
    const detail = err instanceof Error ? `${err.message}\n${err.stack ?? ''}` : String(err)
    console.error(`[${requestId}] ${apiError.code}: ${scrubSecrets(detail).slice(0, 2000)}`)

    return Response.json(
      { error: { code: apiError.code, message: 'Lỗi nội bộ.', requestId } },
      { status: apiError.status, headers },
    )
  }
  return Response.json(apiError.toBody(requestId), { status: apiError.status, headers })
}

/**
 * Bọc một handler yêu cầu xác thực WORKER.
 *
 * Rate limit tính theo TỪNG MÁY worker, dùng bucket lưu ở Neon (AC-6) nên trần
 * vẫn đúng khi Vercel chạy nhiều instance song song.
 */
export function withWorkerAuth(
  capability: WorkerCapability,
  handler: (request: Request, ctx: WorkerContext) => Promise<Response>,
  options: { rateLimit?: { capacity: number; refillRate: number } } = {},
) {
  return async function route(request: Request): Promise<Response> {
    const requestId = randomUUID()
    try {
      const principal = await authenticateWorker(request.headers.get('authorization'))
      requireCapability(principal, capability)

      const limit = options.rateLimit ?? { capacity: 120, refillRate: 2 }
      const verdict = await consumeRateLimit(`worker:${principal.machineId}:${capability}`, limit)
      if (!verdict.allowed) {
        throw new ApiError(ErrorCode.RATE_LIMITED, 'Vượt hạn mức gọi API.', {
          retryAfterSeconds: verdict.retryAfterSeconds,
        })
      }

      const response = await handler(request, { principal, requestId })
      response.headers.set('x-request-id', requestId)
      return response
    } catch (err) {
      return jsonError(err, requestId)
    }
  }
}

/** Kiểm tra tài nguyên thuộc đúng workspace của principal trước khi ghi. */
export function assertSameWorkspace(principal: WorkerPrincipal, workspaceId: string): void {
  if (principal.workspaceId !== workspaceId) {
    // Trả NOT_FOUND chứ không phải FORBIDDEN: nói "cấm" là xác nhận tài nguyên
    // đó tồn tại, giúp người dò quét lập bản đồ dữ liệu của workspace khác.
    throw new ApiError(ErrorCode.NOT_FOUND, 'Không tìm thấy tài nguyên.')
  }
}
