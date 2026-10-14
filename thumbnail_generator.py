"""CLI tạo thumbnail chuẩn SEO cho video Long-form -- audit 9 điểm mục #6.

CHỈ áp dụng cho Long-form: đã xác nhận qua WebFetch support.google.com/
youtube/answer/72431 -- YouTube Shorts KHÔNG hỗ trợ thumbnail tuỳ chỉnh
(chỉ chọn được 1 khung hình có sẵn trong video lúc upload, không đổi được
sau đó) -- upload_thumbnail()/thumbnails.set trong youtube_upload.py chỉ
có tác dụng thật với Long-form.

Thiết kế: KHÔNG dùng ComfyUI sinh ảnh nền mới (server không chạy sẵn
trong môi trường vận hành thường xuyên, thêm phụ thuộc không cần thiết) --
dùng lại 1 ảnh/khung hình ĐÃ CÓ SẴN từ chính tập phim (khung hình đẹp nhất
trong asset đã render, do người dùng chỉ định qua --background) làm nền,
rồi phủ chữ tiêu đề IN ĐẬM qua PIL (font Be Vietnam Pro Bold -- đã glyph-
check tiếng Việt đầy đủ, xem font_glyph_check.py) + dải nền tối bán trong
suốt phía sau chữ để đảm bảo tương phản/đọc được dù ảnh nền sáng hay tối
(chuẩn thực hành thumbnail YouTube phổ biến).

Màu nhấn theo domain, đồng bộ tông đã định nghĩa ở domain_creative_profiles.json
(image_style_anchor) -- KHÔNG dùng màu đỏ/vàng giật gân kiểu clickbait cho
CL (đã cam kết "non-sensational" xuyên suốt dự án)."""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT_ROOT = Path(__file__).parent
FONT_BOLD = PROJECT_ROOT / "video_tool_clone" / "assets" / "fonts" / "BeVietnamPro-Bold.ttf"
OUT_SIZE = (1280, 720)  # chuẩn YouTube thumbnail 16:9

# Màu nhấn theo domain -- đồng bộ tông đã định nghĩa ở domain_creative_profiles.json.
# CL cố ý dùng tông trầm/trung tính (không đỏ/vàng giật gân) khớp cam kết
# "non-sensational" đã áp dụng xuyên suốt dự án cho kênh Hình Sự.
ACCENT_BY_DOMAIN = {
    "BUD": {"accent": (212, 175, 55), "band": (18, 15, 12, 210)},      # vàng ấm, nền tối ấm
    "FS": {"accent": (212, 175, 55), "band": (12, 20, 18, 210)},        # vàng + nền xanh đen ánh Á Đông
    "CL": {"accent": (150, 170, 200), "band": (14, 16, 22, 220)},       # xanh xám trầm, trung tính
}
DEFAULT_ACCENT = {"accent": (230, 230, 230), "band": (10, 10, 10, 210)}


def _font(size: int) -> ImageFont.FreeTypeFont:
    if FONT_BOLD.exists():
        return ImageFont.truetype(str(FONT_BOLD), size)
    return ImageFont.load_default()


def _fit_background(image_path: Path, size: tuple[int, int]) -> Image.Image:
    """Crop-to-fill (giữ tỉ lệ, cắt bớt thay vì méo hình) ảnh nền về đúng
    kích thước thumbnail chuẩn."""
    img = Image.open(image_path).convert("RGB")
    target_w, target_h = size
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    return img.resize(size, Image.LANCZOS)


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if _text_width(draw, trial, font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    """Chiều rộng thật của chuỗi (bbox[2]-bbox[0], KHÔNG phải bbox[2] --
    Codex review vòng 3, lưu ý không-chặn: dùng thẳng bbox[2] giả định
    bbox[0]==0, đúng với font hiện tại nhưng không tổng quát cho mọi
    font/ký tự mở đầu -- chuẩn hoá 1 helper dùng chung để nhất quán với
    _wrap_text())."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _truncate_line_to_width(draw: ImageDraw.ImageDraw, line: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """Cắt bớt 1 dòng (thêm '…') cho vừa max_width -- dùng khi bản thân dòng
    đó (VD: 1 token dài không có khoảng trắng như URL/hashtag/mã vụ án) đã
    rộng hơn max_width, bất kể tổng số dòng có vượt max_lines hay không."""
    ellipsis = "…"
    if _text_width(draw, line, font) <= max_width:
        return line
    truncated = line
    while truncated and _text_width(draw, truncated + ellipsis, font) > max_width:
        truncated = truncated[:-1].rstrip()
    return (truncated + ellipsis) if truncated else ellipsis


def _force_ellipsis_fit(draw: ImageDraw.ImageDraw, line: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """Luôn thêm dấu '…' vào dòng CUỐI khi BIẾT các dòng phía sau đã bị cắt
    bỏ hoàn toàn (xem _fit_title_to_lines) -- kể cả khi bản thân dòng này
    vốn đã vừa max_width, để báo hiệu rõ ràng tiêu đề đã bị rút gọn thay vì
    trông như hiển thị đủ."""
    ellipsis = "…"
    candidate = line
    while candidate and _text_width(draw, candidate + ellipsis, font) > max_width:
        candidate = candidate[:-1].rstrip()
    return (candidate + ellipsis) if candidate else ellipsis


def _fit_title_to_lines(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_lines: int,
                         start_size: int, min_size: int = 40) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Trả về (font, lines) ĐẢM BẢO len(lines) <= max_lines VÀ từng dòng
    <= max_width THẬT SỰ (Codex review vòng 2: _wrap_text() có nhánh
    `or not current` để tránh vòng lặp vô hạn khi 1 token đơn (URL/hashtag/
    mã vụ án) rộng hơn max_width -- token đó vẫn được chấp nhận làm 1 dòng
    riêng dù tràn khung, và nếu đó là dòng DUY NHẤT thì len(lines) không hề
    vượt max_lines nên nhánh cắt-dòng cũ không bao giờ chạy tới). Chiến
    lược: giảm cỡ chữ tới khi vừa max_lines VÀ mọi dòng đều vừa max_width
    (hoặc tới min_size); sau đó LUÔN kiểm tra + cắt riêng từng dòng còn lại
    cho vừa max_width; nếu có dòng bị bỏ hẳn (cắt bớt xuống max_lines) thì
    dòng cuối LUÔN được ép thêm '…' dù bản thân nó vốn đã vừa khung, để báo
    hiệu tiêu đề đã bị rút gọn."""

    def _any_line_too_wide(candidate_lines: list[str], candidate_font: ImageFont.FreeTypeFont) -> bool:
        return any(_text_width(draw, ln, candidate_font) > max_width for ln in candidate_lines)

    size = start_size
    font = _font(size)
    lines = _wrap_text(draw, text, font, max_width)
    while (len(lines) > max_lines or _any_line_too_wide(lines, font)) and size > min_size:
        size -= 8
        font = _font(size)
        lines = _wrap_text(draw, text, font, max_width)

    dropped_lines = len(lines) > max_lines
    if dropped_lines:
        lines = lines[:max_lines]

    fitted: list[str] = []
    last_idx = len(lines) - 1
    for i, ln in enumerate(lines):
        if i == last_idx and dropped_lines:
            fitted.append(_force_ellipsis_fit(draw, ln, font, max_width))
        else:
            fitted.append(_truncate_line_to_width(draw, ln, font, max_width))
    return font, fitted


def generate_thumbnail(background_path: str, title_text: str, output_path: str,
                        domain: str | None = None, font_size: int = 92) -> Path:
    """Tạo 1 thumbnail 1280x720 -- nền là ảnh có sẵn (crop-to-fill), phủ
    dải nền tối bán trong suốt + chữ tiêu đề IN ĐẬM màu nhấn theo domain.
    title_text nên là bản RÚT GỌN/ĐÃ TỐI ƯU riêng cho thumbnail (khác hẳn
    tiêu đề video đầy đủ) -- ngắn (dưới ~6-8 từ), gây tò mò, ĐÚNG NỘI DUNG
    (không giật tít sai sự thật -- vi phạm cùng nguyên tắc trung thực đã
    áp dụng cho toàn bộ nội dung dự án này)."""
    colors = ACCENT_BY_DOMAIN.get(domain or "", DEFAULT_ACCENT)
    canvas = _fit_background(Path(background_path), OUT_SIZE)

    # Làm tối nhẹ toàn bộ nền (vignette đơn giản) để chữ luôn đọc được dù
    # ảnh nền sáng, TRƯỚC KHI vẽ dải nền đậm phía dưới.
    overlay = Image.new("RGBA", OUT_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    dark_overlay = Image.new("RGBA", OUT_SIZE, (0, 0, 0, 60))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), dark_overlay)
    draw = ImageDraw.Draw(canvas)

    margin_x = 64
    max_text_width = OUT_SIZE[0] - 2 * margin_x
    # Không quá 3 dòng -- thumbnail quá nhiều chữ khó đọc ở kích thước nhỏ
    # (khung xem trước trên điện thoại). _fit_title_to_lines() ĐẢM BẢO kết
    # quả <= 3 dòng THẬT SỰ (Codex review: bản trước chỉ giảm cỡ chữ tới
    # ngưỡng rồi DỪNG dù vẫn còn thừa dòng -- tiêu đề rất dài có thể tràn
    # khung hình. Giờ cắt bớt + thêm '…' nếu giảm cỡ chữ vẫn không đủ).
    font, lines = _fit_title_to_lines(draw, title_text.upper(), max_text_width, max_lines=3, start_size=font_size)

    line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
    line_spacing = int(line_height * 0.35)
    block_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
    band_padding = 36
    band_top = OUT_SIZE[1] - block_height - 2 * band_padding
    draw.rectangle([0, band_top, OUT_SIZE[0], OUT_SIZE[1]], fill=colors["band"])

    y = band_top + band_padding
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x = margin_x if line_w > max_text_width * 0.9 else (OUT_SIZE[0] - line_w) // 2
        # Viền đen mỏng quanh chữ (stroke) -- tăng tương phản thêm 1 lớp
        # nữa ngoài dải nền, đúng thực hành thumbnail phổ biến.
        draw.text((x, y), line, font=font, fill=colors["accent"], stroke_width=3, stroke_fill=(0, 0, 0))
        y += line_height + line_spacing

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path, "JPEG", quality=92)
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--background", required=True, help="Ảnh nền có sẵn (khung hình đẹp nhất từ tập phim)")
    ap.add_argument("--title", required=True, help="Chữ tiêu đề NGẮN GỌN cho thumbnail (khác tiêu đề video đầy đủ)")
    ap.add_argument("--output", required=True)
    ap.add_argument("--domain", choices=list(ACCENT_BY_DOMAIN.keys()), default=None)
    ap.add_argument("--font-size", type=int, default=92)
    args = ap.parse_args()

    if not Path(args.background).exists():
        print(f"LỖI: không tìm thấy ảnh nền: {args.background}", file=sys.stderr)
        return 1

    out = generate_thumbnail(args.background, args.title, args.output, domain=args.domain, font_size=args.font_size)
    print(f"OK: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
