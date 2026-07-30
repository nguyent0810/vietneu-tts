import { pgEnum } from 'drizzle-orm/pg-core'

/**
 * Mọi enum đều là danh sách ĐÓNG. Thêm giá trị mới phải qua migration, để một
 * giá trị lạ không thể lọt vào DB rồi làm mọi nhánh `switch` phía ứng dụng rơi
 * vào trạng thái không xác định.
 */

// --- Content ---------------------------------------------------------------

export const contentKindEnum = pgEnum('content_kind', ['LONG_FORM', 'SHORT'])

export const contentStatusEnum = pgEnum('content_status', [
  'DRAFT',
  'IN_REVIEW',
  'APPROVED',
  'PRODUCTION_READY',
  'PUBLISHED',
  'ARCHIVED',
  'REJECTED',
])

/**
 * Revision chỉ có hai trạng thái. FROZEN là một chiều: đã đóng băng thì nội
 * dung không đổi được nữa (cưỡng chế bằng trigger, xem 0000_init).
 * Bất biến S-0: phải FREEZE trước khi chạy bất kỳ audit/score nào.
 */
export const revisionStateEnum = pgEnum('revision_state', ['DRAFT', 'FROZEN'])

// --- Algorithm & analysis --------------------------------------------------

export const algorithmKindEnum = pgEnum('algorithm_kind', [
  'DETERMINISTIC',
  'LLM',
  'HYBRID',
  'EXTERNAL',
])

/**
 * Chủ thể của một lần phân tích. Cả `subject_type` lẫn `subject_id` đều NOT
 * NULL và cùng nhau tạo thành khoá duy nhất của `run_sequence` — xem AC-3:
 * PostgreSQL coi các NULL là KHÁC NHAU, nên một cột nullable trong UNIQUE sẽ
 * không chặn được trùng lặp.
 */
export const analysisSubjectTypeEnum = pgEnum('analysis_subject_type', [
  'CHANNEL',
  'CONTENT_REVISION',
])

export const analysisRunStatusEnum = pgEnum('analysis_run_status', [
  'PENDING',
  'RUNNING',
  'SUCCEEDED',
  'FAILED',
  'CANCELLED',
])

export const analysisResultKindEnum = pgEnum('analysis_result_kind', [
  'DETERMINISTIC_EVIDENCE',
  'LLM_ANALYSIS',
])

// --- Scoring ---------------------------------------------------------------

/**
 * Hai bộ chiều điểm tách biệt: CONTENT chấm bản thân nội dung, ANALYSIS_RUBRIC
 * chấm CHẤT LƯỢNG của một kết quả phân tích (dùng ở Phase 5 để so bản cũ/mới).
 */
export const dimensionSetEnum = pgEnum('dimension_set', ['CONTENT', 'ANALYSIS_RUBRIC'])

export const evaluatorEnum = pgEnum('evaluator', ['DETERMINISTIC', 'CODEX', 'HUMAN'])

export const evaluationVerdictEnum = pgEnum('evaluation_verdict', [
  'ACCEPT',
  'REVISE',
  'REJECT',
])

// --- Audit & approval ------------------------------------------------------

export const actorTypeEnum = pgEnum('actor_type', ['USER', 'WORKER', 'SYSTEM', 'AGENT'])

export const approvalStateEnum = pgEnum('approval_state', ['PENDING', 'APPROVED', 'REJECTED'])

// --- Prompt ----------------------------------------------------------------

export const promptPurposeEnum = pgEnum('prompt_purpose', [
  'ANALYSIS',
  'CRITIQUE',
  'REFINEMENT',
])

export const promptAuthorEnum = pgEnum('prompt_author', ['HUMAN', 'CODEX', 'SYSTEM'])

// --- LLM execution ---------------------------------------------------------

export const llmProviderEnum = pgEnum('llm_provider', ['CURSOR_CLI', 'CODEX_CLI'])

export const llmExecutionStatusEnum = pgEnum('llm_execution_status', [
  'PENDING',
  'RUNNING',
  'SUCCEEDED',
  'FAILED',
  'REJECTED_SCHEMA',
  'TIMED_OUT',
])

// --- Analytics sync (Phase 2 dùng, khai báo sẵn ở Phase 1) ------------------

export const syncRunStatusEnum = pgEnum('sync_run_status', [
  'RUNNING',
  'SUCCEEDED',
  'PARTIAL',
  'FAILED',
])

export const videoFormatEnum = pgEnum('video_format', ['LONG_FORM', 'SHORT', 'UNKNOWN'])

// --- Auth ------------------------------------------------------------------

/**
 * Token của người dùng và token của máy worker là HAI LOẠI TÁCH BIỆT, không
 * dùng chung bảng: worker chỉ được phép nhận job và nộp kết quả, không bao giờ
 * được thừa hưởng quyền phê duyệt của người dùng.
 */
export const tokenScopeEnum = pgEnum('token_scope', [
  'READ',
  'WRITE',
  'APPROVE',
  'ADMIN',
])

export const workerCapabilityEnum = pgEnum('worker_capability', [
  'ANALYZE_CONTENT',
  'SCORE_CONTENT',
  'IMPROVE_CONTENT',
  'SYNC_ANALYTICS',
  'RUN_LLM_ANALYSIS',
])
