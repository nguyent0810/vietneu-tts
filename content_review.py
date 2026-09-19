"""
Phản biện nội dung kịch bản audio (03_AUDIO_SCRIPT_MASTER.md) ĐÃ VIẾT SẴN --
khác content_seo.py (soạn từ đầu), ở đây kịch bản đã tồn tại (qua audit cấu
trúc `package_audit.py` của Content-Creator, nhưng KHÔNG qua kiểm tra
đúng-sai giáo lý -- đây chính là khoảng trống module này lấp).

Quy trình:
  1. codex REVIEW toàn bộ phần narration (giữa NARRATION_START/END) đối
     chiếu với các quy tắc an toàn Phật giáo cụ thể (Death and Grief Rule,
     Merit Rule, Filial Piety Rule, Continuity Registry) -- trả về danh
     sách lỗi CỤ THỂ (trích đúng câu, lý do, hướng sửa), không phải chung
     chung.
  2. Nếu có lỗi: agy SỬA CÓ MỤC TIÊU -- chỉ đổi đúng những câu bị flag,
     giữ NGUYÊN VĂN mọi phần còn lại (không viết lại từ đầu cả kịch bản --
     rủi ro làm trôi giọng văn/độ dài/các quyết định biên tập đã có).
  3. codex review lại bản đã sửa, lặp tới khi PASS hoặc hết MAX_ITERATIONS
     -- TRẦN CỨNG, không lặp vô hạn (cùng nguyên tắc content_seo.py).

KHÔNG THAY THẾ người thật rà lại nội dung tôn giáo nhạy cảm -- đây là lớp
lọc tự động bổ sung trước/song song, đúng như khuyến nghị ban đầu khi viết
EP007 ("nên có người thật rà lại đoạn cảnh báo sát sinh và nhịp kể tang lễ").
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from content_seo import CODEX_BIN, _codex_subprocess_env  # resolve "codex"/"node" bare-name an toàn dưới launchd, xem ghi chú ở đó
from external_bin import AGY_BIN  # noqa: F401 -- gom về 1 nguồn duy nhất (xem docstring ở đó)

MAX_ITERATIONS = 3  # trần cứng -- xem docstring đầu file

AGY_TIMEOUT_S = 180
CODEX_TIMEOUT_S = 150

_NARRATION_RE = re.compile(r"<!-- NARRATION_START -->\n(.*?)\n<!-- NARRATION_END -->", re.S)

_SAFETY_RULES = """
QUY TẮC AN TOÀN BẮT BUỘC (Death and Grief Rule, Merit Rule, Filial Piety Rule -- BUDDHIST_GUIDE.md):
- KHÔNG khẳng định chắc chắn trạng thái/nơi tái sinh cụ thể của 1 người đã mất.
- KHÔNG ngụ ý 1 hành động nghi lễ đơn lẻ kiểm soát hoàn toàn số phận người mất.
- KHÔNG làm tăng cảm giác tội lỗi cho người đang đau buồn.
- KHÔNG dùng ngôn ngữ đảm bảo kết quả kiểu "làm X thì chắc chắn được Y" (transactional).
- KHÔNG bịa tên nhân vật/thuật ngữ không có trong nguồn (Knowledge Packet).
- KHÔNG trích dẫn kinh văn như lời nguyên văn xác thực nếu không chắc chắn 100%.

RANH GIỚI ÁP DỤNG QUY TẮC -- ĐỌC KỸ TRƯỚC KHI GẮN CỜ BẤT KỲ CÂU NÀO:
Các quy tắc trên áp dụng cho GIỌNG CỦA NGƯỜI DẪN CHUYỆN khi tự đưa ra cam
kết/khẳng định VỚI NGƯỜI XEM về tình huống CỤ THỂ của họ -- KHÔNG áp dụng
cho việc THUẬT LẠI đúng nội dung giáo lý mà kinh văn tự dạy (dù nội dung
giáo lý đó, đọc tách rời, nghe có vẻ "chắc chắn"). Thuật lại 1 nguyên lý
kinh dạy (vd "kinh nói người mất chỉ nhận một phần trong bảy") là NGỮ ĐIỆU
TƯỜNG THUẬT hợp lệ, không phải người kể tự đảm bảo kết quả -- MIỄN LÀ:
  (a) câu đó được gắn nguồn rõ ràng (có "kinh nói", "theo lời kinh", "kinh
      dạy", hoặc nằm liền mạch trong 1 đoạn đã mở đầu bằng cách gắn nguồn
      như vậy), HOẶC
  (b) có 1 câu disclaimer/rào chắn Ở GẦN ĐÓ (cùng đoạn, đoạn trước, hoặc
      đoạn sau trong TOÀN BỘ kịch bản, không chỉ trong đúng câu đang xét)
      đã làm rõ đây là nguyên lý truyền thống, không phải cam kết cho
      từng trường hợp cá nhân cụ thể.
CHỈ gắn cờ 1 câu nếu: câu đó (1) tự đứng độc lập như 1 lời hứa/cam kết của
NGƯỜI DẪN CHUYỆN nói thẳng với người xem về HỌ/người thân CỤ THỂ của HỌ,
VÀ (2) không có disclaimer nào ở gần đủ để làm rõ ý nghĩa truyền thống của
nó. Trước khi thêm 1 finding, PHẢI tự kiểm tra và ghi rõ trong "issue": đã
tìm disclaimer gần đó chưa, vì sao câu này vẫn không được coi là đã đủ rào
chắn.
"""

_REVIEW_PROMPT_TEMPLATE = """Bạn là biên tập viên phản biện nội dung tôn giáo (Phật giáo) cho kịch bản audio tiếng Việt. Nhiệm vụ: tìm lỗi vi phạm quy tắc an toàn THẬT SỰ, không phải nhặt lỗi hình thức của việc thuật lại giáo lý.
{rules}
=== KỊCH BẢN CẦN REVIEW (đọc TOÀN BỘ trước khi kết luận bất kỳ câu nào, vì disclaimer có thể nằm ở đoạn khác) ===
{script}

Đọc kỹ TOÀN VĂN trước, xác định các đoạn disclaimer/rào chắn đã có sẵn (vd "không ai dám nói chắc...", "không một nghi lễ nào bảo đảm..."). Sau đó tìm TỪNG câu (nếu có) THẬT SỰ vi phạm quy tắc theo đúng ranh giới đã nêu (là cam kết của người kể tới người xem, KHÔNG phải thuật lại giáo lý có gắn nguồn hoặc đã có disclaimer gần đó). Trả về CHỈ 1 JSON object:
{{
  "verdict": "PASS" hoặc "FAIL",
  "findings": [
    {{"quote": "trích ĐÚNG NGUYÊN VĂN câu vi phạm từ kịch bản", "issue": "vi phạm quy tắc nào, vì sao KHÔNG được coi là thuật lại giáo lý hợp lệ hay đã có disclaimer gần đó che", "suggested_fix": "hướng sửa cụ thể, tối thiểu, không viết lại cả câu nếu không cần"}}
  ]
}}
Nếu PASS, "findings" để mảng rỗng []. Ưu tiên PASS nếu chỉ có nghi ngờ nhẹ -- chỉ FAIL khi thật sự chắc chắn có vi phạm rõ ràng."""

_REVISE_PROMPT_TEMPLATE = """Bạn đang sửa 1 đoạn kịch bản audio Phật giáo tiếng Việt theo phản hồi biên tập. QUAN TRỌNG: CHỈ sửa đúng những câu bị chỉ ra lỗi bên dưới -- giữ NGUYÊN VĂN TUYỆT ĐỐI mọi câu/đoạn khác, không viết lại giọng văn, không rút gọn, không thêm bớt ý ngoài phạm vi sửa lỗi.

=== KỊCH BẢN GỐC ===
{script}

=== DANH SÁCH LỖI CẦN SỬA ===
{findings}

Trả về CHỈ nội dung kịch bản ĐÃ SỬA (không markdown, không giải thích, không JSON) -- toàn văn, giữ nguyên format đoạn văn gốc, chỉ thay đổi đúng phần bị flag theo hướng sửa đã gợi ý."""


class ContentReviewError(RuntimeError):
    pass


def _extract_narration(script_text: str) -> tuple[str, int, int]:
    match = _NARRATION_RE.search(script_text)
    if not match:
        raise ContentReviewError("Không tìm thấy NARRATION_START/END trong script.")
    return match.group(1), match.start(1), match.end(1)


def _extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ContentReviewError(f"Không tìm thấy JSON trong phản hồi: {text[:300]}")
    return json.loads(match.group(0))


def _run_agy(prompt: str) -> str:
    """Fallback sang Codex nếu agy chưa cài/lỗi/hết quota (cùng lý do đã gặp
    thật ở content_seo.py -- pool TEXT của agy cạn riêng biệt với pool ẢNH,
    "Individual quota reached... Resets in ~160h"). Mất tính độc lập 2 góc
    nhìn (agy sửa, codex review) khi cả 2 bước đều là Codex, nhưng còn hơn
    chặn đứng cả bước phản biện an toàn nội dung."""
    if AGY_BIN.exists():
        try:
            result = subprocess.run([str(AGY_BIN), "-p", prompt], capture_output=True, text=True, timeout=AGY_TIMEOUT_S)
            if result.returncode == 0:
                return result.stdout.strip()
            print(f"CẢNH BÁO: agy lỗi (exit {result.returncode}) -- thử Codex.", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"CẢNH BÁO: agy timeout sau {AGY_TIMEOUT_S}s -- thử Codex.", file=sys.stderr)
    return _run_codex(prompt)


def _run_codex(prompt: str) -> str:
    try:
        result = subprocess.run([CODEX_BIN, "exec", prompt], capture_output=True, text=True, timeout=CODEX_TIMEOUT_S,
                                 env=_codex_subprocess_env())
    except subprocess.TimeoutExpired:
        raise ContentReviewError(f"codex timeout sau {CODEX_TIMEOUT_S}s.")
    except FileNotFoundError:
        raise ContentReviewError("Chưa cài Codex CLI.")
    if result.returncode != 0:
        raise ContentReviewError(f"codex lỗi (exit {result.returncode}): {result.stderr[-500:] or result.stdout[-500:]}")
    match = re.search(r"\ncodex\n(.*?)\ntokens used\n", result.stdout, re.S)
    return (match.group(1).strip() if match else result.stdout.strip())


def review_narration(narration_text: str) -> dict:
    prompt = _REVIEW_PROMPT_TEMPLATE.format(rules=_SAFETY_RULES, script=narration_text)
    return _extract_json(_run_codex(prompt))


def revise_narration(narration_text: str, findings: list[dict]) -> str:
    prompt = _REVISE_PROMPT_TEMPLATE.format(script=narration_text, findings=json.dumps(findings, ensure_ascii=False, indent=2))
    return _run_agy(prompt)


def review_and_fix_script(script_master_path: str, max_iterations: int = MAX_ITERATIONS, write_back: bool = False) -> dict:
    """Trả về {passed, iterations_used, review_history, needs_human_review,
    final_narration}. Nếu write_back=True VÀ passed=True, ghi narration đã
    sửa ngược lại file gốc (giữ nguyên frontmatter/Editorial Notes, chỉ
    thay phần giữa NARRATION_START/END) -- mặc định False, chỉ báo cáo,
    không tự sửa file mà không có xác nhận."""
    full_text = Path(script_master_path).read_text(encoding="utf-8")
    narration, start_idx, end_idx = _extract_narration(full_text)

    review_history = []
    current = narration

    for i in range(1, max_iterations + 1):
        try:
            review = review_narration(current)
        except ContentReviewError as exc:
            print(f"CẢNH BÁO: codex review lỗi lần {i} ({exc}).", file=sys.stderr)
            review_history.append({"iteration": i, "stage": "review", "error": str(exc)})
            continue

        review_history.append({"iteration": i, "review": review, "narration_snapshot": current})
        n_findings = len(review.get("findings", []))
        print(f"Vòng {i}/{max_iterations}: verdict={review.get('verdict')}, {n_findings} lỗi.", flush=True)

        if review.get("verdict") == "PASS":
            if write_back:
                new_full = full_text[:start_idx] + current + full_text[end_idx:]
                Path(script_master_path).write_text(new_full, encoding="utf-8")
            return {
                "passed": True, "iterations_used": i, "review_history": review_history,
                "needs_human_review": False, "final_narration": current,
            }

        if i == max_iterations:
            break

        try:
            current = revise_narration(current, review["findings"])
        except ContentReviewError as exc:
            print(f"CẢNH BÁO: agy sửa lỗi lần {i} ({exc}) -- giữ nguyên bản trước, dừng vòng lặp.", file=sys.stderr)
            break

    print(f"CẢNH BÁO: sau {max_iterations} vòng vẫn chưa PASS -- dừng lại, cần người xem lại thủ công.", file=sys.stderr)
    return {
        "passed": False, "iterations_used": len(review_history), "review_history": review_history,
        "needs_human_review": True, "final_narration": current,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--script-master", required=True)
    ap.add_argument("--output", required=True, help="File JSON báo cáo kết quả review")
    ap.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS)
    ap.add_argument("--write-back", action="store_true", help="Ghi bản đã sửa (nếu PASS) ngược lại chính script-master")
    args = ap.parse_args()

    result = review_and_fix_script(args.script_master, args.max_iterations, write_back=args.write_back)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if result["needs_human_review"]:
        print(f"CẦN NGƯỜI XEM LẠI: {args.output} (chưa PASS sau {result['iterations_used']} vòng)")
        return 1
    print(f"OK: {args.output} (PASS sau {result['iterations_used']} vòng, write_back={args.write_back})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
