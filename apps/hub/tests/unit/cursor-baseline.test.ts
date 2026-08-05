import { describe, expect, it } from 'vitest'

import { detectSemanticDrift, isUsableBaselineClaim } from '@/lib/cursor/run'

/**
 * Quy tắc dựng MỐC NGỮ NGHĨA của runner, tách riêng để kiểm trực tiếp.
 *
 * Đây là bản sao đúng logic trong `run.ts`. Test này giữ cho quy tắc "chỉ nhận
 * mốc khi mọi claim có id hợp lệ" không bị nới lỏng mà không ai thấy.
 */
function baselineFromLooseJson(json: string): unknown[] | null {
  try {
    const loose = JSON.parse(json) as { metricClaims?: unknown }
    if (!Array.isArray(loose.metricClaims)) return null
    return loose.metricClaims.every(isUsableBaselineClaim) ? loose.metricClaims : null
  } catch {
    return null
  }
}

/** Claim đầy đủ theo nghĩa của phép so — dùng làm mẫu hợp lệ. */
const FULL = {
  id: 'MC-001',
  claimType: 'OBSERVATION',
  subjectMetric: 'views_d7',
  relatedMetric: 'NONE',
  judgement: 'HIGH',
  assertionStatus: 'ASSERTED',
  evidenceIds: ['OBS-001'],
  requiresMissingnessDisclosure: false,
  // 2.1: TRỎ tới ô gốc thay vì sao chép nội dung.
  sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'statement', ordinal: 0 },
}

/** Văn bản đã phân giải theo claim id — thứ mà drift so sánh ở 2.1. */
const textOf = (m: Record<string, string>) => new Map(Object.entries(m))

describe('mốc ngữ nghĩa từ output gốc', () => {
  it('JSON hỏng -> KHÔNG có mốc', () => {
    expect(baselineFromLooseJson('{"metricClaims":[')).toBeNull()
  })

  it('claim thiếu id -> KHÔNG có mốc (ca thật lô cấu trúc)', () => {
    const json = JSON.stringify({
      metricClaims: [
        { claimType: 'OBSERVATION', subjectMetric: 'views', text: 'lượt xem thấp' },
        { claimType: 'OBSERVATION', subjectMetric: 'retention', text: 'giữ chân thấp' },
      ],
    })
    expect(baselineFromLooseJson(json)).toBeNull()
  })

  it('id sai định dạng -> KHÔNG có mốc', () => {
    const json = JSON.stringify({ metricClaims: [{ id: 'claim-1' }] })
    expect(baselineFromLooseJson(json)).toBeNull()
  })

  it('MỘT claim thiếu id cũng đủ để loại cả mốc', () => {
    const json = JSON.stringify({ metricClaims: [{ id: 'MC-001' }, { subjectMetric: 'views' }] })
    expect(baselineFromLooseJson(json)).toBeNull()
  })

  it('claim ĐẦY ĐỦ -> CÓ mốc', () => {
    const json = JSON.stringify({ metricClaims: [FULL, { ...FULL, id: 'MC-002' }] })
    expect(baselineFromLooseJson(json)).toHaveLength(2)
  })

  it('CHỈ có id thôi -> KHÔNG có mốc (tránh TypeError ở evidenceIds)', () => {
    // Codex: {"metricClaims":[{"id":"MC-001"}]} từng được nhận làm mốc, rồi
    // `r.evidenceIds.filter(...)` ném TypeError và làm hỏng cả lần chạy.
    expect(baselineFromLooseJson(JSON.stringify({ metricClaims: [{ id: 'MC-001' }] }))).toBeNull()
  })

  it('thiếu sourceRef -> KHÔNG có mốc', () => {
    const { sourceRef, ...noRef } = FULL
    void sourceRef
    expect(baselineFromLooseJson(JSON.stringify({ metricClaims: [noRef] }))).toBeNull()
  })

  it('sourceRef thiếu field -> KHÔNG có mốc', () => {
    const bad = { ...FULL, sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', ordinal: 0 } }
    expect(baselineFromLooseJson(JSON.stringify({ metricClaims: [bad] }))).toBeNull()
  })

  it('evidenceIds không phải mảng -> KHÔNG có mốc', () => {
    expect(
      baselineFromLooseJson(JSON.stringify({ metricClaims: [{ ...FULL, evidenceIds: 'OBS-001' }] })),
    ).toBeNull()
  })

  it('phần tử null -> KHÔNG có mốc', () => {
    expect(baselineFromLooseJson(JSON.stringify({ metricClaims: [null] }))).toBeNull()
  })

  it('mốc hợp lệ KHÔNG ném lỗi khi so với bản sửa', () => {
    const root = [FULL] as never
    // Giữ nguyên con số "7" — bỏ nó đi là đổi dữ liệu, không phải diễn đạt lại.
    const repaired = [{ ...FULL }] as never
    expect(() => detectSemanticDrift(root, repaired)).not.toThrow()
    expect(detectSemanticDrift(root, repaired)).toHaveLength(0)
  })

  it('mảng claim RỖNG là mốc hợp lệ (không có claim nào để bảo toàn)', () => {
    expect(baselineFromLooseJson(JSON.stringify({ metricClaims: [] }))).toHaveLength(0)
  })

  it('thiếu hẳn metricClaims -> KHÔNG có mốc', () => {
    expect(baselineFromLooseJson(JSON.stringify({ keyFindings: [] }))).toBeNull()
  })
})

describe('số trong text là DỮ LIỆU, không phải cách diễn đạt', () => {
  const withId = (id = 'MC-001') => ({ ...FULL, id })

  it('BẮT: đổi giá trị số trong text (ca Codex)', () => {
    const d = detectSemanticDrift(
      [withId()] as never,
      [withId()] as never,
      textOf({ 'MC-001': 'views_d7 là 100' }),
      textOf({ 'MC-001': 'views_d7 là 1000' }),
    ).join(' ')
    expect(d).toContain('đổi SỐ trong text')
  })

  it('2.1 SIẾT HƠN: đổi cách viết số cũng là đụng văn xuôi gốc -> chặn', () => {
    // Ở 2.0, `text` là BẢN SAO nên viết lại số được coi là vô hại. Ở 2.1 claim
    // TRỎ tới văn xuôi thật, và một lần sửa KỸ THUẬT không có lý do gì phải
    // viết lại câu gốc. Mọi thay đổi nội dung ô đều là trôi dạt.
    const d = detectSemanticDrift(
      [withId()] as never, [withId()] as never,
      textOf({ 'MC-001': 'views_d7 là 1000' }),
      textOf({ 'MC-001': 'views_d7 đạt 1.000' }),
    ).join(' ')
    expect(d).toContain('văn bản ô nguồn đã đổi')
  })

  it('KHÔNG đụng văn xuôi -> KHÔNG trôi dạt', () => {
    const same = textOf({ 'MC-001': 'views_d7 là 1000' })
    expect(detectSemanticDrift([withId()] as never, [withId()] as never, same, same)).toHaveLength(0)
  })

  it('CHO PHÉP: viết lại câu mà không đụng số', () => {
    // Viết lại câu mà giữ nguyên số: KHÔNG phải trôi dạt về SỐ, nhưng nội dung
    // ô đã đổi -> drift bắt bằng quy tắc "văn bản ô nguồn đã đổi".
    const d = detectSemanticDrift(
      [withId()] as never, [withId()] as never,
      textOf({ 'MC-001': 'views_d7 là 100' }),
      textOf({ 'MC-001': 'Lượt xem 7 ngày đạt 100.' }),
    ).join(' ')
    expect(d).toContain('văn bản ô nguồn đã đổi')
  })

  it('BẮT: thêm một con số vốn không có', () => {
    const d = detectSemanticDrift(
      [withId()] as never, [withId()] as never,
      textOf({ 'MC-001': 'lượt xem ở mức cao' }),
      textOf({ 'MC-001': 'lượt xem ở mức cao, khoảng 900' }),
    ).join(' ')
    expect(d).toContain('đổi SỐ trong text')
  })
})

describe('enum của mốc phải thuộc tập hợp lệ', () => {
  it('claimType gõ sai -> KHÔNG có mốc', () => {
    // Codex: "OBSERVATON" là chuỗi khác rỗng nên từng được nhận làm mốc, rồi
    // lần sửa chữa đúng chính tả lại bị báo trôi dạt.
    expect(isUsableBaselineClaim({ ...FULL, claimType: 'OBSERVATON' })).toBe(false)
  })

  it('subjectMetric lạ -> KHÔNG có mốc', () => {
    expect(isUsableBaselineClaim({ ...FULL, subjectMetric: 'khong_ton_tai' })).toBe(false)
  })

  it('assertionStatus lạ -> KHÔNG có mốc', () => {
    expect(isUsableBaselineClaim({ ...FULL, assertionStatus: 'MAYBE' })).toBe(false)
  })

  it('claim hoàn toàn hợp lệ -> CÓ mốc', () => {
    expect(isUsableBaselineClaim(FULL)).toBe(true)
  })
})

/**
 * Đổi CHIỀU trong text mà giữ nguyên số.
 *
 * Codex nêu: "views_d7 ở mức cao" -> "ở mức thấp" giữ nguyên token số ["7"],
 * nên phép so trôi dạt KHÔNG bắt. Câu hỏi thực sự là: nó có lọt qua CẢ HỆ
 * THỐNG không? Kiểm bằng chính bộ kiểm định, thay vì suy luận.
 */
describe('đổi chiều trong text: ai bắt?', () => {
  it('phép so trôi dạt KHÔNG bắt (ghi nhận đúng giới hạn của nó)', () => {
    const root = [{ ...FULL, text: 'views_d7 ở mức cao' }] as never
    const repaired = [{ ...FULL, text: 'views_d7 ở mức thấp' }] as never
    expect(detectSemanticDrift(root, repaired)).toHaveLength(0)
  })

  it('nhưng BỘ KIỂM ĐỊNH bắt: judgement HIGH mâu thuẫn với "thấp"', async () => {
    const { validateCursorOutput } = await import('@/lib/cursor/validate')
    const { buildPrompt } = await import('@/lib/cursor/prompt')
    const mod = await import('./cursor-validate.test')
    void mod
    // Dựng gói tối thiểu ngay tại đây để test độc lập.
    const pkg: any = {
      schemaVersion: '1.0.0',
      algorithmVersion: '1.0.0',
      scope: {
        workspaceId: 'w', channelId: 'c', channelLabel: 'x', channelTitle: 't',
        reportingTimezone: 'UTC', windowStart: '2026-06-01', windowEnd: '2026-07-27',
        analysisRunId: 'r', inputHash: 'a'.repeat(64),
      },
      channelSummary: { videos: 20 },
      dataCoverage: {
        videosTotal: 20, videosWithMetrics: 18, videosImmature: 2, metricRows: 180,
        expectedDates: 57, observedDates: 57, missingDates: [],
        metricCoverage: { views: 1, impressions: 0 }, revisedRows: 0,
      },
      confidence: { score: 0.8, band: 'HIGH', drivers: {} },
      baselines: [], featureDefinitions: [],
      observations: [{
        kind: 'TOP_PERFORMER', polarity: 'POSITIVE',
        statement: 'views_d7 của nhóm này ở mức cao', metricValues: { views_d7: 900 },
        baselineKind: 'CHANNEL_FORMAT', confidence: 0.8, limitations: [],
        evidenceRefs: [], isHypothesis: false,
      }],
      anomalies: [], rankedVideos: [], cohortComparisons: [], formatComparison: null,
      hypothesisCandidates: [], unresolvedQuestions: [], missingData: [], analysisTasks: [],
      limitsApplied: {
        positiveObservations: { included: 1, total: 1 }, negativeObservations: { included: 0, total: 0 },
        anomalies: { included: 0, total: 0 }, rankedVideos: { included: 0, total: 0 },
        cohorts: { included: 0, total: 0 }, hypotheses: { included: 0, total: 0 },
        truncatedForSize: false,
      },
    }
    const built = buildPrompt({ pkg })
    const out = {
      schemaVersion: '2.1',
      analysisSummary: {
        overallAssessment: 'Kênh có một nhóm video vượt trội rõ rệt trong cửa sổ xét.',
        confidence: 'MEDIUM',
        confidenceRationale: 'Độ phủ chỉ số cốt lõi đầy đủ trong kỳ được xét.',
        primaryConstraint: 'Thiếu dữ liệu tiếp cận nên chưa đủ cơ sở kết luận.',
      },
      keyFindings: [{
        id: 'F-001', statement: 'Nhóm video dẫn đầu về lượt xem 7 ngày.',
        findingType: 'OBSERVATION', confidence: 'HIGH', evidenceIds: ['OBS-001'],
        supportingReasoning: 'Quan sát tất định ghi nhận phân vị cao trong nhóm.',
        contradictingEvidenceIds: [], limitations: ['views_d7 ở mức thấp'],
      }],
      hypotheses: [], recommendations: [], experiments: [],
      manualReviewTargets: [], dataRequests: [],
      explicitNonConclusions: ['Không kết luận về khâu tiếp cận.'],
      // Claim TRỎ vào limitations[0] của F-001, nơi chứa câu "views_d7 ở mức thấp".
      metricClaims: [
        { ...FULL, sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 } },
      ],
      selfCheck: {
        usedOnlyProvidedEvidence: true, recomputedMetrics: false, madeCausalClaims: false,
        madeCtrOrImpressionClaims: false, allFindingEvidenceResolved: true,
      },
    }
    const r = validateCursorOutput({
      raw: JSON.stringify(out), pkg,
      allowedEvidenceIds: built.allowedEvidenceIds,
      allowedVideoIds: built.allowedVideoIds,
      allowedCohortKeys: built.allowedCohortKeys,
      hadProseOutsideJson: false,
    })
    // In ra để chẩn đoán nếu quy tắc không kích hoạt như mong đợi.
    const rules = r.report.claimIssues.map((i) => i.rule).join(', ')
    expect(r.report.claimIssues.some((i) => i.rule === 'judgement_contradicts_text'), rules).toBe(true)
    expect(r.report.passed).toBe(false)
  })
})

/**
 * Root VƯỢT TRẦN mảng không được dùng làm mốc.
 *
 * Ca thật (lần chạy thăm dò hinh_su): root có 32 claim, trần lúc đó là 30. Cách
 * sửa duy nhất khả dĩ là xoá bớt, nhưng quy tắc bất biến ngữ nghĩa cấm xoá —
 * bế tắc, và bị báo sai thành "đổi ngữ nghĩa". Hai thay đổi cùng đóng lỗ này:
 * trần được nâng lên đúng bản chất (số claim do nội dung quyết định), và root
 * vượt trần thì không còn được nhận làm mốc.
 */
describe('root vượt trần mảng', () => {
  it('trần metricClaims đủ rộng cho output thật', async () => {
    const { OUTPUT_LIMITS } = await import('@/lib/cursor/schema')
    // Lần chạy thật sinh 32 claim; trần phải rộng hơn nhiều lần con số đó.
    expect(OUTPUT_LIMITS.metricClaims).toBeGreaterThanOrEqual(100)
  })

  it('xoá bớt claim VẪN là trôi dạt (quy tắc không bị nới)', () => {
    const root = [FULL, { ...FULL, id: 'MC-002' }] as never
    const trimmed = [FULL] as never
    expect(detectSemanticDrift(root, trimmed).join(' ')).toContain('bỏ mất claim MC-002')
  })
})
