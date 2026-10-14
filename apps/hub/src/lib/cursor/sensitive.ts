import { SENSITIVE_METRICS } from './schema'

/**
 * TỪ VỰNG CHỈ SỐ dùng chung cho cả hai lượt.
 *
 * Tách khỏi `validate.ts` vì bộ SINH NGHĨA VỤ (lượt 1) và bộ KIỂM ĐỊNH (lượt 2)
 * đều cần đúng bộ từ vựng này. Để nó nằm trong validator rồi cho bộ sinh nghĩa
 * vụ import ngược lại sẽ tạo vòng phụ thuộc; chép sang một bản thứ hai thì sớm
 * muộn cũng lệch — và "hai danh sách cho cùng một khái niệm" đúng là lỗi đã
 * khiến "tỷ lệ click" không được nhận là chỉ số nhạy cảm.
 *
 * ĐÂY LÀ HỢP ĐỒNG, không phải tiện ích: đổi bất kỳ mẫu nào trong tệp này là đổi
 * định nghĩa "ô nào phải khai báo", nên phải tăng `OBLIGATION_GENERATOR_VERSION`.
 */

/** Tên chỉ số (kể cả cách gọi tiếng Việt) có xuất hiện trong câu không. */
const METRIC_ALIAS_RAW: Record<string, RegExp> = {
  impressions: /impressions?|lượt hiển thị/iu,
  // `impression_ctr` phải khớp CHÍNH TÊN KHOÁ của nó.
  //
  // `\bctr\b` KHÔNG khớp chuỗi "impression_ctr": ký tự đứng trước "ctr" là "_",
  // vốn thuộc `\w`, nên biên từ không tồn tại ở đó. Đây là lần thứ tư cùng cái
  // bẫy `\b` trong tệp này — và lần này nó đắt nhất, vì prompt BẢO mô hình dùng
  // đúng chuỗi `impression_ctr`, nên mô hình viết đúng chữ đó vào văn xuôi rồi
  // bị S1 báo "chủ ngữ không xuất hiện trong câu". Lần thăm dõi hinh_su đầu tiên
  // của 3.0.0 mất 4 lỗi mồ côi và 4 lỗi chủ ngữ chỉ vì một biên từ.
  //
  // Có test bất biến: mọi khoá trong CLAIM_METRICS phải tự khớp tên nó.
  impression_ctr: /impression_ctr|\bctr\b|click-?through|tỉ lệ nhấp|tỷ lệ nhấp|tỷ lệ click|tỉ lệ click/iu,
  // "ảnh bìa" là cách gọi PHỔ BIẾN NHẤT cho thumbnail trong tiếng Việt, và nó
  // vắng mặt suốt — bảng này biết "hình thu nhỏ" (bản dịch sát nghĩa, ít ai
  // dùng) và "ảnh đại diện" (thật ra là avatar) nhưng KHÔNG biết "ảnh bìa".
  //
  // Hệ quả không phải một cảnh báo bị bỏ sót, mà là một hiện vật SAI: một bài
  // phân tích viết toàn bộ kết luận về "ảnh bìa" sinh ra 0 nghĩa vụ, đi qua
  // chặng hợp nhất, và ra đời với đầy đủ giấy tờ — đọc như "phân tích sạch"
  // trong khi sự thật là "bộ dò không thấy gì". Xem mục 5 của
  // `creator_specs/PHASE4_TRUST_BOUNDARIES.md`.
  //
  // Dùng dạng HAI TỪ ("ảnh bìa"/"hình bìa"), không dùng "bìa" trần: từ đơn ấy
  // xuất hiện trong quá nhiều ngữ cảnh không liên quan.
  thumbnail: /thumbnail|hình thu nhỏ|ảnh đại diện|ảnh bìa|hình bìa/iu,
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

/**
 * Dạng viết CỦA CHÍNH KHOÁ — snake_case VÀ camelCase — sinh TỰ ĐỘNG.
 *
 * Lô thăm dò 2026-08-13 trượt 0/18 vì đúng một khoảng trống ở đây. Mô hình viết
 * `impressionCtr` (camelCase) chứ không viết `impression_ctr`, và nó viết vậy vì
 * đó là TÊN TRƯỜNG THẬT trong gói dữ liệu nó được đưa: `metricCoverage
 * .impressionCtr`, vốn lấy nguyên từ tên trường của YouTube API qua
 * `sync/ingest`. Bí danh chỉ biết `impression_ctr` và `\bctr\b`; trong
 * "impressionCtr" thì trước "C" là "n" nên KHÔNG có biên từ, và cả hai đều trượt.
 *
 * Hệ quả không phải một cảnh báo bị bỏ sót mà là TOÀN BỘ đường ống đứng: mọi
 * kênh đều có ràng buộc chính là "impressions/CTR phủ 0%", nên bài phân tích nào
 * cũng phải nhắc tới nó, nên bài nào cũng ăn `subject_metric_not_in_text` ở chặng
 * hợp nhất. 0 hiện vật chính thức trên 18 lần thử.
 *
 * Đây là lần thứ NĂM cùng cái bẫy biên từ trong tệp này. Bốn lần trước đều được
 * vá bằng cách thêm tay một mẫu nữa — và lần nào cũng chỉ vá đúng khoá vừa cháy.
 * Nên lần này KHÔNG vá tay: dạng tên của chính khoá được SINH RA từ khoá, nên
 * mọi khoá thêm về sau tự có cả hai dạng, kể cả khoá chưa ai nghĩ tới.
 *
 * `views_d7` -> `viewsD7` và `average_view_percentage` -> `averageViewPercentage`
 * cũng đang hỏng y hệt; bản sinh này đóng cả ba cùng lúc.
 */
function selfNameSource(metric: string): string {
  const esc = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/gu, '\\$&')
  const camel = metric.replace(/_([a-z0-9])/gu, (_m, c: string) => c.toUpperCase())
  return camel === metric ? esc(metric) : `${esc(metric)}|${esc(camel)}`
}

/**
 * Bảng bí danh THẬT: bí danh viết tay ở trên, CỘNG dạng tên tự sinh của khoá.
 *
 * Gói vào một chỗ để `metricNamedIn`, `SENSITIVE_MENTION` và
 * `mentionedSensitiveMetrics` cùng hưởng — cả ba đều đọc từ bảng này, nên không
 * có đường nào nhận ra `impressionCtr` mà đường kia thì không.
 */
export const METRIC_ALIASES: Record<string, RegExp> = Object.fromEntries(
  Object.entries(METRIC_ALIAS_RAW).map(([key, re]) => [
    key,
    new RegExp(`${selfNameSource(key)}|${re.source}`, 'iu'),
  ]),
)

export function metricNamedIn(metric: string, text: string): boolean {
  const re = METRIC_ALIASES[metric]
  return re ? re.test(text) : true
}

/**
 * Có nhắc tới chỉ số NHẠY CẢM hay không — chỉ để hỏi "đã khai chưa".
 *
 * Cố ý RỘNG và NGU: nó không cần biết ai bổ nghĩa cho ai, chỉ cần biết ô này có
 * chạm tới vùng nhạy cảm. Mọi phán xét ngữ nghĩa nằm ở `metricClaims`.
 *
 * SINH TỪ `METRIC_ALIASES`, không viết tay lần thứ hai. Bản viết tay đã lệch:
 * nó biết "tỉ lệ nhấp" nhưng KHÔNG biết "tỷ lệ click" — trong khi bảng bí danh
 * biết cả hai. Hệ quả là một ô viết "tỷ lệ click thấp" không bị coi là ô nhạy
 * cảm, nên U3 không đòi khai báo và cả phát biểu đó lọt qua trong im lặng. Hai
 * danh sách cho cùng một khái niệm thì sớm muộn cũng lệch; một danh sách thì không.
 */
/**
 * Nguồn CHUNG cho mọi biểu thức nhận diện chỉ số nhạy cảm.
 *
 * Xuất ra dưới dạng CHUỖI vì `validate.ts` cần ghép nó vào một biểu thức lớn hơn
 * (chủ ngữ + phán xét). Trước đây tệp đó tự viết một danh sách chủ ngữ THỨ HAI
 * (`ctr|click-?through|impressions?|thumbnail|hình thu nhỏ|tỉ lệ nhấp`), và hai
 * danh sách lệch nhau đúng như tệp này đã cảnh báo: `ảnh bìa`, `hình bìa`,
 * `ảnh đại diện`, `packaging`, `đóng gói`, `tỷ lệ click` có trong bảng bí danh
 * nhưng KHÔNG có trong danh sách kia. Hệ quả: một khẳng định dùng các tên ấy
 * không bị nhận là khẳng định, và câu tự-từ-chối đi kèm hạ nó xuống lớp THỬ LẠI
 * ĐƯỢC. Một danh sách thì không lệch được.
 */
export const SENSITIVE_SUBJECT_SOURCE = SENSITIVE_METRICS.map(
  (m) => METRIC_ALIASES[m]!.source,
).join('|')

export const SENSITIVE_MENTION = new RegExp(`(?:${SENSITIVE_SUBJECT_SOURCE})`, 'iu')

export function mentionedSensitiveMetrics(text: string): Set<string> {
  const out = new Set<string>()
  for (const m of SENSITIVE_METRICS) {
    if (METRIC_ALIASES[m]!.test(text)) out.add(m)
  }
  return out
}


/**
 * Ô mà CẤU TRÚC đã quy định hành vi lời nói — tình thái không đọc từ từ ngữ.
 *
 * Vấn đề thật, thấy ở CẢ HAI lần thăm dò hinh_su của 3.0.0. Một ô như
 *   dataRequests[0].metricOrArtifact = "impressions cấp video"
 * là một NHÃN: nó nêu dữ liệu cần thu thập, không phát biểu gì về giá trị của
 * chỉ số. Nhãn không mang từ điều kiện, từ nghi vấn, từ phủ định hay từ giới
 * hạn — nên MỌI `assertionStatus` cần dấu hiệu đều bị S2 từ chối. Trạng thái
 * DUY NHẤT sống sót là `ASSERTED`, vì S2 không đòi dấu hiệu cho nó.
 *
 * Tức là: ở đúng những ô vô hại nhất, hợp đồng ép mô hình khai trạng thái MẠNH
 * NHẤT. Lần thăm dò 1 chọn các trạng thái đúng nghĩa và ăn 21 lỗi tình thái;
 * lần 2 né bằng cách không khai gì và ăn 17 lỗi U3. Hai chiến lược ngược nhau,
 * cùng một nguyên nhân.
 *
 * Cách sửa KHÔNG phải nới S2 — mà là lấy tình thái từ nguồn TẤT ĐỊNH hơn: tên
 * trường trong schema. `metricOrArtifact` là "dữ liệu cần thu thập",
 * `missingEvidence` là "bằng chứng còn thiếu", `reviewQuestions` là "câu hỏi".
 * Cấu trúc nói điều đó chắc chắn hơn mọi phép dò từ khoá.
 *
 * Và nó SIẾT chứ không nới: `ASSERTED` bị CẤM ở các ô này. Trước đây nó là
 * trạng thái duy nhất đi qua được; nay nó là trạng thái duy nhất KHÔNG đi qua.
 */
export const STRUCTURAL_SPEECH_ACT: Record<string, { allowed: readonly string[]; role: string }> = {
  'DATA_REQUEST|metricOrArtifact': {
    allowed: ['CONDITIONAL', 'LIMITATION'],
    role: 'nhãn dữ liệu CẦN THU THẬP',
  },
  'HYPOTHESIS|missingEvidence': {
    allowed: ['LIMITATION', 'CONDITIONAL'],
    role: 'bằng chứng CÒN THIẾU',
  },
  'MANUAL_REVIEW|reviewQuestions': {
    allowed: ['QUESTION', 'CONDITIONAL'],
    role: 'câu hỏi rà soát thủ công',
  },
}


/** Khoá tra `STRUCTURAL_SPEECH_ACT` từ một `sourceRef`. */
export function speechActKey(section: string, field: string): string {
  return `${section}|${field.replace(/@\d+$/u, '')}`
}
