import { and, eq, inArray, sql } from 'drizzle-orm'

import { getDb, withTransaction, type Executor } from '@/db/client'
import {
  analyticsApiCall,
  channel,
  channelDailyMetric,
  syncCheckpoint,
  syncRun,
  video,
  videoDailyMetric,
} from '@/db/schema'
import { ApiError, ErrorCode, scrubSecrets, toApiError } from './errors'

/**
 * YouTube còn sửa số liệu trong 48-72h sau khi công bố. Mỗi lần đồng bộ vì thế
 * phải lấy lại một CỬA SỔ LÙI kể từ checkpoint, không chỉ lấy từ checkpoint trở
 * đi — nếu không thì mọi chỉnh sửa muộn của YouTube sẽ không bao giờ vào
 * database, và số liệu ở đây vĩnh viễn lệch so với YouTube Studio.
 *
 * 7 ngày là gấp đôi cửa sổ 72h, đủ biên an toàn cho cả trường hợp sync gián
 * đoạn một hai ngày.
 */
export const LOOKBACK_DAYS = 7

/**
 * YouTube Analytics chưa chốt số liệu của 1-2 ngày gần nhất. Lấy tới hôm nay
 * sẽ ghi vào những con số gần như chắc chắn sẽ bị sửa, làm `revision_count`
 * tăng vô ích và gây nhiễu cho phân tích.
 */
export const RECENT_INCOMPLETE_DAYS = 2

export interface MetricValues {
  views?: number | null
  estimatedMinutesWatched?: number | null
  averageViewDurationSeconds?: number | null
  averageViewPercentage?: number | null
  impressions?: number | null
  impressionCtr?: number | null
  likes?: number | null
  dislikes?: number | null
  comments?: number | null
  shares?: number | null
  subscribersGained?: number | null
  subscribersLost?: number | null
}

export interface VideoInput {
  youtubeVideoId: string
  title: string
  description?: string | null
  publishedAt: string
  durationSeconds?: number | null
  format?: 'LONG_FORM' | 'SHORT' | 'UNKNOWN'
  privacyStatus?: string | null
  publishedHourLocal?: number | null
}

export interface VideoMetricInput extends MetricValues {
  youtubeVideoId: string
  date: string
}

export interface ChannelMetricInput extends MetricValues {
  date: string
}

/**
 * Ngày báo cáo mà YouTube coi là đã ổn định, tính theo múi giờ BÁO CÁO của
 * kênh chứ không phải giờ máy chạy sync.
 *
 * Dùng `Intl.DateTimeFormat` với `en-CA` vì locale đó cho ra đúng dạng
 * YYYY-MM-DD, tránh phải tự ghép chuỗi ngày (nguồn lỗi lệch múi giờ kinh điển).
 */
export function reportingDateBounds(
  timezone: string,
  now: Date = new Date(),
): { today: string; lastComplete: string } {
  const fmt = new Intl.DateTimeFormat('en-CA', {
    timeZone: timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
  const today = fmt.format(now)
  const complete = new Date(now.getTime() - RECENT_INCOMPLETE_DAYS * 86_400_000)
  return { today, lastComplete: fmt.format(complete) }
}

export function addDays(isoDate: string, days: number): string {
  const [y, m, d] = isoDate.split('-').map(Number)
  // UTC có chủ đích: đây là số học trên NHÃN NGÀY, không phải trên thời điểm.
  // Dùng giờ địa phương ở đây sẽ làm ngày nhảy khi máy chạy ở múi giờ khác.
  const dt = new Date(Date.UTC(y!, m! - 1, d!))
  dt.setUTCDate(dt.getUTCDate() + days)
  return dt.toISOString().slice(0, 10)
}

/** Khoảng ngày cần lấy cho lần đồng bộ tới, có tính cửa sổ lùi. */
export function computeSyncWindow(params: {
  timezone: string
  lastCompleteDate: string | null
  /** Khi chưa có checkpoint: lùi bao nhiêu ngày cho lần chạy đầu. */
  initialDays: number
  now?: Date
}): { from: string; to: string } {
  const { lastComplete } = reportingDateBounds(params.timezone, params.now)
  const from = params.lastCompleteDate
    ? addDays(params.lastCompleteDate, -LOOKBACK_DAYS)
    : addDays(lastComplete, -params.initialDays)
  // Không bao giờ lấy quá mốc ổn định, kể cả khi checkpoint đã vượt lên.
  const to = lastComplete
  return { from: from > to ? to : from, to }
}

export async function startSyncRun(params: {
  workspaceId: string
  channelId: string
  requestedFrom: string
  requestedTo: string
  workerLabel: string
}): Promise<string> {
  const [row] = await getDb()
    .insert(syncRun)
    .values({
      workspaceId: params.workspaceId,
      channelId: params.channelId,
      requestedFrom: params.requestedFrom,
      requestedTo: params.requestedTo,
      workerLabel: params.workerLabel,
      status: 'RUNNING',
    })
    .returning({ id: syncRun.id })
  return row!.id
}

/**
 * AC-4 — ranh giới transaction khi nhập dữ liệu.
 *
 * Dữ liệu nghiệp vụ (video, chỉ số) nằm TRONG transaction và rollback trọn vẹn
 * khi lỗi. Nhưng `sync_run` được cập nhật ở một transaction RIÊNG sau đó, nên
 * bản ghi kiểm toán luôn sống sót ở trạng thái FAILED kèm lỗi.
 *
 * Nếu gói tất cả vào một transaction thì rollback sẽ xoá luôn bằng chứng đã
 * chạy gì — đúng kiểu lỗi chỉ phát hiện được khi cần điều tra mà không còn gì
 * để đọc.
 */
export async function finishSyncRun(params: {
  syncRunId: string
  status: 'SUCCEEDED' | 'PARTIAL' | 'FAILED'
  error?: unknown
  warnings?: unknown[]
  stats?: {
    videosSeen?: number
    videosUpserted?: number
    videoMetricRowsUpserted?: number
    channelMetricRowsUpserted?: number
    metricRowsRevised?: number
  }
}): Promise<void> {
  const errorPayload =
    params.status === 'FAILED'
      ? { message: describeError(params.error), at: new Date().toISOString() }
      : null

  await getDb()
    .update(syncRun)
    .set({
      status: params.status,
      finishedAt: new Date(),
      error: errorPayload,
      ...(params.warnings ? { warnings: params.warnings } : {}),
      ...(params.stats ?? {}),
    })
    .where(eq(syncRun.id, params.syncRunId))
}

/**
 * Chỉ lấy phần mô tả AN TOÀN của lỗi.
 *
 * Không bao giờ ghi nguyên object lỗi vào database: lỗi từ driver Postgres và
 * từ fetch có thể mang theo connection string (chứa mật khẩu) hoặc header
 * Authorization.
 */
function describeError(err: unknown): string {
  const raw =
    err instanceof ApiError
      ? `${err.code}: ${err.message}`
      : err instanceof Error
        ? err.message
        : 'Lỗi không xác định'
  // Lọc credential TRƯỚC khi ghi vào database: message của driver Postgres có
  // thể chứa nguyên connection string kèm mật khẩu.
  return scrubSecrets(raw).slice(0, 500)
}

/** Upsert video theo lô, idempotent theo `youtube_video_id`. */
export async function upsertVideos(params: {
  workspaceId: string
  channelId: string
  videos: VideoInput[]
  /** Truyền transaction vào để cả lô nhập cùng rollback được (AC-4). */
  db?: Executor
}): Promise<number> {
  if (params.videos.length === 0) return 0

  const rows = params.videos.map((v) => ({
    workspaceId: params.workspaceId,
    channelId: params.channelId,
    youtubeVideoId: v.youtubeVideoId,
    title: v.title,
    description: v.description ?? null,
    publishedAt: new Date(v.publishedAt),
    durationSeconds: v.durationSeconds ?? null,
    format: v.format ?? ('UNKNOWN' as const),
    privacyStatus: v.privacyStatus ?? null,
    publishedHourLocal: v.publishedHourLocal ?? null,
  }))

  await (params.db ?? getDb())
    .insert(video)
    .values(rows)
    .onConflictDoUpdate({
      target: video.youtubeVideoId,
      set: {
        title: sql`excluded.title`,
        description: sql`excluded.description`,
        durationSeconds: sql`excluded.duration_seconds`,
        format: sql`excluded.format`,
        privacyStatus: sql`excluded.privacy_status`,
        publishedHourLocal: sql`excluded.published_hour_local`,
        updatedAt: new Date(),
      },
    })

  // Upsert luôn tác động lên toàn bộ hàng truyền vào, nên không cần RETURNING
  // (và RETURNING không dùng được khi executor là union HTTP | transaction).
  return rows.length
}

/**
 * Upsert chỉ số video theo ngày. Idempotent: chạy lại cùng dữ liệu không tạo
 * hàng mới và không sinh thêm lịch sử (trigger chỉ ghi khi giá trị thực sự đổi).
 */
export async function upsertVideoMetrics(params: {
  workspaceId: string
  syncRunId: string
  metrics: VideoMetricInput[]
  db?: Executor
}): Promise<{ upserted: number; revised: number }> {
  if (params.metrics.length === 0) return { upserted: 0, revised: 0 }

  const db = params.db ?? getDb()

  // Ánh xạ youtube_video_id -> uuid nội bộ. Video chưa có trong DB thì bỏ qua
  // hàng chỉ số đó thay vì tạo video rỗng: một video "ma" không có tiêu đề và
  // ngày đăng sẽ làm hỏng mọi so sánh ở Phase 3.
  const ids = [...new Set(params.metrics.map((m) => m.youtubeVideoId))]
  // `inArray` chứ không phải sql`= ANY(${ids})`: cách thứ hai truyền mảng JS
  // như một tham số đơn nên Postgres báo "op ANY/ALL (array) requires array on
  // right side" ngay lần chạy thật đầu tiên.
  const known = await db
    .select({ id: video.id, ytId: video.youtubeVideoId })
    .from(video)
    .where(and(eq(video.workspaceId, params.workspaceId), inArray(video.youtubeVideoId, ids)))
  const byYtId = new Map(known.map((k) => [k.ytId, k.id]))

  const rows = params.metrics
    .filter((m) => byYtId.has(m.youtubeVideoId))
    .map((m) => ({
      workspaceId: params.workspaceId,
      videoId: byYtId.get(m.youtubeVideoId)!,
      date: m.date,
      lastSyncRunId: params.syncRunId,
      ...normalizeMetrics(m),
    }))

  if (rows.length === 0) return { upserted: 0, revised: 0 }

  const before = await countRevisions(params.workspaceId, db)

  await db
    .insert(videoDailyMetric)
    .values(rows)
    .onConflictDoUpdate({
      target: [videoDailyMetric.videoId, videoDailyMetric.date],
      set: metricUpdateSet(videoDailyMetric),
    })

  const after = await countRevisions(params.workspaceId, db)
  return { upserted: rows.length, revised: after - before }
}

export async function upsertChannelMetrics(params: {
  workspaceId: string
  channelId: string
  syncRunId: string
  metrics: ChannelMetricInput[]
  db?: Executor
}): Promise<number> {
  if (params.metrics.length === 0) return 0

  const rows = params.metrics.map((m) => ({
    workspaceId: params.workspaceId,
    channelId: params.channelId,
    date: m.date,
    lastSyncRunId: params.syncRunId,
    ...normalizeMetrics(m),
  }))

  await (params.db ?? getDb())
    .insert(channelDailyMetric)
    .values(rows)
    .onConflictDoUpdate({
      target: [channelDailyMetric.channelId, channelDailyMetric.date],
      set: metricUpdateSet(channelDailyMetric),
    })

  return rows.length
}

/**
 * Chuẩn hoá chỉ số: `undefined` -> `null`.
 *
 * KHÔNG đổi thiếu-dữ-liệu thành 0. "0 lượt xem" và "YouTube không trả chỉ số
 * này" là hai sự thật khác nhau; gộp lại là bịa số liệu, và Phase 3 sẽ tính
 * sai độ đầy đủ lẫn độ tin cậy.
 */
function normalizeMetrics(m: MetricValues) {
  const num = (v: number | null | undefined) =>
    v === undefined || v === null || Number.isNaN(v) ? null : v
  const str = (v: number | null | undefined) => {
    const n = num(v)
    return n === null ? null : String(n)
  }
  return {
    views: num(m.views),
    estimatedMinutesWatched: str(m.estimatedMinutesWatched),
    averageViewDurationSeconds: str(m.averageViewDurationSeconds),
    averageViewPercentage: str(m.averageViewPercentage),
    impressions: num(m.impressions),
    impressionCtr: str(m.impressionCtr),
    likes: num(m.likes),
    dislikes: num(m.dislikes),
    comments: num(m.comments),
    shares: num(m.shares),
    subscribersGained: num(m.subscribersGained),
    subscribersLost: num(m.subscribersLost),
  }
}

function metricUpdateSet(table: typeof videoDailyMetric | typeof channelDailyMetric) {
  void table
  return {
    views: sql`excluded.views`,
    estimatedMinutesWatched: sql`excluded.estimated_minutes_watched`,
    averageViewDurationSeconds: sql`excluded.average_view_duration_seconds`,
    averageViewPercentage: sql`excluded.average_view_percentage`,
    impressions: sql`excluded.impressions`,
    impressionCtr: sql`excluded.impression_ctr`,
    likes: sql`excluded.likes`,
    dislikes: sql`excluded.dislikes`,
    comments: sql`excluded.comments`,
    shares: sql`excluded.shares`,
    subscribersGained: sql`excluded.subscribers_gained`,
    subscribersLost: sql`excluded.subscribers_lost`,
    lastSyncRunId: sql`excluded.last_sync_run_id`,
  }
}

async function countRevisions(workspaceId: string, db: Executor = getDb()): Promise<number> {
  const res = await db.execute<{ total: string }>(sql`
    SELECT COALESCE(SUM(revision_count), 0)::text AS total
    FROM video_daily_metric WHERE workspace_id = ${workspaceId}
  `)
  return Number(res.rows[0]?.total ?? 0)
}

/** Ghi nhật ký một lời gọi API. Tham số đã được lọc ở phía gọi. */
export async function recordApiCall(params: {
  syncRunId: string
  endpoint: string
  requestParams: Record<string, unknown>
  httpStatus?: number | null
  rowCount?: number | null
  // nullable: lời gọi thất bại không có thân phản hồi để băm, nhưng vẫn phải
  // được ghi nhật ký — đó chính là lúc cần truy vết nhất.
  responseHash?: string | null
  columnHeaders?: unknown
  durationMs?: number | null
  db?: Executor
}): Promise<void> {
  await (params.db ?? getDb()).insert(analyticsApiCall).values({
    syncRunId: params.syncRunId,
    endpoint: params.endpoint,
    requestParams: params.requestParams,
    httpStatus: params.httpStatus ?? null,
    rowCount: params.rowCount ?? null,
    responseHash: params.responseHash ?? null,
    columnHeaders: params.columnHeaders ?? null,
    durationMs: params.durationMs ?? null,
  })
}

/**
 * Đẩy checkpoint tiến lên.
 *
 * Chỉ tiến, không lùi (`GREATEST`): một lần chạy lấy lại dữ liệu cũ không được
 * kéo checkpoint về quá khứ, nếu không lần sau sẽ đồng bộ thừa vô hạn.
 */
export async function advanceCheckpoint(params: {
  workspaceId: string
  channelId: string
  syncRunId: string
  lastCompleteDate: string
}): Promise<void> {
  await getDb()
    .insert(syncCheckpoint)
    .values({
      workspaceId: params.workspaceId,
      channelId: params.channelId,
      lastCompleteDate: params.lastCompleteDate,
      lastSyncRunId: params.syncRunId,
    })
    .onConflictDoUpdate({
      target: syncCheckpoint.channelId,
      set: {
        lastCompleteDate: sql`GREATEST(sync_checkpoint.last_complete_date, excluded.last_complete_date)`,
        lastSyncRunId: sql`excluded.last_sync_run_id`,
        updatedAt: new Date(),
      },
    })
}

export async function getChannelByLabel(params: {
  workspaceId: string
  label: string
}): Promise<{
  id: string
  label: string
  youtubeChannelId: string
  reportingTimezone: string
  lastCompleteDate: string | null
} | null> {
  const rows = await getDb()
    .select({
      id: channel.id,
      label: channel.label,
      youtubeChannelId: channel.youtubeChannelId,
      reportingTimezone: channel.reportingTimezone,
      lastCompleteDate: syncCheckpoint.lastCompleteDate,
    })
    .from(channel)
    .leftJoin(syncCheckpoint, eq(syncCheckpoint.channelId, channel.id))
    .where(and(eq(channel.workspaceId, params.workspaceId), eq(channel.label, params.label)))
    .limit(1)

  return rows[0] ?? null
}

export { toApiError, ErrorCode }
export const __testing = { describeError, normalizeMetrics, withTransaction }
