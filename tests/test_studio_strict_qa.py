"""studio --strict: QA lint/check không đạt thì thoát khác 0; không --strict thì giữ hành vi cũ."""
import sys
from pathlib import Path

import pytest

import studio

OK = {"lint": {"ok": True}, "check": {"ok": True}}


@pytest.mark.parametrize("rep,expected", [
    (OK, True),
    ({"lint": {"ok": False}, "check": {"ok": True}}, False),
    ({"lint": {"ok": True}, "check": {"ok": False}}, False),
    ({"lint": {"raw": "x"}, "check": {"ok": True}}, False),
    ({"lint": {"ok": True}}, False),
])
def test_qa_ok(rep, expected):
    assert studio.qa_ok(rep) is expected


@pytest.mark.parametrize("strict,rep,expected", [
    (True, {"lint": {"ok": False}, "check": {"ok": True}}, False),
    (False, {"lint": {"ok": False}, "check": {"ok": False}}, True),   # không --strict: như cũ
    (True, OK, True),
])
def test_qa_gate(monkeypatch, tmp_path, strict, rep, expected):
    monkeypatch.setattr(studio, "qa", lambda *a, **k: rep)
    assert studio.qa_gate(tmp_path, 10.0, [], None, strict) is expected


@pytest.mark.parametrize("built,code", [(False, 1), (True, 0), (None, 0)])
def test_main_exit_code(monkeypatch, built, code):
    monkeypatch.setattr(studio, "build", lambda *a, **k: built)
    monkeypatch.setattr(sys, "argv", ["studio.py", "build", "s.json", "--qa", "--strict"])
    assert studio.main() == code
