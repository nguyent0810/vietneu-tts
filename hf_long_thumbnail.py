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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--domain", choices=list(PALETTE), required=True)
    ap.add_argument("--big1", required=True); ap.add_argument("--big2", required=True)
    ap.add_argument("--promise", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--hero-side", default="right", choices=["right", "left"])
    a = ap.parse_args()
    make(a.hero, a.out, domain=a.domain, big1=a.big1, big2=a.big2, promise=a.promise, tag=a.tag, hero_side=a.hero_side)
