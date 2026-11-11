"""Sinh composition mẫu GH-276; không render. Chạy từ creator_v2."""
from pathlib import Path
import base64
import json
import sys
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import idcards
import build_long

def main():
    image_dir = build_long.HF / 'assets' / 'long' / 'mata-hari' / 'img'
    if not image_dir.is_dir():
        image_dir = Path(r'D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\motion\hf\assets\long\mata-hari\img')
    imgs = {}
    for key in ('mh_hat', 'vin_gate'):
        path = image_dir / f'{key}.jpg'
        with Image.open(path) as im:
            width, height = im.size
        imgs[key] = {'src': 'data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode('ascii'),
                     'w': width, 'h': height}
    styles = ('index_card', 'fingerprint', 'passport', 'verdict', 'wanted', 'envelope',
              'seal_slip', 'case_divider', 'terminal', 'spec_sheet', 'app_card', 'slate',
              'lower_third', 'callout', 'news_clip', 'telegram', 'polaroid', 'edict_scroll',
              'receipt', 'museum_label')
    scenes = []
    for i, style in enumerate(styles):
        t = i * 6.0
        scenes.append({"type": "file", "style": style, "t0": t, "t1": t + 6,
                       "k": style, "name": "CÂU CHUYỆN MẪU", "desc": "Dữ liệu minh họa",
                       "img": 'mh_hat' if i % 2 == 0 else 'vin_gate', "date": "1910", "focus": [0.5, 0.35], "cam": "push_in",
                       "rows": [{"k": "BỐI CẢNH", "v": "Một câu chuyện giả lập", "at": t + 1.2},
                                {"k": "CHI TIẾT", "v": "Thông tin đang được đọc", "at": t + 2.0}]})
        if style == 'wanted':
            scenes[-1]['reward'] = 'VÍ DỤ GIẢ ĐỊNH'
        if style == 'receipt':
            scenes[-1]['rows'] = [{'k': 'KHOẢN MẪU', 'v': '100.000', 'at': t + 1.2},
                                  {'k': 'TỔNG', 'v': '100.000', 'at': t + 2.0}]
        if style in {'receipt', 'telegram', 'index_card', 'terminal'}:
            scenes[-1]['rows'].append({'k': 'CHỮ NHỎ', 'v': 'Nguyễn Thị Ngọc Ẩn, Huỳnh Hữu Khoảng, Ỷ Lại, ỨNG ĐẪN', 'at': t + 3.2})
    case = {"dur": 120, "seed": 276, "hud": {"t": "MẪU THẺ THÔNG TIN"}, "lines": [], "imgs": imgs, "scenes": scenes}
    html = build_long.HTML.replace('<script src="{data}"></script>', '<script>window.CASE = ' + json.dumps(case, ensure_ascii=False).replace('</', '<' + chr(92) + '/') + ';</script>')
    html = html.replace('{fonts}', 'https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;700;900&family=Playfair+Display:wght@700;900&family=Itim&family=IBM+Plex+Mono:wght@400;700&display=swap').replace('{dur}', '120').replace('{title}', 'Mẫu thẻ thông tin').replace('{videos}', '')
    target = build_long.HF / 'compositions' / 'long' / 'idcards_demo.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')
    print(target)

if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from factory.console import utf8_console
    utf8_console()
    main()
