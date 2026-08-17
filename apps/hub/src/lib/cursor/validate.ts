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
  ANALYSIS_SCHEMA_VERSION,
  cursorAnalysisSchema,
  declarationOutputSchema,
  SENSITIVE_METRICS,
  type ClaimDeclaration,
  type ClaimObligationSet,
  type CursorOutput,
} from './schema'
import { checkDeclarationIdentity, checkObligationSetHash } from './obligation'
import {
  METRIC_ALIASES,
  mentionedSensitiveMetrics,
  metricNamedIn,
  SENSITIVE_MENTION,
  SENSITIVE_SUBJECT_SOURCE,
  speechActKey,
  STRUCTURAL_SPEECH_ACT,
} from './sensitive'

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

/**
 * MÂU THUẪN giữa `claimType` và `assertionStatus` — NGUỒN DUY NHẤT.
 *
 * Xuất ra để `declaration-prompt.ts` in đúng năm luật này cho mô hình. Trước
 * đây bảng nằm ngay trong vòng lặp kiểm định, còn prompt chép tay MỘT PHẦN —
 * và phần chép thiếu đúng hai luật, khiến lô 5 ăn 8 lỗi `NEGATED_ACTION không
 * thể là OBSERVATION` cho một quy tắc chưa từng được nêu. Có test buộc mọi
 * thông điệp ở đây phải xuất hiện trong prompt.
 */
export const CLAIM_CONTRADICTIONS: ReadonlyArray<{
  message: string
  test: (mc: { assertionStatus: string; claimType: string }, judgemental: boolean) => boolean
}> = [
  {
    message: 'NEGATED_ACTION không thể là OBSERVATION',
    test: (mc) => mc.assertionStatus === 'NEGATED_ACTION' && mc.claimType === 'OBSERVATION',
  },
  {
    message: 'LIMITATION không thể là RECOMMENDATION',
    test: (mc) => mc.assertionStatus === 'LIMITATION' && mc.claimType === 'RECOMMENDATION',
  },
  {
    message: 'QUESTION không được mang phán xét khẳng định',
    test: (mc, judgemental) => mc.assertionStatus === 'QUESTION' && judgemental,
  },
  {
    message: 'DIAGNOSTIC_PLAN phải CONDITIONAL/QUESTION, không ASSERTED',
    test: (mc) => mc.claimType === 'DIAGNOSTIC_PLAN' && mc.assertionStatus === 'ASSERTED',
  },
  {
    message: 'METHODOLOGY_LIMITATION phải ở trạng thái LIMITATION',
    test: (mc) => mc.claimType === 'METHODOLOGY_LIMITATION' && mc.assertionStatus === 'ASSERTED',
  },
]

/**
 * XUẤT RA để `declaration-prompt.ts` DẠY đúng luật này cho mô hình.
 *
 * Lô thăm dò 2026-08-13 (cả hai lần) trượt 0/18, và 101 lỗi BLOCKER là
 * `modality_not_supported_by_text` — tức mô hình bị chấm theo một luật mà prompt
 * CHƯA TỪNG nêu. Prompt chỉ bảo "chọn assertionStatus trong danh sách hợp lệ",
 * không nói mỗi trạng thái đòi một DẤU HIỆU TỪ VỰNG ngay trong câu.
 *
 * Không model nào vượt được một luật không được phát. Nên bảng này phải là
 * nguồn DUY NHẤT cho cả hai phía: bên cưỡng chế và bên yêu cầu. Có test bất
 * biến buộc mọi ví dụ in ra prompt phải THẬT SỰ khớp bảng này.
 */
export const MODALITY_MARKERS: Record<string, RegExp> = {
  /*
   * CÓ RÀO ĐÓN cũng là một dấu hiệu ĐIỀU KIỆN.
   *
   * Thiếu nhóm này thì một giả thuyết nhân quả ĐƯỢC RÀO ĐÓN ĐÚNG CÁCH không còn
   * bản khai nào hợp lệ — đã đo bằng chạy trên cả 10 tổ hợp claimType ×
   * assertionStatus của câu "Có thể thumbnail kém dẫn tới lượt xem giảm.":
   *
   *   CAUSAL      + ASSERTED  -> asserted_causal_claim (R5 cấm tuyệt đối)
   *   CAUSAL      + 4 tình thái còn lại -> modality_not_supported_by_text
   *   không-CAUSAL + mọi tình thái      -> causal_language_in_non_causal_claim
   *
   * Tức là chặng hợp nhất từ chối VĨNH VIỄN một bài phân tích đúng hợp đồng, và
   * mô hình không có nước sửa nào — trong khi chính prompt sửa lỗi bảo nó viết
   * đúng dạng ấy, và bản quét theo Ô đã tha đúng câu ấy nhờ `HEDGE_PATTERN`.
   * Hai bề mặt cùng đọc một câu mà kết luận ngược nhau.
   *
   * Từ vựng ở đây khớp `HEDGE_PATTERN`: rào đón nghĩa là "có thể xảy ra", đúng
   * nghĩa CONDITIONAL. Nới ở đây KHÔNG mở đường cho khẳng định: R5 vẫn cấm tuyệt
   * đối CAUSAL + ASSERTED, và R4 vẫn buộc claim CAUSAL phải trích bằng chứng.
   */
  CONDITIONAL:
    /(?:nếu|\bkhi\b|khi nào|khi có|sau khi|một khi|giả sử|sẽ|nếu như|\bif\b|\bwhen\b|\bonce\b|\bshould\b|>\s*0|>=|đạt|mục tiêu|target|cần đo|cần thu thập|có thể|có lẽ|có khả năng|dường như|nghi ngờ|chưa kiểm chứng|\bmay\b|\bmight\b|\bcould\b|possibly|plausible)/iu,
  QUESTION: /\?\s*$|(?:có phải|hay là|có nên|\bhay\b|liệu|\bwhether\b)/iu,
  NEGATED_ACTION: /(?:thay vì|không|chưa|tránh|đừng|instead of|avoid|\bnot\b|\bno\b)/iu,
  /*
   * CÁCH TIẾNG VIỆT DIỄN ĐẠT "BẤT KHẢ" — đo trên 383 câu thật của 4 lô thăm dò.
   *
   * Bảng cũ chỉ biết một dạng duy nhất là "0%":
   *
   *   "không … được"   123 câu -> bắt  18, BỎ SÓT 105
   *   "thiếu"          116 câu -> bắt  12, BỎ SÓT 104
   *   "không có"        72 câu -> bắt   4, BỎ SÓT  68
   *   "chưa … được"     13 câu -> bắt   1, BỎ SÓT  12
   *   "phủ 0%"          50 câu -> bắt  50, bỏ sót   0
   *
   * Hệ quả là một vòng luẩn quẩn: câu nêu thiếu dữ liệu BUỘC phải là
   * METHODOLOGY_LIMITATION, thứ này BUỘC assertionStatus = LIMITATION, mà
   * LIMITATION lại không nhận ra chính câu ấy. 96/145 lỗi BLOCKER của lô 4 là
   * đúng vòng này — 64 lần chọn LIMITATION rồi trượt dấu hiệu, 32 lần né sang
   * trạng thái khác rồi trượt claimType.
   *
   * Nới ở đây KHÔNG mở đường cho khẳng định: xem chốt R1b ngay dưới R1, cấm mọi
   * bản khai không-ASSERTED mang PHÁN XÉT về chỉ số thiếu dữ liệu. Nói cách
   * khác, "không đánh giá được khâu tiếp cận" thì qua, còn "CTR thấp nên không
   * tăng được view" thì bị chặn — vì nó phán xét một chỉ số phủ 0%.
   */
  LIMITATION:
    /(?:nhiễu|không ổn định|chưa đủ|không đủ|hạn chế|giới hạn|độ tin cậy|khó|dễ nhầm|chưa thể|không thể|noisy|unstable|insufficient|limitation|unreliable|0\s*%|bằng không|bằng 0|=\s*0|quá thấp để|thấp để|không\s+\S+(?:\s+\S+){0,2}\s+được|chưa\s+\S+(?:\s+\S+){0,2}\s+được|không có|\bthiếu\b|vắng mặt|chưa thu thập|chưa có)/iu,
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
/**
 * Liên từ LIỆT KÊ — nối các MỤC, không mở mệnh đề mới.
 *
 * KHÔNG bọc `\b`: "và" và "hoặc" kết thúc bằng chữ có dấu, `\b` phía sau là
 * nhánh chết (lần thứ năm của cái bẫy này trong tệp).
 */
const LIST_COORD_INITIAL = /^(?:và|hay|hoặc)(?=\s|$)/iu
const LIST_COORD_ANY = /(?:^|\s)(?:và|hay|hoặc)(?=\s)/iu

/**
 * Liên từ ĐỐI LẬP / NHÂN QUẢ — luôn mở một mệnh đề mới.
 *
 * Đứng đầu một mảnh thì mảnh đó là phát biểu riêng, bất kể phần trước có phải
 * liệt kê hay không. Nhờ nó, "A, B, hay C, nhưng D" ra đúng HAI phát biểu chứ
 * không phải một.
 */
const NEW_CLAUSE_INITIAL =
  /^(?:nhưng|tuy nhiên|do đó|vì vậy|vì thế|song|còn|mặt khác|ngoài ra|đồng thời|trong khi|nên)(?=\s|$)/iu

/** Trạng ngữ ĐỨNG TRƯỚC: "Khi có X, làm Y" là MỘT phát biểu có điều kiện. */
const FRONTED_ADJUNCT =
  /^(?:nếu như|nếu|khi nào|khi có|khi|sau khi|một khi|giả sử|trong trường hợp|với điều kiện)(?=\s|$)/iu

/** Dấu hiệu PHÁN XÉT — dùng để phân biệt mục liệt kê với một phát biểu thật. */
const JUDGEMENT_ANY =
  /(?:\bcao\b|\bthấp\b|\btốt\b|\bkém\b|\bmạnh\b|\byếu\b|vượt trội|\btăng\b|\bgiảm\b|sụt|cải thiện|hiệu quả|\bhigh\b|\blow\b|\bstrong\b|\bweak\b|\bgood\b|\bpoor\b|increased?|decreased?|improved?|dropped|\bfell\b|\bgrew\b)/iu

/**
 * Khẳng định ĐỊNH LƯỢNG — "đạt 10.000", "bằng 0%", "dưới 2%".
 *
 * Một mục liệt kê là một cái TÊN; gắn số vào là đã phát biểu điều gì đó. Thiếu
 * phép kiểm này, "CTR đạt 8%, impressions và lượt xem đạt 10.000" bị gộp thành
 * một mệnh đề và U1 không thấy hai khẳng định. Ca do Codex dựng.
 *
 * KHÔNG dùng "có chữ số" làm dấu hiệu: ô hợp lệ "…hoặc packaging vì impressions
 * và impression_ctr độ phủ 0%" cũng có chữ số, và chặn nó là quay lại đúng lỗi
 * chặn oan vừa sửa. Phải là ĐỘNG TỪ định lượng đi kèm số.
 *
 * KHÔNG bọc `\b`: "đạt"/"bằng"/"dưới" mở đầu bằng chữ có dấu, `\b` phía trước
 * là nhánh chết với cờ `u`. `(?:^|\s)` làm đúng việc đó mà không chết.
 */
const QUANTITATIVE_ASSERTION = /(?:^|\s)(?:đạt|bằng|chiếm|vượt|dưới|trên)\s+[\d<>≥≤]/iu

/** Mảnh này có phát biểu điều gì không, hay chỉ là một cái TÊN trong danh sách. */
function carriesPredication(fragment: string): boolean {
  return JUDGEMENT_ANY.test(fragment) || QUANTITATIVE_ASSERTION.test(fragment)
}

/**
 * Một CHUỖI mảnh nối bằng dấu phẩy có phải LIỆT KÊ hay TRẠNG NGỮ ĐỨNG TRƯỚC không.
 *
 * Hai dấu hiệu, cả hai đều nhìn vào VỊ TRÍ chứ không chỉ nhìn từ khoá:
 *
 *  - một mảnh (không phải mảnh đầu) MỞ ĐẦU bằng liên từ liệt kê
 *    -> "thumbnail, tiêu đề, hay packaging";
 *  - một mảnh (không phải mảnh đầu) CHỨA liên từ liệt kê mà KHÔNG mang dấu hiệu
 *    phán xét nào -> "tiếp cận, CTR, thumbnail và packaging" (tiếng Việt thường
 *    bỏ dấu phẩy trước "và" ở mục cuối, nên liên từ nằm GIỮA mảnh cuối).
 *
 * Điều kiện "không mang phán xét" là hàng rào giữ cho phép gộp không nuốt một ca
 * hai phát biểu thật: "CTR thấp, impressions và thumbnail đều cao" có "cao" ở
 * mảnh sau nên KHÔNG bị coi là liệt kê.
 */
function isEnumerationRun(run: string[]): boolean {
  if (run.length < 2) return false
  // Điều kiện "không mang phát biểu" áp cho CẢ HAI nhánh, kể cả nhánh mở đầu
  // bằng liên từ. Thiếu nó, "CTR thấp, và impressions cao" bị gộp thành một —
  // hai khẳng định thật biến mất khỏi tầm nhìn của U1. Ca do Codex dựng.
  return run
    .slice(1)
    .some(
      (f) =>
        (LIST_COORD_INITIAL.test(f) || LIST_COORD_ANY.test(f)) && !carriesPredication(f),
    )
}

/**
 * Cụm trong ngoặc đơn không được tách: dấu câu bên trong là của cụm, không của câu.
 *
 * LẶP từ trong ra ngoài. Một lượt `replace` chỉ che được cặp ngoặc TRONG CÙNG,
 * nên "CTR (ghi chu (a, b), tiep) thap" con sot dau phay cua cap ngoai va van bi
 * cat. Ca do Codex dung. Tran vong lap la hang rao chong van ban di dang.
 *
 * Ngoac THIEU VE DONG thi khong che duoc — khong co cach nao biet cum ket thuc o
 * dau. Ghi ro o day thay vi doan bua.
 *
 * Ky tu canh viet bang ESCAPE `\u0000`, KHONG dat ky tu dieu khien that vao tep
 * nguon: mot byte NUL nam trong ma khien `rg`/`grep` coi ca tep la nhi phan va bo
 * qua no — chinh dieu do da can mot vong ra soat Codex.
 */
function maskParentheticals(text: string): { masked: string; restore: (s: string) => string } {
  const store: string[] = []
  const OPEN = '\u0000'
  const CLOSE = '\u0001'
  let masked = text
  for (let pass = 0; pass < 8; pass++) {
    const next = masked.replace(/\([^()]*\)/gu, (m) => {
      store.push(m)
      return `${OPEN}${store.length - 1}${CLOSE}`
    })
    if (next === masked) break
    masked = next
  }
  const restore = (s: string): string => {
    let out = s
    for (let pass = 0; pass < 8; pass++) {
      // CHI thay chi so CO THAT. Ban truoc thay moi thu khop mau bang `?? ''`,
      // nen mot chuoi canh co san trong van ban dau vao se bi XOA mat.
      const next = out.replace(
        new RegExp(`${OPEN}(\\d+)${CLOSE}`, 'gu'),
        (m, n: string) => store[Number(n)] ?? m,
      )
      if (next === out) break
      out = next
    }
    return out
  }
  return { masked, restore }
}

const CLAUSE_SEPARATOR =
  /((?:\.(?!\d)|[!?;:\n])|,\s+|\s+(?:nhưng|còn|đồng thời|trong khi|tuy nhiên|mặt khác|ngoài ra)\s+)/iu

export function clausesOf(text: string): string[] {
  const { masked, restore } = maskParentheticals(text)

  // Tách nhưng GIỮ dấu phân cách: `split` với nhóm bắt trả về xen kẽ
  // [mảnh, dấu, mảnh, dấu, …], nhờ đó phân biệt được ranh giới DẤU PHẨY với các
  // ranh giới khác. Chỉ dấu phẩy mới được xét gộp lại.
  const parts = masked.split(CLAUSE_SEPARATOR)
  const frags: string[] = []
  const seps: string[] = []
  parts.forEach((p, i) => {
    if (i % 2 === 0) frags.push((p ?? '').trim())
    else seps.push(p ?? '')
  })

  const out: string[] = []
  let i = 0
  while (i < frags.length) {
    // Chuỗi tối đa các mảnh nối liên tiếp bằng DẤU PHẨY, dừng trước một mảnh mở
    // đầu bằng liên từ đối lập/nhân quả — mảnh đó luôn là phát biểu riêng.
    let j = i
    while (
      j < frags.length - 1 &&
      /^,/u.test(seps[j] ?? '') &&
      !NEW_CLAUSE_INITIAL.test(frags[j + 1] ?? '')
    ) {
      j++
    }
    const run = frags.slice(i, j + 1).filter(Boolean)
    if (run.length > 1 && isEnumerationRun(run)) {
      // Liệt kê: cả chuỗi là MỘT phát biểu.
      out.push(run.join(', '))
    } else if (run.length > 1 && FRONTED_ADJUNCT.test(run[0]!)) {
      // Trạng ngữ đứng trước chỉ chứng minh dấu phẩy THỨ NHẤT thuộc cấu trúc
      // điều kiện. Gộp cả chuỗi là quá tay: trong
      //   "Nếu CTR dưới 2%, thumbnail đang dùng bản A, impressions đạt 10.000"
      // mảnh thứ ba là một khẳng định riêng, và gộp nó vào sẽ giấu mất một phát
      // biểu khỏi U1. Ca do Codex dựng.
      out.push([run[0], run[1]].join(', '), ...run.slice(2))
    } else {
      out.push(...run)
    }
    i = j + 1
  }

  return out.map(restore).map((x) => x.trim()).filter(Boolean)
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
/*
 * ĐÃ GỠ: `CTR_SUBJECT` / `CTR_JUDGEMENT` / `CTR_QUANTITY` / `CTR_CLAIM_PATTERNS`.
 *
 * Bộ dò phán xét hai chiều ấy từng được dùng để hỏi "mệnh đề này có KHẲNG ĐỊNH
 * gì về chỉ số không". Hai vòng rà soát liên tiếp phá được nó theo đúng một
 * kiểu: không gian cách diễn đạt một khẳng định là VÔ HẠN, nên mọi danh sách từ
 * vựng đều thiếu, và mỗi chỗ thiếu là một khẳng định bị cấm được tha.
 *
 * Nay phép thử là ĐÓNG (`onlyDisclaims` trong `scanProseOutsideJson`): liệt kê
 * cái VÔ HẠI thay vì cái bị cấm. Giữ lại mã chết kèm ~80 dòng chú thích mô tả
 * một cơ chế không còn chạy chính là thứ rà soát đối kháng đã gọi tên, nên nó
 * được gỡ hẳn thay vì để lại.
 */


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

/**
 * `path` của mọi vi phạm phát hiện trong VĂN BẢN NGOÀI JSON.
 *
 * Hằng số chứ không phải chuỗi rải rác: phép lọc theo chặng phải phân biệt được
 * "ô trong JSON" với "văn bản ngoài JSON", và một chuỗi gõ tay ở ba nơi thì chỉ
 * cần lệch một dấu cách là phép lọc âm thầm sai.
 */
export const PROSE_OUTSIDE_JSON_PATH = '(văn bản ngoài JSON)'

/**
 * MỌI quy tắc làm `ctrViolations` tăng — MỘT danh sách, dùng ở mọi nơi.
 *
 * Ba tên này được phát ra ở BỐN chỗ (một trong số đó là văn bản ngoài JSON).
 * Trước đây khối hướng dẫn CTR mang hai danh sách riêng: một để lọc theo chặng
 * (đúng) và một để chọn câu vi phạm (`ctr_claim_without_coverage` — không quy
 * tắc nào phát ra, nên luôn rỗng). Hai danh sách cho cùng một khái niệm thì sớm
 * muộn cũng lệch; một danh sách thì không.
 */
/**
 * Quy tắc chặng KHAI BÁO là lỗi KỸ THUẬT — được phép thử lại.
 *
 * Cả năm đều là "mô hình chép sai hoặc khai không đúng TẬP được giao", và
 * `repairErrors` đã nêu chính xác phải sửa gì. Thử lại ở đây không cho mô hình
 * đổi kết luận: tập nghĩa vụ cố định trong suốt lần chạy.
 */
export const DECLARATION_TECHNICAL_RULES = [
  'obligation_set_drift',
  'declaration_duplicate',
  'declaration_unknown_obligation',
  'declaration_missing_obligation',
  'declaration_count_mismatch',
] as const satisfies readonly string[]

export const CTR_VIOLATION_RULES = [
  'undeclared_metric_in_claim_text',
  'multiple_assertions_in_source_unit',
  'undeclared_sensitive_unit',
] as const satisfies readonly string[]

/**
 * Mệnh đề TỰ TỪ CHỐI kết luận — bề mặt DUY NHẤT được hạ khỏi vi phạm nội dung.
 *
 * ## Vì sao là DANH SÁCH LOẠI TRỪ, không phải danh sách dấu hiệu khẳng định
 *
 * Bản đầu của F7 làm ngược: liệt kê dấu hiệu KHẲNG ĐỊNH (số, %, từ so sánh) và
 * coi mọi thứ còn lại là vô hại. Bộ test hiện có bác bỏ ngay trong lần chạy đầu:
 * "CTR hiện tại của kênh đang thấp" và "CTR thấp rõ rệt ở nhóm này" đều là
 * khẳng định thẳng thừng mà KHÔNG mang dấu hiệu nào trong danh sách. Một danh
 * sách dấu hiệu khẳng định sẽ luôn thiếu, và mỗi chỗ thiếu là một khẳng định bị
 * cấm được THA và cho THỬ LẠI — hỏng đúng chiều nguy hiểm.
 *
 * Đảo lại thì hướng sai an toàn cũng đảo theo: mặc định VẪN là vi phạm nội dung
 * (đúng hành vi cũ, không thêm rủi ro), và chỉ những cách nói tự-từ-chối NHẬN
 * RA ĐƯỢC mới được hạ xuống thất bại định dạng. Cách nói lạ thì vẫn bị chặn.
 *
 * KHÔNG dùng `\b`: biên từ của JavaScript tính theo `\w` (ASCII), nên `\btránh\b`
 * không khớp như mong đợi khi từ mang dấu. Đây là lần thứ năm cái bẫy đó xuất
 * hiện trong tầng này.
 */
const PROSE_SELF_DISCLAIMER =
  /(?:không|chưa|tránh|no |not )[^.;!?]{0,80}(?:kết luận|khẳng định|đề cập|nhắc tới|nhắc đến|bàn tới|nhận định|phát biểu|phân tích|đánh giá|claim|conclusion)/iu

export interface ProseScanResult {
  issues: ValidationIssue[]
  causalViolations: number
  ctrViolations: number
}

/**
 * QUÉT VĂN BẢN NGOÀI JSON — chạy ĐỘC LẬP với mọi cổng schema.
 *
 * ## Vì sao là hàm riêng, và vì sao "độc lập" chứ không phải "trước" (F2)
 *
 * Văn bản ngoài JSON cũng là lời của mô hình. Trước đây phép quét này nằm GIỮA
 * thân `validateCursorOutput`, tức SAU bốn `return` sớm (JSON hỏng, hai nhánh
 * `schemaVersion`, schema hỏng) và SAU cả nhánh hỏng-hình-dạng riêng của
 * `validateAnalysisOutput`. Hệ quả là fail-open: một câu nhân quả và một khẳng
 * định CTR nằm ngoài JSON biến mất KHÔNG DẤU VẾT bất cứ khi nào thân JSON hỏng,
 * và lớp thất bại là `MISSING_REQUIRED_FIELD` / `INVALID_JSON` — đều nằm trong
 * `RETRYABLE`. Tức là mô hình chỉ cần kèm một thân JSON hỏng là mọi khẳng định
 * bị cấm nó viết ở ngoài đều được tha, và vòng chạy còn tự thử lại.
 *
 * Chọn ĐỘC LẬP thay vì chỉ "chạy trước": thân JSON và văn bản ngoài JSON là hai
 * NGUỒN vi phạm khác nhau. Một nguồn hỏng không được phép làm câm nguồn kia theo
 * bất kỳ chiều nào — kể cả chiều ngược lại (văn xuôi sạch không được biến lỗi
 * schema thành lỗi nội dung không thử lại được).
 *
 * `SENSITIVE_MENTION` không mang cờ `g` nên `.test` ở đây không có trạng thái.
 */
export function scanProseOutsideJson(proseText: string | undefined): ProseScanResult {
  const issues: ValidationIssue[] = []
  let causalViolations = 0
  let ctrViolations = 0
  if (!proseText || !proseText.trim()) return { issues, causalViolations, ctrViolations }

  for (const { re, label } of CAUSAL_PATTERNS) {
    for (const m of allMatches(re, proseText)) {
      causalViolations++
      issues.push({
        rule: 'causal_claim',
        severity: 'BLOCKER',
        message: `Ngôn ngữ nhân quả trong văn bản ngoài JSON: "${label}"`,
        path: PROSE_OUTSIDE_JSON_PATH,
        excerpt: excerptAround(proseText, m),
      })
    }
  }
  /*
   * F7 — NHẮC TÊN một chỉ số nhạy cảm KHÁC với KHẲNG ĐỊNH về nó.
   *
   * Bản trước coi mọi lần `SENSITIVE_MENTION` khớp là vi phạm CTR, và vì
   * `ctrViolations > 0` ép lớp thất bại thành `UNSUPPORTED_CLAIM` (KHÔNG nằm
   * trong `RETRYABLE`), một câu bọc vô hại như "Tôi đã tránh mọi kết luận về CTR
   * và thumbnail" — tức mô hình đang TỰ TỪ CHỐI kết luận — trở thành thất bại
   * NỘI DUNG vĩnh viễn. Đó là chặn quá tay theo đúng nghĩa: hình phạt nặng nhất
   * dành cho hành vi mà lớp này muốn khuyến khích.
   *
   * Phép hạ lớp là FAIL-CLOSED (xem `PROSE_SELF_DISCLAIMER`):
   *   • mặc định -> vi phạm NỘI DUNG, không thử lại. Giữ NGUYÊN hành vi cũ, nên
   *     không cách nói lạ nào lọt qua vì danh sách thiếu.
   *   • CHỈ khi MỌI mệnh đề nhạy cảm đều là câu tự-từ-chối nhận ra được -> VẪN là
   *     BLOCKER và VẪN chặn `passed` (hợp đồng vẫn là "chỉ một object JSON"),
   *     nhưng là thất bại ĐỊNH DẠNG nên được thử lại. Không im lặng bỏ qua, chỉ
   *     phân loại đúng chỗ.
   */
  const sensitiveClauses = clausesOf(proseText).filter((c) => SENSITIVE_MENTION.test(c))
  if (sensitiveClauses.length) {
    /*
     * HẠ LỚP đòi HAI điều kiện, không phải một.
     *
     * Bản đầu chỉ hỏi "mệnh đề có câu tự-từ-chối không". Rà soát đối kháng phá
     * được ngay, và tôi đã KIỂM CHỨNG BẰNG CHẠY: `clausesOf` không tách trên
     * `và`/`vì`/`dù`/`but`, nên MỘT mệnh đề mang được cả khẳng định lẫn lời từ
     * chối, và lời từ chối thắng. Cả năm câu dưới đây tụt xuống lớp THỬ LẠI ĐƯỢC
     * dù chúng khẳng định thẳng thừng về CTR:
     *
     *   "CTR hiện tại của kênh đang thấp và tôi tránh kết luận thêm."
     *   "CTR của kênh đang thấp vì thiếu dữ liệu impressions"
     *   "CTR thấp rõ rệt dù độ phủ 0% ở gói này"
     *   "Không thể tránh kết luận rằng CTR đang thấp"
     *   "The CTR is low but I do not draw a conclusion."
     *
     * Nay muốn được hạ lớp thì mệnh đề phải (a) có câu tự-từ-chối NHẬN RA ĐƯỢC
     * *và* (b) KHÔNG chứa phán xét nào về chính chỉ số ấy. Mặc định vẫn là vi
     * phạm NỘI DUNG, nên cách nói lạ vẫn bị chặn.
     *
     * Phép thử "chỉ từ chối" (`onlyDisclaims`) là ĐÓNG: nó liệt kê cái VÔ HẠI
     * (hư từ) thay vì cái bị cấm, nên không từ vựng nào phá được.
     */
    /*
     * MỆNH ĐỀ CHỈ TỪ CHỐI — phép thử ĐÓNG, không phải danh sách từ vựng.
     *
     * Hai vòng rà soát liên tiếp phá được cách tiếp cận "liệt kê dấu hiệu khẳng
     * định": trước là tính từ (`CTR đang thấp`), sau là số đo (`CTR là 2%`), rồi
     * số viết bằng chữ (`CTR là hai phần trăm`). Không gian ấy VÔ HẠN, nên mọi
     * danh sách đều sẽ thiếu, và mỗi chỗ thiếu là một khẳng định bị cấm được THA
     * và cho THỬ LẠI.
     *
     * Đảo sang phép thử ĐÓNG: một mệnh đề chỉ được hạ lớp khi, sau khi bỏ đi
     * (a) cụm tự-từ-chối và (b) mọi tên chỉ số nhạy cảm, phần CÒN LẠI không mang
     * nội dung gì — chỉ hư từ và dấu câu. Bất cứ thứ gì khác còn sót lại đều là
     * nội dung bổ sung, và nội dung bổ sung cạnh một chỉ số nhạy cảm bị coi là
     * khẳng định. Không từ vựng nào phá được phép thử này, vì nó không liệt kê
     * cái bị cấm mà liệt kê cái VÔ HẠI.
     *
     * Phép thử KHÔNG phải là bất khả xâm phạm: nó mạnh bằng danh sách hư từ VÀ
     * bằng việc cụm bị xoá không được nuốt chính khẳng định (xem
     * `onlyDisclaimsClause`). Một ĐỘNG TỪ lọt vào danh sách ấy là đủ để mở lại lỗ (đã xảy ra với
     * `có`). Khác biệt so với cách cũ là hướng sai: thiếu một hư từ gây CHẶN
     * OAN (thử lại được), còn thiếu một từ khẳng định thì gây THA (mất hẳn).
     *
     * Sai an toàn theo chiều CHẶN: một lời từ chối viết dài dòng có thể bị chặn
     * oan, và đó là lớp THỬ LẠI ĐƯỢC chứ không mất mát gì.
     */
    const onlyDisclaims = onlyDisclaimsClause
    const assertsAboutMetric = (c: string) => !onlyDisclaims(c)
    const assertive = sensitiveClauses.filter(
      (c) => assertsAboutMetric(c) || !PROSE_SELF_DISCLAIMER.test(c),
    )
    if (assertive.length) {
      ctrViolations++
      issues.push({
        rule: 'undeclared_sensitive_unit',
        severity: 'BLOCKER',
        message: 'Văn bản ngoài JSON KHẲNG ĐỊNH về chỉ số nhạy cảm mà không thể khai báo được',
        path: PROSE_OUTSIDE_JSON_PATH,
        excerpt: assertive[0]!.slice(0, 180),
      })
    } else {
      issues.push({
        rule: 'prose_sensitive_mention',
        severity: 'BLOCKER',
        message:
          'Văn bản ngoài JSON nhắc chỉ số nhạy cảm. Không phát hiện khẳng định, ' +
          'nhưng hợp đồng vẫn yêu cầu CHỈ một object JSON.',
        path: PROSE_OUTSIDE_JSON_PATH,
        excerpt: sensitiveClauses[0]!.slice(0, 180),
      })
    }
  }
  return { issues, causalViolations, ctrViolations }
}

/**
 * KHÔNG CÓ object JSON nào trong output — nhưng VẪN phải quét văn xuôi.
 *
 * Đây là lỗ hổng fail-open thứ hai, cùng họ với F2 và nghiêm trọng hơn: vòng
 * chạy có một nhánh `else if (!json)` trả thẳng `INVALID_JSON` mà KHÔNG gọi bộ
 * kiểm định, nên `proseText` — lúc này là TOÀN BỘ stdout — bị vứt đi. Một câu
 * nhân quả hoặc một khẳng định CTR viết ra ngoài mọi dấu ngoặc không được quét,
 * không được đếm, không được lưu; và `INVALID_JSON` nằm trong `RETRYABLE` nên
 * mô hình chỉ việc trả lời lại cho đúng định dạng.
 *
 * Bản sửa F2 đặt phép quét ở đầu `validateCursorOutput` — tức THẤP HƠN một tầng
 * so với nhánh vừa nói. Hàm này là phần còn thiếu ấy.
 */
/**
 * Mọi chuỗi văn bản nằm TRONG một giá trị JSON đã parse.
 *
 * Dùng cho các đường THẤT BẠI KỸ THUẬT, nơi payload không qua nổi cổng schema
 * nên không có `enumerateUnits` để đi. Không có nó thì một câu nhân quả nằm
 * trong JSON biến mất mỗi khi lần chạy hỏng vì lý do kỹ thuật.
 */
function stringValuesOf(v: unknown): Array<{ text: string; path: string }> {
  /*
   * DUYỆT LẶP, KHÔNG ĐỆ QUY, và KHÔNG có trần độ sâu.
   *
   * Bản trước dừng ở `depth > 12` và IM LẶNG bỏ phần sâu hơn — một câu nhân quả
   * chôn dưới 13 lớp object biến mất và lần chạy giữ nguyên lớp RETRYABLE. Một
   * cái trần fail-open đặt trong lớp an toàn thì chính nó là lỗ hổng.
   *
   * `JSON.parse` không sinh chu trình nên duyệt hết là an toàn; ngăn xếp tường
   * minh để cấu trúc rất sâu không làm tràn ngăn xếp lời gọi.
   */
  const out: Array<{ text: string; path: string }> = []
  const stack: Array<{ node: unknown; path: string }> = [{ node: v, path: '' }]
  while (stack.length) {
    const { node, path } = stack.pop()!
    if (typeof node === 'string') out.push({ text: node, path })
    else if (Array.isArray(node)) {
      for (let i = node.length - 1; i >= 0; i--) stack.push({ node: node[i], path })
    } else if (node && typeof node === 'object') {
      for (const [k, val] of Object.entries(node as Record<string, unknown>)) {
        stack.push({ node: val, path: path ? `${path}.${k}` : k })
      }
    }
  }
  return out
}

/**
 * Ô mà việc nêu cơ chế nhân quả ĐƯỢC PHÉP khi có rào đón.
 *
 * Phải khớp ngữ nghĩa của đường chạy đầy đủ, nơi ngoại lệ rào đón chỉ áp cho
 * `HYPOTHESIS` và `EXPERIMENT`. Áp nó cho MỌI chuỗi — như bản trước — nghĩa là
 * một câu nhân quả CÓ rào đón nằm trong `keyFindings` được tha, dù ở đó nó vẫn
 * là vi phạm.
 */
const HEDGEABLE_PATH = /(^|\.)(hypotheses|experiments)(\.|$)/iu

/**
 * NGÔN NGỮ NHÂN QUẢ trong văn bản mô hình đã phát ra, KỂ CẢ khi payload hỏng.
 *
 * ## Vì sao CHỈ nhân quả, không quét chỉ số nhạy cảm
 *
 * Nhắc một chỉ số nhạy cảm BÊN TRONG JSON không phải là vi phạm — nó được điều
 * chỉnh bằng cơ chế KHAI BÁO ở chặng sau. Ngược lại, ngôn ngữ nhân quả bị cấm ở
 * MỌI chặng và MỌI ô, nên nó quét được an toàn mà không cần biết ô nào.
 *
 * ## Đây là quyết định thiết kế, không phải thiếu sót — đã được chất vấn và giữ
 *
 * Một vòng rà soát đề nghị quét cả khẳng định về chỉ số nhạy cảm ở đây, coi
 * "Thumbnail hiện tại kém." trong payload hỏng schema là thất bại vĩnh viễn.
 * ĐỀ NGHỊ ẤY BỊ TỪ CHỐI, vì nó mâu thuẫn với chính kiến trúc hai lượt:
 *
 *   * Ở chặng ANALYSIS, U3 (`undeclared_sensitive_unit`) cho các ô TRONG JSON bị
 *     LỌC BỎ CÓ CHỦ ĐÍCH — "lượt 1 chưa có bản khai để mà khai". Một ô nhạy cảm
 *     chưa khai ở lượt 1 KHÔNG phải vi phạm; nó là đầu vào của bộ sinh nghĩa vụ.
 *   * Thử lại một payload hỏng schema KHÔNG phải "chạy lại tới khi mô hình thôi
 *     nói điều đó": mô hình sửa schema rồi giữ nguyên câu, và câu ấy đi tiếp qua
 *     cơ chế khai báo đúng như thiết kế.
 *   * Quét ở đây sẽ biến MỌI bài phân tích có nhắc CTR kèm một lỗi schema thành
 *     thất bại vĩnh viễn — đúng kiểu chặn quá tay mà F7 đã phải sửa, ở quy mô lớn hơn.
 *
 * Ranh giới thật nằm ở CHỖ ĐẶT: ngoài JSON thì không chặng nào khai báo được,
 * nên ở đó khẳng định nhạy cảm LÀ vi phạm nội dung (`scanProseOutsideJson`).
 * Trong JSON thì có đường khai báo, nên nó được điều chỉnh chứ không bị cấm.
 *
 * Rào đón được tha ĐÚNG ở ô giả thuyết/thí nghiệm (`HEDGEABLE_PATH`), giống hệt
 * đường chạy đầy đủ. Ở mọi ô khác — `keyFindings`, `recommendations`, … — rào
 * đón KHÔNG tha, vì câu nhân quả ở đó vẫn là vi phạm.
 */
/**
 * Quét NGÔN NGỮ NHÂN QUẢ trên VĂN BẢN THÔ của một payload KHÔNG parse được.
 *
 * `extractJson` bóc một object CÂN BẰNG NGOẶC ra khỏi `proseText`, nhưng cân
 * bằng ngoặc KHÔNG có nghĩa là JSON hợp lệ: một dấu phẩy thừa, một escape sai,
 * một token hỏng đều làm `JSON.parse` ném. Khi ấy `scanCausalInEmittedJson`
 * không có gì để duyệt, `proseText` đã bị lấy mất object, và câu nhân quả nằm
 * trong object thoát KHỎI MỌI phép quét — trả về `INVALID_JSON`, RETRYABLE.
 *
 * KHÔNG có ngoại lệ rào đón ở đây, vì không parse được thì không biết ô nào. Đó
 * là cùng quy ước với `scanProseOutsideJson`, và sai an toàn theo chiều CHẶN:
 * một giả thuyết rào đón nằm trong JSON HỎNG bị chặn oan, và mô hình chỉ cần
 * trả JSON hợp lệ là nó được xét theo ô như bình thường.
 */
export function scanCausalInRawText(raw: string): ProseScanResult {
  const issues: ValidationIssue[] = []
  let causalViolations = 0
  for (const { re, label } of CAUSAL_PATTERNS) {
    for (const m of allMatches(re, raw)) {
      causalViolations++
      issues.push({
        rule: 'causal_claim',
        severity: 'BLOCKER',
        message: `Ngôn ngữ nhân quả trong payload KHÔNG parse được: "${label}"`,
        path: EMITTED_JSON_PATH,
        excerpt: excerptAround(raw, m),
      })
    }
  }
  return { issues, causalViolations, ctrViolations: 0 }
}

const FILLER = new RegExp(
  `^(?:${[
    'tôi', 'toi', 'mình', 'chúng ta', 'chúng tôi', 'phần', 'này', 'đó', 'ở', 'đây',
    'đã', 'đang', 'sẽ', 'còn', 'nào', 'gì', 'về', 'của', 'và', 'hay', 'hoặc', 'với',
    'mọi', 'các', 'cả', 'thêm', 'nữa', 'trong', 'ra', 'bất', 'kỳ',
    'i', 'we', 'the', 'a', 'an', 'any', 'no', 'not', 'on', 'about', 'and', 'or', 'of',
    'this', 'that', 'here',
    /*
     * CỐ Ý KHÔNG có ở đây: `có`, `là`, `đưa`, `do`, `does`, `draw`, `make`.
     *
     * Chúng là ĐỘNG TỪ mang khẳng định, không phải hư từ. Để `có` trong danh
     * sách khiến "Có CTR và tôi không kết luận." rút gọn về toàn hư từ — tức
     * một khẳng định RẰNG DỮ LIỆU CTR TỒN TẠI được hạ xuống lớp THỬ LẠI ĐƯỢC.
     *
     * Bỏ chúng ra KHÔNG làm hỏng các câu từ chối thật: ở "Không có phát biểu
     * nào về CTR", chính cụm tự-từ-chối đã nuốt trọn chữ `có`, nên nó không
     * còn nằm ở phần dư.
     */
  ].join('|')})$`,
  'iu',
)
function onlyDisclaimsClause(c: string): boolean {
  const m = PROSE_SELF_DISCLAIMER.exec(c)
  if (!m) return false
  /*
   * Cụm tự-từ-chối KHÔNG được NUỐT chính khẳng định.
   *
   * `PROSE_SELF_DISCLAIMER` cho phép tối đa 80 ký tự giữa từ phủ định và danh từ
   * ("kết luận", "nhận định", …). Nếu khẳng định nằm LỌT trong khoảng ấy thì nó
   * bị xoá cùng cụm, phần dư rỗng, và mệnh đề được coi là "chỉ từ chối":
   *
   *   "Không những CTR thấp mà tôi tránh kết luận"
   *   "Không phải CTR thấp nên tôi tránh kết luận"
   *   "Chưa kể CTR thấp và đó là kết luận"
   *
   * Cả ba đều KHẲNG ĐỊNH `CTR thấp`. Đã kiểm bằng chạy: trước bản sửa cả sáu
   * biến thể không-dấu-phẩy đều cho `ctrViolations = 0`.
   *
   * Quy tắc: nếu chính cụm bị xoá có nhắc chỉ số nhạy cảm thì đó không phải một
   * lời từ chối thuần — nó là một phát biểu VỀ chỉ số, và không được hạ lớp.
   * Lời từ chối thật ("tránh mọi kết luận về CTR") để tên chỉ số NGOÀI cụm.
   */
  if (SENSITIVE_MENTION.test(m[0])) return false
  const rest = c
    .replace(m[0], ' ')
    .replace(new RegExp(SENSITIVE_SUBJECT_SOURCE, 'giu'), ' ')
    .replace(/[.,;:!?()"'\-–—/%]/gu, ' ')
  return rest
    .split(/\s+/u)
    .filter(Boolean)
  .every((w) => FILLER.test(w))
}


/**
 * KHẲNG ĐỊNH về chỉ số nhạy cảm trong payload KHAI BÁO.
 *
 * ## Vì sao lượt 2 khác lượt 1 ở đúng điểm này
 *
 * Ở lượt PHÂN TÍCH, một câu nhắc chỉ số nhạy cảm nằm trong payload là ĐẦU VÀO
 * của bộ sinh nghĩa vụ: nó sẽ được khai báo ở lượt sau. Vì thế quét nó ở đó là
 * chặn oan (xem ghi chú trong `scanCausalInEmittedJson`).
 *
 * Ở lượt KHAI BÁO thì KHÔNG có bước ấy nữa. Bộ sinh nghĩa vụ đã chạy xong, và
 * một câu văn xuôi nhét vào trường thừa của bản khai KHÔNG bao giờ được rà soát
 * ngữ nghĩa bởi bất cứ chặng nào. `.strict()` chỉ cho ra `SCHEMA_MISMATCH`, vốn
 * RETRYABLE — nên vòng chạy cứ thử lại tới khi mô hình thôi viết câu đó.
 *
 * Dùng CHUNG phép thử "chỉ từ chối" với văn bản ngoài JSON, nên hai nơi không
 * thể lệch nhau.
 */
/**
 * Khẳng định nhạy cảm nằm ở TRƯỜNG THỪA của payload PHÂN TÍCH — ở BẤT KỲ ĐỘ SÂU NÀO.
 *
 * ## Vì sao hỏi CHÍNH SCHEMA thay vì giữ một danh sách khoá
 *
 * Bản trước liệt kê mười khoá cấp cao nhất và miễn trừ cả cây con của chúng.
 * `{"analysisSummary":{"overallAssessment":"...","extra":"CTR thấp."}}` do đó lọt:
 * `analysisSummary` là khoá hợp lệ, nhưng `extra` bên trong nó bị `.strict()` LỒNG
 * từ chối vĩnh viễn — nên nó cũng không bao giờ thành nghĩa vụ.
 *
 * Một danh sách khoá viết tay là BẢN SAO THỨ HAI của schema, và nó đã lệch ngay
 * ở lần đầu. Nay hỏi thẳng `cursorAnalysisSchema`: mọi khoá `unrecognized_keys`
 * mà zod báo, ở mọi độ sâu, chính là tập trường thừa — theo đúng định nghĩa,
 * không theo phỏng đoán.
 *
 * Ranh giới R11 giữ nguyên: ô phân tích HỢP LỆ không nằm trong tập này, nên câu
 * nhạy cảm ở đó vẫn là đầu vào của bộ sinh nghĩa vụ và vẫn thử lại được.
 */
export function scanSensitiveInAnalysisExtras(parsed: unknown): ProseScanResult {
  const empty: ProseScanResult = { issues: [], causalViolations: 0, ctrViolations: 0 }
  if (!parsed || typeof parsed !== 'object') return empty

  const shape = cursorAnalysisSchema.safeParse(parsed)
  if (shape.success) return empty

  /** Đi tới container mà zod trỏ tới bằng `issue.path`. */
  const at = (root: unknown, path: ReadonlyArray<string | number>): unknown => {
    let cur: unknown = root
    for (const k of path) {
      if (cur === null || typeof cur !== 'object') return undefined
      cur = (cur as Record<string | number, unknown>)[k]
    }
    return cur
  }

  const extras: Record<string, unknown> = {}
  let n = 0
  for (const issue of shape.error.issues) {
    if (issue.code !== 'unrecognized_keys') continue
    const container = at(parsed, issue.path)
    if (!container || typeof container !== 'object') continue
    for (const k of (issue as unknown as { keys: string[] }).keys) {
      extras[`extra_${n++}`] = (container as Record<string, unknown>)[k]
    }
  }
  if (!n) return empty
  return scanSensitiveInDeclarationJson(extras)
}

/**
 * Khôi phục các CHUỖI của một khối JSON hỏng CÚ PHÁP, theo TỪ VỰNG.
 *
 * `stringValuesOf({ raw })` trả về ĐÚNG MỘT giá trị: cả payload gộp làm một
 * chuỗi. Mọi phép lọc theo từng giá trị — `isKnownFieldValue` của
 * `scanSensitiveInDeclarationJson` — vì thế mất tác dụng hoàn toàn, và
 * `clausesOf` đem chính cú pháp JSON ra cắt thành "mệnh đề". Hệ quả đo được:
 * một bản khai ĐÚNG chỉ thừa một dấu phẩy bị xếp `UNSUPPORTED_CLAIM` vĩnh viễn
 * vì nó có `"relatedMetric":"impression_ctr"` — tức là vứt bỏ một bài phân tích
 * đã kiểm định xong, tốn 100–235 giây, vì một dấu phẩy.
 *
 * JSON hỏng cú pháp thì hầu như vẫn còn nguyên các chuỗi. Tách chúng theo từ
 * vựng rồi quét TỪNG chuỗi một, ta lấy lại đúng độ mịn của đường đã parse được
 * mà không cần tới bộ phân tích cú pháp nào.
 *
 * Trả về mảng chuỗi để dùng thẳng làm đầu vào cho các hàm quét sẵn có.
 */
/**
 * Bỏ dấu phẩy THỪA ngay trước `}` hoặc `]`, có phân biệt trong/ngoài chuỗi.
 *
 * Không dùng regex trần: `,(\s*[}\]])` khớp cả bên TRONG một chuỗi, nên nó sẽ
 * lặng lẽ sửa nội dung câu văn mà ta sắp đem đi quét. Phép sửa dùng để CHẨN ĐOÁN
 * thì tuyệt đối không được đổi lời của mô hình.
 */
function stripTrailingCommas(raw: string): string {
  let out = ''
  let inString = false
  let escaped = false
  for (let i = 0; i < raw.length; i++) {
    const ch = raw[i]!
    if (inString) {
      out += ch
      if (escaped) escaped = false
      else if (ch === '\\') escaped = true
      else if (ch === '"') inString = false
      continue
    }
    if (ch === '"') {
      inString = true
      out += ch
      continue
    }
    if (ch === ',') {
      let j = i + 1
      while (j < raw.length && /\s/u.test(raw[j]!)) j++
      if (j < raw.length && (raw[j] === '}' || raw[j] === ']')) continue
    }
    out += ch
  }
  return out
}

/**
 * Thử SỬA lỗi cú pháp TẦM THƯỜNG rồi parse lại — để lấy lại CẤU TRÚC TRƯỜNG.
 *
 * Đây là chỗ hoà giải hai đòi hỏi đối nghịch, cả hai đều đúng:
 *
 *  - R18: khẳng định nhạy cảm ở trường THỪA không được tha chỉ vì payload hỏng,
 *    nếu không thì lời bị cấm biến khỏi hồ sơ mỗi lần payload hỏng.
 *  - C-1: ô phân tích HỢP LỆ được phép nhắc chỉ số nhạy cảm (ranh giới R11), nên
 *    quét cả khối thô biến mọi bài phân tích thật kèm một lỗi cú pháp thành thất
 *    bại vĩnh viễn.
 *
 * Mâu thuẫn chỉ tồn tại khi ta MẤT cấu trúc trường. Lỗi cú pháp áp đảo của LLM
 * là dấu phẩy thừa; sửa đúng nó rồi parse lại thì `unrecognized_keys` hoạt động
 * trở lại và cả hai đòi hỏi cùng được thoả — trường THỪA vẫn bị bắt, ô THẬT vẫn
 * được tha.
 *
 * Chỉ MỘT phép sửa, và là phép sửa duy nhất không thể đổi nghĩa payload. Khi nó
 * không giúp parse được, ta thừa nhận là không còn cấu trúc và lùi về quét nhân
 * quả — chứ không đoán.
 */
function reparseAfterTrivialRepair(raw: string): { ok: true; value: unknown } | { ok: false } {
  const repaired = stripTrailingCommas(raw)
  if (repaired === raw) return { ok: false }
  try {
    return { ok: true, value: JSON.parse(repaired) }
  } catch {
    return { ok: false }
  }
}

export function recoverJsonStringLiterals(raw: string): string[] {
  const out: string[] = []
  // Chuỗi JSON: mở ngoặc kép, thân không chứa `"` chưa thoát, đóng ngoặc kép.
  const re = /"((?:[^"\\]|\\.)*)"/gu
  let m: RegExpExecArray | null
  while ((m = re.exec(raw)) !== null) {
    let text = m[1]!
    try {
      // Giải mã escape để `ả` trở lại thành chữ thật trước khi quét.
      text = JSON.parse(`"${m[1]}"`) as string
    } catch {
      // Escape hỏng: giữ nguyên phần thô, quét vẫn hơn bỏ qua.
    }
    out.push(text)
  }
  return out
}

export function scanSensitiveInDeclarationJson(parsed: unknown): ProseScanResult {
  const issues: ValidationIssue[] = []
  let ctrViolations = 0
  for (const { text, path } of stringValuesOf(parsed)) {
    /*
     * BỎ QUA giá trị TRƯỜNG đã biết, quét MỌI thứ còn lại.
     *
     * Bản khai hợp lệ mang đầy giá trị enum/id/băm — `impression_ctr`, `views`,
     * `MC-001`, một chuỗi 64 hex. Quét cả chúng thì mọi bản khai ĐÚNG bị chặn
     * oan, vì `relatedMetric: "impression_ctr"` khớp `SENSITIVE_MENTION` theo
     * đúng nghĩa đen (đã kiểm bằng chạy: bản đầu làm đỏ bốn test bản khai đúng).
     *
     * Bản trước dùng "có khoảng trắng" làm ranh giới. SAI: `"CTR-thấp."` là một
     * khẳng định nhạy cảm chỉ gồm MỘT token, và nó lọt. Danh sách loại trừ phải
     * là những HÌNH DẠNG BIẾT TRƯỚC, không phải một suy đoán về số từ — nhờ vậy
     * mọi chuỗi lạ đều bị QUÉT (fail-closed) thay vì được tha.
     */
    const t = text.trim()
    const isKnownFieldValue =
      /^[0-9a-f]{64}$/iu.test(t) || // băm
      /^[A-Z]{1,6}-\d{1,4}$/u.test(t) || // id nghĩa vụ, ví dụ MC-001
      /^\d+(\.\d+)*$/u.test(t) || // số phiên bản
      Object.prototype.hasOwnProperty.call(METRIC_ALIASES, t) // tên chỉ số ĐÚNG NGUYÊN VĂN
    if (isKnownFieldValue) continue
    const sensitive = clausesOf(text).filter((c) => SENSITIVE_MENTION.test(c))
    const assertive = sensitive.filter((c) => !onlyDisclaimsClause(c))
    if (!assertive.length) continue
    ctrViolations++
    issues.push({
      rule: 'undeclared_sensitive_unit',
      severity: 'BLOCKER',
      message:
        'Bản KHAI BÁO chứa khẳng định về chỉ số nhạy cảm ngoài cấu trúc khai báo — ' +
        'không chặng nào rà soát ngữ nghĩa cho nó.',
      path: path ? `${EMITTED_JSON_PATH} ${path}` : EMITTED_JSON_PATH,
      excerpt: assertive[0]!.slice(0, 180),
    })
  }
  return { issues, causalViolations: 0, ctrViolations }
}

export function scanCausalInEmittedJson(parsed: unknown): ProseScanResult {
  const issues: ValidationIssue[] = []
  let causalViolations = 0
  for (const { text, path } of stringValuesOf(parsed)) {
    const hedgeable = HEDGEABLE_PATH.test(path)
    for (const { re, label } of CAUSAL_PATTERNS) {
      for (const m of allMatches(re, text)) {
        // Rào đón CHỈ tha ở ô giả thuyết/thí nghiệm — như đường chạy đầy đủ.
        if (hedgeable && HEDGE_PATTERN.test(sentenceAround(text, m.index))) continue
        causalViolations++
        issues.push({
          rule: 'causal_claim',
          severity: 'BLOCKER',
          message: `Ngôn ngữ nhân quả trong payload (payload không qua được cổng schema): "${label}"`,
          path: path ? `${EMITTED_JSON_PATH} ${path}` : EMITTED_JSON_PATH,
          excerpt: excerptAround(text, m),
        })
      }
    }
  }
  return { issues, causalViolations, ctrViolations: 0 }
}

/** `path` của vi phạm tìm thấy trong payload chưa qua được cổng schema. */
export const EMITTED_JSON_PATH = '(payload chưa qua cổng schema)'

export function validateProseOnly(input: {
  proseText?: string
  hadProseOutsideJson: boolean
  /** Phần JSON đã bóc được (nếu có) — cũng là lời của mô hình và cũng phải quét. */
  emittedJson?: string | null
  /**
   * Đây có phải lượt KHAI BÁO không.
   *
   * Lượt khai báo phải quét CẢ khẳng định về chỉ số nhạy cảm, không chỉ nhân
   * quả: sau nó không còn chặng nào sinh nghĩa vụ nữa (xem
   * `scanSensitiveInDeclarationJson`). Khi CLI hỏng, `validateDeclarationOutput`
   * KHÔNG chạy, nên phép quét ấy phải được gọi từ đây.
   */
  declarationPass?: boolean
  /**
   * Đây có phải lượt PHÂN TÍCH không.
   *
   * Lượt phân tích quét khẳng định nhạy cảm ở TRƯỜNG THỪA (không bao giờ thành
   * nghĩa vụ) nhưng KHÔNG quét ở ô phân tích hợp lệ — xem
   * `scanSensitiveInAnalysisExtras` và ranh giới R11.
   */
  analysisPass?: boolean
}): { report: ValidationReport; failureClass: ValidateResult['failureClass']; repairErrors: string[] } {
  const proseOnly = scanProseOutsideJson(input.proseText)
  let emitted: ProseScanResult = { issues: [], causalViolations: 0, ctrViolations: 0 }
  const scanParsedEmitted = (parsed: unknown): ProseScanResult => {
    const causal = scanCausalInEmittedJson(parsed)
    const sensitive = input.declarationPass
      ? scanSensitiveInDeclarationJson(parsed)
      : input.analysisPass
        ? scanSensitiveInAnalysisExtras(parsed)
        : { issues: [], causalViolations: 0, ctrViolations: 0 }
    return {
      issues: [...causal.issues, ...sensitive.issues],
      causalViolations: causal.causalViolations,
      ctrViolations: sensitive.ctrViolations,
    }
  }
  if (input.emittedJson) {
    try {
      emitted = scanParsedEmitted(JSON.parse(input.emittedJson))
    } catch {
      // Cân bằng ngoặc nhưng KHÔNG hợp lệ: `extractJson` đã lấy object ra khỏi
      // `proseText`, nên nếu không quét thô ở đây thì câu trong đó thoát hết.
      /*
       * Sửa dấu phẩy thừa rồi parse lại TRƯỚC — lấy lại được cấu trúc trường thì
       * quét y hệt nhánh trên, không phải đoán gì cả.
       */
      const repaired = reparseAfterTrivialRepair(input.emittedJson)
      if (repaired.ok) {
        emitted = scanParsedEmitted(repaired.value)
      } else {
        const causal = scanCausalInRawText(input.emittedJson)
        /*
         * Vẫn không parse được -> khôi phục CHUỖI theo từ vựng rồi quét từng cái.
         *
         * `analysisPass` KHÔNG quét khẳng định nhạy cảm ở đây, đúng như nhánh
         * `catch` của `validateCursorOutput`: ở lượt 1 một ô hợp lệ ĐƯỢC PHÉP
         * nhắc chỉ số nhạy cảm, và khi mất hẳn cấu trúc thì không còn
         * `unrecognized_keys` để tách trường THỪA ra khỏi ô thật.
         */
        const sensitive =
          input.declarationPass
            ? scanSensitiveInDeclarationJson(recoverJsonStringLiterals(input.emittedJson))
            : { issues: [], causalViolations: 0, ctrViolations: 0 }
        emitted = {
          issues: [...causal.issues, ...sensitive.issues],
          causalViolations: causal.causalViolations,
          ctrViolations: sensitive.ctrViolations,
        }
      }
    }
  }
  const prose: ProseScanResult = {
    issues: [...proseOnly.issues, ...emitted.issues],
    causalViolations: proseOnly.causalViolations + emitted.causalViolations,
    ctrViolations: proseOnly.ctrViolations + emitted.ctrViolations,
  }
  /*
   * BẢN GHI phải nói ĐÚNG chuyện đã xảy ra.
   *
   * Hàm này được gọi từ CẢ HAI nhánh `if (execFailure)` của `run.ts`, nơi
   * `emittedJson` RẤT THƯỜNG khác rỗng: mô hình trả payload tử tế và chỉ có CLI
   * thoát khác 0. Câu "không tìm thấy object JSON nào" khi ấy là một khẳng định
   * SAI, và nó được ghi thẳng vào `analysis_validation` rồi đưa lại cho mô hình
   * trong prompt sửa lỗi — bảo nó sửa đúng thứ không hề hỏng.
   */
  const hadJson = Boolean(input.emittedJson)
  const jsonProblem = hadJson
    ? 'Có object JSON nhưng KHÔNG parse được, hoặc lần chạy hỏng trước khi kiểm định xong.'
    : 'Không tìm thấy object JSON nào trong output.'
  const repairErrors = [`${jsonProblem} Trả về DUY NHẤT một object JSON hợp lệ.`]
  if (prose.issues.length > 0) {
    repairErrors.push(
      `${prose.issues.length} vi phạm trong VĂN BẢN NGOÀI JSON — bỏ hẳn phần văn bản đó:\n` +
        prose.issues
          .slice(0, 3)
          .map((i) => `  • ${i.message}${i.excerpt ? `: "${i.excerpt}"` : ''}`)
          .join('\n'),
    )
  }
  return {
    report: {
      passed: false,
      structuralIssues: [
        {
          rule: 'json_parse',
          severity: 'BLOCKER',
          message: jsonProblem,
        },
      ],
      evidenceIssues: [],
      claimIssues: prose.issues,
      qualityIssues: [],
      evidenceResolutionRate: null,
      totalEvidenceRefs: 0,
      unresolvedEvidenceRefs: 0,
      causalViolations: prose.causalViolations,
      ctrViolations: prose.ctrViolations,
      unsupportedMetricViolations: 0,
      counts: { findings: 0, hypotheses: 0, recommendations: 0, experiments: 0 },
    },
    // Khẳng định bị cấm là thất bại NỘI DUNG và thắng lỗi định dạng.
    failureClass:
      prose.causalViolations > 0 || prose.ctrViolations > 0 ? 'UNSUPPORTED_CLAIM' : 'INVALID_JSON',
    repairErrors,
  }
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
  /**
   * CHẶNG đang kiểm. Quyết định quy tắc nào ÁP DỤNG ĐƯỢC.
   *
   * `ANALYSIS` bỏ U3 và hệ quả của nó vì lượt 1 chưa có bản khai để mà khai
   * thiếu. Mặc định `COMPOSITE` — chặng có đủ mọi thứ, nên không bỏ gì.
   */
  stage?: 'ANALYSIS' | 'COMPOSITE'
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
  let claimIssues: ValidationIssue[] = []
  let qualityIssues: ValidationIssue[] = []
  /**
   * Dòng sửa lỗi, KÈM quy tắc sinh ra nó.
   *
   * Thăm dò 2026-08-06 lộ ra vì sao cần cái đuôi `rule`: chặng PHÂN TÍCH lọc bỏ
   * U3 và `selfcheck_contradicted` về CTR, nhưng `repairErrors` được gom từ tập
   * CHƯA lọc, nên prompt sửa lỗi bảo mô hình "bỏ mọi kết luận về CTR" trong khi
   * báo cáo chính thức ghi `ctr_violations = 0`. Một prompt sửa lỗi nói về một
   * lỗi không tồn tại sẽ đẩy lần thử sau đi sai hướng.
   *
   * `rule: null` = lời khuyên về ĐỊNH DẠNG, luôn áp dụng ở mọi chặng.
   */
  const repairSources: Array<{ text: string; rules: string[] | null }> = []
  /**
   * `rules = null` -> lời khuyên ĐỊNH DẠNG, luôn giữ.
   * `rules = [...]` -> giữ nếu BẤT KỲ quy tắc nào trong danh sách còn sống.
   *
   * Danh sách chứ không phải một chuỗi: nhiều quy tắc khác nhau cùng làm một bộ
   * đếm tăng, nên một nhãn đơn lẻ sẽ lọc nhầm dòng hướng dẫn của các quy tắc còn lại.
   */
  const pushRepair = (text: string, rule: string | string[] | null = null) => {
    repairSources.push({ text, rules: rule === null ? null : (Array.isArray(rule) ? rule : [rule]) })
  }
  const repairErrors: string[] = []
  /**
   * Đổ `repairSources` -> `repairErrors`. Phải gọi TRƯỚC MỌI `return`.
   *
   * F1 (hồi quy do G-R2): trước đây vòng đổ chỉ nằm ở CUỐI hàm, sau bốn `return`
   * sớm (JSON hỏng, hai nhánh schemaVersion, schema hỏng). Cả bốn lớp thất bại ấy
   * đều nằm trong `RETRYABLE`, nên lần thử 2–3 chạy với prompt sửa lỗi RỖNG —
   * đốt ngân sách thử lại vào phỏng đoán mù, và không có gì kêu lên.
   *
   * `drained` chống gọi hai lần: đường chạy đầy đủ vẫn gọi ở cuối, và một bản sửa
   * ngây thơ sẽ nhân đôi mọi dòng hướng dẫn.
   */
  let drained = false
  const drainRepairs = (issues: ValidationIssue[]): string[] => {
    if (drained) return repairErrors
    drained = true
    const surviving = new Set(issues.map((i) => i.rule))
    for (const src of repairSources) {
      if (src.rules === null || src.rules.some((r) => surviving.has(r))) {
        repairErrors.push(src.text)
      }
    }
    return repairErrors
  }
  /** Tập vi phạm tại một `return` sớm. */
  const issuesSoFar = () => [...structuralIssues, ...evidenceIssues, ...claimIssues, ...qualityIssues]

  /*
   * F2 — quét văn bản ngoài JSON NGAY, trước mọi cổng schema.
   *
   * Đặt ở đây chứ không ở giữa thân hàm vì bốn `return` sớm bên dưới đều bỏ qua
   * phần giữa. Kết quả được nạp thẳng vào `claimIssues` và vào bộ đếm, nên mọi
   * `return` — sớm hay đủ — đều mang theo vi phạm này.
   */
  const proseOutside = scanProseOutsideJson(input.proseText)
  /*
   * Payload CHƯA qua cổng schema cũng phải được quét ngôn ngữ nhân quả.
   *
   * Các `return` sớm bên dưới (bản schema không hỗ trợ, thiếu trường bắt buộc)
   * đều trả lớp RETRYABLE. Nếu chỉ quét văn bản NGOÀI JSON thì một câu nhân quả
   * nằm TRONG payload biến mất mỗi khi payload hỏng schema — mô hình chỉ cần
   * kèm một lỗi schema là lời bị cấm được tha và vòng chạy tự thử lại.
   *
   * Chỉ nhân quả, không quét chỉ số nhạy cảm — xem `scanCausalInEmittedJson`.
   */
  let emittedScan: ProseScanResult = { issues: [], causalViolations: 0, ctrViolations: 0 }
  // Trường THỪA không bao giờ thành nghĩa vụ -> quét cả khẳng định nhạy cảm.
  const scanEmittedAnalysis = (parsedRaw: unknown): ProseScanResult => {
    const causal = scanCausalInEmittedJson(parsedRaw)
    const extras = scanSensitiveInAnalysisExtras(parsedRaw)
    return {
      issues: [...causal.issues, ...extras.issues],
      causalViolations: causal.causalViolations,
      ctrViolations: extras.ctrViolations,
    }
  }
  try {
    emittedScan = scanEmittedAnalysis(JSON.parse(input.raw))
  } catch {
    /*
     * KHÔNG parse được: quét NHÂN QUẢ trên văn bản thô, nhưng KHÔNG quét khẳng
     * định nhạy cảm.
     *
     * Bản trước quét cả hai với lý do "chiều sai là CHẶN". Đo bằng chạy thì
     * chiều ấy chặn quá tay tới mức xoá sổ một lớp thất bại:
     *
     *   {"schemaVersion":"3.0","analysisSummary":{"primaryConstraint":
     *    "Độ phủ impressions bằng 0% ở gói này"},}      <- THỪA một dấu phẩy
     *     -> UNSUPPORTED_CLAIM (vĩnh viễn, chết ở lần thử 1)
     *
     *   cùng payload, đổi "impressions" thành "dữ liệu"
     *     -> INVALID_JSON (được thử lại)
     *
     * Câu bị phạt là một câu NÊU GIỚI HẠN hoàn toàn hợp lệ. Nguyên nhân: khi
     * JSON hỏng CÚ PHÁP thì cả payload là MỘT chuỗi, nên `isKnownFieldValue`
     * của bản quét khai báo không còn cách nào tách ô thật khỏi trường thừa, và
     * `clausesOf` cắt chính cú pháp JSON thành "mệnh đề".
     *
     * Điều đó phá đúng bất đối xứng CÓ CHỦ Ý của lượt 1 (R11): một ô phân tích
     * hợp lệ ĐƯỢC PHÉP nhắc impressions/CTR/thumbnail — chính nó là ĐẦU VÀO của
     * bộ sinh nghĩa vụ. Chỉ trường THỪA (nhánh `try`, lấy từ `unrecognized_keys`)
     * và văn bản NGOÀI JSON mới là vi phạm. Vì gần như mọi bài phân tích thật
     * đều nhắc một trong các chỉ số ấy, `INVALID_JSON` — lớp retry sinh ra đúng
     * để xử lý JSON hỏng — trên thực tế không còn tồn tại.
     *
     * Bỏ quét ở đây KHÔNG mở đường lách. Payload hỏng cú pháp không sinh ra thứ
     * gì chính thức: không tập nghĩa vụ, không bản khai, không hàng COMPOSITE.
     * Lần thử lại buộc phải trả JSON hợp lệ, và khi đó nhánh `try` mới có đủ
     * cấu trúc trường để bắt ĐÚNG chỗ. Văn bản NGOÀI JSON vẫn bị
     * `scanProseOutsideJson` quét độc lập, không đi qua nhánh này.
     *
     * TRƯỚC KHI lùi tới đó: thử sửa dấu phẩy thừa rồi parse lại. Sửa được thì ta
     * có LẠI cấu trúc trường, và quét đúng như nhánh `try` — nên khẳng định ở
     * trường THỪA vẫn bị bắt (R18) mà ô THẬT vẫn được tha (C-1).
     */
    const repaired = reparseAfterTrivialRepair(input.raw)
    if (repaired.ok) {
      emittedScan = scanEmittedAnalysis(repaired.value)
    } else {
      const causal = scanCausalInRawText(input.raw)
      emittedScan = {
        issues: causal.issues,
        causalViolations: causal.causalViolations,
        ctrViolations: 0,
      }
    }
  }
  /*
   * `emittedScan` CHỈ dùng cho các `return` SỚM.
   *
   * Đường chạy ĐẦY ĐỦ đã quét ngôn ngữ nhân quả trên từng Ô qua `enumerateUnits`
   * — chính xác hơn nhiều, vì nó biết ô nào là giả thuyết (được phép nêu cơ chế
   * khi có rào đón) và trỏ được `path` thật. Gộp thêm bản quét thô vào đường ấy
   * sẽ ĐẾM HAI LẦN cùng một câu.
   */
  const prose = proseOutside
  claimIssues.push(...prose.issues)
  if (prose.issues.length > 0) {
    // `rule: null` — lời khuyên ĐỊNH DẠNG, luôn giữ ở mọi chặng. Vi phạm nằm
    // NGOÀI JSON thì không chặng nào khai báo được, nên nó không bao giờ bị lọc.
    pushRepair(
      `${prose.issues.length} vi phạm trong VĂN BẢN NGOÀI JSON — bỏ hẳn phần văn bản đó:\n` +
        prose.issues
          .slice(0, 3)
          .map((i) => `  • ${i.message}${i.excerpt ? `: "${i.excerpt}"` : ''}`)
          .join('\n'),
    )
  }

  const emptyReport = (): ValidationReport => ({
    passed: false,
    structuralIssues,
    evidenceIssues,
    // Ở `return` sớm, bản quét thô là thứ DUY NHẤT có — đường chạy đầy đủ chưa
    // bao giờ tới được phần quét theo Ô.
    claimIssues: [...claimIssues, ...emittedScan.issues],
    qualityIssues,
    evidenceResolutionRate: null,
    totalEvidenceRefs: 0,
    unresolvedEvidenceRefs: 0,
    causalViolations: prose.causalViolations + emittedScan.causalViolations,
    ctrViolations: prose.ctrViolations + emittedScan.ctrViolations,
    unsupportedMetricViolations: 0,
    counts: { findings: 0, hypotheses: 0, recommendations: 0, experiments: 0 },
  })

  /**
   * Phân loại thất bại tại một `return` sớm.
   *
   * Khẳng định BỊ CẤM trong văn bản ngoài JSON là thất bại NỘI DUNG và thắng mọi
   * thất bại KỸ THUẬT: nếu không, mô hình chỉ cần kèm một thân JSON hỏng là mọi
   * câu nhân quả/CTR nó viết ở ngoài đều rơi vào lớp RETRYABLE và được thử lại.
   */
  const earlyFailureClass = (
    technical: ValidateResult['failureClass'],
  ): ValidateResult['failureClass'] =>
    prose.causalViolations + emittedScan.causalViolations > 0 ||
    prose.ctrViolations + emittedScan.ctrViolations > 0
      ? 'UNSUPPORTED_CLAIM'
      : technical

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
    pushRepair('Output không phải JSON hợp lệ. Trả về DUY NHẤT một object JSON.')
    return {
      report: emptyReport(),
      output: null,
      failureClass: earlyFailureClass('INVALID_JSON'),
      repairErrors: drainRepairs(issuesSoFar()),
    }
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
    pushRepair('Trả về DUY NHẤT một object JSON, không kèm văn bản nào ngoài nó.')
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
    pushRepair(`schemaVersion phải đúng bằng "${CURSOR_OUTPUT_SCHEMA_VERSION}".`)
    return {
      report: emptyReport(),
      output: null,
      failureClass: earlyFailureClass('UNSUPPORTED_SCHEMA_VERSION'),
      repairErrors: drainRepairs(issuesSoFar()),
    }
  }
  if (version !== undefined && version !== CURSOR_OUTPUT_SCHEMA_VERSION) {
    structuralIssues.push({
      rule: 'schema_version',
      severity: 'BLOCKER',
      message: `schemaVersion không hỗ trợ: ${String(version)}`,
    })
    pushRepair(`schemaVersion phải đúng bằng "${CURSOR_OUTPUT_SCHEMA_VERSION}".`)
    return {
      report: emptyReport(),
      output: null,
      failureClass: earlyFailureClass('UNSUPPORTED_SCHEMA_VERSION'),
      repairErrors: drainRepairs(issuesSoFar()),
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
      pushRepair(`${issue.path.join('.') || '(gốc)'}: ${issue.message}`)
    }
    const missingRequired = result.error.issues.some((i) => i.code === 'invalid_type')
    return {
      report: emptyReport(),
      output: null,
      failureClass: earlyFailureClass(missingRequired ? 'MISSING_REQUIRED_FIELD' : 'SCHEMA_MISMATCH'),
      repairErrors: drainRepairs(issuesSoFar()),
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
      pushRepair(`${name}: id phải duy nhất (trùng: ${[...new Set(dupes)].join(', ')}).`)
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
      pushRepair(`experiments[${i}].hypothesisId phải là một id có trong hypotheses.`)
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
    pushRepair(
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
    pushRepair(
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
            : res.error === 'DUPLICATE_ITEM_ID'
              ? 'duplicate_source_item'
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
  // Bộ đếm KHỞI TẠO từ phép quét văn bản ngoài JSON đã chạy ở đầu hàm (F2).
  let causalViolations = prose.causalViolations
  let ctrViolations = prose.ctrViolations
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
    const structural =
      STRUCTURAL_SPEECH_ACT[speechActKey(mc.sourceRef.section, mc.sourceRef.field)]
    if (structural) {
      // Ô do CẤU TRÚC quy định: tình thái đọc từ tên trường, không từ từ ngữ.
      if (!structural.allowed.includes(mc.assertionStatus)) {
        claimIssues.push({
          rule: 'assertion_status_wrong_for_field',
          severity: 'BLOCKER',
          message:
            `${at}: ô này là ${structural.role}, nên assertionStatus phải là ` +
            `${structural.allowed.join(' hoặc ')} — không phải ${mc.assertionStatus}. ` +
            `ASSERTED bị cấm ở đây: một nhãn dữ liệu không khẳng định gì về chỉ số.`,
          path: at,
          excerpt: claimText.slice(0, 180),
        })
      }
    } else {
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

    // S4 — PHÂN CỰC của mệnh đề chứa CHỦ NGỮ phải khớp `assertionStatus`.
    //
    // S3 (ngay trên) chỉ bắt được chiều NGƯỢC HẲN: câu nói "cao", khai LOW. Nó
    // mù trước PHỦ ĐỊNH CÂN BẰNG, vì câu phủ định vẫn CHỨA từ cùng chiều:
    //
    //   ô:    "CTR không thấp, retention giảm"
    //   khai: subjectMetric=impression_ctr, judgement=LOW, ASSERTED
    //
    // "thấp" có mặt nên `self` khớp, "cao" vắng mặt nên `opposite` không khớp —
    // S3 im lặng, và một khẳng định BỊ ĐẢO đi qua trọn vẹn. Ca này do Codex dựng.
    //
    // 2.0 so phân cực giữa `claim.text` và văn xuôi; 2.1 không còn hai bản, nên
    // phép so đổi thành: mệnh đề chứa chủ ngữ có PHỦ ĐỊNH dấu hiệu phán xét hay
    // không, và điều đó có khớp với trạng thái đã khai hay không.
    //
    // Chỉ áp cho ASSERTED: các trạng thái khác (NEGATED_ACTION, LIMITATION,
    // CONDITIONAL, QUESTION) vốn được phép — và thường buộc phải — mang phủ định,
    // và đã có S2 đối chiếu dấu hiệu tình thái riêng.
    if (mc.assertionStatus === 'ASSERTED' && judgemental) {
      const jm = JUDGEMENT_MARKERS[mc.judgement]
      if (jm) {
        for (const clause of clausesOf(claimText)) {
          // Chỉ xét mệnh đề THỰC SỰ nói về chủ ngữ. Phủ định ở một mệnh đề khác
          // ("retention không giảm") không nói gì về chủ ngữ.
          if (mc.subjectMetric !== 'NONE' && !metricNamedIn(mc.subjectMetric, clause)) continue
          const hit = allMatches(jm.self, clause)[0]
          if (!hit) continue
          if (hasLocalNegation(clause, hit.index)) {
            claimIssues.push({
              rule: 'claim_polarity_mismatch',
              severity: 'BLOCKER',
              message:
                `${at}: khai ASSERTED + judgement=${mc.judgement} nhưng mệnh đề chứa ` +
                `"${mc.subjectMetric}" PHỦ ĐỊNH dấu hiệu đó. Khẳng định bị đảo chiều.`,
              path: at,
              excerpt: clause.slice(0, 180),
            })
          }
          break
        }
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
        /*
         * KHÔNG tăng `causalViolations` ở đây — bản quét theo Ô đã đếm rồi.
         *
         * `claimText` chính là `unit.text` của ô mà `sourceRef` trỏ tới, và vòng
         * quét theo Ô bên dưới đếm MỌI câu nhân quả trong MỌI ô. Tăng ở cả hai
         * chỗ khiến một câu duy nhất thành 2 (đã đo: P6 của vòng thăm dò). Con số
         * ấy được ghi vào `analysis_validation.causal_violations` và trích
         * nguyên văn trong `selfcheck_contradicted`, nên mọi báo cáo ổn định đọc
         * cột đó đều bị thổi phồng.
         *
         * BLOCKER vẫn giữ: đây là lỗi KHAI SAI NHÃN, khác với bản thân câu nhân
         * quả, và nó vẫn chặn `passed`.
         */
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
      /*
       * MIỄN cho claim KHÔNG khẳng định gì.
       *
       * Quy tắc này sinh ra để chặn một claim GIẤU phán xét về chỉ số chưa khai
       * ("thumbnail caused lower views" nối vào cuối một câu hợp lệ). Nó giả định
       * ngầm rằng mọi chỉ số được nhắc đều là chỉ số bị phán xét.
       *
       * Giả định đó sai với câu TỪ CHỐI KẾT LUẬN — loại câu mà hệ thống này BẮT
       * BUỘC phải có. Đo trên lô 6: 14/17 lần chặn là câu nhắc 3–4 chỉ số nhạy
       * cảm, mà một claim chỉ có HAI ô (`subjectMetric` + `relatedMetric`) và mỗi
       * nghĩa vụ chỉ ánh xạ tới MỘT claim. Câu điển hình:
       *
       *   "Không kết luận hiệu quả thumbnail, tiêu đề hút click, hay packaging
       *    vì impressions/CTR độ phủ 0%."
       *
       * Câu ấy nhắc cả bốn chỉ số CHÍNH VÌ nó đang từ chối kết luận về cả bốn —
       * và vì thế không khai nổi. Lượt 2 không sửa được văn xuôi, nên mô hình
       * không có đường thoát.
       *
       * Điều kiện miễn hẹp và tất định: claim KHÔNG mang phán xét
       * (`judgement` là UNKNOWN/NOT_APPLICABLE) VÀ không phải `ASSERTED`. Một
       * claim như vậy không khẳng định gì, nên nó không thể GIẤU điều gì. Ngay
       * khi có phán xét hoặc chuyển sang ASSERTED, quy tắc hoạt động lại đầy đủ.
       */
      const assertsNothing = !judgemental && mc.assertionStatus !== 'ASSERTED'
      if (undeclaredInText.length > 0 && !assertsNothing) {
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
    /*
     * MIỄN `data_coverage` — chủ ngữ SIÊU HÌNH, không phải chỉ số bị phán xét.
     *
     * R0b tồn tại để chặn khai SAI chỉ số bị phán xét ("câu nói về thumbnail mà
     * khai subjectMetric=views"). `data_coverage` không thuộc loại đó: thứ bị
     * phán xét là SỰ VẮNG MẶT của dữ liệu, mà sự vắng mặt không xuất hiện dưới
     * dạng một danh từ trong câu.
     *
     * Không miễn thì hai luật đối nghịch nhau và câu quan trọng nhất của cả miền
     * này không còn bản khai hợp lệ nào. Đo được trên lô 2026-08-13:
     *
     *   "Không có impressions/CTR nên không tách được mức tiếp cận khỏi mức xem"
     *     subjectMetric=impressions    -> methodology_subject_also_missing
     *     subjectMetric=data_coverage  -> subject_metric_not_in_text  (113 lần)
     *     mọi chỉ số khác              -> cũng không có trong câu
     *
     * Lượt 2 KHÔNG được sửa văn xuôi, nên mô hình không có đường thoát. Trong khi
     * chính hệ thống BẮT BUỘC bài phân tích phải công bố việc thiếu dữ liệu.
     *
     * Miễn ở đây KHÔNG nới lỏng phần còn lại: `methodology_without_related_metric`
     * vẫn buộc `relatedMetric` khác `NONE`, và chỉ số ấy thì CÓ mặt trong câu
     * (`impressions` ở ví dụ trên); `assertionStatus` vẫn phải là LIMITATION;
     * `judgement` vẫn phải UNKNOWN. Ràng buộc chỉ chuyển từ chủ ngữ sang bổ ngữ,
     * chỗ mà nó kiểm được thật.
     */
    if (
      mc.subjectMetric !== 'NONE' &&
      mc.subjectMetric !== 'data_coverage' &&
      !metricNamedIn(mc.subjectMetric, claimText)
    ) {
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

    /*
     * R1b — CHỐT BÙ cho việc nới `LIMITATION`.
     *
     * R1 chỉ soi `ASSERTED` và chỉ soi `subjectMetric`. Sau khi `LIMITATION`
     * nhận thêm "không … được" / "thiếu" / "không có", một câu như
     *
     *   "CTR thấp nên không tăng được view"
     *
     * sẽ khớp `LIMITATION`, và nếu khai `subjectMetric = data_coverage` (đã miễn
     * R0b) thì mọi cửa còn lại đều lọt — đúng "đường lách hiển nhiên nhất" mà
     * chú thích của `methodology_disguising_assertion` đã cảnh báo: dán nhãn
     * GIỚI HẠN lên một KHẲNG ĐỊNH.
     *
     * Chốt nhắm ĐÚNG cửa mà việc miễn R0b vừa mở ra, và không rộng hơn một ly:
     * `subjectMetric = data_coverage` KHÔNG được mang phán xét. `data_coverage`
     * là chủ ngữ SIÊU HÌNH nói về sự VẮNG MẶT của dữ liệu; một sự vắng mặt thì
     * không thể "cao" hay "thấp". Muốn phán xét thì phải nêu đích danh chỉ số bị
     * phán xét làm chủ ngữ — và khi ấy R0b buộc nó phải có mặt trong câu, còn R1
     * buộc nó phải có dữ liệu.
     *
     * KHÔNG soi `relatedMetric`. Bản đầu của chốt này có soi, và nó chặn oan
     * đúng những câu mà bộ test gọi là "các câu THẬT từng bị chặn oan":
     *
     *   "views quá thấp để ổn định CTR"
     *     subjectMetric=views (CÓ dữ liệu, bị phán xét LOW) + relatedMetric=CTR
     *
     * Ở đó phán xét thuộc về CHỦ NGỮ, còn `relatedMetric` chỉ là chỉ số CHỊU
     * ảnh hưởng. Soi bổ ngữ là hiểu sai ai đang bị phán xét.
     */
    /*
     * R1c — `judgement=UNKNOWN` KHÔNG được CHE một phán xét có thật trong câu.
     *
     * Codex vòng 21 tìm ra lỗ này, và nó là hệ quả GHÉP của ba miễn trừ chứ
     * không của riêng cái nào:
     *
     *   văn xuôi : "Thumbnail kém dù thiếu impressions/CTR."
     *   bản khai : data_coverage / impression_ctr / UNKNOWN / LIMITATION
     *
     * "thiếu" làm câu khớp LIMITATION; `data_coverage` được miễn R0b; và vì
     * claim tự khai UNKNOWN nên nó vừa được miễn `undeclared_metric_in_claim_text`
     * vừa làm R1b im lặng. Không quy tắc nào nổ, trong khi câu khẳng định thẳng
     * rằng `thumbnail` — một chỉ số phủ 0% — là "kém".
     *
     * Sai lầm gốc: `judgemental` suy ra TỪ TRƯỜNG KHAI BÁO, không từ văn xuôi.
     * Người khai chỉ cần nói "tôi không phán xét gì" là mọi chốt dựa trên phán
     * xét đều tắt. Một bản tự khai không thể là bằng chứng về chính nó.
     *
     * Phép kiểm theo MỆNH ĐỀ, không theo cả câu: chặn khi MỘT mệnh đề chứa ĐỒNG
     * THỜI một chỉ số phủ 0% và một từ phán xét. Xét cả câu sẽ chặn oan
     * "Độ phủ ngày rất thấp và impressions/CTR bằng không" — ở đó "thấp" nói về
     * độ phủ ngày, không nói về impressions. Đây đúng cái bẫy đã làm đỏ 10 test
     * khi bản đầu của R1b soi `relatedMetric`.
     */
    /*
     * CHỈ áp cho `LIMITATION`, không cho CONDITIONAL/QUESTION/NEGATED_ACTION.
     *
     * Ba trạng thái kia ĐÁNH DẤU SẴN rằng phán xét là giả định hoặc bị phủ định,
     * nên một từ phán xét nằm trong đó không phải khẳng định:
     *
     *   "nếu CTR thấp và impressions cao sẽ hướng kiểm chứng…"  (CONDITIONAL)
     *   "Độ phủ impressions/CTR >0 và observedDates tăng…"      (CONDITIONAL)
     *
     * Bản đầu của R1c xét mọi trạng thái không-ASSERTED và làm đỏ đúng ba câu
     * trong nhóm test "các câu THẬT từng bị chặn oan" — lần thứ hai trong vòng
     * này tôi mắc đúng lỗi ấy.
     *
     * `LIMITATION` thì khác: nó tuyên bố "câu này nêu GIỚI HẠN, không phát biểu
     * gì về giá trị chỉ số". Có phán xét trong đó nghĩa là cái nhãn ấy SAI.
     *
     * Và đường thoát bị bịt: muốn né sang CONDITIONAL/QUESTION/NEGATED_ACTION
     * thì câu phải mang dấu hiệu tương ứng, nếu không R0a
     * (`modality_not_supported_by_text`) chặn ngay.
     */
    /*
     * R1c — PHÁN XÉT trong câu về chỉ số phủ 0% bị chặn, BẤT KỂ bản khai nói gì.
     *
     * Bản trước chỉ soi `UNKNOWN` + `LIMITATION`, và tự rà soát bằng chạy cho
     * thấy ba đường né chỉ bằng cách đổi TRẠNG THÁI KHAI BÁO, giữ nguyên câu:
     *
     *   "Thumbnail kém chưa cải thiện."        NEGATED_ACTION -> LỌT
     *   "Thumbnail kém sẽ kéo lượt xem xuống."  CONDITIONAL   -> LỌT
     *   "Liệu thumbnail kém."                   QUESTION      -> LỌT
     *
     * Cả ba đều KHẲNG ĐỊNH `thumbnail` là "kém" rồi treo một từ tình thái ở VẾ
     * SAU. Gốc rễ vẫn là gốc rễ cũ: validator tin lời tự khai. Nên nay bỏ hẳn
     * việc hỏi bản khai, và chỉ hỏi CÂU VĂN. Hai câu hỏi, cả hai đều là VỊ TRÍ:
     *
     * (a) Từ phán xét đang phán xét AI? -> chỉ số GẦN NHẤT theo mép, không phải
     *     chỉ số phủ 0% đầu tiên bắt gặp trong mệnh đề. Thiếu chốt này thì
     *     "So sánh impressions của nhóm high-retention/low-views" bị chặn oan:
     *     HIGH khớp vào TÊN NHÓM `high-retention` (mép cách `retention` 1 ký tự,
     *     cách `impressions` 12) chứ không phán xét gì về impressions.
     *     Cùng chốt này tha "views quá thấp để ổn định CTR" — `thấp` dính
     *     `views`, còn CTR chỉ được nhắc tới.
     *
     * (b) Từ tình thái có BAO TRÙM phán xét không? -> nó phải đứng TRƯỚC.
     *     "Nếu thumbnail kém thì cần kiểm chứng"   nếu(0)  < kém(15) -> giả định, THA
     *     "Thumbnail kém sẽ kéo lượt xem xuống"    kém(10) < sẽ(14)  -> khẳng định, CHẶN
     *     Đó là khác biệt giữa "giả định về một phán xét" và "một phán xét kèm
     *     hệ quả giả định" — sự CÓ MẶT của từ tình thái không phân biệt được.
     */
    for (const clause of clausesOf(claimText)) {
      const marker = Object.entries(JUDGEMENT_MARKERS).find(([, j]) => j.self.test(clause))
      if (!marker) continue
      const judgeHit = clause.match(marker[1].self)
      if (!judgeHit || judgeHit.index === undefined) continue
      const judgeFrom = judgeHit.index
      const judgeTo = judgeFrom + judgeHit[0].length

      // (a) chỉ số nào sát từ phán xét nhất -> đó là kẻ bị phán xét
      let judgedMetric: string | null = null
      let bestGap = Number.POSITIVE_INFINITY
      for (const [m, re] of Object.entries(METRIC_ALIASES)) {
        const hit = clause.match(re)
        if (!hit || hit.index === undefined) continue
        const from = hit.index
        const to = from + hit[0].length
        const gap = to <= judgeFrom ? judgeFrom - to : from >= judgeTo ? from - judgeTo : 0
        if (gap < bestGap) {
          bestGap = gap
          judgedMetric = m
        }
      }
      if (!judgedMetric || !zeroCoverage.has(judgedMetric)) continue

      // (b) tình thái mở đầu -> bao trùm phán xét -> đây là giả định, không phải khẳng định
      const modalAt = Object.values(MODALITY_MARKERS).reduce((best, re) => {
        const i = clause.search(re)
        return i >= 0 && (best < 0 || i < best) ? i : best
      }, -1)
      if (modalAt >= 0 && modalAt < judgeFrom) continue

      claimIssues.push({
        rule: 'judgement_on_missing_metric_in_text',
        severity: 'BLOCKER',
        message:
          `${at}: mệnh đề "${clause.trim().slice(0, 80)}" phán xét (${marker[0]}) về ` +
          `"${judgedMetric}" — chỉ số phủ 0%. Khai assertionStatus=${mc.assertionStatus} / ` +
          `judgement=${mc.judgement} KHÔNG xoá được khẳng định đã nằm trong câu; ` +
          `từ tình thái phải đứng TRƯỚC phán xét thì mới là giả định.`,
        path: at,
        excerpt: claimText.slice(0, 180),
      })
      break
    }

    if (mc.assertionStatus !== 'ASSERTED' && judgemental && mc.subjectMetric === 'data_coverage') {
      claimIssues.push({
        rule: 'limitation_carries_judgement_on_missing_metric',
        severity: 'BLOCKER',
        message:
          `${at}: subjectMetric=data_coverage nhưng mang judgement=${mc.judgement}. ` +
          `Độ phủ dữ liệu là sự VẮNG MẶT, không "cao"/"thấp" được. Dùng judgement=UNKNOWN, ` +
          `hoặc nêu đích danh chỉ số bị phán xét làm chủ ngữ.`,
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
    const contradictions: Array<[boolean, string]> = CLAIM_CONTRADICTIONS.map(
      (r) => [r.test(mc as never, judgemental), r.message] as [boolean, string],
    )
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
    pushRepair(
      `${assertedOnMissing} metricClaims khẳng định về chỉ số có độ phủ 0%. ` +
        `Đổi assertionStatus sang CONDITIONAL/QUESTION/LIMITATION/NEGATED_ACTION và khai đúng ` +
        `claimType, hoặc bỏ hẳn phát biểu đó.`,
      'asserted_claim_on_missing_metric',
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

  // Văn bản NGOÀI JSON đã được quét ở ĐẦU hàm, độc lập với mọi cổng schema —
  // xem `scanProseOutsideJson` và ghi chú F2. Không quét lại ở đây: quét hai lần
  // sẽ nhân đôi bộ đếm vi phạm.

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

  /*
   * DÒNG SỬA LỖI dẫn xuất từ vi phạm — dựng ở ĐÂY, sau khi ĐẾM XONG.
   *
   * Khiếm khuyết CÓ TỪ TRƯỚC, lộ ra khi sửa rò rỉ giữa các chặng: hai khối này
   * từng nằm ở giữa hàm, TRƯỚC các lần `causalViolations++` ở phần quét phát
   * hiện/khuyến nghị. Nên một câu nhân quả nằm trong `keyFindings[].statement`
   * — đúng ca của lần thăm dò 2026-08-06 — bị CHẶN đúng, nhưng prompt sửa lỗi
   * KHÔNG hề nhắc tới nó. Thiếu hướng dẫn cho một vi phạm có thật là mặt kia
   * của cùng một đồng xu với việc rò hướng dẫn cho một vi phạm không có thật.
   */
  if (causalViolations) {
    // Kèm ĐÚNG câu vi phạm vào prompt sửa lỗi: bảo "bỏ ngôn ngữ nhân quả" mà
    // không chỉ ra ở đâu thì lần sửa sau chủ yếu là đoán.
    const samples = claimIssues
      .filter((i) => i.rule === 'causal_claim' && i.excerpt)
      .slice(0, 3)
      .map((i) => `  • ${i.path}: "${i.excerpt}"`)
    pushRepair(
      'Bỏ ngôn ngữ nhân quả ở phần khẳng định (tóm tắt, phát hiện, lý do khuyến nghị). ' +
        'Dùng "có liên hệ với", "phù hợp với", "có thể cho thấy". Trong hypotheses/experiments, ' +
        'nếu nêu cơ chế thì PHẢI rào đón bằng "có thể"/"giả thuyết"/"may"/"plausible".' +
        (samples.length ? `\nCác câu vi phạm:\n${samples.join('\n')}` : ''),
      ['causal_claim', 'causal_language_in_non_causal_claim', 'asserted_causal_claim'],
    )
  }

  if (ctrViolations) {
    /*
     * F4 — HAI khiếm khuyết trong đúng khối này, cả hai đều im lặng.
     *
     * 1. Phép chọn câu vi phạm lọc theo `ctr_claim_without_coverage`, một tên
     *    KHÔNG quy tắc nào phát ra. `samples` vì thế RỖNG ở mọi trường hợp, và
     *    dòng hướng dẫn CTR không bao giờ trích được câu vi phạm — đúng cái mà
     *    khối nhân quả ngay bên trên đã được sửa để làm.
     *
     * 2. Câu "các chỉ số đó có độ phủ 0% ở gói này" được khẳng định VÔ ĐIỀU KIỆN.
     *    Ba quy tắc làm `ctrViolations` tăng đều nói về KHAI BÁO, không về độ
     *    phủ — nên với một gói CÓ impressions, prompt sửa lỗi nói với mô hình một
     *    điều SAI SỰ THẬT về chính dữ liệu nó vừa đọc.
     */
    const samples = claimIssues
      .filter((i) => (CTR_VIOLATION_RULES as readonly string[]).includes(i.rule) && i.excerpt)
      .slice(0, 3)
      .map((i) => `  • ${i.path}: "${i.excerpt}"`)
    pushRepair(
      (ctrCoverage === 0
        ? 'Bỏ mọi kết luận về CTR/impressions/thumbnail — các chỉ số đó có độ phủ 0% ở gói này.'
        : (input.stage ?? 'COMPOSITE') === 'ANALYSIS'
          ? // Lượt PHÂN TÍCH KHÔNG được sinh `metricClaims` — bảo nó khai báo ở đó
            // là bảo nó làm đúng thứ mà `claims_in_analysis_pass` chặn thẳng.
            // Ở lượt này cách sửa đúng là TÁCH Ô, không phải khai báo.
            'Mỗi ô chỉ được mang MỘT phát biểu: tách phát biểu về ' +
            'CTR/impressions/thumbnail thành phần tử riêng. KHÔNG thêm `metricClaims` ' +
            'vào lượt này — khai báo ngữ nghĩa là một lượt RIÊNG chạy sau.'
          : 'Mọi phát biểu chạm tới CTR/impressions/thumbnail phải được KHAI BÁO trong `metricClaims`, ' +
            'và mỗi ô chỉ mang MỘT phát biểu.') +
        (samples.length ? `\nCác câu vi phạm:\n${samples.join('\n')}` : ''),
      // MỘT danh sách dùng cho CẢ phép chọn câu vi phạm LẪN nhãn lọc theo chặng.
      // Hai danh sách riêng cho cùng một khái niệm đúng là cách F4 ra đời.
      [...CTR_VIOLATION_RULES],
    )
  }

  /*
   * LỌC THEO CHẶNG — làm ở ĐÂY, trước mọi thứ phụ thuộc vào nó.
   *
   * Chặng PHÂN TÍCH chưa có bản khai, nên U3 (`undeclared_sensitive_unit`) và
   * hệ quả của nó không áp dụng được: lượt 1 KHÔNG THỂ khai gì cả. Trước đây
   * phép lọc nằm ở `validateAnalysisOutput`, tức SAU khi `repairErrors`,
   * `highs` và `failureClass` đã được tính từ tập chưa lọc — nên báo cáo lưu lại
   * một đằng, prompt sửa lỗi nói một nẻo. Lọc ở đây thì mọi thứ phía sau nhất quán.
   */
  const stage = input.stage ?? 'COMPOSITE'
  if (stage === 'ANALYSIS') {
    // CHỈ lọc U3 phát sinh TỪ CÁC Ô TRONG JSON — thứ mà lượt 1 không thể khai
    // báo vì bản khai chưa tồn tại.
    //
    // U3 còn được phát ra cho VĂN BẢN NGOÀI JSON (path `(văn bản ngoài JSON)`),
    // và đó là chuyện khác hẳn: mô hình viết một khẳng định nhạy cảm ở nơi KHÔNG
    // THỂ khai báo được ở bất kỳ chặng nào. Lọc theo quy tắc mà không xét path
    // đã xoá luôn vi phạm ấy khỏi hồ sơ, hạ `ctrViolations` về 0, và — vì phép
    // lọc chạy TRƯỚC `failureClass` — đổi phân loại thành `PROSE_OUTSIDE_JSON`,
    // vốn nằm trong RETRYABLE. Tức là biến một thất bại NỘI DUNG thành một thất
    // bại KỸ THUẬT được phép thử lại: đúng cái "chạy lại tới khi mô hình thôi
    // nói điều đó" mà lớp này tồn tại để cấm.
    const isProseUnit = (i: ValidationIssue) => i.path === PROSE_OUTSIDE_JSON_PATH
    const u3 = claimIssues.filter(
      (i) => i.rule === 'undeclared_sensitive_unit' && !isProseUnit(i),
    )
    claimIssues = claimIssues.filter(
      (i) => i.rule !== 'undeclared_sensitive_unit' || isProseUnit(i),
    )
    // `selfcheck_contradicted` về CTR chỉ được bỏ khi nó do U3-trong-JSON gây
    // ra. Nếu sau khi trừ vẫn còn vi phạm CTR (U1, văn bản ngoài JSON, ...) thì
    // lời tự khai "không có kết luận CTR" VẪN mâu thuẫn với thực tế và phải giữ.
    const ctrAfter = Math.max(0, ctrViolations - u3.length)
    if (ctrAfter === 0) {
      qualityIssues = qualityIssues.filter(
        (i) => !(i.rule === 'selfcheck_contradicted' && i.path === 'selfCheck.madeCtrOrImpressionClaims'),
      )
    }
    ctrViolations = ctrAfter
  }

  const allIssues = [...structuralIssues, ...evidenceIssues, ...claimIssues, ...qualityIssues]

  /*
   * DÒNG SỬA LỖI chỉ giữ những gì thuộc về tập vi phạm CUỐI CÙNG.
   *
   * `rule: null` là lời khuyên định dạng, luôn giữ. Còn lại phải có quy tắc
   * tương ứng còn sống sau khi lọc theo chặng.
   */

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

  /*
   * `prose_outside_json` KHÔNG được xếp trên các lớp NỘI DUNG.
   *
   * Bản trước xét `input.hadProseOutsideJson` ngay sau nhóm vi phạm khẳng định,
   * tức là TRÊN cả `EVIDENCE_UNRESOLVED` lẫn lớp HIGH-thuần-chất-lượng. Vì
   * `PROSE_OUTSIDE_JSON` nằm trong `RETRYABLE` còn hai lớp kia thì không, một
   * khối ```json bọc ngoài — thứ mô hình thêm vào theo phản xạ — ĐỔI HẲN cách
   * xử lý một thất bại nội dung:
   *
   *   cùng một payload, evidenceIds = ["OBS-999"]
   *     không bọc  -> EVIDENCE_UNRESOLVED -> dừng ở lần thử 1
   *     có bọc     -> PROSE_OUTSIDE_JSON  -> thử lại 3 lần kèm prompt sửa lỗi
   *
   * Đo được bằng chạy: P3/P4 của vòng thăm dò. Đây đúng là "thử lại cho tới khi
   * mô hình thôi nói điều bị cấm" mà `run.ts` cấm — chỉ khác là cánh cửa mở ra
   * bằng một lỗi ĐỊNH DẠNG hoàn toàn vô can.
   *
   * Cách xếp lại: tách BLOCKER cấu trúc THẬT khỏi `prose_outside_json`. Còn
   * BLOCKER cấu trúc thật thì đây là thất bại KỸ THUẬT (được thử lại); không
   * còn cái nào mà vẫn có HIGH thì HIGH ấy là thất bại NỘI DUNG và phải chặn.
   * `prose_outside_json` đứng một mình mới trả về lớp mang tên nó.
   */
  const structuralBlockers = blockers.filter((i) => i.rule !== 'prose_outside_json')

  const failureClass: ValidateResult['failureClass'] =
    blockers.length === 0 && highs.length === 0
      ? 'NONE'
      : // Khẳng định bị cấm được xét TRƯỚC mọi lỗi định dạng: nếu văn bản ngoài
        // JSON chứa câu nhân quả/CTR thì đó là thất bại NỘI DUNG, không được thử
        // lại, dù đồng thời cũng có lỗi định dạng.
        causalViolations > 0 || ctrViolations > 0 || unsupportedMetricViolations > 0
        ? 'UNSUPPORTED_CLAIM'
        : unresolvedRefs > 0 || ungroundedItems > 0
          ? 'EVIDENCE_UNRESOLVED'
          : structuralBlockers.length > 0
            ? // Lỗi cấu trúc thật -> KỸ THUẬT. Nếu đồng thời có văn bản ngoài
              // JSON thì lấy lớp cụ thể hơn; cả hai đều nằm trong RETRYABLE.
              input.hadProseOutsideJson
              ? 'PROSE_OUTSIDE_JSON'
              : 'SCHEMA_MISMATCH'
            : highs.length > 0
              ? // Lỗi HIGH thuần chất lượng (thiếu bằng chứng, tự tin thái quá)
                // là thất bại NỘI DUNG, không phải kỹ thuật -> không được retry,
                // kể cả khi payload cũng bị bọc ngoài JSON.
                'UNSUPPORTED_CLAIM'
              : 'PROSE_OUTSIDE_JSON'

  if (highs.length > 0) {
    pushRepair(
      `${highs.length} lỗi mức HIGH: ` +
        highs
          .slice(0, 5)
          .map((i) => `${i.path ?? i.rule}: ${i.message}`)
          .join(' | '),
    )
  }

  drainRepairs(allIssues)

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

/* =========================================================================
 * KIỂM ĐỊNH THEO CHẶNG — kiến trúc HAI LƯỢT
 * ====================================================================== */

/**
 * CHẶNG ANALYSIS — kiểm bản VĂN XUÔI của lượt 1.
 *
 * Cài đặt bằng cách UỶ QUYỀN cho `validateCursorOutput` với `metricClaims: []`,
 * KHÔNG bằng cách nhân đôi logic. Lý do: mọi quy tắc văn xuôi ở đó — neo bằng
 * chứng, U1, ngôn ngữ nhân quả, chỉ số bịa, chất lượng — đã qua bốn lần thăm dò
 * thật và 568 test. Viết lại chúng ở đây là tạo ra một bản thứ hai để lệch.
 *
 * Khác biệt DUY NHẤT so với chặng hợp nhất: `undeclared_sensitive_unit` (U3) bị
 * BỎ QUA. Ở lượt 1 chưa có claim nào theo đúng thiết kế, nên U3 sẽ báo cho MỌI ô
 * nhạy cảm — đó là tiếng ồn, không phải phát hiện. U3 được cưỡng chế bằng cấu
 * trúc ở chặng sau: tập nghĩa vụ CHÍNH LÀ tập ô nhạy cảm.
 */
export function validateAnalysisOutput(input: ValidateInput): ValidateResult {
  // 1. Hình dạng lượt 1 trước đã — đây là chỗ chặn việc tuồn `metricClaims`.
  let parsed: unknown
  try {
    parsed = JSON.parse(input.raw)
  } catch {
    return validateCursorOutput(input) // để nhánh json_parse chung xử lý
  }
  const shape = cursorAnalysisSchema.safeParse(parsed)
  if (!shape.success) {
    const smuggled = shape.error.issues.some(
      (i) => i.code === 'unrecognized_keys' && JSON.stringify(i).includes('metricClaims'),
    )
    const issues: ValidationIssue[] = []
    const repairErrors: string[] = []
    if (smuggled) {
      issues.push({
        rule: 'claims_in_analysis_pass',
        severity: 'BLOCKER',
        message:
          'Lượt PHÂN TÍCH sinh ra `metricClaims`. Lượt này chỉ viết văn xuôi; khai báo ' +
          'ngữ nghĩa là một lượt RIÊNG chạy sau, trên chính văn bản này.',
      })
      repairErrors.push('Bỏ hoàn toàn trường `metricClaims` khỏi output.')
    }
    for (const i of shape.error.issues.slice(0, 25)) {
      issues.push({ rule: 'schema', severity: 'BLOCKER', message: i.message, path: i.path.join('.') })
      repairErrors.push(`${i.path.join('.') || '(gốc)'}: ${i.message}`)
    }

    /*
     * F2 — nhánh này là ĐƯỜNG VÒNG quanh `validateCursorOutput`, nên nó phải tự
     * quét văn bản ngoài JSON. Trước đây nó không quét: hình dạng lượt 1 hỏng là
     * đủ để mọi khẳng định bị cấm nằm ngoài JSON biến mất, và lớp thất bại rơi
     * vào `MISSING_REQUIRED_FIELD` (RETRYABLE).
     *
     * Dùng CHUNG `scanProseOutsideJson` với đường chạy đầy đủ — không viết lại
     * bản thứ hai để rồi lệch.
     */
    const proseOnly = scanProseOutsideJson(input.proseText)
    /*
     * Payload ĐÃ PARSE nhưng hỏng hình dạng lượt 1 cũng phải được quét.
     *
     * Nhánh này là đường vòng quanh `validateCursorOutput`, nên nó KHÔNG hưởng
     * phép quét ở các `return` sớm bên đó. Không có dòng này thì một câu nhân
     * quả nằm TRONG payload biến mất mỗi khi payload hỏng schema lượt 1 — và cả
     * hai lớp thất bại ở đây đều RETRYABLE.
     */
    const emittedCausal = scanCausalInEmittedJson(parsed)
    // Trường THỪA của lượt 1 không bao giờ thành nghĩa vụ (`.strict()` từ chối
    // mãi mãi), nên khẳng định nhạy cảm ở đó cũng phải bị chặn — khác với một Ô
    // PHÂN TÍCH hợp lệ, nơi câu ấy sẽ đi qua cơ chế khai báo (ranh giới R11).
    const emittedExtras = scanSensitiveInAnalysisExtras(parsed)
    const emittedScan: ProseScanResult = {
      issues: [...emittedCausal.issues, ...emittedExtras.issues],
      causalViolations: emittedCausal.causalViolations,
      ctrViolations: emittedExtras.ctrViolations,
    }
    const prose: ProseScanResult = {
      issues: [...proseOnly.issues, ...emittedScan.issues],
      causalViolations: proseOnly.causalViolations + emittedScan.causalViolations,
      ctrViolations: proseOnly.ctrViolations + emittedScan.ctrViolations,
    }
    if (input.hadProseOutsideJson) {
      issues.push({
        rule: 'prose_outside_json',
        severity: 'BLOCKER',
        message: 'Có văn bản ngoài object JSON — hợp đồng yêu cầu CHỈ một object JSON.',
      })
      repairErrors.push('Trả về DUY NHẤT một object JSON, không kèm văn bản nào ngoài nó.')
    }
    if (prose.issues.length > 0) {
      repairErrors.push(
        `${prose.issues.length} vi phạm trong VĂN BẢN NGOÀI JSON: ` +
          prose.issues
            .slice(0, 5)
            .map((i) => i.message)
            .join(' | '),
      )
    }

    const technical = shape.error.issues.some((i) => i.code === 'invalid_type')
      ? 'MISSING_REQUIRED_FIELD'
      : 'SCHEMA_MISMATCH'

    return {
      report: {
        passed: false,
        structuralIssues: issues,
        evidenceIssues: [],
        claimIssues: prose.issues,
        qualityIssues: [],
        evidenceResolutionRate: null,
        totalEvidenceRefs: 0,
        unresolvedEvidenceRefs: 0,
        causalViolations: prose.causalViolations,
        ctrViolations: prose.ctrViolations,
        unsupportedMetricViolations: 0,
        counts: { findings: 0, hypotheses: 0, recommendations: 0, experiments: 0 },
      },
      output: null,
      // Thất bại NỘI DUNG thắng thất bại KỸ THUẬT — xem `earlyFailureClass`.
      failureClass:
        prose.causalViolations > 0 || prose.ctrViolations > 0 ? 'UNSUPPORTED_CLAIM' : technical,
      repairErrors,
    }
  }

  // 2. Chạy bộ quy tắc văn xuôi qua bộ kiểm định chung.
  const asComposite = {
    ...shape.data,
    schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
    metricClaims: [] as unknown[],
  }
  // 3. Lọc theo chặng nay nằm TRONG `validateCursorOutput` (tham số `stage`).
  //
  // Trước đây lọc ở đây, tức SAU khi bộ kiểm đã tính `repairErrors`, `highs` và
  // `failureClass` từ tập CHƯA lọc. Hệ quả lộ ra ở lần thăm dò 2026-08-06: báo
  // cáo lưu `ctr_violations = 0` trong khi prompt sửa lỗi vẫn bảo mô hình "bỏ
  // mọi kết luận về CTR". Lọc muộn thì mọi con số dẫn xuất đều sai theo.
  const r = validateCursorOutput({ ...input, raw: JSON.stringify(asComposite), stage: 'ANALYSIS' })

  return {
    report: r.report,
    output: r.report.passed || r.output ? (shape.data as unknown as CursorOutput) : null,
    failureClass: r.failureClass,
    repairErrors: r.repairErrors,
  }
}

export interface DeclarationValidateInput {
  raw: string
  obligationSet: ClaimObligationSet
  obligationSetHash: string
}

export interface DeclarationValidateResult {
  report: ValidationReport
  declarations: ClaimDeclaration[] | null
  failureClass: ValidateResult['failureClass']
  repairErrors: string[]
}

/**
 * CHẶNG DECLARATION — kiểm bản khai của lượt 2.
 *
 * Chạy: hình dạng, băm tập nghĩa vụ (O-INV-4), danh tính khai báo (O-INV-3), và
 * `assertionStatus` phải nằm trong tập hợp lệ của chính ô đó.
 *
 * KHÔNG chạy S1–S8 ở đây. Chúng cần `metricClaims` đã GHÉP với `sourceRef` và
 * cần độ phủ của gói, tức cần bước hợp nhất — việc của chặng COMPOSITE (G5).
 * Bản thiết kế mục 3.3.1 xếp S vào chặng này; chuyển sang COMPOSITE là một sai
 * khác CÓ GHI NHẬN, vì ghép claim là thao tác của chặng hợp nhất chứ không phải
 * của lượt khai báo.
 */
export function validateDeclarationOutput(
  input: DeclarationValidateInput,
): DeclarationValidateResult {
  const structuralIssues: ValidationIssue[] = []
  const claimIssues: ValidationIssue[] = []
  const repairErrors: string[] = []
  const empty = (): ValidationReport => ({
    passed: false,
    structuralIssues,
    evidenceIssues: [],
    claimIssues,
    qualityIssues: [],
    evidenceResolutionRate: null,
    totalEvidenceRefs: 0,
    unresolvedEvidenceRefs: 0,
    causalViolations: 0,
    ctrViolations: 0,
    unsupportedMetricViolations: 0,
    counts: { findings: 0, hypotheses: 0, recommendations: 0, experiments: 0 },
  })

  /*
   * Ngôn ngữ nhân quả trong payload KHAI BÁO.
   *
   * Lượt 2 chỉ được khai báo ngữ nghĩa, nhưng không gì ngăn mô hình nhét một câu
   * nhân quả vào một trường thừa (`.strict()` sẽ báo lỗi schema — RETRYABLE — và
   * câu ấy trôi qua). Đây là người gọi thứ tư và cuối cùng của phép quét.
   *
   * PHẠM VI, nói chính xác: NGÔN NGỮ NHÂN QUẢ được quét ở MỌI đường thất bại.
   * Nhắc/khẳng định về CHỈ SỐ NHẠY CẢM bên trong JSON thì KHÔNG — và đó là chủ
   * đích, không phải thiếu sót. Xem `scanCausalInEmittedJson`.
   */
  let emittedScan: ProseScanResult = { issues: [], causalViolations: 0, ctrViolations: 0 }

  let parsed: unknown
  try {
    parsed = JSON.parse(input.raw)
    const causal = scanCausalInEmittedJson(parsed)
    // Lượt KHAI BÁO cũng phải chặn khẳng định về chỉ số nhạy cảm nhét ngoài cấu
    // trúc khai báo — ở đây KHÔNG còn chặng nào rà soát ngữ nghĩa cho nó nữa.
    const sensitive = scanSensitiveInDeclarationJson(parsed)
    emittedScan = {
      issues: [...causal.issues, ...sensitive.issues],
      causalViolations: causal.causalViolations,
      ctrViolations: sensitive.ctrViolations,
    }
    claimIssues.push(...emittedScan.issues)
  } catch (err) {
    /*
     * Không parse được vẫn quét — VÀ ở lượt KHAI BÁO phải quét CẢ khẳng định
     * nhạy cảm, không chỉ nhân quả.
     *
     * Lý do vẫn là lý do của R13: bản khai hỏng cú pháp KHÔNG có đường sinh
     * nghĩa vụ nào phía sau, nên một câu như `{"extra":"CTR thấp.",}` sẽ trôi
     * qua với lớp `INVALID_JSON` (RETRYABLE) nếu chỉ quét nhân quả.
     *
     * Nhưng KHÔNG được quét cả payload như MỘT chuỗi. Làm vậy thì
     * `isKnownFieldValue` mất tác dụng và một bản khai ĐÚNG bị chặn vĩnh viễn
     * chỉ vì nó chứa `"relatedMetric":"impression_ctr"` — trong khi lỗi duy
     * nhất là một dấu phẩy thừa. `recoverJsonStringLiterals` lấy lại từng chuỗi
     * một, nên phép loại trừ giá trị-trường hoạt động y như đường đã parse
     * được, mà `{"extra":"CTR thấp.",}` vẫn bị bắt.
     */
    const repaired = reparseAfterTrivialRepair(input.raw)
    const rawCausal = repaired.ok
      ? scanCausalInEmittedJson(repaired.value)
      : scanCausalInRawText(input.raw)
    const rawSensitive = scanSensitiveInDeclarationJson(
      repaired.ok ? repaired.value : recoverJsonStringLiterals(input.raw),
    )
    emittedScan = {
      issues: [...rawCausal.issues, ...rawSensitive.issues],
      causalViolations: rawCausal.causalViolations,
      ctrViolations: rawSensitive.ctrViolations,
    }
    claimIssues.push(...emittedScan.issues)
    structuralIssues.push({
      rule: 'json_parse',
      severity: 'BLOCKER',
      message: `Không parse được JSON: ${err instanceof Error ? err.message : 'lỗi không rõ'}`,
    })
    repairErrors.push('Trả về DUY NHẤT một object JSON.')
    return {
      report: {
        ...empty(),
        causalViolations: emittedScan.causalViolations,
        ctrViolations: emittedScan.ctrViolations,
      },
      declarations: null,
      failureClass:
        emittedScan.causalViolations + emittedScan.ctrViolations > 0
          ? 'UNSUPPORTED_CLAIM'
          : 'INVALID_JSON',
      repairErrors,
    }
  }

  const shape = declarationOutputSchema.safeParse(parsed)
  if (!shape.success) {
    // Ca RIÊNG: mô hình cố viết `sourceRef` hay `text` vào bản khai. `.strict()`
    // đã chặn, nhưng thông điệp chung chung không nói được vì sao — và đây chính
    // là điều 4 của hợp đồng ("không đổi mục tiêu") đang được cưỡng chế.
    const dump = JSON.stringify(shape.error.issues)
    if (dump.includes('sourceRef') || dump.includes('"text"')) {
      structuralIssues.push({
        rule: 'declaration_defines_target',
        severity: 'BLOCKER',
        message:
          'Bản khai cố ghi `sourceRef`/`text`. Ô đã được chỉ định sẵn trong tập nghĩa vụ; ' +
          'lượt khai báo chỉ điền ngữ nghĩa, không chọn hay đổi ô.',
      })
      repairErrors.push('Bỏ mọi trường định vị (`sourceRef`, `text`) khỏi từng mục khai báo.')
    }
    for (const i of shape.error.issues.slice(0, 25)) {
      structuralIssues.push({
        rule: 'schema',
        severity: 'BLOCKER',
        message: i.message,
        path: i.path.join('.'),
      })
      repairErrors.push(`${i.path.join('.') || '(gốc)'}: ${i.message}`)
    }
    return {
      report: {
        ...empty(),
        causalViolations: emittedScan.causalViolations,
        ctrViolations: emittedScan.ctrViolations,
      },
      declarations: null,
      // Khẳng định bị cấm THẮNG lỗi hình dạng: nếu không, mô hình chỉ cần nhét
      // câu ấy vào một trường thừa là `.strict()` cho ra lỗi schema RETRYABLE và
      // câu bị cấm trôi qua.
      failureClass:
        emittedScan.causalViolations + emittedScan.ctrViolations > 0
          ? 'UNSUPPORTED_CLAIM'
          : shape.error.issues.some((i) => i.code === 'invalid_type')
            ? 'MISSING_REQUIRED_FIELD'
            : 'SCHEMA_MISMATCH',
      repairErrors,
    }
  }

  const out = shape.data

  // O-INV-4 — bản khai phải trả lời ĐÚNG tập nghĩa vụ đang hiện hành.
  const hashCheck = checkObligationSetHash(input.obligationSetHash, out.obligationSetHash)
  if (!hashCheck.ok) {
    structuralIssues.push({ rule: hashCheck.rule, severity: 'BLOCKER', message: hashCheck.message })
    repairErrors.push(`obligationSetHash phải đúng bằng "${input.obligationSetHash}".`)
  }

  // O-INV-3 — không thiếu, không thừa, không trùng.
  for (const issue of checkDeclarationIdentity(input.obligationSet, out.declarations.map((d) => d.id))) {
    if (issue.ok) continue
    claimIssues.push({ rule: issue.rule, severity: 'BLOCKER', message: issue.message, path: issue.path })
    repairErrors.push(issue.message)
  }

  // `assertionStatus` phải nằm trong tập hợp lệ CỦA CHÍNH Ô ĐÓ.
  //
  // Với ô nhãn, tập này không chứa `ASSERTED` — nên trạng thái mạnh nhất trở
  // thành bất khả biểu diễn ở đúng những ô vô hại nhất.
  const byId = new Map(input.obligationSet.obligations.map((o) => [o.id, o]))
  for (const d of out.declarations) {
    const ob = byId.get(d.id)
    if (!ob) continue // đã báo ở O-INV-3
    if (!ob.allowedAssertionStatuses.includes(d.assertionStatus)) {
      claimIssues.push({
        rule: 'assertion_status_wrong_for_field',
        severity: 'BLOCKER',
        message:
          `${d.id}: assertionStatus=${d.assertionStatus} không nằm trong tập hợp lệ của ô này ` +
          `(${ob.allowedAssertionStatuses.join(', ')}).`,
        path: ob.pointer,
        excerpt: ob.resolvedText.slice(0, 180),
      })
      repairErrors.push(
        `${d.id}: chọn assertionStatus trong ${ob.allowedAssertionStatuses.join(' | ')}.`,
      )
    }
  }

  const allIssues = [...structuralIssues, ...claimIssues]
  const blockers = allIssues.filter((i) => i.severity === 'BLOCKER')
  const passed = blockers.length === 0

  return {
    report: {
      ...empty(),
      passed,
      causalViolations: emittedScan.causalViolations,
      ctrViolations: emittedScan.ctrViolations,
    },
    declarations: passed ? out.declarations : null,
    /*
     * PHÂN LOẠI theo DANH SÁCH TƯỜNG MINH, không theo "mọi thứ khác là nội dung".
     *
     * Bản trước chỉ cho `rule === 'schema'` là kỹ thuật và ném MỌI thứ còn lại
     * vào `UNSUPPORTED_CLAIM` — lớp KHÔNG được thử lại. Hệ quả kiểm chứng được:
     * mô hình chép sai MỘT ký tự của `obligationSetHash` thì `obligation_set_drift`
     * thành thất bại NỘI DUNG vĩnh viễn, vòng chạy dừng ngay sau lần thử đầu, và
     * một bài phân tích ĐÃ ĐÓNG BĂNG hợp lệ bị vứt đi — trong khi dòng sửa lỗi
     * cho đúng cái đó đã nằm sẵn trong `repairErrors`.
     *
     * Đây là chiều sai NGƯỢC với các lỗ fail-open đã sửa, nhưng vẫn là sai: hợp
     * đồng nói rõ thất bại KỸ THUẬT được thử lại, NỘI DUNG thì không.
     *
     * KỸ THUẬT = mô hình chép sai / khai không đúng TẬP được giao. Thử lại chỉ
     * khiến nó khai cho ĐÚNG tập ấy, không cho nó đổi kết luận: tập nghĩa vụ đã
     * cố định cho cả lần chạy, và ngữ nghĩa của từng bản khai vẫn bị kiểm riêng.
     *
     * NỘI DUNG = mọi thứ còn lại (tình thái không được phép, chủ ngữ không có
     * trong ô, nguồn nghĩa vụ trôi dạt). Mặc định vẫn là NỘI DUNG — danh sách
     * dưới đây liệt kê cái ĐƯỢC tha, nên một quy tắc mới thêm vào sẽ tự động rơi
     * vào phía nghiêm ngặt.
     */
    // Khẳng định bị cấm THẮNG mọi lớp kỹ thuật — như ở lượt 1.
    failureClass: emittedScan.causalViolations + emittedScan.ctrViolations > 0
      ? 'UNSUPPORTED_CLAIM'
      : passed
      ? 'NONE'
      : blockers.some((i) => i.rule === 'schema')
        ? 'SCHEMA_MISMATCH'
        : blockers.every((i) => (DECLARATION_TECHNICAL_RULES as readonly string[]).includes(i.rule))
          ? 'MISSING_REQUIRED_FIELD'
          : 'UNSUPPORTED_CLAIM',
    repairErrors,
  }
}
