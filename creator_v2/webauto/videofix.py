"""Remove the fixed Gemini sparkle from downloaded Flow videos."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .imagefix import _crop_size, fixed_mark_box


def _probe(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "json", str(path)],
        check=True, capture_output=True, text=True)
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise ValueError(f"không tìm thấy luồng video: {path}")
    return int(streams[0]["width"]), int(streams[0]["height"])


def strip_video(path, mode="crop"):
    """Crop/repair Flow's lower-right sparkle; audio is stream-copied."""
    if mode not in ("crop", "delogo", "off"):
        raise ValueError("mode phải là crop, delogo hoặc off")
    path = Path(path)
    if mode == "off":
        return path
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("cần ffmpeg và ffprobe trong PATH để xử lý video")
    w, h = _probe(path)
    x0, y0, x1, y1 = fixed_mark_box(w, h)
    if mode == "crop":
        # Cut right AND bottom: on the 1080p download (06/11) the sparkle sits ~180 px in from both
        # edges, ~70 px wide, outside this box; only the two-sided cut (1586x892 → rescale) drops it.
        cw, ch = _crop_size(w, h, (x0, y0, x1, y1), either=False)
        vf = f"crop={cw}:{ch}:0:0,scale={w}:{h}:flags=lanczos"
    else:
        vf = f"delogo=x={x0}:y={y0}:w={x1-x0}:h={y1-y0}:show=0"
    with tempfile.NamedTemporaryFile(suffix=path.suffix, dir=path.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
                        "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-c:a", "copy", "-movflags", "+faststart", str(tmp_path)], check=True)
        tmp_path.replace(path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return path


def upscale_video_1080p(path, target_res=(1920, 1080)):
    """Upscale video to 1080p (default 1920x1080 for 16:9, or 1080x1920 for 9:16) using ffmpeg lanczos.

    Returns (path, was_upscaled: bool).
    """
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("cần ffmpeg và ffprobe trong PATH để xử lý video")
    path = Path(path)
    w, h = _probe(path)
    if w >= 1920 or h >= 1920 or (w == 1080 and h == 1920) or (w == 1920 and h == 1080):
        return path, False

    tw, th = target_res
    if h > w and tw > th:
        tw, th = th, tw  # vertical: 1080x1920
    elif w == h:
        tw, th = 1080, 1080

    scale_filter = f"scale={tw}:{th}:flags=lanczos"
    with tempfile.NamedTemporaryFile(suffix=path.suffix, dir=path.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
                        "-vf", scale_filter, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-c:a", "copy", "-movflags", "+faststart", str(tmp_path)], check=True)
        tmp_path.replace(path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return path, True
