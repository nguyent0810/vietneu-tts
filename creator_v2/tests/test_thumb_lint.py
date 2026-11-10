"""Lint thumbnail: số từ chữ lớn, cỡ chữ sau FIT, độ phẳng của ảnh."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT)]
import thumb as T  # noqa: E402


def page(*bigs):
    return "<html><body>" + "".join(bigs) + "</body></html>"


def big(text, size=140, left=80):
    return f'<div class="big" style="left:{left}px;top:300px;font-size:{size}px">{text}</div>'


def test_a_word_count_pass_warn_error():
    assert T.lint_html(page(big("BA CHIẾC ĐAO"), big("KHÔNG CÓ TRONG SỬ"))) == ([], [])      # 7 từ
    warns, errs = T.lint_html(page(big("MỘT HAI BA BỐN"), big("NĂM SÁU BẢY TÁM")))            # 8 từ
    assert warns and not errs
    warns, errs = T.lint_html(page(big("A B C D E F"), big("G H I J K")))                    # 11 từ
    assert errs and "11 từ" in errs[0]


def test_a_counts_tile_b_and_data_fit_and_strips_tags():
    html = page('<div class="tile red"><b>CHỨNG KHOÁN</b><span>↓</span></div>',
                '<div data-fit style="font-size:100px">MỘT <em>HAI</em> BA</div>', "<p>không tính câu này ở đây</p>")
    assert sum(len(i["text"].split()) for i in T.big_texts(html)) == 5


def test_b_small_font_after_fit_is_an_error():
    assert T.lint_html(page(big("BA CHIẾC ĐAO", size=140)))[1] == []
    assert T.lint_html(page(big("CHỮ NHỎ", size=60)))[1]
    # chữ dài ở cỡ 140 bị FIT co tới dưới 72 px
    assert T.lint_html(page(big("MỘT DÒNG CHỮ DÀI QUÁ MỨC CHO MỘT KHUNG THUMBNAIL", size=140)))[1]


def _frame(body, width=1920, height=1080):
    return (f'<html><body><div data-width="{width}" data-height="{height}">' + body + "</div></body></html>")


def test_feed_missing_img_is_warning_not_error():
    warns, errs = T.lint_feed(_frame('<div class="big" style="left:80px;top:80px;font-size:140px">BA CHỮ</div>'))
    assert warns and "không có <img>" in warns[0]
    assert not any("badge" in e or "44px" in e for e in errs)
    warns, errs = T.lint_feed(_frame('<img src="a.jpg"><div class="big" style="left:80px;top:80px;font-size:140px">BA CHỮ</div>'))
    assert not warns


def test_feed_small_text_uses_1280_frame():
    small = _frame('<div style="left:80px;top:80px;font-size:60px">NHÃN NHỎ</div>')
    assert any("44px" in e for e in T.lint_feed(small)[1])
    exact = _frame('<div style="left:80px;top:80px;font-size:66px">ĐỦ CỠ</div>')
    assert not any("44px" in e for e in T.lint_feed(exact)[1])
    on_1280 = _frame('<div style="left:80px;top:80px;font-size:44px">ĐỦ 1280</div>', 1280, 720)
    assert not any("44px" in e for e in T.lint_feed(on_1280)[1])
    under = _frame('<div style="left:40px;top:40px;font-size:43px">NHỎ 1280</div>', 1280, 720)
    assert any("44px" in e for e in T.lint_feed(under)[1])


def test_feed_badge_zone_is_bottom_right():
    inside = _frame('<div style="left:1600px;top:950px;font-size:80px">GÓC</div>')
    assert any("badge" in e for e in T.lint_feed(inside)[1])
    outside = _frame('<div style="left:80px;top:80px;font-size:80px">TRÁI</div>')
    assert not any("badge" in e for e in T.lint_feed(outside)[1])


def test_feed_class_font_size_and_tiny_export():
    html = '<style>.tag{font-size:30px}</style>' + _frame('<div class="tag" style="left:80px;top:80px">NHÃN</div>')
    assert any("44px" in e for e in T.lint_feed(html)[1])
    assert T.TINY == (168, 94)
    source = (ROOT / "motion" / "long" / "thumb.py").read_text(encoding="utf-8")
    assert 'f"{t}_tiny.jpg"' in source or 'f"{t}_tiny.jpg"' in source.replace("'", '"')
    assert "scale={TINY[0]}:{TINY[1]}" in source


def test_c_flat_image_is_an_error(tmp_path):
    from PIL import Image
    Image.new("RGB", (64, 36), (120, 120, 120)).save(tmp_path / "flat.jpg")
    img = Image.new("RGB", (64, 36), (0, 0, 0))
    img.paste((255, 255, 255), (0, 0, 32, 36))
    img.save(tmp_path / "contrast.jpg")
    assert T.lint_image(tmp_path / "flat.jpg")
    assert T.lint_image(tmp_path / "contrast.jpg") == []
    warns, errs = T.lint("x", page(big("BA CHỮ")), tmp_path / "flat.jpg")
    assert errs
