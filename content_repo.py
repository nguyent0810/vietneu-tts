"""
Kết nối trực tiếp với repo Content-Creator (GitHub) làm nguồn input, thay
thế việc upload thủ công lên Drive. CHỈ ĐỌC (pull) — không commit/push gì
ngược lại repo đó (quyết định rõ ràng của người dùng, tránh toàn bộ ma sát
với cơ chế chặn push của hệ thống khi thao tác trên repo ngoài).

Luồng:
  ensure_content_repo()   -> clone/cập nhật bản clone local (shallow, --depth 1)
  discover_episodes()     -> quét DOMAINS/*/PRODUCTION_PACKAGES/*/EP*/
  gate_episode()          -> đọc manifest.json của Long + TOÀN BỘ manifest
                              từng đoạn Short, chỉ coi "sẵn sàng" khi
                              content_status + qa_status đạt yêu cầu
                              (fail-closed nếu thiếu/lạ — không đoán)
  stage_ready_episodes()  -> copy file Long/Short đã qua gate vào thư mục
                              local mà process_long_folder/process_short_folder
                              đã biết đọc — không tải lại qua Drive

Usage debug (in báo cáo gate, KHÔNG stage/render gì):
    uv run python content_repo.py --dry-run
"""
import argparse
import base64
import json
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from drive_utils import RETRY_ATTEMPTS, RETRY_BACKOFF_S

READY_CONTENT_STATUSES = {"READY_FOR_TTS_HANDOFF"}
ACCEPTABLE_QA_STATUSES = {"PASS", "PASS_WITH_ADVISORIES"}
REQUIRED_MANIFEST_KEYS = ("content_status", "qa_status", "domain_id", "package_id")

CONTENT_REPO_LOCAL = Path(__file__).parent / "content_repo_clone"
DOMAIN_TOPICS_FILE = Path(__file__).parent / "domain_topics.json"
DEFAULT_STAGING_ROOT = Path("drive_input/content_repo_staged")

# GIT_BIN giờ resolve qua external_bin.py (module DUY NHẤT cho mọi binary
# ngoài, xem docstring ở đó).
from external_bin import GIT_BIN  # noqa: E402, F401


class ContentRepoUnavailableError(RuntimeError):
    pass


class ManifestError(RuntimeError):
    pass


# ─── Git (chỉ đọc — clone/fetch/reset, không bao giờ commit/push) ──────────

def _git_auth(*args: str, cwd: Path, token: str, retries: int = RETRY_ATTEMPTS) -> subprocess.CompletedProcess:
    """Chạy 1 lệnh git với auth header TẠM THỜI cho đúng lệnh này — không
    bao giờ lưu token vào .git/config (tránh lỗi rò rỉ credential đã gặp
    khi nhúng token thẳng vào URL)."""
    header = "Authorization: Basic " + base64.b64encode(f"x-access-token:{token}".encode()).decode()
    cmd = [GIT_BIN, "-c", f"http.extraHeader={header}", *args]
    last_result = None
    for attempt in range(retries):
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            return result
        last_result = result
        if attempt < retries - 1:
            time.sleep(RETRY_BACKOFF_S * (attempt + 1))
    return last_result


def _validate_content_repo_structure(local_path: Path) -> None:
    """Kiểm tra hậu-fetch: repo vừa clone/fetch về THẬT SỰ là repo nội
    dung (có DOMAINS/ chứa ít nhất 1 thư mục domain con), không phải một
    repo/nội dung khác đã bị đổi ngầm dưới cùng 1 URL/tên (sự cố thật đã
    xảy ra: CONTENT_TOOL_REPO từng trỏ vào 1 repo mà nhánh main sau đó bị
    thay bằng code pipeline, khiến discover_episodes() âm thầm trả về
    rỗng thay vì báo lỗi rõ ràng). Fail-closed ngay tại điểm fetch, không
    chờ tới discover_episodes() mới phát hiện gián tiếp."""
    domains_root = local_path / "DOMAINS"
    if not domains_root.is_dir():
        raise ContentRepoUnavailableError(
            f"Repo nội dung tại {local_path} KHÔNG có thư mục DOMAINS/ sau khi fetch/clone -- "
            f"đây không phải cấu trúc repo nội dung hợp lệ (có thể CONTENT_TOOL_REPO đang trỏ nhầm "
            f"repo, hoặc nhánh main của repo đó đã bị thay nội dung khác). DỪNG, không dùng dữ liệu "
            f"này để tránh xử lý sai lặng lẽ."
        )
    if not any(p.is_dir() for p in domains_root.iterdir()):
        raise ContentRepoUnavailableError(
            f"DOMAINS/ tại {local_path} tồn tại nhưng rỗng (không có thư mục domain con nào) -- "
            f"DỪNG, không dùng dữ liệu này."
        )


def ensure_content_repo(token: str, repo_url: str, local_path: Path = CONTENT_REPO_LOCAL) -> Path:
    """Clone lần đầu nếu chưa có; lần sau fetch + reset --hard về bản mới
    nhất trên remote (không dùng `pull` — không bao giờ có commit local nên
    reset an toàn/đơn giản hơn, tránh mọi khả năng conflict)."""
    if not token:
        raise ContentRepoUnavailableError("Thiếu GITHUB_TOKEN — không thể truy cập Content-Creator repo.")
    if not repo_url:
        raise ContentRepoUnavailableError("Thiếu CONTENT_TOOL_REPO trong .github_integration.env.")

    if (local_path / ".git").exists():
        branch_result = subprocess.run([GIT_BIN, "branch", "--show-current"],
                                        cwd=local_path, capture_output=True, text=True)
        branch = branch_result.stdout.strip() or "main"

        result = _git_auth("fetch", "--depth", "1", "origin", branch, cwd=local_path, token=token)
        if result.returncode != 0:
            raise ContentRepoUnavailableError(f"git fetch thất bại: {result.stderr.strip()}")

        reset = subprocess.run([GIT_BIN, "reset", "--hard", "FETCH_HEAD"],
                                cwd=local_path, capture_output=True, text=True)
        if reset.returncode != 0:
            raise ContentRepoUnavailableError(f"git reset thất bại: {reset.stderr.strip()}")
        _validate_content_repo_structure(local_path)
        return local_path

    local_path.parent.mkdir(parents=True, exist_ok=True)
    result = _git_auth("clone", "--depth", "1", repo_url, str(local_path),
                        cwd=local_path.parent, token=token)
    if result.returncode != 0:
        raise ContentRepoUnavailableError(f"git clone thất bại: {result.stderr.strip()}")
    _validate_content_repo_structure(local_path)
    return local_path


# ─── Khám phá episode + đọc manifest ────────────────────────────────────────

@dataclass
class EpisodePaths:
    episode_dir: Path
    long_txt: Optional[Path]
    long_manifest: Optional[Path]
    short_txt: Optional[Path]
    short_manifests: list  # list[Path], 1 file / đoạn Short


def discover_episodes(repo_root: Path) -> list:
    """Quét DOMAINS/*/PRODUCTION_PACKAGES/*/EP*/. Không lọc theo domain ở
    bước này — tên thư mục domain (vd "BUDDHISM") KHÔNG chắc khớp domain_id
    thật trong manifest (vd "BUD"); việc lọc theo domain_topics.json chỉ
    làm được SAU khi đã đọc domain_id thật từ manifest, trong gate_episode()."""
    episodes = []
    domains_root = repo_root / "DOMAINS"
    if not domains_root.exists():
        return episodes
    for ep_dir in sorted(domains_root.glob("*/PRODUCTION_PACKAGES/*/EP*")):
        if not ep_dir.is_dir():
            continue
        long_dir, short_dir = ep_dir / "Long", ep_dir / "Short"
        long_txts = sorted(long_dir.glob("*.txt")) if long_dir.exists() else []
        short_txts = sorted(short_dir.glob("*.txt")) if short_dir.exists() else []
        long_manifest = ep_dir / "_PRODUCTION" / "Long" / "_INTERNAL" / "manifest.json"
        short_manifests = sorted((ep_dir / "_PRODUCTION" / "Short").glob("*/_INTERNAL/manifest.json"))

        long_txt = long_txts[0] if len(long_txts) == 1 else None
        resolved_long_manifest = long_manifest if long_manifest.exists() else None

        # Fallback -- Content-Creator dùng SONG SONG 1 format cũ hơn (thấy
        # thật trên EP004/BUDDHISM và cả 2 tập đầu tiên của CRIMINAL_LAW/
        # FENG_SHUI): manifest phẳng ở "_INTERNAL/manifest.json" (không
        # lồng "_PRODUCTION/Long/"), KHÔNG có thư mục "Long/*.txt" -- chỉ
        # có "OUTPUT/<tên file>" mà chính manifest.json tự khai qua field
        # "tts_output" (tương đối so với thư mục CHỨA "_INTERNAL/"). Field
        # này tồn tại y hệt trên cả 2 format (đã xác nhận qua manifest thật
        # của EP006) nên đọc thẳng nó thay vì đoán tên thư mục cố định --
        # để pipeline không phải chờ Content-Creator "chuẩn hoá" định dạng
        # trước khi dùng được nội dung đã QA PASS sẵn.
        if long_txt is None and resolved_long_manifest is None:
            flat_manifest = ep_dir / "_INTERNAL" / "manifest.json"
            if flat_manifest.exists():
                try:
                    flat_info = json.loads(flat_manifest.read_text(encoding="utf-8"))
                    tts_output = flat_info.get("tts_output")
                    if tts_output:
                        candidate = flat_manifest.parent.parent / tts_output
                        if candidate.exists():
                            long_txt = candidate
                            resolved_long_manifest = flat_manifest
                except (json.JSONDecodeError, OSError):
                    pass

        episodes.append(EpisodePaths(
            episode_dir=ep_dir,
            long_txt=long_txt,
            long_manifest=resolved_long_manifest,
            short_txt=short_txts[0] if len(short_txts) == 1 else None,
            short_manifests=short_manifests,
        ))
    return episodes


@dataclass
class ManifestInfo:
    content_status: str
    qa_status: str
    domain_id: str
    package_id: str
    raw: dict


def read_manifest(path: Path) -> ManifestInfo:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ManifestError(f"không đọc/parse được {path}: {e}")
    missing = [k for k in REQUIRED_MANIFEST_KEYS if k not in data]
    if missing:
        raise ManifestError(f"{path} thiếu field: {missing}")
    return ManifestInfo(
        content_status=data["content_status"],
        qa_status=data["qa_status"],
        domain_id=data["domain_id"],
        package_id=data["package_id"],
        raw=data,
    )


def manifest_is_ready(info: ManifestInfo) -> bool:
    return info.content_status in READY_CONTENT_STATUSES and info.qa_status in ACCEPTABLE_QA_STATUSES


# ─── Gate (chặt chẽ: Long/Short xét độc lập, fail-closed) ──────────────────

@dataclass
class EpisodeGateResult:
    episode: EpisodePaths
    domain_id: Optional[str] = None
    long_ready: bool = False
    short_ready: bool = False
    problems: list = field(default_factory=list)


# Audit kênh Hình Sự (2026-08-14, Part 1 -- hook/storytelling yếu): domain
# CL đã có sẵn 1 ngân hàng hook mở đầu chi tiết, đã tự kiểm tra an toàn
# (`content_repo_clone/DOMAINS/CRIMINAL_LAW/CREATIVE_KNOWLEDGE/CK_CL_001_Hinh_Su.md`,
# Phần 4 -- 5 Pillar, mỗi Pillar nhiều hook mã H1-H15+ sẵn dùng) -- nhưng
# KHÔNG CÓ cơ chế nào bắt buộc episode planner phải thực sự trích dẫn/dùng nó
# khi soạn mở đầu. EP001 (tập giải thích quy tắc kênh, không thuộc Pillar
# nào) là ví dụ hợp lệ không cần trích dẫn hook -- nhưng với các tập ÁN THẬT
# tiếp theo (từ cl_case_batch.py), việc bỏ qua ngân hàng hook có sẵn sẽ lặp
# lại đúng vấn đề "nặng về giải thích, thiếu hook cuốn hút" đã audit.
#
# VÒNG 2 (Cursor review, "NEEDS REWRITE"): vòng 1 khớp substring "hook"/
# "ck_cl_001" bất kỳ đâu -- PASS IM LẶNG cho MỌI planner thật, vì khung
# episode planner chuẩn của Content-Creator LUÔN có sẵn heading "Opening
# Hook"/"Hook Mở Đầu" (không liên quan gì Phần 4) và EP001 thật cũng cite
# CK_CL_001 cho lý do KHÁC (§2.4, kỹ thuật an toàn tường thuật, không phải
# hook Phần 4) -- false-negative đúng chính failure mode Part 1 đang cố bắt.
# SỬA: matcher giờ đòi hỏi 1 trong 2 tín hiệu CỤ THỂ mới coi là "đã trích
# dẫn hook bank": (a) 1 mã hook thật dạng "H" + số (vd "H9", "H12" -- đúng
# định dạng Phần 4 dùng), hoặc (b) cụm "Phần 4" xuất hiện GẦN "CK_CL_001"
# (cùng câu/đoạn, không phải CK_CL_001 nhắc ở chỗ khác cho mục đích khác).
#
# Cũng sửa (cùng review): `long_batch_runner.py`'s `discover_ready_episodes()`
# (đường dùng THẬT cho pipeline Long-form, khác `stage_ready_episodes()`)
# trước đây gọi gate_episode() nhưng BỎ HẲN result.problems -- cảnh báo này
# không bao giờ tới console thật khi vận hành Long-form CL. Đã nối lại, xem
# long_batch_runner.py.
#
# Phạm vi CHƯA che (ghi nhận rõ, không giả vờ đã xong): pipeline Short của CL
# (`cl_case_batch.py`/`cl_case_generation.py`) là 1 luồng HOÀN TOÀN khác
# (không đọc `02_EPISODE_PLANNER.md`/không qua gate_episode() dạng Long) --
# check này KHÔNG áp dụng cho 8 case Short đang chờ người review thủ công.
_CL_HOOK_CODE_RE = re.compile(r"\bh\d{1,3}\b", re.IGNORECASE)
_CL_HOOK_BANK_SECTION_RE = re.compile(r"ck_cl_001[^\n]{0,80}ph[aầ]n\s*4|ph[aầ]n\s*4[^\n]{0,80}ck_cl_001", re.IGNORECASE)


def _check_cl_hook_bank_citation(long_manifest_path: Path) -> list[str]:
    planner_path = long_manifest_path.parent / "02_EPISODE_PLANNER.md"
    if not planner_path.exists():
        return []  # không có planner để kiểm tra -- không phải lỗi của check này
    text = planner_path.read_text(encoding="utf-8", errors="ignore")
    if _CL_HOOK_CODE_RE.search(text) or _CL_HOOK_BANK_SECTION_RE.search(text):
        return []
    return [
        f"CẢNH BÁO (advisory, không chặn): {planner_path.name} không trích dẫn mã hook cụ thể "
        f"(vd \"H9\") hay Phần 4 của CK_CL_001_Hinh_Su.md (ngân hàng hook mở đầu domain CL) -- "
        f"nếu đây là tập kể 1 vụ án thật (không phải tập giải thích quy tắc kênh), cân nhắc "
        f"trích dẫn 1 hook từ Phần 4 làm mở đầu trước khi render, tránh lặp lại vấn đề "
        f"'nặng giải thích, thiếu hook' đã audit ở EP001. (Lưu ý: check này chỉ áp dụng cho "
        f"pipeline Long-form -- các case Short từ cl_case_batch.py đi qua luồng khác, không "
        f"được kiểm tra ở đây.)"
    ]


def gate_episode(episode: EpisodePaths) -> EpisodeGateResult:
    problems = []
    domain_id = None
    long_ready = False
    short_ready = False

    if episode.long_txt is None:
        problems.append("Long/: thiếu hoặc có >1 file .txt (cần đúng 1)")
    if episode.long_manifest is None:
        problems.append("thiếu _PRODUCTION/Long/_INTERNAL/manifest.json")
    if episode.long_txt is not None and episode.long_manifest is not None:
        try:
            info = read_manifest(episode.long_manifest)
            domain_id = info.domain_id
            long_ready = manifest_is_ready(info)
            if not long_ready:
                problems.append(f"Long chưa sẵn sàng: content_status={info.content_status} qa_status={info.qa_status}")
            elif domain_id == "CL":
                problems.extend(_check_cl_hook_bank_citation(episode.long_manifest))
        except ManifestError as e:
            problems.append(f"Long manifest lỗi: {e}")

    if episode.short_txt is None:
        problems.append("Short/: thiếu hoặc có >1 file .txt (cần đúng 1)")
    elif not episode.short_manifests:
        problems.append("không tìm thấy manifest nào cho Short (_PRODUCTION/Short/*/_INTERNAL/manifest.json)")
    else:
        all_ready = True
        for mpath in episode.short_manifests:
            try:
                info = read_manifest(mpath)
                if domain_id is None:
                    domain_id = info.domain_id
                if not manifest_is_ready(info):
                    all_ready = False
                    problems.append(f"{mpath.parent.parent.name}: content_status={info.content_status} qa_status={info.qa_status}")
            except ManifestError as e:
                all_ready = False
                problems.append(f"Short manifest lỗi ({mpath}): {e}")
        short_ready = all_ready

    return EpisodeGateResult(episode=episode, domain_id=domain_id,
                              long_ready=long_ready, short_ready=short_ready, problems=problems)


# ─── Domain -> chủ đề + staging ─────────────────────────────────────────────

def load_domain_topics() -> dict:
    if not DOMAIN_TOPICS_FILE.exists():
        return {}
    data = json.loads(DOMAIN_TOPICS_FILE.read_text(encoding="utf-8"))
    return data.get("domains", {})


def stage_ready_episodes(
    repo_root: Path,
    domain_topics: dict,
    local_staging_root: Path = DEFAULT_STAGING_ROOT,
) -> dict:
    """Trả về {topic: {"long": [Path,...], "short": [Path,...]}} — file đã
    copy sẵn ra local_staging_root, tên giữ nguyên như trong repo gốc."""
    staged: dict = {}

    for ep in discover_episodes(repo_root):
        result = gate_episode(ep)
        for p in result.problems:
            print(f"[content_repo] {ep.episode_dir.name}: {p}", flush=True)

        if result.domain_id is None:
            print(f"[content_repo] {ep.episode_dir.name}: không đọc được domain_id từ bất kỳ manifest nào — bỏ qua.", flush=True)
            continue

        topic = domain_topics.get(result.domain_id)
        if topic is None:
            print(f"[content_repo] {ep.episode_dir.name}: domain_id '{result.domain_id}' "
                  f"chưa có trong domain_topics.json — bỏ qua.", flush=True)
            continue

        bucket = staged.setdefault(topic, {"long": [], "short": []})

        if result.long_ready:
            dest_dir = local_staging_root / topic / "Long"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / ep.long_txt.name
            shutil.copy2(ep.long_txt, dest)
            bucket["long"].append(dest)
            print(f"[content_repo] {ep.episode_dir.name}: staged Long -> {dest}", flush=True)

        if result.short_ready:
            dest_dir = local_staging_root / topic / "Short"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / ep.short_txt.name
            shutil.copy2(ep.short_txt, dest)
            bucket["short"].append(dest)
            print(f"[content_repo] {ep.episode_dir.name}: staged Short -> {dest}", flush=True)

    return staged


# ─── CLI debug: báo cáo gate mà không stage/render gì ──────────────────────

def load_github_credentials() -> tuple:
    import os
    env_file = Path(__file__).parent / ".github_integration.env"
    values = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            values[k.strip()] = v.strip()
    token = os.environ.get("GITHUB_TOKEN") or values.get("GITHUB_TOKEN")
    url = os.environ.get("CONTENT_TOOL_REPO") or values.get("CONTENT_TOOL_REPO")
    return token, url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Chỉ in báo cáo gate, không stage/render gì")
    args = ap.parse_args()

    token, repo_url = load_github_credentials()
    repo_root = ensure_content_repo(token, repo_url)
    domain_topics = load_domain_topics()

    episodes = discover_episodes(repo_root)
    print(f"Tìm thấy {len(episodes)} episode trong Content-Creator repo.\n")
    for ep in episodes:
        result = gate_episode(ep)
        topic = domain_topics.get(result.domain_id, "(chưa map)") if result.domain_id else "(không rõ domain)"
        print(f"{ep.episode_dir.relative_to(repo_root)}")
        print(f"  domain_id={result.domain_id}  topic={topic}")
        print(f"  long_ready={result.long_ready}  short_ready={result.short_ready}")
        for p in result.problems:
            print(f"  ! {p}")
        print()

    if args.dry_run:
        return 0

    staged = stage_ready_episodes(repo_root, domain_topics)
    print("Đã stage:", {k: {"long": len(v["long"]), "short": len(v["short"])} for k, v in staged.items()})
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
