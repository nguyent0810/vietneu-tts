"""Dựng creator_v2 trên máy mới: nối thư mục media lớn (không nằm trong git) và kiểm môi trường.

    python scripts/setup_local.py --media-root <thư mục media>   # tạo link / chép file nhỏ, rồi kiểm
    python scripts/setup_local.py --check                        # chỉ báo cáo, không đổi gì
    python scripts/setup_local.py --media-root <...> --link-output   # ngày chuyển hẳn: nối cả output/

"Media root" là thư mục có cùng bố cục với creator_v2 (mặc định lấy từ biến môi trường CREATOR_MEDIA_ROOT).
Windows: nối bằng directory junction (`mklink /J`, không cần quyền admin); nơi khác: symlink.
KHÔNG BAO GIỜ ghi đè hay xóa: đích đã có (thư mục, file hay link) thì báo "đã có" và bỏ qua.
Bảo mật: YT_CREDS_DIR chỉ kiểm `is_dir()`; không liệt kê, không mở, không in giá trị.
Mã thoát: 0 nếu mọi mục BẮT BUỘC ổn, 1 nếu không.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Đường dẫn tương đối (từ media root -> creator_v2) được nối bằng link. Thêm mục mới ở đây.
LINKS = (
    "motion/hf/assets/clips",
    "motion/hf/assets/cases",
    "motion/hf/assets/long",
    "output/music",
    ".ref",
)
OUTPUT_LINK = "output"                     # --link-output: nối cả output/ thay cho output/music
OUTPUT_SUBLINKS = ("output/music",)
# File nhỏ được CHÉP (glob từ media root), chỉ chép khi đích chưa có.
COPY_GLOBS = ("motion/stier/ambience/*.wav",)

# Cùng danh sách với CI (job creator-v2-tests): tên pip -> tên import.
PACKAGES = (("vnlunar", "vnlunar"), ("numpy", "numpy"), ("scipy", "scipy"), ("pillow", "PIL"),
            ("requests", "requests"), ("soundfile", "soundfile"), ("httpx", "httpx"))
VNLUNAR_PIN = "1.0.4"
PIP_CMD = 'pip install "pytest>=8.0" "httpx>=0.27" "vnlunar==1.0.4" numpy scipy "pillow>=10" requests soundfile'

OK, WARN, FAIL = "OK", "CẢNH BÁO", "THIẾU"


class Report:
    """Gom kết quả: (nhóm, mục, trạng thái, ghi chú, bắt buộc?)."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str, str, bool]] = []

    def add(self, group: str, item: str, status: str, note: str = "", required: bool = True) -> None:
        self.rows.append((group, item, status, note, required))
        print(f"[{status}] {item}" + (f" - {note}" if note else ""))

    @property
    def ok(self) -> bool:
        return not any(s == FAIL and req for _, _, s, _, req in self.rows)

    def table(self) -> None:
        print("\n== Tóm tắt ==")
        w = max((len(r[1]) for r in self.rows), default=10)
        for _g, item, status, _n, _r in self.rows:
            print(f"{item.ljust(w)}  {status}")
        counts = {s: sum(1 for r in self.rows if r[2] == s) for s in (OK, WARN, FAIL)}
        print(f"\n{counts[OK]} ổn, {counts[WARN]} cảnh báo, {counts[FAIL]} thiếu"
              f" -> {'ĐẠT' if self.ok else 'CHƯA ĐẠT'}")


def is_link(p: Path) -> bool:
    """Symlink hoặc junction (Windows: Path.is_junction, Python 3.12+; 3.11 dùng reparse point)."""
    if p.is_symlink():
        return True
    isj = getattr(p, "is_junction", None)
    if isj is not None:
        return bool(isj())
    try:
        return bool(os.lstat(p).st_file_attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    except (AttributeError, OSError):
        return False


def make_link(dest: Path, src: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(dest), str(src)], capture_output=True, text=True)
        if r.returncode != 0:
            raise OSError((r.stderr or r.stdout).strip() or f"mklink lỗi {r.returncode}")
    else:
        os.symlink(src, dest, target_is_directory=src.is_dir())


def exists_any(p: Path) -> bool:
    return p.exists() or is_link(p)


def link_one(rep: Report, rel: str, media: Path, root: Path, dry: bool) -> None:
    src, dest = media / rel, root / rel
    name = f"link {rel}"
    if exists_any(dest):
        if is_link(dest) and Path(os.path.realpath(dest)) != Path(os.path.realpath(src)):
            rep.add("link", name, WARN, "đã có, nhưng link trỏ chỗ khác media root (giữ nguyên)", required=False)
        elif rel == OUTPUT_LINK and not is_link(dest):
            rep.add("link", name, WARN, "output/ đã là thư mục thật nên không nối được; đổi tên nó rồi chạy lại",
                    required=False)
        else:
            rep.add("link", name, OK, "đã có")
        return
    if not src.exists():
        rep.add("link", name, WARN, f"không thấy nguồn trong media root ({rel}), bỏ qua", required=False)
        return
    if dry:
        rep.add("link", name, FAIL, "chưa nối (chạy không kèm --check để nối)")
        return
    try:
        make_link(dest, src)
    except OSError as e:
        rep.add("link", name, FAIL, f"không tạo được link: {e}")
        return
    rep.add("link", name, OK, "đã nối")


def copy_small(rep: Report, media: Path, root: Path, dry: bool) -> None:
    for pat in COPY_GLOBS:
        srcs = sorted(media.glob(pat))
        if not srcs:
            rep.add("copy", f"chép {pat}", WARN, "không thấy nguồn trong media root", required=False)
            continue
        for src in srcs:
            rel = src.relative_to(media)
            dest = root / rel
            if exists_any(dest):
                rep.add("copy", f"chép {rel.as_posix()}", OK, "đã có")
            elif dry:
                rep.add("copy", f"chép {rel.as_posix()}", WARN, "chưa có (chạy không kèm --check để chép)", required=False)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                rep.add("copy", f"chép {rel.as_posix()}", OK, "đã chép")


def check_env(rep: Report, root: Path) -> None:
    for pip_name, mod in PACKAGES:
        try:
            importlib.import_module(mod)
            rep.add("env", f"gói {pip_name}", OK)
        except Exception:
            rep.add("env", f"gói {pip_name}", FAIL, f"không import được; cài: {PIP_CMD}")
    try:
        ver = importlib.metadata.version("vnlunar")
        if ver == VNLUNAR_PIN:
            rep.add("env", f"vnlunar=={VNLUNAR_PIN}", OK)
        else:
            rep.add("env", f"vnlunar=={VNLUNAR_PIN}", WARN,
                    f'đang {ver}; cài lại: pip install "vnlunar=={VNLUNAR_PIN}"', required=False)
    except importlib.metadata.PackageNotFoundError:
        rep.add("env", f"vnlunar=={VNLUNAR_PIN}", FAIL, f'chưa cài; cài: pip install "vnlunar=={VNLUNAR_PIN}"')
    for exe in ("node", "npx", "ffmpeg"):
        found = shutil.which(exe)
        rep.add("env", f"{exe} trong PATH", OK if found else FAIL, "" if found else f"không thấy {exe}")
    if (root / "data" / "stier" / "specs").is_dir():
        rep.add("env", "data/stier/specs", OK)
    else:
        rep.add("env", "data/stier/specs", FAIL, "chưa có; dữ liệu data/ đến cùng PR #134")
    creds = os.environ.get("YT_CREDS_DIR")
    if not creds:
        rep.add("env", "YT_CREDS_DIR", FAIL, "chưa đặt")
    elif Path(creds).is_dir():       # chỉ is_dir(); không liệt kê/mở/in
        rep.add("env", "YT_CREDS_DIR", OK, "đã đặt")
    else:
        rep.add("env", "YT_CREDS_DIR", FAIL, "đã đặt nhưng thư mục không tồn tại")


def run(media_root: str | None, check: bool, link_output: bool, root: Path | None = None) -> int:
    root = root or ROOT
    rep = Report()
    media = Path(media_root).resolve() if media_root else None
    if media is None:
        rep.add("media", "media root", FAIL, "chưa đặt (--media-root hoặc CREATOR_MEDIA_ROOT)")
    elif not media.is_dir():
        rep.add("media", "media root", FAIL, "thư mục không tồn tại")
        media = None
    else:
        rep.add("media", "media root", OK, "đã đặt")
    if media is not None:
        links = list(LINKS)
        if link_output:
            links = [x for x in links if x not in OUTPUT_SUBLINKS] + [OUTPUT_LINK]
        for rel in links:
            link_one(rep, rel, media, root, dry=check)
        copy_small(rep, media, root, dry=check)
    check_env(rep, root)
    rep.table()
    return 0 if rep.ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--media-root", default=os.environ.get("CREATOR_MEDIA_ROOT"),
                    help="thư mục media (cùng bố cục creator_v2); mặc định env CREATOR_MEDIA_ROOT")
    ap.add_argument("--check", action="store_true", help="chỉ báo cáo, không đổi gì; thoát 0 nếu đủ, 1 nếu thiếu")
    ap.add_argument("--link-output", action="store_true", help="nối cả output/ thay vì chỉ output/music (ngày chuyển hẳn)")
    a = ap.parse_args(argv)
    return run(a.media_root, a.check, a.link_output)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))   # site-packages có gói "factory" khác (factory_boy)
    from factory.console import utf8_console
    utf8_console()
    sys.exit(main())
