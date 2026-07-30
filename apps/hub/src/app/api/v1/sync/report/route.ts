import { sql } from 'drizzle-orm'
import { z } from 'zod'

import { getDb } from '@/db/client'
import { ApiError, ErrorCode } from '@/lib/errors'
import { withWorkerAuth } from '@/lib/route'
import { channelLabelSchema, parseQuery } from '@/lib/validation'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

const querySchema = z
  .object({
    channelLabel: channelLabelSchema.optional(),
    syncRunId: z.string().uuid().optional(),
    /** Kèm danh sách TỪNG video và TỪNG ngày đã nhập, không chỉ số tổng. */
    detail: z.enum(['true', 'false']).optional(),
    detailLimit: z.coerce.number().int().min(1).max(1000).default(200),
  })
  .strict()

/**
 * Báo cáo CHÍNH XÁC những gì đã nhập: kênh nào, bao nhiêu video, dải ngày nào,
 * chỉ số nào có mặt và chỉ số nào thiếu.
 *
 * Độ phủ từng chỉ số được tính riêng thay vì chỉ đếm số hàng: một hàng tồn tại
 * không có nghĩa là mọi chỉ số trong đó đều có dữ liệu. YouTube thường không
 * trả `impressions`/`impressionCtr`, và nếu chỉ đếm hàng thì báo cáo sẽ nói
 * "đủ" trong khi Phase 3 lại thấy trống.
 */
export const GET = withWorkerAuth('SYNC_ANALYTICS', async (request, ctx) => {
  const url = new URL(request.url)
  const query = parseQuery(url, querySchema)

  const channels = await getDb().execute<{
    label: string
    youtube_channel_id: string
    reporting_timezone: string
    video_count: string
    metric_rows: string
    first_date: string | null
    last_date: string | null
    last_complete_date: string | null
    revised_rows: string
  }>(sql`
    SELECT
      c.label,
      c.youtube_channel_id,
      c.reporting_timezone,
      (SELECT count(*) FROM video v WHERE v.channel_id = c.id)::text AS video_count,
      (SELECT count(*) FROM video_daily_metric m JOIN video v ON v.id = m.video_id
        WHERE v.channel_id = c.id)::text AS metric_rows,
      (SELECT min(m.date)::text FROM video_daily_metric m JOIN video v ON v.id = m.video_id
        WHERE v.channel_id = c.id) AS first_date,
      (SELECT max(m.date)::text FROM video_daily_metric m JOIN video v ON v.id = m.video_id
        WHERE v.channel_id = c.id) AS last_date,
      (SELECT cp.last_complete_date::text FROM sync_checkpoint cp WHERE cp.channel_id = c.id) AS last_complete_date,
      (SELECT count(*) FROM video_daily_metric_history h JOIN video v ON v.id = h.video_id
        WHERE v.channel_id = c.id)::text AS revised_rows
    FROM channel c
    WHERE c.workspace_id = ${ctx.principal.workspaceId}
      AND (${query.channelLabel ?? null}::text IS NULL OR c.label = ${query.channelLabel ?? null})
    ORDER BY c.label
  `)

  if (query.channelLabel && channels.rows.length === 0) {
    throw new ApiError(ErrorCode.NOT_FOUND, `Không tìm thấy kênh "${query.channelLabel}".`)
  }

  // Độ phủ từng chỉ số: bao nhiêu hàng THỰC SỰ có giá trị, không phải NULL.
  const coverage = await getDb().execute<Record<string, string>>(sql`
    SELECT
      c.label,
      count(*)::text AS total,
      count(m.views)::text AS views,
      count(m.estimated_minutes_watched)::text AS estimated_minutes_watched,
      count(m.average_view_duration_seconds)::text AS average_view_duration_seconds,
      count(m.average_view_percentage)::text AS average_view_percentage,
      count(m.impressions)::text AS impressions,
      count(m.impression_ctr)::text AS impression_ctr,
      count(m.likes)::text AS likes,
      count(m.comments)::text AS comments,
      count(m.shares)::text AS shares,
      count(m.subscribers_gained)::text AS subscribers_gained,
      count(m.subscribers_lost)::text AS subscribers_lost
    FROM channel c
    JOIN video v ON v.channel_id = c.id
    JOIN video_daily_metric m ON m.video_id = v.id
    WHERE c.workspace_id = ${ctx.principal.workspaceId}
      AND (${query.channelLabel ?? null}::text IS NULL OR c.label = ${query.channelLabel ?? null})
    GROUP BY c.label
    ORDER BY c.label
  `)

  const recentRuns = await getDb().execute<{
    id: string
    label: string
    status: string
    requested_from: string
    requested_to: string
    videos_seen: number
    video_metric_rows_upserted: number
    channel_metric_rows_upserted: number
    metric_rows_revised: number
    warnings: unknown
    started_at: string
    finished_at: string | null
  }>(sql`
    SELECT r.id, c.label, r.status, r.requested_from::text, r.requested_to::text,
           r.videos_seen, r.video_metric_rows_upserted, r.channel_metric_rows_upserted,
           r.metric_rows_revised, r.warnings, r.started_at::text, r.finished_at::text
    FROM sync_run r JOIN channel c ON c.id = r.channel_id
    WHERE r.workspace_id = ${ctx.principal.workspaceId}
      AND (${query.syncRunId ?? null}::uuid IS NULL OR r.id = ${query.syncRunId ?? null}::uuid)
      AND (${query.channelLabel ?? null}::text IS NULL OR c.label = ${query.channelLabel ?? null})
    ORDER BY r.started_at DESC
    LIMIT 20
  `)

  const coverageByLabel = new Map(coverage.rows.map((r) => [r.label, r]))

  /**
   * Chi tiết TỪNG video và TỪNG ngày.
   *
   * Số tổng hợp ở trên trả lời "bao nhiêu", nhưng tiêu chí Phase 2 đòi biết
   * CHÍNH XÁC video nào và ngày nào đã được nhập. Không có phần này thì một lỗ
   * hổng ở giữa dải ngày (ví dụ thiếu đúng ngày 2026-07-04) sẽ vô hình, vì
   * min/max vẫn trông bình thường.
   */
  let detail: unknown = undefined
  if (query.detail === 'true') {
    const perVideo = await getDb().execute<{
      label: string
      youtube_video_id: string
      title: string
      published_at: string
      format: string
      duration_seconds: number | null
      metric_days: string
      first_date: string | null
      last_date: string | null
      total_views: string | null
      missing_days: string
    }>(sql`
      SELECT c.label, v.youtube_video_id, v.title, v.published_at::text, v.format,
             v.duration_seconds,
             count(m.*)::text AS metric_days,
             min(m.date)::text AS first_date,
             max(m.date)::text AS last_date,
             sum(m.views)::text AS total_views,
             -- Số ngày TRỐNG giữa ngày đầu và ngày cuối: lỗ hổng ở giữa dải.
             GREATEST(0, (max(m.date) - min(m.date) + 1) - count(m.*))::text AS missing_days
      FROM channel c
      JOIN video v ON v.channel_id = c.id
      LEFT JOIN video_daily_metric m ON m.video_id = v.id
      WHERE c.workspace_id = ${ctx.principal.workspaceId}
        AND (${query.channelLabel ?? null}::text IS NULL OR c.label = ${query.channelLabel ?? null})
      GROUP BY c.label, v.youtube_video_id, v.title, v.published_at, v.format, v.duration_seconds
      ORDER BY c.label, sum(m.views) DESC NULLS LAST
      LIMIT ${query.detailLimit}
    `)

    const perDate = await getDb().execute<{
      label: string
      date: string
      videos_with_data: string
      total_views: string | null
    }>(sql`
      SELECT c.label, m.date::text, count(*)::text AS videos_with_data, sum(m.views)::text AS total_views
      FROM channel c
      JOIN video v ON v.channel_id = c.id
      JOIN video_daily_metric m ON m.video_id = v.id
      WHERE c.workspace_id = ${ctx.principal.workspaceId}
        AND (${query.channelLabel ?? null}::text IS NULL OR c.label = ${query.channelLabel ?? null})
      GROUP BY c.label, m.date
      ORDER BY c.label, m.date
      LIMIT ${query.detailLimit}
    `)

    detail = {
      videos: perVideo.rows.map((v) => ({
        channel: v.label,
        youtubeVideoId: v.youtube_video_id,
        title: v.title,
        publishedAt: v.published_at,
        format: v.format,
        durationSeconds: v.duration_seconds,
        metricDays: Number(v.metric_days),
        dateRange: { first: v.first_date, last: v.last_date },
        totalViews: v.total_views === null ? null : Number(v.total_views),
        missingDaysInRange: Number(v.missing_days),
      })),
      dates: perDate.rows.map((d) => ({
        channel: d.label,
        date: d.date,
        videosWithData: Number(d.videos_with_data),
        totalViews: d.total_views === null ? null : Number(d.total_views),
      })),
      truncated: {
        videos: perVideo.rows.length >= query.detailLimit,
        dates: perDate.rows.length >= query.detailLimit,
      },
    }
  }

  return Response.json({
    channels: channels.rows.map((c) => {
      const cov = coverageByLabel.get(c.label)
      const total = Number(cov?.total ?? 0)
      const pct = (key: string) =>
        total === 0 ? null : Math.round((Number(cov?.[key] ?? 0) / total) * 1000) / 10

      return {
        label: c.label,
        youtubeChannelId: c.youtube_channel_id,
        reportingTimezone: c.reporting_timezone,
        videoCount: Number(c.video_count),
        metricRows: Number(c.metric_rows),
        dateRange: { first: c.first_date, last: c.last_date },
        checkpoint: c.last_complete_date,
        revisedRows: Number(c.revised_rows),
        // Phần trăm hàng có dữ liệu cho từng chỉ số. `null` = chưa có hàng nào.
        metricCoveragePercent: {
          views: pct('views'),
          estimatedMinutesWatched: pct('estimated_minutes_watched'),
          averageViewDurationSeconds: pct('average_view_duration_seconds'),
          averageViewPercentage: pct('average_view_percentage'),
          impressions: pct('impressions'),
          impressionCtr: pct('impression_ctr'),
          likes: pct('likes'),
          comments: pct('comments'),
          shares: pct('shares'),
          subscribersGained: pct('subscribers_gained'),
          subscribersLost: pct('subscribers_lost'),
        },
      }
    }),
    recentSyncRuns: recentRuns.rows,
    ...(detail === undefined ? {} : { detail }),
  })
})
