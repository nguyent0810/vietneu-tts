import { describe, expect, it } from 'vitest'

import { cursorOutputSchema, CURSOR_OUTPUT_SCHEMA_VERSION } from '@/lib/cursor/schema'

/**
 * TEST ĐẶC TẢ — khoá lại mọi ràng buộc đã KHÔI PHỤC bằng tay.
 *
 * Bảy schema mục (`keyFindingSchema` … `selfCheckSchema`) từng bị một lệnh thay
 * chuỗi xoá nhầm, và không khôi phục được từ git vì Phase 4 chưa commit. Chúng
 * được dựng lại bằng tay rồi đối chiếu 26/26 với bản ghi độc lập của Codex
 * (vòng rà soát tương ứng prompt↔schema, có TRƯỚC sự cố).
 *
 * Tệp này biến bản đối chiếu đó thành ràng buộc chạy được: mọi sai lệch về sau
 * — dù do refactor hay do khôi phục sai — đều làm test đỏ thay vì âm thầm đổi
 * điều mà validator cưỡng chế.
 *
 * KHÔNG sửa các con số ở đây để test xanh. Chúng LÀ đặc tả.
 */

/** Payload tối thiểu hợp lệ; các test dưới đây biến đổi từ nó. */
function minimal(): Record<string, unknown> {
  return {
    schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'a'.repeat(30),
      confidence: 'MEDIUM',
      confidenceRationale: 'b'.repeat(20),
      primaryConstraint: 'c'.repeat(10),
    },
    keyFindings: [
      {
        id: 'F-001',
        statement: 'd'.repeat(20),
        findingType: 'OBSERVATION',
        confidence: 'HIGH',
        evidenceIds: ['OBS-001'],
        supportingReasoning: 'e'.repeat(20),
      },
    ],
    hypotheses: [],
    recommendations: [],
    experiments: [],
    manualReviewTargets: [],
    dataRequests: [],
    explicitNonConclusions: ['không kết luận về tiếp cận'],
    metricClaims: [],
    selfCheck: {
      usedOnlyProvidedEvidence: true,
      recomputedMetrics: false,
      madeCausalClaims: false,
      madeCtrOrImpressionClaims: false,
      allFindingEvidenceResolved: true,
    },
  }
}

const parse = (o: unknown) => cursorOutputSchema.safeParse(o)

describe('đặc tả: ràng buộc ĐỘ DÀI chuỗi (đối chiếu 26/26 với bản ghi Codex)', () => {
  /** [đường dẫn, min, max, cách đặt giá trị] */
  const CASES: Array<[string, number, number, (v: string) => Record<string, unknown>]> = [
    ['analysisSummary.overallAssessment', 20, 2000, (v) => {
      const o = minimal(); (o.analysisSummary as any).overallAssessment = v; return o }],
    ['analysisSummary.confidenceRationale', 10, 1000, (v) => {
      const o = minimal(); (o.analysisSummary as any).confidenceRationale = v; return o }],
    ['analysisSummary.primaryConstraint', 5, 600, (v) => {
      const o = minimal(); (o.analysisSummary as any).primaryConstraint = v; return o }],
    ['keyFindings[].statement', 10, 600, (v) => {
      const o = minimal(); (o.keyFindings as any[])[0].statement = v; return o }],
    ['keyFindings[].supportingReasoning', 10, 1200, (v) => {
      const o = minimal(); (o.keyFindings as any[])[0].supportingReasoning = v; return o }],
  ]

  for (const [name, min, max, build] of CASES) {
    it(`${name}: ${min}..${max}`, () => {
      if (min > 1) expect(parse(build('x'.repeat(min - 1))).success, `dưới ${min} phải bị từ chối`).toBe(false)
      expect(parse(build('x'.repeat(min))).success, `đúng ${min} phải được chấp nhận`).toBe(true)
      expect(parse(build('x'.repeat(max))).success, `đúng ${max} phải được chấp nhận`).toBe(true)
      expect(parse(build('x'.repeat(max + 1))).success, `trên ${max} phải bị từ chối`).toBe(false)
    })
  }
})

describe('đặc tả: ràng buộc phần tử MẢNG', () => {
  it('keyFindings: 1..10 phần tử', () => {
    const o = minimal()
    o.keyFindings = []
    expect(parse(o).success, 'mảng rỗng phải bị từ chối').toBe(false)
    const one = (minimal().keyFindings as any[])[0]
    o.keyFindings = Array.from({ length: 10 }, (_, i) => ({ ...one, id: `F-${String(i + 1).padStart(3, '0')}` }))
    expect(parse(o).success, '10 phần tử phải được chấp nhận').toBe(true)
    o.keyFindings = Array.from({ length: 11 }, (_, i) => ({ ...one, id: `F-${String(i + 1).padStart(3, '0')}` }))
    expect(parse(o).success, '11 phần tử phải bị từ chối').toBe(false)
  })

  it('explicitNonConclusions: 1..10, mỗi phần tử <=500', () => {
    const o = minimal()
    o.explicitNonConclusions = []
    expect(parse(o).success).toBe(false)
    o.explicitNonConclusions = ['x'.repeat(500)]
    expect(parse(o).success).toBe(true)
    o.explicitNonConclusions = ['x'.repeat(501)]
    expect(parse(o).success).toBe(false)
  })

  it('keyFindings[].evidenceIds <=12, limitations <=6', () => {
    const o = minimal()
    ;(o.keyFindings as any[])[0].evidenceIds = Array.from({ length: 12 }, () => 'OBS-001')
    expect(parse(o).success).toBe(true)
    ;(o.keyFindings as any[])[0].evidenceIds = Array.from({ length: 13 }, () => 'OBS-001')
    expect(parse(o).success).toBe(false)

    const o2 = minimal()
    ;(o2.keyFindings as any[])[0].limitations = Array.from({ length: 6 }, () => 'x')
    expect(parse(o2).success).toBe(true)
    ;(o2.keyFindings as any[])[0].limitations = Array.from({ length: 7 }, () => 'x')
    expect(parse(o2).success).toBe(false)
  })

  it('metricClaims <=120 (trần do NỘI DUNG quyết định, không phải ép ưu tiên)', async () => {
    const { OUTPUT_LIMITS } = await import('@/lib/cursor/schema')
    expect(OUTPUT_LIMITS.metricClaims).toBe(120)
  })
})

describe('đặc tả: GIÁ TRỊ MẶC ĐỊNH — kiểm bằng HÀNH VI, không đọc mã', () => {
  it('keyFindings[]: contradictingEvidenceIds và limitations mặc định []', () => {
    const p = parse(minimal())
    expect(p.success).toBe(true)
    if (!p.success) return
    const f = p.data.keyFindings[0]!
    expect(f.contradictingEvidenceIds).toEqual([])
    expect(f.limitations).toEqual([])
  })

  it('hypotheses[]: contradictingEvidenceIds mặc định []', () => {
    const o = minimal()
    o.hypotheses = [{
      id: 'H-001', statement: 'x'.repeat(20), status: 'UNVERIFIED', confidence: 'LOW',
      supportingEvidenceIds: ['OBS-001'], missingEvidence: [], validationMethod: 'y'.repeat(20),
    }]
    const p = parse(o)
    expect(p.success).toBe(true)
    if (p.success) expect(p.data.hypotheses[0]!.contradictingEvidenceIds).toEqual([])
  })

  it('recommendations[]: risks mặc định []', () => {
    const o = minimal()
    o.recommendations = [{
      id: 'R-001', action: 'x'.repeat(20), priority: 'P1', category: 'CONTINUE',
      rationale: 'y'.repeat(20), evidenceIds: ['OBS-001'], expectedValue: 'MEDIUM',
      effort: 'LOW', reversibility: 'HIGH', measurementFeasibility: 'HIGH',
      successMetric: 'views_d7 không giảm',
    }]
    const p = parse(o)
    expect(p.success).toBe(true)
    if (p.success) expect(p.data.recommendations[0]!.risks).toEqual([])
  })

  it('experiments[]: sampleLimitations mặc định []', () => {
    const o = minimal()
    o.hypotheses = [{
      id: 'H-001', statement: 'x'.repeat(20), status: 'UNVERIFIED', confidence: 'LOW',
      supportingEvidenceIds: ['OBS-001'], missingEvidence: [], validationMethod: 'y'.repeat(20),
    }]
    o.experiments = [{
      id: 'E-001', hypothesisId: 'H-001', change: 'x'.repeat(20), baseline: 'mốc hiện tại',
      successMetrics: ['views_d7 tăng'], minimumWindowDays: 14,
      stopConditions: ['dừng nếu giảm nửa'], interpretationRisks: ['có thể trùng mùa vụ'],
    }]
    const p = parse(o)
    expect(p.success).toBe(true)
    if (p.success) expect(p.data.experiments[0]!.sampleLimitations).toEqual([])
  })

  it('manualReviewTargets[]: evidenceIds mặc định []', () => {
    const o = minimal()
    o.manualReviewTargets = [{
      targetType: 'VIDEO', targetId: 'aaaaaaaaaaa', reason: 'cần rà soát',
      reviewQuestions: ['xem lại?'],
    }]
    const p = parse(o)
    expect(p.success).toBe(true)
    if (p.success) expect(p.data.manualReviewTargets[0]!.evidenceIds).toEqual([])
  })

  it('metricClaims[]: relatedMetric/evidenceIds/requiresMissingnessDisclosure có mặc định', () => {
    const o = minimal()
    o.metricClaims = [{
      id: 'MC-001', claimType: 'METHODOLOGY_LIMITATION', subjectMetric: 'views',
      judgement: 'LOW', assertionStatus: 'LIMITATION',
      sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'statement' },
    }]
    const p = parse(o)
    expect(p.success, JSON.stringify(p.success ? '' : p.error.issues.slice(0, 3))).toBe(true)
    if (!p.success) return
    const mc = p.data.metricClaims[0]!
    expect(mc.relatedMetric).toBe('NONE')
    expect(mc.evidenceIds).toEqual([])
    expect(mc.requiresMissingnessDisclosure).toBe(false)
    expect(mc.sourceRef.ordinal).toBe(0)
  })
})

describe('đặc tả: hypotheses[].status là LITERAL "UNVERIFIED"', () => {
  const mk = (status: unknown) => {
    const o = minimal()
    o.hypotheses = [{
      id: 'H-001', statement: 'x'.repeat(20), status, confidence: 'LOW',
      supportingEvidenceIds: ['OBS-001'], missingEvidence: [], validationMethod: 'y'.repeat(20),
    }]
    return parse(o)
  }

  it('chấp nhận đúng "UNVERIFIED"', () => {
    expect(mk('UNVERIFIED').success).toBe(true)
  })

  it('từ chối mọi giá trị khác — kể cả khác hoa thường', () => {
    // Cho phép "VERIFIED" sẽ mở đường cho mô hình tự phong là đã chứng minh.
    for (const bad of ['VERIFIED', 'CONFIRMED', 'unverified', 'Unverified', '', null, true]) {
      expect(mk(bad).success, `giá trị ${JSON.stringify(bad)} lẽ ra phải bị từ chối`).toBe(false)
    }
  })
})

describe('đặc tả: mẫu ID và khoảng số', () => {
  it('id phải đúng ba chữ số theo tiền tố', () => {
    const o = minimal()
    for (const bad of ['F-1', 'F-0001', 'f-001', 'X-001', 'F001', '']) {
      ;(o.keyFindings as any[])[0].id = bad
      expect(parse(o).success, `id "${bad}" lẽ ra phải bị từ chối`).toBe(false)
    }
    ;(o.keyFindings as any[])[0].id = 'F-001'
    expect(parse(o).success).toBe(true)
  })

  it('experiments[].minimumWindowDays: số nguyên 1..365', () => {
    const build = (v: unknown) => {
      const o = minimal()
      o.hypotheses = [{
        id: 'H-001', statement: 'x'.repeat(20), status: 'UNVERIFIED', confidence: 'LOW',
        supportingEvidenceIds: ['OBS-001'], missingEvidence: [], validationMethod: 'y'.repeat(20),
      }]
      o.experiments = [{
        id: 'E-001', hypothesisId: 'H-001', change: 'x'.repeat(20), baseline: 'mốc',
        successMetrics: ['m'], minimumWindowDays: v,
        stopConditions: ['s'], interpretationRisks: ['r'],
      }]
      return parse(o)
    }
    expect(build(1).success).toBe(true)
    expect(build(365).success).toBe(true)
    expect(build(0).success).toBe(false)
    expect(build(366).success).toBe(false)
    expect(build(1.5).success).toBe(false)
    expect(build(-1).success).toBe(false)
  })
})

describe('đặc tả: .strict() — trường lạ bị từ chối ở MỌI tầng', () => {
  it('cấp cao nhất', () => {
    const o = minimal()
    ;(o as any).truongLa = 1
    expect(parse(o).success).toBe(false)
  })

  it('trong keyFindings', () => {
    const o = minimal()
    ;(o.keyFindings as any[])[0].truongLa = 1
    expect(parse(o).success).toBe(false)
  })

  it('trong sourceRef', () => {
    const o = minimal()
    o.metricClaims = [{
      id: 'MC-001', claimType: 'OBSERVATION', subjectMetric: 'views',
      judgement: 'LOW', assertionStatus: 'ASSERTED',
      sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'statement', truongLa: 1 },
    }]
    expect(parse(o).success).toBe(false)
  })
})
