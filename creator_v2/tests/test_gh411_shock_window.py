import json
import sys
import types
import warnings

import pytest

from motion.long import opening_gate as gate
from motion.stier import build as short


def line(text, start=0):
    return {"text": text, "start": start, "end": start + 1, "words": []}


def codes(scenes, lines):
    return " ".join(gate.shock_findings(scenes, lines))


def test_missing_shock_and_early_question():
    assert "O7" in codes([], [line("Someone stands there.")])
    assert "O7" not in codes([], [line("Vì sao cánh cửa không mở?", 3)])


@pytest.mark.parametrize("start", [40, 45])
def test_late_paradox(start):
    assert "O7" in codes([], [line("Anh nhìn ra sân."), line("Ngày đẹp nhất, nhưng lại xung tuổi mình.", start)])


def test_hook_and_paradox_markers():
    for text in ("Ngày đẹp nhất, nhưng lại xung tuổi mình.", "Lời đáp ở chương ba.", "Điều gì xảy ra"):
        assert "O7" not in codes([], [line(text)])


def test_strong_visuals_count_each_scene_once_and_exclude_40():
    scenes = [{"t0": 0, "type": "slam", "vid": "x"},
              {"t0": 4, "type": "photo", "move": "push"},
              {"t0": 40, "type": "counter"}]
    assert "2 nhịp" in codes(scenes, [])
    scenes[-1]["t0"] = 39.9
    assert "O8" not in codes(scenes, [])
    assert "O8" in codes([{"t0": 0, "type": "photo"}], [])


def test_warnings_do_not_become_errors():
    with warnings.catch_warnings(record=True) as found:
        warnings.simplefilter("always")
        errors = gate.check("", [{"t0": 0, "t1": 1, "type": "photo"}], [line("Someone walks.")], legacy=False)
    assert not any("O7" in error or "O8" in error for error in errors)
    assert {"O7", "O8"} <= {str(w.message).split()[0] for w in found}


def test_problems_uses_external_real_timing(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    data = root / "data" / "long" / "topic"
    data.mkdir(parents=True)
    (data / "spec.json").write_text(json.dumps({"chapters": ["ch00"], "youtube": {"titles": [""]}}), encoding="utf-8")
    (data / "ch00.json").write_text(json.dumps({"lines": ["Câu hỏi?"]}), encoding="utf-8")
    out = tmp_path / "external" / "topic" / "ch00"
    out.mkdir(parents=True)
    (out / "timing.json").write_text(json.dumps({"duration": 50, "segments": [{"text": "Câu hỏi?", "start": 40, "end": 45}]}), encoding="utf-8")
    fake = types.SimpleNamespace(word_lines=lambda t, wav: [line(x["text"], x["start"]) for x in t["segments"]],
                                 plan=lambda chapter, lines, duration: [{"t0": 0, "t1": 1, "type": "photo"}])
    monkeypatch.setitem(sys.modules, "build_long", fake)
    with warnings.catch_warnings(record=True) as found:
        warnings.simplefilter("always")
        gate.problems("topic", root, tmp_path / "external")
    assert any("O7" in str(w.message) for w in found)
    timing = {"duration": 50, "segments": [{"text": "Câu hỏi?", "start": 39, "end": 45}]}
    (out / "timing.json").write_text(json.dumps(timing), encoding="utf-8")
    with warnings.catch_warnings(record=True) as found:
        warnings.simplefilter("always")
        gate.problems("topic", root, tmp_path / "external")
    assert not any("O7" in str(w.message) for w in found)


def test_short_first_line_warning_not_error(tmp_path):
    spec = {"rules": 3, "lines": ["one two three four five six seven eight nine ten"],
            "hooks": ["one", "two"], "scenes": [{"type": "photo"}], "kicker": "one", "title": "one"}
    errors, notes = short.retention_hook_lint(spec, "new", tmp_path)
    assert not errors
    assert any("lời mở dài 10 từ" in note for note in notes)
    assert not any("lời mở dài" in error for error in short.hook_errors(spec))
    spec["lines"] = ["one two three four five six seven eight nine"]
    assert not any("lời mở dài" in note for note in short.retention_hook_lint(spec, "new", tmp_path)[1])
    spec["rules"] = 2
    spec["lines"] = ["one two three four five six seven eight nine ten"]
    assert not any("lời mở dài" in note for note in short.retention_hook_lint(spec, "new", tmp_path)[1])
