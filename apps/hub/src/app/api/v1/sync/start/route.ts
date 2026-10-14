import { z } from 'zod'

import { assertSameWorkspace, withWorkerAuth } from '@/lib/route'
import { ApiError, ErrorCode } from '@/lib/errors'
import { channelLabelSchema, parseBody } from '@/lib/validation'
import { computeSyncWindow, getChannelByLabel, startSyncRun } from '@/lib/sync'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

const bodySchema = z
  .object({
    channelLabel: channelLabelSchema,
    workerLabel: z.string().min(1).max(64),
    /** Lần chạy đầu (chưa có checkpoint) thì lùi bao nhiêu ngày. */
    initialDays: z.number().int().min(1).max(400).default(90),
    /** Ép khoảng ngày, bỏ qua checkpoint. Dùng khi cần lấy lại lịch sử. */
    forceFrom: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
    forceTo: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  })
  .strict()

/**
 * Mở một lần đồng bộ và trả về khoảng ngày mà CLI PHẢI lấy.
 *
 * Cửa sổ do server tính chứ không do client tự chọn: nó phụ thuộc checkpoint,
 * múi giờ báo cáo của kênh và cửa sổ lùi cho dữ liệu đến trễ. Để client tự tính
 * thì mỗi máy worker có thể hiểu khác nhau và tạo lỗ hổng dữ liệu âm thầm.
 */
export const POST = withWorkerAuth('SYNC_ANALYTICS', async (request, ctx) => {
  const body = await parseBody(request, bodySchema)

  const found = await getChannelByLabel({
    workspaceId: ctx.principal.workspaceId,
    label: body.channelLabel,
  })
  if (!found) {
    throw new ApiError(ErrorCode.NOT_FOUND, `Không tìm thấy kênh "${body.channelLabel}".`)
  }
  assertSameWorkspace(ctx.principal, ctx.principal.workspaceId)

  const window =
    body.forceFrom && body.forceTo
      ? { from: body.forceFrom, to: body.forceTo }
      : computeSyncWindow({
          timezone: found.reportingTimezone,
          lastCompleteDate: found.lastCompleteDate,
          initialDays: body.initialDays,
        })

  if (window.from > window.to) {
    throw new ApiError(ErrorCode.VALIDATION_FAILED, 'Khoảng ngày không hợp lệ (from > to).')
  }

  const syncRunId = await startSyncRun({
    workspaceId: ctx.principal.workspaceId,
    channelId: found.id,
    requestedFrom: window.from,
    requestedTo: window.to,
    workerLabel: body.workerLabel,
  })

  return Response.json({
    syncRunId,
    channel: {
      id: found.id,
      label: found.label,
      youtubeChannelId: found.youtubeChannelId,
      reportingTimezone: found.reportingTimezone,
    },
    window,
    previousCheckpoint: found.lastCompleteDate,
  })
})
