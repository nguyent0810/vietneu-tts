"""Tests cho Task 028: Toàn cảnh quét ngang (panorama pan 3840×1080)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import hyperframes_bridge as HB
from hyperframes_bridge import (
    CINE_FX,
    PAN_DIRS,
    PAN_EASES,
    PAN_HOLD_MAX_S,
    PAN_SPEED_MAX,
    HyperFramesError,
    copy_pan,
    interpolate_pan_x,
    motion_layout,
    pan_hold_duration,
    pan_speed_check,
    parse_pan,
    validate_pan,
)

ROOT = Path(__file__).resolve().parents[1]


def test_parse_pan_none_returns_none():
    assert parse_pan(None) is None
    assert validate_pan(None) is None
    media_out = {"query": "local:wide.png", "layout": "full"}
    assert copy_pan(media_out, {"kind": "local", "path": "wide.png"}) is None
    assert "pan" not in media_out


def test_parse_pan_defaults():
    raw = {
        "dir": "ltr",
        "stops": [{"line": 1, "x": 0.0}, {"line": 2, "x": 0.5}, {"line": 3, "x": 1.0}],
    }
    out = parse_pan(raw)
    assert out is not None
    assert out["dir"] == "ltr"
    assert len(out["stops"]) == 3
    assert out["stops"][0] == {"line": 1, "x": 0.0}
    assert out["stops"][1] == {"line": 2, "x": 0.5}
    assert out["stops"][2] == {"line": 3, "x": 1.0}
    assert out["ease"] == "inOut"
    assert out["depth"] is False
    assert out["fx"] == []
    assert out["intensity"] == 0.75
    assert out["transition_in"] == "cut"


def test_parse_pan_with_depth_fx_grade():
    raw = {
        "dir": "rtl",
        "stops": [{"line": 2, "x": 0.9, "at": "start"}, {"line": 4, "x": 0.1, "at": "end"}],
        "ease": "sine.inOut",
        "depth": True,
        "fx": ["mist_drift", "dust", "mist_drift"],  # có trùng lặp để dedup
        "grade": "warm",
        "intensity": 0.85,
        "transition_in": "flash_white",
        "end_x": 0.0,
    }
    out = parse_pan(raw)
    assert out is not None
    assert out["dir"] == "rtl"
    assert out["depth"] is True
    assert out["fx"] == ["mist_drift", "dust"]  # đã dedup
    assert out["grade"] == "warm"
    assert out["intensity"] == 0.85
    assert out["transition_in"] == "flash_white"
    assert out["end_x"] == 0.0


@pytest.mark.parametrize(
    "bad_input",
    [
        "not_a_dict",
        123,
        [],
        {"unknown_key": 1},
        {"dir": "diagonal", "stops": [{"line": 1, "x": 0.0}]},
        {"stops": []},
        {"stops": "not_a_list"},
        {"stops": [{"line": 0, "x": 0.0}]},  # line < 1
        {"stops": [{"line": -1, "x": 0.0}]},
        {"stops": [{"line": "abc", "x": 0.0}]},
        {"stops": [{"line": 2, "x": 0.0}, {"line": 1, "x": 0.5}]},  # line không tăng dần
        {"stops": [{"line": 1, "x": -0.1}]},  # x < 0
        {"stops": [{"line": 1, "x": 1.05}]},  # x > 1
        {"stops": [{"line": 1, "x": "half"}]},
        {"stops": [{"line": 1, "x": 0.0, "at": "middle"}]},  # at lạ
        {"stops": [{"line": 1, "x": 0.0}], "ease": "bounce"},
        {"stops": [{"line": 1, "x": 0.0}], "depth": "yes"},
        {"stops": [{"line": 1, "x": 0.0}], "fx": ["non_existent_fx"]},
        {"stops": [{"line": 1, "x": 0.0}], "fx": ["dust", "fog", "rain", "embers"]},  # > 3 lớp
        {"stops": [{"line": 1, "x": 0.0}], "grade": "sepia_vintage"},
        {"stops": [{"line": 1, "x": 0.0}], "intensity": 1.5},
        {"stops": [{"line": 1, "x": 0.0}], "transition_in": "circle_wipe"},
        {"stops": [{"line": 1, "x": 0.0}], "end_x": -0.2},
    ],
)
def test_parse_pan_rejects_invalid(bad_input):
    with pytest.raises(HyperFramesError):
        parse_pan(bad_input)


def test_interpolate_pan_x_exact_stops():
    pan_spec = {
        "dir": "ltr",
        "stops": [
            {"line": 1, "x": 0.0},
            {"line": 2, "x": 0.45},
            {"line": 3, "x": 0.85},
        ],
        "ease": "inOut",
        "end_x": 1.0,
    }
    line_times = [
        {"sentence_id": 1, "start": 0.0, "end": 5.0},
        {"sentence_id": 2, "start": 5.0, "end": 10.0},
        {"sentence_id": 3, "start": 10.0, "end": 15.0},
    ]

    # Kiểm tra ĐÚNG lúc bắt đầu từng câu, toạ độ x phải chính xác bằng stop.x
    assert interpolate_pan_x(pan_spec, 0.0, line_times) == 0.0
    assert interpolate_pan_x(pan_spec, 5.0, line_times) == 0.45
    assert interpolate_pan_x(pan_spec, 10.0, line_times) == 0.85
    assert interpolate_pan_x(pan_spec, 15.0, line_times) == 1.0

    # Trước t0 và sau tend
    assert interpolate_pan_x(pan_spec, -1.0, line_times) == 0.0
    assert interpolate_pan_x(pan_spec, 20.0, line_times) == 1.0

    # Tại trung điểm từng đoạn phải nội suy mượt và tăng dần
    x_mid1 = interpolate_pan_x(pan_spec, 2.5, line_times)
    assert 0.0 < x_mid1 < 0.45
    assert abs(x_mid1 - 0.225) < 0.01  # inOut tại u=0.5 đạt 0.5 đoạn

    x_mid2 = interpolate_pan_x(pan_spec, 7.5, line_times)
    assert 0.45 < x_mid2 < 0.85


def test_interpolate_pan_x_linear():
    pan_spec = {
        "dir": "ltr",
        "stops": [{"line": 1, "x": 0.0}, {"line": 2, "x": 1.0}],
        "ease": "linear",
    }
    line_times = {
        1: (0.0, 10.0),
        2: (10.0, 15.0),
    }
    assert interpolate_pan_x(pan_spec, 0.0, line_times) == 0.0
    assert interpolate_pan_x(pan_spec, 5.0, line_times) == 0.5
    assert interpolate_pan_x(pan_spec, 10.0, line_times) == 1.0


def test_pan_speed_check():
    # 3840×1080 -> max_travel_px = 3840 - 1920 = 1920 px
    # Trường hợp 1: Tốc độ an toàn < 180 px/s
    # dx = 0.4 * 1920 = 768 px qua 5s -> speed = 153.6 px/s
    pan_ok = {
        "dir": "ltr",
        "stops": [{"line": 1, "x": 0.0}, {"line": 2, "x": 0.4}],
    }
    times_ok = {1: (0.0, 5.0), 2: (5.0, 10.0)}
    warns = pan_speed_check(pan_ok, times_ok, iw=3840, ih=1080)
    assert len(warns) == 0

    # Trường hợp 2: Tốc độ vượt 180 px/s
    # dx = 0.8 * 1920 = 1536 px qua 3s -> speed = 512.0 px/s
    pan_fast = {
        "dir": "ltr",
        "stops": [{"line": 1, "x": 0.0}, {"line": 2, "x": 0.8}],
    }
    times_fast = {1: (0.0, 3.0), 2: (3.0, 6.0)}
    warns_fast = pan_speed_check(pan_fast, times_fast, iw=3840, ih=1080)
    assert len(warns_fast) == 1
    assert "vượt mức khuyến nghị ~180 px/s" in warns_fast[0]


def test_pan_hold_duration():
    # Hợp lệ <= 20s
    pan_spec = {
        "dir": "ltr",
        "stops": [{"line": 1, "x": 0.0}, {"line": 3, "x": 1.0}],
    }
    times_valid = [
        {"sentence_id": 1, "start": 0.0, "end": 5.0},
        {"sentence_id": 2, "start": 5.0, "end": 10.0},
        {"sentence_id": 3, "start": 10.0, "end": 15.0},
    ]
    dur = pan_hold_duration(pan_spec, times_valid)
    assert dur == 15.0

    # Quá 20s -> LỖI
    times_too_long = [
        {"sentence_id": 1, "start": 0.0, "end": 10.0},
        {"sentence_id": 2, "start": 10.0, "end": 20.0},
        {"sentence_id": 3, "start": 20.0, "end": 25.0},  # tổng 25s
    ]
    with pytest.raises(HyperFramesError, match="vượt tối đa 20s"):
        pan_hold_duration(pan_spec, times_too_long)


def test_motion_layout_pan():
    spec_depth = {"kind": "local", "path": "p.png", "pan": {"depth": True, "stops": [{"line": 1, "x": 0}]}}
    spec_nodepth = {"kind": "local", "path": "p.png", "pan": {"depth": False, "stops": [{"line": 1, "x": 0}]}}

    assert motion_layout("full", spec_depth, tall=False) == "depth"
    assert motion_layout("", spec_depth, tall=False) == "depth"
    assert motion_layout("full", spec_nodepth, tall=False) == "full"
    assert motion_layout("", spec_nodepth, tall=False) == "full"

    # Ảnh dọc bảo vệ không cắt đầu
    assert motion_layout("pinned", spec_depth, tall=True) == "pinned"


def test_js_and_css_pan_contracts():
    js_long = ROOT / "hyperframes_short/compositions/longform.js"
    js_eng = ROOT / "hyperframes_short/compositions/engine.js"
    css_long = (ROOT / "hyperframes_short/compositions/longform.css").read_text(encoding="utf-8")

    for js_file in (js_long, js_eng):
        res = subprocess.run(["node", "--check", str(js_file)], capture_output=True, text=True)
        assert res.returncode == 0, res.stderr

    assert ".media-clip.media-pan" in css_long
    assert '[data-pan="1"]' in css_long
    assert "pan: runPan" in js_long.read_text(encoding="utf-8")


def test_pano_stitch_dimensions():
    from output.cl_staging.long.pano_stitch import stitch_panorama

    img1 = ROOT / "output/cl_staging/long/research/ai_media/p1_temiya_v2/co_hero_169.png"
    img2 = ROOT / "output/cl_staging/long/research/ai_media/p1_temiya_v2/pit_169.png"
    if img1.exists() and img2.exists():
        res = stitch_panorama(img1, img2, overlap=0.20, mode="multiband")
        assert res.width == 3840
        assert res.height == 1080
