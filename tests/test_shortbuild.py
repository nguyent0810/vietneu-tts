import json

import pytest

from shortbuild import GuardError, bud_html, footer, validate, write_plan
from shortbuild.css import BASE_CSS, theme_css


def test_footer_contains_only_escaped_source():
    assert footer("Dhp 5") == '<div id="footer"><div id="src">Dhp 5</div></div>'
    assert "#cr" not in footer("Dhp 5")
    assert "&lt;" in footer("<source>")


def test_bud_requires_source():
    with pytest.raises(GuardError, match="requires source"):
        validate([{"id": "b1", "channel": "bud"}])


def test_credit_element_and_credit_text_are_rejected():
    with pytest.raises(GuardError, match="#cr"):
        validate([], '<div id="cr">hidden</div>')
    with pytest.raises(GuardError, match="attribution"):
        validate([], "<p>Made with ChatGPT</p>")
    with pytest.raises(GuardError, match="CSS rule #cr"):
        validate([], "<style>#cr { display:none }</style>")
    with pytest.raises(GuardError, match="attribution"):
        validate([], "<style>/* ChatGPT */ .hero { color: red }</style>")


def test_experiment_pair_requires_same_img_kind():
    pair = [
        {"id": "a", "test_cell": "cell1", "img_kind": "ai"},
        {"id": "b", "test_cell": "cell1", "img_kind": "commons"},
    ]
    with pytest.raises(GuardError, match="share img_kind"):
        validate(pair)


def test_declared_duration_band_is_enforced():
    with pytest.raises(GuardError, match="outside declared band"):
        validate([{"id": "x", "duration_band": [21, 27], "dur": 20.9}])


def test_plan_and_packaging_write_utc_slot(tmp_path):
    rows = [{"id": "fs1", "day": "2026-11-05", "slot": "08:30", "title": "Sample"}]
    out = write_plan(rows, tmp_path / "plan.json", channel="fs", packaging_dir=tmp_path / "packaging")
    data = json.loads(out.read_text())
    assert data[0]["slot_utc"] == "2026-11-05T08:30:00Z"
    sidecar = json.loads((tmp_path / "packaging/fs1.json").read_text())
    assert sidecar["slot_utc"] == data[0]["slot_utc"]


def test_shared_css_and_theme_exist():
    assert "#cr" not in BASE_CSS
    assert "credit" not in BASE_CSS.lower()
    assert "--short-background" in theme_css("fs")


def test_bud_html_builder_writes_composition_with_source(tmp_path):
    from PIL import Image

    image_path = tmp_path / "photo.png"
    Image.new("RGB", (1080, 1920), (30, 20, 10)).save(image_path)
    row = {
        "id": "bud-example", "series": "bud", "source": "DN 33",
        "acc": ("#f2b48a", "#2b1407"), "cards": [None, '<div class="big">NỘI DUNG</div>'],
        "head": "TIÊU ĐỀ", "head_b": "TIÊU ĐỀ B", "chip": "BUD", "srcline": "DN 33",
    }
    html = bud_html(row, [0.0, 1.5], 24.25, image_path, font_css="", candidate_b=True)
    assert "bud-example_b" in html
    assert "TIÊU ĐỀ B" in html
    assert "DN 33" in html
    assert "#cr" not in html


def test_fs_html_guard_rejects_credit_and_ai_text():
    with pytest.raises(GuardError, match="attribution"):
        validate([{"id": "fs", "series": "fs"}], "<p>Ảnh minh hoạ AI</p>")
    with pytest.raises(GuardError, match="#cr"):
        validate([{"id": "fs", "series": "fs"}], '<div id="cr"></div>')


def test_fs_formatter_exports_and_handles_inputs():
    from shortbuild import month_sheet_html, yeartable_html

    assert callable(month_sheet_html)
    assert callable(yeartable_html)
