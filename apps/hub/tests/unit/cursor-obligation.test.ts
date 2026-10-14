import { describe, expect, it } from 'vitest'

import {
  buildObligationSet,
  checkDeclarationIdentity,
  checkObligationBelongsTo,
  checkObligationSetHash,
  checkObligationSourcesIntact,
  composeMetricClaims,
  hashAnalysisPayload,
  hashObligationSet,
  hashText,
} from '@/lib/cursor/obligation'
import {
  ANALYSIS_SCHEMA_VERSION,
  claimObligationSetSchema,
  cursorAnalysisSchema,
  OBLIGATION_GENERATOR_VERSION,
  type CursorAnalysis,
} from '@/lib/cursor/schema'
import { enumerateUnits } from '@/lib/cursor/source-ref'

/**
 * NHÓM O — bộ sinh nghĩa vụ (cổng G2 của kế hoạch triển khai).
 *
 * Đây là tầng thay cho toàn bộ nhóm R và ba trên bốn quy tắc nhóm U của 2.1.
 * Bảo đảm không tự nhiên có: nó CHUYỂN từ "mô hình phải làm đúng" sang "ứng dụng
 * không cho phép làm sai", nên mỗi bất biến phải có test riêng ở đây.
 *
 * Xem creator_specs/PHASE4_1_DECLARATION_PASS_DESIGN.md mục 1.2 (O-INV-1..4).
 */

function analysis(over: Partial<CursorAnalysis> = {}): CursorAnalysis {
  return {
    schemaVersion: ANALYSIS_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
      confidence: 'MEDIUM',
      confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ trong cửa sổ quan sát này.',
      primaryConstraint: 'Cỡ mẫu còn nhỏ nên kết luận xu hướng cần thận trọng.',
    },
    keyFindings: [
      {
        id: 'F-001',
        statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
        findingType: 'OBSERVATION',
        confidence: 'MEDIUM',
        evidenceIds: ['OBS-001'],
        supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
        contradictingEvidenceIds: [],
        limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu'],
      },
    ],
    hypotheses: [],
    recommendations: [],
    experiments: [],
    manualReviewTargets: [],
    dataRequests: [],
    explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
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

describe('O1 — tập nghĩa vụ = ĐÚNG tập ô nhắc chỉ số nhạy cảm', () => {
  it('mốc: một ô nhạy cảm -> đúng một nghĩa vụ', () => {
    const set = buildObligationSet(analysis())
    expect(set.obligations).toHaveLength(1)
    expect(set.obligations[0]!.canonical).toBe('KEY_FINDING|F-001|limitations#0')
    expect(set.obligations[0]!.resolvedText).toBe('cỡ mẫu lượt xem thấp nên CTR nhiễu')
    expect(set.obligations[0]!.mentionedMetrics).toEqual(['impression_ctr'])
  })

  it('ô KHÔNG nhạy cảm không sinh nghĩa vụ', () => {
    const set = buildObligationSet(
      analysis({
        keyFindings: [
          { ...analysis().keyFindings[0]!, limitations: ['cỡ mẫu còn nhỏ trong cửa sổ này'] },
        ],
      }),
    )
    expect(set.obligations).toHaveLength(0)
  })

  it('tập nghĩa vụ khớp CHÍNH XÁC tập ô nhạy cảm của bộ liệt kê', () => {
    // Đối chiếu độc lập: đếm lại bằng `enumerateUnits` thay vì tin bộ sinh.
    const out = analysis({
      keyFindings: [
        {
          ...analysis().keyFindings[0]!,
          statement: 'Nhóm dẫn đầu về lượt xem, chưa đọc được impressions trong kỳ.',
          limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'],
        },
      ],
      explicitNonConclusions: ['Không kết luận hiệu quả thumbnail.'],
    })
    const set = buildObligationSet(out)
    const expected = enumerateUnits(out).filter((u) =>
      /impressions?|\bctr\b|thumbnail|packaging/iu.test(u.text),
    )
    expect(set.obligations.map((o) => o.canonical)).toEqual(expected.map((u) => u.canonical))
  })

  it('id cấp TUẦN TỰ theo thứ tự liệt kê', () => {
    const set = buildObligationSet(
      analysis({
        keyFindings: [
          {
            ...analysis().keyFindings[0]!,
            limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'],
          },
        ],
        explicitNonConclusions: ['Không kết luận hiệu quả thumbnail.'],
      }),
    )
    expect(set.obligations.map((o) => o.id)).toEqual(['MC-001', 'MC-002', 'MC-003'])
  })

  it('tập nghĩa vụ hợp lệ theo schema của chính nó', () => {
    expect(claimObligationSetSchema.safeParse(buildObligationSet(analysis())).success).toBe(true)
  })
})

describe('O2 — TẤT ĐỊNH', () => {
  it('cùng payload -> cùng băm, 100 lần', () => {
    const out = analysis()
    const first = hashObligationSet(buildObligationSet(out))
    for (let i = 0; i < 100; i++) {
      expect(hashObligationSet(buildObligationSet(out))).toBe(first)
    }
  })

  it('băm KHÔNG phụ thuộc thứ tự khoá của payload', () => {
    // Payload đi qua JSONB sẽ quay về với thứ tự khoá khác (jsonb sắp lại theo
    // độ dài rồi theo byte). Nếu băm nhạy thứ tự khoá thì mọi lần đọc lại từ
    // database đều báo trôi dạt giả.
    //
    // ĐẢO khoá thật sự, đệ quy. KHÔNG dùng tham số replacer của `JSON.stringify`:
    // nó là danh sách CHO PHÉP chứ không phải thứ tự, nên nó lọc mất khoá lồng
    // và tạo ra một object KHÁC — phép kiểm khi ấy đo nhầm thứ.
    const reverseKeys = (v: unknown): unknown => {
      if (Array.isArray(v)) return v.map(reverseKeys)
      if (v !== null && typeof v === 'object') {
        return Object.fromEntries(
          Object.entries(v as Record<string, unknown>)
            .reverse()
            .map(([k, x]) => [k, reverseKeys(x)]),
        )
      }
      return v
    }
    const a = analysis()
    const reordered = reverseKeys(a) as CursorAnalysis
    expect(Object.keys(reordered)).not.toEqual(Object.keys(a))
    expect(hashAnalysisPayload(reordered)).toBe(hashAnalysisPayload(a))
  })

  it('đổi MỘT ký tự của văn xuôi thì băm đổi', () => {
    const a = analysis()
    const b = analysis({
      keyFindings: [{ ...a.keyFindings[0]!, limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu.'] }],
    })
    expect(hashAnalysisPayload(b)).not.toBe(hashAnalysisPayload(a))
  })

  it('băm văn bản bỏ qua khoảng trắng thừa, KHÔNG bỏ qua chữ hoa', () => {
    expect(hashText('CTR  nhiễu')).toBe(hashText('CTR nhiễu'))
    expect(hashText('ctr nhiễu')).not.toBe(hashText('CTR nhiễu'))
  })

  it('resolvedHash bằng đúng băm của resolvedText', () => {
    for (const ob of buildObligationSet(analysis()).obligations) {
      expect(ob.resolvedHash).toBe(hashText(ob.resolvedText))
    }
  })
})

describe('O3 — ĐẢO THỨ TỰ mảng đổi ref nhưng KHÔNG đổi nội dung', () => {
  it('đảo keyFindings: tập văn bản giữ nguyên, băm tập ĐỔI (và đó là đúng)', () => {
    const F2 = {
      ...analysis().keyFindings[0]!,
      id: 'F-002' as const,
      statement: 'Một phát hiện thứ hai, trung tính, về nhịp đăng của kênh.',
      limitations: ['chưa bật đo impressions'],
    }
    const a = analysis({ keyFindings: [analysis().keyFindings[0]!, F2] })
    const b = analysis({ keyFindings: [F2, analysis().keyFindings[0]!] })

    const textsA = buildObligationSet(a).obligations.map((o) => o.resolvedText).sort()
    const textsB = buildObligationSet(b).obligations.map((o) => o.resolvedText).sort()
    expect(textsB).toEqual(textsA)

    // Băm ĐỔI vì thứ tự `id` đổi theo thứ tự liệt kê. Đúng: hai bản phân tích
    // khác nhau về hình thức là hai bản khác nhau, và mỗi bản có tập nghĩa vụ
    // riêng. Tập nghĩa vụ KHÔNG được dùng chéo giữa hai bản.
    expect(hashObligationSet(buildObligationSet(b))).not.toBe(
      hashObligationSet(buildObligationSet(a)),
    )
  })
})

describe('O4 — ô NHÃN: ASSERTED bị loại khỏi tập trạng thái hợp lệ', () => {
  const withRequest = () =>
    analysis({
      dataRequests: [
        {
          metricOrArtifact: 'impressions cấp video',
          reason: 'Cần để tách khâu tiếp cận khỏi khâu giữ chân.',
          decisionUnlocked: 'Biết nên ưu tiên sửa gì trước.',
        },
      ],
    })

  it('metricOrArtifact -> CONDITIONAL | LIMITATION, không có ASSERTED', () => {
    const ob = buildObligationSet(withRequest()).obligations.find((o) =>
      o.canonical.startsWith('DATA_REQUEST'),
    )!
    expect(ob.allowedAssertionStatuses).toEqual(['CONDITIONAL', 'LIMITATION'])
    expect(ob.allowedAssertionStatuses).not.toContain('ASSERTED')
  })

  it('ô văn xuôi thường giữ ĐỦ năm trạng thái', () => {
    const ob = buildObligationSet(analysis()).obligations[0]!
    expect(ob.allowedAssertionStatuses).toHaveLength(5)
    expect(ob.allowedAssertionStatuses).toContain('ASSERTED')
  })
})

describe('O-INV-1 — tập nghĩa vụ thuộc ĐÚNG bản phân tích', () => {
  it('cùng bản phân tích -> ok', () => {
    const a = analysis()
    expect(checkObligationBelongsTo(buildObligationSet(a), a).ok).toBe(true)
  })

  it('bản phân tích KHÁC -> obligation_analysis_mismatch', () => {
    const a = analysis()
    const b = analysis({ explicitNonConclusions: ['Một câu hoàn toàn khác.'] })
    const r = checkObligationBelongsTo(buildObligationSet(a), b)
    expect(r.ok).toBe(false)
    expect(r.ok === false && r.rule).toBe('obligation_analysis_mismatch')
  })
})

describe('O-INV-2 — sourceRef và băm khớp bản phân tích đóng băng', () => {
  it('bản không đổi -> không lỗi', () => {
    const a = analysis()
    expect(checkObligationSourcesIntact(buildObligationSet(a), a)).toEqual([])
  })

  it('VĂN BẢN ô bị đổi sau khi sinh nghĩa vụ -> obligation_source_drift', () => {
    const a = analysis()
    const set = buildObligationSet(a)
    const tampered = analysis({
      keyFindings: [
        { ...a.keyFindings[0]!, limitations: ['cỡ mẫu lượt xem RẤT thấp nên CTR nhiễu'] },
      ],
    })
    const issues = checkObligationSourcesIntact(set, tampered)
    expect(issues.map((i) => i.ok === false && i.rule)).toContain('obligation_source_drift')
  })

  it('ô được trỏ bị XOÁ -> obligation_source_unresolved', () => {
    const a = analysis()
    const set = buildObligationSet(a)
    const tampered = analysis({ keyFindings: [{ ...a.keyFindings[0]!, limitations: [] }] })
    const issues = checkObligationSourcesIntact(set, tampered)
    expect(issues.map((i) => i.ok === false && i.rule)).toContain('obligation_source_unresolved')
  })

  it('đổi SỐ trong ô cũng bị bắt', () => {
    const a = analysis({
      keyFindings: [{ ...analysis().keyFindings[0]!, limitations: ['CTR cần đạt 2% mới đọc được'] }],
    })
    const set = buildObligationSet(a)
    const tampered = analysis({
      keyFindings: [{ ...analysis().keyFindings[0]!, limitations: ['CTR cần đạt 9% mới đọc được'] }],
    })
    expect(checkObligationSourcesIntact(set, tampered).length).toBeGreaterThan(0)
  })
})

describe('O-INV-3 — danh tính khai báo', () => {
  const set = buildObligationSet(
    analysis({
      keyFindings: [
        {
          ...analysis().keyFindings[0]!,
          limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'],
        },
      ],
    }),
  )

  it('đủ và đúng -> không lỗi', () => {
    expect(checkDeclarationIdentity(set, ['MC-001', 'MC-002'])).toEqual([])
  })

  it('ĐẢO THỨ TỰ không phải lỗi', () => {
    expect(checkDeclarationIdentity(set, ['MC-002', 'MC-001'])).toEqual([])
  })

  it('THIẾU -> declaration_missing_obligation', () => {
    const r = checkDeclarationIdentity(set, ['MC-001'])
    expect(r.map((i) => i.ok === false && i.rule)).toContain('declaration_missing_obligation')
  })

  it('THỪA -> declaration_unknown_obligation', () => {
    const r = checkDeclarationIdentity(set, ['MC-001', 'MC-002', 'MC-009'])
    expect(r.map((i) => i.ok === false && i.rule)).toContain('declaration_unknown_obligation')
  })

  it('TRÙNG -> declaration_duplicate', () => {
    const r = checkDeclarationIdentity(set, ['MC-001', 'MC-001', 'MC-002'])
    expect(r.map((i) => i.ok === false && i.rule)).toContain('declaration_duplicate')
  })

  it('lệch SỐ LƯỢNG -> declaration_count_mismatch', () => {
    const r = checkDeclarationIdentity(set, ['MC-001'])
    expect(r.map((i) => i.ok === false && i.rule)).toContain('declaration_count_mismatch')
  })
})

describe('O-INV-4 — băm tập nghĩa vụ', () => {
  it('khớp -> ok', () => {
    expect(checkObligationSetHash('a'.repeat(64), 'a'.repeat(64)).ok).toBe(true)
  })
  it('lệch -> obligation_set_drift', () => {
    const r = checkObligationSetHash('a'.repeat(64), 'b'.repeat(64))
    expect(r.ok === false && r.rule).toBe('obligation_set_drift')
  })
})

describe('GHÉP — sourceRef luôn lấy từ NGHĨA VỤ', () => {
  it('khai báo KHÔNG thể đổi mục tiêu của claim', () => {
    const set = buildObligationSet(analysis())
    // Khai báo cố tình kèm một `sourceRef` khác. Bộ ghép phải bỏ qua nó hoàn
    // toàn — đây là hàng rào cuối của điều 4 ("không đổi mục tiêu"), sau
    // `.strict()` của schema lượt 2.
    const claims = composeMetricClaims(set, [
      {
        id: 'MC-001',
        claimType: 'METHODOLOGY_LIMITATION',
        subjectMetric: 'views',
        relatedMetric: 'impression_ctr',
        judgement: 'LOW',
        assertionStatus: 'LIMITATION',
        evidenceIds: [],
        requiresMissingnessDisclosure: false,
        sourceRef: { section: 'RECOMMENDATION', itemId: 'R-999', field: 'action', ordinal: 0 },
      },
    ])
    expect(claims[0]!.sourceRef).toEqual(set.obligations[0]!.sourceRef)
  })

  it('ghép theo id, không theo vị trí', () => {
    const set = buildObligationSet(
      analysis({
        keyFindings: [
          {
            ...analysis().keyFindings[0]!,
            limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'],
          },
        ],
      }),
    )
    const mk = (id: string, subject: string) => ({
      id,
      claimType: 'METHODOLOGY_LIMITATION',
      subjectMetric: subject,
      relatedMetric: 'NONE',
      judgement: 'UNKNOWN',
      assertionStatus: 'LIMITATION',
      evidenceIds: [],
      requiresMissingnessDisclosure: false,
    })
    const claims = composeMetricClaims(set, [mk('MC-002', 'impressions'), mk('MC-001', 'views')])
    expect(claims.map((c) => [c.id, c.subjectMetric])).toEqual([
      ['MC-001', 'views'],
      ['MC-002', 'impressions'],
    ])
  })
})

describe('lượt 1 KHÔNG được mang metricClaims', () => {
  it('.strict() từ chối payload lượt 1 có metricClaims', () => {
    const bad = { ...analysis(), metricClaims: [] }
    expect(cursorAnalysisSchema.safeParse(bad).success).toBe(false)
  })

  it('phiên bản bộ sinh có mặt trong tập nghĩa vụ', () => {
    expect(buildObligationSet(analysis()).generatorVersion).toBe(OBLIGATION_GENERATOR_VERSION)
  })
})
