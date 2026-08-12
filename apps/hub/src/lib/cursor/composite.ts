import { createHash } from 'node:crypto'

import { eq, sql } from 'drizzle-orm'

import { getDb, withTransaction } from '@/db/client'
import * as schema from '@/db/schema'
import type { AnalysisPackage } from '../analysis/package'
import { stableStringify } from '../analysis/package'
import {
  buildObligationSet,
  checkDeclarationIdentity,
  checkObligationBelongsTo,
  checkObligationSetHash,
  checkObligationSourcesIntact,
  composeMetricClaims,
  hashAnalysisPayload,
  hashObligationSet,
} from './obligation'
import {
  claimObligationSetSchema,
  COMPOSITE_VALIDATOR_VERSION,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  cursorOutputSchema,
  declarationOutputSchema,
  OBLIGATION_GENERATOR_VERSION,
  type ClaimObligationSet,
  type CursorAnalysis,
  type CursorOutput,
} from './schema'
import { validateCursorOutput, type ValidationIssue, type ValidationReport } from './validate'

/**
 * CHẶNG HỢP NHẤT — phán quyết CUỐI CÙNG, và là chặng DUY NHẤT cấp phép cho một
 * kết quả chính thức.
 *
 * Nguyên tắc chi phối toàn tệp: **không tin gì trong bộ nhớ**. Mọi đầu vào được
 * ĐỌC LẠI TỪ DATABASE và đối chiếu lại băm trước khi ghép. Lý do không phải hình
 * thức — giữa lượt phân tích và chặng này có hai lời gọi LLM, nhiều phút, và một
 * vòng đi qua JSONB. Bất cứ thứ gì còn nằm trong RAM đều KHÔNG chứng minh được
 * nó vẫn là thứ đã được kiểm định.
 *
 * Thất bại ở đây chia làm HAI LOẠI và được đối xử ngược nhau — xem
 * `CompositeFailureClass`. Gộp chúng lại là sai cả hai chiều: coi tất cả là lỗi
 * hệ thống thì một bản khai sai ngữ nghĩa không bao giờ được sửa; coi tất cả là
 * lỗi mô hình thì một lỗi lập trình bị đếm vào cột "mô hình thất bại" của lô đo.
 */

export interface CompositeInputs {
  analysisExecutionId: string
  declarationExecutionId: string
  analysis: CursorAnalysis
  analysisPayloadHash: string
  obligationSet: ClaimObligationSet
  obligationSetHash: string
  generatorVersion: string
  declarations: Array<{ id: string } & Record<string, unknown>>
  declaredObligationSetHash: string
  requestId: string
  channelId: string
  analysisRunId: string
  workspaceId: string
}

/**
 * HAI LOẠI thất bại của chặng hợp nhất — và chúng phải được đối xử NGƯỢC NHAU.
 *
 * `SYSTEM_OR_INTEGRITY`: thiếu hàng đã lưu, lineage/vai/băm lệch, văn xuôi hay
 * tập nghĩa vụ bị đổi, ghép hoặc ghi hỏng, validator ném ngoại lệ. Mọi thứ ở đây
 * chỉ so những gì THUẬT TOÁN đã sinh và database đã lưu — mô hình không có cách
 * nào làm chúng sai. Bảo nó "thử lại" là đổ lỗi nhầm chỗ và che mất một lỗi
 * thật. KHÔNG retry, và KHÔNG tính là mô hình thất bại.
 *
 * `DECLARATION_SEMANTIC`: S1–S8, phân cực, tình thái, chiều phán xét, chủ ngữ,
 * nhân quả, P0, và bằng chứng (kể cả `evidence_support_unverified`). Đây là lỗi
 * của BẢN KHAI, thuộc về đúng execution khai báo đã sinh ra nó.
 *
 * Vì sao DECLARATION_SEMANTIC ĐƯỢC phép thử lại, trong khi hợp đồng một lượt
 * cấm retry lỗi ngữ nghĩa: ở kiến trúc hai lượt, VĂN XUÔI ĐÃ ĐÓNG BĂNG. Một lần
 * khai lại không thể đổi kết luận — nó chỉ có thể dán nhãn lại cho những kết
 * luận đã cố định. Không gian khai hợp lệ cho một ô do chính chữ trong ô đó quy
 * định, nên "thử lại" ở đây là "gắn nhãn cho đúng", không phải "nói lại cho vừa ý".
 *
 * RỦI RO CÒN LẠI, ghi rõ: mô hình vẫn có thể dò dần tới một bộ nhãn lọt lưới S.
 * Trần lần thử là thứ giới hạn điều đó, và mọi lần thử hỏng đều được lưu lại để
 * đọc — một lần "đạt ở lần thứ ba" nhìn khác hẳn một lần "đạt ngay".
 */
export type CompositeFailureClass = 'SYSTEM_OR_INTEGRITY' | 'DECLARATION_SEMANTIC'

export type CompositeOutcome =
  | { ok: true; result: CompositeSuccess }
  | {
      ok: false
      failureClass: CompositeFailureClass
      issues: ValidationIssue[]
      report: ValidationReport | null
    }

export interface CompositeSuccess {
  payload: CursorOutput & { _meta: Record<string, unknown> }
  payloadHash: string
  report: ValidationReport
  claimCount: number
}

const blocker = (rule: string, message: string, path?: string): ValidationIssue => ({
  rule,
  severity: 'BLOCKER',
  message,
  path,
})

/**
 * ĐỌC LẠI toàn bộ đầu vào của chặng hợp nhất từ database.
 *
 * Trả `null` kèm lý do khi thiếu một mảnh — thiếu là chặn, không phải bỏ qua.
 */
export async function loadCompositeInputs(
  analysisExecutionId: string,
  declarationExecutionId: string,
): Promise<{ inputs: CompositeInputs } | { issues: ValidationIssue[] }> {
  const db = getDb()
  const issues: ValidationIssue[] = []

  const analysisRow = (
    await db.execute<{
      payload: unknown
      payload_hash: string
      request_id: string
      channel_id: string
      analysis_run_id: string
      workspace_id: string
    }>(sql`
      SELECT payload, payload_hash, request_id, channel_id, analysis_run_id, workspace_id
      FROM cursor_analysis_result
      WHERE llm_execution_id = ${analysisExecutionId} AND result_role = 'ANALYSIS'
      LIMIT 1`)
  ).rows[0]
  if (!analysisRow) {
    return {
      issues: [
        blocker(
          'composite_missing_analysis_payload',
          `Không có payload PHÂN TÍCH đã lưu cho execution ${analysisExecutionId}.`,
        ),
      ],
    }
  }

  // Băm VĂN XUÔI ĐÃ LƯU, tính lại từ payload chứ không đọc cột.
  //
  // Mọi phép neo phía dưới quy về giá trị này, nên nó phải đến từ dữ liệu thật.
  // Lấy từ cột `payload_hash` sẽ biến ba phép kiểm dưới đây thành phép so cột
  // với chính nó — luôn đúng, không chứng minh gì.
  // `hashAnalysisPayload`, KHÔNG phải `hashText`: hàm sau chuẩn hoá khoảng
  // trắng trước khi băm, nên hai hàm cho hai giá trị khác nhau trên cùng một
  // payload. Dùng nhầm hàm ở đây sẽ chặn MỌI lần chạy hợp lệ.
  const analysisHash = hashAnalysisPayload(analysisRow.payload as CursorAnalysis)
  if (analysisHash !== analysisRow.payload_hash) {
    issues.push(
      blocker(
        'composite_analysis_payload_hash_mismatch',
        `Văn xuôi đã lưu KHÔNG khớp băm của chính nó: cột ${analysisRow.payload_hash.slice(0, 12)}…, ` +
          `tính lại ${analysisHash.slice(0, 12)}….`,
      ),
    )
  }

  const obligationRow = (
    await db.execute<{
      obligations: unknown
      analysis_hash: string
      obligation_set_hash: string
      generator_version: string
      obligation_count: number
    }>(sql`
      SELECT obligations, analysis_hash, obligation_set_hash, generator_version, obligation_count
      FROM cursor_claim_obligation
      WHERE analysis_execution_id = ${analysisExecutionId}
      LIMIT 1`)
  ).rows[0]
  if (!obligationRow) {
    return {
      issues: [
        blocker(
          'composite_missing_obligation_set',
          `Lượt phân tích ${analysisExecutionId} chưa có tập nghĩa vụ.`,
        ),
      ],
    }
  }

  const declarationRow = (
    await db.execute<{
      payload: unknown
      analysis_execution_id: string
      analysis_payload_hash: string
      obligation_set_hash: string
      payload_hash: string
      declaration_count: number
    }>(sql`
      SELECT payload, analysis_execution_id, analysis_payload_hash, obligation_set_hash,
             payload_hash, declaration_count
      FROM cursor_declaration_result
      WHERE llm_execution_id = ${declarationExecutionId}
      LIMIT 1`)
  ).rows[0]
  if (!declarationRow) {
    return {
      issues: [
        blocker(
          'composite_missing_declaration_payload',
          `Không có bản khai đã lưu cho execution ${declarationExecutionId}.`,
        ),
      ],
    }
  }

  // BĂM CỦA CHÍNH HÀNG ĐÃ LƯU — tính lại, không tin cột.
  //
  // Các phép kiểm phía dưới đều đọc `payload`; không phép nào chứng minh
  // `payload` ĐÚNG LÀ thứ mà `payload_hash` đại diện. Một lần ghi hỏng (hoặc một
  // script ghi thẳng) đặt payload B cạnh hash của payload A sẽ đi lọt toàn bộ:
  // B hợp schema, B mang đúng `obligationSetHash`, B qua S1–S8 — và được cấp
  // phép làm hiện vật chính thức trong khi hàng tự nói nó là A.
  const recomputed = createHash('sha256')
    .update(stableStringify(declarationRow.payload), 'utf8')
    .digest('hex')
  if (recomputed !== declarationRow.payload_hash) {
    issues.push(
      blocker(
        'composite_declaration_payload_hash_mismatch',
        `Bản khai đã lưu KHÔNG khớp băm của chính nó: cột ${declarationRow.payload_hash.slice(0, 12)}…, ` +
          `tính lại ${recomputed.slice(0, 12)}….`,
      ),
    )
  }

  // Cột neo của bản khai phải khớp băm văn xuôi THẬT, không chỉ khớp lẫn nhau.
  if (declarationRow.analysis_payload_hash !== analysisHash) {
    issues.push(
      blocker(
        'composite_declaration_analysis_hash_mismatch',
        `Cột neo văn xuôi của bản khai là ${declarationRow.analysis_payload_hash.slice(0, 12)}…, ` +
          `nhưng văn xuôi đã lưu băm ra ${analysisHash.slice(0, 12)}….`,
      ),
    )
  }

  // Hàng tập nghĩa vụ cũng phải tự nhất quán: cột `analysis_hash` là thứ neo
  // O-INV-1, và nó chưa từng được đối chiếu ở đâu.
  if (obligationRow.analysis_hash !== analysisHash) {
    issues.push(
      blocker(
        'composite_obligation_analysis_hash_mismatch',
        `Tập nghĩa vụ neo vào ${obligationRow.analysis_hash.slice(0, 12)}…, ` +
          `văn xuôi đã lưu băm ra ${analysisHash.slice(0, 12)}….`,
      ),
    )
  }

  // LINEAGE: bản khai phải trỏ về ĐÚNG lượt phân tích đang được hợp nhất.
  if (declarationRow.analysis_execution_id !== analysisExecutionId) {
    issues.push(
      blocker(
        'composite_declaration_wrong_analysis',
        `Bản khai thuộc lượt phân tích ${declarationRow.analysis_execution_id}, ` +
          `không phải ${analysisExecutionId}.`,
      ),
    )
  }

  const obligationParse = claimObligationSetSchema.safeParse(obligationRow.obligations)
  if (!obligationParse.success) {
    issues.push(
      blocker('composite_obligation_set_malformed', 'Tập nghĩa vụ đã lưu không đúng hình dạng.'),
    )
  }
  const declarationParse = declarationOutputSchema.safeParse(declarationRow.payload)
  if (!declarationParse.success) {
    issues.push(
      blocker('composite_declaration_malformed', 'Bản khai đã lưu không đúng hình dạng.'),
    )
  }
  if (issues.length > 0) return { issues }

  return {
    inputs: {
      analysisExecutionId,
      declarationExecutionId,
      analysis: analysisRow.payload as CursorAnalysis,
      analysisPayloadHash: analysisRow.payload_hash,
      obligationSet: obligationParse.data!,
      obligationSetHash: obligationRow.obligation_set_hash,
      generatorVersion: obligationRow.generator_version,
      declarations: declarationParse.data!.declarations as never,
      declaredObligationSetHash: declarationParse.data!.obligationSetHash,
      requestId: analysisRow.request_id,
      channelId: analysisRow.channel_id,
      analysisRunId: analysisRow.analysis_run_id,
      workspaceId: analysisRow.workspace_id,
    },
  }
}

/**
 * MỌI phép kiểm phải chạy TRƯỚC khi ghép.
 *
 * Ghép rồi mới kiểm là sai thứ tự: một phép ghép trên dữ liệu đã trôi dạt sẽ tạo
 * ra một object trông hoàn toàn hợp lệ, và mọi quy tắc S sau đó chạy trên một
 * bài phân tích không tồn tại.
 */
export function verifyCompositeInputs(inputs: CompositeInputs): ValidationIssue[] {
  const issues: ValidationIssue[] = []

  // 1. Băm payload phân tích — bản đọc lại có đúng là bản đã ký không.
  const recomputed = hashAnalysisPayload(inputs.analysis)
  if (recomputed !== inputs.analysisPayloadHash) {
    issues.push(
      blocker(
        'composite_analysis_payload_drift',
        `Băm payload phân tích tính lại (${recomputed.slice(0, 12)}…) khác cột đã lưu ` +
          `(${inputs.analysisPayloadHash.slice(0, 12)}…).`,
      ),
    )
  }

  // 2. Băm tập nghĩa vụ + phiên bản bộ sinh.
  const obligationHash = hashObligationSet(inputs.obligationSet)
  if (obligationHash !== inputs.obligationSetHash) {
    issues.push(
      blocker(
        'composite_obligation_set_drift',
        `Băm tập nghĩa vụ tính lại (${obligationHash.slice(0, 12)}…) khác cột đã lưu ` +
          `(${inputs.obligationSetHash.slice(0, 12)}…).`,
      ),
    )
  }
  if (inputs.generatorVersion !== OBLIGATION_GENERATOR_VERSION) {
    issues.push(
      blocker(
        'composite_generator_version_drift',
        `Tập nghĩa vụ sinh bởi bộ sinh ${inputs.generatorVersion}, bản đang chạy là ` +
          `${OBLIGATION_GENERATOR_VERSION}. Đổi bộ sinh là đổi định nghĩa "đầy đủ".`,
      ),
    )
  }

  /*
   * 2b. TÁI SINH tập nghĩa vụ từ chính bản phân tích — không chỉ tự-nhất-quán.
   *
   * Mọi phép kiểm phía trên chỉ chứng minh tập nghĩa vụ NHẤT QUÁN VỚI CHÍNH NÓ:
   * băm của nó khớp cột lưu băm của nó. Chúng KHÔNG chứng minh nó là tập mà bộ
   * sinh tất định sẽ tạo ra từ bản phân tích này.
   *
   * Hai trường không hề được tái sinh ở đâu khác: `mentionedMetrics` và
   * `allowedAssertionStatuses`. Trường thứ hai là nơi DUY NHẤT cưỡng chế hành vi
   * lời nói theo cấu trúc (`STRUCTURAL_SPEECH_ACT`), và nó chỉ được đối chiếu
   * với chính bản đã lưu (`validate.ts`, S2). Một hàng nghĩa vụ mang `sourceRef`
   * và băm THẬT nhưng `allowedAssertionStatuses: ['ASSERTED']` trên một ô
   * `DATA_REQUEST|metricOrArtifact` sẽ qua mọi CHECK của database và mọi phép so
   * băm — rồi cấp phép cho đúng trạng thái mà 3.0 tuyên bố là BẤT KHẢ BIỂU DIỄN
   * ở ô đó.
   *
   * `buildObligationSet` là tất định trên `analysis`, nên so băm là đủ và rẻ.
   */
  const rebuilt = hashObligationSet(buildObligationSet(inputs.analysis))
  if (rebuilt !== inputs.obligationSetHash) {
    issues.push(
      blocker(
        'composite_obligation_set_not_reproducible',
        `Tập nghĩa vụ TÁI SINH từ bản phân tích có băm ${rebuilt.slice(0, 12)}… ` +
          `khác tập đã lưu (${inputs.obligationSetHash.slice(0, 12)}…). ` +
          `Tập đã lưu không phải tập mà bộ sinh tất định tạo ra từ chính bản phân tích này.`,
      ),
    )
  }

  // 3. O-INV-1: tập nghĩa vụ thuộc đúng bản phân tích này.
  const belongs = checkObligationBelongsTo(inputs.obligationSet, inputs.analysis)
  if (!belongs.ok) issues.push(blocker(belongs.rule, belongs.message))

  // 4. Băm mà LƯỢT KHAI BÁO đã dội lại.
  const echo = checkObligationSetHash(inputs.obligationSetHash, inputs.declaredObligationSetHash)
  if (!echo.ok) issues.push(blocker(echo.rule, echo.message))

  // 5. O-INV-3: danh tính khai báo — thiếu / thừa / trùng / lệch số lượng.
  for (const i of checkDeclarationIdentity(
    inputs.obligationSet,
    inputs.declarations.map((d) => d.id),
  )) {
    if (!i.ok) issues.push(blocker(i.rule, i.message, i.path))
  }

  // 6. O-INV-2: `sourceRef` và băm văn bản vẫn khớp bản phân tích đóng băng.
  for (const i of checkObligationSourcesIntact(inputs.obligationSet, inputs.analysis)) {
    if (!i.ok) issues.push(blocker(i.rule, i.message, i.path))
  }

  return issues
}

/**
 * Chạy CHẶNG HỢP NHẤT: kiểm, ghép, rồi áp S1–S8 lên bản ghép.
 *
 * `sourceRef` LUÔN lấy từ nghĩa vụ, bảy trường ngữ nghĩa LUÔN lấy từ khai báo —
 * mô hình không chạm được vào id claim, quyền sở hữu ô, hay mục tiêu của claim.
 */
export function runCompositeStage(
  inputs: CompositeInputs,
  pkg: AnalysisPackage,
  allowed: { evidenceIds: string[]; videoIds: string[]; cohortKeys: string[] },
  provenance: Record<string, unknown>,
): CompositeOutcome {
  const preIssues = verifyCompositeInputs(inputs)
  if (preIssues.length > 0) {
    return { ok: false, failureClass: 'SYSTEM_OR_INTEGRITY', issues: preIssues, report: null }
  }

  const metricClaims = composeMetricClaims(inputs.obligationSet, inputs.declarations)
  const composed = {
    ...inputs.analysis,
    schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
    metricClaims,
  }

  // S1–S8 và mọi chính sách bằng chứng/P0/nhân quả chạy Ở ĐÂY, trên VĂN XUÔI ĐÃ
  // ĐÓNG BĂNG và trên claim đã ghép — không phải trên một bản sao do mô hình gửi.
  const validated = validateCursorOutput({
    raw: JSON.stringify(composed),
    pkg,
    allowedEvidenceIds: allowed.evidenceIds,
    allowedVideoIds: allowed.videoIds,
    allowedCohortKeys: allowed.cohortKeys,
    hadProseOutsideJson: false,
  })

  if (!validated.report.passed || !validated.output) {
    // S1–S8 và các chính sách bằng chứng/P0/nhân quả: lỗi của BẢN KHAI.
    return {
      ok: false,
      failureClass: 'DECLARATION_SEMANTIC',
      issues: [],
      report: validated.report,
    }
  }

  const payload = {
    ...validated.output,
    _meta: {
      ...provenance,
      analysisExecutionId: inputs.analysisExecutionId,
      declarationExecutionId: inputs.declarationExecutionId,
      analysisPayloadHash: inputs.analysisPayloadHash,
      obligationSetHash: inputs.obligationSetHash,
      obligationCount: inputs.obligationSet.obligations.length,
      obligationGeneratorVersion: inputs.generatorVersion,
      compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
    },
  }
  return {
    ok: true,
    result: {
      payload,
      payloadHash: createHash('sha256').update(stableStringify(payload), 'utf8').digest('hex'),
      report: validated.report,
      claimCount: metricClaims.length,
    },
  }
}

/**
 * Ghi phán quyết COMPOSITE, và CHỈ KHI ĐẠT mới ghi kết quả chính thức.
 *
 * Một transaction: phán quyết và kết quả phải cùng sống hoặc cùng chết. Ghi
 * phán quyết rồi hỏng ở kết quả sẽ để lại một "COMPOSITE ĐẠT" không có kết quả —
 * và trigger chặn phán quyết cạnh tranh sẽ khoá luôn mọi lần thử sau.
 */
export async function persistComposite(args: {
  inputs: CompositeInputs
  outcome: CompositeOutcome
  failureClass: string
}): Promise<{ resultId: string | null; compositeValidationId: string }> {
  const { inputs, outcome } = args
  const report =
    outcome.ok
      ? outcome.result.report
      : (outcome.report ?? {
          passed: false,
          structuralIssues: outcome.ok ? [] : outcome.issues,
          evidenceIssues: [],
          claimIssues: [],
          qualityIssues: [],
          evidenceResolutionRate: null,
          totalEvidenceRefs: 0,
          unresolvedEvidenceRefs: 0,
          causalViolations: 0,
          ctrViolations: 0,
          unsupportedMetricViolations: 0,
          counts: { findings: 0, hypotheses: 0, recommendations: 0, experiments: 0 },
        })
  const structural = outcome.ok ? report.structuralIssues : [...report.structuralIssues, ...outcome.issues]

  return withTransaction(async (tx) => {
    const [vrow] = await tx.insert(schema.analysisValidation).values({
      workspaceId: inputs.workspaceId,
      analysisRunId: inputs.analysisRunId,
      llmExecutionId: inputs.declarationExecutionId,
      channelId: inputs.channelId,
      stage: 'COMPOSITE',
      passed: outcome.ok,
      failureClass: args.failureClass as never,
      structuralIssues: structural,
      evidenceIssues: report.evidenceIssues,
      claimIssues: report.claimIssues,
      qualityIssues: report.qualityIssues,
      evidenceResolutionRate:
        report.evidenceResolutionRate === null ? null : String(report.evidenceResolutionRate),
      totalEvidenceRefs: report.totalEvidenceRefs,
      unresolvedEvidenceRefs: report.unresolvedEvidenceRefs,
      causalViolations: report.causalViolations,
      ctrViolations: report.ctrViolations,
      unsupportedMetricViolations: report.unsupportedMetricViolations,
      findingCount: report.counts.findings,
      hypothesisCount: report.counts.hypotheses,
      recommendationCount: report.counts.recommendations,
      experimentCount: report.counts.experiments,
    }).returning({ id: schema.analysisValidation.id })
    const compositeValidationId = vrow!.id

    // KHÔNG ĐẠT -> không có hiện vật chính thức nào. Dừng ở đây.
    if (!outcome.ok) return { resultId: null, compositeValidationId }

    const [row] = await tx
      .insert(schema.cursorAnalysisResult)
      .values({
        workspaceId: inputs.workspaceId,
        analysisRunId: inputs.analysisRunId,
        llmExecutionId: inputs.declarationExecutionId,
        requestId: inputs.requestId,
        channelId: inputs.channelId,
        schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
        resultRole: 'COMPOSITE',
        payload: outcome.result.payload as never,
        payloadHash: outcome.result.payloadHash,
        analysisPayloadHash: inputs.analysisPayloadHash,
        obligationSetHash: inputs.obligationSetHash,
      })
      .returning({ id: schema.cursorAnalysisResult.id })

    // CHỐT TRẠNG THÁI của execution khai báo.
    //
    // Không có dòng này thì execution khai báo nằm mãi ở `RUNNING`, và mọi truy
    // vấn độ ổn định — vốn đòi `e.status = 'SUCCEEDED'` VÀ `v.passed = true` —
    // trả về RỖNG. Báo cáo khi ấy in "cần ít nhất 2 lần chạy" rồi thoát 0: một
    // cổng luôn xanh vì không bao giờ nhìn thấy dữ liệu. Đây là hỏng tệ nhất
    // trong các kiểu hỏng, vì nó trông y hệt "chưa chạy đủ".
    //
    // Đặt SUCCEEDED ở ĐÂY chứ không ở chỗ khác: execution khai báo thành công
    // ĐÚNG KHI nó sinh ra hiện vật chính thức. Lần khai qua được kiểm định
    // DECLARATION nhưng trượt hợp nhất thì KHÔNG thành công — và vẫn giữ nguyên
    // trạng thái cũ để bảng lần thử đếm nó là một lần trượt.
    await tx
      .update(schema.llmExecution)
      .set({ status: 'SUCCEEDED', analysisResultId: null })
      .where(eq(schema.llmExecution.id, inputs.declarationExecutionId))

    return { resultId: row!.id, compositeValidationId }
  })
}

/* =========================================================================
 * ĐỌC LẠI một payload HỢP NHẤT ĐÃ LƯU
 * ====================================================================== */

export interface StoredPayloadCheck {
  ok: boolean
  issues: ValidationIssue[]
  /** Payload đã GỠ `_meta`, hợp lệ theo schema nghiêm ngặt. `null` khi hỏng. */
  payload: CursorOutput | null
  meta: Record<string, unknown> | null
}

/**
 * Cách DUY NHẤT đúng để đọc lại một payload hợp nhất đã lưu.
 *
 * `cursorOutputSchema` là `.strict()`, còn payload đã lưu MANG THÊM `_meta`. Ai
 * cầm payload từ database rồi ném thẳng vào `safeParse` sẽ nhận "unrecognized
 * key: _meta" và kết luận sai rằng dữ liệu hỏng. Ngược lại, ai nhớ gỡ `_meta`
 * nhưng quên KIỂM nó thì bỏ qua chính phần mang nguồn gốc.
 *
 * Hàm này làm cả hai, theo đúng thứ tự: kiểm `_meta` trước (nó là bằng chứng
 * lineage), rồi mới kiểm phần còn lại bằng schema nghiêm ngặt.
 *
 * `expected` cho phép đối chiếu `_meta` với các hàng database thật. Bỏ trống thì
 * chỉ kiểm hình dạng — dùng khi chưa biết mình đang mong đợi gì.
 */
export function parseStoredCompositePayload(
  stored: unknown,
  expected?: Partial<{
    analysisExecutionId: string
    declarationExecutionId: string
    analysisPayloadHash: string
    obligationSetHash: string
    obligationCount: number
  }>,
): StoredPayloadCheck {
  const issues: ValidationIssue[] = []

  if (typeof stored !== 'object' || stored === null || Array.isArray(stored)) {
    return {
      ok: false,
      issues: [blocker('stored_payload_not_object', 'Payload đã lưu không phải một object.')],
      payload: null,
      meta: null,
    }
  }

  const { _meta, ...rest } = stored as Record<string, unknown>

  if (_meta === undefined) {
    issues.push(
      blocker(
        'stored_payload_missing_meta',
        'Payload hợp nhất thiếu `_meta`. Không có nó thì không đối chiếu được với bất kỳ hàng nào.',
      ),
    )
  } else if (typeof _meta !== 'object' || _meta === null || Array.isArray(_meta)) {
    issues.push(blocker('stored_payload_malformed_meta', '`_meta` không phải một object.'))
  } else {
    const meta = _meta as Record<string, unknown>
    const REQUIRED = [
      'analysisExecutionId',
      'declarationExecutionId',
      'analysisPayloadHash',
      'obligationSetHash',
      'obligationCount',
      'obligationGeneratorVersion',
      'compositeValidatorVersion',
    ] as const
    for (const k of REQUIRED) {
      if (meta[k] === undefined || meta[k] === null) {
        issues.push(blocker('stored_payload_malformed_meta', `\`_meta.${k}\` thiếu.`))
      }
    }
    // GIÁ TRỊ phiên bản, không chỉ SỰ CÓ MẶT.
    //
    // Vòng `REQUIRED` ở trên chỉ đòi khác `undefined/null`, nên một payload mang
    // `"obligationGeneratorVersion": "bịa"` vẫn được công nhận hợp lệ. Hai hợp
    // đồng này quyết định ngữ nghĩa của bản khai; đọc lại một hiện vật cũ dưới
    // phiên bản mới mà không ai kêu chính là trôi dạt phiên bản trong im lặng.
    const PINNED: Array<[string, string]> = [
      ['obligationGeneratorVersion', OBLIGATION_GENERATOR_VERSION],
      ['compositeValidatorVersion', COMPOSITE_VALIDATOR_VERSION],
    ]
    for (const [k, want] of PINNED) {
      if (meta[k] === undefined || meta[k] === null) continue // đã báo ở trên
      if (meta[k] !== want) {
        issues.push(
          blocker(
            'stored_payload_meta_version_drift',
            `\`_meta.${k}\` = ${JSON.stringify(meta[k])} nhưng mã đang chạy là ` +
              `${JSON.stringify(want)}. Hiện vật này thuộc một hợp đồng KHÁC.`,
          ),
        )
      }
    }

    for (const [k, want] of Object.entries(expected ?? {})) {
      if (want === undefined) continue
      if (meta[k] !== want) {
        issues.push(
          blocker(
            'stored_payload_meta_mismatch',
            `\`_meta.${k}\` = ${JSON.stringify(meta[k])} nhưng hàng database là ` +
              `${JSON.stringify(want)}.`,
          ),
        )
      }
    }
  }

  // Phần còn lại phải hợp lệ theo schema NGHIÊM NGẶT — `_meta` đã được gỡ ra.
  const parsed = cursorOutputSchema.safeParse(rest)
  if (!parsed.success) {
    for (const i of parsed.error.issues.slice(0, 10)) {
      issues.push(blocker('stored_payload_schema', i.message, i.path.join('.')))
    }
  }

  const ok = issues.length === 0
  return {
    ok,
    issues,
    payload: parsed.success ? parsed.data : null,
    meta: (_meta as Record<string, unknown> | undefined) ?? null,
  }
}
