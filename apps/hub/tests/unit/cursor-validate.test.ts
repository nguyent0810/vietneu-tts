import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

import type { AnalysisPackage } from '@/lib/analysis/package'
import { extractJson } from '@/lib/cursor/exec'
import {
  buildPrompt,
  buildRepairPrompt,
  evidenceIdsFor,
  PROMPT_VERSION,
  schemaConstraintLines,
} from '@/lib/cursor/prompt'
import {
  CURSOR_OUTPUT_SCHEMA_VERSION,
  cursorOutputSchema,
  type CursorOutput,
} from '@/lib/cursor/schema'
import { validateCursorOutput } from '@/lib/cursor/validate'
import { detectSemanticDrift } from '@/lib/cursor/run'

/** Gói bằng chứng tối thiểu nhưng thực tế, dùng chung cho cả tệp. */
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
      // Cả ba kênh thật đều 0% — đây là ca chính cần kiểm.
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

function makeOutput(over: Partial<CursorOutput> = {}): CursorOutput {
  return {
    schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
      confidence: 'MEDIUM',
      confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ nhưng impressions chưa đủ dữ liệu.',
      primaryConstraint: 'Thiếu dữ liệu impressions nên chưa đủ cơ sở đánh giá tiếp cận.',
    },
    keyFindings: [
      {
        id: 'F-001',
        statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
        findingType: 'OBSERVATION',
        confidence: 'HIGH',
        evidenceIds: ['OBS-001'],
        supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
        contradictingEvidenceIds: [],
        limitations: [],
      },
    ],
    hypotheses: [],
    recommendations: [],
    experiments: [],
    manualReviewTargets: [],
    dataRequests: [],
    explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
    // Gói mẫu có impressions độ phủ 0, và hai trường tóm tắt đều nhắc tới nó.
    // Từ schema 2.0, mỗi câu như vậy phải có khai báo tương ứng.
    metricClaims: [
      {
        id: 'MC-001',
        claimType: 'METHODOLOGY_LIMITATION',
        subjectMetric: 'data_coverage',
        relatedMetric: 'impressions',
        judgement: 'UNKNOWN',
        assertionStatus: 'LIMITATION',
        evidenceIds: [],
        requiresMissingnessDisclosure: true,
        sourceRef: { section: 'ANALYSIS_SUMMARY', itemId: '', field: 'primaryConstraint', ordinal: 0 },
      },
      {
        id: 'MC-002',
        claimType: 'METHODOLOGY_LIMITATION',
        subjectMetric: 'data_coverage',
        relatedMetric: 'impressions',
        judgement: 'UNKNOWN',
        assertionStatus: 'LIMITATION',
        evidenceIds: [],
        requiresMissingnessDisclosure: true,
        sourceRef: { section: 'ANALYSIS_SUMMARY', itemId: '', field: 'confidenceRationale', ordinal: 0 },
      },
    ],
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

function run(output: unknown, pkg = makePackage(), hadProse = false) {
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

describe('dựng prompt', () => {
  it('tất định: cùng gói cho cùng băm', () => {
    const a = buildPrompt({ pkg: makePackage() })
    const b = buildPrompt({ pkg: makePackage() })
    expect(a.hash).toBe(b.hash)
    expect(a.text).toBe(b.text)
  })

  it('đổi gói thì đổi băm', () => {
    const a = buildPrompt({ pkg: makePackage() })
    const b = buildPrompt({ pkg: makePackage({ channelSummary: { videos: 21 } }) })
    expect(a.hash).not.toBe(b.hash)
  })

  it('có đủ 13 phần bắt buộc', () => {
    const { text } = buildPrompt({ pkg: makePackage() })
    for (const s of [
      'ROLE',
      'OBJECTIVE',
      'HARD CONSTRAINTS',
      'ANALYSIS SCOPE',
      'DATA COVERAGE',
      'BASELINE DEFINITIONS',
      'DETERMINISTIC OBSERVATIONS',
      'RANKED VIDEOS AND COHORTS',
      'ANOMALIES',
      'HYPOTHESIS CANDIDATES',
      'MISSING DATA',
      'REQUIRED OUTPUT SCHEMA',
      'QUALITY CHECKLIST',
    ]) {
      expect(text, `thiếu phần ${s}`).toContain(`## ${s}`)
    }
  })

  it('ràng buộc CTR xuất hiện khi độ phủ bằng 0', () => {
    const { text } = buildPrompt({ pkg: makePackage() })
    expect(text).toContain('độ phủ 0%')
    expect(text).toContain('KHÔNG được kết luận gì về hiệu quả thumbnail')
  })

  it('kèm phiên bản, băm input và cửa sổ phân tích', () => {
    const { text } = buildPrompt({ pkg: makePackage() })
    expect(text).toContain(PROMPT_VERSION)
    expect(text).toContain('a'.repeat(64))
    expect(text).toContain('2026-06-01')
  })

  it('KHÔNG chứa credential hay chuỗi kết nối', () => {
    const { text } = buildPrompt({ pkg: makePackage() })
    const lower = text.toLowerCase()
    for (const bad of ['postgres://', 'postgresql://', 'vhw_', 'vhu_', 'bearer ', 'client_secret', 'refresh_token', 'api_key']) {
      expect(lower, `prompt chứa ${bad}`).not.toContain(bad)
    }
  })

  it('evidence id ổn định và bao phủ mọi loại bằng chứng', () => {
    const { ids } = evidenceIdsFor(makePackage())
    expect(ids).toContain('OBS-001')
    expect(ids).toContain('ANOM-001')
    expect(ids).toContain('VIDEO-aaaaaaaaaaa')
    expect(ids).toContain('COHORT-001')
    expect(new Set(ids).size).toBe(ids.length)
  })

  it('prompt sửa lỗi chỉ chứa lỗi + hợp đồng + output sai, KHÔNG gửi lại bằng chứng', () => {
    const r = buildRepairPrompt({ errors: ['lỗi A'], invalidOutput: '{"x":1}' })
    expect(r.text).toContain('lỗi A')
    expect(r.text).toContain('{"x":1}')
    expect(r.text).not.toContain('DETERMINISTIC OBSERVATIONS')
    expect(r.text).not.toContain('OBS-001')
  })

  it('prompt sửa lỗi CHỨA TRỌN output cỡ thật, không cắt', () => {
    // Output thật quan sát được 26-30 KB. Cắt còn 8k như bản đầu buộc mô hình
    // viết lại phần nó không nhìn thấy, mà không có bằng chứng trong tay.
    const r = buildRepairPrompt({ errors: ['e'], invalidOutput: 'x'.repeat(30_000) })
    expect(r.truncated).toBe(false)
    expect(r.text).not.toContain('đã cắt bớt')
  })

  it('output vượt trần thì ĐÁNH DẤU đã cắt, để bên gọi từ chối thử lại', () => {
    const r = buildRepairPrompt({ errors: ['e'], invalidOutput: 'x'.repeat(200_000) })
    expect(r.truncated).toBe(true)
    expect(r.text).toContain('đã cắt bớt')
  })
})

describe('bóc JSON khỏi stdout', () => {
  it('JSON trần', () => {
    const r = extractJson('{"a":1}')
    expect(r.json).toBe('{"a":1}')
    expect(r.hadProseOutsideJson).toBe(false)
  })

  it('JSON trong khối ``` bị đánh dấu là có văn bản thừa', () => {
    const r = extractJson('```json\n{"a":1}\n```')
    expect(r.json).toBe('{"a":1}')
    expect(r.hadProseOutsideJson).toBe(true)
  })

  it('có lời dẫn trước JSON', () => {
    const r = extractJson('Đây là kết quả:\n{"a":1}\nHy vọng hữu ích.')
    expect(JSON.parse(r.json!)).toEqual({ a: 1 })
    expect(r.hadProseOutsideJson).toBe(true)
  })

  it('không nhầm ngoặc nằm trong chuỗi', () => {
    const r = extractJson('x {"a":"}{","b":2} y')
    expect(JSON.parse(r.json!)).toEqual({ a: '}{', b: 2 })
  })

  it('không có JSON', () => {
    expect(extractJson('không có gì cả').json).toBeNull()
    expect(extractJson('').json).toBeNull()
  })
})

describe('kiểm định cấu trúc', () => {
  it('JSON hỏng -> INVALID_JSON', () => {
    const r = run('{ hỏng')
    expect(r.failureClass).toBe('INVALID_JSON')
    expect(r.output).toBeNull()
  })

  it('schemaVersion lạ bị từ chối', () => {
    const r = run(makeOutput({ schemaVersion: '9.9' as never }))
    expect(r.failureClass).toBe('UNSUPPORTED_SCHEMA_VERSION')
  })

  it('trường lạ ở cấp cao nhất bị từ chối (.strict)', () => {
    const r = run({ ...makeOutput(), somethingExtra: true })
    expect(r.report.passed).toBe(false)
    expect(r.failureClass).toBe('SCHEMA_MISMATCH')
  })

  it('thiếu trường bắt buộc -> MISSING_REQUIRED_FIELD', () => {
    const o = makeOutput() as Record<string, unknown>
    delete o.selfCheck
    expect(run(o).failureClass).toBe('MISSING_REQUIRED_FIELD')
  })

  it('id trùng bị chặn', () => {
    const r = run(
      makeOutput({
        keyFindings: [makeOutput().keyFindings[0]!, { ...makeOutput().keyFindings[0]!, id: 'F-001' }],
      }),
    )
    expect(r.report.structuralIssues.some((i) => i.rule === 'duplicate_ids')).toBe(true)
  })

  it('experiment trỏ hypothesis không tồn tại bị chặn', () => {
    const r = run(
      makeOutput({
        experiments: [
          {
            id: 'E-001',
            hypothesisId: 'H-999',
            change: 'Thử thay đổi cách mở đầu video',
            baseline: 'cohort hiện tại',
            successMetrics: ['views_d7'],
            minimumWindowDays: 14,
            sampleLimitations: [],
            stopConditions: ['dừng nếu không đủ mẫu'],
            interpretationRisks: ['nhiễu theo mùa'],
          },
        ],
      }),
    )
    expect(r.report.structuralIssues.some((i) => i.rule === 'dangling_hypothesis_ref')).toBe(true)
  })

  it('mảng vượt trần bị Zod chặn', () => {
    const one = makeOutput().keyFindings[0]!
    const many = Array.from({ length: 12 }, (_, i) => ({
      ...one,
      id: `F-${String(i + 1).padStart(3, '0')}`,
    }))
    expect(run(makeOutput({ keyFindings: many })).report.passed).toBe(false)
  })

  it('văn bản ngoài JSON CHẶN, và là lỗi kỹ thuật nên được thử lại', () => {
    // Trước đây chỉ là MEDIUM nên không ảnh hưởng `passed`. Hợp đồng nói rõ
    // "chỉ một object JSON", và phần ngoài JSON không hề được kiểm khẳng định.
    const r = run(makeOutput(), makePackage(), true)
    expect(r.report.structuralIssues.some((i) => i.rule === 'prose_outside_json')).toBe(true)
    expect(r.report.passed).toBe(false)
    expect(r.failureClass).toBe('PROSE_OUTSIDE_JSON')
  })
})

describe('kiểm định bằng chứng', () => {
  it('evidence id không có trong gói bị chặn', () => {
    const r = run(
      makeOutput({
        keyFindings: [{ ...makeOutput().keyFindings[0]!, evidenceIds: ['OBS-999'] }],
      }),
    )
    expect(r.failureClass).toBe('EVIDENCE_UNRESOLVED')
    expect(r.report.unresolvedEvidenceRefs).toBe(1)
    expect(r.report.evidenceResolutionRate).toBe(0)
  })

  it('video của kênh khác bị chặn', () => {
    const r = run(
      makeOutput({
        manualReviewTargets: [
          {
            targetType: 'VIDEO',
            targetId: 'zzzzzzzzzzz',
            reason: 'cần xem lại',
            evidenceIds: [],
            reviewQuestions: ['nội dung có gì khác?'],
          },
        ],
      }),
    )
    expect(r.report.evidenceIssues.some((i) => i.rule === 'cross_channel_video')).toBe(true)
  })

  it('cohort có thật được chấp nhận', () => {
    const r = run(
      makeOutput({
        manualReviewTargets: [
          {
            targetType: 'COHORT',
            targetId: '2026-07-14..2026-07-27 (SHORT)',
            reason: 'cohort này giảm',
            evidenceIds: ['COHORT-001'],
            reviewQuestions: ['chủ đề có đổi không?'],
          },
        ],
      }),
    )
    expect(r.report.passed).toBe(true)
  })

  it('khuyến nghị được trích dẫn CHÍNH phát hiện của nó (F-00x)', () => {
    // Cách viết tự nhiên của một nhà phân tích: "khuyến nghị này dựa trên phát
    // hiện F-001". Chặn nó là chặn nhầm.
    const r = run(
      makeOutput({
        recommendations: [
          {
            id: 'R-001',
            action: 'Nhân rộng định dạng của video dẫn đầu sang các chủ đề lân cận',
            priority: 'P1',
            category: 'TEST',
            rationale: 'Dựa trên phát hiện F-001.',
            evidenceIds: ['F-001'],
            expectedValue: 'MEDIUM',
            effort: 'MEDIUM',
            reversibility: 'HIGH',
            measurementFeasibility: 'HIGH',
            risks: [],
            successMetric: 'views_d7 của nhóm thử',
          },
        ],
      }),
    )
    expect(r.report.unresolvedEvidenceRefs).toBe(0)
    expect(r.report.passed).toBe(true)
  })

  it('id nội bộ KHÔNG tồn tại vẫn bị chặn', () => {
    const r = run(
      makeOutput({
        recommendations: [
          {
            id: 'R-001',
            action: 'Một hành động nào đó cần kiểm chứng thêm',
            priority: 'P2',
            category: 'INVESTIGATE',
            rationale: 'Dựa trên F-099 không tồn tại.',
            evidenceIds: ['F-099'],
            expectedValue: 'LOW',
            effort: 'LOW',
            reversibility: 'HIGH',
            measurementFeasibility: 'LOW',
            risks: [],
            successMetric: 'n/a',
          },
        ],
      }),
    )
    expect(r.report.unresolvedEvidenceRefs).toBe(1)
  })

  it('video được NHẮC TỚI trong câu quan sát vẫn là mục tiêu hợp lệ', () => {
    // rankedVideos bị cắt ở top-20 nhưng câu quan sát vẫn nêu video ngoài top;
    // chúng vẫn thuộc kênh này nên phải được phép rà soát.
    const pkg = makePackage({
      observations: [
        {
          kind: 'BOTTOM_PERFORMER',
          polarity: 'NEGATIVE',
          statement: 'Video kqE6KQJloug chỉ đạt phân vị 2 về lượt xem 7 ngày.',
          metricValues: {},
          baselineKind: 'CHANNEL_FORMAT',
          confidence: 0.7,
          limitations: [],
          evidenceRefs: [{ refType: 'VIDEO' }],
          isHypothesis: false,
        },
      ],
    } as never)
    const built = buildPrompt({ pkg })
    expect(built.allowedVideoIds).toContain('kqE6KQJloug')
  })

  it('tỉ lệ giải bằng chứng tính đúng', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, evidenceIds: ['OBS-001', 'OBS-999'] },
        ],
      }),
    )
    expect(r.report.totalEvidenceRefs).toBe(2)
    expect(r.report.unresolvedEvidenceRefs).toBe(1)
    expect(r.report.evidenceResolutionRate).toBe(0.5)
  })
})

describe('an toàn về khẳng định', () => {
  it('câu nhân quả trong PHÁT HIỆN bị chặn', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          {
            ...makeOutput().keyFindings[0]!,
            supportingReasoning: 'Việc đăng dày làm giảm lượt xem trung vị của kênh.',
          },
        ],
      }),
    )
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
    expect(r.report.causalViolations).toBeGreaterThan(0)
  })

  it('câu về PHƯƠNG PHÁP (độ tin cậy) KHÔNG bị coi là nhân quả', () => {
    // Ví dụ thật từ output Cursor, từng bị báo động giả:
    //   "dateCompleteness thấp làm giảm tin cậy xu hướng kênh"
    // Đây là lập luận về phương pháp — đúng thứ ta muốn mô hình nói ra.
    const r = run(
      makeOutput({
        keyFindings: [
          {
            ...makeOutput().keyFindings[0]!,
            supportingReasoning:
              'dateCompleteness thấp làm giảm tin cậy của xu hướng kênh trong cửa sổ này.',
          },
        ],
      }),
    )
    expect(r.report.causalViolations).toBe(0)
  })

  it('vẫn chặn "làm giảm <hiệu suất>"', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, supportingReasoning: 'Đăng dày làm giảm lượt xem trung vị.' },
        ],
      }),
    )
    expect(r.report.causalViolations).toBeGreaterThan(0)
  })

  it('báo cáo kèm ĐOẠN VĂN vi phạm, không chỉ tên quy tắc', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, supportingReasoning: 'Tiêu đề ngắn làm giảm lượt xem.' },
        ],
      }),
    )
    const issue = r.report.claimIssues.find((i) => i.rule === 'causal_claim')
    expect(issue?.excerpt, 'thiếu excerpt thì phải chạy lại LLM mới biết sai ở câu nào').toBeTruthy()
    expect(issue!.excerpt).toContain('làm giảm')
  })

  it('GIẢ THUYẾT có rào đón được phép nêu cơ chế', () => {
    // Giả thuyết theo định nghĩa là đề xuất một cơ chế; cấm tuyệt đối thì
    // không thể phát biểu giả thuyết nào.
    const r = run(
      makeOutput({
        hypotheses: [
          {
            id: 'H-001',
            statement: 'Có thể thời lượng ngắn làm giảm khả năng giữ chân — đây là giả thuyết chưa kiểm chứng.',
            status: 'UNVERIFIED',
            confidence: 'LOW',
            supportingEvidenceIds: ['OBS-001'],
            contradictingEvidenceIds: [],
            missingEvidence: ['dữ liệu retention theo giây'],
            validationMethod: 'So sánh nhóm video cùng chủ đề khác thời lượng.',
          },
        ],
      }),
    )
    expect(r.report.causalViolations).toBe(0)
    expect(r.report.passed).toBe(true)
  })

  it('GIẢ THUYẾT KHÔNG rào đón vẫn bị chặn', () => {
    const r = run(
      makeOutput({
        hypotheses: [
          {
            id: 'H-001',
            statement: 'Thời lượng ngắn làm giảm khả năng giữ chân.',
            status: 'UNVERIFIED',
            confidence: 'LOW',
            supportingEvidenceIds: ['OBS-001'],
            contradictingEvidenceIds: [],
            missingEvidence: ['x'],
            validationMethod: 'So sánh hai nhóm.',
          },
        ],
      }),
    )
    expect(r.report.causalViolations).toBeGreaterThan(0)
  })

  it('kết luận CTR khi độ phủ 0 bị chặn', () => {
    const r = run(
      makeOutput({
        analysisSummary: {
          ...makeOutput().analysisSummary,
          overallAssessment: 'CTR của kênh này rất thấp và cần cải thiện thumbnail ngay lập tức.',
        },
      }),
    )
    expect(r.report.ctrViolations).toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('bắt cả khi phán xét ĐỨNG TRƯỚC chỉ số', () => {
    const r = run(
      makeOutput({
        analysisSummary: {
          ...makeOutput().analysisSummary,
          overallAssessment: 'The high number of impressions suggests the channel reaches many people.',
        },
      }),
    )
    expect(r.report.ctrViolations).toBeGreaterThan(0)
  })

  it('NÓI VỀ việc thiếu CTR là hợp lệ KHI ĐƯỢC KHAI BÁO', () => {
    const text = 'Không thể đánh giá tiếp cận vì impressions và CTR có độ phủ 0% dữ liệu.'
    const base = makeOutput()
    const r = run(
      makeOutput({
        analysisSummary: { ...base.analysisSummary, overallAssessment: text },
        metricClaims: [
          ...base.metricClaims,
          {
            id: 'MC-050',
            claimType: 'METHODOLOGY_LIMITATION',
            subjectMetric: 'data_coverage',
            relatedMetric: 'impression_ctr',
            judgement: 'UNKNOWN',
            assertionStatus: 'LIMITATION',
            evidenceIds: [],
            requiresMissingnessDisclosure: true,
            sourceRef: { section: 'ANALYSIS_SUMMARY', itemId: '', field: 'overallAssessment', ordinal: 0 },
          },
        ],
      }),
    )
    expect(r.report.ctrViolations, JSON.stringify(r.report.claimIssues)).toBe(0)
  })


  it('chỉ số bịa (rpm/revenue) bị ghi nhận', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, supportingReasoning: 'RPM của kênh đang ở mức 2.5 USD.' },
        ],
      }),
    )
    expect(r.report.unsupportedMetricViolations).toBeGreaterThan(0)
  })
})

describe('kiểm định chất lượng', () => {
  it('phát hiện dạng dữ kiện mà không có bằng chứng bị gắn cờ', () => {
    const r = run(
      makeOutput({
        keyFindings: [{ ...makeOutput().keyFindings[0]!, evidenceIds: [] }],
      }),
    )
    expect(r.report.qualityIssues.some((i) => i.rule === 'finding_without_evidence')).toBe(true)
  })

  it('LIMITATION được phép không có bằng chứng', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          {
            ...makeOutput().keyFindings[0]!,
            findingType: 'LIMITATION',
            evidenceIds: [],
            statement: 'Không có impressions nên không đánh giá được khâu tiếp cận.',
          },
        ],
      }),
    )
    expect(r.report.qualityIssues.some((i) => i.rule === 'finding_without_evidence')).toBe(false)
  })

  it('P0 không bằng chứng bị gắn cờ', () => {
    const r = run(
      makeOutput({
        recommendations: [
          {
            id: 'R-001',
            action: 'Dừng toàn bộ việc sản xuất Shorts ngay lập tức',
            priority: 'P0',
            category: 'STOP',
            rationale: 'Cần hành động nhanh.',
            evidenceIds: [],
            expectedValue: 'HIGH',
            effort: 'LOW',
            reversibility: 'HIGH',
            measurementFeasibility: 'HIGH',
            risks: [],
            successMetric: 'views_d7',
          },
        ],
      }),
    )
    expect(r.report.qualityIssues.some((i) => i.rule === 'p0_without_evidence')).toBe(true)
  })

  it('selfCheck mâu thuẫn với kiểm định độc lập bị ghi nhận', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, supportingReasoning: 'Điều này làm giảm lượt xem.' },
        ],
        selfCheck: { ...makeOutput().selfCheck, madeCausalClaims: false },
      }),
    )
    expect(r.report.qualityIssues.some((i) => i.rule === 'selfcheck_contradicted')).toBe(true)
  })

  it('tin cậy CAO trong khi dữ liệu tin cậy THẤP bị gắn cờ', () => {
    const pkg = makePackage({ confidence: { score: 0.3, band: 'LOW', drivers: {} } })
    const built = buildPrompt({ pkg })
    const r = validateCursorOutput({
      raw: JSON.stringify(
        makeOutput({ analysisSummary: { ...makeOutput().analysisSummary, confidence: 'HIGH' } }),
      ),
      pkg,
      allowedEvidenceIds: built.allowedEvidenceIds,
      allowedVideoIds: built.allowedVideoIds,
      allowedCohortKeys: built.allowedCohortKeys,
      hadProseOutsideJson: false,
    })
    expect(r.report.qualityIssues.some((i) => i.rule === 'confidence_exceeds_coverage')).toBe(true)
  })

  it('output hợp lệ thì ĐẠT', () => {
    const r = run(makeOutput())
    expect(r.report.passed).toBe(true)
    expect(r.failureClass).toBe('NONE')
    expect(r.report.evidenceResolutionRate).toBe(1)
  })
})

/**
 * Các lỗ hổng do Codex phát hiện ở vòng rà soát Phase 4.
 *
 * Mỗi ca dưới đây từng ĐẠT trước khi sửa. Giữ chúng lại vì cả năm lỗ đều thuộc
 * cùng một họ: kiểm định *trông như* đã chạy, nhưng có vùng nó không chạm tới,
 * và một payload sai vẫn được ghi là SUCCEEDED.
 */
describe('lỗ hổng kiểm định (Codex Phase 4)', () => {
  it('câu nhân quả + kết luận thumbnail trong manualReviewTargets bị bắt', () => {
    // Trước khi sửa, `manualReviewTargets` KHÔNG hề được quét. Đây là chỗ tự
    // nhiên nhất để viết một câu vừa nhân quả vừa kết luận về thumbnail.
    const r = run(
      makeOutput({
        manualReviewTargets: [
          {
            targetType: 'VIDEO',
            targetId: 'aaaaaaaaaaa',
            reason: 'Thumbnail kém dẫn tới lượt xem thấp',
            evidenceIds: [],
            reviewQuestions: ['Có nên thay thumbnail không?'],
          },
        ],
      }),
    )
    expect(r.report.passed).toBe(false)
    expect(r.report.causalViolations).toBeGreaterThan(0)
    expect(r.report.ctrViolations).toBeGreaterThan(0)
  })

  it('câu miễn trừ ở đầu trường KHÔNG tha cho khẳng định ở câu sau', () => {
    // "Không có dữ liệu CTR." làm cả trường trông như đang nói về thiếu dữ liệu,
    // trong khi câu thứ hai vẫn kết luận thẳng. Ngoại lệ phải xét theo TỪNG CÂU.
    const r = run(
      makeOutput({
        analysisSummary: {
          ...makeOutput().analysisSummary,
          overallAssessment:
            'Không có dữ liệu CTR. Tuy nhiên thumbnail hiện tại kém và impressions thấp.',
        },
      }),
    )
    expect(r.report.passed).toBe(false)
    expect(r.report.ctrViolations).toBeGreaterThan(0)
  })


  it('phát hiện tự trích chính nó bị chặn', () => {
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, id: 'F-001', evidenceIds: ['F-001'] },
        ],
      }),
    )
    expect(r.report.passed).toBe(false)
    expect(r.report.evidenceIssues.some((i) => i.rule === 'self_referential_evidence')).toBe(true)
  })

  it('trích dẫn nội bộ VÒNG TRÒN bị chặn', () => {
    // F-001 -> H-001 -> F-001. Mọi id đều "tồn tại", tỉ lệ giải được 100%,
    // nhưng không có một mẩu bằng chứng nào của gói đứng sau.
    const r = run(
      makeOutput({
        keyFindings: [{ ...makeOutput().keyFindings[0]!, id: 'F-001', evidenceIds: ['H-001'] }],
        hypotheses: [
          {
            id: 'H-001',
            statement: 'Một giả thuyết có thể đúng về nhịp đăng của kênh này.',
            status: 'UNVERIFIED',
            confidence: 'LOW',
            supportingEvidenceIds: ['F-001'],
            contradictingEvidenceIds: [],
            missingEvidence: ['Chưa có dữ liệu tiếp cận'],
            validationMethod: 'Theo dõi thêm hai tuần rồi so sánh lại.',
          },
        ],
      }),
    )
    expect(r.report.passed).toBe(false)
    expect(r.report.evidenceIssues.some((i) => i.rule === 'evidence_not_grounded')).toBe(true)
    expect(r.failureClass).toBe('EVIDENCE_UNRESOLVED')
  })

  it('trích nội bộ có neo về bằng chứng gói thì HỢP LỆ', () => {
    // F-002 dựa trên F-001, mà F-001 neo vào OBS-001. Đây là cách viết đúng và
    // phải được phép — quy tắc chống vòng tròn không được cấm trích chéo.
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, id: 'F-001', evidenceIds: ['OBS-001'] },
          { ...makeOutput().keyFindings[0]!, id: 'F-002', evidenceIds: ['F-001'] },
        ],
      }),
    )
    expect(r.report.evidenceIssues.filter((i) => i.rule === 'evidence_not_grounded')).toHaveLength(0)
  })

  it('lỗi mức HIGH chặn ĐẠT, không được ghi là thành công', () => {
    // Ca thật: một lần chạy hinh_su từng được lưu SUCCEEDED kèm 3 lỗi HIGH.
    const r = run(
      makeOutput({
        keyFindings: [
          { ...makeOutput().keyFindings[0]!, findingType: 'OBSERVATION', evidenceIds: [] },
        ],
      }),
    )
    expect(r.report.qualityIssues.some((i) => i.rule === 'finding_without_evidence')).toBe(true)
    expect(r.report.passed).toBe(false)
    expect(r.failureClass).not.toBe('NONE')
  })

  it('chỉ số bịa (rpm/cpm/revenue) chặn ĐẠT', () => {
    const r = run(
      makeOutput({
        analysisSummary: {
          ...makeOutput().analysisSummary,
          overallAssessment: 'Kênh có xu hướng rpm giảm trong giai đoạn được xét gần đây.',
        },
      }),
    )
    expect(r.report.unsupportedMetricViolations).toBeGreaterThan(0)
    expect(r.report.passed).toBe(false)
  })
})

describe('trần kích thước prompt', () => {
  it('khi cắt bớt, prompt NÊU RÕ phần đã lược bỏ', () => {
    // Không nói cho mô hình biết danh sách đã bị cắt thì nó sẽ suy luận như thể
    // danh sách là đầy đủ.
    const many = Array.from({ length: 40 }, (_, i) => ({
      youtubeVideoId: `vid${String(i).padStart(7, '0')}`,
      title: `Video số ${i} với tiêu đề dài để đẩy kích thước prompt lên cao`,
      format: 'SHORT' as const,
      viewsD7: 100 + i,
    }))
    const pkg = makePackage({ rankedVideos: many })
    const built = buildPrompt({ pkg, maxChars: 20_000 })
    expect(built.omissions.length).toBeGreaterThan(0)
    expect(built.text).toContain('OMITTED EVIDENCE')
    expect(built.text).toContain('KHÔNG đầy đủ')
    expect(built.text.length).toBeLessThanOrEqual(20_000)
  })

  it('trần là trần thật: vượt sau khi cắt thì báo lỗi, không im lặng chấp nhận', () => {
    const pkg = makePackage()
    expect(() => buildPrompt({ pkg, maxChars: 500 })).toThrow(/vượt trần/)
  })
})


describe('neo bằng chứng: đồ thị nhiều tầng', () => {
  const base = makeOutput()

  it('chuỗi neo NHIỀU TẦNG vẫn hợp lệ bất kể thứ tự kiểm', () => {
    // F-003 -> F-002 -> F-001 -> OBS-001. Bản nhớ đệm DFS cũ có thể nhớ nhầm
    // một kết quả phụ thuộc đường đi và từ chối oan tuỳ thứ tự duyệt.
    const r = run(
      makeOutput({
        keyFindings: [
          { ...base.keyFindings[0]!, id: 'F-001', evidenceIds: ['OBS-001'] },
          { ...base.keyFindings[0]!, id: 'F-002', evidenceIds: ['F-001'] },
          { ...base.keyFindings[0]!, id: 'F-003', evidenceIds: ['F-002'] },
        ],
      }),
    )
    expect(r.report.evidenceIssues.filter((i) => i.rule === 'evidence_not_grounded')).toHaveLength(0)
    expect(r.report.passed).toBe(true)
  })

  it('chu trình có MỘT lối neo thì cả cụm hợp lệ', () => {
    // F-001 <-> H-001, nhưng F-001 cũng neo vào OBS-001.
    const r = run(
      makeOutput({
        keyFindings: [{ ...base.keyFindings[0]!, id: 'F-001', evidenceIds: ['H-001', 'OBS-001'] }],
        hypotheses: [
          {
            id: 'H-001',
            statement: 'Một giả thuyết có thể đúng về nhịp đăng của kênh này.',
            status: 'UNVERIFIED',
            confidence: 'LOW',
            supportingEvidenceIds: ['F-001'],
            contradictingEvidenceIds: [],
            missingEvidence: ['Chưa có dữ liệu tiếp cận'],
            validationMethod: 'Theo dõi thêm hai tuần rồi so sánh lại.',
          },
        ],
      }),
    )
    expect(r.report.evidenceIssues.filter((i) => i.rule === 'evidence_not_grounded')).toHaveLength(0)
  })

  it('chu trình HOÀN TOÀN khép kín bị chặn dù dài', () => {
    // F-001 -> F-002 -> F-003 -> F-001, không mục nào chạm bằng chứng gói.
    const r = run(
      makeOutput({
        keyFindings: [
          { ...base.keyFindings[0]!, id: 'F-001', evidenceIds: ['F-002'] },
          { ...base.keyFindings[0]!, id: 'F-002', evidenceIds: ['F-003'] },
          { ...base.keyFindings[0]!, id: 'F-003', evidenceIds: ['F-001'] },
        ],
      }),
    )
    expect(r.report.passed).toBe(false)
    expect(r.report.evidenceIssues.filter((i) => i.rule === 'evidence_not_grounded').length).toBe(3)
  })
})





/**
 * Bốn câu THẬT bị từ chối oan trong lần đo độ ổn định, kèm các ca đối chứng
 * chứng minh quy tắc vẫn chặn kết luận CTR thật.
 */



/**
 * Không nhánh nào trong từ vựng được phép CHẾT.
 *
 * `\b` chỉ tính theo [A-Za-z0-9_], nên mọi cụm tiếng Việt kết thúc bằng chữ có
 * dấu mà bọc trong `\b...\b` sẽ không bao giờ khớp — và im lặng. Ba lần đã dính
 * bẫy này ("0%", "thay vì", "hiệu quả"), nên nay kiểm bằng máy từng cụm một.
 */


/**
 * Hợp đồng KHẲNG ĐỊNH CÓ CẤU TRÚC (schema 2.0).
 *
 * Bảy cấu trúc ngữ pháp đã đánh bại cách dò chuỗi. Ở đây từng câu THẬT đó được
 * kiểm lại theo ba trạng thái: khai đúng -> cho qua; không khai -> chặn vì
 * thiếu khai báo; khai là ASSERTED -> chặn vì khẳng định không có căn cứ.
 */
function claim(over: Partial<CursorOutput['metricClaims'][number]> = {}) {
  return {
    id: 'MC-100',
    claimType: 'METHODOLOGY_LIMITATION' as const,
    subjectMetric: 'views' as const,
    relatedMetric: 'impression_ctr' as const,
    judgement: 'LOW' as const,
    assertionStatus: 'LIMITATION' as const,
    evidenceIds: [] as string[],
    requiresMissingnessDisclosure: false,
    // 2.1: TRỎ tới ô gốc. Mặc định trỏ vào limitations[0] của F-001, nơi
    // `withProse` đặt câu cần kiểm.
    sourceRef: { section: 'KEY_FINDING' as const, itemId: 'F-001', field: 'limitations', ordinal: 0 },
    ...over,
  }
}

/** Đặt câu vào một trường tự do rồi kèm (hoặc không kèm) khai báo. */
function withProse(text: string, claims: Array<ReturnType<typeof claim>>) {
  const base = makeOutput()
  return makeOutput({
    keyFindings: [{ ...base.keyFindings[0]!, limitations: [text] }],
    metricClaims: [...base.metricClaims, ...claims],
  })
}

describe('hợp đồng có cấu trúc: các câu THẬT từng bị chặn oan', () => {
  const REAL_SENTENCES: Array<[string, ReturnType<typeof claim>]> = [
    [
      'views quá thấp để ổn định CTR',
      claim({ id: 'MC-101', subjectMetric: 'views', relatedMetric: 'impression_ctr' }),
    ],
    [
      'Sample size view thấp làm CTR nhiễu',
      claim({ id: 'MC-102', subjectMetric: 'sample_size', relatedMetric: 'impression_ctr' }),
    ],
    [
      'Dễ nhầm retention thấp với vấn đề CTR',
      claim({ id: 'MC-103', subjectMetric: 'retention', relatedMetric: 'impression_ctr' }),
    ],
    [
      'Khi có impressions/CTR: so sánh CTR và impressions của nhóm high-retention/low-views',
      claim({
        id: 'MC-104',
        claimType: 'DIAGNOSTIC_PLAN',
        subjectMetric: 'impression_ctr',
        relatedMetric: 'retention',
        judgement: 'UNKNOWN',
        assertionStatus: 'CONDITIONAL',
      }),
    ],
    [
      'nếu CTR thấp + impressions cao sẽ hướng kiểm chứng khác nhau',
      claim({
        id: 'MC-105',
        claimType: 'DIAGNOSTIC_PLAN',
        subjectMetric: 'impression_ctr',
        judgement: 'UNKNOWN',
        assertionStatus: 'CONDITIONAL',
      }),
    ],
    [
      'ưu tiên retention thay vì đổi thumbnail hàng loạt',
      claim({
        id: 'MC-106',
        claimType: 'RECOMMENDATION',
        subjectMetric: 'thumbnail',
        judgement: 'NOT_APPLICABLE',
        assertionStatus: 'NEGATED_ACTION',
      }),
    ],
    [
      'Độ phủ impressions/CTR >0 và observedDates tăng rõ',
      claim({
        id: 'MC-107',
        claimType: 'RECOMMENDATION',
        subjectMetric: 'data_coverage',
        relatedMetric: 'impression_ctr',
        judgement: 'UNKNOWN',
        assertionStatus: 'CONDITIONAL',
      }),
    ],
  ]

  for (const [sentence, mc] of REAL_SENTENCES) {
    it(`KHAI ĐÚNG -> cho qua: "${sentence.slice(0, 46)}…"`, () => {
      const r = run(withProse(sentence, [mc]))
      expect(r.report.claimIssues.filter((i) => i.rule === 'undeclared_sensitive_unit')).toHaveLength(0)
      expect(r.report.passed, JSON.stringify(r.report.claimIssues)).toBe(true)
    })

    it(`KHÔNG KHAI -> chặn vì thiếu khai báo: "${sentence.slice(0, 36)}…"`, () => {
      const r = run(withProse(sentence, []))
      expect(r.report.claimIssues.some((i) => i.rule === 'undeclared_sensitive_unit')).toBe(true)
      expect(r.report.passed).toBe(false)
    })
  }
})

describe('hợp đồng có cấu trúc: khẳng định thật vẫn bị CHẶN', () => {
  const ASSERTED: Array<[string, string]> = [
    ['CTR thấp', 'impression_ctr'],
    ['CTR không cao', 'impression_ctr'],
    ['CTR không thấp', 'impression_ctr'],
    ['Thumbnail không hiệu quả', 'thumbnail'],
    ['Hình thu nhỏ kém hấp dẫn', 'thumbnail'],
  ]
  for (const [sentence, metric] of ASSERTED) {
    it(`ASSERTED về chỉ số phủ 0% -> chặn: "${sentence}"`, () => {
      const r = run(
        withProse(sentence, [
          claim({
            id: 'MC-200',
            claimType: 'OBSERVATION',
            subjectMetric: metric as 'impression_ctr',
            relatedMetric: 'NONE',
            judgement: 'LOW',
            assertionStatus: 'ASSERTED',
            evidenceIds: ['OBS-001'],
          }),
        ]),
      )
      expect(r.report.claimIssues.some((i) => i.rule === 'asserted_claim_on_missing_metric')).toBe(true)
      expect(r.report.passed).toBe(false)
    })
  }

  it('CAUSAL + ASSERTED bị cấm tuyệt đối', () => {
    const r = run(
      withProse('thumbnail kém gây ra sụt giảm lượt xem', [
        claim({
          id: 'MC-201',
          claimType: 'CAUSAL',
          subjectMetric: 'thumbnail',
          judgement: 'INEFFECTIVE',
          assertionStatus: 'ASSERTED',
          evidenceIds: ['OBS-001'],
        }),
      ]),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'asserted_causal_claim')).toBe(true)
    expect(r.report.passed).toBe(false)
  })
})

describe('hợp đồng có cấu trúc: chống LẠM DỤNG tự khai', () => {
  it('"CTR thấp" dán nhãn METHODOLOGY_LIMITATION bị chặn (subject trùng related)', () => {
    const r = run(
      withProse('CTR thấp', [
        claim({
          id: 'MC-300',
          claimType: 'METHODOLOGY_LIMITATION',
          subjectMetric: 'impression_ctr',
          relatedMetric: 'impression_ctr',
          judgement: 'LOW',
          assertionStatus: 'LIMITATION',
        }),
      ]),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'methodology_disguising_assertion')).toBe(true)
    expect(r.report.passed).toBe(false)
  })

  it('giới hạn phương pháp có CHỦ NGỮ cũng thiếu dữ liệu bị chặn', () => {
    const r = run(
      withProse('impressions thấp làm CTR nhiễu', [
        claim({
          id: 'MC-301',
          claimType: 'METHODOLOGY_LIMITATION',
          subjectMetric: 'impressions',
          relatedMetric: 'impression_ctr',
          judgement: 'LOW',
          assertionStatus: 'LIMITATION',
        }),
      ]),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'methodology_subject_also_missing')).toBe(true)
  })

  it('QUESTION mang phán xét khẳng định bị chặn', () => {
    const r = run(
      withProse('CTR thấp phải không?', [
        claim({
          id: 'MC-302',
          claimType: 'DIAGNOSTIC_PLAN',
          subjectMetric: 'impression_ctr',
          judgement: 'LOW',
          assertionStatus: 'QUESTION',
        }),
      ]),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'contradictory_claim_fields')).toBe(true)
  })

  it('DIAGNOSTIC_PLAN + ASSERTED bị chặn', () => {
    const r = run(
      withProse('sẽ đo CTR trong kỳ tới', [
        claim({
          id: 'MC-303',
          claimType: 'DIAGNOSTIC_PLAN',
          subjectMetric: 'impression_ctr',
          judgement: 'LOW',
          assertionStatus: 'ASSERTED',
          evidenceIds: ['OBS-001'],
        }),
      ]),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'contradictory_claim_fields')).toBe(true)
  })

  it('ASSERTED có phán xét mà KHÔNG bằng chứng bị chặn (chỉ số có dữ liệu)', () => {
    const r = run(
      withProse('lượt xem 7 ngày ở mức cao', [
        claim({
          id: 'MC-304',
          claimType: 'OBSERVATION',
          subjectMetric: 'views_d7',
          relatedMetric: 'NONE',
          judgement: 'HIGH',
          assertionStatus: 'ASSERTED',
          evidenceIds: [],
        }),
      ]),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'asserted_claim_without_evidence')).toBe(true)
  })

  it('id claim trùng bị chặn', () => {
    const c = claim({ id: 'MC-400' })
    const r = run(withProse('views quá thấp để ổn định CTR', [c, { ...c }]))
    expect(r.report.structuralIssues.some((i) => i.rule === 'duplicate_claim_id')).toBe(true)
  })
})

describe('hợp đồng có cấu trúc: độ phủ đọc từ GÓI, không hardcode', () => {
  it('khi impressions CÓ dữ liệu thì ASSERTED về CTR được phép', () => {
    const pkg = makePackage({
      dataCoverage: {
        ...makePackage().dataCoverage,
        metricCoverage: { views: 1, impressions: 0.9, impressionCtr: 0.9 },
      },
    })
    const built = buildPrompt({ pkg })
    const out = withProse('CTR ở mức cao so với median', [
      claim({
        id: 'MC-500',
        claimType: 'OBSERVATION',
        subjectMetric: 'impression_ctr',
        relatedMetric: 'NONE',
        judgement: 'HIGH',
        assertionStatus: 'ASSERTED',
        evidenceIds: ['OBS-001'],
      }),
    ])
    const r = validateCursorOutput({
      raw: JSON.stringify(out),
      pkg,
      allowedEvidenceIds: built.allowedEvidenceIds,
      allowedVideoIds: built.allowedVideoIds,
      allowedCohortKeys: built.allowedCohortKeys,
      hadProseOutsideJson: false,
    })
    expect(r.report.claimIssues.filter((i) => i.rule === 'asserted_claim_on_missing_metric')).toHaveLength(0)
  })
})

/**
 * RANH GIỚI TIN CẬY của phép nối văn xuôi ↔ claim.
 *
 * Phép nối là HEURISTIC (trùng 60% từ nội dung). Nó chặn được việc QUÊN KHAI.
 * Nó KHÔNG chứng minh `text` của claim đúng là câu trong văn xuôi. Các test dưới
 * đây ghi lại chính xác chỗ nó mạnh và chỗ nó yếu — chỗ yếu được xử lý bằng quy
 * tắc tất định trên trường, không bằng phép nối.
 */

/**
 * TÍNH CHẤT BẤT BIẾN — quét toàn bộ tổ hợp thay vì vài ca lẻ.
 *
 * Mục đích: không tổ hợp hợp-lệ-về-schema nào lọt qua MỌI nhánh kiểm định, và
 * không có cách nào biến một khẳng định không căn cứ thành hợp lệ chỉ bằng cách
 * đổi nhãn.
 */
describe('bất biến của hợp đồng có cấu trúc', () => {
  const base = makeOutput()
  const SENSITIVE = ['impressions', 'impression_ctr', 'thumbnail', 'packaging'] as const
  const AVAILABLE = ['views', 'views_d7', 'retention', 'sample_size', 'engagement'] as const
  const JUDGEMENTS = ['HIGH', 'LOW', 'INCREASED', 'DECREASED', 'EFFECTIVE', 'INEFFECTIVE'] as const

  // 2.1: văn xuôi do test đặt vào ô; claim chỉ TRỎ tới. Mặc định dùng một câu
  // chứa cả chủ ngữ lẫn chỉ số liên quan để các quy tắc S có dữ liệu thật.
  const mk = (c: ReturnType<typeof claim>, prose = 'lượt xem thấp nên CTR chưa ổn định') =>
    makeOutput({
      keyFindings: [{ ...base.keyFindings[0]!, limitations: [prose] }],
      metricClaims: [...base.metricClaims, c],
    })

  it('BẤT BIẾN 1: ASSERTED + phán xét + chỉ số phủ 0% luôn CHẶN, mọi tổ hợp', () => {
    for (const metric of SENSITIVE) {
      for (const judgement of JUDGEMENTS) {
        for (const claimType of ['OBSERVATION', 'COMPARISON', 'RECOMMENDATION'] as const) {
          const r = run(
            mk(
              claim({
                id: 'MC-900',
                claimType,
                subjectMetric: metric,
                relatedMetric: 'NONE',
                judgement,
                assertionStatus: 'ASSERTED',
                evidenceIds: ['OBS-001'],
              }),
            ),
          )
          expect(
            r.report.claimIssues.some((i) => i.rule === 'asserted_claim_on_missing_metric'),
            `${claimType}/${metric}/${judgement} KHÔNG bị chặn`,
          ).toBe(true)
          expect(r.report.passed).toBe(false)
        }
      }
    }
  })

  it('BẤT BIẾN 2: chỉ đổi relatedMetric KHÔNG biến khẳng định sai thành hợp lệ', () => {
    for (const related of [...AVAILABLE, 'NONE'] as const) {
      const r = run(
        mk(
          claim({
            id: 'MC-901',
            claimType: 'OBSERVATION',
            subjectMetric: 'impression_ctr',
            relatedMetric: related,
            judgement: 'LOW',
            assertionStatus: 'ASSERTED',
            evidenceIds: ['OBS-001'],
          }),
        ),
      )
      expect(r.report.passed, `relatedMetric=${related} lại cho qua`).toBe(false)
    }
  })

  it('BẤT BIẾN 3: đổi LIMITATION -> ASSERTED thì chặn ngay khi thiếu dữ liệu', () => {
    const asLimitation = claim({
      id: 'MC-902',
      claimType: 'METHODOLOGY_LIMITATION',
      subjectMetric: 'views',
      relatedMetric: 'impression_ctr',
      judgement: 'LOW',
      assertionStatus: 'LIMITATION',
    })
    expect(run(mk(asLimitation)).report.passed).toBe(true)

    const asAsserted = {
      ...asLimitation,
      claimType: 'OBSERVATION' as const,
      subjectMetric: 'impression_ctr' as const,
      relatedMetric: 'NONE' as const,
      assertionStatus: 'ASSERTED' as const,
      evidenceIds: ['OBS-001'],
    }
    expect(run(mk(asAsserted, 'CTR thấp trong kỳ này')).report.passed).toBe(false)
  })

  it('BẤT BIẾN 4: CAUSAL không thể nấp sau CONDITIONAL/QUESTION mà bỏ bằng chứng', () => {
    for (const status of ['CONDITIONAL', 'QUESTION'] as const) {
      const r = run(
        mk(
          claim({
            id: 'MC-903',
            claimType: 'CAUSAL',
            subjectMetric: 'thumbnail',
            relatedMetric: 'views',
            judgement: 'UNKNOWN',
            assertionStatus: status,
            evidenceIds: [],
          }),
        ),
      )
      // Không ASSERTED nên không bị cấm tuyệt đối, nhưng cũng không được coi là
      // phát hiện: nó vẫn nằm ở dạng chưa kiểm chứng.
      expect(r.report.claimIssues.some((i) => i.rule === 'asserted_causal_claim')).toBe(false)
    }
    const asserted = run(
      mk(
        claim({
          id: 'MC-904',
          claimType: 'CAUSAL',
          subjectMetric: 'thumbnail',
          relatedMetric: 'views',
          judgement: 'INEFFECTIVE',
          assertionStatus: 'ASSERTED',
          evidenceIds: ['OBS-001'],
        }),
      ),
    )
    expect(asserted.report.claimIssues.some((i) => i.rule === 'asserted_causal_claim')).toBe(true)
  })

  it('BẤT BIẾN 5: mọi từ vựng nhạy cảm đều được bộ quét đầy đủ phát hiện', () => {
    const TERMS = ['CTR', 'click-through', 'impressions', 'impression', 'thumbnail', 'hình thu nhỏ', 'tỉ lệ nhấp', 'packaging']
    for (const t of TERMS) {
      const r = run(mk(claim({ id: 'MC-905' }), `Cần xem lại ${t} ở kỳ sau.`))
      expect(
        r.report.claimIssues.some((i) => i.rule === 'undeclared_sensitive_unit'),
        `từ "${t}" KHÔNG được bộ quét phát hiện`,
      ).toBe(true)
    }
  })

  it('BẤT BIẾN 6: METHODOLOGY_LIMITATION với chủ ngữ thiếu dữ liệu luôn chặn', () => {
    for (const subject of SENSITIVE) {
      for (const related of SENSITIVE) {
        const r = run(
          mk(
            claim({
              id: 'MC-906',
              claimType: 'METHODOLOGY_LIMITATION',
              subjectMetric: subject,
              relatedMetric: related,
              judgement: 'LOW',
              assertionStatus: 'LIMITATION',
            }),
          ),
        )
        expect(r.report.passed, `${subject}/${related} lại cho qua`).toBe(false)
      }
    }
  })

  it('BẤT BIẾN 7: chỉ số CÓ dữ liệu vẫn cho phép khẳng định có bằng chứng', () => {
    for (const metric of AVAILABLE) {
      const r = run(
        mk(
          claim({
            id: 'MC-907',
            claimType: 'OBSERVATION',
            subjectMetric: metric,
            relatedMetric: 'impression_ctr',
            judgement: 'HIGH',
            assertionStatus: 'ASSERTED',
            evidenceIds: ['OBS-001'],
          }),
        ),
      )
      expect(
        r.report.claimIssues.some((i) => i.rule === 'asserted_claim_on_missing_metric'),
        `${metric} bị chặn oan`,
      ).toBe(false)
    }
  })
})

/**
 * MỌI bề mặt văn bản đều phải bị quét.
 *
 * Test này đặt một câu nhạy cảm CHƯA KHAI vào từng trường tự do một, và đòi bộ
 * quét phải bắt được ở mọi trường. Nếu sau này thêm một trường tự do mới vào
 * schema mà quên đăng ký, ca tương ứng sẽ đỏ — thay vì lặng lẽ trở thành lỗ.
 */
describe('phủ kín bề mặt văn bản', () => {
  const base = makeOutput()
  const PROBE = 'CTR thấp rõ rệt ở nhóm này'
  const expectCaught = (out: CursorOutput, where: string) => {
    const r = run(out)
    expect(
      r.report.claimIssues.some((i) => i.rule === 'undeclared_sensitive_unit'),
      `trường "${where}" KHÔNG được quét`,
    ).toBe(true)
  }

  it('tóm tắt phân tích', () => {
    for (const k of ['overallAssessment', 'confidenceRationale', 'primaryConstraint'] as const) {
      expectCaught(
        makeOutput({ analysisSummary: { ...base.analysisSummary, [k]: `${PROBE} và cần xem lại.` } }),
        `analysisSummary.${k}`,
      )
    }
  })

  it('phát hiện: statement, supportingReasoning, limitations', () => {
    expectCaught(makeOutput({ keyFindings: [{ ...base.keyFindings[0]!, statement: `${PROBE} trong kỳ.` }] }), 'statement')
    expectCaught(
      makeOutput({ keyFindings: [{ ...base.keyFindings[0]!, supportingReasoning: `${PROBE} theo quan sát.` }] }),
      'supportingReasoning',
    )
    expectCaught(makeOutput({ keyFindings: [{ ...base.keyFindings[0]!, limitations: [PROBE] }] }), 'limitations')
  })

  it('giả thuyết: statement, validationMethod, missingEvidence', () => {
    const h = {
      id: 'H-001' as const,
      statement: 'Một giả thuyết trung tính về nhịp đăng của kênh này.',
      status: 'UNVERIFIED' as const,
      confidence: 'LOW' as const,
      supportingEvidenceIds: ['OBS-001'],
      contradictingEvidenceIds: [],
      missingEvidence: ['Chưa có dữ liệu tiếp cận'],
      validationMethod: 'Theo dõi thêm hai tuần rồi so sánh lại.',
    }
    expectCaught(makeOutput({ hypotheses: [{ ...h, statement: `${PROBE} nên cần xem.` }] }), 'hyp.statement')
    expectCaught(makeOutput({ hypotheses: [{ ...h, validationMethod: `${PROBE} nên cần đo.` }] }), 'validationMethod')
    expectCaught(makeOutput({ hypotheses: [{ ...h, missingEvidence: [PROBE] }] }), 'missingEvidence')
  })

  it('khuyến nghị: action, rationale, successMetric, risks', () => {
    const r0 = base.recommendations[0]
    const rec = r0 ?? {
      id: 'R-001' as const,
      action: 'Giữ nhịp đăng hiện tại trong hai tuần tới.',
      priority: 'P1' as const,
      category: 'CONTINUE' as const,
      rationale: 'Bằng chứng cho thấy nhịp hiện tại phù hợp.',
      evidenceIds: ['OBS-001'],
      expectedValue: 'MEDIUM' as const,
      effort: 'LOW' as const,
      reversibility: 'HIGH' as const,
      measurementFeasibility: 'HIGH' as const,
      risks: [],
      successMetric: 'views_d7 trung vị không giảm',
    }
    for (const k of ['action', 'rationale', 'successMetric'] as const) {
      expectCaught(makeOutput({ recommendations: [{ ...rec, [k]: `${PROBE} nên điều chỉnh.` }] }), `rec.${k}`)
    }
    expectCaught(makeOutput({ recommendations: [{ ...rec, risks: [PROBE] }] }), 'rec.risks')
  })

  it('thí nghiệm: change, baseline, successMetrics, sampleLimitations, stopConditions, interpretationRisks', () => {
    const exp = {
      id: 'E-001' as const,
      hypothesisId: 'H-001' as const,
      change: 'Đổi nhịp đăng sang hai video mỗi tuần.',
      baseline: 'Nhịp hiện tại một video mỗi tuần.',
      successMetrics: ['views_d7 trung vị tăng'] as string[],
      minimumWindowDays: 14,
      sampleLimitations: [] as string[],
      stopConditions: ['Dừng nếu lượt xem giảm quá nửa'] as string[],
      interpretationRisks: ['Có thể trùng mùa vụ'] as string[],
    }
    const h = {
      id: 'H-001' as const,
      statement: 'Một giả thuyết trung tính về nhịp đăng của kênh này.',
      status: 'UNVERIFIED' as const,
      confidence: 'LOW' as const,
      supportingEvidenceIds: ['OBS-001'],
      contradictingEvidenceIds: [],
      missingEvidence: ['Chưa có dữ liệu tiếp cận'],
      validationMethod: 'Theo dõi thêm hai tuần rồi so sánh lại.',
    }
    const mk = (over: Partial<typeof exp>) =>
      makeOutput({ hypotheses: [h], experiments: [{ ...exp, ...over }] })
    expectCaught(mk({ change: `${PROBE} nên thử đổi.` }), 'exp.change')
    expectCaught(mk({ baseline: `${PROBE} làm mốc.` }), 'exp.baseline')
    expectCaught(mk({ successMetrics: [PROBE] }), 'exp.successMetrics')
    expectCaught(mk({ sampleLimitations: [PROBE] }), 'exp.sampleLimitations')
    expectCaught(mk({ stopConditions: [PROBE] }), 'exp.stopConditions')
    expectCaught(mk({ interpretationRisks: [PROBE] }), 'exp.interpretationRisks')
  })

  it('mục rà soát thủ công và yêu cầu dữ liệu', () => {
    expectCaught(
      makeOutput({
        manualReviewTargets: [
          { targetType: 'VIDEO', targetId: 'aaaaaaaaaaa', reason: `${PROBE} nên xem.`, evidenceIds: ['OBS-001'], reviewQuestions: ['Xem lại?'] },
        ],
      }),
      'manualReview.reason',
    )
    expectCaught(
      makeOutput({
        manualReviewTargets: [
          { targetType: 'VIDEO', targetId: 'aaaaaaaaaaa', reason: 'Cần rà soát nội dung.', evidenceIds: ['OBS-001'], reviewQuestions: [PROBE] },
        ],
      }),
      'manualReview.reviewQuestions',
    )
    for (const k of ['metricOrArtifact', 'reason', 'decisionUnlocked'] as const) {
      const dr = { metricOrArtifact: 'impressions theo ngày', reason: 'Cần để tách tiếp cận.', decisionUnlocked: 'Biết nên sửa gì trước.' }
      expectCaught(makeOutput({ dataRequests: [{ ...dr, [k]: `${PROBE} nên thu thập.` }] }), `dataRequest.${k}`)
    }
  })

  it('explicitNonConclusions', () => {
    expectCaught(makeOutput({ explicitNonConclusions: [PROBE] }), 'explicitNonConclusions')
  })

  it('văn bản NGOÀI JSON', () => {
    const built = buildPrompt({ pkg: makePackage() })
    const r = validateCursorOutput({
      raw: JSON.stringify(makeOutput()),
      pkg: makePackage(),
      allowedEvidenceIds: built.allowedEvidenceIds,
      allowedVideoIds: built.allowedVideoIds,
      allowedCohortKeys: built.allowedCohortKeys,
      hadProseOutsideJson: true,
      proseText: PROBE,
    })
    expect(r.report.claimIssues.some((i) => i.rule === 'undeclared_sensitive_unit')).toBe(true)
  })
})

/**
 * SỬA LỖI KỸ THUẬT không được đổi NGỮ NGHĨA.
 *
 * Prompt sửa lỗi có dặn "giữ nguyên kết luận", nhưng dặn không phải là ràng
 * buộc. Nếu không kiểm, một lần sửa có thể hạ ASSERTED xuống LIMITATION rồi
 * "đạt" — và kết quả đó thuộc về một phân tích khác với phân tích đã bị từ chối.
 */
describe('bất biến ngữ nghĩa của lần sửa lỗi', () => {
  const mkClaim = (over: Record<string, unknown> = {}) => ({
    id: 'MC-001',
    claimType: 'OBSERVATION',
    subjectMetric: 'views_d7',
    relatedMetric: 'NONE',
    judgement: 'HIGH',
    assertionStatus: 'ASSERTED',
    evidenceIds: ['OBS-001', 'VIDEO-aaaaaaaaaaa'],
    requiresMissingnessDisclosure: false,
    sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'statement', ordinal: 0 },
    ...over,
  })

  const root = [mkClaim()] as never
  /** 2.1: drift so VĂN BẢN ĐÃ PHÂN GIẢI, truyền qua map theo claim id. */
  const T = (m: Record<string, string>) => new Map(Object.entries(m))
  const SAME = T({ 'MC-001': 'lượt xem 7 ngày ở mức cao' })

  it('không trôi dạt khi mọi thứ giữ nguyên', () => {
    expect(detectSemanticDrift(root, [mkClaim()] as never, SAME, SAME)).toHaveLength(0)
  })

  it('BẮT: đổi văn xuôi ô nguồn (2.1 siết hơn 2.0)', () => {
    const d = detectSemanticDrift(
      root, [mkClaim()] as never,
      SAME, T({ 'MC-001': 'Lượt xem trong 7 ngày đầu ở mức cao.' }),
    ).join(' ')
    expect(d).toContain('văn bản ô nguồn đã đổi')
  })

  it('BẮT: bỏ mất claim', () => {
    expect(detectSemanticDrift(root, [] as never, SAME, SAME)).toContain('bỏ mất claim MC-001')
  })

  it('BẮT: hạ ASSERTED xuống LIMITATION', () => {
    const repaired = [mkClaim({ assertionStatus: 'LIMITATION' })] as never
    expect(detectSemanticDrift(root, repaired).join(' ')).toContain('assertionStatus')
  })

  it('BẮT: đổi subjectMetric', () => {
    const repaired = [mkClaim({ subjectMetric: 'impression_ctr' })] as never
    expect(detectSemanticDrift(root, repaired).join(' ')).toContain('subjectMetric')
  })

  it('BẮT: đổi relatedMetric', () => {
    const repaired = [mkClaim({ relatedMetric: 'retention' })] as never
    expect(detectSemanticDrift(root, repaired).join(' ')).toContain('relatedMetric')
  })

  it('BẮT: đổi claimType', () => {
    const repaired = [mkClaim({ claimType: 'METHODOLOGY_LIMITATION' })] as never
    expect(detectSemanticDrift(root, repaired).join(' ')).toContain('claimType')
  })

  it('BẮT: đổi judgement', () => {
    const repaired = [mkClaim({ judgement: 'LOW' })] as never
    expect(detectSemanticDrift(root, repaired).join(' ')).toContain('judgement')
  })

  it('BẮT: rút bớt evidenceIds', () => {
    const repaired = [mkClaim({ evidenceIds: ['OBS-001'] })] as never
    expect(detectSemanticDrift(root, repaired).join(' ')).toContain('mất bằng chứng')
  })

  it('BẮT: THÊM bằng chứng cũng là đổi ngữ nghĩa (chính sách đóng băng)', () => {
    // "Thiếu bằng chứng" là thất bại NỘI DUNG, vốn không được retry. Nên một
    // lần sửa KỸ THUẬT không bao giờ có lý do chính đáng để thêm bằng chứng —
    // thêm được nghĩa là nó đang tạo ra một phân tích khác.
    const repaired = [mkClaim({ evidenceIds: ['OBS-001', 'VIDEO-aaaaaaaaaaa', 'OBS-002'] })] as never
    expect(detectSemanticDrift(root, repaired).join(' ')).toContain('THÊM bằng chứng')
  })
})

describe('danh tính claim độc lập với thứ tự, ánh xạ MỘT-MỘT', () => {
  const mk = (over: Record<string, unknown> = {}) => ({
    id: 'MC-001',
    claimType: 'OBSERVATION',
    subjectMetric: 'views_d7',
    relatedMetric: 'NONE',
    judgement: 'HIGH',
    assertionStatus: 'ASSERTED',
    evidenceIds: ['OBS-001'],
    requiresMissingnessDisclosure: false,
    sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'statement', ordinal: 0 },
    ...over,
  })
  const root = [mk(), mk({ id: 'MC-002' })] as never
  const SAME = new Map([
    ['MC-001', 'lượt xem 7 ngày ở mức cao'],
    ['MC-002', 'lượt xem 7 ngày ở mức cao'],
    ['MC-009', 'lượt xem 7 ngày ở mức cao'],
    ['MC-003', 'lượt xem 7 ngày ở mức cao'],
  ])

  it('ĐẢO THỨ TỰ không phải trôi dạt', () => {
    const rev = [mk({ id: 'MC-002' }), mk()] as never
    expect(detectSemanticDrift(root, rev)).toHaveLength(0)
  })

  it('BẮT: đổi TÊN id dù ngữ nghĩa giữ nguyên', () => {
    const renamed = [mk({ id: 'MC-009' }), mk({ id: 'MC-002' })] as never
    const d = detectSemanticDrift(root, renamed).join(' ')
    expect(d).toContain('MC-009')
    expect(d).toContain('bỏ mất claim MC-001')
  })

  it('BẮT: claim trùng id', () => {
    const dup = [mk(), mk(), mk({ id: 'MC-002' })] as never
    expect(detectSemanticDrift(root, dup).join(' ')).toContain('trùng')
  })

  it('BẮT: TÁCH một claim thành nhiều', () => {
    const split = [
      mk(),
      mk({ id: 'MC-002' }),
      mk({ id: 'MC-003' }),
    ] as never
    expect(detectSemanticDrift(root, split).join(' ')).toContain('MỚI xuất hiện')
  })

  it('BẮT: GỘP nhiều claim thành một', () => {
    expect(detectSemanticDrift(root, [mk()] as never, SAME, SAME).join(' ')).toContain('bỏ mất claim MC-002')
  })

  it('BẮT: đổi QUYỀN SỞ HỮU (surface/owner)', () => {
    const moved = [
      mk({ sourceSection: 'RECOMMENDATION', sourceId: 'R-001' }),
      mk({ id: 'MC-002' }),
    ] as never
    const d = detectSemanticDrift(root, moved).join(' ')
    expect(d).toContain('sourceSection')
    expect(d).toContain('sourceId')
  })

  it('BẮT: THAY bằng chứng (bỏ cũ, thêm mới) chứ không phải chỉ thêm', () => {
    const replaced = [
      mk({ evidenceIds: ['OBS-999'] }),
      mk({ id: 'MC-002' }),
    ] as never
    expect(detectSemanticDrift(root, replaced).join(' ')).toContain('mất bằng chứng')
  })
})

/**
 * Hai lớp BLOCKER do Codex phát hiện — giữ test vĩnh viễn.
 *
 * Cả hai đều tấn công đúng chỗ yếu của tự khai: mô hình dán nhãn sai để thoát
 * quy tắc. Chúng không phải giả định lý thuyết, mà là ca cụ thể Codex dựng ra.
 */
describe('BLOCKER Codex: khai báo phải nhất quán với chính câu văn', () => {
  const base = makeOutput()
  const mk = (c: Record<string, unknown>, prose?: string) =>
    makeOutput({
      keyFindings: [{ ...base.keyFindings[0]!, limitations: [prose ?? 'CTR chưa ổn định trong kỳ này'] }],
      metricClaims: [...base.metricClaims, c as never],
    })
  const C = (over: Record<string, unknown>) => ({
    id: 'MC-800',
    claimType: 'OBSERVATION',
    subjectMetric: 'views',
    relatedMetric: 'NONE',
    judgement: 'LOW',
    assertionStatus: 'ASSERTED',
    evidenceIds: ['OBS-001'],
    requiresMissingnessDisclosure: false,
    sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
    ...over,
  })

  it('BLOCKER-1: "CTR hiện tại thấp" KHÔNG thể khai CONDITIONAL', () => {
    const r = run(
      mk(C({
        claimType: 'DIAGNOSTIC_PLAN',
        subjectMetric: 'impression_ctr',
        assertionStatus: 'CONDITIONAL',
      })),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'modality_not_supported_by_text')).toBe(true)
    expect(r.report.passed).toBe(false)
  })

  it('BLOCKER-1b: khẳng định KHÔNG thể nguỵ trang thành câu hỏi', () => {
    const r = run(
      mk(C({
        claimType: 'DIAGNOSTIC_PLAN',
        subjectMetric: 'impression_ctr',
        judgement: 'UNKNOWN',
        assertionStatus: 'QUESTION',
      })),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'modality_not_supported_by_text')).toBe(true)
  })

  it('BLOCKER-1c: khẳng định KHÔNG thể nguỵ trang thành giới hạn phương pháp', () => {
    const r = run(
      mk(C({
        claimType: 'METHODOLOGY_LIMITATION',
        subjectMetric: 'views',
        relatedMetric: 'impression_ctr',
        assertionStatus: 'LIMITATION',
      })),
    )
    // Vừa thiếu dấu hiệu giới hạn, vừa không nhắc tới chủ ngữ views.
    expect(
      r.report.claimIssues.some(
        (i) => i.rule === 'modality_not_supported_by_text' || i.rule === 'subject_metric_not_in_text',
      ),
    ).toBe(true)
    expect(r.report.passed).toBe(false)
  })

  it('BLOCKER-2: subjectMetric=views KHÔNG phủ được "Thumbnail hiện tại kém"', () => {
    const r = run(
      mk(C({
        claimType: 'METHODOLOGY_LIMITATION',
        subjectMetric: 'views',
        relatedMetric: 'thumbnail',
        assertionStatus: 'LIMITATION',
      })),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'subject_metric_not_in_text')).toBe(true)
    expect(r.report.passed).toBe(false)
  })

  it('bí danh chỉ số hoạt động cho cả tiếng Việt lẫn tiếng Anh', () => {
    for (const [metric, text] of [
      ['views', 'lượt xem quá thấp để ổn định CTR'],
      ['views', 'views too low to stabilise CTR'],
      ['retention', 'giữ chân thấp dễ nhầm với vấn đề CTR'],
      ['sample_size', 'cỡ mẫu thấp làm CTR nhiễu'],
    ] as const) {
      const r = run(
        mk(C({
          claimType: 'METHODOLOGY_LIMITATION',
          subjectMetric: metric,
          relatedMetric: 'impression_ctr',
          judgement: 'LOW',
          assertionStatus: 'LIMITATION',
          text,
        })),
      )
      expect(
        r.report.claimIssues.some((i) => i.rule === 'subject_metric_not_in_text'),
        `bí danh "${metric}" không nhận ra trong "${text}"`,
      ).toBe(false)
    }
  })


})

/**
 * Ba BLOCKER của vòng rà soát CUỐI.
 *
 * Cả ba đều thuộc cùng một họ: cấu trúc khai báo NÓI MỘT ĐẰNG, câu văn nói một
 * nẻo — và trước đây không có gì đối chiếu hai bên.
 */
describe('BLOCKER Codex vòng cuối', () => {
  const base = makeOutput()
  const mk = (c: Record<string, unknown>, prose?: string) =>
    makeOutput({
      keyFindings: [{ ...base.keyFindings[0]!, limitations: [prose ?? 'CTR chưa ổn định trong kỳ này'] }],
      metricClaims: [...base.metricClaims, c as never],
    })
  const C = (over: Record<string, unknown>) => ({
    id: 'MC-900',
    claimType: 'OBSERVATION',
    subjectMetric: 'views',
    relatedMetric: 'NONE',
    judgement: 'LOW',
    assertionStatus: 'ASSERTED',
    evidenceIds: ['OBS-001'],
    requiresMissingnessDisclosure: false,
    sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
    ...over,
  })

  it('BLOCKER-A: khai judgement NGƯỢC chiều câu bị chặn', () => {
    // Câu nói "cao", cấu trúc khai LOW.
    const r = run(mk(C({ judgement: 'LOW', subjectMetric: 'views' }), 'lượt xem ở mức cao, CTR chưa đo'))
    expect(r.report.claimIssues.some((i) => i.rule === 'judgement_contradicts_text')).toBe(true)
    expect(r.report.passed).toBe(false)
  })

  it('BLOCKER-A2: chiều tăng/giảm cũng bị đối chiếu', () => {
    const r = run(mk(C({ judgement: 'INCREASED', subjectMetric: 'views' }), 'lượt xem giảm rõ rệt, CTR chưa đo'))
    expect(r.report.claimIssues.some((i) => i.rule === 'judgement_contradicts_text')).toBe(true)
  })

  it('BLOCKER-A3: khai ĐÚNG chiều thì cho qua', () => {
    const r = run(mk(C({ judgement: 'LOW', subjectMetric: 'views' }), 'lượt xem ở mức cao, CTR chưa đo'))
    expect(r.report.claimIssues.some((i) => i.rule === 'judgement_contradicts_text')).toBe(false)
  })

  it('BLOCKER-B: phủ định CÂN BẰNG không còn lách được phép so phân cực', () => {
    // prose:  "CTR không thấp, retention giảm"
    // claim:  "CTR thấp, retention không giảm"
    // Cùng tập từ, cùng "có phủ định" — nhưng khẳng định về CTR bị đảo.
    const r = run(
      mk(
        C({
          subjectMetric: 'impression_ctr',
          relatedMetric: 'retention',
          judgement: 'LOW',
          assertionStatus: 'ASSERTED',
        }),
        'CTR không thấp, retention giảm',
      ),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'claim_polarity_mismatch')).toBe(true)
    expect(r.report.passed).toBe(false)
  })

  it('BLOCKER-C: CAUSAL + CONDITIONAL vẫn PHẢI có bằng chứng', () => {
    const r = run(
      mk(
        C({
          claimType: 'CAUSAL',
          subjectMetric: 'views',
          relatedMetric: 'thumbnail',
          judgement: 'UNKNOWN',
          assertionStatus: 'CONDITIONAL',
          evidenceIds: [],
        }),
      ),
    )
    expect(r.report.claimIssues.some((i) => i.rule === 'causal_claim_without_evidence')).toBe(true)
    expect(r.report.passed).toBe(false)
  })

  it('BLOCKER-C2: bằng chứng KHÔNG nhắc tới chủ ngữ -> EVIDENCE_SUPPORT_UNVERIFIED', () => {
    // OBS-001 trong gói mẫu nói về lượt xem 7 ngày; claim khai chủ ngữ retention.
    const r = run(
      mk(
        C({
          subjectMetric: 'retention',
          relatedMetric: 'NONE',
          judgement: 'LOW',
          assertionStatus: 'ASSERTED',
          evidenceIds: ['OBS-001'],
        }),
      ),
    )
    expect(r.report.qualityIssues.some((i) => i.rule === 'evidence_support_unverified')).toBe(true)
    // HIGH => không được coi là đạt không giám sát.
    expect(r.report.passed).toBe(false)
  })

  it('bí danh bổ sung: "thời gian xem", "người theo dõi", "tỷ lệ click"', () => {
    for (const [metric, text] of [
      ['watch_time', 'thời gian xem thấp ở nhóm này'],
      ['subscribers', 'người theo dõi thấp ở nhóm này'],
      ['impression_ctr', 'tỷ lệ click thấp ở nhóm này'],
    ] as const) {
      const r = run(mk(C({ subjectMetric: metric, judgement: 'LOW', text })))
      expect(
        r.report.claimIssues.some((i) => i.rule === 'subject_metric_not_in_text'),
        `bí danh "${metric}" chưa nhận ra trong "${text}"`,
      ).toBe(false)
    }
  })
})

/**
 * Mốc ngữ nghĩa phải có DANH TÍNH đầy đủ.
 *
 * Ca thật ở lô cấu trúc đầu tiên: root hỏng schema vì thiếu `id`/`sourceSection`;
 * lần sửa bổ sung đúng các trường đó; phép so danh tính báo 23 claim "mới" và 4
 * claim `undefined` bị mất, rồi kết luận ĐỔI NGỮ NGHĨA. Lần sửa đúng, phép so sai.
 */
describe('mốc ngữ nghĩa cần danh tính đầy đủ', () => {
  const withId = (id: string) => ({
    id,
    claimType: 'OBSERVATION',
    subjectMetric: 'views_d7',
    relatedMetric: 'NONE',
    judgement: 'HIGH',
    assertionStatus: 'ASSERTED',
    evidenceIds: ['OBS-001'],
    requiresMissingnessDisclosure: false,
  })

  it('KHÔNG báo trôi dạt giả khi root và bản sửa có cùng danh tính', () => {
    const root = [withId('MC-001'), withId('MC-002')] as never
    const repaired = [withId('MC-001'), withId('MC-002')] as never
    expect(detectSemanticDrift(root, repaired)).toHaveLength(0)
  })

  it('claim THIẾU id sinh ra trôi dạt giả nếu bị dùng làm mốc', () => {
    // Ghi lại đúng hành vi sai trước đây: mốc không có id -> mọi claim thật đều
    // bị coi là "mới" và các mục `undefined` bị coi là "mất".
    const badRoot = [{ ...withId('MC-001'), id: undefined }] as never
    const good = [withId('MC-001')] as never
    const drift = detectSemanticDrift(badRoot, good).join(' ')
    expect(drift).toContain('MỚI xuất hiện')
    expect(drift).toContain('undefined')
    // => vì vậy runner KHÔNG được dựng mốc từ dữ liệu như thế (test dưới).
  })

  it('bản sửa THÊM trường schema bắt buộc không bị coi là đổi ngữ nghĩa', () => {
    // Khi mốc hợp lệ, việc bổ sung trường không thuộc danh tính là vô hại.
    const root = [withId('MC-001')] as never
    const repaired = [{ ...withId('MC-001'), requiresMissingnessDisclosure: true }] as never
    expect(detectSemanticDrift(root, repaired)).toHaveLength(0)
  })
})

/**
 * Prompt phải NÊU RÕ hình dạng JSON của metricClaims.
 *
 * Lô cấu trúc #1 và #2 đều hỏng vì prompt mô tả KHÁI NIỆM nhưng không hề nêu
 * tên trường: mô hình bỏ `id` và đoán `sourceSection: "keyFindings"`. Không thể
 * trách mô hình vì trường nó chưa từng được cho biết. Test này giữ cho đặc tả
 * không bị rơi mất lần nữa.
 */
describe('prompt nêu đủ đặc tả metricClaims', () => {
  const { text } = buildPrompt({ pkg: makePackage() })

  it('có tên MỌI trường bắt buộc', () => {
    for (const f of [
      'id', 'claimType', 'subjectMetric', 'relatedMetric', 'judgement',
      'assertionStatus', 'evidenceIds', 'requiresMissingnessDisclosure',
      'text', 'sourceSection', 'sourceId',
    ]) {
      expect(text, `prompt thiếu trường "${f}"`).toContain(`"${f}"`)
    }
  })

  it('có MỌI giá trị enum của sourceSection', () => {
    for (const v of [
      'ANALYSIS_SUMMARY', 'KEY_FINDING', 'HYPOTHESIS', 'RECOMMENDATION',
      'EXPERIMENT', 'MANUAL_REVIEW', 'DATA_REQUEST', 'NON_CONCLUSION',
    ]) {
      expect(text, `prompt thiếu enum "${v}"`).toContain(v)
    }
  })

  it('có MỌI giá trị enum của claimType và assertionStatus', () => {
    for (const v of [
      'OBSERVATION', 'COMPARISON', 'CAUSAL', 'DIAGNOSTIC_PLAN',
      'METHODOLOGY_LIMITATION', 'ASSERTED', 'CONDITIONAL', 'QUESTION',
      'NEGATED_ACTION', 'LIMITATION',
    ]) {
      expect(text, `prompt thiếu enum "${v}"`).toContain(v)
    }
  })

  it('liệt kê mọi chỉ số hợp lệ cho subjectMetric', () => {
    for (const m of ['impression_ctr', 'thumbnail', 'views_d7', 'sample_size', 'data_coverage']) {
      expect(text, `prompt thiếu chỉ số "${m}"`).toContain(m)
    }
  })

  it('nêu rõ dạng id MC-001 và cảnh báo lỗi hay gặp', () => {
    expect(text).toContain('MC-001')
    expect(text).toContain('KHÔNG viết "keyFindings"')
  })
})

/**
 * Ràng buộc trong prompt phải SINH TỪ schema, không viết tay.
 *
 * Một lần thử ở lô 5 hỏng vì "Array must contain at most 12 element(s)" — trần
 * lồng nhau mà prompt chưa bao giờ nói. Viết tay danh sách này là công thức để
 * lệch; sinh từ `_def` thì schema đổi là prompt đổi theo.
 */
describe('prompt nêu đủ ràng buộc của schema', () => {
  const lines = schemaConstraintLines()
  const { text } = buildPrompt({ pkg: makePackage() })

  it('sinh được ràng buộc cho mọi nhóm trường chính', () => {
    for (const f of [
      'analysisSummary.overallAssessment',
      'keyFindings',
      'keyFindings[].evidenceIds',
      'hypotheses[].missingEvidence',
      'recommendations[].risks',
      'experiments[].stopConditions',
      'experiments[].minimumWindowDays',
      'manualReviewTargets[].reviewQuestions',
      'dataRequests[].reason',
      'explicitNonConclusions',
      'metricClaims',
      'metricClaims[].text',
    ]) {
      expect(lines.some((l) => l.includes(f)), `thiếu ràng buộc cho "${f}"`).toBe(true)
    }
  })

  it('mọi ràng buộc sinh ra đều CÓ MẶT trong prompt', () => {
    for (const l of lines) expect(text).toContain(l.trim())
  })

  it('nêu đúng mảng BẮT BUỘC không rỗng', () => {
    expect(lines.some((l) => l.includes('keyFindings: mảng 1..'))).toBe(true)
    expect(lines.some((l) => l.includes('explicitNonConclusions: mảng 1..'))).toBe(true)
    expect(lines.some((l) => l.includes('experiments[].stopConditions: mảng 1..'))).toBe(true)
  })

  it('nêu khoảng số nguyên của minimumWindowDays', () => {
    expect(lines.some((l) => /minimumWindowDays: số nguyên 1\.\.365/.test(l))).toBe(true)
  })

  it('không còn mâu thuẫn "đủ 10 trường"', () => {
    expect(text).not.toContain('đủ 10 trường')
    expect(text).toContain('ĐỦ CẢ 11 trường')
  })
})

/**
 * Bộ sinh ràng buộc phải theo kịp schema.
 *
 * Sinh tự động KHÔNG tự nó loại bỏ được lệch pha: nếu schema dùng một kiểu Zod
 * mà bộ sinh chưa biết (ví dụ `.refine()`), ràng buộc đó im lặng biến mất khỏi
 * prompt — đúng loại khoảng trống đã làm hỏng hai lô. Test này bắt ngay khi
 * schema mọc thêm kiểu mới hoặc thêm regex mới.
 */
describe('bộ sinh ràng buộc theo kịp schema', () => {
  const HANDLED = new Set([
    'ZodObject', 'ZodArray', 'ZodString', 'ZodNumber',
    'ZodDefault', 'ZodOptional', 'ZodNullable', 'ZodEnum', 'ZodBoolean', 'ZodLiteral',
  ])

  const walk = (n: any, path: string, acc: { types: Set<string>; regexes: string[] }) => {
    const d = n?._def
    if (!d) return
    acc.types.add(d.typeName)
    if (['ZodDefault', 'ZodOptional', 'ZodNullable'].includes(d.typeName)) return walk(d.innerType, path, acc)
    if (d.typeName === 'ZodObject') {
      for (const [k, v] of Object.entries(d.shape())) walk(v, path ? `${path}.${k}` : k, acc)
      return
    }
    if (d.typeName === 'ZodArray') return walk(d.type, `${path}[]`, acc)
    if (d.typeName === 'ZodString') {
      const r = (d.checks ?? []).find((c: any) => c.kind === 'regex')
      if (r) acc.regexes.push(path)
    }
  }

  it('KHÔNG có kiểu Zod nào nằm ngoài khả năng của bộ sinh', () => {
    const acc = { types: new Set<string>(), regexes: [] as string[] }
    walk(cursorOutputSchema, '', acc)
    const unhandled = [...acc.types].filter((t) => !HANDLED.has(t))
    expect(unhandled, `schema dùng kiểu bộ sinh chưa biết: ${unhandled.join(', ')}`).toHaveLength(0)
  })

  it('MỌI ràng buộc regex đều được nêu trong prompt', () => {
    const acc = { types: new Set<string>(), regexes: [] as string[] }
    walk(cursorOutputSchema, '', acc)
    const lines = schemaConstraintLines().join('\n')
    for (const p of acc.regexes) {
      expect(lines, `thiếu ràng buộc regex cho "${p}"`).toContain(p)
    }
    expect(acc.regexes.length).toBeGreaterThanOrEqual(6)
  })
})

/**
 * Hiệu chỉnh phép đo tương ứng: CHỨA ĐỰNG, có phân cực canh giữ.
 *
 * Ba lần chạy thăm dò đều báo "khớp MẬP MỜ" cho những claim TRÍCH ĐÚNG một mệnh
 * đề trong câu dài — vì Jaccard chia cho HỢP nên phạt độ dài. Quan hệ cần đo là
 * "claim có phải trích từ câu này", tức CHỨA ĐỰNG.
 */


/**
 * Một claim CHUNG CHUNG không được thoả nhiều phát biểu nhạy cảm KHÁC NHAU.
 *
 * Đây là đường lách còn lại của quy tắc độ phủ: viết một claim dài chứa từ vựng
 * của cả hai vế rồi coi như đã khai cả hai. Ngưỡng 75% được ĐÓNG BĂNG cùng lô;
 * test này giữ cho nó không bị nới sau này.
 */
