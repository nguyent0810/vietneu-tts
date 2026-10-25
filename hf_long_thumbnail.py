"""Thumbnail cho video dài -- theo đúng công thức của video dài thắng nhất hai
kênh ("TUỔI MÃO NỬA CUỐI 2026": 6.871 view, giữ chân 8 phút), đối chiếu với
thumbnail thua (cả câu 10 chữ nhồi vào một dải; hoặc không có thumbnail):

  * MỘT chủ thể (con vật / pho tượng), nửa khung, ánh nhìn về phía chữ
  * HAI dòng chữ cực lớn, 1-2 từ mỗi dòng -- đọc được ở cỡ cột đề xuất
  * MỘT dòng lời hứa ngắn + MỘT nhãn series
  * KHÔNG đặt chữ đè lên mặt tượng (luật của kênh Phật giáo)

Xuất kèm bản thu nhỏ 246x138 và 168x94 (cỡ thật ở cột "video đề xuất", nơi
gần như toàn bộ lượt xem video dài của hai kênh đến từ đó) để kiểm tra.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
FONTS = ROOT / "video_tool_clone" / "assets" / "fonts"
W, H = 1280, 720
PALETTE = {  # nền, chữ chính, nhấn
    "BUD": ((20, 13, 8), (246, 234, 208), (214, 170, 74)),
    "FS":  ((10, 13, 34), (246, 232, 196), (214, 169, 58)),
}


def serif(size):
    f = ImageFont.truetype(str(FONTS / "Lora-Variable.ttf"), size)
    try:
        f.set_variation_by_name("Bold")
    except Exception:  # noqa: BLE001
        pass
    return f


def sans(size):
    return ImageFont.truetype(str(FONTS / "BeVietnamPro-Bold.ttf"), size)


def cover(img, w, h, focus_x=0.5, focus_y=0.4):
    s = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x = int((img.width - w) * focus_x); y = int((img.height - h) * focus_y)
    return img.crop((x, y, x + w, y + h))


def fit(draw, text, font_fn, max_w, start):
    size = start
    while size > 40 and draw.textlength(text, font=font_fn(size)) > max_w:
        size -= 4
    return font_fn(size)


def make(hero, out, *, domain, big1, big2, promise, tag, hero_side="right", focus=(0.5, 0.35)):
    bg, fg, acc = PALETTE[domain]
    canvas = Image.new("RGB", (W, H), bg)
    hw = int(W * 0.56)
    h_img = cover(Image.open(hero).convert("RGB"), hw, H, *focus)
    hx = W - hw if hero_side == "right" else 0
    canvas.paste(h_img, (hx, 0))
    # Mép ảnh tan vào nền để chữ đứng trên mảng tối liền, không phải một khối dán
    grad = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(grad)
    for i in range(hw):
        t = i / hw
        a = int(255 * max(0.0, 1 - t / 0.45)) if hero_side == "right" else int(255 * max(0.0, (t - 0.55) / 0.45))
        x = hx + i
        gd.line([(x, 0), (x, H)], fill=a)
    canvas = Image.composite(Image.new("RGB", (W, H), bg), canvas, grad)
    d = ImageDraw.Draw(canvas)
    tx = 70 if hero_side == "right" else W - int(W * 0.5) + 10
    maxw = int(W * 0.46)  # hẹp hơn nửa khung: chữ không chạm vào chủ thể
    # nhãn series
    tf = sans(30); tw = d.textlength(tag, font=tf)
    d.rectangle([tx, 70, tx + tw + 36, 70 + 54], fill=acc)
    d.text((tx + 18, 78), tag, font=tf, fill=bg)
    # hai dòng chữ lớn -- bóng đổ dày để tách khỏi nền ở cỡ nhỏ
    y = 160
    for line, start in ((big1, 170), (big2, 170)):
        f = fit(d, line, serif, maxw, start)
        for dx, dy in ((0, 8), (4, 8), (-4, 8)):
            d.text((tx + dx, y + dy), line, font=f, fill=(0, 0, 0))
        d.text((tx, y), line, font=f, fill=fg, stroke_width=3, stroke_fill=(0, 0, 0))
        y += int(f.size * 1.08)
    # lời hứa
    pf = fit(d, promise, sans, maxw, 44)
    d.rectangle([tx, y + 26, tx + 8, y + 26 + pf.size + 10], fill=acc)
    d.text((tx + 26, y + 26), promise, font=pf, fill=acc, stroke_width=2, stroke_fill=(0, 0, 0))
    canvas.save(out, quality=92)
    # bản thu nhỏ để soi độ đọc được
    for w, h in ((246, 138), (168, 94)):
        canvas.resize((w, h), Image.LANCZOS).save(Path(out).with_name(Path(out).stem + f"_{w}.png"))
    return out


def make_v2(hero, out, *, domain, text, variant="A", focus=(0.5, 0.12)):
    """Tạo một thumbnail V2: 0–3 từ, một chủ thể và không có nhãn phụ.

    `variant` chỉ thay bố cục chữ; chữ được lấy nguyên từ cold open/neo nội dung.
    Dùng ảnh tư liệu thật ở BUD (không tự vẽ/tạo mặt Đức Phật).
    """
    variant = variant.upper()
    if variant not in {"A", "B", "C"}:
        raise ValueError("variant phải là A, B hoặc C")
    words = text.strip().upper().split()
    if not words or len(words) > 3:
        raise ValueError("thumbnail V2 cần từ 1 đến 3 từ")
    if domain not in PALETTE:
        raise ValueError(f"domain không hợp lệ: {domain}")

    bg, fg, acc = PALETTE[domain]
    canvas = Image.new("RGB", (W, H), bg)
    hero_w = int(W * 0.58)
    hero_img = cover(Image.open(hero).convert("RGB"), hero_w, H, *focus)
    canvas.paste(hero_img, (W - hero_w, 0))

    # Fade ảnh về nền trái để chữ không chạm chủ thể.
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(W - hero_w, W):
        t = (x - (W - hero_w)) / hero_w
        alpha = int(255 * max(0.0, 1.0 - t / 0.30))
        gd.line([(x, 0), (x, H)], fill=alpha)
    canvas = Image.composite(Image.new("RGB", (W, H), bg), canvas, grad)

    d = ImageDraw.Draw(canvas)
    maxw = int(W * 0.46)
    # A/B/C có nhịp bố cục khác nhau nhưng đều giữ mặt tượng bên phải, không đè chữ.
    if variant == "A":
        tx, y = 66, 182
        font_fn, start, gap = serif, 166, 14
        d.rectangle((66, 143, 82, 576), fill=acc)
    elif variant == "B":
        tx, y = 76, 245
        font_fn, start, gap = sans, 150, 18
        d.rectangle((56, 205, 88, 560), fill=acc)
    else:
        tx, y = 66, 172
        font_fn, start, gap = serif, 158, 10
        d.line((66, 580, 66 + maxw, 580), fill=acc, width=12)

    # Chia 2–3 từ thành tối đa 3 dòng, cân dòng khi có ba từ.
    if len(words) == 1:
        lines = words
    elif len(words) == 2:
        lines = words
    else:
        lines = [" ".join(words[:2]), words[2]]
    for line in lines:
        f = fit(d, line, font_fn, maxw, start)
        d.text((tx + 4, y + 8), line, font=f, fill=(0, 0, 0), stroke_width=5, stroke_fill=(0, 0, 0))
        d.text((tx, y), line, font=f, fill=fg, stroke_width=2, stroke_fill=(0, 0, 0))
        y += int(f.size * 1.12) + gap

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=94)
    for w, h in ((168, 94),):
        canvas.resize((w, h), Image.Resampling.LANCZOS).save(
            out.with_name(out.stem + f"_{w}.png")
        )
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--domain", choices=list(PALETTE), required=True)
    ap.add_argument("--big1", required=True); ap.add_argument("--big2", required=True)
    ap.add_argument("--promise", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--hero-side", default="right", choices=["right", "left"])
    a = ap.parse_args()
    make(a.hero, a.out, domain=a.domain, big1=a.big1, big2=a.big2, promise=a.promise, tag=a.tag, hero_side=a.hero_side)
