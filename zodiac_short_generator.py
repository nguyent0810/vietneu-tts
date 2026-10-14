"""Sinh nội dung Short "Con giáp hợp/kỵ hôm nay" cho kênh Phong Thuỷ --
CÙNG kiến trúc "sự thật tính toán được" như lich_hoang_dao_generator.py,
dùng chung short_judge_panel_engine.py.

Căn cứ:
- "Kỵ" (tuổi xung): vnlunar.get_full_info()['conflicting_ages'] -- field
  CÓ SẴN trong vnlunar (đã kiểm chứng đối chiếu 2 nguồn độc lập thật cho
  phần lịch âm/giờ hoàng đạo trước đó trong dự án), không phải tự suy diễn.
- "Hợp" (Tam Hợp): vnlunar KHÔNG có field này -- tự tra cứu bảng Tam Hợp cố
  định (4 nhóm x 3 con giáp), đã đối chiếu qua WebSearch nhiều nguồn độc
  lập (mytour.vn, horos.vn, market.vinhomes.vn... đều khớp): Thân-Tý-Thìn
  (Thuỷ cục), Tỵ-Dậu-Sửu (Kim cục), Dần-Ngọ-Tuất (Hoả cục), Hợi-Mão-Mùi
  (Mộc cục) -- xem phiên làm việc. Đây là bảng TRA CỨU CỐ ĐỊNH (giống cách
  đã vẽ sơ đồ Bát Quái/Ngũ Hành), KHÔNG phải suy luận, KHÔNG được agy tự
  tính lại."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from short_judge_panel_engine import generate_verified_script  # noqa: E402

try:
    import vnlunar
except ImportError:
    print("CẦN CÀI: pip install vnlunar", file=sys.stderr)
    raise

import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.GROUNDED_DATA  # xem content_categories.py
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"

# Đã đối chiếu WebSearch nhiều nguồn độc lập -- xem docstring.
TAM_HOP_GROUPS = [
    {"Thân", "Tý", "Thìn"},
    {"Tỵ", "Dậu", "Sửu"},
    {"Dần", "Ngọ", "Tuất"},
    {"Hợi", "Mão", "Mùi"},
]

CHI_TO_ANIMAL = {
    "Tý": "Chuột", "Sửu": "Trâu", "Dần": "Hổ", "Mão": "Mèo", "Thìn": "Rồng", "Tỵ": "Rắn",
    "Ngọ": "Ngựa", "Mùi": "Dê", "Thân": "Khỉ", "Dậu": "Gà", "Tuất": "Chó", "Hợi": "Lợn",
}


def _tam_hop_group_for(chi: str) -> set[str]:
    for group in TAM_HOP_GROUPS:
        if chi in group:
            return group
    raise ValueError(f"Chi không hợp lệ: {chi}")


def compute_zodiac_facts(target_date: date) -> dict:
    info = vnlunar.get_full_info(target_date.day, target_date.month, target_date.year)
    day_chi = info["conflicting_ages"]["day_chi"]
    hop_chis = sorted(_tam_hop_group_for(day_chi))
    # BUG THẬT phát hiện qua phản hồi thật: trước đây có "day_type" và
    # "auspicious_hours" trong facts dù prompt bên dưới KHÔNG hề yêu cầu
    # dùng 2 field này -- agy vẫn tự nhặt vào kịch bản/tiêu đề (vd "Ngày
    # Hắc Đạo 24/07: Con Giáp Nào Vẫn May Mắn?"), kéo nội dung con giáp về
    # khung "ngày hoàng đạo" giống hệt mảng ĐÃ TẠM DỪNG (trùng lặp với hệ
    # thống cũ). Bài học: facts đưa vào prompt phải ĐÚNG-ĐỦ những gì thật
    # sự cần dùng, không thừa field -- thừa field vẫn có thể rò rỉ vào nội
    # dung dù prompt không yêu cầu.
    return {
        # BUG THẬT phát hiện qua phản hồi người dùng vòng sau (xem phiên
        # làm việc): solar_date/day_of_week CÙNG bug pattern với day_type/
        # auspicious_hours ở trên -- không được prompt tham chiếu tên field
        # cụ thể nhưng vẫn rò rỉ vào kịch bản, tạo câu dẫn ngày dài dòng
        # kém hấp dẫn. Bỏ hẳn, day_can_chi đã đủ neo "hôm nay".
        "day_can_chi": info["can_chi"]["day"],
        "hop_animals": [{"chi": c, "animal": CHI_TO_ANIMAL[c]} for c in hop_chis],
        "ky_animal": {"chi": info["conflicting_ages"]["conflict_chi"], "animal": info["conflicting_ages"]["conflict_animal"]},
    }


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form tử vi/12 con giáp tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) nói về CÁC CON GIÁP HỢP/KỴ hôm nay, dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

(hop_animals: nhóm Tam Hợp bao gồm CẢ con giáp của chính ngày hôm nay -- 3 con giáp này hợp nhau, thuận lợi hôm nay. ky_animal: con giáp xung với ngày hôm nay, cần thận trọng.)

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI TÊN CON GIÁP NGAY: mở bằng "3 con giáp [tên]..." nêu thẳng các con giáp may mắn hôm nay, tạo cảm giác hấp dẫn/muốn xem tiếp để biết mình có trong đó không.
B. CẢNH BÁO CON GIÁP KỴ TRƯỚC: mở bằng lời cảnh báo nhẹ cho con giáp xung (ky_animal), rồi chuyển sang tin vui cho nhóm hợp.
C. CÂU HỎI TRỰC TIẾP: mở bằng câu hỏi "Hôm nay con giáp nào may mắn nhất?" rồi trả lời -- ĐƯỢC PHÉP nêu tên ngay ở câu 2 (không bắt buộc giấu tên), NHƯNG các câu GIỮA sau đó (không tính câu cuối/lời chúc kết -- câu đó do quy tắc echo-hook riêng quản) PHẢI mở ra giá trị MỚI thay vì chỉ nhắc lại tên đã nêu dưới dạng khác. LƯU Ý: đổi tên thường sang Can Chi (hoặc ngược lại) mà KHÔNG kèm thêm dữ kiện/quan hệ gì KHÔNG tính là giá trị mới; NHƯNG nêu Can Chi của CHÍNH NGÀY HÔM ĐÓ (dữ kiện mới, khác với chỉ đổi nhãn tên con giáp) thì tính là hợp lệ -- ví dụ hợp lệ khác: nêu con giáp kỵ (ky_animal) để tạo đối lập, hoặc gợi ý chung nên tận dụng ngày này ra sao (trong khung "được xem là/có thể là tín hiệu thuận hoà" đã quy định ở QUY TẮC BẮT BUỘC phía trên, không bịa lý do cụ thể ngoài khung đó).

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ được nhắc đúng các con giáp có trong hop_animals (nhóm hợp) và ky_animal (con giáp kỵ) -- KHÔNG bịa thêm con giáp khác, KHÔNG tự gán lý do/vận may cụ thể (tài lộc, tình duyên...) ngoài khung "hợp/thuận lợi" chung chung.
- LỖI THẬT ĐÃ GẶP -- MỨC ĐỘ CHẮC CHẮN: dữ liệu chỉ xác nhận 3 con giáp THUỘC NHÓM TAM HỢP với ngày hôm nay, KHÔNG chứng minh "vận khí đại cát"/"vô cùng thuận lợi"/"mọi việc suôn sẻ" -- TUYỆT ĐỐI KHÔNG dùng cụm tăng cường mức độ (vô cùng, đại cát, chắc chắn, tuyệt đối...), chỉ nói mức "được xem là/có thể là tín hiệu thuận hoà theo quan niệm dân gian".
- Với ky_animal: giọng cảnh báo NHẸ NHÀNG (nên thận trọng), KHÔNG doạ dẫm hậu quả cụ thể.
- Ngày tháng dương lịch cụ thể chỉ nên xuất hiện SAU câu hook.
- ĐÁNH DẤU TÊN CON GIÁP quan trọng bằng **hai dấu sao** (vd "**Tuổi Thìn**", "**Tuổi Tý**") -- 1-3 cụm mỗi câu.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = """Bạn là giám khảo 2 vai trò: (1) fact-checker NGHIÊM NGẶT, (2) chuyên gia short-form tử vi. Chấm 3 phương án dưới đây.

=== DỮ LIỆU GỐC (nguồn sự thật duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi fact-check.

BƯỚC 1 -- FACT-CHECK (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ nhắc đúng các con giáp trong hop_animals/ky_animal, không thêm con giáp khác, (b) không tự gán lý do/vận may cụ thể (tài lộc, tình duyên, sức khoẻ...) không có trong dữ liệu, (c) với ky_animal không doạ dẫm hậu quả cụ thể, (d) LỖI THẬT ĐÃ GẶP -- có dùng cụm tăng cường mức độ chắc chắn không (vô cùng, đại cát, chắc chắn, tuyệt đối, hứa hẹn...)? Dữ liệu chỉ xác nhận quan hệ Tam Hợp, không chứng minh mức độ thuận lợi cụ thể -- có thì FAIL, (e) có trình bày quan hệ Tam Hợp/Tứ Hành Xung hoặc mức độ hợp/kỵ như SỰ THẬT KHÁCH QUAN mà không có framing dè dặt ("theo quan niệm dân gian", "được xem là") không? Đây là điểm ĐỘC LẬP với (d) -- 1 câu có thể pass (d) (không dùng từ cường điệu) nhưng vẫn FAIL ở đây nếu thiếu framing dè dặt. Vi phạm bất kỳ điểm nào → LOẠI.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua fact-check: câu đầu có đủ hấp dẫn (gọi tên con giáp ngay, tạo tò mò "mình có trong đó không") không?

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def write_short_bundle_file(target_date: date, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ep_prefix = f"CONGIAP{target_date.strftime('%Y%m%d')}"
    out_path = OUTPUT_DIR / f"{ep_prefix}_ConGiap_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, mặc định hôm nay")
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date.today()
    facts = compute_zodiac_facts(target_date)
    print(f"Dữ liệu con giáp {target_date.isoformat()}:", json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

    result = generate_verified_script(facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- fact-check chưa PASS, cần người xem lại.", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(target_date, result["script"])
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
