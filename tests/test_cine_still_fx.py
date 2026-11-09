"""Tests cho 024: Ảnh điện ảnh (cine still + 2.5D depth + FX + grade + transition_in) ở cold open Long."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

import hyperframes_bridge as HB
from hyperframes_bridge import (
    CINE_CAMS,
    CINE_FX,
    CINE_GRADES,
    CINE_TRANSITIONS,
    HyperFramesError,
    copy_cine,
    motion_layout,
    parse_cine,
    validate_cine,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_asset_gate():
    gate_path = ROOT / "output/cl_staging/long/asset_gate.py"
    if not gate_path.exists():  # output/ nằm ngoài git: chỉ có trên máy staging
        pytest.skip("asset_gate.py chỉ có trên máy staging (output/ bị gitignore)")
    spec = importlib.util.spec_from_file_location("asset_gate", gate_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_parse_cine_none_preserves_old_plan():
    assert parse_cine(None) is None
    assert validate_cine(None) is None
    media_out = {"query": "local:a.png", "reveal": "", "layout": "full"}
    assert copy_cine(media_out, {"kind": "local", "path": "a.png"}) is None
    assert "cine" not in media_out


@pytest.mark.parametrize("cam", CINE_CAMS)
def test_parse_cine_all_cameras(cam: str):
    out = parse_cine({"cam": cam, "depth": True, "fx": ["dust"]})
    assert out is not None
    assert out["cam"] == cam
    assert out["depth"] is True
    assert out["fx"] == ["dust"]
    assert out["intensity"] == 0.75
    assert out["transition_in"] == "cut"


@pytest.mark.parametrize("fx_name", CINE_FX)
def test_parse_cine_all_fx(fx_name: str):
    out = parse_cine({"cam": "push_in", "depth": True, "fx": [fx_name]})
    assert out is not None
    assert out["fx"] == [fx_name]


@pytest.mark.parametrize("grade", CINE_GRADES)
def test_parse_cine_all_grades(grade: str):
    out = parse_cine({"cam": "push_in", "grade": grade, "intensity": 0.6})
    assert out is not None
    assert out["grade"] == grade
    assert out["intensity"] == 0.6


@pytest.mark.parametrize("tr", CINE_TRANSITIONS)
def test_parse_cine_all_transitions(tr: str):
    out = parse_cine({"cam": "push_in", "transition_in": tr})
    assert out is not None
    assert out["transition_in"] == tr


def test_parse_cine_fx_dedup_and_max_three():
    out = parse_cine({"fx": ["fog", "mist_drift", "fog", "god_rays"]})
    assert out is not None
    assert out["fx"] == ["fog", "mist_drift", "god_rays"]

    with pytest.raises(HyperFramesError, match="tối đa 3 lớp"):
        parse_cine({"fx": ["fog", "mist_drift", "god_rays", "dust"]})


@pytest.mark.parametrize(
    "bad_input",
    [
        "not_a_dict",
        ["push_in"],
        {"unknown_key": 1},
        {"cam": "orbit_360"},
        {"depth": "yes"},
        {"depth": 1},
        {"fx": "fog"},
        {"fx": ["unknown_fx"]},
        {"grade": "neon"},
        {"intensity": -0.1},
        {"intensity": 1.05},
        {"intensity": True},
        {"intensity": "0.5"},
        {"transition_in": "star_wipe"},
    ],
)
def test_parse_cine_rejects_invalid(bad_input):
    with pytest.raises(HyperFramesError):
        parse_cine(bad_input)


def test_motion_layout_upgrades_to_depth_when_cine_depth_true():
    spec = {"kind": "local", "path": "a.png", "layout": "full", "cine": {"cam": "push_in", "depth": True, "fx": ["dust"]}}
    assert motion_layout("full", spec, tall=False) == "depth"
    assert motion_layout("", spec, tall=False) == "depth"
    # Ảnh dọc vẫn giữ quy tắc né full/depth để không cắt đầu
    assert motion_layout("pinned", spec, tall=True) == "pinned"
    # Không khai cine -> giữ nguyên hành vi cũ
    assert motion_layout("full", {"kind": "local", "path": "a.png", "layout": "full"}, tall=False) == "full"


def test_asset_gate_accepts_cine_stills_with_depth_and_fx(tmp_path: Path):
    ag = _load_asset_gate()
    assert ag.is_cold_cine({"cine": {"depth": True, "fx": ["fog"]}}, "a.png") is True
    assert ag.is_cold_cine({"cine": {"depth": False, "fx": ["fog"]}}, "a.png") is False
    assert ag.is_cold_cine({"cine": {"depth": True, "fx": []}}, "a.png") is False
    assert ag.is_cold_cine({}, "clip.mp4") is True
    assert ag.is_cold_cine({}, "still.png") is False

    # Kiểm trực tiếp plan_P1_temiya.json
    p1 = ROOT / "output/cl_staging/long/plan_P1_temiya.json"
    if p1.exists():
        assert ag.check(p1) == []


def test_js_and_css_cine_contracts():
    js_long = ROOT / "hyperframes_short/compositions/longform.js"
    js_eng = ROOT / "hyperframes_short/compositions/engine.js"
    css_long = (ROOT / "hyperframes_short/compositions/longform.css").read_text(encoding="utf-8")

    for js_file in (js_long, js_eng):
        res = subprocess.run(["node", "--check", str(js_file)], capture_output=True, text=True)
        assert res.returncode == 0, res.stderr

    for fx in CINE_FX:
        assert f"lf-cine-fx-{fx}" in css_long
    for grade in CINE_GRADES:
        assert f"lf-cine-grade-{grade}" in css_long
    for cls in ("lf-cine-trans-flash", "lf-cine-trans-black", "lf-cine-trans-whip"):
        assert cls in css_long
