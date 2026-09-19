"""Phản biện + tối ưu "hook" cho kịch bản Short (khác content_review.py --
file đó kiểm tra AN TOÀN giáo lý cho Long, không đánh giá độ hấp dẫn).

Short lấy nguyên văn từ file *_Short.txt của Content-Creator (mỗi tập 30
đoạn "*** N") -- các đoạn này được viết như trích đoạn châm ngôn cho tập
Long, CHƯA từng được viết/duyệt riêng cho chuẩn short-form (hook trong
1-3 giây đầu, nhịp nhanh, không có đoạn chùng).

THIẾT KẾ (đã đổi sau khi test thật): ban đầu dùng vòng lặp sửa tuần tự
(agy sửa 1 bản -> codex chê -> agy sửa tiếp bản đó) giống content_seo.py --
test trên 3 short thật cho kết quả KHÔNG hội tụ tốt, điểm hook dao động lên
xuống thay vì tăng dần qua các vòng (bằng chứng: seg1 6->5->6, seg3
6->7->6) vì sửa tuần tự trên 1 ứng viên duy nhất dễ "đi lạc" khi viết sáng
tạo (khác hẳn sửa lỗi khách quan như chính tả/an toàn giáo lý). Đổi sang
mô hình JUDGE PANEL: agy sinh 3 phương án khác góc độ hook trong 1 lần gọi
(câu hỏi trực diện / mâu thuẫn niềm tin / xưng hô cá nhân), Codex chấm
+ chọn bản tốt nhất trong 1 lần -- không "đi lạc" qua nhiều vòng sửa vì
luôn so sánh với chính kịch bản GỐC, không lệch dần qua từng bước sửa.

BUG THẬT phát hiện qua audit toàn phiên làm việc (xem phiên làm việc):
module này TỪNG tự cài lại TOÀN BỘ vòng lặp generate/judge/retry (copy gần
như y hệt short_judge_panel_engine.py -- module đã qua 6+ vòng Codex CLI
review độc lập, vá schema validation/chặn winner_script bịa/ép trần
hook_score...) nhưng KHÔNG hề import module đó -- 2 bản implementation
song song, bản này KHÔNG có bất kỳ hardening nào đã làm cho bản kia (đúng
lớp lỗi đã rút kinh nghiệm với rotation_state.py/topic_bank.py: sửa 1 chỗ
không tự lan sang bản sao chép). Refactor: `review_and_optimize_short()`
giờ CHỈ còn là wrapper mỏng gọi `short_judge_panel_engine.generate_verified_
script()` -- giữ NGUYÊN chữ ký hàm + hình dạng dict trả về để short_batch_
runner.py không cần đổi gì, nhưng cơ chế bên trong (validate/retry/chặn
bịa) giờ dùng CHUNG với 10 generator Phong Thủy, tự động thừa hưởng mọi
lần hardening sau này.

Đổi kèm: "ORIGINAL" (giữ nguyên bản gốc nếu cả 3 phương án đều tệ hơn)
KHÔNG còn là 1 lựa chọn winner riêng (engine chỉ nhận A/B/C/NONE) -- dựa
vào cơ chế best-effort + needs_human_review=True sẵn có của engine khi cả
3 đều fail fact-check, nhất quán với triết lý "không tự ý âm thầm hạ chuẩn
xuống bản CHƯA từng viết cho short-form, để người thật quyết định" thay vì
"tự động phát bản gốc chưa tối ưu". Đổi kèm: thêm fact_check CÓ CẤU TRÚC
theo từng phương án (bắt buộc bởi engine) thay vì chấm 3 tiêu chí rời rạc
trong văn xuôi -- ĐÂY LÀ CẢI THIỆN CHẤT LƯỢNG THẬT, không chỉ là refactor:
buộc giám khảo phải nêu RÕ "có đổi Ý GIÁO LÝ không" cho TỪNG phương án
thay vì gộp chung trong 1 câu feedback tự do.

Cùng trần cứng MAX_ROUNDS như content_seo.py/content_review.py -- không
lặp vô hạn; nếu sau MAX_ROUNDS vẫn chưa đạt ngưỡng điểm, trả về bản tốt
nhất đã có kèm needs_human_review=True (đúng triết lý đã dùng cho Long:
không tự ép PASS, để người thật quyết định)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from short_judge_panel_engine import generate_verified_script  # noqa: E402

MAX_ROUNDS = 3
PASS_SCORE_THRESHOLD = 8  # /10 -- ngưỡng chấp nhận, không cần tuyệt đối 10

_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên short-form (TikTok/YouTube Shorts) cho kênh Phật giáo tiếng Việt. Viết lại kịch bản dưới đây thành 3 PHƯƠNG ÁN KHÁC NHAU, mỗi phương án theo 1 chiến lược hook riêng, dựa DUY NHẤT trên dữ liệu sau:

{facts_json}

(original_script: kịch bản GỐC cần viết lại -- đây là trích đoạn châm ngôn cho tập Long, CHƯA từng được viết/duyệt riêng cho chuẩn short-form.)

3 chiến lược bắt buộc áp dụng (mỗi phương án 1 chiến lược, không trộn):
A. CÂU HỎI TRỰC DIỆN: mở bằng câu hỏi thẳng vào người xem ngay câu đầu tiên.
B. MÂU THUẪN NIỀM TIN: mở bằng 1 câu nêu niềm tin phổ biến RẤT NGẮN GỌN, rồi lập tức phản bác trong câu 2 (không giải thích dài trước khi phản bác).
C. HÌNH ẢNH/TÌNH HUỐNG CỤ THỂ: mở bằng 1 hình ảnh/tình huống đời thường cụ thể (không trừu tượng) khiến người xem liên tưởng ngay tới bản thân.

Với CẢ 3 phương án:
- Đoạn giữa: nén câu chữ, bỏ từ đệm/lặp cấu trúc thừa, thay khái niệm trừu tượng bằng hình ảnh cụ thể nếu hợp lý.
- Payoff cuối: câu hỏi mở/ý bất ngờ, nối logic rõ với phần trước.
- RÀNG BUỘC BẮT BUỘC: KHÔNG đổi/thêm/bớt Ý GIÁO LÝ so với original_script, KHÔNG thêm nhận định/số liệu không có trong original_script, giọng văn tự nhiên tiếng Việt, không giật gân/clickbait sai lệch.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = """Bạn là giám khảo 2 vai trò: (1) kiểm tra KHÔNG đổi Ý GIÁO LÝ so với bản gốc, (2) chuyên gia dựng nội dung Short-form cho kênh Phật giáo tiếng Việt. Chấm 3 phương án dưới đây, không khen cho có, phải chỉ rõ điểm yếu của từng bản.

=== KỊCH BẢN GỐC (nguồn đối chiếu duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

BƯỚC 1 -- FACT-CHECK (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) có đổi/thêm/bớt Ý GIÁO LÝ so với original_script không, (b) có thêm nhận định/số liệu KHÔNG có trong original_script không, (c) có giật gân/clickbait sai lệch không. Vi phạm bất kỳ điểm nào → LOẠI (FAIL).

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua fact-check, theo 3 tiêu chí:
1. HOOK: 1-2 câu ĐẦU có đủ sức giữ chân người xem trong ~3 giây không (mâu thuẫn/bất ngờ/câu hỏi ngay từ đầu)?
2. NHỊP: có đoạn nào lan man, thừa chữ không (short cần nhịp nhanh)?
3. PAYOFF: câu kết có giữ tò mò, nối logic rõ không?

Trả về CHỈ 1 JSON object:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "toàn bộ kịch bản của bản thắng, mỗi câu 1 dòng", "hook_score": 1-10, "feedback": "vì sao chọn bản này, còn thiếu gì để đạt điểm tối đa nếu hook_score < 10"}}"""


def review_and_optimize_short(script_text: str, max_rounds: int = MAX_ROUNDS, pass_threshold: int = PASS_SCORE_THRESHOLD) -> dict:
    """Trả về {final_script, passed, hook_score, rounds_used, round_history,
    needs_human_review} -- GIỮ NGUYÊN hình dạng cũ (short_batch_runner.py
    không cần đổi gì) dù bên trong giờ delegate hoàn toàn cho
    short_judge_panel_engine.generate_verified_script()."""
    facts = {"original_script": script_text}
    result = generate_verified_script(
        facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT,
        max_rounds=max_rounds, hook_pass_threshold=pass_threshold,
    )
    return {
        "final_script": result["script"],
        "passed": result["passed"],
        "hook_score": result["hook_score"],
        "rounds_used": result["iterations_used"],
        "round_history": result["history"],
        "needs_human_review": result["needs_human_review"],
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--script-text", help="Đọc trực tiếp từ tham số")
    ap.add_argument("--script-file", help="Đọc từ file .txt")
    ap.add_argument("--output", required=True)
    ap.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    ap.add_argument("--pass-threshold", type=int, default=PASS_SCORE_THRESHOLD)
    args = ap.parse_args()

    if args.script_file:
        script_text = Path(args.script_file).read_text(encoding="utf-8").strip()
    elif args.script_text:
        script_text = args.script_text
    else:
        print("Cần --script-text hoặc --script-file.", file=sys.stderr)
        return 1

    result = review_and_optimize_short(script_text, args.max_rounds, args.pass_threshold)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {args.output} (passed={result['passed']}, hook_score={result['hook_score']})")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
