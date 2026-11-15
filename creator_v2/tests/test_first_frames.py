import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

from motion import first_frames
from motion.long import build_long

needs_ffmpeg = pytest.mark.skipif(not (Path(first_frames.FFMPEG).exists() or shutil.which(first_frames.FFMPEG)),
                                  reason="cần ffmpeg để tạo và đo video")


def make_video(tmp_path, kinds):
    rng = np.random.default_rng(416)
    for i, kind in enumerate(kinds):
        pixels = np.clip(128 + rng.normal(0, 2, (240, 320)), 0, 255).astype("uint8")
        image = Image.fromarray(pixels, "L").convert("RGB")
        draw = ImageDraw.Draw(image)
        draw.text((10, 5), "HUD", fill="white")
        if kind == "detail":
            draw.ellipse((80, 45, 240, 220), fill=(65, 65, 65))
            draw.ellipse((110, 85, 125, 100), fill="white")
            draw.ellipse((190, 85, 205, 100), fill="white")
            draw.line((120, 155, 200, 155), fill="white", width=4)
        image.save(tmp_path / f"frame{i}.png")
    video = tmp_path / "sample.mp4"
    subprocess.run([first_frames.FFMPEG, "-v", "error", "-y", "-framerate", "1", "-i",
                    str(tmp_path / "frame%d.png"), "-r", "10", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)], check=True)
    return video


@needs_ffmpeg
@pytest.mark.parametrize("kinds,expected", [(["flat"] * 3, True), (["detail"] * 3, False),
                                             (["flat", "detail", "detail"], False)])
def test_video_frames(tmp_path, kinds, expected):
    video = make_video(tmp_path, kinds)
    measurements = first_frames.measure(video, [.3, 1.0, 2.0])
    assert first_frames.flat(measurements[0]) == (kinds[0] == "flat")
    assert bool(first_frames.problems(video, [.3, 1.0, 2.0])) == expected


def test_legacy_skips_frame_check(monkeypatch):
    monkeypatch.setattr(build_long, "is_legacy_topic", lambda topic: True)
    def fail(*args):
        raise AssertionError("legacy không được đo")
    monkeypatch.setattr(first_frames, "problems", fail)
    build_long._check_first_frames("legacy", Path("missing.mp4"))


def test_new_long_blocks_bad_frames(monkeypatch):
    monkeypatch.setattr(build_long, "is_legacy_topic", lambda topic: False)
    monkeypatch.setattr(first_frames, "problems", lambda video, times: ["std=1, edge=0"])
    with pytest.raises(SystemExit, match="LỖI khung đầu.*std=1"):
        build_long._check_first_frames("new", Path("sample.mp4"))
