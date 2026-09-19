"""Batch Runner cho Short: nối toàn bộ chuỗi chọn đoạn -> TTS -> review hook
(judge panel) -> render video -> SEO -> upload YouTube thành 1 lệnh.

Chạy dưới python3 hệ thống (giống content_seo.py) -- gọi sang 2 venv khác
qua subprocess cho 2 bước không tương thích:
  - TTS (_short_tts_render.py) cần .venv (repo root, có vieneu/soundfile).
  - Render video (render_short.py) cần video_tool_clone/.venv-video.

State registry (output/shorts/registry.json) theo dõi từng đoạn đã xử lý
tới bước nào -- resumable, không xử lý lại đoạn đã xong, đúng nguyên tắc
đã rút ra khi audit workflow trước đó trong phiên (cần registry để batch
chạy nền không giám sát vẫn biết đoạn nào đã làm tới đâu).

QUAN TRỌNG: né trùng nội dung với 30 short EP005 ĐÃ ĐĂNG THỦ CÔNG trước đó
(xem lịch sử phiên làm việc) -- mặc định chỉ lấy nguồn từ EP006 trở đi,
KHÔNG động vào EP005.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import certifi  # noqa: E402
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

import asset_safety  # noqa: E402
from short_content_review import review_and_optimize_short  # noqa: E402
from short_seo import generate_short_seo_with_review  # noqa: E402
from short_upload import upload_short  # noqa: E402
from youtube_catalog import find_playlist_by_title, add_video_to_playlist  # noqa: E402
import bgm_tracks  # noqa: E402
from registry_lock import (  # noqa: E402
    FileLock,
    mark_production_entry,
    read_registry_safe,
    write_registry_atomic,
)
# discover_segments()/discover_all_episode_prefixes() giờ sống ở
# short_segment_discovery.py (module thuần đọc file, không phụ thuộc gì
# ở đây) -- tách ra để short_health_check.py chỉ cần đúng phần đọc file
# này mà không phải kéo theo toàn bộ runner (xem docstring module đó).
from short_segment_discovery import (  # noqa: E402, F401
    discover_all_episode_prefixes, discover_segments, cl_metadata_sidecar_path,
    cl_story_plan_sidecar_path, cl_script_binding_sidecar_path,
)
import cl_claim_ledger  # noqa: E402 -- publish-boundary fact_verification binding check (STORYTELLING sidecar only)

VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
VIDEO_TOOL_VENV_PYTHON = PROJECT_ROOT / "video_tool_clone" / ".venv-video" / "bin" / "python"
RENDER_SHORT_SCRIPT = PROJECT_ROOT / "render_short.py"
TTS_HELPER_SCRIPT = PROJECT_ROOT / "_short_tts_render.py"

DEFAULT_TOPIC = "Phật giáo"  # giữ mặc định này để không phá cron/launchd đã lên lịch (--topic chưa truyền)


def _registry_path(topic: str) -> Path:
    # THAM SỐ HOÁ THEO TOPIC -- mỗi kênh registry riêng, tránh đè lẫn nhau
    # khi chạy đa kênh (Phật giáo/Phong Thuỷ/Hình Sự dùng chung code này).
    return PROJECT_ROOT / "output" / "shorts" / topic / "registry.json"


# Cây production thật cho registry Short -- dùng bởi write_registry_atomic()
# để nhận diện "path này có phải production thật không" (xem registry_lock.py
# mục 4). CHỈ so khớp cây, KHÔNG phụ thuộc topic cụ thể -- 1 hằng số cho mọi
# topic (Phật giáo/Phong Thuỷ/Hình Sự...).
_REGISTRY_PRODUCTION_ROOT = PROJECT_ROOT / "output" / "shorts"


# Từ short_content_strategy.json vòng 3 (chưa PASS phản biện -- dữ liệu
# không đủ để "chứng minh" cả 5 khung giờ, xem ghi chú). 23:00 và 16:20 UTC
# là 2 khung ĐÃ CÓ traffic thật (đăng thủ công trước đây); 3 khung còn lại
# là GIẢ THUYẾT cần theo dõi hiệu suất thật rồi điều chỉnh, không phải kết
# luận chắc chắn -- gắn is_proven=False để phân biệt khi báo cáo.
DEFAULT_TIME_SLOTS = [
    {"utc_time": "23:00", "is_proven": True, "label": "châm ngôn ngắn 10-13s (khung đã có traffic thật)"},
    {"utc_time": "16:20", "is_proven": True, "label": "câu chuyện có hook 25-35s (khung đã có traffic thật)"},
    {"utc_time": "03:30", "is_proven": False, "label": "khung thử nghiệm -- cần theo dõi hiệu suất thật"},
    {"utc_time": "08:00", "is_proven": False, "label": "khung thử nghiệm -- cần theo dõi hiệu suất thật"},
    {"utc_time": "12:30", "is_proven": False, "label": "khung thử nghiệm -- cần theo dõi hiệu suất thật"},
]

# Khung giờ RIÊNG cho Phong Thuỷ (khác DEFAULT_TIME_SLOTS ở trên, vốn dựa
# trên phân tích traffic thật CỦA KÊNH PHẬT GIÁO -- không có căn cứ áp
# dụng chéo sang kênh khác). 6h ICT/23:00 UTC dành riêng cho nội dung
# lịch/hoàng đạo do hệ thống CŨ phụ trách, xem lich_hoang_dao_generator.py
# docstring -- KHÔNG nằm trong danh sách này để tránh trùng nội dung.
#
# Cập nhật sau khi phân tích thật YouTube Analytics 45 ngày (2026-08-20,
# N=13-17 video/khung, views/ngày đã chuẩn hoá theo tuổi video + retention
# thật): 18h/21h ICT (11:00/14:00 UTC) vượt trội rõ rệt (views/ngày
# 194-243 so với 100-130 ở 12h/15h ICT; 14:00 UTC còn dẫn đầu cả retention
# 62.0%) -- đủ căn cứ gắn is_proven=True. Khung 12h ICT (05:00 UTC) là
# khung YẾU NHẤT về reach (100 views/ngày, thấp nhất) nên đã DỊCH sang
# 19:30 ICT (12:30 UTC), nằm giữa 2 khung đã chứng minh tốt -- giữ
# is_proven=False vì đây là khung MỚI, chưa có dữ liệu thật ở đúng giờ
# này. N vẫn còn khiêm tốn (13-17), nên coi đây là điều chỉnh có căn cứ,
# không phải kết luận cuối cùng -- tiếp tục theo dõi rồi tinh chỉnh thêm.
PHONG_THUY_TIME_SLOTS = [
    {"utc_time": "08:00", "is_proven": False, "label": "15h ICT -- nội dung đa dạng phi-hoàng-đạo"},
    {"utc_time": "11:00", "is_proven": True, "label": "18h ICT -- views/ngày cao nhất (khung đã có traffic thật)"},
    {"utc_time": "12:30", "is_proven": False, "label": "19h30 ICT -- khung mới, thay 12h ICT (yếu nhất) trong dải giờ đã chứng minh tốt"},
    {"utc_time": "14:00", "is_proven": True, "label": "21h ICT -- retention cao nhất (khung đã có traffic thật)"},
]

TIME_SLOTS_BY_TOPIC = {"Phong Thủy": PHONG_THUY_TIME_SLOTS}


def time_slots_for_topic(topic: str) -> list[dict]:
    return TIME_SLOTS_BY_TOPIC.get(topic, DEFAULT_TIME_SLOTS)

MIN_LEAD_HOURS = 2  # đệm an toàn hơn hẳn mức tối thiểu 15 phút của YouTube


def load_registry(topic: str = DEFAULT_TOPIC) -> dict:
    path = _registry_path(topic)
    return read_registry_safe(path)


def save_registry(registry: dict, topic: str = DEFAULT_TOPIC) -> None:
    """Ghi registry -- MERGE với bản mới nhất trên đĩa dưới khoá ngắn hạn
    (xem registry_lock.py) thay vì ghi đè trắng bằng bản trong bộ nhớ, vốn
    có thể cũ hơn nếu 1 tiến trình KHÁC (cùng topic) đã save trong lúc tiến
    trình này đang xử lý (registry được giữ trong bộ nhớ suốt cả batch, có
    thể mất nhiều phút -- xem audit tự động hoá đa kênh, mục C).

    QUAN TRỌNG: `registry` (dict truyền vào) KHÔNG được đồng bộ ngược lại
    bằng bản đã merge -- nếu làm vậy, các key CỦA TIẾN TRÌNH KHÁC vô tình
    "dính" vào bản trong bộ nhớ của tiến trình này, rồi lần save SAU đó sẽ
    coi bản dính đó là "của mình" và ghi đè lại giá trị MỚI HƠN mà tiến
    trình kia vừa cập nhật -- lỗi này đã tự phát hiện qua test thật (2 tiến
    trình giả lập, xem lịch sử sửa) trước khi áp dụng bản này. Chỗ nào cần
    view TƯƠI của TOÀN BỘ registry (vd next_available_slot() chống trùng
    slot đăng) phải tự gọi load_registry(topic) lại, không dựa vào biến cục
    bộ đã cũ."""
    path = _registry_path(topic)
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(path):
        on_disk = read_registry_safe(path)
        merged = {**on_disk, **registry}
        write_registry_atomic(path, merged, production_root=_REGISTRY_PRODUCTION_ROOT)


def save_registry_entry(key: str, entry: dict, topic: str = DEFAULT_TOPIC) -> None:
    """Cập nhật ĐÚNG 1 key trên bản registry MỚI NHẤT trên đĩa, dưới CÙNG 1
    khoá đọc-sửa-ghi -- KHÁC save_registry() (merge CẢ snapshot `registry`
    trong bộ nhớ, vốn có thể chứa giá trị CŨ cho các key KHÁC nếu tiến
    trình này giữ registry trong bộ nhớ lâu -- xem docstring save_registry).

    Codex review điểm #4 (BGM, audit 9 điểm): thêm 1 lần lưu TRUNG GIAN
    giữa chừng xử lý 1 item (persist entry["bgm"] trước khi render, để
    resume không pick lại) làm TĂNG tần suất gọi save giữa chừng 1 batch
    dài -- tăng cửa sổ rủi ro merge-snapshot-cũ của save_registry() dù bug
    nền không phải do BGM tạo ra. Dùng hàm NÀY (chỉ đụng đúng 1 key trên
    bản mới nhất) cho các lần lưu TRUNG GIAN như vậy; save_registry() (merge
    cả batch, giữ hành vi cũ) vẫn dùng cho lần lưu SAU CÙNG khi hoàn tất 1
    bước, như các bước khác (1/2/4/5) đã làm từ trước."""
    path = _registry_path(topic)
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(path):
        on_disk = read_registry_safe(path)
        on_disk[key] = entry
        write_registry_atomic(path, on_disk, production_root=_REGISTRY_PRODUCTION_ROOT)


def next_available_slot(registry: dict, time_slots: list[dict]) -> tuple[str, dict]:
    """Trả về (iso_utc_string, slot_info) cho lần đăng kế tiếp -- cycle qua
    time_slots theo ngày, bắt đầu từ NGÀY MAI (né sát giờ upload xong)."""
    used_slots = {v["publish_at"] for v in registry.values() if v.get("publish_at")}
    now = datetime.now(timezone.utc)
    day_offset = 1
    while True:
        for slot in time_slots:
            hh, mm = map(int, slot["utc_time"].split(":"))
            candidate_date = now.date() + timedelta(days=day_offset)
            candidate = datetime(candidate_date.year, candidate_date.month, candidate_date.day, hh, mm, tzinfo=timezone.utc)
            iso = candidate.strftime("%Y-%m-%dT%H:%M:%SZ")
            if iso not in used_slots and candidate - now > timedelta(hours=MIN_LEAD_HOURS):
                return iso, slot
        day_offset += 1
        if day_offset > 30:
            raise RuntimeError("Không tìm được slot trống trong 30 ngày tới -- registry có vấn đề?")


# Quy tắc sản xuất chuẩn (2026-09-04): Short ĐẦU TIÊN đăng mỗi ngày trên
# kênh Phong Thuỷ BẮT BUỘC là nội dung Lịch Hoàng Đạo của CHÍNH ngày đó
# (xem lich_hoang_dao_generator.py) -- lịch âm/giờ tốt của "hôm nay" chỉ có
# giá trị nếu lên sớm nhất trong ngày, không thể xếp round-robin chung với
# PHONG_THUY_TIME_SLOTS (dành cho nội dung KHÔNG gắn 1 ngày cụ thể, xem
# comment ở PHONG_THUY_TIME_SLOTS). Slot cố định 23:00 UTC = 6h sáng ICT
# NGÀY HÔM SAU của target_date trong tên file -- khớp đúng docstring gốc
# của generator ("đăng cố định 6h sáng mỗi ngày"). Đây LÀ slot sớm nhất
# trong ngày ICT so với cả 4 slot FS khác (15h/18h/19h30/21h ICT), nên tự
# nhiên trở thành Short đầu tiên miễn là chỉ có ĐÚNG 1 file LICH mỗi ngày
# (đúng thiết kế generator: 1 lệnh --date sinh 1 file).
_LICH_HOANG_DAO_EPISODE_RE = re.compile(r"^LICH(\d{4})(\d{2})(\d{2})_LichHoangDao$")
LICH_HOANG_DAO_UTC_TIME = "23:00"


def lich_hoang_dao_publish_slot(episode: str) -> tuple[str, dict] | None:
    """Trả về (iso_utc_string, slot_info) CỐ ĐỊNH cho 1 episode Lịch Hoàng
    Đạo (suy ra ngày mục tiêu TỪ TÊN FILE, không phải ngày xử lý), hoặc
    ``None`` nếu `episode` không khớp đúng định dạng LICHYYYYMMDD_LichHoangDao
    -- fail-closed về nhánh round-robin thường (không tự đoán ngày)."""
    m = _LICH_HOANG_DAO_EPISODE_RE.match(episode)
    if m is None:
        return None
    try:
        target_date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
    hh, mm = map(int, LICH_HOANG_DAO_UTC_TIME.split(":"))
    publish_day = target_date - timedelta(days=1)
    candidate = datetime(publish_day.year, publish_day.month, publish_day.day, hh, mm, tzinfo=timezone.utc)
    iso = candidate.strftime("%Y-%m-%dT%H:%M:%SZ")
    return iso, {"utc_time": LICH_HOANG_DAO_UTC_TIME, "is_proven": False,
                 "label": f"6h ICT {target_date.isoformat()} -- Short ĐẦU TIÊN trong ngày, Lịch Hoàng Đạo (slot cố định, không round-robin)"}


def _voice_for_topic(topic: str) -> str:
    voices_path = PROJECT_ROOT / "topic_voices.json"
    data = json.loads(voices_path.read_text(encoding="utf-8"))
    return data.get("voices", {}).get(topic, data.get("_default", "Binh"))


# Phase 2 PASS WITH CAVEAT (xem PHASE2_FINAL_PATCH_SUMMARY.md): FS ("Phong
# Thủy") + BUD ("Phật giáo") dùng quy ước script "mỗi câu 1 dòng" -- trước
# patch "ranh giới câu/đoạn", MỌI ranh giới đó bị misclassify thành "para" và
# nghe 0.35s giữa MỌI câu, xuyên suốt toàn bộ nội dung ĐÃ PUBLISH. Patch sửa
# ĐÚNG phân loại nhưng giá trị pause TỐI ƯU cho "sentence" của riêng FS/BUD
# CHƯA có bằng chứng đủ mạnh (P1 pilot n=1 cho thấy 0.18s bị đánh giá kém hơn
# 0.35s) -- giữ NGUYÊN 0.35s cho FS/BUD để không đổi trải nghiệm audience đã
# quen. CL ("Hình Sự") KHÔNG dùng quy ước "mỗi câu 1 dòng" (chưa từng có gap
# "para" nào, không liên quan bug này) -- CL PHẢI giữ nguyên default 0.18s
# hiện tại của hệ thống, KHÔNG được đụng vào bằng override này.
#
# QUYẾT ĐỊNH KÊNH NÀO DÙNG OVERRIDE NÀO nằm Ở ĐÂY, tại call site -- KHÔNG suy
# luận tên kênh bên trong core_utils.py/render_engine.py/_short_tts_render.py
# (những module đó chỉ nhận `silence_map` tường minh, không tự biết kênh gì).
#
# Giá trị PHẢI khớp `vieneu_utils.core_utils.FS_BUD_SENTENCE_SAFE_DEFAULT` --
# khoá đồng bộ bằng test_short_batch_runner_silence_override.py (chạy trong
# venv có vieneu_utils; module này chạy dưới python3 hệ thống, không import
# trực tiếp được vieneu_utils nên phải định nghĩa lại tường minh ở đây).
_FS_BUD_TOPICS = {"Phong Thủy", "Phật giáo"}
_FS_BUD_SENTENCE_SAFE_DEFAULT = {"para": 0.35, "sentence": 0.35, "minor": 0.04}

# 3 topic THẬT DUY NHẤT của hệ thống (khớp tên thư mục output/shorts/<topic>/
# và topic_voices.json). SỬA theo Codex review vòng 6: exact-match "im lặng"
# (topic lạ/gõ sai -> rơi về None -> CL default 0.18s) không fail-safe cho
# FS/BUD -- 1 lỗi chính tả nhỏ (vd "Phật giáo " thừa khoảng trắng) sẽ ÂM THẦM
# đổi FS/BUD từ 0.35s về 0.18s mà không ai biết. Validate NGHIÊM tại input
# boundary: topic PHẢI là 1 trong 3 giá trị canonical, nếu không raise lỗi rõ
# ràng thay vì âm thầm default sai.
_KNOWN_TOPICS = {"Phong Thủy", "Phật giáo", "Hình Sự"}


def _silence_map_for_topic(topic: str) -> dict | None:
    """Trả về override silence_map cho FS/BUD, hoặc ``None`` (dùng default
    hệ thống -- ÁP DỤNG CHO CL) cho topic CL. Raise ``ValueError`` cho bất kỳ
    topic nào không nằm trong 3 giá trị canonical đã biết -- KHÔNG âm thầm
    coi topic lạ/gõ sai là CL."""
    if topic not in _KNOWN_TOPICS:
        raise ValueError(
            f"Topic không hợp lệ: {topic!r}. Phải là 1 trong {sorted(_KNOWN_TOPICS)} "
            "(exact match, không tự strip/case-fold) -- kiểm tra lại chính tả/khoảng "
            "trắng thừa, KHÔNG âm thầm coi topic lạ là kênh CL."
        )
    return _FS_BUD_SENTENCE_SAFE_DEFAULT if topic in _FS_BUD_TOPICS else None


def run_tts(text: str, out_wav: Path, cache_dir: Path, topic: str = DEFAULT_TOPIC) -> dict:
    text_file = out_wav.with_suffix(".input.txt")
    text_file.write_text(text, encoding="utf-8")
    cmd = [str(VENV_PYTHON), str(TTS_HELPER_SCRIPT), "--text-file", str(text_file),
           "--voice", _voice_for_topic(topic),
           "--output-wav", str(out_wav), "--cache-dir", str(cache_dir)]
    silence_map = _silence_map_for_topic(topic)
    if silence_map is not None:
        cmd += ["--silence-map-json", json.dumps(silence_map)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    text_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"TTS lỗi: {result.stderr[-800:] or result.stdout[-800:]}")
    lines = [l for l in result.stdout.splitlines() if l.strip().startswith("{")]
    return json.loads(lines[-1])


def resolve_bgm_for_attribution(entry: dict, topic: str) -> dict | None:
    """Xác định thông tin BGM (dict {path, attribution}) dùng để ghi
    attribution vào description -- tách riêng thành hàm thuần (không tác
    dụng phụ) để test độc lập được (Codex review điểm #4 yêu cầu).

    Ưu tiên entry["bgm"] (đã lưu ở bước 3, ĐÚNG track thật đã mix vào
    video). Chỉ fallback về bgm_tracks.bgm_for_topic() (LEGACY, track ĐẦU
    TIÊN cố định) khi entry THIẾU "bgm" VÀ topic nằm trong
    bgm_tracks.LEGACY_SINGLE_TRACK_TOPICS (đã có SẴN đúng 1 track trước
    migration rotation -- BUD/FS). BUG THẬT phát hiện qua Codex CLI review:
    CL ("Hình Sự") có 0 track trước migration -- áp fallback này cho CL sẽ
    gán NHẦM attribution cho track chưa từng mix vào (entry CL cũ thật sự
    không có BGM)."""
    bgm_info = entry.get("bgm")
    if bgm_info is None and topic in bgm_tracks.LEGACY_SINGLE_TRACK_TOPICS:
        bgm_info = bgm_tracks.bgm_for_topic(topic)
    return bgm_info


def backfill_bgm_gain_db(bgm_choice: dict | None, topic: str) -> tuple[dict | None, bool]:
    """G4 (Codex review finding High #1): entry["bgm"] đã lưu vào registry
    TRƯỚC KHI G4 thêm gain_db vào bgm_tracks.py (xác nhận thật: registry
    sản xuất có 28 entry Phật giáo/Phong Thuỷ dạng path+attribution nhưng
    THIẾU gain_db) sẽ khiến bgm_volume_pct tính ra None ở bước render,
    render_short.py âm thầm rơi về default 10% cũ -- TÁI HIỆN ĐÚNG bug E2
    cho mọi entry cũ mỗi lần resume dù catalog đã sửa.

    Trả về (bgm_choice đã backfill nếu cần, đã_thay_đổi: bool) -- tách
    riêng thành hàm THUẦN (không tác dụng phụ ghi registry) để test độc
    lập được, cùng lý do resolve_bgm_for_attribution() đã tách riêng.
    Caller (process_one_segment) tự quyết định lưu lại registry khi
    changed=True.

    FAIL-CLOSED qua bgm_tracks.resolve_gain_db_for_path(): nếu path không
    khớp đúng 1 track nào trong catalog hiện tại, KHÔNG đoán -- trả về
    bgm_choice nguyên vẹn, changed=False (caller giữ hành vi cũ, không áp
    nhầm gain của track khác)."""
    if bgm_choice is None or "gain_db" in bgm_choice:
        return bgm_choice, False
    resolved_gain_db = bgm_tracks.resolve_gain_db_for_path(bgm_choice["path"], topic)
    if resolved_gain_db is None:
        return bgm_choice, False
    return {**bgm_choice, "gain_db": resolved_gain_db}, True


def run_video_render(audio_wav: Path, segments_json: Path, output_mp4: Path, topic: str = DEFAULT_TOPIC,
                      bgm_path: str | None = None, bgm_volume_pct: float | None = None) -> dict:
    # BUG THẬT phát hiện qua phản hồi người dùng (xem phiên làm việc):
    # render_short.py ĐÃ hỗ trợ --bgm (BGMConfig) từ trước, nhưng
    # run_video_render() chưa từng truyền -- Short SINH RA KHÔNG BAO GIỜ có
    # nhạc nền dù khả năng đã có sẵn.
    #
    # bgm_path: caller (process_one_segment) PHẢI tự chọn track qua
    # bgm_tracks.pick_bgm_for_topic() TRƯỚC khi gọi hàm này và truyền path
    # vào đây -- KHÔNG để hàm này tự tra cứu (audit 9 điểm mục #4, xem
    # cảnh báo bgm_tracks.py: mỗi topic giờ có NHIỀU track xoay vòng, tự
    # tra cứu ở đây sẽ rotate 1 lần nữa, khác lần rotate caller đã dùng để
    # lưu attribution vào registry -- track THẬT mix vào video sẽ không
    # khớp attribution ghi trong description, vi phạm giấy phép CC BY 4.0).
    #
    # bgm_volume_pct (G4, finding E2): tương tự -- caller PHẢI tự tính từ
    # ĐÚNG track đã chọn (bgm_choice["gain_db"] qua
    # bgm_tracks.gain_db_to_volume_pct()) và truyền vào đây, KHÔNG để
    # render_short.py tự suy luận -- track nào ứng với gain nào đã được
    # quyết định + lưu registry tại thời điểm pick_bgm_for_topic(), không
    # tính lại ở bước render.
    cmd = [str(VIDEO_TOOL_VENV_PYTHON), str(RENDER_SHORT_SCRIPT),
           "--audio", str(audio_wav), "--segments-json", str(segments_json), "--output", str(output_mp4),
           "--topic", topic]
    if bgm_path:
        cmd += ["--bgm", bgm_path]
        if bgm_volume_pct is not None:
            cmd += ["--bgm-volume-pct", str(bgm_volume_pct)]
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=300, cwd=str(PROJECT_ROOT),
    )
    lines = [l for l in result.stdout.splitlines() if l.strip().startswith("{")]
    if not lines:
        raise RuntimeError(f"Render video không trả JSON: {result.stdout[-500:]} {result.stderr[-500:]}")
    parsed = json.loads(lines[-1])
    if not parsed.get("ok"):
        raise RuntimeError(f"Render video lỗi: {parsed.get('error')}")
    return parsed


def _asset_safety_block_reason(seg_dir: Path, video_path: Path) -> str | None:
    """G5 Codex review round 1 finding #2: the ORIGINAL content-safety scan
    (see the long comment at the render step in process_one_segment()) only
    ran once, inline with the render step itself (`status == "audio_ready"`)
    -- an entry RESUMED at status="video_ready" or "seo_ready" (a prior run
    already passed this exact check once) skipped straight to SEO/upload
    with NO re-scan, even though a human could rename/add an unsafe sibling
    file into `seg_dir`, or an explicit unsafe/review_required sidecar
    record could appear on the tracked video, AFTER that prior run. Same
    fail-closed-defense-in-depth philosophy already used in this function
    for needs_human_review flags and BGM attribution (Codex review rounds
    5/6, see the SEO/upload steps below) -- never trust a saved status
    alone right before an irreversible step, re-verify directly. Returns
    the block reason string if the segment directory/tracked video is
    currently unsafe, else None."""
    legacy_flagged = asset_safety.scan_for_legacy_unsafe_assets(seg_dir)
    try:
        asset_safety.assert_asset_safe_for_assembly(video_path)
        if legacy_flagged:
            raise asset_safety.AssetSafetyBlockedError(
                f"thư mục output '{seg_dir}' chứa {len(legacy_flagged)} file bị đánh dấu unsafe theo "
                f"quy ước tên cũ: {[str(p) for p in legacy_flagged]}"
            )
    except asset_safety.AssetSafetyBlockedError as exc:
        return str(exc)
    return None


CL_TOPIC = "Hình Sự"


def _run_cl_phase_c_d_and_upload(entry: dict, seg_dir: Path, wav_path: Path, video_path: Path,
                                  credentials_path: str, publish_at: str) -> tuple:
    """CL Risk Gate Stage 3 (task #241) -- Phase C (post-render audio
    chain-of-custody + sampled-frame OCR person-reference check) + Phase D
    (atomic UploadManifest + exclusive staging + safe upload), chạy NGAY
    TRƯỚC upload thật cho CL Short, cùng vị trí/tinh thần fail-closed với
    các gate khác trong process_one_segment() (asset-safety, needs_human_
    review...). Trả (passed, reason, video_id_or_None) -- KHÔNG BAO GIỜ
    raise ra ngoài (mọi lỗi -- kể cả bug lập trình không lường trước --
    phải trở thành fail-closed needs_review, không phải crash cả batch).

    THÍCH NGHI KIẾN TRÚC THẬT cho pipeline Short cụ thể này, ghi rõ thay vì
    giấu (xem CL_GATE_WIRING_TODO ở cl_risk_gate_orchestrator.py cho thiết
    kế gốc đã duyệt):
    - N=1 segment: run_tts() (hàm ở trên) sinh ĐÚNG 1 file WAV cho toàn bộ
      script (không per-câu như Long-form) -- "audio custody chain" suy
      biến về 1 segment DUY NHẤT.
    - Mix collapses vào bước render: đọc trực tiếp core/stockfootage/
      assembly_job.py (video_tool_clone) xác nhận render_short.py mix BGM
      VÀ encode video trong CÙNG 1 lệnh ffmpeg -filter_complex -- KHÔNG có
      file "audio đã mix, chưa encode" trung gian nào để hash riêng.
      record_mix_manifest()'s mixed_output_path vì vậy nhận CHÍNH
      video_path (điểm SỚM NHẤT audio-đã-mix thực sự tồn tại thành file).
    - Không có thumbnail asset cho Short (khác Long-form, task #132) --
      stage_artifacts_exclusive()/assemble_upload_manifest()/safe_upload()
      gọi với thumbnail_path=None (xem docstring UploadManifest,
      cl_risk_gate_lifecycle.py -- adaptation riêng cho increment này).

    run_id sinh MỚI mỗi LẦN GỌI hàm này (mỗi lần thử upload, không phải cố
    định theo candidate) -- khớp đúng thiết kế exclusive-create của
    stage_artifacts_exclusive() (fail loud nếu reuse run_id, xem docstring
    ở đó): retry sau lỗi Phase D giữa chừng phải có staging path MỚI,
    không cố ghi đè debris của lần thử trước.

    Description KHÔNG được ghi kèm attribution BGM lúc gọi assemble_upload_
    manifest() (entry["seo"] giữ NGUYÊN VĂN bản Phase A đã review, để
    current_editorial_hash khớp reviewed_editorial_hash) -- attribution
    (chuỗi cố định, không phải nội dung model sinh, không cần review) chỉ
    được nối vào NGAY TRƯỚC lệnh upload_short() thật, bên trong _upload_fn.

    KHÔNG gọi cl_risk_gate_lifecycle.verify_phase_c_audio_chain() (bug thật
    tự bắt khi viết integration test cho hàm này, không phải Codex/Cursor
    round nào): hàm đó reconstruct segment bằng CÁCH TÁCH LẠI reviewed_
    final_script_text theo CÂU (_SEGMENT_SPLIT_RE -- ranh giới .!?/xuống
    dòng), rồi so số lượng với expected_segments -- ĐÚNG cho thiết kế gốc
    (N segment TTS thật, mỗi câu 1 file audio riêng), nhưng SAI cho CL
    Short: final_script luôn nhiều câu (script thật, không phải 1 câu),
    trong khi expected_segments chỉ có ĐÚNG 1 record (N=1, 1 WAV cho toàn
    bộ script) -- gọi thẳng hàm đó sẽ LUÔN fail "số đoạn script khác số
    segment audio" cho MỌI script CL thật, khoá cứng pipeline vô lý.

    FIX (review độc lập Cursor/Grok round 1, HIGH #2 -- "custody N=1 đang
    tự xác nhận trong cùng một lần gọi"): bản đầu tính narration_stem_hash/
    mix_manifest/script_text_hash NGAY TRONG hàm này rồi tự so với CHÍNH
    giá trị vừa tính vài dòng trước đó -- tautological, KHÔNG bắt được
    trường hợp wav_path/video_path bị thay/hỏng GIỮA lúc TTS/render xong
    (Phase B, các bước 2-3 ở process_one_segment()) và lúc hàm này chạy
    (Phase C, bước 5, có thể CÁCH RẤT XA về thời gian/khác cả tiến trình
    nếu resume sau crash). Giờ so khớp hash TÍNH LẠI Ở ĐÂY (bước 5) với hash
    đã PERSIST vào registry NGAY SAU KHI file được tạo (bước 2 TTS ghi
    entry["cl_narration_stem_hash"], bước 3 render ghi entry["cl_video_
    audio_hash"]) -- 2 thời điểm THẬT SỰ khác nhau, đóng đúng invariant
    chain-of-custody (phát hiện file bị thay/hỏng giữa 2 mốc), không còn
    tự xác nhận trong 1 lần gọi. script_text_hash so PERSISTED CHÍNH TỪ
    SIDECAR (entry["cl_reviewed_script_hash"], đã verify khớp bundle .txt
    ở bước 1) -- không cần tính lại vì entry["final_script"] bất biến từ
    bước 1, không đọc lại từ đĩa."""
    from cl_risk_gate_lifecycle import (
        LifecycleError, compute_narration_stem_hash, _decode_pcm_hash, _script_text_hash,
        sample_frame_timestamps, sample_and_ocr_frames, run_visual_person_reference_check,
        stage_artifacts_exclusive, assemble_upload_manifest, safe_upload, _pcm_duration_s,
    )
    import cl_risk_gate as _g

    try:
        final_script = entry["final_script"]
        named = entry.get("cl_named_individuals") or []
        candidate = _g.CandidateCase(
            case_id=entry.get("cl_case_id", entry["key"]), case_key=entry.get("cl_case_id", entry["key"]),
            working_title=entry.get("cl_final_editorial", {}).get("title", ""),
            named_individuals=[
                _g.NamedIndividual(
                    canonical_name=p["canonical_name"], identity_confidence="high",
                    role=p.get("role", "named_relative_or_associate"),
                    short_form_alias=p.get("short_form_alias"),
                )
                for p in named if isinstance(p, dict) and p.get("canonical_name")
            ],
        )

        persisted_narration_hash = entry.get("cl_narration_stem_hash")
        persisted_video_audio_hash = entry.get("cl_video_audio_hash")
        persisted_script_hash = entry.get("cl_reviewed_script_hash")
        if not persisted_narration_hash or not persisted_video_audio_hash or not persisted_script_hash:
            return False, "Thiếu hash custody đã persist tại bước TTS/render/sidecar-gate (entry cũ/thiếu field) -- fail-closed, không thể xác lập chain-of-custody.", None

        if _script_text_hash(final_script) != persisted_script_hash:
            return False, "Audio custody chain đứt: final_script hiện tại khác cl_reviewed_script_hash đã persist -- entry có thể đã bị sửa tay/hỏng.", None

        current_narration_hash = compute_narration_stem_hash([wav_path])
        if current_narration_hash != persisted_narration_hash:
            return False, "Audio custody chain đứt: narration wav hiện tại khác hash đã persist NGAY SAU TTS -- file có thể đã bị thay/hỏng.", None

        current_video_audio_hash = _decode_pcm_hash(video_path)
        if current_video_audio_hash != persisted_video_audio_hash:
            return False, "Audio custody chain đứt: video hiện tại khác hash audio đã persist NGAY SAU render -- file có thể đã bị thay/hỏng.", None

        video_duration_s = _pcm_duration_s(video_path)
        frame_timestamps = sample_frame_timestamps(video_duration_s, [], video_path)
        frame_samples = sample_and_ocr_frames(video_path, frame_timestamps, seg_dir / "cl_phase_c_frames")
        # FIX (bug thật phát hiện qua publish thật, task #270): content
        # STORYTELLING (phase_a_variant="storytelling_v1", named_individuals
        # LUÔN rỗng) đi qua run_visual_person_reference_check() dùng chung
        # (cl_risk_gate_lifecycle.py) bị chặn NHẦM ở danh từ vai trò IN HOA
        # style phụ đề Short ("NGƯỜI ĐÁNH BẠC", "NGƯỜI CHỊU ÁN") -- CÙNG lớp
        # bug đã sửa cho check dạng text ở criminal_law_storytelling_phase_a.
        # py. Dùng đúng biến thể HẸP tương ứng cho content type này; content
        # case pipeline nặng (phase_a_variant khác/None) vẫn dùng nguyên hàm
        # chung, KHÔNG đổi hành vi.
        if entry.get("cl_phase_a_variant") in ("storytelling_v1", "storytelling_provenance_v1"):
            # storytelling_provenance_v1 (C4 Round 6) dùng CHUNG lớp person-
            # check này -- named_individuals cũng LUÔN rỗng cho content type
            # này (xem cl_story_fact_pack.py: fact pack không trích danh
            # tính nào ngoài đã có trong nguồn). Person-check text-level ở
            # Phase A fail-closed cho bất kỳ tên người thật cụ thể nào, TRỪ
            # 1 miễn trừ HẸP cho nhân vật lịch sử đã qua xác minh 2 model
            # độc lập (xem _independent_historical_figure_exempt(), task
            # #310) -- run_storytelling_visual_person_check() tái dùng ĐÚNG
            # cổng đó nên hành vi (kể cả miễn trừ) nhất quán với text-level.
            from criminal_law_storytelling_phase_a import run_storytelling_visual_person_check
            ok, msg = run_storytelling_visual_person_check(frame_samples)
        else:
            ok, msg, _refs = run_visual_person_reference_check(frame_samples, candidate)
        if not ok:
            return False, msg, None

        run_id = uuid.uuid4().hex
        staging_dir = PROJECT_ROOT / "output" / "cl_staging"
        video_lock_dir = PROJECT_ROOT / "output" / "locks"
        staged_video_path, staged_thumbnail_path = stage_artifacts_exclusive(run_id, video_path, None, staging_dir)

        upload_policy_values = {
            "scheduling": publish_at, "privacy_setting": "private",
            "channel_account_id": credentials_path, "upload_operation_mode": "scheduled_private_publish_at",
        }
        manifest_result = assemble_upload_manifest(
            run_id=run_id, staged_video_path=staged_video_path, staged_thumbnail_path=staged_thumbnail_path,
            audio_chain_manifest_hash=current_video_audio_hash,
            current_editorial=entry["seo"], reviewed_editorial_hash=entry["cl_reviewed_editorial_hash"],
            upload_policy_values=upload_policy_values, expected_channel_account_id=credentials_path,
        )
        if not manifest_result.passed:
            return False, f"Phase D manifest ({manifest_result.reason_code}): {manifest_result.evidence}", None

        bgm_info = entry.get("bgm")
        attribution = bgm_info["attribution"] if bgm_info else None

        def _upload_fn(video_fileobj, thumbnail_bytes, editorial_values, upload_policy_values_):
            # video_fileobj đã được safe_upload() mở/hash/seek(0) DƯỚI CÙNG
            # FileLock đang giữ khi closure này chạy -- upload_short() chỉ
            # nhận path (không nhận file object), nên đọc lại ĐÚNG path đã
            # stage (read-only, chmod 0o444, cùng bytes vừa hash) an toàn
            # tại đây, không mở lại path GỐC có thể còn mutable.
            description = editorial_values["description"]
            if attribution and attribution not in description:
                description = description.rstrip() + "\n\n" + attribution
            return upload_short(
                manifest_result.manifest.staged_video_path, editorial_values["title"], description,
                editorial_values["tags"], upload_policy_values_["scheduling"], credentials_path,
            )

        video_id = safe_upload(manifest_result.manifest, _upload_fn, video_lock_dir)
        return True, "CL Phase C/D PASS, upload thật đã gửi.", video_id
    except LifecycleError as exc:
        return False, f"CL Phase C/D lỗi (fail-closed): {exc}", None
    except Exception as exc:  # noqa: BLE001 -- fail-closed cho MỌI lỗi không lường trước, không để crash cả batch
        return False, f"CL Phase C/D lỗi không lường trước (fail-closed, loại: {type(exc).__name__}): {exc}", None


def _validate_provenance_binding(episode: str, topic: str, script_text: str) -> str | None:
    """CỔNG TIÊU THỤ (consumer) cho variant "storytelling_provenance_v1"
    (C4 Round 6) -- mirror đúng kỷ luật của cl_claim_ledger.validate_fact_
    verification_binding(): KHÔNG tin field tự khai nào trong sidecar,
    đọc LẠI artifact thật trên đĩa (fact pack + story plan + script
    binding) rồi tính lại/đối chiếu TẠI THỜI ĐIỂM publish. Trả None nếu
    hợp lệ (không chặn), ngược lại trả lý do chặn (string).

    Đọc lazy (import trong hàm) để short_batch_runner.py không kéo theo
    cl_story_fact_pack.py/cl_story_plan_and_generation.py cho MỌI import
    module này (kể cả khi không dùng CL provenance) -- cùng phong cách
    lazy-import đã dùng cho các module CL khác trong file này."""
    import cl_story_fact_pack
    import cl_story_plan_and_generation as spg

    plan_path = cl_story_plan_sidecar_path(episode, topic)
    binding_path = cl_script_binding_sidecar_path(episode, topic)
    if not plan_path.exists() or not binding_path.exists():
        return f"Thiếu sidecar provenance bắt buộc ('{plan_path.name}' hoặc '{binding_path.name}') -- nội dung CHƯA qua provenance pipeline đầy đủ."
    try:
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        binding_data = json.loads(binding_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return f"Lỗi đọc/parse sidecar provenance: {exc}."

    topic_id = plan_data.get("topic_id")
    if not isinstance(topic_id, str) or not topic_id.strip():
        return "story_plan.json thiếu topic_id hợp lệ."

    # Fact pack đọc LẠI từ đĩa (KHÔNG dùng lại object đã build lúc Phase A --
    # đây chính là điểm re-derive: nếu pack đã bị rebuild/sửa/xoá kể từ lúc
    # sinh, pack_hash() tính lại SẼ khác binding.pack_hash_at_generation).
    pack = cl_story_fact_pack.load_fact_pack(topic_id)
    if pack is None:
        return f"Không tìm thấy Story Fact Pack cho topic_id={topic_id!r} trên đĩa -- có thể đã bị xoá/chưa từng tồn tại."

    current_pack_hash = pack.pack_hash()
    if plan_data.get("fact_pack_hash") != current_pack_hash:
        return (
            f"story_plan.json.fact_pack_hash ({plan_data.get('fact_pack_hash')}) không khớp fact pack HIỆN TẠI "
            f"trên đĩa (hash={current_pack_hash}) -- pack đã bị rebuild/sửa kể từ lúc plan được tạo."
        )
    if binding_data.get("fact_pack_hash") != current_pack_hash:
        return f"script_binding.json.fact_pack_hash không khớp fact pack hiện tại trên đĩa -- fail-closed."
    if binding_data.get("plan_hash") != plan_data.get("plan_hash"):
        return "script_binding.json.plan_hash không khớp story_plan.json hiện tại -- plan đã bị đổi kể từ lúc binding được tạo."

    bindings = binding_data.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        return "script_binding.json thiếu 'bindings' hợp lệ."

    # Script HIỆN TẠI (seg["text"], đã qua so khớp reviewed_script_hash ở
    # bước trên) phải khớp CHÍNH XÁC văn bản đã ghép từ bindings trên đĩa --
    # chặn trường hợp binding thật nhưng script đã bị soạn/thay khác đi mà
    # 2 bên hash script (reviewed_script_hash) tình cờ vẫn khớp nhau (không
    # thể xảy ra với sha256 thật, nhưng đây là lớp kiểm tra độc lập thứ 2,
    # không phụ thuộc riêng 1 phép so khớp hash duy nhất).
    joined_prose = "\n".join(b.get("prose", "") for b in bindings)
    if joined_prose.strip() != script_text.strip():
        return "Văn bản ghép từ script_binding.json.bindings không khớp script đang publish -- fail-closed."

    integrity_violations = spg.validate_binding_integrity(bindings, pack)
    if integrity_violations:
        return f"Binding integrity fail (fail-closed): {integrity_violations}"
    guard_violations = spg.run_deterministic_guards(bindings, pack)
    if guard_violations:
        return f"Numeric guard fail (fail-closed): {guard_violations}"
    # KHÔNG chạy lại C4 drift detector ở consumer boundary (đã chạy ở Phase
    # A, tốn LLM call thật) -- integrity + numeric guard ở đây LÀ đủ để
    # phát hiện binding bị copy/sửa/stale (mục tiêu của cổng consumer,
    # khác mục tiêu của Phase A là phát hiện drift ngữ nghĩa lúc SINH).
    return None


def process_one_segment(seg: dict, out_dir: Path, credentials_path: str, time_slots: list[dict], registry: dict,
                         playlist_title: str | None, hook_pass_threshold: int, dry_run: bool, topic: str = DEFAULT_TOPIC) -> dict:
    key = seg["key"]
    entry = registry.get(key, {"key": key, "episode": seg["episode"], "segment_index": seg["segment_index"]})
    known_status = entry.get("status")

    # Chống 2 tiến trình CÙNG topic chạy đồng thời cùng chọn trùng 1 đoạn
    # (registry trong bộ nhớ được load 1 LẦN lúc bắt đầu cả batch -- có thể
    # cũ nếu tiến trình khác đã tiến triển đoạn này từ đó tới giờ, dù đoạn
    # đó đang ở bước dở dang có thể resume bình thường, vd "audio_ready" từ
    # 1 lần chạy trước bị ngắt giữa chừng). So sánh status TƯƠI trên đĩa với
    # status đã biết LÚC ĐỌC registry ban đầu -- nếu KHÁC, nghĩa là 1 tiến
    # trình khác vừa động vào đoạn này, bỏ qua thay vì làm trùng; nếu GIỐNG
    # (không ai động vào), tiến hành resume/xử lý bình thường dù status là
    # gì. Không xoá được hoàn toàn cửa sổ race (vẫn còn khoảng ngắn giữa lần
    # đọc này và lần ghi status đầu tiên), chỉ thu hẹp đáng kể -- xem audit
    # tự động hoá đa kênh, mục C, rủi ro được ghi nhận là "hẹp".
    fresh_entry = load_registry(topic).get(key)
    fresh_status = fresh_entry.get("status") if fresh_entry else None
    if fresh_status != known_status:
        print(f"[{key}] Bỏ qua -- tiến trình khác (cùng topic) đã đổi trạng thái đoạn này kể từ lần đọc trước ({known_status!r} -> {fresh_status!r}).", flush=True)
        if fresh_entry:
            registry[key] = fresh_entry
        return fresh_entry or entry

    seg_dir = out_dir / seg["episode"]
    seg_dir.mkdir(parents=True, exist_ok=True)

    # 1. Review hook (judge panel) -- CHỈ áp dụng cho topic mặc định (Phật
    # giáo). BUG THẬT phát hiện khi rà soát trước khi mass-produce Phong
    # Thuỷ (xem phiên làm việc): review_and_optimize_short() (short_content_
    # review.py) viết CHO "kênh Phật giáo tiếng Việt", ràng buộc "KHÔNG đổi
    # Ý GIÁO LÝ" -- áp cho topic khác vừa vô nghĩa vừa RỦI RO: đây là bước
    # rewrite domain-blind/KHÔNG có facts để fact-check, có thể VÔ TÌNH XOÁ
    # các sửa chữa category-aware đã làm kỹ trong short_judge_panel_engine.py
    # (vd viết lại làm rò rỉ "Hoàng Đạo", liệt kê giờ...) mà không ai kiểm
    # tra lại. Script nguồn của các topic KHÁC Phật giáo (Phong Thuỷ...) đã
    # được CHÍNH generator sinh ra tự viết hook A/B/C + judge-panel fact-
    # check + category rubric NGAY TỪ ĐẦU (xem short_judge_panel_engine.py)
    # -- dùng thẳng, không review lại lần 2 domain-blind.
    if entry.get("status") in (None, "pending"):
        if topic == CL_TOPIC:
            # CL Risk Gate Stage 3 (task #241): CL Short BẮT BUỘC đi qua
            # run_cl_case_gate() (Phase A review) TRƯỚC KHI tới đây -- sidecar
            # JSON (ghi bởi cl_case_batch.py cùng lúc với file .txt bundle) là
            # BẰNG CHỨNG DUY NHẤT của việc đó. KHÔNG dùng nhánh "topic !=
            # DEFAULT_TOPIC" chung ở dưới (seg["text"] đi thẳng vào final_script
            # mà không qua review nào) -- làm vậy sẽ BỎ QUA HOÀN TOÀN Stage
            # 1/2/3 safety cho bất kỳ file .txt nào lỡ rơi vào drive_input/
            # content_repo_staged/Hình Sự/Short/ (thủ công/nhầm lẫn), tái hiện
            # đúng lớp sự cố CL từng xảy ra thật (chọn nhầm case có nạn nhân vị
            # thành niên, xem docstring twice_weekly_batch.py) dưới 1 đường
            # vòng mới. Fail-closed nếu sidecar thiếu/hỏng -- không tự đoán.
            sidecar_path = cl_metadata_sidecar_path(seg["episode"], topic)
            sidecar = None
            error_reason = None
            if not sidecar_path.exists():
                error_reason = f"Không tìm thấy sidecar CL Risk Gate ('{sidecar_path}') -- nội dung CHƯA qua Phase A review."
            else:
                try:
                    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError) as exc:
                    error_reason = f"Sidecar CL Risk Gate lỗi đọc/parse ('{sidecar_path}'): {exc}."
                else:
                    missing = [f for f in ("reviewed_editorial_hash", "reviewed_script_hash", "final_editorial", "named_individuals") if f not in sidecar]
                    if missing:
                        error_reason = f"Sidecar CL Risk Gate thiếu field bắt buộc {missing}."
                    else:
                        # FIX (review độc lập Cursor/Grok, HIGH #1): reviewed_
                        # editorial_hash CHỈ cover title/description/tags/
                        # thumbnail_brief (_EDITORIAL_FIELDS) -- KHÔNG cover
                        # final_script. Trước fix này, đổi file .txt bundle
                        # SAU KHI cl_case_batch.py ghi sidecar (thủ công/nhầm
                        # lẫn) vẫn qua được gate: sidecar vẫn "hợp lệ" nhưng
                        # script Phase A đã review (C4/C7/claim/person-ref)
                        # KHÔNG CÒN LÀ script sắp TTS/render/upload. So khớp
                        # TRỰC TIẾP hash script -- fail-closed nếu lệch,
                        # KHÔNG tự động re-run Phase A (cần người/agent chạy
                        # lại cl_case_batch.py để có sidecar khớp bundle mới).
                        from cl_risk_gate_lifecycle import _script_text_hash as _cl_script_hash
                        actual_script_hash = _cl_script_hash(seg["text"])
                        if actual_script_hash != sidecar["reviewed_script_hash"]:
                            error_reason = (
                                f"Script trong bundle .txt KHÔNG khớp reviewed_script_hash trong sidecar "
                                f"(expected={sidecar['reviewed_script_hash'][:16]}... actual={actual_script_hash[:16]}...) -- "
                                f"script đã bị đổi SAU khi Phase A review."
                            )
                        elif sidecar.get("phase_a_variant") == "storytelling_v1":
                            # Vá lỗi thật phát hiện qua review độc lập (yêu cầu
                            # vá lỗi "CLOSE PUBLISH-BOUNDARY BYPASS"): reviewed_
                            # script_hash CHỈ chứng minh script KHỚP sidecar --
                            # KHÔNG chứng minh sidecar đó THẬT SỰ đến từ claim-
                            # ledger gate (run_cl_storytelling_phase_a.py). 1
                            # sidecar viết tay/scratchpad với reviewed_script_
                            # hash tính đúng (hàm hash không phải bí mật, ai
                            # cũng gọi lại được) NHƯNG fact_verification giả/
                            # thiếu/copy từ episode khác vẫn qua được TRƯỚC
                            # bước này. validate_fact_verification_binding()
                            # đối chiếu LẠI với ledger THẬT trên đĩa + ràng
                            # buộc claim với CHÍNH script này -- KHÔNG tin field
                            # tự khai suông. CHỈ áp dụng cho sidecar storytelling
                            # (phase_a_variant="storytelling_v1") -- case pipeline
                            # nặng (cl_case_batch.py, không có field này) đã có
                            # C1-C7 xác minh nguồn thật riêng, không đi qua nhánh
                            # claim-ledger này.
                            fv_ok, fv_reason = cl_claim_ledger.validate_fact_verification_binding(
                                sidecar.get("fact_verification"), seg["text"],
                            )
                            if not fv_ok:
                                error_reason = f"fact_verification không hợp lệ: {fv_reason}"
                        elif sidecar.get("phase_a_variant") == "storytelling_provenance_v1":
                            # C4 Round 6 -- consumer RE-DERIVE toàn bộ provenance
                            # TẠI THỜI ĐIỂM publish, không tin lại provenance_state
                            # tự khai trong sidecar (yêu cầu tích hợp §20 "CONSUMER
                            # MUST RE-DERIVE TRUST"). Đọc LẠI fact pack + story
                            # plan + script binding từ đĩa (3 sidecar riêng, xem
                            # short_segment_discovery.py), tính lại hash, gọi lại
                            # validate_binding_integrity()/run_deterministic_guards()
                            # NGAY TẠI ĐÂY -- 1 sidecar giả/copy/stale với đúng
                            # reviewed_script_hash (hash không phải bí mật) vẫn
                            # KHÔNG qua được nếu fact pack/plan/binding trên đĩa
                            # không khớp, hoặc pack đã bị rebuild kể từ lúc sinh.
                            error_reason = _validate_provenance_binding(seg["episode"], topic, seg["text"])
                            if error_reason is None:
                                # Phần claim-ledger dùng LẠI ĐÚNG hàm consumer đã
                                # có (KHÔNG viết lại cổng xác minh song song) --
                                # cùng lý do variant "storytelling_v1" ở trên.
                                fv_ok, fv_reason = cl_claim_ledger.validate_fact_verification_binding(
                                    sidecar.get("fact_verification"), seg["text"],
                                )
                                if not fv_ok:
                                    error_reason = f"fact_verification không hợp lệ: {fv_reason}"
            if error_reason:
                entry["status"] = "needs_review"
                entry["needs_human_review_cl_gate"] = f"{error_reason} KHÔNG được tự động TTS/render/upload."
                registry[key] = entry
                save_registry(registry, topic)
                print(f"[{key}] DỪNG: {entry['needs_human_review_cl_gate']}", flush=True)
                return entry
            entry["hook_score"] = None
            entry["needs_human_review_hook"] = False
            entry["final_script"] = seg["text"]
            entry["cl_case_id"] = sidecar.get("case_id", key)
            entry["cl_reviewed_editorial_hash"] = sidecar["reviewed_editorial_hash"]
            entry["cl_reviewed_script_hash"] = sidecar["reviewed_script_hash"]
            entry["cl_final_editorial"] = sidecar["final_editorial"]
            entry["cl_named_individuals"] = sidecar["named_individuals"]
            entry["cl_phase_a_variant"] = sidecar.get("phase_a_variant")
            entry["status"] = "scripted"
            registry[key] = entry
            save_registry(registry, topic)
        elif topic != DEFAULT_TOPIC:
            print(f"[{key}] Bỏ qua review hook chung (script đã qua judge-panel category-aware riêng của generator lúc sinh) -- dùng thẳng.", flush=True)
            entry["hook_score"] = None
            entry["needs_human_review_hook"] = False
            entry["final_script"] = seg["text"]
            entry["status"] = "scripted"
            registry[key] = entry
            save_registry(registry, topic)
        else:
            print(f"[{key}] Review hook...", flush=True)
            review = review_and_optimize_short(seg["text"], max_rounds=3, pass_threshold=hook_pass_threshold)
            entry["hook_score"] = review["hook_score"]
            entry["needs_human_review_hook"] = review["needs_human_review"]
            entry["final_script"] = review["final_script"]
            # BUG THẬT phát hiện qua Codex CLI review độc lập (xem phiên làm
            # việc): trước đây status LUÔN chuyển "scripted" bất kể
            # needs_human_review_hook -- cờ chỉ được GHI LẠI, không hề GATE
            # pipeline, nên TTS/render/SEO/upload vẫn chạy tiếp và ĐĂNG THẬT
            # lên YouTube dù script chưa từng đạt ngưỡng chất lượng sau
            # MAX_ROUNDS vòng review (chỉ là "bản tốt nhất tìm được", không
            # phải bản đã PASS). Sửa: fail-closed -- needs_human_review=True
            # thì DỪNG HẲN ở đây, không tự tiến further, cần người duyệt thủ
            # công rồi chạy lại (không nằm trong TERMINAL_STATUSES nên vẫn
            # resumable, nhưng KHÔNG bị batch tự động chọn lại -- xem TERMINAL_STATUSES).
            entry["status"] = "needs_review" if review["needs_human_review"] else "scripted"
            registry[key] = entry
            save_registry(registry, topic)
            if review["needs_human_review"]:
                print(f"[{key}] DỪNG: hook chưa đạt ngưỡng sau review -- CẦN NGƯỜI DUYỆT thủ công trước khi tiếp tục, KHÔNG tự động TTS/render/upload.", flush=True)
                return entry

    # 2. TTS
    wav_path = seg_dir / f"{seg['segment_index']:02d}_short.wav"
    json_path = wav_path.with_suffix(".json")
    if entry.get("status") == "scripted":
        print(f"[{key}] TTS render...", flush=True)
        run_tts(entry["final_script"], wav_path, seg_dir / "cache" / f"seg{seg['segment_index']}", topic)
        if topic == CL_TOPIC:
            # FIX (review độc lập Cursor/Grok, HIGH #2): persist hash NGAY
            # SAU KHI TTS tạo file wav THẬT -- Phase C (bước 5, có thể chạy
            # RẤT LÂU sau, kể cả ở lần resume KHÁC tiến trình/máy) so khớp
            # LẠI hash TẠI THỜI ĐIỂM ĐÓ với giá trị đã persist NGAY ĐÂY, bắt
            # được tampering/hỏng file GIỮA 2 thời điểm khác nhau thật --
            # khác hẳn bản trước (tính lại rồi tự so với chính nó trong
            # CÙNG 1 lần gọi hàm, vô nghĩa/tautological, đã bị chỉ ra).
            from cl_risk_gate_lifecycle import compute_narration_stem_hash as _cl_narration_hash
            entry["cl_narration_stem_hash"] = _cl_narration_hash([wav_path])
        entry["status"] = "audio_ready"
        registry[key] = entry
        save_registry(registry, topic)

    # 3. Render video
    video_path = seg_dir / f"{seg['segment_index']:02d}_short_render.mp4"
    if entry.get("status") == "audio_ready":
        # Chọn BGM TRƯỚC render, LƯU NGAY vào registry (Codex review điểm
        # #4: nếu pick rồi crash TRƯỚC khi lưu, lần resume sẽ pick lại --
        # rotation_state.pick_and_commit_next() đã atomic/không mất mát,
        # nhưng vẫn TIÊU HAO 1 lượt xoay vòng vô ích mỗi lần crash giữa
        # chừng). Nếu entry["bgm"] đã tồn tại (resume sau crash SAU khi đã
        # lưu nhưng TRƯỚC khi render xong) -- DÙNG LẠI, không pick lại.
        if "bgm" in entry:
            # G4 (Codex review finding High #1): backfill gain_db cho entry
            # cũ đã lưu TRƯỚC KHI G4 thêm gain_db vào catalog -- không
            # backfill sẽ tái hiện đúng bug E2 mỗi lần resume (xem docstring
            # backfill_bgm_gain_db()).
            bgm_choice, gain_db_backfilled = backfill_bgm_gain_db(entry["bgm"], topic)
            if gain_db_backfilled:
                entry["bgm"] = bgm_choice
                registry[key] = entry
                save_registry_entry(key, entry, topic)
        else:
            picked = bgm_tracks.pick_bgm_for_topic(topic)
            # G4 (finding E2): lưu luôn gain_db (dùng để tính volume_pct
            # mix vào video) cùng lúc với path/attribution -- CÙNG 1 lần
            # pick, CÙNG 1 track, không tách rời gain khỏi track thật đã
            # chọn (tương tự lý do attribution phải khớp track thật, xem
            # cảnh báo bgm_tracks.py).
            bgm_choice = (
                {"path": str(picked["path"]), "attribution": picked["attribution"], "gain_db": picked["gain_db"]}
                if picked else None
            )
            entry["bgm"] = bgm_choice
            registry[key] = entry
            # save_registry_entry() (chỉ đụng đúng key này trên bản mới
            # nhất), KHÔNG dùng save_registry() (merge cả snapshot batch)
            # cho lần lưu TRUNG GIAN này -- xem docstring save_registry_entry.
            save_registry_entry(key, entry, topic)

        print(f"[{key}] Render video...", flush=True)
        bgm_volume_pct = (
            bgm_tracks.gain_db_to_volume_pct(bgm_choice["gain_db"])
            if bgm_choice and "gain_db" in bgm_choice else None
        )
        run_video_render(wav_path, json_path, video_path, topic=topic,
                          bgm_path=bgm_choice["path"] if bgm_choice else None,
                          bgm_volume_pct=bgm_volume_pct)

        if topic == CL_TOPIC:
            # FIX (review độc lập Cursor/Grok, HIGH #2, tiếp): persist hash
            # audio của video NGAY SAU KHI render xong (mix BGM + encode đã
            # xảy ra bên trong render_short.py, xem docstring _run_cl_phase_
            # c_d_and_upload()) -- Phase C so khớp LẠI ở bước 5 để bắt file
            # video bị thay/hỏng SAU render, TRƯỚC upload.
            from cl_risk_gate_lifecycle import _decode_pcm_hash as _cl_decode_pcm_hash
            entry["cl_video_audio_hash"] = _cl_decode_pcm_hash(video_path)

        # G5 (Video Generation remediation): BUG THẬT phát hiện qua audit --
        # 1 video output thật (output/shorts/Hình Sự/LUATHS_AnTreo/
        # 01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4) từng bị con người
        # đánh dấu unsafe CHỈ BẰNG CÁCH đổi tên file thành 1 tên KHÁC tên
        # chuẩn (nằm CÙNG thư mục với 01_short_render.mp4 "đã sửa"), và
        # KHÔNG CÓ GÌ trong pipeline từng đọc/tôn trọng tên đó -- item vẫn
        # có thể tiến thẳng lên video_ready/seo_ready/uploaded như bình
        # thường. Quét CẢ THƯ MỤC segment (không chỉ đúng 1 file video_path
        # chuẩn) để bắt đúng dạng sự cố này -- 1 file rác cùng thư mục mang
        # tên UNSAFE/DO_NOT_USE, dù registry không hề trỏ tới nó, vẫn phải
        # chặn resume/tiếp tục cho tới khi con người dọn/duyệt. Cùng nguyên
        # tắc fail-closed như review hook/SEO ở trên.
        block_reason = _asset_safety_block_reason(seg_dir, video_path)
        if block_reason is not None:
            entry["status"] = "needs_review"
            entry["video_path"] = str(video_path)
            entry["needs_human_review_asset_safety"] = block_reason
            registry[key] = entry
            save_registry(registry, topic)
            print(f"[{key}] DỪNG: video output bị chặn bởi content-safety gate -- CẦN NGƯỜI DUYỆT thủ công trước khi tiếp tục, KHÔNG tự động SEO/upload. Lý do: {block_reason}", flush=True)
            return entry

        entry["status"] = "video_ready"
        entry["video_path"] = str(video_path)
        registry[key] = entry
        save_registry(registry, topic)

    # 4. SEO
    if entry.get("status") == "video_ready":
        # G5 Codex review round 1 finding #2: re-check content-safety on
        # EVERY pass through this branch, not just the run that first
        # rendered the video -- an entry RESUMED straight into
        # status="video_ready" (registry from a prior run) must not skip
        # straight to SEO without this same gate re-running, see
        # _asset_safety_block_reason() docstring.
        block_reason = _asset_safety_block_reason(seg_dir, video_path)
        if block_reason is not None:
            entry["status"] = "needs_review"
            entry["needs_human_review_asset_safety"] = block_reason
            registry[key] = entry
            save_registry(registry, topic)
            print(f"[{key}] DỪNG: content-safety gate chặn TRƯỚC BƯỚC SEO (resume) -- CẦN NGƯỜI DUYỆT thủ công, KHÔNG tự động SEO/upload. Lý do: {block_reason}", flush=True)
            return entry

        if topic == CL_TOPIC:
            # KHÔNG gọi generate_short_seo_with_review() -- entry["cl_final_
            # editorial"] ĐÃ qua Phase A review (run_phase_a_final_review(),
            # lúc cl_case_batch.py ghi sidecar); regenerate ở đây sẽ tạo
            # editorial MỚI CHƯA TỪNG qua review nào. entry["seo"] giữ NGUYÊN
            # VĂN bản đã review (KHÔNG nối attribution BGM ở đây, khác các
            # topic khác) -- Phase D's current_editorial_hash phải khớp
            # reviewed_editorial_hash tính từ CHÍNH bản Phase A đã thấy; nối
            # thêm text ở bước này sẽ làm lệch hash. Attribution (chuỗi cố
            # định, không phải nội dung cần review) được nối vào description
            # thật NGAY TRƯỚC lệnh upload, bên trong _run_cl_phase_c_d_and_upload().
            print(f"[{key}] Dùng SEO đã qua Phase A review (không regenerate)...", flush=True)
            entry["seo"] = dict(entry["cl_final_editorial"])
            entry["needs_human_review_seo"] = False
            entry["status"] = "seo_ready"
            registry[key] = entry
            save_registry(registry, topic)
        else:
            print(f"[{key}] SEO...", flush=True)
            seo_result = generate_short_seo_with_review(entry["final_script"], context=f"Trích từ tập {seg['episode']}", topic=topic)
            entry["seo"] = seo_result["seo"]
            # Ghi nguồn BGM bắt buộc theo giấy phép CC BY 4.0 (xem bgm_tracks.py
            # docstring) -- nối THẲNG chuỗi cố định vào description, KHÔNG để
            # model tự viết lại (rủi ro diễn giải sai/thiếu câu ghi nguồn đúng
            # nguyên văn giấy phép yêu cầu). Đọc từ entry["bgm"] đã LƯU Ở BƯỚC 3
            # (lúc track thật sự được chọn+mix) -- KHÔNG gọi lại bgm_tracks để
            # tránh rotate lệch khỏi track thật đã mix vào video (xem cảnh báo
            # bgm_tracks.py + run_video_render()).
            bgm_info = entry.get("bgm")
            if bgm_info:
                entry["seo"]["description"] = entry["seo"]["description"].rstrip() + "\n\n" + bgm_info["attribution"]
            entry["needs_human_review_seo"] = seo_result["needs_human_review"]
            # Cùng bug/cùng cách sửa với bước 1 (review hook) -- xem ghi chú ở
            # đó: fail-closed thay vì chỉ ghi cờ rồi vẫn tiến tới upload thật.
            entry["status"] = "needs_review" if seo_result["needs_human_review"] else "seo_ready"
            registry[key] = entry
            save_registry(registry, topic)
            if seo_result["needs_human_review"]:
                print(f"[{key}] DỪNG: SEO chưa đạt ngưỡng sau review -- CẦN NGƯỜI DUYỆT thủ công trước khi upload, KHÔNG tự động đăng.", flush=True)
                return entry

    # 5. Upload
    if entry.get("status") == "seo_ready":
        # BUG THẬT phát hiện qua Codex CLI review độc lập (đợt kiểm tra thứ
        # 5, sau khi đã thêm gate fail-closed ở bước 1/4 -- Codex tự
        # adversarial-test tiếp): entry có thể đạt status="seo_ready" từ 1
        # LẦN CHẠY CŨ (trước khi có gate mới) với needs_human_review_hook/
        # needs_human_review_seo=True vẫn còn TỒN ĐỌNG trong registry --
        # nhánh upload chỉ kiểm tra STATUS, KHÔNG kiểm tra lại field cờ, nên
        # registry "tồn kho" cũ vẫn lọt qua upload thật. Không tin status
        # suông -- kiểm tra lại TRỰC TIẾP ngay trước hành động không thể
        # hoàn tác (upload thật lên YouTube), phòng thủ theo chiều sâu bất
        # kể entry đi tới đây bằng đường nào (registry cũ, resume, sửa tay).
        if entry.get("needs_human_review_hook") or entry.get("needs_human_review_seo"):
            entry["status"] = "needs_review"
            registry[key] = entry
            save_registry(registry, topic)
            print(f"[{key}] DỪNG: registry có cờ needs_human_review chưa qua duyệt (có thể từ lần chạy cũ trước gate mới) -- CẦN NGƯỜI DUYỆT, KHÔNG upload.", flush=True)
            return entry

        # G5 Codex review round 1 finding #2: same fail-closed re-check,
        # right before the truly IRREVERSIBLE step (real YouTube upload) --
        # an entry resumed straight into status="seo_ready" must not reach
        # upload without this gate re-running, see
        # _asset_safety_block_reason() docstring. Cheapest, most defensive
        # place for this specific check: even if SEO's own re-check above
        # somehow got bypassed (registry hand-edited, older code path),
        # nothing reaches the actual upload call without passing here too.
        block_reason = _asset_safety_block_reason(seg_dir, video_path)
        if block_reason is not None:
            entry["status"] = "needs_review"
            entry["needs_human_review_asset_safety"] = block_reason
            registry[key] = entry
            save_registry(registry, topic)
            print(f"[{key}] DỪNG: content-safety gate chặn TRƯỚC UPLOAD (resume) -- CẦN NGƯỜI DUYỆT thủ công, KHÔNG upload. Lý do: {block_reason}", flush=True)
            return entry

        # BUG THẬT phát hiện qua Codex CLI review (đợt kiểm tra thứ 6):
        # attribution BGM (bắt buộc theo giấy phép CC BY 4.0) chỉ được nối
        # vào description ở bước 4 (SEO) -- nếu 1 entry RESUME thẳng vào
        # status="seo_ready" (registry cũ từ trước khi có tính năng
        # attribution, hoặc tiến trình bị gián đoạn giữa chừng ở phiên bản
        # code cũ hơn) thì bước 4 bị BỎ QUA hoàn toàn (status đã vượt qua
        # "video_ready"), description có thể ĐI THẲNG lên upload mà KHÔNG
        # có ghi nguồn -- vi phạm giấy phép. Kiểm tra lại TRỰC TIẾP ngay
        # trước hành động không thể hoàn tác, cùng tinh thần với check
        # needs_human_review ở trên -- không tin state đã lưu, tự vá nếu
        # thiếu thay vì chỉ tin tưởng bước 4 đã chạy đúng.
        #
        # Logic chọn đúng track/fallback xem docstring resolve_bgm_for_attribution().
        #
        # KHÔNG áp dụng patch này cho CL (task #241): entry["seo"] cho CL
        # PHẢI giữ NGUYÊN VĂN bản Phase A đã review (Phase D's assemble_
        # upload_manifest() so current_editorial_hash == reviewed_editorial_
        # hash tính từ CHÍNH entry["seo"]) -- mutate description ở đây SẼ
        # làm lệch hash, gây FALSE positive "EDITORIAL_CHANGED_SINCE_REVIEW"
        # cho MỌI CL Short có BGM (bug thật tự bắt qua test, không phải
        # review round nào). Attribution BGM cho CL được nối vào description
        # THẬT ngay trước upload_short(), bên trong _run_cl_phase_c_d_and_
        # upload()'s _upload_fn -- KHÔNG đụng entry["seo"].
        if topic != CL_TOPIC:
            bgm_info = resolve_bgm_for_attribution(entry, topic)
            if bgm_info and bgm_info["attribution"] not in entry.get("seo", {}).get("description", ""):
                entry["seo"]["description"] = entry["seo"]["description"].rstrip() + "\n\n" + bgm_info["attribution"]
                registry[key] = entry
                save_registry(registry, topic)
                print(f"[{key}] Đã bổ sung ghi nguồn BGM còn thiếu vào description (phòng thủ trước khi upload).", flush=True)

        if dry_run:
            print(f"[{key}] [DRY RUN] Sẽ upload: {entry['seo']['title']}", flush=True)
            entry["status"] = "dry_run_done"
            registry[key] = entry
            save_registry(registry, topic)
            return entry

        # Đọc registry TƯƠI trên đĩa (không dùng biến `registry` trong bộ
        # nhớ, có thể thiếu slot mà 1 tiến trình khác CÙNG topic vừa book)
        # để chống 2 tiến trình chọn trùng slot đăng -- xem ghi chú ở
        # save_registry() về việc registry không tự đồng bộ ngược.
        fresh_registry = load_registry(topic)
        lich_slot = lich_hoang_dao_publish_slot(seg["episode"]) if topic == "Phong Thủy" else None
        if lich_slot is not None:
            publish_at, slot = lich_slot
            now = datetime.now(timezone.utc)
            candidate_dt = datetime.strptime(publish_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            used_slots = {v["publish_at"] for v in fresh_registry.values() if v.get("publish_at")}
            if candidate_dt - now <= timedelta(hours=MIN_LEAD_HOURS):
                entry["status"] = "needs_review"
                entry["needs_human_review_lich_hoang_dao"] = (
                    f"Slot cố định 6h ICT ({publish_at}) đã quá cận/quá khứ so với hiện tại -- "
                    "nội dung lịch/hoàng đạo gắn 1 ngày cụ thể, KHÔNG tự dồn sang slot round-robin "
                    "khác (sẽ sai ngày thật). Cần người xem lại (có thể do sinh trễ)."
                )
                registry[key] = entry
                save_registry(registry, topic)
                print(f"[{key}] DỪNG: {entry['needs_human_review_lich_hoang_dao']}", flush=True)
                return entry
            if publish_at in used_slots:
                entry["status"] = "needs_review"
                entry["needs_human_review_lich_hoang_dao"] = (
                    f"Slot 6h ICT ({publish_at}) đã có entry khác đăng -- có thể có 2 file Lịch Hoàng "
                    "Đạo trùng ngày mục tiêu. Cần người xem lại thay vì tự chọn slot khác."
                )
                registry[key] = entry
                save_registry(registry, topic)
                print(f"[{key}] DỪNG: {entry['needs_human_review_lich_hoang_dao']}", flush=True)
                return entry
        else:
            publish_at, slot = next_available_slot(fresh_registry, time_slots)

        if topic == CL_TOPIC:
            # CL Risk Gate Stage 3 (task #241) -- Phase C (post-render audio
            # custody + visual person-reference check) + Phase D (atomic
            # UploadManifest + exclusive staging + safe upload) NGAY TRƯỚC
            # upload thật, cùng vị trí/tinh thần fail-closed các gate khác ở
            # trên. Đây LÀ lệnh upload thật cho CL (thay _run_cl_phase_c_d_and_
            # upload() gọi upload_short() nội bộ, không gọi lại ở dưới).
            #
            # FIX (review độc lập Cursor/Grok, MEDIUM #1): sidecar-gate ở
            # bước 1 CHỈ chạy khi status in (None, "pending") -- 1 entry
            # resume/sửa tay thẳng vào status="seo_ready" với đủ field cl_*
            # "hợp lệ" (tự chế/tự khớp hash) sẽ KHÔNG bao giờ đọc lại sidecar,
            # có thể tới thẳng Phase C/D dù chưa từng thật sự qua Phase A.
            # Cùng nguyên tắc "không tin state đã lưu, re-check TRỰC TIẾP
            # ngay trước hành động không thể hoàn tác" đã dùng cho asset-
            # safety/needs_human_review/BGM attribution ở trên -- đọc LẠI
            # sidecar từ đĩa, so khớp CẢ 2 hash (editorial + script) với
            # entry trước khi cho Phase C/D chạy.
            sidecar_path = cl_metadata_sidecar_path(seg["episode"], topic)
            sidecar_recheck_error = None
            if not sidecar_path.exists():
                sidecar_recheck_error = f"Sidecar CL Risk Gate không còn tồn tại ('{sidecar_path}') ngay trước Phase C/D."
            else:
                try:
                    sidecar_now = json.loads(sidecar_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError) as exc:
                    sidecar_recheck_error = f"Sidecar CL Risk Gate lỗi đọc/parse ngay trước Phase C/D: {exc}."
                else:
                    if sidecar_now.get("reviewed_editorial_hash") != entry.get("cl_reviewed_editorial_hash"):
                        sidecar_recheck_error = "reviewed_editorial_hash trên entry KHÔNG khớp sidecar hiện tại (ngay trước Phase C/D)."
                    elif sidecar_now.get("reviewed_script_hash") != entry.get("cl_reviewed_script_hash"):
                        sidecar_recheck_error = "reviewed_script_hash trên entry KHÔNG khớp sidecar hiện tại (ngay trước Phase C/D)."
                    else:
                        # FIX (caveat LOW, review độc lập Cursor/Grok round 2):
                        # named_individuals KHÔNG có hash riêng nào ràng buộc
                        # -- 2 hash ở trên chỉ cover editorial/script, 1 entry
                        # bị sửa tay đúng field cl_named_individuals (vd xoá
                        # bớt 1 người) mà không đụng gì khác vẫn qua được nếu
                        # chỉ so hash. RE-BIND TRỰC TIẾP từ sidecar (nguồn sự
                        # thật) thay vì chỉ so sánh -- Phase C's person-
                        # reference check LUÔN chạy trên đúng roster Phase A
                        # đã duyệt, không phụ thuộc entry có bị sửa hay không.
                        entry["cl_named_individuals"] = sidecar_now.get("named_individuals", [])
            if sidecar_recheck_error:
                entry["status"] = "needs_review"
                entry["needs_human_review_cl_gate"] = f"{sidecar_recheck_error} KHÔNG upload."
                registry[key] = entry
                save_registry(registry, topic)
                print(f"[{key}] DỪNG: {entry['needs_human_review_cl_gate']}", flush=True)
                return entry

            print(f"[{key}] CL Phase C/D...", flush=True)
            cl_ok, cl_reason, cl_video_id = _run_cl_phase_c_d_and_upload(
                entry, seg_dir, wav_path, video_path, credentials_path, publish_at,
            )
            if not cl_ok:
                entry["status"] = "needs_review"
                entry["needs_human_review_cl_gate"] = cl_reason
                registry[key] = entry
                save_registry(registry, topic)
                print(f"[{key}] DỪNG: {cl_reason} -- CẦN NGƯỜI DUYỆT thủ công, KHÔNG upload.", flush=True)
                return entry
            video_id = cl_video_id
            print(f"[{key}] Upload YouTube (CL, đã qua Phase C/D), lên lịch {publish_at} ({slot['label']})...", flush=True)
        else:
            print(f"[{key}] Upload YouTube, lên lịch {publish_at} ({slot['label']})...", flush=True)
            video_id = upload_short(
                str(video_path), entry["seo"]["title"], entry["seo"]["description"],
                entry["seo"]["tags"], publish_at, credentials_path,
            )
        entry["video_id"] = video_id
        entry["publish_at"] = publish_at
        entry["slot_label"] = slot["label"]
        entry["status"] = "uploaded"
        registry[key] = entry
        save_registry(registry, topic)

        if playlist_title:
            playlist = find_playlist_by_title(credentials_path, playlist_title)
            if playlist:
                add_video_to_playlist(credentials_path, playlist["id"], video_id)

    return entry


MAX_RETRIES_PER_SEGMENT = 3  # trần cứng -- lỗi lặp lại quá số này thì đánh dấu "failed" (không tự thử lại nữa), cần người xem
# "needs_review" nằm trong TERMINAL_STATUSES cùng lý do với "failed": đây
# KHÔNG phải lỗi kỹ thuật (script/SEO đã sinh xong, chỉ là chưa đạt ngưỡng
# chất lượng sau đủ vòng judge-panel) -- tự động thử lại với CÙNG nội dung
# nguồn nhiều khả năng ra lại kết quả tương tự, không có giá trị. Cần người
# thật xem final_script/seo trong registry rồi TỰ QUYẾT: sửa tay + đổi
# status ngược về "scripted"/"seo_ready" để tiếp tục, hoặc bỏ hẳn đoạn đó.
TERMINAL_STATUSES = ("uploaded", "dry_run_done", "failed", "needs_review")


def main() -> int:
    # PHẢI là dòng đầu tiên -- đánh dấu tiến trình này là entry point CLI
    # thật, cho phép write_registry_atomic() ghi vào production thật (xem
    # registry_lock.py mục 4 / G1). KHÔNG gọi mark_production_entry() ở nơi
    # nào khác trong file này hay trong test.
    mark_production_entry()
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default=DEFAULT_TOPIC, help='Kênh/chủ đề, vd "Phong Thủy"/"Hình Sự" -- quyết định nguồn Short + registry riêng')
    ap.add_argument("--episodes", nargs="+", default=["06"], help="Tiền tố tập nguồn, vd 06 07 (mặc định né EP005 đã đăng thủ công) -- bỏ qua nếu dùng --auto-discover")
    ap.add_argument("--auto-discover", action="store_true", help="Tự dò MỌI tiền tố có sẵn trong Short/ của topic thay vì liệt kê --episodes thủ công -- cần cho topic có nhiều generator khác nhau (vd Phong Thuỷ: lịch/12 vị Thần/con giáp/màu mệnh/kiến thức nền)")
    ap.add_argument("--count", type=int, default=5, help="Số short xử lý trong lần chạy này")
    ap.add_argument("--credentials", default=None, help="Mặc định suy ra từ --topic (vd .youtube_channels/phong_thuy.json) nếu bỏ trống")
    ap.add_argument("--playlist", default=None, help="Tên playlist thêm vào sau upload (để trống nếu Short không thuộc series nào)")
    ap.add_argument("--hook-pass-threshold", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    topic = args.topic
    credentials_path = args.credentials
    if credentials_path is None:
        if topic == DEFAULT_TOPIC:
            credentials_path = str(PROJECT_ROOT / ".youtube_channels" / "phat_giao.json")
        else:
            print("LỖI: --topic khác mặc định (Phật giáo) bắt buộc phải truyền --credentials rõ ràng "
                  "-- tránh đoán nhầm kênh khi đăng thật.", file=sys.stderr)
            return 1

    registry = load_registry(topic)
    episode_prefixes = discover_all_episode_prefixes(topic) if args.auto_discover else args.episodes
    segments = discover_segments(episode_prefixes, topic)
    pending = [s for s in segments if registry.get(s["key"], {}).get("status") not in TERMINAL_STATUSES]

    print(f"[{topic}] Tổng {len(segments)} đoạn khả dụng, {len(pending)} chưa xử lý xong, xử lý {min(args.count, len(pending))} đoạn.", flush=True)

    n_done = n_failed = n_needs_review = 0
    for seg in pending[:args.count]:
        try:
            result_entry = process_one_segment(seg, PROJECT_ROOT / "output" / "shorts" / topic, credentials_path,
                                                time_slots_for_topic(topic), registry, args.playlist, args.hook_pass_threshold, args.dry_run, topic)
            if result_entry.get("status") == "needs_review":
                n_needs_review += 1
            else:
                n_done += 1
        except Exception as exc:  # noqa: BLE001 -- batch phải tiếp tục dù 1 đoạn lỗi
            # BUG ĐÃ SỬA: trước đây ghi status="error" đè lên chính field
            # dùng để biết "đã xong bước nào" -- process_one_segment() điều
            # hướng theo status ("scripted"/"audio_ready"/...), không có
            # nhánh nào khớp "error" nên đoạn lỗi bị TREO VĨNH VIỄN: vẫn lọt
            # vào `pending` mỗi lần chạy (khác "uploaded"/"dry_run_done")
            # nhưng process_one_segment() không làm gì cả (không khớp bước
            # nào), coi như "thành công" một cách im lặng mà không tiến
            # triển -- chiếm 1 suất batch vô ích mãi mãi. Sửa: KHÔNG đụng
            # tới status (giữ nguyên bước cuối đã xong để lần sau resume
            # đúng chỗ), chỉ tăng error_count riêng; đủ MAX_RETRIES_PER_SEGMENT
            # lần lỗi mới chuyển hẳn sang "failed" (nằm trong
            # TERMINAL_STATUSES, dừng tự thử lại, cần người xem).
            print(f"[{seg['key']}] LỖI: {exc}", file=sys.stderr, flush=True)
            entry = registry.setdefault(seg["key"], {"key": seg["key"], "episode": seg["episode"], "segment_index": seg["segment_index"]})
            entry["last_error"] = str(exc)
            entry["error_count"] = entry.get("error_count", 0) + 1
            if entry["error_count"] >= MAX_RETRIES_PER_SEGMENT:
                entry["status"] = "failed"
                print(f"[{seg['key']}] Lỗi {entry['error_count']} lần liên tiếp -- đánh dấu failed, dừng tự thử lại, cần người xem.", file=sys.stderr, flush=True)
            save_registry(registry, topic)
            n_failed += 1

    print(f"\nHoàn tất: {n_done} đoạn xong, {n_failed} lỗi, {n_needs_review} đoạn CẦN NGƯỜI DUYỆT (xem registry status=needs_review, không tự upload).", flush=True)
    return 1 if (n_failed > 0 or n_needs_review > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
