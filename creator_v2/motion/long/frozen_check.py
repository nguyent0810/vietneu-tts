"""So sánh ba khung hình thu nhỏ để phát hiện video render đứng hình."""
from __future__ import annotations

import math
import subprocess

from PIL import Image, ImageChops, ImageStat

WIDTH, HEIGHT = 160, 90


def is_frozen(frames, threshold=1.0):
    """True khi mọi cặp khung chỉ khác trung bình không quá một mức màu."""
    frames = [frame.convert("RGB").resize((WIDTH, HEIGHT)) for frame in frames]
    if len(frames) != 3:
        raise ValueError("cần đúng ba khung hình")
    return all(sum(ImageStat.Stat(ImageChops.difference(frames[i], frames[j])).mean) / 3 <= threshold
               for i, j in ((0, 1), (0, 2), (1, 2)))


def check(video, ffmpeg, duration):
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("thời lượng không hợp lệ")
    frames = []
    for fraction in (0.1, 0.5, 0.9):
        result = subprocess.run([str(ffmpeg), "-v", "error", "-ss", str(duration * fraction), "-i", str(video),
                                 "-frames:v", "1", "-vf", f"scale={WIDTH}:{HEIGHT}", "-f", "rawvideo",
                                 "-pix_fmt", "rgb24", "pipe:1"], capture_output=True, check=True)
        if len(result.stdout) != WIDTH * HEIGHT * 3:
            raise ValueError(f"không trích được khung {fraction:.0%}")
        frames.append(Image.frombytes("RGB", (WIDTH, HEIGHT), result.stdout))
    return is_frozen(frames)
