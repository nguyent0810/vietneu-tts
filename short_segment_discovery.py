"""Dò + parse file nguồn Short (*_Short.txt) -- TÁCH RIÊNG khỏi
short_batch_runner.py để module này KHÔNG kéo theo review/SEO/upload/
registry/bgm/youtube_catalog (short_health_check.py chỉ cần đúng phần
đọc file THUẦN TUÝ này, không cần toàn bộ runner -- xem báo cáo
dependency-closure + design refactor trong lịch sử phiên làm việc, audit
launchd 04/08). short_batch_runner.py giờ import lại 2 hàm này thay vì tự
định nghĩa -- 1 nguồn sự thật DUY NHẤT, không copy-paste.

Nội dung + logic bên trong 2 hàm giữ NGUYÊN VẸN so với bản gốc trong
short_batch_runner.py. MỘT thay đổi API có chủ đích (Codex CLI review round
2 nhấn mạnh: nên nói rõ, không chỉ nói "logic không đổi"): `topic` giờ là
tham số BẮT BUỘC (bỏ default DEFAULT_TOPIC cũ) -- xác nhận qua grep toàn
repo: mọi call site thật (short_batch_runner.py, short_health_check.py)
đều đã truyền topic tường minh, không có nơi nào dựa vào default, nên
không tạo runtime drift cho code hiện tại -- nhưng đây VẪN LÀ 1 thay đổi
chữ ký hàm thật, không phải "hoàn toàn không đổi"."""
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

MARKER_RE = re.compile(r"^\*\*\*\s*(\d+)\s*$", re.MULTILINE)


def _shorts_source_dir(topic: str) -> Path:
    return PROJECT_ROOT / "drive_input" / "content_repo_staged" / topic / "Short"


def cl_metadata_sidecar_path(episode: str, topic: str) -> Path:
    """CL Risk Gate Stage 3 (task #241): CL Short's `.txt` bundle nội dung
    ĐÃ qua Phase A review (cl_risk_gate_orchestrator.run_cl_case_gate() ->
    cl_case_batch.py ghi ra file) đi kèm 1 sidecar JSON CÙNG TÊN (đổi hậu
    tố) mang reviewed_editorial_hash/named_individuals/run_id -- cần thiết
    cho short_batch_runner.py's Phase C/D wiring (không nằm trong seg dict
    trả về từ discover_segments(), vốn chỉ có text -- xem ghi chú đầu
    file). Tách hàm dùng CHUNG giữa cl_case_batch.py (bên GHI) và
    short_batch_runner.py (bên ĐỌC), đúng nguyên tắc "1 nguồn sự thật" đã
    nêu ở docstring đầu file này -- không để 2 nơi tự suy đường dẫn riêng,
    dễ lệch nhau khi 1 bên đổi quy ước mà bên kia không hay.

    `episode` PHẢI là file_id (tên file KHÔNG có hậu tố `_Short.txt`,
    khớp `discover_segments()`'s `seg["episode"]`) -- 1 sidecar áp dụng
    cho TOÀN BỘ file (CL Gate ghi mỗi candidate PASS Phase A thành đúng 1
    file bundle độc lập, không gộp nhiều candidate/segment_index vào 1
    file như generator xoay vòng evergreen của Phong Thuỷ)."""
    return _shorts_source_dir(topic) / f"{episode}_Short.cl_meta.json"


def cl_topic_meta_sidecar_path(episode: str, topic: str) -> Path:
    """Vá lỗi "excerpt-as-ground-truth" (CL claim ledger, xem cl_claim_
    ledger.py): trước bản vá này, `source_file`/`excerpt` mà criminal_law_
    short_generator.py's next_unused_topic() đã có SẴN ở thời điểm sinh
    nội dung bị VỨT BỎ ngay sau khi ghi file .txt (chỉ topic["title"] sống
    sót, qua slug -- fragile, đổi khi --rebuild-bank sinh lại title). Sidecar
    NÀY (ghi bởi write_short_bundle_file(), đọc bởi run_cl_storytelling_
    phase_a.py) giữ lại đúng 3 trường {title, source_file, excerpt} đã có
    sẵn tại thời điểm sinh -- KHÔNG phải 1 hệ thống định danh mới, chỉ là
    làm bền field source_file vốn đã tồn tại (cùng khớp key dùng trong
    SOURCE_REGISTRY.md) để Phase A dùng lại được thay vì phải fuzzy-match
    lại qua title. Cùng thư mục + quy ước hậu tố với cl_metadata_sidecar_
    path() ở trên, đổi .cl_meta.json -> .topic_meta.json."""
    return _shorts_source_dir(topic) / f"{episode}_Short.topic_meta.json"


def cl_story_plan_sidecar_path(episode: str, topic: str) -> Path:
    """C4 Round 6 (tích hợp production kiến trúc provenance-preserving,
    xem cl_story_plan_and_generation.py): sidecar riêng cho Story Plan của
    variant "storytelling_provenance_v1" -- KHÔNG gộp vào `.cl_meta.json`
    (đó là kết quả Phase A, sidecar này là ĐẦU VÀO cấu trúc cho Phase A,
    cần đọc lại được ĐỘC LẬP để short_batch_runner.py's consumer re-check
    tự re-derive plan_hash/fact_ids từ đĩa, không tin lại self-report).
    Cùng thư mục + quy ước hậu tố với 2 hàm trên."""
    return _shorts_source_dir(topic) / f"{episode}_Short.story_plan.json"


def cl_script_binding_sidecar_path(episode: str, topic: str) -> Path:
    """Sidecar bindings (segment_id -> fact_ids -> prose -> pack_hash_at_
    generation) của variant "storytelling_provenance_v1" -- đây LÀ artifact
    consumer-side re-check (short_batch_runner.py) dùng để gọi lại
    validate_binding_integrity()/run_deterministic_guards() TẠI THỜI ĐIỂM
    publish, không tin lại provenance_state tự khai trong `.cl_meta.json`."""
    return _shorts_source_dir(topic) / f"{episode}_Short.script_binding.json"


def discover_all_episode_prefixes(topic: str) -> list[str]:
    """Tự dò MỌI tiền tố tập nguồn có sẵn trong Short/ của topic (thay vì
    người gọi phải liệt kê thủ công qua --episodes) -- cần thiết từ khi có
    nhiều generator Short khác nhau cho Phong Thuỷ (lịch hoàng đạo, 12 vị
    Thần, con giáp, màu mệnh, kiến thức nền...), mỗi loại 1 kiểu tiền tố
    riêng (LICH*/THAN*/CONGIAP*/MENH_*/KIENTHUC_*) -- không còn 1 quy ước
    tiền tố số tập cố định như "06" của Phật giáo để liệt kê tay được."""
    source_dir = _shorts_source_dir(topic)
    # Tiền tố THẬT SỰ là phần trước "_<Loại>_Short.txt" -- suy ngược theo
    # đúng quy ước discover_segments() dùng để glob (f"{ep_prefix}_*_Short.txt"):
    # bỏ hậu tố "_Short.txt", rồi bỏ tiếp cụm cuối (tên loại nội dung, vd
    # "LichHoangDao"/"12ViThan"/"ConGiap"/"MauSacHopMenh").
    prefixes = set()
    for f in source_dir.glob("*_Short.txt"):
        stem = f.name[: -len("_Short.txt")]
        prefix = stem.rsplit("_", 1)[0]
        prefixes.add(prefix)
    return sorted(prefixes)


def discover_segments(episodes: list[str], topic: str) -> list[dict]:
    """[{key, episode, segment_index, text}] -- key dùng làm registry key.

    BUG THẬT phát hiện khi chuẩn bị chạy batch thật (xem phiên làm việc):
    discover_all_episode_prefixes() suy đoán "cụm cuối cùng sau dấu _ là
    LOẠI nội dung" rồi bỏ đi để lấy prefix -- ĐÚNG với generator có tiền
    tố ngày/tháng cố định (CONGIAPTHANG06_ConGiapThang, MENHNGAY20260725_
    MenhTaiLoc) nhưng SAI với generator xoay vòng evergreen: western_zodiac
    (CUNGHD_<tên cung>), iching (KINHDICH_<tên quẻ>), educational (KIENTHUC_
    <slug chủ đề>) dùng CHÍNH cụm cuối làm phần PHÂN BIỆT, không phải loại
    nội dung -- nhiều file khác nhau bị gộp nhầm về CÙNG 1 prefix. Bản gốc
    chỉ lấy `matches[0]` (khớp ĐẦU TIÊN) -- các file còn lại bị BỎ QUA HOÀN
    TOÀN, không bao giờ được batch xử lý dù đã sẵn sàng.

    Lần sửa ĐẦU dùng key=ep_prefix khi chỉ 1 file khớp (giữ key cũ) và chỉ
    đổi sang key=tên-file-đầy-đủ khi PHÁT HIỆN collision -- nhưng phát
    hiện lỗi SÂU HƠN khi test thật: cách này KHÔNG ỔN ĐỊNH theo thời gian
    -- 1 prefix hiện chỉ khớp 1 file (dùng key cũ, đã lưu registry) nhưng
    sau đó sinh thêm 1 file MỚI cùng prefix (vd sinh thêm 1 chủ đề
    educational khác) sẽ khiến file CŨ ĐÃ ĐĂNG bị đổi ngược sang key MỚI ở
    lần chạy sau -- registry tra theo key cũ không khớp nữa, nhìn như
    "chưa xử lý", RỦI RO ĐĂNG TRÙNG nội dung đã đăng. Sửa triệt để: LUÔN
    dùng tên file đầy đủ (không phụ thuộc số lượng file khớp tại thời điểm
    gọi) -- xác định 1-1 với file vật lý, không đổi theo thời gian.

    BUG THẬT phát hiện qua Codex CLI review (đợt kiểm tra thứ 6, adversarial
    test thật): 2 prefix KHÁC NHAU trong `episodes` có thể LỒNG NHAU (vd
    "A" và "A_B" cùng suy ra từ 1 bộ file) -- glob(f"{ep_prefix}_*_Short.txt")
    của prefix NGẮN HƠN ("A_*_Short.txt") vẫn khớp NHẦM file thuộc prefix
    DÀI HƠN (vd "A_B_C_Short.txt" khớp cả "A_*" lẫn "A_B_*") -- 1 file vật
    lý bị xử lý HAI LẦN qua 2 vòng lặp prefix khác nhau, sinh 2 segment
    trùng key. Chặn bằng `seen_files` -- mỗi file vật lý chỉ được xử lý
    ĐÚNG 1 LẦN trong 1 lệnh gọi discover_segments(), bất kể khớp bao nhiêu
    prefix."""
    source_dir = _shorts_source_dir(topic)
    segments = []
    seen_files = set()
    for ep_prefix in episodes:
        matches = sorted(source_dir.glob(f"{ep_prefix}_*_Short.txt"))
        if not matches:
            print(f"CẢNH BÁO: không tìm thấy file Short cho {ep_prefix} trong {source_dir}.", file=sys.stderr)
            continue
        if len(matches) > 1:
            print(f"CẢNH BÁO: {len(matches)} file cùng khớp prefix '{ep_prefix}' (generator xoay vòng evergreen) -- xử lý TẤT CẢ: {[m.name for m in matches]}", flush=True)
        for src in matches:
            if src in seen_files:
                continue  # đã xử lý qua 1 prefix khác trùng lặp (xem docstring) -- bỏ qua, không xử lý lại
            seen_files.add(src)
            file_id = src.name[: -len("_Short.txt")]
            text = src.read_text(encoding="utf-8")
            parts = list(MARKER_RE.finditer(text))
            for i, m in enumerate(parts):
                idx = int(m.group(1))
                start = m.end()
                end = parts[i + 1].start() if i + 1 < len(parts) else len(text)
                seg_text = text[start:end].strip()
                if seg_text:
                    segments.append({"key": f"{file_id}_{idx:02d}", "episode": file_id, "segment_index": idx, "text": seg_text})
    return segments
