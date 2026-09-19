"""Batch Runner cho Long -- nối toàn bộ chuỗi phát hiện tập sẵn sàng ->
audio -> Director Bible/shot list -> sinh asset -> render video -> BGM ->
finalize -> SEO -> upload YouTube thành 1 lệnh, giống short_batch_runner.py
nhưng cho tập dài.

THAM SỐ HOÁ THEO DOMAIN/KÊNH NGAY TỪ ĐẦU (đã bàn trong phiên làm việc):
--domain/--topic/--credentials/--playlist đều là tham số, không hard-code
"Phật giáo" -- khi Phong Thuỷ/Hình Sự có nội dung thật, chỉ cần đổi tham số,
không cần sửa code này.
creative_director.py/director_bible.py giờ đọc domain_creative_profiles.json
(qua --domain truyền xuống) thay vì hardcode "Phật giáo/tâm linh" -- gồm cả
tỷ lệ treatment (video/image/typography) và symbol_library (ký hiệu cố định
như Bát Quái cần asset chính xác dựng sẵn, không phó mặc AI). BUD giữ đúng
tỷ lệ 60/20/20 đã kiểm chứng qua EP005/006/007.

State registry (output/long/registry.json) resumable theo từng episode,
cùng thiết kế MAX_RETRIES_PER_SEGMENT + TERMINAL_STATUSES đã kiểm chứng ở
short_batch_runner.py.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import certifi  # noqa: E402
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from content_repo import (  # noqa: E402
    discover_episodes, gate_episode, load_domain_topics, load_github_credentials, ensure_content_repo,
)
from youtube_upload import VideoMetadata, upload_video  # noqa: E402
from youtube_catalog import ensure_playlist_and_add  # noqa: E402
import domain_creative_profiles as creative_profiles  # noqa: E402
from duplicate_check import channel_upload_lock, check_for_possible_duplicate  # noqa: E402
from registry_lock import (  # noqa: E402
    FileLock,
    mark_production_entry,
    read_registry_safe,
    write_registry_atomic,
)

VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
VIDEO_TOOL_VENV_PYTHON = PROJECT_ROOT / "video_tool_clone" / ".venv-video" / "bin" / "python"
VENDORED_FFMPEG = PROJECT_ROOT / "video_tool_clone" / "vendor" / "ffmpeg-macos-libass" / "ffmpeg"
VENDORED_FFPROBE = PROJECT_ROOT / "video_tool_clone" / "vendor" / "ffmpeg-macos-libass" / "ffprobe"
AUDIO_RENDER_SCRIPT = PROJECT_ROOT / "video_tool_clone" / "scripts" / "audio_tool_render.py"

# BUG THẬT phát hiện khi lên kế hoạch sản xuất Phong Thuỷ: registry.json
# CŨ dùng 1 file DUY NHẤT cho MỌI domain, khoá theo episode_id trần
# ("EP001") -- Phong Thuỷ và Phật giáo ĐỀU có tập "EP001" (trùng tên do
# Content-Creator đánh số lại từ đầu cho mỗi domain). Chạy --domain FS sẽ
# đọc NHẦM entry EP001 của Phật giáo (đã status=uploaded) và coi Phong Thuỷ
# EP001 là "đã xong", bỏ qua hoàn toàn -- hoặc tệ hơn, ghi đè thư mục làm
# việc output/long/EP001/ của Phật giáo. Scope theo topic (cùng cách
# short_batch_runner.py đã làm cho registry Short) -- mỗi topic 1 file/
# 1 thư mục riêng, không thể đụng nhau dù trùng episode_id.
def _output_dir(topic: str) -> Path:
    return PROJECT_ROOT / "output" / "long" / topic


def _registry_path(topic: str) -> Path:
    return _output_dir(topic) / "registry.json"


# Cây production thật cho registry Long -- xem _REGISTRY_PRODUCTION_ROOT
# tương ứng trong short_batch_runner.py (cùng cơ chế G1, registry_lock.py
# mục 4). 1 hằng số cho mọi topic (Phật giáo/Phong Thuỷ/Hình Sự...).
_REGISTRY_PRODUCTION_ROOT = PROJECT_ROOT / "output" / "long"


MAX_RETRIES_PER_EPISODE = 3
# "possible_duplicate_detected" nằm trong TERMINAL_STATUSES cùng lý do với
# "needs_review" ở short_batch_runner.py: đây KHÔNG phải lỗi kỹ thuật (mọi
# bước render/SEO đã xong, video đã sẵn sàng upload) -- tự động thử lại chỉ
# render+kiểm tra lại CHÍNH episode đó, gần như chắc chắn ra lại đúng kết
# quả nghi trùng y hệt (cùng audio nguồn, cùng video đã có sẵn trên kênh),
# không có giá trị. Cần người thật xem duplicate_check trong registry rồi
# TỰ QUYẾT: xác nhận là tập MỚI thật (không phải trùng) và đổi status
# ngược về "seo_ready" để pipeline tự upload lại, HOẶC xác nhận đúng là
# trùng và dùng record_existing_upload.py để backfill video_id đã có sẵn
# thay vì upload lần nữa (xem BUG THẬT + thiết kế đầy đủ ở duplicate_check.py).
TERMINAL_STATUSES = ("uploaded", "dry_run_done", "failed", "possible_duplicate_detected")

_FALLBACK_TREATMENT_RATIO = {"video": 0.6, "image": 0.2, "typography": 0.2}  # đã kiểm chứng thật trên EP005/006/007 (BUD)


def treatment_ratio_for_domain(domain: str) -> dict:
    profile = creative_profiles.load_profile(domain)
    return profile.get("treatment_ratio") or _FALLBACK_TREATMENT_RATIO


def load_registry(topic: str) -> dict:
    path = _registry_path(topic)
    return read_registry_safe(path)


def save_registry(registry: dict, topic: str) -> None:
    """Ghi registry -- MERGE với bản mới nhất trên đĩa dưới khoá ngắn hạn
    (xem registry_lock.py) thay vì ghi đè trắng bằng bản trong bộ nhớ, vốn
    có thể cũ hơn nếu 1 tiến trình KHÁC (cùng topic) xử lý 1 episode khác đã
    save trong lúc episode này đang xử lý (registry được giữ trong bộ nhớ
    suốt cả episode, có thể mất nhiều phút/giờ -- xem audit tự động hoá đa
    kênh, mục C).

    QUAN TRỌNG: `registry` (dict truyền vào) KHÔNG được đồng bộ ngược lại
    bằng bản đã merge -- cùng lý do với short_batch_runner.py's save_registry()
    (xem docstring ở đó): nếu làm vậy, key của tiến trình khác sẽ "dính" vào
    bộ nhớ cục bộ rồi bị ghi đè lại giá trị cũ ở lần save sau, xoá mất cập
    nhật của tiến trình kia -- lỗi này đã tự phát hiện qua test thật trước
    khi áp dụng bản này."""
    path = _registry_path(topic)
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(path):
        on_disk = read_registry_safe(path)
        merged = {**on_disk, **registry}
        write_registry_atomic(path, merged, production_root=_REGISTRY_PRODUCTION_ROOT)


def discover_ready_episodes(domain_id: str, topic: str) -> list[dict]:
    """Dùng LẠI đúng gate_episode() của content_repo.py -- không tự chế
    logic kiểm tra riêng, tránh lệch chuẩn với những gì process_topics.py
    đã dùng để quyết định 1 tập có sẵn sàng hay không."""
    token, repo_url = load_github_credentials()
    repo_root = ensure_content_repo(token, repo_url)
    ready = []
    for ep in discover_episodes(repo_root):
        result = gate_episode(ep)
        # BUG THẬT (Cursor review, audit kênh Hình Sự Part 1, 2026-08-14):
        # result.problems (bao gồm cảnh báo advisory "thiếu trích dẫn hook
        # bank CL", xem content_repo.py) trước đây bị BỎ HẲN ở đây -- đường
        # discover THẬT dùng cho pipeline Long-form (khác stage_ready_episodes()
        # của content_repo.py, nơi problems có được in) khiến mọi cảnh báo
        # advisory không bao giờ tới console thật khi vận hành. In ra (không
        # chặn -- vẫn advisory đúng tinh thần ban đầu) trước khi quyết
        # ready/not ready.
        for p in result.problems:
            print(f"[discover] {ep.episode_dir.name}: {p}", flush=True)
        if result.domain_id != domain_id or not result.long_ready:
            continue
        manifest_path = ep.long_manifest
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ready.append({
            "episode_id": _episode_num(ep.episode_dir.name),
            "episode_dir_name": ep.episode_dir.name,
            "title": manifest.get("title", ep.episode_dir.name),
            "long_txt": ep.long_txt,
            "internal_dir": manifest_path.parent,
        })
    return ready


_EPISODE_NUMBER_BRANDING_RE = re.compile(r"\btập\s*\d+\b", re.IGNORECASE)


def _pick_title(titles: list[str]) -> str:
    """content_seo.py trả về 5 LỰA CHỌN ("titles", số nhiều) chứ không có
    sẵn 1 "title" -- BUG THẬT phát hiện khi chạy EP001: long_batch_runner.py
    ban đầu đọc thẳng entry["seo"]["title"] (không tồn tại) gây KeyError
    'title', crash đúng bước upload cuối cùng sau khi đã tốn hết asset+video+
    BGM+finalize. Trước đây (EP005/006/007) việc chọn 1 trong 5 làm THỦ CÔNG
    ngay trong phiên chat, ưu tiên tiêu đề KHÔNG đánh số tập (đã xác nhận qua
    dữ liệu YouTube Analytics thật: tiêu đề có "Tập N" hiệu suất kém hơn hẳn
    tiêu đề rời số, xem nghiên cứu EP007 trong lịch sử phiên). Tự động hoá
    lại đúng quy tắc đó thay vì đoán ngẫu nhiên."""
    if not titles:
        raise ValueError("content_seo.py trả về danh sách titles rỗng.")
    for t in titles:
        if not _EPISODE_NUMBER_BRANDING_RE.search(t):
            return t
    return titles[0]  # mọi lựa chọn đều đánh số tập -- đành lấy bản đầu, còn hơn crash


def _episode_num(episode_dir_name: str) -> str:
    m = re.search(r"EP0*(\d+)", episode_dir_name, re.IGNORECASE)
    return f"EP{int(m.group(1)):03d}" if m else episode_dir_name


def run_audio_stage(topic: str) -> None:
    """1 lệnh phủ MỌI tập sẵn sàng của topic (idempotent -- tự skip tập đã
    render, đã kiểm chứng ở task #18 trong phiên này)."""
    result = subprocess.run(
        [str(VENV_PYTHON), "process_topics.py", "--content-repo", "--long", "--topic", topic],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=3600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"process_topics.py lỗi: {result.stderr[-1000:] or result.stdout[-1000:]}")


def find_audio_output(topic: str, episode_dir_name: str, source_long_txt: Path | None = None) -> tuple[Path, Path]:
    """BUG THẬT phát hiện khi render thật FS/CL lần đầu (audit tự động hoá
    đa kênh, mục D): đoán tên file output bằng glob `{:02d}_*.wav` theo số
    episode chỉ đúng cho nguồn Drive CŨ (file đặt tên theo tiêu đề đã đánh
    số thủ công, vd "01_Địa Tạng Vương là ai.wav"). Với episode nguồn
    Content-Creator qua nhánh manifest phẳng (`content_repo.py:143-155`),
    `process_drive_queue.py`'s `process_long_folder()` đặt tên output =
    STEM CỦA FILE .txt NGUỒN (vd "03_AUDIO_SCRIPT_TTS.wav", "03" là số thứ
    tự STAGE trong Content-Creator, KHÔNG phải số episode) -- glob theo số
    episode không khớp, luôn báo "không tìm thấy" dù audio đã render xong
    thật (đã tự xác nhận: file tồn tại cả local lẫn trên Drive). Sửa: nếu
    biết đường dẫn file .txt nguồn thật (`source_long_txt`, từ
    `discover_ready_episodes()`'s `ep["long_txt"]`), suy thẳng tên output từ
    STEM của nó -- khớp chính xác quy ước đặt tên thật, không đoán. Giữ lại
    glob theo số episode làm fallback cho nguồn Drive cũ (không có
    source_long_txt) để không đổi hành vi cho luồng đã chạy thật trước đó."""
    long_dir = PROJECT_ROOT / "output" / "topics" / topic / "Long"
    if source_long_txt is not None:
        wav = long_dir / f"{Path(source_long_txt).stem}.wav"
        if wav.exists():
            return wav, wav.with_suffix(".json")
    num = re.search(r"\d+", episode_dir_name).group(0).lstrip("0") or "0"
    matches = list(long_dir.glob(f"{int(num):02d}_*.wav"))
    if not matches:
        raise RuntimeError(f"Không tìm thấy audio đã render cho {episode_dir_name} trong {long_dir}")
    wav = matches[0]
    return wav, wav.with_suffix(".json")


def run_step(cmd: list[str], cwd: Path = PROJECT_ROOT, timeout: int = 1800) -> str:
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"Lệnh lỗi ({' '.join(cmd[:2])}...): {result.stderr[-1200:] or result.stdout[-1200:]}")
    return result.stdout


def _is_valid_image_file(path: Path) -> bool:
    """Xác nhận `path` THẬT SỰ là file ảnh mở được -- Codex review điểm #6:
    beat treatment="diagram" có annotation có thể bị asset_generation.py
    THAY asset_path bằng đường dẫn CLIP MP4 đã render (xem
    render_annotated_diagram_clip()) -- chỉ kiểm .exists() không đủ, dễ
    trả nhầm video cho PIL (crash lúc tạo thumbnail). Dùng Image.open()
    .verify() thay vì suy đoán qua đuôi file."""
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def _pick_thumbnail_background(shot_list_path: str) -> Path | None:
    """Chọn 1 ảnh nền cho thumbnail từ chính asset ĐÃ RENDER của tập (audit
    9 điểm mục #6) -- ưu tiên beat treatment="image" đầu tiên có asset_path
    THẬT SỰ là file ảnh hợp lệ (không sinh ảnh mới qua ComfyUI -- giữ nhất
    quán với hình ảnh đã dùng trong chính video, không thêm phụ thuộc
    server ComfyUI phải chạy sẵn). Rơi về treatment="diagram" nếu không có
    beat image thuần nào -- LƯU Ý: diagram có thể đã bị thay asset_path
    bằng clip MP4 (xem _is_valid_image_file), sẽ tự bỏ qua case đó, không
    trả video cho PIL. None nếu tập không có beat ảnh hợp lệ nào cả (vd
    toàn video/typography, hoặc mọi diagram đều đã thành clip), caller tự
    quyết định fallback (không tạo thumbnail)."""
    data = json.loads(Path(shot_list_path).read_text(encoding="utf-8"))
    beats = data.get("beats", [])
    for preferred_treatment in ("image", "diagram"):
        for beat in beats:
            if beat.get("treatment") != preferred_treatment:
                continue
            asset_path = beat.get("asset_path")
            if asset_path and Path(asset_path).exists() and _is_valid_image_file(Path(asset_path)):
                return Path(asset_path)
    return None


def process_one_episode(ep: dict, topic: str, credentials_path: str, playlist_title: str | None,
                         publish_at: str, dry_run: bool, domain: str = "BUD") -> dict:
    key = ep["episode_id"]
    registry = load_registry(topic)
    entry = registry.get(key, {"key": key, "episode_dir_name": ep["episode_dir_name"], "title": ep["title"]})
    known_status = entry.get("status")

    # Chống 2 tiến trình CÙNG topic chạy đồng thời cùng chọn trùng 1 episode
    # -- đọc lại registry LẦN NỮA (độc lập với bản đã load ở trên) ngay
    # trước khi bắt đầu bước đầu tiên. So sánh status TƯƠI với status đã
    # biết ở lần đọc trên: KHÁC nghĩa là tiến trình khác vừa động vào
    # episode này (kể cả đang resume 1 episode dở dang, vd "audio_ready" từ
    # lần chạy trước) -- bỏ qua thay vì làm trùng; GIỐNG thì xử lý bình
    # thường dù đang ở bước nào. Không xoá được hoàn toàn cửa sổ race (vẫn
    # còn khoảng ngắn giữa lần đọc thứ 2 này và lần ghi status đầu tiên),
    # chỉ thu hẹp đáng kể -- cùng tinh thần với short_batch_runner.py (audit
    # tự động hoá đa kênh, mục C).
    recheck_entry = load_registry(topic).get(key)
    recheck_status = recheck_entry.get("status") if recheck_entry else None
    if recheck_status != known_status:
        print(f"[{key}] Bỏ qua -- tiến trình khác (cùng topic) đã đổi trạng thái episode này kể từ lần đọc trước ({known_status!r} -> {recheck_status!r}).", flush=True)
        if recheck_entry:
            registry[key] = recheck_entry
        return recheck_entry or entry

    ep_dir = _output_dir(topic) / key
    ep_dir.mkdir(parents=True, exist_ok=True)
    internal = ep["internal_dir"]

    if entry.get("status") in (None, "pending"):
        wav_path, json_path = find_audio_output(topic, ep["episode_dir_name"], ep.get("long_txt"))
        entry["wav_path"], entry["json_path"] = str(wav_path), str(json_path)
        entry["status"] = "audio_ready"
        registry[key] = entry
        save_registry(registry, topic)

    shot_list_path = ep_dir / "shot_list_final.json"
    if entry.get("status") == "audio_ready":
        print(f"[{key}] Director Bible + shot list...", flush=True)
        ratio = treatment_ratio_for_domain(domain)
        run_step([
            str(VENV_PYTHON), "creative_director.py",
            "--segments-json", entry["json_path"], "--output", str(shot_list_path),
            "--episode-planner", str(internal / "02_EPISODE_PLANNER.md"),
            "--script-master", str(internal / "03_AUDIO_SCRIPT_MASTER.md"),
            "--research-brief", str(internal / "01_RESEARCH_BRIEF.md"),
            "--episode-id", key,
            "--domain", domain,
            "--video-ratio", str(ratio["video"]),
            "--image-ratio", str(ratio["image"]),
            "--typography-ratio", str(ratio["typography"]),
        ], timeout=1800)
        entry["shot_list_path"] = str(shot_list_path)
        entry["status"] = "bible_ready"
        registry[key] = entry
        save_registry(registry, topic)

    if entry.get("status") == "bible_ready":
        print(f"[{key}] Sinh asset (ảnh/video/typography)...", flush=True)
        run_step([str(VENV_PYTHON), "asset_generation.py", "--shot-list", entry["shot_list_path"]], timeout=7200)
        entry["status"] = "assets_ready"
        registry[key] = entry
        save_registry(registry, topic)

    video_raw_path = ep_dir / "render_raw.mp4"
    if entry.get("status") == "assets_ready":
        # P4b (E2E validation remediation, real incident, FS channel):
        # symbol_asset_path is resolved ONCE and baked into shot_list_final.json
        # at shot-list-creation time -- if the symbol_library naming
        # convention has changed since (confirmed real for FS: flat
        # filename -> 3-color rotation), a stale baked-in path would crash
        # deep inside ffmpeg on the render step below with a generic "No
        # such file or directory". Heal BEFORE every render attempt (fresh
        # or resumed) -- cheap no-op when nothing is stale (checks
        # Path.is_file() per symbol beat, only re-resolves+rewrites when
        # actually needed).
        healed = creative_profiles.heal_stale_symbol_asset_paths(entry["shot_list_path"], domain)
        if healed:
            print(f"[{key}] Đã hồi phục {healed} đường dẫn symbol_library asset bị lỗi thời.", flush=True)
        print(f"[{key}] Render video...", flush=True)
        # P3 (E2E validation remediation, real incident): a real ~27-minute
        # episode's combined render+compose+subtitle-burn-in step (this ONE
        # subprocess call) hit the old 7200s cap under real-world
        # conditions (confounded by, but not solely explained by, 3-way
        # concurrent machine load during that specific validation run).
        # audio_tool_render.py itself was separately fixed to make a RETRY
        # of this step cheap (reuses its render+compose checkpoint instead
        # of redoing it from scratch) -- this timeout bump is a secondary,
        # modest mitigation (+50%) for the FIRST attempt specifically
        # (which has no checkpoint to reuse yet), not a substitute for that
        # fix. Not raised without limit -- a real per-episode timeout still
        # exists and still protects against a genuinely stuck run.
        run_step([
            str(VIDEO_TOOL_VENV_PYTHON), str(AUDIO_RENDER_SCRIPT),
            "--audio", entry["wav_path"], "--segments-json", entry["json_path"],
            "--shot-list", entry["shot_list_path"], "--policy", "content_sync",
            "--output", str(video_raw_path),
        ], timeout=10800)
        entry["video_raw_path"] = str(video_raw_path)
        entry["ass_path"] = str(video_raw_path.with_suffix(".ass"))
        entry["status"] = "video_ready"
        registry[key] = entry
        save_registry(registry, topic)

    video_bgm_path = ep_dir / "with_bgm.mp4"
    if entry.get("status") == "video_ready":
        print(f"[{key}] Trộn BGM...", flush=True)
        run_step([
            str(VENV_PYTHON), "mix_bgm.py", "--video", entry["video_raw_path"], "--output", str(video_bgm_path),
            "--ffmpeg", str(VENDORED_FFMPEG), "--ffprobe", str(VENDORED_FFPROBE),
        ], timeout=1200)
        entry["video_bgm_path"] = str(video_bgm_path)
        entry["status"] = "bgm_ready"
        registry[key] = entry
        save_registry(registry, topic)

    if entry.get("status") == "bgm_ready":
        print(f"[{key}] Finalize (đổi tên + upload Drive + dọn cache)...", flush=True)
        out = run_step([
            str(VENV_PYTHON), "finalize_episode.py", "--video", entry["video_bgm_path"], "--ass", entry["ass_path"],
            "--episode-id", key, "--title", ep["title"], "--topic", topic,
        ], timeout=1800)
        entry["status"] = "finalized"
        registry[key] = entry
        save_registry(registry, topic)

    seo_path = ep_dir / "seo.json"
    if entry.get("status") == "finalized":
        print(f"[{key}] SEO...", flush=True)
        run_step([
            str(VENV_PYTHON), "content_seo.py",
            "--research-brief", str(internal / "01_RESEARCH_BRIEF.md"),
            "--script-master", str(internal / "03_AUDIO_SCRIPT_MASTER.md"),
            "--output", str(seo_path),
            "--domain", domain,
        ], timeout=1800)
        seo = json.loads(seo_path.read_text(encoding="utf-8"))["seo"]
        seo["title"] = _pick_title(seo["titles"])
        entry["seo"] = seo
        entry["status"] = "seo_ready"
        registry[key] = entry
        save_registry(registry, topic)

    if entry.get("status") == "seo_ready":
        # BUG THẬT (2026-08-13, phát hiện khi resume EP004 sau khi đã render
        # từ lâu -- gián đoạn trước khi tới bước upload): fallback CŨ (glob
        # "output/video_test" rồi tới entry["video_bgm_path"]) không tính
        # trường hợp finalize_episode.py's build_canonical_name() ĐÃ đổi tên
        # file thành bản canonical (vd "EP004 - <tiêu đề>.mp4" trong CHÍNH
        # ep_dir) TỪ TRƯỚC, khiến cả 2 fallback đều trỏ vào file không còn
        # tồn tại -- "Không tìm thấy file để đo thời lượng" dù video đã render
        # xong thật. Kiểm tra bản canonical trong ep_dir TRƯỚC TIÊN (đúng vị
        # trí/tên finalize_episode.py thật sự dùng), 2 fallback cũ giữ nguyên
        # cho episode chưa qua finalize rename.
        from finalize_episode import build_canonical_name
        canonical_video = ep_dir / build_canonical_name(key, entry.get("title", ep["title"]), ".mp4")
        finalized_video = canonical_video if canonical_video.exists() else (
            next((PROJECT_ROOT / "output" / "video_test").glob(f"{key} - *.mp4"), None)
            or Path(entry["video_bgm_path"])
        )
        if dry_run:
            print(f"[{key}] [DRY RUN] Sẽ upload: {entry['seo']['title']}", flush=True)
            entry["status"] = "dry_run_done"
            registry[key] = entry
            save_registry(registry, topic)
            return entry

        # BUG THẬT (2026-08-11, xem duplicate_check.py docstring đầy đủ):
        # kênh BUD có 3 tập bị đăng TRÙNG thật (EP005 x3, EP006 x2, EP007
        # x2) vì registry.json KHÔNG BAO GIỜ là nguồn sự thật đầy đủ về
        # "đã đăng lên YouTube chưa" -- 1 số bản render đã được upload THỦ
        # CÔNG ngoài luồng registry (giai đoạn test pipeline). Đối chiếu
        # THẬT với kênh YouTube (duration + audio nguồn cục bộ, 2 tín hiệu
        # độc lập -- xem docstring module) NGAY TRƯỚC khi gọi upload_video()
        # -- KHÔNG tin registry cục bộ 1 mình nữa. FAIL CLOSED: nếu tìm
        # thấy khả năng trùng, KHÔNG upload, đánh dấu registry rồi dừng --
        # cần người thật xác nhận (xem TERMINAL_STATUSES ở trên +
        # record_existing_upload.py).
        #
        # channel_upload_lock() (Codex CLI adversarial review round 1,
        # finding HIGH -- race condition thật): giữ khoá liên-tiến-trình
        # theo kênh XUYÊN SUỐT từ lúc kiểm tra trùng tới khi đã lưu
        # video_id/status="uploaded" vào registry -- không có khoá này, 2
        # tiến trình (vd 1 lần launchd theo lịch + 1 lần chạy tay chồng
        # lấn) đều có thể đọc catalog kênh gần như đồng thời, CẢ HAI đều
        # thấy "chưa có bản nào khớp" (video của tiến trình kia CHƯA xuất
        # hiện trên kênh lúc đó), cả hai đều upload -- tạo bản TRÙNG THẬT
        # giống hệt sự cố gốc dù mỗi tiến trình RIÊNG LẺ đã kiểm tra đúng.
        # Xem docstring channel_upload_lock() cho giới hạn thật của khoá này.
        with channel_upload_lock(credentials_path):
            # Codex CLI adversarial review round 2, finding HIGH còn sót lại
            # sau khi thêm channel_upload_lock() ở trên: khoá kênh tuần tự
            # hoá đúng bước upload, NHƯNG tiến trình B (đang CHỜ khoá) vẫn
            # cầm `entry` CŨ (đọc từ RẤT LÂU trước, ở đầu process_one_episode())
            # -- nếu B chờ xong, vào được khoá NGAY SAU KHI A vừa upload +
            # lưu registry xong, B vẫn dùng entry cũ (status="seo_ready")
            # thay vì entry MỚI (status="uploaded") mà chính A vừa ghi
            # trong lúc B đang chờ CHÍNH khoá này. Tệ hơn: catalog YouTube
            # có thể CHƯA kịp phản ánh video A vừa upload (read-after-write
            # lag thật, đã xác nhận ở nơi khác trong codebase -- xem
            # youtube_catalog.py's _list_playlist_video_ids_tolerant()) nên
            # duplicate_check của B dựa vào catalog cũng không chắc bắt
            # được. Đọc lại registry NGAY sau khi giành được khoá (không
            # phụ thuộc YouTube API, chỉ phụ thuộc chính registry mà A vừa
            # ghi DƯỚI CÙNG khoá này -- đảm bảo B thấy được) -- nếu status
            # đã là terminal (điển hình "uploaded", do A vừa xong trong lúc
            # B chờ), dừng ngay, KHÔNG upload lần 2.
            fresh_entry = load_registry(topic).get(key)
            fresh_status = fresh_entry.get("status") if fresh_entry else None
            if fresh_status in TERMINAL_STATUSES:
                print(
                    f"[{key}] Bỏ qua upload -- tiến trình khác (cùng kênh) đã xử lý xong episode này "
                    f"trong lúc chờ khoá kênh (status hiện tại: {fresh_status!r}).",
                    flush=True,
                )
                registry[key] = fresh_entry
                return fresh_entry

            print(f"[{key}] Kiểm tra trùng lặp với kênh YouTube thật trước khi upload...", flush=True)
            possible_dup = check_for_possible_duplicate(
                video_path=finalized_video,
                credentials_path=credentials_path,
                ffprobe_path=str(VENDORED_FFPROBE),
                audio_path=entry.get("wav_path"),
            )
            # Override CÓ NGƯỜI xác nhận (2026-08-13, EP004 -- trùng thời
            # lượng NGẪU NHIÊN với 1 video chủ đề khác hẳn, đăng trước cả
            # series này bắt đầu): chỉ bỏ qua block nếu suspected_video_id
            # KHỚP ĐÚNG cái đã được người xác nhận, KHÔNG bỏ qua toàn bộ
            # check cho episode này mãi mãi -- nếu 1 nghi vấn trùng THẬT SỰ
            # KHÁC (video_id khác) xuất hiện sau này, vẫn phải chặn lại bình
            # thường, không để override cũ vô tình che luôn sự cố mới.
            override = entry.get("duplicate_check_override")
            if possible_dup is not None and override and override.get("confirmed_not_duplicate_for_video_id") == possible_dup.suspected_video_id:
                print(
                    f"[{key}] Bỏ qua cảnh báo trùng lặp (video_id={possible_dup.suspected_video_id}) -- "
                    f"đã có người xác nhận KHÔNG phải trùng: {override.get('reason', '')[:200]}",
                    flush=True,
                )
                possible_dup = None
            if possible_dup is not None:
                entry["status"] = "possible_duplicate_detected"
                entry["possible_duplicate"] = possible_dup.to_dict()
                registry[key] = entry
                save_registry(registry, topic)
                print(
                    f"[{key}] DỪNG -- nghi ngờ video này ĐÃ có sẵn trên kênh: "
                    f"video_id={possible_dup.suspected_video_id} title={possible_dup.suspected_title!r} "
                    f"duration_diff={possible_dup.duration_diff_seconds:.1f}s "
                    f"(secondary_signal_matched={possible_dup.secondary_signal_matched}). "
                    f"KHÔNG upload. Cần người xem registry entry '{key}' rồi tự quyết: "
                    f"đổi status về 'seo_ready' nếu xác nhận đây LÀ tập mới thật, hoặc dùng "
                    f"record_existing_upload.py để backfill video_id đã có sẵn nếu đúng là trùng.",
                    file=sys.stderr, flush=True,
                )
                return entry

            print(f"[{key}] Upload YouTube, lên lịch {publish_at}...", flush=True)
            metadata = VideoMetadata(
                title=entry["seo"]["title"], description=entry["seo"]["description"], tags=entry["seo"]["tags"],
                category_id="22", privacy_status="private", publish_at=publish_at,
            )
            # QUAN TRỌNG (Codex review điểm #6, bug nghiêm trọng phát hiện):
            # KHÔNG truyền thumbnail_path vào upload_video() -- youtube_upload.py
            # gọi upload_thumbnail() BÊN TRONG upload_video() SAU KHI video đã
            # upload xong; nếu set-thumbnail lỗi, exception văng ra TRƯỚC KHI
            # runner này kịp lưu video_id/status="uploaded" vào registry -- lần
            # resume sau sẽ KHÔNG biết video đã upload thành công, có thể
            # upload TRÙNG. Tách hẳn: upload video trước (không kèm thumbnail,
            # không thể fail vì lý do thumbnail), LƯU NGAY video_id/status, rồi
            # mới thử set thumbnail như 1 bước RIÊNG có thể fail độc lập mà
            # không ảnh hưởng tính đúng đắn của resume.
            result = upload_video(str(finalized_video), metadata, credentials_path)
            video_id = result["id"]
            entry["video_id"] = video_id
            entry["publish_at"] = publish_at
            entry["status"] = "uploaded"
            registry[key] = entry
            save_registry(registry, topic)

        # Tạo + set thumbnail (audit 9 điểm mục #6) -- CHỈ áp dụng Long-form,
        # đã xác nhận Shorts không hỗ trợ thumbnail tuỳ chỉnh (xem
        # thumbnail_generator.py docstring). Lỗi ở TOÀN BỘ bước này (tạo
        # ảnh HOẶC set qua API) KHÔNG được coi là lỗi upload -- video đã
        # upload xong ở trên, chỉ thiếu thumbnail tuỳ chỉnh (YouTube tự
        # chọn khung hình đại diện, hành vi mặc định cũ) -- fail-open có
        # chủ đích, khác hẳn chặn an toàn fail-CLOSED ở điểm #1 (ở đây
        # không có rủi ro an toàn/pháp lý). Lưu thumbnail_status để biết
        # tập nào cần set lại thủ công sau.
        entry["thumbnail_status"] = "skipped"
        try:
            background = _pick_thumbnail_background(entry["shot_list_path"])
            if background:
                import thumbnail_generator
                thumb_out = ep_dir / "thumbnail.jpg"
                title_text = entry["seo"].get("thumbnail_text")
                if not title_text:
                    # BUG THẬT (audit kênh Hình Sự 2026-08-14): fallback này dùng
                    # nguyên TIÊU ĐỀ VIDEO ĐẦY ĐỦ (thường 10-12 từ) làm chữ
                    # thumbnail -- content_seo.py giờ LUÔN sinh "thumbnail_text"
                    # (có kiểm tra cứng, xem _thumbnail_text_problem()), nên
                    # nhánh này chỉ nên chạy cho seo.json CŨ (sinh trước fix) --
                    # cảnh báo rõ thay vì lặng lẽ tái diễn bug cũ không dấu vết.
                    print(f"[{key}] CẢNH BÁO: seo.json thiếu 'thumbnail_text' (có thể sinh trước fix 2026-08-14) "
                          f"-- dùng tạm tiêu đề video đầy đủ cho thumbnail, có thể bị tràn chữ.", flush=True)
                    title_text = entry["seo"]["title"]
                thumbnail_generator.generate_thumbnail(str(background), title_text, str(thumb_out), domain=domain)
                from youtube_upload import upload_thumbnail
                upload_thumbnail(video_id, str(thumb_out), credentials_path)
                entry["thumbnail_status"] = "uploaded"
                print(f"[{key}] Đã set thumbnail tuỳ chỉnh.", flush=True)
            else:
                print(f"[{key}] Không có beat ảnh nào để làm nền thumbnail -- bỏ qua, dùng khung hình YouTube tự chọn.", flush=True)
        except Exception as exc:
            entry["thumbnail_status"] = "failed"
            print(f"[{key}] CẢNH BÁO: tạo/set thumbnail lỗi ({exc}) -- video ĐÃ upload thành công, chỉ thiếu thumbnail tuỳ chỉnh.", flush=True)
        registry[key] = entry
        save_registry(registry, topic)

        if playlist_title:
            # BUG THẬT phát hiện khi đăng EP_ADIDA_001 (2026-08-13): dùng
            # find_playlist_by_title() (substring match) + add_video_to_playlist()
            # -- nếu playlist CHƯA TỒN TẠI (series mới lần đầu đăng), find trả về
            # None và code CŨ chỉ lặng lẽ bỏ qua, không tạo playlist, không log lỗi,
            # video upload "thành công" nhưng không nằm trong playlist nào. Đổi sang
            # ensure_playlist_and_add() (đã có sẵn, dùng cho backfill Short) -- tự
            # tạo playlist nếu thiếu, verify sau khi thêm, và raise rõ nếu thật sự lỗi.
            try:
                # privacy_status="public" -- mọi playlist nội dung khác trên kênh này đều
                # public (kiểm tra thật qua API 2026-08-13); default "private" của
                # ensure_playlist_and_add() sẽ tạo playlist ẩn với người xem nếu không
                # truyền tường minh, đúng lỗi thật đã xảy ra với EP_ADIDA_001 lần đầu.
                ensure_playlist_and_add(credentials_path, playlist_title, video_id, privacy_status="public")
            except Exception as exc:
                print(f"[{key}] CẢNH BÁO: gán playlist '{playlist_title}' lỗi ({exc}) -- "
                      f"video ĐÃ upload thành công, chỉ thiếu playlist.", flush=True)

        # Dọn 2 bản trung gian giờ đã dư thừa (render_raw.mp4 trước khi trộn
        # BGM, with_bgm.mp4 trước khi đổi tên canonical) -- tới đây Drive đã
        # có bản canonical (qua finalize_episode.py) và YouTube đã có
        # video_id ở trên, nên KHÔNG còn lý do giữ 3 bản ~cùng dung lượng
        # của cùng 1 tập cục bộ mãi mãi (đã gây phình ổ đĩa thật, ~2-4GB dư
        # thừa mỗi tập Long). Giữ lại đúng 1 bản canonical, khớp cách Short
        # chỉ giữ 1 file render cuối/tập.
        from finalize_episode import build_canonical_name
        canonical_path = ep_dir / build_canonical_name(key, ep["title"], ".mp4")
        # finalized_video có thể trỏ vào output/video_test/ (nhánh fallback
        # legacy ở trên) thay vì video_bgm_path -- cũng dư thừa hệt như
        # render_raw/with_bgm 1 khi tới đây (đã upload xong), dọn luôn.
        stale_candidates = [entry.get("video_raw_path"), entry.get("video_bgm_path"), str(finalized_video)]
        for stale_path_str in stale_candidates:
            if not stale_path_str:
                continue
            stale_path = Path(stale_path_str)
            if stale_path.exists() and stale_path.resolve() != canonical_path.resolve():
                freed_mb = stale_path.stat().st_size / (1024 * 1024)
                stale_path.unlink()
                print(f"[{key}] Dọn bản trung gian dư thừa: {stale_path.name} (~{freed_mb:.0f}MB)", flush=True)

    return entry


def next_available_weekly_slot(registry: dict, weekday_targets: list[int], hour_utc: int) -> str:
    """weekday_targets: 0=Mon..6=Sun. Trả về publish_at ISO UTC kế tiếp
    trùng 1 trong các thứ mục tiêu, cách hiện tại ít nhất 2 giờ."""
    used = {v["publish_at"] for v in registry.values() if v.get("publish_at")}
    now = datetime.now(timezone.utc)
    for day_offset in range(1, 60):
        candidate_date = now.date() + timedelta(days=day_offset)
        if candidate_date.weekday() not in weekday_targets:
            continue
        candidate = datetime(candidate_date.year, candidate_date.month, candidate_date.day, hour_utc, 0, tzinfo=timezone.utc)
        iso = candidate.strftime("%Y-%m-%dT%H:%M:%SZ")
        if iso not in used and candidate - now > timedelta(hours=2):
            return iso
    raise RuntimeError("Không tìm được slot trống trong 60 ngày tới.")


def main() -> int:
    # PHẢI là dòng đầu tiên -- xem ghi chú tương ứng ở short_batch_runner.py's
    # main() / registry_lock.py mục 4 (G1). KHÔNG gọi mark_production_entry()
    # ở nơi nào khác trong file này hay trong test.
    mark_production_entry()
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="BUD", help="domain_id trong manifest.json Content-Creator")
    ap.add_argument("--topic", default=None, help="Tên thư mục Drive/topic_voices.json -- để trống sẽ tự suy ra ĐÚNG theo --domain qua domain_topics.json (xem P4c bên dưới)")
    ap.add_argument("--credentials", default=str(PROJECT_ROOT / ".youtube_channels" / "phat_giao.json"))
    ap.add_argument("--playlist", default=None, help="Tên playlist Long series thêm vào sau upload -- để trống nếu channel/topic chưa có playlist Long series (twice_weekly_batch.py LONG_PLAYLIST_BY_CHANNEL truyền tường minh giá trị này theo channel, KHÔNG dựa vào default ở đây; default trước đây hard-code tên playlist riêng của BUD, áp nhầm cho mọi channel khi gọi thiếu --playlist -- vô hại vì tên không khớp playlist nào bên FS/CL nhưng vẫn là lỗi cấu hình)")
    ap.add_argument("--count", type=int, default=1, help="Số tập xử lý trong lần chạy này")
    ap.add_argument("--weekly-days", nargs="+", type=int, default=[0, 3], help="Thứ trong tuần đăng (0=Thứ 2), mặc định Thứ 2 + Thứ 5 cho nhịp 2/tuần")
    ap.add_argument("--publish-hour-utc", type=int, default=13)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # P4c (E2E validation remediation): --topic từng default TĨNH về
    # 'Phật giáo' (topic của BUD) bất kể --domain là gì -- gọi `--domain
    # FS`/`--domain CL` mà quên `--topic` âm thầm xử lý NHẦM registry/thư
    # mục output của BUD trong khi mọi bước sinh nội dung khác (creative
    # profile, B-roll sanitizer...) vẫn dùng ĐÚNG domain FS/CL đã truyền
    # -- lẫn kênh ngay trong 1 lần chạy. Chỉ tự suy ra khi --topic THỰC SỰ
    # bị bỏ trống (None) -- --topic truyền tường minh (kể cả giá trị test
    # không khớp domain_topics.json thật, xem test suite) vẫn được tôn
    # trọng nguyên vẹn, không bị validate/ghi đè.
    if args.topic is None:
        resolved_topic = creative_profiles.topic_for_domain_id(args.domain)
        if resolved_topic is None:
            print(
                f"LỖI: --topic bị bỏ trống và domain '{args.domain}' chưa có trong domain_topics.json -- "
                f"không thể tự suy ra topic an toàn (không đoán tên). Truyền --topic tường minh.",
                file=sys.stderr,
            )
            return 1
        args.topic = resolved_topic
    topic = args.topic

    print("Đảm bảo audio đã render cho mọi tập sẵn sàng...", flush=True)
    run_audio_stage(args.topic)

    ready = discover_ready_episodes(args.domain, args.topic)
    registry = load_registry(topic)
    pending = [e for e in ready if registry.get(e["episode_id"], {}).get("status") not in TERMINAL_STATUSES]

    print(f"Tổng {len(ready)} tập sẵn sàng, {len(pending)} chưa xử lý xong, xử lý {min(args.count, len(pending))} tập.", flush=True)
    if not pending:
        print("Hết nguồn Long sẵn sàng -- cần Content-Creator bổ sung thêm tập.", flush=True)
        return 0

    n_done = n_failed = 0
    for ep in pending[:args.count]:
        try:
            registry = load_registry(topic)
            publish_at = next_available_weekly_slot(registry, args.weekly_days, args.publish_hour_utc)
            process_one_episode(ep, args.topic, args.credentials, args.playlist, publish_at, args.dry_run, domain=args.domain)
            n_done += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[{ep['episode_id']}] LỖI: {exc}", file=sys.stderr, flush=True)
            registry = load_registry(topic)
            entry = registry.setdefault(ep["episode_id"], {"key": ep["episode_id"]})
            entry["last_error"] = str(exc)
            # P3 (E2E validation remediation): classify a subprocess-timeout
            # failure distinctly from other errors -- a real ~27-minute
            # episode hit exactly this failure mode (long_batch_runner.py's
            # own 7200s run_step() timeout, not a content/code defect) and
            # was left permanently `failed` with no way to tell "worth just
            # retrying" from "needs real investigation" apart from manually
            # re-reading the raw error text. Does NOT change the retry
            # ceiling/terminal-status mechanism itself (still fails closed
            # after MAX_RETRIES_PER_EPISODE, per G1's registry-integrity
            # design) -- purely a machine-readable classification so an
            # operator (or future automation) can triage a `failed` episode
            # correctly at a glance.
            entry["last_error_type"] = "timeout" if isinstance(exc, subprocess.TimeoutExpired) else "error"
            entry["error_count"] = entry.get("error_count", 0) + 1
            if entry["error_count"] >= MAX_RETRIES_PER_EPISODE:
                entry["status"] = "failed"
                print(f"[{ep['episode_id']}] Lỗi {entry['error_count']} lần liên tiếp ({entry['last_error_type']}) -- đánh dấu failed.", file=sys.stderr, flush=True)
            save_registry(registry, topic)
            n_failed += 1

    print(f"\nHoàn tất: {n_done} tập xong, {n_failed} lỗi.", flush=True)
    return 1 if n_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
