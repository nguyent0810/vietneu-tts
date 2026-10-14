"""Sinh nội dung Short "Trending/Newsjacking" -- CATEGORY 6 (xem
content_categories.py) -- MVP BÁN THỦ CÔNG cho điểm #9 của audit 9 điểm.

BÁN THỦ CÔNG CÓ CHỦ ĐÍCH (không tự động hoá hoàn toàn): MVP này KHÔNG tự
crawl/scrape tin tức -- người dùng tự dán ĐOẠN TIN TỨC NGUỒN (--source-text
hoặc --source-file) + URL + ngày tin, cùng domain kênh (BUD/FS/CL) qua CLI.
QUAN TRỌNG (Codex review vòng 1): nội dung nguồn là NGƯỜI DÙNG TỰ XÁC NHẬN
("human-attested"), KHÔNG phải hệ thống đã kiểm chứng độc lập -- không có
gì ngăn người dùng dán nhầm/thiếu ngữ cảnh/ghép sai URL với nội dung khác.
Đây là giới hạn CHẤP NHẬN ĐƯỢC của MVP (đánh đổi lấy việc không tự động
crawl nguồn không kiểm soát được), không phải đã được giải quyết.

HAI BƯỚC BẮT BUỘC, TÁCH RIÊNG (Codex review vòng 1, CRITICAL #2 -- xem
lịch sử sửa): bản v1 dựa vào agy tự phân loại facts["mentions_real_person"]
làm GATE AN TOÀN DUY NHẤT -- nếu agy phân loại SAI (false-negative, không
có lớp kiểm tra thứ 2), gate biến mất hoàn toàn, không có gì chặn tự động
ghi file. SỬA TRIỆT ĐỂ: bỏ hẳn ý tưởng "gate dựa vào 1 lần phân loại của
model" -- thay bằng 2 bước lệnh CLI TÁCH RIÊNG, không thể gộp:
  1. `draft`  -- trích facts + sinh kịch bản qua judge-panel, LUÔN LUÔN ghi
     ra 1 file JSON nháp, KHÔNG BAO GIỜ tự ghi file Short, BẤT KỂ facts nói
     gì hay hook_score cao đến đâu.
  2. `publish` -- CHỈ chạy SAU KHI người dùng tự đọc file JSON nháp (đọc kỹ
     script + mentions_real_person + still_developing), rồi CHỦ ĐỘNG gọi
     lệnh publish kèm --confirm-reviewed (bắt buộc, không có giá trị mặc
     định) để thật sự ghi file Short.
Nhờ đó, dù mentions_real_person bị phân loại sai, hành vi HỆ THỐNG vẫn
GIỐNG HỆT NHAU (luôn dừng ở draft, luôn cần publish thủ công) -- an toàn
không còn phụ thuộc vào 1 điểm lỗi duy nhất của model nữa.

GIỚI HẠN CÔNG NHẬN, KHÔNG GIẤU (Codex review vòng 2): đây là ranh giới QUY
TRÌNH CLI (chặn đường dùng bình thường), KHÔNG PHẢI ranh giới bảo mật chống
người dùng cố tình phá -- Python không có access control cấp module, 1
script khác có quyền chạy Python + quyền ghi workspace vẫn có thể import
và gọi thẳng write_short_bundle_file()/extract_facts()/generate_verified_
script() bỏ qua CLI. Việc này KHÔNG khác gì mọi generator khác trong repo
(chưa có generator nào có ranh giới bảo mật cấp module) -- MVP này chỉ cam
kết đóng đường bypass QUA CLI CHUẨN, đúng phạm vi threat model "người vận
hành dùng CLI, có thể mắc lỗi/phân loại sai", không phải "kẻ tấn công có
quyền thực thi mã tuỳ ý trong workspace."

GROUNDING CHỐNG HALLUCINATION (Codex review vòng 1, CRITICAL #1): trước
đây judge-panel chỉ đối chiếu candidate với "excerpt"/"summary" do CHÍNH
agy tạo ra khi extract_facts() -- nếu agy tự thêm 1 chi tiết vào excerpt/
summary lúc trích, fact-check sau đó PASS vì đối chiếu với bản đã nhiễm,
không phải nguồn thật. SỬA: extract_facts() giữ nguyên `source_text` gốc
trong facts, và BẮT BUỘC kiểm tra bằng code rằng "excerpt" (sau chuẩn hoá
khoảng trắng) THẬT SỰ là 1 đoạn con của source_text -- fail-closed (raise)
nếu không khớp, TRƯỚC KHI đưa facts cho generate/judge. Judge prompt cũng
được yêu cầu đối chiếu với source_text đầy đủ, không chỉ excerpt/summary.

TÁI FACT-CHECK ĐỘC LẬP TẠI publish (Codex review vòng 2, HIGH): vòng 1 chỉ
kiểm tra "excerpt" của draft còn khớp "source_text" hay không -- nhưng
KHÔNG kiểm tra chính "script" sắp ghi có còn khớp nguồn không, và "passed"
chỉ được đọc truthy. Vì draft.json là 1 file JSON THƯỜNG (editable working
document, không có chữ ký/HMAC), ai đó (kể cả vô tình khi sửa tay) có thể
đổi "script" hoặc đặt "passed": true mà 2 check cũ không phát hiện được.
SỬA: publish() giờ (a) validate schema NGHIÊM (type(passed) is bool VÀ
True, script/source_text/excerpt là chuỗi khác rỗng), và (b) gọi lại 1
lượt fact-check ĐỘC LẬP (_reverify_script_against_source()) đối chiếu
CHÍNH "script" sắp ghi với "source_text" đầy đủ, KHÔNG tin bất kỳ verdict
cũ nào -- publish chỉ thành công nếu re-verify PASS thật tại thời điểm đó.

NGUỒN-ONLY CHO "GÓC NHÌN KÊNH" (Codex review vòng 1, HIGH #4): Category 6
khác Category 2/3 (vốn có research draft đã qua kiểm chứng làm nền) --
category tin tức CHỈ có đúng đoạn nguồn người dùng dán, không có "kiến
thức nền" nào được duyệt trước. Vì vậy "góc nhìn kênh" (bài học Phật giáo,
quan niệm phong thuỷ, khía cạnh pháp lý) BẮT BUỘC không được tự thêm khái
niệm/thuật ngữ chuyên môn cụ thể nào KHÔNG có trong facts, dù đúng thật
ngoài đời -- xem rubric TRENDING trong content_categories.py."""
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import _run_agy, _run_codex, _extract_json, ContentSeoError  # noqa: E402
from short_judge_panel_engine import generate_verified_script  # noqa: E402
from content_repo import load_domain_topics  # noqa: E402
import content_categories  # noqa: E402

CONTENT_CATEGORY = content_categories.TRENDING  # xem content_categories.py
MAX_ITERATIONS = 3
VALID_DOMAINS = ("BUD", "FS", "CL")
MIN_SOURCE_TEXT_CHARS = 80  # chặn paste tiêu đề trơ trọi/thiếu ngữ cảnh -- ngưỡng RỘNG RÃI, chỉ bắt case rõ ràng quá ngắn

_EXTRACT_FACTS_PROMPT = """Bạn đang chuẩn bị chất liệu fact-check cho 1 Short-form (~20-30 giây/video) tiếng Việt BÌNH LUẬN 1 tin tức/sự kiện đang được quan tâm, cho kênh chủ đề "{domain_topic}".

=== NGUỒN TIN (do người dùng cung cấp, CHƯA qua hệ thống kiểm chứng độc lập -- chỉ người dùng tự xác nhận) ===
URL: {source_url}
Ngày tin: {source_date}
Nội dung:
{source_text}

Nhiệm vụ CHỈ trích xuất, KHÔNG được thêm/suy diễn thông tin ngoài đoạn trên:
1. "excerpt": trích ĐOẠN VĂN NGUYÊN VẸN quan trọng nhất (copy CHÍNH XÁC từng chữ từ nguồn, KHÔNG diễn giải/tóm tắt/đổi từ, 3-10 câu) làm căn cứ fact-check -- BẮT BUỘC là 1 đoạn CON thật sự của nội dung trên, hệ thống sẽ tự kiểm tra bằng code.
2. "summary": tóm tắt 1-2 câu sự việc CHÍNH, chỉ dùng thông tin có trong nguồn (đây là bản diễn giải TIỆN DÙNG, không phải căn cứ fact-check độc lập).
3. "mentions_real_person": true nếu nguồn tin nêu TÊN CỤ THỂ 1 người thật (không phải nhóm/tổ chức chung chung, không phải nhân vật ẩn danh) liên quan trực tiếp tới sự việc, false nếu không.
4. "still_developing": true nếu nguồn tin dùng ngôn ngữ cho thấy sự việc CHƯA CHỐT (đang điều tra, số liệu sơ bộ, "theo nguồn tin ban đầu"...), false nếu đã là kết luận/sự việc đã xảy ra rõ ràng.

Trả về CHỈ 1 JSON object:
{{"excerpt": "...", "summary": "...", "mentions_real_person": true hoặc false, "still_developing": true hoặc false}}"""


def _normalize_for_substring_check(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_facts(domain: str, domain_topic: str, source_text: str, source_url: str, source_date: str) -> dict:
    prompt = _EXTRACT_FACTS_PROMPT.format(
        domain_topic=domain_topic, source_url=source_url, source_date=source_date, source_text=source_text,
    )
    result = _extract_json(_run_agy(prompt))
    for key in ("excerpt", "summary", "mentions_real_person", "still_developing"):
        if key not in result:
            raise ContentSeoError(f"agy trích facts thiếu key '{key}': {result!r}"[:500])

    excerpt, summary = result["excerpt"], result["summary"]
    if not isinstance(excerpt, str) or not excerpt.strip():
        raise ContentSeoError(f"'excerpt' không phải chuỗi khác rỗng: {excerpt!r}"[:500])
    if not isinstance(summary, str) or not summary.strip():
        raise ContentSeoError(f"'summary' không phải chuỗi khác rỗng: {summary!r}"[:500])
    # BẮT BUỘC kiểu bool CHÍNH XÁC (type() is bool, không phải isinstance --
    # bool là subclass của int trong Python, isinstance(1, bool) == False
    # nhưng isinstance(True, int) == True; ngược lại ở đây ta cần LOẠI cả
    # trường hợp JSON trả 0/1/"true" thay vì true/false thật, nên dùng type()).
    if type(result["mentions_real_person"]) is not bool:
        raise ContentSeoError(f"'mentions_real_person' không phải boolean thật: {result['mentions_real_person']!r}"[:500])
    if type(result["still_developing"]) is not bool:
        raise ContentSeoError(f"'still_developing' không phải boolean thật: {result['still_developing']!r}"[:500])

    # GROUNDING CHỐNG HALLUCINATION (Codex review vòng 1, CRITICAL #1): excerpt
    # PHẢI THẬT SỰ là 1 đoạn con của source_text -- fail-closed nếu không khớp,
    # KHÔNG được tin agy trích đúng chỉ vì JSON hợp lệ.
    if _normalize_for_substring_check(excerpt) not in _normalize_for_substring_check(source_text):
        raise ContentSeoError(
            "agy trích 'excerpt' KHÔNG khớp nguyên văn source_text -- nghi ngờ hallucination lúc trích, "
            "DỪNG (fail-closed), không đưa vào judge-panel."
        )

    return {
        "excerpt": excerpt, "summary": summary,
        "mentions_real_person": result["mentions_real_person"],
        "still_developing": result["still_developing"],
        "domain": domain, "source_url": source_url, "source_date": source_date,
        # Giữ NGUYÊN VĂN nguồn để judge đối chiếu trực tiếp -- KHÔNG chỉ tin
        # excerpt/summary (vốn là sản phẩm trung gian do agy tạo, có thể sai
        # sót khi trích dù đã qua grounding check ở trên).
        "source_text": source_text,
    }


_GENERATE_CANDIDATES_PROMPT = """Bạn là biên tập viên Short-form tin tức/thời sự tiếng Việt cho kênh chủ đề "{domain_topic}". Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) BÌNH LUẬN sự việc dưới đây, dựa DUY NHẤT trên facts đã cho:

{facts_json}

(facts.source_text là NGUYÊN VĂN nguồn tin đầy đủ -- đây mới là căn cứ AUTHORITATIVE, facts.summary chỉ là bản diễn giải tiện dùng.)

3 chiến lược hook bắt buộc (mỗi phương án 1 chiến lược, không trộn) -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. VÀO THẲNG SỰ VIỆC: mở bằng chi tiết đáng chú ý nhất của sự việc, không giới thiệu dài dòng.
B. CÂU HỎI THỜI SỰ: mở bằng câu hỏi khơi gợi về sự việc đang được quan tâm.
C. GÓC NHÌN KÊNH: mở bằng góc liên hệ tới chủ đề kênh, NHƯNG CHỈ được dùng khung cảm nhận/diễn đạt chung rồi quay lại đúng nội dung facts (VD "điều này gợi nhắc..." rồi trở lại sự việc) -- TUYỆT ĐỐI KHÔNG được tự thêm giáo lý/quan niệm phong thuỷ cụ thể/thuật ngữ pháp lý/tội danh nào KHÔNG xuất hiện trong facts, dù đúng thật ngoài đời và dù hợp lý với chủ đề kênh.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ được dùng thông tin có trong facts (source_text/excerpt/summary) -- KHÔNG bịa thêm chi tiết, số liệu, hay suy đoán diễn biến/kết quả ngoài facts.
- MỌI khái niệm/thuật ngữ chuyên môn (giáo lý, quan niệm phong thuỷ, tội danh/điều luật...) xuất hiện trong kịch bản PHẢI có trong facts -- không được tự thêm dù đúng thật ngoài đời.
- BẮT BUỘC có 1 mốc thời gian rõ ràng gắn với source_date đã cho (vd "theo tin ngày {source_date}...") -- không dùng cụm mơ hồ như "mới đây" mà không kèm ngày cụ thể.
- Nếu facts.still_developing=true: dùng ngôn ngữ dè dặt ("theo thông tin ban đầu", "chưa được xác nhận chính thức"), KHÔNG khẳng định như kết luận cuối cùng.
- Nếu facts.mentions_real_person=true: giữ giọng trung lập, tường thuật, KHÔNG phán xét/suy đoán động cơ ngoài facts.
- ĐÁNH DẤU TỪ/CỤM TỪ QUAN TRỌNG bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
{revision_note}
Trả về CHỈ 1 JSON object:
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
(mỗi "script" là toàn bộ kịch bản, các câu ngăn cách bằng \\n)"""

_JUDGE_PROMPT = (
    """Bạn là giám khảo 2 vai trò: (1) kiểm tra đúng nguồn tin + mốc thời gian + giọng điệu phù hợp, (2) chuyên gia short-form thời sự. Chấm 3 phương án dưới đây.

=== FACTS (căn cứ duy nhất) ===
{facts_json}

(facts.source_text là NGUYÊN VĂN nguồn đầy đủ -- BẮT BUỘC đối chiếu MỌI chi tiết trong 3 phương án với ĐÚNG source_text này, không chỉ excerpt/summary. Nếu 1 chi tiết chỉ khớp summary nhưng KHÔNG xác nhận được trong source_text, coi như KHÔNG có căn cứ -- FAIL.)

=== 3 PHƯƠNG ÁN ===
{candidates_text}

GHI CHÚ ĐỊNH DẠNG: cụm bọc trong **hai dấu sao** là đánh dấu hiển thị, KHÔNG phải nội dung thêm -- bỏ qua dấu ** khi kiểm tra.

"""
    + content_categories.category_rubric_block(content_categories.TRENDING)
    + """

BƯỚC 1 -- LOẠI TRỪ THEO TIÊU CHUẨN CATEGORY 6 Ở TRÊN (đối chiếu source_text đầy đủ, không chỉ excerpt/summary).

BƯỚC 2 -- CHỌN HOOK TỐT NHẤT trong số còn lại.

Trả về CHỈ 1 JSON object -- "winner_script" PHẢI giữ nguyên dấu **:
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}"""
)


def output_dir_for_domain(domain: str) -> Path:
    domain_topics = load_domain_topics()
    topic = domain_topics.get(domain)
    if not topic or not isinstance(topic, str):
        raise ContentSeoError(f"Domain '{domain}' chưa có trong domain_topics.json hoặc giá trị không hợp lệ.")
    staging_root = (Path(__file__).parent / "drive_input" / "content_repo_staged").resolve()
    out_dir = (staging_root / topic / "Short").resolve()
    # Path containment check (Codex review vòng 1, MEDIUM #7): nếu
    # domain_topics.json bị sửa chứa "../../x" hay absolute path, out_dir có
    # thể thoát khỏi staging_root -- CLI chỉ allowlist domain (BUD/FS/CL),
    # KHÔNG tự bảo vệ được giá trị topic đọc từ config. Xác nhận containment
    # THẬT SỰ trước khi trả về, không chỉ tin cấu hình.
    if not out_dir.is_relative_to(staging_root):
        raise ContentSeoError(f"Domain topic '{topic}' (domain={domain}) tạo ra đường dẫn thoát khỏi staging root -- từ chối vì an toàn.")
    return out_dir


def write_short_bundle_file(domain: str, summary: str, script: str) -> Path:
    out_dir = output_dir_for_domain(domain)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9]+", "", summary)[:30] or "TinTuc"
    out_path = out_dir / f"TRENDING_{slug}_Short.txt"
    n = 1
    while out_path.exists():
        n += 1
        out_path = out_dir / f"TRENDING_{slug}_{n}_Short.txt"
    out_path.write_text(f"*** 1\n\n{script}\n", encoding="utf-8")
    return out_path


def _run_draft(args) -> int:
    if args.source_file:
        try:
            source_text = Path(args.source_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"LỖI: không đọc được --source-file: {exc}", file=sys.stderr)
            return 1
    else:
        source_text = args.source_text

    if len(source_text.strip()) < MIN_SOURCE_TEXT_CHARS:
        print(f"LỖI: nội dung nguồn quá ngắn (<{MIN_SOURCE_TEXT_CHARS} ký tự sau khi loại khoảng trắng thừa) -- có thể chỉ là tiêu đề, thiếu ngữ cảnh.", file=sys.stderr)
        return 1

    if not re.match(r"^https?://", args.source_url):
        print("LỖI: --source-url phải bắt đầu bằng http:// hoặc https://.", file=sys.stderr)
        return 1

    try:
        date.fromisoformat(args.source_date)
    except ValueError:
        print("LỖI: --source-date phải đúng định dạng ISO (VD 2026-07-29).", file=sys.stderr)
        return 1

    domain_topics = load_domain_topics()
    domain_topic = domain_topics.get(args.domain)
    if not domain_topic:
        print(f"LỖI: domain '{args.domain}' chưa có trong domain_topics.json.", file=sys.stderr)
        return 1

    try:
        facts = extract_facts(args.domain, domain_topic, source_text, args.source_url, args.source_date)
    except ContentSeoError as exc:
        print(f"LỖI: trích facts thất bại ({exc}) -- DỪNG, không ghi nháp (fail-closed).", file=sys.stderr)
        return 1

    print(
        f"Tóm tắt: {facts['summary']} "
        f"(mentions_real_person={facts['mentions_real_person']}, still_developing={facts['still_developing']})",
        flush=True,
    )

    prompt_with_topic = _GENERATE_CANDIDATES_PROMPT.replace("{domain_topic}", domain_topic).replace(
        "{source_date}", args.source_date,
    )
    # 2 lần .replace() trên chỉ thay literal domain_topic/source_date, không
    # đụng {facts_json}/{revision_note} (generate_verified_script() cần
    # nguyên vẹn 2 placeholder này để tự .format() bên trong).
    result = generate_verified_script(facts, prompt_with_topic, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)

    # LUÔN cần người duyệt -- xem docstring đầu file (Codex review vòng 1,
    # CRITICAL #2): KHÔNG dựa vào 1 lần phân loại mentions_real_person của
    # agy làm gate an toàn duy nhất -- mọi draft, KHÔNG PHÂN BIỆT facts nói
    # gì hay hook_score cao đến đâu, đều dừng ở đây. File Short THẬT chỉ
    # được ghi ở bước `publish` riêng, sau khi người dùng tự xác nhận.
    result["needs_human_review"] = True

    draft_payload = {"facts": facts, **result}
    Path(args.output_json).write_text(json.dumps(draft_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"NHÁP đã ghi: {args.output_json} -- ĐỌC KỸ file này (đặc biệt mentions_real_person/"
        f"still_developing/toàn bộ script) rồi chạy `trending_short_generator.py publish "
        f"--draft-json {args.output_json} --confirm-reviewed` để đăng thật.",
        flush=True,
    )
    return 0 if result["passed"] else 1


_REVERIFY_PROMPT = """Bạn là người fact-check ĐỘC LẬP ngay TRƯỚC KHI xuất bản (không phải vòng chấm sinh nội dung ban đầu -- coi như CHƯA biết gì về vòng trước, vì draft có thể đã bị chỉnh sửa tay giữa lúc sinh và lúc xuất bản này).

=== NGUỒN TIN NGUYÊN VĂN (căn cứ duy nhất) ===
{source_text}

=== KỊCH BẢN SẮP XUẤT BẢN (kiểm tra lại từ đầu, không tin bất kỳ nhãn PASS nào trước đó) ===
{script}

Kiểm tra NGHIÊM: MỌI chi tiết trong kịch bản (sự việc, tên, ngày tháng, số liệu, khái niệm chuyên môn) có TRUY ĐƯỢC về đúng nguồn tin nguyên văn trên không? Có bịa thêm chi tiết/khái niệm nào không có trong nguồn không? Bỏ qua dấu ** (chỉ là đánh dấu hiển thị).

Trả về CHỈ 1 JSON object:
{{"verdict": "PASS" hoặc "FAIL", "reason": "lý do ngắn gọn"}}"""


def _reverify_script_against_source(script: str, source_text: str) -> tuple[bool, str]:
    """Fact-check LẠI TỪ ĐẦU, độc lập với 'passed' đã lưu trong draft -- xem
    docstring đầu file (Codex review vòng 2, HIGH): draft.json là editable
    working document, KHÔNG được coi field "passed"/"script" là bất biến --
    ai đó (kể cả vô tình) có thể sửa "script" mà vẫn giữ nguyên
    source_text/excerpt hợp lệ, khiến check grounding cũ (chỉ so excerpt)
    không phát hiện được. Gọi lại Codex fact-check TRỰC TIẾP script sắp ghi
    so với source_text đầy đủ, ngay tại thời điểm publish, không tái sử
    dụng bất kỳ verdict cũ nào."""
    prompt = _REVERIFY_PROMPT.format(source_text=source_text, script=script)
    result = _extract_json(_run_codex(prompt))
    verdict = result.get("verdict")
    reason = result.get("reason", "")
    if not isinstance(verdict, str) or verdict.strip().upper() != "PASS":
        return False, str(reason)
    return True, str(reason)


def _run_publish(args) -> int:
    try:
        draft = json.loads(Path(args.draft_json).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"LỖI: không đọc được --draft-json: {exc}", file=sys.stderr)
        return 1

    facts = draft.get("facts")
    script = draft.get("script")
    # Schema NGHIÊM tại publish (Codex review vòng 2): type(passed) is bool
    # VÀ True, KHÔNG chỉ truthy -- và mọi chuỗi liên quan phải khác rỗng.
    # Đây là sàn tối thiểu, KHÔNG thay thế bước re-verify script bên dưới.
    if (
        not isinstance(facts, dict)
        or type(draft.get("passed")) is not bool or draft.get("passed") is not True
        or not isinstance(script, str) or not script.strip()
    ):
        print("LỖI: draft chưa PASS judge-panel thật (hoặc thiếu/sai kiểu facts/script) -- không thể publish.", file=sys.stderr)
        return 1

    source_text, excerpt = facts.get("source_text", ""), facts.get("excerpt", "")
    if not isinstance(source_text, str) or not source_text.strip() or not isinstance(excerpt, str) or not excerpt.strip():
        print("LỖI: draft thiếu source_text/excerpt hợp lệ -- không thể publish.", file=sys.stderr)
        return 1

    # Defense-in-depth lớp 1: excerpt PHẢI khớp source_text đã lưu.
    if _normalize_for_substring_check(excerpt) not in _normalize_for_substring_check(source_text):
        print("LỖI: excerpt trong draft KHÔNG khớp source_text đã lưu -- nghi ngờ draft bị hỏng/chỉnh sửa, DỪNG (fail-closed).", file=sys.stderr)
        return 1

    # Defense-in-depth lớp 2 (Codex review vòng 2, HIGH -- lớp 1 chỉ kiểm tra
    # excerpt, KHÔNG kiểm tra chính "script" sắp ghi; "script" có thể bị
    # thay đổi tuỳ ý trong lúc excerpt/source_text vẫn còn hợp lệ, "passed"
    # cũng có thể bị sửa tay thành true -- 2 lớp check cũ hoàn toàn không
    # phát hiện được). Fact-check LẠI TỪ ĐẦU đúng "script" sắp ghi so với
    # source_text đầy đủ, KHÔNG tin nhãn "passed" cũ.
    ok, reason = _reverify_script_against_source(script, source_text)
    if not ok:
        print(f"LỖI: fact-check LẠI tại thời điểm publish KHÔNG đạt ({reason}) -- nghi ngờ script không còn khớp nguồn (có thể đã bị chỉnh sửa), DỪNG (fail-closed).", file=sys.stderr)
        return 1

    domain = facts.get("domain")
    if domain not in VALID_DOMAINS:
        print(f"LỖI: domain '{domain}' trong draft không hợp lệ.", file=sys.stderr)
        return 1

    out_path = write_short_bundle_file(domain, facts.get("summary", ""), script)
    print(
        f"OK: {out_path} (mentions_real_person={facts.get('mentions_real_person')}, "
        f"still_developing={facts.get('still_developing')}, đã publish sau khi người dùng xác nhận qua --confirm-reviewed, "
        f"đã fact-check lại độc lập tại thời điểm publish: {reason})"
    )
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)

    draft_ap = sub.add_parser("draft", help="Bước 1: trích facts + sinh kịch bản, LUÔN ghi nháp JSON, KHÔNG BAO GIỜ tự ghi file Short.")
    draft_ap.add_argument("--domain", required=True, choices=VALID_DOMAINS)
    src_group = draft_ap.add_mutually_exclusive_group(required=True)
    src_group.add_argument("--source-text", help="Nội dung tin tức nguồn (dán trực tiếp)")
    src_group.add_argument("--source-file", help="Đường dẫn file chứa nội dung tin tức nguồn")
    draft_ap.add_argument("--source-url", required=True, help="Phải bắt đầu bằng http:// hoặc https://")
    draft_ap.add_argument("--source-date", required=True, help="Ngày tin, định dạng ISO, vd 2026-07-29")
    draft_ap.add_argument("--output-json", required=True, help="Đường dẫn ghi file nháp JSON")

    publish_ap = sub.add_parser("publish", help="Bước 2: CHỈ chạy sau khi đã tự đọc kỹ file nháp -- ghi file Short thật.")
    publish_ap.add_argument("--draft-json", required=True)
    publish_ap.add_argument(
        "--confirm-reviewed", action="store_true", required=True,
        help="Bắt buộc -- xác nhận bạn đã tự đọc kỹ nội dung script + mentions_real_person + still_developing trong file nháp.",
    )

    args = ap.parse_args()
    if args.mode == "draft":
        return _run_draft(args)
    return _run_publish(args)


if __name__ == "__main__":
    sys.exit(main())
