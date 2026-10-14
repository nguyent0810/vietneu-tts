import { sql } from 'drizzle-orm'
import {
  bigint,
  check,
  date,
  foreignKey,
  index,
  integer,
  jsonb,
  numeric,
  pgTable,
  text,
  timestamp,
  unique,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

import { syncRunStatusEnum, videoFormatEnum } from './enums'
import { channel, workspace } from './workspace'

/**
 * Video trên YouTube. `youtubeVideoId` (11 ký tự) là định danh thật và duy
 * nhất toàn cục — một video không thể thuộc hai kênh.
 *
 * `durationSeconds` và `format` lấy từ YouTube Data API chứ không suy đoán:
 * ranh giới Shorts từng đổi (60s rồi 180s), nên suy từ độ dài sẽ sai với dữ
 * liệu cũ. Khi API không nói rõ thì để UNKNOWN, và Phase 3 phải xử lý được
 * UNKNOWN thay vì đoán bừa.
 */
export const video = pgTable(
  'video',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),
    youtubeVideoId: text('youtube_video_id').notNull(),
    title: text('title').notNull(),
    description: text('description'),
    publishedAt: timestamp('published_at', { withTimezone: true }).notNull(),
    durationSeconds: integer('duration_seconds'),
    format: videoFormatEnum('format').notNull().default('UNKNOWN'),
    privacyStatus: text('privacy_status'),
    /** Giờ đăng theo múi giờ báo cáo của kênh — Phase 3 phân tích "giờ đăng". */
    publishedHourLocal: integer('published_hour_local'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'video_channel_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('video_youtube_id_key').on(t.youtubeVideoId),
    unique('video_id_workspace_key').on(t.id, t.workspaceId),
    index('video_channel_published_idx').on(t.channelId, t.publishedAt),
    check('video_youtube_id_format', sql`${t.youtubeVideoId} ~ '^[A-Za-z0-9_-]{11}$'`),
    check(
      'video_duration_nonneg',
      sql`${t.durationSeconds} IS NULL OR ${t.durationSeconds} >= 0`,
    ),
    check(
      'video_hour_range',
      sql`${t.publishedHourLocal} IS NULL OR (${t.publishedHourLocal} >= 0 AND ${t.publishedHourLocal} <= 23)`,
    ),
  ],
)

/**
 * Một lần chạy đồng bộ. Là bản ghi kiểm toán: mỗi lần gọi CLI tạo đúng một
 * hàng, kể cả khi thất bại.
 *
 * AC-4: khi có lỗi giữa chừng, dữ liệu nghiệp vụ được rollback nhưng hàng này
 * PHẢI sống sót ở trạng thái FAILED kèm lỗi — nếu rollback cả transaction thì
 * mất luôn bằng chứng đã chạy gì. Xem `runSync` trong src/lib/sync.
 */
export const syncRun = pgTable(
  'sync_run',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),
    status: syncRunStatusEnum('status').notNull().default('RUNNING'),

    /** Khoảng ngày ĐÃ YÊU CẦU (theo lịch báo cáo của kênh). */
    requestedFrom: date('requested_from').notNull(),
    requestedTo: date('requested_to').notNull(),

    /** Máy worker đã chạy. Chỉ nhãn, KHÔNG BAO GIỜ chứa token. */
    workerLabel: text('worker_label'),

    videosSeen: integer('videos_seen').notNull().default(0),
    videosUpserted: integer('videos_upserted').notNull().default(0),
    videoMetricRowsUpserted: integer('video_metric_rows_upserted').notNull().default(0),
    channelMetricRowsUpserted: integer('channel_metric_rows_upserted').notNull().default(0),
    /** Số hàng đã có nhưng bị YouTube sửa lại số liệu (dữ liệu đến trễ). */
    metricRowsRevised: integer('metric_rows_revised').notNull().default(0),

    /** Cảnh báo không chặn: ngày thiếu dữ liệu, chỉ số vắng mặt... */
    warnings: jsonb('warnings').notNull().default(sql`'[]'::jsonb`),
    error: jsonb('error'),

    startedAt: timestamp('started_at', { withTimezone: true }).notNull().defaultNow(),
    finishedAt: timestamp('finished_at', { withTimezone: true }),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'sync_run_channel_workspace_fk',
    }).onDelete('restrict'),
    index('sync_run_channel_started_idx').on(t.channelId, t.startedAt),
    unique('sync_run_id_workspace_key').on(t.id, t.workspaceId),
    check('sync_run_range_order', sql`${t.requestedTo} >= ${t.requestedFrom}`),
    // Đã kết thúc thì phải có finished_at; FAILED thì phải nói rõ lỗi.
    check(
      'sync_run_finished_consistency',
      sql`(${t.status} = 'RUNNING') = (${t.finishedAt} IS NULL)`,
    ),
    check('sync_run_failed_has_error', sql`${t.status} <> 'FAILED' OR ${t.error} IS NOT NULL`),
  ],
)

/**
 * Điểm nối tiếp cho đồng bộ tăng dần, mỗi kênh một hàng.
 *
 * `lastCompleteDate` là ngày cuối được coi là ỔN ĐỊNH. YouTube còn sửa số liệu
 * trong 48-72h, nên lần chạy sau vẫn phải lấy lại một cửa sổ lùi kể từ mốc này
 * — xem `LOOKBACK_DAYS`. Nếu chỉ lấy từ mốc trở đi thì mọi chỉnh sửa muộn của
 * YouTube sẽ không bao giờ vào database.
 */
export const syncCheckpoint = pgTable(
  'sync_checkpoint',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),
    lastCompleteDate: date('last_complete_date'),
    lastSyncRunId: uuid('last_sync_run_id'),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'sync_checkpoint_channel_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('sync_checkpoint_channel_key').on(t.channelId),
  ],
)

/**
 * Cột chỉ số dùng chung cho cả cấp video và cấp kênh.
 *
 * TẤT CẢ đều nullable, có chủ đích: YouTube Analytics chỉ trả `impressions` /
 * `impressionClickThroughRate` cho một số truy vấn và một số kênh. Ghi 0 khi
 * thiếu sẽ là BỊA SỐ LIỆU — Phase 3 phân biệt "bằng 0" với "không có dữ liệu"
 * để tính độ đầy đủ và độ tin cậy.
 */
const metricColumns = {
  views: bigint('views', { mode: 'number' }),
  estimatedMinutesWatched: numeric('estimated_minutes_watched', { precision: 16, scale: 4 }),
  averageViewDurationSeconds: numeric('average_view_duration_seconds', { precision: 12, scale: 3 }),
  // precision 12 chứ không phải 8: numeric(8,4) chỉ chứa tới 9999.9999, mà dữ
  // liệu THẬT đã tràn — một Short rất ngắn được xem lặp có thể cho phần trăm
  // xem lớn hơn thế nhiều. Lỗi này chỉ lộ ra nhờ log lỗi server thêm ở Phase 2;
  // trước đó nó chỉ là một 500 không dấu vết.
  averageViewPercentage: numeric('average_view_percentage', { precision: 12, scale: 4 }),
  impressions: bigint('impressions', { mode: 'number' }),
  impressionCtr: numeric('impression_ctr', { precision: 12, scale: 4 }),
  likes: integer('likes'),
  dislikes: integer('dislikes'),
  comments: integer('comments'),
  shares: integer('shares'),
  subscribersGained: integer('subscribers_gained'),
  subscribersLost: integer('subscribers_lost'),
}

/**
 * Chỉ số theo ngày của từng video.
 *
 * `date` là NGÀY BÁO CÁO của YouTube theo múi giờ của kênh (thường là
 * America/Los_Angeles), KHÔNG phải ngày UTC. Vì thế cột là `date` chứ không
 * phải timestamp: quy đổi sang timestamp sẽ ngầm gắn một múi giờ và làm lệch
 * ranh giới ngày.
 */
export const videoDailyMetric = pgTable(
  'video_daily_metric',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    videoId: uuid('video_id').notNull(),
    date: date('date').notNull(),
    ...metricColumns,
    /** Lần chạy đồng bộ ghi giá trị hiện tại — truy nguồn được từng con số. */
    lastSyncRunId: uuid('last_sync_run_id'),
    /** Số lần YouTube sửa lại số liệu của hàng này sau khi đã ghi. */
    revisionCount: integer('revision_count').notNull().default(0),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.videoId, t.workspaceId],
      foreignColumns: [video.id, video.workspaceId],
      name: 'video_daily_metric_video_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('video_daily_metric_video_date_key').on(t.videoId, t.date),
    index('video_daily_metric_date_idx').on(t.date),
    check('video_daily_metric_views_nonneg', sql`${t.views} IS NULL OR ${t.views} >= 0`),
    check(
      'video_daily_metric_ctr_range',
      sql`${t.impressionCtr} IS NULL OR (${t.impressionCtr} >= 0 AND ${t.impressionCtr} <= 100)`,
    ),
    // KHÔNG chặn trên ở 100: người xem tua lại nên phần trăm xem trung bình
    // vượt 100 là dữ liệu THẬT của YouTube, không phải lỗi. Chặn ở 100 sẽ loại
    // bỏ đúng những video giữ chân tốt nhất.
    check(
      'video_daily_metric_pct_range',
      sql`${t.averageViewPercentage} IS NULL OR ${t.averageViewPercentage} >= 0`,
    ),
  ],
)

/**
 * Lịch sử SCD-2 của chỉ số video.
 *
 * YouTube sửa lại số liệu trong 48-72h sau khi công bố. Nếu chỉ UPSERT đè lên
 * thì một phân tích chạy hôm qua không còn tái lập được, vì con số nó đã đọc
 * đã biến mất. Bảng này giữ GIÁ TRỊ CŨ mỗi lần bị đè, do trigger ghi tự động
 * nên không đường ghi nào bỏ sót được.
 */
export const videoDailyMetricHistory = pgTable(
  'video_daily_metric_history',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    metricId: uuid('metric_id').notNull(),
    videoId: uuid('video_id').notNull(),
    date: date('date').notNull(),
    ...metricColumns,
    /** Lần chạy đã ghi giá trị CŨ này. */
    supersededSyncRunId: uuid('superseded_sync_run_id'),
    /** Thời điểm giá trị này bị thay thế. */
    supersededAt: timestamp('superseded_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    index('video_daily_metric_history_metric_idx').on(t.metricId),
    index('video_daily_metric_history_video_date_idx').on(t.videoId, t.date),
  ],
)

/** Chỉ số theo ngày ở cấp kênh (tổng hợp, không phải tổng các video). */
export const channelDailyMetric = pgTable(
  'channel_daily_metric',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),
    date: date('date').notNull(),
    ...metricColumns,
    lastSyncRunId: uuid('last_sync_run_id'),
    revisionCount: integer('revision_count').notNull().default(0),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'channel_daily_metric_channel_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('channel_daily_metric_channel_date_key').on(t.channelId, t.date),
    index('channel_daily_metric_date_idx').on(t.date),
    check('channel_daily_metric_views_nonneg', sql`${t.views} IS NULL OR ${t.views} >= 0`),
  ],
)

/**
 * Nguồn gốc lời gọi API.
 *
 * Lưu tham số truy vấn + tiêu đề cột + số hàng + hash phản hồi, KHÔNG lưu
 * access token và KHÔNG lưu header xác thực. Nhờ đó tái dựng được đúng truy
 * vấn đã chạy để đối chiếu khi số liệu trông đáng ngờ, mà không biến bảng này
 * thành nơi chứa credential.
 */
export const analyticsApiCall = pgTable(
  'analytics_api_call',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    syncRunId: uuid('sync_run_id').notNull(),
    endpoint: text('endpoint').notNull(),
    /** Tham số truy vấn đã lọc — ids/metrics/dimensions/startDate/endDate. */
    requestParams: jsonb('request_params').notNull(),
    httpStatus: integer('http_status'),
    rowCount: integer('row_count'),
    /** sha256 của thân phản hồi — phát hiện dữ liệu đổi giữa hai lần gọi. */
    responseHash: text('response_hash'),
    columnHeaders: jsonb('column_headers'),
    durationMs: integer('duration_ms'),
    fetchedAt: timestamp('fetched_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    index('analytics_api_call_sync_run_idx').on(t.syncRunId),
    check(
      'analytics_api_call_hash_format',
      sql`${t.responseHash} IS NULL OR ${t.responseHash} ~ '^[0-9a-f]{64}$'`,
    ),
  ],
)
