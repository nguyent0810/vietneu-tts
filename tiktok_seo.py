"""Sinh caption (không phải "title/description/tags" như YouTube) cho 1
Short đăng lên TikTok -- khác hẳn short_seo.py về CẤU TRÚC, không chỉ đổi
platform:

TikTok Content Posting API chỉ có ĐÚNG 1 field "title" (tối đa 2200 UTF-16
code unit, xem tiktok_upload.py::init_video_post) đóng vai trò caption đầy
đủ -- không có field description/tags riêng như YouTube. Hashtag (#) và
mention (@) nằm NGAY TRONG field đó, không phải mảng tag tách biệt (đã xác
nhận qua tài liệu chính thức developers.tiktok.com, không suy đoán).

Vì vậy KHÔNG tái dùng draft_short_seo() của short_seo.py rồi ghép
title+description lại -- thiết kế lại hoàn toàn: 1 caption ngắn (thực tế
100-300 ký tự đọc được là hợp lý dù giới hạn kỹ thuật 2200, vì TikTok là
nền tảng đọc lướt, caption dài không được đọc hết) + cụm hashtag cuối
caption, cùng mô hình soạn (agy) - phản biện (Codex) như short_seo.py để
giữ nhất quán về mức độ rigor, nhưng review prompt kiểm tra tiêu chí khác
(không kiểm tra #Shorts -- đó là quy ước riêng của YouTube, vô nghĩa trên
TikTok).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import _run_agy, _run_codex, _extract_json, ContentSeoError  # noqa: E402

MAX_ITERATIONS = 3
MAX_CAPTION_UTF16_UNITS = 2200  # giới hạn cứng của TikTok API, xem docstring

_DRAFT_PROMPT = """Bạn là chuyên gia caption TikTok cho kênh {topic} tiếng Việt. Đọc kịch bản Short dưới đây, soạn 1 caption TikTok đầy đủ (không phải tiêu đề YouTube).

=== KỊCH BẢN SHORT (đã tối ưu hook) ===
{script}

=== BỐI CẢNH (tập Long gốc, nếu có) ===
{context}
{revision_note}
YÊU CẦU BẮT BUỘC (TikTok KHÁC YouTube -- không áp dụng khuôn "tiêu đề + mô tả + tag" cũ):
- Đây là 1 CAPTION DUY NHẤT, không tách title/description riêng. Cấu trúc: 1 câu hook ngắn gọn lấy Ý CHÍNH kịch bản (giọng tự nhiên, gần gũi, phù hợp cách người dùng TikTok thật sự viết caption -- không phải giọng "tiêu đề báo" kiểu YouTube) + xuống dòng + cụm 4-6 hashtag liên quan ở cuối.
- Độ dài caption (kể cả hashtag) nên trong khoảng 80-280 ký tự -- KHÔNG viết dài như mô tả YouTube, TikTok là nền tảng đọc lướt, caption dài không được đọc hết. Giới hạn kỹ thuật cứng là 2200 ký tự nhưng KHÔNG dùng hết giới hạn đó làm mục tiêu.
- Hashtag: trộn 1-2 hashtag rộng (vd #phatgiao #phatphap) với 2-4 hashtag hẹp/cụ thể theo đúng chủ đề kịch bản (KHÔNG bịa hashtag không liên quan để câu view).
- KHÔNG đánh số tập, KHÔNG thêm chữ "Short"/"TikTok" vào caption.
- TUYỆT ĐỐI KHÔNG có claim nào ngoài kịch bản (không bịa/phóng đại nội dung giáo lý).

Trả về CHỈ 1 JSON object:
{{"caption": "toàn bộ caption kèm hashtag, đúng định dạng TikTok thật"}}"""

_REVIEW_PROMPT = """Bạn là biên tập viên phản biện caption TikTok cho kênh {topic} tiếng Việt. Tìm lỗi, không khen cho có.

=== KỊCH BẢN GỐC (để đối chiếu) ===
{script}

=== DRAFT CAPTION CẦN REVIEW ===
{draft}

Kiểm tra NGHIÊM: (1) caption có claim nào KHÔNG có trong kịch bản không (bịa/phóng đại nội dung giáo lý), (2) giọng văn có đúng kiểu caption TikTok tự nhiên không hay vẫn đọc như "tiêu đề YouTube" dán thêm hashtag, (3) độ dài có hợp lý (~80-280 ký tự) không, quá dài thì FAIL, (4) hashtag có liên quan thật tới nội dung không, có hashtag nào bịa/spam/không liên quan không, (5) có lỡ đánh số tập/thêm chữ "Short"/"TikTok" vào caption không, (6) CHÍNH TẢ: đọc từng chữ trong caption/hashtag, có từ nào viết sai/thiếu dấu/thiếu chữ cái không (vd hashtag bị cụt/thiếu chữ) -- lỗi chính tả dù nhỏ cũng là FAIL.

Trả về CHỈ 1 JSON object:
{{"verdict": "PASS" hoặc "FAIL", "feedback": "nếu FAIL, liệt kê CỤ THỂ; nếu PASS để rỗng"}}"""


def draft_tiktok_caption(script: str, context: str = "", topic: str = "Phật giáo", revision_feedback: str | None = None) -> dict:
    revision_note = (
        f"\n=== PHẢN HỒI TỪ BIÊN TẬP VIÊN LẦN TRƯỚC -- BẮT BUỘC SỬA THEO ===\n{revision_feedback}\n"
        if revision_feedback else ""
    )
    prompt = _DRAFT_PROMPT.format(script=script, context=context or "(không có)", topic=topic, revision_note=revision_note)
    return _extract_json(_run_agy(prompt))


def review_tiktok_caption(draft: dict, script: str, topic: str = "Phật giáo") -> dict:
    prompt = _REVIEW_PROMPT.format(script=script, draft=json.dumps(draft, ensure_ascii=False, indent=2), topic=topic)
    return _extract_json(_run_codex(prompt))


def generate_tiktok_caption_with_review(script: str, context: str = "", topic: str = "Phật giáo", max_iterations: int = MAX_ITERATIONS) -> dict:
    review_history = []
    draft = None
    feedback = None

    for i in range(1, max_iterations + 1):
        try:
            draft = draft_tiktok_caption(script, context, topic=topic, revision_feedback=feedback)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: agy soạn caption lỗi lần {i} ({exc}).", file=sys.stderr)
            review_history.append({"iteration": i, "stage": "draft", "error": str(exc)})
            continue

        caption = draft.get("caption", "") if isinstance(draft, dict) else ""
        if len(caption.encode("utf-16-le")) // 2 > MAX_CAPTION_UTF16_UNITS:
            print(f"CẢNH BÁO: caption vượt giới hạn cứng {MAX_CAPTION_UTF16_UNITS} UTF-16 code unit của TikTok -- loại vòng {i}.", file=sys.stderr)
            review_history.append({"iteration": i, "draft": draft, "stage": "hard_limit_check", "error": "caption vượt giới hạn TikTok"})
            feedback = f"Caption vừa soạn vượt giới hạn cứng {MAX_CAPTION_UTF16_UNITS} ký tự UTF-16 của TikTok -- PHẢI viết ngắn lại."
            continue

        try:
            review = review_tiktok_caption(draft, script, topic=topic)
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
    result = generate_tiktok_caption_with_review(script, args.context, topic=args.topic)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {args.output} (passed={result['passed']})")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
