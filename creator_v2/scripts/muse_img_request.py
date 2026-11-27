"""Tạo ảnh AI cho Long trực tiếp qua `muse-cli` (agent muse.ai của chủ kênh), không qua webhook bot (#539).

    python scripts/muse_img_request.py <topic> [--only ai_03,ai_07] [--wait 1200] [--faces]

- Đọc `data/long/<topic>/ai_prompts.md` (mục `## ai_NN.png …` như ai_img_request.py), mỗi ảnh còn thiếu gửi MỘT tin
  vào một side chat riêng của topic (thread id lưu ở `output/long/<topic>/muse_thread.txt`), chờ agent trả ảnh,
  tải về `motion/hf/assets/long/<topic>/img/ai/ai_NN.png`, cuối cùng chạy `scripts/ai_img_import.py` như đường cũ.
- Muse trả ảnh sau ~30 s (đo 27/11/2026); script dò `muse-cli files` thay vì `send --wait` (không nhận ra ảnh). Hết giờ chờ thì ghi message id vào `muse_pending.json`; lần chạy sau
  tải lại theo id ấy trước, không gửi lại prompt.
- Không in thông tin tài khoản; muse-cli tự giữ phiên đăng nhập.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUSE = shutil.which("muse-cli") or "muse-cli"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
RULE = ("Create exactly ONE image, 16:9 landscape, 1920x1080. No text, no letters, no numbers, no logos, "
        "no watermark, no signature. Reply with only the image.")


def sections(text: str) -> dict[str, str]:
    """{ai_NN.png: khối prompt của mục ấy}."""
    out = {}
    for m in re.finditer(r"(?ms)^#+[ \t]+(ai_\d+\.png)\b[^\n]*\n(.*?)(?=^#+[ \t]+|\Z)", text):
        out[m.group(1)] = m.group(2).strip()
    return out


def common_style(text: str) -> str:
    """Mục 'Phong cách chung' / 'Hồ sơ chung' (nếu có) áp cho mọi ảnh."""
    m = re.search(r"(?ms)^#+[ \t]+(?:Phong cách chung|Hồ sơ chung)[^\n]*\n(.*?)(?=^#+[ \t]+|\Z)", text)
    return m.group(1).strip() if m else ""


def prompt_for(block: str, style: str) -> str:
    """Ưu tiên dòng '- Prompt…:' (tiếng Anh); không có thì dùng cả khối."""
    m = re.search(r"(?m)^-?\s*Prompt[^:]*:\s*(.+)$", block)
    body = m.group(1).strip() if m else block
    return f"{RULE}\n\nStyle: {style}\n\nImage: {body}" if style else f"{RULE}\n\nImage: {body}"


def muse(*args: str, timeout: int = 120) -> str:
    r = subprocess.run([MUSE, *args], capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=timeout)
    if r.returncode:
        raise RuntimeError(f"muse-cli {args[0]} lỗi: {(r.stderr or r.stdout)[-400:]}")
    return r.stdout


def thread_for(topic: str, od: Path) -> str:
    f = od / "muse_thread.txt"
    if f.is_file() and f.read_text(encoding="utf-8").strip():
        return f.read_text(encoding="utf-8").strip()
    out = muse("session-start", "--title", f"Ảnh Long {topic}")
    m = re.search(r'"(?:thread_id|id|session_id)"\s*:\s*"([^"]+)"', out)
    if not m:
        raise SystemExit(f"không đọc được thread id từ session-start: {out[:200]}")
    f.write_text(m.group(1), encoding="utf-8")
    return m.group(1)


def thread_images(thread: str) -> list[dict]:
    """Ảnh agent đã tạo trong side chat (muse-cli files), cũ -> mới."""
    try:
        rows = json.loads(muse("files", "--thread", thread, "--limit", "50"))
    except (RuntimeError, json.JSONDecodeError):
        return []
    return sorted((r for r in rows if r.get("kind") == "image"), key=lambda r: r.get("seq", 0))


def wait_new_image(thread: str, seen: set, wait: int, poll: int = 8) -> dict | None:
    """Dò `files` mỗi `poll` giây tới khi có ảnh mới (seq chưa thấy). muse-cli `send --wait` không nhận ra
    câu trả lời dạng ảnh (delta.presentation) nên chờ hết giờ dù ảnh có sau ~30 s (#539, 27/11/2026)."""
    t0 = time.time()
    while time.time() - t0 < wait:
        new = [r for r in thread_images(thread) if r.get("seq") not in seen]
        if new:
            return new[-1]
        time.sleep(poll)
    return None


def newest_image(d: Path) -> Path | None:
    files = [p for p in d.iterdir() if p.suffix.lower() in IMG_EXT]
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def last_assistant_id(thread: str) -> str | None:
    try:
        rows = json.loads(muse("history", "--thread", thread, "--limit", "3"))
    except (RuntimeError, json.JSONDecodeError):
        return None
    ids = [r.get("message_id") for r in rows if r.get("role") == "assistant"]
    return ids[-1] if ids else None


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from factory.console import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("topic")
    ap.add_argument("--only", help="ai_03,ai_07 …")
    ap.add_argument("--wait", type=int, default=600, help="giây chờ tối đa mỗi ảnh (thường ~30 s)")
    ap.add_argument("--no-import", action="store_true")
    a = ap.parse_args()
    text = (ROOT / "data" / "long" / a.topic / "ai_prompts.md").read_text(encoding="utf-8")
    secs, style = sections(text), common_style(text)
    want = [n if n.endswith(".png") else n + ".png" for n in (a.only.split(",") if a.only else secs)]
    out = ROOT / "motion" / "hf" / "assets" / "long" / a.topic / "img" / "ai"
    od = ROOT / "output" / "long" / a.topic
    out.mkdir(parents=True, exist_ok=True)
    od.mkdir(parents=True, exist_ok=True)
    pend_f = od / "muse_pending.json"
    pending = json.loads(pend_f.read_text(encoding="utf-8")) if pend_f.is_file() else {}
    thread = thread_for(a.topic, od)
    failed = []
    for name in want:
        dest = out / name
        if dest.is_file():
            continue
        if name not in secs:
            print(f"!! {name}: không có trong ai_prompts.md")
            failed.append(name)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            if pending.get(name):   # lần trước hết giờ: tải theo message id, không gửi lại
                try:
                    muse("download", pending[name], "--thread", thread, "-o", str(t), timeout=300)
                except RuntimeError as e:
                    print(f"  {name}: tải lại theo id lỗi ({e}); gửi lại prompt")
            if not newest_image(t):
                t0 = time.time()
                seen = {r.get("seq") for r in thread_images(thread)}
                print(f"gửi {name}…", flush=True)
                # --wait 0 (fire-and-forget) làm tin bị rơi; giữ kết nối ~60 s cho tin vào chat, rồi dò files.
                muse("send", "--thread", thread, "--wait", "60", prompt_for(secs[name], style), timeout=200)
                got = wait_new_image(thread, seen, a.wait)
                if got:
                    muse("download", got["message_id"], "--thread", thread, "-o", str(t), timeout=300)
                print(f"  {name}: {time.time() - t0:.0f}s", flush=True)
            img = newest_image(t)
            if not img:
                mid = last_assistant_id(thread)
                if mid:
                    pending[name] = mid
                    pend_f.write_text(json.dumps(pending, indent=1), encoding="utf-8")
                print(f"!! {name}: chưa có ảnh trong {a.wait}s (đã ghi id để lần sau tải lại)")
                failed.append(name)
                continue
            shutil.copyfile(img, dest)
            pending.pop(name, None)
            pend_f.write_text(json.dumps(pending, indent=1), encoding="utf-8")
            print(f"  {name} <- {img.name}", flush=True)
    if failed:
        print(f"!! thiếu {len(failed)}: {', '.join(failed)} — chạy lại lệnh để lấy tiếp")
    if not a.no_import:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "ai_img_import.py"), a.topic])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
