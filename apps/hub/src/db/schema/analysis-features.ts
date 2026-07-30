import { sql } from 'drizzle-orm'
import {
  boolean,
  check,
  date,
  foreignKey,
  index,
  integer,
  jsonb,
  numeric,
  pgEnum,
  pgTable,
  text,
  timestamp,
  unique,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

import { analysisRun } from './analysis'
import { video } from './analytics'
import { channel, workspace } from './workspace'

/**
 * QUYẾT ĐỊNH LƯU TRỮ — vì sao chọn HỖN HỢP (typed + EAV có ràng buộc + JSONB)
 *
 * Ba phương án đã cân nhắc:
 *
 * 1. Cột typed cho từng feature (`view_velocity numeric, ctr numeric, ...`).
 *    Truy vấn nhanh và an toàn kiểu, NHƯNG mỗi feature mới là một migration
 *    ALTER TABLE, và ~28 feature × nhiều phiên bản sẽ thành bảng hàng trăm cột
 *    phần lớn NULL. Quan trọng hơn: KHÔNG versioning được — đổi công thức là
 *    viết lại ý nghĩa của toàn bộ dữ liệu lịch sử trong cùng một cột.
 *
 * 2. Một JSONB blob mỗi (subject, run): `{"ctr": 3.2, "views_7d": 900, ...}`.
 *    Linh hoạt nhất, nhưng KHÔNG có ràng buộc nào: sai chính tả tên feature là
 *    một feature mới im lặng. Và các phép cần thiết ở đây — percentile, median,
 *    xếp hạng trong nhóm — trở thành quét toàn bảng rồi tính ngoài SQL.
 *
 * 3. ĐÃ CHỌN — EAV CÓ RÀNG BUỘC: `feature_value` là bảng hẹp với đúng một cột
 *    số, và `feature_version_id` là KHOÁ NGOẠI tới một danh mục ĐÓNG. Đây không
 *    phải "generic feature store không giới hạn" mà đề bài cảnh báo: một feature
 *    không tồn tại trong danh mục thì DB từ chối ghi, nên không gian khoá bị
 *    chặn bởi ràng buộc chứ không bởi quy ước.
 *
 * Vì sao hợp với dữ liệu này: MỌI feature ở Phase 3 đều là SỐ THỰC, nên một cột
 * `numeric` là đủ — không cần cột value theo kiểu. Percentile và median chạy
 * bằng SQL cửa sổ ngay trên bảng hẹp này.
 *
 * JSONB CHỈ dùng ở nơi tải trọng thật sự biến thiên: `evidence`, `metric_values`
 * của observation, và bản thân gói phân tích (vốn LÀ một tài liệu). Những chỗ
 * dùng để LỌC hoặc SẮP XẾP đều là cột typed.
 *
 * `missing_reason` là enum tường minh thay vì để NULL trần: đề bài yêu cầu "lưu
 * lý do thiếu, không bịa giá trị", và NULL trần không phân biệt được "chưa đủ
 * tuổi", "YouTube không cấp chỉ số này" và "mẫu quá nhỏ".
 */

export const featureUnitEnum = pgEnum('feature_unit', [
  'COUNT',
  'RATIO',
  'PERCENT',
  'SECONDS',
  'MINUTES',
  'PER_DAY',
  'ZSCORE',
  'RANK',
  'HOUR_OF_DAY',
  'DAY_OF_WEEK',
])

/** Chiều "tốt" của feature — dùng để xếp hạng, không dùng để kết luận nhân quả. */
export const featureDirectionEnum = pgEnum('feature_direction', [
  'HIGHER_IS_BETTER',
  'LOWER_IS_BETTER',
  'NEUTRAL',
])

/**
 * Vì sao một feature KHÔNG tính được. Bịa số 0 vào những ca này sẽ làm mọi
 * median, percentile và so sánh lệch đi mà không ai thấy.
 */
export const missingReasonEnum = pgEnum('missing_reason', [
  'METRIC_NOT_PROVIDED',   // YouTube không cấp chỉ số này cho kênh
  'INSUFFICIENT_AGE',      // video chưa đủ tuổi cho cửa sổ N ngày
  'INSUFFICIENT_SAMPLE',   // nhóm so sánh quá ít phần tử
  'NO_METRIC_ROWS',        // không có hàng chỉ số nào trong cửa sổ
  'DIVISION_BY_ZERO',      // mẫu số bằng 0 (vd CTR khi impressions = 0)
  'DEPENDENCY_MISSING',    // feature phụ thuộc một feature khác đang thiếu
  'OUTSIDE_WINDOW',        // video xuất bản ngoài cửa sổ phân tích
])

export const featureSubjectTypeEnum = pgEnum('feature_subject_type', ['CHANNEL', 'VIDEO'])

export const observationKindEnum = pgEnum('observation_kind', [
  'TOP_PERFORMER',
  'BOTTOM_PERFORMER',
  'HIGH_RETENTION_LOW_REACH',
  'HIGH_REACH_LOW_RETENTION',
  'HIGH_CTR_LOW_WATCH',
  'LOW_CTR_HIGH_RETENTION',
  'SUBSCRIBER_EFFICIENT',
  'COHORT_TREND',
  'FORMAT_COMPARISON',
  'PUBLISH_TIME_COMPARISON',
  'CHANNEL_TREND_CHANGE',
  'ANOMALY',
  'DATA_QUALITY',
  'HYPOTHESIS_CANDIDATE',
])

export const observationPolarityEnum = pgEnum('observation_polarity', [
  'POSITIVE',
  'NEGATIVE',
  'NEUTRAL',
])

export const baselineKindEnum = pgEnum('baseline_kind', [
  'CHANNEL_ALL',
  'CHANNEL_FORMAT',
  'RECENT_WINDOW',
  'MATURE_VIDEOS',
  'COHORT',
  'NONE',
])

export const confidenceBandEnum = pgEnum('confidence_band', ['HIGH', 'MEDIUM', 'LOW'])

export const cohortKindEnum = pgEnum('cohort_kind', [
  'PUBLISH_FORTNIGHT',
  'FORMAT',
  'DURATION_BUCKET',
  'PUBLISH_HOUR_BUCKET',
  'PUBLISH_WEEKDAY',
])

export const anomalyKindEnum = pgEnum('anomaly_kind', [
  'VIEW_SPIKE',
  'VIEW_COLLAPSE',
  'RETENTION_OUTLIER',
  'CTR_OUTLIER',
  'ENGAGEMENT_OUTLIER',
  'INCONSISTENT_VALUE',
  'SUSPICIOUS_VALUE',
])

// --- Danh mục feature ------------------------------------------------------

export const featureDefinition = pgTable(
  'feature_definition',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    key: text('key').notNull(),
    label: text('label').notNull(),
    description: text('description').notNull(),
    unit: featureUnitEnum('unit').notNull(),
    direction: featureDirectionEnum('direction').notNull().default('NEUTRAL'),
    subjectType: featureSubjectTypeEnum('subject_type').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('feature_definition_key_key').on(t.key),
    check('feature_definition_key_format', sql`${t.key} ~ '^[a-z][a-z0-9_]{2,63}$'`),
  ],
)

/**
 * Phiên bản của công thức.
 *
 * Đổi công thức PHẢI tạo hàng mới ở đây, không sửa hàng cũ (trigger chặn) — nếu
 * không thì một kết quả tính từ tháng trước sẽ mang ý nghĩa của công thức hôm
 * nay, và mọi so sánh theo thời gian trở thành vô nghĩa.
 */
export const featureVersion = pgTable(
  'feature_version',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    definitionId: uuid('definition_id')
      .notNull()
      .references(() => featureDefinition.id, { onDelete: 'restrict' }),
    version: text('version').notNull(),
    /** Công thức viết dạng người đọc được — đi vào cả gói gửi cho Cursor. */
    formula: text('formula').notNull(),
    /** Tham số/ngưỡng của phiên bản này. */
    spec: jsonb('spec').notNull().default(sql`'{}'::jsonb`),
    /** Chỉ số YouTube bắt buộc phải có; thiếu thì feature = MISSING. */
    requiredMetrics: text('required_metrics').array().notNull().default(sql`ARRAY[]::text[]`),
    codeHash: text('code_hash'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('feature_version_def_version_key').on(t.definitionId, t.version),
    unique('feature_version_id_def_key').on(t.id, t.definitionId),
  ],
)

/**
 * Giá trị feature.
 *
 * Bất biến: KHÔNG có UPDATE. Tính lại thì tạo `analysis_run` mới; kết quả cũ
 * giữ nguyên (đề bài: "append-only hoặc có revision, không ghi đè").
 */
export const featureValue = pgTable(
  'feature_value',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    analysisRunId: uuid('analysis_run_id')
      .notNull()
      .references(() => analysisRun.id, { onDelete: 'restrict' }),
    featureVersionId: uuid('feature_version_id')
      .notNull()
      .references(() => featureVersion.id, { onDelete: 'restrict' }),

    subjectType: featureSubjectTypeEnum('subject_type').notNull(),
    channelId: uuid('channel_id').notNull(),
    /** NULL khi subjectType = CHANNEL. */
    videoId: uuid('video_id'),

    windowStart: date('window_start').notNull(),
    windowEnd: date('window_end').notNull(),

    /** Đúng MỘT trong hai: có giá trị, hoặc có lý do thiếu. */
    numericValue: numeric('numeric_value', { precision: 20, scale: 6 }),
    missingReason: missingReasonEnum('missing_reason'),
    /** Số hàng dữ liệu đã dùng để tính — cơ sở đánh giá độ tin cậy. */
    sampleSize: integer('sample_size'),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'feature_value_channel_workspace_fk',
    }).onDelete('restrict'),
    // Khoá ngoại GHÉP tới analysis_run trên CẢ BA cột (run, workspace, channel).
    //
    // Chỉ neo (run, workspace) là chưa đủ: trong cùng một workspace, một kết quả
    // vẫn khai được kênh B trong khi thuộc lần chạy của kênh A. Neo đủ ba cột
    // khiến nguồn gốc phân tích không thể mâu thuẫn nội tại.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'feature_value_run_workspace_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.videoId, t.workspaceId],
      foreignColumns: [video.id, video.workspaceId],
      name: 'feature_value_video_workspace_fk',
    }).onDelete('restrict'),
    // Một feature chỉ có một giá trị cho mỗi chủ thể trong mỗi lần chạy.
    uniqueIndex('feature_value_run_feature_subject_key').on(
      t.analysisRunId,
      t.featureVersionId,
      t.subjectType,
      t.channelId,
      t.videoId,
    ),
    index('feature_value_run_idx').on(t.analysisRunId),
    index('feature_value_feature_idx').on(t.featureVersionId),
    // "Có giá trị" và "thiếu" loại trừ nhau -- đây là ràng buộc khiến việc bịa
    // số 0 cho dữ liệu thiếu trở thành bất khả thi ở tầng DB.
    check(
      'feature_value_exactly_one_of_value_or_reason',
      sql`(${t.numericValue} IS NULL) <> (${t.missingReason} IS NULL)`,
    ),
    check(
      'feature_value_subject_consistency',
      sql`(${t.subjectType} = 'VIDEO') = (${t.videoId} IS NOT NULL)`,
    ),
    check('feature_value_window_order', sql`${t.windowEnd} >= ${t.windowStart}`),
    check(
      'feature_value_sample_nonneg',
      sql`${t.sampleSize} IS NULL OR ${t.sampleSize} >= 0`,
    ),
  ],
)

// --- Quan sát tất định ------------------------------------------------------

export const deterministicObservation = pgTable(
  'deterministic_observation',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    analysisRunId: uuid('analysis_run_id')
      .notNull()
      .references(() => analysisRun.id, { onDelete: 'restrict' }),

    kind: observationKindEnum('kind').notNull(),
    polarity: observationPolarityEnum('polarity').notNull().default('NEUTRAL'),
    channelId: uuid('channel_id').notNull(),
    videoId: uuid('video_id'),

    /** Câu mô tả THUẦN MÔ TẢ, không suy luận nhân quả. */
    statement: text('statement').notNull(),

    /** Các chỉ số liên quan: {"views_7d": 900, "ctr": 3.1}. */
    metricValues: jsonb('metric_values').notNull().default(sql`'{}'::jsonb`),
    baselineKind: baselineKindEnum('baseline_kind').notNull().default('NONE'),
    baselineValue: numeric('baseline_value', { precision: 20, scale: 6 }),
    observedValue: numeric('observed_value', { precision: 20, scale: 6 }),
    deltaRatio: numeric('delta_ratio', { precision: 12, scale: 6 }),
    percentile: numeric('percentile', { precision: 6, scale: 3 }),

    windowStart: date('window_start').notNull(),
    windowEnd: date('window_end').notNull(),

    confidence: numeric('confidence', { precision: 5, scale: 4 }).notNull(),
    confidenceBand: confidenceBandEnum('confidence_band').notNull(),
    sampleSize: integer('sample_size'),

    /** Điều KHÔNG kết luận được từ quan sát này. */
    limitations: jsonb('limitations').notNull().default(sql`'[]'::jsonb`),

    /**
     * Giả thuyết CHƯA kiểm chứng. Bắt buộc `hypothesisQuestion` khi bật, và
     * `statement` vẫn phải thuần mô tả — chính chỗ này ngăn tầng tất định
     * tuyên bố nhân quả.
     */
    isHypothesis: boolean('is_hypothesis').notNull().default(false),
    /** Câu HỎI cần kiểm chứng — bắt buộc khi isHypothesis = true. */
    hypothesisQuestion: text('hypothesis_question'),

    /** Thứ tự ổn định để cùng input cho ra cùng gói và cùng hash. */
    rankScore: numeric('rank_score', { precision: 12, scale: 6 }).notNull().default('0'),
    orderKey: text('order_key').notNull(),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'observation_channel_workspace_fk',
    }).onDelete('restrict'),
    // Khoá ngoại GHÉP tới analysis_run trên CẢ BA cột (run, workspace, channel).
    //
    // Chỉ neo (run, workspace) là chưa đủ: trong cùng một workspace, một kết quả
    // vẫn khai được kênh B trong khi thuộc lần chạy của kênh A. Neo đủ ba cột
    // khiến nguồn gốc phân tích không thể mâu thuẫn nội tại.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'observation_run_workspace_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.videoId, t.workspaceId],
      foreignColumns: [video.id, video.workspaceId],
      name: 'observation_video_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('observation_run_order_key').on(t.analysisRunId, t.orderKey),
    index('observation_run_kind_idx').on(t.analysisRunId, t.kind),
    check(
      'observation_confidence_range',
      sql`${t.confidence} >= 0 AND ${t.confidence} <= 1`,
    ),
    check(
      'observation_percentile_range',
      sql`${t.percentile} IS NULL OR (${t.percentile} >= 0 AND ${t.percentile} <= 100)`,
    ),
    check('observation_window_order', sql`${t.windowEnd} >= ${t.windowStart}`),
    // Giả thuyết BẮT BUỘC phải kèm câu hỏi cần kiểm chứng. Không có ràng buộc
    // này thì một suy đoán nhân quả có thể lọt vào dưới dạng "quan sát".
    check(
      'observation_hypothesis_needs_question',
      sql`${t.isHypothesis} = false OR ${t.hypothesisQuestion} IS NOT NULL`,
    ),
  ],
)

/** Con trỏ tới dữ liệu gốc chống lưng cho một quan sát. */
export const evidenceReference = pgTable(
  'evidence_reference',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    observationId: uuid('observation_id')
      .notNull()
      .references(() => deterministicObservation.id, { onDelete: 'restrict' }),
    /** VIDEO | VIDEO_DAILY_METRIC | CHANNEL_DAILY_METRIC | FEATURE_VALUE | COHORT_SUMMARY */
    refType: text('ref_type').notNull(),
    refId: uuid('ref_id'),
    /** Khoá tự nhiên khi ref không phải uuid (vd "video:abc123,date:2026-07-01"). */
    refKey: text('ref_key'),
    detail: jsonb('detail').notNull().default(sql`'{}'::jsonb`),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    index('evidence_observation_idx').on(t.observationId),
    check('evidence_has_target', sql`${t.refId} IS NOT NULL OR ${t.refKey} IS NOT NULL`),
  ],
)

// --- Cohort, bất thường, chất lượng -----------------------------------------

export const cohortSummary = pgTable(
  'cohort_summary',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    analysisRunId: uuid('analysis_run_id')
      .notNull()
      .references(() => analysisRun.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),

    kind: cohortKindEnum('kind').notNull(),
    /** vd "2026-07-14..2026-07-27", "SHORT", "hour_18_21". */
    cohortKey: text('cohort_key').notNull(),
    videoCount: integer('video_count').notNull(),

    /**
     * Dùng MEDIAN và IQR chứ không dùng mean/stddev: phân phối lượt xem trên
     * YouTube lệch rất mạnh, một video viral sẽ kéo trung bình đi và làm mọi so
     * sánh cohort vô nghĩa.
     */
    medianViews: numeric('median_views', { precision: 20, scale: 4 }),
    p25Views: numeric('p25_views', { precision: 20, scale: 4 }),
    p75Views: numeric('p75_views', { precision: 20, scale: 4 }),
    medianAvgViewPercentage: numeric('median_avg_view_percentage', { precision: 10, scale: 4 }),
    medianAvgViewDuration: numeric('median_avg_view_duration', { precision: 12, scale: 3 }),
    medianEngagementRate: numeric('median_engagement_rate', { precision: 12, scale: 6 }),
    medianSubsPerThousandViews: numeric('median_subs_per_thousand_views', { precision: 12, scale: 6 }),

    windowStart: date('window_start').notNull(),
    windowEnd: date('window_end').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'cohort_channel_workspace_fk',
    }).onDelete('restrict'),
    // Khoá ngoại GHÉP tới analysis_run trên CẢ BA cột (run, workspace, channel).
    //
    // Chỉ neo (run, workspace) là chưa đủ: trong cùng một workspace, một kết quả
    // vẫn khai được kênh B trong khi thuộc lần chạy của kênh A. Neo đủ ba cột
    // khiến nguồn gốc phân tích không thể mâu thuẫn nội tại.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'cohort_run_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('cohort_run_channel_kind_key').on(t.analysisRunId, t.channelId, t.kind, t.cohortKey),
    check('cohort_video_count_positive', sql`${t.videoCount} >= 0`),
  ],
)

export const anomaly = pgTable(
  'anomaly',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    analysisRunId: uuid('analysis_run_id')
      .notNull()
      .references(() => analysisRun.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),
    videoId: uuid('video_id'),

    kind: anomalyKindEnum('kind').notNull(),
    /** Tên phương pháp, vd "modified_zscore_mad". */
    method: text('method').notNull(),
    /** z hiệu chỉnh theo MAD; dấu cho biết hướng lệch. */
    score: numeric('score', { precision: 12, scale: 6 }).notNull(),
    threshold: numeric('threshold', { precision: 12, scale: 6 }).notNull(),
    observedValue: numeric('observed_value', { precision: 20, scale: 6 }).notNull(),
    medianValue: numeric('median_value', { precision: 20, scale: 6 }).notNull(),
    madValue: numeric('mad_value', { precision: 20, scale: 6 }),
    sampleSize: integer('sample_size').notNull(),
    metricKey: text('metric_key').notNull(),
    context: jsonb('context').notNull().default(sql`'{}'::jsonb`),

    windowStart: date('window_start').notNull(),
    windowEnd: date('window_end').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'anomaly_channel_workspace_fk',
    }).onDelete('restrict'),
    // Khoá ngoại GHÉP tới analysis_run trên CẢ BA cột (run, workspace, channel).
    //
    // Chỉ neo (run, workspace) là chưa đủ: trong cùng một workspace, một kết quả
    // vẫn khai được kênh B trong khi thuộc lần chạy của kênh A. Neo đủ ba cột
    // khiến nguồn gốc phân tích không thể mâu thuẫn nội tại.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'anomaly_run_workspace_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.videoId, t.workspaceId],
      foreignColumns: [video.id, video.workspaceId],
      name: 'anomaly_video_workspace_fk',
    }).onDelete('restrict'),
    index('anomaly_run_idx').on(t.analysisRunId),
    check('anomaly_sample_size_min', sql`${t.sampleSize} >= 0`),
  ],
)

/** Chất lượng và độ đầy đủ dữ liệu của một lần chạy phân tích. */
export const analysisQuality = pgTable(
  'analysis_quality',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    analysisRunId: uuid('analysis_run_id')
      .notNull()
      .references(() => analysisRun.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),

    videosTotal: integer('videos_total').notNull(),
    videosWithMetrics: integer('videos_with_metrics').notNull(),
    videosImmature: integer('videos_immature').notNull(),
    metricRows: integer('metric_rows').notNull(),
    expectedDates: integer('expected_dates').notNull(),
    observedDates: integer('observed_dates').notNull(),
    missingDates: text('missing_dates').array().notNull().default(sql`ARRAY[]::text[]`),

    /** Tỉ lệ 0..1 cho từng chỉ số: {"views":1,"impressions":0}. */
    metricCoverage: jsonb('metric_coverage').notNull().default(sql`'{}'::jsonb`),
    /** Số hàng bị YouTube sửa lại — dấu hiệu dữ liệu đến trễ. */
    revisedRows: integer('revised_rows').notNull().default(0),
    /** Lần sync gần nhất có lỗ hổng hay không. */
    hasSyncGaps: boolean('has_sync_gaps').notNull().default(false),

    confidence: numeric('confidence', { precision: 5, scale: 4 }).notNull(),
    confidenceBand: confidenceBandEnum('confidence_band').notNull(),
    limitations: jsonb('limitations').notNull().default(sql`'[]'::jsonb`),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'analysis_quality_channel_workspace_fk',
    }).onDelete('restrict'),
    // Khoá ngoại GHÉP tới analysis_run trên CẢ BA cột (run, workspace, channel).
    //
    // Chỉ neo (run, workspace) là chưa đủ: trong cùng một workspace, một kết quả
    // vẫn khai được kênh B trong khi thuộc lần chạy của kênh A. Neo đủ ba cột
    // khiến nguồn gốc phân tích không thể mâu thuẫn nội tại.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'analysis_quality_run_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('analysis_quality_run_channel_key').on(t.analysisRunId, t.channelId),
    check('analysis_quality_confidence_range', sql`${t.confidence} >= 0 AND ${t.confidence} <= 1`),
  ],
)

/**
 * Gói bằng chứng gọn gửi cho Cursor CLI.
 *
 * `payload` là JSONB vì nó THỰC SỰ là một tài liệu có cấu trúc lồng nhau, và
 * nó được đọc nguyên khối chứ không truy vấn theo trường. `payloadHash` khoá
 * tính tất định: cùng input phải cho cùng hash.
 */
export const analysisPackage = pgTable(
  'analysis_package',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    analysisRunId: uuid('analysis_run_id')
      .notNull()
      .references(() => analysisRun.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),

    schemaVersion: text('schema_version').notNull(),
    payload: jsonb('payload').notNull(),
    payloadHash: text('payload_hash').notNull(),

    /** Số liệu chứng minh mức nén trước khi gọi LLM. */
    packageBytes: integer('package_bytes').notNull(),
    rawInputBytes: integer('raw_input_bytes').notNull(),
    reductionPercent: numeric('reduction_percent', { precision: 6, scale: 3 }).notNull(),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'analysis_package_channel_workspace_fk',
    }).onDelete('restrict'),
    // Khoá ngoại GHÉP tới analysis_run trên CẢ BA cột (run, workspace, channel).
    //
    // Chỉ neo (run, workspace) là chưa đủ: trong cùng một workspace, một kết quả
    // vẫn khai được kênh B trong khi thuộc lần chạy của kênh A. Neo đủ ba cột
    // khiến nguồn gốc phân tích không thể mâu thuẫn nội tại.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'analysis_package_run_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('analysis_package_run_channel_key').on(t.analysisRunId, t.channelId),
    check('analysis_package_hash_format', sql`${t.payloadHash} ~ '^[0-9a-f]{64}$'`),
    check('analysis_package_bytes_positive', sql`${t.packageBytes} > 0 AND ${t.rawInputBytes} > 0`),
  ],
)
