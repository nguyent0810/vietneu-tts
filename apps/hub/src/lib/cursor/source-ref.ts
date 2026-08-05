import type { CursorOutput, SourceRef } from './schema'

/**
 * Phân giải tham chiếu nguồn — thay cho việc so hai bản văn bản.
 *
 * RANH GIỚI TIN CẬY, nói rõ ngay từ đây:
 *
 *  - Phân giải tham chiếu và tính DUY NHẤT của `itemId` là TẤT ĐỊNH: một ref
 *    hoặc trỏ tới đúng một ô có thật, hoặc không.
 *  - Việc đếm "mệnh đề nhạy cảm" và quy tắc "một ô một phát biểu" là HEURISTIC
 *    NGÔN NGỮ: chúng dựa trên tách mệnh đề và nhận diện từ khoá, không phải phân
 *    tích cú pháp. Không được gộp chung hai nhóm này rồi gọi cả tầng là tất định.
 */

export interface ResolvedUnit {
  /** Văn bản THẬT tại ô được trỏ tới. */
  text: string
  /** Con trỏ suy ra, CHỈ để chẩn đoán — không phải nguồn sự thật. */
  pointer: string
  /** Danh tính chuẩn tắc của ô: section|itemId|field. KHÔNG gồm ordinal. */
  canonical: string
}

export type ResolveError =
  | 'ITEM_NOT_FOUND'
  | 'FIELD_NOT_FOUND'
  | 'ORDINAL_OUT_OF_RANGE'
  | 'FIELD_NOT_TEXT'
  | 'MALFORMED_REF'
  | 'AMBIGUOUS_DUPLICATE_TEXT'

/** Các mục có `id` theo từng section. */
const SECTION_ITEMS: Record<string, (o: CursorOutput) => Array<{ id: string }>> = {
  KEY_FINDING: (o) => o.keyFindings,
  HYPOTHESIS: (o) => o.hypotheses,
  RECOMMENDATION: (o) => o.recommendations,
  EXPERIMENT: (o) => o.experiments,
}

/** Section KHÔNG có id: trỏ thẳng vào mảng/đối tượng cấp cao nhất. */
const SECTION_ROOTS: Record<string, (o: CursorOutput) => unknown> = {
  ANALYSIS_SUMMARY: (o) => o.analysisSummary,
  MANUAL_REVIEW: (o) => o.manualReviewTargets,
  DATA_REQUEST: (o) => o.dataRequests,
  NON_CONCLUSION: (o) => ({ explicitNonConclusions: o.explicitNonConclusions }),
}

/**
 * `itemId` phải DUY NHẤT trong section của nó.
 *
 * Trùng id nghĩa là một tham chiếu có thể trỏ tới hai mục khác nhau — không được
 * phép chọn bừa một cái.
 */
export function findDuplicateItemIds(output: CursorOutput): Array<{ section: string; id: string }> {
  const dup: Array<{ section: string; id: string }> = []
  for (const [section, get] of Object.entries(SECTION_ITEMS)) {
    const seen = new Set<string>()
    for (const it of get(output)) {
      if (seen.has(it.id)) dup.push({ section, id: it.id })
      seen.add(it.id)
    }
  }
  return dup
}

function normalize(t: string): string {
  return t.trim().toLowerCase().replace(/\s+/gu, ' ')
}

/**
 * Lấy giá trị field, kèm phát hiện MẬP MỜ do trùng nội dung.
 *
 * Nếu một field mảng chứa hai phần tử trùng nội dung thì `ordinal` không còn xác
 * định được ô nào là ô được nói tới sau khi đảo thứ tự. Trả lỗi thay vì đoán.
 */
function readField(
  container: unknown,
  field: string,
  ordinal: number,
): { text: string } | { error: ResolveError } {
  if (typeof container !== 'object' || container === null) return { error: 'ITEM_NOT_FOUND' }
  const v = (container as Record<string, unknown>)[field]
  if (v === undefined) return { error: 'FIELD_NOT_FOUND' }

  if (typeof v === 'string') {
    if (ordinal !== 0) return { error: 'ORDINAL_OUT_OF_RANGE' }
    return { text: v }
  }
  if (Array.isArray(v)) {
    if (!v.every((x) => typeof x === 'string')) return { error: 'FIELD_NOT_TEXT' }
    const arr = v as string[]
    if (ordinal < 0 || ordinal >= arr.length) return { error: 'ORDINAL_OUT_OF_RANGE' }
    // FAIL-CLOSED: trùng nội dung trong cùng field -> ordinal không còn xác định.
    const norms = arr.map(normalize)
    if (norms.some((x, i) => norms.indexOf(x) !== i)) {
      return { error: 'AMBIGUOUS_DUPLICATE_TEXT' }
    }
    return { text: arr[ordinal]! }
  }
  return { error: 'FIELD_NOT_TEXT' }
}

export function resolveSourceRef(
  output: CursorOutput,
  ref: SourceRef,
): { ok: ResolvedUnit } | { error: ResolveError } {
  const canonical = `${ref.section}|${ref.itemId}|${ref.field}`

  const itemsOf = SECTION_ITEMS[ref.section]
  if (itemsOf) {
    if (!ref.itemId) return { error: 'MALFORMED_REF' }
    const items = itemsOf(output)
    const idx = items.findIndex((x) => x.id === ref.itemId)
    if (idx === -1) return { error: 'ITEM_NOT_FOUND' }
    const got = readField(items[idx], ref.field, ref.ordinal)
    if ('error' in got) return got
    return {
      ok: { text: got.text, canonical, pointer: `${ref.section}(${ref.itemId}).${ref.field}[${ref.ordinal}]` },
    }
  }

  const rootOf = SECTION_ROOTS[ref.section]
  if (!rootOf) return { error: 'MALFORMED_REF' }
  // Section không có id thì `itemId` PHẢI rỗng — khai id ở đây là mâu thuẫn.
  if (ref.itemId) return { error: 'MALFORMED_REF' }

  const root = rootOf(output)
  // MANUAL_REVIEW / DATA_REQUEST là mảng đối tượng: `ordinal` chọn phần tử,
  // `field` chọn thuộc tính bên trong. Dùng cú pháp "field@n" cho phần tử.
  if (Array.isArray(root)) {
    const m = /^(.+)@(\d+)$/u.exec(ref.field)
    if (!m) return { error: 'MALFORMED_REF' }
    const inner = m[1]!
    const itemIdx = Number(m[2])
    if (itemIdx < 0 || itemIdx >= root.length) return { error: 'ORDINAL_OUT_OF_RANGE' }
    const got = readField(root[itemIdx], inner, ref.ordinal)
    if ('error' in got) return got
    return {
      ok: {
        text: got.text,
        canonical: `${ref.section}|${itemIdx}|${inner}`,
        pointer: `${ref.section}[${itemIdx}].${inner}[${ref.ordinal}]`,
      },
    }
  }

  const got = readField(root, ref.field, ref.ordinal)
  if ('error' in got) return got
  return { ok: { text: got.text, canonical, pointer: `${ref.section}.${ref.field}[${ref.ordinal}]` } }
}

/**
 * Mọi Ô VĂN BẢN của output, kèm danh tính chuẩn tắc.
 *
 * Dùng để liệt kê ô nào có nhắc chỉ số nhạy cảm mà chưa được khai. Danh sách này
 * phải phủ MỌI bề mặt văn bản — thiếu một bề mặt là để lại một lỗ im lặng.
 */
export function enumerateUnits(output: CursorOutput): ResolvedUnit[] {
  const out: ResolvedUnit[] = []
  const push = (section: string, itemId: string, field: string, ordinal: number, text: string) =>
    out.push({
      text,
      canonical: `${section}|${itemId}|${field}`,
      pointer: `${section}(${itemId}).${field}[${ordinal}]`,
    })

  const s = output.analysisSummary
  for (const f of ['overallAssessment', 'confidenceRationale', 'primaryConstraint'] as const) {
    push('ANALYSIS_SUMMARY', '', f, 0, s[f])
  }
  output.keyFindings.forEach((it) => {
    push('KEY_FINDING', it.id, 'statement', 0, it.statement)
    push('KEY_FINDING', it.id, 'supportingReasoning', 0, it.supportingReasoning)
    it.limitations.forEach((t, i) => push('KEY_FINDING', it.id, 'limitations', i, t))
  })
  output.hypotheses.forEach((it) => {
    push('HYPOTHESIS', it.id, 'statement', 0, it.statement)
    push('HYPOTHESIS', it.id, 'validationMethod', 0, it.validationMethod)
    it.missingEvidence.forEach((t, i) => push('HYPOTHESIS', it.id, 'missingEvidence', i, t))
  })
  output.recommendations.forEach((it) => {
    push('RECOMMENDATION', it.id, 'action', 0, it.action)
    push('RECOMMENDATION', it.id, 'rationale', 0, it.rationale)
    push('RECOMMENDATION', it.id, 'successMetric', 0, it.successMetric)
    it.risks.forEach((t, i) => push('RECOMMENDATION', it.id, 'risks', i, t))
  })
  output.experiments.forEach((it) => {
    push('EXPERIMENT', it.id, 'change', 0, it.change)
    push('EXPERIMENT', it.id, 'baseline', 0, it.baseline)
    it.successMetrics.forEach((t, i) => push('EXPERIMENT', it.id, 'successMetrics', i, t))
    it.sampleLimitations.forEach((t, i) => push('EXPERIMENT', it.id, 'sampleLimitations', i, t))
    it.stopConditions.forEach((t, i) => push('EXPERIMENT', it.id, 'stopConditions', i, t))
    it.interpretationRisks.forEach((t, i) => push('EXPERIMENT', it.id, 'interpretationRisks', i, t))
  })
  output.manualReviewTargets.forEach((it, mi) => {
    push('MANUAL_REVIEW', '', `reason@${mi}`, 0, it.reason)
    it.reviewQuestions.forEach((t, i) => push('MANUAL_REVIEW', '', `reviewQuestions@${mi}`, i, t))
  })
  output.dataRequests.forEach((it, di) => {
    push('DATA_REQUEST', '', `metricOrArtifact@${di}`, 0, it.metricOrArtifact)
    push('DATA_REQUEST', '', `reason@${di}`, 0, it.reason)
    push('DATA_REQUEST', '', `decisionUnlocked@${di}`, 0, it.decisionUnlocked)
  })
  output.explicitNonConclusions.forEach((t, i) =>
    push('NON_CONCLUSION', '', 'explicitNonConclusions', i, t),
  )
  return out
}
