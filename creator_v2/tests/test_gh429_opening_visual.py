import json
import sys
import types
import warnings

import pytest

from motion.long import opening_gate as gate


def line(text, start=0):
    return {"text": text, "start": start, "end": start + 1, "words": []}


def findings(scenes, lines=None):
    return gate.opening_visual_findings(scenes, lines or [line("Vì sao?")])


@pytest.mark.parametrize("scene,expected", [
    ({"type": "photo", "img": "a", "tone": "dark"}, True),
    ({"type": "photo", "img": "a", "move": "push"}, False),
    ({"type": "photo", "img": "a", "cam": "dolly"}, False),
    ({"type": "pano", "img": "a", "stops": [{"x": 0}, {"x": 1}]}, False),
    ({"type": "pano", "img": "a", "stops": [{"x": 0}, {"x": 0}]}, True),
    ({"type": "slam", "vid": "x"}, False),
    ({"type": "map"}, True),
])
def test_o9(scene, expected):
    assert any("O9" in x for x in findings([dict(scene, t0=0)])) is expected


@pytest.mark.parametrize("typ", sorted(gate.OPEN_TEXT_TYPES))
def test_o10_all_text_types_and_time_boundary(typ):
    scenes = [{"type": typ, "t0": 9.9}, {"type": typ, "t0": 10}]
    result = [x for x in findings(scenes) if "O10" in x]
    assert len(result) == 1
    assert typ in result[0] and "9.9s" in result[0]


@pytest.mark.parametrize("texts,expected", [
    (["Một câu.", "Câu hai.", "Câu ba.", "Vì sao?"], True),
    (["Một câu.", "Nhưng có điều lạ.", "Câu ba."], False),
    (["Một câu.", "Câu hai.", "Bí mật ở đâu."], False),
    (["Một câu?", "Câu hai.", "Câu ba."], False),
])
def test_o11_first_three_lines(texts, expected):
    assert any("O11" in x for x in findings([], [line(t) for t in texts])) is expected


def test_warnings_do_not_block():
    with warnings.catch_warnings(record=True) as found:
        warnings.simplefilter("always")
        errors = gate.check("", [{"type": "slam", "t0": 0, "t1": 1}],
                            [line("Một câu.")], legacy=False)
    assert {"O9", "O10", "O11"} <= {str(w.message).split()[0] for w in found}
    assert not any(code in e for e in errors for code in ("O9", "O10", "O11"))


@pytest.mark.parametrize("start,expected", [(9.9, True), (10, False), (10.1, False)])
def test_external_timing_drives_planned_scenes(tmp_path, monkeypatch, start, expected):
    root = tmp_path / "repo"
    data = root / "data" / "long" / "topic"
    data.mkdir(parents=True)
    (data / "spec.json").write_text(json.dumps({"chapters": ["ch00"], "youtube": {"titles": [""]}}), encoding="utf-8")
    (data / "ch00.json").write_text(json.dumps({"lines": ["Câu đầu.", "Vì sao?"]}), encoding="utf-8")
    out = tmp_path / "external" / "topic" / "ch00"
    out.mkdir(parents=True)
    timing = {"duration": 20, "segments": [{"text": "Câu đầu.", "start": 0, "end": 1},
                                           {"text": "Vì sao?", "start": start, "end": start + 1}]}
    (out / "timing.json").write_text(json.dumps(timing), encoding="utf-8")
    fake = types.SimpleNamespace(plan=lambda chapter, lines, duration: [
        {"type": "photo", "move": "push", "t0": 0, "t1": 1},
        {"type": "chapter", "t0": lines[1]["start"], "t1": duration}])
    monkeypatch.setitem(sys.modules, "build_long", fake)
    with warnings.catch_warnings(record=True) as found:
        warnings.simplefilter("always")
        gate.problems("topic", root, tmp_path / "external")
    assert any("O10" in str(w.message) for w in found) is expected
