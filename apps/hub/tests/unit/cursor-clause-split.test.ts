import { describe, expect, it } from 'vitest'

import { clausesOf } from '@/lib/cursor/validate'

/**
 * U1 — TÁCH MỆNH ĐỀ và vai trò của DẤU PHẨY.
 *
 * U1 đếm "một ô có mấy phát biểu chạm chỉ số nhạy cảm". Phép đếm đó chỉ đúng khi
 * bộ tách mệnh đề tách đúng chỗ. Dấu phẩy là dấu nguy hiểm nhất trong tiếng Việt
 * vì nó gánh ÍT NHẤT ba vai khác nhau:
 *
 *   1. ngăn cách MỆNH ĐỀ    — "CTR thấp, impressions cao"          -> tách ĐÚNG
 *   2. ngăn cách MỤC LIỆT KÊ — "thumbnail, tiêu đề, hay packaging"  -> tách SAI
 *   3. ngăn cách TRẠNG NGỮ ĐỨNG TRƯỚC — "Khi có CTR, so sánh…"      -> tách SAI
 *
 * Chỉ vai (1) là ranh giới mệnh đề. Hai vai kia bị đếm thành nhiều phát biểu và
 * sinh ra `multiple_assertions_in_source_unit` OAN.
 *
 * BẰNG CHỨNG, không phải suy đoán: quét 517 ô THẬT lấy từ 74 lần chạy Cursor đã
 * lưu trong database. Dấu phẩy làm đổi kết quả U1 ở 25 ô, và cả 25 đều rơi vào
 * vai (2) hoặc (3) — KHÔNG ô nào là hai phát biểu thật. Ba nhóm quan sát được:
 *
 *   A. liệt kê có liên từ  (15 ô) "…thumbnail, tiêu đề, hay packaging…"
 *   B. trạng ngữ đứng trước (5 ô) "Khi có impression_ctr, so sánh CTR…"
 *   C. liệt kê TÂN NGỮ      (4 ô) "khôi phục impressions, impression_ctr và chuỗi ngày…"
 *
 * Bản sửa nhắm A và B. C được ghi lại là GIỚI HẠN CÒN LẠI ở cuối tệp này, không
 * sửa — xem lý do ở đó.
 *
 * KHÔNG bỏ tách theo dấu phẩy. Nhóm "PHẢI VẪN TÁCH" bên dưới là hàng rào giữ cho
 * bản sửa không biến thành "bỏ dấu phẩy cho xong".
 */

/** Bộ dò chỉ số nhạy cảm, giữ đồng bộ với SENSITIVE_MENTION của validator. */
const SENS =
  /(?:impressions?|lượt hiển thị|impression_ctr|\bctr\b|click-?through|tỉ lệ nhấp|tỷ lệ nhấp|tỷ lệ click|tỉ lệ click|thumbnail|hình thu nhỏ|ảnh đại diện|packaging|đóng gói)/iu

/** Số mệnh đề CHẠM chỉ số nhạy cảm — chính là con số U1 dùng để chặn. */
const sensitiveClauses = (text: string): string[] => clausesOf(text).filter((c) => SENS.test(c))
const count = (text: string): number => sensitiveClauses(text).length

describe('U1 — dấu phẩy KHÔNG được tách: liệt kê danh từ', () => {
  it('liệt kê ba danh từ nối bằng "hoặc" là MỘT phát biểu', () => {
    const t = 'Không kết luận hiệu quả thumbnail, tiêu đề hút click, hoặc packaging.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('liệt kê nối bằng "hay" là MỘT phát biểu', () => {
    const t = 'Không kết luận hiệu quả thumbnail, khả năng hút click của tiêu đề, hay packaging.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('liệt kê nối bằng "và" ở mục cuối là MỘT phát biểu', () => {
    const t = 'Chặn mọi kết luận về tiếp cận, CTR, thumbnail và packaging.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })
})

describe('U1 — nhiều chỉ số trong MỘT liệt kê nhưng chỉ MỘT kết luận', () => {
  it('ca THẬT của thăm dò #3: bốn chỉ số, một câu không-kết-luận', () => {
    // Ô này là một trong hai lỗi U còn lại của lần thăm dò thứ ba.
    const t =
      'Không kết luận hiệu quả thumbnail, tiêu đề hút click, hoặc packaging vì impressions và impression_ctr độ phủ 0%.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('liệt kê chỉ số ở vế lý do cũng không nhân đôi phát biểu', () => {
    const t = 'Không kết luận packaging vì impressions, impression_ctr và độ phủ ngày đều thiếu.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })
})

describe('U1 — trạng ngữ ĐỨNG TRƯỚC ngăn bằng dấu phẩy', () => {
  it('ca THẬT của thăm dò #3: "Khi có X, so sánh X…"', () => {
    // Lỗi U thứ hai của lần thăm dò thứ ba. Một hành động, một điều kiện đứng
    // trước — không phải hai phát biểu.
    const t = 'Khi có impression_ctr, so sánh CTR nhóm high-retention/low-views với nhóm median-retention.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('"Nếu vẫn thiếu X, mọi suy luận Y giữ trạng thái chưa kiểm chứng"', () => {
    const t = 'Nếu vẫn thiếu impressions, mọi suy luận packaging giữ status chưa kiểm chứng.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('DẤU HAI CHẤM vẫn tách, kể cả sau trạng ngữ đứng trước', () => {
    // Miễn trừ CHỈ áp cho dấu phẩy. Bản thiết kế đã chốt rằng
    // "Khi có impressions/CTR: so sánh CTR và impressions…" PHẢI bị tách —
    // và ca đó là ví dụ mẫu của quy tắc một-ô-một-phát-biểu.
    const t = 'Khi có impressions/CTR: so sánh CTR và impressions của nhóm high-retention/low-views'
    expect(count(t), JSON.stringify(clausesOf(t))).toBeGreaterThan(1)
  })
})

describe('U1 — PHẢI VẪN TÁCH: hai khẳng định nhạy cảm thật', () => {
  it('hai cặp chủ ngữ/phán xét riêng, ngăn bằng dấu phẩy', () => {
    const t = 'CTR thấp, impressions cao'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('hai phán xét khác chiều trên hai chỉ số khác nhau', () => {
    const t = 'thumbnail kém hiệu quả, packaging đã cải thiện rõ'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('dấu phẩy trước liên từ ĐỐI LẬP vẫn tách', () => {
    const t = 'CTR chưa đo được, nhưng thumbnail đã đổi hai lần'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('dấu phẩy trước liên từ NHÂN QUẢ vẫn tách', () => {
    const t = 'impressions còn thiếu, do đó packaging chưa đánh giá được'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('"tuy nhiên" sau dấu phẩy vẫn tách', () => {
    const t = 'Không có dữ liệu CTR, tuy nhiên thumbnail hiện tại kém'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('liên từ ĐỐI LẬP không bị nhầm thành liên từ LIỆT KÊ', () => {
    // "nhưng"/"còn" mở một mệnh đề mới; "và"/"hay"/"hoặc" nối các mục. Bản sửa
    // chỉ được nhận nhóm sau là liệt kê.
    const t = 'Không kết luận thumbnail, tiêu đề, hay packaging, nhưng CTR vẫn phải đo lại'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })
})

describe('U1 — mục liệt kê tự chứa từ TÌNH THÁI hoặc PHÂN CỰC', () => {
  it('mục liệt kê mang "hiệu quả", "khả năng" vẫn là một liệt kê', () => {
    // Không được dùng "có từ phán xét trong mục" làm dấu hiệu mệnh đề mới: các
    // mục liệt kê thật đều mang những từ đó.
    const t =
      'Không kết luận hiệu quả thumbnail, khả năng hút click của tiêu đề, hay độ hấp dẫn packaging.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('mục liệt kê mang từ PHỦ ĐỊNH vẫn là một liệt kê', () => {
    const t = 'Chưa đánh giá được thumbnail, chưa đo được CTR, và chưa bật impressions.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })
})

describe('U1 — số kiểu Việt Nam không được cắt câu', () => {
  it('dấu chấm PHÂN CÁCH NGHÌN không phải kết câu', () => {
    const t = 'impressions đạt 1.000 lượt trong kỳ'
    expect(clausesOf(t), JSON.stringify(clausesOf(t))).toHaveLength(1)
  })

  it('dấu chấm THẬP PHÂN không phải kết câu', () => {
    const t = 'Điểm tin cậy gói 0.7262 nhưng impressions vẫn phủ 0%'
    // "nhưng" là ranh giới thật; "0.7262" thì không.
    expect(clausesOf(t).some((c) => c.includes('0.7262')), JSON.stringify(clausesOf(t))).toBe(true)
  })

  it('dấu phẩy THẬP PHÂN kiểu Việt không phải ranh giới mệnh đề', () => {
    const t = 'CTR 1,5% vẫn nằm trong khoảng nhiễu'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('số có phân cách KHÔNG che mất một khẳng định thật đứng sau', () => {
    const t = 'impressions đạt 1.000 lượt, CTR vẫn chưa đo'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })
})

describe('U1 — dấu phẩy ĐỒNG VỊ và cụm CHÊM', () => {
  it('cụm chêm trong NGOẶC ĐƠN không tách câu', () => {
    const t = 'impressions (chỉ số hiển thị, chưa bật đo) hiện có độ phủ 0%'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('ngoặc đơn chứa dấu chấm cũng không tách câu', () => {
    const t = 'Ưu tiên thu thập impressions (xem mục 2.1 của gói) trước mọi quyết định'
    expect(clausesOf(t), JSON.stringify(clausesOf(t))).toHaveLength(1)
  })

  /**
   * GIỚI HẠN ĐÃ BIẾT — đồng vị ngăn bằng dấu phẩy, KHÔNG có liên từ.
   *
   * "impressions, chỉ số đo lượt hiển thị, hiện phủ 0%" là một phát biểu với một
   * cụm đồng vị. Không có liên từ liệt kê và không có trạng ngữ đứng trước, nên
   * cả hai quy tắc của bản sửa đều không nhận ra nó, và U1 đếm thành hai.
   *
   * KHÔNG sửa ở vòng này, có chủ ý: phân biệt đồng vị với hai mệnh đề thật cần
   * phân tích cú pháp, còn mọi dấu hiệu bề mặt rẻ tiền đều sẽ nuốt luôn ca
   * "CTR thấp, impressions cao" ở trên. Ca này KHÔNG xuất hiện trong 517 ô thật
   * đã quét. Test ghi lại hành vi HIỆN TẠI để lần sau đổi thì thấy ngay.
   */
  it('GIỚI HẠN: đồng vị không liên từ vẫn bị đếm thành hai', () => {
    const t = 'impressions, chỉ số đo lượt hiển thị, hiện phủ 0%'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })
})

/**
 * Rà soát ĐỐI KHÁNG của Codex trên chính bản sửa này.
 *
 * Bảy ca được dựng ra để phá phép gộp mới; SÁU ca là thật và đã sửa, MỘT ca sai.
 * Giữ cả bảy làm test: ca sai cũng có giá trị, nó khoá lại hành vi đúng để lần
 * sau không ai "sửa" nhầm theo một báo cáo sai.
 */
describe('U1 — ca đối kháng do Codex dựng trên bản sửa dấu phẩy', () => {
  it('C1a: khẳng định ĐỊNH LƯỢNG sau dấu phẩy không phải mục liệt kê', () => {
    const t = 'CTR đạt 8%, impressions và lượt xem đạt 10.000'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('C1b: mảnh mở đầu bằng "và" nhưng CÓ phán xét thì vẫn tách', () => {
    const t = 'CTR thấp, và impressions cao'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('C2: trạng ngữ đứng trước chỉ gộp dấu phẩy THỨ NHẤT', () => {
    const t = 'Nếu CTR dưới 2%, thumbnail đang dùng bản A, impressions đạt 10.000'
    expect(clausesOf(t), JSON.stringify(clausesOf(t))).toEqual([
      'Nếu CTR dưới 2%, thumbnail đang dùng bản A',
      'impressions đạt 10.000',
    ])
  })

  it('C3: BÁO SAI — dấu chấm rồi khoảng trắng rồi chữ số VẪN kết câu', () => {
    // Codex cho rằng `\.(?!\d)` nuốt ranh giới này. Không đúng: ký tự ngay sau
    // dấu chấm là khoảng trắng, nên lookahead vẫn cho qua.
    const t = 'CTR thấp. 2025 impressions cao.'
    expect(clausesOf(t), JSON.stringify(clausesOf(t))).toEqual(['CTR thấp', '2025 impressions cao'])
  })

  it('C4: ngoặc LỒNG NHAU được che hết', () => {
    const t = 'CTR (ghi chú (a, b), tiếp) thấp'
    expect(clausesOf(t), JSON.stringify(clausesOf(t))).toHaveLength(1)
  })

  it('C5: chuỗi canh có sẵn trong văn bản KHÔNG bị xoá mất', () => {
    const t = `CTR  0 thấp`
    expect(clausesOf(t).join(''), JSON.stringify(clausesOf(t))).toContain('0')
  })

  it('C6: S4 vẫn thấy được phép đảo chiều của CTR', () => {
    // Mảnh sau có "thấp" nên không bị coi là mục liệt kê; nhờ đó mệnh đề chứa
    // CTR đứng riêng và phép so phân cực nhìn đúng chỗ.
    const t = 'impressions thấp, và CTR không thấp'
    const clauses = clausesOf(t)
    expect(clauses, JSON.stringify(clauses)).toHaveLength(2)
    expect(clauses[1]).toContain('không thấp')
  })

  /**
   * GIỚI HẠN ĐÃ BIẾT — "hay" còn nghĩa "thường xuyên".
   *
   * "impressions hay thay đổi" dùng "hay" như trạng từ, không như liên từ liệt
   * kê, nên bị gộp nhầm. Phân biệt hai nghĩa cần biết từ đứng sau là danh từ hay
   * động từ — tức cần một từ điển từ loại, thứ tầng này cố ý không có. Ca không
   * xuất hiện trong 517 ô thật đã quét.
   */
  it('GIỚI HẠN: "hay" nghĩa "thường xuyên" bị hiểu thành liên từ liệt kê', () => {
    const t = 'CTR thấp, impressions hay thay đổi'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })
})

/**
 * Nhóm C — liệt kê TÂN NGỮ sau một động từ duy nhất.
 *
 * "Ưu tiên khôi phục/bổ sung impressions, impression_ctr và chuỗi ngày cấp kênh"
 * có MỘT động từ và một danh sách tân ngữ. Mảnh sau dấu phẩy KHÔNG mở đầu bằng
 * liên từ, nên quy tắc "mở đầu bằng liên từ" không thấy nó — nhưng quy tắc thứ
 * hai thì có: mảnh đó CHỨA "và" và KHÔNG mang dấu hiệu phán xét nào.
 *
 * Chính điều kiện "không mang phán xét" là thứ giữ cho quy tắc này không nuốt
 * luôn ca hai phát biểu thật; ca đó nằm ngay dưới đây làm hàng rào.
 */
describe('U1 — liệt kê TÂN NGỮ sau một động từ', () => {
  it('"khôi phục A, B và C" là MỘT phát biểu', () => {
    const t = 'Ưu tiên khôi phục/bổ sung impressions, impression_ctr và chuỗi ngày cấp kênh.'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(1)
  })

  it('HÀNG RÀO: mảnh sau có PHÁN XÉT riêng thì vẫn tách, dù có "và"', () => {
    // Khác ca trên đúng một chỗ: "đều cao" là phán xét, nên mảnh sau là một phát
    // biểu chứ không phải mục liệt kê.
    const t = 'CTR thấp, impressions và thumbnail đều cao'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })

  it('HÀNG RÀO: "tăng/giảm" cũng chặn phép gộp', () => {
    const t = 'CTR chưa đo, impressions và thumbnail cùng giảm'
    expect(count(t), JSON.stringify(clausesOf(t))).toBe(2)
  })
})
