import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import build_long as B  # noqa: E402


@pytest.fixture
def html_setup(monkeypatch):
    tmp_path = Path("fake_output")
    durations = {"ch01": 0.5, "ch02": 0.5}
    monkeypatch.setattr(Path, "exists", lambda p: p.name == "timing.json")
    monkeypatch.setattr(Path, "read_text", lambda p, **kwargs: json.dumps({"duration": durations[p.parent.name]}))
    monkeypatch.setattr(Path, "write_text", lambda *args, **kwargs: None)
    chapters = []
    spec = {"chapters": ["ch01", "ch02"], "channel": "MIM", "kinetic_auto": False}
    for name in spec["chapters"]:
        chapters.append((name, {"scenes": [{"type": "chapter"}]}))
    monkeypatch.setattr(B, "load", lambda topic: (spec, chapters, tmp_path))
    for name in ("_refuse_html_lint", "_refuse_craft", "_refuse_opening"):
        monkeypatch.setattr(B, name, lambda *args: None)
    monkeypatch.setattr(B, "beat2_advice", lambda spec: None)
    monkeypatch.setattr(B, "ck_source_brands", lambda spec: [])
    monkeypatch.setattr(B.variety, "resolve_bgm", lambda *args: None)
    monkeypatch.setattr(B.variety, "look", lambda *args: {})
    monkeypatch.setattr(B, "word_lines", lambda *args: [])
    monkeypatch.setattr(B.scene_params, "validate_topic", lambda *args, **kwargs: {"errors": [], "warnings": []})
    monkeypatch.setattr(B.scene_params, "pano_speed_problems", lambda *args: [])
    return spec, chapters, durations


def test_missing_bgm_stops_before_loading_assets(html_setup, monkeypatch):
    spec, chapters, _ = html_setup
    chapters[0][1]["bgm"] = {"mood": "missing"}
    chapters[1][1]["bgm"] = [{"mood": "other"}]
    monkeypatch.setattr(B.variety, "look", lambda *args: pytest.fail("assets must not load"))
    with pytest.raises(SystemExit) as exc:
        B.do_html("sample")
    assert "nhạc nền" in str(exc.value)
    assert "ch01" in str(exc.value) and "ch02" in str(exc.value)
    assert "output/long/sample/bgm_picks.json" in str(exc.value)


def test_short_scenes_are_gathered_across_chapters(html_setup):
    with pytest.raises(SystemExit) as exc:
        B.do_html("sample")
    message = str(exc.value)
    assert "tham số cảnh" in message
    assert "ch01" in message and "ch02" in message
    assert message.count("quá ngắn") == 2


def test_date_group_at_is_checked_before_audio(html_setup):
    spec, chapters, durations = html_setup
    spec["chapters"] = ["ch01"]
    chapters.pop()
    chapters[0][1]["scenes"] = [{"type": "date", "date": "12/2026", "groupAt": [0.4]}]
    durations["ch01"] = 10
    with pytest.raises(SystemExit, match="ch01#0 date: groupAt có 1 mốc, date có 2 nhóm số"):
        B.do_html("sample")
