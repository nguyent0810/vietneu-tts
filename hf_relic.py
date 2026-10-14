"""Chuẩn bị ảnh hiện vật cho cảnh `relic` (2.5D) của video dài.

Từ một ảnh bảo tàng (nền phông trơn), dựng bốn thứ:
  bg.jpg      nền đã lấp chỗ hiện vật (trôi chậm, mờ nhẹ)
  fg.png      hiện vật cắt rời (RGBA, trôi nhanh hơn nền -> chiều sâu)
  sketch.png  nét phác hiện vật (chỉ kênh alpha; màu do CSS tô qua mask-image)
  outline     đường viền ngoài, toạ độ chuẩn hoá 0..1 (SVG tự vẽ nét)

Tách chủ thể bằng Vision của macOS (hf_depth / tools/fgmask.swift) -- chạy cục bộ,
không tải model. Ảnh không tách được chủ thể -> None (dùng cảnh museum thường).

    prepare(ảnh) -> {"bg", "fg", "sketch", "outline", "w", "h"} | None
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

import hf_depth

CACHE = Path(__file__).parent / "chunks_cache" / "relic"
MAX_W = 2000
MIN_COVER, MAX_COVER = 0.04, 0.92
VERSION = "3"


def _mask(src: Image.Image, key: str) -> np.ndarray | None:
    tmp_in, tmp_mask = CACHE / f"{key}_in.jpg", CACHE / f"{key}_mask.png"
    src.save(tmp_in, quality=92)
    res = subprocess.run([str(hf_depth._fgmask_bin()), str(tmp_in), str(tmp_mask)], capture_output=True, text=True)
    tmp_in.unlink(missing_ok=True)
    cov = float((res.stdout or "0").strip() or 0) if res.returncode in (0, 2) else 0.0
    if res.returncode != 0 or not (MIN_COVER <= cov <= MAX_COVER) or not tmp_mask.exists():
        tmp_mask.unlink(missing_ok=True)
        return None
    m = np.asarray(Image.open(tmp_mask).convert("L").resize(src.size, Image.LANCZOS)).astype(np.float32) / 255
    tmp_mask.unlink(missing_ok=True)
    return m


def _parts(binary: np.ndarray, min_frac: float = .2) -> list[np.ndarray]:
    """Các mảng hiện vật (đã lấp lỗ), giữ mảng >= min_frac của mảng lớn nhất -- ảnh hai mặt đồng xu có hai mảng."""
    lab, n = ndimage.label(binary)
    if n == 0:
        return []
    sizes = ndimage.sum(binary, lab, range(1, n + 1))
    big = max(sizes)
    return [ndimage.binary_fill_holes(lab == i + 1) for i in range(n) if sizes[i] >= min_frac * big]


def trace(binary: np.ndarray) -> list[tuple[int, int]]:
    """Đường biên ngoài của vùng True (dò lân cận Moore, dừng khi về điểm đầu theo cùng hướng)."""
    h, w = binary.shape
    pad = np.zeros((h + 2, w + 2), bool)
    pad[1:-1, 1:-1] = binary
    ys, xs = np.nonzero(pad)
    if not len(ys):
        return []
    k = np.lexsort((xs, ys))[0]
    start = (int(xs[k]), int(ys[k]))
    # 8 hướng theo chiều kim đồng hồ, bắt đầu từ tây
    dirs = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]
    pts, cur, back = [start], start, 0      # điểm vào từ phía tây (ô trống)
    for _ in range(8 * (h + w) * 4):
        found = False
        for i in range(8):
            d = (back + 1 + i) % 8
            nx, ny = cur[0] + dirs[d][0], cur[1] + dirs[d][1]
            if pad[ny, nx]:
                back = (d + 4) % 8
                cur = (nx, ny)
                found = True
                break
        if not found or cur == start:
            break
        pts.append(cur)
    return [(x - 1, y - 1) for x, y in pts]


def rdp(pts: list[tuple[float, float]], eps: float) -> list[tuple[float, float]]:
    """Douglas–Peucker (lặp, không đệ quy -- biên dài vài nghìn điểm)."""
    if len(pts) < 3:
        return pts
    a = np.asarray(pts, float)
    keep = np.zeros(len(a), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(a) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        p, q = a[i], a[j]
        seg = q - p
        n = np.hypot(*seg) or 1.0
        d = np.abs(seg[0] * (a[i + 1:j, 1] - p[1]) - seg[1] * (a[i + 1:j, 0] - p[0])) / n
        k = int(np.argmax(d))
        if d[k] > eps:
            m = i + 1 + k
            keep[m] = True
            stack += [(i, m), (m, j)]
    return [tuple(x) for x in a[keep]]


def _sketch(gray: np.ndarray, region: np.ndarray) -> np.ndarray:
    """Nét phác: biên độ gradient sau làm mờ, giữ ~12% nét mạnh nhất trong vùng hiện vật."""
    g = ndimage.gaussian_filter(gray, 1.6)
    mag = np.hypot(ndimage.sobel(g, 1), ndimage.sobel(g, 0))
    inside = mag[region]
    if not inside.size:
        return np.zeros_like(gray)
    lo, hi = np.percentile(inside, 82), np.percentile(inside, 99.2)
    a = np.clip((mag - lo) / max(1e-6, hi - lo), 0, 1) ** 0.8
    return a * region


def prepare(image: Path) -> dict | None:
    image = Path(image)
    key = hashlib.sha1(image.read_bytes() + VERSION.encode()).hexdigest()[:16]
    meta_f = CACHE / f"{key}.json"
    if meta_f.exists():
        meta = json.loads(meta_f.read_text())
        return {**meta, **{k: CACHE / meta[k] for k in ("bg", "fg", "sketch")}} if meta else None
    CACHE.mkdir(parents=True, exist_ok=True)
    src = Image.open(image).convert("RGB")
    if src.width > MAX_W:
        src = src.resize((MAX_W, round(src.height * MAX_W / src.width)), Image.LANCZOS)
    m = _mask(src, key)
    if m is None:
        meta_f.write_text("null")
        return None
    w, h = src.size
    parts = _parts(m > .5)
    solid = np.logical_or.reduce(parts)
    rgb = np.asarray(src).astype(np.float32)
    # nền: lỗ lấn ra ngoài hiện vật một chút (không để "bóng ma" khi hai lớp trôi lệch)
    hole = ndimage.binary_dilation(solid, iterations=max(6, w // 160))
    plate = hf_depth._fill_hole(rgb, hole)
    Image.fromarray(np.clip(plate, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)).save(CACHE / f"{key}_bg.jpg", quality=88)
    alpha = Image.fromarray((ndimage.gaussian_filter(solid.astype(np.float32), 1.0) * 255).astype(np.uint8))
    cut = src.copy(); cut.putalpha(alpha); cut.save(CACHE / f"{key}_fg.png", optimize=True)
    gray = np.asarray(src.convert("L")).astype(np.float32)
    sk = _sketch(gray, ndimage.binary_dilation(solid, iterations=3))
    a8 = (sk * 255).astype(np.uint8)   # mask-image đọc kênh ALPHA -> ảnh xám không alpha sẽ thành khối đặc
    Image.merge("LA", (Image.fromarray(np.full_like(a8, 255)), Image.fromarray(a8))).save(CACHE / f"{key}_sketch.png", optimize=True)
    # viền: dò từng mảng trên mặt nạ thu nhỏ (~1000px), làm trơn nhẹ, rút gọn
    s = 1000 / max(w, h)
    sw, sh = max(8, round(w * s)), max(8, round(h * s))
    outline = []
    for part in parts:
        small = np.asarray(Image.fromarray(part.astype(np.uint8) * 255).resize((sw, sh), Image.BILINEAR)) > 127
        pts = trace(small)
        if len(pts) < 12:
            continue
        a = np.asarray(pts, float)
        a = np.stack([ndimage.uniform_filter1d(a[:, 0], 3, mode="wrap"), ndimage.uniform_filter1d(a[:, 1], 3, mode="wrap")], 1)
        outline.append([[round(x / sw, 4), round(y / sh, 4)] for x, y in rdp([tuple(p) for p in a], .8)])
    meta = {"bg": f"{key}_bg.jpg", "fg": f"{key}_fg.png", "sketch": f"{key}_sketch.png", "outline": outline, "w": w, "h": h}
    meta_f.write_text(json.dumps(meta))
    return {**meta, **{k: CACHE / meta[k] for k in ("bg", "fg", "sketch")}}


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        r = prepare(Path(p))
        print(p, None if r is None else {k: (v if k != "outline" else f"{len(v)} điểm") for k, v in r.items()})
