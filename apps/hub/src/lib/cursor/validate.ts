import type { AnalysisPackage } from '../analysis/package'
import {
  enumerateUnits,
  findDuplicateItemIds,
  resolveSourceRef,
  type ResolvedUnit,
} from './source-ref'
import {
  CURSOR_OUTPUT_SCHEMA_VERSION,
  cursorOutputSchema,
  LEGACY_SCHEMA_VERSIONS,
  OUTPUT_LIMITS,
  type CursorOutput,
} from './schema'

/**
 * Kiểm định output của Cursor.
 *
 * Nguyên tắc: JSON hợp lệ KHÔNG có nghĩa là nội dung đáng tin. Bộ kiểm định
 * này chạy ĐỘC LẬP với `selfCheck` mà mô hình tự khai, và có quyền phủ quyết —
 * mô hình khai "không có câu nhân quả" mà văn bản vẫn có thì bản khai đó sai,
 * và chính điều đó được ghi lại.
 *
 * Kết quả kiểm định lưu TÁCH RIÊNG khỏi output gốc. Không bao giờ sửa output
 * của Cursor rồi trình bày như bản gốc.
 */

export type IssueSeverity = 'BLOCKER' | 'HIGH' | 'MEDIUM' | 'LOW'

export interface ValidationIssue {
  rule: string
  severity: IssueSeverity
  message: string
  path?: string
  /**
   * Đoạn văn bản đã gây vi phạm (có cắt ngắn).
   *
   * Không có nó, báo cáo chỉ nói "có ngôn ngữ nhân quả" mà không nói ở CÂU NÀO
   * — muốn biết phải chạy lại LLM, mỗi lần vài phút. Đây là output của chính
   * Cursor nên không có rủi ro lộ bí mật.
   */
  excerpt?: string
}

/**
 * Có nhắc tới chỉ số NHẠY CẢM hay không — chỉ để hỏi "đã khai chưa".
 *
 * Cố ý RỘNG và NGU: nó không cần biết ai bổ nghĩa cho ai, chỉ cần biết câu này
 * có chạm tới vùng nhạy cảm. Mọi phán xét ngữ nghĩa nằm ở `metricClaims`.
 */
const SENSITIVE_MENTION =
  /(?:ctr|click-?through|impressions?|thumbnail|hình thu nhỏ|tỉ lệ nhấp|packaging)/iu

/**
 * Chỉ số nhạy cảm nào ĐƯỢC NHẮC TỚI trong câu.
 *
 * Dùng để buộc claim đã khai phải nói về ĐÚNG chỉ số mà câu nhắc tới. Không
 * suy đoán ngữ pháp — chỉ đối chiếu tên chỉ số, hoàn toàn tất định.
 */
/**
 * Dấu hiệu BỀ MẶT của từng trạng thái khẳng định.
 *
 * Đây KHÔNG phải quay lại đoán ngữ pháp. Nó không hỏi "tính từ bổ nghĩa cho ai"
 * — câu hỏi khó đã được `subjectMetric` trả lời. Nó chỉ hỏi một câu dễ và tất
 * định: mô hình khai câu này là ĐIỀU KIỆN, vậy trong câu có dấu hiệu điều kiện
 * nào không?
 *
 * Không có phép kiểm này, tự khai trở thành lời nói suông: cứ dán
 * CONDITIONAL lên "CTR hiện tại thấp" là thoát mọi quy tắc.
 */
/**
 * Dấu hiệu BỀ MẶT của từng phán xét, theo hai cực đối lập.
 *
 * Ca thật Codex dựng: câu nói "CTR cao", claim khai `judgement: LOW`. Khớp từ
 * vựng 1.0, phân cực đồng ý, và payload đi qua với KẾT LUẬN NGƯỢC HẲN nội dung.
 * Kiểm chủ ngữ thôi là chưa đủ — phải kiểm cả CHIỀU.
 */
const JUDGEMENT_MARKERS: Record<string, { self: RegExp; opposite: RegExp }> = {
  HIGH: {
    self: /(?:\bcao\b|\btốt\b|\bmạnh\b|vượt trội|\bhigh\b|\bstrong\b|\bgood\b)/iu,
    opposite: /(?:\bthấp\b|\bkém\b|\byếu\b|\blow\b|\bpoor\b|\bweak\b)/iu,
  },
  LOW: {
    self: /(?:\bthấp\b|\bkém\b|\byếu\b|\blow\b|\bpoor\b|\bweak\b)/iu,
    opposite: /(?:\bcao\b|\btốt\b|\bmạnh\b|vượt trội|\bhigh\b|\bstrong\b|\bgood\b)/iu,
  },
  INCREASED: {
    self: /(?:\btăng\b|cải thiện|\bincreased?\b|\bimproved?\b|\bgrew\b)/iu,
    opposite: /(?:\bgiảm\b|sụt|\bdecreased?\b|\bdropped\b|\bfell\b)/iu,
  },
  DECREASED: {
    self: /(?:\bgiảm\b|sụt|\bdecreased?\b|\bdropped\b|\bfell\b)/iu,
    opposite: /(?:\btăng\b|cải thiện|\bincreased?\b|\bimproved?\b|\bgrew\b)/iu,
  },
  EFFECTIVE: {
    self: /(?:hiệu quả|\btốt\b|\beffective\b)/iu,
    opposite: /(?:không hiệu quả|\bkém\b|\bineffective\b)/iu,
  },
  INEFFECTIVE: {
    self: /(?:không hiệu quả|\bkém\b|\bineffective\b)/iu,
    opposite: /(?:\bhiệu quả\b|\beffective\b)/iu,
  },
}

const MODALITY_MARKERS: Record<string, RegExp> = {
  CONDITIONAL:
    /(?:nếu|khi nào|khi có|sau khi|một khi|giả sử|sẽ|nếu như|\bif\b|\bwhen\b|\bonce\b|\bshould\b|>\s*0|>=|đạt|mục tiêu|target|cần đo|cần thu thập)/iu,
  QUESTION: /\?\s*$|(?:có phải|hay là|liệu|\bwhether\b)/iu,
  NEGATED_ACTION: /(?:thay vì|không|chưa|tránh|đừng|instead of|avoid|\bnot\b|\bno\b)/iu,
  LIMITATION: /(?:nhiễu|không ổn định|chưa đủ|không đủ|hạn chế|giới hạn|độ tin cậy|khó|dễ nhầm|chưa thể|không thể|noisy|unstable|insufficient|limitation|unreliable|0\s*%|quá thấp để|thấp để)/iu,
}

/** Tên chỉ số (kể cả cách gọi tiếng Việt) có xuất hiện trong câu không. */
const METRIC_ALIASES: Record<string, RegExp> = {
  impressions: /impressions?|lượt hiển thị/iu,
  impression_ctr: /\bctr\b|click-?through|tỉ lệ nhấp|tỷ lệ nhấp|tỷ lệ click|tỉ lệ click/iu,
  thumbnail: /thumbnail|hình thu nhỏ|ảnh đại diện/iu,
  packaging: /packaging|đóng gói/iu,
  views: /\bviews?\b|lượt xem/iu,
  views_d7: /views_d7|\bviews?\b|lượt xem/iu,
  retention: /retention|giữ chân|avp|average_view_percentage/iu,
  average_view_percentage: /average_view_percentage|avp|retention|giữ chân/iu,
  watch_time: /watch_?time|thời lượng xem|thời gian xem/iu,
  reach: /reach|tiếp cận/iu,
  subscribers: /subscribers?|đăng ký|người theo dõi|người đăng ký/iu,
  engagement: /engagement|tương tác/iu,
  sample_size: /sample.?size|cỡ mẫu|số lượng mẫu|\bn\b|số video/iu,
  publish_cadence: /cadence|nhịp đăng|tần suất/iu,
  data_coverage: /coverage|độ phủ|dữ liệu|data/iu,
}

function metricNamedIn(metric: string, text: string): boolean {
  const re = METRIC_ALIASES[metric]
  return re ? re.test(text) : true
}

function mentionedSensitiveMetrics(text: string): Set<string> {
  const out = new Set<string>()
  if (/(?:\bctr\b|click-?through|tỉ lệ nhấp)/iu.test(text)) out.add('impression_ctr')
  if (/impressions?/iu.test(text)) out.add('impressions')
  if (/(?:thumbnail|hình thu nhỏ)/iu.test(text)) out.add('thumbnail')
  if (/packaging/iu.test(text)) out.add('packaging')
  return out
}

/**
 * Hai chuỗi có cùng NỘI DUNG đáng kể hay không.
 *
 * Dùng để nối một câu văn xuôi với claim đã khai. Không đòi giống hệt: mô hình
 * có thể cắt bớt khi đưa vào `text`. Ngưỡng đặt ở mức "đa số từ nội dung trùng".
 *
 * GIỚI HẠN TIN CẬY, ghi rõ ở đây: phép nối này là HEURISTIC. Nó không chứng
 * minh được `text` của claim đúng là câu trong văn xuôi. Nó chỉ chặn trường hợp
 * QUÊN KHAI. Việc khai SAI ngữ nghĩa được chặn bằng các quy tắc tất định trên
 * trường, và bằng rà soát thủ công — không bằng hàm này.
 */
/**
 * Tách một ô văn bản thành các MỆNH ĐỀ.
 *
 * Dùng để đếm "một ô có mấy phát biểu về chỉ số nhạy cảm". Đây là HEURISTIC
 * NGÔN NGỮ, không phải phân tích cú pháp — ranh giới này được ghi rõ ở
 * creator_specs/PHASE4_TRUST_BOUNDARIES.md và không được trình bày là tất định.
 */
export function clausesOf(text: string): string[] {
  return text
    .split(/[.!?;:\n]|,\s+|\s+\bnhưng\b\s+|\s+\bvà\b\s+|\s+\bcòn\b\s+/iu)
    .map((x) => x.trim())
    .filter(Boolean)
}

/** Cắt một đoạn quanh vị trí khớp, để báo cáo chỉ đúng chỗ sai. */
function excerptAround(text: string, match: RegExpExecArray | null, span = 90): string {
  if (!match) return text.slice(0, span * 2)
  const start = Math.max(0, match.index - span)
  const end = Math.min(text.length, match.index + match[0].length + span)
  return (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '')
}

export interface ValidationReport {
  passed: boolean
  structuralIssues: ValidationIssue[]
  evidenceIssues: ValidationIssue[]
  claimIssues: ValidationIssue[]
  qualityIssues: ValidationIssue[]
  evidenceResolutionRate: number | null
  totalEvidenceRefs: number
  unresolvedEvidenceRefs: number
  causalViolations: number
  ctrViolations: number
  unsupportedMetricViolations: number
  counts: {
    findings: number
    hypotheses: number
    recommendations: number
    experiments: number
  }
}

/**
 * Cụm từ nhân quả bị cấm.
 *
 * Dùng biên từ (`\b` hoặc khoảng trắng) chứ không tìm chuỗi con: "do" là chuỗi
 * con của "doanh thu", "độ dài", "do dự"..., và tìm thô sẽ sinh ra hàng loạt
 * báo động giả rồi khiến cả bộ kiểm định bị bỏ qua.
 */
/**
 * Danh từ chỉ KẾT QUẢ HIỆU SUẤT.
 *
 * "A làm giảm B" chỉ là khẳng định nhân quả đáng chặn khi B là một kết quả hiệu
 * suất. Câu "độ đầy đủ dữ liệu thấp làm giảm ĐỘ TIN CẬY" nói về PHƯƠNG PHÁP, và
 * đó chính là kiểu lập luận ta MUỐN mô hình đưa ra — chặn nó là dạy nó nói mơ hồ.
 * Ví dụ thật đã bị báo động giả:
 *   "dateCompleteness thấp làm giảm tin cậy xu hướng kênh"
 */
const PERF_OBJECT =
  '(?:lượt xem|view\\w*|retention|giữ chân|tiếp cận|reach|đăng ký|subscriber\\w*|tương tác|engagement|hiệu suất|performance|thứ hạng|ranking|ctr|impressions?)'

const CAUSAL_PATTERNS: Array<{ re: RegExp; label: string }> = [
  { re: /\bgây ra\b/iu, label: 'gây ra' },
  { re: /\bdẫn (?:tới|đến)\b/iu, label: 'dẫn tới' },
  { re: /\bchứng minh (?:rằng|là)\b/iu, label: 'chứng minh rằng' },
  { re: /\bnguyên nhân là\b/iu, label: 'nguyên nhân là' },
  {
    re: new RegExp(`\\blàm (?:giảm|tăng)\\s+(?:\\S+\\s+){0,2}?${PERF_OBJECT}`, 'iu'),
    label: 'làm giảm/tăng <hiệu suất>',
  },
  {
    re: new RegExp(`\\bkhiến (?:cho\\s+)?(?:\\S+\\s+){0,3}?${PERF_OBJECT}\\s+(?:giảm|tăng)`, 'iu'),
    label: 'khiến <hiệu suất> giảm/tăng',
  },
  { re: /\bdo\s+(?:tiêu đề|thumbnail|giờ đăng|thuật toán)\b/iu, label: 'do <yếu tố>' },
  { re: /\bvì\s+(?:tiêu đề|thumbnail|giờ đăng|thuật toán)\b/iu, label: 'vì <yếu tố>' },
  { re: /\bcaused\b/i, label: 'caused' },
  { re: /\bbecause of\b/i, label: 'because of' },
  { re: /\bresulted from\b/i, label: 'resulted from' },
  { re: /\bproved?\b(?!\s*(?:n't|not))/i, label: 'proved' },
  { re: /\bled to\b/i, label: 'led to' },
  { re: /\bdue to\b/i, label: 'due to' },
  { re: /\bthe (?:thumbnail|title) failed\b/i, label: 'the thumbnail/title failed' },
  { re: /\balgorithm (?:suppressed|penalized|throttled)\b/i, label: 'algorithm suppressed' },
]

/**
 * Cụm từ về impressions/CTR/packaging bị cấm khi độ phủ = 0.
 *
 * Chỉ chặn KẾT LUẬN, không chặn việc NHẮC TỚI: câu "không có dữ liệu CTR nên
 * chưa kết luận được" là đúng đắn và phải được phép. Vì thế các mẫu dưới đây
 * đều nhắm vào lời khẳng định, và có bộ lọc phủ định ở `mentionsMissingness`.
 */
/**
 * Biên từ HIỂU UNICODE.
 *
 * `\b` chỉ tính theo `\w` = [A-Za-z0-9_]. Mọi cụm tiếng Việt kết thúc bằng chữ
 * có dấu — "hiệu quả", "hình thu nhỏ" — khi bọc trong `\b...\b` sẽ thành NHÁNH
 * CHẾT: không bao giờ khớp được, và không có gì báo. Đây là lần thứ ba cùng một
 * cái bẫy trong tệp này (trước đó là "0%" và "thay vì"), nên nó được đặt tên và
 * dùng chung thay vì sửa từng chỗ.
 */
const UB = '(?<![\\p{L}\\p{N}_])'
const UE = '(?![\\p{L}\\p{N}_])'

const CTR_SUBJECT = '(?:ctr|click-?through|impressions?|thumbnail|hình thu nhỏ|tỉ lệ nhấp)'
const CTR_JUDGEMENT = '(?:thấp|cao|kém|tốt|yếu|mạnh|hiệu quả|hấp dẫn|giảm|tăng|low|high|poor|strong|weak|effective|dropped|increased|underperform\\w*|outperform\\w*)'

/**
 * Bắt phán xét về CTR/impressions/thumbnail theo CẢ HAI chiều ngữ pháp.
 *
 * Chỉ bắt một chiều (danh từ trước tính từ) sẽ bỏ lọt "the HIGH number of
 * IMPRESSIONS" — đúng dạng câu tiếng Anh tự nhiên nhất, và là một vi phạm thật.
 * Kiểm chứng bằng test `catches judgement stated before the metric`.
 */
const CTR_CLAIM_PATTERNS: Array<{ re: RegExp; label: string }> = [
  {
    // Cấm dấu câu ở giữa và giới hạn 30 ký tự: phán xét phải THỰC SỰ bổ nghĩa
    // cho chỉ số, không phải chỉ đứng gần nó.
    //
    // Với cửa sổ rộng, câu "Khi có impressions: so sánh retention cao/reach
    // thấp..." bị bắt nhầm — "cao"/"thấp" thuộc về retention và reach, còn
    // "impressions" chỉ là điều kiện tương lai. Vế "CTR is low" vẫn khớp.
    // Liên từ ĐẲNG LẬP cũng kết thúc vùng bổ nghĩa.
    //
    // "Độ phủ impressions/CTR >0 và observedDates tăng" — "tăng" thuộc về
    // observedDates ở vế sau "và", không thuộc về CTR. Câu này là MỤC TIÊU THU
    // THẬP dữ liệu, không phải kết luận về CTR. Ca thật từ hinh_su.
    re: new RegExp(
      `${UB}${CTR_SUBJECT}${UE}(?:(?!${UB}(?:và|and)${UE})[^.!?,;:()–—/]){0,30}?${UB}${CTR_JUDGEMENT}${UE}`,
      'iu',
    ),
    label: 'kết luận về CTR/impressions/thumbnail',
  },
  {
    // Chiều NGƯỢC phải chặt hơn nhiều: cấm dấu câu ở giữa và giới hạn 25 ký tự,
    // để phán xét thực sự BỔ NGHĨA cho chỉ số.
    //
    // Với cửa sổ rộng, câu "retention cao–reach thấp, ... (không dùng CTR làm
    // tiêu chí)" bị bắt nhầm: "thấp" thuộc về "reach", không thuộc về "CTR".
    // Vế "the high number of impressions" vẫn khớp vì không có dấu câu chen vào.
    // Liên từ MỤC ĐÍCH / KẾT QUẢ cũng kết thúc vùng bổ nghĩa.
    //
    // "views quá thấp ĐỂ ổn định CTR" và "sample size view thấp LÀM CTR nhiễu"
    // đều là phát biểu về ĐỘ TIN CẬY PHÉP ĐO: phán xét "thấp" thuộc về views /
    // cỡ mẫu, còn CTR là thứ ĐƯỢC ĐO, không phải thứ bị phán xét. Cả hai nằm ở
    // `stopConditions` và `interpretationRisks` — đúng những ô sinh ra để chứa
    // cảnh báo phương pháp. Chặn chúng là phạt mô hình vì nói đúng về giới hạn
    // đo lường. Hai câu này đến từ lần chạy hinh_su thật.
    re: new RegExp(
      `${UB}${CTR_JUDGEMENT}${UE}(?:(?!${UB}(?:để|làm|khiến|nên)${UE})[^.!?,;()–—]){0,25}?${UB}${CTR_SUBJECT}${UE}`,
      'iu',
    ),
    label: 'kết luận về CTR/impressions/thumbnail (phán xét đứng trước)',
  },
]

/**
 * Câu đang NÓI VỀ việc thiếu dữ liệu thì không tính là vi phạm.
 *
 * "impressions/CTR có độ phủ 0% nên chưa kết luận được" là câu ĐÚNG ĐẮN và phải
 * được phép — nếu không, mô hình bị phạt vì nói thật về giới hạn dữ liệu.
 *
 * Lưu ý về regex: mẫu "0%" KHÔNG được bọc trong `\b...\b`. `%` là ký tự
 * non-word nên biên từ phía sau không bao giờ khớp, khiến "0%" trở thành nhánh
 * chết và mọi câu nói về độ phủ 0% bị coi là vi phạm. Bản đầu mắc đúng lỗi này
 * và đã từ chối oan một lần chạy thật.
 */
function mentionsMissingness(text: string): boolean {
  return (
    /0\s*%/u.test(text) ||
    /\b(?:unavailable|missing|not available|no data|zero coverage|insufficient|cannot be (?:determined|concluded|assessed|evaluated)|not assessable|not enough to conclude|do not treat as confirmed)\b/iu.test(
      text,
    ) ||
    // Tiếng Việt: bắt cả các cách nói KIỀM CHẾ, không chỉ "thiếu dữ liệu".
    //
    // Hai câu sau đến từ output THẬT và đều bị báo động giả ở bản đầu — cả hai
    // là hành vi ĐÚNG mà quy tắc này lẽ ra phải khuyến khích:
    //   "...không đủ để kết luận tiêu đề/thumbnail."
    //   "...không đổi thumbnail như giải pháp đã xác nhận"
    // Phạt mô hình vì nói thật về giới hạn là cách nhanh nhất để dạy nó nói
    // mập mờ hơn.
    //
    // ĐÃ GỠ "đã xác nhận": nó nghĩa là ĐÃ ĐƯỢC XÁC NHẬN, tức ngược hẳn với
    // thiếu dữ liệu, nên "Thumbnail kém đã xác nhận." từng được tha oan. Câu
    // gốc từng cần nó ("không đổi thumbnail như giải pháp đã xác nhận") vẫn
    // được tha nhờ `hasLocalNegation` bắt chữ "không" đứng ngay trước.
    /(?:không có|thiếu|chưa có|không khả dụng|không có dữ liệu|không đủ|chưa đủ|không thể kết luận|không kết luận được|không phân biệt được|không đánh giá được|không xác nhận|chưa xác nhận|không suy ra|chưa thể|trước khi kết luận|chờ|cần thu thập|bật đo|chưa kết luận)/iu.test(
      text,
    ) ||
    // ĐIỀU KIỆN VỀ VIỆC CÓ DỮ LIỆU TRONG TƯƠNG LAI.
    //
    // "Khi có impressions: impressions thấp hay CTR thấp?" nói rằng hiện GIỜ
    // chưa có impressions, và đặt câu hỏi chẩn đoán cho lúc có. Nó không khẳng
    // định gì về CTR — nó là kế hoạch đo, đúng thứ ta muốn mô hình viết ra thay
    // vì đoán bừa. Câu này đến từ một lần chạy phong_thuy thật và từng bị từ
    // chối oan.
    //
    // Đây KHÔNG phải nới lỏng quy tắc CTR: quy tắc vẫn chặn mọi KẾT LUẬN. Cái
    // được bổ sung là một cách diễn đạt sự THIẾU dữ liệu mà danh sách cũ chưa
    // có — "khi nào có X" cũng là một cách nói "hiện chưa có X".
    /(?:khi có|khi nào có|sau khi có|một khi có|khi thu thập được|khi bật được)\s/iu.test(text) ||
    /\b(?:when|once)\s+\w*\s*(?:is |are |becomes? )?available\b/iu.test(text) ||
    // Câu ĐỀ XUẤT THU THẬP dữ liệu, hoặc HOÃN kết luận, không phải câu khẳng
    // định. Ví dụ thật: "bật đo impressions/CTR và chờ chín các video đáy TRƯỚC
    // KHI kết luận kém hiệu quả" — đây là yêu cầu dữ liệu kèm hoãn kết luận,
    // đúng hành vi mong muốn.
    /\b(?:before concluding|once available|enable|start (?:measuring|tracking)|collect|await|pending)\b/iu.test(
      text,
    )
  )
}

/**
 * Phủ định NGAY TRƯỚC chỗ nhắc tới chỉ số.
 *
 * Danh sách cụm từ cố định không bao giờ đủ: mô hình diễn đạt sự kiềm chế bằng
 * vô số cách ("không dùng CTR làm tiêu chí", "không lấy impressions để đánh
 * giá"...). Quy tắc ngôn ngữ tổng quát hơn: một từ phủ định đứng sát trước chủ
 * ngữ thì cả mệnh đề đó là phủ định, không phải khẳng định.
 *
 * Cửa sổ 50 ký tự: đủ để bắt "không dùng X làm Y" mà không vơ nhầm một phủ định
 * ở mệnh đề hoàn toàn khác.
 */
/**
 * MỌI lần khớp của một mẫu, không chỉ lần đầu.
 *
 * `exec` không cờ `g` chỉ trả về lần khớp đầu tiên. Khi lần đầu rơi vào một
 * ngoại lệ hợp lệ, mọi vi phạm phía sau dùng cùng mẫu đó sẽ không bao giờ được
 * kiểm — một lối lách im lặng.
 *
 * `lastIndex` được đẩy tiến ít nhất 1 để mẫu khớp rỗng không lặp vô hạn.
 */
function allMatches(re: RegExp, text: string): RegExpExecArray[] {
  const g = new RegExp(re.source, re.flags.includes('g') ? re.flags : `${re.flags}g`)
  const out: RegExpExecArray[] = []
  let m: RegExpExecArray | null
  while ((m = g.exec(text)) !== null) {
    out.push(m)
    if (m.index === g.lastIndex) g.lastIndex++
    // KHÔNG đặt trần số lần khớp.
    //
    // Bản trước dừng ở 50. Trần đó âm thầm đổi NGỮ NGHĨA kiểm định: 50 câu có
    // rào đón đứng trước là đủ để đẩy một câu khẳng định trần ra ngoài vùng
    // quét, và trường 800 ký tự thừa chỗ cho việc đó. Các mẫu ở đây không khớp
    // chuỗi rỗng, và `lastIndex` luôn tiến, nên vòng lặp chắc chắn dừng.
  }
  return out
}

/**
 * "thay vì X" / "instead of X" — phủ định một HÀNH ĐỘNG.
 *
 * Tách riêng khỏi bộ từ phủ định chung vì chỉ nhóm này được phép miễn trừ khi
 * nằm GIỮA phán xét và chỉ số.
 */
const INSTEAD_OF = /(?:thay vì|instead of)/iu

/** Từ phủ định dùng cho phép kiểm PHÍA TRƯỚC chỗ khớp. */
/**
 * Cụm kết thúc bằng chữ cái NGOÀI ASCII phải nằm ngoài cặp `\b...\b`.
 *
 * Với cờ `u`, `\b` chỉ tính theo `\w` = [A-Za-z0-9_]. "thay vì" kết thúc bằng
 * "ì" nên `\b` phía sau KHÔNG BAO GIỜ khớp, biến nhánh đó thành nhánh chết —
 * đúng cái bẫy đã gặp với mẫu "0%". Test "thay vì X" là thứ phát hiện ra.
 */
const NEGATION_WORDS =
  /(?:\b(?:không|chưa|tránh|khỏi|no|not|avoid|without|never|exclude)\b|thay vì|instead of)/iu

function hasLocalNegation(text: string, matchIndex: number): boolean {
  const before = text.slice(Math.max(0, matchIndex - 50), matchIndex)
  // "thay vì X" nghĩa là KHÔNG làm X — dạng phủ định rất hay gặp trong khuyến
  // nghị: "...thay vì đổi thumbnail hàng loạt" là lời khuyên ĐỪNG đụng vào
  // thumbnail, tức ngược hẳn với một kết luận về thumbnail. Ca thật từ phong_thuy.
  return NEGATION_WORDS.test(before)
}

/**
 * Dấu hiệu ĐÃ RÀO ĐÓN — câu đang đề xuất chứ không khẳng định.
 *
 * Danh sách này lấy thẳng từ phần "từ ngữ nên dùng" của hợp đồng: "có thể cho
 * thấy", "là giả thuyết hợp lý", "may indicate", "plausible hypothesis"...
 */
const HEDGE_PATTERN =
  /(?:có thể|có lẽ|có khả năng|giả thuyết|chưa kiểm chứng|nghi ngờ|dường như|có liên hệ|phù hợp với|cần thêm bằng chứng|may |might |could |possibly|plausible|hypothes\w+|appears? to|consistent with|associated with|suggests?|unverified)/iu

// Lưu ý: dùng "có khả năng" chứ KHÔNG dùng "khả năng" trần.
// Trong tiếng Việt "khả năng" vừa nghĩa "possibility" (rào đón) vừa nghĩa
// "ability" — nên "khả năng giữ chân" (retention ABILITY) từng bị hiểu nhầm là
// đã rào đón, và một giả thuyết nhân quả trần trụi lọt qua kiểm định.

/**
 * Mọi chuỗi văn bản tự do trong output.
 *
 * `isHypothesis` quyết định mức nghiêm khắc với ngôn ngữ nhân quả. Một GIẢ
 * THUYẾT, theo định nghĩa, đề xuất một cơ chế — cấm tuyệt đối ngôn ngữ nhân quả
 * ở đó thì không thể phát biểu giả thuyết nào, và chính hợp đồng cũng gợi ý
 * dùng "là giả thuyết hợp lý". Nên ở ngữ cảnh giả thuyết, cơ chế được phép NẾU
 * có rào đón; còn ở phần khẳng định (tóm tắt, phát hiện, lý do khuyến nghị) thì
 * ngôn ngữ nhân quả vẫn bị chặn tuyệt đối.
 */
function textFields(
  output: CursorOutput,
): Array<{ path: string; text: string; isHypothesis: boolean }> {
  const out: Array<{ path: string; text: string; isHypothesis: boolean }> = []
  const s = output.analysisSummary
  const assert = (path: string, text: string) => out.push({ path, text, isHypothesis: false })
  const hypo = (path: string, text: string) => out.push({ path, text, isHypothesis: true })
  const assertEach = (base: string, xs: string[]) =>
    xs.forEach((t, j) => assert(`${base}[${j}]`, t))
  const hypoEach = (base: string, xs: string[]) => xs.forEach((t, j) => hypo(`${base}[${j}]`, t))

  assert('analysisSummary.overallAssessment', s.overallAssessment)
  assert('analysisSummary.confidenceRationale', s.confidenceRationale)
  assert('analysisSummary.primaryConstraint', s.primaryConstraint)

  output.keyFindings.forEach((f, i) => {
    assert(`keyFindings[${i}].statement`, f.statement)
    assert(`keyFindings[${i}].supportingReasoning`, f.supportingReasoning)
    assertEach(`keyFindings[${i}].limitations`, f.limitations)
  })
  output.hypotheses.forEach((h, i) => {
    hypo(`hypotheses[${i}].statement`, h.statement)
    hypo(`hypotheses[${i}].validationMethod`, h.validationMethod)
    hypoEach(`hypotheses[${i}].missingEvidence`, h.missingEvidence)
  })
  output.recommendations.forEach((r, i) => {
    assert(`recommendations[${i}].action`, r.action)
    assert(`recommendations[${i}].rationale`, r.rationale)
    assert(`recommendations[${i}].successMetric`, r.successMetric)
    assertEach(`recommendations[${i}].risks`, r.risks)
  })
  output.experiments.forEach((e, i) => {
    // Thí nghiệm mô tả một thay đổi ĐỀ XUẤT để kiểm chứng -> cùng nhóm giả thuyết.
    hypo(`experiments[${i}].change`, e.change)
    hypo(`experiments[${i}].baseline`, e.baseline)
    hypoEach(`experiments[${i}].successMetrics`, e.successMetrics)
    hypoEach(`experiments[${i}].sampleLimitations`, e.sampleLimitations)
    hypoEach(`experiments[${i}].stopConditions`, e.stopConditions)
    hypoEach(`experiments[${i}].interpretationRisks`, e.interpretationRisks)
  })

  // Các trường dưới đây từng KHÔNG được quét. Đó là một lỗ thật, không phải
  // thiếu sót hình thức: `manualReviewTargets[].reason` là chỗ tự nhiên nhất để
  // viết "thumbnail kém dẫn tới lượt xem thấp" — vừa nhân quả vừa kết luận về
  // thumbnail khi độ phủ impressions bằng 0 — và toàn bộ payload vẫn "ĐẠT".
  // Quy tắc: MỌI chuỗi tự do đều bị quét; không có vùng nào miễn kiểm.
  output.manualReviewTargets.forEach((m, i) => {
    assert(`manualReviewTargets[${i}].reason`, m.reason)
    assertEach(`manualReviewTargets[${i}].reviewQuestions`, m.reviewQuestions)
  })
  output.dataRequests.forEach((d, i) => {
    assert(`dataRequests[${i}].metricOrArtifact`, d.metricOrArtifact)
    assert(`dataRequests[${i}].reason`, d.reason)
    assert(`dataRequests[${i}].decisionUnlocked`, d.decisionUnlocked)
  })
  // `explicitNonConclusions` là nơi mô hình liệt kê điều nó KHÔNG kết luận. Nội
  // dung đúng đắn ở đây gần như luôn chứa phủ định, nên bộ lọc thiếu-dữ-liệu sẽ
  // tha; nhưng quét vẫn cần, vì một khẳng định trá hình cũng có thể nấp ở đây.
  assertEach('explicitNonConclusions', output.explicitNonConclusions)
  return out
}

/**
 * Tách câu để xét ngoại lệ theo TỪNG CÂU, không theo cả trường.
 *
 * Áp `mentionsMissingness` lên cả trường tạo ra một lối lách nguy hiểm: chỉ cần
 * mở đầu bằng một câu miễn trừ đúng chuẩn là mọi khẳng định bị cấm phía sau đều
 * được tha. Ví dụ thật của lối lách này:
 *
 *   "Không có dữ liệu CTR. Tuy nhiên thumbnail hiện tại kém và impressions thấp."
 *
 * Câu đầu hợp lệ, câu sau vi phạm — nhưng cả trường được tha. Tệ hơn: mô hình
 * làm đúng yêu cầu "nêu rõ dữ liệu thiếu" lại chính là thứ mở khoá cho vi phạm.
 * Vì vậy ngoại lệ chỉ áp cho câu CHỨA chỗ khớp.
 */
function sentenceAround(text: string, matchIndex: number): string {
  const before = text.slice(0, matchIndex)
  // Dấu hai chấm và dấu ba chấm CŨNG là ranh giới mệnh đề.
  //
  // Thiếu chúng, một mệnh đề miễn trừ nối bằng dấu hai chấm sẽ tha cho khẳng
  // định đứng sau: "Không có dữ liệu CTR: thumbnail hiện tại kém." — vế trái
  // nói thiếu dữ liệu, vế phải kết luận thẳng, và cả cụm được tha.
  const start = Math.max(
    before.lastIndexOf('.'),
    before.lastIndexOf('!'),
    before.lastIndexOf('?'),
    before.lastIndexOf('\n'),
    before.lastIndexOf(';'),
    before.lastIndexOf(':'),
    before.lastIndexOf('…'),
  )
  const rest = text.slice(matchIndex)
  const endRel = rest.search(/[.!?;:…\n]/u)
  const end = endRel === -1 ? text.length : matchIndex + endRel + 1
  return text.slice(start + 1, end)
}

/**
 * Mệnh đề NGHI VẤN không phải là kết luận.
 *
 * Quy tắc CTR chặn KẾT LUẬN. "Khi có impressions: impressions thấp hay CTR
 * thấp?" là câu hỏi chẩn đoán cho lúc có dữ liệu — nó không khẳng định điều gì
 * về CTR hiện tại, và đó chính là hành vi kiềm chế ta muốn khuyến khích.
 *
 * Sau khi dấu hai chấm trở thành ranh giới, vế phải đứng riêng và không còn
 * mang dấu hiệu thiếu dữ liệu, nên cần nhận diện nó là câu hỏi.
 *
 * Rủi ro còn lại, có ý thức chấp nhận: câu hỏi TU TỪ ("Phải chăng CTR thấp?")
 * vẫn là khẳng định trá hình. Ngoại lệ này chỉ áp cho quy tắc CTR, không áp cho
 * ngôn ngữ nhân quả, và các trường liên quan (`reviewQuestions`) vốn được thiết
 * kế để chứa câu hỏi.
 */
function isInterrogative(clause: string): boolean {
  return clause.trimEnd().endsWith('?')
}

/**
 * Mệnh đề ĐIỀU KIỆN không khẳng định điều gì là sự thật.
 *
 * "nếu CTR thấp + impressions thấp/cao sẽ hướng kiểm chứng khác nhau" mô tả
 * cách xử lý KHI có dữ liệu; nó không nói CTR đang thấp. Đây là kế hoạch kiểm
 * chứng — đúng thứ ta muốn mô hình viết thay vì đoán bừa. Cả hai ca thật
 * (hinh_su và phong_thuy) đều thuộc dạng này.
 *
 * Song song với `isInterrogative`, và cũng chỉ áp cho quy tắc CTR: câu điều
 * kiện KHÔNG được phép chứa ngôn ngữ nhân quả trần trụi.
 *
 * Rủi ro còn lại, có ý thức chấp nhận: một khẳng định có thể được nguỵ trang
 * thành mệnh đề điều kiện. Đổi lại, phạt mô hình vì lập kế hoạch đo lường có
 * điều kiện sẽ dạy nó nói mơ hồ hơn.
 */
function isConditional(clause: string): boolean {
  return /\b(?:nếu|khi nào|nếu như|giả sử|if|when|once|should)\b/iu.test(clause)
}

export interface ValidateInput {
  raw: string
  pkg: AnalysisPackage
  allowedEvidenceIds: string[]
  allowedVideoIds: string[]
  allowedCohortKeys: string[]
  hadProseOutsideJson: boolean
  /** Văn bản ngoài JSON — cũng là lời của mô hình, nên cũng phải bị quét. */
  proseText?: string
  strict?: boolean
}

export interface ValidateResult {
  report: ValidationReport
  output: CursorOutput | null
  failureClass:
    | 'NONE'
    | 'INVALID_JSON'
    | 'PROSE_OUTSIDE_JSON'
    | 'SCHEMA_MISMATCH'
    | 'MISSING_REQUIRED_FIELD'
    | 'UNSUPPORTED_SCHEMA_VERSION'
    | 'UNSUPPORTED_CLAIM'
    | 'EVIDENCE_UNRESOLVED'
  /** Lỗi ngắn gọn để đưa vào prompt sửa lỗi. */
  repairErrors: string[]
}

export function validateCursorOutput(input: ValidateInput): ValidateResult {
  const structuralIssues: ValidationIssue[] = []
  const evidenceIssues: ValidationIssue[] = []
  const claimIssues: ValidationIssue[] = []
  const qualityIssues: ValidationIssue[] = []
  const repairErrors: string[] = []

  const emptyReport = (): ValidationReport => ({
    passed: false,
    structuralIssues,
    evidenceIssues,
    claimIssues,
    qualityIssues,
    evidenceResolutionRate: null,
    totalEvidenceRefs: 0,
    unresolvedEvidenceRefs: 0,
    causalViolations: 0,
    ctrViolations: 0,
    unsupportedMetricViolations: 0,
    counts: { findings: 0, hypotheses: 0, recommendations: 0, experiments: 0 },
  })

  // --- 1. Cấu trúc ---------------------------------------------------------
  let parsed: unknown
  try {
    parsed = JSON.parse(input.raw)
  } catch (err) {
    structuralIssues.push({
      rule: 'json_parse',
      severity: 'BLOCKER',
      message: `Không parse được JSON: ${err instanceof Error ? err.message : 'lỗi không rõ'}`,
    })
    repairErrors.push('Output không phải JSON hợp lệ. Trả về DUY NHẤT một object JSON.')
    return { report: emptyReport(), output: null, failureClass: 'INVALID_JSON', repairErrors }
  }

  if (input.hadProseOutsideJson) {
    // BLOCKER, không phải MEDIUM.
    //
    // Hợp đồng nói "chỉ trả về một object JSON". Trước đây vi phạm này chỉ là
    // MEDIUM nên không ảnh hưởng `passed`, và phần văn bản ngoài JSON bị vứt đi
    // mà không hề được kiểm — mô hình có thể viết một câu nhân quả/CTR ở ngoài
    // rồi kèm một JSON sạch, và lần chạy vẫn được ghi SUCCEEDED.
    //
    // Đây là thất bại KỸ THUẬT (sai định dạng) nên ĐƯỢC phép thử lại. Nhưng nếu
    // phần văn bản đó chứa khẳng định bị cấm thì nó thành thất bại NỘI DUNG và
    // không được thử lại — xử lý ở phần quét khẳng định bên dưới.
    structuralIssues.push({
      rule: 'prose_outside_json',
      severity: 'BLOCKER',
      message: 'Có văn bản ngoài object JSON — hợp đồng yêu cầu CHỈ một object JSON.',
    })
    repairErrors.push('Trả về DUY NHẤT một object JSON, không kèm văn bản nào ngoài nó.')
  }

  const version = (parsed as { schemaVersion?: unknown })?.schemaVersion
  // Payload schema 1 bị TỪ CHỐI dứt khoát, không "tương thích ngược" âm thầm.
  //
  // Chấp nhận 1.0 nghĩa là chấp nhận một payload KHÔNG có `metricClaims` — tức
  // là mất toàn bộ tầng khai báo ngữ nghĩa mà 2.0 sinh ra để có. Một payload
  // yếu hơn lọt qua vì "tương thích" là đúng kiểu thành công giả.
  if (typeof version === 'string' && (LEGACY_SCHEMA_VERSIONS as readonly string[]).includes(version)) {
    structuralIssues.push({
      rule: 'legacy_schema_version',
      severity: 'BLOCKER',
      message:
        `schemaVersion ${version} là bản CŨ (thiếu metricClaims). ` +
        `Lần chạy này yêu cầu ${CURSOR_OUTPUT_SCHEMA_VERSION}.`,
    })
    repairErrors.push(`schemaVersion phải đúng bằng "${CURSOR_OUTPUT_SCHEMA_VERSION}".`)
    return {
      report: emptyReport(),
      output: null,
      failureClass: 'UNSUPPORTED_SCHEMA_VERSION',
      repairErrors,
    }
  }
  if (version !== undefined && version !== CURSOR_OUTPUT_SCHEMA_VERSION) {
    structuralIssues.push({
      rule: 'schema_version',
      severity: 'BLOCKER',
      message: `schemaVersion không hỗ trợ: ${String(version)}`,
    })
    repairErrors.push(`schemaVersion phải đúng bằng "${CURSOR_OUTPUT_SCHEMA_VERSION}".`)
    return {
      report: emptyReport(),
      output: null,
      failureClass: 'UNSUPPORTED_SCHEMA_VERSION',
      repairErrors,
    }
  }

  const result = cursorOutputSchema.safeParse(parsed)
  if (!result.success) {
    for (const issue of result.error.issues.slice(0, 25)) {
      structuralIssues.push({
        rule: 'schema',
        severity: 'BLOCKER',
        message: issue.message,
        path: issue.path.join('.'),
      })
      repairErrors.push(`${issue.path.join('.') || '(gốc)'}: ${issue.message}`)
    }
    const missingRequired = result.error.issues.some((i) => i.code === 'invalid_type')
    return {
      report: emptyReport(),
      output: null,
      failureClass: missingRequired ? 'MISSING_REQUIRED_FIELD' : 'SCHEMA_MISMATCH',
      repairErrors,
    }
  }

  const output = result.data

  // ID phải duy nhất trong từng nhóm.
  for (const [name, arr] of [
    ['keyFindings', output.keyFindings],
    ['hypotheses', output.hypotheses],
    ['recommendations', output.recommendations],
    ['experiments', output.experiments],
  ] as const) {
    const ids = (arr as Array<{ id: string }>).map((x) => x.id)
    const dupes = ids.filter((id, i) => ids.indexOf(id) !== i)
    if (dupes.length) {
      structuralIssues.push({
        rule: 'duplicate_ids',
        severity: 'BLOCKER',
        message: `${name} có id trùng: ${[...new Set(dupes)].join(', ')}`,
      })
      repairErrors.push(`${name}: id phải duy nhất (trùng: ${[...new Set(dupes)].join(', ')}).`)
    }
  }

  // Thí nghiệm phải trỏ tới giả thuyết có thật.
  const hypothesisIds = new Set(output.hypotheses.map((h) => h.id))
  for (const [i, e] of output.experiments.entries()) {
    if (!hypothesisIds.has(e.hypothesisId)) {
      structuralIssues.push({
        rule: 'dangling_hypothesis_ref',
        severity: 'BLOCKER',
        message: `experiments[${i}].hypothesisId "${e.hypothesisId}" không tồn tại`,
        path: `experiments[${i}].hypothesisId`,
      })
      repairErrors.push(`experiments[${i}].hypothesisId phải là một id có trong hypotheses.`)
    }
  }

  // --- 2. Bằng chứng -------------------------------------------------------
  // Cho phép trích dẫn CHÉO NỘI BỘ: một khuyến nghị dựa trên chính phát hiện
  // F-00x của nó là cách viết tự nhiên và hợp lệ. Chỉ cần id đó thực sự tồn tại
  // trong output — điều được kiểm ngay dưới đây.
  const internalIds = new Set<string>([
    ...output.keyFindings.map((f) => f.id),
    ...output.hypotheses.map((h) => h.id),
  ])
  const allowed = new Set([...input.allowedEvidenceIds, ...internalIds])
  const allowedVideos = new Set(input.allowedVideoIds)
  let totalRefs = 0
  let unresolvedRefs = 0

  const checkRefs = (ids: string[], path: string): void => {
    for (const id of ids) {
      totalRefs++
      if (!allowed.has(id)) {
        unresolvedRefs++
        evidenceIssues.push({
          rule: 'unknown_evidence_id',
          severity: 'BLOCKER',
          message: `Evidence id "${id}" không có trong gói đầu vào`,
          path,
        })
      }
    }
  }

  output.keyFindings.forEach((f, i) => {
    checkRefs(f.evidenceIds, `keyFindings[${i}].evidenceIds`)
    checkRefs(f.contradictingEvidenceIds, `keyFindings[${i}].contradictingEvidenceIds`)
  })
  output.hypotheses.forEach((h, i) => {
    checkRefs(h.supportingEvidenceIds, `hypotheses[${i}].supportingEvidenceIds`)
    checkRefs(h.contradictingEvidenceIds, `hypotheses[${i}].contradictingEvidenceIds`)
  })
  output.recommendations.forEach((r, i) => {
    checkRefs(r.evidenceIds, `recommendations[${i}].evidenceIds`)
  })
  const allowedCohorts = new Set(input.allowedCohortKeys)
  output.manualReviewTargets.forEach((m, i) => {
    checkRefs(m.evidenceIds, `manualReviewTargets[${i}].evidenceIds`)
    totalRefs++
    if (m.targetType === 'VIDEO') {
      // Video phải thuộc ĐÚNG kênh đang phân tích — chặn tham chiếu chéo kênh.
      if (!allowedVideos.has(m.targetId)) {
        unresolvedRefs++
        evidenceIssues.push({
          rule: 'cross_channel_video',
          severity: 'BLOCKER',
          message: `manualReviewTargets[${i}].targetId "${m.targetId}" không phải video của kênh đang phân tích`,
          path: `manualReviewTargets[${i}].targetId`,
        })
      }
    } else if (!allowedCohorts.has(m.targetId)) {
      unresolvedRefs++
      evidenceIssues.push({
        rule: 'unknown_cohort',
        severity: 'BLOCKER',
        message: `manualReviewTargets[${i}].targetId "${m.targetId}" không phải cohort có trong gói`,
        path: `manualReviewTargets[${i}].targetId`,
      })
    }
  })

  if (unresolvedRefs > 0) {
    repairErrors.push(
      `${unresolvedRefs} evidence id không hợp lệ. Chỉ dùng id có trong danh sách EVIDENCE ID đã cho.`,
    )
  }

  // --- 2b. Trích dẫn nội bộ phải NEO được về bằng chứng của gói ---------------
  //
  // Cho phép F-002 dựa trên F-001 là hợp lý. Nhưng chỉ kiểm "id có tồn tại" thì
  // mở ra một lỗ hổng nghiêm trọng: F-001 trích chính F-001, hoặc F-001 trích
  // H-001 trong khi H-001 trích lại F-001. Mọi id đều "tồn tại", tỉ lệ giải
  // được báo 100%, và kết quả ĐẠT — trong khi KHÔNG có một mẩu bằng chứng nào
  // từ tầng tất định đứng sau nó. Đó đúng là thứ mà cả tầng kiểm định này sinh
  // ra để chặn: kết luận tự nuôi chính nó.
  //
  // Quy tắc: đi theo chuỗi trích dẫn nội bộ, phải chạm tới ÍT NHẤT một id của
  // gói. Chu trình được phát hiện bằng tập đã thăm và tính là KHÔNG neo được.
  // Đếm RIÊNG với `unresolvedEvidenceRefs`: một id không tồn tại là lỗi của
  // THAM CHIẾU, còn không neo được là lỗi của MỤC. Gộp chung sẽ đếm đôi một id
  // sai (vừa không tồn tại, vừa làm mục đó không neo được).
  let ungroundedItems = 0
  const packageIds = new Set(input.allowedEvidenceIds)
  const internalRefs = new Map<string, string[]>()
  for (const f of output.keyFindings) internalRefs.set(f.id, f.evidenceIds)
  for (const h of output.hypotheses) internalRefs.set(h.id, h.supportingEvidenceIds)

  /**
   * Tính "neo được" bằng ĐIỂM BẤT ĐỘNG, không phải DFS có nhớ đệm.
   *
   * Bản DFS đầu tiên nhớ đệm kết quả tính ra khi tập `seen` đang KHÁC RỖNG. Kết
   * quả đó phụ thuộc đường đi: một nút bị coi là "không neo được" chỉ vì đường
   * đi hiện tại đã đi qua nút neo nó, rồi giá trị sai ấy được nhớ và dùng lại
   * cho các phép kiểm sau. Nhớ đệm một kết quả phụ thuộc đường đi là không đúng.
   *
   * Điểm bất động không có vấn đề đó: xuất phát từ các mục trích thẳng bằng
   * chứng của gói, rồi lan dần. Chu trình tự nhiên không bao giờ được đánh dấu
   * vì không có gì neo chúng. Luôn dừng sau tối đa n vòng.
   */
  const grounded = new Set<string>()
  for (let pass = 0; pass <= internalRefs.size; pass++) {
    let changed = false
    for (const [id, refs] of internalRefs) {
      if (grounded.has(id)) continue
      if (refs.some((r) => r !== id && (packageIds.has(r) || grounded.has(r)))) {
        grounded.add(id)
        changed = true
      }
    }
    if (!changed) break
  }
  const isGrounded = (id: string): boolean => packageIds.has(id) || grounded.has(id)

  const checkGrounding = (id: string, refs: string[], path: string, label: string): void => {
    if (refs.length === 0) return // đã có quy tắc riêng cho "không bằng chứng"
    if (refs.includes(id)) {
      evidenceIssues.push({
        rule: 'self_referential_evidence',
        severity: 'BLOCKER',
        message: `${label} tự trích chính nó (${id}) làm bằng chứng`,
        path,
      })
      ungroundedItems++
      return
    }
    if (!refs.some((r) => r !== id && isGrounded(r))) {
      evidenceIssues.push({
        rule: 'evidence_not_grounded',
        severity: 'BLOCKER',
        message: `${label} chỉ trích dẫn nội bộ, không neo về bằng chứng nào của gói`,
        path,
      })
      ungroundedItems++
    }
  }

  output.keyFindings.forEach((f, i) =>
    checkGrounding(f.id, f.evidenceIds, `keyFindings[${i}].evidenceIds`, `keyFindings[${i}]`),
  )
  output.hypotheses.forEach((h, i) =>
    checkGrounding(
      h.id,
      h.supportingEvidenceIds,
      `hypotheses[${i}].supportingEvidenceIds`,
      `hypotheses[${i}]`,
    ),
  )
  output.recommendations.forEach((r, i) => {
    if (r.evidenceIds.length === 0) return
    if (!r.evidenceIds.some((x) => isGrounded(x))) {
      evidenceIssues.push({
        rule: 'evidence_not_grounded',
        severity: 'BLOCKER',
        message: `recommendations[${i}] chỉ trích dẫn nội bộ, không neo về bằng chứng nào của gói`,
        path: `recommendations[${i}].evidenceIds`,
      })
      ungroundedItems++
    }
  })

  if (evidenceIssues.some((i) => i.rule === 'evidence_not_grounded' || i.rule === 'self_referential_evidence')) {
    repairErrors.push(
      'Mỗi phát hiện/giả thuyết/khuyến nghị phải trích ÍT NHẤT một evidence id của gói ' +
        '(OBS-/ANOM-/VIDEO-/BASE-/COHORT-). Trích chéo F-/H- chỉ được dùng THÊM, ' +
        'không được thay thế, và không được tự trích chính nó.',
    )
  }

  // --- 3b. THAM CHIẾU NGUỒN và TÍNH ĐẦY ĐỦ -------------------------------
  //
  // RANH GIỚI TIN CẬY: phân giải tham chiếu và tính duy nhất của itemId là TẤT
  // ĐỊNH. Việc đếm mệnh đề nhạy cảm và quy tắc "một ô một phát biểu" là
  // HEURISTIC NGÔN NGỮ. Hai nhóm này được báo cáo riêng, không gộp.
  for (const d of findDuplicateItemIds(output)) {
    structuralIssues.push({
      rule: 'duplicate_source_item',
      severity: 'BLOCKER',
      message: `${d.section} có hai mục cùng id "${d.id}" — tham chiếu nguồn trở nên mập mờ`,
    })
  }

  /** claim id -> ô đã phân giải, dùng lại ở phần kiểm ngữ nghĩa và ở drift. */
  const resolvedByClaim = new Map<string, ResolvedUnit>()
  const claimsPerCanonical = new Map<string, string[]>()

  for (const [i, mc] of output.metricClaims.entries()) {
    const at = `metricClaims[${i}]`
    const res = resolveSourceRef(output, mc.sourceRef)
    if ('error' in res) {
      evidenceIssues.push({
        rule:
          res.error === 'AMBIGUOUS_DUPLICATE_TEXT'
            ? 'source_ref_ambiguous'
            : res.error === 'MALFORMED_REF'
              ? 'source_ref_malformed'
              : 'source_ref_unresolved',
        severity: 'BLOCKER',
        message: `${at}.sourceRef không phân giải được: ${res.error}`,
        path: `${at}.sourceRef`,
      })
      continue
    }
    resolvedByClaim.set(mc.id, res.ok)
    claimsPerCanonical.set(res.ok.canonical, [
      ...(claimsPerCanonical.get(res.ok.canonical) ?? []),
      mc.id,
    ])
  }


  // --- 3. KHẲNG ĐỊNH CÓ CẤU TRÚC (nguồn sự thật) ---------------------------
  //
  // Từ schema 2.0, ngữ nghĩa do MÔ HÌNH KHAI BÁO, không do bộ kiểm định đoán.
  // Bảy cấu trúc ngữ pháp đã đánh bại cách dò chuỗi; vấn đề nằm ở chính việc
  // suy đoán, nên nó bị thay bằng kiểm tra trường tất định.
  const ctrCoverage = input.pkg.dataCoverage.metricCoverage['impressions'] ?? 0

  /**
   * Chỉ số KHÔNG có dữ liệu trong gói NÀY — đọc từ gói, không hardcode.
   *
   * Nhờ vậy, nếu một kênh về sau có impressions thật thì quy tắc tự nới; và nếu
   * một chỉ số khác tụt về 0 thì quy tắc tự siết.
   */
  const zeroCoverage = new Set<string>()
  if (ctrCoverage === 0) {
    for (const m of ['impressions', 'impression_ctr', 'thumbnail', 'packaging']) zeroCoverage.add(m)
  }
  for (const [k, v] of Object.entries(input.pkg.dataCoverage.metricCoverage)) {
    if (v === 0) zeroCoverage.add(k)
  }

  /** OBS-nnn -> quan sát tương ứng trong gói, để đối chiếu nội dung bằng chứng. */
  const observationByEvidenceId = new Map<
    string,
    { statement: string; metricValues?: Record<string, unknown> }
  >()
  input.pkg.observations.forEach((o, i) => {
    observationByEvidenceId.set(`OBS-${String(i + 1).padStart(3, '0')}`, {
      statement: o.statement,
      metricValues: o.metricValues as Record<string, unknown> | undefined,
    })
  })

  let assertedOnMissing = 0
  let causalViolations = 0
  let ctrViolations = 0
  const claimIds = new Set<string>()
  const claimById = new Map<string, (typeof output.metricClaims)[number]>()

  for (const [i, mc] of output.metricClaims.entries()) {
    const at = `metricClaims[${i}]`

    // Văn bản THẬT tại ô được trỏ tới. Không còn bản sao `text` để lệch nhau —
    // đó chính là lớp lỗi đã làm hỏng toàn bộ lô cấu trúc 2.0.
    //
    // Claim không phân giải được đã bị báo lỗi ở khối 3b; ở đây bỏ qua để không
    // báo trùng, và các quy tắc ngữ nghĩa không chạy trên dữ liệu không có thật.
    const unit = resolvedByClaim.get(mc.id)
    const claimText = unit?.text
    if (claimText === undefined) continue

    if (claimIds.has(mc.id)) {
      structuralIssues.push({
        rule: 'duplicate_claim_id',
        severity: 'BLOCKER',
        message: `${at}: id trùng "${mc.id}"`,
        path: at,
      })
    }
    claimIds.add(mc.id)
    claimById.set(mc.id, mc)

    const judgemental = mc.judgement !== 'UNKNOWN' && mc.judgement !== 'NOT_APPLICABLE'

    // R0a — TRẠNG THÁI KHAI BÁO phải có dấu hiệu tương ứng trong chính câu.
    //
    // Ca thật Codex đưa ra: câu "CTR hiện tại thấp" khai là CONDITIONAL +
    // DIAGNOSTIC_PLAN. Khớp từ vựng hoàn hảo, né được quy tắc độ phủ 0, và
    // không quy tắc mâu thuẫn nào bắt. Tự khai mà không đối chiếu với văn bản
    // thì chỉ là lời nói suông.
    const marker = MODALITY_MARKERS[mc.assertionStatus]
    if (marker && !marker.test(claimText)) {
      claimIssues.push({
        rule: 'modality_not_supported_by_text',
        severity: 'BLOCKER',
        message:
          `${at}: khai assertionStatus=${mc.assertionStatus} nhưng câu không có dấu hiệu ` +
          `tương ứng (điều kiện / nghi vấn / phủ định hành động / giới hạn). ` +
          `Nếu đây là khẳng định thì phải khai ASSERTED.`,
        path: at,
        excerpt: claimText.slice(0, 180),
      })
    }

    // R0d — PHÁN XÉT khai báo phải khớp CHIỀU của câu.
    //
    // Chỉ kiểm chủ ngữ là chưa đủ: câu "CTR cao" khai `judgement: LOW` vẫn khớp
    // từ vựng hoàn hảo và phân cực đồng ý, rồi đi qua với kết luận ngược hẳn.
    {
      const jm = JUDGEMENT_MARKERS[mc.judgement]
      if (jm && !jm.self.test(claimText) && jm.opposite.test(claimText)) {
        claimIssues.push({
          rule: 'judgement_contradicts_text',
          severity: 'BLOCKER',
          message:
            `${at}: khai judgement=${mc.judgement} nhưng câu nói theo chiều NGƯỢC LẠI. ` +
            `Kết luận có cấu trúc phải cùng chiều với chính câu văn.`,
          path: at,
          excerpt: claimText.slice(0, 180),
        })
      }
    }

    // R0c — `text` của claim là BỀ MẶT KHÔNG ĐÁNG TIN, phải quét như văn xuôi.
    //
    // Ca thật Codex đưa ra: claim sao chép đủ câu hợp lệ để đạt ngưỡng khớp, rồi
    // NỐI THÊM "thumbnail caused lower views". Phần nối thêm được lưu vào payload
    // chính thức nhưng chưa bao giờ bị quét nhân quả hay chỉ số bịa.
    //
    // Hai quy tắc tất định:
    //  (a) ngôn ngữ nhân quả trong text đòi claimType = CAUSAL;
    //  (b) text không được nhắc chỉ số NHẠY CẢM nào ngoài subject/related đã khai.
    for (const { re, label } of CAUSAL_PATTERNS) {
      if (!re.test(claimText)) continue
      if (mc.claimType !== 'CAUSAL') {
        causalViolations++
        claimIssues.push({
          rule: 'causal_language_in_non_causal_claim',
          severity: 'BLOCKER',
          message: `${at}: text chứa ngôn ngữ nhân quả ("${label}") nhưng claimType=${mc.claimType}`,
          path: `${at}.text`,
          excerpt: claimText.slice(0, 180),
        })
      }
      break
    }
    {
      const declaredMetrics = new Set<string>(
        [mc.subjectMetric as string, mc.relatedMetric as string].map((m) =>
          m === 'impressions' ? 'impression_ctr' : m,
        ),
      )
      const inText = [...mentionedSensitiveMetrics(claimText)].map((m) =>
        m === 'impressions' ? 'impression_ctr' : m,
      )
      const undeclaredInText = inText.filter((m) => !declaredMetrics.has(m))
      if (undeclaredInText.length > 0) {
        ctrViolations++
        claimIssues.push({
          rule: 'undeclared_metric_in_claim_text',
          severity: 'BLOCKER',
          message:
            `${at}: text nhắc tới ${undeclaredInText.join(', ')} nhưng không khai ở ` +
            `subjectMetric/relatedMetric. Mỗi phát biểu cần một claim riêng.`,
          path: `${at}.text`,
          excerpt: claimText.slice(0, 180),
        })
      }
    }

    // R0b — CHỦ NGỮ phải được NHẮC TỚI trong chính câu.
    //
    // Ca thật Codex đưa ra: câu "Thumbnail hiện tại kém" khai subjectMetric=views,
    // relatedMetric=thumbnail. Vì views có dữ liệu nên mọi quy tắc đều lọt, trong
    // khi thứ bị phán xét rõ ràng là thumbnail. Đối chiếu tên chủ ngữ với câu
    // đóng đúng đường đó, và hoàn toàn tất định.
    if (mc.subjectMetric !== 'NONE' && !metricNamedIn(mc.subjectMetric, claimText)) {
      claimIssues.push({
        rule: 'subject_metric_not_in_text',
        severity: 'BLOCKER',
        message:
          `${at}: subjectMetric="${mc.subjectMetric}" không hề xuất hiện trong câu. ` +
          `Chủ ngữ phải là chỉ số THỰC SỰ bị phán xét trong câu đó.`,
        path: at,
        excerpt: claimText.slice(0, 180),
      })
    }

    // R1 — khẳng định về chỉ số KHÔNG có dữ liệu: chặn, không ngoại lệ diễn đạt.
    if (mc.assertionStatus === 'ASSERTED' && judgemental && zeroCoverage.has(mc.subjectMetric)) {
      assertedOnMissing++
      claimIssues.push({
        rule: 'asserted_claim_on_missing_metric',
        severity: 'BLOCKER',
        message:
          `${at}: khẳng định "${mc.judgement}" về "${mc.subjectMetric}" trong khi chỉ số này ` +
          `có độ phủ 0%. Nếu là kế hoạch đo hay giới hạn phương pháp thì khai đúng loại.`,
        path: at,
        excerpt: claimText.slice(0, 180),
      })
    }

    // R2 — khẳng định có phán xét phải có bằng chứng NEO ĐƯỢC về gói.
    if (mc.assertionStatus === 'ASSERTED' && judgemental) {
      if (mc.evidenceIds.length === 0) {
        claimIssues.push({
          rule: 'asserted_claim_without_evidence',
          severity: 'BLOCKER',
          message: `${at}: ASSERTED nhưng không trích bằng chứng nào`,
          path: `${at}.evidenceIds`,
          excerpt: claimText.slice(0, 180),
        })
      } else if (!mc.evidenceIds.some((e) => isGrounded(e))) {
        claimIssues.push({
          rule: 'asserted_claim_not_grounded',
          severity: 'BLOCKER',
          message: `${at}: bằng chứng không neo được về gói`,
          path: `${at}.evidenceIds`,
        })
      }
    }

    // R4 — giới hạn phương pháp phải có CHỦ NGỮ KHÁC chỉ số bị ảnh hưởng.
    //
    // Đây là đường lách hiển nhiên nhất: dán nhãn "giới hạn phương pháp" lên
    // một khẳng định về chính chỉ số đang thiếu dữ liệu.
    if (mc.claimType === 'METHODOLOGY_LIMITATION') {
      if (mc.relatedMetric === 'NONE') {
        claimIssues.push({
          rule: 'methodology_without_related_metric',
          severity: 'BLOCKER',
          message: `${at}: METHODOLOGY_LIMITATION phải nêu relatedMetric bị ảnh hưởng`,
          path: at,
        })
      } else if (mc.relatedMetric === mc.subjectMetric) {
        claimIssues.push({
          rule: 'methodology_disguising_assertion',
          severity: 'BLOCKER',
          message: `${at}: subjectMetric trùng relatedMetric -> khẳng định trá hình`,
          path: at,
          excerpt: claimText.slice(0, 180),
        })
      } else if (zeroCoverage.has(mc.subjectMetric) && judgemental) {
        // Chủ ngữ cũng phải là chỉ số CÓ dữ liệu, nếu không thì vẫn là phán xét
        // về chỉ số thiếu, chỉ đổi nhãn.
        claimIssues.push({
          rule: 'methodology_subject_also_missing',
          severity: 'BLOCKER',
          message: `${at}: chủ ngữ "${mc.subjectMetric}" cũng không có dữ liệu -> vẫn là khẳng định về chỉ số thiếu`,
          path: at,
          excerpt: claimText.slice(0, 180),
        })
      }
    }

    // R2b — BẰNG CHỨNG phải NÓI VỀ chỉ số được phán xét.
    //
    // "Giải được id" không phải "ủng hộ kết luận". Ca thật Codex dựng: claim
    // `views LOW` trích OBS-001 vốn chỉ chứa dữ liệu retention CAO. Cả hai tồn
    // tại, cùng lineage, không chu trình — nhưng bằng chứng không nói điều claim
    // nói.
    //
    // Khi không kết luận được, phát `evidence_support_unverified` mức HIGH:
    // chặn "đạt không giám sát", chứ KHÔNG giả vờ đã chứng minh. Xem
    // creator_specs/PHASE4_TRUST_BOUNDARIES.md.
    if (mc.evidenceIds.length > 0 && mc.subjectMetric !== 'NONE') {
      const cited = mc.evidenceIds
        .map((id) => observationByEvidenceId.get(id))
        .filter((o): o is { statement: string; metricValues?: Record<string, unknown> } => Boolean(o))
      if (cited.length > 0) {
        const supports = cited.some((o) =>
          metricNamedIn(mc.subjectMetric, `${o.statement} ${Object.keys(o.metricValues ?? {}).join(' ')}`),
        )
        if (!supports) {
          qualityIssues.push({
            rule: 'evidence_support_unverified',
            severity: 'HIGH',
            message:
              `${at}: bằng chứng được trích không hề nhắc tới "${mc.subjectMetric}". ` +
              `Giải được id KHÔNG đồng nghĩa ủng hộ kết luận — cần người rà soát.`,
            path: `${at}.evidenceIds`,
            excerpt: claimText.slice(0, 180),
          })
        }
      }
    }

    // R5b — NHÂN QUẢ luôn cần bằng chứng, kể cả ở dạng có điều kiện.
    //
    // Yêu cầu bằng chứng trước đây chỉ áp cho ASSERTED, nên một claim
    // CAUSAL + CONDITIONAL đi qua mà KHÔNG có bằng chứng nào.
    if (mc.claimType === 'CAUSAL' && mc.evidenceIds.length === 0) {
      claimIssues.push({
        rule: 'causal_claim_without_evidence',
        severity: 'BLOCKER',
        message: `${at}: claim CAUSAL phải trích bằng chứng, kể cả ở dạng có điều kiện`,
        path: `${at}.evidenceIds`,
        excerpt: claimText.slice(0, 180),
      })
    }

    // R5 — nhân quả chỉ hợp lệ khi CÓ ĐIỀU KIỆN và có bằng chứng.
    if (mc.claimType === 'CAUSAL' && mc.assertionStatus === 'ASSERTED') {
      causalViolations++
      claimIssues.push({
        rule: 'asserted_causal_claim',
        severity: 'BLOCKER',
        message: `${at}: CAUSAL + ASSERTED bị cấm tuyệt đối ở tầng này`,
        path: at,
        excerpt: claimText.slice(0, 180),
      })
    }

    // R6 — tự khai cần nêu thiếu dữ liệu thì tóm tắt phải nêu thật.
    if (mc.requiresMissingnessDisclosure) {
      const constraint = output.analysisSummary.primaryConstraint.toLowerCase()
      if (!/impression|ctr|thumbnail|packaging|độ phủ|thiếu/.test(constraint)) {
        qualityIssues.push({
          rule: 'missing_missingness_disclosure',
          severity: 'HIGH',
          message: `${at}: khai cần nêu thiếu dữ liệu nhưng primaryConstraint không nhắc tới`,
          path: 'analysisSummary.primaryConstraint',
        })
      }
    }

    // R7 — tổ hợp mâu thuẫn giữa loại, trạng thái và phán xét.
    const contradictions: Array<[boolean, string]> = [
      [
        mc.assertionStatus === 'NEGATED_ACTION' && mc.claimType === 'OBSERVATION',
        'NEGATED_ACTION không thể là OBSERVATION',
      ],
      [
        mc.assertionStatus === 'LIMITATION' && mc.claimType === 'RECOMMENDATION',
        'LIMITATION không thể là RECOMMENDATION',
      ],
      [mc.assertionStatus === 'QUESTION' && judgemental, 'QUESTION không được mang phán xét khẳng định'],
      [
        mc.claimType === 'DIAGNOSTIC_PLAN' && mc.assertionStatus === 'ASSERTED',
        'DIAGNOSTIC_PLAN phải CONDITIONAL/QUESTION, không ASSERTED',
      ],
      [
        mc.claimType === 'METHODOLOGY_LIMITATION' && mc.assertionStatus === 'ASSERTED',
        'METHODOLOGY_LIMITATION phải ở trạng thái LIMITATION',
      ],
    ]
    for (const [bad, msg] of contradictions) {
      if (bad) {
        claimIssues.push({
          rule: 'contradictory_claim_fields',
          severity: 'BLOCKER',
          message: `${at}: ${msg}`,
          path: at,
          excerpt: claimText.slice(0, 180),
        })
      }
    }
  }

  if (assertedOnMissing > 0) {
    repairErrors.push(
      `${assertedOnMissing} metricClaims khẳng định về chỉ số có độ phủ 0%. ` +
        `Đổi assertionStatus sang CONDITIONAL/QUESTION/LIMITATION/NEGATED_ACTION và khai đúng ` +
        `claimType, hoặc bỏ hẳn phát biểu đó.`,
    )
  }

  // U2 — một ô chỉ được MỘT claim trỏ tới.
  for (const [canonical, ids] of claimsPerCanonical) {
    if (ids.length > 1) {
      claimIssues.push({
        rule: 'multiple_claims_for_source_unit',
        severity: 'BLOCKER',
        message: `Ô ${canonical} bị ${ids.length} claim cùng trỏ tới (${ids.join(', ')})`,
        path: canonical,
      })
    }
  }

  // U1 + U3 + U4 — đếm mệnh đề nhạy cảm trên TỪNG ô.
  const allUnits = enumerateUnits(output)
  for (const u of allUnits) {
    const clauses = clausesOf(u.text).filter((c) => SENSITIVE_MENTION.test(c))
    const declared = claimsPerCanonical.has(u.canonical)

    if (clauses.length > 1) {
      ctrViolations++
      claimIssues.push({
        rule: 'multiple_assertions_in_source_unit',
        severity: 'BLOCKER',
        message:
          `Ô ${u.canonical} chứa ${clauses.length} phát biểu về chỉ số nhạy cảm. ` +
          `Mỗi ô chỉ được một phát biểu — tách thành nhiều phần tử.`,
        path: u.pointer,
        excerpt: u.text.slice(0, 180),
      })
    }
    if (clauses.length >= 1 && !declared) {
      ctrViolations++
      claimIssues.push({
        rule: 'undeclared_sensitive_unit',
        severity: 'BLOCKER',
        message: `Ô ${u.canonical} nhắc chỉ số nhạy cảm nhưng không claim nào trỏ tới`,
        path: u.pointer,
        excerpt: u.text.slice(0, 180),
      })
    }
  }
  // U4 — claim MỒ CÔI.
  //
  // Định nghĩa theo CHỦ NGỮ ĐÃ KHAI, không theo "có nhắc chỉ số nhạy cảm".
  // Bản đầu chặn cả một claim hợp lệ về `views_d7` chỉ vì ô đó không nhắc
  // CTR/impressions — trong khi khai báo về chỉ số CÓ dữ liệu là hoàn toàn chính
  // đáng và vẫn được hưởng các phép kiểm chiều/bằng chứng.
  //
  // Việc "chủ ngữ phải xuất hiện trong ô" do quy tắc S1 đảm nhiệm; ở đây chỉ bắt
  // trường hợp ô hoàn toàn không liên quan tới bất kỳ chỉ số nào đã khai.
  for (const [id, r] of resolvedByClaim) {
    const mc = output.metricClaims.find((x) => x.id === id)
    if (!mc) continue
    const subjectSeen = mc.subjectMetric === 'NONE' || metricNamedIn(mc.subjectMetric, r.text)
    const relatedSeen = mc.relatedMetric !== 'NONE' && metricNamedIn(mc.relatedMetric, r.text)
    if (!subjectSeen && !relatedSeen) {
      claimIssues.push({
        rule: 'orphan_metric_claim',
        severity: 'BLOCKER',
        message: `${id} trỏ tới ô không nhắc tới chỉ số nào đã khai (${r.canonical})`,
        path: r.pointer,
        excerpt: r.text.slice(0, 180),
      })
    }
  }

  if (causalViolations) {
    // Kèm ĐÚNG câu vi phạm vào prompt sửa lỗi: bảo "bỏ ngôn ngữ nhân quả" mà
    // không chỉ ra ở đâu thì lần sửa sau chủ yếu là đoán.
    const samples = claimIssues
      .filter((i) => i.rule === 'causal_claim' && i.excerpt)
      .slice(0, 3)
      .map((i) => `  • ${i.path}: "${i.excerpt}"`)
    repairErrors.push(
      'Bỏ ngôn ngữ nhân quả ở phần khẳng định (tóm tắt, phát hiện, lý do khuyến nghị). ' +
        'Dùng "có liên hệ với", "phù hợp với", "có thể cho thấy". Trong hypotheses/experiments, ' +
        'nếu nêu cơ chế thì PHẢI rào đón bằng "có thể"/"giả thuyết"/"may"/"plausible".' +
        (samples.length ? `\nCác câu vi phạm:\n${samples.join('\n')}` : ''),
    )
  }
  if (ctrViolations) {
    const samples = claimIssues
      .filter((i) => i.rule === 'ctr_claim_without_coverage' && i.excerpt)
      .slice(0, 3)
      .map((i) => `  • ${i.path}: "${i.excerpt}"`)
    repairErrors.push(
      'Bỏ mọi kết luận về CTR/impressions/thumbnail — các chỉ số đó có độ phủ 0% ở gói này.' +
        (samples.length ? `\nCác câu vi phạm:\n${samples.join('\n')}` : ''),
    )
  }

  // Chỉ số bịa: tên chỉ số không có trong danh mục feature của gói.
  const knownMetrics = new Set(input.pkg.featureDefinitions.map((f) => f.key))
  let unsupportedMetricViolations = 0
  const metricLike = /\b(?:ctr|impressions?|watch_time|retention_rate|engagement_rate|rpm|cpm|revenue)\b/gi
  // Quét chỉ số BỊA trên MỌI ô văn bản (rpm/cpm/revenue không tồn tại trong hệ
  // thống). Nguồn ô nay là `enumerateUnits`, không còn `scanTargets` của 2.0.
  // NGÔN NGỮ NHÂN QUẢ trên MỌI ô văn xuôi.
  //
  // Khôi phục sau refactor 2.1: bản thay khối tương ứng cũ đã vô tình bỏ mất
  // phép quét này, khiến câu nhân quả trong văn xuôi không còn bị bắt. Đây là
  // quy tắc an toàn cốt lõi, không liên quan tới cơ chế khai báo.
  //
  // Giả thuyết/thí nghiệm được nêu CƠ CHẾ nếu có rào đón — đó là việc của một
  // giả thuyết. Phần khẳng định thì cấm tuyệt đối.
  for (const u of allUnits) {
    const isHypothesisCtx = u.canonical.startsWith('HYPOTHESIS') || u.canonical.startsWith('EXPERIMENT')
    for (const { re, label } of CAUSAL_PATTERNS) {
      for (const m of allMatches(re, u.text)) {
        if (isHypothesisCtx && HEDGE_PATTERN.test(sentenceAround(u.text, m.index))) continue
        causalViolations++
        claimIssues.push({
          rule: 'causal_claim',
          severity: 'BLOCKER',
          message: isHypothesisCtx
            ? `Giả thuyết nêu cơ chế nhân quả mà KHÔNG rào đón: "${label}"`
            : `Ngôn ngữ nhân quả không được bằng chứng hỗ trợ: "${label}"`,
          path: u.pointer,
          excerpt: excerptAround(u.text, m),
        })
      }
    }
  }

  // Văn bản NGOÀI JSON cũng là lời của mô hình: quét nhân quả và chỉ số nhạy cảm.
  if (input.proseText && input.proseText.trim()) {
    const pt = input.proseText
    for (const { re, label } of CAUSAL_PATTERNS) {
      for (const m of allMatches(re, pt)) {
        causalViolations++
        claimIssues.push({
          rule: 'causal_claim',
          severity: 'BLOCKER',
          message: `Ngôn ngữ nhân quả trong văn bản ngoài JSON: "${label}"`,
          path: '(văn bản ngoài JSON)',
          excerpt: excerptAround(pt, m),
        })
      }
    }
    if (SENSITIVE_MENTION.test(pt)) {
      ctrViolations++
      claimIssues.push({
        rule: 'undeclared_sensitive_unit',
        severity: 'BLOCKER',
        message: 'Văn bản ngoài JSON nhắc chỉ số nhạy cảm mà không thể khai báo được',
        path: '(văn bản ngoài JSON)',
        excerpt: pt.slice(0, 180),
      })
    }
  }

  for (const { pointer: path, text } of allUnits) {
    const matches = text.match(metricLike) ?? []
    for (const m of matches) {
      const key = m.toLowerCase()
      if (knownMetrics.has(key)) continue
      // "impressions"/"ctr" đã bị bắt ở nhánh CTR khi độ phủ 0; ở đây chỉ nhắm
      // các chỉ số KHÔNG hề tồn tại trong hệ thống (rpm/cpm/revenue...).
      if (['rpm', 'cpm', 'revenue'].includes(key)) {
        unsupportedMetricViolations++
        claimIssues.push({
          rule: 'unsupported_metric',
          severity: 'HIGH',
          message: `Nhắc tới chỉ số không có trong gói: "${m}"`,
          path,
        })
      }
    }
  }

  // --- 4. Chất lượng -------------------------------------------------------
  output.keyFindings.forEach((f, i) => {
    if (f.findingType !== 'LIMITATION' && f.evidenceIds.length === 0) {
      qualityIssues.push({
        rule: 'finding_without_evidence',
        severity: 'HIGH',
        message: `keyFindings[${i}] là ${f.findingType} nhưng không trích bằng chứng nào`,
        path: `keyFindings[${i}].evidenceIds`,
      })
    }
    // Độ tin cậy CAO trong khi bằng chứng mỏng là kiểu tự tin thái quá cần chặn.
    if (f.confidence === 'HIGH' && f.evidenceIds.length < 2 && f.findingType === 'SYNTHESIS') {
      qualityIssues.push({
        rule: 'overconfident_synthesis',
        severity: 'MEDIUM',
        message: `keyFindings[${i}] là SYNTHESIS, confidence HIGH nhưng chỉ có ${f.evidenceIds.length} bằng chứng`,
        path: `keyFindings[${i}].confidence`,
      })
    }
  })

  output.recommendations.forEach((r, i) => {
    if (r.priority === 'P0' && r.evidenceIds.length === 0) {
      qualityIssues.push({
        rule: 'p0_without_evidence',
        severity: 'HIGH',
        message: `recommendations[${i}] là P0 nhưng không có bằng chứng`,
        path: `recommendations[${i}]`,
      })
    }
    if (r.category !== 'INVESTIGATE' && r.successMetric.trim().length < 3) {
      qualityIssues.push({
        rule: 'unmeasurable_recommendation',
        severity: 'MEDIUM',
        message: `recommendations[${i}] không phải INVESTIGATE nhưng thiếu successMetric`,
        path: `recommendations[${i}].successMetric`,
      })
    }
  })

  // Độ tin cậy tổng thể phải phản ánh độ phủ dữ liệu.
  if (output.analysisSummary.confidence === 'HIGH' && input.pkg.confidence.band === 'LOW') {
    qualityIssues.push({
      rule: 'confidence_exceeds_coverage',
      severity: 'HIGH',
      message: 'Cursor báo confidence HIGH trong khi độ tin cậy dữ liệu của gói là LOW',
      path: 'analysisSummary.confidence',
    })
  }

  // selfCheck là lời tự khai; đối chiếu với kết quả kiểm định độc lập.
  if (output.selfCheck.madeCausalClaims === false && causalViolations > 0) {
    qualityIssues.push({
      rule: 'selfcheck_contradicted',
      severity: 'HIGH',
      message: `selfCheck khai không có câu nhân quả nhưng phát hiện ${causalViolations}`,
      path: 'selfCheck.madeCausalClaims',
    })
  }
  if (output.selfCheck.madeCtrOrImpressionClaims === false && ctrViolations > 0) {
    qualityIssues.push({
      rule: 'selfcheck_contradicted',
      severity: 'HIGH',
      message: `selfCheck khai không có kết luận CTR nhưng phát hiện ${ctrViolations}`,
      path: 'selfCheck.madeCtrOrImpressionClaims',
    })
  }
  if (output.selfCheck.allFindingEvidenceResolved === true && unresolvedRefs > 0) {
    qualityIssues.push({
      rule: 'selfcheck_contradicted',
      severity: 'HIGH',
      message: `selfCheck khai bằng chứng đã giải hết nhưng còn ${unresolvedRefs} id không hợp lệ`,
      path: 'selfCheck.allFindingEvidenceResolved',
    })
  }

  // Trần mảng (Zod đã chặn, nhưng kiểm lại để báo cáo có con số rõ ràng).
  const overLimit: string[] = []
  if (output.keyFindings.length > OUTPUT_LIMITS.keyFindings) overLimit.push('keyFindings')
  if (output.hypotheses.length > OUTPUT_LIMITS.hypotheses) overLimit.push('hypotheses')
  if (output.recommendations.length > OUTPUT_LIMITS.recommendations) overLimit.push('recommendations')
  for (const name of overLimit) {
    structuralIssues.push({
      rule: 'array_limit',
      severity: 'BLOCKER',
      message: `${name} vượt trần cho phép`,
    })
  }

  const allIssues = [...structuralIssues, ...evidenceIssues, ...claimIssues, ...qualityIssues]

  /**
   * ĐẠT đòi hỏi không còn BLOCKER *và* không còn HIGH.
   *
   * Trước đây chỉ BLOCKER mới chặn, nên một kết quả có thể được ghi SUCCEEDED
   * trong khi vẫn mang lỗi HIGH. Đây không phải rủi ro lý thuyết: một lần chạy
   * hinh_su thật đã được lưu là SUCCEEDED kèm 3 lỗi HIGH — hai phát hiện không
   * trích bằng chứng nào và một khuyến nghị P0 không bằng chứng. Kết quả "đạt"
   * ấy trông y hệt một kết quả thực sự đạt ở mọi bảng biểu phía sau.
   *
   * HIGH ở đây gồm: nhắc chỉ số không tồn tại (rpm/cpm/revenue), phát hiện
   * không bằng chứng, P0 không bằng chứng, tin cậy vượt độ phủ dữ liệu, và
   * selfCheck mâu thuẫn với kiểm định. Không cái nào nên đi kèm chữ "đạt".
   */
  const blockers = allIssues.filter((i) => i.severity === 'BLOCKER')
  const highs = allIssues.filter((i) => i.severity === 'HIGH')

  const failureClass: ValidateResult['failureClass'] =
    blockers.length === 0 && highs.length === 0
      ? 'NONE'
      : // Khẳng định bị cấm được xét TRƯỚC lỗi định dạng: nếu văn bản ngoài JSON
        // chứa câu nhân quả/CTR thì đó là thất bại NỘI DUNG, không được thử lại,
        // dù đồng thời cũng có lỗi định dạng.
        causalViolations > 0 || ctrViolations > 0 || unsupportedMetricViolations > 0
        ? 'UNSUPPORTED_CLAIM'
        : input.hadProseOutsideJson
          ? 'PROSE_OUTSIDE_JSON'
        : unresolvedRefs > 0 || ungroundedItems > 0
          ? 'EVIDENCE_UNRESOLVED'
          : blockers.length > 0
            ? 'SCHEMA_MISMATCH'
            : // Lỗi HIGH thuần chất lượng (thiếu bằng chứng, tự tin thái quá) là
              // thất bại NỘI DUNG, không phải kỹ thuật -> không được retry.
              'UNSUPPORTED_CLAIM'

  if (highs.length > 0) {
    repairErrors.push(
      `${highs.length} lỗi mức HIGH: ` +
        highs
          .slice(0, 5)
          .map((i) => `${i.path ?? i.rule}: ${i.message}`)
          .join(' | '),
    )
  }

  return {
    report: {
      passed: blockers.length === 0 && highs.length === 0,
      structuralIssues,
      evidenceIssues,
      claimIssues,
      qualityIssues,
      evidenceResolutionRate: totalRefs === 0 ? null : (totalRefs - unresolvedRefs) / totalRefs,
      totalEvidenceRefs: totalRefs,
      unresolvedEvidenceRefs: unresolvedRefs,
      causalViolations,
      ctrViolations,
      unsupportedMetricViolations,
      counts: {
        findings: output.keyFindings.length,
        hypotheses: output.hypotheses.length,
        recommendations: output.recommendations.length,
        experiments: output.experiments.length,
      },
    },
    output,
    failureClass,
    repairErrors,
  }
}
