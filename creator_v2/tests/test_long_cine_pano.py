"""Cảnh điện ảnh của Long (port từ engine gốc, PR #250): pano, cam/fx/transition_in, map route.

Mọi khoá đều tuỳ chọn: spec cũ phải ra đúng như trước.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT / "motion" / "stier"), str(ROOT)]
import build_long as BL  # noqa: E402
import cadence  # noqa: E402
import floor  # noqa: E402
import scene_params as SP  # noqa: E402


def lines(n=8):
    words = "mot hai ba bon nam sau".split()
    return [{"text": " ".join(words), "start": i * 4.0, "end": i * 4.0 + 3.5,
             "words": [{"w": w, "t": i * 4.0 + 0.5 * k, "d": 0.4} for k, w in enumerate(words)]} for i in range(n)]


def check(scenes, imgs=None):
    return SP.validate_topic([("ch00", scenes)], imgs, "noir")


def pano(t0=0.0, t1=12.0, **kw):
    return {"type": "pano", "t0": t0, "t1": t1, "img": "w",
            "stops": [{"x": 0.0, "at": t0 + 1}, {"x": 0.5, "at": t0 + 6}, {"x": 1.0, "at": t0 + 11}], **kw}


# ---- scene_params ----
def test_pano_duration_8_to_20_accepted_25_rejected():
    for dur in (8.0, 14.0, 20.0):
        assert check([pano(0, dur, stops=[{"x": 0, "at": 1}, {"x": 1, "at": dur - 0.5}])])["errors"] == []
    bad = check([pano(0, 25.0, stops=[{"x": 0, "at": 1}, {"x": 1, "at": 24}])])["errors"]
    assert any("thời lượng 25.00s ngoài [8.0s, 20.0s]" in e for e in bad)
    assert any("thời lượng" in e for e in check([pano(0, 6.0, stops=[{"x": 0, "at": 1}, {"x": 1, "at": 5}])])["errors"])


def test_other_scene_types_keep_2_5_to_9():
    assert any("thời lượng 12.00s" in e for e in check([{"type": "photo", "t0": 0, "t1": 12, "img": "a"}])["errors"])
    assert check([{"type": "photo", "t0": 0, "t1": 9, "img": "a"}])["errors"] == []


def test_cine_option_values_are_validated_and_unknown_keys_still_blocked():
    ok = {"type": "photo", "t0": 0, "t1": 5, "img": "a", "cam": "dolly", "fx": ["rain", "fog"], "transition_in": "whip"}
    assert check([ok])["errors"] == []
    for key, val in (("cam", "zoom"), ("fx", ["lightning"]), ("fx", "a"), ("transition_in", "match_dissolve"), ("fx", ["fog", "dust", "rain", "embers"])):
        assert check([{**ok, key: val}])["errors"], (key, val)
    assert check([{"type": "broll", "t0": 0, "t1": 5, "cam": "dolly"}])["errors"]       # cam chỉ đọc ở photo/pano
    assert check([pano(cam="dolly")])["errors"] and check([pano(cam="push_in")])["errors"] == []


def test_pano_stops_contract():
    assert check([{"type": "pano", "t0": 0, "t1": 10, "img": "w"}])["errors"]                      # thiếu stops
    assert check([pano(stops=[{"x": 0, "at": 1}])])["errors"]                                       # < 2 điểm
    assert check([pano(stops=[{"x": 0, "at": 5}, {"x": 1, "at": 3}])])["errors"]                    # at không tăng
    assert check([pano(stops=[{"x": 0, "at": 1}, {"x": 1.5, "at": 3}])])["errors"]                  # x ngoài [0,1]
    assert check([pano(stops=[{"x": 0, "at": 1}, {"x": 1, "at": 99}])])["errors"]                   # at ngoài cảnh


def test_map_route_contract():
    pins = [{"name": "A", "at": 1.0}, {"name": "B", "at": 2.0}, {"name": "C", "at": 3.0}]
    m = {"type": "map", "t0": 0, "t1": 6, "pins": pins, "route": ["A", "B", "C"]}
    assert check([m])["errors"] == []
    assert check([{**m, "route": ["A", "Z"]}])["errors"]
    assert check([{**m, "route": ["C", "A"]}])["errors"]       # ngược thứ tự pin.at
    assert check([{**m, "route": ["A"]}])["errors"]


def test_pano_speed_cap_uses_image_size():
    imgs = {"w": {"w": 3240, "h": 1080}}                       # quãng lia = 3240 - 1920 = 1320 px
    slow = [dict(pano(), **{"stops": [{"x": 0, "at": 0}, {"x": 1, "at": 8}]})]      # 165 px/s
    fast = [dict(pano(), **{"stops": [{"x": 0, "at": 0}, {"x": 1, "at": 6}]})]      # 220 px/s
    assert SP.pano_speed_problems("ch00", slow, imgs) == []
    assert "220 px/s" in SP.pano_speed_problems("ch00", fast, imgs)[0]
    assert SP.pano_speed_problems("ch00", fast, {}) == []      # chưa biết cỡ ảnh -> không đoán


# ---- plan(): mốc neo -> giây ----
def planned(scenes, dur=40.0):
    return BL.plan({"scenes": scenes}, lines(), dur)


def test_pano_stops_resolve_to_increasing_seconds():
    out = planned([{"type": "chapter", "no": "1", "title": "X"},
                   {"type": "pano", "at": 1, "img": "w",
                    "stops": [{"x": 0, "at": [1, "mot"]}, {"x": 0.5, "at": [2, "ba"]}, {"x": 1, "at": [3, "nam"]}]}])
    stops = out[1]["stops"]
    assert [q["at"] for q in stops] == [4.0, 9.0, 14.0]
    assert all(isinstance(q["at"], float) for q in stops)
    assert BL.unresolved_cues(out[1]) == []


def test_no_new_keys_means_unchanged_scene_dicts():
    sc = [{"type": "chapter", "no": "1", "title": "X"}, {"type": "photo", "at": 1, "img": "a"},
          {"type": "map", "at": 2, "geo": "main", "pins": [{"name": "A"}, {"name": "B"}]}]
    out = planned(sc)
    assert set(out[1]) == {"type", "img", "t0", "t1"}
    assert set(out[2]) == {"type", "geo", "pins", "t0", "t1"}
    blob = json.dumps(out)
    for key in ("cam", "fx", "transition_in", "stops", "route"):
        assert f'"{key}"' not in blob


def test_new_keys_reach_data_js_only_when_set():
    out = planned([{"type": "chapter", "no": "1", "title": "X"},
                   {"type": "photo", "at": 1, "img": "a", "cam": "tilt_up", "fx": ["dust"], "transition_in": "dip_black"},
                   {"type": "map", "at": 2, "geo": "main", "pins": [{"name": "A"}, {"name": "B"}], "route": ["A", "B"]}])
    assert (out[1]["cam"], out[1]["fx"], out[1]["transition_in"]) == ("tilt_up", ["dust"], "dip_black")
    assert out[2]["route"] == ["A", "B"]
    assert out[2]["pins"][0]["at"] < out[2]["pins"][1]["at"]    # plan() cho pin at mặc định -> route có mốc vẽ


def test_pano_counts_as_frame_scene_for_late_first():
    out = planned([{"type": "chapter", "no": "1", "title": "X"},
                   {"type": "pano", "at": 1, "img": "w", "stops": [{"x": 0, "at": [1, "mot"]}, {"x": 1, "at": [3, "nam"]}]}])
    assert BL.late_first(out, "ch00") == []


# ---- cadence: mỗi điểm dừng là một lần đổi hình ----
def test_cadence_counts_each_pano_stop():
    scene = {"type": "pano", "t0": 0, "t1": 16,
             "stops": [{"x": 0, "at": 0.0}, {"x": 0.5, "at": 5.0}, {"x": 0.8, "at": 9.0}, {"x": 1, "at": 13.0}]}
    events = cadence.subevents(scene, 0, 16, [], planned=True)
    assert events == [5.0, 9.0, 13.0]                          # điểm dừng đầu trùng đầu cảnh: đã tính là đầu cảnh
    plain = cadence.subevents({"type": "photo", "t0": 0, "t1": 16}, 0, 16, [], planned=True)
    assert plain == []


# ---- floor: tối đa 6 pano và 25% thời lượng ----
def chapters(n_pano):
    return [("ch00", {"scenes": [{"type": "pano"} for _ in range(n_pano)] + [{"type": "photo"}]})]


def test_floor_trips_on_more_than_six_pano():
    assert floor.pano_problems(chapters(6)) == []
    bad = floor.pano_problems(chapters(7))
    assert len(bad) == 1 and "7 cảnh pano" in bad[0]
    assert any("pano" in x for x in floor.problems(chapters(7), "MIM", None))


def test_floor_trips_on_pano_runtime_share():
    ok = [[{"type": "photo", "t0": 0, "t1": 60}, {"type": "pano", "t0": 60, "t1": 80}, {"type": "photo", "t0": 80, "t1": 200}]]
    count, share = floor.pano_share(ok)
    assert count == 1 and abs(share - 0.1) < 1e-9
    too_much = [[{"type": "photo", "t0": 0, "t1": 50}, {"type": "pano", "t0": 50, "t1": 70}]]
    assert floor.pano_share(too_much)[1] > floor.MAX_PANO_SHARE


def test_floor_share_reads_planned_data_js(tmp_path):
    base = tmp_path / "demo" / "ch00"
    base.mkdir(parents=True)
    scenes = [{"type": "photo", "t0": 0, "t1": 40}, {"type": "pano", "t0": 40, "t1": 60}]
    (base / "data.js").write_text("window.CASE = " + json.dumps({"scenes": scenes}) + ";\n", encoding="utf-8")
    bad = floor.pano_problems([("ch00", {"scenes": [{"type": "pano"}]})], "demo", out_root=tmp_path)
    assert len(bad) == 1 and "33%" in bad[0]
    assert floor.pano_problems([("ch00", {"scenes": [{"type": "pano"}]})], "demo", out_root=tmp_path / "missing") == []


# ---- engine ----
def test_engine_exposes_new_scene_and_options():
    js = (ROOT / "motion" / "hf" / "assets" / "engine" / "casewide.js").read_text(encoding="utf-8")
    assert "B.pano" in js and "CINE_FX" in js and "cineTrans" in js and "s.route" in js
    for name in SP.CINE_FX:
        assert f"{name}(L, o)" in js, name
    for cam in SP.CINE_CAMS:
        assert cam in js, cam
    assert "Math.random" not in js.split("điện ảnh (tuỳ chọn)")[1].split("B.print")[0]
