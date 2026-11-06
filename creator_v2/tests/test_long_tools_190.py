"""GH-190: các lỗ hổng công cụ Long lộ ra khi dựng Bao Thanh Thiên (#179)."""
import importlib.util
import sys
from pathlib import Path

LONG = Path(__file__).resolve().parents[1] / "motion" / "long"


def _load(name):
    spec = importlib.util.spec_from_file_location(f"gh190_{name}", LONG / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path[:0] = [str(LONG), str(LONG.parents[1])]
    spec.loader.exec_module(mod)
    return mod


SP = _load("scene_params")
LH = _load("lint_html")


def _errors(scenes, imgs):
    return SP.validate_topic([("ch13", scenes)], imgs, None)["errors"]


def test_endcard_may_run_20s_but_not_past_25s():
    ok = _errors([{"type": "endcard", "t0": 0, "t1": 20}], {})
    long = _errors([{"type": "endcard", "t0": 0, "t1": 25.5}], {})
    assert not any("thời lượng" in e for e in ok)
    assert any("thời lượng" in e for e in long)


def test_other_scenes_keep_9s_cap():
    errs = _errors([{"type": "photo", "t0": 0, "t1": 20, "img": "a"}], {"a": "File:a.jpg"})
    assert any("thời lượng" in e for e in errs)


def test_scene_image_missing_from_spec_imgs_is_blocked_with_location():
    errs = _errors([{"type": "date", "t0": 0, "t1": 4, "bg": "pag215"}], {"pag218": "File:x.jpg"})
    assert any("pag215" in e and "chưa khai báo" in e and "ch13#0" in e for e in errs)


def test_declared_scene_image_passes():
    errs = _errors([{"type": "date", "t0": 0, "t1": 4, "bg": "pag218"}], {"pag218": "File:x.jpg"})
    assert not any("chưa khai báo" in e for e in errs)


def test_nested_pin_image_is_checked():
    errs = _errors([{"type": "map", "t0": 0, "t1": 4, "pins": [{"img": "ghost"}]}], {})
    assert any("ghost" in e and "chưa khai báo" in e for e in errs)


def test_missing_font_gives_one_line_hint_not_traceback(tmp_path, monkeypatch):
    monkeypatch.setattr(LH, "FONT_DIR", tmp_path)
    scenes = [{"type": "file", "t0": 0, "t1": 4, "name": "HỒ SƠ", "stamp": {"text": "MẬT"}}]
    out = LH.check_scenes("ch01", scenes)
    assert any("thiếu font" in line and "google/fonts" in line for line in out)


def test_stt_takes_no_hardcoded_cuda_or_venv():
    src = (LONG / "stt_takes.py").read_text(encoding="utf-8")
    assert ".venv-video" not in src
    assert 'device="cuda"' not in src
    assert '("cpu", "int8")' in src
