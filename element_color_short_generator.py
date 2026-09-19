"""Sinh nội dung Short "Màu sắc/vật phẩm hợp mệnh Ngũ Hành" cho kênh Phong
Thuỷ -- CÙNG kiến trúc "sự thật tính toán được", dùng chung
short_judge_panel_engine.py. KHÁC lich_hoang_dao_generator.py/
twelve_gods_short_generator.py/zodiac_short_generator.py: nội dung này
KHÔNG gắn với 1 ngày cụ thể (evergreen) -- xoay vòng qua 5 mệnh
(Kim/Mộc/Thuỷ/Hoả/Thổ), mỗi lần gọi ra 1 mệnh tiếp theo trong vòng.

Căn cứ: màu theo mệnh + vòng tương sinh -- ĐÃ đối chiếu WebSearch nhiều
nguồn độc lập trong phiên làm việc (giống cách đã xác nhận cho sơ đồ Ngũ
Hành). Không tự bịa "màu hợp mệnh" theo cảm tính."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from short_judge_panel_engine import generate_verified_script  # noqa: E402
import rotation_state  # noqa: E402
import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.GROUNDED_DATA  # xem content_categories.py -- evergreen (không gắn ngày) nhưng vẫn là dữ liệu tính toán được (màu theo mệnh đã kiểm chứng), không phải diễn giải
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
ROTATION_STATE_PATH = Path(__file__).parent / "chunks_cache" / "element_color_rotation_state.json"

# Đã đối chiếu WebSearch nhiều nguồn độc lập (unica.vn, deco-crystal.com,
# toagroup.com.vn...) -- xem phiên làm việc.
ELEMENT_COLORS = {
    "Kim": "trắng, bạc, ánh kim",
    "Mộc": "xanh lá cây",
    "Thuỷ": "đen, xanh dương đậm",
    "Hoả": "đỏ, hồng, tím",
    "Thổ": "nâu, cam, vàng đất",
}
# Vòng tương sinh (đã kiểm chứng, xem generate_symbol_assets.py): mỗi mệnh
# được "mẹ" của nó (hành sinh ra nó) hỗ trợ/nuôi dưỡng -- Mộc sinh Hoả,
# Hoả sinh Thổ, Thổ sinh Kim, Kim sinh Thuỷ, Thuỷ sinh Mộc.
GENERATING_ELEMENT = {"Hoả": "Mộc", "Thổ": "Hoả", "Kim": "Thổ", "Thuỷ": "Kim", "Mộc": "Thuỷ"}
# Vòng tương khắc: hành nào KHẮC mệnh này (nên tránh lạm dụng màu tương ứng).
OVERCOMING_ELEMENT = {"Thổ": "Mộc", "Thuỷ": "Thổ", "Hoả": "Thuỷ", "Kim": "Hoả", "Mộc": "Kim"}
ROTATION_ORDER = ["Kim", "Mộc", "Thuỷ", "Hoả", "Thổ"]


def compute_element_facts(element: str | None = None) -> dict:
    element = element or rotation_state.peek_next(ROTATION_STATE_PATH, ROTATION_ORDER, "last_element")
    generating = GENERATING_ELEMENT[element]
    overcoming = OVERCOMING_ELEMENT[element]
    return {
        "element": element,
        "element_colors": ELEMENT_COLORS[element],
        "generating_element": generating,
        "generating_element_colors": ELEMENT_COLORS[generating],
        "overcoming_element": overcoming,
        "overcoming_element_colors": ELEMENT_COLORS[overcoming],
    }


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form phong thuỷ tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về MÀU SẮC/VẬT PHẨM (ví, hình nền điện thoại, trang phục) hợp cho người khuyết mệnh {facts_json_element}, dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

(element: mệnh đang thiếu. element_colors: màu của chính mệnh đó -- dùng trực tiếp để bổ khuyết. generating_element/generating_element_colors: mệnh "sinh" ra mệnh đang thiếu -- màu này hỗ trợ gián tiếp. overcoming_element/overcoming_element_colors: mệnh khắc chế mệnh đang thiếu -- nên tránh lạm dụng màu này.)

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI THẲNG VẤN ĐỀ: mở bằng "Nếu bạn thấy công việc/cuộc sống trục trặc, có thể bạn đang khuyết mệnh {facts_json_element}" rồi vào giải pháp màu sắc.
B. GIẢI PHÁP TRỰC TIẾP: mở bằng "Người mệnh khuyết {facts_json_element}, đây là màu ví/hình nền cứu mệnh cho bạn" rồi liệt kê màu.
C. CẢNH BÁO MÀU NÊN TRÁNH: mở bằng màu nên tránh (overcoming_element_colors) trước, tạo bất ngờ, rồi mới nói màu nên dùng.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ dùng đúng màu sắc/tên mệnh có trong dữ liệu trên -- KHÔNG bịa thêm màu, KHÔNG bịa thêm vật phẩm cụ thể ngoài ví/hình nền điện thoại/trang phục (nhóm vật phẩm chung, không cần chính xác tuyệt đối).
- KHÔNG cam kết kết quả chắc chắn (không nói "chắc chắn giàu có/may mắn"), chỉ nói ở mức "được xem là hỗ trợ/cân bằng".
- ĐÁNH DẤU tên mệnh và màu sắc quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
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

BƯỚC 1 -- FACT-CHECK (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ dùng đúng màu/tên mệnh có trong dữ liệu, không thêm màu khác, (b) không cam kết kết quả chắc chắn dưới bất kỳ hình thức nào -- không chỉ "giàu có/may mắn tuyệt đối" mà cả các khẳng định nhân quả không dè dặt (vd "gây khắc chế và làm năng lượng mất cân bằng" nói như sự thật tuyệt đối), (c) không bịa vật phẩm cụ thể ngoài ví/hình nền/trang phục, (d) có trình bày mối quan hệ Ngũ Hành (khắc chế, tương sinh, bổ trợ...) như SỰ THẬT KHÁCH QUAN, không có framing dè dặt ("theo quan niệm Ngũ Hành", "được xem là", "có thể") không? Đây là điểm ĐỘC LẬP với (b) -- 1 câu có thể không "cam kết chắc chắn" (không dùng từ tuyệt đối) nhưng VẪN vi phạm nếu trình bày quan hệ Ngũ Hành như sự thật khoa học. Có thì FAIL. Vi phạm bất kỳ điểm nào → LOẠI.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua fact-check.

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def write_short_bundle_file(element: str, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Không gắn ngày (evergreen) -- đặt tên theo mệnh, đủ để không trùng
    # trong 1 vòng xoay 5 mệnh.
    out_path = OUTPUT_DIR / f"MENH_{element}_MauSacHopMenh_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--element", default=None, choices=list(ELEMENT_COLORS), help="Kim/Mộc/Thuỷ/Hoả/Thổ, mặc định lấy tiếp theo trong vòng xoay")
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    facts = compute_element_facts(args.element)
    print(f"Dữ liệu mệnh {facts['element']}:", json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

    prompt_with_element = _GENERATE_CANDIDATES_PROMPT.replace("{facts_json_element}", facts["element"])
    result = generate_verified_script(facts, prompt_with_element, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- fact-check chưa PASS, cần người xem lại (mệnh vẫn giữ nguyên vị trí trong vòng xoay để thử lại).", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(facts["element"], result["script"])
    if args.element is None:
        # Chỉ commit vòng xoay khi mệnh được TỰ ĐỘNG chọn (không phải người
        # dùng ép qua --element) -- và CHỈ SAU KHI đã PASS thật, xem
        # rotation_state.py.
        rotation_state.commit(ROTATION_STATE_PATH, facts["element"], "last_element")
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
