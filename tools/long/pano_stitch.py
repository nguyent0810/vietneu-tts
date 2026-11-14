"""Ghép hai ảnh 16:9 thành ảnh toàn cảnh rộng 3840×1080 cho camera pan video dài (Task 028).

Nguyên tắc:
1. Nhận 2 ảnh 16:9 (trái, phải).
2. Chuẩn hoá chiều cao về 1080p (1920×1080).
3. Tìm vùng chồng mép qua tương quan chéo (template/correlation) trong khoảng 15–25%,
   hoặc dùng chồng cố định (mặc định 20% nếu không tìm thấy cấu trúc tương đồng).
4. Hoà mép: feather (alpha cosine mịn) hoặc multi-band (tách tần số thấp/cao).
5. Xuất ảnh đúng kích thước 3840×1080 (phóng tỉ lệ theo chiều ngang rồi crop chiều cao).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def detect_overlap_offset(
    img1_rgb: np.ndarray,
    img2_rgb: np.ndarray,
    min_overlap: float = 0.15,
    max_overlap: float = 0.25,
    default_overlap: float = 0.20,
) -> int:
    """Tìm độ rộng dải chồng mép tối ưu qua tương quan chéo chuẩn hoá giữa mép phải img1 và mép trái img2."""
    h, w, _ = img1_rgb.shape
    min_ov_px = int(round(w * min_overlap))
    max_ov_px = int(round(w * max_overlap))
    default_ov_px = int(round(w * default_overlap))

    # Chuyển sang ảnh xám để tính tương quan
    gray1 = np.dot(img1_rgb[..., :3].astype(np.float32), [0.2989, 0.5870, 0.1140])
    gray2 = np.dot(img2_rgb[..., :3].astype(np.float32), [0.2989, 0.5870, 0.1140])

    best_score = -1.0
    best_ov = default_ov_px

    # Quét qua các độ rộng overlap khả dĩ
    step = max(1, (max_ov_px - min_ov_px) // 40)
    for ov in range(min_ov_px, max_ov_px + 1, step):
        strip1 = gray1[:, w - ov :]
        strip2 = gray2[:, :ov]

        # Trừ trung bình để tính tương quan chéo (NCC)
        s1 = strip1 - np.mean(strip1)
        s2 = strip2 - np.mean(strip2)
        norm1 = np.linalg.norm(s1)
        norm2 = np.linalg.norm(s2)

        if norm1 > 1e-4 and norm2 > 1e-4:
            ncc = float(np.sum(s1 * s2) / (norm1 * norm2))
            if ncc > best_score:
                best_score = ncc
                best_ov = ov

    # Nếu tương quan yếu (< 0.25), dùng tỉ lệ chồng cố định mặc định
    if best_score < 0.25:
        return default_ov_px
    return best_ov


def blend_feather(strip1: np.ndarray, strip2: np.ndarray) -> np.ndarray:
    """Hoà mép dạng feather bằng hàm cosine mềm (smoothstep/cosine ramp)."""
    h, ov, c = strip1.shape
    # Alpha đi từ 1.0 (mép trái dải chồng) về 0.0 (mép phải dải chồng)
    x = np.linspace(0, np.pi, ov, endpoint=True)
    alpha = (0.5 * (1.0 + np.cos(x))).reshape(1, ov, 1).astype(np.float32)
    blended = strip1.astype(np.float32) * alpha + strip2.astype(np.float32) * (1.0 - alpha)
    return np.clip(blended, 0, 255).astype(np.uint8)


def blend_multiband(strip1: np.ndarray, strip2: np.ndarray, sigma: float = 16.0) -> np.ndarray:
    """Hoà mép multi-band: tách tần số thấp (ánh sáng/màu) hoà rộng, tần số cao (chi tiết) hoà hẹp."""
    h, ov, c = strip1.shape
    s1 = strip1.astype(np.float32)
    s2 = strip2.astype(np.float32)

    # Tầng tần số thấp (low-pass)
    low1 = np.zeros_like(s1)
    low2 = np.zeros_like(s2)
    for ch in range(c):
        low1[..., ch] = gaussian_filter(s1[..., ch], sigma=sigma)
        low2[..., ch] = gaussian_filter(s2[..., ch], sigma=sigma)

    # Tầng tần số cao (high-pass)
    high1 = s1 - low1
    high2 = s2 - low2

    # Trọng số mềm cho tần số thấp
    x_low = np.linspace(0, np.pi, ov, endpoint=True)
    alpha_low = (0.5 * (1.0 + np.cos(x_low))).reshape(1, ov, 1)
    blended_low = low1 * alpha_low + low2 * (1.0 - alpha_low)

    # Trọng số dốc hơn cho tần số cao (ở giữa vùng overlap)
    x_high = np.clip((np.linspace(-1.0, 1.0, ov, endpoint=True) * 2.5), -1.0, 1.0)
    alpha_high = (0.5 * (1.0 - x_high)).reshape(1, ov, 1)
    blended_high = high1 * alpha_high + high2 * (1.0 - alpha_high)

    blended = blended_low + blended_high
    return np.clip(blended, 0, 255).astype(np.uint8)


def stitch_panorama(
    left_path: Path | str,
    right_path: Path | str,
    output_path: Path | str | None = None,
    overlap: float = 0.20,
    auto_detect: bool = True,
    mode: str = "multiband",
    target_width: int = 3840,
    target_height: int = 1080,
) -> Image.Image:
    """Ghép 2 ảnh 16:9 thành 1 ảnh panorama 3840×1080."""
    left_p = Path(left_path)
    right_p = Path(right_path)
    if not left_p.is_file():
        raise FileNotFoundError(f"Không tìm thấy ảnh trái: {left_p}")
    if not right_p.is_file():
        raise FileNotFoundError(f"Không tìm thấy ảnh phải: {right_p}")

    im1 = Image.open(left_p).convert("RGB")
    im2 = Image.open(right_p).convert("RGB")

    # Chuẩn hoá kích thước ban đầu về 1080p (chiều cao 1080, chiều rộng tương ứng 16:9 = 1920)
    base_h = 1080
    w1 = int(round(im1.width * (base_h / im1.height)))
    w2 = int(round(im2.width * (base_h / im2.height)))
    im1_norm = im1.resize((w1, base_h), Image.Resampling.LANCZOS)
    im2_norm = im2.resize((w2, base_h), Image.Resampling.LANCZOS)

    arr1 = np.asarray(im1_norm)
    arr2 = np.asarray(im2_norm)

    if auto_detect:
        ov_px = detect_overlap_offset(arr1, arr2, min_overlap=0.15, max_overlap=0.25, default_overlap=overlap)
    else:
        ov_px = int(round(min(w1, w2) * overlap))

    ov_px = max(8, min(ov_px, min(w1, w2) - 10))

    # Tách các dải
    left_exclusive = arr1[:, : w1 - ov_px]
    strip1 = arr1[:, w1 - ov_px :]
    strip2 = arr2[:, :ov_px]
    right_exclusive = arr2[:, ov_px:]

    # Hoà mép
    if mode == "feather":
        blended_strip = blend_feather(strip1, strip2)
    else:
        blended_strip = blend_multiband(strip1, strip2)

    # Ghép 3 dải thành một tấm
    stitched_arr = np.concatenate([left_exclusive, blended_strip, right_exclusive], axis=1)
    stitched_img = Image.fromarray(stitched_arr)

    # Quy chuẩn kích thước về 3840×1080 (crop chiều cao)
    # Phóng ảnh sao cho width = target_width
    scale = target_width / stitched_img.width
    scaled_h = int(round(stitched_img.height * scale))
    scaled_img = stitched_img.resize((target_width, scaled_h), Image.Resampling.LANCZOS)

    # Crop chiều cao căn giữa
    if scaled_h >= target_height:
        top = (scaled_h - target_height) // 2
        final_img = scaled_img.crop((0, top, target_width, top + target_height))
    else:
        # Nếu chiều cao thiếu, phóng theo chiều cao rồi crop chiều rộng
        scale_h = target_height / scaled_img.height
        new_w = int(round(scaled_img.width * scale_h))
        scaled_img2 = scaled_img.resize((new_w, target_height), Image.Resampling.LANCZOS)
        left = max(0, (new_w - target_width) // 2)
        final_img = scaled_img2.crop((left, 0, left + target_width, target_height))

    if output_path is not None:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        final_img.save(out_p, quality=95)

    return final_img


def main():
    parser = argparse.ArgumentParser(description="Ghép 2 ảnh 16:9 thành panorama 3840×1080")
    parser.add_argument("left", type=str, help="Đường dẫn ảnh trái (16:9)")
    parser.add_argument("right", type=str, help="Đường dẫn ảnh phải (16:9)")
    parser.add_argument("-o", "--output", type=str, required=True, help="Đường dẫn lưu ảnh panorama")
    parser.add_argument("--overlap", type=float, default=0.20, help="Tỉ lệ chồng mép cố định (0.15-0.25)")
    parser.add_argument("--mode", choices=["multiband", "feather"], default="multiband", help="Kiểu hoà mép")
    parser.add_argument("--no-auto", action="store_true", help="Tắt tự động dò khớp tương quan, dùng overlap cố định")

    args = parser.parse_args()

    out_path = Path(args.output)
    res = stitch_panorama(
        args.left,
        args.right,
        output_path=out_path,
        overlap=args.overlap,
        auto_detect=not args.no_auto,
        mode=args.mode,
    )
    print(f"Đã ghép xong ảnh panorama: {out_path} ({res.width}×{res.height})")


if __name__ == "__main__":
    main()
