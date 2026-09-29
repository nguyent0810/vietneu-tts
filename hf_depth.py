"""Tách một ảnh thành hai lớp cho bố cục 2.5D (parallax) của video dài.

Chủ thể (người, tượng, con vật...) được cắt bằng Vision của macOS
(tools/fgmask.swift -> chunks_cache/bin/fgmask, chạy cục bộ, không tải model).
Lỗ chủ thể để lại trên nền được lấp bằng nội suy nhiều tầng (push-pull): mờ
dần từ viền vào trong -- không đẹp như inpainting thật, nhưng nền sẽ bị làm mờ
và trôi chậm hơn chủ thể, lớp chủ thể che gần hết chỗ lấp.

    split_depth(ảnh) -> (nền.jpg, chủ_thể.png, tỉ lệ diện tích) | None
None khi không tìm được chủ thể, hoặc chủ thể quá nhỏ / quá to để ra chiều sâu.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).parent
FGMASK_SRC = ROOT / "tools" / "fgmask.swift"
FGMASK_BIN = ROOT / "chunks_cache" / "bin" / "fgmask"
CACHE = ROOT / "chunks_cache" / "depth"
MIN_COVER, MAX_COVER = 0.06, 0.62   # ngoài khoảng này tách lớp không ra chiều sâu
MAX_W = 2400


def _fgmask_bin() -> Path:
    if not FGMASK_BIN.exists() or FGMASK_BIN.stat().st_mtime < FGMASK_SRC.stat().st_mtime:
        FGMASK_BIN.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["swiftc", "-O", str(FGMASK_SRC), "-o", str(FGMASK_BIN)], check=True, capture_output=True)
    return FGMASK_BIN


def _fill_hole(rgb: np.ndarray, hole: np.ndarray, scale: int = 4) -> np.ndarray:
    """Lấp vùng `hole` bằng trung bình có trọng số ở các tầng mờ tăng dần.
    Tính ở 1/4 độ phân giải rồi phóng lại: chỗ lấp vốn mờ, còn làm mờ bán kính
    lớn trên ảnh 2400px mất gần 2 phút mỗi ảnh."""
    h, w = hole.shape
    sw, sh = max(8, w // scale), max(8, h // scale)
    small = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((sw, sh), Image.BILINEAR)).astype(np.float32)
    shole = np.asarray(Image.fromarray(hole.astype(np.uint8) * 255).resize((sw, sh), Image.BILINEAR)) > 20
    known = (~shole).astype(np.float32)
    fill = small.copy()
    todo = shole.copy()
    for r in (2, 4, 8, 16, 32, 64, 128, 256):
        num = np.stack([gaussian_filter(small[..., c] * known, r) for c in range(3)], -1)
        den = gaussian_filter(known, r)
        ok = todo & (den > 0.005)
        fill[ok] = num[ok] / den[ok][:, None]
        todo &= ~ok
        if not todo.any():
            break
    # Chủ thể to chạm mép ảnh (tượng Phật ngồi kín đáy khung): giữa lỗ cách nền
    # quá xa, không tầng nào với tới -> lấp bằng màu trung bình của nền, không
    # để nguyên chủ thể gốc trên lớp nền.
    if todo.any():
        fill[todo] = small[~shole].mean(0) if (~shole).any() else 0
    big = np.asarray(Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32)
    out = rgb.copy()
    out[hole] = big[hole]
    return out


def split_depth(image: Path) -> tuple[Path, Path, float] | None:
    image = Path(image)
    key = hashlib.sha1(image.read_bytes()).hexdigest()[:16]
    bg, fg, cov_f = CACHE / f"{key}_bg.jpg", CACHE / f"{key}_fg.png", CACHE / f"{key}.cover"
    if cov_f.exists():
        cov = float(cov_f.read_text())
        return (bg, fg, cov) if cov > 0 and bg.exists() and fg.exists() else None
    CACHE.mkdir(parents=True, exist_ok=True)
    src = Image.open(image).convert("RGB")
    if src.width > MAX_W:
        src = src.resize((MAX_W, round(src.height * MAX_W / src.width)), Image.LANCZOS)
    tmp_in, tmp_mask = CACHE / f"{key}_in.jpg", CACHE / f"{key}_mask.png"
    src.save(tmp_in, quality=92)
    res = subprocess.run([str(_fgmask_bin()), str(tmp_in), str(tmp_mask)], capture_output=True, text=True)
    tmp_in.unlink(missing_ok=True)
    cov = float((res.stdout or "0").strip() or 0) if res.returncode in (0, 2) else 0.0
    if res.returncode != 0 or not (MIN_COVER <= cov <= MAX_COVER):
        cov_f.write_text("0")
        tmp_mask.unlink(missing_ok=True)
        return None
    mask = Image.open(tmp_mask).convert("L").resize(src.size, Image.LANCZOS)
    tmp_mask.unlink(missing_ok=True)
    rgb = np.asarray(src).astype(np.float32)
    # Lỗ trên nền lấn ra ngoài chủ thể một chút: viền mờ của chủ thể không được
    # để lại "bóng ma" trên lớp nền khi hai lớp trôi lệch nhau.
    hole = np.asarray(mask.filter(ImageFilter.MaxFilter(21))) > 40
    plate = _fill_hole(rgb, hole)
    Image.fromarray(np.clip(plate, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)).save(bg, quality=90)
    alpha = mask.filter(ImageFilter.GaussianBlur(1.2))
    cut = src.copy(); cut.putalpha(alpha)
    cut.save(fg, optimize=True)
    cov_f.write_text(f"{cov:.4f}")
    return bg, fg, cov


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        print(p, split_depth(Path(p)))
