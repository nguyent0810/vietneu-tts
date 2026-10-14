"""Sinh nội dung Short "Mệnh nào có tài lộc/cần thận trọng hôm nay" cho
kênh Phong Thuỷ -- CÙNG kiến trúc "sự thật tính toán được", dùng chung
short_judge_panel_engine.py. KHÁC 12 vị Thần/con giáp (đã dừng dùng ở các
khung giờ khác 6h) -- nội dung này KHÔNG nhắc Hoàng Đạo/Hắc Đạo, chỉ xoay
quanh Ngũ Hành thuần tuý (mệnh nào được tiếp sức, mệnh nào cần cẩn trọng
hôm nay theo vòng tương sinh/tương khắc).

Căn cứ: elements.day.can (mệnh Ngũ Hành của Can ngày hôm nay, vnlunar) +
vòng tương sinh/tương khắc ĐÃ kiểm chứng WebSearch nhiều nguồn (xem
element_color_short_generator.py, generate_symbol_assets.py).

BUG THẬT phát hiện trước khi build: vnlunar viết "Thủy"/"Hỏa" (tổ hợp
Unicode KHÁC "Thuỷ"/"Hoả" đã dùng trong element_color_short_generator.py --
nhìn giống hệt nhưng so sánh chuỗi KHÔNG khớp, gây KeyError nếu tra thẳng).
Phải chuẩn hoá qua _normalize_element() trước khi tra cứu."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from element_color_short_generator import ELEMENT_COLORS, GENERATING_ELEMENT, OVERCOMING_ELEMENT  # noqa: E402
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

# vnlunar spell "Thủy"/"Hỏa" bằng tổ hợp Unicode khác "Thuỷ"/"Hoả" đã dùng
# trong element_color_short_generator.py (xem docstring) -- chuẩn hoá về
# đúng spelling dùng chung trong dự án trước khi tra ELEMENT_COLORS/
# GENERATING_ELEMENT/OVERCOMING_ELEMENT (đều khoá theo "Thuỷ"/"Hoả").
_VNLUNAR_ELEMENT_NORMALIZE = {"Thủy": "Thuỷ", "Hỏa": "Hoả"}


def _normalize_element(vnlunar_element: str) -> str:
    return _VNLUNAR_ELEMENT_NORMALIZE.get(vnlunar_element, vnlunar_element)


# Sinh ra (X sinh ra Y -- Y được tiếp sức) và Khắc ra (X khắc Y -- Y cần
# thận trọng hơn) là chiều NGƯỢC của GENERATING_ELEMENT/OVERCOMING_ELEMENT
# (vốn khoá theo "được sinh bởi ai"/"bị khắc bởi ai") -- cùng 1 vòng, chỉ
# đảo chiều đọc, không phải bảng tra mới.
_GENERATES = {parent: child for child, parent in GENERATING_ELEMENT.items()}
_OVERCOMES = {other: element for element, other in OVERCOMING_ELEMENT.items()}


def compute_element_luck_facts(target_date: date) -> dict:
    info = vnlunar.get_full_info(target_date.day, target_date.month, target_date.year)
    day_element = _normalize_element(info["elements"]["day"]["can"])
    boosted = _GENERATES[day_element]
    cautioned = _OVERCOMES[day_element]
    return {
        # BUG THẬT phát hiện qua feedback người dùng (xem phiên làm việc):
        # solar_date/day_of_week TRƯỚC ĐÂY có trong facts nhưng KHÔNG được
        # prompt nào tham chiếu tên field cụ thể -- agy vẫn tự nhét vào
        # kịch bản vì field có sẵn trong facts_json (CÙNG BUG PATTERN với
        # day_type đã sửa ở twelve_gods_short_generator.py/zodiac_short_
        # generator.py trước đó), tạo câu dẫn ngày dài dòng kém hấp dẫn
        # (vd "Ngày Thứ bảy 25/07/2026 có Can Chi Canh Tý..."). Bỏ hẳn 2
        # field này -- day_can_chi đã đủ neo "hôm nay" 1 cách sinh động,
        # không cần thêm ngày dương lịch/thứ đọc thành lời.
        "day_can_chi": info["can_chi"]["day"],
        "day_element": day_element,
        "boosted_element": boosted,
        "boosted_element_colors": ELEMENT_COLORS[boosted],
        "cautioned_element": cautioned,
        "cautioned_element_colors": ELEMENT_COLORS[cautioned],
    }


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form phong thuỷ tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về MỆNH NGŨ HÀNH nào được tiếp sức/cần thận trọng hôm nay, dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

(day_can_chi: tổ hợp Can+Chi của ngày, vd "Canh Tý" -- gồm 2 phần RIÊNG BIỆT, mỗi phần 1 hành KHÁC NHAU, KHÔNG phải cả tổ hợp cùng chung 1 hành. day_element: hành của RIÊNG Thiên Can (nửa ĐẦU của day_can_chi) -- đây là hành dùng để tính tương sinh/khắc trong bài này. boosted_element: mệnh được ngày hôm nay TIẾP SỨC theo vòng tương sinh -- người mệnh này may mắn hơn. cautioned_element: mệnh bị ngày hôm nay KHẮC CHẾ -- người mệnh này nên cẩn trọng hơn.)

QUAN TRỌNG -- LỖI THẬT ĐÃ GẶP, TRÁNH LẶP LẠI: TUYỆT ĐỐI KHÔNG viết kiểu "Ngày [day_can_chi] thuộc hành [day_element]" (vd "Ngày Canh Tý thuộc hành Kim") -- đây là SAI, vì day_element CHỈ là hành của riêng Thiên Can (nửa đầu day_can_chi), Địa Chi (nửa sau) luôn có hành RIÊNG khác (vd Tý thuộc Thuỷ, không phải Kim). Nếu nhắc day_can_chi, chỉ dùng để XƯNG DANH ngày (vd "Hôm nay, ngày Canh Tý,..."), KHÔNG được nối trực tiếp với "thuộc hành X". Muốn nhắc tới hành, hãy nói rõ "Thiên Can của ngày hôm nay thuộc hành [day_element]" hoặc chỉ dùng "hôm nay" + [day_element] mà không nhắc day_can_chi trong cùng câu.

QUAN TRỌNG: TUYỆT ĐỐI KHÔNG nhắc tới "Hoàng Đạo", "Hắc Đạo", hay bất kỳ khái niệm ngày tốt/xấu tổng thể nào -- nội dung này CHỈ xoay quanh Ngũ Hành, độc lập hoàn toàn với hệ Hoàng Đạo/Hắc Đạo.

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI THẲNG MỆNH MAY MẮN: mở bằng "Mệnh [boosted_element] hôm nay..." nêu ngay tin vui.
B. SO SÁNH 2 MỆNH: mở bằng đối lập giữa mệnh được tiếp sức và mệnh cần thận trọng, tạo tò mò "mình thuộc mệnh nào".
C. CÂU HỎI TRỰC TIẾP: "Hôm nay mệnh nào may mắn nhất?" rồi trả lời.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ dùng đúng tên mệnh/màu sắc có trong dữ liệu -- KHÔNG bịa thêm mệnh khác, KHÔNG bịa lý do cụ thể (tài lộc bao nhiêu, sự kiện gì) ngoài khung "được tiếp sức/cần thận trọng theo Ngũ Hành" chung chung.
- KHÔNG cam kết kết quả chắc chắn.
- ĐÁNH DẤU tên mệnh quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = """Bạn là giám khảo 2 vai trò: (1) fact-checker NGHIÊM NGẶT, (2) chuyên gia short-form phong thuỷ. Chấm 3 phương án dưới đây.

=== DỮ LIỆU GỐC (nguồn sự thật duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi fact-check.

BƯỚC 1 -- FACT-CHECK (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ dùng đúng tên mệnh/màu trong dữ liệu, (b) không bịa lý do/sự kiện cụ thể, (c) không cam kết kết quả chắc chắn, (d) TUYỆT ĐỐI không nhắc "Hoàng Đạo"/"Hắc Đạo"/ngày tốt xấu tổng thể, (e) LỖI THẬT ĐÃ GẶP -- có câu nào viết kiểu "Ngày [day_can_chi] thuộc hành [day_element]" không (vd "Canh Tý thuộc hành Kim")? Đây là SAI vì day_element chỉ là hành của riêng Thiên Can, không phải cả tổ hợp Can Chi -- có thì FAIL ngay, (f) có trình bày mối quan hệ mệnh/ngũ hành/can chi như SỰ THẬT KHÁCH QUAN mà không có framing dè dặt phù hợp ("theo quan niệm", "được xem là") không? Đây là điểm ĐỘC LẬP với (c) -- 1 câu có thể pass (c) (không dùng từ chắc chắn/tuyệt đối) nhưng vẫn FAIL ở đây nếu thiếu framing dè dặt cho 1 nhận định dựa trên niềm tin truyền thống. Vi phạm bất kỳ điểm nào → LOẠI.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua fact-check.

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def write_short_bundle_file(target_date: date, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ep_prefix = f"MENHNGAY{target_date.strftime('%Y%m%d')}"
    out_path = OUTPUT_DIR / f"{ep_prefix}_MenhTaiLoc_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, mặc định hôm nay")
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date.today()
    facts = compute_element_luck_facts(target_date)
    print(f"Dữ liệu mệnh tài lộc {target_date.isoformat()}:", json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

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
