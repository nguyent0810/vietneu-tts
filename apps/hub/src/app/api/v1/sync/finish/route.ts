import { eq, sql } from 'drizzle-orm'
import { z } from 'zod'

import { getDb } from '@/db/client'
import { auditEvent, syncRun } from '@/db/schema'
import { ApiError, ErrorCode } from '@/lib/errors'
import { assertSameWorkspace, withWorkerAuth } from '@/lib/route'
import { isoDateSchema, parseBody, uuidSchema } from '@/lib/validation'
import { advanceCheckpoint, finishSyncRun } from '@/lib/sync'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

const bodySchema = z
  .object({
    syncRunId: uuidSchema,
    status: z.enum(['SUCCEEDED', 'PARTIAL', 'FAILED']),
    /** Chỉ đẩy checkpoint khi CLI khẳng định đã lấy đủ tới ngày này. */
    lastCompleteDate: isoDateSchema.optional(),
    warnings: z.array(z.string().max(500)).max(200).default([]),
    errorMessage: z.string().max(1000).optional(),
  })
  .strict()

/**
 * Đóng một lần đồng bộ và (nếu thành công) đẩy checkpoint tiến lên.
 *
 * AC-4: bản ghi `sync_run` được cập nhật ở transaction RIÊNG với dữ liệu
 * nghiệp vụ, nên nó luôn sống sót kể cả khi lần chạy thất bại giữa chừng — có
 * lỗi, có thời điểm, có thống kê. Gói chung một transaction thì rollback sẽ
 * xoá luôn bằng chứng đã chạy gì.
 *
 * Checkpoint CHỈ tiến khi status = SUCCEEDED. PARTIAL nghĩa là còn lỗ hổng
 * trong khoảng ngày; đẩy checkpoint lúc đó sẽ khoá vĩnh viễn phần thiếu, vì
 * lần sau chỉ lấy từ checkpoint trở đi.
 */
export const POST = withWorkerAuth('SYNC_ANALYTICS', async (request, ctx) => {
  const body = await parseBody(request, bodySchema)

  const runs = await getDb()
    .select({
      id: syncRun.id,
      workspaceId: syncRun.workspaceId,
      channelId: syncRun.channelId,
      status: syncRun.status,
      requestedTo: syncRun.requestedTo,
    })
    .from(syncRun)
    .where(eq(syncRun.id, body.syncRunId))
    .limit(1)

  const run = runs[0]
  if (!run) throw new ApiError(ErrorCode.NOT_FOUND, 'Không tìm thấy sync run.')
  assertSameWorkspace(ctx.principal, run.workspaceId)
  if (run.status !== 'RUNNING') {
    throw new ApiError(ErrorCode.CONFLICT, `Sync run đã kết thúc (${run.status}).`)
  }

  // Kiểm tra checkpoint TRƯỚC KHI chốt trạng thái run.
  //
  // Bản đầu kiểm sau khi đã gọi finishSyncRun: run bị đánh dấu SUCCEEDED rồi
  // request mới trả 400, nên run vĩnh viễn kẹt — không còn ở RUNNING để chốt
  // lại, mà cũng không phản ánh đúng kết quả. Kiểm trước thì run vẫn ở RUNNING
  // và client sửa rồi gọi lại được.
  //
  // Bản thân giới hạn: checkpoint không được vượt quá khoảng ngày mà chính lần
  // chạy này đã yêu cầu. Tin lời client ở đây là cho phép một worker lỗi (hoặc
  // bị chiếm) đẩy checkpoint nhảy qua những ngày CHƯA HỀ được lấy — và vì lần
  // sau chỉ lấy từ checkpoint trở đi, lỗ hổng đó thành vĩnh viễn và im lặng.
  if (body.status === 'SUCCEEDED' && body.lastCompleteDate && body.lastCompleteDate > run.requestedTo) {
    throw new ApiError(
      ErrorCode.VALIDATION_FAILED,
      `lastCompleteDate (${body.lastCompleteDate}) vượt quá khoảng đã yêu cầu (đến ${run.requestedTo}).`,
    )
  }

  // Thống kê tính TỪ DỮ LIỆU ĐÃ GHI, không tin con số client gửi lên: client
  // có thể retry một lô và đếm trùng.
  const stats = await getDb().execute<{
    videos_seen: string
    video_rows: string
    channel_rows: string
    revised: string
  }>(sql`
    SELECT
      (SELECT count(*) FROM video WHERE channel_id = ${run.channelId})::text AS videos_seen,
      (SELECT count(*) FROM video_daily_metric m
         JOIN video v ON v.id = m.video_id
        WHERE v.channel_id = ${run.channelId} AND m.last_sync_run_id = ${run.id})::text AS video_rows,
      (SELECT count(*) FROM channel_daily_metric
        WHERE channel_id = ${run.channelId} AND last_sync_run_id = ${run.id})::text AS channel_rows,
      (SELECT count(*) FROM video_daily_metric_history h
         JOIN video v ON v.id = h.video_id
        WHERE v.channel_id = ${run.channelId} AND h.superseded_at >= now() - interval '1 hour')::text AS revised
  `)
  const s = stats.rows[0]

  await finishSyncRun({
    syncRunId: run.id,
    status: body.status,
    error: body.status === 'FAILED' ? new Error(body.errorMessage ?? 'Không rõ lỗi') : undefined,
    warnings: body.warnings,
    stats: {
      videosSeen: Number(s?.videos_seen ?? 0),
      videoMetricRowsUpserted: Number(s?.video_rows ?? 0),
      channelMetricRowsUpserted: Number(s?.channel_rows ?? 0),
      metricRowsRevised: Number(s?.revised ?? 0),
    },
  })

  let checkpointAdvanced = false
  if (body.status === 'SUCCEEDED' && body.lastCompleteDate) {
    await advanceCheckpoint({
      workspaceId: run.workspaceId,
      channelId: run.channelId,
      syncRunId: run.id,
      lastCompleteDate: body.lastCompleteDate,
    })
    checkpointAdvanced = true
  }

  await getDb().insert(auditEvent).values({
    workspaceId: run.workspaceId,
    actorType: 'WORKER',
    actorId: ctx.principal.machineLabel,
    action: 'SYNC_ANALYTICS_FINISHED',
    entityType: 'sync_run',
    entityId: run.id,
    payload: {
      status: body.status,
      warningCount: body.warnings.length,
      checkpointAdvanced,
    },
  })

  return Response.json({
    syncRunId: run.id,
    status: body.status,
    checkpointAdvanced,
    stats: {
      videosSeen: Number(s?.videos_seen ?? 0),
      videoMetricRowsUpserted: Number(s?.video_rows ?? 0),
      channelMetricRowsUpserted: Number(s?.channel_rows ?? 0),
      metricRowsRevised: Number(s?.revised ?? 0),
    },
  })
})
