"""Test cổng nhịp cắt 120s đầu cho video dài:
- Cảnh có chuyển động <= 8.0s, tĩnh <= 4.0s; nền trống liên tục <= 1.5s (mức ERROR).
- Cờ plan `pace_gate: off` để tắt cho Long cũ. Sau 120s giữ luật cũ.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hf_batch_render as HBR


def _segs_from_durs(durs):
    out, t = [], 0.0
    for d in durs:
        out.append({"start": round(t, 3), "end": round(t + d - 0.05, 3)})
        t += d
    return out


def test_pace_gate_pass_under_4s_and_no_naked_run():
    # 6 câu trong 120s đầu: mỗi câu 2.5s - 3.5s có ảnh riêng, câu 2 là visual word 1.2s <= 1.5s
    script = [f"Câu {i} kể chuyện lịch sử." for i in range(1, 7)]
    durs = [3.0, 1.2, 3.5, 2.8, 3.0, 2.5]
    media = {
        "1": {"kind": "commons", "ref": "m1"},
        "3": {"kind": "local", "path": "p3.png"},
        "4": {"kind": "image", "query": "q4"},
        "5": {"kind": "commons", "ref": "m5"},
        "6": {"kind": "image", "query": "q6"},
    }
    visuals = {"2": {"type": "word"}}
    # Câu 2 ngắt hold của ảnh 1, kéo dài 1.2s (naked <= 1.5s) -> ĐẠT
    row = {"script": script, "media": media, "visuals": visuals, "kinetic": True}
    segs = _segs_from_durs(durs)
    errs = HBR.pace_gate_issues(row, segs)
    assert errs == []
    rep, bad = HBR.pacing(row, segs)
    assert not any(x.startswith("120s đầu:") for x in bad)


def test_pace_gate_moving_shots_allow_6s_but_fail_over_8s():
    script = [f"Câu {i}." for i in range(1, 5)]
    durs = [3.0, 6.0, 9.0, 2.5]
    media = {
        "1": {"kind": "commons", "ref": "m1"},
        "2": {"kind": "commons", "ref": "m2"},
        "3": {"kind": "commons", "ref": "m3"},
        "4": {"kind": "commons", "ref": "m4"},
    }
    # Ảnh cine 6s đạt; 9s vượt ngưỡng chuyển động 8s.
    media["2"]["cine"] = {"cam": "push_in"}
    media["3"]["cine"] = {"cam": "push_in"}
    row = {"script": script, "media": media, "visuals": {}, "kinetic": True}
    segs = _segs_from_durs(durs)
    errs = HBR.pace_gate_issues(row, segs)
    assert any("120s đầu: cảnh 'tư liệu' có chuyển động dài 9.0s từ câu 3 (> 8.0s)" in e for e in errs)
    assert not any("câu 2" in e for e in errs)
    _, bad = HBR.pacing(row, segs)
    assert any("cảnh 'tư liệu' có chuyển động dài 9.0s" in x for x in bad)


def test_pace_gate_static_6s_fails():
    row = {"script": ["Ảnh tĩnh."], "media": {"1": {"kind": "commons", "ref": "m1"}}}
    assert any("tĩnh dài 6.0s" in e and "(> 4.0s)" in e
               for e in HBR.pace_gate_issues(row, _segs_from_durs([6.0])))


def test_pace_gate_fail_naked_run_over_1_5s_in_first_120s():
    # Cold open 2 câu đầu chữ trên nền trống: 1.0s + 1.0s = 2.0s > 1.5s
    script = [f"Câu {i}." for i in range(1, 5)]
    durs = [1.0, 1.0, 3.0, 2.5]
    media = {
        "3": {"kind": "commons", "ref": "m3"},
        "4": {"kind": "commons", "ref": "m4"},
    }
    row = {"script": script, "media": media, "visuals": {}, "kinetic": True}
    segs = _segs_from_durs(durs)
    errs = HBR.pace_gate_issues(row, segs)
    assert any("120s đầu: chữ trên nền trống 2.0s liên tục từ câu 1 (> 1.5s)" in e for e in errs)
    _, bad = HBR.pacing(row, segs)
    assert any("chữ trên nền trống 2.0s liên tục" in x for x in bad)


def test_pace_gate_flag_off_bypasses_check():
    # Plan có cả lỗi cảnh dài và lỗi chữ trên nền trống
    script = [f"Câu {i}." for i in range(1, 5)]
    durs = [5.0, 2.0, 2.0, 2.5]
    row = {"script": script, "pace_gate": "off", "kinetic": True}
    segs = _segs_from_durs(durs)
    assert HBR.pace_gate_issues(row, segs) == []

    # Cờ boolean False
    row["pace_gate"] = False
    assert HBR.pace_gate_issues(row, segs) == []


def test_pace_gate_allows_shots_and_naked_run_after_120s():
    # 40 câu đầu: mỗi câu 3.0s có ảnh riêng (tổng đúng 120.0s)
    # Từ giây 120s trở đi: câu 41 dài 6.0s và câu 42 chữ trên nền trống 3.0s
    script = [f"Câu {i}." for i in range(1, 43)]
    durs = [3.0] * 40 + [6.0, 3.0]
    media = {str(i + 1): {"kind": "commons", "ref": f"m{i}"} for i in range(41)}
    row = {"script": script, "media": media, "visuals": {}, "kinetic": True}
    segs = _segs_from_durs(durs)
    errs = HBR.pace_gate_issues(row, segs)
    assert errs == []


def test_pace_gate_media_holds_tracking():
    # Câu 1 (2.0s) có ảnh, câu 2 (2.5s) giữ ảnh đó -> tổng cảnh 4.5s > 4.0s
    script = [f"Câu {i}." for i in range(1, 4)]
    durs = [2.0, 2.5, 2.0]
    media = {"1": {"kind": "commons", "ref": "m1"}, "3": {"kind": "commons", "ref": "m3"}}
    row = {"script": script, "media": media, "visuals": {}, "kinetic": True}
    segs = _segs_from_durs(durs)
    errs = HBR.pace_gate_issues(row, segs)
    assert any("cảnh 'tư liệu' tĩnh dài 4.5s từ câu 1 (> 4.0s)" in e for e in errs)

    # Nếu giữ 1.5s + 1.8s = 3.3s <= 4.0s -> ĐẠT và câu 2 không bị tính là naked
    durs_ok = [1.5, 1.8, 2.0]
    segs_ok = _segs_from_durs(durs_ok)
    assert HBR.pace_gate_issues(row, segs_ok) == []


def test_pace_gate_pan_stops_count_as_cuts():
    # Ảnh rộng câu 1 lia qua 4 câu (11s): mỗi điểm dừng pan là một khung mới -> không vượt 4s.
    script = [f"Câu {i}." for i in range(1, 6)]
    durs = [2.5, 2.0, 3.0, 3.5, 3.0]
    pan = {"dir": "ltr", "stops": [{"line": 1, "x": 0.0}, {"line": 2, "x": 0.3}, {"line": 3, "x": 0.6}, {"line": 4, "x": 1.0}]}
    media = {"1": {"kind": "local", "path": "pano.jpg", "pan": pan}, "5": {"kind": "local", "path": "p5.png"}}
    row = {"script": script, "media": media, "visuals": {}, "kinetic": True}
    segs = _segs_from_durs(durs)
    assert HBR.pace_gate_issues(row, segs) == []
    # Bỏ điểm dừng giữa -> 7.5s vẫn trong ngưỡng động 8s; kéo dài trên 8s mới bị chặn.
    pan2 = {"dir": "ltr", "stops": [{"line": 1, "x": 0.0}, {"line": 4, "x": 1.0}]}
    row["media"]["1"]["pan"] = pan2
    assert HBR.pace_gate_issues(row, segs) == []
    segs_long = _segs_from_durs([3.0, 3.0, 3.5, 3.0, 3.0])
    errs = HBR.pace_gate_issues(row, segs_long)
    assert any("có chuyển động dài 9.5s từ câu 1 (> 8.0s)" in e for e in errs)


def test_pace_gate_text_line_without_media_is_static():
    """Lead 17/11: dòng không có media không được coi là clip (kind mặc định 'video')."""
    row = {"script": ["Chỉ có chữ."], "media": {}}
    assert any("tĩnh dài 6.0s" in e for e in HBR.pace_gate_issues(row, _segs_from_durs([6.0])))
