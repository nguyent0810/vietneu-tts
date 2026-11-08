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
    interpolate_camera,
    interpolate_pan_x,
    interpolate_pan_y,
    interpolate_pan_zoom,
    motion_layout,
    pan_hold_duration,
    pan_speed_check,
    pan_zoom_resolution_check,
    parse_camera,
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


# ==============================================================================
# Tests cho 028b: Mở rộng các kiểu lia (push/pull zoom, vertical tilt, whip, focus_pull, unified camera)
# ==============================================================================

def test_pan_zoom_push_pull_parsing_and_interp():
    # Đẩy vào (push in): zoom 1.0 -> 1.35
    spec_push = {
        "dir": "ltr",
        "stops": [
            {"line": 1, "x": 0.0, "zoom": 1.0},
            {"line": 2, "x": 1.0, "zoom": 1.35},
        ],
        "ease": "linear",
    }
    out = parse_pan(spec_push)
    assert out["stops"][0]["zoom"] == 1.0
    assert out["stops"][1]["zoom"] == 1.35

    times = {1: (0.0, 5.0), 2: (5.0, 10.0)}
    assert interpolate_pan_zoom(out, 0.0, times) == 1.0
    assert interpolate_pan_zoom(out, 2.5, times) == 1.175
    assert interpolate_pan_zoom(out, 5.0, times) == 1.35

    # Kéo lùi (pull out): zoom 1.5 -> 1.0
    spec_pull = {
        "dir": "ltr",
        "stops": [
            {"line": 1, "x": 0.0, "zoom": 1.5},
            {"line": 2, "x": 1.0, "zoom": 1.0},
        ],
        "ease": "linear",
    }
    out_pull = parse_pan(spec_pull)
    assert out_pull["stops"][0]["zoom"] == 1.5
    assert out_pull["stops"][1]["zoom"] == 1.0
    assert interpolate_pan_zoom(out_pull, 0.0, times) == 1.5
    assert interpolate_pan_zoom(out_pull, 2.5, times) == 1.25
    assert interpolate_pan_zoom(out_pull, 5.0, times) == 1.0


def test_pan_zoom_validation_limits():
    # Zoom < 1.0 hoặc > 1.6 ném lỗi
    with pytest.raises(HyperFramesError, match="zoom ngoài khoảng 1.0..1.6"):
        parse_pan({"stops": [{"line": 1, "x": 0.0, "zoom": 0.9}]})
    with pytest.raises(HyperFramesError, match="zoom ngoài khoảng 1.0..1.6"):
        parse_pan({"stops": [{"line": 1, "x": 0.0, "zoom": 1.65}]})
    with pytest.raises(HyperFramesError, match="zoom phải là số"):
        parse_pan({"stops": [{"line": 1, "x": 0.0, "zoom": "extreme"}]})


def test_pan_zoom_resolution_check_warnings():
    # Ảnh 3840×1080: hiển thị cao 1080p -> base_scale = 1.0. Zoom 1.35x -> vượt 1.0 so với pixel gốc -> CẢNH BÁO
    pan_zoom_warn = {
        "stops": [{"line": 1, "x": 0.0, "zoom": 1.0}, {"line": 2, "x": 1.0, "zoom": 1.35}]
    }
    warns = pan_zoom_resolution_check(pan_zoom_warn, iw=3840, ih=1080)
    assert len(warns) == 1
    assert "vượt 1.0 so với pixel gốc" in warns[0]

    # Ảnh 7680×2160 (4K): hiển thị cao 1080p -> base_scale = 0.5. Zoom 1.5x -> 0.75 <= 1.0 -> KHÔNG cảnh báo
    warns_4k = pan_zoom_resolution_check(pan_zoom_warn, iw=7680, ih=2160)
    assert len(warns_4k) == 0


def test_pan_vertical_tilt_axis_v():
    spec_v = {
        "axis": "v",
        "dir": "ttb",
        "stops": [
            {"line": 1, "y": 0.0},
            {"line": 2, "y": 0.5},
            {"line": 3, "y": 1.0},
        ],
        "ease": "inOut",
    }
    out = parse_pan(spec_v)
    assert out["axis"] == "v"
    assert out["dir"] == "ttb"
    assert out["stops"][0]["y"] == 0.0
    assert out["stops"][1]["y"] == 0.5
    assert out["stops"][2]["y"] == 1.0

    times = {1: (0.0, 4.0), 2: (4.0, 8.0), 3: (8.0, 12.0)}
    assert interpolate_pan_y(out, 0.0, times) == 0.0
    assert interpolate_pan_y(out, 4.0, times) == 0.5
    assert interpolate_pan_y(out, 8.0, times) == 1.0

    # Lỗi nếu axis=v nhưng thiếu toạ độ y
    with pytest.raises(HyperFramesError, match="thiếu toạ độ y"):
        parse_pan({"axis": "v", "stops": [{"line": 1}]})
    with pytest.raises(HyperFramesError, match="y ngoài khoảng 0.0..1.0"):
        parse_pan({"axis": "v", "stops": [{"line": 1, "y": 1.5}]})


def test_pan_vertical_tilt_speed_check():
    # Ảnh cao 1080×3240: hiển thị rộng 1920 -> scaled_height = 3240 * (1920/1080) = 5760 px
    # max_travel_y = 5760 - 1080 = 4680 px
    # Trường hợp chậm: dy = 0.1 * 4680 = 468 px qua 4s -> speed = 117 px/s <= 180 px/s (OK)
    spec_ok = {
        "axis": "v",
        "stops": [{"line": 1, "y": 0.0}, {"line": 2, "y": 0.1}],
    }
    times_ok = {1: (0.0, 4.0), 2: (4.0, 8.0)}
    assert len(pan_speed_check(spec_ok, times_ok, iw=1080, ih=3240)) == 0

    # Trường hợp nhanh: dy = 0.5 * 4680 = 2340 px qua 3s -> speed = 780 px/s > 180 px/s (CẢNH BÁO)
    spec_fast = {
        "axis": "v",
        "stops": [{"line": 1, "y": 0.0}, {"line": 2, "y": 0.5}],
    }
    times_fast = {1: (0.0, 3.0), 2: (3.0, 6.0)}
    warns = pan_speed_check(spec_fast, times_fast, iw=1080, ih=3240)
    assert len(warns) == 1
    assert "tốc độ tilt dọc" in warns[0]


def test_pan_whip_transition():
    # Whip pan transition_out và transition_in
    spec_whip = {
        "stops": [{"line": 1, "x": 0.0}, {"line": 2, "x": 1.0}],
        "transition_in": "whip",
        "transition_out": "whip",
    }
    out = parse_pan(spec_whip)
    assert out["transition_in"] == "whip"
    assert out["transition_out"] == "whip"

    with pytest.raises(HyperFramesError, match="transition_out lạ"):
        parse_pan({"stops": [{"line": 1, "x": 0.0}], "transition_out": "zoom_spin"})


def test_pan_focus_pull():
    spec_fp = {
        "depth": True,
        "stops": [{"line": 1, "x": 0.0}, {"line": 3, "x": 1.0}],
        "focus_pull": {"line": 2, "to": "fg", "dur": 1.0},
    }
    out = parse_pan(spec_fp)
    assert out["depth"] is True
    assert len(out["focus_pull"]) == 1
    assert out["focus_pull"][0] == {"line": 2, "to": "fg", "dur": 1.0}

    # Focus pull to bg
    spec_fp_bg = {
        "stops": [{"line": 1, "x": 0.0}],
        "focus_pull": [{"line": 1, "to": "bg", "dur": 0.5}],
    }
    out_bg = parse_pan(spec_fp_bg)
    assert out_bg["focus_pull"][0]["to"] == "bg"

    # Lỗi nếu to không phải fg/bg hoặc dur <= 0
    with pytest.raises(HyperFramesError, match="'to' phải là 'fg' hoặc 'bg'"):
        parse_pan({"stops": [{"line": 1, "x": 0.0}], "focus_pull": {"line": 1, "to": "actor"}})
    with pytest.raises(HyperFramesError, match="dur phải là số > 0"):
        parse_pan({"stops": [{"line": 1, "x": 0.0}], "focus_pull": {"line": 1, "to": "fg", "dur": -1}})


def test_unified_camera_for_visuals():
    # Cú pháp camera dùng chung cho visuals đồ hoạ
    cam_raw = {
        "canvas": {"w": 3840, "h": 1080},
        "stops": [
            {"line": 1, "x": 0.0, "y": 0.1, "zoom": 1.0, "focus": "Quán Thánh"},
            {"line": 2, "x": 0.35, "y": 0.4, "zoom": 1.2, "focus": "Bạch Mã"},
            {"line": 3, "x": 0.7, "y": 0.6, "zoom": 1.1, "focus": "Kim Liên"},
            {"line": 4, "x": 1.0, "y": 0.8, "zoom": 1.35, "focus": "Voi Phục"},
        ],
        "transition_out": "whip",
        "orbit": {"deg": [0, 45], "line": [1, 3]},
    }
    out = parse_camera(cam_raw)
    assert out["canvas"] == {"w": 3840, "h": 1080}
    assert len(out["stops"]) == 4
    assert out["stops"][0]["focus"] == "Quán Thánh"
    assert out["transition_out"] == "whip"
    assert out["orbit"] == {"deg": [0.0, 45.0], "line": [1, 3]}

    # Test interpolate_camera trả đủ x, y, zoom
    times = {1: (0.0, 3.0), 2: (3.0, 6.0), 3: (6.0, 9.0), 4: (9.0, 12.0)}
    c0 = interpolate_camera(out, 0.0, times)
    assert c0["x"] == 0.0
    assert c0["y"] == 0.1
    assert c0["zoom"] == 1.0

    c2 = interpolate_camera(out, 3.0, times)
    assert c2["x"] == 0.35
    assert c2["y"] == 0.4
    assert c2["zoom"] == 1.2

    # Orbit không cần stops tường minh (tự tạo stop mặc định)
    out_orb = parse_camera({"orbit": {"deg": [0, 45], "line": [1, 2]}})
    assert len(out_orb["stops"]) == 1
    assert out_orb["orbit"] == {"deg": [0.0, 45.0], "line": [1, 2]}

    # Lỗi khi canvas quá nhỏ
    with pytest.raises(HyperFramesError, match="camera.canvas tối thiểu 1920x1080"):
        parse_camera({"canvas": {"w": 1280, "h": 720}, "stops": [{"line": 1}]})

    # Lỗi khi orbit sai format
    with pytest.raises(HyperFramesError, match="orbit.line câu không hợp lệ"):
        parse_camera({"stops": [{"line": 1}], "orbit": {"deg": [0, 90], "line": [3, 1]}})


def test_opening_gate_satisfaction_with_pan_styles():
    # Kiểm tra opening_gate đạt chuẩn khi câu mở đầu 40s dùng các kiểu lia mới
    import hf_batch_render as HBR

    segs = [
        {"sentence_id": i + 1, "start": i * 4.0, "end": (i + 1) * 4.0, "text": f"Câu mở đầu {i + 1} Bậc Giác Ngộ."}
        for i in range(10)
    ]
    media = {
        str(i + 1): {
            "kind": "local",
            "path": f"img_{i + 1}.png",
            **(
                {
                    "pan": {
                        "dir": "ltr",
                        "stops": [{"line": 1, "x": 0.0, "zoom": 1.0}, {"line": 2, "x": 0.8, "zoom": 1.35}],
                        "transition_out": "whip",
                        "depth": True,
                        "focus_pull": {"line": 1, "to": "fg", "dur": 1.0},
                    }
                }
                if i == 0
                else {}
            ),
        }
        for i in range(8)
    }
    row = {
        "id": "demo_pano_open",
        "series": "bud",
        "title": "Bậc Giác Ngộ Rời Thành",
        "format": "long",
        "script": [s["text"] for s in segs],
        "media": media,
    }
    errs = HBR.opening_gate_issues(row, segs)
    # Không có lỗi nào trong opening_gate
    assert errs == []
