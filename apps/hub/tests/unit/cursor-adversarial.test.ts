import { describe, expect, it } from 'vitest'

import type { AnalysisPackage } from '@/lib/analysis/package'
import { buildPrompt } from '@/lib/cursor/prompt'
import {
  CLAIM_METRICS,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  sourceRefSections,
  type CursorOutput,
} from '@/lib/cursor/schema'
import { enumerateUnits, resolveSourceRef } from '@/lib/cursor/source-ref'
import { validateCursorOutput } from '@/lib/cursor/validate'
import { detectSemanticDrift, resolvedTextByClaim } from '@/lib/cursor/run'
import { buildDeclarationPrompt } from '@/lib/cursor/declaration-prompt'
import { buildObligationSet, hashObligationSet } from '@/lib/cursor/obligation'

/**
 * MA TRẬN ĐỐI KHÁNG của schema 2.1 — mục 6 của `creator_specs/PHASE4_1_DESIGN_V2.md`.
 *
 * Đánh số THEO ĐÚNG bản thiết kế để đối chiếu được từng dòng. Bốn ca cuối (38–41)
 * là phần bổ sung mà bản bàn giao yêu cầu thêm; 42–45 là các lỗ THẬT tìm ra khi
 * cài đặt ma trận này, giữ lại làm test hồi quy vĩnh viễn.
 *
 * Ca 33 và 34 (round-trip JSONB, CHECK 0022) phải chạy trên database thật nên
 * nằm ở `tests/integration/cursor-persistence.test.ts`, không ở đây.
 *
 * RANH GIỚI TIN CẬY, nhắc lại vì ma trận này dễ bị đọc quá lời: nhóm R là TẤT
 * ĐỊNH (một ref hoặc trỏ tới một ô có thật, hoặc không). Nhóm U dựa trên phép
 * tách mệnh đề — HEURISTIC NGÔN NGỮ. Nhóm S dựa trên nhận diện từ khoá — cũng
 * heuristic. Ma trận xanh KHÔNG có nghĩa "không phát biểu sai nào lọt được".
 */

function makePackage(over: Partial<AnalysisPackage> = {}): AnalysisPackage {
  return {
    schemaVersion: '1.0.0',
    algorithmVersion: '1.0.0',
    scope: {
      workspaceId: 'ws-1',
      channelId: 'ch-1',
      channelLabel: 'phong_thuy',
      channelTitle: 'Kênh Test',
      reportingTimezone: 'America/Los_Angeles',
      windowStart: '2026-06-01',
      windowEnd: '2026-07-27',
      analysisRunId: 'run-1',
      inputHash: 'a'.repeat(64),
    },
    channelSummary: { videos: 20, medianViewsD7: 100 },
    dataCoverage: {
      videosTotal: 20,
      videosWithMetrics: 18,
      videosImmature: 2,
      metricRows: 180,
      expectedDates: 57,
      observedDates: 57,
      missingDates: [],
      metricCoverage: { views: 1, impressions: 0, impressionCtr: 0 },
      revisedRows: 0,
    },
    confidence: { score: 0.8, band: 'HIGH', drivers: {} },
    baselines: [
      { key: 'CHANNEL_FORMAT:SHORT', kind: 'CHANNEL_FORMAT', description: 'Shorts', videoCount: 12, medianViewsD7: 100 },
    ],
    featureDefinitions: [
      { key: 'views_d7', label: 'Views 7d', unit: 'COUNT', direction: 'HIGHER_IS_BETTER', version: '1.0.0', formula: 'sum(views) 7 ngày đầu' },
    ],
    observations: [
      {
        kind: 'TOP_PERFORMER',
        polarity: 'POSITIVE',
        statement: 'Video aaaaaaaaaaa ở phân vị 92 về lượt xem 7 ngày.',
        metricValues: { views_d7: 900 },
        baselineKind: 'CHANNEL_FORMAT',
        confidence: 0.8,
        limitations: [],
        evidenceRefs: [{ refType: 'VIDEO', refId: 'v1' }],
        isHypothesis: false,
      },
    ],
    anomalies: [{ kind: 'VIEW_SPIKE', youtubeVideoId: 'aaaaaaaaaaa', score: 4.2 }],
    rankedVideos: [
      { youtubeVideoId: 'aaaaaaaaaaa', title: 'A', format: 'SHORT', viewsD7: 900 },
      { youtubeVideoId: 'bbbbbbbbbbb', title: 'B', format: 'SHORT', viewsD7: 50 },
    ],
    cohortComparisons: [{ key: '2026-07-14..2026-07-27 (SHORT)', kind: 'PUBLISH_FORTNIGHT', videoCount: 8, medianViewsD7: 90 }],
    formatComparison: null,
    hypothesisCandidates: [],
    unresolvedQuestions: ['Không có impressions/CTR.'],
    missingData: ['impressions: độ phủ 0%'],
    analysisTasks: ['Suy luận, không tính lại.'],
    limitsApplied: {
      positiveObservations: { included: 1, total: 1 },
      negativeObservations: { included: 0, total: 0 },
      anomalies: { included: 1, total: 1 },
      rankedVideos: { included: 2, total: 2 },
      cohorts: { included: 1, total: 1 },
      hypotheses: { included: 0, total: 0 },
      truncatedForSize: false,
    },
    ...over,
  } as AnalysisPackage
}

const FINDING = {
  id: 'F-001' as const,
  statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
  findingType: 'OBSERVATION' as const,
  confidence: 'MEDIUM' as const,
  evidenceIds: ['OBS-001'],
  supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
  contradictingEvidenceIds: [] as string[],
  limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu'],
}

/** Claim mốc: giới hạn phương pháp hợp lệ, trỏ vào `F-001.limitations[0]`. */
const CLAIM = {
  id: 'MC-001' as const,
  claimType: 'METHODOLOGY_LIMITATION' as const,
  subjectMetric: 'views' as const,
  relatedMetric: 'impression_ctr' as const,
  judgement: 'LOW' as const,
  assertionStatus: 'LIMITATION' as const,
  evidenceIds: [] as string[],
  requiresMissingnessDisclosure: false,
  sourceRef: { section: 'KEY_FINDING' as const, itemId: 'F-001', field: 'limitations', ordinal: 0 },
}

/**
 * Output MỐC — cố ý KHÔNG có chỉ số nhạy cảm ngoài ô đang xét.
 *
 * Mỗi ca chỉ đổi một thứ, nên mọi lỗi báo ra đều quy được về đúng thứ đã đổi.
 */
function base(over: Partial<CursorOutput> = {}): CursorOutput {
  return {
    schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
      confidence: 'MEDIUM',
      confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ trong cửa sổ quan sát này.',
      primaryConstraint: 'Cỡ mẫu còn nhỏ nên kết luận xu hướng cần thận trọng.',
    },
    keyFindings: [FINDING],
    hypotheses: [],
    recommendations: [],
    experiments: [],
    manualReviewTargets: [],
    dataRequests: [],
    explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
    metricClaims: [CLAIM],
    selfCheck: {
      usedOnlyProvidedEvidence: true,
      recomputedMetrics: false,
      madeCausalClaims: false,
      madeCtrOrImpressionClaims: false,
      allFindingEvidenceResolved: true,
    },
    ...over,
  }
}

function run(output: unknown, pkg = makePackage()) {
  const built = buildPrompt({ pkg })
  return validateCursorOutput({
    raw: typeof output === 'string' ? output : JSON.stringify(output),
    pkg,
    allowedEvidenceIds: built.allowedEvidenceIds,
    allowedVideoIds: built.allowedVideoIds,
    allowedCohortKeys: built.allowedCohortKeys,
    hadProseOutsideJson: false,
  })
}

const rules = (r: ReturnType<typeof run>): string[] =>
  [...r.report.structuralIssues, ...r.report.evidenceIssues, ...r.report.claimIssues, ...r.report.qualityIssues].map(
    (i) => i.rule,
  )

/** Claim với `sourceRef` thay thế, giữ nguyên phần còn lại. */
const at = (
  ref: Partial<{ section: string; itemId: string; field: string; ordinal: number }>,
  over: Record<string, unknown> = {},
) => ({ ...CLAIM, ...over, sourceRef: { ...CLAIM.sourceRef, ...ref } }) as unknown as typeof CLAIM

describe('ma trận đối kháng 2.1 — MỐC', () => {
  it('output mốc ĐẠT (nếu ca này đỏ thì mọi ca dưới đều vô nghĩa)', () => {
    const r = run(base())
    expect(rules(r), JSON.stringify(r.report)).toEqual([])
    expect(r.report.passed).toBe(true)
  })
})

describe('ma trận 1–7: PHÂN GIẢI (R) — tất định', () => {
  it('1. ref hợp lệ tới KEY_FINDING/F-001/statement', () => {
    const res = resolveSourceRef(base(), {
      section: 'KEY_FINDING',
      itemId: 'F-001',
      field: 'statement',
      ordinal: 0,
    })
    expect('ok' in res && res.ok.text).toBe(FINDING.statement)
    expect('ok' in res && res.ok.pointer).toBe('KEY_FINDING(F-001).statement[0]')
  })

  it('2. itemId KHÔNG tồn tại -> R1 source_ref_unresolved', () => {
    const r = run(base({ metricClaims: [at({ itemId: 'F-999' })] }))
    expect(rules(r)).toContain('source_ref_unresolved')
    expect(r.report.passed).toBe(false)
  })

  it('3. field KHÔNG tồn tại -> R2 source_ref_unresolved', () => {
    const r = run(base({ metricClaims: [at({ field: 'khongCoTruongNay' })] }))
    expect(rules(r)).toContain('source_ref_unresolved')
    expect(r.report.passed).toBe(false)
  })

  it('4. ordinal NGOÀI phạm vi -> R3 source_ref_unresolved', () => {
    const r = run(base({ metricClaims: [at({ ordinal: 5 })] }))
    expect(rules(r)).toContain('source_ref_unresolved')
    expect(r.report.passed).toBe(false)
  })

  it('5. hai item cùng itemId -> R4 duplicate_source_item', () => {
    const r = run(base({ keyFindings: [FINDING, { ...FINDING, statement: 'Một phát biểu khác hẳn về nhịp đăng.' }] }))
    expect(rules(r)).toContain('duplicate_source_item')
    expect(r.report.passed).toBe(false)
  })

  it('6. ANALYSIS_SUMMARY kèm itemId khác rỗng -> R5 source_ref_malformed', () => {
    const r = run(
      base({
        metricClaims: [at({ section: 'ANALYSIS_SUMMARY', itemId: 'F-001', field: 'primaryConstraint' })],
      }),
    )
    expect(rules(r)).toContain('source_ref_malformed')
    expect(r.report.passed).toBe(false)
  })

  it('7. ref tới field KHÔNG phải văn xuôi (confidence) -> R2', () => {
    // `confidence` là ENUM: lúc chạy giá trị vẫn là chuỗi, nên kiểm `typeof`
    // không đủ. Danh sách trường hợp lệ phải hỏi SCHEMA.
    const r = run(base({ metricClaims: [at({ field: 'confidence' })] }))
    expect(rules(r)).toContain('source_ref_unresolved')
    expect(r.report.passed).toBe(false)
  })

  it('7b. ref tới field SỐ (minimumWindowDays) -> R2', () => {
    const out = base({
      hypotheses: [
        {
          id: 'H-001',
          statement: 'Một giả thuyết trung tính về nhịp đăng của kênh này.',
          status: 'UNVERIFIED',
          confidence: 'LOW',
          supportingEvidenceIds: ['OBS-001'],
          contradictingEvidenceIds: [],
          missingEvidence: ['Chưa có dữ liệu tiếp cận'],
          validationMethod: 'Theo dõi thêm hai tuần rồi so sánh lại.',
        },
      ],
      experiments: [
        {
          id: 'E-001',
          hypothesisId: 'H-001',
          change: 'Đổi nhịp đăng sang hai video mỗi tuần.',
          baseline: 'Nhịp hiện tại một video mỗi tuần.',
          successMetrics: ['views_d7 trung vị tăng'],
          minimumWindowDays: 14,
          sampleLimitations: [],
          stopConditions: ['Dừng nếu lượt xem giảm quá nửa'],
          interpretationRisks: ['Có thể trùng mùa vụ'],
        },
      ],
      metricClaims: [at({ section: 'EXPERIMENT', itemId: 'E-001', field: 'minimumWindowDays' })],
    })
    expect(rules(run(out))).toContain('source_ref_unresolved')
  })
})

describe('ma trận 8–12: ỔN ĐỊNH trước thay đổi thứ tự', () => {
  const F2 = {
    ...FINDING,
    id: 'F-002' as const,
    statement: 'Một phát hiện thứ hai, trung tính, về nhịp đăng của kênh.',
    limitations: ['chưa đủ ngày quan sát để đọc xu hướng'],
  }

  it('8. ĐẢO THỨ TỰ keyFindings -> mọi ref vẫn phân giải ĐÚNG ô cũ', () => {
    const a = base({ keyFindings: [FINDING, F2] })
    const b = base({ keyFindings: [F2, FINDING] })
    const ref = { section: 'KEY_FINDING' as const, itemId: 'F-001', field: 'limitations', ordinal: 0 }
    const ra = resolveSourceRef(a, ref)
    const rb = resolveSourceRef(b, ref)
    expect('ok' in ra && ra.ok.text).toBe(FINDING.limitations[0])
    expect('ok' in rb && rb.ok.text).toBe(FINDING.limitations[0])
    expect(run(b).report.passed).toBe(true)
  })

  it('9. CHÈN một finding mới -> ref cũ không đổi', () => {
    const out = base({ keyFindings: [F2, FINDING] })
    expect(run(out).report.passed).toBe(true)
    const res = resolveSourceRef(out, CLAIM.sourceRef)
    expect('ok' in res && res.ok.text).toBe(FINDING.limitations[0])
  })

  it('10. XOÁ phần tử được trỏ -> R3 hoặc D3', () => {
    const out = base({ keyFindings: [{ ...FINDING, limitations: [] }] })
    expect(rules(run(out))).toContain('source_ref_unresolved')
  })

  it('11. đảo thứ tự TRONG limitations và sửa ordinal cho khớp -> D4 cho phép', () => {
    const root = [CLAIM] as never
    const repaired = [at({ ordinal: 1 })] as never
    const text = new Map([['MC-001', FINDING.limitations[0]!]])
    expect(detectSemanticDrift(root, repaired, text, text)).toHaveLength(0)
  })

  it('12. đảo thứ tự nhưng KHÔNG sửa ordinal -> D3 chặn (nội dung ô đã khác)', () => {
    const root = [CLAIM] as never
    const repaired = [CLAIM] as never
    const drift = detectSemanticDrift(
      root,
      repaired,
      new Map([['MC-001', 'cỡ mẫu lượt xem thấp nên CTR nhiễu']]),
      new Map([['MC-001', 'chưa đủ ngày quan sát để đọc xu hướng']]),
    )
    expect(drift.join(' ')).toContain('văn bản ô nguồn đã đổi')
  })
})

describe('ma trận 13–17: MỘT Ô — MỘT PHÁT BIỂU (U)', () => {
  const twoStatements = 'CTR chưa đo trong kỳ này; impressions cũng chưa bật'

  it('13. ô có HAI mệnh đề nhạy cảm, MỘT claim -> U1', () => {
    const r = run(base({ keyFindings: [{ ...FINDING, limitations: [twoStatements] }] }))
    expect(rules(r)).toContain('multiple_assertions_in_source_unit')
    expect(r.report.passed).toBe(false)
  })

  it('14. ô có HAI mệnh đề nhạy cảm, HAI claim cùng trỏ vào -> vẫn U1 (phải TÁCH ô)', () => {
    const r = run(
      base({
        keyFindings: [{ ...FINDING, limitations: [twoStatements] }],
        metricClaims: [CLAIM, at({}, { id: 'MC-002', subjectMetric: 'sample_size' })],
      }),
    )
    expect(rules(r)).toContain('multiple_assertions_in_source_unit')
    expect(r.report.passed).toBe(false)
  })

  it('15. HAI claim cùng trỏ MỘT ô -> U2', () => {
    const r = run(base({ metricClaims: [CLAIM, at({}, { id: 'MC-002' })] }))
    expect(rules(r)).toContain('multiple_claims_for_source_unit')
    expect(r.report.passed).toBe(false)
  })

  it('16. ô nhạy cảm KHÔNG có claim -> U3', () => {
    const r = run(base({ metricClaims: [] }))
    expect(rules(r)).toContain('undeclared_sensitive_unit')
    expect(r.report.passed).toBe(false)
  })

  it('17. claim trỏ ô KHÔNG liên quan chỉ số đã khai -> U4 orphan', () => {
    const r = run(base({ metricClaims: [at({ field: 'statement' }, { subjectMetric: 'packaging' })] }))
    expect(rules(r)).toContain('orphan_metric_claim')
    expect(r.report.passed).toBe(false)
  })
})

describe('ma trận 18–25: NGỮ NGHĨA trên VĂN BẢN ĐÃ PHÂN GIẢI (S)', () => {
  /** Đặt câu vào ô rồi khai bằng một claim trỏ đúng ô đó. */
  const withProse = (prose: string, over: Record<string, unknown>) =>
    base({
      keyFindings: [{ ...FINDING, limitations: [prose] }],
      metricClaims: [at({}, over)],
    })

  it('18. S1: subjectMetric KHÔNG có trong ô', () => {
    const r = run(withProse('CTR nhiễu trong kỳ này', { subjectMetric: 'retention' }))
    expect(rules(r)).toContain('subject_metric_not_in_text')
  })

  it('19. S2: tình thái KHÔNG khớp', () => {
    const r = run(
      withProse('lượt xem thấp và CTR thấp', {
        claimType: 'DIAGNOSTIC_PLAN',
        subjectMetric: 'views',
        assertionStatus: 'CONDITIONAL',
      }),
    )
    expect(rules(r)).toContain('modality_not_supported_by_text')
  })

  it('20. S3: chiều phán xét NGƯỢC', () => {
    const r = run(
      withProse('lượt xem ở mức cao nên CTR nhiễu', { subjectMetric: 'views', judgement: 'LOW' }),
    )
    expect(rules(r)).toContain('judgement_contradicts_text')
  })

  it('21. S4: phân cực NGƯỢC (phủ định cân bằng)', () => {
    const r = run(
      withProse('CTR không thấp, retention giảm', {
        claimType: 'OBSERVATION',
        subjectMetric: 'impression_ctr',
        relatedMetric: 'retention',
        judgement: 'LOW',
        assertionStatus: 'ASSERTED',
        evidenceIds: ['OBS-001'],
      }),
    )
    expect(rules(r)).toContain('claim_polarity_mismatch')
  })

  it('22. S5: ASSERTED về chỉ số phủ 0%', () => {
    const r = run(
      withProse('CTR thấp', {
        claimType: 'OBSERVATION',
        subjectMetric: 'impression_ctr',
        relatedMetric: 'NONE',
        judgement: 'LOW',
        assertionStatus: 'ASSERTED',
        evidenceIds: ['OBS-001'],
      }),
    )
    expect(rules(r)).toContain('asserted_claim_on_missing_metric')
  })

  it('23a. S6: CAUSAL + ASSERTED bị cấm tuyệt đối', () => {
    const r = run(
      withProse('thumbnail kém gây ra sụt giảm lượt xem', {
        claimType: 'CAUSAL',
        subjectMetric: 'thumbnail',
        relatedMetric: 'views',
        judgement: 'INEFFECTIVE',
        assertionStatus: 'ASSERTED',
        evidenceIds: ['OBS-001'],
      }),
    )
    expect(rules(r)).toContain('asserted_causal_claim')
  })

  it('23b. S6: CAUSAL KHÔNG bằng chứng, kể cả ở dạng CONDITIONAL', () => {
    const r = run(
      withProse('nếu thumbnail kém thì lượt xem có thể giảm', {
        claimType: 'CAUSAL',
        subjectMetric: 'thumbnail',
        relatedMetric: 'views',
        judgement: 'UNKNOWN',
        assertionStatus: 'CONDITIONAL',
        evidenceIds: [],
      }),
    )
    expect(rules(r)).toContain('causal_claim_without_evidence')
  })

  it('24. S7: METHODOLOGY_LIMITATION có subject TRÙNG related', () => {
    const r = run(
      withProse('CTR nhiễu trong kỳ này', {
        subjectMetric: 'impression_ctr',
        relatedMetric: 'impression_ctr',
      }),
    )
    expect(rules(r)).toContain('methodology_disguising_assertion')
  })

  it('24b. S7: METHODOLOGY_LIMITATION có subject CŨNG thiếu dữ liệu', () => {
    const r = run(
      withProse('impressions nhiễu nên CTR chưa đọc được', {
        subjectMetric: 'impressions',
        relatedMetric: 'impression_ctr',
      }),
    )
    expect(rules(r)).toContain('methodology_subject_also_missing')
  })

  it('25. S8: tổ hợp loại/trạng thái/phán xét MÂU THUẪN', () => {
    const COMBOS: Array<Record<string, unknown>> = [
      { assertionStatus: 'NEGATED_ACTION', claimType: 'OBSERVATION' },
      { assertionStatus: 'LIMITATION', claimType: 'RECOMMENDATION' },
      { assertionStatus: 'QUESTION', judgement: 'LOW', claimType: 'DIAGNOSTIC_PLAN' },
      { assertionStatus: 'ASSERTED', claimType: 'DIAGNOSTIC_PLAN', evidenceIds: ['OBS-001'] },
      { assertionStatus: 'ASSERTED', claimType: 'METHODOLOGY_LIMITATION', evidenceIds: ['OBS-001'] },
    ]
    for (const c of COMBOS) {
      const r = run(withProse('không dùng CTR làm tiêu chí, chưa đủ dữ liệu', { subjectMetric: 'impression_ctr', ...c }))
      expect(rules(r), JSON.stringify(c)).toContain('contradictory_claim_fields')
    }
  })
})

describe('ma trận 26–30: BẤT BIẾN khi SỬA LỖI (D)', () => {
  const root = [CLAIM] as never
  const T = (t: string) => new Map([['MC-001', t]])
  const SAME = T(FINDING.limitations[0]!)

  it('26. đổi sourceRef sang ô có NỘI DUNG KHÁC -> chặn', () => {
    const repaired = [at({ field: 'statement' })] as never
    const drift = detectSemanticDrift(root, repaired, SAME, T(FINDING.statement)).join(' ')
    expect(drift).toContain('sourceRef')
    expect(drift).toContain('văn bản ô nguồn đã đổi')
  })

  it('27. đổi VĂN BẢN của ô được trỏ -> D3', () => {
    const drift = detectSemanticDrift(root, root, SAME, T('cỡ mẫu lượt xem quá nhỏ nên CTR nhiễu')).join(' ')
    expect(drift).toContain('văn bản ô nguồn đã đổi')
  })

  it('28. đổi SỐ trong ô được trỏ -> D5', () => {
    const drift = detectSemanticDrift(
      root,
      root,
      T('cỡ mẫu 12 video nên CTR nhiễu'),
      T('cỡ mẫu 120 video nên CTR nhiễu'),
    ).join(' ')
    expect(drift).toContain('đổi SỐ trong text')
  })

  it('29. CHỈ đổi ordinal, ô vẫn là ô cũ và nội dung y hệt -> CHO PHÉP', () => {
    // Bản thiết kế viết D4 rộng hơn ("đổi sourceRef mà resolvedText y hệt thì
    // cho phép"). Cài đặt SIẾT lại: chỉ `ordinal` được đổi. Lý do ở ca 40 —
    // hai mục khác nhau có thể chứa cùng một câu, nên "nội dung giống" không đủ
    // để kết luận vẫn là cùng một phát biểu.
    expect(detectSemanticDrift(root, [at({ ordinal: 1 })] as never, SAME, SAME)).toHaveLength(0)
  })

  it('30. thêm/bớt/đổi tên claim -> D1; đổi trường ngữ nghĩa -> D2', () => {
    expect(detectSemanticDrift(root, [] as never, SAME, SAME).join(' ')).toContain('bỏ mất claim MC-001')
    expect(
      detectSemanticDrift(root, [CLAIM, { ...CLAIM, id: 'MC-002' }] as never, SAME, SAME).join(' '),
    ).toContain('MỚI xuất hiện')
    expect(
      detectSemanticDrift(root, [{ ...CLAIM, id: 'MC-009' }] as never, SAME, SAME).join(' '),
    ).toContain('MC-009')
    for (const k of ['subjectMetric', 'relatedMetric', 'claimType', 'assertionStatus', 'judgement'] as const) {
      const changed = { ...CLAIM, [k]: k === 'judgement' ? 'HIGH' : k === 'claimType' ? 'OBSERVATION' : 'retention' }
      expect(detectSemanticDrift(root, [changed] as never, SAME, SAME).join(' ')).toContain(k)
    }
  })
})

describe('ma trận 31–32: TƯƠNG THÍCH (33–34 nằm ở test tích hợp)', () => {
  it('31. payload 2.0 -> UNSUPPORTED_SCHEMA_VERSION', () => {
    expect(run({ ...base(), schemaVersion: '2.0' }).failureClass).toBe('UNSUPPORTED_SCHEMA_VERSION')
  })

  it('32. payload 1.0 -> UNSUPPORTED_SCHEMA_VERSION', () => {
    expect(run({ ...base(), schemaVersion: '1.0' }).failureClass).toBe('UNSUPPORTED_SCHEMA_VERSION')
  })
})

describe('ma trận 35–37: TÍNH CHẤT (quét tổ hợp)', () => {
  it('35. MỌI section × MỌI field hợp lệ đều phân giải được', () => {
    const out = base({
      hypotheses: [
        {
          id: 'H-001',
          statement: 'Một giả thuyết trung tính về nhịp đăng của kênh này.',
          status: 'UNVERIFIED',
          confidence: 'LOW',
          supportingEvidenceIds: ['OBS-001'],
          contradictingEvidenceIds: [],
          missingEvidence: ['Chưa có dữ liệu tiếp cận'],
          validationMethod: 'Theo dõi thêm hai tuần rồi so sánh lại.',
        },
      ],
      recommendations: [
        {
          id: 'R-001',
          action: 'Giữ nhịp đăng hiện tại trong hai tuần tới.',
          priority: 'P1',
          category: 'CONTINUE',
          rationale: 'Bằng chứng cho thấy nhịp hiện tại phù hợp với nhóm cùng định dạng.',
          evidenceIds: ['OBS-001'],
          expectedValue: 'MEDIUM',
          effort: 'LOW',
          reversibility: 'HIGH',
          measurementFeasibility: 'HIGH',
          risks: ['Có thể trùng mùa vụ'],
          successMetric: 'views_d7 trung vị không giảm',
        },
      ],
      experiments: [
        {
          id: 'E-001',
          hypothesisId: 'H-001',
          change: 'Đổi nhịp đăng sang hai video mỗi tuần.',
          baseline: 'Nhịp hiện tại một video mỗi tuần.',
          successMetrics: ['views_d7 trung vị tăng'],
          minimumWindowDays: 14,
          sampleLimitations: ['Số video trong cửa sổ còn ít'],
          stopConditions: ['Dừng nếu lượt xem giảm quá nửa'],
          interpretationRisks: ['Có thể trùng mùa vụ'],
        },
      ],
      manualReviewTargets: [
        {
          targetType: 'VIDEO',
          targetId: 'aaaaaaaaaaa',
          reason: 'Cần rà soát nội dung của video dẫn đầu.',
          evidenceIds: ['OBS-001'],
          reviewQuestions: ['Nội dung có khác biệt gì rõ rệt?'],
        },
      ],
      dataRequests: [
        {
          metricOrArtifact: 'Dữ liệu tiếp cận theo ngày',
          reason: 'Cần để tách khâu tiếp cận khỏi khâu giữ chân.',
          decisionUnlocked: 'Biết nên ưu tiên sửa gì trước.',
        },
      ],
    })

    let checked = 0
    for (const spec of sourceRefSections()) {
      for (const f of spec.fields) {
        const field = spec.kind === 'INDEXED' ? `${f.name}@0` : f.name
        const res = resolveSourceRef(out, {
          section: spec.section as never,
          itemId: spec.kind === 'ITEM' ? spec.itemIdExample : '',
          field,
          ordinal: 0,
        })
        expect(res, `${spec.section}.${field} KHÔNG phân giải được`).toHaveProperty('ok')
        checked++
      }
    }
    // Bảng phải KHÔNG rỗng — một bộ sinh hỏng trả về mảng rỗng cũng làm vòng lặp
    // trên xanh, và ca này sẽ im lặng không kiểm gì.
    expect(checked).toBe(enumerateUnits(out).length)
  })

  it('36. MỌI chỉ số nhạy cảm × MỌI assertionStatus giữ đúng S1–S5', () => {
    const SENSITIVE = ['impressions', 'impression_ctr', 'thumbnail', 'packaging'] as const
    const STATUSES = ['ASSERTED', 'CONDITIONAL', 'QUESTION', 'NEGATED_ACTION', 'LIMITATION'] as const
    for (const metric of SENSITIVE) {
      for (const status of STATUSES) {
        // Ô nói thẳng "X thấp" — một KHẲNG ĐỊNH trần về chỉ số phủ 0%.
        const prose = `${metric} thấp trong kỳ này`
        const r = run(
          base({
            keyFindings: [{ ...FINDING, limitations: [prose] }],
            metricClaims: [
              at({}, {
                claimType: 'OBSERVATION',
                subjectMetric: metric,
                relatedMetric: 'NONE',
                judgement: 'LOW',
                assertionStatus: status,
                evidenceIds: ['OBS-001'],
              }),
            ],
          }),
        )
        expect(r.report.passed, `${metric}/${status} lại ĐẠT`).toBe(false)
      }
    }
  })

  it('37. KHÔNG tổ hợp hợp-lệ-schema nào lọt qua toàn bộ nhánh R/U/S', () => {
    const TYPES = ['OBSERVATION', 'COMPARISON', 'CAUSAL', 'DIAGNOSTIC_PLAN', 'METHODOLOGY_LIMITATION', 'RECOMMENDATION'] as const
    const STATUSES = ['ASSERTED', 'CONDITIONAL', 'QUESTION', 'NEGATED_ACTION', 'LIMITATION'] as const
    const JUDGEMENTS = ['HIGH', 'LOW', 'INCREASED', 'DECREASED', 'EFFECTIVE', 'INEFFECTIVE', 'UNKNOWN', 'NOT_APPLICABLE'] as const
    const RELATED = ['NONE', 'views', 'retention'] as const

    let swept = 0
    for (const claimType of TYPES) {
      for (const assertionStatus of STATUSES) {
        for (const judgement of JUDGEMENTS) {
          for (const relatedMetric of RELATED) {
            const r = run(
              base({
                // Câu này là một KẾT LUẬN trần về CTR ở gói có độ phủ 0%. Không
                // cách khai báo nào được phép biến nó thành hợp lệ.
                keyFindings: [{ ...FINDING, limitations: ['CTR thấp rõ rệt ở nhóm này'] }],
                metricClaims: [
                  at({}, {
                    claimType,
                    subjectMetric: 'impression_ctr',
                    relatedMetric,
                    judgement,
                    assertionStatus,
                    evidenceIds: ['OBS-001'],
                  }),
                ],
              }),
            )
            expect(
              r.report.passed,
              `${claimType}/${assertionStatus}/${judgement}/${relatedMetric} lại ĐẠT`,
            ).toBe(false)
            swept++
          }
        }
      }
    }
    expect(swept).toBe(TYPES.length * STATUSES.length * JUDGEMENTS.length * RELATED.length)
  })
})

/**
 * 38–41: bốn ca BỔ SUNG mà bản bàn giao yêu cầu.
 *
 * Cả bốn tấn công cùng một chỗ: "nội dung giống nhau" KHÔNG đủ để kết luận "vẫn
 * là cùng một phát biểu". Hai mục khác nhau có thể chứa y hệt một câu; cho phép
 * nhảy giữa chúng là cho phép đổi CHỦ SỞ HỮU của một kết luận mà không ai thấy.
 */
describe('ma trận 38–41: TRÙNG VĂN BẢN và ĐỔI QUYỀN SỞ HỮU', () => {
  const SAME_TEXT = 'cỡ mẫu lượt xem thấp nên CTR nhiễu'
  const T = (t: string) => new Map([['MC-001', t]])

  it('38. văn bản TRÙNG HỆT ở hai ITEM khác nhau -> đổi ref vẫn bị chặn', () => {
    const root = [CLAIM] as never
    const moved = [at({ itemId: 'F-002' })] as never
    const drift = detectSemanticDrift(root, moved, T(SAME_TEXT), T(SAME_TEXT)).join(' ')
    expect(drift).toContain('sourceRef')
    expect(drift).toContain('KEY_FINDING|F-001|limitations')
    expect(drift).toContain('KEY_FINDING|F-002|limitations')
  })

  it('39. văn bản TRÙNG HỆT ở hai SECTION khác nhau -> đổi ref vẫn bị chặn', () => {
    const root = [CLAIM] as never
    const moved = [at({ section: 'RECOMMENDATION', itemId: 'R-001', field: 'risks' })] as never
    const drift = detectSemanticDrift(root, moved, T(SAME_TEXT), T(SAME_TEXT)).join(' ')
    expect(drift).toContain('RECOMMENDATION|R-001|risks')
  })

  it('40. ĐỔI QUYỀN SỞ HỮU finding -> recommendation với nội dung Y HỆT', () => {
    // Đây là ca quyết định chính sách: nếu chỉ so nội dung thì lần sửa này lọt
    // hoàn toàn, và một GIỚI HẠN của phát hiện F-001 lặng lẽ trở thành RỦI RO
    // của khuyến nghị R-001 — cùng chữ, khác hẳn ý nghĩa vận hành.
    const root = [CLAIM] as never
    const moved = [at({ section: 'RECOMMENDATION', itemId: 'R-001', field: 'rationale' })] as never
    expect(detectSemanticDrift(root, moved, T(SAME_TEXT), T(SAME_TEXT)).length).toBeGreaterThan(0)
  })

  it('41. TRÙNG nội dung trong CÙNG field -> AMBIGUOUS_DUPLICATE_TEXT, không đoán bừa', () => {
    const out = base({
      keyFindings: [{ ...FINDING, limitations: [SAME_TEXT, SAME_TEXT] }],
    })
    const res = resolveSourceRef(out, CLAIM.sourceRef)
    expect('error' in res && res.error).toBe('AMBIGUOUS_DUPLICATE_TEXT')
    const r = run(out)
    expect(rules(r)).toContain('source_ref_ambiguous')
    expect(r.report.passed).toBe(false)
  })
})

/**
 * 42–45: LỖ THẬT tìm ra khi cài đặt ma trận trên.
 *
 * Không ca nào trong bốn ca này nằm trong bản thiết kế — chúng lộ ra vì ma trận
 * ép phải viết ra ca "đã sửa đúng thì phải đi qua", chứ không chỉ ca "sai thì
 * phải chặn". Một bộ quy tắc chỉ có ca chặn có thể siết tới mức không ai viết
 * đúng được, và không test nào phát hiện.
 */
describe('ma trận 42–45: hồi quy cho các lỗ tìm ra khi cài đặt', () => {
  it('42. hai claim trỏ HAI PHẦN TỬ khác nhau của cùng field -> KHÔNG phải U2', () => {
    // Danh tính ô phải gồm `ordinal`. Thiếu nó thì `limitations[0]` và
    // `limitations[1]` mang cùng danh tính, U2 báo "hai claim cùng một ô", và
    // cách sửa mà U1 yêu cầu (tách thành nhiều phần tử) tự nó bị chặn.
    const r = run(
      base({
        keyFindings: [{ ...FINDING, limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'] }],
        metricClaims: [
          CLAIM,
          at({ ordinal: 1 }, {
            id: 'MC-002',
            claimType: 'RECOMMENDATION',
            subjectMetric: 'impressions',
            relatedMetric: 'NONE',
            judgement: 'UNKNOWN',
            assertionStatus: 'NEGATED_ACTION',
          }),
        ],
      }),
    )
    expect(rules(r), JSON.stringify(r.report.claimIssues)).not.toContain('multiple_claims_for_source_unit')
    expect(r.report.passed).toBe(true)
  })

  it('43. khai cho limitations[0] KHÔNG làm limitations[1] thành "đã khai"', () => {
    const r = run(
      base({
        keyFindings: [{ ...FINDING, limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'] }],
      }),
    )
    expect(
      r.report.claimIssues.some(
        (i) => i.rule === 'undeclared_sensitive_unit' && i.path === 'KEY_FINDING(F-001).limitations[1]',
      ),
    ).toBe(true)
  })

  it('44. claim trỏ vào manualReviewTargets ĐƯỢC TÍNH là đã khai', () => {
    // Bộ phân giải và bộ liệt kê từng dựng hai chuỗi danh tính khác nhau cho
    // cùng một ô (`MANUAL_REVIEW|0|reason` với `MANUAL_REVIEW||reason@0`), nên
    // mọi claim trỏ vào đây đều bị báo "chưa khai" dù đã khai đúng.
    const r = run(
      base({
        manualReviewTargets: [
          {
            targetType: 'VIDEO',
            targetId: 'aaaaaaaaaaa',
            reason: 'chưa bật đo impressions nên cần xem tay',
            evidenceIds: ['OBS-001'],
            reviewQuestions: ['Nội dung có khác biệt gì rõ rệt?'],
          },
        ],
        metricClaims: [
          CLAIM,
          at({ section: 'MANUAL_REVIEW', itemId: '', field: 'reason@0' }, {
            id: 'MC-002',
            claimType: 'RECOMMENDATION',
            subjectMetric: 'impressions',
            relatedMetric: 'NONE',
            judgement: 'UNKNOWN',
            assertionStatus: 'NEGATED_ACTION',
          }),
        ],
      }),
    )
    expect(rules(r), JSON.stringify(r.report.claimIssues)).not.toContain('undeclared_sensitive_unit')
    expect(r.report.passed).toBe(true)
  })

  it('45b. C1 (Codex): resolveSourceRef TỰ từ chối itemId trùng, không lấy mục đầu', () => {
    // `findIndex` lặng lẽ chọn mục đầu tiên. Luồng đầy đủ vẫn chặn nhờ
    // `findDuplicateItemIds`, nhưng hàm phân giải là hàm dùng chung: nó không
    // được phép trả "ok" cho một tham chiếu mập mờ.
    const out = base({
      keyFindings: [
        { ...FINDING, statement: 'CTR thấp ở nhóm A trong cửa sổ quan sát này.' },
        { ...FINDING, statement: 'CTR cao ở nhóm B trong cửa sổ quan sát này.' },
      ],
    })
    const res = resolveSourceRef(out, {
      section: 'KEY_FINDING',
      itemId: 'F-001',
      field: 'statement',
      ordinal: 0,
    })
    expect('error' in res && res.error).toBe('DUPLICATE_ITEM_ID')
    expect(rules(run(out))).toContain('duplicate_source_item')
  })

  it('45c. C3 (Codex): "đồng thời" tách mệnh đề -> U1 bắt hai phán xét trong một ô', () => {
    const r = run(base({ keyFindings: [{ ...FINDING, limitations: ['CTR thấp đồng thời CTR giảm mạnh'] }] }))
    expect(rules(r)).toContain('multiple_assertions_in_source_unit')
    expect(r.report.passed).toBe(false)
  })

  it('45d. C5 (Codex): D3/D5 phải THẬT SỰ chạy khi runner gọi drift', () => {
    // Runner từng gọi `detectSemanticDrift(root, repaired)` mà không truyền hai
    // map văn bản, nên D3 ("nội dung ô không đổi") và D5 ("số không đổi") bỏ qua
    // MỌI claim. Phép kiểm có chạy, không báo lỗi, và không nhìn vào gì cả.
    //
    // Ca này dựng lại đúng đường đi thật: cùng một claim, ô được trỏ tới đổi số.
    const rootOut = base({ keyFindings: [{ ...FINDING, limitations: ['CTR cần đạt 2% trước khi kết luận'] }] })
    const repairedOut = base({ keyFindings: [{ ...FINDING, limitations: ['CTR cần đạt 9% trước khi kết luận'] }] })
    const drift = detectSemanticDrift(
      rootOut.metricClaims,
      repairedOut.metricClaims,
      resolvedTextByClaim(rootOut, rootOut.metricClaims),
      resolvedTextByClaim(repairedOut, repairedOut.metricClaims),
    )
    expect(drift.join(' ')).toContain('đổi SỐ trong text')
    expect(drift.join(' ')).toContain('văn bản ô nguồn đã đổi')

    // Và bản đồ văn bản phải KHÔNG rỗng — một map rỗng cũng làm mọi phép so
    // "không thấy trôi dạt", đúng lỗi đang sửa.
    expect(resolvedTextByClaim(rootOut, rootOut.metricClaims).get('MC-001')).toBe(
      'CTR cần đạt 2% trước khi kết luận',
    )
  })

  it('45e. C7 (Codex): prompt NÓI RÕ ràng buộc bằng chứng phải nhắc subjectMetric', () => {
    // Một ràng buộc có hiệu lực lúc chạy (mức HIGH, chặn ĐẠT) mà prompt không
    // hề nêu là đúng khoảng trống đã làm hỏng hai lô trước.
    // Ràng buộc này áp cho KHAI BÁO, nên nó sống ở prompt lượt 2.
    const set = buildObligationSet(base())
    const { text } = buildDeclarationPrompt({
      analysisPayload: base(), obligationSet: set,
      obligationSetHash: hashObligationSet(set), analysisPayloadHash: set.analysisHash,
    })
    expect(text).toContain('Bằng chứng được trích phải NÓI VỀ chính `subjectMetric`')
  })

  it('45f. MỌI khoá chỉ số phải khớp CHÍNH TÊN NÓ trong văn xuôi', () => {
    // Prompt bảo mô hình dùng đúng các chuỗi này ở `subjectMetric`, nên mô hình
    // cũng viết đúng chúng vào văn xuôi. Một khoá không tự khớp tên mình biến
    // hành vi đúng đó thành lỗi `subject_metric_not_in_text`.
    //
    // `impression_ctr` đã hỏng đúng như vậy: `\bctr\b` không khớp "impression_ctr"
    // vì "_" là ký tự \w nên không có biên từ. Lần thăm dò hinh_su đầu tiên mất
    // 8 lỗi vì một biên từ.
    for (const metric of CLAIM_METRICS) {
      if (metric === 'NONE') continue
      const r = run(
        base({
          keyFindings: [{ ...FINDING, limitations: [`Chưa đọc được ${metric} trong cửa sổ này`] }],
          metricClaims: [
            at({}, {
              claimType: 'METHODOLOGY_LIMITATION',
              subjectMetric: metric,
              relatedMetric: metric === 'views' ? 'retention' : 'views',
              judgement: 'UNKNOWN',
              assertionStatus: 'LIMITATION',
            }),
          ],
        }),
      )
      expect(
        r.report.claimIssues.some((i) => i.rule === 'subject_metric_not_in_text'),
        `khoá "${metric}" KHÔNG tự khớp tên nó`,
      ).toBe(false)
    }
  })

  it('45g. gạch ngang GHÉP DANH NGỮ không bị đếm thành hai phát biểu', () => {
    // Ca thật từ hinh_su: "quyết định phân phối–packaging" và "nhóm giữ chân
    // cao–views thấp" dùng gạch ngang để ghép danh ngữ. Tách ở đó là chặn oan.
    const r = run(
      base({
        keyFindings: [
          {
            ...FINDING,
            limitations: ['Thiếu impressions nên quyết định phân phối–packaging nằm ngoài phạm vi'],
          },
        ],
        metricClaims: [
          at({}, {
            claimType: 'METHODOLOGY_LIMITATION',
            subjectMetric: 'data_coverage',
            relatedMetric: 'impressions',
            judgement: 'UNKNOWN',
            assertionStatus: 'LIMITATION',
          }),
        ],
      }),
    )
    expect(
      r.report.claimIssues.some((i) => i.rule === 'multiple_assertions_in_source_unit'),
      JSON.stringify(r.report.claimIssues),
    ).toBe(false)
  })

  it('45h. Ô NHÃN khai được bằng trạng thái ĐÚNG NGHĨA, và ASSERTED bị cấm ở đó', () => {
    // Trước khi có tình thái theo cấu trúc, ô "impressions cấp video" chỉ đi qua
    // được với ASSERTED — trạng thái MẠNH NHẤT ở đúng ô vô hại nhất. Cả hai lần
    // thăm dò hinh_su đều gãy ở đây, theo hai kiểu ngược nhau.
    const withRequest = (assertionStatus: string) =>
      base({
        dataRequests: [
          {
            metricOrArtifact: 'impressions cấp video',
            reason: 'Cần để tách khâu tiếp cận khỏi khâu giữ chân.',
            decisionUnlocked: 'Biết nên ưu tiên sửa gì trước.',
          },
        ],
        metricClaims: [
          CLAIM,
          at({ section: 'DATA_REQUEST', itemId: '', field: 'metricOrArtifact@0' }, {
            id: 'MC-002',
            claimType: 'DIAGNOSTIC_PLAN',
            subjectMetric: 'impressions',
            relatedMetric: 'NONE',
            judgement: 'UNKNOWN',
            assertionStatus,
          }),
        ],
      })

    const ok = run(withRequest('CONDITIONAL'))
    expect(rules(ok), JSON.stringify(ok.report.claimIssues)).toEqual([])
    expect(ok.report.passed).toBe(true)

    // SIẾT chứ không nới: ASSERTED nay bị chặn ở chính ô mà trước đây nó là lối
    // đi duy nhất.
    const bad = run(withRequest('ASSERTED'))
    expect(rules(bad)).toContain('assertion_status_wrong_for_field')
    expect(bad.report.passed).toBe(false)
  })

  it('45i. tình thái theo cấu trúc KHÔNG lan sang ô văn xuôi thường', () => {
    // Miễn trừ chỉ áp cho ba trường nhãn. Ở ô văn xuôi, S2 vẫn đòi dấu hiệu.
    const r = run(
      base({
        keyFindings: [{ ...FINDING, limitations: ['CTR thấp rõ rệt ở nhóm này'] }],
        metricClaims: [
          at({}, {
            claimType: 'DIAGNOSTIC_PLAN',
            subjectMetric: 'impression_ctr',
            relatedMetric: 'NONE',
            judgement: 'UNKNOWN',
            assertionStatus: 'CONDITIONAL',
          }),
        ],
      }),
    )
    expect(rules(r)).toContain('modality_not_supported_by_text')
  })

  it('45. "tỷ lệ click" được nhận là nhắc chỉ số nhạy cảm', () => {
    // Bảng bí danh biết cách gọi này, nhưng bộ dò ô nhạy cảm viết tay thì không
    // — nên một phát biểu về CTR viết bằng tiếng Việt lọt qua U3 trong im lặng.
    const r = run(base({ keyFindings: [{ ...FINDING, limitations: ['tỷ lệ click thấp ở nhóm này'] }], metricClaims: [] }))
    expect(
      r.report.claimIssues.some(
        (i) => i.rule === 'undeclared_sensitive_unit' && i.path === 'KEY_FINDING(F-001).limitations[0]',
      ),
    ).toBe(true)
  })
})
