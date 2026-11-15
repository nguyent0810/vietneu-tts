"""Khói cho builder Short W47/W48: dữ liệu khớp, composition qua cổng M7 (không chạy TTS/render)."""
import importlib.util
from pathlib import Path

import pytest

from shortbuild import validate

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "builders/short" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_list3_items_khop_va_qua_cong():
    b = _load("build_063_bud_list3")
    assert b.ROOT == ROOT
    assert len(b.ITEMS) == 6
    for it in b.ITEMS:
        assert len(it["script"]) == len(it["scene_img"]) == len(it["visual_caption"]), it["id"]
        it = dict(it, dur=28.0, scene_times=[i * 3.5 + .5 for i in range(len(it["script"]))] + [27.7])
        html = b.composition(it) if all((ROOT / p).exists() for p in it["scene_img"]) else ""
        if html:
            assert "const T=[]" not in html
        validate([it], html)


def test_list3_scene_times_lay_tu_giong():
    b = _load("build_063_bud_list3")
    it = dict(b.ITEMS[0], dur=28.0, scene_times=[0.5, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 27.7])
    if not all((ROOT / p).exists() for p in it["scene_img"]):
        pytest.skip("ảnh AI chỉ có trên máy dựng")
    html = b.composition(it)
    starts = [float(x) for x in __import__("re").findall(r'tl\.fromTo\("#s\d+",\{opacity:0,y:28\},\{opacity:1,y:0,duration:\.4\},([0-9.]+)\)', html)]
    assert starts == it["scene_times"][:-1]


def test_fs_w47_builder_import_va_root():
    b = _load("build_061_fs_w47")
    assert b.ROOT == ROOT
