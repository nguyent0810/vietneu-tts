import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

import type { AnalysisPackage } from '@/lib/analysis/package'
import {
  buildDeclarationPrompt,
  buildDeclarationRepairPrompt,
  DECLARATION_PROMPT_VERSION,
} from '@/lib/cursor/declaration-prompt'
import { buildObligationSet, hashObligationSet, checkObligationBelongsTo } from '@/lib/cursor/obligation'
import { ANALYSIS_PROMPT_VERSION, buildPrompt } from '@/lib/cursor/prompt'
import {
  ANALYSIS_SCHEMA_VERSION,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  DECLARATION_SCHEMA_VERSION,
  type ClaimObligationSet,
  type CursorAnalysis,
} from '@/lib/cursor/schema'
import {
  CTR_VIOLATION_RULES,
  PROSE_OUTSIDE_JSON_PATH,
  validateAnalysisOutput,
  validateCursorOutput,
  validateDeclarationOutput,
} from '@/lib/cursor/validate'

/**
 * G4 — HAI PROMPT và HAI CHẶNG KIỂM ĐỊNH.
 *
 * Kiểm hợp đồng của từng lượt một cách độc lập với database: lượt 1 không được
 * khai báo, lượt 2 không được chọn ô. Phần nối hai lượt vào vòng chạy thật nằm ở
 * phần còn lại của G4.
 */

function makePackage(): AnalysisPackage {
  return {
    schemaVersion: '1.0.0',
    algorithmVersion: '1.0.0',
    scope: {
      workspaceId: 'ws-1', channelId: 'ch-1', channelLabel: 'hinh_su', channelTitle: 'K',
      reportingTimezone: 'America/Los_Angeles', windowStart: '2026-06-01', windowEnd: '2026-07-27',
      analysisRunId: 'run-1', inputHash: 'a'.repeat(64),
    },
    channelSummary: { videos: 20, medianViewsD7: 100 },
    dataCoverage: {
      videosTotal: 20, videosWithMetrics: 18, videosImmature: 2, metricRows: 180,
      expectedDates: 57, observedDates: 57, missingDates: [],
      metricCoverage: { views: 1, impressions: 0, impressionCtr: 0 }, revisedRows: 0,
    },
    confidence: { score: 0.8, band: 'HIGH', drivers: {} },
    baselines: [{ key: 'CHANNEL_FORMAT:SHORT', kind: 'CHANNEL_FORMAT', description: 'S', videoCount: 12, medianViewsD7: 100 }],
    featureDefinitions: [{ key: 'views_d7', label: 'V', unit: 'COUNT', direction: 'HIGHER_IS_BETTER', version: '1.0.0', formula: 'sum' }],
    observations: [{
      kind: 'TOP_PERFORMER', polarity: 'POSITIVE',
      statement: 'Video aaaaaaaaaaa ở phân vị 92 về lượt xem 7 ngày.',
      metricValues: { views_d7: 900 }, baselineKind: 'CHANNEL_FORMAT', confidence: 0.8,
      limitations: [], evidenceRefs: [{ refType: 'VIDEO', refId: 'v1' }], isHypothesis: false,
    }],
    anomalies: [], rankedVideos: [{ youtubeVideoId: 'aaaaaaaaaaa', title: 'A', format: 'SHORT', viewsD7: 900 }],
    cohortComparisons: [], formatComparison: null, hypothesisCandidates: [],
    unresolvedQuestions: [], missingData: [], analysisTasks: [],
    limitsApplied: {
      positiveObservations: { included: 1, total: 1 }, negativeObservations: { included: 0, total: 0 },
      anomalies: { included: 0, total: 0 }, rankedVideos: { included: 1, total: 1 },
      cohorts: { included: 0, total: 0 }, hypotheses: { included: 0, total: 0 }, truncatedForSize: false,
    },
  } as AnalysisPackage
}

function analysis(over: Partial<CursorAnalysis> = {}): CursorAnalysis {
  return {
    schemaVersion: ANALYSIS_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
      confidence: 'MEDIUM',
      confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ trong cửa sổ quan sát này.',
      primaryConstraint: 'Cỡ mẫu còn nhỏ nên kết luận xu hướng cần thận trọng.',
    },
    keyFindings: [{
      id: 'F-001',
      statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
      findingType: 'OBSERVATION', confidence: 'MEDIUM', evidenceIds: ['OBS-001'],
      supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
      contradictingEvidenceIds: [], limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu'],
    }],
    hypotheses: [], recommendations: [], experiments: [],
    manualReviewTargets: [], dataRequests: [],
    explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
    selfCheck: {
      usedOnlyProvidedEvidence: true, recomputedMetrics: false, madeCausalClaims: false,
      madeCtrOrImpressionClaims: false, allFindingEvidenceResolved: true,
    },
    ...over,
  }
}

function runAnalysis(payload: unknown) {
  const pkg = makePackage()
  const built = buildPrompt({ pkg })
  return validateAnalysisOutput({
    raw: typeof payload === 'string' ? payload : JSON.stringify(payload),
    pkg,
    allowedEvidenceIds: built.allowedEvidenceIds,
    allowedVideoIds: built.allowedVideoIds,
    allowedCohortKeys: built.allowedCohortKeys,
    hadProseOutsideJson: false,
  })
}

const decl = (id: string, over: Record<string, unknown> = {}) => ({
  id,
  subjectMetric: 'views',
  relatedMetric: 'impression_ctr',
  claimType: 'METHODOLOGY_LIMITATION',
  judgement: 'LOW',
  assertionStatus: 'LIMITATION',
  evidenceIds: [] as string[],
  requiresMissingnessDisclosure: false,
  ...over,
})

function declarationPayload(set: ClaimObligationSet, over: Record<string, unknown> = {}) {
  return {
    schemaVersion: DECLARATION_SCHEMA_VERSION,
    obligationSetHash: hashObligationSet(set),
    declarations: set.obligations.map((o) => decl(o.id)),
    ...over,
  }
}

function runDeclaration(set: ClaimObligationSet, payload: unknown) {
  return validateDeclarationOutput({
    raw: typeof payload === 'string' ? payload : JSON.stringify(payload),
    obligationSet: set,
    obligationSetHash: hashObligationSet(set),
  })
}

describe('lượt 1 — prompt phân tích KHÔNG còn hợp đồng khai báo', () => {
  const { text } = buildPrompt({ pkg: makePackage() })

  it('không nhắc metricClaims, sourceRef hay bảng section/field', () => {
    // `MỘT Ô — MỘT PHÁT BIỂU` VẪN phải có: U1 được cưỡng chế ở chặng ANALYSIS.
    // Chỉ hợp đồng KHAI BÁO là chuyển đi.
    for (const gone of ['metricClaims', 'sourceRef', 'subjectMetric']) {
      expect(text, `prompt lượt 1 còn sót "${gone}"`).not.toContain(gone)
    }
  })

  it('GIỮ quy tắc một-ô-một-phát-biểu (U1 vẫn chặn ở chặng ANALYSIS)', () => {
    expect(text).toContain('MỘT Ô — MỘT PHÁT BIỂU')
    expect(text).toContain('ĐÚNG — tách thành hai phần tử')
  })

  it('khai đúng schemaVersion của lượt phân tích', () => {
    expect(text).toContain(`schemaVersion = "${ANALYSIS_SCHEMA_VERSION}"`)
  })

  it('phiên bản prompt phân tích tách riêng', () => {
    expect(ANALYSIS_PROMPT_VERSION).toBe('4.1.0')
  })

  it('PHÁT RA ràng buộc trật tự từ mà validator 1.6 cưỡng chế', () => {
    /*
     * Lượt 2 không sửa được văn xuôi. Nếu lượt 1 viết "Thumbnail kém sẽ …" thì
     * không bản khai nào cứu được, nên luật này phải nằm ở prompt lượt 1 —
     * ngược lại thì `judgement_on_missing_metric_in_text` là một luật chỉ phạt
     * mà không bao giờ dạy.
     */
    expect(text).toContain('TRẬT TỰ TỪ')
    expect(text).toContain('Nếu thumbnail kém thì')
  })

  it('TẤT ĐỊNH: cùng gói cho cùng băm', () => {
    expect(buildPrompt({ pkg: makePackage() }).hash).toBe(buildPrompt({ pkg: makePackage() }).hash)
  })

  it('ràng buộc sinh từ schema KHÔNG nêu metricClaims', () => {
    expect(text).not.toMatch(/metricClaims\[\]/)
  })
})

describe('lượt 1 — chặng kiểm định ANALYSIS', () => {
  it('bản văn xuôi hợp lệ ĐẠT', () => {
    const r = runAnalysis(analysis())
    expect(r.report.passed, JSON.stringify(r.report.claimIssues)).toBe(true)
  })

  it('TUỒN metricClaims vào lượt 1 -> claims_in_analysis_pass', () => {
    const r = runAnalysis({ ...analysis(), metricClaims: [] })
    expect(r.report.structuralIssues.map((i) => i.rule)).toContain('claims_in_analysis_pass')
    expect(r.report.passed).toBe(false)
  })

  it('tuồn một claim ĐẦY ĐỦ cũng bị chặn', () => {
    const r = runAnalysis({
      ...analysis(),
      metricClaims: [{ id: 'MC-001', claimType: 'OBSERVATION', subjectMetric: 'views',
        relatedMetric: 'NONE', judgement: 'LOW', assertionStatus: 'ASSERTED', evidenceIds: [],
        requiresMissingnessDisclosure: false,
        sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 } }],
    })
    expect(r.report.structuralIssues.map((i) => i.rule)).toContain('claims_in_analysis_pass')
  })

  it('KHÔNG báo undeclared_sensitive_unit (chưa có claim là ĐÚNG thiết kế)', () => {
    const r = runAnalysis(analysis())
    expect(r.report.claimIssues.map((i) => i.rule)).not.toContain('undeclared_sensitive_unit')
  })

  it('U1 VẪN chạy ở lượt 1 — ô hai phát biểu bị chặn', () => {
    const r = runAnalysis(
      analysis({
        keyFindings: [{ ...analysis().keyFindings[0]!, limitations: ['CTR chưa đo; impressions cũng chưa bật'] }],
      }),
    )
    expect(r.report.claimIssues.map((i) => i.rule)).toContain('multiple_assertions_in_source_unit')
    expect(r.report.passed).toBe(false)
  })

  it('ngôn ngữ nhân quả VẪN bị chặn ở lượt 1', () => {
    const r = runAnalysis(
      analysis({
        keyFindings: [{ ...analysis().keyFindings[0]!, supportingReasoning: 'Tiêu đề kém gây ra sụt giảm lượt xem trong kỳ.' }],
      }),
    )
    expect(r.report.claimIssues.map((i) => i.rule)).toContain('causal_claim')
  })

  it('JSON hỏng -> INVALID_JSON', () => {
    expect(runAnalysis('{ hỏng').failureClass).toBe('INVALID_JSON')
  })

  it('thiếu trường bắt buộc -> MISSING_REQUIRED_FIELD', () => {
    const { keyFindings, ...rest } = analysis()
    expect(runAnalysis(rest).failureClass).toBe('MISSING_REQUIRED_FIELD')
  })

  it('phiên bản CŨ bị từ chối', () => {
    expect(runAnalysis({ ...analysis(), schemaVersion: '2.1' }).failureClass).not.toBe('NONE')
  })
})

describe('lượt 2 — prompt khai báo', () => {
  const set = buildObligationSet(analysis())
  const built = buildDeclarationPrompt({
    analysisPayload: analysis(),
    obligationSet: set,
    obligationSetHash: hashObligationSet(set),
    analysisPayloadHash: set.analysisHash,
  })

  it('mang ĐÚNG băm tập nghĩa vụ để mô hình sao chép lại', () => {
    expect(built.text).toContain(hashObligationSet(set))
  })

  it('liệt kê đủ số nghĩa vụ và văn bản của từng ô', () => {
    expect(built.obligationCount).toBe(set.obligations.length)
    for (const ob of set.obligations) {
      expect(built.text).toContain(ob.id)
      expect(built.text).toContain(ob.resolvedText)
      expect(built.text).toContain(ob.allowedAssertionStatuses.join(' | '))
    }
  })

  it('nói rõ điều KHÔNG được làm', () => {
    expect(built.text).toContain('KHÔNG thêm một mục nào ngoài danh sách nghĩa vụ')
    expect(built.text).toContain('KHÔNG bỏ sót một nghĩa vụ nào')
    expect(built.text).toContain('KHÔNG viết `sourceRef`')
  })

  it('TẤT ĐỊNH: cùng đầu vào cho cùng băm', () => {
    const again = buildDeclarationPrompt({
      analysisPayload: analysis(),
      obligationSet: buildObligationSet(analysis()),
      obligationSetHash: hashObligationSet(set),
      analysisPayloadHash: set.analysisHash,
    })
    expect(again.hash).toBe(built.hash)
  })

  it('THỨ TỰ nghĩa vụ trong prompt là thứ tự id, tất định', () => {
    const multi = buildObligationSet(
      analysis({
        keyFindings: [{
          ...analysis().keyFindings[0]!,
          limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'],
        }],
        explicitNonConclusions: ['Không kết luận hiệu quả thumbnail.'],
      }),
    )
    const p = buildDeclarationPrompt({
      analysisPayload: {}, obligationSet: multi,
      obligationSetHash: hashObligationSet(multi), analysisPayloadHash: multi.analysisHash,
    })
    const order = ['MC-001', 'MC-002', 'MC-003'].map((id) => p.text.indexOf(`### ${id}`))
    expect(order).toEqual([...order].sort((a, b) => a - b))
    expect(order.every((i) => i > 0)).toBe(true)
  })

  it('prompt sửa lỗi giữ lại bảng nghĩa vụ nhưng KHÔNG gửi lại văn xuôi', () => {
    const r = buildDeclarationRepairPrompt({
      errors: ['thiếu MC-001'], invalidOutput: '{}',
      obligationSet: set, obligationSetHash: hashObligationSet(set),
    })
    expect(r.text).toContain('MC-001')
    expect(r.text).toContain('GIỮ NGUYÊN mọi phán xét ngữ nghĩa bạn đã khai đúng')
  })

  it('phiên bản prompt khai báo tách riêng', () => {
    // 1.0.0 -> 1.1.0 (2026-08-13): prompt nay NÊU RA các luật vốn đã bị cưỡng
    // chế trong im lặng (dấu hiệu tình thái, dạng khai cho câu thiếu dữ liệu).
    // Ghim này tồn tại để buộc người sửa phải cố ý — số đo hai bên mốc không gộp.
    expect(DECLARATION_PROMPT_VERSION).toBe('1.2.0')
    expect(built.promptVersion).toBe(DECLARATION_PROMPT_VERSION)
  })
})

describe('lượt 2 — chặng kiểm định DECLARATION', () => {
  const set = buildObligationSet(
    analysis({
      keyFindings: [{
        ...analysis().keyFindings[0]!,
        limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'],
      }],
    }),
  )

  it('bản khai đủ và đúng ĐẠT', () => {
    const r = runDeclaration(set, declarationPayload(set))
    expect(r.report.passed, JSON.stringify([...r.report.structuralIssues, ...r.report.claimIssues])).toBe(true)
    expect(r.declarations).toHaveLength(set.obligations.length)
  })

  it('ĐẢO THỨ TỰ không phải lỗi', () => {
    const p = declarationPayload(set)
    p.declarations = [...p.declarations].reverse()
    expect(runDeclaration(set, p).report.passed).toBe(true)
  })

  it('THIẾU một khai báo -> declaration_missing_obligation', () => {
    const p = declarationPayload(set)
    p.declarations = p.declarations.slice(0, 1)
    const rules = runDeclaration(set, p).report.claimIssues.map((i) => i.rule)
    expect(rules).toContain('declaration_missing_obligation')
    expect(rules).toContain('declaration_count_mismatch')
  })

  it('THỪA một khai báo -> declaration_unknown_obligation', () => {
    const p = declarationPayload(set)
    p.declarations = [...p.declarations, decl('MC-099')]
    expect(runDeclaration(set, p).report.claimIssues.map((i) => i.rule)).toContain(
      'declaration_unknown_obligation',
    )
  })

  it('TRÙNG id -> declaration_duplicate', () => {
    const p = declarationPayload(set)
    p.declarations = [p.declarations[0]!, p.declarations[0]!]
    expect(runDeclaration(set, p).report.claimIssues.map((i) => i.rule)).toContain(
      'declaration_duplicate',
    )
  })

  it('băm tập nghĩa vụ LỆCH -> obligation_set_drift', () => {
    const p = declarationPayload(set, { obligationSetHash: 'f'.repeat(64) })
    expect(runDeclaration(set, p).report.structuralIssues.map((i) => i.rule)).toContain(
      'obligation_set_drift',
    )
  })

  it('cố ghi sourceRef -> declaration_defines_target', () => {
    const p = declarationPayload(set)
    ;(p.declarations[0] as Record<string, unknown>).sourceRef = {
      section: 'RECOMMENDATION', itemId: 'R-001', field: 'action', ordinal: 0,
    }
    const rules = runDeclaration(set, p).report.structuralIssues.map((i) => i.rule)
    expect(rules).toContain('declaration_defines_target')
  })

  it('cố ghi text cũng bị chặn', () => {
    const p = declarationPayload(set)
    ;(p.declarations[0] as Record<string, unknown>).text = 'một câu tự chế'
    expect(runDeclaration(set, p).report.passed).toBe(false)
  })

  it('assertionStatus ngoài tập hợp lệ của Ô bị chặn', () => {
    const labelSet = buildObligationSet(
      analysis({
        dataRequests: [{
          metricOrArtifact: 'impressions cấp video',
          reason: 'Cần để tách khâu tiếp cận khỏi khâu giữ chân.',
          decisionUnlocked: 'Biết nên ưu tiên sửa gì trước.',
        }],
      }),
    )
    const ob = labelSet.obligations.find((o) => o.canonical.startsWith('DATA_REQUEST'))!
    const p = {
      schemaVersion: DECLARATION_SCHEMA_VERSION,
      obligationSetHash: hashObligationSet(labelSet),
      declarations: labelSet.obligations.map((o) =>
        decl(o.id, o.id === ob.id ? { assertionStatus: 'ASSERTED', subjectMetric: 'impressions' } : {}),
      ),
    }
    const rules = runDeclaration(labelSet, p).report.claimIssues.map((i) => i.rule)
    expect(rules).toContain('assertion_status_wrong_for_field')
  })

  it('JSON hỏng -> INVALID_JSON', () => {
    expect(runDeclaration(set, '{ hỏng').failureClass).toBe('INVALID_JSON')
  })

  it('sai schemaVersion -> chặn', () => {
    expect(runDeclaration(set, declarationPayload(set, { schemaVersion: '2.1' })).report.passed).toBe(false)
  })
})

describe('tập nghĩa vụ CHÉO bản phân tích', () => {
  it('tập của bản A dùng cho bản B -> obligation_analysis_mismatch', () => {
    const a = analysis()
    const b = analysis({ explicitNonConclusions: ['Một câu hoàn toàn khác với bản A.'] })
    const r = checkObligationBelongsTo(buildObligationSet(a), b)
    expect(r.ok).toBe(false)
    expect(r.ok === false && r.rule).toBe('obligation_analysis_mismatch')
  })

  it('băm tập của hai bản phân tích khác nhau thì khác nhau', () => {
    const a = buildObligationSet(analysis())
    const b = buildObligationSet(
      analysis({ keyFindings: [{ ...analysis().keyFindings[0]!, limitations: ['CTR nhiễu vì cỡ mẫu nhỏ'] }] }),
    )
    expect(hashObligationSet(b)).not.toBe(hashObligationSet(a))
  })
})

describe('kích thước ĐO ĐƯỢC (chưa đóng băng trần nào)', () => {
  it('ghi lại kích thước prompt của hai lượt', () => {
    const p1 = buildPrompt({ pkg: makePackage() })
    const set = buildObligationSet(analysis())
    const p2 = buildDeclarationPrompt({
      analysisPayload: analysis(), obligationSet: set,
      obligationSetHash: hashObligationSet(set), analysisPayloadHash: set.analysisHash,
    })
    // Không khẳng định ngưỡng nào: đây là SỐ ĐO, và trần chỉ được đặt sau khi có
    // số đo từ lần thăm dò thật.
    console.log(
      `[G4 kích thước] prompt lượt 1 = ${p1.bytes} B; prompt lượt 2 = ${p2.bytes} B ` +
        `(${set.obligations.length} nghĩa vụ, gói mẫu tối thiểu)`,
    )
    expect(p1.bytes).toBeGreaterThan(0)
    expect(p2.bytes).toBeGreaterThan(0)
  })
})

/**
 * `repairErrors` chỉ được mang lỗi ÁP DỤNG ĐƯỢC cho ĐÚNG chặng đang kiểm.
 *
 * Khiếm khuyết do lần thăm dò 2026-08-06 phát hiện: bộ kiểm gom `repairErrors`
 * TRƯỚC khi lọc theo chặng, nên báo cáo lưu `ctr_violations = 0` trong khi prompt
 * sửa lỗi vẫn bảo mô hình "bỏ mọi kết luận về CTR". Một prompt sửa lỗi nói về lỗi
 * không tồn tại sẽ đẩy lần thử sau đi sai hướng — và không ai thấy, vì hai nơi
 * ấy không bao giờ được đem so.
 */
describe('rò rỉ lỗi giữa các chặng', () => {
  /** Bản phân tích có ĐÚNG một câu nhân quả, và selfCheck khai là không có. */
  const causal = () =>
    analysis({
      keyFindings: [{
        id: 'F-001',
        statement: 'CTA dày làm giảm giữ chân người xem ở nhóm Shorts của kênh này.',
        findingType: 'OBSERVATION', confidence: 'MEDIUM', evidenceIds: ['OBS-001'],
        supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
        contradictingEvidenceIds: [], limitations: [],
      }],
    } as never)

  it('chặng ANALYSIS: KHÔNG rò lời khuyên về CTR đã bị lọc bỏ', () => {
    const r = runAnalysis(causal())
    expect(r.report.ctrViolations).toBe(0)
    const leaked = r.repairErrors.filter((e) => /CTR|impressions|thumbnail/i.test(e))
    expect(leaked, `rò rỉ: ${JSON.stringify(leaked)}`).toEqual([])
  })

  it('chặng ANALYSIS: KHÔNG rò `selfcheck_contradicted` về CTR', () => {
    const r = runAnalysis(causal())
    const stored = [...r.report.claimIssues, ...r.report.qualityIssues]
    expect(stored.some((i) => i.path === 'selfCheck.madeCtrOrImpressionClaims')).toBe(false)
    expect(r.repairErrors.some((e) => e.includes('madeCtrOrImpressionClaims'))).toBe(false)
  })

  it('RANH GIỚI: vi phạm THẬT vẫn bị chặn và vẫn được chỉ tên', () => {
    // Sửa rò rỉ KHÔNG được làm im lặng một vi phạm có thật. Đây chính là câu
    // nhân quả đã chặn lần thăm dò, và nó phải tiếp tục bị chặn.
    const r = runAnalysis(causal())
    expect(r.report.passed).toBe(false)
    expect(r.report.claimIssues.some((i) => i.rule === 'causal_claim')).toBe(true)
    expect(r.repairErrors.some((e) => e.includes('nhân quả'))).toBe(true)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('tổng kết "N lỗi mức HIGH" khớp số HIGH THẬT trong báo cáo', () => {
    const r = runAnalysis(causal())
    const highs = [
      ...r.report.structuralIssues, ...r.report.evidenceIssues,
      ...r.report.claimIssues, ...r.report.qualityIssues,
    ].filter((i) => i.severity === 'HIGH')
    const summary = r.repairErrors.find((e) => /^\d+ lỗi mức HIGH:/.test(e))
    if (summary) {
      expect(Number(summary.match(/^(\d+)/)![1]), 'tổng kết lệch số HIGH thật').toBe(highs.length)
    } else {
      expect(highs.length).toBe(0)
    }
  })

  it('câu nhân quả trong keyFindings NAY được nêu kèm trong prompt sửa lỗi', () => {
    // Khiếm khuyết CÓ TỪ TRƯỚC: khối sinh hướng dẫn nằm TRƯỚC các lần đếm vi
    // phạm ở phần quét phát hiện, nên đúng ca của lần thăm dò 2026-08-06 bị
    // chặn mà không có một dòng hướng dẫn nào.
    const r = runAnalysis(causal())
    const line = r.repairErrors.find((e) => e.includes('nhân quả'))
    expect(line, 'không có hướng dẫn nào cho một vi phạm CÓ THẬT').toBeDefined()
    // Phải chỉ ĐÚNG câu vi phạm, không nói chung chung.
    expect(line).toContain('CTA dày làm giảm giữ chân')
  })

  /** Gói + prompt dùng chung cho các ca dưới đây. */
  const baseInput = () => {
    const pkg = makePackage()
    const built = buildPrompt({ pkg })
    return {
      pkg, allowedEvidenceIds: built.allowedEvidenceIds,
      allowedVideoIds: built.allowedVideoIds, allowedCohortKeys: built.allowedCohortKeys,
    }
  }

  it('A-3: khẳng định CTR trong VĂN BẢN NGOÀI JSON vẫn bị chặn ở chặng ANALYSIS', () => {
    // Ca tái dựng được: bộ lọc theo chặng lọc U3 THEO QUY TẮC, nên nó xoá luôn
    // vi phạm ở văn bản ngoài JSON — thứ mà lượt 1 KHÔNG có cách nào khai báo.
    // Hồ sơ mất vi phạm, `ctrViolations` về 0, và phân loại đổi sang
    // PROSE_OUTSIDE_JSON vốn ĐƯỢC PHÉP THỬ LẠI.
    const r = validateCursorOutput({
      ...baseInput(),
      raw: JSON.stringify({ ...analysis(), schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, metricClaims: [] }),
      hadProseOutsideJson: true,
      proseText: 'CTR hiện tại của kênh đang thấp và thumbnail kém hấp dẫn.',
      stage: 'ANALYSIS',
    })
    const prose = r.report.claimIssues.filter((i) => i.path === PROSE_OUTSIDE_JSON_PATH)
    expect(prose.length, 'vi phạm ngoài JSON bị xoá khỏi hồ sơ').toBeGreaterThan(0)
    expect(r.report.ctrViolations, 'ctrViolations bị hạ về 0').toBeGreaterThan(0)
    // Và quan trọng nhất: KHÔNG được rơi vào lớp cho phép thử lại.
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('A-3: U3 của các Ô TRONG JSON vẫn được lọc ở ANALYSIS', () => {
    // Ranh giới ngược lại: sửa rò rỉ không được làm U3-trong-JSON sống lại ở
    // lượt 1, vì lượt 1 chưa có bản khai để mà khai thiếu.
    const withSensitiveCell = {
      ...analysis({
        keyFindings: [{
          id: 'F-001',
          statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
          findingType: 'OBSERVATION', confidence: 'MEDIUM', evidenceIds: ['OBS-001'],
          supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
          contradictingEvidenceIds: [], limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu'],
        }],
      } as never),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, metricClaims: [] as unknown[],
    }
    const r = validateCursorOutput({
      ...baseInput(), raw: JSON.stringify(withSensitiveCell),
      hadProseOutsideJson: false, stage: 'ANALYSIS',
    })
    expect(r.report.claimIssues.some((i) => i.rule === 'undeclared_sensitive_unit')).toBe(false)
  })

  it('A-2: vi phạm CTR CÓ THẬT luôn kèm dòng hướng dẫn', () => {
    // Nhãn cũ (`ctr_claim_without_coverage`) không quy tắc nào phát ra, nên dòng
    // hướng dẫn bị lọc bỏ ở MỌI trường hợp.
    const withSensitiveCell = {
      ...analysis({
        keyFindings: [{
          id: 'F-001',
          statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
          findingType: 'OBSERVATION', confidence: 'MEDIUM', evidenceIds: ['OBS-001'],
          supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
          contradictingEvidenceIds: [], limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu'],
        }],
      } as never),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, metricClaims: [] as unknown[],
    }
    const r = validateCursorOutput({
      ...baseInput(), raw: JSON.stringify(withSensitiveCell), hadProseOutsideJson: false,
    })
    expect(r.report.ctrViolations).toBeGreaterThan(0)
    expect(
      r.repairErrors.some((e) => /CTR|impressions|thumbnail/i.test(e)),
      'vi phạm CTR có thật nhưng KHÔNG có hướng dẫn nào',
    ).toBe(true)
  })

  it('A-2/F5: mọi TÊN QUY TẮC được tham chiếu phải là quy tắc CÓ THẬT', () => {
    /*
     * Hàng rào tĩnh: một nhãn gõ sai sẽ lọc bỏ dòng hướng dẫn trong im lặng.
     *
     * F5 — bản trước của phép kiểm này BỎ SÓT theo HAI chiều, và cả hai đều đã
     * để lọt một khiếm khuyết thật:
     *
     *   1. Neo `^\s+\[?'...'` chỉ đọc tên ĐẦU TIÊN mỗi dòng, nên mảng một dòng
     *      `['causal_claim', 'causal_language_in_non_causal_claim', ...]` chỉ được
     *      kiểm 1/3 tên.
     *   2. Nó chỉ nhìn nhãn của `pushRepair`, KHÔNG nhìn các phép so
     *      `i.rule === '...'` — và đúng ở đó có `ctr_claim_without_coverage`, một
     *      tên không quy tắc nào phát ra, khiến khối chọn câu vi phạm CTR trả về
     *      rỗng ở MỌI trường hợp (F4).
     */
    const src = readFileSync(
      new URL('../../src/lib/cursor/validate.ts', import.meta.url), 'utf8')
    const emitted = new Set([...src.matchAll(/rule: '([a-z_]+)'/g)].map((m) => m[1]!))

    /*
     * (a) MỌI tên trong mảng nhãn của `pushRepair`, kể cả nhiều tên trên một dòng.
     *
     * Cắt ĐÚNG phạm vi lời gọi `pushRepair(...)` bằng cách dò ngoặc cân bằng,
     * không quét cả tệp: quét cả tệp sẽ bắt nhầm những mảng tên CHỈ SỐ như
     * `['impressions', 'impression_ctr', ...]`, và một phép kiểm hay báo động giả
     * thì sớm muộn cũng bị nới cho im — mất luôn tác dụng.
     */
    const pushRepairArgs: string[] = []
    for (let i = src.indexOf('pushRepair('); i !== -1; i = src.indexOf('pushRepair(', i + 1)) {
      let depth = 0
      let quote: string | null = null
      let j = i + 'pushRepair'.length
      for (; j < src.length; j++) {
        const ch = src[j]!
        if (quote) {
          if (ch === '\\') j++
          else if (ch === quote) quote = null
          continue
        }
        if (ch === "'" || ch === '"' || ch === '`') quote = ch
        else if (ch === '(') depth++
        else if (ch === ')') {
          depth--
          if (depth === 0) break
        }
      }
      pushRepairArgs.push(src.slice(i, j + 1))
    }
    // MỌI tên kiểu snake_case trong phạm vi lời gọi, dù là nhãn đơn hay mảng.
    // Phần thông điệp là văn xuôi tiếng Việt nên không sinh token dạng này.
    const tagged = pushRepairArgs.flatMap((call) =>
      [...call.matchAll(/'([a-z]+(?:_[a-z]+)+)'/g)].map((t) => t[1]!),
    )
    // Phép kiểm phải THẤY các nhãn — nếu bộ cắt hỏng thì `tagged` rỗng và cả
    // hàng rào này im lặng biến mất mà vẫn xanh.
    expect(tagged, 'không cắt được nhãn nào từ pushRepair').toContain('causal_claim')
    // (b) MỌI tên dùng trong phép so quy tắc.
    const compared = [...src.matchAll(/\.rule\s*(?:===|!==)\s*'([a-z_]+)'/g)].map((m) => m[1]!)

    // (c) Danh sách quy tắc XUẤT KHẨU — kiểm ở RUNTIME, không qua regex.
    const bogus = [...new Set([...tagged, ...compared, ...CTR_VIOLATION_RULES])].filter(
      (t) => t.includes('_') && !emitted.has(t),
    )
    expect(bogus, `tên không quy tắc nào phát ra: ${bogus.join(', ')}`).toEqual([])
  })

  it('U3 VẪN CÒN NGUYÊN ở chặng COMPOSITE (mặc định), chỉ tắt ở ANALYSIS', () => {
    // Rủi ro lớn nhất của việc chuyển phép lọc VÀO trong bộ kiểm: lỡ tay tắt U3
    // ở mọi chặng thì lớp này mất đúng quy tắc đã sinh ra kiến trúc hai lượt, và
    // không có gì kêu lên cả.
    const pkg = makePackage()
    const built = buildPrompt({ pkg })
    const base = {
      pkg, allowedEvidenceIds: built.allowedEvidenceIds,
      allowedVideoIds: built.allowedVideoIds, allowedCohortKeys: built.allowedCohortKeys,
      hadProseOutsideJson: false,
    }
    // Ô nhạy cảm (nhắc CTR) nhưng KHÔNG khai trong metricClaims -> U3 phải kêu.
    const withSensitive = {
      ...analysis({
        keyFindings: [{
          id: 'F-001',
          statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
          findingType: 'OBSERVATION', confidence: 'MEDIUM', evidenceIds: ['OBS-001'],
          supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
          contradictingEvidenceIds: [], limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu'],
        }],
      } as never),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      metricClaims: [] as unknown[],
    }
    // Mặc định = COMPOSITE: U3 PHẢI kêu.
    const composite = validateCursorOutput({ ...base, raw: JSON.stringify(withSensitive) })
    expect(
      composite.report.claimIssues.some((i) => i.rule === 'undeclared_sensitive_unit'),
      'U3 biến mất ở chặng COMPOSITE',
    ).toBe(true)

    // Chặng ANALYSIS: U3 tắt, vì lượt 1 chưa có bản khai để mà khai thiếu.
    const anal = validateCursorOutput({ ...base, raw: JSON.stringify(withSensitive), stage: 'ANALYSIS' })
    expect(anal.report.claimIssues.some((i) => i.rule === 'undeclared_sensitive_unit')).toBe(false)
  })

  it('bản phân tích SẠCH: không lỗi, không dòng sửa lỗi thừa', () => {
    const r = runAnalysis(analysis())
    expect(r.report.passed, JSON.stringify(r.report.claimIssues)).toBe(true)
    expect(r.repairErrors).toEqual([])
  })
})
