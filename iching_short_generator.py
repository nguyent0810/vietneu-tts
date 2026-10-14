"""Sinh nội dung Short "Kinh Dịch ứng dụng" cho kênh Phong Thuỷ --
CATEGORY 3 (Traditional Interpretation, xem content_categories.py), KHÁC
HẲN Category 1 (lịch/12 vị Thần/con giáp) -- không có "quẻ chính thức của
hôm nay" (đã tra cứu: gieo quẻ Kinh Dịch thật -- Mai Hoa Dịch Số/Lục Hào --
cần 1 CÂU HỎI cụ thể + công thức riêng, không phải 1 quẻ cố định mọi người
xem cùng ngày đều giống nhau). Vì vậy nội dung này KHÔNG giả vờ có "quẻ của
ngày" -- xoay vòng qua BÁT THUẦN QUÁI (8 quẻ đơn nhân đôi, vd Càn chồng Càn
= Càn Vi Thiên), giới thiệu Ý NGHĨA TRUYỀN THỐNG của quẻ, luôn nói rõ đây
là "1 cách hiểu/ứng dụng truyền thống", không phải dự đoán tương lai người
xem.

Căn cứ: 8 quẻ đơn (Càn/Khôn/Chấn/Tốn/Khảm/Ly/Cấn/Đoài) + ý nghĩa cốt lõi --
ĐÃ kiểm chứng WebSearch nhiều nguồn (cùng lần tra cứu vẽ sơ đồ bát quái,
xem generate_symbol_assets.py::generate_bat_quai()) + xác nhận lại ý
nghĩa cơ bản khi build generator này."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from short_judge_panel_engine import generate_verified_script  # noqa: E402
import rotation_state  # noqa: E402
import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.INTERPRETATION  # xem content_categories.py
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
ROTATION_STATE_PATH = Path(__file__).parent / "chunks_cache" / "iching_rotation_state.json"

# Bát Thuần Quái (8 quẻ đơn nhân đôi) -- đã đối chiếu WebSearch, xem docstring.
BAT_THUAN_QUAI = [
    {"name": "Càn Vi Thiên", "trigram": "Càn (Trời)", "essence": "thuần Dương, mạnh mẽ, khởi đầu, kiên định không ngừng", "keyword": "Sáng Tạo"},
    {"name": "Khôn Vi Địa", "trigram": "Khôn (Đất)", "essence": "thuần Âm, nuôi dưỡng, bao dung, thuận theo tự nhiên", "keyword": "Tiếp Nhận"},
    {"name": "Chấn Vi Lôi", "trigram": "Chấn (Sấm)", "essence": "Dương động, khởi đầu đột ngột, chấn động, thức tỉnh", "keyword": "Khởi Động"},
    {"name": "Tốn Vi Phong", "trigram": "Tốn (Gió)", "essence": "Âm linh hoạt, thấm nhuần từ từ, mềm mỏng nhưng bền bỉ", "keyword": "Thấm Nhuần"},
    {"name": "Khảm Vi Thuỷ", "trigram": "Khảm (Nước)", "essence": "Âm sâu lắng, hiểm trở, kiên trì vượt qua khó khăn", "keyword": "Hiểm Nguy"},
    {"name": "Ly Vi Hoả", "trigram": "Ly (Lửa)", "essence": "Dương sáng rõ, rực rỡ, minh bạch, bám vào điều tốt đẹp", "keyword": "Sáng Rõ"},
    {"name": "Cấn Vi Sơn", "trigram": "Cấn (Núi)", "essence": "Âm tĩnh lặng, dừng lại đúng lúc, giữ vững, trầm ổn", "keyword": "Tĩnh Lặng"},
    {"name": "Đoài Vi Trạch", "trigram": "Đoài (Hồ)", "essence": "Âm dương giao hoà, vui vẻ, cởi mở, giao tiếp hài hoà", "keyword": "Vui Vẻ"},
]
ROTATION_ORDER = [q["name"] for q in BAT_THUAN_QUAI]


def _peek_quai() -> dict:
    name = rotation_state.peek_next(ROTATION_STATE_PATH, ROTATION_ORDER, "last_quai")
    return next(q for q in BAT_THUAN_QUAI if q["name"] == name)


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form Kinh Dịch/triết học phương Đông tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) giới thiệu Ý NGHĨA TRUYỀN THỐNG của quẻ Kinh Dịch sau, dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

QUAN TRỌNG -- ĐÂY LÀ NỘI DUNG DIỄN GIẢI, KHÔNG PHẢI "QUẺ CỦA HÔM NAY": PHẢI nói rõ ràng đây là 1 QUẺ TRONG KINH DỊCH (giới thiệu/khám phá), KHÔNG được ngụ ý đây là "quẻ hôm nay"/"quẻ của bạn"/dự đoán tương lai cụ thể cho người xem. Ví dụ ĐÚNG: "Trong Kinh Dịch, quẻ Càn Vi Thiên tượng trưng cho..." Ví dụ SAI (không được viết): "Hôm nay bạn gieo được quẻ Càn..."

3 chiến lược hook bắt buộc -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI TÊN QUẺ NGAY: mở bằng tên quẻ + hình ảnh mạnh (vd "Càn Vi Thiên -- quẻ của bầu trời không ngừng chuyển động").
B. CÂU HỎI TRIẾT LÝ: mở bằng câu hỏi liên hệ ý nghĩa quẻ với đời sống (vd "Khi nào nên dừng lại đúng lúc?" cho quẻ Cấn).
C. HÌNH ẢNH ẨN DỤ: mở bằng hình ảnh cụ thể của trigram (trời/đất/sấm/gió/nước/lửa/núi/hồ) rồi liên hệ ý nghĩa.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ dùng đúng ý nghĩa/từ khoá có trong dữ liệu (essence, keyword) -- KHÔNG bịa thêm chi tiết lịch sử, KHÔNG bịa hào từ/lời giải quẻ cụ thể không có trong dữ liệu.
- KHÔNG được dự đoán/khẳng định điều gì sẽ xảy ra với người xem -- đây là giới thiệu triết lý, không phải bói toán cho ai cả.
- ĐÁNH DẤU tên quẻ/từ khoá quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
- MỖI câu có nội dung diễn giải/gán ý nghĩa vẫn cần framing truyền thống riêng ("1 cách hiểu/diễn giải truyền thống"...) nhưng nếu từ 2 câu liên tiếp trở lên, SAU KHI bỏ qua tiền tố/mệnh đề dẫn nhập ngắn không mang nội dung hedge phía trước (vd "Theo...", "Đây là...", "Đây đại diện cho..."), đều chứa CÙNG 1 khuôn cụm danh từ dạng "một cách [X] truyền thống"/"một [X] truyền thống" (chỉ đổi từ X, vd hiểu/diễn giải/góc nhìn) → VI PHẠM. Sửa bằng cách đổi CẤU TRÚC câu (không chỉ thêm/đổi tiền tố trong khi giữ nguyên khuôn cụm danh từ bên trong) qua từng câu, hoặc gộp các ý liên quan vào DUY NHẤT 1 câu dưới 1 mệnh đề dẫn nhập chung (không được để 1 câu hedge độc lập rồi các câu sau không liên quan ngữ pháp trực tiếp dựa vào hedge đó).
- MỞ RỘNG (Prompt Delta Retention v2): NGOÀI việc chống lặp khuôn cụm danh từ ở trên, cũng tránh để TỪ 3 CÂU LIÊN TIẾP trở lên cùng NHỊP NGHE "[cụm quy nguồn] + [động từ gán nghĩa] + [nội dung tĩnh]" dù từ vựng có đổi hay không -- vd "Diễn giải cổ xưa trả lời qua..." rồi "Góc nhìn dân gian xem đây là..." rồi "Cổ nhân truyền lại rằng..." là VI PHẠM dù 3 cụm mở đầu khác từ. Cách sửa: đặt framing XEN GIỮA câu thay vì luôn mở đầu bằng cụm quy nguồn (vd "Biết dừng đúng lúc, theo cách hiểu này, cũng được xem là một dạng vững vàng" -- vẫn đủ framing nhưng khác nhịp).
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = (
    """Bạn là giám khảo 2 vai trò: (1) kiểm tra đúng khuôn khổ diễn giải, (2) chuyên gia short-form triết học. Chấm 3 phương án dưới đây.

=== DỮ LIỆU GỐC (nguồn duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi kiểm tra.

"""
    + content_categories.category_rubric_block(content_categories.INTERPRETATION)
    + """

BƯỚC 1 -- KIỂM TRA (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ dùng đúng essence/keyword trong dữ liệu, không bịa hào từ/chi tiết lịch sử khác, (b) có NGỤ Ý đây là "quẻ của hôm nay"/dự đoán riêng cho người xem không -- có thì FAIL NGAY (vi phạm quy tắc Category 3 nghiêm trọng nhất), (c) có khẳng định chắc chắn điều gì sẽ xảy ra không -- có thì FAIL, (d) có từ 2 câu liên tiếp trở lên, SAU KHI bỏ qua tiền tố/mệnh đề dẫn nhập ngắn không mang nội dung hedge phía trước câu (vd "Theo...", "Đây là...", "Đây đại diện cho..."), đều chứa CÙNG 1 khuôn cụm danh từ dạng "một cách [X] truyền thống"/"một [X] truyền thống" (chỉ đổi từ X -- vd "Theo một cách hiểu truyền thống..." rồi "Một cách diễn giải truyền thống..." rồi "Đây đại diện cho một góc nhìn truyền thống..." dùng liên tiếp VẪN TÍNH LÀ VI PHẠM dù tiền tố mở đầu mỗi câu khác nhau, vì khuôn cụm danh từ bên trong giống nhau) không -- có thì FAIL (lặp khuôn bề mặt, đọc rối, dù mỗi câu riêng lẻ đúng khung Category 3; hedge dùng cấu trúc câu thật sự KHÁC nhau, không chỉ đổi tiền tố dẫn nhập, KHÔNG tính là vi phạm điểm này). Vi phạm bất kỳ điểm nào → LOẠI.
(e) [Prompt Delta Retention v2, ngưỡng RIÊNG với (d)] Có TỪ 3 CÂU LIÊN TIẾP trở lên cùng NHỊP NGHE "[cụm quy nguồn] + [động từ gán nghĩa] + [nội dung tĩnh]" không, DÙ từ vựng cụm quy nguồn/động từ có đổi hay không (khác (d) vốn chỉ bắt đúng 1 khuôn cụm danh từ cụ thể -- (e) bắt CẢ nhịp câu tổng quát hơn, kể cả khi (d) không FAIL)? Nếu CÓ từ 3 câu liên tiếp trở lên -- FAIL (lặp nhịp, đọc như liệt kê thay vì kể chuyện). Nếu CHỈ 2 câu liên tiếp cùng nhịp -- KHÔNG loại, nhưng PHẢI ghi cảnh báo cụ thể vào "feedback".

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua kiểm tra.

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""
)


def write_short_bundle_file(quai_name: str, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    import re
    slug = re.sub(r"[^a-zA-Z0-9]+", "", quai_name)[:30] or "Que"
    out_path = OUTPUT_DIR / f"KINHDICH_{slug}_Short.txt"
    n = 1
    while out_path.exists():
        n += 1
        out_path = OUTPUT_DIR / f"KINHDICH_{slug}_{n}_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    quai = _peek_quai()
    print(f"Quẻ: {quai['name']}", flush=True)
    facts = {"quai_name": quai["name"], "trigram": quai["trigram"], "essence": quai["essence"], "keyword": quai["keyword"]}
    print(json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

    result = generate_verified_script(facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- kiểm tra chưa PASS, cần người xem lại (quẻ vẫn giữ nguyên vị trí trong vòng xoay để thử lại).", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(quai["name"], result["script"])
    rotation_state.commit(ROTATION_STATE_PATH, quai["name"], "last_quai")
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
