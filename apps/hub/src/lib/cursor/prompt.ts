import { createHash } from 'node:crypto'

import type { AnalysisPackage } from '../analysis/package'
import {
  ANALYSIS_SCHEMA_VERSION,
  cursorAnalysisSchema,
  OUTPUT_LIMITS,
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
export const ANALYSIS_PROMPT_VERSION = '4.0.0'

/**
 * 4.0.0 — prompt lượt PHÂN TÍCH, chỉ VĂN XUÔI.
 *
 * 3.0.0 vẫn bắt mô hình vừa viết vừa KHAI BÁO. Bốn lần thăm dò cho thấy nó trỏ
 * `sourceRef` đúng 100% nhưng đếm sót ô phải khai, dao động 2–19 lỗi và nghịch
 * chiều với số claim nó viết. 4.0.0 bỏ hẳn phần khai báo khỏi prompt này: việc
 * đếm ô là việc sổ sách, và `enumerateUnits` tính được nó tất định.
 *
 * Hệ quả với chính prompt: mọi đặc tả `metricClaims`, `sourceRef`, bảng
 * section/field và quy tắc một-ô-một-phát-biểu ĐÃ ĐƯỢC GỠ khỏi đây. Chúng sống ở
 * `declaration-prompt.ts`.
 */
export const PROMPT_VERSION = ANALYSIS_PROMPT_VERSION

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
  describeConstraints(cursorAnalysisSchema, '', out)
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

  // U1 VẪN được cưỡng chế ở lượt PHÂN TÍCH, nên mô hình phải được cho biết.
  //
  // Khi gỡ hợp đồng khai báo khỏi prompt này, quy tắc một-ô-một-phát-biểu suýt
  // bị gỡ theo — nhưng nó là quy tắc VĂN XUÔI, không phải quy tắc khai báo, và
  // bộ kiểm định chặng ANALYSIS vẫn chặn. Một ràng buộc có hiệu lực mà prompt
  // không nói là đúng khoảng trống đã làm hỏng hai lô trước.
  parts.push(
    section(
      'MỘT Ô — MỘT PHÁT BIỂU',
      [
        'Mỗi Ô văn bản chỉ được chứa TỐI ĐA MỘT phát biểu nhắc tới impressions /',
        'CTR / thumbnail / packaging. Ô = một trường chuỗi, hoặc MỘT PHẦN TỬ của',
        'một trường mảng. Bộ kiểm định ĐẾM, không hỏi ý bạn.',
        '',
        'Dấu chấm, chấm phẩy, DẤU HAI CHẤM và các liên từ "nhưng"/"còn"/"đồng thời"/',
        '"trong khi"/"tuy nhiên" đều mở một phát biểu mới.',
        '',
        'SAI — một ô, hai phát biểu (dấu hai chấm tách chúng ra):',
        '  "limitations": [',
        '    "Khi có impressions/CTR: so sánh CTR và impressions của nhóm high-retention"',
        '  ]',
        '',
        'ĐÚNG — tách thành hai phần tử:',
        '  "limitations": [',
        '    "So sánh impressions của nhóm high-retention/low-views khi có dữ liệu",',
        '    "So sánh CTR của nhóm high-retention/low-views khi có dữ liệu"',
        '  ]',
        '',
        'Cách viết ĐÚNG đưa điều kiện VÀO TRONG cùng một mệnh đề ("... khi có dữ',
        'liệu") thay vì tách bằng dấu hai chấm. Ý nghĩa giữ nguyên, số phát biểu là một.',
        '',
        'TRƯỜNG CHUỖI ĐƠN KHÔNG TÁCH ĐƯỢC. `analysisSummary.*`,',
        '`keyFindings[].statement`, `keyFindings[].supportingReasoning`,',
        '`hypotheses[].statement`, `hypotheses[].validationMethod`,',
        '`recommendations[].rationale` chỉ có MỘT ô. Với chúng, giới hạn này là ràng',
        'buộc lên ĐỘ DÀI: viết ngắn lại, hoặc chuyển phát biểu thứ hai sang một',
        'trường MẢNG (`limitations`, `risks`, `missingEvidence`, `explicitNonConclusions`).',
      ].join('\n'),
    ),
  )

  parts.push(
    section(
      'REQUIRED OUTPUT SCHEMA',
      [
        `Trả về DUY NHẤT một object JSON, schemaVersion = "${ANALYSIS_SCHEMA_VERSION}".`,
        'KHÔNG có văn bản ngoài JSON. KHÔNG dùng khối ```. KHÔNG lời mở đầu, không lời kết.',
        '',
        'Trần mảng: ' +
          `keyFindings<=${OUTPUT_LIMITS.keyFindings}, hypotheses<=${OUTPUT_LIMITS.hypotheses}, ` +
          `recommendations<=${OUTPUT_LIMITS.recommendations}, experiments<=${OUTPUT_LIMITS.experiments}, ` +
          `manualReviewTargets<=${OUTPUT_LIMITS.manualReviewTargets}, dataRequests<=${OUTPUT_LIMITS.dataRequests}.`,
        '',
        'ID theo dạng F-001, H-001, R-001, E-001, MC-001 (đúng ba chữ số).',
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
          schemaVersion: ANALYSIS_SCHEMA_VERSION,
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
    `Trả về DUY NHẤT một object JSON, schemaVersion = "${ANALYSIS_SCHEMA_VERSION}".`,
    'KHÔNG văn bản ngoài JSON. KHÔNG khối ```. KHÔNG lời mở đầu hay lời kết.',
    'Giữ nguyên các kết luận phân tích; CHỈ sửa những lỗi liệt kê ở trên.',
    'KHÔNG có `metricClaims` trong output này. Lượt PHÂN TÍCH chỉ sinh văn xuôi;',
    'phần khai báo ngữ nghĩa là một LƯỢT RIÊNG, chạy sau, trên chính văn bản này.',
    'Thêm `metricClaims` vào đây sẽ khiến toàn bộ output bị từ chối.',
    'Mọi evidenceIds phải nằm trong danh sách hợp lệ đã cho ở lần trước.',
    '',
    '## OUTPUT KHÔNG HỢP LỆ',
    excerpt,
    '',
    'Trả về JSON đã sửa, và chỉ JSON.',
  ].join('\n')

  return { text, hash: createHash('sha256').update(text, 'utf8').digest('hex'), truncated }
}
