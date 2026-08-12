import { sourceRefSections, type CursorAnalysis, type SourceRef } from './schema'

/**
 * Bộ phân giải làm việc trên THÂN PHÂN TÍCH, không đòi `metricClaims`.
 *
 * Nhờ vậy nó chạy được ở LƯỢT 1 (khi chưa có claim nào) để sinh tập nghĩa vụ, và
 * chạy lại được ở chặng COMPOSITE trên chính bản phân tích đã đóng băng. Kết quả
 * hợp nhất vẫn truyền vào được vì nó có đủ mọi trường của thân phân tích.
 */
type CursorOutput = CursorAnalysis

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
  /**
   * Danh tính của Ô: section|itemId|field#ordinal.
   *
   * GỒM `ordinal`, và điều đó là bắt buộc. Đơn vị khai báo của 2.1 là Ô, mà một
   * field mảng có NHIỀU ô. Bỏ ordinal ra ngoài thì cả `limitations[0]` và
   * `limitations[1]` mang cùng một danh tính, kéo theo hai hỏng nặng:
   *
   *  - U2 chặn oan: hai claim trỏ hai phần tử KHÁC NHAU bị báo "cùng trỏ một ô".
   *    Mà "tách thành nhiều phần tử" lại đúng là cách sửa mà U1 yêu cầu — nên
   *    cách sửa duy nhất khả dĩ tự nó bị chặn. Bế tắc.
   *  - U3 để lọt: khai báo cho `limitations[0]` khiến `limitations[1]` cũng được
   *    tính là ĐÃ KHAI. Một phát biểu nhạy cảm chưa khai lọt qua trong im lặng.
   *
   * Danh tính dùng cho phép so TRÔI DẠT thì NGƯỢC LẠI: nó cố tình bỏ ordinal,
   * để đảo thứ tự mảng không bị coi là đổi ngữ nghĩa (D3/D4). Hai khái niệm
   * khác nhau, và được tính ở hai nơi khác nhau (`run.ts` tự dựng của nó).
   */
  canonical: string
}

/**
 * Danh tính và con trỏ của một Ô — MỘT chỗ dựng duy nhất.
 *
 * `resolveSourceRef` và `enumerateUnits` phải sinh ra CÙNG chuỗi cho cùng một ô,
 * nếu không thì U2/U3 so hai hệ danh tính khác nhau và luôn cho kết quả sai.
 * Đã từng lệch thật: nhánh mảng cấp cao nhất dựng `MANUAL_REVIEW|0|reason` trong
 * khi bộ liệt kê dựng `MANUAL_REVIEW||reason@0`, nên MỌI claim trỏ vào
 * `manualReviewTargets`/`dataRequests` đều bị báo "chưa khai" dù đã khai đúng.
 */
function unitKey(section: string, itemId: string, field: string, ordinal: number): string {
  return `${section}|${itemId}|${field}#${ordinal}`
}

function unitPointer(section: string, itemId: string, field: string, ordinal: number): string {
  return `${section}(${itemId}).${field}[${ordinal}]`
}

export type ResolveError =
  | 'ITEM_NOT_FOUND'
  | 'FIELD_NOT_FOUND'
  | 'ORDINAL_OUT_OF_RANGE'
  | 'FIELD_NOT_TEXT'
  | 'MALFORMED_REF'
  | 'AMBIGUOUS_DUPLICATE_TEXT'
  | 'DUPLICATE_ITEM_ID'

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

/**
 * Trường VĂN XUÔI hợp lệ của từng section — sinh từ schema, tính một lần.
 *
 * Không đủ nếu chỉ kiểm kiểu lúc chạy: `keyFindings[].confidence` là một ENUM,
 * nhưng giá trị của nó vẫn là chuỗi, nên `typeof v === 'string'` cho qua và một
 * claim có thể "trỏ" vào ô "MEDIUM". Ô đó không nằm trong `enumerateUnits`, nên
 * nó không khai báo được cho bất kỳ ô nhạy cảm nào — nhưng nó cũng không bị bắt,
 * và một tham chiếu vô nghĩa được ghi lại như một tham chiếu hợp lệ.
 *
 * Danh sách này chính là danh sách in ra trong prompt: cái mô hình được cho biết
 * và cái bộ kiểm định chấp nhận là MỘT.
 */
const ALLOWED_FIELDS: Map<string, Set<string>> = new Map(
  sourceRefSections().map((s) => [s.section, new Set(s.fields.map((f) => f.name))]),
)

export function resolveSourceRef(
  output: CursorOutput,
  ref: SourceRef,
): { ok: ResolvedUnit } | { error: ResolveError } {
  const canonical = unitKey(ref.section, ref.itemId, ref.field, ref.ordinal)
  const pointer = unitPointer(ref.section, ref.itemId, ref.field, ref.ordinal)

  const itemsOf = SECTION_ITEMS[ref.section]
  if (itemsOf) {
    if (!ref.itemId) return { error: 'MALFORMED_REF' }
    if (!ALLOWED_FIELDS.get(ref.section)?.has(ref.field)) return { error: 'FIELD_NOT_TEXT' }
    const items = itemsOf(output)
    const matches = items.filter((x) => x.id === ref.itemId)
    if (matches.length === 0) return { error: 'ITEM_NOT_FOUND' }
    // R4 tại CHÍNH CHỖ phân giải, không chỉ ở phép kiểm riêng.
    //
    // `findIndex` lặng lẽ lấy mục ĐẦU TIÊN khi có hai mục trùng id, nên hàm này
    // trả về "ok" cho một tham chiếu mập mờ. Trong luồng đầy đủ,
    // `findDuplicateItemIds` vẫn chặn cả output — nhưng `resolveSourceRef` là
    // hàm dùng chung và không được phép tự nó đoán bừa: chọn bừa một trong hai
    // mục là đúng loại "thành công giả" mà tầng này sinh ra để chống.
    if (matches.length > 1) return { error: 'DUPLICATE_ITEM_ID' }
    const idx = items.findIndex((x) => x.id === ref.itemId)
    const got = readField(items[idx], ref.field, ref.ordinal)
    if ('error' in got) return got
    return { ok: { text: got.text, canonical, pointer } }
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
    if (!ALLOWED_FIELDS.get(ref.section)?.has(inner)) return { error: 'FIELD_NOT_TEXT' }
    const itemIdx = Number(m[2])
    if (itemIdx < 0 || itemIdx >= root.length) return { error: 'ORDINAL_OUT_OF_RANGE' }
    const got = readField(root[itemIdx], inner, ref.ordinal)
    if ('error' in got) return got
    // Danh tính giữ NGUYÊN VẸN `ref.field` ("reason@0"), không tách thành
    // `itemIdx` + `inner`: bộ liệt kê cũng dựng bằng đúng chuỗi đó, và hai bên
    // phải khớp từng ký tự thì U2/U3 mới nói về cùng một ô.
    return { ok: { text: got.text, canonical, pointer } }
  }

  if (!ALLOWED_FIELDS.get(ref.section)?.has(ref.field)) return { error: 'FIELD_NOT_TEXT' }
  const got = readField(root, ref.field, ref.ordinal)
  if ('error' in got) return got
  return { ok: { text: got.text, canonical, pointer } }
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
      canonical: unitKey(section, itemId, field, ordinal),
      pointer: unitPointer(section, itemId, field, ordinal),
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
