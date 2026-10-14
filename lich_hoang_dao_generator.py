"""Sinh nội dung Short "Lịch Hoàng Đạo" hàng ngày cho kênh Phong Thuỷ --
đăng cố định 6h sáng mỗi ngày, nói về ngày âm lịch/hoàng đạo hắc đạo/giờ
tốt của CHÍNH NGÀY HÔM ĐÓ.

KIẾN TRÚC BẮT BUỘC (khác hẳn Short lấy từ Content-Creator): đây là nội
dung có SỰ THẬT TÍNH TOÁN ĐƯỢC (ngày âm lịch, Can Chi, Hoàng Đạo/Hắc Đạo,
giờ tốt...) -- không được để agy/Codex "nhớ" hay tự suy luận những con số
này, sai là sai khách quan, ảnh hưởng thật nếu người xem tin theo. Quy
trình:
  1. vnlunar (đã kiểm chứng đối chiếu 2 nguồn độc lập thật -- xem lịch sử
     phiên làm việc, khớp chính xác cả câu chữ phần giờ hoàng đạo) TÍNH
     TOÁN toàn bộ sự kiện lịch cho ngày cần đăng.
  2. agy soạn kịch bản Short (~20-30s) DIỄN GIẢI các sự kiện đó cho hấp
     dẫn -- KHÔNG được thêm số liệu/sự kiện ngoài dict đã tính.
  3. Codex PHẢN BIỆN ĐỐI CHIẾU TỪNG SỐ trong kịch bản với dict gốc -- đây
     là fact-check, không phải chấm hook hay hay dở. Bất kỳ số/tên nào
     không khớp dict gốc là FAIL ngay, không thương lượng.
  4. Trần cứng MAX_ITERATIONS, giống mọi vòng lặp agy-Codex khác trong dự
     án -- không lặp vô hạn.

Output ghi theo ĐÚNG format "*** N" mà short_batch_runner.py/discover_segments()
đã đọc được -- tái dùng nguyên vẹn pipeline TTS->render->SEO->upload đã có,
không viết lại.
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from short_judge_panel_engine import generate_verified_script as _engine_generate_verified_script  # noqa: E402

try:
    import vnlunar
except ImportError:
    print("CẦN CÀI: pip install vnlunar (đã kiểm chứng độ chính xác trong phiên làm việc -- "
          "khớp chính xác nguồn độc lập baoquocte.vn/vietnam.vn cho ngày 23/7/2026).", file=sys.stderr)
    raise

import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.GROUNDED_DATA  # xem content_categories.py
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"


def compute_calendar_facts(target_date: date) -> dict:
    """Chỉ lấy đúng field cần cho 1 Short ngắn -- không đưa cả object đầy
    đủ vào prompt (đỡ nhiễu, đỡ token) -- nhưng MỌI con số trong kịch bản
    cuối cùng phải truy được về ĐÚNG các field này."""
    info = vnlunar.get_full_info(target_date.day, target_date.month, target_date.year)
    return {
        # BUG THẬT phát hiện qua phản hồi người dùng (xem phiên làm việc,
        # cùng bug pattern đã sửa ở 3 generator ngày khác): solar_date/
        # day_of_week không được prompt tham chiếu tên field cụ thể nhưng
        # vẫn rò rỉ vào kịch bản, tạo câu dẫn ngày dài dòng kém hấp dẫn.
        # Bỏ hẳn -- lunar_date GIỮ LẠI vì đây là generator lịch âm, bản
        # thân lunar_date là trọng tâm nội dung (khác solar_date/day_of_week
        # chỉ là thông tin phụ không ai yêu cầu dùng).
        "lunar_date": f"{info['lunar']['day']}/{info['lunar']['month']}" + (" (nhuận)" if info["lunar"]["leap"] else ""),
        "lunar_year_can_chi": info["can_chi"]["year"],
        "day_can_chi": info["can_chi"]["day"],
        "truc": info["12_constructions"]["name"],
        "truc_good_for": info["12_constructions"]["good_for"],
        "truc_bad_for": info["12_constructions"]["bad_for"],
        "day_type": info["day_type"]["type"],  # "Hoàng Đạo" hoặc "Hắc Đạo"
        "day_type_desc": info["day_type"]["desc"],
        "auspicious_hours": info["auspicious_hours"],
        "good_directions": info["directions"]["good_text"],
        "bad_directions": info["directions"]["bad_text"],
    }


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form phong thuỷ/lịch âm tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) giới thiệu ngày hôm nay theo lịch vạn niên, dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG 1 CÂU ĐẦU TIÊN, KHÔNG được mở đầu bằng cách liệt kê ngày tháng/âm lịch trước rồi mới vào ý chính:
A. CÂU HỎI GÂY TÒ MÒ: mở bằng câu hỏi xoáy thẳng vào 1 chi tiết bất ngờ nhất trong dữ liệu (vd nghịch lý Hoàng Đạo nhưng Trực xấu, hoặc giờ đặc biệt) -- ngày tháng cụ thể nhắc SAU câu hook, không mở đầu bằng nó.
B. CẢNH BÁO/NGHỊCH LÝ: mở bằng 1 câu nêu bật điểm mâu thuẫn hoặc điều dễ hiểu lầm trong dữ liệu hôm nay (vd "Hoàng Đạo không có nghĩa là mọi việc đều thuận") rồi mới giải thích.
C. LỢI ÍCH TRỰC TIẾP: mở bằng 1 câu nói thẳng người xem được lợi gì NẾU biết đúng giờ/hướng hôm nay, tạo cảm giác "xem tiếp để biết".

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ được dùng đúng số liệu/tên gọi có trong dữ liệu trên -- KHÔNG được thêm ngày tháng, Can Chi, giờ, hướng, hay bất kỳ chi tiết nào KHÔNG có trong dữ liệu.
- Ngày tháng dương lịch cụ thể (vd "23/07/2026") chỉ nên xuất hiện SAU câu hook, không phải câu đầu tiên -- mở đầu bằng liệt kê ngày tháng luôn là hook yếu.
- KHÔNG LIỆT KÊ GIỜ/HƯỚNG: auspicious_hours/good_directions trong dữ liệu có thể có 4-6 mục -- giọng đọc TTS liệt kê hết ("Dần 3-5h, Thìn 7-9h, Tỵ 9-11h...") nghe dông dài, khó theo dõi qua tai, không hấp dẫn (đã kiểm chứng: video thật bị chê vì lỗi này). CHỈ CHỌN ĐÚNG 1 giờ/1 hướng NỔI BẬT NHẤT trong số đó, gắn với 1 lợi ích cụ thể, tự nhiên (vd "giờ Thìn, từ 7 đến 9 giờ sáng, là lúc hợp nhất để bắt đầu việc quan trọng hôm nay" -- KHÔNG phải "giờ Thìn (7-9h)"). Phần giờ/hướng còn lại (nếu cần) để hiển thị trên màn hình dạng chữ, không đọc thành lời.
- Kết thúc bằng gợi ý hành động nhẹ nhàng phù hợp giờ/hướng tốt hôm đó (không cam kết kết quả chắc chắn, không ngôn ngữ mê tín tuyệt đối).
- Giọng văn tự nhiên, gần gũi, không giật gân/không doạ dẫm. Đọc thử to lên trong đầu trước khi chọn: câu có bị vấp/dài dòng không?
- ĐÁNH DẤU TỪ/CỤM TỪ QUAN TRỌNG bằng **hai dấu sao** (vd "**Trực phá**", "**giờ Dần**") -- 1-3 cụm mỗi câu, đúng những con số/tên gọi cốt lõi (Can Chi, tên Trực, Hoàng Đạo/Hắc Đạo, giờ, hướng) để video sau này phóng to đúng lúc nói tới -- KHÔNG đánh dấu từ nối/từ đệm, chỉ đánh dấu đúng phần MANG THÔNG TIN.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = """Bạn là giám khảo 2 vai trò: (1) fact-checker NGHIÊM NGẶT, (2) chuyên gia short-form. Chấm 3 phương án dưới đây.

=== DỮ LIỆU GỐC (nguồn sự thật duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: các cụm bọc trong **hai dấu sao** (vd "**Trực phá**") là đánh dấu hiển thị (để phóng to trên video), KHÔNG phải nội dung thêm -- khi fact-check, BỎ QUA dấu ** và chỉ so sánh phần CHỮ bên trong với dữ liệu gốc như bình thường.

BƯỚC 1 -- FACT-CHECK (LÀM TRƯỚC, LOẠI TRỪ): với MỖI phương án, đối chiếu TỪNG con số/tên gọi (ngày âm lịch, Can Chi, tên Trực, Hoàng Đạo/Hắc Đạo, giờ tốt, hướng) với dữ liệu gốc. Phương án nào có BẤT KỲ sai lệch/tự thêm chi tiết không có trong dữ liệu gốc → LOẠI, không được chọn làm winner dù hook hay đến đâu. Cũng kiểm tra: có đánh dấu ** hợp lý không (1-3 cụm/câu, đúng phần mang thông tin) hay đánh dấu tràn lan/thiếu? RIÊNG PHẦN GIỜ/HƯỚNG: phương án nào LIỆT KÊ từ 2 giờ/hướng trở lên liền nhau trong 1 câu (vd "giờ Dần, Thìn, Tỵ..." hoặc nhiều cặp ngoặc đơn thời gian liên tiếp) → LOẠI, vì nghe qua giọng đọc dông dài/khó theo dõi -- chỉ chấp nhận phương án chọn ĐÚNG 1 giờ/1 hướng nổi bật. Cũng kiểm tra: có dùng ngôn ngữ khẳng định chắc chắn/tuyệt đối cho mức độ tốt xấu của ngày/giờ/hướng không (vd "chắc chắn đại cát", "tuyệt đối thuận lợi"), VÀ có trình bày ý nghĩa cát/hung của ngày như sự thật khách quan mà không có framing dè dặt ("theo lịch pháp truyền thống", "được xem là") không? Vi phạm 1 trong 2 → FAIL, cùng mức nghiêm trọng như sai lệch dữ liệu.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số các phương án đã qua fact-check: câu đầu tiên có đủ sức giữ chân trong ~3 giây không (không phải liệt kê ngày tháng trước)? Có nghịch lý/thông tin bất ngờ ngay từ đầu không?

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên các dấu ** của phương án thắng, không được bóc bỏ:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE" (nếu cả 3 đều FAIL fact-check), "winner_script": "kịch bản đầy đủ của bản thắng KÈM dấu **, để rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def generate_verified_script(facts: dict, max_rounds: int = MAX_ITERATIONS, hook_pass_threshold: int = 8) -> dict:
    """Uỷ quyền cho short_judge_panel_engine.py (đã tách ra dùng chung cho
    mọi generator Short "sự thật tính toán được" -- xem module đó). Giữ
    nguyên tên hàm + prompt template CỐ ĐỊNH của lịch hoàng đạo ở đây,
    hành vi y hệt bản gốc trước khi tách."""
    return _engine_generate_verified_script(
        facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT, max_rounds=max_rounds, hook_pass_threshold=hook_pass_threshold,
    )


def write_short_bundle_file(target_date: date, script: str) -> Path:
    """Ghi đúng format '*** N' để short_batch_runner.py's discover_segments()
    đọc được -- episode prefix riêng theo ngày, tách biệt hoàn toàn khỏi
    nguồn Short từ Content-Creator (không lẫn lộn 2 nguồn nội dung)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ep_prefix = f"LICH{target_date.strftime('%Y%m%d')}"
    out_path = OUTPUT_DIR / f"{ep_prefix}_LichHoangDao_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, mặc định hôm nay")
    ap.add_argument("--output-json", default=None, help="Ghi thêm kết quả đầy đủ (facts+script+lịch sử) ra JSON, để kiểm tra")
    args = ap.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date.today()
    facts = compute_calendar_facts(target_date)
    print(f"Dữ liệu lịch {target_date.isoformat()}:", json.dumps(facts, ensure_ascii=False, indent=2), flush=True)

    result = generate_verified_script(facts)
    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- fact-check chưa PASS, cần người xem lại kết quả trên.", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(target_date, result["script"])
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
