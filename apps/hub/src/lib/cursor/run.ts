import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { and, eq, sql } from 'drizzle-orm'

import { getDb, withTransaction } from '@/db/client'
import * as schema from '@/db/schema'
import type { AnalysisPackage } from '../analysis/package'
import { stableStringify } from '../analysis/package'
import { extractJson, runCursor, type CursorExecOptions, type CursorExecResult } from './exec'
import { execAnthropicMessages } from './exec-anthropic'
import { buildPrompt, buildRepairPrompt, PROMPT_VERSION, type BuiltPrompt } from './prompt'
import { resolveSourceRef } from './source-ref'
import { buildContractProvenance } from './provenance'
import {
  ANALYSIS_SCHEMA_VERSION,
  assertionStatusEnum,
  CLAIM_METRICS,
  COMPOSITE_VALIDATOR_VERSION,
  OBLIGATION_GENERATOR_VERSION,
  OUTPUT_LIMITS,
  claimSourceEnum,
  claimTypeEnum,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  judgementEnum,
  type ClaimDeclaration,
  type ClaimObligationSet,
  type CursorAnalysis,
  type CursorOutput,
  type ExecutionRole,
  type ValidationStage,
  DECLARATION_SCHEMA_VERSION,
} from './schema'
import {
  buildDeclarationPrompt,
  buildDeclarationRepairPrompt,
  DECLARATION_PROMPT_VERSION,
} from './declaration-prompt'
import {
  loadCompositeInputs,
  persistComposite,
  runCompositeStage,
  type CompositeFailureClass,
  type CompositeOutcome,
} from './composite'
import {
  buildObligationSet,
  checkObligationBelongsTo,
  checkObligationSourcesIntact,
  hashAnalysisPayload,
  hashObligationSet,
} from './obligation'
import {
  validateAnalysisOutput,
  validateCursorOutput,
  scanProseOutsideJson,
  validateDeclarationOutput,
  validateProseOnly,
  type ValidationIssue,
  type ValidationReport,
} from './validate'

/**
 * Điều phối một lần phân tích Cursor cho MỘT gói bằng chứng.
 *
 * Chính sách thử lại: lần đầu + tối đa 2 lần SỬA LỖI, và chỉ khi thất bại
 * thuộc loại KỸ THUẬT (JSON hỏng, sai schema, CLI lỗi, timeout).
 *
 * Thất bại về NỘI DUNG — câu nhân quả không có căn cứ, kết luận CTR khi không
 * có dữ liệu, evidence id không giải được — KHÔNG được retry. Retry những cái
 * đó nghĩa là chạy lại cho tới khi mô hình nói điều ta muốn nghe, và kết quả
 * "đạt" khi ấy chỉ phản ánh sự kiên nhẫn của vòng lặp chứ không phản ánh bằng
 * chứng. Những lần chạy đó được lưu lại ở trạng thái thất bại, kèm nguyên văn
 * lý do.
 */

export const MAX_ATTEMPTS = 3 // 1 lần đầu + 2 lần sửa

/** Nhãn `toolName` cho lượt khai báo RỖNG — không có tiến trình con nào chạy. */
export const EMPTY_DECLARATION_TOOL = '(khai báo rỗng tất định — không gọi LLM)'

/**
 * Bản khai RỖNG TẤT ĐỊNH cho lần chạy không có nghĩa vụ nào.
 *
 * Trả về đúng hình dạng `CursorExecResult` để phần còn lại của vòng lặp không
 * cần biết có gọi LLM hay không — một đường đi, một chỗ cấp phép.
 */
function syntheticEmptyDeclaration(obligationSetHash: string): CursorExecResult {
  const payload = JSON.stringify({
    schemaVersion: DECLARATION_SCHEMA_VERSION,
    obligationSetHash,
    declarations: [],
  })
  // Thời điểm THẬT, không phải epoch: `started_at`/`finished_at` được dùng để
  // sắp thứ tự và để đọc lại lịch sử. Tính tất định nằm ở PAYLOAD, không ở dấu
  // thời gian — đóng băng dấu thời gian chỉ làm hỏng mọi truy vấn theo thời gian.
  const now = new Date()
  return {
    stdout: payload,
    stderr: '',
    stdoutHash: createHash('sha256').update(payload, 'utf8').digest('hex'),
    stderrHash: createHash('sha256').update('', 'utf8').digest('hex'),
    stdoutBytes: Buffer.byteLength(payload, 'utf8'),
    exitCode: 0,
    timedOut: false,
    truncated: false,
    durationMs: 0,
    startedAt: now,
    finishedAt: now,
    flags: [],
    toolName: EMPTY_DECLARATION_TOOL,
  }
}

/**
 * Băm MÃ NGUỒN của ba tệp quyết định ngữ nghĩa kiểm định.
 *
 * Tính MỘT LẦN lúc nạp module, tức là gắn vào execution ngay khi tạo — không
 * suy ngược từ artifact sau khi chạy. Suy ngược chỉ là đọc lại chính thứ mình
 * vừa ghi, và không phát hiện được worker cũ đang chạy song song.
 */
function hashSource(file: string): string {
  try {
    const here = dirname(fileURLToPath(import.meta.url))
    return createHash('sha256').update(readFileSync(join(here, file), 'utf8'), 'utf8').digest('hex')
  } catch {
    return 'unavailable'
  }
}

/**
 * Băm LOCKFILE và commit git — mở rộng phạm vi nguồn gốc.
 *
 * Băm ba tệp mã nguồn KHÔNG bao được hành vi của validator: chỉ cần đổi một
 * phụ thuộc được import là hành vi khác trong khi ba băm kia y nguyên. Lockfile
 * và commit thu hẹp khoảng trống đó, nhưng vẫn KHÔNG phải attestation — xem
 * creator_specs/PHASE4_TRUST_BOUNDARIES.md.
 */
function hashRepoFile(rel: string): string {
  try {
    const here = dirname(fileURLToPath(import.meta.url))
    return createHash('sha256')
      .update(readFileSync(join(here, '..', '..', '..', rel), 'utf8'), 'utf8')
      .digest('hex')
  } catch {
    return 'unavailable'
  }
}

export const LOCKFILE_HASH = hashRepoFile('package-lock.json')
export const VALIDATOR_HASH = hashSource('validate.ts')
export const SCHEMA_HASH = hashSource('schema.ts')
export const PROMPT_SOURCE_HASH = hashSource('prompt.ts')
export const DECLARATION_PROMPT_SOURCE_HASH = hashSource('declaration-prompt.ts')
export const OBLIGATION_GENERATOR_HASH = hashSource('obligation.ts')
export const COMPOSITE_SOURCE_HASH = hashSource('composite.ts')
/**
 * `sensitive.ts` LÀ HỢP ĐỒNG, không phải tiện ích.
 *
 * Nó định nghĩa "ô nào phải khai báo" và được import bởi CẢ bộ sinh nghĩa vụ lẫn
 * bộ kiểm định. Sửa một mẫu regex trong đó là đổi ngữ nghĩa của U3 và S1 — nhưng
 * trước đây không băm nào phủ nó, và vì tệp chưa được theo dõi bởi git,
 * `git diff HEAD` cũng không thấy. Hai lần chạy với hai định nghĩa khác nhau có
 * nguồn gốc GIỐNG HỆT nhau từng byte.
 */
export const SENSITIVE_LEXICON_HASH = hashSource('sensitive.ts')
/** Hai tệp dựng nguồn gốc/danh tính — đổi chúng là đổi cách lô được ghi lại. */
export const IDENTITY_SOURCE_HASH = hashSource('identity.ts')
export const PROVENANCE_SOURCE_HASH = hashSource('provenance.ts')

/**
 * Bản ghi NGUỒN GỐC dùng chung cho mọi bề mặt — tính MỘT LẦN lúc nạp module.
 *
 * Mọi nơi cần nguồn gốc (`_meta`, `INDEX.json`, bản kê) đều chép từ đây, nên
 * lệch nhau giữa các bề mặt trở thành phát hiện được bằng phép so thay vì phụ
 * thuộc vào việc ba chỗ nhớ cập nhật giống nhau.
 */
export const CONTRACT_PROVENANCE = buildContractProvenance({
  validatorHash: VALIDATOR_HASH,
  schemaHash: SCHEMA_HASH,
  promptSourceHash: PROMPT_SOURCE_HASH,
  declarationPromptSourceHash: DECLARATION_PROMPT_SOURCE_HASH,
  obligationGeneratorHash: OBLIGATION_GENERATOR_HASH,
  compositeSourceHash: COMPOSITE_SOURCE_HASH,
  sensitiveLexiconHash: SENSITIVE_LEXICON_HASH,
  identitySourceHash: IDENTITY_SOURCE_HASH,
  provenanceSourceHash: PROVENANCE_SOURCE_HASH,
  lockfileHash: LOCKFILE_HASH,
  analysisPromptVersion: PROMPT_VERSION,
  declarationPromptVersion: DECLARATION_PROMPT_VERSION,
})

/**
 * NHÀ CUNG CẤP của lượt gọi — CHỌN MỘT LẦN, dùng cho cả hai lượt.
 *
 * Vì sao là biến môi trường chứ không phải cờ dòng lệnh: cả hai lượt (phân tích
 * và khai báo) và cả chỗ GHI bản kê đều phải nhất trí. Một lô nửa CLI nửa API là
 * lô trộn hai người phân tích — đúng thứ mà `mixedAcrossBatch` sinh ra để bắt,
 * và cũng là thứ không được phép tồn tại ngay từ đầu.
 *
 * Mặc định là `CURSOR_CLI`: mọi lô đã chạy đều bằng nó, và một thay đổi mã
 * KHÔNG được lặng lẽ đổi người phân tích của lô kế tiếp.
 *
 * Đổi giá trị này là đổi THƯỚC ĐO. Lô `ANTHROPIC_API` không gộp được với lô
 * `CURSOR_CLI`, đúng quy tắc đã áp khi đổi bản runtime của `cursor-agent`.
 */
export type LlmProviderKind = 'CURSOR_CLI' | 'ANTHROPIC_API'

export function selectedProvider(): LlmProviderKind {
  return process.env.CURSOR_PROVIDER === 'ANTHROPIC_API' ? 'ANTHROPIC_API' : 'CURSOR_CLI'
}

/** Gọi đúng bộ thực thi của nhà cung cấp đang chọn. Cùng vào, cùng ra. */
async function runProvider(options: CursorExecOptions): Promise<CursorExecResult> {
  return selectedProvider() === 'ANTHROPIC_API'
    ? execAnthropicMessages(options)
    : runCursor(options)
}

const RETRYABLE = new Set([
  'INVALID_JSON',
  'PROSE_OUTSIDE_JSON',
  'SCHEMA_MISMATCH',
  'MISSING_REQUIRED_FIELD',
  'TRUNCATED_OUTPUT',
  'UNSUPPORTED_SCHEMA_VERSION',
  'CLI_NONZERO_EXIT',
  'CLI_TIMEOUT',
  'OUTPUT_TOO_LARGE',
])

export interface RunCursorAnalysisParams {
  workspaceId: string
  channelLabel: string
  sandboxDir: string
  /** Dùng gói mới nhất nếu không chỉ định. */
  analysisPackageId?: string
  model?: string
  timeoutMs?: number
  /** Chạy Cursor thật nhưng KHÔNG ghi — dùng cho kiểm tra thủ công. */
  dryRun?: boolean
}

export interface AttemptRecord {
  attemptNumber: number
  llmExecutionId: string | null
  failureClass: string
  passed: boolean
  durationMs: number
  exitCode: number | null
  timedOut: boolean
  stdoutBytes: number
  repairErrors: string[]
  report: ValidationReport | null
}

export interface RunCursorAnalysisResult {
  requestId: string | null
  channelLabel: string
  packageHash: string
  promptHash: string
  promptBytes: number
  /**
   * Lần thử của LƯỢT PHÂN TÍCH — cũng chính là lần thử ĐỘ ỔN ĐỊNH.
   *
   * Lượt khai báo KHÔNG cộng vào đây, có chủ đích: bảng lần thử trả lời câu
   * "phải chạy lại bài phân tích mấy lần", và một lần sửa khai báo không phải
   * một bài phân tích mới. Gộp vào sẽ làm mọi tỉ lệ đạt của lô sai lệch.
   */
  attempts: AttemptRecord[]
  finalAttempt: number | null
  output: CursorOutput | null
  report: ValidationReport | null
  status: 'SUCCEEDED' | 'REJECTED_SCHEMA' | 'FAILED'

  /** Cùng nội dung với `attempts`, đặt tên rõ vai để đọc báo cáo khỏi nhầm. */
  analysisAttempts: AttemptRecord[]
  /** Lần thử của LƯỢT KHAI BÁO — ghi lại đầy đủ, nhưng KHÔNG phải lần thử độ ổn định. */
  declarationAttempts: AttemptRecord[]
  analysisExecutionId: string | null
  obligationCount: number | null
  obligationSetHash: string | null
  analysisPayloadHash: string | null
  declarations: ClaimDeclaration[] | null
  declarationPromptBytes: number | null
  /**
   * Thất bại HỆ THỐNG — lỗi của MÃ hoặc của dữ liệu, không phải của mô hình.
   *
   * Tách riêng khỏi `status` vì gộp chúng vào cùng một con số sẽ đẩy một lỗi lập
   * trình vào cột "mô hình thất bại" của lô đo.
   */
  systemFailure?: { stage: 'OBLIGATION_GENERATION' | 'COMPOSITE'; message: string }
  declarationExecutionId?: string | null
  compositeReport?: ValidationReport | null
  compositePayloadHash?: string | null
  /** id hàng kết quả CHÍNH THỨC. `null` nghĩa là chưa có hiện vật nào được cấp phép. */
  resultId?: string | null
  /**
   * id hàng kiểm định HỢP NHẤT gần nhất — kể cả khi nó KHÔNG ĐẠT.
   *
   * Ghi cả phán quyết trượt là có chủ đích: một lần khai báo trượt ngữ nghĩa vẫn
   * phải TRUY được, nếu không thì bảng lần thử nói "trượt" mà không chỉ được ra
   * bằng chứng nào.
   */
  compositeValidationId?: string | null
  /** Danh tính CHẠY, để INDEX.json không phải suy ngược từ tên tệp. */
  analysisRunId?: string | null
  channelId?: string | null
  /**
   * Loại thất bại của chặng hợp nhất, nếu có.
   *
   * Tách khỏi `status` vì hai loại phải được ĐẾM khác nhau khi tổng kết lô:
   * `SYSTEM_OR_INTEGRITY` là lỗi của ta, `DECLARATION_SEMANTIC` là lỗi của bản khai.
   */
  compositeFailureClass?: CompositeFailureClass
}

interface LoadedPackage {
  packageId: string
  analysisRunId: string
  channelId: string
  packageHash: string
  pkg: AnalysisPackage
}

async function loadPackage(
  workspaceId: string,
  channelLabel: string,
  packageId?: string,
): Promise<LoadedPackage> {
  const db = getDb()
  const rows = await db.execute<{
    id: string
    analysis_run_id: string
    channel_id: string
    payload_hash: string
    payload: AnalysisPackage
  }>(sql`
    SELECT p.id, p.analysis_run_id, p.channel_id, p.payload_hash, p.payload
    FROM analysis_package p
    JOIN channel c ON c.id = p.channel_id
    WHERE p.workspace_id = ${workspaceId}
      AND c.label = ${channelLabel}
      AND (${packageId ?? null}::uuid IS NULL OR p.id = ${packageId ?? null}::uuid)
    ORDER BY p.created_at DESC
    LIMIT 1
  `)
  const row = rows.rows[0]
  if (!row) throw new Error(`Không tìm thấy gói phân tích cho kênh "${channelLabel}".`)
  return {
    packageId: row.id,
    analysisRunId: row.analysis_run_id,
    channelId: row.channel_id,
    packageHash: row.payload_hash,
    pkg: row.payload,
  }
}

/** Bản prompt trong DB — tạo một lần rồi dùng lại, bất biến theo thiết kế. */
async function ensurePromptRevision(
  workspaceId: string,
  promptText: string,
): Promise<string> {
  const db = getDb()
  const key = 'cursor.analysis.channel'

  await db
    .insert(schema.promptTemplate)
    .values({ workspaceId, key, purpose: 'ANALYSIS', description: 'Phân tích kênh bằng Cursor CLI' })
    .onConflictDoNothing()

  const tpl = await db
    .select({ id: schema.promptTemplate.id })
    .from(schema.promptTemplate)
    .where(
      and(eq(schema.promptTemplate.workspaceId, workspaceId), eq(schema.promptTemplate.key, key)),
    )
    .limit(1)
  const templateId = tpl[0]!.id

  const existing = await db.execute<{ id: string }>(sql`
    SELECT id FROM prompt_revision
    WHERE template_id = ${templateId} AND revision_number = 1
    LIMIT 1
  `)
  if (existing.rows[0]) return existing.rows[0].id

  // `body` lưu SƯỜN prompt (phiên bản), không lưu bản đã render kèm dữ liệu —
  // bản render đổi theo từng gói, còn phiên bản prompt thì không.
  const [row] = await db
    .insert(schema.promptRevision)
    .values({
      templateId,
      workspaceId,
      revisionNumber: 1,
      body: promptText.slice(0, 200_000),
      variables: ['package', 'contentMetadata'],
      contentHash: createHash('sha256').update(PROMPT_VERSION, 'utf8').digest('hex'),
      authoredBy: 'HUMAN',
      changeReason: `Prompt cơ sở Phase 4 v${PROMPT_VERSION}`,
    })
    .returning({ id: schema.promptRevision.id })
  return row!.id
}

function classifyExec(exec: CursorExecResult): string | null {
  if (exec.timedOut) return 'CLI_TIMEOUT'
  if (exec.truncated) return 'OUTPUT_TOO_LARGE'
  if (exec.exitCode !== 0) return 'CLI_NONZERO_EXIT'
  return null
}

/**
 * Kết quả của MỘT lượt (phân tích hoặc khai báo).
 *
 * Vòng lặp thử lại giống nhau ở hai lượt — khác nhau ở prompt, ở bộ kiểm định và
 * ở cái được ghi kèm. Tách ra một hàm để hai lượt KHÔNG thể trôi dạt hành vi
 * retry của nhau: một lượt cho phép ba lần thử còn lượt kia bốn là loại lệch
 * không ai nhìn thấy cho tới lúc đọc bảng lần thử.
 */
interface PassOutcome<T> {
  attempts: AttemptRecord[]
  value: T | null
  report: ValidationReport | null
  finalAttempt: number | null
  lastExecutionId: string | null
  failureClass: string
}

/** Một lần thử của một lượt, đã chạy Cursor và đã kiểm định. */
interface PassStep<T> {
  value: T | null
  report: ValidationReport | null
  failureClass: string
  repairErrors: string[]
}

/**
 * Vòng thử lại DÙNG CHUNG cho cả hai lượt.
 *
 * Ngân sách RIÊNG cho mỗi lượt (`MAX_ATTEMPTS` mỗi bên): một lỗi hình dạng ở
 * lượt khai báo không được tiêu mất lần thử của lượt phân tích, và ngược lại.
 * Đây chính là khoản tiết kiệm của kiến trúc hai lượt — hợp đồng một lượt bắt
 * vứt cả bài phân tích 100–235 giây chỉ vì một lỗi khai báo.
 */
async function runPass<T>(args: {
  params: RunCursorAnalysisParams
  loaded: LoadedPackage
  requestId: string | null
  promptRevisionId: string | null
  role: ExecutionRole
  stage: ValidationStage
  initialPrompt: string
  /** Kiểm định một output thô. */
  check: (json: string, hadProse: boolean, prose?: string) => PassStep<T>
  /** Dựng prompt sửa lỗi; trả `null` nghĩa là KHÔNG được thử lại. */
  repair: (errors: string[], invalidOutput: string) => { text: string; truncated: boolean } | null
  analysisExecutionId?: string | null
  declarationProvenance?: PersistAttemptArgs['declarationProvenance']
  persistResultOf?: (value: T) => PersistAttemptArgs['persistResult']
}): Promise<PassOutcome<T>> {
  const attempts: AttemptRecord[] = []
  let promptText = args.initialPrompt
  // Cha CHỈ trong phạm vi lượt này. Không bao giờ trỏ sang lượt khác — trigger
  // `cursor_repair_version_immutable` chặn chuỗi trộn vai, và ở đây ta không
  // bao giờ tạo ra chuỗi như thế ngay từ đầu.
  let parentExecutionId: string | null = null
  let value: T | null = null
  let report: ValidationReport | null = null
  let finalAttempt: number | null = null
  let lastExecutionId: string | null = null
  let failureClass = 'NONE'

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const exec = await runProvider({
      prompt: promptText,
      sandboxDir: args.params.sandboxDir,
      timeoutMs: args.params.timeoutMs,
      model: args.params.model,
    })

    const execFailure = classifyExec(exec)
    const { json, hadProseOutsideJson, proseText } = extractJson(exec.stdout)

    let step: PassStep<T> = { value: null, report: null, failureClass: 'NONE', repairErrors: [] }
    if (execFailure) {
      /*
       * CLI hỏng KHÔNG xoá lời mô hình đã nói.
       *
       * `CLI_NONZERO_EXIT`, `CLI_TIMEOUT`, `OUTPUT_TOO_LARGE` đều nằm trong
       * `RETRYABLE`. Nếu nhánh này bỏ qua phần quét thì mô hình chỉ cần in một
       * khẳng định bị cấm rồi thoát khác 0 là câu ấy biến mất khỏi hồ sơ và vòng
       * chạy tự thử lại — đúng cái "chạy lại tới khi nó thôi nói điều đó" mà cả
       * tầng này tồn tại để cấm. stdout có thể cụt, nhưng phần đọc được vẫn là
       * lời của mô hình.
       *
       * Hỏng hạ tầng THẬT (timeout không kịp in gì) không sinh văn xuôi, nên nó
       * vẫn giữ nguyên lớp kỹ thuật và vẫn được thử lại.
       */
      const p = validateProseOnly({ proseText, hadProseOutsideJson, emittedJson: json, analysisPass: true })
      const forbidden = p.report.causalViolations > 0 || p.report.ctrViolations > 0
      step = {
        value: null,
        report: forbidden ? p.report : null,
        failureClass: forbidden ? 'UNSUPPORTED_CLAIM' : execFailure,
        repairErrors: [`Cursor CLI thất bại: ${execFailure}`, ...(forbidden ? p.repairErrors : [])],
      }
    } else if (!json) {
      // KHÔNG bỏ qua văn xuôi ở đây: `proseText` lúc này là TOÀN BỘ stdout, và
      // nhánh này không đi qua bộ kiểm định. Xem `validateProseOnly`.
      const p = validateProseOnly({ proseText, hadProseOutsideJson, emittedJson: json, analysisPass: true })
      step = { value: null, report: p.report, failureClass: p.failureClass, repairErrors: p.repairErrors }
    } else {
      step = args.check(json, hadProseOutsideJson, proseText)
    }

    const passed = step.failureClass === 'NONE' && step.report?.passed === true
    failureClass = step.failureClass

    let llmExecutionId: string | null = null
    if (!args.params.dryRun && args.requestId && args.promptRevisionId) {
      llmExecutionId = await persistAttempt({
        workspaceId: args.params.workspaceId,
        channelId: args.loaded.channelId,
        analysisRunId: args.loaded.analysisRunId,
        requestId: args.requestId,
        promptRevisionId: args.promptRevisionId,
        attempt,
        parentExecutionId,
        exec,
        failureClass: step.failureClass,
        passed,
        report: step.report,
        output: null,
        model: args.params.model,
        executionRole: args.role,
        stage: args.stage,
        analysisExecutionId: args.analysisExecutionId ?? null,
        declarationProvenance: args.declarationProvenance,
        persistResult: passed && step.value && args.persistResultOf ? args.persistResultOf(step.value) : null,
      })
      parentExecutionId = llmExecutionId
      lastExecutionId = llmExecutionId
    }

    attempts.push({
      attemptNumber: attempt,
      llmExecutionId,
      failureClass: step.failureClass,
      passed,
      durationMs: exec.durationMs,
      exitCode: exec.exitCode,
      timedOut: exec.timedOut,
      stdoutBytes: exec.stdoutBytes,
      repairErrors: step.repairErrors,
      report: step.report,
    })

    if (passed) {
      value = step.value
      report = step.report
      finalAttempt = attempt
      break
    }

    // Chỉ thử lại với thất bại KỸ THUẬT. Thất bại nội dung dừng ngay tại đây.
    if (!RETRYABLE.has(step.failureClass)) break
    if (attempt === MAX_ATTEMPTS) break
    const repair = args.repair(step.repairErrors, json ?? exec.stdout)
    if (!repair || repair.truncated) {
      attempts[attempts.length - 1]!.repairErrors.push(
        'Không thử lại: output trước đó quá dài để đưa trọn vào prompt sửa lỗi.',
      )
      break
    }
    promptText = repair.text
  }

  return { attempts, value, report, finalAttempt, lastExecutionId, failureClass }
}

/**
 * Điều phối HAI LƯỢT cho một gói bằng chứng.
 *
 * Thứ tự bắt buộc, và mỗi bước là một CỔNG cho bước sau:
 *
 *   1. LƯỢT PHÂN TÍCH -> văn xuôi. Hỏng thì DỪNG: không sinh nghĩa vụ, không
 *      tạo execution khai báo nào.
 *   2. SINH NGHĨA VỤ từ payload ĐỌC LẠI TỪ DATABASE, không từ object trong bộ
 *      nhớ. Đọc lại là cách duy nhất chứng minh thứ được khai báo chính là thứ
 *      đã được lưu — một object trong RAM có thể đã bị sửa sau khi ghi.
 *   3. LƯỢT KHAI BÁO trên đúng tập nghĩa vụ đó.
 *
 * Chặng COMPOSITE và kết quả hợp nhất KHÔNG thuộc hàm này.
 */
export async function runCursorAnalysis(
  params: RunCursorAnalysisParams,
): Promise<RunCursorAnalysisResult> {
  const loaded = await loadPackage(params.workspaceId, params.channelLabel, params.analysisPackageId)
  const built: BuiltPrompt = buildPrompt({ pkg: loaded.pkg })

  let requestId: string | null = null
  let promptRevisionId: string | null = null
  if (!params.dryRun) {
    promptRevisionId = await ensurePromptRevision(params.workspaceId, built.text)
    const [row] = await getDb()
      .insert(schema.cursorAnalysisRequest)
      .values({
        workspaceId: params.workspaceId,
        channelId: loaded.channelId,
        analysisRunId: loaded.analysisRunId,
        analysisPackageId: loaded.packageId,
        packageHash: loaded.packageHash,
        promptRevisionId,
        promptHash: built.hash,
        promptBytes: built.bytes,
        omissions: built.omissions,
      })
      .returning({ id: schema.cursorAnalysisRequest.id })
    requestId = row!.id
  }

  // --- LƯỢT 1: PHÂN TÍCH ---------------------------------------------------
  const analysisPass = await runPass<CursorAnalysis>({
    params,
    loaded,
    requestId,
    promptRevisionId,
    role: 'ANALYSIS',
    stage: 'ANALYSIS',
    initialPrompt: built.text,
    check: (json, hadProse, prose) => {
      const v = validateAnalysisOutput({
        raw: json,
        pkg: loaded.pkg,
        allowedEvidenceIds: built.allowedEvidenceIds,
        allowedVideoIds: built.allowedVideoIds,
        allowedCohortKeys: built.allowedCohortKeys,
        hadProseOutsideJson: hadProse,
        proseText: prose,
      })
      return {
        value: v.output as unknown as CursorAnalysis | null,
        report: v.report,
        failureClass: v.failureClass,
        repairErrors: v.repairErrors,
      }
    },
    repair: (errors, invalidOutput) => buildRepairPrompt({ errors, invalidOutput }),
    persistResultOf: (analysis) => ({
      role: 'ANALYSIS',
      payload: analysis,
      payloadHash: hashAnalysisPayload(analysis),
    }),
  })

  const result: RunCursorAnalysisResult = {
    requestId,
    channelLabel: params.channelLabel,
    packageHash: loaded.packageHash,
    promptHash: built.hash,
    promptBytes: built.bytes,
    attempts: analysisPass.attempts,
    finalAttempt: analysisPass.finalAttempt,
    output: null,
    report: analysisPass.report,
    status: 'REJECTED_SCHEMA',
    analysisAttempts: analysisPass.attempts,
    declarationAttempts: [],
    analysisExecutionId: analysisPass.lastExecutionId,
    obligationCount: null,
    obligationSetHash: null,
    analysisPayloadHash: null,
    declarations: null,
    declarationPromptBytes: null,
    analysisRunId: loaded.analysisRunId,
    channelId: loaded.channelId,
    compositeValidationId: null,
  }

  // CỔNG: lượt 1 hỏng thì DỪNG HẲN. Không nghĩa vụ, không lượt 2.
  if (!analysisPass.value) {
    const last = analysisPass.attempts[analysisPass.attempts.length - 1]
    result.status =
      last?.failureClass === 'CLI_TIMEOUT' || last?.failureClass === 'CLI_NONZERO_EXIT'
        ? 'FAILED'
        : 'REJECTED_SCHEMA'
    return result
  }

  // Ở chế độ dryRun không có gì được ghi, nên cũng không có gì để đọc lại.
  if (params.dryRun || !requestId || !promptRevisionId || !analysisPass.lastExecutionId) {
    result.output = analysisPass.value as unknown as CursorOutput
    result.status = 'SUCCEEDED'
    return result
  }

  // --- BƯỚC 2: SINH NGHĨA VỤ TỪ PAYLOAD ĐÃ LƯU -----------------------------
  let obligationSet: ClaimObligationSet
  let obligationSetHash: string
  try {
    const reloaded = await getDb().execute<{ payload: unknown; payload_hash: string }>(sql`
      SELECT payload, payload_hash FROM cursor_analysis_result
      WHERE llm_execution_id = ${analysisPass.lastExecutionId} AND result_role = 'ANALYSIS'
      LIMIT 1
    `)
    const persisted = reloaded.rows[0]
    if (!persisted) throw new Error('không đọc lại được payload phân tích vừa ghi')

    // Sinh nghĩa vụ TỪ BẢN ĐỌC LẠI, không từ `analysisPass.value`.
    const fromDb = persisted.payload as CursorAnalysis
    obligationSet = buildObligationSet(fromDb)

    // Bản đọc lại phải đúng là bản đã ghi. Trùng lặp có chủ đích với CHECK của
    // database: JSONB không giữ thứ tự khoá, nên đây là chỗ duy nhất chứng minh
    // phép băm bất biến trước vòng đời đó.
    const belongs = checkObligationBelongsTo(obligationSet, fromDb)
    if (!belongs.ok) throw new Error(belongs.message)
    if (obligationSet.analysisHash !== persisted.payload_hash) {
      throw new Error(
        `băm payload đọc lại (${obligationSet.analysisHash.slice(0, 12)}…) khác cột payload_hash ` +
          `(${persisted.payload_hash.slice(0, 12)}…)`,
      )
    }

    // PHÂN GIẢI LẠI mọi sourceRef trước khi lưu — O-INV-2 ở tầng ứng dụng.
    const drift = checkObligationSourcesIntact(obligationSet, fromDb)
    if (drift.length > 0) {
      throw new Error(drift.map((d) => (d.ok ? '' : d.message)).filter(Boolean).join('; '))
    }

    obligationSetHash = hashObligationSet(obligationSet)
    await getDb().insert(schema.cursorClaimObligation).values({
      workspaceId: params.workspaceId,
      analysisRunId: loaded.analysisRunId,
      channelId: loaded.channelId,
      requestId,
      analysisExecutionId: analysisPass.lastExecutionId,
      analysisHash: obligationSet.analysisHash,
      obligationSetHash,
      generatorVersion: OBLIGATION_GENERATOR_VERSION,
      obligationCount: obligationSet.obligations.length,
      obligations: obligationSet,
    })
  } catch (err) {
    // THẤT BẠI HỆ THỐNG, không phải thất bại của mô hình.
    //
    // Bộ sinh nghĩa vụ là THUẬT TOÁN: cùng payload cho cùng tập, không có yếu tố
    // ngẫu nhiên nào. Nó hỏng nghĩa là mã hỏng hoặc dữ liệu bị đổi dưới chân —
    // và cả hai đều phải điều tra tay, không được retry. Gán nó vào mô hình sẽ
    // biến một lỗi lập trình thành một con số trong bảng "mô hình thất bại".
    result.status = 'FAILED'
    result.systemFailure = {
      stage: 'OBLIGATION_GENERATION',
      message: err instanceof Error ? err.message : String(err),
    }
    result.output = analysisPass.value as unknown as CursorOutput
    return result
  }

  result.obligationCount = obligationSet.obligations.length
  result.obligationSetHash = obligationSetHash
  result.analysisPayloadHash = obligationSet.analysisHash

  /*
   * KHÔNG có ô nhạy cảm nào -> KHÔNG gọi LLM, nhưng VẪN đi hết đường cấp phép.
   *
   * Bản trước tắt ngang ở đây: đặt `status = 'SUCCEEDED'` rồi `return`. Hậu quả
   * là một lần chạy được tính vào mẫu số ĐẠT và ghi ra artifact trong khi KHÔNG
   * có phán quyết COMPOSITE, KHÔNG có hàng kết quả chính thức, `resultId` null.
   * Nó tạo ra một ĐƯỜNG CẤP PHÉP THỨ HAI — một đường không có bằng chứng nào.
   *
   * Nay: sinh một BẢN KHAI RỖNG TẤT ĐỊNH, neo vào đúng băm văn xuôi và băm tập
   * nghĩa vụ đã đóng băng, rồi cho nó đi qua ĐÚNG chặng hợp nhất như mọi lần
   * chạy khác. Đúng MỘT đường cấp phép, và "đạt" vẫn có nghĩa là "có phán quyết
   * COMPOSITE ĐẠT và một hiện vật chính thức đã được ghi".
   */
  const emptyDeclarationRun = obligationSet.obligations.length === 0

  // --- LƯỢT 2: KHAI BÁO + HỢP NHẤT, CÙNG một vòng thử lại -------------------
  //
  // Chặng hợp nhất nằm TRONG vòng lặp, không đứng sau nó. Lý do: một bản khai
  // sai ngữ nghĩa (S1–S8) chỉ lộ ra ở chặng hợp nhất, và nó là lỗi CÓ THỂ SỬA —
  // văn xuôi đã đóng băng nên khai lại không đổi được kết luận, chỉ đổi được
  // nhãn. Đặt hợp nhất ngoài vòng lặp thì lỗi ấy tiêu luôn cả lần chạy.
  const declPrompt = buildDeclarationPrompt({
    analysisPayload: analysisPass.value,
    obligationSet,
    obligationSetHash,
    analysisPayloadHash: obligationSet.analysisHash,
  })
  result.declarationPromptBytes = declPrompt.bytes

  const declProvenance = {
    obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION,
    declarationPromptVersion: DECLARATION_PROMPT_VERSION,
    declarationPromptSourceHash: DECLARATION_PROMPT_SOURCE_HASH,
    compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
    analysisPayloadHash: obligationSet.analysisHash,
    obligationSetHash,
  }
  const compositeProvenance = {
    ...CONTRACT_PROVENANCE,
    channelLabel: params.channelLabel,
    packageHash: loaded.packageHash,
    promptHash: built.hash,
    declarationPromptHash: declPrompt.hash,
    requestId,
    analysisRunId: loaded.analysisRunId,
    channelId: loaded.channelId,
    analysisPackageId: loaded.packageId,
  }

  let declPromptText = declPrompt.text
  let declParent: string | null = null
  const declarationAttempts: AttemptRecord[] = []

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    // Bản khai RỖNG: không gọi CLI. `stdout` là payload tất định, nên mọi phép
    // kiểm phía sau (schema, băm tập nghĩa vụ, danh tính) chạy y như thường.
    const exec = emptyDeclarationRun
      ? syntheticEmptyDeclaration(obligationSetHash)
      : await runProvider({
          prompt: declPromptText,
          sandboxDir: params.sandboxDir,
          timeoutMs: params.timeoutMs,
          model: params.model,
        })
    const execFailure = classifyExec(exec)
    const { json, hadProseOutsideJson, proseText } = extractJson(exec.stdout)

    let failureClass = execFailure ?? 'NONE'
    let repairErrors: string[] = execFailure ? [`Cursor CLI thất bại: ${execFailure}`] : []
    let declReport: ValidationReport | null = null
    let declarations: ClaimDeclaration[] | null = null

    // Cùng lý do như lượt phân tích: CLI hỏng không xoá lời mô hình đã nói.
    if (execFailure) {
      const p = validateProseOnly({ proseText, hadProseOutsideJson, emittedJson: json, declarationPass: true })
      if (p.report.causalViolations > 0 || p.report.ctrViolations > 0) {
        declReport = p.report
        failureClass = 'UNSUPPORTED_CLAIM'
        repairErrors = [...repairErrors, ...p.repairErrors]
      }
    }

    if (!execFailure) {
      if (!json) {
        const p = validateProseOnly({ proseText, hadProseOutsideJson, emittedJson: json, declarationPass: true })
        declReport = p.report
        failureClass = p.failureClass
        repairErrors = p.repairErrors
      } else {
        const v = validateDeclarationOutput({ raw: json, obligationSet, obligationSetHash })
        declReport = v.report
        declarations = v.declarations
        failureClass = v.failureClass
        repairErrors = v.repairErrors

        /*
         * LƯỢT KHAI BÁO cũng phải bị quét văn xuôi.
         *
         * F2 sửa `validateCursorOutput` và nhánh vòng của `validateAnalysisOutput`,
         * nhưng bỏ sót người gọi thứ ba và mới nhất. Hợp đồng của lượt 2 cũng nói
         * "Trả về DUY NHẤT một object JSON" — mà không gì cưỡng chế nó. Mô hình
         * viết một câu nhân quả quanh JSON khai báo thì bản khai vẫn ĐẠT, chặng
         * hợp nhất chạy trên văn xuôi ĐÃ ĐÓNG BĂNG nên không thể thấy, và lần
         * chạy được ghi SUCCEEDED kèm một khẳng định bị cấm không có lớp thất bại nào.
         */
        const prose = scanProseOutsideJson(proseText)
        if (hadProseOutsideJson || prose.issues.length > 0) {
          const extra: ValidationIssue[] = [...prose.issues]
          if (hadProseOutsideJson) {
            extra.push({
              rule: 'prose_outside_json',
              severity: 'BLOCKER',
              message: 'Có văn bản ngoài object JSON — hợp đồng yêu cầu CHỈ một object JSON.',
            })
          }
          declReport = {
            ...v.report,
            passed: false,
            claimIssues: [...v.report.claimIssues, ...prose.issues],
            structuralIssues: [
              ...v.report.structuralIssues,
              ...extra.filter((i) => i.rule === 'prose_outside_json'),
            ],
            causalViolations: v.report.causalViolations + prose.causalViolations,
            ctrViolations: v.report.ctrViolations + prose.ctrViolations,
          }
          declarations = null
          // Khẳng định bị cấm thắng lỗi định dạng; định dạng thuần vẫn thử lại được.
          failureClass =
            prose.causalViolations > 0 || prose.ctrViolations > 0
              ? 'UNSUPPORTED_CLAIM'
              : failureClass === 'NONE'
                ? 'PROSE_OUTSIDE_JSON'
                : failureClass
          repairErrors = [
            ...repairErrors,
            'Trả về DUY NHẤT một object JSON, không kèm văn bản nào ngoài nó.',
            ...(prose.issues.length
              ? [
                  `${prose.issues.length} vi phạm trong VĂN BẢN NGOÀI JSON:\n` +
                    prose.issues.slice(0, 3).map((i) => `  • ${i.message}`).join('\n'),
                ]
              : []),
          ]
        }
      }
    }

    const declPassed = failureClass === 'NONE' && declReport?.passed === true
    const declExecutionId = await persistAttempt({
      workspaceId: params.workspaceId,
      channelId: loaded.channelId,
      analysisRunId: loaded.analysisRunId,
      requestId,
      promptRevisionId,
      attempt,
      parentExecutionId: declParent,
      exec,
      failureClass,
      passed: declPassed,
      report: declReport,
      output: null,
      model: params.model,
      executionRole: 'DECLARATION',
      stage: 'DECLARATION',
      analysisExecutionId: analysisPass.lastExecutionId,
      declarationProvenance: declProvenance,
      persistResult: null,
    })
    declParent = declExecutionId

    const record: AttemptRecord = {
      attemptNumber: attempt,
      llmExecutionId: declExecutionId,
      failureClass,
      passed: declPassed,
      durationMs: exec.durationMs,
      exitCode: exec.exitCode,
      timedOut: exec.timedOut,
      stdoutBytes: exec.stdoutBytes,
      repairErrors,
      report: declReport,
    }
    declarationAttempts.push(record)
    result.declarationAttempts = declarationAttempts
    result.declarationExecutionId = declExecutionId

    if (!declPassed) {
      if (!RETRYABLE.has(failureClass) || attempt === MAX_ATTEMPTS) break
      const rep = buildDeclarationRepairPrompt({
        errors: repairErrors, invalidOutput: json ?? exec.stdout, obligationSet, obligationSetHash,
      })
      if (rep.truncated) {
        record.repairErrors.push('Không thử lại: output trước đó quá dài để đưa vào prompt sửa lỗi.')
        break
      }
      declPromptText = rep.text
      continue
    }

    // --- BẢN KHAI ĐẠT: lưu lại rồi HỢP NHẤT --------------------------------
    const declarationPayload = {
      schemaVersion: DECLARATION_SCHEMA_VERSION,
      obligationSetHash,
      declarations,
    }
    await getDb().insert(schema.cursorDeclarationResult).values({
      workspaceId: params.workspaceId,
      analysisRunId: loaded.analysisRunId,
      channelId: loaded.channelId,
      requestId,
      llmExecutionId: declExecutionId,
      analysisExecutionId: analysisPass.lastExecutionId,
      analysisPayloadHash: obligationSet.analysisHash,
      obligationSetHash,
      declarationCount: declarations!.length,
      payload: declarationPayload,
      payloadHash: createHash('sha256')
        .update(stableStringify(declarationPayload), 'utf8')
        .digest('hex'),
    })

    const loadedInputs = await loadCompositeInputs(analysisPass.lastExecutionId, declExecutionId)
    if ('issues' in loadedInputs) {
      // Thiếu hàng đã lưu -> HỆ THỐNG. Không thử lại: mô hình không gây ra nó.
      result.status = 'FAILED'
      result.compositeFailureClass = 'SYSTEM_OR_INTEGRITY'
      result.systemFailure = {
        stage: 'COMPOSITE',
        message: loadedInputs.issues.map((i) => i.message).join('; '),
      }
      return result
    }

    let outcome: CompositeOutcome
    try {
      outcome = runCompositeStage(
        loadedInputs.inputs, loaded.pkg,
        {
          evidenceIds: built.allowedEvidenceIds,
          videoIds: built.allowedVideoIds,
          cohortKeys: built.allowedCohortKeys,
        },
        compositeProvenance,
      )
    } catch (err) {
      // Validator ném ngoại lệ = trạng thái nội bộ bất khả. HỆ THỐNG, không retry.
      result.status = 'FAILED'
      result.compositeFailureClass = 'SYSTEM_OR_INTEGRITY'
      result.systemFailure = {
        stage: 'COMPOSITE',
        message: `validator ném ngoại lệ: ${err instanceof Error ? err.message : String(err)}`,
      }
      return result
    }

    const persisted = await persistComposite({
      inputs: loadedInputs.inputs,
      outcome,
      failureClass: outcome.ok ? 'NONE' : 'UNSUPPORTED_CLAIM',
    })
    result.compositeReport = outcome.ok ? outcome.result.report : outcome.report
    result.resultId = persisted.resultId
    result.compositeValidationId = persisted.compositeValidationId

    if (outcome.ok) {
      result.declarations = declarations
      result.output = outcome.result.payload as unknown as CursorOutput
      result.compositePayloadHash = outcome.result.payloadHash
      result.status = 'SUCCEEDED'
      return result
    }

    result.compositeFailureClass = outcome.failureClass
    if (outcome.failureClass === 'SYSTEM_OR_INTEGRITY') {
      // Toàn vẹn hỏng: dừng ngay. Thử lại chỉ lặp lại cùng một mâu thuẫn.
      result.status = 'FAILED'
      result.systemFailure = {
        stage: 'COMPOSITE',
        message: outcome.issues.map((i) => i.message).join('; '),
      }
      return result
    }

    // DECLARATION_SEMANTIC: lỗi CỦA BẢN KHAI, thuộc đúng execution này, và SỬA
    // ĐƯỢC — văn xuôi đã đóng băng nên khai lại không đổi được kết luận.
    const semanticErrors = [
      ...(outcome.report?.claimIssues ?? []),
      ...(outcome.report?.qualityIssues ?? []),
    ]
      .filter((i: ValidationIssue) => i.severity === 'BLOCKER' || i.severity === 'HIGH')
      .slice(0, 12)
      .map((i: ValidationIssue) => `${i.rule}${i.path ? ` @ ${i.path}` : ''}: ${i.message}`)
    record.repairErrors = semanticErrors
    record.passed = false

    if (attempt === MAX_ATTEMPTS) break
    const rep = buildDeclarationRepairPrompt({
      errors: semanticErrors,
      invalidOutput: json ?? exec.stdout,
      obligationSet,
      obligationSetHash,
    })
    if (rep.truncated) break
    declPromptText = rep.text
  }

  // Cạn ngân sách khai báo: cả lần chạy THẤT BẠI, nhưng văn xuôi và tập nghĩa vụ
  // vẫn còn nguyên làm bằng chứng.
  result.output = analysisPass.value as unknown as CursorOutput
  const lastDecl = declarationAttempts[declarationAttempts.length - 1]
  result.status =
    lastDecl?.failureClass === 'CLI_TIMEOUT' || lastDecl?.failureClass === 'CLI_NONZERO_EXIT'
      ? 'FAILED'
      : 'REJECTED_SCHEMA'
  return result
}


/**
 * So sánh claim GỐC với claim sau khi sửa lỗi.
 *
 * Trả về danh sách khác biệt về NGỮ NGHĨA. Cách diễn đạt (`text`) được phép
 * đổi — đó chính là thứ đang được sửa. Những gì KHÔNG được đổi là ý nghĩa:
 * chỉ số nào bị phán xét, phán xét gì, ở trạng thái nào, dựa trên bằng chứng gì.
 */
/**
 * Một claim chỉ dùng làm MỐC khi MỌI trường mà phép so đọc tới đều dùng được.
 *
 * Chỉ kiểm `id` là chưa đủ, và để lại hai lỗi:
 *
 *  1. `{"id":"MC-001"}` được nhận làm mốc, rồi `r.evidenceIds.filter(...)` ném
 *     TypeError vì `evidenceIds` là `undefined` — làm hỏng cả lần chạy thay vì
 *     phân loại đúng là thiếu mốc.
 *  2. Root có `id` và đủ trường ngữ nghĩa nhưng THIẾU `sourceSection`; lần sửa
 *     bổ sung đúng trường đó lại bị báo `undefined -> "KEY_FINDING"`, tức từ
 *     chối oan một lần sửa hợp lệ.
 *
 * Nguyên tắc: mốc phải ĐẦY ĐỦ theo nghĩa của phép so, nếu không thì KHÔNG CÓ mốc.
 */
/**
 * Các con số xuất hiện trong một câu, đã chuẩn hoá.
 *
 * Bỏ dấu phân cách nghìn và chuẩn hoá dấu thập phân để "1.000" và "1,000" và
 * "1000" được coi là CÙNG một số — đổi cách viết là diễn đạt, đổi giá trị mới
 * là bịa dữ liệu.
 */
export function numericTokens(text: string): string[] {
  return (text.match(/\d[\d.,]*/g) ?? [])
    .map((n) => n.replace(/[.,](?=\d{3}\b)/g, '').replace(',', '.'))
    .map((n) => String(Number(n)))
    .filter((n) => n !== 'NaN')
    .sort()
}

export function isUsableBaselineClaim(c: unknown): boolean {
  if (typeof c !== 'object' || c === null) return false
  const o = c as Record<string, unknown>
  if (typeof o.id !== 'string' || !/^MC-\d{3}$/.test(o.id)) return false
  // Enum phải THUỘC TẬP HỢP LỆ, không chỉ "chuỗi khác rỗng".
  //
  // `claimType: "OBSERVATON"` (gõ sai) vẫn là chuỗi khác rỗng, nên mốc được
  // nhận; lần sửa chữa lại thành "OBSERVATION" liền bị báo trôi dạt — từ chối
  // oan một lần sửa đúng.
  const ENUMS: Record<string, readonly string[]> = {
    subjectMetric: CLAIM_METRICS,
    relatedMetric: CLAIM_METRICS,
    claimType: claimTypeEnum.options,
    assertionStatus: assertionStatusEnum.options,
    judgement: judgementEnum.options,
  }
  for (const [k, allowed] of Object.entries(ENUMS)) {
    const v = o[k]
    if (typeof v !== 'string' || !allowed.includes(v)) return false
  }
  // `sourceRef` phải đầy đủ và dùng được: thiếu nó thì không có gì để đối chiếu.
  const ref = o.sourceRef as Record<string, unknown> | undefined
  if (typeof ref !== 'object' || ref === null) return false
  if (!claimSourceEnum.options.includes(ref.section as never)) return false
  if (typeof ref.itemId !== 'string') return false
  if (typeof ref.field !== 'string' || ref.field.length === 0) return false
  if (typeof ref.ordinal !== 'number' || !Number.isInteger(ref.ordinal)) return false
  if (!Array.isArray(o.evidenceIds)) return false
  return true
}

/**
 * claim id -> VĂN BẢN ĐÃ PHÂN GIẢI tại ô mà claim đó trỏ tới.
 *
 * Đây là thứ D3/D5 so sánh. Không có nó, `detectSemanticDrift` vẫn chạy nhưng
 * hai phép kiểm mạnh nhất của nó — "nội dung ô không đổi" và "số trong ô không
 * đổi" — im lặng không kiểm gì, vì cả hai đều bỏ qua khi không có văn bản. Đúng
 * kiểu hỏng mà cả Phase 4 sinh ra để chống: một phép kiểm CÓ CHẠY, KHÔNG báo
 * lỗi, và không hề nhìn vào dữ liệu.
 *
 * Nhận `unknown` vì mốc ngữ nghĩa có thể là một output LỎNG (parse được nhưng
 * chưa qua schema). Ô nào không phân giải được thì vắng mặt — và D3 bỏ qua
 * claim đó, có chủ ý: nếu ref của bản gốc vốn đã hỏng, lần sửa PHẢI được phép
 * sửa nó. Danh tính chuẩn tắc `section|itemId|field` vẫn bị khoá, nên khoảng
 * hở này chỉ rộng đúng bằng một lần sửa `ordinal` ngoài phạm vi.
 */
export function resolvedTextByClaim(
  output: unknown,
  claims: CursorOutput['metricClaims'],
): Map<string, string> {
  const out = new Map<string, string>()
  for (const c of claims ?? []) {
    if (!c?.id || !c.sourceRef) continue
    try {
      const res = resolveSourceRef(output as CursorOutput, c.sourceRef)
      if ('ok' in res) out.set(c.id, res.ok.text)
    } catch {
      /* mốc lỏng thiếu hẳn một mảng -> không có văn bản để đối chiếu */
    }
  }
  return out
}

export function detectSemanticDrift(
  root: CursorOutput['metricClaims'],
  repaired: CursorOutput['metricClaims'],
  /** claim id -> văn bản đã phân giải ở output GỐC. */
  rootText: Map<string, string> = new Map(),
  /** claim id -> văn bản đã phân giải ở output ĐÃ SỬA. */
  repairedText: Map<string, string> = new Map(),
): string[] {
  const drift: string[] = []

  // Danh tính claim KHÔNG phụ thuộc thứ tự mảng — đây là lựa chọn có chủ đích.
  //
  // Vị trí trong mảng không mang ngữ nghĩa: `sourceSection`/`sourceId` mới là
  // thứ nói claim thuộc về đâu, và cả hai đều bị khoá bên dưới. Bắt lỗi đảo thứ
  // tự sẽ từ chối oan một lần sửa hoàn toàn hợp lệ.
  //
  // Cái BỊ CẤM là ánh xạ không một-một: tách một claim thành nhiều, gộp nhiều
  // thành một, đổi tên id, hoặc thêm/bớt — tất cả đều là đổi nội dung phân tích
  // chứ không phải sửa định dạng.
  const rootIds = root.map((c) => c.id)
  const repIds = repaired.map((c) => c.id)

  const dupRoot = repIds.filter((id, i) => repIds.indexOf(id) !== i)
  if (dupRoot.length > 0) drift.push(`claim id trùng sau khi sửa: ${[...new Set(dupRoot)].join(', ')}`)

  const added = repIds.filter((id) => !rootIds.includes(id))
  if (added.length > 0) drift.push(`claim MỚI xuất hiện sau khi sửa: ${added.join(', ')}`)
  if (repaired.length !== root.length) {
    drift.push(`số claim đổi: ${root.length} -> ${repaired.length}`)
  }

  const byId = new Map(repaired.map((c) => [c.id, c]))
  for (const r of root) {
    const c = byId.get(r.id)
    if (!c) {
      drift.push(`bỏ mất claim ${r.id}`)
      continue
    }
    for (const k of [
      'subjectMetric',
      'relatedMetric',
      'claimType',
      'assertionStatus',
      'judgement',
    ] as const) {
      if (r[k] !== c[k]) drift.push(`${r.id}.${k}: "${r[k]}" -> "${c[k]}"`)
    }

    // DANH TÍNH CHUẨN TẮC của ô nguồn: section | itemId | field.
    //
    // KHÔNG được đổi, kể cả khi ô mới có nội dung y hệt. Hai mục khác nhau có
    // thể chứa cùng một câu; cho phép nhảy sang mục khác vì "văn bản giống" là
    // cho phép đổi CHỦ SỞ HỮU của kết luận mà không ai thấy.
    //
    // Chỉ `ordinal` — dữ liệu vị trí suy ra — được phép đổi sau khi đảo thứ tự.
    //
    // Đọc PHÒNG THỦ: mốc có thể là dữ liệu đã lưu từ một lần chạy cũ, và một mốc
    // thiếu `sourceRef` KHÔNG được phép làm sập cả vòng sửa lỗi. Thiếu thì canon
    // thành "(thiếu)" — khác mọi canon thật, nên nó BÁO TRÔI DẠT (fail-closed)
    // thay vì ném ngoại lệ hay im lặng cho qua.
    const canonOf = (x: { sourceRef?: { section?: string; itemId?: string; field?: string } }) =>
      x.sourceRef ? `${x.sourceRef.section}|${x.sourceRef.itemId}|${x.sourceRef.field}` : '(thiếu sourceRef)'
    const rCanon = canonOf(r)
    const cCanon = canonOf(c)
    if (rCanon !== cCanon) {
      drift.push(`${r.id}.sourceRef: "${rCanon}" -> "${cCanon}"`)
    }
    // BẰNG CHỨNG ĐÓNG BĂNG trong lần sửa lỗi kỹ thuật.
    //
    // Bản trước chỉ chặn việc BỚT, cho phép THÊM. Nhưng thêm bằng chứng biến một
    // khẳng định vốn không có căn cứ thành một phân tích KHÁC — mà "thiếu bằng
    // chứng" vốn là thất bại NỘI DUNG, không được retry ngay từ đầu. Vậy một
    // lần sửa KỸ THUẬT không bao giờ có lý do chính đáng để thêm bằng chứng.
    //
    // Thiếu bằng chứng => phải chạy lại một execution GỐC mới.
    // SỐ trong VĂN BẢN ĐƯỢC TRỎ TỚI là dữ liệu, không phải cách diễn đạt.
    //
    // Sửa lỗi kỹ thuật được phép viết lại câu, nhưng KHÔNG được đổi con số:
    // "views_d7 là 100" -> "views_d7 là 1.000" giữ nguyên mọi trường được so,
    // nên lọt hoàn toàn — trong khi đó là bịa lại dữ liệu.
    const rootNums = numericTokens(rootText.get(r.id) ?? '')
    const repNums = numericTokens(repairedText.get(c.id) ?? '')
    if (rootNums.join(',') !== repNums.join(',')) {
      drift.push(`${r.id} đổi SỐ trong text: [${rootNums.join(', ')}] -> [${repNums.join(', ')}]`)
    }

    // Nội dung ô được trỏ tới KHÔNG được đổi.
    const rt = rootText.get(r.id)
    const ct = repairedText.get(c.id)
    if (rt !== undefined && ct !== undefined && rt.trim() !== ct.trim()) {
      drift.push(`${r.id}: văn bản ô nguồn đã đổi`)
    }

    const lost = r.evidenceIds.filter((e) => !c.evidenceIds.includes(e))
    const gained = c.evidenceIds.filter((e) => !r.evidenceIds.includes(e))
    if (lost.length > 0) drift.push(`${r.id} mất bằng chứng: ${lost.join(', ')}`)
    if (gained.length > 0) drift.push(`${r.id} THÊM bằng chứng: ${gained.join(', ')}`)
  }
  return drift
}

interface PersistAttemptArgs {
  workspaceId: string
  channelId: string
  analysisRunId: string
  requestId: string
  promptRevisionId: string
  attempt: number
  parentExecutionId: string | null
  exec: CursorExecResult
  failureClass: string
  passed: boolean
  report: ValidationReport | null
  output: CursorOutput | null
  model?: string

  /** Vai của lượt này. Quyết định bản kê, chặng kiểm định và vai kết quả. */
  executionRole: ExecutionRole
  /** Chặng kiểm định của dòng phán quyết ghi kèm. */
  stage: ValidationStage
  /** Chỉ lượt KHAI BÁO: lượt phân tích mà nó phục vụ. */
  analysisExecutionId?: string | null
  /** Chỉ lượt KHAI BÁO: bộ nguồn gốc của hợp đồng lượt 2. */
  declarationProvenance?: {
    obligationGeneratorVersion: string
    declarationPromptVersion: string
    declarationPromptSourceHash: string
    compositeValidatorVersion: string
    analysisPayloadHash: string
    obligationSetHash: string
  }
  /** Payload bất biến cần ghi kèm khi lượt này ĐẠT. G4 chỉ ghi vai ANALYSIS. */
  persistResult?: { role: 'ANALYSIS'; payload: unknown; payloadHash: string } | null
}

/**
 * Ghi MỘT lần thử.
 *
 * Mọi lần thử đều được giữ, kể cả lần hỏng — đề bài yêu cầu "giữ lại mọi lần
 * thử". Nhờ đó về sau còn kiểm được: mô hình đã sai ở đâu, sửa được sau mấy
 * lần, và có phải lần "đạt" chỉ là kết quả của việc thử nhiều lần hay không.
 */
async function persistAttempt(args: PersistAttemptArgs): Promise<string> {
  return withTransaction(async (tx) => {
    // `iteration` dành cho vòng tinh chỉnh prompt của Phase 5, KHÔNG phải retry
    // kỹ thuật. Ở Phase 4 luôn bằng 1; số lần thử nằm ở manifest.
    //
    // Trạng thái SUCCEEDED bị CHECK `llm_execution_succeeded_has_result` ràng
    // buộc phải có kết quả kèm theo, nên không thể chèn SUCCEEDED trước rồi gắn
    // kết quả sau. Chèn ở trạng thái RUNNING, gắn kết quả, rồi mới chốt.
    // Số thứ tự lần chạy kế tiếp cho (run, provider). Khoá duy nhất trên cột
    // này sẽ bắt được va chạm nếu có hai tiến trình cùng ghi.
    const seqRow = await tx.execute<{ next: string }>(sql`
      SELECT COALESCE(MAX(execution_sequence), 0) + 1 AS next
      FROM llm_execution
      WHERE analysis_run_id = ${args.analysisRunId} AND provider = 'CURSOR_CLI'
    `)
    const executionSequence = Number(seqRow.rows[0]?.next ?? 1)

    const [exe] = await tx
      .insert(schema.llmExecution)
      .values({
        workspaceId: args.workspaceId,
        analysisRunId: args.analysisRunId,
        executionSequence,
        promptRevisionId: args.promptRevisionId,
        provider: selectedProvider(),
        model: args.model ?? null,
        iteration: 1,
        status: args.passed ? 'RUNNING' : args.exec.timedOut ? 'TIMED_OUT' : 'REJECTED_SCHEMA',
        rawOutputHash: args.exec.stdoutHash,
        validationError: args.passed
          ? null
          : {
              failureClass: args.failureClass,
              structural: args.report?.structuralIssues ?? [],
              evidence: args.report?.evidenceIssues ?? [],
              claims: args.report?.claimIssues ?? [],
            },
        startedAt: args.exec.startedAt,
        finishedAt: args.exec.finishedAt,
        durationMs: args.exec.durationMs,
      })
      .returning({ id: schema.llmExecution.id })

    const llmExecutionId = exe!.id

    // THỨ TỰ GHI QUAN TRỌNG: bản kê -> kiểm định -> kết quả.
    //
    // Trigger `cursor_result_semantic_lineage` đối chiếu kết quả với bản kê và
    // với dòng kiểm định. Ghi kết quả TRƯỚC thì cả hai chưa tồn tại, và trigger
    // từ chối mọi lần chạy thật. Test tích hợp là thứ phát hiện ra điều này
    // trước khi nó kịp làm hỏng một lô đo ổn định.
    // Bản kê thực thi — không lưu dòng lệnh đầy đủ, không lưu môi trường.
    await tx.insert(schema.cursorExecutionManifest).values({
      workspaceId: args.workspaceId,
      analysisRunId: args.analysisRunId,
      llmExecutionId,
      requestId: args.requestId,
      attemptNumber: args.attempt,
      parentExecutionId: args.parentExecutionId,
      toolName: args.exec.toolName,
      model: args.model ?? null,
      flags: args.exec.flags,
      startedAt: args.exec.startedAt,
      finishedAt: args.exec.finishedAt,
      durationMs: args.exec.durationMs,
      exitCode: args.exec.exitCode,
      timedOut: args.exec.timedOut,
      stdoutHash: args.exec.stdoutHash,
      stdoutBytes: args.exec.stdoutBytes,
      stderrHash: args.exec.stderrHash,
      stderrExcerpt: args.exec.stderr.slice(0, 2000),
      outputSchemaVersion: args.output ? ANALYSIS_SCHEMA_VERSION : null,
      executionRole: args.executionRole,
      analysisExecutionId: args.analysisExecutionId ?? null,
      ...(args.declarationProvenance ?? {}),
      // Nguồn gốc phiên bản — gắn lúc tạo, dùng để chặn chuỗi retry trộn bản.
      //
      // `schemaVersion` là bản của LƯỢT PHÂN TÍCH ở CẢ HAI vai, có chủ đích: nó
      // định danh HỌ hợp đồng, và trigger 0020 dùng nó để chặn chuỗi thử lại
      // trộn bản. Bản riêng của lượt khai báo nằm ở `declaration_prompt_version`.
      schemaVersion: ANALYSIS_SCHEMA_VERSION,
      promptVersion: PROMPT_VERSION,
      validatorHash: VALIDATOR_HASH,
      schemaHash: SCHEMA_HASH,
      promptSourceHash: PROMPT_SOURCE_HASH,
      /*
       * Năm băm còn lại của hợp đồng (0035, M-3).
       *
       * Chép từ `CONTRACT_PROVENANCE` — cùng một nguồn với `_meta` của hiện vật
       * và với `INDEX.json`. Chỉ khi cả ba bề mặt chép từ MỘT nguồn thì phép so
       * giữa chúng mới có nghĩa; mỗi bề mặt tự gom lấy thì chúng lệch nhau mà
       * không ai thấy.
       */
      obligationGeneratorHash: CONTRACT_PROVENANCE.obligationGeneratorHash,
      compositeSourceHash: CONTRACT_PROVENANCE.compositeSourceHash,
      sensitiveLexiconHash: CONTRACT_PROVENANCE.sensitiveLexiconHash,
      identitySourceHash: CONTRACT_PROVENANCE.identitySourceHash,
      provenanceSourceHash: CONTRACT_PROVENANCE.provenanceSourceHash,
      failureClass: args.failureClass as never,
    })

    // Báo cáo kiểm định — lưu TÁCH RIÊNG khỏi output gốc.
    if (args.report) {
      await tx.insert(schema.analysisValidation).values({
        workspaceId: args.workspaceId,
        analysisRunId: args.analysisRunId,
        llmExecutionId,
        channelId: args.channelId,
        stage: args.stage,
        passed: args.report.passed,
        failureClass: args.failureClass as never,
        structuralIssues: args.report.structuralIssues,
        evidenceIssues: args.report.evidenceIssues,
        claimIssues: args.report.claimIssues,
        qualityIssues: args.report.qualityIssues,
        evidenceResolutionRate:
          args.report.evidenceResolutionRate === null
            ? null
            : String(args.report.evidenceResolutionRate),
        totalEvidenceRefs: args.report.totalEvidenceRefs,
        unresolvedEvidenceRefs: args.report.unresolvedEvidenceRefs,
        causalViolations: args.report.causalViolations,
        ctrViolations: args.report.ctrViolations,
        unsupportedMetricViolations: args.report.unsupportedMetricViolations,
        findingCount: args.report.counts.findings,
        hypothesisCount: args.report.counts.hypotheses,
        recommendationCount: args.report.counts.recommendations,
        experimentCount: args.report.counts.experiments,
      })
    }

    // Kết quả đã validate: khoá theo LẦN CHẠY, không theo lần phân tích, để
    // các lần chạy lặp lại (đo độ ổn định) không ghi đè nhau.
    // Kết quả BẤT BIẾN của lượt này.
    //
    // G4 chỉ ghi vai ANALYSIS: văn xuôi đã đóng băng, làm đầu vào cho bộ sinh
    // nghĩa vụ. Kết quả HỢP NHẤT (vai COMPOSITE) là việc của chặng hợp nhất —
    // không ghi ở đây, và trigger 0026 sẽ từ chối nếu ai đó thử.
    if (args.passed && args.persistResult) {
      await tx.insert(schema.cursorAnalysisResult).values({
        workspaceId: args.workspaceId,
        analysisRunId: args.analysisRunId,
        llmExecutionId,
        requestId: args.requestId,
        channelId: args.channelId,
        schemaVersion: ANALYSIS_SCHEMA_VERSION,
        resultRole: args.persistResult.role,
        payload: args.persistResult.payload as never,
        payloadHash: args.persistResult.payloadHash,
      })
      // Chốt trạng thái SAU khi đã có kết quả, để CHECK của Phase 1 được thoả.
      // `analysisResultId` để NULL: Cursor result nằm ở bảng riêng.
      await tx
        .update(schema.llmExecution)
        .set({ status: 'SUCCEEDED', analysisResultId: null })
        .where(eq(schema.llmExecution.id, llmExecutionId))
    }

    return llmExecutionId
  })
}
