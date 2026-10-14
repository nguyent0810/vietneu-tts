"""Sinh nội dung Short "Con giáp cần cẩn thận trong tháng âm lịch này" cho
kênh Phong Thuỷ -- CÙNG kiến trúc "sự thật tính toán được", dùng chung
short_judge_panel_engine.py. KHÁC zodiac_short_generator.py (theo NGÀY) --
đây là góc nhìn THEO THÁNG âm lịch, không nhắc Hoàng Đạo/Hắc Đạo.

Căn cứ: can_chi.month (Can Chi của THÁNG âm lịch, vnlunar) + bảng Tứ Hành
Xung (4 nhóm x 4 chi xung nhau) -- ĐÃ đối chiếu WebSearch nhiều nguồn độc
lập (mytour.vn, horos.vn...): Thìn-Tuất-Sửu-Mùi, Dần-Thân-Tỵ-Hợi,
Tý-Ngọ-Mão-Dậu (xem phiên làm việc, cùng lần tra cứu Tam Hợp cho
zodiac_short_generator.py)."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zodiac_short_generator import CHI_TO_ANIMAL  # noqa: E402
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
TU_HANH_XUNG_GROUPS = [
    {"Thìn", "Tuất", "Sửu", "Mùi"},
    {"Dần", "Thân", "Tỵ", "Hợi"},
    {"Tý", "Ngọ", "Mão", "Dậu"},
]


def _xung_group_for(chi: str) -> set[str]:
    for group in TU_HANH_XUNG_GROUPS:
        if chi in group:
            return group
    raise ValueError(f"Chi không hợp lệ: {chi}")


def compute_month_zodiac_facts(target_date: date) -> dict:
    info = vnlunar.get_full_info(target_date.day, target_date.month, target_date.year)
    month_can_chi = info["can_chi"]["month"]
    month_chi = month_can_chi.split()[-1]  # "Ất Mùi" -> "Mùi"
    xung_group = _xung_group_for(month_chi)
    cautioned_chis = sorted(xung_group - {month_chi})
    return {
        "lunar_month_number": info["lunar"]["month"],
        "lunar_month_name": info["lunar"]["month_name"],
        "month_can_chi": month_can_chi,
        "month_chi": month_chi,
        "month_animal": CHI_TO_ANIMAL[month_chi],
        "cautioned_animals": [{"chi": c, "animal": CHI_TO_ANIMAL[c]} for c in cautioned_chis],
    }


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form tử vi/12 con giáp tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về CÁC CON GIÁP CẦN CẨN TRỌNG trong THÁNG ÂM LỊCH này (không phải hôm nay), dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

(month_chi/month_animal: Chi và con giáp của chính tháng âm lịch này. cautioned_animals: 3 con giáp thuộc nhóm Tứ Hành Xung với tháng này -- cần cẩn trọng hơn trong THÁNG này, không phải riêng hôm nay.)

QUAN TRỌNG: TUYỆT ĐỐI KHÔNG nhắc "Hoàng Đạo"/"Hắc Đạo"/ngày tốt xấu -- đây là góc nhìn THEO THÁNG, độc lập với hệ ngày. Phải nói rõ đây là CẢ THÁNG âm lịch (dùng lunar_month_number/lunar_month_name, vd "tháng 6 âm lịch" hoặc "trong tháng này"), không phải 1 ngày cụ thể.

3 chiến lược hook bắt buộc -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI TÊN CON GIÁP NGAY: mở bằng "3 con giáp [tên]... cần chú ý trong tháng này" nêu thẳng.
B. CẢNH BÁO NHẸ: mở bằng lời nhắc nhẹ nhàng về tháng Tứ Hành Xung, rồi nêu tên các con giáp.
C. CÂU HỎI TRỰC TIẾP: "Tháng này con giáp nào cần cẩn trọng hơn?" rồi trả lời -- ĐƯỢC PHÉP nêu tên ngay ở câu 2, NHƯNG các câu GIỮA sau đó (không tính câu cuối/lời chúc kết) PHẢI mở ra giá trị MỚI thay vì chỉ nhắc lại tên đã nêu. LƯU Ý: KHÔNG bịa lý do cụ thể (đã cấm ở QUY TẮC BẮT BUỘC phía trên) -- ví dụ hợp lệ nằm chắc trong dữ liệu: nêu rõ đây là quan hệ THEO CẢ THÁNG (không phải 1 sự kiện/ngày cụ thể), hoặc đưa lời khuyên chung được giới hạn rõ (bình tĩnh, cẩn trọng hơn trong quyết định, không gán lĩnh vực/hậu quả cụ thể) -- miễn câu đó không chỉ lặp lại đúng 3 cái tên đã nêu.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ nhắc đúng các con giáp trong cautioned_animals -- KHÔNG bịa thêm con giáp khác, KHÔNG bịa lý do cụ thể (sự kiện, tài lộc, sức khoẻ...) ngoài khung "cần cẩn trọng hơn theo Tứ Hành Xung tháng".
- Giọng cảnh báo NHẸ NHÀNG, không doạ dẫm hậu quả cụ thể.
- ĐÁNH DẤU tên con giáp quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
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

BƯỚC 1 -- FACT-CHECK (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ nhắc đúng con giáp trong cautioned_animals, (b) không bịa lý do cụ thể, (c) không doạ dẫm hậu quả, (d) TUYỆT ĐỐI không nhắc "Hoàng Đạo"/"Hắc Đạo", (e) có nói rõ đây là THEO THÁNG (không phải theo ngày) không, (f) (độc lập với check doạ dẫm ở (c)): có dùng ngôn ngữ khẳng định chắc chắn/tuyệt đối cho hậu quả/kết quả không, và có trình bày quan hệ xung khắc/tương hợp theo tháng như sự thật khách quan mà không có framing dè dặt ("theo quan niệm", "được xem là") không? Vi phạm 1 trong 2 → FAIL. Vi phạm bất kỳ điểm nào → LOẠI.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua fact-check.

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def write_short_bundle_file(target_date: date, month_number: int, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ep_prefix = f"CONGIAPTHANG{month_number:02d}"
    out_path = OUTPUT_DIR / f"{ep_prefix}_ConGiapThang_Short.txt"
    n = 1
    while out_path.exists():
        n += 1
        out_path = OUTPUT_DIR / f"{ep_prefix}_ConGiapThang_{n}_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, mặc định hôm nay (chỉ dùng để xác định tháng âm lịch hiện tại)")
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date.today()
    facts = compute_month_zodiac_facts(target_date)
    print(f"Dữ liệu con giáp theo tháng ({target_date.isoformat()}):", json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

    result = generate_verified_script(facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- fact-check chưa PASS, cần người xem lại.", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(target_date, facts["lunar_month_number"], result["script"])
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
