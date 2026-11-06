"""Regression tests for channel-specific Long title limits."""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "creator_v2" / "scripts"))
import long_gate
from library.tools import channel_profile


@pytest.fixture
def run_gate(tmp_path, monkeypatch):
    monkeypatch.setattr(long_gate, "ROOT", tmp_path)
    topic = tmp_path / "data" / "long" / "example"
    topic.mkdir(parents=True)
    (topic / "ch00.json").write_text(json.dumps({"hud": {"t": "chapter"}, "scenes": [], "lines": []}), encoding="utf-8")

    def run(spec):
        (topic / "spec.json").write_text(json.dumps(spec), encoding="utf-8")
        errors, warnings, _ = long_gate.gate("example", 0)
        return [e for e in errors if e.startswith("tiêu đề ")], warnings
    return run


def test_cl_allows_84_characters(run_gate):
    errors, warnings = run_gate({"channel": "CL", "title": "x" * 84})
    assert errors == []
    assert warnings == []


def test_mim_rejects_61_characters(run_gate):
    errors, _ = run_gate({"channel": "MIM", "title": "x" * 61})
    assert errors == ["tiêu đề 61 ký tự > 60 (MIM)"]


def test_empty_youtube_title_falls_back_to_spec_title(run_gate):
    errors, _ = run_gate({"channel": "MIM", "title": "x" * 61, "youtube": {"titles": [""]}})
    assert errors == ["tiêu đề 61 ký tự > 60 (MIM)"]


def test_unreadable_profile_defaults_to_60(run_gate, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("unreadable")
    monkeypatch.setattr(channel_profile, "load", fail)
    errors, warnings = run_gate({"channel": "CL", "title": "x" * 61})
    assert errors == ["tiêu đề 61 ký tự > 60 (CL)"]
    assert any("60" in warning and "unreadable" in warning for warning in warnings)
