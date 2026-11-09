"""Tests cho Task 028c: Máy bám nhân vật (tracking layers) bằng 2 ảnh -- nền sạch + nhân vật PNG alpha.
"""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
from PIL import Image
import pytest

import hyperframes_bridge as HB
from hyperframes_bridge import (
    HyperFramesError,
    compute_follow_camera_pan,
    copy_pan,
    interpolate_layer_bob,
    interpolate_layer_sway,
    interpolate_layer_track,
    match_color,
    parse_layers,
    parse_pan,
    validate_layers,
)


def test_parse_layers_none_or_empty():
    assert parse_layers(None) == []
    assert parse_layers([]) == []
    assert validate_layers(None) == []


def test_parse_layers_full_valid():
    raw = [
        {
            "path": "assets/horse.png",
            "fps": 4,
            "track": [
                {"line": 1, "x": 0.1, "y": 0.7, "scale": 0.4},
                {"line": 2, "x": 0.5, "y": 0.72, "scale": 0.5},
                {"line": 3, "x": 0.9, "y": 0.75, "scale": 0.6},
            ],
            "bob": {"px": 3.5, "hz": 1.6},
            "sway": {"deg": 1.2, "hz": 0.8},
            "shadow": {"light": "right", "opacity": 0.5},
            "water": False,
            "match_color": True,
            "follow": True,
            "light": "right",
            "opacity": 0.95,
        }
    ]
    out = parse_layers(raw)
    assert len(out) == 1
    lyr = out[0]
    assert lyr["path"] == "assets/horse.png"
    assert len(lyr["track"]) == 3
    assert lyr["track"][0] == {"line": 1, "x": 0.1, "y": 0.7, "scale": 0.4}
    assert lyr["track"][1] == {"line": 2, "x": 0.5, "y": 0.72, "scale": 0.5}
    assert lyr["track"][2] == {"line": 3, "x": 0.9, "y": 0.75, "scale": 0.6}
    assert lyr["bob"] == {"px": 3.5, "hz": 1.6}
    assert lyr["sway"] == {"deg": 1.2, "hz": 0.8}
    assert lyr["shadow"] == {"light": "right", "opacity": 0.5}
    assert lyr["water"] is False
    assert lyr["match_color"] is True
    assert lyr["follow"] is True
    assert lyr["light"] == "right"
    assert lyr["opacity"] == 0.95


def test_parse_layers_path_frames():
    raw = {
        "path_frames": ["frame1.png", "frame2.png", "frame3.png"],
        "fps": 6,
        "track": [{"line": 1, "x": 0.2, "y": 0.8, "scale": 1.0}],
    }
    out = parse_layers(raw)
    assert len(out) == 1
    assert out[0]["path_frames"] == ["frame1.png", "frame2.png", "frame3.png"]
    assert out[0]["fps"] == 6.0


def test_parse_layers_rejects_invalid_keys():
    with pytest.raises(HyperFramesError, match="khoá lạ"):
        parse_layers([{"path": "a.png", "unknown_prop": 123, "track": [{"line": 1, "x": 0.5, "y": 0.5}]}])


def test_parse_layers_rejects_missing_path():
    with pytest.raises(HyperFramesError, match="cần có path"):
        parse_layers([{"track": [{"line": 1, "x": 0.5, "y": 0.5}]}])


def test_parse_layers_rejects_invalid_track():
    # Non-increasing line
    with pytest.raises(HyperFramesError, match="tăng dần"):
        parse_layers([{
            "path": "a.png",
            "track": [
                {"line": 2, "x": 0.2, "y": 0.5},
                {"line": 1, "x": 0.3, "y": 0.5},
            ],
        }])

    # Out of bounds x
    with pytest.raises(HyperFramesError, match="ngoài khoảng 0.0..1.0"):
        parse_layers([{
            "path": "a.png",
            "track": [{"line": 1, "x": 1.5, "y": 0.5}],
        }])

    # Out of bounds scale (<0.2 or >1.5)
    with pytest.raises(HyperFramesError, match="ngoài khoảng 0.2..1.5"):
        parse_layers([{
            "path": "a.png",
            "track": [{"line": 1, "x": 0.5, "y": 0.5, "scale": 0.1}],
        }])
    with pytest.raises(HyperFramesError, match="ngoài khoảng 0.2..1.5"):
        parse_layers([{
            "path": "a.png",
            "track": [{"line": 1, "x": 0.5, "y": 0.5, "scale": 2.0}],
        }])


def test_parse_layers_shadow_and_water_toggle():
    # Shadow True default
    out1 = parse_layers([{"path": "a.png", "shadow": True, "light": "left", "track": [{"line": 1, "x": 0.5, "y": 0.5}]}])
    assert out1[0]["shadow"] == {"light": "left", "opacity": 0.45}
    assert out1[0]["water"] is False

    # Water True
    out2 = parse_layers([{"path": "a.png", "water": True, "shadow": False, "track": [{"line": 1, "x": 0.5, "y": 0.5}]}])
    assert out2[0]["shadow"] is False
    assert out2[0]["water"] is True


def test_interpolate_layer_track():
    layer = {
        "track": [
            {"line": 1, "x": 0.1, "y": 0.4, "scale": 0.5},
            {"line": 2, "x": 0.5, "y": 0.6, "scale": 1.0},
            {"line": 3, "x": 0.9, "y": 0.8, "scale": 1.2},
        ]
    }
    line_times = {
        1: (0.0, 3.0),
        2: (3.0, 6.0),
        3: (6.0, 9.0),
    }

    # At start t=0
    p0 = interpolate_layer_track(layer, 0.0, line_times)
    assert p0["x"] == 0.1
    assert p0["y"] == 0.4
    assert p0["scale"] == 0.5

    # At mid segment 1 (t=1.5)
    pm = interpolate_layer_track(layer, 1.5, line_times)
    assert 0.1 < pm["x"] < 0.5
    assert 0.4 < pm["y"] < 0.6
    assert 0.5 < pm["scale"] < 1.0

    # At boundary t=3.0
    p1 = interpolate_layer_track(layer, 3.0, line_times)
    assert p1["x"] == 0.5
    assert p1["y"] == 0.6
    assert p1["scale"] == 1.0

    # At end t=6.0
    p2 = interpolate_layer_track(layer, 6.0, line_times)
    assert p2["x"] == 0.9
    assert p2["y"] == 0.8
    assert p2["scale"] == 1.2


def test_compute_follow_camera_pan_ltr():
    # Character moves from left (0.2) to right (0.8) on 3840px panorama
    layer = {
        "track": [
            {"line": 1, "x": 0.2, "y": 0.7, "scale": 0.5},
            {"line": 2, "x": 0.8, "y": 0.7, "scale": 0.5},
        ]
    }
    pan = compute_follow_camera_pan(layer, bg_w=3840, bg_h=1080, viewport_w=1920)
    assert pan["dir"] == "ltr"
    stops = pan["stops"]
    assert len(stops) == 2
    # At start: char_x = 0.2 * 3840 = 768px.
    # Target 1/3 viewport = 640px.
    # cam_x = 768 - 640 = 128px.
    # pan_x = 128 / (3840 - 1920) = 128 / 1920 = 0.0667
    assert 0.06 <= stops[0]["x"] <= 0.08

    # At end: char_x = 0.8 * 3840 = 3072px.
    # cam_x = 3072 - 640 = 2432px -> clamped to 1920px -> pan_x = 1.0
    assert stops[1]["x"] == 1.0


def test_compute_follow_camera_pan_rtl():
    # Character moves from right (0.8) to left (0.2)
    layer = {
        "track": [
            {"line": 1, "x": 0.8, "y": 0.7, "scale": 0.5},
            {"line": 2, "x": 0.2, "y": 0.7, "scale": 0.5},
        ]
    }
    pan = compute_follow_camera_pan(layer, bg_w=3840, bg_h=1080, viewport_w=1920)
    assert pan["dir"] == "rtl"
    stops = pan["stops"]
    assert len(stops) == 2
    # RTL target is 2/3 viewport = 1280px.
    # char_x = 0.8 * 3840 = 3072px.
    # cam_x = 3072 - 1280 = 1792px.
    # pan_x = 1792 / 1920 = 0.9333
    assert 0.90 <= stops[0]["x"] <= 0.95


def test_interpolate_layer_bob():
    bob = {"px": 4.0, "hz": 2.0}
    # t=0 -> sin(0) = 0
    assert interpolate_layer_bob(bob, 0.0) == 0.0
    # t = 1/(4*hz) = 1/8 = 0.125 -> sin(pi/2) = 1 -> 4.0
    assert math.isclose(interpolate_layer_bob(bob, 0.125), 4.0, abs_tol=0.01)
    # Disabled
    assert interpolate_layer_bob(None, 0.5) == 0.0


def test_interpolate_layer_sway():
    sway = {"deg": 2.0, "hz": 1.0}
    # t=0 -> 0
    assert interpolate_layer_sway(sway, 0.0) == 0.0
    # t=0.25 -> sin(pi/2) = 1 -> 2.0
    assert math.isclose(interpolate_layer_sway(sway, 0.25), 2.0, abs_tol=0.01)
    # Disabled
    assert interpolate_layer_sway(None, 0.5) == 0.0


def test_match_color_preserves_alpha():
    # Create RGBA layer with complex alpha gradient & details
    h, w = 80, 80
    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((x - 40) ** 2 + (y - 40) ** 2)
    alpha = np.clip((35 - dist) * 10, 0, 255).astype(np.uint8)

    # Initial layer RGB (bright yellow/white)
    r = np.full((h, w), 250, dtype=np.uint8)
    g = np.full((h, w), 240, dtype=np.uint8)
    b = np.full((h, w), 220, dtype=np.uint8)
    layer_im = Image.fromarray(np.dstack([r, g, b, alpha]))

    # Background (dark moody blue/indigo)
    bg_im = Image.new("RGB", (w, h), (15, 25, 60))

    orig_alpha = np.array(layer_im.split()[3], copy=True)

    matched = match_color(layer_im, bg_im, defringe_px=2, light_wrap=0.15)
    res_alpha = np.array(matched.split()[3])

    # RULE CHECK: Alpha channel must be 100% strictly identical
    assert np.array_equal(res_alpha, orig_alpha), "Alpha channel was altered by match_color!"

    # RGB should be darkened/shifted toward the dark blue background
    res_arr = np.array(matched)
    core = (orig_alpha > 200)
    assert res_arr[core, 0].mean() < 250  # Red reduced
    assert res_arr[core, 2].mean() > 10   # Blue presence maintained/adjusted


def test_parse_pan_with_layers():
    spec = {
        "dir": "ltr",
        "stops": [{"line": 1, "x": 0.0}],
        "layers": [
            {
                "path": "horse.png",
                "track": [{"line": 1, "x": 0.1, "y": 0.7}],
                "bob": 3,
                "shadow": True,
            }
        ]
    }
    out = parse_pan(spec)
    assert out is not None
    assert "layers" in out
    assert len(out["layers"]) == 1
    assert out["layers"][0]["bob"] == {"px": 3.0, "hz": 1.6}
    assert out["layers"][0]["shadow"] == {"light": "top", "opacity": 0.45}


def test_copy_pan_with_layers():
    media_out = {}
    spec = {
        "pan": {"stops": [{"line": 1, "x": 0.0}]},
        "layers": [{"path": "boat.png", "track": [{"line": 1, "x": 0.2, "y": 0.8}]}],
    }
    copy_pan(media_out, spec)
    assert "pan" in media_out
    assert "layers" in media_out
    assert media_out["layers"][0]["path"] == "boat.png"
