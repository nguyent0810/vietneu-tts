import { sql } from 'drizzle-orm'

import { getDb } from '@/db/client'
import { toApiError } from '@/lib/errors'

/**
 * Health check. Cố ý KHÔNG yêu cầu xác thực và KHÔNG trả bất kỳ thông tin nào
 * về hạ tầng: không host, không tên database, không phiên bản. Một endpoint
 * health rò chi tiết hạ tầng là món quà miễn phí cho người dò quét.
 */
export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET(): Promise<Response> {
  const startedAt = Date.now()
  try {
    await getDb().execute(sql`SELECT 1`)
    return Response.json({
      status: 'ok',
      database: 'reachable',
      latencyMs: Date.now() - startedAt,
    })
  } catch (err) {
    const apiError = toApiError(err)
    // Chỉ trả mã lỗi đã chuẩn hoá, không trả message gốc của driver/Postgres.
    return Response.json(
      { status: 'degraded', database: 'unreachable', code: apiError.code },
      { status: 503 },
    )
  }
}
