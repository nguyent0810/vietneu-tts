"""Thumbnail tự dựng cho Long thử Cao Biền: tên mỏ neo 2 dòng + câu hỏi ≤ 3 chữ (luật 23/10), giống bố cục fs26_A đã duyệt.

    python thumb_cb.py <hero> <out.jpg> [focus_x focus_y] [full] [q=<cỡ tối đa dòng câu hỏi>] [t=DÒNG1|DÒNG2|CÂU HỎI] [pal=BUD]
                       [k=NGOÀI ĐỜI THẬT]
    full: ảnh nền đã chừa mảng trống bên trái -> trải tràn khung, chỉ phủ tối nhẹ sau chữ.
    k=  : dải nhận diện series (nền đỏ, chữ kem) đặt ngay trên tên mỏ neo (đề xuất ChatGPT 25/10).
"""
import sys
import argparse
from pathlib import Path

if "--help" in sys.argv:
    argparse.ArgumentParser(description="Tạo thumbnail Long từ ảnh nền và chữ đặt tay.").print_help()
    raise SystemExit(0)

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from hf_long_thumbnail import PALETTE, W, H, cover, fit, sans, serif  # noqa: E402

args = sys.argv[1:]
full = "full" in args
qmax = next((int(a[2:]) for a in args if a.startswith("q=")), 120)
text = next((a[2:].split("|") for a in args if a.startswith("t=")), ["CAO", "BIỀN", "AI YỂM AI?"])
pal = next((a[4:] for a in args if a.startswith("pal=")), "FS")
kicker = next((a[2:] for a in args if a.startswith("k=")), "")
args = [a for a in args if a != "full" and not a.startswith(("q=", "t=", "pal=", "k="))]
hero, out = args[0], Path(args[1])
fx, fy = (float(args[2]), float(args[3])) if len(args) > 3 else (0.5, 0.35)
bg, fg, acc = PALETTE[pal]
canvas = Image.new("RGB", (W, H), bg)
if full:
    canvas.paste(cover(Image.open(hero).convert("RGB"), W, H, fx, fy), (0, 0))
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(W):   # tối dần sau khối chữ (trái), trả nguyên ảnh từ giữa khung sang phải
        gd.line([(x, 0), (x, H)], fill=int(150 * max(0.0, 1 - x / (W * 0.55))))
    canvas = Image.composite(Image.new("RGB", (W, H), bg), canvas, grad)
else:
    hw = int(W * 0.60)
    canvas.paste(cover(Image.open(hero).convert("RGB"), hw, H, fx, fy), (W - hw, 0))
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for i in range(hw):
        gd.line([(W - hw + i, 0), (W - hw + i, H)], fill=int(255 * max(0.0, 1 - (i / hw) / 0.40)))
    canvas = Image.composite(Image.new("RGB", (W, H), bg), canvas, grad)
d = ImageDraw.Draw(canvas)
lines, maxw, tx = text, int(W * 0.42), 60
nmax = 250 if qmax <= 120 else 205   # câu hỏi to thì tên nhỏ lại một chút cho vừa chiều cao
qw = maxw if qmax <= 120 else int(W * 0.53)
name_w = max(lines[:2], key=lambda t: d.textlength(t, font=serif(100)))   # hai dòng tên cùng cỡ, theo dòng rộng hơn
fonts = [fit(d, name_w, serif, maxw, nmax), fit(d, name_w, serif, maxw, nmax), fit(d, lines[2], serif, qw, qmax)]


def ink(ln, f):
    pad = f.size
    m = Image.new("L", (int(d.textlength(ln, font=f)) + 2 * pad, f.size * 3), 0)
    ImageDraw.Draw(m).text((pad, pad), ln, font=f, fill=255, stroke_width=4)
    l, t, r, b = m.getbbox()
    return l - pad, t - pad, r - pad, b - pad


boxes = [ink(ln, f) for ln, f in zip(lines, fonts)]
tops = [0]
for k in range(1, 3):
    gap = int(max(fonts[k - 1].size, fonts[k].size) * 0.16)
    tops.append(tops[-1] + boxes[k - 1][3] + gap - boxes[k][1])
total = tops[-1] + boxes[-1][3] - boxes[0][1]
kf = sans(40)
band = (kf.size + 22) if kicker else 0
y0 = (H - total + band + 14 * bool(kicker)) // 2 - boxes[0][1]
if kicker:
    by = y0 + boxes[0][1] - band - 14
    bw = int(d.textlength(kicker, font=kf)) + 36
    d.rectangle((tx, by, tx + bw, by + band), fill=(168, 24, 24))
    d.text((tx + 18, by + band // 2), kicker, font=kf, fill=(250, 240, 220), anchor="lm")
for i, (ln, f) in enumerate(zip(lines, fonts)):
    y = y0 + tops[i]
    col = acc if i == 2 else fg
    for dx, dy in ((0, 10), (5, 10), (-5, 10)):
        d.text((tx + dx, y + dy), ln, font=f, fill=(0, 0, 0))
    d.text((tx, y), ln, font=f, fill=col, stroke_width=4, stroke_fill=(0, 0, 0))
canvas.save(out, quality=92)
canvas.resize((168, 94), Image.LANCZOS).save(out.with_name(out.stem + "_168.png"))
print(out)
