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
