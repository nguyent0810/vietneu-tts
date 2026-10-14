"""Sinh nội dung Short "Kiến thức nền Phong Thuỷ/Tử Vi" cho kênh Phong Thuỷ
-- KHÁC 3 generator kia (không có nguồn "sự thật tính toán được" như
vnlunar), căn cứ ở đây là research draft THẬT trong
content_repo_clone/DOMAINS/FENG_SHUI/SOURCES/ (Content-Creator, pull-only,
đã qua đối chiếu 3+ nguồn độc lập theo chính quy trình của họ -- xem
DOMAIN_GUIDE.md §3 Source Priority Hierarchy được nhắc trong mỗi file).

KIẾN TRÚC: 2 giai đoạn, tách biệt để không tốn agy/Codex lặp lại việc đọc
toàn bộ file mỗi lần sinh 1 Short:
  1. extract_topic_bank() -- đọc 1 file SOURCES, agy đề xuất N chủ đề rời,
     MỖI chủ đề kèm ĐOẠN TRÍCH NGUYÊN VĂN (không diễn giải) làm căn cứ
     fact-check -- cache/merge/retry-lỗi do topic_bank.py (dùng chung với
     storytelling_short_generator.py) đảm nhiệm, module này chỉ cung cấp
     PROMPT trích chủ đề của riêng mình.
  2. generate: lấy 1 chủ đề CHƯA DÙNG từ bank, chạy judge-panel (dùng chung
     short_judge_panel_engine.py) với "facts" = chính đoạn trích nguyên văn
     đó -- Codex fact-check đối chiếu kịch bản với ĐÚNG đoạn trích, không
     phải cả file gốc (tránh mơ hồ)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import _run_agy, _extract_json  # noqa: E402
from short_judge_panel_engine import generate_verified_script  # noqa: E402
import topic_bank  # noqa: E402
import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.EDUCATIONAL  # xem content_categories.py
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
TOPIC_BANK_PATH = Path(__file__).parent / "chunks_cache" / "fs_educational_topic_bank.json"
SOURCES_DIR = Path(__file__).parent / "content_repo_clone" / "DOMAINS" / "FENG_SHUI" / "SOURCES"
TOPICS_PER_SOURCE = 5
MAX_SOURCE_CHARS = 14000  # đủ cho research draft dài nhất (~290 dòng), tránh vượt ngưỡng context vô ích

_EXTRACT_TOPICS_PROMPT = """Bạn đang chuẩn bị chất liệu cho 1 chuỗi Short-form (~20-30 giây/video) về Phong Thuỷ/Tử Vi tiếng Việt, dựa trên research draft dưới đây.

=== RESEARCH DRAFT ===
{source_text}

Đề xuất ĐÚNG {n_topics} chủ đề RIÊNG BIỆT, mỗi chủ đề đủ thú vị/dễ hiểu để làm 1 Short độc lập cho khán giả đại chúng (không cần kiến thức nền trước). Ưu tiên chủ đề có yếu tố bất ngờ/hay bị hiểu lầm/hình ảnh cụ thể (giống mục "Chất liệu kịch bản" nếu draft có phần đó). TRÁNH chủ đề mà draft tự đánh giá độ tin cậy thấp/còn tranh cãi giữa nguồn (đọc kỹ các ghi chú "độ tin cậy", "cần xác minh thêm", "tranh cãi giữa nguồn" trong draft -- bỏ qua các điểm đó).

Với MỖI chủ đề, trích ĐOẠN VĂN NGUYÊN VẸN từ chính draft trên (copy chính xác, 3-8 câu liền mạch, KHÔNG diễn giải lại) làm căn cứ fact-check sau này.

Trả về CHỈ 1 JSON object:
{{"topics": [{{"title": "tiêu đề ngắn gọn", "excerpt": "đoạn trích nguyên văn từ draft"}}, ...]}} (đúng {n_topics} phần tử)"""


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


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form phong thuỷ/tử vi tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về chủ đề "{topic_title}", dựa DUY NHẤT trên đoạn trích nguồn sau:

{facts_json}

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN, KHÔNG mở đầu bằng định nghĩa khô khan:
A. CÂU HỎI GÂY TÒ MÒ: mở bằng câu hỏi xoáy vào điểm bất ngờ/hay bị hiểu lầm trong đoạn trích.
B. MYTH-BUST: mở bằng "Nhiều người nghĩ... nhưng thực ra..." nếu đoạn trích có nội dung sửa hiểu lầm phổ biến; nếu không, dùng "Ít ai biết rằng..."
C. HÌNH ẢNH CỤ THỂ: mở bằng 1 hình ảnh/ví dụ cụ thể có trong đoạn trích, rồi mới giải thích khái niệm.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ được dùng thông tin có trong đoạn trích nguồn (excerpt) -- KHÔNG bịa thêm số liệu, tên gọi, hay khẳng định ngoài đoạn trích.
- KHÔNG tuyệt đối hoá (không nói "chắc chắn đúng", "khoa học đã chứng minh") nếu đoạn trích không khẳng định điều đó.
- Giọng văn tự nhiên, gần gũi, mang tính giáo dục nhưng không khô khan.
- ĐÁNH DẤU TỪ/CỤM TỪ QUAN TRỌNG bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = """Bạn là giám khảo 2 vai trò: (1) kiểm tra đúng tài liệu tham khảo, (2) chuyên gia short-form giáo dục. Chấm 3 phương án dưới đây.

=== ĐOẠN TRÍCH NGUỒN (căn cứ duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi kiểm tra.

""" + content_categories.category_rubric_block(content_categories.EDUCATIONAL) + """

BƯỚC 1 -- KIỂM TRA ĐÚNG TÀI LIỆU (LOẠI TRỪ TRƯỚC): với MỖI phương án, đối chiếu từng khẳng định với đoạn trích nguồn theo đúng tiêu chuẩn Category 2 ở trên -- được kể chuyện/so sánh/minh hoạ, nhưng phương án nào có chi tiết/số liệu KHÔNG có trong đoạn trích, hoặc diễn giải SAI LỆCH ý gốc, hoặc tuyệt đối hoá quá mức → LOẠI.

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số đã qua kiểm tra.

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def write_short_bundle_file(topic_title: str, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9]+", "", topic_title)[:30] or "ChuDe"
    out_path = OUTPUT_DIR / f"KIENTHUC_{slug}_Short.txt"
    n = 1
    while out_path.exists():
        n += 1
        out_path = OUTPUT_DIR / f"KIENTHUC_{slug}_{n}_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild-bank", action="store_true", help="Trích lại toàn bộ topic bank từ SOURCES (bỏ qua cache)")
    ap.add_argument("--output-json", default=None)
    args = ap.parse_args()

    if args.rebuild_bank:
        build_full_topic_bank(force_refresh=True)

    topic = next_unused_topic()
    if topic is None:
        print("DỪNG: hết chủ đề trong topic bank -- cần --rebuild-bank hoặc SOURCES có thêm research draft mới.", file=sys.stderr)
        return 1

    print(f"Chủ đề: {topic['title']} (nguồn: {topic['source_file']})", flush=True)
    facts = {"topic_title": topic["title"], "excerpt": topic["excerpt"], "source_file": topic["source_file"]}

    prompt_with_title = _GENERATE_CANDIDATES_PROMPT.replace("{topic_title}", topic["title"])
    result = generate_verified_script(facts, prompt_with_title, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- fact-check chưa PASS, cần người xem lại (chủ đề vẫn giữ nguyên trạng thái CHƯA DÙNG để thử lại).", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(topic["title"], result["script"])
    mark_topic_used(topic["title"])
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
