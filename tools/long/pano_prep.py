"""Chuẩn bị ảnh siêu rộng cho máy lia."""
import argparse
from PIL import Image, ImageFilter


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--height", type=int, default=1080)
    args = parser.parse_args(argv)
    im = Image.open(args.source).convert("RGB")
    scale = args.height / im.height
    if scale > 2.0:
        print(f"CẢNH BÁO: phóng {scale:.2f}x — ảnh sẽ mờ, nên lấy bản lớn hơn")
    out = im.resize((round(im.width * scale), args.height), Image.Resampling.LANCZOS)
    if scale > 1.05:
        out = out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    out.save(args.destination, quality=93)
    print(f"{args.source} {im.size} -> {args.destination} {out.size} (x{scale:.2f})")


if __name__ == "__main__":
    main()
