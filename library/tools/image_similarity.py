"""Small, shared perceptual image comparison for adjacent scene selection."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def near_duplicate(path_a: str | Path, path_b: str | Path) -> bool:
    """Compare grayscale 64x36 thumbnails; mean absolute pixel difference < 18."""
    try:
        with Image.open(path_a) as a, Image.open(path_b) as b:
            aa = np.asarray(a.convert("L").resize((64, 36)), dtype=np.int16)
            bb = np.asarray(b.convert("L").resize((64, 36)), dtype=np.int16)
        return float(np.abs(aa - bb).mean()) < 18.0
    except (OSError, ValueError):
        return False
