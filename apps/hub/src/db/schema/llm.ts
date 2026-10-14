import { sql } from 'drizzle-orm'
import {
  check,
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

import { llmExecutionStatusEnum, llmProviderEnum } from './enums'
import { analysisResult, analysisRun } from './analysis'
import { promptRevision } from './prompt'
import { workspace } from './workspace'

/**
 * Một lần chạy LLM cục bộ (Cursor CLI hoặc Codex CLI).
 *
 * KHÔNG lưu prompt đã render lẫn output thô ở đây: prompt truy được qua
 * `promptRevisionId` + biến, còn output hợp lệ nằm ở `analysis_result`. Chỉ
 * lưu HASH của output thô để chứng minh cái đã validate đúng là cái LLM trả về.
 * Output không hợp lệ thì giữ lý do lỗi (`validationError`) chứ không giữ nội
 * dung — tránh biến bảng này thành nơi tích trữ văn bản không kiểm soát.
 */
export const llmExecution = pgTable(
  'llm_execution',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    analysisRunId: uuid('analysis_run_id').notNull(),
    promptRevisionId: uuid('prompt_revision_id').notNull(),

    provider: llmProviderEnum('provider').notNull(),
    model: text('model'),

    /**
     * Vòng lặp tinh chỉnh thứ mấy (1..3). Điều kiện dừng cứng của Phase 5 là
     * tối đa 3 vòng mỗi gói phân tích — cưỡng chế bằng CHECK ở đây, không chỉ
     * bằng vòng lặp phía ứng dụng.
     */
    iteration: integer('iteration').notNull().default(1),

    /**
     * Số thứ tự lần chạy trong phạm vi (analysis_run, provider).
     *
     * Khác `iteration`: `iteration` là vòng TINH CHỈNH PROMPT của Phase 5, còn
     * đây đếm MỌI lần gọi tiến trình — kể cả retry kỹ thuật lẫn các lần chạy
     * lặp lại để đo độ ổn định. Phase 4 yêu cầu tường minh rằng cùng gói + cùng
     * prompt chạy được nhiều lần và các kết quả KHÔNG ghi đè nhau, nên khoá
     * duy nhất phải mang chiều này.
     */
    executionSequence: integer('execution_sequence').notNull().default(1),

    status: llmExecutionStatusEnum('status').notNull().default('PENDING'),
    /** sha256 của stdout thô từ CLI. */
    rawOutputHash: text('raw_output_hash'),
    /** Lỗi validate schema khi output bị từ chối. */
    validationError: jsonb('validation_error'),
    /** Kết quả đã validate, nếu lần chạy này thành công. */
    analysisResultId: uuid('analysis_result_id'),

    startedAt: timestamp('started_at', { withTimezone: true }),
    finishedAt: timestamp('finished_at', { withTimezone: true }),
    durationMs: integer('duration_ms'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    // Đích cho khoá ngoại phức hợp từ kết quả/kiểm định/bản kê của Phase 4:
    // buộc chúng phải thuộc cùng lần phân tích với execution.
    unique('llm_execution_id_ws_run_key').on(t.id, t.workspaceId, t.analysisRunId),
    // Khoá ngoại ghép: run phải thuộc đúng workspace mà execution khai báo.
    foreignKey({
      columns: [t.analysisRunId, t.workspaceId],
      foreignColumns: [analysisRun.id, analysisRun.workspaceId],
      name: 'llm_execution_run_workspace_fk',
    }).onDelete('restrict'),
    // Prompt phải thuộc đúng workspace của execution.
    foreignKey({
      columns: [t.promptRevisionId, t.workspaceId],
      foreignColumns: [promptRevision.id, promptRevision.workspaceId],
      name: 'llm_execution_prompt_workspace_fk',
    }).onDelete('restrict'),
    // Kết quả phải thuộc ĐÚNG run của execution này. Khoá ngoại đơn sang
    // analysis_result sẽ cho phép một execution nhận vơ kết quả của run khác
    // (kể cả run thuộc workspace khác), làm hỏng nguồn gốc dữ liệu.
    foreignKey({
      columns: [t.analysisResultId, t.analysisRunId],
      foreignColumns: [analysisResult.id, analysisResult.analysisRunId],
      name: 'llm_execution_result_run_fk',
    }).onDelete('restrict'),
    // Đích cho khoá ngoại ghép từ critique.
    unique('llm_execution_id_workspace_key').on(t.id, t.workspaceId),
    // Đích để critique neo vào ĐÚNG prompt mà execution đã thực sự dùng.
    unique('llm_execution_id_prompt_key').on(t.id, t.promptRevisionId),
    uniqueIndex('llm_execution_run_provider_sequence_key').on(
      t.analysisRunId,
      t.provider,
      t.executionSequence,
    ),
    index('llm_execution_run_idx').on(t.analysisRunId),
    index('llm_execution_prompt_idx').on(t.promptRevisionId),
    check('llm_execution_iteration_bounds', sql`${t.iteration} >= 1 AND ${t.iteration} <= 3`),
    check(
      'llm_execution_output_hash_format',
      sql`${t.rawOutputHash} IS NULL OR ${t.rawOutputHash} ~ '^[0-9a-f]{64}$'`,
    ),
    // Bất biến "SUCCEEDED phải có kết quả đã validate" được cưỡng chế bằng
    // TRIGGER (migration 0013), không bằng CHECK.
    //
    // Lý do: kết quả của Cursor nằm ở bảng `cursor_analysis_result` (khoá theo
    // LẦN CHẠY, để các lần chạy lặp lại đo độ ổn định không ghi đè nhau), còn
    // CHECK thì không nhìn được sang bảng khác. Giữ CHECK cũ sẽ buộc phải hoặc
    // bỏ bất biến, hoặc bỏ khả năng chạy lặp lại — trigger giữ được cả hai.
    // Bị từ chối vì schema thì bắt buộc phải nói rõ sai ở đâu.
    check(
      'llm_execution_rejected_has_error',
      sql`${t.status} <> 'REJECTED_SCHEMA' OR ${t.validationError} IS NOT NULL`,
    ),
  ],
)

/**
 * Phê bình của Codex đối với một lần chạy LLM, kèm bản prompt đề xuất.
 *
 * `findings` giữ danh sách có cấu trúc theo đúng các trục Phase 5 yêu cầu:
 * unsupported claims, missed evidence, contradictory conclusions, weak
 * recommendations, overconfidence, prompt weaknesses, output-schema violations.
 */
export const critique = pgTable(
  'critique',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    llmExecutionId: uuid('llm_execution_id').notNull(),
    /** Bản prompt đã dùng để sinh ra kết quả bị phê bình. */
    critiquedPromptRevisionId: uuid('critiqued_prompt_revision_id').notNull(),
    /** Bản prompt Codex đề xuất thay thế. NULL = không đề xuất sửa. */
    proposedPromptRevisionId: uuid('proposed_prompt_revision_id'),

    findings: jsonb('findings').notNull().default(sql`'[]'::jsonb`),
    /** {"BLOCKER":0,"HIGH":1,"MEDIUM":3,"LOW":2} — dùng cho điều kiện dừng. */
    severitySummary: jsonb('severity_summary').notNull().default(sql`'{}'::jsonb`),
    summary: text('summary'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.llmExecutionId, t.workspaceId],
      foreignColumns: [llmExecution.id, llmExecution.workspaceId],
      name: 'critique_execution_workspace_fk',
    }).onDelete('restrict'),
    // Prompt bị phê bình phải là ĐÚNG prompt mà execution đó đã dùng, không chỉ
    // "một prompt nào đó cùng workspace". Ràng buộc riêng lẻ theo workspace cho
    // phép một critique khai sai rằng execution đã dùng prompt khác — làm hỏng
    // nguồn gốc của cả vòng lặp tinh chỉnh ở Phase 5, nơi việc so sánh
    // trước/sau phụ thuộc hoàn toàn vào việc biết prompt nào sinh ra kết quả nào.
    //
    // Ràng buộc này bao hàm luôn điều kiện cùng workspace (execution đã bị neo
    // workspace ở trên), nên không cần thêm khoá ngoại workspace riêng cho cột này.
    foreignKey({
      columns: [t.llmExecutionId, t.critiquedPromptRevisionId],
      foreignColumns: [llmExecution.id, llmExecution.promptRevisionId],
      name: 'critique_execution_prompt_fk',
    }).onDelete('restrict'),
    // Prompt ĐỀ XUẤT là bản mới chưa từng chạy, nên chỉ ràng buộc theo workspace.
    // Cột nullable + MATCH SIMPLE nghĩa là "không đề xuất sửa" vẫn hợp lệ.
    foreignKey({
      columns: [t.proposedPromptRevisionId, t.workspaceId],
      foreignColumns: [promptRevision.id, promptRevision.workspaceId],
      name: 'critique_proposed_prompt_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('critique_execution_key').on(t.llmExecutionId),
    index('critique_workspace_idx').on(t.workspaceId),
  ],
)
