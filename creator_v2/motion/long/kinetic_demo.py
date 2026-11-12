"""Sinh composition mẫu GH-277 (mọi hiệu ứng chữ x kiểu chữ); không render. Chạy từ creator_v2."""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_long
import kinetic_style

LINES = ["MỘT TRĂM NGÀN", "KHÔNG PHẢI VÀNG · MÀ LÀ GIẤY", "Năm 1799", "ĐỪNG TIN LỜI ĐỒN",
         "Hai mươi tội danh", "Ông không hề gù", "Kho bạc Sơn Đông", "SAI · ĐÚNG",
         "Mười bảy năm sau", "Ngự sử Tiền Phong", "Bản kê tài sản", "Ỷ LẠI · ỨNG ĐẪN", "Nét mực cuối cùng"]


def main():
    scenes, t = [], 0.0
    styles = kinetic_style.STYLES
    for i, fx in enumerate(kinetic_style.EFFECTS + ("strike",)):
        text = LINES[i % len(LINES)]
        style = styles[i % len(styles)]
        item = {"text": text, "at": t + 0.4, "fx": fx, "typestyle": style}
        if kinetic_style._negative(text) and fx != "strike":
            item["autoStrike"] = True
        scenes.append({"type": "kinetic", "t0": t, "t1": t + 5, "label": f"{fx} / {style}",
                       "items": [item, {"text": f"{fx} · {style}", "at": t + 2.2, "sm": True}]})
        t += 5
    case = {"dur": t, "seed": 277, "hud": {"t": "MẪU CHỮ ĐỘNG"}, "lines": [], "imgs": {}, "scenes": scenes}
    html = build_long.HTML.replace('<script src="{data}"></script>', '<script>window.CASE = ' + json.dumps(case, ensure_ascii=False).replace('</', '<' + chr(92) + '/') + ';</script>')
    html = html.replace('{fonts}', 'https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;700;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Barlow+Condensed:wght@700;900&display=swap').replace('{dur}', str(int(t))).replace('{title}', 'Mẫu chữ động').replace('{videos}', '')
    target = build_long.HF / 'compositions' / 'long' / 'kinetic_demo.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')
    print(target, t)


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from factory.console import utf8_console
    utf8_console()
    main()
