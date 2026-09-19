"""Sinh nội dung Short "12 Cung Hoàng Đạo Phương Tây" cho kênh Phong Thuỷ --
CATEGORY 4 (Creative Astrology, xem content_categories.py) -- KHÁC HẲN
Category 1-3: KHÔNG fact-check theo kiểu đối chiếu dữ liệu/nguồn, đánh giá
bằng CHẤT LƯỢNG SÁNG TẠO (tránh sáo rỗng, tránh tuyệt đối hoá, không khẳng
định chắc chắn tương lai).

Nội dung xoay quanh TÍNH CÁCH/ĐẶC TRƯNG evergreen của từng cung (không phải
"tử vi hôm nay" -- daily horoscope thật cần dữ liệu thiên văn/ephemeris
không có sẵn trong dự án, và bản chất diễn giải, không computable). Dữ
liệu nền (ngày sinh/nguyên tố/từ khoá) là kiến thức phổ thông về chiêm
tinh phương Tây, được công nhận rộng rãi, không phải điểm gây tranh cãi."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from short_judge_panel_engine import generate_verified_script  # noqa: E402
import short_judge_panel_engine  # noqa: E402
import rotation_state  # noqa: E402
import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.CREATIVE_ASTROLOGY  # xem content_categories.py
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
ROTATION_STATE_PATH = Path(__file__).parent / "chunks_cache" / "western_zodiac_rotation_state.json"

# Kiến thức phổ thông chiêm tinh phương Tây (ngày/nguyên tố/từ khoá cốt lõi)
# -- không phải điểm gây tranh cãi, dùng chung khắp mọi nguồn chiêm tinh.
WESTERN_SIGNS = [
    {"name": "Bạch Dương", "english": "Aries", "date_range": "21/3 - 19/4", "element": "Hoả", "keyword": "tiên phong, nhiệt huyết, dám bắt đầu"},
    {"name": "Kim Ngưu", "english": "Taurus", "date_range": "20/4 - 20/5", "element": "Thổ", "keyword": "kiên định, thực tế, yêu sự ổn định"},
    {"name": "Song Tử", "english": "Gemini", "date_range": "21/5 - 20/6", "element": "Khí", "keyword": "linh hoạt, tò mò, giỏi giao tiếp"},
    {"name": "Cự Giải", "english": "Cancer", "date_range": "21/6 - 22/7", "element": "Thuỷ", "keyword": "nhạy cảm, giàu tình cảm, gắn bó gia đình"},
    {"name": "Sư Tử", "english": "Leo", "date_range": "23/7 - 22/8", "element": "Hoả", "keyword": "tự tin, hào phóng, thích toả sáng"},
    {"name": "Xử Nữ", "english": "Virgo", "date_range": "23/8 - 22/9", "element": "Thổ", "keyword": "tỉ mỉ, cầu toàn, phân tích sắc bén"},
    {"name": "Thiên Bình", "english": "Libra", "date_range": "23/9 - 22/10", "element": "Khí", "keyword": "hài hoà, công bằng, yêu cái đẹp"},
    {"name": "Thiên Yết", "english": "Scorpio", "date_range": "23/10 - 21/11", "element": "Thuỷ", "keyword": "mãnh liệt, bí ẩn, ý chí mạnh mẽ"},
    {"name": "Nhân Mã", "english": "Sagittarius", "date_range": "22/11 - 21/12", "element": "Hoả", "keyword": "phóng khoáng, ham khám phá, lạc quan"},
    {"name": "Ma Kết", "english": "Capricorn", "date_range": "22/12 - 19/1", "element": "Thổ", "keyword": "kỷ luật, tham vọng, kiên nhẫn"},
    {"name": "Bảo Bình", "english": "Aquarius", "date_range": "20/1 - 18/2", "element": "Khí", "keyword": "độc lập, sáng tạo, tư duy khác biệt"},
    {"name": "Song Ngư", "english": "Pisces", "date_range": "19/2 - 20/3", "element": "Thuỷ", "keyword": "mơ mộng, giàu cảm xúc, trực giác nhạy bén"},
]
ROTATION_ORDER = [s["name"] for s in WESTERN_SIGNS]


def _peek_sign() -> dict:
    name = rotation_state.peek_next(ROTATION_STATE_PATH, ROTATION_ORDER, "last_sign")
    return next(s for s in WESTERN_SIGNS if s["name"] == name)


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form chiêm tinh phương Tây tiếng Việt, viết cho khán giả trẻ yêu thích 12 cung hoàng đạo. Viết 4 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về TÍNH CÁCH ĐẶC TRƯNG của cung hoàng đạo sau, dựa trên dữ liệu:

{facts_json}

4 chiến lược hook bắt buộc -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI TÊN CUNG NGAY: mở bằng "Cung [tên]..." kèm 1 đặc điểm nổi bật nhất, tạo cảm giác "đúng là mình" cho người thuộc cung đó.
B. CÂU HỎI ĐỒNG CẢM: mở bằng câu hỏi mà người thuộc cung này thường tự hỏi/hay gặp (vd với Xử Nữ: "Bạn có hay để ý từng chi tiết nhỏ mà người khác bỏ qua không?").
C. NGHỊCH LÝ THÚ VỊ: mở bằng 1 nghịch lý/mặt ít ai để ý của cung này.
D. GƯƠNG SOI HÀNH VI: mở bằng 1 CÂU KHẲNG ĐỊNH (không phải câu hỏi, KHÁC Strategy B ở chỗ này) mô tả XU HƯỚNG HÀNH VI chung (không phải khoảnh khắc "ngay lúc này") của người thuộc cung này, PHẢI suy ra TRỰC TIẾP từ `keyword` của cung trong dữ liệu nền (không thêm hành vi/so sánh nào ngoài những gì `keyword` gợi ý), dùng 1 trong các marker xu hướng đã quy định ở QUY TẮC BẮT BUỘC bên dưới ("thường"/"hay"/"có xu hướng") -- KHÔNG bắt buộc đúng 1 cụm cố định, miễn thuộc nhóm marker đó (vd với Xử Nữ, `keyword`="tỉ mỉ, cầu toàn, phân tích sắc bén": "Người cung này thường để ý từng chi tiết nhỏ." -- LƯU Ý: KHÔNG thêm vế so sánh như "mà người khác lướt qua/bỏ qua" — đó là khẳng định về hành vi của NGƯỜI KHÁC, không suy ra được từ `keyword` (vốn chỉ mô tả cung đang viết)), rồi mới gọi tên cung.

QUY TẮC BẮT BUỘC cho CẢ 4 phương án (tiêu chuẩn Category 4 -- xem chi tiết):
- CỤ THỂ cho ĐÚNG cung này -- KHÔNG viết chung chung kiểu "ai cũng có lúc buồn lúc vui" (áp cho cung nào cũng đúng = sáo rỗng, không được viết).
- KHÔNG khẳng định chắc chắn điều sẽ xảy ra (không nói "bạn sẽ...", chỉ nói "người cung này thường có xu hướng...").
- Giọng văn trẻ trung, gần gũi, được phép hài hước nhẹ -- đây là nội dung giải trí.
- ĐÁNH DẤU tên cung/từ khoá quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
- RIÊNG PHƯƠNG ÁN D, câu mở đầu: (0) BẮT BUỘC xu hướng hành vi phải suy ra TRỰC TIẾP từ `keyword` của cung đang viết -- KHÔNG được thêm hành vi mới, KHÔNG được so sánh với người khác/nhóm khác (vd cấm "mà người khác lướt qua," "không giống ai," -- đây là claim về đối tượng KHÁC ngoài cung đang viết, `keyword` không xác nhận được); (1) PHẢI dùng 1 marker xu hướng hành vi chung ("thường"/"hay"/"có xu hướng" -- không bắt buộc đúng cụm "thường có xu hướng" nguyên văn, chỉ cần thuộc nhóm này), KHÔNG phải khoảnh khắc thời gian thực; (2) TUYỆT ĐỐI KHÔNG được viết "ngay lúc này bạn đang..." hay bất kỳ khẳng định thời điểm cụ thể nào về người xem (facts không biết người xem đang làm gì); (3) KHÔNG khẳng định lịch sử cá nhân của người xem (vd "bạn từng..."); (4) KHÔNG khẳng định 1 kết quả/cảm xúc cụ thể của người xem như sự thật đã xác lập -- chỉ mô tả xu hướng hành vi CHUNG của người thuộc cung này, không phải khẳng định riêng về người xem cụ thể.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}, {{"strategy": "D", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = (
    """Bạn là giám khảo chuyên gia short-form chiêm tinh/giải trí. Chấm 4 phương án dưới đây.

=== DỮ LIỆU NỀN (cung đang viết) ===
{facts_json}

=== 4 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi chấm.

"""
    + content_categories.category_rubric_block(content_categories.CREATIVE_ASTROLOGY)
    + """

BƯỚC 1 -- LOẠI TRỪ THEO TIÊU CHUẨN CATEGORY 4 Ở TRÊN: phương án nào SÁO RỖNG (đổi tên cung khác vẫn đúng y hệt), hoặc KHẲNG ĐỊNH CHẮC CHẮN tương lai ("bạn sẽ..."), hoặc dùng SAI element/tên cung trong dữ liệu nền → LOẠI. RIÊNG PHƯƠNG ÁN D: kiểm tra thêm câu mở đầu có dùng marker xu hướng ("thường"/"hay"/"có xu hướng") không, có khẳng định kết quả/lịch sử cá nhân/thời điểm thực/cảm xúc cụ thể của người xem không (facts không có dữ liệu riêng về người xem, chỉ có sign_name/date_range/element/keyword của cung) -- vi phạm bất kỳ điểm nào → LOẠI D, không được chọn làm winner. Ngoài ra: xu hướng hành vi của D phải được bảo chứng trực tiếp bởi keyword của đúng cung đang xét; nếu thêm hành vi mới hoặc so sánh với người khác/nhóm khác mà không suy ra được trực tiếp từ keyword → LOẠI D.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số còn lại: câu đầu có tạo cảm giác "đúng là mình"/tò mò không? Có cụ thể, sinh động, không nhàm chán không?

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do", "D": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "D" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""
)


def write_short_bundle_file(sign_name: str, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9]+", "", sign_name)[:30] or "Cung"
    out_path = OUTPUT_DIR / f"CUNGHD_{slug}_Short.txt"
    n = 1
    while out_path.exists():
        n += 1
        out_path = OUTPUT_DIR / f"CUNGHD_{slug}_{n}_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    sign = _peek_sign()
    facts = {"sign_name": sign["name"], "date_range": sign["date_range"], "element": sign["element"], "keyword": sign["keyword"]}
    print(f"Cung: {sign['name']}", json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

    result = generate_verified_script(facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS,
                                       valid_strategies=short_judge_panel_engine._PILOT_STRATEGIES_ABCD)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- chưa PASS, cần người xem lại (cung vẫn giữ nguyên vị trí trong vòng xoay để thử lại).", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(sign["name"], result["script"])
    rotation_state.commit(ROTATION_STATE_PATH, sign["name"], "last_sign")
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
