"""Cổng 3 giây đầu của Short (`build.py --preflight`, hook_errors): mỗi luật một ca đạt và một ca hỏng."""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
import build as B  # noqa: E402

GOOD = {
    "title": "Vụ án bồn tắm của George Smith",
    "kicker": "HỒ SƠ 1915", "sub": "GEORGE SMITH",
    "lines": ["Ba cái chết giống nhau trong bồn tắm.", "Cảnh sát Anh bắt giữ George Smith."],
    "imgs": {"i0": "local:bright.png"},
    "scenes": [{"type": "photo", "img": "i0", "label": "NGHI PHẠM"}, {"type": "kinetic", "at": 1, "items": [{"text": "A", "at": 1}]}],
}


def run(tmp_path, **patch):
    from PIL import Image
    Image.new("RGB", (32, 32), (200, 200, 200)).save(tmp_path / "i0.jpg")
    Image.new("RGB", (32, 32), (5, 5, 5)).save(tmp_path / "dark.jpg")
    spec = copy.deepcopy(GOOD)
    spec.update(patch)
    return B.hook_errors(spec, assets_dir=tmp_path, slug="t")


def has(errs, frag):
    return any(frag in e for e in errs)


def test_good_spec_passes(tmp_path):
    assert run(tmp_path) == []


def test_a_text_only_first_scene_fails(tmp_path):
    bad = [{"type": "kinetic", "items": [{"text": "A", "at": 0}]}]
    assert has(run(tmp_path, scenes=bad), "chỉ có chữ")
    ok = [{"type": "kinetic", "bg": "x.jpg", "items": [{"text": "A", "at": 0}]}]
    assert not has(run(tmp_path, scenes=ok), "chỉ có chữ")
    assert not has(run(tmp_path, scenes=[{"type": "counter", "to": 5}]), "chỉ có chữ")


def test_b_dark_first_image_fails(tmp_path):
    dark = run(tmp_path, imgs={"dark": "File:x.jpg"}, scenes=[{"type": "photo", "img": "dark", "label": "X"}])
    assert has(dark, "quá tối")
    assert not has(run(tmp_path), "quá tối")


def test_c_first_line_rules(tmp_path):
    long_line = ["Một hai ba bốn năm sáu bảy tám chín mười George Smith."]
    assert has(run(tmp_path, lines=long_line), "dài")
    assert not has(run(tmp_path), "dài")
    # không số, không từ khoá của tiêu đề
    assert has(run(tmp_path, lines=["Chuyện kể rằng mọi thứ rất kỳ lạ."]), "từ khoá")
    # số bằng chữ hoặc chữ số đều qua
    assert not has(run(tmp_path, lines=["Chuyện kể về 3 người lạ."]), "từ khoá")
    assert not has(run(tmp_path, lines=["Chuyện kể về hai người lạ."]), "từ khoá")
    # từ khoá của tiêu đề (George) qua
    assert not has(run(tmp_path, lines=["George làm gì đêm đó?"]), "từ khoá")


def test_d_on_screen_hook_text_required(tmp_path):
    assert has(run(tmp_path, kicker="", sub="", scenes=[{"type": "photo", "img": "i0"}]), "chữ hook")
    assert not has(run(tmp_path, kicker="", sub="", scenes=[{"type": "photo", "img": "i0", "label": "NGHI PHẠM"}]), "chữ hook")
    assert not has(run(tmp_path), "chữ hook")


def test_e_timing(tmp_path):
    late_scene = [{"type": "photo", "img": "i0", "at": [0, None, 0, 0.8], "label": "X"}]
    assert has(run(tmp_path, scenes=late_scene), "phải bắt đầu ở 0,0s")
    late_text = [{"type": "hero", "img": "i0", "head": "A B", "headAt": 1.2}]
    assert has(run(tmp_path, scenes=late_text), "chữ đầu")
    early = [{"type": "hero", "img": "i0", "head": "A B", "headAt": 0.3}]
    assert not has(run(tmp_path, scenes=early), "chữ đầu")
    assert not has(run(tmp_path, scenes=[{"type": "photo", "img": "i0", "at": 0, "label": "X"}]), "phải bắt đầu")
