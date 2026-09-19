"""
Sinh nội dung SEO (tiêu đề/mô tả/tag) cho 1 tập, từ 01_RESEARCH_BRIEF.md +
03_AUDIO_SCRIPT_MASTER.md -- theo mô hình "soạn - phản biện":

  agy   (Antigravity CLI) SOẠN draft đầu tiên (và sửa lại theo feedback).
  codex (Codex CLI)        PHẢN BIỆN draft đó: đúng nội dung nguồn không,
                            giọng điệu phù hợp domain (xem tham số domain_id/
                            context_label) không, có claim giật gân/sai lệch
                            không, SEO có hợp lý không.

QUAN TRỌNG -- tránh loop vô hạn (đã được nhắc trực tiếp trong phiên làm
việc): vòng lặp soạn-phản biện có trần cứng MAX_ITERATIONS. Nếu sau
MAX_ITERATIONS lần vẫn chưa PASS, KHÔNG lặp tiếp -- trả về draft gần nhất
kèm cờ needs_human_review=True và toàn bộ lịch sử phản biện, để người
thật quyết định thay vì để 2 agent tranh cãi nhau vô tận.

agy đảm nhiệm vai trò này (thay vì sinh ảnh) sau khi ComfyUI local thay
thế hoàn toàn agy cho nhánh IMAGE (xem asset_generation.py + comfyui_client.py) --
agy vẫn còn quota Google hạn chế, nhưng tác vụ text/soạn nội dung ít tốn
request hơn nhiều so với sinh ảnh hàng loạt.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# CODEX_BIN/node_subprocess_env() giờ resolve qua external_bin.py (module
# DUY NHẤT cho mọi binary ngoài, xem docstring ở đó) -- re-export tên cũ
# (_codex_subprocess_env) ở đây để KHÔNG phải sửa import ở nơi khác đã dùng
# "from content_seo import CODEX_BIN, _codex_subprocess_env"
# (content_review.py, codex_image_client.py).
from external_bin import CODEX_BIN, AGY_BIN, CURSOR_AGENT_BIN, node_subprocess_env as _codex_subprocess_env  # noqa: F401

AGY_TIMEOUT_S = 120
CURSOR_AGENT_TIMEOUT_S = 120
CODEX_TIMEOUT_S = 120
MAX_ITERATIONS = 3  # trần cứng -- KHÔNG được bỏ qua, xem docstring đầu file


class ContentSeoError(RuntimeError):
    pass


def _read_text(path) -> str:
    p = Path(path)
    if not p.exists():
        raise ContentSeoError(f"Không tìm thấy file: {path}")
    return p.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    """agy/codex đôi khi bọc JSON trong ```json fences hoặc lặp lại câu trả
    lời (xem ghi chú _run_codex) -- tìm khối {...} NGOÀI CÙNG đầu tiên
    thay vì json.loads() thẳng cả chuỗi.

    BUG THẬT phát hiện qua Codex CLI review độc lập: regex cũ r"\\{.*\\}"
    (greedy, re.S) khớp từ dấu { ĐẦU TIÊN tới dấu } CUỐI CÙNG trong toàn bộ
    text -- nếu phản hồi chứa NHIỀU khối {...} tách biệt (vd model in ví dụ
    JSON minh hoạ trước khi trả lời thật, hoặc lặp lại câu trả lời 2 lần),
    2 khối bị ghép lại thành 1 chuỗi hỏng dù từng khối riêng lẻ hợp lệ. Thay
    bằng quét đếm độ sâu ngoặc {} có nhận biết chuỗi (bỏ qua { } nằm trong
    "..." kể cả có \\" escape) để tìm ĐÚNG khối {...} cân bằng ĐẦU TIÊN."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    if start == -1:
        raise ContentSeoError(f"Không tìm thấy JSON trong phản hồi: {text[:300]}")
    depth = 0
    in_string = False
    escape = False
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise ContentSeoError(f"Không tìm thấy khối JSON {{...}} cân bằng dấu ngoặc trong phản hồi: {text[:300]}")
    candidate = text[start:end + 1]
    # BUG THẬT phát hiện khi chạy twelve_gods_short_generator.py: agy/codex
    # đôi khi trả JSON hỏng thật sự (dấu ngoặc kép chưa đóng bên trong 1
    # script tiếng Việt, output bị cắt ngang...) -- json.loads() raise
    # JSONDecodeError thẳng, KHÔNG phải ContentSeoError, nên mọi caller có
    # "except ContentSeoError" (retry vòng sau) không bắt được, crash cả
    # tiến trình thay vì thử lại. Bọc lại thành ContentSeoError để hành vi
    # retry-an-toàn đã thiết kế thực sự hoạt động.
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ContentSeoError(f"JSON hỏng trong phản hồi ({exc}): {candidate[:500]}") from exc


def _run_agy(prompt: str) -> str:
    """Fallback sang Codex nếu agy chưa cài/lỗi/hết quota (pool TEXT của
    agy có thể cạn riêng, đã gặp thật khi xử lý EP006 -- "Individual quota
    reached... Resets in ~160h"). Đánh đổi: mất tính "2 góc nhìn độc lập"
    (soạn agy, phản biện Codex) khi cả soạn lẫn phản biện đều là Codex,
    nhưng vẫn còn hơn dừng hẳn cả pipeline SEO."""
    if AGY_BIN.exists():
        try:
            result = subprocess.run([str(AGY_BIN), "-p", prompt], capture_output=True, text=True, timeout=AGY_TIMEOUT_S)
            if result.returncode == 0:
                return result.stdout
            print(f"CẢNH BÁO: agy lỗi (exit {result.returncode}) -- thử Codex.", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"CẢNH BÁO: agy timeout sau {AGY_TIMEOUT_S}s -- thử Codex.", file=sys.stderr)
    return _run_codex(prompt)


def _run_codex(prompt: str) -> str:
    """codex exec in ra 1 banner (workdir/model/session...) rồi lặp lại nội
    dung câu trả lời 2 lần (ngay sau marker 'codex' VÀ lần nữa ở cuối sau
    'tokens used') -- lấy đoạn ĐẦU TIÊN giữa 2 marker đó, ổn định hơn lấy
    dòng cuối cùng (dễ lẫn với số token).

    Fallback sang _run_cursor (vendor độc lập thứ 3, KHÔNG phải agy) khi
    Codex lỗi/hết quota -- xác nhận thật 2026-08-22: "You've hit your usage
    limit... try again at Aug 27th". Cố ý KHÔNG fallback sang agy ở đây:
    _run_codex đóng vai trò PHẢN BIỆN độc lập với agy (bên soạn) trong toàn
    bộ pipeline SEO/C4 fact-check -- nếu agy vừa soạn vừa tự chấm điểm luôn
    thì lớp kiểm tra độc lập coi như vô nghĩa. cursor-agent (Grok, vendor
    thứ 3) giữ đúng tính độc lập đó."""
    try:
        result = subprocess.run(
            [CODEX_BIN, "exec", prompt], capture_output=True, text=True, timeout=CODEX_TIMEOUT_S,
            env=_codex_subprocess_env(),
        )
    except subprocess.TimeoutExpired:
        print(f"CẢNH BÁO: codex timeout sau {CODEX_TIMEOUT_S}s -- thử cursor-agent.", file=sys.stderr)
        return _run_cursor(prompt)
    except FileNotFoundError:
        raise ContentSeoError("Chưa cài Codex CLI (npm install -g @openai/codex).")
    if result.returncode != 0:
        print(f"CẢNH BÁO: codex lỗi (exit {result.returncode}) -- thử cursor-agent.", file=sys.stderr)
        return _run_cursor(prompt)

    stdout = result.stdout
    match = re.search(r"\ncodex\n(.*?)\ntokens used\n", stdout, re.S)
    return match.group(1).strip() if match else stdout.strip()


def _run_cursor(prompt: str) -> str:
    """cursor-agent (xAI/Grok) -- vendor độc lập thứ 3 ngoài agy/Gemini và
    Codex/GPT. Từ 2026-08-22: _run_codex TỰ ĐỘNG fallback vào đây khi Codex
    hết quota (xem docstring _run_codex) -- không còn "không dùng làm mặc
    định" như trước, đây LÀ đường dự phòng đang hoạt động thật cho tới khi
    Codex phục hồi (dự kiến 27/08). KHÔNG có fallback nội bộ tiếp theo --
    nếu cursor-agent cũng lỗi, fail-closed thẳng ra caller (không rơi xuống
    agy, xem lý do ở _run_codex).

    model "auto" (không phải "cursor-grok-4.5-high"): plan hiện tại của
    account chỉ cho phép model "Auto" ("Named models unavailable... Free
    plans can only use Auto" khi thử model cụ thể, xác nhận thật 2026-08-22).

    --output-format text: trả thẳng nội dung câu trả lời (không banner như
    codex exec), không cần regex tách như _run_codex ở trên."""
    if not CURSOR_AGENT_BIN.exists():
        raise ContentSeoError(f"Chưa cài cursor-agent CLI (không thấy tại {CURSOR_AGENT_BIN}).")
    try:
        result = subprocess.run(
            [str(CURSOR_AGENT_BIN), "-p", prompt, "--model", "auto", "--output-format", "text"],
            capture_output=True, text=True, timeout=CURSOR_AGENT_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        raise ContentSeoError(f"cursor-agent timeout sau {CURSOR_AGENT_TIMEOUT_S}s.")
    except FileNotFoundError:
        raise ContentSeoError("Chưa cài cursor-agent CLI.")
    if result.returncode != 0:
        raise ContentSeoError(f"cursor-agent lỗi (exit {result.returncode}): {result.stderr[-500:] or result.stdout[-500:]}")
    return result.stdout.strip()



# Audit kênh Hình Sự (2026-08-14): 2 bug thật phát hiện cùng lúc trong
# module này khi soạn thumbnail hấp dẫn hơn --
#
# (1) THIẾU field "thumbnail_text": thumbnail_generator.py's generate_thumbnail()
# vốn được thiết kế để nhận 1 tiêu đề THUMBNAIL RIÊNG, rút gọn (<=6-8 từ,
# xem docstring của nó) -- nhưng schema JSON ở đây chưa từng có field này,
# nên long_batch_runner.py's fallback `entry["seo"].get("thumbnail_text") or
# entry["seo"]["title"]` LUÔN rơi vào nhánh fallback, dùng nguyên TIÊU ĐỀ
# VIDEO ĐẦY ĐỦ (thường 10-12 từ dạng câu hỏi) làm chữ thumbnail -- xác nhận
# qua chính EP001 CL: thumbnail thật hiện nguyên "VÌ SAO KÊNH KHÔNG GỌI AI
# LÀ HUNG THỦ TRƯỚC KHI TÒA TUYÊN ÁN?" tràn 3 dòng, rất khó đọc ở kích
# thước preview nhỏ. Thêm field "thumbnail_text" vào schema, sinh SONG SONG
# với titles/description/tags (cùng 1 lượt gọi LLM, không tốn thêm request).
#
# (2) Prompt CỨNG "kênh Phật giáo/tâm linh" bất kể domain THẬT gọi module
# này -- content_seo.py không hề nhận tham số domain, nên khi FS/CL gọi qua
# `long_batch_runner.py`, LLM vẫn được bảo là đang viết SEO cho kênh Phật
# giáo. Output thực tế của CL EP001 (đã kiểm tra) tình cờ vẫn đúng chủ đề
# pháp lý -- LLM có vẻ ưu tiên nội dung script/brief thật hơn vai trò được
# gán nhầm -- nhưng đây là hành vi KHÔNG được đảm bảo, chỉ là may mắn, không
# nên tiếp tục dựa vào đó. Sửa bằng field context_label (đã có sẵn cho từng
# domain trong domain_creative_profiles.json, tái dùng nguyên -- không tạo
# thêm nguồn sự thật mới) truyền qua tham số domain_id, mặc định "BUD" để
# giữ đúng hành vi cũ khi gọi không truyền gì (mọi call site cũ vẫn chạy y
# hệt trước khi có fix này).
def _context_label_for_domain(domain_id: str) -> str:
    import domain_creative_profiles as _cp
    return _cp.load_profile(domain_id).get("context_label", "Phật giáo/tâm linh")


_DRAFT_PROMPT_TEMPLATE = """Bạn là chuyên gia SEO YouTube cho kênh {context_label} tiếng Việt. Đọc kịch bản dưới đây, soạn nội dung mô tả video.

=== RESEARCH BRIEF ===
{brief}

=== KỊCH BẢN ĐẦY ĐỦ ===
{script}
{revision_note}
Trả về CHỈ 1 JSON object (không markdown, không giải thích thêm), đúng schema:
{{
  "titles": ["3-5 lựa chọn tiêu đề, mỗi cái <=70 ký tự, không giật gân/clickbait sai sự thật"],
  "thumbnail_text": "Tiêu đề RIÊNG cho ảnh thumbnail, RÚT GỌN, KHÔNG PHẢI trùng titles ở trên -- tối đa 6-8 từ, gây tò mò nhưng ĐÚNG nội dung (không giật tít sai sự thật), đủ ngắn để đọc được ở kích thước preview nhỏ trên điện thoại (vừa trong 1-2 dòng, không phải câu hỏi đầy đủ dài dòng)",
  "description": "mô tả video 2-3 đoạn, trung thực với nội dung, có gợi ý hành động nhẹ nhàng ở cuối",
  "tags": ["8-15 từ khoá SEO liên quan, tiếng Việt"]
}}"""

_REVIEW_PROMPT_TEMPLATE = """Bạn là biên tập viên phản biện (adversarial reviewer) cho nội dung SEO 1 video {context_label} tiếng Việt. Nhiệm vụ: tìm lỗi, không phải khen.

=== RESEARCH BRIEF (nguồn gốc, để đối chiếu) ===
{brief}

=== DRAFT SEO CẦN REVIEW ===
{draft}

Kiểm tra NGHIÊM: (1) tiêu đề/mô tả/thumbnail_text có claim nào KHÔNG có trong Research Brief không (bịa đặt/phóng đại), (2) có giật gân/clickbait/gây hoang mang không, (3) có ngôn ngữ đảm bảo kết quả cụ thể không (vd "làm X chắc chắn được Y" -- vi phạm nguyên tắc không transactional), (4) tag có spam/không liên quan không, (5) thumbnail_text có thật sự ngắn gọn (<=6-8 từ) và khác titles không, hay chỉ chép lại nguyên 1 title dài.

Trả về CHỈ 1 JSON object:
{{"verdict": "PASS" hoặc "FAIL", "feedback": "nếu FAIL, liệt kê CỤ THỂ từng lỗi và cách sửa; nếu PASS, để rỗng"}}"""


def draft_seo_content(research_brief: str, script_master: str, revision_feedback: str | None = None, domain_id: str = "BUD") -> dict:
    revision_note = (
        f"\n=== PHẢN HỒI TỪ BIÊN TẬP VIÊN Ở LẦN TRƯỚC -- BẮT BUỘC SỬA THEO ===\n{revision_feedback}\n"
        if revision_feedback else ""
    )
    prompt = _DRAFT_PROMPT_TEMPLATE.format(
        brief=research_brief[:8000], script=script_master[:15000], revision_note=revision_note,
        context_label=_context_label_for_domain(domain_id),
    )
    return _extract_json(_run_agy(prompt))


def review_seo_content(draft: dict, research_brief: str, domain_id: str = "BUD") -> dict:
    prompt = _REVIEW_PROMPT_TEMPLATE.format(
        brief=research_brief[:8000], draft=json.dumps(draft, ensure_ascii=False, indent=2),
        context_label=_context_label_for_domain(domain_id),
    )
    return _extract_json(_run_codex(prompt))


_MAX_THUMBNAIL_TEXT_WORDS = 10  # prompt yêu cầu 6-8 -- nới nhẹ để không loại oan bản hợp lý xém ngưỡng


def _thumbnail_text_problem(draft: dict) -> str | None:
    """Kiểm tra CỨNG, đếm được -- không giao hẳn cho LLM review phán đoán
    (Cursor review Part 2: review prompt CHỈ nhờ LLM chấm điểm tiêu chí #5,
    'soft' -- nếu cả agy lẫn codex cùng bỏ sót/đồng ý nhầm 1 draft thiếu/dài
    thumbnail_text, long_batch_runner.py's fallback `.get("thumbnail_text")
    or entry["seo"]["title"]` sẽ lặng lẽ tái diễn đúng bug EP001 gốc). Trả
    về chuỗi mô tả lỗi CỤ THỂ (dùng làm feedback bắt buộc sửa ở vòng sau) hoặc
    None nếu hợp lệ."""
    text = draft.get("thumbnail_text")
    if not text or not str(text).strip():
        return 'Thiếu field "thumbnail_text" (hoặc để rỗng) -- BẮT BUỘC phải có, xem schema.'
    text = str(text).strip()
    n_words = len(text.split())
    if n_words > _MAX_THUMBNAIL_TEXT_WORDS:
        return f'"thumbnail_text" dài {n_words} từ, vượt quá {_MAX_THUMBNAIL_TEXT_WORDS} từ cho phép -- rút gọn lại, đây là chữ hiển thị trên ảnh thumbnail nhỏ, không phải tiêu đề video.'
    if text in (draft.get("titles") or []):
        return '"thumbnail_text" đang TRÙNG NGUYÊN VĂN 1 trong các titles -- phải là bản RÚT GỌN RIÊNG, không phải copy lại 1 title dài.'
    return None


def generate_seo_with_review(research_brief_path: str, script_master_path: str, max_iterations: int = MAX_ITERATIONS, domain_id: str = "BUD") -> dict:
    """Vòng soạn (agy) - phản biện (codex), trần cứng max_iterations --
    KHÔNG BAO GIỜ lặp vô hạn. Trả về:
    {seo, passed, iterations_used, review_history, needs_human_review}"""
    research_brief = _read_text(research_brief_path)
    script_master = _read_text(script_master_path)

    review_history = []
    draft = None
    feedback = None

    for i in range(1, max_iterations + 1):
        try:
            draft = draft_seo_content(research_brief, script_master, revision_feedback=feedback, domain_id=domain_id)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: agy soạn draft lỗi lần {i} ({exc}).", file=sys.stderr)
            review_history.append({"iteration": i, "stage": "draft", "error": str(exc)})
            continue

        thumb_problem = _thumbnail_text_problem(draft)
        if thumb_problem is not None:
            print(f"Vòng {i}/{max_iterations}: FAIL cứng (kiểm tra đếm được, không qua LLM review) -- {thumb_problem}", flush=True)
            review_history.append({
                "iteration": i, "draft": draft,
                "review": {"verdict": "FAIL", "feedback": thumb_problem, "source": "hard_check_thumbnail_text"},
            })
            feedback = thumb_problem
            continue

        try:
            review = review_seo_content(draft, research_brief, domain_id=domain_id)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: codex review lỗi lần {i} ({exc}) -- coi như chưa review được, thử lại.", file=sys.stderr)
            review_history.append({"iteration": i, "draft": draft, "stage": "review", "error": str(exc)})
            continue

        review_history.append({"iteration": i, "draft": draft, "review": review})
        print(f"Vòng {i}/{max_iterations}: verdict={review.get('verdict')}", flush=True)

        if review.get("verdict") == "PASS":
            return {
                "seo": draft, "passed": True, "iterations_used": i,
                "review_history": review_history, "needs_human_review": False,
            }
        feedback = review.get("feedback", "")

    # Hết max_iterations mà vẫn chưa PASS -- DỪNG LẠI, không lặp thêm. Trả
    # bản draft gần nhất kèm cờ rõ ràng cho người review thay vì tự quyết.
    print(f"CẢNH BÁO: sau {max_iterations} vòng vẫn chưa PASS -- dừng lại, cần người xem lại thủ công.", file=sys.stderr)
    return {
        "seo": draft, "passed": False, "iterations_used": max_iterations,
        "review_history": review_history, "needs_human_review": True,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--research-brief", required=True)
    ap.add_argument("--script-master", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS)
    ap.add_argument("--domain", default="BUD", help="domain_id (BUD/FS/CL) -- quyết định context_label trong prompt SEO, xem domain_creative_profiles.json. Mặc định BUD giữ đúng hành vi cũ khi không truyền.")
    args = ap.parse_args()

    result = generate_seo_with_review(args.research_brief, args.script_master, args.max_iterations, domain_id=args.domain)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if result["needs_human_review"]:
        print(f"CẦN NGƯỜI XEM LẠI: {args.output} (chưa qua được review sau {result['iterations_used']} vòng)")
        return 1
    print(f"OK: {args.output} (PASS sau {result['iterations_used']} vòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
