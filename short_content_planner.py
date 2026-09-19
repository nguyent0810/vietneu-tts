"""Lập chiến lược nội dung + khung giờ đăng cho Short, dựa trên dữ liệu
YouTube Analytics THẬT của kênh (không suy đoán) -- vòng soạn (agy) - phản
biện (Codex), cùng mô hình đã dùng cho content_seo.py/short_content_review.py.

Input: số liệu channel analytics (traffic source, top-performing shorts
theo views/ngày, khung giờ đã đăng thủ công trước đây) -- caller tự thu
thập qua youtube_analytics.py/youtube_catalog.py, truyền vào dạng dict, để
module này không tự gọi API (tách rõ thu thập dữ liệu / ra quyết định).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import _run_agy, _run_codex, _extract_json, ContentSeoError  # noqa: E402

MAX_ROUNDS = 3

_DRAFT_PROMPT = """Bạn là chuyên gia chiến lược nội dung YouTube Shorts cho kênh Phật giáo tiếng Việt. Dựa trên dữ liệu THẬT dưới đây, đề xuất chiến lược nội dung + khung giờ đăng để đạt 5 short/ngày với chất lượng cao (không chạy theo số lượng mà giảm chất).

=== DỮ LIỆU KÊNH THẬT (90 ngày gần nhất) ===
{channel_summary}

=== HIỆU SUẤT CÁC SHORT ĐÃ ĐĂNG (views/ngày kể từ lúc đăng) ===
{top_shorts}

=== KHUNG GIỜ ĐÃ DÙNG THỦ CÔNG TRƯỚC ĐÂY (có dữ liệu thật) ===
{existing_slots}
{revision_note}
Đề xuất:
1. 5 khung giờ đăng/ngày cụ thể (giờ UTC), có lý do dựa trên dữ liệu (không phải đoán chung chung "giờ vàng").
2. Với mỗi khung giờ, đề xuất KIỂU nội dung phù hợp (vd: khung giờ tối đăng nội dung suy ngẫm dài hơi hơn, khung giờ trưa đăng câu châm ngôn ngắn) -- dựa trên pattern thật đã thấy (short 10-13s vs short 22-45s hiệu suất khác nhau ở khung giờ khác nhau không?).
3. Tỷ lệ trộn giữa 2 định dạng đã chứng minh hiệu quả (câu châm ngôn cực ngắn ~10s vs câu chuyện có hook ~25-35s) trong 5 slot/ngày.
4. Rủi ro cụ thể nếu tăng lên 5 short/ngày (vd: cạnh tranh nội dung với chính mình, thuật toán giảm ưu tiên nếu đăng dồn dập, nguồn nội dung có đủ 5 đoạn chất lượng/ngày không).

Trả về CHỈ 1 JSON object:
{{"time_slots": [{{"utc_time": "HH:MM", "content_type": "...", "rationale": "..."}}, ...5 slot...], "format_mix": "...", "risks": ["...", "..."], "summary": "tóm tắt chiến lược 2-3 câu"}}"""

_REVIEW_PROMPT = """Bạn là biên tập viên phản biện chiến lược nội dung. Nhiệm vụ: TÌM LỖI trong đề xuất dưới đây, không khen cho có.

=== DỮ LIỆU GỐC ===
{channel_summary}

=== ĐỀ XUẤT CẦN PHẢN BIỆN ===
{draft}

Kiểm tra nghiêm: (1) khung giờ đề xuất có THỰC SỰ dựa trên dữ liệu đưa ra không, hay chỉ là suy đoán chung chung đội lốt số liệu? (2) 5 slot/ngày có dấu hiệu tự cạnh tranh (đăng quá sát giờ nhau) không? (3) tỷ lệ định dạng có hợp lý với dữ liệu hiệu suất thật không? (4) rủi ro nêu ra có đủ cụ thể/thực tế không hay chung chung?

Trả về CHỈ 1 JSON object:
{{"verdict": "PASS" hoặc "FAIL", "feedback": "nếu FAIL, liệt kê CỤ THỂ từng điểm yếu; nếu PASS để rỗng"}}"""


def draft_content_strategy(channel_summary: str, top_shorts: str, existing_slots: str, revision_feedback: str | None = None) -> dict:
    revision_note = (
        f"\n=== PHẢN HỒI TỪ BIÊN TẬP VIÊN LẦN TRƯỚC -- BẮT BUỘC SỬA THEO ===\n{revision_feedback}\n"
        if revision_feedback else ""
    )
    prompt = _DRAFT_PROMPT.format(
        channel_summary=channel_summary, top_shorts=top_shorts, existing_slots=existing_slots, revision_note=revision_note,
    )
    return _extract_json(_run_agy(prompt))


def review_content_strategy(draft: dict, channel_summary: str) -> dict:
    prompt = _REVIEW_PROMPT.format(channel_summary=channel_summary, draft=json.dumps(draft, ensure_ascii=False, indent=2))
    return _extract_json(_run_codex(prompt))


def plan_with_review(channel_summary: str, top_shorts: str, existing_slots: str, max_rounds: int = MAX_ROUNDS) -> dict:
    review_history = []
    draft = None
    feedback = None

    for i in range(1, max_rounds + 1):
        try:
            draft = draft_content_strategy(channel_summary, top_shorts, existing_slots, revision_feedback=feedback)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: agy soạn lỗi lần {i} ({exc}).", file=sys.stderr)
            review_history.append({"round": i, "stage": "draft", "error": str(exc)})
            continue

        try:
            review = review_content_strategy(draft, channel_summary)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: codex review lỗi lần {i} ({exc}).", file=sys.stderr)
            review_history.append({"round": i, "draft": draft, "stage": "review", "error": str(exc)})
            continue

        review_history.append({"round": i, "draft": draft, "review": review})
        print(f"Vòng {i}/{max_rounds}: verdict={review.get('verdict')}", flush=True)

        if review.get("verdict") == "PASS":
            return {"strategy": draft, "passed": True, "rounds_used": i, "review_history": review_history, "needs_human_review": False}
        feedback = review.get("feedback", "")

    print(f"CẢNH BÁO: sau {max_rounds} vòng vẫn chưa PASS -- dừng lại, cần người xem lại.", file=sys.stderr)
    return {"strategy": draft, "passed": False, "rounds_used": max_rounds, "review_history": review_history, "needs_human_review": True}
