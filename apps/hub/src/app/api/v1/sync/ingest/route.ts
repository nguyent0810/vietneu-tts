import { eq } from 'drizzle-orm'
import { z } from 'zod'

import { getDb, withTransaction } from '@/db/client'
import { syncRun } from '@/db/schema'
import { ApiError, ErrorCode } from '@/lib/errors'
import { assertSameWorkspace, withWorkerAuth } from '@/lib/route'
import {
  isoDateSchema,
  parseBody,
  sha256Schema,
  uuidSchema,
  youtubeVideoIdSchema,
} from '@/lib/validation'
import {
  recordApiCall,
  upsertChannelMetrics,
  upsertVideoMetrics,
  upsertVideos,
} from '@/lib/sync'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

/**
 * Chỉ số đều nullable: YouTube không trả `impressions`/`impressionCtr` cho mọi
 * truy vấn. Cho phép NULL đi thẳng vào DB thay vì ép 0 — xem `normalizeMetrics`.
 */
/**
 * Ràng buộc chỉ chặn giá trị BẤT KHẢ THI, không chặn giá trị gây ngạc nhiên.
 * Cả hai nới lỏng dưới đây đến từ dữ liệu THẬT của 3 kênh, không phải suy đoán:
 *
 *  - `averageViewPercentage` VƯỢT 100 được: người xem tua lại, nên thời lượng
 *    xem có thể lớn hơn độ dài video. Chặn ở 100 là loại bỏ chính những video
 *    giữ chân tốt nhất.
 *  - `likes`/`dislikes`/`comments`/`shares` ÂM được: báo cáo theo ngày là
 *    CHÊNH LỆCH, nên gỡ like/xoá bình luận cho ra số âm.
 *
 * Còn `views`/`impressions`/`subscribers*` là phép đếm thuần nên vẫn >= 0.
 */
const metricSchema = z.object({
  views: z.number().int().min(0).nullable().optional(),
  estimatedMinutesWatched: z.number().min(0).nullable().optional(),
  averageViewDurationSeconds: z.number().min(0).nullable().optional(),
  averageViewPercentage: z.number().min(0).nullable().optional(),
  impressions: z.number().int().min(0).nullable().optional(),
  impressionCtr: z.number().min(0).max(100).nullable().optional(),
  likes: z.number().int().nullable().optional(),
  dislikes: z.number().int().nullable().optional(),
  comments: z.number().int().nullable().optional(),
  shares: z.number().int().nullable().optional(),
  subscribersGained: z.number().int().min(0).nullable().optional(),
  subscribersLost: z.number().int().min(0).nullable().optional(),
})

const bodySchema = z
  .object({
    syncRunId: uuidSchema,
    videos: z
      .array(
        z
          .object({
            youtubeVideoId: youtubeVideoIdSchema,
            title: z.string().min(1).max(500),
            description: z.string().max(10_000).nullable().optional(),
            publishedAt: z.string().datetime({ offset: true }),
            durationSeconds: z.number().int().min(0).nullable().optional(),
            format: z.enum(['LONG_FORM', 'SHORT', 'UNKNOWN']).optional(),
            privacyStatus: z.string().max(32).nullable().optional(),
            publishedHourLocal: z.number().int().min(0).max(23).nullable().optional(),
          })
          .strict(),
      )
      .max(500)
      .default([]),
    videoMetrics: z
      .array(
        metricSchema
          .extend({ youtubeVideoId: youtubeVideoIdSchema, date: isoDateSchema })
          .strict(),
      )
      .max(3000)
      .default([]),
    channelMetrics: z
      .array(metricSchema.extend({ date: isoDateSchema }).strict())
      .max(1000)
      .default([]),
    apiCalls: z
      .array(
        z
          .object({
            endpoint: z.string().max(200),
            requestParams: z.record(z.unknown()),
            httpStatus: z.number().int().optional(),
            rowCount: z.number().int().min(0).optional(),
            // nullable, không chỉ optional: một lời gọi THẤT BẠI vẫn phải được
            // ghi nhật ký (đó mới là lúc cần truy vết nhất), và khi đó không có
            // thân phản hồi để băm.
            responseHash: sha256Schema.nullable().optional(),
            columnHeaders: z.unknown().nullable().optional(),
            durationMs: z.number().int().min(0).nullable().optional(),
          })
          .strict(),
      )
      .max(50)
      .default([]),
  })
  .strict()

/**
 * Nhận một LÔ dữ liệu cho lần đồng bộ đang mở.
 *
 * Giới hạn lô cố ý đặt thấp hơn nhiều so với trần 4.5 MB của Vercel: vượt trần
 * sẽ bị hạ tầng chặn bằng 413 TRƯỚC KHI code chạy, nên client nhận một lỗi
 * không nằm trong bảng phân loại. CLI tự chia lô theo các trần này.
 *
 * Gọi lại cùng một lô là AN TOÀN: tất cả đều là upsert theo khoá tự nhiên
 * (`youtube_video_id`, `(video_id, date)`), nên retry sau timeout mạng không
 * tạo bản trùng và không sinh lịch sử giả.
 */
export const POST = withWorkerAuth(
  'SYNC_ANALYTICS',
  async (request, ctx) => {
    const body = await parseBody(request, bodySchema)

    const runs = await getDb()
      .select({
        id: syncRun.id,
        workspaceId: syncRun.workspaceId,
        channelId: syncRun.channelId,
        status: syncRun.status,
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

    // AC-4 — cả lô nhập nằm trong MỘT transaction.
    //
    // Nếu chạy rời từng câu lệnh (driver HTTP), một lỗi giữa chừng sẽ để lại lô
    // nhập dở dang: video đã ghi, chỉ số video đã ghi, còn chỉ số kênh thì
    // chưa. Các upsert đều idempotent nên không hỏng dữ liệu, nhưng "một lô =
    // một đơn vị" là đúng thứ AC-4 yêu cầu, và nó khiến việc suy luận về trạng
    // thái sau lỗi đơn giản hơn hẳn.
    //
    // `sync_run` CỐ Ý nằm NGOÀI transaction này (cập nhật ở /sync/finish), nên
    // rollback dữ liệu nghiệp vụ không xoá mất bằng chứng đã chạy gì.
    const result = await withTransaction(async (tx) => {
      // Thứ tự bắt buộc: video TRƯỚC chỉ số. Chỉ số tham chiếu video qua
      // youtube_video_id, và hàng chỉ số của video chưa biết sẽ bị bỏ qua.
      const videosUpserted = await upsertVideos({
        workspaceId: run.workspaceId,
        channelId: run.channelId,
        videos: body.videos,
        db: tx,
      })

      const videoMetrics = await upsertVideoMetrics({
        workspaceId: run.workspaceId,
        syncRunId: run.id,
        metrics: body.videoMetrics,
        db: tx,
      })

      const channelMetricRows = await upsertChannelMetrics({
        workspaceId: run.workspaceId,
        channelId: run.channelId,
        syncRunId: run.id,
        metrics: body.channelMetrics,
        db: tx,
      })

      for (const call of body.apiCalls) {
        await recordApiCall({ syncRunId: run.id, ...call, db: tx })
      }

      return { videosUpserted, videoMetrics, channelMetricRows }
    })

    const { videosUpserted, videoMetrics, channelMetricRows } = result

    const skipped = body.videoMetrics.length - videoMetrics.upserted

    return Response.json({
      videosUpserted,
      videoMetricRowsUpserted: videoMetrics.upserted,
      videoMetricRowsRevised: videoMetrics.revised,
      channelMetricRowsUpserted: channelMetricRows,
      // Báo rõ số hàng bị bỏ vì chưa biết video — im lặng bỏ qua sẽ khiến
      // dữ liệu thiếu mà không ai nhận ra.
      videoMetricRowsSkippedUnknownVideo: skipped,
    })
  },
  // Lô lớn nên hạn mức rộng hơn mặc định.
  { rateLimit: { capacity: 300, refillRate: 5 } },
)
