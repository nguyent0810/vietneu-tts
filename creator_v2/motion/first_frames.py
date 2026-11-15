"""Kiểm hình thật trong ba giây đầu của video Long và Short."""
from __future__ import annotations

import io
import os
import shutil
import subprocess

import numpy as np
from PIL import Image

_VENDOR = r"C:\Tools\Youtuber\video-editor\vendor\ffmpeg"
_FF_DIR = os.environ.get("FFMPEG_DIR") or (_VENDOR if os.path.isdir(_VENDOR) else None)
FFMPEG = os.path.join(_FF_DIR, "ffmpeg.exe") if _FF_DIR else (shutil.which("ffmpeg") or "ffmpeg")
STD_MIN = 8.0
EDGE_MIN = 0.025
EDGE_THRESHOLD = 20


def measure(video_path, times) -> list[dict]:
    """Đo vùng giữa: bỏ HUD, phụ đề và lề; edge là chênh sáng láng giềng."""
    results = []
    for timestamp in times:
        r = subprocess.run([FFMPEG, "-v", "error", "-ss", str(timestamp), "-i", str(video_path),
                            "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True, check=True)
        if not r.stdout:
            raise ValueError(f"không trích được khung tại {timestamp}s")
        with Image.open(io.BytesIO(r.stdout)) as image:
            image = image.convert("L")
            w, h = image.size
            image = image.crop((round(w * .05), round(h * .12), round(w * .95), round(h * .78)))
            image.thumbnail((320, 320), Image.Resampling.LANCZOS)
            a = np.asarray(image, dtype=np.float32)
        if min(a.shape) < 2:
            raise ValueError("khung quá nhỏ để đo")
        dx = np.abs(a[:-1, 1:] - a[:-1, :-1])
        dy = np.abs(a[1:, :-1] - a[:-1, :-1])
        results.append({"time": float(timestamp), "std": float(a.std()),
                        "edge": float(np.mean(np.maximum(dx, dy) > EDGE_THRESHOLD))})
    return results


def flat(m) -> bool:
    return m["std"] < STD_MIN and m["edge"] < EDGE_MIN


def problems(video, times) -> list[str]:
    measurements = measure(video, times)
    if not measurements:
        raise ValueError("cần ít nhất một mốc đo khung đầu")
    if all(flat(m) for m in measurements):
        values = "; ".join(f"{m['time']:.1f}s: std={m['std']:.2f}, edge={m['edge']:.4f}" for m in measurements)
        return [f"ba khung đầu đều phẳng ({values}); kiểm tra focus ảnh dọc, cảnh đầu phải là hình mạnh nhất"]
    return []
