"""Sinh SEO (tiêu đề/mô tả/tag) cho 1 Short, khác content_seo.py (dành cho
Long, input là research brief + script master đầy đủ) -- Short chỉ có 1
đoạn kịch bản ngắn (đã qua short_content_review.py) làm input, tiêu đề
PHẢI ngắn hơn nhiều (khớp cách kênh đã đăng thủ công: câu khẳng định/câu
hỏi ngắn, KHÔNG đánh số tập, xem short_content_planner.py's phân tích thật
-- các short hiệu suất tốt đều không có số tập trong tiêu đề).

BẮT BUỘC: mọi Short phải có hashtag #Shorts trong mô tả/tag để YouTube xếp
đúng vào Shorts shelf (thiếu hashtag này có thể khiến video bị xử lý như
video thường, mất lợi thế thuật toán Shorts -- đã xác nhận qua audit trước
đây trong phiên: nguồn traffic áp đảo của kênh là từ mục Shorts).

Cùng mô hình soạn (agy) - phản biện (Codex), trần cứng MAX_ITERATIONS,
tái dùng thẳng các hàm helper của content_seo.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import _run_agy, _run_codex, _extract_json, ContentSeoError  # noqa: E402

MAX_ITERATIONS = 3

_DRAFT_PROMPT = """Bạn là chuyên gia SEO YouTube Shorts cho kênh {topic} tiếng Việt. Đọc kịch bản Short dưới đây, soạn tiêu đề + mô tả + tag.

=== KỊCH BẢN SHORT (đã tối ưu hook) ===
{script}

=== BỐI CẢNH (tập Long gốc, nếu có) ===
{context}
{revision_note}
YÊU CẦU BẮT BUỘC (khác Long):
- Tiêu đề: NGẮN (dưới 60 ký tự lý tưởng), là câu khẳng định/câu hỏi trực tiếp lấy Ý CHÍNH của kịch bản -- TUYỆT ĐỐI KHÔNG đánh số tập/không thêm "Short" vào tiêu đề.
- Mô tả: 1-2 câu ngắn gọn (Short không cần mô tả dài như Long), PHẢI có hashtag #Shorts.
- Tag: 5-8 từ khoá ngắn liên quan.

Trả về CHỈ 1 JSON object:
{{"title": "tiêu đề, không quá 70 ký tự", "description": "mô tả ngắn kèm #Shorts và 1-2 hashtag chủ đề khác", "tags": ["5-8 tag"]}}"""

_REVIEW_PROMPT = """Bạn là biên tập viên phản biện SEO Short cho kênh {topic} tiếng Việt. Tìm lỗi, không khen cho có.

=== KỊCH BẢN GỐC (để đối chiếu) ===
{script}

=== DRAFT SEO CẦN REVIEW ===
{draft}

Kiểm tra NGHIÊM: (1) tiêu đề có claim nào KHÔNG có trong kịch bản không (bịa/phóng đại), (2) tiêu đề có giật gân/clickbait sai lệch không, (3) mô tả có hashtag #Shorts chưa (BẮT BUỘC, nếu thiếu là FAIL), (4) tiêu đề có lỡ đánh số tập/thêm chữ "Short" không (không được có), (5) tag có spam không, (6) CHÍNH TẢ: đọc từng chữ trong tiêu đề/mô tả/hashtag, có từ nào viết sai/thiếu dấu/thiếu chữ cái không (vd hashtag bị cụt/thiếu chữ) -- lỗi chính tả dù nhỏ cũng là FAIL.

Trả về CHỈ 1 JSON object:
{{"verdict": "PASS" hoặc "FAIL", "feedback": "nếu FAIL, liệt kê CỤ THỂ; nếu PASS để rỗng"}}"""


def draft_short_seo(script: str, context: str = "", topic: str = "Phật giáo", revision_feedback: str | None = None) -> dict:
    revision_note = (
        f"\n=== PHẢN HỒI TỪ BIÊN TẬP VIÊN LẦN TRƯỚC -- BẮT BUỘC SỬA THEO ===\n{revision_feedback}\n"
        if revision_feedback else ""
    )
    prompt = _DRAFT_PROMPT.format(script=script, context=context or "(không có)", topic=topic, revision_note=revision_note)
    return _extract_json(_run_agy(prompt))


def review_short_seo(draft: dict, script: str, topic: str = "Phật giáo") -> dict:
    prompt = _REVIEW_PROMPT.format(script=script, draft=json.dumps(draft, ensure_ascii=False, indent=2), topic=topic)
    return _extract_json(_run_codex(prompt))


# BUG THẬT phát hiện khi rà soát trước khi mass-produce Phong Thuỷ (xem
# phiên làm việc): prompt draft/review TRƯỚC ĐÂY hardcode cứng "kênh Phật
# giáo tiếng Việt" -- chạy cho topic khác (Phong Thuỷ...) vẫn tự nhận là
# "chuyên gia SEO ... Phật giáo", có thể lệch tông/từ khoá dù script không
# liên quan gì tới Phật giáo. Tham số hoá theo topic, mặc định "Phật giáo"
# để không phá cron/launchd cũ chưa truyền topic.
def generate_short_seo_with_review(script: str, context: str = "", topic: str = "Phật giáo", max_iterations: int = MAX_ITERATIONS) -> dict:
    review_history = []
    draft = None
    feedback = None

    for i in range(1, max_iterations + 1):
        try:
            draft = draft_short_seo(script, context, topic=topic, revision_feedback=feedback)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: agy soạn SEO lỗi lần {i} ({exc}).", file=sys.stderr)
            review_history.append({"iteration": i, "stage": "draft", "error": str(exc)})
            continue

        try:
            review = review_short_seo(draft, script, topic=topic)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: codex review lỗi lần {i} ({exc}).", file=sys.stderr)
            review_history.append({"iteration": i, "draft": draft, "stage": "review", "error": str(exc)})
            continue

        review_history.append({"iteration": i, "draft": draft, "review": review})
        print(f"Vòng {i}/{max_iterations}: verdict={review.get('verdict')}", flush=True)

        if review.get("verdict") == "PASS":
            return {"seo": draft, "passed": True, "iterations_used": i, "review_history": review_history, "needs_human_review": False}
        feedback = review.get("feedback", "")

    print(f"CẢNH BÁO: sau {max_iterations} vòng vẫn chưa PASS -- dừng lại, cần người xem lại.", file=sys.stderr)
    return {"seo": draft, "passed": False, "iterations_used": max_iterations, "review_history": review_history, "needs_human_review": True}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--script-file", required=True)
    ap.add_argument("--context", default="")
    ap.add_argument("--topic", default="Phật giáo")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    script = Path(args.script_file).read_text(encoding="utf-8").strip()
    result = generate_short_seo_with_review(script, args.context, topic=args.topic)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {args.output} (passed={result['passed']})")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
