import { sql } from 'drizzle-orm'
import {
  boolean,
  check,
  date,
  foreignKey,
  index,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  unique,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

import {
  algorithmKindEnum,
  analysisResultKindEnum,
  analysisRunStatusEnum,
  analysisSubjectTypeEnum,
} from './enums'
import { contentRevision } from './content'
import { channel, workspace } from './workspace'

/** Danh mục thuật toán: 'deterministic-analysis', 'cursor-llm-analysis', ... */
export const algorithm = pgTable(
  'algorithm',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    key: text('key').notNull(),
    name: text('name').notNull(),
    kind: algorithmKindEnum('kind').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [uniqueIndex('algorithm_key_key').on(t.key)],
)

/**
 * Phiên bản thuật toán. `spec` giữ tham số/ngưỡng, `codeHash` neo vào đúng bản
 * code đã chạy — nhờ đó một kết quả cũ luôn truy ngược được về logic sinh ra nó
 * kể cả sau khi thuật toán đã đổi.
 */
export const algorithmVersion = pgTable(
  'algorithm_version',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    algorithmId: uuid('algorithm_id')
      .notNull()
      .references(() => algorithm.id, { onDelete: 'restrict' }),
    version: text('version').notNull(),
    spec: jsonb('spec').notNull().default(sql`'{}'::jsonb`),
    codeHash: text('code_hash'),
    isActive: boolean('is_active').notNull().default(true),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('algorithm_version_algo_version_key').on(t.algorithmId, t.version),
    index('algorithm_version_algo_idx').on(t.algorithmId),
  ],
)

/**
 * Một lần chạy phân tích.
 *
 * AC-3 — vì sao `algorithmVersionId` là NOT NULL:
 * PostgreSQL coi các NULL là KHÁC NHAU trong ràng buộc UNIQUE. Nếu cột này
 * nullable (cho audit do người/công cụ ngoài chạy) thì UNIQUE chứa nó sẽ KHÔNG
 * chặn được hai run trùng `run_sequence` — mỗi hàng NULL đều "khác" mọi hàng
 * NULL khác. Cách xử lý: không cho phép NULL, và seed một hàng
 * `algorithm_version` sentinel cho nhánh 'external/human' (xem seed).
 *
 * Tương tự, phạm vi duy nhất dùng `(subjectType, subjectId)` — cả hai NOT NULL
 * — chứ không dùng `content_revision_id` nullable, vì phân tích cấp kênh không
 * có revision nào và sẽ rơi lại đúng cái bẫy NULL ở trên.
 */
export const analysisRun = pgTable(
  'analysis_run',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),

    subjectType: analysisSubjectTypeEnum('subject_type').notNull(),
    subjectId: uuid('subject_id').notNull(),

    /** Chỉ điền khi subjectType = CONTENT_REVISION. Dùng để join thuận tiện. */
    contentRevisionId: uuid('content_revision_id'),

    algorithmId: uuid('algorithm_id')
      .notNull()
      .references(() => algorithm.id, { onDelete: 'restrict' }),
    algorithmVersionId: uuid('algorithm_version_id')
      .notNull()
      .references(() => algorithmVersion.id, { onDelete: 'restrict' }),

    runSequence: integer('run_sequence').notNull(),

    /** sha256 của toàn bộ input đã chuẩn hoá. Cùng input + cùng version = tái lập được. */
    inputHash: text('input_hash').notNull(),

    periodStart: date('period_start').notNull(),
    periodEnd: date('period_end').notNull(),

    status: analysisRunStatusEnum('status').notNull().default('PENDING'),
    startedAt: timestamp('started_at', { withTimezone: true }),
    finishedAt: timestamp('finished_at', { withTimezone: true }),
    error: jsonb('error'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    // Khoá ngoại GHÉP: kênh và revision phải thuộc ĐÚNG workspace mà run khai
    // báo. Khoá ngoại rời nhau sẽ cho phép một run của workspace A trỏ vào dữ
    // liệu của workspace B mà không có gì báo lỗi.
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'analysis_run_channel_workspace_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.contentRevisionId, t.workspaceId],
      foreignColumns: [contentRevision.id, contentRevision.workspaceId],
      name: 'analysis_run_revision_workspace_fk',
    }).onDelete('restrict'),
    // Đích cho khoá ngoại ghép từ llm_execution.
    unique('analysis_run_id_workspace_key').on(t.id, t.workspaceId),
    // Khoá duy nhất KHÔNG chứa cột nullable nào -- đây chính là nội dung AC-3.
    uniqueIndex('analysis_run_sequence_key').on(
      t.subjectType,
      t.subjectId,
      t.algorithmVersionId,
      t.runSequence,
    ),
    index('analysis_run_workspace_idx').on(t.workspaceId),
    index('analysis_run_channel_idx').on(t.channelId),
    index('analysis_run_subject_idx').on(t.subjectType, t.subjectId),
    check('analysis_run_sequence_positive', sql`${t.runSequence} >= 1`),
    check('analysis_run_period_order', sql`${t.periodEnd} >= ${t.periodStart}`),
    check('analysis_run_input_hash_format', sql`${t.inputHash} ~ '^[0-9a-f]{64}$'`),
    // subjectType và contentRevisionId phải nhất quán: phân tích cấp kênh không
    // được mang revision, phân tích cấp revision bắt buộc phải có.
    check(
      'analysis_run_subject_consistency',
      sql`(${t.subjectType} = 'CONTENT_REVISION') = (${t.contentRevisionId} IS NOT NULL)`,
    ),
  ],
)

/**
 * Kết quả có cấu trúc của một lần chạy. `payload` được Zod validate TRƯỚC khi
 * ghi; DB chỉ giữ bản đã hợp lệ. `schemaVersion` cho phép đọc lại payload cũ
 * sau khi schema đã tiến hoá.
 */
export const analysisResult = pgTable(
  'analysis_result',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    /**
     * `restrict` chứ KHÔNG phải cascade: nếu cascade thì xoá một `analysis_run`
     * sẽ xoá luôn kết quả đã ghi, vòng qua trigger bất biến của
     * `analysis_result` — lịch sử so sánh giữa các vòng tinh chỉnh ở Phase 5 bị
     * viết lại phía sau lưng.
     */
    analysisRunId: uuid('analysis_run_id')
      .notNull()
      .references(() => analysisRun.id, { onDelete: 'restrict' }),
    kind: analysisResultKindEnum('kind').notNull(),
    schemaVersion: text('schema_version').notNull(),
    payload: jsonb('payload').notNull(),
    /** sha256 của payload chuẩn hoá — phát hiện sửa đổi sau khi ghi. */
    payloadHash: text('payload_hash').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    // Mỗi run cho ra đúng một kết quả mỗi loại. Chạy lại thì tạo run mới
    // (run_sequence tăng), không ghi đè kết quả cũ -- lịch sử phải giữ nguyên.
    uniqueIndex('analysis_result_run_kind_key').on(t.analysisRunId, t.kind),
    index('analysis_result_run_idx').on(t.analysisRunId),
    // Đích cho khoá ngoại ghép từ llm_execution: một execution chỉ được nhận
    // kết quả THUỘC ĐÚNG run của chính nó.
    unique('analysis_result_id_run_key').on(t.id, t.analysisRunId),
    check('analysis_result_hash_format', sql`${t.payloadHash} ~ '^[0-9a-f]{64}$'`),
  ],
)
