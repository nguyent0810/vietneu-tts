"""
Resolve MỌI binary/CLI ngoài (git, rclone, codex, node, npx, osascript) dùng
trong pipeline qua 1 module DUY NHẤT -- thay cho các bản RCLONE_BIN/CODEX_BIN/
GIT_BIN từng khai báo rời rạc ở drive_utils.py/content_seo.py/content_repo.py.

LÝ DO CÓ MODULE NÀY (phát hiện thật qua nhiều vòng debug launchd 04/08):
launchd chạy process con với PATH TỐI GIẢN (/usr/bin:/bin:/usr/sbin:/sbin)
-- KHÔNG có /opt/homebrew/bin, KHÔNG có nvm sourcing từ .zshrc. Bất kỳ
subprocess.run(["<tên bare>", ...]) nào cũng có nguy cơ:
  (a) FileNotFoundError thẳng (rclone, codex, node, npx -- đều ở
      /opt/homebrew hoặc ~/.nvm, không nằm trong PATH tối giản), hoặc
  (b) ÂM THẦM dùng NHẦM bản khác (git -- /usr/bin/git của Apple CŨ hơn
      bản /opt/homebrew/git dùng lúc chạy tay, không crash nhưng hành vi
      có thể khác).

FAIL-CLOSED khi capability THẬT SỰ được gọi (KHÔNG phải lúc import module
này nữa -- BUG THẬT phát hiện qua CI Linux, xem PR #2 review): mỗi
get_<tool>_bin() resolve + cache (functools.lru_cache) đúng 1 LẦN, vào lúc
CALLER ĐẦU TIÊN thực sự cần binary đó -- không phải lúc `import
external_bin` hay lúc import bất kỳ module nào transitively kéo theo nó.
Trước đây cả 6 binary (git/rclone/node/codex/npx/osascript) resolve NGAY
lúc import module -- nghĩa là 1 consumer chỉ cần đúng 1 binary (vd
short_health_check.py chỉ cần osascript) vẫn bị crash import nếu BẤT KỲ
binary nào khác trong 6 cái đó thiếu, kể cả những cái consumer đó không hề
dùng tới. Phát hiện thật trên CI: chạy trên Ubuntu (không có rclone, không
có osascript -- osascript về bản chất KHÔNG THỂ cài trên Linux, đây là
binary macOS thuần) khiến collect test_short_health_check.py (chỉ cần
osascript) crash vì RCLONE_BIN resolve trước đó trong cùng module. Lỗi
rõ ràng và sớm nhất có thể vẫn được giữ nguyên tinh thần -- chỉ trễ lại
tới đúng lúc capability đó được gọi, thay vì lúc import bất kỳ thứ gì có
thể transitively chạm module này. Version vẫn được log 1 lần ra stderr
lúc resolve (không đổi)."""
import functools
import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


class MissingBinaryError(RuntimeError):
    pass


def _version_sort_key(path: str) -> tuple:
    """Khoá sắp xếp cho fallback glob (vd nvm versions/*/bin/node) -- ưu
    tiên đúng version BÁN NGỮ NGHĨA (semantic: so tuple số, "v20.20.2" >
    "v9.x.x") thay vì string sort thuần (BUG THẬT phát hiện qua Codex CLI
    review trước khi commit: "v9" xếp SAU "v20" theo alphabet dù cũ hơn
    hẳn -- vòng sửa đầu dùng mtime cũng bị Codex bác vì mtime "mới cài gần
    đây" không tương đương "version cao hơn", vd downgrade sau khi đã có
    bản mới). Tách "vN.N.N" từ đường dẫn nếu có (đúng format thư mục nvm);
    KHÔNG tìm được pattern version rõ ràng thì fallback về mtime (không
    throw, không đoán mù -- vẫn cần 1 tiêu chí xác định cho binary không
    nằm trong thư mục kiểu nvm)."""
    match = re.search(r"v(\d+)\.(\d+)\.(\d+)", path)
    if match:
        return (1, tuple(int(g) for g in match.groups()))
    return (0, os.path.getmtime(path))


def resolve_bin(display_name: str, exe_name: str, extra_glob_patterns: list[str] | None = None,
                 install_hint: str = "", version_env: dict | None = None) -> str:
    """Thử shutil.which() (đúng PATH hiện tại) trước, rồi tới các glob
    pattern dự phòng (vd nvm versions/*/bin/<exe>) theo thứ tự cho tới khi
    khớp. KHÔNG bao giờ trả về tên bare -- không tìm thấy gì thì raise
    MissingBinaryError NGAY (fail-closed), không để lỗi trôi xuống tận lúc
    subprocess.run() thật mới báo (traceback lúc đó không nói rõ nguyên
    nhân PATH).

    version_env: env dict TÙY CHỌN để chạy `<bin> --version` -- cần cho
    codex/npx (script node, "--version" cũng tự chạy "env node ..." bên
    trong, PHÁT HIỆN THẬT lúc build module này: probe version của chính
    codex/npx cũng lỗi "env: node: No such file or directory" dưới PATH
    tối giản nếu không truyền PATH có chứa thư mục node vào đây)."""
    found = shutil.which(exe_name)
    if found:
        _log_resolved(display_name, found, env=version_env)
        return found

    for pattern in (extra_glob_patterns or []):
        matches = glob.glob(pattern)
        if matches:
            resolved = max(matches, key=_version_sort_key)
            _log_resolved(display_name, resolved, via="fallback glob", env=version_env)
            return resolved

    hint = f" ({install_hint})" if install_hint else ""
    raise MissingBinaryError(
        f"Không tìm thấy binary '{exe_name}' (cho {display_name}) qua PATH hiện tại lẫn "
        f"mọi fallback path đã biết{hint}. PATH hiện tại: {os.environ.get('PATH', '<rỗng>')}"
    )


def _log_resolved(display_name: str, path: str, via: str = "PATH", env: dict | None = None) -> None:
    version = _probe_version(path, env=env)
    print(f"[external_bin] {display_name}: {path} (qua {via}){' -- ' + version if version else ''}",
          file=sys.stderr, flush=True)


def _probe_version(path: str, env: dict | None = None) -> str:
    """Chạy `<path> --version` với timeout ngắn để log ra bản THẬT đang
    dùng -- best-effort, KHÔNG raise nếu lệnh không hỗ trợ --version hoặc
    treo (vd 1 số binary không có flag này, hoặc cần network để check update
    trước khi in version)."""
    try:
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5,
                                 env=env if env is not None else os.environ.copy())
        line = (result.stdout or result.stderr or "").strip().splitlines()
        return line[0] if line else ""
    except Exception:
        return ""


# ─── Binary cụ thể -- MỖI cái resolve LAZY (đúng 1 lần, cache qua
# functools.lru_cache) vào lúc get_<tool>_bin() được gọi THẬT lần đầu,
# KHÔNG phải lúc import module này. ──────────────────────────────────────

@functools.lru_cache(maxsize=1)
def get_git_bin() -> str:
    return resolve_bin("git", "git")


@functools.lru_cache(maxsize=1)
def get_rclone_bin() -> str:
    return resolve_bin(
        "rclone", "rclone",
        extra_glob_patterns=["/opt/homebrew/bin/rclone", "/usr/local/bin/rclone"],
        install_hint="brew install rclone",
    )


@functools.lru_cache(maxsize=1)
def get_node_bin() -> str:
    """PHẢI được gọi TRƯỚC get_codex_bin()/get_npx_bin() (dù bản thân node
    hiếm khi bị gọi trực tiếp) -- node_subprocess_env() bên dưới cần nó để
    probe version của chính codex/npx cho đúng (2 cái đó tự "env node" bên
    trong). Cả hai getter đó tự gọi node_subprocess_env(), nên thứ tự này
    tự động đúng, không cần caller lo."""
    return resolve_bin(
        "node", "node",
        extra_glob_patterns=[str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "node")],
        install_hint="nvm install node, hoặc brew install node",
    )


def node_subprocess_env() -> dict:
    """codex/npx đều là script node (shebang "#!/usr/bin/env node") --
    resolve ĐƯỢC đường dẫn binary thôi CHƯA ĐỦ dưới launchd: lúc thực thi,
    OS tự chạy "env node ..." để tìm interpreter, và "node" lại là 1
    bare-name KHÁC launchd không thấy được qua PATH tối giản (phát hiện
    thật: sau khi resolve xong CODEX_BIN, lỗi đổi thành "codex lỗi (exit
    127): env: node: No such file or directory" -- và ngay cả việc PROBE
    VERSION của chính codex/npx lúc resolve() cũng dính lỗi y hệt nếu
    không gọi hàm này trước). Prepend thư mục chứa node vào PATH của
    subprocess con để "env node" bên trong tự thấy. Gọi get_node_bin() ở
    đây (không phải hằng số module-level) -- node CHỈ resolve khi 1 trong
    2 caller thật (codex/npx) cần tới, không phải lúc import."""
    env = os.environ.copy()
    node_dir = str(Path(get_node_bin()).parent)
    env["PATH"] = f"{node_dir}:{env.get('PATH', '')}"
    return env


@functools.lru_cache(maxsize=1)
def get_codex_bin() -> str:
    return resolve_bin(
        "codex", "codex",
        extra_glob_patterns=[str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "codex")],
        install_hint="npm install -g @openai/codex",
        version_env=node_subprocess_env(),
    )


@functools.lru_cache(maxsize=1)
def get_npx_bin() -> str:
    return resolve_bin(
        "npx", "npx",
        extra_glob_patterns=[str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "npx")],
        install_hint="đi kèm node/npm",
        version_env=node_subprocess_env(),
    )


@functools.lru_cache(maxsize=1)
def get_osascript_bin() -> str:
    """osascript LUÔN nằm ở /usr/bin/osascript trên mọi máy macOS -- /usr/bin
    CÓ trong PATH tối giản của launchd (/usr/bin:/bin:/usr/sbin:/sbin), nên
    bare "osascript" thực ra KHÔNG crash dưới launchd (khác hẳn
    rclone/codex/node/npx -- đã xác minh thật qua env -i
    PATH=/usr/bin:/bin:/usr/sbin:/sbin). Vẫn resolve qua đây (thay vì để
    bare ở call site) để tuân đúng yêu cầu "1 module duy nhất, log rõ
    path/version" -- KHÔNG phải vì có bug PATH thật. osascript hoàn toàn
    KHÔNG tồn tại trên Linux (framework macOS thuần, không cài được qua
    apt/bất kỳ package manager Linux nào) -- đây chính xác là lý do
    resolution phải LAZY: importer chỉ cần biết osascript khi thực sự gọi
    _notify_macos(), không phải lúc import short_health_check.py (phát
    hiện thật qua CI Linux crash lúc collect test, xem PR #2 review)."""
    return resolve_bin("osascript", "osascript")


# AGY (Antigravity CLI) KHÁC hẳn 5 binary trên: cố ý KHÔNG fail-closed ở đây
# -- agy là optional/best-effort trong toàn pipeline (quota Google hạn chế,
# mọi call site đã tự kiểm tra AGY_BIN.exists() và fallback sang Codex nếu
# thiếu/hết quota, xem content_seo.py/content_review.py/director_bible.py/
# creative_director.py/agy_image_client.py). Trước đây hằng số này bị khai
# báo LẶP LẠI y hệt ở cả 5 file đó -- gom về đây làm 1 nguồn duy nhất, giữ
# nguyên đúng hành vi "không có cũng không crash" cho caller tự quyết định.
AGY_BIN = Path.home() / ".local" / "bin" / "agy"
if AGY_BIN.exists():
    _log_resolved("agy (optional)", str(AGY_BIN), via="fixed path")
else:
    print(f"[external_bin] agy (optional): KHÔNG thấy tại {AGY_BIN} -- caller tự fallback, không fail-closed.",
          file=sys.stderr, flush=True)
