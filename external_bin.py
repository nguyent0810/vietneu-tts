"""
Resolve MỌI binary/CLI ngoài (git, rclone, codex, node, npx...) dùng trong
pipeline qua 1 module DUY NHẤT -- thay cho các bản RCLONE_BIN/CODEX_BIN/
GIT_BIN từng khai báo rời rạc ở drive_utils.py/content_seo.py/content_repo.py
(giữ lại re-export ở đó để không phải sửa import khắp nơi, nhưng nguồn thật
là ở đây).

LÝ DO CÓ MODULE NÀY (phát hiện thật qua nhiều vòng debug launchd 04/08):
launchd chạy process con với PATH TỐI GIẢN (/usr/bin:/bin:/usr/sbin:/sbin)
-- KHÔNG có /opt/homebrew/bin, KHÔNG có nvm sourcing từ .zshrc. Bất kỳ
subprocess.run(["<tên bare>", ...]) nào cũng có nguy cơ:
  (a) FileNotFoundError thẳng (rclone, codex, node, npx -- đều ở
      /opt/homebrew hoặc ~/.nvm, không nằm trong PATH tối giản), hoặc
  (b) ÂM THẦM dùng NHẦM bản khác (git -- /usr/bin/git của Apple CŨ hơn
      bản /opt/homebrew/git dùng lúc chạy tay, không crash nhưng hành vi
      có thể khác).

FAIL-CLOSED: resolve NGAY lúc import (không đợi lúc gọi thật mới báo lỗi)
-- lỗi phải rõ ràng và sớm nhất có thể, không phải 1 dòng traceback mơ hồ
sâu trong lúc render. Version được log 1 lần ra stderr lúc resolve để biết
CHÍNH XÁC bản nào đang chạy (đối chiếu khi có báo cáo hành vi lạ).
"""
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


# ─── Binary cụ thể, resolve NGAY lúc import module này (fail-closed sớm) ──

GIT_BIN = resolve_bin("git", "git")

RCLONE_BIN = resolve_bin(
    "rclone", "rclone",
    extra_glob_patterns=["/opt/homebrew/bin/rclone", "/usr/local/bin/rclone"],
    install_hint="brew install rclone",
)

# NODE_BIN PHẢI resolve TRƯỚC codex/npx (dù bản thân node hiếm khi bị gọi
# trực tiếp) -- vì node_subprocess_env() bên dưới cần nó để probe version
# của chính codex/npx cho đúng (2 cái đó tự "env node" bên trong).
NODE_BIN = resolve_bin(
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
    không gọi hàm này trước). Prepend thư mục chứa NODE_BIN vào PATH của
    subprocess con để "env node" bên trong tự thấy."""
    env = os.environ.copy()
    node_dir = str(Path(NODE_BIN).parent)
    env["PATH"] = f"{node_dir}:{env.get('PATH', '')}"
    return env


CODEX_BIN = resolve_bin(
    "codex", "codex",
    extra_glob_patterns=[str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "codex")],
    install_hint="npm install -g @openai/codex",
    version_env=node_subprocess_env(),
)

NPX_BIN = resolve_bin(
    "npx", "npx",
    extra_glob_patterns=[str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "npx")],
    install_hint="đi kèm node/npm",
    version_env=node_subprocess_env(),
)

# osascript LUÔN nằm ở /usr/bin/osascript trên mọi máy macOS -- /usr/bin CÓ
# trong PATH tối giản của launchd (/usr/bin:/bin:/usr/sbin:/sbin), nên bare
# "osascript" thực ra KHÔNG crash dưới launchd (khác hẳn rclone/codex/node/npx
# -- đã xác minh thật qua env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin). Vẫn
# resolve qua đây (thay vì để bare ở call site) để tuân đúng yêu cầu "1 module
# duy nhất, log rõ path/version" -- KHÔNG phải vì có bug PATH thật.
OSASCRIPT_BIN = resolve_bin("osascript", "osascript")

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
