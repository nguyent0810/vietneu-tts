"""Sinh nội dung Short "Án đã xử / Kiến thức luật hình sự" cho kênh Hình Sự
(CL) -- mirror kiến trúc educational_short_generator.py (topic bank 2 giai
đoạn + judge-panel dùng chung short_judge_panel_engine.py), căn cứ ở đây là
research draft THẬT trong content_repo_clone/DOMAINS/CRIMINAL_LAW/SOURCES/
(đã qua đối chiếu nguồn theo DOMAIN_GUIDE.md §3 Source Priority Hierarchy --
KHÔNG phải case mới chưa ai duyệt, đây là nguồn đã curate sẵn trước đó,
KHÁC HẲN phạm vi của cl_risk_gate.py's auto-discovery cho case THẬT SỰ mới).

AN TOÀN LÀ TRỌNG TÂM (domain risk_level: critical, cao hơn 1 bậc so với FS):
cả 2 prompt (trích chủ đề + soạn kịch bản) VÀ prompt chấm điểm đều nhúng
TRỰC TIẾP các hard rule của DOMAIN_GUIDE.md (§4 trình bày tình trạng pháp lý
đúng mức/không quy kết tội trước khi có bản án cuối cùng, §5 theory-labeling
cho case chưa có lời giải, §6 bảo vệ danh tính nạn nhân/tuyệt đối không nêu
nạn nhân vị thành niên, §7 không tư vấn pháp lý cho tình huống cụ thể của
người xem, §8 không có chi tiết vận hành tội phạm/không tôn vinh, §9 chống
giật gân/khai thác nạn nhân) -- bước chấm điểm coi VI PHẠM BẤT KỲ hard rule
nào là LOẠI TRỪ NGAY, độc lập với fact-check nội dung (2 lớp riêng, không
gộp làm 1 để tránh 1 lớp che lấp lỗi của lớp kia)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import _run_agy, _extract_json  # noqa: E402
from short_judge_panel_engine import generate_verified_script  # noqa: E402
import topic_bank  # noqa: E402
import content_categories  # noqa: E402
from short_segment_discovery import cl_topic_meta_sidecar_path  # noqa: E402

CONTENT_CATEGORY = content_categories.STORYTELLING  # án đã xử = tường thuật có mở-thân-kết, xem content_categories.py
CL_TOPIC = "Hình Sự"
MAX_ITERATIONS = 3
OUTPUT_DIR = Path(__file__).parent / "drive_input" / "content_repo_staged" / "Hình Sự" / "Short"
TOPIC_BANK_PATH = Path(__file__).parent / "chunks_cache" / "cl_criminal_law_topic_bank.json"
SOURCES_DIR = Path(__file__).parent / "content_repo_clone" / "DOMAINS" / "CRIMINAL_LAW" / "SOURCES"
TOPICS_PER_SOURCE = 5
MAX_SOURCE_CHARS = 14000  # đủ cho research draft dài nhất, tránh vượt ngưỡng context vô ích

_EXTRACT_TOPICS_PROMPT = """Bạn đang chuẩn bị chất liệu cho 1 chuỗi Short-form (~20-30 giây/video) về Hình Sự/Án đã xử tiếng Việt, dựa trên research draft dưới đây.

=== RESEARCH DRAFT ===
{source_text}

Đề xuất ĐÚNG {n_topics} chủ đề RIÊNG BIỆT, mỗi chủ đề đủ thú vị/dễ hiểu để làm 1 Short độc lập.

CHỈ chọn chủ đề AN TOÀN theo các quy tắc sau (bỏ qua chủ đề nào không đạt, không cố ép):
- ƯU TIÊN case đã có bản án CUỐI CÙNG (đã có hiệu lực pháp luật, không còn kháng cáo) với người liên quan đã MẤT hoặc case đã quá lâu/rõ ràng không còn tranh cãi -- đây là dạng AN TOÀN NHẤT (Format 1 theo DOMAIN_GUIDE §4a).
- Nếu chọn case CHƯA có lời giải/còn tranh cãi: CHỈ chọn nếu draft đã trình bày RÕ đây là 1 giả thuyết trong nhiều giả thuyết (không phải kết luận độc quyền của draft), và KHÔNG chọn nếu case chỉ có 1 nghi phạm được nêu tên mà chưa từng bị truy tố công khai qua nguồn.
- TUYỆT ĐỐI KHÔNG chọn chủ đề có chi tiết xâm hại tình dục cụ thể, hoặc chi tiết có thể dùng như hướng dẫn vận hành tội phạm (cách rửa tiền, cách tuyển mộ, cách né tránh điều tra) -- 2 loại này không có cách kể an toàn nào, loại thẳng.
- Case có nạn nhân vị thành niên: KHÔNG tự động loại chủ đề chỉ vì có nạn nhân trẻ em -- CHỈ chọn nếu góc kể hấp dẫn KHÔNG bắt buộc phải nêu tên/chi tiết nhận diện đứa trẻ (vd trọng tâm là quá trình điều tra/đột phá giám định pháp y/hệ thống tư pháp, không phải tiểu sử cá nhân nạn nhân) -- nếu chọn, đặt title KHÔNG chứa tên thật của nạn nhân trẻ em (dùng "đứa trẻ", "nạn nhân", vai trò...). Việc script cuối cùng không được nêu tên/nhận diện nạn nhân vị thành niên đã được ép buộc riêng, độc lập, ở bước sinh kịch bản và bước chấm điểm phía sau (fail-closed nếu vi phạm) -- không cần bước này gánh hết trách nhiệm đó, chỉ cần không loại nhầm chủ đề có thể kể an toàn.
- TRÁNH chủ đề mà draft tự đánh giá độ tin cậy thấp/còn tranh cãi giữa nguồn (đọc kỹ ghi chú "độ tin cậy", "cần xác minh thêm", "tranh cãi giữa nguồn" trong draft).

Với MỖI chủ đề, trích ĐOẠN VĂN NGUYÊN VẸN từ chính draft trên (copy chính xác, 3-8 câu liền mạch, KHÔNG diễn giải lại) làm căn cứ fact-check sau này.

Trả về CHỈ 1 JSON object:
{{"topics": [{{"title": "tiêu đề ngắn gọn", "excerpt": "đoạn trích nguyên văn từ draft"}}, ...]}} (TỐI ĐA {n_topics} phần tử -- ÍT HƠN nếu draft không đủ chủ đề AN TOÀN theo quy tắc trên, KHÔNG được ép đủ số lượng bằng cách hạ chuẩn an toàn)"""


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
    build_full_topic_bank()  # cache/merge/retry-lỗi do topic_bank.py đảm nhiệm
    return topic_bank.next_unused_topic(TOPIC_BANK_PATH)


def mark_topic_used(title: str) -> None:
    topic_bank.mark_topic_used(TOPIC_BANK_PATH, title)


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form Hình Sự/Án đã xử tiếng Việt. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về chủ đề "{topic_title}", dựa DUY NHẤT trên đoạn trích nguồn sau:

{facts_json}

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. CÂU HỎI GÂY TÒ MÒ VỀ SỰ KIỆN/DIỄN BIẾN (không phải câu hỏi tu từ gợi ý tội danh trước khi kết luận).
B. HÌNH ẢNH/CHI TIẾT CỤ THỂ có trong đoạn trích, rồi mới dẫn vào diễn biến.
C. MỞ BẰNG MỐC THỜI GIAN/ĐỊA ĐIỂM CỤ THỂ có trong đoạn trích.

QUY TẮC NỘI DUNG BẮT BUỘC:
- CHỈ được dùng thông tin có trong đoạn trích nguồn (excerpt) -- KHÔNG bịa thêm chi tiết, lời thoại, số liệu, hay khẳng định ngoài đoạn trích.
- Giọng văn điềm tĩnh, tường thuật, KHÔNG giật gân/không dùng cụm như "sự thật rùng rợn", "kinh hoàng", "không ai dám kể", không đếm ngược kiểu horror. Tôn trọng nạn nhân -- không mô tả chi tiết đau thương/máu me mang tính khai thác cảm xúc.
- ĐÁNH DẤU TỪ/CỤM TỪ QUAN TRỌNG bằng **hai dấu sao** -- 1-3 cụm mỗi câu.

QUY TẮC PHÁP LÝ BẮT BUỘC (DOMAIN_GUIDE.md §4/§5/§6/§7/§8 -- KHÔNG có ngoại lệ):
- Nếu 1 người CÒN SỐNG và CHƯA có bản án cuối cùng có hiệu lực pháp luật: CHỈ được gọi họ bằng thuật ngữ đúng mức ("bị tình nghi", "bị can", "bị cáo") -- TUYỆT ĐỐI KHÔNG gọi là "kẻ giết người", "hung thủ", hay bất kỳ danh từ quy kết tội nào, DÙ đoạn trích nguồn có ngụ ý điều đó.
- Nếu case CHƯA có lời giải: trình bày MỌI suy đoán về thủ phạm/động cơ như 1 GIẢ THUYẾT có gắn nguồn ("theo 1 giả thuyết được đưa ra bởi...", "cảnh sát từng coi X là nghi phạm nhưng chưa từng truy tố") -- KHÔNG được kết luận "đó chính là người đã làm".
- KHÔNG bao giờ nêu danh tính/chi tiết nhận diện nạn nhân vị thành niên. KHÔNG mô tả chi tiết xâm hại tình dục. Với nạn nhân trưởng thành, chỉ dùng chi tiết đã có trong đoạn trích/hồ sơ công khai, không suy diễn thêm.
- KHÔNG đưa lời khuyên pháp lý áp dụng cho tình huống riêng của người xem.
- KHÔNG mô tả chi tiết có thể dùng như hướng dẫn vận hành tội phạm (cách thực hiện/né tránh điều tra/tuyển mộ) -- kể sự việc đã xảy ra, không hướng dẫn cách làm.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = """Bạn là giám khảo 3 vai trò: (1) kiểm tra đúng tài liệu tham khảo, (2) kiểm tra tuân thủ quy tắc biên tập Hình Sự (DOMAIN_GUIDE.md), (3) chuyên gia short-form tường thuật. Chấm 3 phương án dưới đây.

=== ĐOẠN TRÍCH NGUỒN (căn cứ duy nhất) ===
{facts_json}

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi kiểm tra.

""" + content_categories.category_rubric_block(content_categories.STORYTELLING) + """

BƯỚC 1 -- KIỂM TRA ĐÚNG TÀI LIỆU (LOẠI TRỪ TRƯỚC): với MỖI phương án, đối chiếu từng khẳng định với đoạn trích nguồn -- phương án nào có chi tiết/số liệu/lời thoại KHÔNG có trong đoạn trích, hoặc diễn giải SAI LỆCH ý gốc → LOẠI.

BƯỚC 2 -- KIỂM TRA TUÂN THỦ DOMAIN_GUIDE (LOẠI TRỪ, ĐỘC LẬP với bước 1 -- vi phạm BẤT KỲ mục nào dưới đây là LOẠI, kể cả khi bước 1 PASS):
(a) Có gọi 1 người còn sống, chưa có bản án cuối cùng, bằng danh từ quy kết tội ("kẻ giết người", "hung thủ", "tội phạm") thay vì thuật ngữ đúng mức ("bị tình nghi"/"bị can"/"bị cáo") không?
(b) Với case chưa có lời giải, có trình bày 1 nghi phạm/giả thuyết như KẾT LUẬN chắc chắn thay vì giả thuyết có gắn nguồn không?
(c) Có nêu danh tính/chi tiết nhận diện nạn nhân vị thành niên, hoặc mô tả chi tiết xâm hại tình dục, hoặc chi tiết nạn nhân vượt quá hồ sơ công khai không?
(d) Có đưa lời khuyên pháp lý áp dụng trực tiếp cho tình huống người xem không?
(e) Có chi tiết vận hành tội phạm dùng được như hướng dẫn (cách né điều tra/rửa tiền/tuyển mộ) không, hoặc có tôn vinh/lãng mạn hoá nhân vật/tổ chức tội phạm không?
(f) Có dùng ngôn ngữ giật gân/khai thác cảm xúc kiểu horror ("rùng rợn", "kinh hoàng", đếm ngược kiểu horror) hoặc mô tả đau thương mang tính khai thác không?

BƯỚC 3 -- CHỌN HOOK TỐT NHẤT trong số đã qua CẢ 2 bước kiểm tra.

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do (nêu rõ FAIL vì bước 1 hay bước 2, mục nào)", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""


def write_short_bundle_file(topic_title: str, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9]+", "", topic_title)[:30] or "ChuDe"
    out_path = OUTPUT_DIR / f"ANDAXU_{slug}_Short.txt"
    n = 1
    while out_path.exists():
        n += 1
        out_path = OUTPUT_DIR / f"ANDAXU_{slug}_{n}_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def write_topic_meta_sidecar(bundle_path: Path, topic: dict) -> Path:
    """Vá lỗi claim-ledger topic identity (xem cl_topic_meta_sidecar_path()
    docstring, short_segment_discovery.py): giữ lại {title, source_file,
    excerpt} MÀ next_unused_topic() ĐÃ CÓ SẴN ngay tại thời điểm sinh, thay
    vì để mất sau khi ghi .txt (trước bản vá, chỉ title sống sót qua slug,
    fragile khi --rebuild-bank sinh lại title). `bundle_path` PHẢI là path
    trả về từ write_short_bundle_file() -- suy episode = tên file bỏ hậu
    tố "_Short.txt", khớp discover_segments()'s seg["episode"]/quy ước
    cl_metadata_sidecar_path()."""
    episode = bundle_path.name.removesuffix("_Short.txt")
    sidecar_path = cl_topic_meta_sidecar_path(episode, CL_TOPIC)
    sidecar = {"title": topic["title"], "source_file": topic["source_file"], "excerpt": topic["excerpt"]}
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = sidecar_path.with_suffix(sidecar_path.suffix + f".tmp{__import__('uuid').uuid4().hex[:8]}")
    tmp_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    __import__("os").replace(tmp_path, sidecar_path)
    return sidecar_path


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
        print("DỪNG: hết chủ đề AN TOÀN trong topic bank -- cần --rebuild-bank hoặc SOURCES có thêm research draft mới. KHÔNG hạ chuẩn an toàn để có thêm chủ đề.", file=sys.stderr)
        return 1

    print(f"Chủ đề: {topic['title']} (nguồn: {topic['source_file']})", flush=True)
    facts = {"topic_title": topic["title"], "excerpt": topic["excerpt"], "source_file": topic["source_file"]}

    prompt_with_title = _GENERATE_CANDIDATES_PROMPT.replace("{topic_title}", topic["title"])
    result = generate_verified_script(facts, prompt_with_title, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps({"facts": facts, **result}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not result["passed"]:
        print("DỪNG: không tự động ghi file Short -- fact-check/DOMAIN_GUIDE-check chưa PASS, cần người xem lại (chủ đề vẫn giữ nguyên trạng thái CHƯA DÙNG để thử lại).", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(topic["title"], result["script"])
    write_topic_meta_sidecar(out_path, topic)
    mark_topic_used(topic["title"])
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
