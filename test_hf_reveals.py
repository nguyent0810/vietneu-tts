"""Bốn kiểu hiện ảnh sống ở ba nơi: tên trong `hyperframes_bridge.REVEALS`,
class trong `base.css`, nhánh tween trong `engine.js`. Hôm nay đã mất nửa tiếng
vì engine thiếu ba nhánh trong khi CSS và bridge đều đủ -- video render ra
"thành công" với ba màn trắng trơn, không có lỗi nào bắn ra.

Test này bắt đúng kiểu trôi đó.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
CSS = ROOT / "hyperframes_short" / "compositions" / "base.css"
ENGINE = ROOT / "hyperframes_short" / "compositions" / "engine.js"


def _reveals():
    # Đọc bằng regex thay vì import: import bridge kéo theo kiểm external_bin.
    src = (ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8")
    m = re.search(r"^REVEALS\s*=\s*\(([^)]*)\)", src, re.M)
    assert m, "không tìm thấy REVEALS trong hyperframes_bridge.py"
    return tuple(re.findall(r'"([a-z]+)"', m.group(1)))


REVEALS = _reveals()


def test_co_du_bon_kieu():
    assert set(REVEALS) == {"ink", "wipe", "iris", "rise"}


@pytest.mark.parametrize("how", REVEALS)
def test_css_co_class(how):
    assert f".media-reveal-{how}" in CSS.read_text(encoding="utf-8")


@pytest.mark.parametrize("how", REVEALS)
def test_css_khai_bien(how):
    """Class phải tự đặt giá trị đầu cho biến nó dùng, nếu không tween của
    GSAP không có điểm xuất phát."""
    css = CSS.read_text(encoding="utf-8")
    block = css.split(f".media-reveal-{how}", 1)[1].split("}", 1)[0]
    assert f"--{how}:" in block


@pytest.mark.parametrize("how", REVEALS)
def test_engine_co_nhanh_tween(how):
    engine = ENGINE.read_text(encoding="utf-8")
    assert f'how === "{how}"' in engine, f"engine.js thiếu nhánh cho {how!r}"
    assert f'"--{how}"' in engine, f"engine.js không tween biến --{how}"


def test_css_khong_co_class_thua():
    """Class trong CSS mà bridge không cho phép thì không ai gọi tới được."""
    found = set(re.findall(r"\.media-reveal-([a-z]+)", CSS.read_text(encoding="utf-8")))
    assert found == set(REVEALS)


def test_khong_reveal_bang_filter_hay_scale():
    """`filter` đang chở house grade, `scale` đang chở Ken Burns."""
    css = CSS.read_text(encoding="utf-8")
    for how in REVEALS:
        block = css.split(f".media-reveal-{how}", 1)[1].split("}", 1)[0]
        assert "filter:" not in block
        assert "transform:" not in block


def _paper_styles():
    src = (ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8")
    m = re.search(r"^PAPER_STYLES\s*=\s*\(([^)]*)\)", src, re.M)
    assert m, "không tìm thấy PAPER_STYLES"
    return tuple(re.findall(r'"([a-z]+)"', m.group(1)))


def test_ink_chi_cho_style_nen_giay():
    """Vệt mực trên nền tối ra một mảng sáng lem, không ra thư pháp."""
    paper = _paper_styles()
    assert paper, "PAPER_STYLES rỗng thì 'ink' không dùng được ở đâu cả"
    src = (ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8")
    assert 'how == "ink" and style not in PAPER_STYLES' in src


def test_paper_styles_deu_co_that():
    src = (ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8")
    khai = set(re.findall(r'^\s*"([a-z]+)":\s*\{"file":', src, re.M))
    assert set(_paper_styles()) <= khai


BUD_STYLES = ("inkwash", "oilpaint", "silence", "lightfield", "dustbeam")
COMPS = ROOT / "hyperframes_short" / "compositions"


@pytest.mark.parametrize("style", BUD_STYLES)
def test_bud_khong_co_nhan_tu_lieu(style):
    """Nhãn kiểu "HÌNH MINH HOẠ" là ngôn ngữ phóng sự, không phải ngôn ngữ
    phim. Kênh Phật giáo bỏ hẳn."""
    src = (COMPS / f"{style}.html").read_text(encoding="utf-8")
    assert "mv-slug" not in src
    assert "MINH HOẠ" not in src


@pytest.mark.parametrize("style", ("dossier", "casemap", "vhs", "interrogation"))
def test_cl_van_giu_nhan(style):
    """Kênh hình sự thì GIỮ: ở đó nhãn còn là lời nói rõ rằng ảnh chỉ mang
    tính minh hoạ cho một vụ án có thật, không phải ảnh hiện trường."""
    src = (COMPS / f"{style}.html").read_text(encoding="utf-8")
    assert "mv-slug" in src


def test_lop_dien_anh_chi_cho_bud():
    engine = (COMPS / "engine.js").read_text(encoding="utf-8")
    assert 'V.series === "bud"' in engine
    assert '#cine' in (COMPS / "base.css").read_text(encoding="utf-8")
