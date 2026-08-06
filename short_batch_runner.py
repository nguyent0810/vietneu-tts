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
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import certifi  # noqa: E402
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from short_content_review import review_and_optimize_short  # noqa: E402
from short_seo import generate_short_seo_with_review  # noqa: E402
from short_upload import upload_short  # noqa: E402
from youtube_catalog import find_playlist_by_title, add_video_to_playlist  # noqa: E402
import bgm_tracks  # noqa: E402
from registry_lock import FileLock  # noqa: E402
# discover_segments()/discover_all_episode_prefixes() giờ sống ở
# short_segment_discovery.py (module thuần đọc file, không phụ thuộc gì
# ở đây) -- tách ra để short_health_check.py chỉ cần đúng phần đọc file
# này mà không phải kéo theo toàn bộ runner (xem docstring module đó).
from short_segment_discovery import discover_all_episode_prefixes, discover_segments  # noqa: E402, F401

VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
VIDEO_TOOL_VENV_PYTHON = PROJECT_ROOT / "video_tool_clone" / ".venv-video" / "bin" / "python"
RENDER_SHORT_SCRIPT = PROJECT_ROOT / "render_short.py"
TTS_HELPER_SCRIPT = PROJECT_ROOT / "_short_tts_render.py"

DEFAULT_TOPIC = "Phật giáo"  # giữ mặc định này để không phá cron/launchd đã lên lịch (--topic chưa truyền)


def _registry_path(topic: str) -> Path:
    # THAM SỐ HOÁ THEO TOPIC -- mỗi kênh registry riêng, tránh đè lẫn nhau
    # khi chạy đa kênh (Phật giáo/Phong Thuỷ/Hình Sự dùng chung code này).
    return PROJECT_ROOT / "output" / "shorts" / topic / "registry.json"


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
# dụng chéo sang kênh khác). 12h/15h/18h/21h ICT = 05:00/08:00/11:00/14:00
# UTC -- đúng 4 khung "không phải giờ hoàng đạo" người dùng đã chốt dùng
# thật trong phiên (6h ICT/23:00 UTC dành riêng cho nội dung lịch/hoàng
# đạo do hệ thống CŨ phụ trách, xem lich_hoang_dao_generator.py docstring
# -- KHÔNG nằm trong danh sách này để tránh trùng nội dung).
PHONG_THUY_TIME_SLOTS = [
    {"utc_time": "05:00", "is_proven": False, "label": "12h ICT -- nội dung đa dạng phi-hoàng-đạo"},
    {"utc_time": "08:00", "is_proven": False, "label": "15h ICT -- nội dung đa dạng phi-hoàng-đạo"},
    {"utc_time": "11:00", "is_proven": False, "label": "18h ICT -- nội dung đa dạng phi-hoàng-đạo"},
    {"utc_time": "14:00", "is_proven": False, "label": "21h ICT -- nội dung đa dạng phi-hoàng-đạo"},
]

TIME_SLOTS_BY_TOPIC = {"Phong Thủy": PHONG_THUY_TIME_SLOTS}


def time_slots_for_topic(topic: str) -> list[dict]:
    return TIME_SLOTS_BY_TOPIC.get(topic, DEFAULT_TIME_SLOTS)

MIN_LEAD_HOURS = 2  # đệm an toàn hơn hẳn mức tối thiểu 15 phút của YouTube


def load_registry(topic: str = DEFAULT_TOPIC) -> dict:
    path = _registry_path(topic)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


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
        on_disk = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        merged = {**on_disk, **registry}
        path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")


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
        on_disk = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        on_disk[key] = entry
        path.write_text(json.dumps(on_disk, ensure_ascii=False, indent=2), encoding="utf-8")


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


def run_video_render(audio_wav: Path, segments_json: Path, output_mp4: Path, topic: str = DEFAULT_TOPIC,
                      bgm_path: str | None = None) -> dict:
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
    cmd = [str(VIDEO_TOOL_VENV_PYTHON), str(RENDER_SHORT_SCRIPT),
           "--audio", str(audio_wav), "--segments-json", str(segments_json), "--output", str(output_mp4),
           "--topic", topic]
    if bgm_path:
        cmd += ["--bgm", bgm_path]
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
        if topic != DEFAULT_TOPIC:
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
            bgm_choice = entry["bgm"]
        else:
            picked = bgm_tracks.pick_bgm_for_topic(topic)
            bgm_choice = {"path": str(picked["path"]), "attribution": picked["attribution"]} if picked else None
            entry["bgm"] = bgm_choice
            registry[key] = entry
            # save_registry_entry() (chỉ đụng đúng key này trên bản mới
            # nhất), KHÔNG dùng save_registry() (merge cả snapshot batch)
            # cho lần lưu TRUNG GIAN này -- xem docstring save_registry_entry.
            save_registry_entry(key, entry, topic)

        print(f"[{key}] Render video...", flush=True)
        run_video_render(wav_path, json_path, video_path, topic=topic,
                          bgm_path=bgm_choice["path"] if bgm_choice else None)
        entry["status"] = "video_ready"
        entry["video_path"] = str(video_path)
        registry[key] = entry
        save_registry(registry, topic)

    # 4. SEO
    if entry.get("status") == "video_ready":
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
        publish_at, slot = next_available_slot(load_registry(topic), time_slots)
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
