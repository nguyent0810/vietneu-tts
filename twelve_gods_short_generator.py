"""Sinh nội dung Short "12 vị Thần hôm nay" (Thanh Long/Bạch Hổ/Chu Tước/
Huyền Vũ/Kim Quỹ/Minh Đường/Ngọc Đường/Thiên Đức/Tư Mệnh/Câu Trần/Thiên
Hình/Thiên Lao) cho kênh Phong Thuỷ -- CÙNG kiến trúc "sự thật tính toán
được" như lich_hoang_dao_generator.py (đã kiểm chứng qua judge-panel +
fact-check), dùng chung short_judge_panel_engine.py.

Căn cứ: vnlunar.get_full_info()['12_gods'] -- ĐÃ xác nhận đây chính là hệ
12 vị Thần mà kênh Phong Thuỷ (Astro Việt Insights) từng dùng cho các tiêu
đề như "BẠCH HỔ GẦM VANG", "Đại Họa Chu Tước Sà Xuống", "RỒNG XANH GIÁNG
THẾ" (= Thanh Long) -- tra thấy 12/12 giá trị field này khớp đúng bộ 12
vị Thần cổ điển (xem phiên làm việc). vnlunar đã kiểm chứng đối chiếu 2
nguồn độc lập thật cho phần lịch âm/giờ hoàng đạo trước đó trong dự án.

GHI CHÚ GIỚI HẠN ĐÃ BIẾT: khi vị Thần hôm nay là 1 trong 4 Tứ Tượng (Thanh
Long/Bạch Hổ/Chu Tước/Huyền Vũ), domain_creative_profiles.json đã có sẵn
ảnh AI đẹp cho các linh vật này (render_mode="ai_generate_ok", đã test qua
Long) -- nhưng render_short.py hiện CHỈ tự động dùng ảnh tĩnh cho
render_mode="static_asset" (Bát Quái/Ngũ Hành), CHƯA nối tới ComfyUI/Cursor
cho Short. Short dạng này tạm thời vẫn rơi về B-roll Pexels thường (đúng
hành vi hiện tại, không phải lỗi) -- việc nối AI-generate cho Short là việc
riêng, chưa làm trong lần này."""
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


def compute_god_facts(target_date: date) -> dict:
    info = vnlunar.get_full_info(target_date.day, target_date.month, target_date.year)
    god = info["12_gods"]
    # BUG THẬT phát hiện qua phản hồi thật: trước đây có thêm field
    # "day_type" (Hoàng Đạo/Hắc Đạo CỦA CẢ NGÀY, khác hệ với 12 vị Thần) --
    # khiến nội dung/tiêu đề bị kéo về khung "Ngày Hoàng Đạo/Hắc Đạo" giống
    # hệt mảng lịch hoàng đạo ĐÃ TẠM DỪNG (trùng lặp với nội dung hệ thống
    # cũ đã phủ sẵn). Bỏ hẳn field này -- nội dung 12 vị Thần giờ ĐỘC LẬP
    # với hệ Hoàng Đạo/Hắc Đạo tổng thể của ngày, chỉ còn xoay quanh CHÍNH
    # vị Thần (god_description có thể vẫn nhắc "Hoàng Đạo"/"Hắc Đạo" như
    # NHÃN RIÊNG của vị Thần đó -- đây là thông tin đúng, khác day_type).
    return {
        # BUG THẬT phát hiện qua phản hồi người dùng (xem phiên làm việc):
        # solar_date/day_of_week trước đây có trong facts nhưng không được
        # prompt tham chiếu tên field cụ thể -- agy vẫn tự nhét vào kịch
        # bản (CÙNG BUG PATTERN với day_type đã sửa ở trên), tạo câu dẫn
        # ngày dài dòng kém hấp dẫn. Bỏ hẳn, day_can_chi đã đủ neo "hôm nay".
        "day_can_chi": info["can_chi"]["day"],
        "god_name": god["name"],
        "god_type": god["type"],  # "auspicious" hoặc "inauspicious"
        "god_status": god["status"],  # "good" hoặc "bad"
        "god_description": god["description"],  # vd "Sao xấu - Hắc Đạo" -- nhãn RIÊNG của vị Thần này, không phải loại ngày tổng thể
        "auspicious_hours": info["auspicious_hours"],
    }


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form phong thuỷ/huyền học tiếng Việt, chuyên viết theo phong cách kịch tính-thần thoại (giống các tiêu đề "BẠCH HỔ GẦM VANG", "RỒNG XANH GIÁNG THẾ" đã thành công trên kênh). Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) giới thiệu VỊ THẦN cai quản ngày hôm nay, dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN, KHÔNG mở đầu bằng liệt kê ngày tháng:
A. GỌI TÊN THẦN NGAY: mở bằng chính tên vị Thần hôm nay kèm 1 tính từ/hình ảnh mạnh (vd "Bạch Hổ ngự trị..." nếu god_status=bad, "Thanh Long giáng thế..." nếu tốt) -- tạo cảm giác kịch tính/thần thoại đúng phong cách đã thành công, nhưng KHÔNG bịa thêm chi tiết thần thoại ngoài god_description.
B. CẢNH BÁO/CƠ HỘI: nếu god_status=bad, mở bằng lời cảnh báo nhẹ (không doạ dẫm quá mức); nếu god_status=good, mở bằng lời mời gọi cơ hội hôm nay.
C. CÂU HỎI GÂY TÒ MÒ: mở bằng câu hỏi về việc hôm nay nên/không nên làm gì, liên hệ tới vị Thần.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ được dùng đúng tên Thần/loại (tốt-xấu, Hoàng Đạo-Hắc Đạo)/mô tả có trong dữ liệu trên -- KHÔNG bịa thêm truyền thuyết, quyền năng, hay hậu quả cụ thể không có trong dữ liệu.
- Nếu god_status=bad: giọng cảnh báo NHẸ NHÀNG, không mê tín tuyệt đối, không doạ dẫm hậu quả nghiêm trọng cụ thể (vd không nói "sẽ gặp tai hoạ", chỉ nói "nên thận trọng hơn").
- Ngày tháng dương lịch cụ thể chỉ nên xuất hiện SAU câu hook.
- KHÔNG LIỆT KÊ GIỜ: auspicious_hours có thể có 4-6 mục -- giọng đọc TTS liệt kê hết ("Sửu, Thìn, Ngọ, Mùi, Tuất, Hợi...") nghe dông dài, khó theo dõi qua tai, không hấp dẫn (đã kiểm chứng: video thật bị chê vì lỗi này). Nếu nhắc tới giờ tốt, CHỈ CHỌN ĐÚNG 1 giờ NỔI BẬT NHẤT, gắn với 1 lợi ích cụ thể, đọc tự nhiên (vd "giờ Thìn, từ 7 đến 9 giờ sáng, rất hợp để bắt đầu việc quan trọng" -- KHÔNG phải "giờ Thìn (7-9h)"). Có thể bỏ hẳn phần giờ nếu câu chuyện về vị Thần đã đủ hấp dẫn mà không cần thêm.
- Kết thúc bằng gợi ý hành động nhẹ nhàng phù hợp.
- ĐÁNH DẤU TỪ/CỤM TỪ QUAN TRỌNG bằng **hai dấu sao** (vd "**Bạch Hổ**", "**Hắc Đạo**") -- 1-3 cụm mỗi câu, đúng tên Thần/loại ngày/giờ, KHÔNG đánh dấu từ đệm.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = """Bạn là giám khảo 2 vai trò: (1) fact-checker NGHIÊM NGẶT, (2) chuyên gia short-form kịch tính-thần thoại. Chấm 3 phương án dưới đây.

=== DỮ LIỆU GỐC (nguồn sự thật duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi fact-check.

BƯỚC 1 -- FACT-CHECK (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) tên Thần đúng god_name không, (b) loại tốt/xấu đúng god_status không, (c) KHÔNG bịa thêm truyền thuyết/quyền năng/hậu quả cụ thể ngoài god_description, (d) nếu god_status=bad thì giọng văn có "doạ dẫm hậu quả nghiêm trọng cụ thể" không (vd nói thẳng "sẽ mất tiền/gặp tai nạn") -- có thì FAIL vì vi phạm quy tắc không mê tín tuyệt đối, (e) có LIỆT KÊ từ 2 giờ trở lên liền nhau không (vd "Sửu, Thìn, Ngọ, Mùi...") -- có thì FAIL vì dông dài/khó nghe, (f) (áp dụng cho CẢ god_status=good VÀ bad, độc lập với check doạ dẫm ở (d)): có dùng ngôn ngữ khẳng định chắc chắn cho kết quả (vd "chắc chắn", "tuyệt đối", "vô cùng may mắn") KHÔNG, và có trình bày quyền năng/ảnh hưởng của vị Thần như sự thật khách quan mà không có framing dè dặt ("theo tín ngưỡng dân gian", "được cho là") không? Vi phạm 1 trong 2 → FAIL. Phương án nào vi phạm bất kỳ điểm nào → LOẠI.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua fact-check: câu đầu có kịch tính/giữ chân được không, đúng phong cách đã thành công trên kênh (gọi tên thần mạnh mẽ) không?

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def write_short_bundle_file(target_date: date, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ep_prefix = f"THAN{target_date.strftime('%Y%m%d')}"
    out_path = OUTPUT_DIR / f"{ep_prefix}_12ViThan_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, mặc định hôm nay")
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date.today()
    facts = compute_god_facts(target_date)
    print(f"Dữ liệu 12 vị Thần {target_date.isoformat()}:", json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

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
