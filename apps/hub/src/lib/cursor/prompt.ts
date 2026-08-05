import { createHash } from 'node:crypto'

import type { AnalysisPackage } from '../analysis/package'
import {
  CLAIM_METRICS,
  cursorOutputSchema,
  OUTPUT_LIMITS,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  sourceRefSections,
} from './schema'

/**
 * Dựng prompt cho Cursor từ các PHẦN có cấu trúc, không phải một khối văn bản
 * tự do.
 *
 * Hai tính chất phải giữ bằng mọi giá:
 *
 * 1. TẤT ĐỊNH — cùng gói + cùng phiên bản prompt cho ra cùng chuỗi và cùng
 *    băm. Không có `Date.now()`, không có thứ tự phụ thuộc Map, không có gì
 *    ngẫu nhiên. Nhờ đó mới so sánh được các lần chạy lặp lại ở phần đo độ ổn định.
 *
 * 2. KHÔNG CẮT ÂM THẦM — chạm trần kích thước thì phải GHI LẠI đã bỏ gì, bao
 *    nhiêu, vì sao, và việc bỏ đó có ảnh hưởng kết luận không. Một prompt bị
 *    cắt lặng lẽ sẽ khiến mô hình kết luận trên bằng chứng thiếu mà cả nó lẫn
 *    ta đều không biết.
 */

/**
 * 3.0.0 — khai báo TRỎ tới ô gốc, không sao chép nó.
 *
 * 1.x để bộ kiểm định ĐOÁN xem tính từ bổ nghĩa cho danh từ nào; bảy cấu trúc
 * ngữ pháp đã đánh bại phép đoán đó qua năm lô. 2.0.0 buộc mô hình KHAI BÁO ngữ
 * nghĩa — đúng hướng — nhưng bắt nó SAO CHÉP NGUYÊN VĂN câu vào `text`, và toàn
 * bộ lô 2.0 hỏng vì hai bản văn bản lệch nhau (55 lỗi "khớp mập mờ", 24 claim mồ
 * côi). Sao chép nguyên văn là việc mô hình ngôn ngữ làm kém nhất.
 *
 * 3.0.0 bỏ `text` và thay bằng `sourceRef` — một THAM CHIẾU tới ô gốc. Chỉ còn
 * MỘT bản văn bản, nên cả lớp lỗi "bản sao khác bản gốc" biến mất theo định
 * nghĩa. Kèm theo đó là ràng buộc mới về cách hành văn: mỗi Ô chỉ được chứa MỘT
 * phát biểu về chỉ số nhạy cảm.
 */
export const PROMPT_VERSION = '3.0.0'

/**
 * Trần ký tự của prompt.
 *
 * Gói lớn nhất hiện tại ~48KB; 200k ký tự cho biên rất rộng mà vẫn là một trần
 * thật, để lỗi kích thước lộ ra ở đây chứ không lộ ra dưới dạng output bị cắt.
 */
export const MAX_PROMPT_CHARS = 200_000

export interface PromptOmission {
  section: string
  omittedCount: number
  reason: string
  /** CRITICAL = bằng chứng cốt lõi; SUPPORTING = ngữ cảnh; OPTIONAL = làm giàu. */
  priority: 'CRITICAL' | 'SUPPORTING' | 'OPTIONAL'
  mayAffectConclusions: boolean
}

export interface ContentMetadata {
  youtubeVideoId: string
  title?: string
  descriptionExcerpt?: string
  seoTags?: string[]
}

export interface BuildPromptInput {
  pkg: AnalysisPackage
  /**
   * Metadata nội dung tuỳ chọn, phải được ĐÍNH KÈM tường minh và giới hạn kích
   * thước. Cursor không được tự đi tìm thêm dữ liệu.
   */
  contentMetadata?: ContentMetadata[]
  maxChars?: number
  /**
   * Phần đã bị lược bỏ ở lần dựng trước, để NÊU TƯỜNG MINH trong prompt.
   *
   * Nội bộ: chỉ `buildPrompt` tự truyền khi dựng lại sau khi cắt bớt. Nếu không
   * nói cho mô hình biết danh sách đã bị cắt, nó sẽ suy luận như thể danh sách
   * là đầy đủ — ví dụ kết luận "chỉ có 10 video đáng chú ý" trong khi thực tế
   * có 20 và 10 cái kia bị cắt vì giới hạn kích thước.
   */
  declaredOmissions?: PromptOmission[]
}

export interface BuiltPrompt {
  text: string
  hash: string
  bytes: number
  omissions: PromptOmission[]
  promptVersion: string
  /** Tập evidenceId hợp lệ mà output được phép tham chiếu. */
  allowedEvidenceIds: string[]
  allowedVideoIds: string[]
  allowedCohortKeys: string[]
}

/**
 * RÀNG BUỘC CỨNG — phần quan trọng nhất của prompt.
 *
 * Câu về impressions/CTR không phải viết cho đẹp: cả ba kênh đều có độ phủ 0%
 * cho hai chỉ số đó, nên mọi kết luận về hiệu quả thumbnail/tiêu đề đều sẽ là
 * bịa. Bộ kiểm định cũng chặn độc lập ở phía sau, nhưng nói rõ ngay trong
 * prompt sẽ rẻ hơn nhiều so với để mô hình viết ra rồi mới từ chối.
 */
function hardConstraints(pkg: AnalysisPackage): string {
  const ctrCoverage = pkg.dataCoverage.metricCoverage['impressions'] ?? 0
  const ctrLine =
    ctrCoverage === 0
      ? 'Impressions và click-through rate KHÔNG CÓ trong phân tích này (độ phủ 0%). ' +
        'KHÔNG được kết luận gì về hiệu quả thumbnail, khả năng hút click của tiêu đề, ' +
        'độ tiếp cận của "packaging", hay tỉ lệ chuyển đổi từ hiển thị. Chủ đề packaging ' +
        'CHỈ được xuất hiện dưới dạng giả thuyết CHƯA KIỂM CHỨNG, và phải nói rõ bằng ' +
        'chứng nào đang thiếu.'
      : `Độ phủ impressions là ${Math.round(ctrCoverage * 100)}%; mọi kết luận về tiếp cận phải nêu rõ mức phủ đó.`

  return [
    ctrLine,
    'Tương quan KHÔNG phải nhân quả.',
    'Thiếu dữ liệu KHÔNG phải bằng 0. Feature có `missingReason` là KHÔNG BIẾT, không phải "kém".',
    'Video chưa đủ chín KHÔNG được đánh giá như video đã chín.',
    'KHÔNG so sánh trực tiếp Shorts với Long-form ngoài phần chuẩn hoá đã cung cấp.',
    'Giá trị phân vị, cohort và đường cơ sở trong gói là CHUẨN — không tính lại, không thay thế.',
    'KHÔNG đưa vào chỉ số nào không có trong gói.',
    'KHÔNG bịa mốc so sánh ngành hay số liệu bên ngoài.',
    'KHÔNG trình bày khuyến nghị như điều đã được chứng minh.',
    'KHÔNG dùng ngôn ngữ nhân quả trừ khi gói có bằng chứng nhân quả (gói này KHÔNG có).',
    'Độ tin cậy PHẢI giảm khi độ phủ dữ liệu yếu.',
    'Tín hiệu mâu thuẫn phải được NÊU RA, không được lấy trung bình cho hoà.',
    '',
    'Từ ngữ BỊ CẤM: "gây ra", "vì", "do", "chứng minh", "dẫn tới", "thumbnail đã thất bại", ' +
      '"tiêu đề làm giảm lượt xem", "giờ đăng tạo ra tăng trưởng", "thuật toán bóp video".',
    'Từ ngữ NÊN DÙNG: "có liên hệ với", "phù hợp với", "có thể cho thấy", "là giả thuyết hợp lý", ' +
      '"không phân biệt được với dữ liệu hiện có", "cần thêm bằng chứng".',
  ].join('\n')
}

/**
 * Sinh danh sách RÀNG BUỘC thẳng từ Zod schema.
 *
 * Viết tay danh sách này là công thức để lệch: schema đổi, prompt không đổi, và
 * mô hình bị từ chối vì một giới hạn chưa ai nói cho nó biết. Chính lỗi đó đã
 * làm hỏng một lần thử ở lô 5 ("Array must contain at most 12 element(s)" —
 * trần lồng nhau chưa từng xuất hiện trong prompt).
 *
 * Đọc trực tiếp từ `_def` nên không thể lệch: đổi schema là prompt đổi theo.
 */
function describeConstraints(node: unknown, path: string, out: string[]): void {
  const def = (node as { _def?: Record<string, unknown> })?._def
  if (!def) return
  const name = def.typeName as string

  if (name === 'ZodDefault' || name === 'ZodOptional' || name === 'ZodNullable') {
    describeConstraints(def.innerType, path, out)
    return
  }
  if (name === 'ZodObject') {
    const shape = (def.shape as () => Record<string, unknown>)()
    for (const [k, v] of Object.entries(shape)) {
      describeConstraints(v, path ? `${path}.${k}` : k, out)
    }
    return
  }
  if (name === 'ZodArray') {
    const min = (def.minLength as { value: number } | null)?.value
    const max = (def.maxLength as { value: number } | null)?.value
    if (min !== undefined || max !== undefined) {
      const lo = min ?? 0
      const hi = max === undefined ? 'không giới hạn' : String(max)
      out.push(`  ${path}: mảng ${lo}..${hi} phần tử`)
    }
    describeConstraints(def.type, `${path}[]`, out)
    return
  }
  if (name === 'ZodString') {
    const checks = (def.checks as Array<{ kind: string; value?: number; regex?: RegExp }>) ?? []
    const min = checks.find((c) => c.kind === 'min')?.value
    const max = checks.find((c) => c.kind === 'max')?.value
    // REGEX cũng phải nêu. Bỏ qua nó là để lại đúng khoảng trống đã gây hỏng
    // hai lô: một ràng buộc có hiệu lực mà mô hình chưa từng được cho biết.
    const re = checks.find((c) => c.kind === 'regex')?.regex
    if (re) {
      out.push(`  ${path}: phải khớp ${String(re)}`)
    } else if (min !== undefined || max !== undefined) {
      out.push(`  ${path}: chuỗi ${min ?? 0}..${max ?? '∞'} ký tự`)
    }
    return
  }
  if (name === 'ZodNumber') {
    const checks = (def.checks as Array<{ kind: string; value: number }>) ?? []
    const min = checks.find((c) => c.kind === 'min')?.value
    const max = checks.find((c) => c.kind === 'max')?.value
    const isInt = checks.some((c) => c.kind === 'int')
    out.push(`  ${path}: ${isInt ? 'số nguyên' : 'số'} ${min ?? '-∞'}..${max ?? '∞'}`)
  }
}

/** Toàn bộ ràng buộc độ dài / số phần tử / khoảng số của schema output. */
export function schemaConstraintLines(): string[] {
  const out: string[] = []
  describeConstraints(cursorOutputSchema, '', out)
  return out
}

/** Bảng `section` / `itemId` / `field` hợp lệ để dán thẳng vào prompt. */
export function sourceRefLines(): string[] {
  return sourceRefSections().map((s) => {
    const itemId = s.kind === 'ITEM' ? `"${s.itemIdExample}"` : '"" (rỗng)'
    const fields = s.fields
      .map((f) => (s.kind === 'INDEXED' ? `${f.name}@N` : f.name) + (f.array ? '[]' : ''))
      .join(', ')
    return `  ${s.section} — itemId ${itemId} — field: ${fields}`
  })
}

function section(title: string, body: string): string {
  return `\n## ${title}\n${body.trim()}\n`
}

/** JSON gọn, khoá đã sắp — giữ prompt tất định. */
function compactJson(value: unknown): string {
  return JSON.stringify(sortKeys(value), null, 1)
}

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys)
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .filter(([, v]) => v !== undefined)
        .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
        .map(([k, v]) => [k, sortKeys(v)]),
    )
  }
  return value
}

/**
 * ID bằng chứng ổn định mà output được phép tham chiếu.
 *
 * Bằng chứng phải ĐỊNH DANH ĐƯỢC thì mới kiểm được: nếu mô hình chỉ viết "theo
 * dữ liệu" thì không có cách nào máy móc để xác minh. Mỗi quan sát, bất thường
 * và video xếp hạng vì thế đều nhận một id ổn định.
 */
export function evidenceIdsFor(pkg: AnalysisPackage): {
  ids: string[]
  observationIds: Map<number, string>
  anomalyIds: Map<number, string>
  videoIds: string[]
  cohortKeys: string[]
} {
  const ids: string[] = []
  const observationIds = new Map<number, string>()
  const anomalyIds = new Map<number, string>()

  pkg.observations.forEach((_, i) => {
    const id = `OBS-${String(i + 1).padStart(3, '0')}`
    observationIds.set(i, id)
    ids.push(id)
  })
  pkg.hypothesisCandidates.forEach((_, i) => {
    ids.push(`HYP-${String(i + 1).padStart(3, '0')}`)
  })
  pkg.anomalies.forEach((_, i) => {
    const id = `ANOM-${String(i + 1).padStart(3, '0')}`
    anomalyIds.set(i, id)
    ids.push(id)
  })
  // Video hợp lệ = danh sách xếp hạng ∪ video được NHẮC TỚI trong các câu quan
  // sát. `rankedVideos` bị cắt ở top-20, nhưng câu quan sát vẫn nêu tên những
  // video ngoài top đó — chúng vẫn thuộc kênh này (gói vốn chỉ chứa một kênh),
  // nên chặn chúng là chặn nhầm. Ở lần chạy thật, Cursor đã đề xuất rà soát một
  // video như vậy và bị từ chối oan.
  const videoIdSet = new Set(pkg.rankedVideos.map((v) => String(v.youtubeVideoId)))
  const YT_IN_TEXT = /\bVideo ([A-Za-z0-9_-]{11})\b/g
  for (const o of [...pkg.observations, ...pkg.hypothesisCandidates]) {
    for (const m of o.statement.matchAll(YT_IN_TEXT)) videoIdSet.add(m[1]!)
  }
  for (const a of pkg.anomalies) {
    const id = (a as { youtubeVideoId?: unknown }).youtubeVideoId
    if (typeof id === 'string') videoIdSet.add(id)
  }
  const videoIds = [...videoIdSet].sort()
  const cohortKeys = pkg.cohortComparisons.map((c) => String((c as { key?: unknown }).key ?? ''))
  for (const v of videoIds) ids.push(`VIDEO-${v}`)
  pkg.baselines.forEach((b) => ids.push(`BASE-${b.key}`))
  pkg.cohortComparisons.forEach((c, i) => ids.push(`COHORT-${String(i + 1).padStart(3, '0')}`))

  return { ids, observationIds, anomalyIds, videoIds, cohortKeys }
}

export function buildPrompt(input: BuildPromptInput): BuiltPrompt {
  const { pkg } = input
  const maxChars = input.maxChars ?? MAX_PROMPT_CHARS
  const omissions: PromptOmission[] = []
  const {
    ids: allowedEvidenceIds,
    observationIds,
    anomalyIds,
    videoIds,
    cohortKeys,
  } = evidenceIdsFor(pkg)

  const parts: string[] = []

  parts.push(
    section(
      'ROLE',
      'Bạn là nhà phân tích tăng trưởng YouTube. Bạn nhận một gói bằng chứng ĐÃ ĐƯỢC TÍNH SẴN ' +
        'bởi một tầng thuật toán tất định. Việc của bạn là SUY LUẬN trên các dữ kiện đó — ' +
        'không tính lại, không dựng lại đường cơ sở, không đi tìm thêm dữ liệu.',
    ),
  )

  parts.push(
    section(
      'OBJECTIVE',
      [
        'Đưa ra phân tích có thể hành động cho MỘT kênh, gồm 5 phần theo thứ tự:',
        '1. Tổng hợp điều hành: tối đa 5 câu — đang xảy ra chuyện gì, mức tin cậy, bằng chứng mạnh nhất, điều CHƯA kết luận được, quyết định tiếp theo quan trọng nhất.',
        '2. Phát hiện có bằng chứng: tách rõ dữ kiện tất định đã cho, diễn giải đa tín hiệu, và giới hạn. KHÔNG lặp lại mọi quan sát tất định.',
        '3. Giả thuyết, xếp theo bằng chứng ủng hộ, mức mâu thuẫn, bằng chứng thiếu và khả năng kiểm chứng.',
        '4. Hành động: tập NHỎ NHẤT các việc giá trị cao. 3 khuyến nghị mạnh tốt hơn 20 gợi ý chung chung.',
        '5. Thí nghiệm và thu thập dữ liệu, tách riêng: thí nghiệm nội dung, cải thiện đo lường, việc cần rà soát thủ công.',
      ].join('\n'),
    ),
  )

  parts.push(section('HARD CONSTRAINTS', hardConstraints(pkg)))

  parts.push(
    section(
      'ANALYSIS SCOPE',
      compactJson({
        channelLabel: pkg.scope.channelLabel,
        channelTitle: pkg.scope.channelTitle,
        reportingTimezone: pkg.scope.reportingTimezone,
        windowStart: pkg.scope.windowStart,
        windowEnd: pkg.scope.windowEnd,
        packageSchemaVersion: pkg.schemaVersion,
        algorithmVersion: pkg.algorithmVersion,
        inputHash: pkg.scope.inputHash,
        promptVersion: PROMPT_VERSION,
        channelSummary: pkg.channelSummary,
      }),
    ),
  )

  parts.push(
    section(
      'DATA COVERAGE',
      compactJson({ coverage: pkg.dataCoverage, confidence: pkg.confidence }),
    ),
  )

  parts.push(
    section(
      'BASELINE DEFINITIONS',
      'Các đường cơ sở này là CHUẨN. Dùng đúng chúng; không tự dựng đường cơ sở khác.\n' +
        compactJson(pkg.baselines.map((b) => ({ evidenceId: `BASE-${b.key}`, ...b }))) +
        '\n\nĐịnh nghĩa feature (công thức đã dùng để tính — chỉ để bạn ĐỌC HIỂU con số, ' +
        'KHÔNG phải để tính lại):\n' +
        compactJson(pkg.featureDefinitions.map((f) => ({ key: f.key, unit: f.unit, formula: f.formula }))),
    ),
  )

  parts.push(
    section(
      'DETERMINISTIC OBSERVATIONS',
      'Mỗi quan sát có một EVIDENCE ID. Trích dẫn id đó trong output.\n' +
        compactJson(
          pkg.observations.map((o, i) => ({
            evidenceId: observationIds.get(i),
            kind: o.kind,
            polarity: o.polarity,
            statement: o.statement,
            metricValues: o.metricValues,
            baselineKind: o.baselineKind,
            percentile: o.percentile,
            deltaRatio: o.deltaRatio,
            confidence: o.confidence,
            limitations: o.limitations,
            videoId: o.videoId,
          })),
        ),
    ),
  )

  parts.push(
    section(
      'RANKED VIDEOS AND COHORTS',
      // Gắn evidenceId TRỰC TIẾP vào từng mục thay vì chỉ mô tả quy tắc bằng
      // lời. Ở lần chạy thật, Cursor đã tự chế "COHORT-<key>" vì phần cohort
      // hiển thị `key` còn id thì chỉ được nêu trong câu dẫn — mô hình suy ra
      // hợp lý, nhưng sai. Dán nhãn sẵn thì không còn gì để suy đoán.
      'Video:\n' +
        compactJson(
          pkg.rankedVideos.map((v) => ({
            evidenceId: `VIDEO-${String(v.youtubeVideoId)}`,
            ...v,
          })),
        ) +
        '\n\nCohort:\n' +
        compactJson(
          pkg.cohortComparisons.map((c, i) => ({
            evidenceId: `COHORT-${String(i + 1).padStart(3, '0')}`,
            ...c,
          })),
        ) +
        (pkg.formatComparison ? '\n\nSo sánh định dạng:\n' + compactJson(pkg.formatComparison) : ''),
    ),
  )

  parts.push(
    section(
      'ANOMALIES',
      pkg.anomalies.length
        ? compactJson(
            pkg.anomalies.map((a, i) => ({ evidenceId: anomalyIds.get(i), ...a })),
          )
        : 'Không phát hiện bất thường nào vượt ngưỡng.',
    ),
  )

  parts.push(
    section(
      'HYPOTHESIS CANDIDATES',
      'Do tầng tất định nêu ra, TẤT CẢ đều CHƯA KIỂM CHỨNG. Hãy đánh giá chúng; ' +
        'không mặc nhiên coi là đúng.\n' +
        compactJson(
          pkg.hypothesisCandidates.map((h, i) => ({
            evidenceId: `HYP-${String(i + 1).padStart(3, '0')}`,
            statement: h.statement,
            question: h.hypothesisQuestion,
            metricValues: h.metricValues,
            limitations: h.limitations,
          })),
        ),
    ),
  )

  parts.push(
    section(
      'MISSING DATA',
      compactJson({
        missingData: pkg.missingData,
        unresolvedQuestions: pkg.unresolvedQuestions,
        limitsApplied: pkg.limitsApplied,
      }),
    ),
  )

  if (input.contentMetadata?.length) {
    parts.push(
      section(
        'CONTENT METADATA (đính kèm tường minh)',
        'Chỉ dùng đúng phần văn bản dưới đây. KHÔNG suy đoán nội dung không có ở đây.\n' +
          compactJson(input.contentMetadata),
      ),
    )
  }

  // Đặt TRƯỚC phần schema: mô hình phải hiểu hợp đồng khai báo rồi mới đọc hình
  // dạng JSON, nếu không nó sẽ điền `metricClaims` như một ô hình thức.
  parts.push(
    section(
      'METRIC CLAIMS (BẮT BUỘC)',
      [
        'Mọi phát biểu có nhắc tới impressions, CTR, thumbnail hoặc packaging — ở BẤT KỲ',
        'trường nào, kể cả risks, limitations, stopConditions, reviewQuestions — phải có',
        'ĐÚNG MỘT mục tương ứng trong `metricClaims`. Văn xuôi được phép giải thích một',
        'claim đã khai, nhưng không được nêu phát biểu mới mà không khai.',
        '',
        'Tách rõ HAI VAI. Đây là phần quan trọng nhất của hợp đồng:',
        '  subjectMetric  = chỉ số ĐANG BỊ PHÁN XÉT (tính từ mô tả nó)',
        '  relatedMetric  = chỉ số chỉ ĐƯỢC NHẮC TỚI, không bị phán xét',
        '',
        'Ví dụ (bám sát các câu thật):',
        '',
        '| câu | subjectMetric | relatedMetric | claimType | assertionStatus |',
        '|---|---|---|---|---|',
        '| "views quá thấp để ổn định CTR" | views | impression_ctr | METHODOLOGY_LIMITATION | LIMITATION |',
        '| "sample size view thấp làm CTR nhiễu" | sample_size | impression_ctr | METHODOLOGY_LIMITATION | LIMITATION |',
        '| "dễ nhầm retention thấp với vấn đề CTR" | retention | impression_ctr | METHODOLOGY_LIMITATION | LIMITATION |',
        '| "so sánh CTR/impressions nhóm high-retention/low-views" | impression_ctr | retention | DIAGNOSTIC_PLAN | CONDITIONAL |',
        '| "nếu CTR thấp + impressions cao sẽ hướng khác nhau" | impression_ctr | NONE | DIAGNOSTIC_PLAN | CONDITIONAL |',
        '| "khi có impressions: CTR thấp hay reach thấp?" | impression_ctr | reach | DIAGNOSTIC_PLAN | QUESTION |',
        '| "ưu tiên retention thay vì đổi thumbnail" | thumbnail | NONE | RECOMMENDATION | NEGATED_ACTION |',
        '| "độ phủ impressions/CTR >0 và observedDates tăng" | data_coverage | impression_ctr | RECOMMENDATION | CONDITIONAL |',
        '| "CTR thấp" | impression_ctr | NONE | OBSERVATION | ASSERTED |',
        '',
        'Ba dòng đầu có subjectMetric KHÁC impression_ctr: chữ "thấp"/"nhiễu" mô tả views,',
        'cỡ mẫu, retention — KHÔNG mô tả CTR. Khai đúng vai là cách duy nhất để những câu',
        'hoàn toàn hợp lệ này không bị hiểu thành kết luận về CTR.',
        '',
        'Chỉ dòng CUỐI là khẳng định. Ở gói này nó sẽ bị TỪ CHỐI (xem ràng buộc dưới).',
        '',
        '### MỘT Ô — MỘT PHÁT BIỂU (quy tắc về CÁCH HÀNH VĂN)',
        '',
        'Đơn vị khai báo là Ô, không phải câu. Ô = một trường chuỗi, hoặc MỘT PHẦN TỬ của',
        'một trường mảng. Mỗi ô chỉ được chứa TỐI ĐA MỘT phát biểu nhắc tới impressions /',
        'CTR / thumbnail / packaging. Bộ kiểm định ĐẾM, không hỏi ý bạn.',
        '',
        'Dấu chấm, chấm phẩy, DẤU HAI CHẤM, dấu phẩy, "nhưng", "còn" đều mở một phát biểu',
        'mới. Hai phát biểu trong một ô bị TỪ CHỐI dù bạn khai bao nhiêu claim đi nữa —',
        'một bản khai không thể mang hai chủ ngữ, hai tình thái, hai chiều phán xét.',
        '',
        'SAI — một ô, hai phát biểu (dấu hai chấm tách chúng ra):',
        '  "limitations": [',
        '    "Khi có impressions/CTR: so sánh CTR và impressions của nhóm high-retention"',
        '  ]',
        '',
        'ĐÚNG — tách thành hai phần tử, mỗi phần tử một claim:',
        '  "limitations": [',
        '    "So sánh impressions của nhóm high-retention/low-views khi có dữ liệu",',
        '    "So sánh CTR của nhóm high-retention/low-views khi có dữ liệu"',
        '  ]',
        '  -> MC-010 sourceRef {KEY_FINDING, F-001, "limitations", 0}, subjectMetric impressions',
        '  -> MC-011 sourceRef {KEY_FINDING, F-001, "limitations", 1}, subjectMetric impression_ctr',
        '',
        'Chú ý cách viết ĐÚNG đưa điều kiện VÀO TRONG cùng một mệnh đề ("... khi có dữ liệu")',
        'thay vì tách bằng dấu hai chấm. Ý nghĩa giữ nguyên, số phát biểu về chỉ số là một.',
        '',
        'TRƯỜNG CHUỖI ĐƠN KHÔNG TÁCH ĐƯỢC. `analysisSummary.*`, `keyFindings[].statement`,',
        '`keyFindings[].supportingReasoning`, `hypotheses[].statement`,',
        '`hypotheses[].validationMethod`, `recommendations[].rationale` — mỗi trường chỉ có',
        'MỘT ô, không có phần tử thứ hai để tách sang. Với chúng, giới hạn "một phát biểu"',
        'là ràng buộc lên ĐỘ DÀI: viết ngắn lại, hoặc chuyển phát biểu thứ hai sang một',
        'trường MẢNG (`limitations`, `risks`, `missingEvidence`, `explicitNonConclusions`).',
        '',
        'SAI — một `validationMethod`, bốn phát biểu chạm chỉ số:',
        '  "Khi có impressions và CTR, so sánh cùng lúc impressions, CTR, avg_view_percentage',
        '   và views_d7 giữa hai nhóm; trước đó chỉ rà soát thủ công."',
        'ĐÚNG — giữ MỘT phát biểu ở đây, phần còn lại đưa xuống `missingEvidence[]`:',
        '  "validationMethod": "So sánh impressions giữa hai nhóm khi có dữ liệu"',
        '  "missingEvidence": ["Chưa có CTR cấp video", "Chưa có impressions cấp video"]',
        '',
        'HAI Ô HAY BỊ QUÊN KHAI nhất, kiểm lại chúng trước khi trả lời:',
        '  - `analysisSummary.overallAssessment` — ô dài nhất output, rất dễ vô tình nhắc',
        '    tới impressions/CTR trong khi mọi claim đều trỏ đi chỗ khác;',
        '  - `keyFindings[].supportingReasoning` — nơi tự nhiên nhất để trích số độ phủ',
        '    ("impressionCtr có metricCoverage=0"), và nhắc tên chỉ số ở đó VẪN cần khai.',
        '',
        'MỘT Ô NHẮC BAO NHIÊU CHỈ SỐ NHẠY CẢM THÌ PHẢI KHAI ĐỦ BẤY NHIÊU.',
        '`subjectMetric` và `relatedMetric` cộng lại chỉ có HAI chỗ. Một ô nhắc tới ba chỉ số',
        'nhạy cảm (ví dụ impressions, CTR và packaging trong cùng một câu) KHÔNG khai đủ được',
        '— đó là dấu hiệu ô đang gộp nhiều phát biểu và phải viết lại. Ví dụ thật bị từ chối:',
        '  "Thiếu impression_ctr không tương đương packaging kém."',
        'Câu này nhắc impression_ctr VÀ packaging, nên phải khai subjectMetric=packaging,',
        'relatedMetric=impression_ctr — không được khai subjectMetric=data_coverage rồi bỏ',
        'trống packaging.',
        '',
        '### sourceRef — TRỎ tới ô, KHÔNG sao chép ô',
        '',
        'Mỗi claim mang `sourceRef` gồm bốn phần:',
        '  { "section": <HẰNG SỐ>, "itemId": <id mục hoặc "">, "field": <tên trường>, "ordinal": <số> }',
        '',
        '  section  — mục đó thuộc phần nào của output (HẰNG SỐ VIẾT HOA ở bảng dưới).',
        '  itemId   — id của mục chứa ô: "F-001", "H-001", "R-001", "E-001".',
        '             CHUỖI RỖNG "" với các section không có id.',
        '  field    — TÊN TRƯỜNG chứa ô, đúng như trong JSON.',
        '  ordinal  — vị trí trong trường MẢNG, đếm từ 0. Với trường chuỗi đơn: 0.',
        '',
        'Ví dụ. Với keyFindings[0] có id "F-001" và',
        '  "limitations": ["cỡ mẫu lượt xem thấp nên CTR nhiễu", "chưa đủ ngày quan sát"]',
        'thì câu thứ NHẤT được trỏ tới bằng:',
        '  "sourceRef": { "section": "KEY_FINDING", "itemId": "F-001",',
        '                 "field": "limitations", "ordinal": 0 }',
        'và câu ở `analysisSummary.primaryConstraint` được trỏ tới bằng:',
        '  "sourceRef": { "section": "ANALYSIS_SUMMARY", "itemId": "",',
        '                 "field": "primaryConstraint", "ordinal": 0 }',
        '',
        'KHÔNG sao chép câu vào claim. Không có trường `text`. Bộ kiểm định tự đọc ô mà',
        'bạn trỏ tới và kiểm ngữ nghĩa TRÊN CHÍNH VĂN BẢN ĐÓ — nên tham chiếu sai là lỗi',
        'nặng hơn nhiều so với diễn đạt vụng.',
        '',
        'GIÁ TRỊ HỢP LỆ (sinh trực tiếp từ schema — không có giá trị nào khác):',
        ...sourceRefLines(),
        '',
        '  `[]` = trường MẢNG: `ordinal` chọn phần tử.',
        '  `@N` = mảng đối tượng cấp cao nhất: thay N bằng chỉ số của mục, đếm từ 0.',
        '         Ví dụ lý do của `manualReviewTargets[1]`: field "reason@1", ordinal 0.',
        '',
        'Ô NHÃN — tình thái do CẤU TRÚC quy định, không do từ ngữ:',
        '  `dataRequests[].metricOrArtifact` -> assertionStatus CONDITIONAL hoặc LIMITATION',
        '  `hypotheses[].missingEvidence`    -> assertionStatus LIMITATION hoặc CONDITIONAL',
        '  `manualReviewTargets[].reviewQuestions` -> assertionStatus QUESTION hoặc CONDITIONAL',
        'Ba ô này nêu dữ liệu CẦN THU THẬP, bằng chứng CÒN THIẾU, và CÂU HỎI rà soát. Chúng',
        'không khẳng định gì về giá trị chỉ số, nên ASSERTED bị CẤM ở đây kể cả khi ô chỉ là',
        'một nhãn trần như "impressions cấp video". Không cần từ điều kiện trong câu — tên',
        'trường đã nói đủ.',
        '',
        'BA LỖI TỪNG LÀM HỎNG CẢ LÔ:',
        '- `section` là HẰNG SỐ VIẾT HOA ở bảng trên. Viết "KEY_FINDING", KHÔNG viết "keyFindings".',
        '- `itemId` phải là id CÓ THẬT trong output của chính bạn, và DUY NHẤT trong section.',
        '  Trỏ tới id không tồn tại thì cả output bị từ chối.',
        '- `ordinal` phải nằm TRONG phạm vi mảng. Trường chuỗi đơn luôn dùng 0.',
        '',
        'Hai phần tử TRÙNG NỘI DUNG trong cùng một trường mảng khiến `ordinal` mất nghĩa;',
        'bộ kiểm định từ chối thay vì đoán. Đừng lặp lại y hệt một câu trong cùng một mảng.',
        '',
        'RÀNG BUỘC CỨNG:',
        '- assertionStatus = ASSERTED với subjectMetric là impressions / impression_ctr /',
        '  thumbnail / packaging sẽ bị TỪ CHỐI khi các chỉ số đó có độ phủ 0%. Không có',
        '  cách diễn đạt nào lách được: quy tắc đọc TRƯỜNG, không đọc câu chữ.',
        '- METHODOLOGY_LIMITATION bắt buộc subjectMetric KHÁC relatedMetric, và',
        '  subjectMetric phải là chỉ số CÓ dữ liệu. Dán nhãn này lên một khẳng định về',
        '  chính chỉ số đang thiếu sẽ bị từ chối.',
        '- claimType = CAUSAL chỉ hợp lệ khi assertionStatus = CONDITIONAL và có evidenceIds.',
        '  CAUSAL + ASSERTED bị cấm tuyệt đối.',
        '- Mọi claim ASSERTED có judgement khác UNKNOWN/NOT_APPLICABLE phải trích evidenceIds',
        '  neo được về bằng chứng trong gói.',
        '- Bằng chứng được trích phải NÓI VỀ chính subjectMetric. "Giải được id" KHÔNG',
        '  đồng nghĩa "ủng hộ kết luận": ít nhất một observation được trích phải nhắc tới',
        '  subjectMetric trong `statement` hoặc trong khoá của `metricValues`. Trích',
        '  OBS-001 (nói về retention) cho một claim về views sẽ bị đánh dấu cần người rà',
        '  soát và KHÔNG được tính là đạt. Chọn đúng quan sát, đừng chọn quan sát gần nhất.',
        '- QUESTION không được mang judgement khẳng định; DIAGNOSTIC_PLAN không được ASSERTED.',
        '',
        'TỰ SOÁT trước khi trả lời:',
        '1. Mỗi Ô có chữ CTR / impressions / thumbnail / packaging trong TOÀN BỘ output đã',
        '   có đúng một metricClaims trỏ tới chưa? (kể cả trong risks, limitations,',
        '   stopConditions, interpretationRisks, reviewQuestions, explicitNonConclusions)',
        '2. Ô nào chứa HAI phát biểu nhạy cảm không? Tách thành hai phần tử.',
        '3. Với mỗi claim: tính từ trong ô đang mô tả subjectMetric, hay mô tả chỉ số khác?',
        '   Nếu là chỉ số khác thì subjectMetric phải là chỉ số ấy.',
        '4. Có claim nào ASSERTED về chỉ số độ phủ 0% không? Nếu có, đổi sang loại đúng',
        '   hoặc bỏ hẳn phát biểu.',
        '5. Mỗi `sourceRef` có trỏ tới một ô CÓ THẬT không? Đọc lại output của bạn và dò',
        '   theo đúng section / itemId / field / ordinal đã khai.',
        '6. Có hai claim nào cùng trỏ vào MỘT ô không? Một ô — một claim.',
      ].join('\n'),
    ),
  )

  parts.push(
    section(
      'REQUIRED OUTPUT SCHEMA',
      [
        `Trả về DUY NHẤT một object JSON, schemaVersion = "${CURSOR_OUTPUT_SCHEMA_VERSION}".`,
        'KHÔNG có văn bản ngoài JSON. KHÔNG dùng khối ```. KHÔNG lời mở đầu, không lời kết.',
        '',
        'Trần mảng: ' +
          `keyFindings<=${OUTPUT_LIMITS.keyFindings}, hypotheses<=${OUTPUT_LIMITS.hypotheses}, ` +
          `recommendations<=${OUTPUT_LIMITS.recommendations}, experiments<=${OUTPUT_LIMITS.experiments}, ` +
          `manualReviewTargets<=${OUTPUT_LIMITS.manualReviewTargets}, dataRequests<=${OUTPUT_LIMITS.dataRequests}.`,
        '',
        'ID theo dạng F-001, H-001, R-001, E-001, MC-001 (đúng ba chữ số).',
        '',
        'MẢNG `metricClaims` — HÌNH DẠNG CHÍNH XÁC. Nêu ĐỦ CẢ 9 trường dưới đây:',
        '  {',
        '    "id": "MC-001",',
        '    "claimType": "OBSERVATION" | "COMPARISON" | "CAUSAL" | "DIAGNOSTIC_PLAN"',
        '                 | "METHODOLOGY_LIMITATION" | "RECOMMENDATION",',
        '    "subjectMetric": "<chỉ số BỊ phán xét>",',
        '    "relatedMetric": "<chỉ số chỉ được NHẮC TỚI, hoặc \"NONE\">",',
        '    "judgement": "HIGH" | "LOW" | "INCREASED" | "DECREASED" | "EFFECTIVE"',
        '                 | "INEFFECTIVE" | "UNKNOWN" | "NOT_APPLICABLE",',
        '    "assertionStatus": "ASSERTED" | "CONDITIONAL" | "QUESTION"',
        '                       | "NEGATED_ACTION" | "LIMITATION",',
        '    "evidenceIds": ["OBS-001"],',
        '    "requiresMissingnessDisclosure": true | false,',
        '    "sourceRef": {',
        '      "section": "ANALYSIS_SUMMARY" | "KEY_FINDING" | "HYPOTHESIS"',
        '                 | "RECOMMENDATION" | "EXPERIMENT" | "MANUAL_REVIEW"',
        '                 | "DATA_REQUEST" | "NON_CONCLUSION",',
        '      "itemId": "F-001",   // id mục chứa ô; chuỗi RỖNG "" nếu section không có id',
        '      "field": "limitations",',
        '      "ordinal": 0',
        '    }',
        '  }',
        '',
        'Giá trị hợp lệ cho subjectMetric và relatedMetric (dùng ĐÚNG chuỗi này):',
        `  ${CLAIM_METRICS.join(', ')}`,
        '',
        'LƯU Ý HAY SAI:',
        '- `sourceRef.section` dùng HẰNG SỐ VIẾT HOA ở trên, KHÔNG phải tên trường JSON.',
        '  Viết "KEY_FINDING", KHÔNG viết "keyFindings".',
        '- `id` là BẮT BUỘC và phải theo dạng MC-001, MC-002, … (đúng ba chữ số).',
        '- KHÔNG có trường `text`. Đừng sao chép câu vào claim; hãy TRỎ tới nó bằng',
        '  `sourceRef`. Trường lạ khiến toàn bộ output bị từ chối.',
        '- Một Ô -> đúng MỘT claim; một claim -> đúng MỘT ô.',
        '- Mảng rỗng `"metricClaims": []` là hợp lệ khi output không nhắc tới',
        '  impressions/CTR/thumbnail/packaging ở bất kỳ đâu.',
        '',
        'RÀNG BUỘC ĐỘ DÀI VÀ SỐ PHẦN TỬ (sinh trực tiếp từ schema — vi phạm là bị từ chối):',
        ...schemaConstraintLines(),
        '',
        'Mọi evidenceIds PHẢI sao chép NGUYÊN VĂN từ trường "evidenceId" của các mục ở trên. ' +
          'KHÔNG tự ghép id theo quy tắc suy đoán.',
        'hypotheses[].status luôn là "UNVERIFIED".',
        'manualReviewTargets[].targetId: nếu targetType=VIDEO thì phải là một youtubeVideoId ' +
          'trong RANKED VIDEOS; nếu targetType=COHORT thì phải là một khoá cohort trong phần cohort.',
        '',
        'Cấu trúc:',
        compactJson({
          schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
          analysisSummary: {
            overallAssessment: 'string',
            confidence: 'LOW|MEDIUM|HIGH',
            confidenceRationale: 'string',
            primaryConstraint: 'string',
          },
          keyFindings: [
            {
              id: 'F-001',
              statement: 'string',
              findingType: 'OBSERVATION|SYNTHESIS|LIMITATION',
              confidence: 'LOW|MEDIUM|HIGH',
              evidenceIds: ['OBS-001'],
              supportingReasoning: 'string',
              contradictingEvidenceIds: [],
              limitations: [],
            },
          ],
          hypotheses: [
            {
              id: 'H-001',
              statement: 'string',
              status: 'UNVERIFIED',
              confidence: 'LOW|MEDIUM|HIGH',
              supportingEvidenceIds: ['OBS-001'],
              contradictingEvidenceIds: [],
              missingEvidence: ['string'],
              validationMethod: 'string',
            },
          ],
          recommendations: [
            {
              id: 'R-001',
              action: 'string',
              priority: 'P0|P1|P2',
              category: 'CONTINUE|STOP|INVESTIGATE|TEST|COLLECT_DATA',
              rationale: 'string',
              evidenceIds: ['OBS-001'],
              expectedValue: 'LOW|MEDIUM|HIGH',
              effort: 'LOW|MEDIUM|HIGH',
              reversibility: 'LOW|MEDIUM|HIGH',
              measurementFeasibility: 'LOW|MEDIUM|HIGH',
              risks: [],
              successMetric: 'string',
            },
          ],
          experiments: [
            {
              id: 'E-001',
              hypothesisId: 'H-001',
              change: 'string',
              baseline: 'string',
              successMetrics: ['string'],
              minimumWindowDays: 14,
              sampleLimitations: [],
              stopConditions: ['string'],
              interpretationRisks: ['string'],
            },
          ],
          manualReviewTargets: [
            {
              targetType: 'VIDEO|COHORT',
              targetId: 'youtubeVideoId nếu VIDEO, khoá cohort nếu COHORT',
              reason: 'string',
              evidenceIds: [],
              reviewQuestions: ['string'],
            },
          ],
          dataRequests: [
            { metricOrArtifact: 'string', reason: 'string', decisionUnlocked: 'string' },
          ],
          explicitNonConclusions: ['string'],
          selfCheck: {
            usedOnlyProvidedEvidence: true,
            recomputedMetrics: false,
            madeCausalClaims: false,
            madeCtrOrImpressionClaims: false,
            allFindingEvidenceResolved: true,
          },
        }),
      ].join('\n'),
    ),
  )

  parts.push(
    section(
      'QUALITY CHECKLIST',
      [
        'Trước khi trả lời, tự kiểm:',
        '- Mọi phát hiện dạng dữ kiện đều trích evidence id có thật? (LIMITATION được phép không có)',
        '- Có câu nào nói nhân quả trong khi chỉ có tương quan không?',
        '- Có kết luận nào về thumbnail/CTR/impressions không? (bị CẤM ở gói này)',
        '- Có con số nào không xuất hiện trong gói không?',
        '- Mọi giả thuyết còn ở trạng thái UNVERIFIED?',
        '- Mọi khuyến nghị đều đo được, hoặc được đánh dấu rõ là INVESTIGATE?',
        '- Mỗi P0 có thực sự đủ bằng chứng mạnh VÀ cấp thiết trong thực tế?',
        '- Mỗi thí nghiệm có nêu chỉ số thành công và rủi ro diễn giải sai?',
        '- Độ tin cậy đã hạ xuống ở nơi bằng chứng mâu thuẫn hoặc thưa?',
        '- explicitNonConclusions có nêu đúng những gì KHÔNG kết luận được?',
      ].join('\n'),
    ),
  )

  // Nêu tường minh phần đã lược bỏ. Mô hình phải biết nó đang nhìn danh sách
  // đã bị cắt, nếu không nó sẽ coi phần thấy được là toàn bộ.
  if (input.declaredOmissions?.length) {
    parts.push(
      section(
        'OMITTED EVIDENCE',
        [
          'Các phần sau đã bị LƯỢC BỎ khỏi prompt này do giới hạn kích thước.',
          'Danh sách bạn thấy KHÔNG đầy đủ. Không kết luận gì về những mục không xuất hiện,',
          'và hạ độ tin cậy ở nơi kết luận phụ thuộc vào tính đầy đủ của danh sách.',
          '',
          ...input.declaredOmissions.map(
            (o) => `- ${o.section}: bỏ ${o.omittedCount} mục (${o.reason})`,
          ),
        ].join('\n'),
      ),
    )
  }

  let text = parts.join('\n')

  // Chạm trần: bỏ theo thứ tự ƯU TIÊN THẤP TRƯỚC, và ghi lại từng lần bỏ.
  // Không bao giờ cắt cụt giữa chừng — cắt cụt sẽ để lại JSON hỏng hoặc bằng
  // chứng mất một nửa mà không ai biết.
  // `declaredOmissions` đã có nghĩa là ĐANG ở lần dựng lại — không cắt nữa,
  // nếu không sẽ tự gọi mình vô hạn.
  if (text.length > maxChars && !input.declaredOmissions) {
    const trimmablePackage: AnalysisPackage = {
      ...pkg,
      rankedVideos: pkg.rankedVideos.slice(0, 10),
      cohortComparisons: pkg.cohortComparisons.slice(0, 6),
    }
    omissions.push({
      section: 'RANKED VIDEOS AND COHORTS',
      omittedCount:
        pkg.rankedVideos.length - trimmablePackage.rankedVideos.length +
        (pkg.cohortComparisons.length - trimmablePackage.cohortComparisons.length),
      reason: `Prompt ${text.length} ký tự vượt trần ${maxChars}`,
      priority: 'SUPPORTING',
      mayAffectConclusions: true,
    })
    // Dựng lại KÈM thông báo lược bỏ, và vẫn giữ nguyên trần.
    //
    // Bản trước truyền `Number.MAX_SAFE_INTEGER` nên bản dựng lại không còn bị
    // chặn bởi trần nào — một cái trần mà không chặn gì thì tệ hơn không có,
    // vì nó tạo cảm giác đã có giới hạn.
    const rebuilt = buildPrompt({
      ...input,
      pkg: trimmablePackage,
      maxChars,
      declaredOmissions: omissions,
    })
    text = rebuilt.text
  }

  // Trần phải là trần THẬT: vượt thì báo lỗi, không im lặng chấp nhận.
  if (text.length > maxChars) {
    throw new Error(
      `Prompt vượt trần: ${text.length} > ${maxChars} ký tự. ` +
        `Gói bằng chứng quá lớn — cần siết giới hạn ở tầng đóng gói (Phase 3).`,
    )
  }

  return {
    text,
    hash: createHash('sha256').update(text, 'utf8').digest('hex'),
    bytes: Buffer.byteLength(text, 'utf8'),
    omissions,
    promptVersion: PROMPT_VERSION,
    allowedEvidenceIds,
    allowedVideoIds: videoIds,
    allowedCohortKeys: cohortKeys,
  }
}

/**
 * Prompt SỬA LỖI cho lần thử lại.
 *
 * Cố ý chỉ chứa: lỗi kiểm định, hợp đồng nhiệm vụ gốc, và output sai (đã cắt
 * ngắn). KHÔNG gửi lại toàn bộ bằng chứng — vừa tốn, vừa mở đường cho mô hình
 * đổi luôn cả kết luận thay vì chỉ sửa lỗi định dạng.
 */
export function buildRepairPrompt(params: {
  errors: string[]
  invalidOutput: string
  maxOutputChars?: number
}): { text: string; hash: string; truncated: boolean } {
  // Trần 60k, KHÔNG phải 8k.
  //
  // Prompt sửa lỗi cố ý không gửi lại bằng chứng — mục đích là sửa định dạng,
  // không phải phân tích lại. Nhưng nếu output cũ bị cắt mất phần lớn, mô hình
  // buộc phải VIẾT LẠI phần nó không còn nhìn thấy, mà lại không có bằng chứng
  // trong tay. Đó là công thức để bịa ra kết luận mới rồi vô tình vượt kiểm
  // định. Output thật quan sát được khoảng 26–30 KB, nên 60k đủ chứa trọn vẹn.
  //
  // Khi vẫn phải cắt, `truncated` được trả về để bên gọi TỪ CHỐI thử lại, thay
  // vì thử lại trong điều kiện gần như chắc chắn sinh nội dung bịa.
  // Trần phải đủ chứa payload LỚN NHẤT mà schema cho phép.
  //
  // 120 claim x ~600 ký tự text (chưa kể phần còn lại) có thể vượt 60k, khiến
  // một output hợp lệ bị từ chối sửa lỗi kỹ thuật — từ chối oan. Trần prompt
  // tổng thể là 200k nên 150k vẫn còn chỗ cho phần khung.
  const cap = params.maxOutputChars ?? 150_000
  const truncated = params.invalidOutput.length > cap
  const excerpt = truncated
    ? `${params.invalidOutput.slice(0, cap)}\n...[đã cắt bớt]`
    : params.invalidOutput

  const text = [
    '## SỬA LẠI OUTPUT JSON',
    '',
    'Output trước đó KHÔNG hợp lệ. Các lỗi cần sửa:',
    ...params.errors.map((e, i) => `${i + 1}. ${e}`),
    '',
    '## HỢP ĐỒNG NHIỆM VỤ (không đổi)',
    `Trả về DUY NHẤT một object JSON, schemaVersion = "${CURSOR_OUTPUT_SCHEMA_VERSION}".`,
    'KHÔNG văn bản ngoài JSON. KHÔNG khối ```. KHÔNG lời mở đầu hay lời kết.',
    'Giữ nguyên các kết luận phân tích; CHỈ sửa những lỗi liệt kê ở trên.',
    'metricClaims phải GIỮ NGUYÊN: cùng id, cùng subjectMetric/relatedMetric,',
    'cùng claimType/assertionStatus/judgement, cùng evidenceIds. KHÔNG thêm,',
    'KHÔNG bớt, KHÔNG đổi bằng chứng. Chỉ được sửa cú pháp và cách diễn đạt.',
    'sourceRef phải giữ nguyên section + itemId + field. Chỉ `ordinal` được đổi,',
    'và chỉ khi bạn đảo thứ tự phần tử trong chính trường mảng đó.',
    'VĂN BẢN của ô được trỏ tới KHÔNG được đổi — kể cả viết lại cho gọn, kể cả',
    'đổi một con số. Sửa định dạng thì đừng chạm vào nội dung.',
    'Mọi evidenceIds phải nằm trong danh sách hợp lệ đã cho ở lần trước.',
    '',
    '## OUTPUT KHÔNG HỢP LỆ',
    excerpt,
    '',
    'Trả về JSON đã sửa, và chỉ JSON.',
  ].join('\n')

  return { text, hash: createHash('sha256').update(text, 'utf8').digest('hex'), truncated }
}
