import { sql } from 'drizzle-orm'
import {
  boolean,
  check,
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
import { analysisPackage } from './analysis-features'
import { llmExecution } from './llm'
import { channel, workspace } from './workspace'

/**
 * Phân loại THẤT BẠI của một lần chạy Cursor.
 *
 * Chỉ những loại KỸ THUẬT mới được retry. `UNSUPPORTED_CLAIM` và
 * `EVIDENCE_UNRESOLVED` là thất bại về NỘI DUNG — retry chúng nghĩa là chạy lại
 * cho tới khi mô hình nói điều mình muốn nghe, và đó chính xác là điều đề bài
 * cấm ("không tự động retry chỉ vì kết luận không như ý").
 */
export const cursorFailureClassEnum = pgEnum('cursor_failure_class', [
  'NONE',
  'INVALID_JSON',
  'PROSE_OUTSIDE_JSON',
  'SCHEMA_MISMATCH',
  'MISSING_REQUIRED_FIELD',
  'TRUNCATED_OUTPUT',
  'UNSUPPORTED_SCHEMA_VERSION',
  'CLI_NONZERO_EXIT',
  'CLI_TIMEOUT',
  'OUTPUT_TOO_LARGE',
  // Không retry được — hỏng về nội dung, không phải kỹ thuật.
  'UNSUPPORTED_CLAIM',
  'EVIDENCE_UNRESOLVED',
])

/** Retry được hay không. Dùng ở cả code lẫn tài liệu để không lệch nhau. */
export const RETRYABLE_FAILURE_CLASSES = [
  'INVALID_JSON',
  'PROSE_OUTSIDE_JSON',
  'SCHEMA_MISMATCH',
  'MISSING_REQUIRED_FIELD',
  'TRUNCATED_OUTPUT',
  'UNSUPPORTED_SCHEMA_VERSION',
  'CLI_NONZERO_EXIT',
  'CLI_TIMEOUT',
  'OUTPUT_TOO_LARGE',
] as const

export const validationSeverityEnum = pgEnum('validation_severity', [
  'BLOCKER',
  'HIGH',
  'MEDIUM',
  'LOW',
])

/**
 * Báo cáo kiểm định cho một lần chạy Cursor.
 *
 * Lưu TÁCH RIÊNG khỏi output gốc, theo đúng yêu cầu: "không bao giờ âm thầm
 * viết lại phản hồi của Cursor rồi trình bày như bản gốc". Output thô nằm ở
 * `llm_execution`/`analysis_result`; mọi phán xét về nó nằm ở đây.
 */
export const analysisValidation = pgTable(
  'analysis_validation',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    llmExecutionId: uuid('llm_execution_id').notNull(),
    channelId: uuid('channel_id').notNull(),
    /** Neo về lần phân tích, để kênh và execution không thể lệch nhau. */
    analysisRunId: uuid('analysis_run_id').notNull(),

    passed: boolean('passed').notNull(),
    failureClass: cursorFailureClassEnum('failure_class').notNull().default('NONE'),

    /** Từng nhóm kiểm định, mỗi phần tử {rule, severity, message, path}. */
    structuralIssues: jsonb('structural_issues').notNull().default(sql`'[]'::jsonb`),
    evidenceIssues: jsonb('evidence_issues').notNull().default(sql`'[]'::jsonb`),
    claimIssues: jsonb('claim_issues').notNull().default(sql`'[]'::jsonb`),
    qualityIssues: jsonb('quality_issues').notNull().default(sql`'[]'::jsonb`),

    /** Tỉ lệ evidenceId giải được về gói đầu vào, 0..1. */
    evidenceResolutionRate: numeric('evidence_resolution_rate', { precision: 5, scale: 4 }),
    totalEvidenceRefs: integer('total_evidence_refs').notNull().default(0),
    unresolvedEvidenceRefs: integer('unresolved_evidence_refs').notNull().default(0),

    causalViolations: integer('causal_violations').notNull().default(0),
    ctrViolations: integer('ctr_violations').notNull().default(0),
    unsupportedMetricViolations: integer('unsupported_metric_violations').notNull().default(0),

    findingCount: integer('finding_count').notNull().default(0),
    hypothesisCount: integer('hypothesis_count').notNull().default(0),
    recommendationCount: integer('recommendation_count').notNull().default(0),
    experimentCount: integer('experiment_count').notNull().default(0),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.llmExecutionId, t.workspaceId, t.analysisRunId],
      foreignColumns: [llmExecution.id, llmExecution.workspaceId, llmExecution.analysisRunId],
      name: 'analysis_validation_execution_run_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'analysis_validation_channel_workspace_fk',
    }).onDelete('restrict'),
    // Kênh phải là kênh CỦA LẦN CHẠY đó, không phải một kênh bất kỳ cùng workspace.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'analysis_validation_run_channel_fk',
    }).onDelete('restrict'),
    uniqueIndex('analysis_validation_execution_key').on(t.llmExecutionId),
    check(
      'analysis_validation_rate_range',
      sql`${t.evidenceResolutionRate} IS NULL OR (${t.evidenceResolutionRate} >= 0 AND ${t.evidenceResolutionRate} <= 1)`,
    ),
  ],
)

/**
 * Một YÊU CẦU phân tích: gắn đúng một gói bằng chứng với đúng một phiên bản
 * prompt. Các lần chạy Cursor (kể cả retry và các lần lặp lại để đo độ ổn định)
 * đều treo vào đây.
 *
 * Tách khỏi `llm_execution` vì "cùng gói + cùng prompt chạy nhiều lần" là yêu
 * cầu tường minh của đề bài, và các lần chạy đó không được ghi đè nhau.
 */
export const cursorAnalysisRequest = pgTable(
  'cursor_analysis_request',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),
    analysisRunId: uuid('analysis_run_id').notNull(),
    analysisPackageId: uuid('analysis_package_id').notNull(),

    /** Băm nội dung gói — neo kết quả vào đúng bằng chứng đã dùng. */
    packageHash: text('package_hash').notNull(),
    promptRevisionId: uuid('prompt_revision_id').notNull(),
    /** Băm prompt ĐÃ RENDER, không phải template. */
    promptHash: text('prompt_hash').notNull(),
    promptBytes: integer('prompt_bytes').notNull(),

    /** Phần bằng chứng bị lược bỏ do giới hạn kích thước, kèm lý do. */
    omissions: jsonb('omissions').notNull().default(sql`'[]'::jsonb`),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'cursor_request_channel_workspace_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'cursor_request_run_workspace_channel_fk',
    }).onDelete('restrict'),
    // Gói phải thuộc ĐÚNG lần phân tích và ĐÚNG kênh của yêu cầu này.
    //
    // Ràng buộc cũ chỉ nối gói với workspace, nên trong cùng một workspace vẫn
    // ghi được "lần chạy B của kênh B đã phân tích gói của kênh A". Mọi khoá
    // ngoại hợp lệ, nguồn gốc lưu lại thì sai.
    foreignKey({
      columns: [t.analysisPackageId, t.workspaceId, t.analysisRunId, t.channelId],
      foreignColumns: [
        analysisPackage.id,
        analysisPackage.workspaceId,
        analysisPackage.analysisRunId,
        analysisPackage.channelId,
      ],
      name: 'cursor_request_package_lineage_fk',
    }).onDelete('restrict'),
    unique('cursor_request_id_workspace_key').on(t.id, t.workspaceId),
    // Đích cho khoá ngoại phức hợp từ kết quả và bản kê.
    unique('cursor_request_id_ws_run_channel_key').on(
      t.id,
      t.workspaceId,
      t.analysisRunId,
      t.channelId,
    ),
    index('cursor_request_package_idx').on(t.analysisPackageId),
    check('cursor_request_package_hash_format', sql`${t.packageHash} ~ '^[0-9a-f]{64}$'`),
    check('cursor_request_prompt_hash_format', sql`${t.promptHash} ~ '^[0-9a-f]{64}$'`),
    check('cursor_request_prompt_bytes_positive', sql`${t.promptBytes} > 0`),
  ],
)

/**
 * Bản kê một lần gọi tiến trình con Cursor CLI.
 *
 * KHÔNG lưu dòng lệnh đầy đủ, không lưu môi trường: cả hai đều có thể mang
 * credential. Chỉ lưu định danh công cụ, cờ đã dùng và các băm — đủ để truy vết
 * mà không sao chép bí mật vào database.
 */
export const cursorExecutionManifest = pgTable(
  'cursor_execution_manifest',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    llmExecutionId: uuid('llm_execution_id').notNull(),
    requestId: uuid('request_id').notNull(),
    /** Neo về lần phân tích, để execution và request không thể lệch nhau. */
    analysisRunId: uuid('analysis_run_id').notNull(),

    attemptNumber: integer('attempt_number').notNull(),
    /** Lần chạy trước trong chuỗi retry. NULL = lần đầu. */
    parentExecutionId: uuid('parent_execution_id'),

    toolName: text('tool_name').notNull(),
    toolVersion: text('tool_version'),
    model: text('model'),
    /** Cờ đã dùng, KHÔNG phải dòng lệnh đầy đủ. */
    flags: jsonb('flags').notNull().default(sql`'[]'::jsonb`),

    startedAt: timestamp('started_at', { withTimezone: true }).notNull(),
    finishedAt: timestamp('finished_at', { withTimezone: true }),
    durationMs: integer('duration_ms'),
    exitCode: integer('exit_code'),
    timedOut: boolean('timed_out').notNull().default(false),

    stdoutHash: text('stdout_hash'),
    stdoutBytes: integer('stdout_bytes'),
    /** stderr đã lọc secret; chỉ lưu băm và một đoạn đã lọc. */
    stderrHash: text('stderr_hash'),
    stderrExcerpt: text('stderr_excerpt'),

    outputSchemaVersion: text('output_schema_version'),

    /**
     * Nguồn gốc PHIÊN BẢN, gắn LÚC TẠO execution.
     *
     * Cột thật chứ không nằm trong JSONB: cần truy vấn được ("lô này chạy bằng
     * validator nào") và cần ràng buộc được (chuỗi retry không được trộn phiên
     * bản — xem trigger `cursor_repair_version_immutable`).
     */
    schemaVersion: text('schema_version').notNull(),
    promptVersion: text('prompt_version').notNull(),
    validatorHash: text('validator_hash').notNull(),
    schemaHash: text('schema_hash').notNull(),
    promptSourceHash: text('prompt_source_hash').notNull(),
    failureClass: cursorFailureClassEnum('failure_class').notNull().default('NONE'),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.llmExecutionId, t.workspaceId, t.analysisRunId],
      foreignColumns: [llmExecution.id, llmExecution.workspaceId, llmExecution.analysisRunId],
      name: 'cursor_manifest_execution_run_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.requestId, t.workspaceId, t.analysisRunId],
      foreignColumns: [
        cursorAnalysisRequest.id,
        cursorAnalysisRequest.workspaceId,
        cursorAnalysisRequest.analysisRunId,
      ],
      name: 'cursor_manifest_request_run_fk',
    }).onDelete('restrict'),
    // Chuỗi retry phải trỏ tới execution CÓ THẬT và CÙNG lần phân tích.
    //
    // Ràng buộc chỉ theo (id, workspace) vẫn cho một bản kê của lần chạy B khai
    // cha là execution của lần chạy A — chuỗi retry bắc ngang hai lần phân tích.
    foreignKey({
      columns: [t.parentExecutionId, t.workspaceId, t.analysisRunId],
      foreignColumns: [llmExecution.id, llmExecution.workspaceId, llmExecution.analysisRunId],
      name: 'cursor_manifest_parent_execution_run_fk',
    }).onDelete('restrict'),
    uniqueIndex('cursor_manifest_execution_key').on(t.llmExecutionId),
    index('cursor_manifest_request_idx').on(t.requestId),
    check('cursor_manifest_attempt_bounds', sql`${t.attemptNumber} >= 1 AND ${t.attemptNumber} <= 3`),
    check(
      'cursor_manifest_stdout_hash_format',
      sql`${t.stdoutHash} IS NULL OR ${t.stdoutHash} ~ '^[0-9a-f]{64}$'`,
    ),
    check(
      'cursor_manifest_stderr_hash_format',
      sql`${t.stderrHash} IS NULL OR ${t.stderrHash} ~ '^[0-9a-f]{64}$'`,
    ),
    // Không cho một lần chạy tự nhận là cha của chính nó.
    check('cursor_manifest_no_self_parent', sql`${t.parentExecutionId} IS DISTINCT FROM ${t.llmExecutionId}`),
  ],
)

/**
 * Output ĐÃ VALIDATE của MỘT lần chạy Cursor.
 *
 * Vì sao không dùng `analysis_result`: bảng đó có UNIQUE (analysis_run_id, kind)
 * — mỗi lần chạy phân tích chỉ một kết quả mỗi loại, đúng bất biến của Phase 1.
 * Nhưng Phase 4 yêu cầu tường minh "cùng gói + cùng prompt được chạy nhiều lần
 * để đo độ ổn định, và các kết quả KHÔNG được ghi đè nhau". Hai yêu cầu đó chỉ
 * dung hoà được bằng cách khoá kết quả theo LẦN CHẠY, không theo lần phân tích.
 *
 * Bất biến sau khi ghi (trigger ở migration 0010): chạy lại tạo lần chạy mới.
 */
export const cursorAnalysisResult = pgTable(
  'cursor_analysis_result',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    llmExecutionId: uuid('llm_execution_id').notNull(),
    requestId: uuid('request_id').notNull(),
    /** Neo về lần phân tích, để execution và request không thể lệch nhau. */
    analysisRunId: uuid('analysis_run_id').notNull(),
    channelId: uuid('channel_id').notNull(),

    schemaVersion: text('schema_version').notNull(),
    payload: jsonb('payload').notNull(),
    payloadHash: text('payload_hash').notNull(),

    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    // Execution VÀ request phải cùng một lần phân tích, request phải cùng kênh.
    // Ràng buộc theo workspace đơn lẻ cho phép ghép kết quả của lần chạy này
    // với yêu cầu của lần chạy khác mà mọi khoá ngoại vẫn hợp lệ.
    foreignKey({
      columns: [t.llmExecutionId, t.workspaceId, t.analysisRunId],
      foreignColumns: [llmExecution.id, llmExecution.workspaceId, llmExecution.analysisRunId],
      name: 'cursor_result_execution_run_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.requestId, t.workspaceId, t.analysisRunId, t.channelId],
      foreignColumns: [
        cursorAnalysisRequest.id,
        cursorAnalysisRequest.workspaceId,
        cursorAnalysisRequest.analysisRunId,
        cursorAnalysisRequest.channelId,
      ],
      name: 'cursor_result_request_run_channel_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId, t.channelId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId, analysisRun.channelId],
      name: 'cursor_result_run_channel_fk',
    }).onDelete('restrict'),
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'cursor_result_channel_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('cursor_result_execution_key').on(t.llmExecutionId),
    index('cursor_result_request_idx').on(t.requestId),
    check('cursor_result_hash_format', sql`${t.payloadHash} ~ '^[0-9a-f]{64}$'`),
  ],
)
