"""Vẽ CHÍNH XÁC (không sinh AI, không lấy ảnh mạng) 2 sơ đồ biểu tượng cố
định dùng chung nhiều tập cho domain Phong Thuỷ: Hậu Thiên Bát Quái và
vòng Ngũ Hành tương sinh/tương khắc -- symbol_library trong
domain_creative_profiles.json trỏ tới output của script này.

BIẾN THỂ MÀU (audit 9 điểm, mục #2 -- "trùng lặp ảnh Ngũ Hành khá nhiều"):
mỗi sơ đồ giờ có 3 biến thể PALETTE (nền/màu viền-chữ khác nhau) để
render_short.py xoay vòng qua rotation_state.py, tránh dùng lặp đi lặp
lại đúng 1 file ảnh. QUAN TRỌNG: biến thể CHỈ đổi màu nền/viền/chữ trang
trí (không mang ý nghĩa tra cứu được) -- HÌNH HỌC/BỐ CỤC/HƯỚNG/HÀO QUẺ và
MÀU NÚT NGŨ HÀNH (Mộc=xanh lá/Hoả=đỏ/Thổ=nâu/Kim=trắng bạc/Thuỷ=xanh
dương -- màu truyền thống có Ý NGHĨA, không phải trang trí) giữ NGUYÊN
100% giống hệt nhau giữa các biến thể, đúng tinh thần đã nêu ở trên: sai
hình học/bố cục là nội dung SAI, không được đánh đổi để có thêm biến thể.

LÝ DO không dùng ComfyUI/SDXL-Turbo cho 2 ảnh này: đã test thật (xem phiên
làm việc) -- prompt "Bagua eight trigrams diagram" ra hoa văn trang trí
trừu tượng với "chữ Hán giả" (glitch), không phải sơ đồ bát quái thật.
Diffusion model (kể cả 4-step turbo) yếu ở nội dung cần chính xác hình học/
bố cục (giống lỗi bàn tay/khuôn mặt đã biết) -- sơ đồ có vị trí/hướng SAI
là nội dung sai thật (rủi ro tương tự nhóm CL đã lưu ý), không chỉ là
"không đẹp". Cũng không tải ảnh có sẵn trên mạng về dùng cho kênh có kiếm
tiền (rủi ro bản quyền/giấy phép không rõ ràng) -- tự vẽ vector từ dữ liệu
đã tra cứu, chính xác 100% và sở hữu hoàn toàn.

Dữ liệu đã tra cứu (2 nguồn độc lập qua WebSearch, xem phiên làm việc):
- Hậu Thiên Bát Quái (Văn Vương, dùng trong phong thuỷ -- KHÁC Tiên Thiên
  Bát Quái dùng cho triết học Kinh Dịch): Khảm=Bắc, Cấn=Đông Bắc, Chấn=Đông,
  Tốn=Đông Nam, Ly=Nam, Khôn=Tây Nam, Đoài=Tây, Càn=Tây Bắc.
- Nét quẻ (hào, dưới lên trên, 1=hào dương/liền, 0=hào âm/đứt) theo đúng
  định nghĩa chuẩn Kinh Dịch/Unicode Trigram For X:
  Càn=111, Đoài=110, Ly=101, Chấn=100, Tốn=011, Khảm=010, Cấn=001, Khôn=000.
- Ngũ hành tương sinh (vòng ngoài, chiều kim đồng hồ): Mộc→Hoả→Thổ→Kim→Thuỷ→Mộc.
- Ngũ hành tương khắc (ngôi sao trong): Mộc khắc Thổ, Thổ khắc Thuỷ,
  Thuỷ khắc Hoả, Hoả khắc Kim, Kim khắc Mộc.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).parent / "assets" / "symbol_library"
SIZE = 1600
CENTER = SIZE // 2

# 3 palette trang trí (nền/viền/chữ) -- KHÔNG đụng tới hình học/màu nút Ngũ
# Hành có ý nghĩa. "gold" là palette gốc (giữ nguyên để không đổi ảnh đã
# dùng trước đây), "jade"/"indigo" là 2 biến thể mới cho rotation.
PALETTES = {
    "gold": {
        "bg": (18, 15, 12), "accent": (212, 175, 55),
        "accent_dim": (140, 115, 40), "cream": (240, 230, 210),
    },
    "jade": {
        "bg": (10, 18, 15), "accent": (110, 190, 140),
        "accent_dim": (70, 130, 95), "cream": (225, 240, 230),
    },
    "indigo": {
        "bg": (12, 14, 24), "accent": (150, 170, 220),
        "accent_dim": (95, 110, 150), "cream": (225, 230, 245),
    },
}
VARIANT_KEYS = list(PALETTES.keys())

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _text_centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, font: ImageFont.FreeTypeFont, fill) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((xy[0] - w / 2 - bbox[0], xy[1] - h / 2 - bbox[1]), text, font=font, fill=fill)


# (tên, hướng, hào dưới->trên, 1=dương/liền 0=âm/đứt, góc la bàn 0=Bắc/trên cùng chiều kim đồng hồ)
HAU_THIEN_BAT_QUAI = [
    ("KHẢM", "Bắc", (0, 1, 0), 0),
    ("CẤN", "Đông Bắc", (0, 0, 1), 45),
    ("CHẤN", "Đông", (1, 0, 0), 90),
    ("TỐN", "Đông Nam", (0, 1, 1), 135),
    ("LY", "Nam", (1, 0, 1), 180),
    ("KHÔN", "Tây Nam", (0, 0, 0), 225),
    ("ĐOÀI", "Tây", (1, 1, 0), 270),
    ("CÀN", "Tây Bắc", (1, 1, 1), 315),
]


def _draw_trigram(draw: ImageDraw.ImageDraw, cx: float, cy: float, yao: tuple[int, int, int], bar_w: float, bar_h: float, gap: float, color) -> None:
    """yao[0] = hào dưới cùng -- vẽ từ dưới lên trên đúng quy ước đọc quẻ."""
    spacing = bar_h + gap
    for i, line in enumerate(yao):  # i=0 -> hào dưới cùng -> vẽ thấp nhất
        y = cy + spacing - i * spacing
        if line == 1:
            draw.rectangle([cx - bar_w / 2, y - bar_h / 2, cx + bar_w / 2, y + bar_h / 2], fill=color)
        else:
            seg = bar_w * 0.42
            draw.rectangle([cx - bar_w / 2, y - bar_h / 2, cx - bar_w / 2 + seg, y + bar_h / 2], fill=color)
            draw.rectangle([cx + bar_w / 2 - seg, y - bar_h / 2, cx + bar_w / 2, y + bar_h / 2], fill=color)


def draw_taiji(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, palette: dict) -> None:
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=palette["accent"], width=4)
    # 2 nửa âm dương: vẽ bằng 2 nửa hình tròn lớn + 2 hình tròn nhỏ đối màu
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 90, 270, fill=palette["cream"])
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 90, fill=(20, 20, 24))
    draw.ellipse([cx - r / 2, cy - r, cx + r / 2, cy], fill=palette["cream"])
    draw.ellipse([cx - r / 2, cy, cx + r / 2, cy + r], fill=(20, 20, 24))
    draw.ellipse([cx - r / 6, cy - r / 2 - r / 6, cx + r / 6, cy - r / 2 + r / 6], fill=(20, 20, 24))
    draw.ellipse([cx - r / 6, cy + r / 2 - r / 6, cx + r / 6, cy + r / 2 + r / 6], fill=palette["cream"])


def _draw_arrow_head(draw: ImageDraw.ImageDraw, tip: tuple[float, float], direction_rad: float, size: float, color) -> None:
    """Vẽ tam giác mũi tên tại `tip`, mũi hướng theo direction_rad (đường
    từ gốc tới đích) -- audit 9 điểm mục #2, Codex review chỉ ra tương
    sinh/tương khắc là quan hệ CÓ HƯỚNG (Mộc SINH Hoả khác Hoả SINH Mộc)
    nhưng bản vẽ gốc chỉ có nét liền/đứt không hướng, không khớp mô tả
    "chiều mũi tên" -- thêm mũi tên để đúng nội dung, không chỉ đẹp hơn."""
    back = size * 1.6
    spread = size * 0.55
    bx = tip[0] - back * math.cos(direction_rad)
    by = tip[1] - back * math.sin(direction_rad)
    left = (bx + spread * math.cos(direction_rad + math.pi / 2), by + spread * math.sin(direction_rad + math.pi / 2))
    right = (bx + spread * math.cos(direction_rad - math.pi / 2), by + spread * math.sin(direction_rad - math.pi / 2))
    draw.polygon([tip, left, right], fill=color)


def generate_bat_quai(variant: str = "gold") -> Path:
    """variant: key trong PALETTES -- CHỈ đổi màu nền/viền/chữ trang trí,
    vị trí/hướng/hào quẻ giữ nguyên tuyệt đối giữa mọi variant."""
    palette = PALETTES[variant]
    img = Image.new("RGB", (SIZE, SIZE), palette["bg"])
    draw = ImageDraw.Draw(img)

    ring_r = SIZE * 0.36
    draw.ellipse([CENTER - ring_r, CENTER - ring_r, CENTER + ring_r, CENTER + ring_r], outline=palette["accent_dim"], width=3)
    outer_r = SIZE * 0.44
    draw.ellipse([CENTER - outer_r, CENTER - outer_r, CENTER + outer_r, CENTER + outer_r], outline=palette["accent_dim"], width=2)

    draw_taiji(draw, CENTER, CENTER, SIZE * 0.10, palette)

    name_font = _font(30)
    dir_font = _font(22)
    trigram_r = SIZE * 0.36
    bar_w, bar_h, gap = SIZE * 0.075, SIZE * 0.018, SIZE * 0.012

    for name, direction, yao, angle_deg in HAU_THIEN_BAT_QUAI:
        rad = math.radians(angle_deg - 90)  # -90: 0 độ = hướng lên (Bắc ở trên, đúng quy ước bản đồ)
        px = CENTER + trigram_r * math.cos(rad)
        py = CENTER + trigram_r * math.sin(rad)
        trigram_h = 3 * bar_h + 2 * gap
        _draw_trigram(draw, px, py, yao, bar_w, bar_h, gap, palette["accent"])
        _text_centered(draw, (px, py - trigram_h / 2 - 34), name, name_font, palette["cream"])
        _text_centered(draw, (px, py + trigram_h / 2 + 26), direction, dir_font, palette["accent_dim"])

    title_font = _font(46)
    _text_centered(draw, (CENTER, SIZE * 0.055), "HẬU THIÊN BÁT QUÁI", title_font, palette["accent"])

    out_path = OUT_DIR / f"bat_quai_hau_thien_{variant}.png"
    img.save(out_path)
    return out_path


NGU_HANH = [
    ("MỘC", (46, 125, 50)),
    ("HOẢ", (198, 40, 40)),
    ("THỔ", (168, 124, 60)),
    ("KIM", (200, 200, 210)),
    ("THUỶ", (30, 90, 160)),
]
# Vòng tương khắc: Mộc khắc Thổ, Thổ khắc Thuỷ, Thuỷ khắc Hoả, Hoả khắc Kim, Kim khắc Mộc.
KHAC_PAIRS = [("MỘC", "THỔ"), ("THỔ", "THUỶ"), ("THUỶ", "HOẢ"), ("HOẢ", "KIM"), ("KIM", "MỘC")]


def generate_ngu_hanh(variant: str = "gold") -> Path:
    """variant: key trong PALETTES -- CHỈ đổi màu nền/viền tương sinh/chữ
    trang trí. Màu NÚT từng hành (NGU_HANH ở trên) giữ NGUYÊN 100% giữa
    mọi variant vì đó là màu truyền thống CÓ Ý NGHĨA tra cứu được (Mộc
    xanh lá, Hoả đỏ, Thổ nâu, Kim trắng bạc, Thuỷ xanh dương) -- không
    phải lựa chọn trang trí, đổi màu này sẽ là SAI NỘI DUNG."""
    palette = PALETTES[variant]
    img = Image.new("RGB", (SIZE, SIZE), palette["bg"])
    draw = ImageDraw.Draw(img)

    r = SIZE * 0.30
    pos = {}
    for i, (name, _color) in enumerate(NGU_HANH):
        angle = math.radians(-90 + i * 72)  # Mộc ở đỉnh trên cùng, xuôi kim đồng hồ đúng chiều tương sinh
        pos[name] = (CENTER + r * math.cos(angle), CENTER + r * math.sin(angle))

    order = [n for n, _ in NGU_HANH]
    node_r = SIZE * 0.075
    arrow_size = SIZE * 0.022
    # Vòng tương sinh (ngũ giác ngoài, liền nét theo accent palette, CÓ
    # HƯỚNG a->b nghĩa là "a sinh b"): Mộc->Hoả->Thổ->Kim->Thuỷ->Mộc
    for i in range(5):
        a, b = order[i], order[(i + 1) % 5]
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        draw.line([(x1, y1), (x2, y2)], fill=palette["accent"], width=6)
        ang = math.atan2(y2 - y1, x2 - x1)
        tip = (x2 - node_r * math.cos(ang), y2 - node_r * math.sin(ang))
        _draw_arrow_head(draw, tip, ang, arrow_size, palette["accent"])
    # Vòng tương khắc (ngôi sao trong, nét đứt đỏ trầm -- màu cảnh báo cố
    # định, không đổi theo palette; CÓ HƯỚNG a->b nghĩa là "a khắc b")
    for a, b in KHAC_PAIRS:
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        steps = 24
        for s in range(0, steps, 2):
            t0, t1 = s / steps, (s + 1) / steps
            draw.line([(x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0), (x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1)], fill=(150, 60, 50), width=3)
        ang = math.atan2(y2 - y1, x2 - x1)
        tip = (x2 - node_r * math.cos(ang), y2 - node_r * math.sin(ang))
        _draw_arrow_head(draw, tip, ang, arrow_size * 0.85, (150, 60, 50))

    label_font = _font(38)
    for name, color in NGU_HANH:  # color KHÔNG lấy từ palette -- xem docstring
        x, y = pos[name]
        draw.ellipse([x - node_r, y - node_r, x + node_r, y + node_r], fill=color, outline=palette["accent"], width=4)
        _text_centered(draw, (x, y), name, label_font, (15, 15, 18) if sum(color) > 400 else palette["cream"])

    title_font = _font(46)
    _text_centered(draw, (CENTER, SIZE * 0.055), "NGŨ HÀNH TƯƠNG SINH TƯƠNG KHẮC", title_font, palette["accent"])
    legend_font = _font(24)
    _text_centered(draw, (CENTER, SIZE * 0.94), "— tương sinh   ·   đỏ đứt: tương khắc —", legend_font, palette["accent_dim"])

    out_path = OUT_DIR / f"ngu_hanh_{variant}.png"
    img.save(out_path)
    return out_path


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for variant in VARIANT_KEYS:
        paths.append(generate_bat_quai(variant))
        paths.append(generate_ngu_hanh(variant))
    for p in paths:
        print(f"OK: {p}")
