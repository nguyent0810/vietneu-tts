import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { and, eq, sql } from 'drizzle-orm'

import { getDb, withTransaction } from '@/db/client'
import * as schema from '@/db/schema'
import type { AnalysisPackage } from '../analysis/package'
import { stableStringify } from '../analysis/package'
import { extractJson, runCursor, type CursorExecResult } from './exec'
import { buildPrompt, buildRepairPrompt, PROMPT_VERSION, type BuiltPrompt } from './prompt'
import {
  assertionStatusEnum,
  CLAIM_METRICS,
  OUTPUT_LIMITS,
  claimSourceEnum,
  claimTypeEnum,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  judgementEnum,
  type CursorOutput,
} from './schema'
import { validateCursorOutput, type ValidationReport } from './validate'

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
  attempts: AttemptRecord[]
  finalAttempt: number | null
  output: CursorOutput | null
  report: ValidationReport | null
  status: 'SUCCEEDED' | 'REJECTED_SCHEMA' | 'FAILED'
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

export async function runCursorAnalysis(
  params: RunCursorAnalysisParams,
): Promise<RunCursorAnalysisResult> {
  const loaded = await loadPackage(params.workspaceId, params.channelLabel, params.analysisPackageId)

  const built: BuiltPrompt = buildPrompt({ pkg: loaded.pkg })
  const attempts: AttemptRecord[] = []

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

  /** metricClaims của lần chạy GỐC, dùng để phát hiện trôi dạt ở lần sửa lỗi. */
  let rootClaims: CursorOutput['metricClaims'] | null = null
  let promptText = built.text
  let finalOutput: CursorOutput | null = null
  let finalReport: ValidationReport | null = null
  let finalAttempt: number | null = null
  let parentExecutionId: string | null = null

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const exec = await runCursor({
      prompt: promptText,
      sandboxDir: params.sandboxDir,
      timeoutMs: params.timeoutMs,
      model: params.model,
    })

    const execFailure = classifyExec(exec)
    const { json, hadProseOutsideJson, proseText } = extractJson(exec.stdout)

    let failureClass = execFailure ?? 'NONE'
    let report: ValidationReport | null = null
    let output: CursorOutput | null = null
    let repairErrors: string[] = []

    if (!execFailure) {
      if (!json) {
        failureClass = 'INVALID_JSON'
        repairErrors = ['Không tìm thấy object JSON nào trong output.']
      } else {
        const validated = validateCursorOutput({
          raw: json,
          pkg: loaded.pkg,
          allowedEvidenceIds: built.allowedEvidenceIds,
          allowedVideoIds: built.allowedVideoIds,
          allowedCohortKeys: built.allowedCohortKeys,
          hadProseOutsideJson,
          proseText,
        })
        report = validated.report
        output = validated.output
        failureClass = validated.failureClass
        repairErrors = validated.repairErrors

        // SỬA LỖI KỸ THUẬT KHÔNG ĐƯỢC ĐỔI NGỮ NGHĨA.
        //
        // Prompt sửa lỗi nói "chỉ sửa lỗi định dạng, giữ nguyên kết luận". Đó
        // là một LỜI DẶN, không phải một ràng buộc. Không kiểm thì một lần sửa
        // có thể lặng lẽ bỏ metricClaims, hạ ASSERTED xuống LIMITATION, hoặc
        // rút evidenceIds — và kết quả "đạt" khi ấy là của một phân tích KHÁC
        // với phân tích đã bị từ chối.
        //
        // Ranh giới: sửa KỸ THUẬT được phép đổi cú pháp và cách diễn đạt; PHÂN
        // TÍCH LẠI là một thao tác khác, và hiện không được mô hình hoá ở tầng
        // này. Nếu về sau cần, nó phải là một execution gốc mới, không phải một
        // lần sửa lỗi.
        // KHÔNG CÓ MỐC NGỮ NGHĨA thì không được coi là đã kiểm chứng.
        //
        // Root có JSON hỏng hoàn toàn -> không có gì để đối chiếu. Cho một lần
        // sửa như thế "đạt" nghĩa là tuyên bố đã giữ nguyên kết luận trong khi
        // không hề biết kết luận gốc là gì. Chính sách: khôi phục cú pháp thì
        // được, nhưng phải chạy lại một execution GỐC mới — không tự động đạt.
        if (attempt > 1 && rootClaims === null && output !== null) {
          failureClass = 'UNSUPPORTED_CLAIM'
          output = null
          repairErrors = [
            'SEMANTIC_BASELINE_UNAVAILABLE: output gốc không parse được, hoặc metricClaims ' +
              'thiếu danh tính (id), nên không có mốc để đối chiếu ngữ nghĩa. Cần chạy lại một ' +
              'lần phân tích GỐC, không dùng lần sửa này.',
          ]
          if (report) {
            report.passed = false
            report.qualityIssues.push({
              rule: 'semantic_baseline_unavailable',
              severity: 'HIGH',
              message:
                'Lần sửa lỗi không có mốc ngữ nghĩa để đối chiếu (output gốc hỏng JSON). ' +
                'Không được tính là thành công không giám sát.',
            })
          }
        }

        if (attempt > 1 && rootClaims !== null && output !== null) {
          const drift = detectSemanticDrift(rootClaims, output.metricClaims)
          if (drift.length > 0) {
            failureClass = 'UNSUPPORTED_CLAIM'
            output = null
            repairErrors = [
              'Lần sửa lỗi đã ĐỔI NGỮ NGHĨA so với output gốc, không chỉ sửa định dạng: ' +
                drift.slice(0, 5).join('; '),
            ]
            if (report) report.passed = false
          }
        }
        if (attempt === 1 && validated.output) rootClaims = validated.output.metricClaims
        // Kể cả khi lần đầu hỏng kiểm định, vẫn giữ lại claim để đối chiếu —
        // miễn là JSON đã parse được.
        if (attempt === 1 && rootClaims === null) {
          try {
            const loose = JSON.parse(json) as { metricClaims?: unknown }
            // MỐC NGỮ NGHĨA chỉ hợp lệ khi mọi claim có DANH TÍNH đầy đủ.
            //
            // Bản trước nhận cả claim THIẾU `id`. Ca thật ở lô cấu trúc: root
            // hỏng schema vì thiếu `id`/`sourceSection`; lần sửa bổ sung đúng
            // các trường đó; phép so danh tính thấy 23 claim "mới" và 4 claim
            // "undefined" bị mất, rồi báo ĐỔI NGỮ NGHĨA. Lần sửa hoàn toàn
            // đúng, chỉ có phép so là sai.
            //
            // Không có danh tính thì không có gì để bảo toàn: coi như KHÔNG CÓ
            // mốc, và nhánh SEMANTIC_BASELINE_UNAVAILABLE ở trên sẽ chặn.
            // Root VƯỢT TRẦN mảng thì không có mốc dùng được.
            //
            // Cách sửa duy nhất khả dĩ là XOÁ BỚT claim, mà quy tắc bất biến
            // ngữ nghĩa lại cấm xoá. Nhận nó làm mốc sẽ tạo bế tắc và báo sai
            // thành "đổi ngữ nghĩa". Không có mốc thì phân loại đúng là
            // SEMANTIC_BASELINE_UNAVAILABLE và đòi chạy lại một lần GỐC.
            const withinCap =
              Array.isArray(loose.metricClaims) &&
              loose.metricClaims.length <= OUTPUT_LIMITS.metricClaims
            if (withinCap && (loose.metricClaims as unknown[]).every(isUsableBaselineClaim)) {
              rootClaims = loose.metricClaims as CursorOutput['metricClaims']
            }
          } catch {
            /* JSON hỏng -> không có gì để đối chiếu, đúng như mong đợi */
          }
        }
      }
    } else {
      repairErrors = [`Cursor CLI thất bại: ${execFailure}`]
    }

    const passed = failureClass === 'NONE' && report?.passed === true

    let llmExecutionId: string | null = null
    if (!params.dryRun && requestId && promptRevisionId) {
      llmExecutionId = await persistAttempt({
        workspaceId: params.workspaceId,
        channelId: loaded.channelId,
        analysisRunId: loaded.analysisRunId,
        requestId,
        promptRevisionId,
        attempt,
        parentExecutionId,
        exec,
        failureClass,
        passed,
        report,
        output,
        model: params.model,
      })
      parentExecutionId = llmExecutionId
    }

    attempts.push({
      attemptNumber: attempt,
      llmExecutionId,
      failureClass,
      passed,
      durationMs: exec.durationMs,
      exitCode: exec.exitCode,
      timedOut: exec.timedOut,
      stdoutBytes: exec.stdoutBytes,
      repairErrors,
      report,
    })

    if (passed) {
      finalOutput = output
      finalReport = report
      finalAttempt = attempt
      break
    }

    // Chỉ thử lại với thất bại KỸ THUẬT. Thất bại nội dung dừng ngay tại đây.
    if (!RETRYABLE.has(failureClass)) break
    if (attempt === MAX_ATTEMPTS) break

    const repair = buildRepairPrompt({ errors: repairErrors, invalidOutput: json ?? exec.stdout })
    // Không thử lại khi output cũ không lọt trọn vào prompt sửa lỗi: mô hình sẽ
    // phải viết lại phần nó không nhìn thấy, mà không có bằng chứng trong tay.
    // Một lần "đạt" sinh ra như thế không phản ánh bằng chứng nào.
    if (repair.truncated) {
      attempts[attempts.length - 1]!.repairErrors.push(
        'Không thử lại: output trước đó quá dài để đưa trọn vào prompt sửa lỗi.',
      )
      break
    }
    promptText = repair.text
  }

  const last = attempts[attempts.length - 1]!
  const status: RunCursorAnalysisResult['status'] = finalOutput
    ? 'SUCCEEDED'
    : last.failureClass === 'CLI_TIMEOUT' || last.failureClass === 'CLI_NONZERO_EXIT'
      ? 'FAILED'
      : 'REJECTED_SCHEMA'

  return {
    requestId,
    channelLabel: params.channelLabel,
    packageHash: loaded.packageHash,
    promptHash: built.hash,
    promptBytes: built.bytes,
    attempts,
    finalAttempt,
    output: finalOutput,
    report: finalReport,
    status,
  }
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
    const rCanon = `${r.sourceRef.section}|${r.sourceRef.itemId}|${r.sourceRef.field}`
    const cCanon = `${c.sourceRef.section}|${c.sourceRef.itemId}|${c.sourceRef.field}`
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
        provider: 'CURSOR_CLI',
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
      outputSchemaVersion: args.output ? CURSOR_OUTPUT_SCHEMA_VERSION : null,
      // Nguồn gốc phiên bản — gắn lúc tạo, dùng để chặn chuỗi retry trộn bản.
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      promptVersion: PROMPT_VERSION,
      validatorHash: VALIDATOR_HASH,
      schemaHash: SCHEMA_HASH,
      promptSourceHash: PROMPT_SOURCE_HASH,
      failureClass: args.failureClass as never,
    })

    // Báo cáo kiểm định — lưu TÁCH RIÊNG khỏi output gốc.
    if (args.report) {
      await tx.insert(schema.analysisValidation).values({
        workspaceId: args.workspaceId,
        analysisRunId: args.analysisRunId,
        llmExecutionId,
        channelId: args.channelId,
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
    if (args.passed && args.output) {
      const payloadHash = createHash('sha256')
        .update(stableStringify(args.output), 'utf8')
        .digest('hex')
      await tx.insert(schema.cursorAnalysisResult).values({
        workspaceId: args.workspaceId,
        analysisRunId: args.analysisRunId,
        llmExecutionId,
        requestId: args.requestId,
        channelId: args.channelId,
        schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
        payload: args.output,
        payloadHash,
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
