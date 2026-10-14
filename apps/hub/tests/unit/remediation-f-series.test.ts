import { describe, expect, it } from 'vitest'

import type { AnalysisPackage } from '@/lib/analysis/package'
import { IDENTITY_REQUIRED_ON_SUCCESS } from '@/lib/cursor/identity'
import { buildObligationSet, hashObligationSet } from '@/lib/cursor/obligation'
import { buildPrompt } from '@/lib/cursor/prompt'
import { PROVENANCE_MATRIX } from '@/lib/cursor/provenance'
import {
  ANALYSIS_SCHEMA_VERSION,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  DECLARATION_SCHEMA_VERSION,
  type CursorAnalysis,
} from '@/lib/cursor/schema'
import { SENSITIVE_MENTION, mentionedSensitiveMetrics } from '@/lib/cursor/sensitive'
import {
  PROSE_OUTSIDE_JSON_PATH,
  scanCausalInEmittedJson,
  validateAnalysisOutput,
  validateCursorOutput,
  validateDeclarationOutput,
  validateProseOnly,
} from '@/lib/cursor/validate'

/**
 * VÒNG KHẮC PHỤC F — chứng minh bằng CHẠY, không bằng đọc mã.
 *
 * Mọi test ở đây gọi hàm THẬT và khẳng định trên GIÁ TRỊ TRẢ VỀ. Không grep, không
 * đọc mã nguồn. Lý do ghi ở mục 10 của handoff: một assertion grep của vòng trước
 * vẫn xanh sau khi dòng mã nó tưởng đang bảo vệ bị xoá.
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

/** Đầu vào chuẩn cho bộ kiểm — chỉ `raw` và cờ văn bản ngoài JSON thay đổi. */
function baseInput(raw: string, over: Record<string, unknown> = {}) {
  const pkg = makePackage()
  const built = buildPrompt({ pkg })
  return {
    raw,
    pkg,
    allowedEvidenceIds: built.allowedEvidenceIds,
    allowedVideoIds: built.allowedVideoIds,
    allowedCohortKeys: built.allowedCohortKeys,
    hadProseOutsideJson: false,
    ...over,
  }
}

/* =========================================================================
 * F1 — `repairErrors` phải KHÁC RỖNG ở CẢ BỐN `return` sớm
 * ======================================================================= */

/**
 * F1 là hồi quy do chính G-R2 gây ra: `pushRepair` ghi vào `repairSources`, nhưng
 * vòng đổ sang `repairErrors` nằm ở CUỐI hàm, sau bốn `return` sớm. Cả bốn lớp
 * thất bại ấy đều nằm trong `RETRYABLE`, nên lần thử 2–3 chạy với prompt sửa lỗi
 * KHÔNG nêu lỗi nào — đốt ngân sách thử lại vào phỏng đoán mù.
 *
 * Mỗi ca dưới đây đi qua ĐÚNG một `return` sớm, và khẳng định trên `repairErrors`
 * THẬT mà hàm trả về.
 */
describe('F1 — dòng sửa lỗi ở các return sớm', () => {
  it('INVALID_JSON: có hướng dẫn, không rỗng', () => {
    const r = validateCursorOutput(baseInput('đây không phải JSON'))
    expect(r.failureClass).toBe('INVALID_JSON')
    expect(r.repairErrors, 'return sớm INVALID_JSON trả dòng sửa lỗi RỖNG').not.toEqual([])
    expect(r.repairErrors.join(' ')).toContain('JSON')
  })

  it('UNSUPPORTED_SCHEMA_VERSION (bản CŨ): có hướng dẫn, không rỗng', () => {
    const r = validateCursorOutput(baseInput(JSON.stringify({ schemaVersion: '2.0' })))
    expect(r.failureClass).toBe('UNSUPPORTED_SCHEMA_VERSION')
    expect(r.repairErrors, 'return sớm bản CŨ trả dòng sửa lỗi RỖNG').not.toEqual([])
    expect(r.repairErrors.join(' ')).toContain(CURSOR_OUTPUT_SCHEMA_VERSION)
  })

  it('UNSUPPORTED_SCHEMA_VERSION (không rõ): có hướng dẫn, không rỗng', () => {
    const r = validateCursorOutput(baseInput(JSON.stringify({ schemaVersion: '9.9' })))
    expect(r.failureClass).toBe('UNSUPPORTED_SCHEMA_VERSION')
    expect(r.repairErrors, 'return sớm bản không rõ trả dòng sửa lỗi RỖNG').not.toEqual([])
    expect(r.repairErrors.join(' ')).toContain(CURSOR_OUTPUT_SCHEMA_VERSION)
  })

  it('MISSING_REQUIRED_FIELD: nêu ĐÚNG các trường thiếu', () => {
    const r = validateCursorOutput(
      baseInput(JSON.stringify({ schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION })),
    )
    expect(r.failureClass).toBe('MISSING_REQUIRED_FIELD')
    expect(r.repairErrors, 'return sớm schema trả dòng sửa lỗi RỖNG').not.toEqual([])
    // Không chung chung: phải trỏ tên trường thật.
    expect(r.repairErrors.join(' ')).toContain('analysisSummary')
  })

  it('lời khuyên ĐỊNH DẠNG về văn bản ngoài JSON cũng tới được prompt sửa lỗi', () => {
    // Ca hỗn hợp: vừa có văn bản ngoài JSON, vừa hỏng schema -> `return` sớm.
    // Dòng "chỉ trả về một object JSON" là `rule: null` nên phải LUÔN có mặt.
    const r = validateCursorOutput(
      baseInput(JSON.stringify({ schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION }), {
        hadProseOutsideJson: true,
      }),
    )
    expect(r.repairErrors.some((e) => e.includes('DUY NHẤT một object JSON'))).toBe(true)
  })

  it('KHÔNG trùng lặp: mỗi dòng sửa lỗi chỉ xuất hiện một lần', () => {
    /*
     * Bản trước của ca này chạy trên payload SẠCH, nên `repairErrors` rỗng và
     * assertion là `0 === 0` — một phép kiểm KHÔNG THỂ SAI. Rà soát đối kháng
     * chỉ ra đúng điều đó.
     *
     * Nay chạy trên payload CÓ vi phạm, nên danh sách khác rỗng và tính duy nhất
     * là một tính chất thật: nó bắt được cả việc đổ hai lần LẪN việc hai khối
     * `pushRepair` vô tình sinh cùng một dòng.
     */
    const r = validateCursorOutput(
      baseInput(JSON.stringify({ schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION }), {
        hadProseOutsideJson: true,
        proseText: 'CTA dày làm giảm giữ chân người xem.',
      }),
    )
    expect(r.repairErrors.length, 'ca dựng không sinh dòng sửa lỗi nào').toBeGreaterThan(1)
    expect(r.repairErrors.length).toBe(new Set(r.repairErrors).size)
  })
})

/* =========================================================================
 * F2 — quét văn bản ngoài JSON phải chạy TRƯỚC cổng schema lượt 1
 * ======================================================================= */

/**
 * F2 (fail-open, có sẵn): khi thân JSON hỏng schema lượt 1,
 * `validateAnalysisOutput` trả về từ NHÁNH RIÊNG của nó và `validateCursorOutput`
 * — nơi DUY NHẤT quét văn bản ngoài JSON — không bao giờ chạy. Một câu nhân quả
 * và một khẳng định CTR nằm ngoài JSON biến mất không dấu vết, và lớp thất bại là
 * `MISSING_REQUIRED_FIELD`, nằm TRONG `RETRYABLE`.
 *
 * Quyết định thiết kế (ghi ở đây vì test là nơi nó bị cưỡng chế): phép quét văn
 * xuôi chạy ĐỘC LẬP với cổng schema, và kết quả của nó được hợp nhất TRƯỚC khi
 * phân loại thất bại lần cuối. Lý do chọn "độc lập" chứ không phải "trước": văn
 * bản ngoài JSON và thân JSON là hai nguồn vi phạm khác nhau; một nguồn hỏng
 * không được phép làm câm nguồn kia theo BẤT KỲ chiều nào.
 */
describe('F2 — văn bản ngoài JSON không được biến mất khi thân JSON hỏng schema', () => {
  const prose = 'CTA dày làm giảm giữ chân người xem. CTR của thumbnail cũng tăng theo.'

  it('thân hỏng schema + văn xuôi có câu nhân quả -> vi phạm ĐƯỢC GHI', () => {
    const r = validateAnalysisOutput(
      baseInput(JSON.stringify({ schemaVersion: '1.0' }), {
        hadProseOutsideJson: true,
        proseText: prose,
      }),
    )
    const claims = [...r.report.claimIssues, ...r.report.structuralIssues]
    expect(
      claims.some((i) => i.rule === 'causal_claim' && i.path === PROSE_OUTSIDE_JSON_PATH),
      'câu nhân quả ngoài JSON biến mất không dấu vết',
    ).toBe(true)
    expect(r.report.causalViolations).toBeGreaterThan(0)
  })

  it('thân hỏng schema + văn xuôi có khẳng định CTR -> KHÔNG được thử lại', () => {
    const r = validateAnalysisOutput(
      baseInput(JSON.stringify({ schemaVersion: '1.0' }), {
        hadProseOutsideJson: true,
        proseText: prose,
      }),
    )
    // Thất bại NỘI DUNG thắng thất bại KỸ THUẬT: không được rơi về
    // MISSING_REQUIRED_FIELD/SCHEMA_MISMATCH (cả hai đều RETRYABLE).
    expect(r.failureClass, 'khẳng định bị cấm bị phân loại thành lỗi kỹ thuật retry được').toBe(
      'UNSUPPORTED_CLAIM',
    )
  })

  it('thân hỏng schema + văn xuôi SẠCH -> vẫn là lỗi kỹ thuật, VẪN thử lại được', () => {
    // Ranh giới ngược lại: bản sửa không được biến mọi lỗi schema thành lỗi nội
    // dung không thử lại được.
    const r = validateAnalysisOutput(
      baseInput(JSON.stringify({ schemaVersion: '1.0' }), {
        hadProseOutsideJson: true,
        proseText: 'Đã hoàn tất phân tích, xem JSON bên dưới.',
      }),
    )
    expect(['MISSING_REQUIRED_FIELD', 'SCHEMA_MISMATCH', 'PROSE_OUTSIDE_JSON']).toContain(
      r.failureClass,
    )
  })

  it('thân hỏng schema: dòng sửa lỗi nêu CẢ lỗi schema LẪN vi phạm văn xuôi', () => {
    const r = validateAnalysisOutput(
      baseInput(JSON.stringify({ schemaVersion: '1.0' }), {
        hadProseOutsideJson: true,
        proseText: prose,
      }),
    )
    const joined = r.repairErrors.join(' | ')
    expect(joined, 'mất hướng dẫn về schema').toMatch(/analysisSummary|schemaVersion/)
    expect(joined, 'mất hướng dẫn về văn bản ngoài JSON').toMatch(/ngoài (nó|JSON)/)
  })

  it('CODEX R8: câu nhân quả TRONG payload hỏng cổng schema -> KHÔNG thử lại', () => {
    /*
     * Các `return` sớm của cổng schema (bản không hỗ trợ, thiếu trường bắt buộc)
     * đều trả lớp RETRYABLE. Trước bản sửa, chúng chỉ quét văn bản NGOÀI JSON,
     * nên một câu nhân quả nằm TRONG payload biến mất mỗi khi payload hỏng
     * schema — mô hình chỉ cần kèm một lỗi schema là lời bị cấm được tha.
     */
    const r = validateCursorOutput(
      baseInput(
        JSON.stringify({
          schemaVersion: '9.9',
          analysisSummary: { overallAssessment: 'Thumbnail kém đã làm giảm lượt xem.' },
        }),
      ),
    )
    expect(r.report.causalViolations, 'câu nhân quả trong payload biến mất').toBeGreaterThan(0)
    expect(r.failureClass, 'khẳng định bị cấm rơi vào lớp thử lại được').toBe('UNSUPPORTED_CLAIM')
  })

  it('RANH GIỚI: payload hỏng schema mà SẠCH vẫn thử lại được', () => {
    const r = validateCursorOutput(baseInput(JSON.stringify({ schemaVersion: '9.9' })))
    expect(r.report.causalViolations).toBe(0)
    expect(r.failureClass).toBe('UNSUPPORTED_SCHEMA_VERSION')
  })

  it('KHÔNG đếm hai lần: payload HỢP LỆ có câu nhân quả chỉ tính MỘT', () => {
    // Đường chạy đầy đủ quét theo Ô; nếu bản quét thô cũng cộng vào thì mọi câu
    // nhân quả bị đếm đôi và mọi con số trong báo cáo sai theo.
    const a = healthyComposite()
    const findings = a.keyFindings as Array<{ statement: string }>
    findings[0]!.statement = 'CTA dày làm giảm giữ chân người xem ở nhóm Shorts của kênh này.'
    const r = validateCursorOutput(baseInput(JSON.stringify(a)))
    expect(r.report.causalViolations, 'đếm hai lần cùng một câu').toBe(1)
  })

  it('`metricClaims` tuồn vào lượt 1 vẫn bị chặn NGUYÊN VẸN', () => {
    // Bản sửa F2 không được làm mất phép chặn đặc thù của lượt 1.
    const r = validateAnalysisOutput(
      baseInput(JSON.stringify({ ...healthyAnalysis(), metricClaims: [] })),
    )
    expect(
      r.report.structuralIssues.some((i) => i.rule === 'claims_in_analysis_pass'),
      'mất phép chặn tuồn metricClaims',
    ).toBe(true)
    expect(r.repairErrors.some((e) => e.includes('metricClaims'))).toBe(true)
  })
})

/* =========================================================================
 * F7 — NHẮC TÊN khác KHẲNG ĐỊNH
 * ======================================================================= */

describe('F7 — chỉ số nhạy cảm trong văn bản ngoài JSON', () => {
  const withProse = (proseText: string) =>
    validateCursorOutput(
      baseInput(JSON.stringify(healthyComposite()), { hadProseOutsideJson: true, proseText }),
    )

  it('câu bọc VÔ HẠI chỉ nhắc tên -> vẫn chặn, nhưng ĐƯỢC thử lại', () => {
    // Mô hình đang TỰ TỪ CHỐI kết luận. Biến việc đó thành thất bại nội dung
    // vĩnh viễn là phạt nặng nhất đúng hành vi mà lớp này muốn khuyến khích.
    const r = withProse('Tôi đã tránh mọi kết luận về CTR và thumbnail.')
    expect(r.report.passed, 'văn bản ngoài JSON vẫn phải chặn').toBe(false)
    expect(
      r.report.claimIssues.some((i) => i.rule === 'prose_sensitive_mention'),
      'vi phạm phải được GHI LẠI, không im lặng bỏ qua',
    ).toBe(true)
    expect(r.report.ctrViolations, 'nhắc tên không được tính là vi phạm CTR').toBe(0)
    expect(r.failureClass, 'thất bại ĐỊNH DẠNG phải được thử lại').toBe('PROSE_OUTSIDE_JSON')
  })

  it('KHẲNG ĐỊNH thật về chỉ số nhạy cảm -> KHÔNG được thử lại', () => {
    const r = withProse('CTR của nhóm Shorts tăng 20% trong tuần vừa rồi.')
    expect(r.report.ctrViolations).toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
    const issue = r.report.claimIssues.find(
      (i) => i.rule === 'undeclared_sensitive_unit' && i.path === PROSE_OUTSIDE_JSON_PATH,
    )
    expect(issue, 'khẳng định ngoài JSON phải bị bắt').toBeDefined()
    // Phải trích ĐÚNG mệnh đề vi phạm, không phải cả đoạn.
    expect(issue!.excerpt).toContain('CTR')
  })

  it('FAIL-CLOSED: cách nói khẳng định LẠ vẫn bị chặn, không được tha', () => {
    // Đây là hướng sai an toàn của F7. Không câu nào dưới đây mang số, dấu %,
    // hay từ so sánh — một danh sách "dấu hiệu khẳng định" sẽ tha hết. Chúng vẫn
    // phải là vi phạm NỘI DUNG.
    for (const p of [
      'CTR hiện tại của kênh đang thấp và thumbnail kém hấp dẫn.',
      'CTR thấp rõ rệt ở nhóm này',
      'Thumbnail ở mức đáng lo.',
      'Packaging là điểm nghẽn.',
    ]) {
      const r = withProse(p)
      expect(r.report.ctrViolations, `tha nhầm: "${p}"`).toBeGreaterThan(0)
      expect(r.failureClass, `tha nhầm: "${p}"`).toBe('UNSUPPORTED_CLAIM')
    }
  })

  it('CODEX (HIGH): MỌI bí danh nhạy cảm + câu tự-từ-chối vẫn bị CHẶN', () => {
    /*
     * `scanProseOutsideJson` tìm mệnh đề nhạy cảm bằng `SENSITIVE_MENTION` (sinh
     * từ bảng bí danh, RỘNG) nhưng hỏi "đây có phải khẳng định không" bằng
     * `CTR_CLAIM_PATTERNS`, vốn từng mang một danh sách chủ ngữ VIẾT TAY, HẸP.
     * Mọi bí danh nằm ở phần chênh — `ảnh bìa`, `hình bìa`, `ảnh đại diện`,
     * `packaging`, `đóng gói`, `tỷ lệ click` — đều trả lời "không phải khẳng
     * định", và câu tự-từ-chối đi kèm hạ nguyên câu xuống lớp THỬ LẠI ĐƯỢC.
     *
     * Ca này đi qua TỪNG bí danh, nên một bí danh mới thêm vào `sensitive.ts`
     * mà quên nối vào bộ dò khẳng định sẽ làm đỏ ngay.
     */
    for (const subject of [
      'CTR', 'Thumbnail', 'Ảnh bìa', 'Hình bìa', 'Ảnh đại diện',
      'Packaging', 'Đóng gói', 'Tỷ lệ click', 'Impressions',
    ]) {
      const p = `${subject} hiện tại kém và tôi tránh kết luận thêm.`
      const r = withProse(p)
      expect(r.report.ctrViolations, `tha nhầm bí danh "${subject}": "${p}"`).toBeGreaterThan(0)
      expect(r.failureClass, `tha nhầm bí danh "${subject}"`).toBe('UNSUPPORTED_CLAIM')
    }
  })

  it('CODEX R2 (HIGH): khẳng định ĐỊNH LƯỢNG cũng bị CHẶN', () => {
    /*
     * "CTR hiện tại là 2%" là khẳng định đầy đủ nghĩa về CTR nhưng không mang
     * tính từ nào trong `CTR_JUDGEMENT`. Trước bản sửa, nó kèm một lời tự-từ-
     * chối là tụt xuống lớp THỬ LẠI ĐƯỢC — trong khi "CTR tăng 20%" thì không,
     * khác biệt duy nhất là chữ "tăng" tình cờ có trong danh sách.
     */
    for (const p of [
      'CTR hiện tại là 2% và tôi tránh kết luận thêm.',
      'Impressions đạt 12.000 và tôi tránh kết luận thêm.',
      'Ảnh bìa đạt 3,5 điểm và tôi tránh kết luận thêm.',
      'CTR ở mức 4 và tôi tránh kết luận thêm.',
      'Thumbnail khoảng 1.234 lượt và tôi tránh kết luận thêm.',
    ]) {
      const r = withProse(p)
      expect(r.report.ctrViolations, `tha nhầm số đo: "${p}"`).toBeGreaterThan(0)
      expect(r.failureClass, `tha nhầm số đo: "${p}"`).toBe('UNSUPPORTED_CLAIM')
    }
  })

  it('RANH GIỚI: mệnh đề CHỈ từ chối thì được tha, có thêm NỘI DUNG thì không', () => {
    /*
     * Phép thử là ĐÓNG: bỏ cụm từ chối và tên chỉ số đi, phần còn lại chỉ được
     * là hư từ. Đây là ranh giới CÓ CHỦ ĐÍCH và sai an toàn theo chiều CHẶN —
     * một lời từ chối viết kèm nội dung khác bị chặn, và đó là lớp THỬ LẠI ĐƯỢC
     * chứ không mất mát gì. Đổi lại: không cách diễn đạt khẳng định nào lọt được,
     * kể cả số viết bằng chữ.
     */
    const chỉTừChối = withProse('Không có phát biểu nào về CTR.')
    expect(chỉTừChối.report.ctrViolations).toBe(0)
    expect(chỉTừChối.failureClass).toBe('PROSE_OUTSIDE_JSON')

    const kèmNộiDung = withProse('Không kết luận gì về CTR của 3 video đầu.')
    expect(kèmNộiDung.report.ctrViolations, 'nội dung thêm cạnh chỉ số nhạy cảm phải bị chặn')
      .toBeGreaterThan(0)
  })

  it('CODEX R17: cụm tự-từ-chối KHÔNG được NUỐT chính khẳng định', () => {
    /*
     * `PROSE_SELF_DISCLAIMER` cho phép tối đa 80 ký tự giữa từ phủ định và danh
     * từ. Nếu khẳng định lọt vào khoảng ấy, nó bị xoá cùng cụm và mệnh đề trông
     * như "chỉ từ chối". Sáu biến thể KHÔNG dấu phẩy dưới đây đều từng cho
     * `ctrViolations = 0` dù chúng khẳng định `CTR thấp`.
     */
    for (const p of [
      'Không những CTR thấp mà tôi tránh kết luận',
      'Không phải CTR thấp nên tôi tránh kết luận',
      'Không thể phủ nhận CTR thấp khi đưa ra kết luận',
      'Chưa kể CTR thấp và đó là kết luận',
      'Không rõ vì sao CTR thấp trong mọi kết luận',
      'not that CTR is low in any conclusion',
    ]) {
      const r = withProse(p)
      expect(r.report.ctrViolations, `cụm từ chối nuốt mất khẳng định: "${p}"`).toBeGreaterThan(0)
      expect(r.failureClass, `tha nhầm: "${p}"`).toBe('UNSUPPORTED_CLAIM')
    }
  })

  it('RANH GIỚI R17: lời từ chối THẬT để tên chỉ số NGOÀI cụm, vẫn được tha', () => {
    for (const p of [
      'Tôi đã tránh mọi kết luận về CTR và thumbnail.',
      'Tôi không đưa ra nhận định nào về ảnh bìa.',
      'Phần này không phân tích CTR hay thumbnail.',
      'Không có phát biểu nào về CTR.',
    ]) {
      const r = withProse(p)
      expect(r.report.ctrViolations, `chặn oan lời từ chối thật: "${p}"`).toBe(0)
      expect(r.failureClass).toBe('PROSE_OUTSIDE_JSON')
    }
  })

  it('văn bản ngoài JSON LUÔN có dòng hướng dẫn riêng', () => {
    const r = withProse('Tôi đã tránh mọi kết luận về CTR và thumbnail.')
    expect(r.repairErrors.some((e) => e.includes('VĂN BẢN NGOÀI JSON'))).toBe(true)
  })
})

/* =========================================================================
 * F4 — dòng hướng dẫn CTR phải TRÍCH ĐƯỢC câu vi phạm và KHÔNG nói sai
 * ======================================================================= */

describe('F4 — hướng dẫn sửa lỗi CTR', () => {
  /** Ô nhạy cảm KHÔNG được khai -> U3 kêu, `ctrViolations` tăng. */
  const undeclaredSensitive = () => {
    const a = healthyComposite()
    const findings = a.keyFindings as Array<{ limitations: string[] }>
    findings[0]!.limitations = ['cỡ mẫu lượt xem thấp nên CTR nhiễu']
    return a
  }

  it('vi phạm CTR có thật -> hướng dẫn TRÍCH ĐÚNG câu vi phạm', () => {
    const r = validateCursorOutput(baseInput(JSON.stringify(undeclaredSensitive())))
    expect(r.report.ctrViolations, 'ca dựng không tạo ra vi phạm CTR nào').toBeGreaterThan(0)
    const line = r.repairErrors.find((e) => /CTR|impressions|thumbnail/i.test(e))
    expect(line, 'vi phạm CTR có thật nhưng KHÔNG có hướng dẫn nào').toBeDefined()
    expect(line, 'hướng dẫn không trích được câu vi phạm nào').toContain('Các câu vi phạm:')
  })

  it('gói có độ phủ impressions = 0 -> ĐƯỢC nói "độ phủ 0%"', () => {
    const r = validateCursorOutput(baseInput(JSON.stringify(undeclaredSensitive())))
    const line = r.repairErrors.find((e) => /CTR|impressions|thumbnail/i.test(e))!
    expect(line).toContain('độ phủ 0%')
  })

  it('gói CÓ độ phủ impressions -> KHÔNG được nói "độ phủ 0%"', () => {
    // Bốn quy tắc làm `ctrViolations` tăng đều nói về KHAI BÁO, không về độ phủ.
    // Nói với mô hình một điều SAI SỰ THẬT về chính dữ liệu nó vừa đọc sẽ đẩy
    // lần sửa sau đi sai hướng.
    const pkg = makePackage()
    pkg.dataCoverage.metricCoverage.impressions = 0.9
    pkg.dataCoverage.metricCoverage.impressionCtr = 0.9
    const built = buildPrompt({ pkg })
    const r = validateCursorOutput({
      raw: JSON.stringify(undeclaredSensitive()),
      pkg,
      allowedEvidenceIds: built.allowedEvidenceIds,
      allowedVideoIds: built.allowedVideoIds,
      allowedCohortKeys: built.allowedCohortKeys,
      hadProseOutsideJson: false,
    })
    // KHÔNG bọc trong `if (line)`: bọc thế thì xoá hẳn khối hướng dẫn CTR cũng
    // làm test xanh — đúng loại assertion không-thể-sai mà vòng này đang dọn.
    const line = r.repairErrors.find((e) => /CTR|impressions|thumbnail/i.test(e))
    expect(line, 'vi phạm CTR có thật nhưng KHÔNG có hướng dẫn nào').toBeDefined()
    expect(line, 'prompt sửa lỗi nói SAI về độ phủ của gói').not.toContain('độ phủ 0%')
    // Và phải nêu cách sửa ĐÚNG cho chặng đang kiểm.
    expect(line).toContain('metricClaims')
  })
})

/* =========================================================================
 * VÒNG RÀ SOÁT ĐỐI KHÁNG — lỗ fail-open thứ hai: KHÔNG có object JSON nào
 * ======================================================================= */

/**
 * Nhánh `!json` của vòng chạy KHÔNG đi qua bộ kiểm định.
 *
 * F2 đặt phép quét văn xuôi ở đầu `validateCursorOutput` — thấp hơn MỘT TẦNG so
 * với nhánh này. Khi output không chứa object JSON nào, `proseText` là TOÀN BỘ
 * stdout, và trước bản sửa nó bị vứt đi kèm lớp `INVALID_JSON` (RETRYABLE).
 */
describe('rà soát: output KHÔNG có object JSON nào', () => {
  it('văn xuôi có câu nhân quả -> ghi nhận VÀ không thử lại', () => {
    const r = validateProseOnly({
      hadProseOutsideJson: true,
      proseText: 'Kết luận: ảnh bìa hiện tại kém đã dẫn tới lượt xem giảm.',
    })
    expect(r.report.causalViolations, 'câu nhân quả biến mất không dấu vết').toBeGreaterThan(0)
    expect(r.failureClass, 'khẳng định bị cấm rơi vào lớp thử lại được').toBe('UNSUPPORTED_CLAIM')
    expect(
      r.report.claimIssues.some((i) => i.path === PROSE_OUTSIDE_JSON_PATH),
      'vi phạm không được LƯU nên không truy được về sau',
    ).toBe(true)
  })

  it('văn xuôi có khẳng định về chỉ số nhạy cảm -> không thử lại', () => {
    const r = validateProseOnly({
      hadProseOutsideJson: true,
      proseText: 'CTR của kênh đang thấp nên tôi dừng ở đây.',
    })
    expect(r.report.ctrViolations).toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('RANH GIỚI: văn xuôi SẠCH vẫn là lỗi định dạng, VẪN thử lại được', () => {
    const r = validateProseOnly({
      hadProseOutsideJson: true,
      proseText: 'Xin lỗi, tôi không thể hoàn tất yêu cầu này.',
    })
    expect(r.report.causalViolations).toBe(0)
    expect(r.report.ctrViolations).toBe(0)
    expect(r.failureClass, 'lỗi kỹ thuật thuần phải được thử lại').toBe('INVALID_JSON')
  })

  it('CODEX R8: câu nhân quả TRONG payload khi CLI hỏng -> KHÔNG thử lại', () => {
    /*
     * `extractJson` bóc object ra khỏi `proseText`, nên quét-văn-bản-ngoài-JSON
     * nhìn vào một chuỗi RỖNG. Một câu nhân quả nằm TRONG payload biến mất mỗi
     * khi lần chạy hỏng vì lý do kỹ thuật, và lớp thất bại vẫn RETRYABLE.
     */
    const json = JSON.stringify({
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      keyFindings: [{ statement: 'Thumbnail kém đã làm giảm lượt xem.' }],
    })
    const r = validateProseOnly({ proseText: '', hadProseOutsideJson: false, emittedJson: json })
    expect(r.report.causalViolations, 'câu nhân quả trong payload biến mất').toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('RANH GIỚI: giả thuyết CÓ RÀO ĐÓN trong payload vẫn được thử lại', () => {
    // Phạt một giả thuyết viết ĐÚNG cách sẽ biến lỗi kỹ thuật thành vĩnh viễn.
    const json = JSON.stringify({
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      hypotheses: [{ statement: 'Có thể thumbnail kém đã làm giảm lượt xem.' }],
    })
    const r = validateProseOnly({ proseText: '', hadProseOutsideJson: false, emittedJson: json })
    expect(r.report.causalViolations).toBe(0)
    expect(r.failureClass).toBe('INVALID_JSON')
  })

  it('CODEX R10: câu nhân quả trong payload hỏng hình dạng LƯỢT 1 -> KHÔNG thử lại', () => {
    // `validateAnalysisOutput` có nhánh hỏng-hình-dạng RIÊNG, đi VÒNG quanh
    // `validateCursorOutput`, nên nó không hưởng phép quét ở các return sớm bên đó.
    const r = validateAnalysisOutput(
      baseInput(
        JSON.stringify({
          schemaVersion: '1.0',
          analysisSummary: { overallAssessment: 'Thumbnail kém đã làm giảm lượt xem.' },
        }),
      ),
    )
    expect(r.report.causalViolations, 'câu nhân quả trong payload lượt 1 biến mất').toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('CODEX R10: câu nhân quả trong payload KHAI BÁO -> KHÔNG thử lại', () => {
    // Lượt 2 chỉ khai báo ngữ nghĩa, nhưng không gì ngăn mô hình nhét một câu
    // nhân quả vào một trường thừa — `.strict()` chỉ cho ra lỗi schema RETRYABLE.
    const set = buildObligationSet(healthyAnalysis() as unknown as CursorAnalysis)
    const r = validateDeclarationOutput({
      raw: JSON.stringify({
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: [],
        note: 'Thumbnail kém đã làm giảm lượt xem.',
      }),
      obligationSet: set,
      obligationSetHash: hashObligationSet(set),
    })
    expect(r.report.causalViolations, 'câu nhân quả trong bản khai biến mất').toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('RANH GIỚI (R11, đề nghị BỊ TỪ CHỐI): chỉ số nhạy cảm TRONG JSON vẫn thử lại được', () => {
    /*
     * Một vòng rà soát đề nghị coi "Thumbnail hiện tại kém." trong payload hỏng
     * schema là thất bại VĨNH VIỄN. Đề nghị ấy bị TỪ CHỐI vì nó mâu thuẫn với
     * kiến trúc hai lượt: ở chặng ANALYSIS, U3 cho các ô TRONG JSON bị lọc bỏ CÓ
     * CHỦ ĐÍCH ("lượt 1 chưa có bản khai để mà khai"), nên một ô nhạy cảm chưa
     * khai KHÔNG phải vi phạm — nó là ĐẦU VÀO của bộ sinh nghĩa vụ.
     *
     * Thử lại ở đây không phải "chạy lại tới khi mô hình thôi nói điều đó": mô
     * hình sửa schema, giữ nguyên câu, và câu ấy đi tiếp qua cơ chế khai báo.
     *
     * Ca này KHOÁ hành vi ấy lại để không ai âm thầm siết nó và biến mọi bài
     * phân tích có nhắc CTR kèm một lỗi schema thành thất bại vĩnh viễn.
     */
    const r = validateAnalysisOutput(
      baseInput(
        JSON.stringify({
          schemaVersion: '1.0',
          analysisSummary: { overallAssessment: 'Thumbnail hiện tại kém.' },
        }),
      ),
    )
    expect(r.report.causalViolations).toBe(0)
    expect(
      ['MISSING_REQUIRED_FIELD', 'SCHEMA_MISMATCH'],
      'ô nhạy cảm TRONG JSON bị siết thành thất bại vĩnh viễn',
    ).toContain(r.failureClass)

    // Nhưng ĐÚNG câu ấy NGOÀI JSON thì vẫn là vi phạm nội dung: ở đó không chặng
    // nào khai báo được. Đây là ranh giới thật, và nó nằm ở CHỖ ĐẶT.
    const outside = validateCursorOutput(
      baseInput(JSON.stringify(healthyComposite()), {
        hadProseOutsideJson: true,
        proseText: 'Thumbnail hiện tại kém.',
      }),
    )
    expect(outside.report.ctrViolations).toBeGreaterThan(0)
    expect(outside.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('CODEX R13: khẳng định nhạy cảm trong bản KHAI BÁO -> KHÔNG thử lại', () => {
    /*
     * Khác với lượt PHÂN TÍCH (nơi câu ấy sẽ thành nghĩa vụ ở lượt sau), ở lượt
     * KHAI BÁO bộ sinh nghĩa vụ ĐÃ chạy xong. Một câu văn xuôi nhét vào trường
     * thừa của bản khai KHÔNG bao giờ được rà soát ngữ nghĩa bởi chặng nào, và
     * `.strict()` chỉ cho ra `SCHEMA_MISMATCH` — RETRYABLE.
     */
    const set = buildObligationSet(healthyAnalysis() as unknown as CursorAnalysis)
    const r = validateDeclarationOutput({
      raw: JSON.stringify({
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: [],
        note: 'Thumbnail hiện tại kém.',
      }),
      obligationSet: set,
      obligationSetHash: hashObligationSet(set),
    })
    expect(r.report.ctrViolations, 'khẳng định nhạy cảm trong bản khai biến mất').toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('CODEX R14: khẳng định nhạy cảm MỘT TOKEN trong bản khai -> KHÔNG thử lại', () => {
    // Ranh giới "có khoảng trắng" của bản trước là một suy đoán về SỐ TỪ, và
    // `"CTR-thấp."` phá nó: một khẳng định nhạy cảm chỉ gồm một token.
    const set = buildObligationSet(healthyAnalysis() as unknown as CursorAnalysis)
    const r = validateDeclarationOutput({
      raw: JSON.stringify({
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: [],
        note: 'CTR-thấp.',
      }),
      obligationSet: set,
      obligationSetHash: hashObligationSet(set),
    })
    expect(r.report.ctrViolations, 'khẳng định một token lọt qua').toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('CODEX R15: JSON bản khai HỎNG + khẳng định nhạy cảm -> KHÔNG thử lại', () => {
    // Nhánh `catch` của lượt khai báo trước đây chỉ quét NHÂN QUẢ, nên
    // `{"extra":"CTR thấp.",}` trôi qua với lớp `INVALID_JSON` (RETRYABLE).
    const set = buildObligationSet(healthyAnalysis() as unknown as CursorAnalysis)
    const r = validateDeclarationOutput({
      raw: '{"extra":"CTR thấp.",}',
      obligationSet: set,
      obligationSetHash: hashObligationSet(set),
    })
    expect(r.report.ctrViolations, 'khẳng định nhạy cảm trong JSON hỏng biến mất').toBeGreaterThan(0)
    expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('RANH GIỚI R13: bản khai HỢP LỆ không bị phép quét mới chặn oan', () => {
    // Bản khai đúng cấu trúc vẫn nhắc `impression_ctr` ở trường `relatedMetric`
    // — đó là KHAI BÁO, không phải văn xuôi, và không được bị coi là vi phạm.
    const a2 = healthyAnalysis()
    const findings = a2.keyFindings as Array<{ limitations: string[] }>
    findings[0]!.limitations = ['cỡ mẫu lượt xem thấp nên CTR nhiễu']
    const set = buildObligationSet(a2 as unknown as CursorAnalysis)
    const r = validateDeclarationOutput({
      raw: JSON.stringify({
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: set.obligations.map((o) => ({
          id: o.id, subjectMetric: 'views', relatedMetric: 'impression_ctr',
          claimType: 'METHODOLOGY_LIMITATION', judgement: 'LOW',
          assertionStatus: o.allowedAssertionStatuses[0],
          evidenceIds: [], requiresMissingnessDisclosure: false,
        })),
      }),
      obligationSet: set,
      obligationSetHash: hashObligationSet(set),
    })
    expect(r.report.ctrViolations, 'bản khai hợp lệ bị chặn oan').toBe(0)
    expect(r.failureClass).toBe('NONE')
  })

  it('CODEX R12: JSON CÂN BẰNG NGOẶC nhưng KHÔNG hợp lệ vẫn bị quét', () => {
    /*
     * `extractJson` bóc một object cân bằng ngoặc ra khỏi `proseText`, nhưng cân
     * bằng ngoặc KHÔNG có nghĩa là JSON hợp lệ — một dấu phẩy thừa là đủ. Khi ấy
     * `JSON.parse` ném, không còn gì để duyệt, và câu nhân quả trong object
     * thoát KHỎI MỌI phép quét với lớp `INVALID_JSON` (RETRYABLE).
     */
    const raw = '{"analysisSummary":{"overallAssessment":"Thumbnail kém đã làm giảm lượt xem."},}'
    expect(() => JSON.parse(raw), 'ca dựng phải là JSON KHÔNG hợp lệ').toThrow()

    const viaProse = validateProseOnly({
      proseText: '',
      hadProseOutsideJson: false,
      emittedJson: raw,
    })
    expect(viaProse.report.causalViolations, 'câu nhân quả trong JSON hỏng biến mất').toBeGreaterThan(0)
    expect(viaProse.failureClass).toBe('UNSUPPORTED_CLAIM')

    const viaValidator = validateCursorOutput(baseInput(raw))
    expect(viaValidator.report.causalViolations).toBeGreaterThan(0)
    expect(viaValidator.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('CODEX R18: khẳng định nhạy cảm ở TRƯỜNG THỪA của lượt 1 -> KHÔNG thử lại', () => {
    /*
     * Ranh giới R11 nói: câu nhạy cảm trong một Ô PHÂN TÍCH hợp lệ sẽ thành
     * nghĩa vụ, nên không chặn. Điều đó KHÔNG áp cho trường THỪA: `.strict()` từ
     * chối nó vĩnh viễn, nên nó không bao giờ thành nghĩa vụ, và nếu không quét
     * thì lời bị cấm biến mất khỏi hồ sơ mỗi lần payload hỏng.
     */
    const viaValidator = validateCursorOutput(
      baseInput(JSON.stringify({ schemaVersion: '9.9', extra: 'CTR thấp.' })),
    )
    expect(viaValidator.report.ctrViolations, 'trường thừa không được quét').toBeGreaterThan(0)
    expect(viaValidator.failureClass).toBe('UNSUPPORTED_CLAIM')

    // JSON HỎNG hoàn toàn: không có cấu trúc trường -> quét cả hai loại.
    const viaProse = validateProseOnly({
      proseText: '',
      hadProseOutsideJson: false,
      emittedJson: '{"extra":"CTR thấp.",}',
      analysisPass: true,
    })
    expect(viaProse.report.ctrViolations).toBeGreaterThan(0)
    expect(viaProse.failureClass).toBe('UNSUPPORTED_CLAIM')
  })

  it('CODEX R19: trường thừa LỒNG ở mọi độ sâu -> KHÔNG thử lại', () => {
    /*
     * Danh sách khoá cấp-cao-nhất viết tay là BẢN SAO THỨ HAI của schema và đã
     * lệch ngay lần đầu: `analysisSummary` hợp lệ nên cả cây con được miễn trừ,
     * trong khi `.strict()` LỒNG từ chối `extra` bên trong nó vĩnh viễn.
     */
    for (const payload of [
      { schemaVersion: '9.9', extra: 'CTR thấp.' },
      { schemaVersion: '9.9', analysisSummary: { overallAssessment: 'Bình thường.', extra: 'CTR thấp.' } },
      { schemaVersion: '9.9', keyFindings: [{ id: 'F-001', extra: 'CTR thấp.' }] },
    ]) {
      const r = validateCursorOutput(baseInput(JSON.stringify(payload)))
      expect(
        r.report.ctrViolations,
        `trường thừa không được quét: ${JSON.stringify(payload)}`,
      ).toBeGreaterThan(0)
      expect(r.failureClass).toBe('UNSUPPORTED_CLAIM')
    }
  })

  it('RANH GIỚI R18: Ô PHÂN TÍCH hợp lệ vẫn giữ nguyên ranh giới R11', () => {
    // Không được siết nhầm: câu nhạy cảm trong `analysisSummary` vẫn là đầu vào
    // của bộ sinh nghĩa vụ, nên vẫn phải THỬ LẠI ĐƯỢC.
    const r = validateCursorOutput(
      baseInput(
        JSON.stringify({
          schemaVersion: '9.9',
          analysisSummary: { overallAssessment: 'Thumbnail hiện tại kém.' },
        }),
      ),
    )
    expect(r.report.ctrViolations, 'ô phân tích hợp lệ bị siết nhầm').toBe(0)
    expect(r.failureClass).toBe('UNSUPPORTED_SCHEMA_VERSION')
  })

  it('CODEX R9: rào đón chỉ tha ở Ô GIẢ THUYẾT, không tha ở mọi ô', () => {
    /*
     * Bản trước áp ngoại lệ rào đón cho MỌI chuỗi vì bộ quét không biết ô. Đường
     * chạy đầy đủ chỉ tha ở `HYPOTHESIS`/`EXPERIMENT`, nên cùng một câu nằm
     * trong `keyFindings` được tha oan — và đó là ô mà câu nhân quả bị cấm nhất.
     */
    const S = 'Có thể thumbnail kém đã làm giảm lượt xem.'
    expect(scanCausalInEmittedJson({ hypotheses: [{ statement: S }] }).causalViolations).toBe(0)
    expect(
      scanCausalInEmittedJson({ keyFindings: [{ statement: S }] }).causalViolations,
      'rào đón tha oan một câu nhân quả trong keyFindings',
    ).toBeGreaterThan(0)
    expect(
      scanCausalInEmittedJson({ recommendations: [{ rationale: S }] }).causalViolations,
    ).toBeGreaterThan(0)
  })

  it('CODEX R9: KHÔNG có trần độ sâu — câu chôn sâu vẫn bị bắt', () => {
    // Trần `depth > 12` cũ IM LẶNG bỏ phần sâu hơn: một cái trần fail-open đặt
    // trong lớp an toàn thì chính nó là lỗ hổng.
    let deep: Record<string, unknown> = { statement: 'Thumbnail kém đã làm giảm lượt xem.' }
    for (let i = 0; i < 40; i++) deep = { x: deep }
    expect(scanCausalInEmittedJson(deep).causalViolations, 'câu chôn sâu biến mất').toBeGreaterThan(0)
  })

  it('luôn có hướng dẫn sửa lỗi, kể cả khi không có JSON', () => {
    const r = validateProseOnly({ hadProseOutsideJson: true, proseText: 'CTR đang thấp.' })
    expect(r.repairErrors.length).toBeGreaterThan(1)
    expect(r.repairErrors.join(' ')).toContain('VĂN BẢN NGOÀI JSON')
  })
})

/* =========================================================================
 * CODEX R5 — chặng KHAI BÁO: lỗi KỸ THUẬT phải được THỬ LẠI
 * ======================================================================= */

/**
 * Chiều sai NGƯỢC với các lỗ fail-open: một lỗi kỹ thuật bị xử như lỗi nội dung.
 *
 * Mô hình chép sai MỘT ký tự của `obligationSetHash` thì `obligation_set_drift`
 * từng thành `UNSUPPORTED_CLAIM` — lớp KHÔNG thử lại — nên vòng chạy dừng ngay
 * sau lần thử đầu và vứt một bài phân tích ĐÃ ĐÓNG BĂNG hợp lệ, trong khi dòng
 * sửa lỗi cho đúng cái đó đã nằm sẵn trong `repairErrors`.
 */
describe('R5 — phân loại thất bại của chặng khai báo', () => {
  const analysisFixture = () => {
    const a = healthyAnalysis()
    const findings = a.keyFindings as Array<{ limitations: string[] }>
    findings[0]!.limitations = ['cỡ mẫu lượt xem thấp nên CTR nhiễu']
    return a as unknown as CursorAnalysis
  }
  const declFor = (o: { id: string }) => ({
    id: o.id, subjectMetric: 'views', relatedMetric: 'impression_ctr',
    claimType: 'METHODOLOGY_LIMITATION', judgement: 'LOW', assertionStatus: 'LIMITATION',
    evidenceIds: [] as string[], requiresMissingnessDisclosure: false,
  })

  it('băm tập nghĩa vụ chép SAI -> lỗi KỸ THUẬT, ĐƯỢC thử lại', () => {
    const set = buildObligationSet(analysisFixture())
    const real = hashObligationSet(set)
    const typo = `${real.slice(0, 63)}${real[63] === 'a' ? 'b' : 'a'}`
    const r = validateDeclarationOutput({
      raw: JSON.stringify({
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: typo,
        declarations: set.obligations.map(declFor),
      }),
      obligationSet: set,
      obligationSetHash: real,
    })
    expect(r.report.passed).toBe(false)
    expect(
      r.failureClass,
      'sai một ký tự băm mà vứt cả bài phân tích đã đóng băng',
    ).toBe('MISSING_REQUIRED_FIELD')
    expect(r.repairErrors.length, 'có lớp thử lại nhưng không có hướng dẫn').toBeGreaterThan(0)
  })

  it('khai THIẾU một nghĩa vụ -> lỗi KỸ THUẬT, ĐƯỢC thử lại', () => {
    const set = buildObligationSet(analysisFixture())
    expect(set.obligations.length, 'ca dựng cần ít nhất một nghĩa vụ').toBeGreaterThan(0)
    const r = validateDeclarationOutput({
      raw: JSON.stringify({
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: [],
      }),
      obligationSet: set,
      obligationSetHash: hashObligationSet(set),
    })
    expect(r.failureClass).toBe('MISSING_REQUIRED_FIELD')
  })

  it('RANH GIỚI: vi phạm NGỮ NGHĨA vẫn là NỘI DUNG, KHÔNG thử lại', () => {
    /*
     * Nới lớp kỹ thuật không được kéo theo lớp ngữ nghĩa.
     *
     * Ô `DATA_REQUEST|metricOrArtifact` là NHÃN dữ liệu cần thu thập, nên
     * `STRUCTURAL_SPEECH_ACT` chỉ cho phép CONDITIONAL/LIMITATION — `ASSERTED` là
     * trạng thái DUY NHẤT bị cấm ở đó. Đây là vi phạm NỘI DUNG và phải vĩnh viễn.
     */
    const a = healthyAnalysis()
    ;(a.dataRequests as unknown[]) = [{
      metricOrArtifact: 'impressions cấp video',
      reason: 'Cần impressions để đánh giá khâu tiếp cận của kênh này.',
      decisionUnlocked: 'Quyết định có nên đầu tư lại vào ảnh bìa hay không.',
    }]
    const set = buildObligationSet(a as unknown as CursorAnalysis)
    const target = set.obligations.find((o) => o.sourceRef.section === 'DATA_REQUEST')
    expect(target, 'ca dựng không sinh nghĩa vụ cho DATA_REQUEST').toBeDefined()
    expect(target!.allowedAssertionStatuses).not.toContain('ASSERTED')

    const r = validateDeclarationOutput({
      raw: JSON.stringify({
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: set.obligations.map((o) => ({
          ...declFor(o),
          assertionStatus: o.id === target!.id ? 'ASSERTED' : o.allowedAssertionStatuses[0],
        })),
      }),
      obligationSet: set,
      obligationSetHash: hashObligationSet(set),
    })
    expect(r.report.passed).toBe(false)
    expect(r.failureClass, 'vi phạm ngữ nghĩa lọt vào lớp thử lại được').toBe('UNSUPPORTED_CLAIM')
  })
})

/* =========================================================================
 * RANH GIỚI TIN CẬY — KHÔNG NGHĨA VỤ NÀO, và khoảng trống "ảnh bìa"
 * ======================================================================= */

/**
 * `obligationCount === 0` nghĩa là "BỘ DÒ KHÔNG THẤY GÌ", KHÔNG phải "sạch".
 *
 * Reviewer B, Finding 3. TRƯỚC G-R3, một đầu vào mà bộ dò không nhận ra bị
 * short-circuit: `resultId: null`, và nó rơi khỏi mọi mẫu số. SAU G-R3 (bỏ đường
 * cấp phép thứ hai — đúng), nó sinh ra một hiện vật chính thức ĐẦY ĐỦ GIẤY TỜ
 * với `obligationCount: 0`. Bản sửa ấy đúng, nhưng nó KHÔNG thêm phép kiểm độc
 * lập nào cho chính ca mà nó vừa cấp phép.
 *
 * Hai test dưới đây là phép kiểm còn thiếu: (1) khoảng trống cụ thể đã được bịt;
 * (2) con số 0 phải ĐỌC ĐƯỢC ở nơi người ta thật sự đọc, để "không thấy gì"
 * không đội lốt "sạch".
 */
describe('ranh giới tin cậy: 0 nghĩa vụ', () => {
  it('"ảnh bìa" NAY được nhận là ô nhạy cảm', () => {
    // Đây là cách gọi thumbnail phổ biến nhất trong tiếng Việt, và nó vắng mặt
    // suốt trong khi ba cách gọi ít dùng hơn đều có.
    expect(SENSITIVE_MENTION.test('ảnh bìa'), '"ảnh bìa" vẫn không được nhận').toBe(true)
    expect([...mentionedSensitiveMetrics('Nên thử lại ảnh bìa của video này.')]).toContain(
      'thumbnail',
    )
  })

  it('mọi cách gọi thumbnail đã biết đều được nhận — không cái nào lệch', () => {
    for (const t of ['thumbnail', 'hình thu nhỏ', 'ảnh đại diện', 'ảnh bìa', 'hình bìa']) {
      expect(SENSITIVE_MENTION.test(t), `bộ dò không nhận "${t}"`).toBe(true)
    }
  })

  it('bản phân tích viết về "ảnh bìa" NAY sinh ra nghĩa vụ, không phải 0', () => {
    // Ca của Finding 3: toàn bộ kết luận nói về ảnh bìa. Trước đây -> 0 nghĩa vụ
    // -> hiện vật đọc như "phân tích sạch". Nay phải có nghĩa vụ để mà khai.
    const a = healthyAnalysis()
    const findings = a.keyFindings as Array<{ statement: string }>
    findings[0]!.statement = 'Ảnh bìa của nhóm video dẫn đầu dùng chữ lớn và nền tương phản cao.'
    const set = buildObligationSet(a as never)
    expect(set.obligations.length, 'kết luận về ảnh bìa vẫn sinh 0 nghĩa vụ').toBeGreaterThan(0)
  })

  it('0 nghĩa vụ vẫn là con số ĐỌC ĐƯỢC, không phải sự vắng mặt', () => {
    // Ranh giới ngược lại: bịt khoảng trống không có nghĩa là cấm ca 0 nghĩa vụ.
    // Một bài phân tích thật sự không chạm chỉ số nhạy cảm nào VẪN hợp lệ — điều
    // bắt buộc là con số 0 phải hiện diện tường minh để người đọc phân biệt được
    // "không thấy gì" với "sạch".
    const set = buildObligationSet(healthyAnalysis() as never)
    expect(set.obligations.length).toBe(0)
    expect(
      IDENTITY_REQUIRED_ON_SUCCESS,
      '`obligationCount` phải là trường BẮT BUỘC của một lần chạy ĐẠT',
    ).toContain('obligationCount')
    expect(
      PROVENANCE_MATRIX.artifactMeta.required,
      '`obligationCount` phải nằm trong ma trận phủ, không chỉ trong một assertion tay',
    ).toContain('obligationCount')
  })
})

/* ---------------- fixture: bản phân tích/hợp nhất LÀNH MẠNH --------------- */

/**
 * Bản phân tích LÀNH MẠNH — cùng hình dạng với fixture đã dùng ở
 * `composite-authorization.test.ts`, tức hình dạng THẬT mà schema chấp nhận.
 */
function healthyAnalysis(): Record<string, unknown> {
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
      findingType: 'OBSERVATION',
      confidence: 'MEDIUM',
      evidenceIds: ['OBS-001'],
      supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
      contradictingEvidenceIds: [] as string[],
      limitations: [] as string[],
    }],
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
  }
}

function healthyComposite(): Record<string, unknown> {
  return { ...healthyAnalysis(), schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, metricClaims: [] }
}
