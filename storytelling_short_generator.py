"""Sinh nội dung Short "Giai thoại/Lịch sử/Truyền thuyết Phong Thuỷ-Tử Vi"
cho kênh Phong Thuỷ -- CATEGORY 5 (Storytelling, xem content_categories.py).
KHÁC educational_short_generator.py (Category 2, mục tiêu GIẢI THÍCH khái
niệm): mục tiêu ở đây là KỂ CHUYỆN có hook mạnh/giá trị xem cao, dựa trên
CÙNG kho SOURCES thật (content_repo_clone/.../SOURCES/) nhưng trích góc
GIAI THOẠI/NHÂN VẬT/LỊCH SỬ thay vì khái niệm khô khan -- 2 giai đoạn
extract+generate, cache/merge/retry-lỗi topic bank dùng CHUNG topic_bank.py
với educational_short_generator.py (không copy lại logic cache, chỉ đổi
prompt trích chủ đề + judge rubric sang Category 5)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import _run_agy, _extract_json  # noqa: E402
import content_invariant  # noqa: E402
import content_quality_gate as cqg  # noqa: E402
import script_quality_gate as sqg  # noqa: E402
import short_judge_panel_engine  # noqa: E402
from short_judge_panel_engine import generate_verified_script  # noqa: E402
import topic_bank  # noqa: E402
import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.STORYTELLING  # xem content_categories.py
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
TOPIC_BANK_PATH = Path(__file__).parent / "chunks_cache" / "fs_storytelling_topic_bank.json"
SOURCES_DIR = Path(__file__).parent / "content_repo_clone" / "DOMAINS" / "FENG_SHUI" / "SOURCES"
TOPICS_PER_SOURCE = 4
MAX_SOURCE_CHARS = 14000

_EXTRACT_TOPICS_PROMPT = """Bạn đang chuẩn bị chất liệu KỂ CHUYỆN cho 1 chuỗi Short-form (~20-30 giây/video) Phong Thuỷ/Tử Vi tiếng Việt, dựa trên research draft dưới đây.

=== RESEARCH DRAFT ===
{source_text}

Đề xuất ĐÚNG {n_topics} GÓC KỂ CHUYỆN (KHÔNG PHẢI khái niệm khô khan) từ draft trên -- ưu tiên: giai thoại/nguồn gốc lịch sử, nhân vật cụ thể được nhắc tới, câu chuyện minh hoạ, tình huống "nếu... thì sao" có thể dựng từ ý trong draft. Mỗi góc phải có YẾU TỐ TỰ SỰ (nhân vật/tình huống/diễn biến), không chỉ là định nghĩa.

Với MỖI góc, trích ĐOẠN VĂN NGUYÊN VẸN từ chính draft (copy chính xác, 3-8 câu) làm căn cứ, và ghi rõ is_hypothetical=true nếu góc đó là tình huống GIẢ ĐỊNH (không phải sự kiện lịch sử có thật), false nếu là giai thoại/lịch sử thật theo draft.

Trả về CHỈ 1 JSON object:
{{"topics": [{{"title": "tiêu đề ngắn gọn", "excerpt": "đoạn trích nguyên văn", "is_hypothetical": true hoặc false}}, ...]}} (đúng {n_topics} phần tử, càng ít càng bỏ qua chủ đề không đủ chất liệu tự sự thay vì gượng ép)"""


def extract_topic_bank(source_path: Path, n_topics: int = TOPICS_PER_SOURCE) -> list[dict]:
    source_text = source_path.read_text(encoding="utf-8")[:MAX_SOURCE_CHARS]
    prompt = _EXTRACT_TOPICS_PROMPT.format(source_text=source_text, n_topics=n_topics)
    result = _extract_json(_run_agy(prompt))
    topics = result["topics"]
    for t in topics:
        t["source_file"] = source_path.name
    return topics


def build_full_topic_bank(force_refresh: bool = False) -> dict:
    return topic_bank.build_full_topic_bank(TOPIC_BANK_PATH, SOURCES_DIR, extract_topic_bank, force_refresh=force_refresh)


def next_unused_topic() -> dict | None:
    build_full_topic_bank()  # cache/merge/retry-lỗi do topic_bank.py đảm nhiệm, xem module đó
    return topic_bank.next_unused_topic(TOPIC_BANK_PATH)


def mark_topic_used(title: str) -> None:
    topic_bank.mark_topic_used(TOPIC_BANK_PATH, title)


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form kể chuyện Phong Thuỷ/Tử Vi tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) KỂ CHUYỆN về "{topic_title}", dựa DUY NHẤT trên đoạn trích nguồn sau:

{facts_json}

(is_hypothetical=true nghĩa là đây là tình huống GIẢ ĐỊNH -- BẮT BUỘC phải dùng ngôn ngữ rõ ràng là giả định, vd "Giả sử...", "Nếu như...", "Thử tưởng tượng..." xuyên suốt kịch bản, KHÔNG được viết như thể đó là sự thật đã xảy ra.)

3 chiến lược hook bắt buộc -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. VÀO THẲNG TÌNH HUỐNG: mở bằng 1 khoảnh khắc/tình huống cụ thể trong câu chuyện, không giới thiệu dài dòng.
B. CÂU HỎI TÒ MÒ: mở bằng câu hỏi khơi gợi về nhân vật/sự kiện.
C. "NẾU...THÌ SAO": mở bằng giả định thú vị liên quan tới câu chuyện (chỉ dùng khi hợp lý với nội dung).

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- Cốt truyện chính PHẢI khớp đoạn trích nguồn -- không bịa thêm tình tiết lịch sử không có căn cứ trong đoạn trích.
- Nếu is_hypothetical=true: PHẢI thể hiện rõ đây là giả định trong TOÀN BỘ kịch bản, không chỉ 1 câu đầu.
- Câu chuyện phải MẠCH LẠC (có mở-thân-kết), kết thúc bằng 1 giá trị xem/bài học/insight, không phải liệt kê sự kiện rời rạc.
- ĐÁNH DẤU từ/cụm từ quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = (
    """Bạn là giám khảo 2 vai trò: (1) kiểm tra cốt truyện đúng nguồn + giả định rõ ràng, (2) chuyên gia storytelling short-form. Chấm 3 phương án dưới đây.

=== ĐOẠN TRÍCH NGUỒN + is_hypothetical (căn cứ duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi kiểm tra.

"""
    + content_categories.category_rubric_block(content_categories.STORYTELLING)
    + """

BƯỚC 1 -- LOẠI TRỪ THEO TIÊU CHUẨN CATEGORY 5 Ở TRÊN: phương án nào bịa tình tiết KHÔNG có trong đoạn trích nguồn → LOẠI. Nếu is_hypothetical=true mà phương án viết như sự thật đã xảy ra (không rõ ràng là giả định xuyên suốt) → LOẠI. Câu chuyện rời rạc, không mạch lạc → LOẠI.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số còn lại: có vào thẳng tình huống không, có giá trị xem/bài học ở cuối không?

Trả về CHỈ 1 JSON object -- chọn bản thắng CHỈ bằng "candidate_id" (mã phương án), KHÔNG chép lại hay viết lại kịch bản:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "candidate_id": "A" hoặc "B" hoặc "C" hoặc "NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""
)


def write_short_bundle_file(topic_title: str, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = bundle_path(topic_title)
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def bundle_path(topic_title: str) -> Path:
    """File bundle sẽ được ghi (tên trống kế tiếp nếu trùng)."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "", topic_title)[:30] or "GiaiThoai"
    out_path = OUTPUT_DIR / f"CHUYENKE_{slug}_Short.txt"
    n = 1
    while out_path.exists():
        n += 1
        out_path = OUTPUT_DIR / f"CHUYENKE_{slug}_{n}_Short.txt"
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild-bank", action="store_true")
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    if args.rebuild_bank:
        build_full_topic_bank(force_refresh=True)

    topic = next_unused_topic()
    if topic is None:
        print("DỪNG: hết góc kể chuyện trong topic bank -- cần --rebuild-bank hoặc SOURCES có thêm draft mới.", file=sys.stderr)
        return 1

    print(f"Góc kể chuyện: {topic['title']} (nguồn: {topic['source_file']}, giả định: {topic.get('is_hypothetical')})", flush=True)
    facts = {
        "topic_title": topic["title"], "excerpt": topic["excerpt"],
        "is_hypothetical": topic.get("is_hypothetical", False), "source_file": topic["source_file"],
    }

    prompt_with_title = _GENERATE_CANDIDATES_PROMPT.replace("{topic_title}", topic["title"])
    result = generate_verified_script(facts, prompt_with_title, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    gate = cqg.evaluate(cqg.judge_panel_outcome(
        domain="FS", generator="storytelling_short_generator", generator_file=__file__, category=CONTENT_CATEGORY,
        facts=facts, result=result, content_id=cqg.content_id_for_bundle(bundle_path(topic["title"])),
        prompts=(prompt_with_title, _JUDGE_PROMPT, *short_judge_panel_engine.RETENTION_PROMPT_BLOCKS),
        source_excerpt=topic["excerpt"],
    ))
    if not cqg.report(gate, log=lambda msg: print(msg, file=sys.stderr, flush=True)):
        print("(chủ đề vẫn giữ CHƯA DÙNG để thử lại)", file=sys.stderr)
        return 1

    # S6: Content invariant -- nguồn claim là đúng facts đã đưa cho writer (do
    # code ghi); hook/thứ tự ý/Payoff do Script evaluator trích sau.
    invariant = content_invariant.build(
        claim_source_kind="generator_facts", claim_source_data=facts, source_excerpt=topic["excerpt"],
        versions={"quality_record_id": gate.record["quality_record_id"]},
    )
    # S7: Script Quality Gate ngay sau S1, cùng điểm hội tụ; không PASS thì không ghi bundle.
    script_gate = sqg.evaluate_after_content_gate(gate, invariant=invariant)
    if not sqg.report(script_gate, log=lambda msg: print(msg, file=sys.stderr, flush=True)):
        return 1
    out_path = write_short_bundle_file(topic["title"], gate.decision.script)
    content_invariant.write_sidecar(out_path, script_gate.extra.get("invariant") or invariant)
    mark_topic_used(topic["title"])
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
