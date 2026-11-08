"""Test cổng nhịp cắt 120s đầu cho video dài (Task 010):
- Trong 120s đầu: MỌI cảnh <= 4.0s, chữ trên nền trống liên tục <= 1.5s (mức ERROR).
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


def test_pace_gate_fail_shot_over_4s_in_first_120s():
    script = [f"Câu {i}." for i in range(1, 5)]
    durs = [3.0, 4.8, 3.0, 2.5]
    media = {
        "1": {"kind": "commons", "ref": "m1"},
        "2": {"kind": "commons", "ref": "m2"},
        "3": {"kind": "commons", "ref": "m3"},
        "4": {"kind": "commons", "ref": "m4"},
    }
    # Câu 2 dài 4.8s > 4.0s ở giây 3.0 (< 120s) -> LỖI
    row = {"script": script, "media": media, "visuals": {}, "kinetic": True}
    segs = _segs_from_durs(durs)
    errs = HBR.pace_gate_issues(row, segs)
    assert any("120s đầu: cảnh 'tư liệu' dài 4.8s từ câu 2 (> 4.0s)" in e for e in errs)
    _, bad = HBR.pacing(row, segs)
    assert any(x.startswith("120s đầu: cảnh 'tư liệu' dài 4.8s") for x in bad)


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
    assert any("cảnh 'tư liệu' dài 4.5s từ câu 1 (> 4.0s)" in e for e in errs)

    # Nếu giữ 1.5s + 1.8s = 3.3s <= 4.0s -> ĐẠT và câu 2 không bị tính là naked
    durs_ok = [1.5, 1.8, 2.0]
    segs_ok = _segs_from_durs(durs_ok)
    assert HBR.pace_gate_issues(row, segs_ok) == []
