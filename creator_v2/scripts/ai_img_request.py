"""Nhờ bot tạo ảnh (Grok Bot, routine "CLI Trigger") tạo các ảnh AI trong ai_prompts.md, chờ ảnh về rồi chép vào engine (26/10/2026).

    python scripts/ai_img_request.py <topic> [--wait 900]

- Đọc `GROKBOT_WEBHOOK_URL` / `GROKBOT_WEBHOOK_KEY`: lấy từ biến môi trường, nếu không có thì đọc registry cấp User (Windows).
  Không in giá trị ra màn hình, không ghi vào repo. Hướng dẫn: `docs/tools/grokbot-webhook.md`.
- POST tới webhook: `data/long/<topic>/ai_prompts.md` -> ảnh lưu vào `motion/hf/assets/long/<topic>/img/ai/`.
- Chờ đủ số ảnh `## ai_NN.png` khai trong prompt, rồi chạy `scripts/ai_img_import.py`.
- Bot mất khoảng 2 phút cho mỗi ảnh. Ảnh về vẫn phải được soát bằng mắt trước khi render.
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
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v and sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                v = winreg.QueryValueEx(k, name)[0]
        except OSError:
            v = None
    if not v:
        raise SystemExit(f"thiếu {name} (xem docs/tools/grokbot-webhook.md)")
    return v


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from factory.console import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--wait", type=int, default=900, help="giây chờ tối đa")
    ap.add_argument("--no-send", action="store_true", help="chỉ chờ ảnh đã yêu cầu và chép về")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--images-only", action="store_true")
    mode.add_argument("--videos-only", action="store_true")
    ap.add_argument("--faces", action="store_true",
                    help="nhân vật VÍ DỤ GIẢ ĐỊNH (người hư cấu, CK 27/10/2026): được vẽ rõ mặt, giữ đúng hồ sơ nhân vật trong prompt_file")
    a = ap.parse_args()
    prompts = ROOT / "data" / "long" / a.topic / "ai_prompts.md"
    out = ROOT / "motion" / "hf" / "assets" / "long" / a.topic / "img" / "ai"
    share_root = Path(os.environ.get("GROKBOT_SHARE_DIR") or (Path(os.environ.get("USERPROFILE") or Path.home()) / "Downloads" / "grokbot"))
    share = (share_root / a.topic).resolve()
    share_out = share / "out"
    text = prompts.read_text(encoding="utf-8")
    # Tiêu đề mục có thể có đuôi mô tả: "## ai_01.png — CH00: …" (hoa-than, 06/11).
    images = [] if a.videos_only else re.findall(r"^#+[ \t]+(ai_\d+\.png)\b", text, re.M)
    videos = [] if a.images_only else re.findall(r"^#+[ \t]+(vid_\d+\.mp4)\b", text, re.M)
    if not images and not videos:
        raise SystemExit(f"{prompts}: không có mục ảnh hoặc clip được chọn")
    video_out = ROOT / "output" / "long" / a.topic / "broll"
    share_out.mkdir(parents=True, exist_ok=True)
    shared_prompts = share / "ai_prompts.md"
    shutil.copy2(prompts, shared_prompts)
    if images:
        out.mkdir(parents=True, exist_ok=True)

    def local_name(name):
        """vid_NN.mp4 -> 9000NN.mp4: build_long chỉ nhận id b-roll toàn chữ số (regex broll/(\\d+)...)."""
        if name.startswith("vid_"):
            num = int(re.search(r"\d+", name).group())   # Python 3.11: f-string không chứa được dấu \
            return f"{900000 + num}.mp4"
        return name

    def missing(names, dest):
        return [n for n in names if not (dest / local_name(n)).is_file() and not (share_out / n).is_file()]

    requests = [
        ("generate_images", missing(images, out),
         "Mỗi ảnh 16:9 cỡ 1920x1080, phong cách tranh minh hoạ, không chữ, không số, không logo, "
         + ("nhân vật là người hư cấu: vẽ rõ mặt, mọi ảnh giữ cùng một gương mặt theo 'Hồ sơ nhân vật' trong file. "
            if a.faces else "không thấy rõ mặt người (người chỉ vẽ nghiêng quay đi hoặc từ phía sau). ")),
        ("generate_videos", missing(videos, video_out), "Tạo clip theo mô tả trong prompt_file. "),
    ]
    if not a.no_send:
        for task, names, instruction in requests:
            if not names:
                continue
            body = json.dumps({
                "task": task, "prompt_file": str(shared_prompts), "output_dir": str(share_out),
                "instructions": f"Đọc prompt_file, tạo đúng các file còn thiếu: {', '.join(names)}. "
                                + instruction + "Lưu đúng tên file vào output_dir.",
            }, ensure_ascii=False).encode("utf-8")
            key = env("GROKBOT_WEBHOOK_KEY")
            req = urllib.request.Request(env("GROKBOT_WEBHOOK_URL"), data=body, method="POST", headers={
                "Content-Type": "application/json; charset=utf-8", "Authorization": f"Bearer {key}", "X-Webhook-Secret": key})
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    print(f"đã gửi bot: HTTP {response.status}, {len(names)} file ({task})", flush=True)
            except Exception:
                print("không gửi được webhook; kiểm tra cấu hình và kết nối", file=sys.stderr)
                return 1
    if any(not (out / n).is_file() for n in images) or any(not (video_out / local_name(n)).is_file() for n in videos):
        t0 = time.time()
        while time.time() - t0 < a.wait:
            left = missing(images, out) + missing(videos, video_out)
            if not left:
                break
            time.sleep(15)
        left = missing(images, out) + missing(videos, video_out)
        if left:
            print(f"hết {a.wait}s, còn thiếu: {left}")
            return 1
        time.sleep(5)
    for name in images:
        if not (out / name).exists():
            shutil.copy2(share_out / name, out / name)
    if videos:
        from webauto.videofix import strip_video
        video_out.mkdir(parents=True, exist_ok=True)
        for name in videos:
            dest = video_out / local_name(name)
            if dest.is_file():
                continue
            with tempfile.TemporaryDirectory(dir=video_out) as tmp:
                staged = Path(tmp) / dest.name
                shutil.copy2(share_out / name, staged)
                strip_video(staged, "crop")
                metadata = {"ai_generated": True, "credit": False, "source_name": name}
                (video_out / (dest.stem + ".json")).write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                staged.replace(dest)
    if images:
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "ai_img_import.py"), a.topic]).returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
