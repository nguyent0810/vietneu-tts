/**
 * VÒNG RÀ SOÁT C — hai reviewer độc lập trên đúng cây sẽ đóng băng.
 *
 * Mỗi test ở đây khoá MỘT phát hiện đã được chứng minh bằng CHẠY trước khi sửa:
 * chạy bản cũ thì test ĐỎ, không phải "xanh vì cách viết". Cặp đối chứng là bắt
 * buộc — mọi phát hiện đều có dạng "cùng một payload, đổi một chi tiết vô can,
 * lớp thất bại đổi hẳn", nên chỉ một phía không chứng minh được gì.
 */
import { afterEach, describe, expect, it } from 'vitest'

import type { AnalysisPackage } from '@/lib/analysis/package'
import { buildPrompt } from '@/lib/cursor/prompt'
import { CURSOR_OUTPUT_SCHEMA_VERSION, type CursorOutput } from '@/lib/cursor/schema'
import { selectedProvider } from '@/lib/cursor/run'
import {
  recoverJsonStringLiterals,
  scanSensitiveInDeclarationJson,
  validateCursorOutput,
  validateProseOnly,
} from '@/lib/cursor/validate'
// @ts-expect-error — module JS thuần, dùng chung với `attempt_table.mjs`.
import { ATTEMPT_CAP, samplingCapOk } from '../../attempt_accounting.mjs'

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

function makeOutput(over: Partial<CursorOutput> = {}): CursorOutput {
  return {
    schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
      confidence: 'MEDIUM',
      confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ nhưng impressions chưa đủ dữ liệu.',
      primaryConstraint: 'Thiếu dữ liệu impressions nên chưa đủ cơ sở đánh giá tiếp cận.',
    },
    keyFindings: [{
      id: 'F-001',
      statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
      findingType: 'OBSERVATION',
      confidence: 'HIGH',
      evidenceIds: ['OBS-001'],
      supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
      contradictingEvidenceIds: [],
      limitations: [],
    }],
    hypotheses: [],
    recommendations: [],
    experiments: [],
    manualReviewTargets: [],
    dataRequests: [],
    explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
    metricClaims: [
      {
        id: 'MC-001', claimType: 'METHODOLOGY_LIMITATION', subjectMetric: 'data_coverage',
        relatedMetric: 'impressions', judgement: 'UNKNOWN', assertionStatus: 'LIMITATION',
        evidenceIds: [], requiresMissingnessDisclosure: true,
        sourceRef: { section: 'ANALYSIS_SUMMARY', itemId: '', field: 'primaryConstraint', ordinal: 0 },
      },
      {
        id: 'MC-002', claimType: 'METHODOLOGY_LIMITATION', subjectMetric: 'data_coverage',
        relatedMetric: 'impressions', judgement: 'UNKNOWN', assertionStatus: 'LIMITATION',
        evidenceIds: [], requiresMissingnessDisclosure: true,
        sourceRef: { section: 'ANALYSIS_SUMMARY', itemId: '', field: 'confidenceRationale', ordinal: 0 },
      },
    ],
    selfCheck: {
      usedOnlyProvidedEvidence: true, recomputedMetrics: false, madeCausalClaims: false,
      madeCtrOrImpressionClaims: false, allFindingEvidenceResolved: true,
    },
    ...over,
  } as CursorOutput
}

function run(output: unknown, hadProse = false) {
  const pkg = makePackage()
  const built = buildPrompt({ pkg })
  return validateCursorOutput({
    raw: typeof output === 'string' ? output : JSON.stringify(output),
    pkg,
    allowedEvidenceIds: built.allowedEvidenceIds,
    allowedVideoIds: built.allowedVideoIds,
    allowedCohortKeys: built.allowedCohortKeys,
    hadProseOutsideJson: hadProse,
  })
}

const blockersOf = (r: ReturnType<typeof run>) =>
  [...r.report.structuralIssues, ...r.report.claimIssues]
    .filter((i) => i.severity === 'BLOCKER')
    .map((i) => i.rule)

/* ------------------------------------------------------------------ */

describe('C-1 — JSON hỏng CÚ PHÁP không được biến thành thất bại NỘI DUNG', () => {
  /*
   * Bản cũ quét cả payload thô như MỘT chuỗi, nên `isKnownFieldValue` mất tác
   * dụng và `clausesOf` cắt chính cú pháp JSON. Hệ quả: một dấu phẩy thừa cộng
   * với chữ "impressions" trong một câu NÊU GIỚI HẠN hợp lệ cho ra
   * `UNSUPPORTED_CLAIM` — vĩnh viễn, chết ngay lần thử 1. Vì gần như bài phân
   * tích thật nào cũng nhắc một chỉ số nhạy cảm, lớp `INVALID_JSON` trên thực tế
   * không còn tồn tại.
   */
  const BENIGN = '{"schemaVersion":"3.0","analysisSummary":{"primaryConstraint":"Độ phủ impressions bằng 0% ở gói này"},}'
  const CONTROL = '{"schemaVersion":"3.0","analysisSummary":{"primaryConstraint":"Kênh thiếu dữ liệu ở gói này"},}'

  it('nhắc chỉ số nhạy cảm LÀNH TÍNH vẫn là INVALID_JSON (được thử lại)', () => {
    expect(run(BENIGN).failureClass).toBe('INVALID_JSON')
  })

  it('ĐỐI CHỨNG: cùng lỗi cú pháp, không có chỉ số nhạy cảm', () => {
    expect(run(CONTROL).failureClass).toBe('INVALID_JSON')
  })

  it('KHÔNG nới cho trường THỪA khi JSON HỢP LỆ — vẫn UNSUPPORTED_CLAIM', () => {
    // Đây là phía "chặn" của cặp: nới ở nhánh hỏng cú pháp không được phép làm
    // yếu nhánh parse được, nơi `unrecognized_keys` tách được trường thừa thật.
    const r = run({ ...makeOutput(), extra: 'CTR thấp nên video chết.' })
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('R18 vẫn đúng: trường THỪA + dấu phẩy thừa -> VẪN UNSUPPORTED_CLAIM', () => {
    /*
     * Hai đòi hỏi đối nghịch cùng đúng, và chúng chỉ mâu thuẫn khi MẤT cấu trúc
     * trường. `reparseAfterTrivialRepair` sửa đúng dấu phẩy thừa rồi parse lại,
     * nên `unrecognized_keys` hoạt động trở lại: trường THỪA bị bắt (R18) trong
     * khi ô THẬT của test đầu tiên vẫn được tha (C-1). Không phải chọn một bên.
     */
    expect(run('{"extra":"CTR thấp.",}').failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('phép sửa KHÔNG được đổi lời mô hình: dấu phẩy TRONG chuỗi giữ nguyên', () => {
    // `,(\s*[}\]])` dạng regex trần sẽ sửa cả bên trong chuỗi. Ở đây câu văn
    // chứa đúng chuỗi ký tự ấy và phải sống sót nguyên vẹn qua phép sửa.
    expect(run('{"extra":"CTR thấp, }và video chết.",}').failureClass).toBe('UNSUPPORTED_CLAIM')
  })
})

describe('C-2 — bản KHAI BÁO hỏng cú pháp: khôi phục CHUỖI theo từ vựng', () => {
  /*
   * Ở lượt khai báo, khẳng định nhạy cảm ngoài cấu trúc khai báo VẪN phải chặn.
   * Nhưng bản khai ĐÚNG nào cũng mang `"relatedMetric":"impression_ctr"`, nên
   * quét cả khối thô làm một chuỗi thì một dấu phẩy thừa vứt bỏ nguyên một bài
   * phân tích đã kiểm định xong (100–235 giây).
   */
  it('giá trị TRƯỜNG hợp lệ trong JSON hỏng KHÔNG bị coi là khẳng định', () => {
    const broken = '{"schemaVersion":"1.0","declarations":[{"id":"MC-001","relatedMetric":"impression_ctr"}],}'
    const r = scanSensitiveInDeclarationJson(recoverJsonStringLiterals(broken))
    expect(r.ctrViolations).toBe(0)
  })

  it('ĐỐI CHỨNG: khẳng định nhạy cảm THẬT trong JSON hỏng vẫn bị bắt', () => {
    const broken = '{"schemaVersion":"1.0","extra":"CTR thấp nên video chết.",}'
    const r = scanSensitiveInDeclarationJson(recoverJsonStringLiterals(broken))
    expect(r.ctrViolations).toBeGreaterThan(0)
  })

  it('validateProseOnly lượt KHAI BÁO giữ đúng hai chiều trên', () => {
    const ok = validateProseOnly({
      proseText: '',
      hadProseOutsideJson: false,
      emittedJson: '{"declarations":[{"relatedMetric":"impression_ctr"}],}',
      declarationPass: true,
    })
    expect(ok.failureClass).not.toBe('UNSUPPORTED_CLAIM')

    const bad = validateProseOnly({
      proseText: '',
      hadProseOutsideJson: false,
      emittedJson: '{"extra":"CTR thấp nên video chết.",}',
      declarationPass: true,
    })
    expect(bad.failureClass).toBe('UNSUPPORTED_CLAIM')
  })
})

describe('C-3 — khối ```json không được hạ cấp thất bại NỘI DUNG thành RETRYABLE', () => {
  /*
   * `PROSE_OUTSIDE_JSON` nằm trong RETRYABLE; `EVIDENCE_UNRESOLVED` và lớp
   * HIGH-thuần-chất-lượng thì không. Bản cũ xếp cờ "có văn bản ngoài JSON" TRÊN
   * cả hai, nên một khối bọc — thứ mô hình thêm theo phản xạ — đổi hẳn cách xử
   * lý một thất bại nội dung: từ "dừng ở lần 1" thành "thử lại 3 lần kèm prompt
   * chỉ đúng chỗ cần sửa".
   */
  const badEvidence = () => {
    const base = makeOutput()
    return makeOutput({ keyFindings: [{ ...base.keyFindings[0]!, evidenceIds: ['OBS-999'] }] })
  }

  it('bằng chứng không giải được: KHÔNG bọc -> EVIDENCE_UNRESOLVED', () => {
    expect(run(badEvidence(), false).failureClass).toBe('EVIDENCE_UNRESOLVED')
  })

  it('bằng chứng không giải được: CÓ bọc -> VẪN EVIDENCE_UNRESOLVED', () => {
    expect(run(badEvidence(), true).failureClass).toBe('EVIDENCE_UNRESOLVED')
  })

  it('payload LÀNH MẠNH chỉ bị bọc -> vẫn là PROSE_OUTSIDE_JSON', () => {
    // Phía đối chứng: lớp mang tên nó phải còn nguyên khi nó là lỗi DUY NHẤT,
    // nếu không thì "sửa" chỉ là xoá mất một phép kiểm.
    const r = run(makeOutput(), true)
    expect(r.failureClass).toBe('PROSE_OUTSIDE_JSON')
    expect(blockersOf(r)).toContain('prose_outside_json')
  })
})

describe('C-4 — giả thuyết nhân quả CÓ RÀO ĐÓN phải có bản khai hợp lệ', () => {
  /*
   * Bản quét theo Ô tha câu này nhờ `HEDGE_PATTERN`, nhưng bản quét theo CLAIM
   * thì không, và không tình thái nào khớp câu. Kết quả đo trên cả 10 tổ hợp:
   * mọi tổ hợp đều BLOCKER — chặng hợp nhất từ chối VĨNH VIỄN một bài phân tích
   * đúng hợp đồng, và mô hình không có nước sửa nào.
   */
  const STATEMENT = 'Có thể thumbnail kém dẫn tới lượt xem giảm.'
  const hypothesis = {
    id: 'H-001', statement: STATEMENT, status: 'UNVERIFIED', confidence: 'LOW',
    supportingEvidenceIds: ['OBS-001'], contradictingEvidenceIds: [],
    // Cố ý KHÔNG nhắc chỉ số nhạy cảm: test này nói về câu `statement`.
    missingEvidence: ['Chưa có dữ liệu hiển thị.'],
    validationMethod: 'Cần thu thập dữ liệu hiển thị trước khi kết luận.',
  }
  const withClaim = (claimType: string, assertionStatus: string) => {
    const base = makeOutput()
    return run({
      ...base,
      hypotheses: [hypothesis],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-003', claimType, subjectMetric: 'thumbnail', relatedMetric: 'views',
          judgement: 'UNKNOWN', assertionStatus, evidenceIds: ['OBS-001'],
          requiresMissingnessDisclosure: false,
          sourceRef: { section: 'HYPOTHESIS', itemId: 'H-001', field: 'statement', ordinal: 0 },
        },
      ],
    })
  }

  it('CAUSAL + CONDITIONAL là bản khai HỢP LỆ', () => {
    const rules = blockersOf(withClaim('CAUSAL', 'CONDITIONAL'))
    expect(rules).not.toContain('modality_not_supported_by_text')
    expect(rules).not.toContain('causal_language_in_non_causal_claim')
    expect(rules).not.toContain('asserted_causal_claim')
  })

  it('R5 còn nguyên: CAUSAL + ASSERTED vẫn bị cấm tuyệt đối', () => {
    expect(blockersOf(withClaim('CAUSAL', 'ASSERTED'))).toContain('asserted_causal_claim')
  })

  it('khai SAI NHÃN vẫn bị chặn: không-CAUSAL cho câu nhân quả', () => {
    expect(blockersOf(withClaim('OBSERVATION', 'CONDITIONAL')))
      .toContain('causal_language_in_non_causal_claim')
  })
})

describe('C-5 — MỘT câu nhân quả đếm ĐÚNG MỘT lần', () => {
  it('không cộng hai lần cho cùng một câu trong ô đã khai', () => {
    const base = makeOutput()
    const r = run({
      ...base,
      keyFindings: [{ ...base.keyFindings[0]!, statement: 'Thumbnail kém dẫn tới lượt xem giảm mạnh.' }],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-004', claimType: 'OBSERVATION', subjectMetric: 'thumbnail', relatedMetric: 'views',
          judgement: 'UNKNOWN', assertionStatus: 'LIMITATION', evidenceIds: ['OBS-001'],
          requiresMissingnessDisclosure: false,
          sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'statement', ordinal: 0 },
        },
      ],
    })
    // Con số này được ghi vào `analysis_validation.causal_violations` và trích
    // nguyên văn trong `selfcheck_contradicted`, nên thổi phồng nó làm sai mọi
    // báo cáo ổn định đọc cột ấy.
    expect(r.report.causalViolations).toBe(1)
    expect(blockersOf(r)).toContain('causal_language_in_non_causal_claim')
  })
})

describe('C-14 — câu NÊU THIẾU DỮ LIỆU phải có bản khai hợp lệ', () => {
  /*
   * Trước bản sửa, hai luật đối nghịch nhau và câu bắt buộc nhất của miền này
   * không khai được bằng bất cứ chủ ngữ nào (đo trên lô thật: 113 lần):
   *   subjectMetric=impressions   -> methodology_subject_also_missing
   *   subjectMetric=data_coverage -> subject_metric_not_in_text
   */
  const SENTENCE = 'Không có impressions/CTR nên không tách được mức tiếp cận khỏi mức xem.'

  const withSubject = (subjectMetric: string) => {
    const base = makeOutput()
    return run({
      ...base,
      keyFindings: [{ ...base.keyFindings[0]!, limitations: [SENTENCE] }],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-009', claimType: 'METHODOLOGY_LIMITATION', subjectMetric,
          relatedMetric: 'impressions', judgement: 'UNKNOWN', assertionStatus: 'LIMITATION',
          evidenceIds: [], requiresMissingnessDisclosure: false,
          sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
        },
      ],
    })
  }

  it('data_coverage nay là bản khai HỢP LỆ cho câu thiếu dữ liệu', () => {
    const rules = blockersOf(withSubject('data_coverage'))
    expect(rules).not.toContain('subject_metric_not_in_text')
    expect(rules).not.toContain('methodology_subject_also_missing')
  })

  it('ĐỐI CHỨNG: R0b vẫn CHẶN chủ ngữ sai cho chỉ số THẬT', () => {
    // Ca gốc mà R0b sinh ra để chặn: câu nói về một chỉ số, khai chủ ngữ là chỉ
    // số KHÁC. Nới cho `data_coverage` không được phép làm yếu đường này.
    const base = makeOutput()
    const r = run({
      ...base,
      keyFindings: [{ ...base.keyFindings[0]!, limitations: ['Thumbnail hiện tại kém so với nhóm dẫn đầu.'] }],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-010', claimType: 'OBSERVATION', subjectMetric: 'retention',
          relatedMetric: 'thumbnail', judgement: 'LOW', assertionStatus: 'ASSERTED',
          evidenceIds: ['OBS-001'], requiresMissingnessDisclosure: false,
          sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
        },
      ],
    })
    expect(blockersOf(r)).toContain('subject_metric_not_in_text')
  })
})

describe('C-15 — LIMITATION nhận ra tiếng Việt, nhưng KHÔNG cõng phán xét', () => {
  /*
   * Đo trên 383 câu thật của 4 lô: bảng cũ chỉ biết "0%", bỏ sót 105 câu
   * "không … được", 104 câu "thiếu", 68 câu "không có". Nới là bắt buộc; chốt
   * R1b đi kèm để việc nới không thành đường lách.
   */
  const declare = (limitation: string, over: Record<string, unknown> = {}) => {
    const base = makeOutput()
    return run({
      ...base,
      keyFindings: [{ ...base.keyFindings[0]!, limitations: [limitation] }],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-011', claimType: 'METHODOLOGY_LIMITATION', subjectMetric: 'data_coverage',
          relatedMetric: 'impression_ctr', judgement: 'UNKNOWN', assertionStatus: 'LIMITATION',
          evidenceIds: [], requiresMissingnessDisclosure: false,
          sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
          ...over,
        },
      ],
    })
  }

  it('bốn cách nói BẤT KHẢ của tiếng Việt nay đều khai được', () => {
    for (const s of [
      'Không có impressions/CTR nên không đánh giá được khâu tiếp cận.',
      'Thiếu impressions và CTR nên chưa đọc được khâu tiếp cận.',
      'Không có dữ liệu CTR trong cửa sổ này.',
      'Chưa thu thập được CTR nên chưa kết luận về tiếp cận.',
    ]) {
      expect(blockersOf(declare(s)), `câu: ${s}`).not.toContain('modality_not_supported_by_text')
    }
  })

  it('CHỐT: cùng câu ấy mà mang PHÁN XÉT về chỉ số phủ 0% -> bị chặn', () => {
    // "CTR thấp nên không tăng được view" khớp LIMITATION sau khi nới. Nếu bản
    // khai kèm judgement=LOW về một chỉ số phủ 0% thì đó là khẳng định trá hình.
    const r = declare('CTR thấp nên không tăng được view.', { judgement: 'LOW' })
    expect(blockersOf(r)).toContain('limitation_carries_judgement_on_missing_metric')
  })

  it('ĐỐI CHỨNG: judgement=UNKNOWN trên cùng câu -> KHÔNG bị chốt chặn', () => {
    // Chốt phải nhắm vào PHÁN XÉT, không nhắm vào việc nhắc tên chỉ số.
    expect(blockersOf(declare('Không có impressions/CTR nên không đánh giá được khâu tiếp cận.')))
      .not.toContain('limitation_carries_judgement_on_missing_metric')
  })
})

describe('C-16 — câu TỪ CHỐI KẾT LUẬN nhắc nhiều chỉ số phải khai được', () => {
  /*
   * Lô 6: 14/17 lần chặn là câu nhắc 3–4 chỉ số nhạy cảm, trong khi một claim
   * chỉ có HAI ô chỉ số. Câu bị chặn lại đúng là câu hệ thống muốn có nhất.
   */
  const FOUR = 'Không kết luận hiệu quả thumbnail, tiêu đề hút click, hay packaging vì impressions/CTR độ phủ 0%.'

  const declare = (over: Record<string, unknown> = {}) => {
    const base = makeOutput()
    return run({
      ...base,
      keyFindings: [{ ...base.keyFindings[0]!, limitations: [FOUR] }],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-012', claimType: 'METHODOLOGY_LIMITATION', subjectMetric: 'data_coverage',
          relatedMetric: 'impression_ctr', judgement: 'UNKNOWN', assertionStatus: 'LIMITATION',
          evidenceIds: [], requiresMissingnessDisclosure: false,
          sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
          ...over,
        },
      ],
    })
  }

  it('claim KHÔNG phán xét: nhắc 4 chỉ số vẫn khai được', () => {
    expect(blockersOf(declare())).not.toContain('undeclared_metric_in_claim_text')
  })

  it('ĐỐI CHỨNG: cùng câu mà claim MANG phán xét -> vẫn bị chặn', () => {
    // Miễn trừ chỉ dành cho claim không khẳng định gì. Có phán xét là quy tắc
    // hoạt động lại đầy đủ — nếu không thì đây thành đường giấu kết luận.
    expect(blockersOf(declare({ subjectMetric: 'views', judgement: 'LOW', assertionStatus: 'ASSERTED' })))
      .toContain('undeclared_metric_in_claim_text')
  })
})

describe('C-18 — CODEX R21: judgement=UNKNOWN không được CHE phán xét có thật trong câu', () => {
  /*
   * Ca phá của Codex vòng 21, và nó khai thác đúng chỗ giao của ba miễn trừ:
   *
   *   văn xuôi : "Thumbnail kém dù thiếu impressions/CTR."
   *   bản khai : subjectMetric=data_coverage, relatedMetric=impression_ctr,
   *              judgement=UNKNOWN, assertionStatus=LIMITATION
   *
   * "thiếu" làm câu khớp LIMITATION (nới ở C-15); `data_coverage` được miễn R0b
   * (C-14); claim tự khai UNKNOWN nên được miễn `undeclared_metric_in_claim_text`
   * (C-16) và làm chốt R1b im lặng.
   *
   * Mấu chốt: `judgemental` được suy ra TỪ TRƯỜNG KHAI BÁO, không từ văn xuôi.
   * Nên người khai chỉ cần nói "tôi không phán xét gì" là mọi chốt dựa trên
   * phán xét đều tắt — trong khi câu văn vẫn khẳng định `thumbnail` là "kém",
   * và `thumbnail` nằm trong `zeroCoverage`.
   *
   * Đây là hệ quả GHÉP của ba miễn trừ, không cái nào một mình gây ra.
   */
  const SENTENCE = 'Thumbnail kém dù thiếu impressions/CTR.'

  it('câu KHẲNG ĐỊNH về chỉ số phủ 0% phải bị chặn dù khai UNKNOWN', () => {
    const base = makeOutput()
    const r = run({
      ...base,
      keyFindings: [{ ...base.keyFindings[0]!, limitations: [SENTENCE] }],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-012', claimType: 'METHODOLOGY_LIMITATION', subjectMetric: 'data_coverage',
          relatedMetric: 'impression_ctr', judgement: 'UNKNOWN', assertionStatus: 'LIMITATION',
          evidenceIds: [], requiresMissingnessDisclosure: false,
          sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
        },
      ],
    })
    expect(blockersOf(r), 'khẳng định "thumbnail kém" đi lọt qua chặng hợp nhất').not.toEqual([])
  })

  it('ĐỐI CHỨNG: câu KHÔNG phán xét vẫn khai được bình thường', () => {
    // Bản sửa không được biến mọi câu nêu giới hạn thành lỗi — đó là chính cái
    // nghịch lý mà C-14..C-16 vừa gỡ.
    const base = makeOutput()
    const r = run({
      ...base,
      keyFindings: [{ ...base.keyFindings[0]!, limitations: ['Thiếu impressions/CTR nên không đánh giá được khâu tiếp cận.'] }],
      metricClaims: [
        ...base.metricClaims,
        {
          id: 'MC-013', claimType: 'METHODOLOGY_LIMITATION', subjectMetric: 'data_coverage',
          relatedMetric: 'impression_ctr', judgement: 'UNKNOWN', assertionStatus: 'LIMITATION',
          evidenceIds: [], requiresMissingnessDisclosure: false,
          sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
        },
      ],
    })
    expect(blockersOf(r)).toEqual([])
  })
})

describe('C-17 — bộ chọn NHÀ CUNG CẤP phải mặc định an toàn', () => {
  /*
   * Mặc định sai ở đây không làm test nào đỏ và không in cảnh báo nào — nó chỉ
   * lặng lẽ đổi NGƯỜI PHÂN TÍCH của lô kế tiếp, và ta chỉ phát hiện khi đọc
   * `provider` trong bản kê hàng tháng sau. Vì vậy nó phải có test riêng.
   */
  const KEY = 'CURSOR_PROVIDER'
  const saved = process.env[KEY]
  afterEach(() => {
    if (saved === undefined) delete process.env[KEY]
    else process.env[KEY] = saved
  })

  it('KHÔNG đặt biến -> CURSOR_CLI (mọi lô đã chạy đều bằng nó)', () => {
    delete process.env[KEY]
    expect(selectedProvider()).toBe('CURSOR_CLI')
  })

  it('đặt đúng ANTHROPIC_API -> đổi nhà cung cấp', () => {
    process.env[KEY] = 'ANTHROPIC_API'
    expect(selectedProvider()).toBe('ANTHROPIC_API')
  })

  it('giá trị LẠ -> vẫn CURSOR_CLI, không im lặng đổi', () => {
    // Gõ sai tên nhà cung cấp không được biến thành "chọn cái gì đó khác".
    process.env[KEY] = 'anthropic'
    expect(selectedProvider()).toBe('CURSOR_CLI')
  })
})

describe('C-6 — TRẦN lấy mẫu phải làm cổng ĐỎ, không chỉ in cảnh báo', () => {
  /*
   * `attempt_table.mjs` in đúng chữ "lô này không hợp lệ" rồi `process.exit(0)`:
   * dòng duy nhất trong vòng lặp KHÔNG kèm `gateOk = false`. Trần này là thứ DUY
   * NHẤT chặn việc chạy lại lượt phân tích tới khi các con số đẹp lên — trần 3
   * lần của 0031 là trần lượt KHAI BÁO cho MỘT lượt phân tích.
   */
  it('đúng trần thì đạt, quá trần thì trượt', () => {
    expect(samplingCapOk(ATTEMPT_CAP)).toBe(true)
    expect(samplingCapOk(ATTEMPT_CAP + 1)).toBe(false)
  })
})
