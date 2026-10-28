#!/usr/bin/env python3
"""Hộp bao chủ thể [x, y, w, h] trong 0..1 cho preset pan_focus / highlight.

Ưu tiên mask Vision (tools/fgmask.swift, cùng đường hf_depth dùng cho depth).
Không có chủ thể thì thử saliency (tools/saliency_box.swift).
Không chắc — mask rỗng, quá nhỏ, quá to, chạm từ ba mép — thì trả None.
Khi None, bộ chọn không được gán pan_focus hoặc highlight.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SAL_SRC = ROOT / "tools" / "saliency_box.swift"
SAL_BIN = ROOT / "chunks_cache" / "bin" / "saliency_box"
CACHE = ROOT / "chunks_cache" / "subject"


def bbox_from_mask(mask: Image.Image) -> dict | None:
    """Hộp từ mask xám. None khi không đủ chắc để làm focus."""
    arr = np.asarray(mask.convert("L"))
    on = arr > 40
    ys, xs = np.where(on)
    if xs.size < 32:
        return None
    h, w = arr.shape
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    cover = float(on.mean())
    if not (0.04 <= cover <= 0.72):
        return None
    if bw < w * 0.08 or bh < h * 0.08 or (bw > w * 0.92 and bh > h * 0.92):
        return None
    edges = int(x0 <= 2) + int(y0 <= 2) + int(x1 >= w - 3) + int(y1 >= h - 3)
    if edges >= 3:
        return None
    return {
        "focus": [round(x0 / w, 4), round(y0 / h, 4), round(bw / w, 4), round(bh / h, 4)],
        "source": "vision",
        "cover": round(cover, 4),
    }


def _saliency_bin() -> Path:
    if not SAL_BIN.exists() or SAL_BIN.stat().st_mtime < SAL_SRC.stat().st_mtime:
        SAL_BIN.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["swiftc", "-O", str(SAL_SRC), "-o", str(SAL_BIN)], check=True, capture_output=True)
    return SAL_BIN


def _box_ok(x: float, y: float, w: float, h: float) -> bool:
    if not (0.03 <= w * h <= 0.70 and w >= 0.08 and h >= 0.08):
        return False
    if w > 0.92 and h > 0.92:
        return False
    edges = int(x <= 0.01) + int(y <= 0.01) + int(x + w >= 0.99) + int(y + h >= 0.99)
    return edges < 3 and x >= 0 and y >= 0 and x + w <= 1.001 and y + h <= 1.001


def saliency_box(image: Path) -> dict | None:
    res = subprocess.run([str(_saliency_bin()), str(image)], capture_output=True, text=True)
    if res.returncode != 0:
        return None
    parts = (res.stdout or "").split()
    if len(parts) != 4:
        return None
    try:
        x, y, w, h = (float(v) for v in parts)
    except ValueError:
        return None
    if not _box_ok(x, y, w, h):
        return None
    return {"focus": [round(x, 4), round(y, 4), round(w, 4), round(h, 4)], "source": "saliency"}


def subject_box(image: Path) -> dict | None:
    image = Path(image)
    key = hashlib.sha1(b"v1\n" + image.read_bytes()).hexdigest()[:16]
    cached = CACHE / f"{key}.json"
    if cached.exists():
        data = json.loads(cached.read_text(encoding="utf-8"))
        return data or None
    CACHE.mkdir(parents=True, exist_ok=True)
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import hf_depth  # noqa: PLC0415
    mask_path = CACHE / f"{key}_mask.png"
    res = subprocess.run([str(hf_depth._fgmask_bin()), str(image), str(mask_path)], capture_output=True, text=True)
    found = None
    if res.returncode == 0 and mask_path.exists():
        found = bbox_from_mask(Image.open(mask_path))
    if found is None:
        found = saliency_box(image)
    cached.write_text(json.dumps(found, ensure_ascii=False) if found else "null", encoding="utf-8")
    return found


def main(argv: list[str] | None = None) -> int:
    import sys
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: subject_box.py <ảnh>...", file=sys.stderr)
        return 64
    for raw in args:
        box = subject_box(Path(raw))
        print(json.dumps({"path": raw, **(box or {"focus": None, "source": "none"})}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
