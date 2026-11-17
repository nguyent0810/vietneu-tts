"""Bắt cú giật một khung trong cảnh (QA sau render, mọi engine).

Lỗi Quét nhà (NIj0goKjNtc, 17/11/2026): hai tween cùng giành `scale` của camera -> ảnh trượt rồi nhảy
trong đúng một khung. Contact sheet (khung tĩnh) không thấy. Ở đây đo độ khác nhau giữa các khung liên
tiếp trên ảnh xám thu nhỏ: một khung khác hẳn trong khi khung trước và sau gần như đứng yên = giật.
Chuyển cảnh (seam) và cắt cảnh hợp lệ truyền vào `cuts` để bỏ qua.

    python tools/frame_jumps.py video.mp4 [--crop y0:y1] [--cuts 5.4,9.27]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

W, H = 72, 128          # khung xám thu nhỏ (9:16); khổ ngang thì đảo
SPIKE_MARGIN = 8.0      # khung giật hơn khung kề bên ít nhất bấy nhiêu (độ khác trung bình 0..255)
SPIKE_RATIO = 2.0       # và gấp bao nhiêu lần khung kề bên (camera đang trượt thì khung kề đã ~7-12)
CUT_BEFORE, CUT_AFTER = 0.4, 0.25   # bỏ qua quanh mốc cắt cảnh: seam ra bắt đầu trước mốc 0,3 s
# Hiệu chỉnh 17/11 trên Quét nhà: 5 cú giật thật (20-53 so với kề 7-12) đều bắt, 0 báo nhầm ngoài seam.


def frame_diffs(mp4: str, crop: tuple[float, float] | None = None, fps: float = 30.0) -> list[float]:
    """Độ khác trung bình tuyệt đối giữa khung i và i-1 (phần tử 0 = 0)."""
    import numpy as np  # noqa: PLC0415
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "json", mp4], capture_output=True, text=True, check=True)
    st = json.loads(probe.stdout)["streams"][0]
    w, h = (W, H) if st["height"] >= st["width"] else (H, W)
    vf = [f"fps={fps}"]
    if crop:
        y0, y1 = crop
        vf.append(f"crop=iw:ih*{y1 - y0:.4f}:0:ih*{y0:.4f}")
    vf.append(f"scale={w}:{h},format=gray")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", ",".join(vf), "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    return [0.0, *d.tolist()]


def spikes(diffs: list[float], fps: float = 30.0, cuts: list[float] | None = None,
           margin: float = SPIKE_MARGIN, ratio: float = SPIKE_RATIO) -> list[float]:
    """Giây của các khung giật: vượt cả khung trước lẫn khung sau `margin` đơn vị và gấp `ratio` lần."""
    cuts = cuts or []
    out = []
    for i in range(1, len(diffs) - 1):
        d, nb = diffs[i], max(diffs[i - 1], diffs[i + 1], 0.5)
        if d - nb < margin or d < ratio * nb:
            continue
        t = i / fps
        if any(c - CUT_BEFORE <= t <= c + CUT_AFTER for c in cuts):
            continue
        out.append(round(t, 3))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mp4")
    ap.add_argument("--crop", help="vùng dọc tỉ lệ y0:y1 (vd 0.06:0.75 bỏ phụ đề short)")
    ap.add_argument("--cuts", default="", help="mốc cắt cảnh hợp lệ (giây, phẩy)")
    a = ap.parse_args(argv)
    crop = tuple(float(x) for x in a.crop.split(":")) if a.crop else None
    cuts = [float(x) for x in a.cuts.split(",") if x.strip()]
    found = spikes(frame_diffs(a.mp4, crop), cuts=cuts)
    print(json.dumps({"jumps": found}, ensure_ascii=False))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
