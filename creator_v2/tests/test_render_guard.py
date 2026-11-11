"""Hồi quy cổng render GH-284, không khởi chạy Chrome hay render video."""
from contextlib import nullcontext
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
import pytest

from motion.long import build_long as b
import frozen_check
import pagecheck


def test_pageerror_stops_cmd_render_before_render(tmp_path, monkeypatch):
    hf = tmp_path / "hf"
    comp = hf / "compositions" / "long" / "test_ch01.html"
    comp.parent.mkdir(parents=True)
    comp.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(b, "HF", hf)
    monkeypatch.setattr(b, "late_report", lambda *_: [])
    monkeypatch.setattr(b, "load", lambda *_: ({}, [("ch01", {})], tmp_path))
    monkeypatch.setattr(b, "render_lock", lambda *_: nullcontext())
    monkeypatch.setattr(pagecheck, "find_tools", lambda: ("node", Path("puppeteer"), Path("chrome")))
    result = SimpleNamespace(stdout=json.dumps({"pageerrors": ["missing image mh_hat"], "console_errors": [], "timelines": {}}),
                             stderr="", returncode=0)
    with patch.object(pagecheck.subprocess, "run", return_value=result) as node, \
         patch.object(b, "do_render") as render:
        with pytest.raises(SystemExit, match="missing image mh_hat"):
            b.cmd_render("test")
        node.assert_called_once()
        render.assert_not_called()
    assert not list(hf.glob("_pagecheck_*.html"))


def test_frozen_frame_comparison():
    black = Image.new("RGB", (200, 100), "black")
    white = Image.new("RGB", (200, 100), "white")
    red = Image.new("RGB", (200, 100), "red")
    assert frozen_check.is_frozen([black, black.copy(), black.copy()])
    assert not frozen_check.is_frozen([black, white, red])


def test_endcard_background_counts_as_used(tmp_path, monkeypatch):
    spec = {"chapters": ["ch01"], "imgs": {"end": "File:example"}, "endcard": 10, "endcardBg": "end"}
    chapter = {"scenes": []}
    monkeypatch.setattr(b, "load", lambda *_: (spec, [("ch01", chapter)], tmp_path))
    monkeypatch.setattr(b, "_refuse_html_lint", lambda *_: None)
    def reached_after_image_check(*_):
        raise RuntimeError("reached after image check")
    monkeypatch.setattr(b, "_refuse_craft", reached_after_image_check)
    with pytest.raises(RuntimeError, match="reached after image check"):
        b.do_html("test")
    assert chapter["scenes"] == []
    spec["endcard"] = 0
    with pytest.raises(SystemExit, match="không có cảnh nào dùng"):
        b.do_html("test")


def test_missing_browser_warns_and_does_not_block(monkeypatch, capsys):
    monkeypatch.setattr(pagecheck, "find_tools", lambda: (None, None, None))
    assert pagecheck.check(Path("unused.html"), Path("unused")) == []
    assert "WARNING" in capsys.readouterr().out


def test_render_runs_and_checks_frames_when_page_is_healthy(tmp_path, monkeypatch):
    monkeypatch.setattr(b, "late_report", lambda *_: [])
    monkeypatch.setattr(b, "load", lambda *_: ({}, [("ch01", {})], tmp_path))
    monkeypatch.setattr(b, "render_lock", lambda *_: nullcontext())
    monkeypatch.setattr(pagecheck, "check", lambda *_: [])
    monkeypatch.setattr(b, "probe_dur", lambda *_: 10)
    with patch.object(b, "do_render") as render, patch.object(frozen_check, "check", return_value=False) as check:
        b.cmd_render("test", ["ch01"], ["--draft"])
        render.assert_called_once()
        check.assert_called_once_with(tmp_path / "ch01" / "draft.mp4", b.FFMPEG, 10)


def test_extracts_frames_at_three_percentages():
    pixels = bytes(frozen_check.WIDTH * frozen_check.HEIGHT * 3)
    result = SimpleNamespace(stdout=pixels)
    with patch.object(frozen_check.subprocess, "run", return_value=result) as run:
        assert frozen_check.check(Path("example.mp4"), "ffmpeg", 100)
    assert [call.args[0][4] for call in run.call_args_list] == ["10.0", "50.0", "90.0"]


def test_frozen_render_invalidates_key(tmp_path, monkeypatch):
    monkeypatch.setattr(b, "late_report", lambda *_: [])
    monkeypatch.setattr(b, "load", lambda *_: ({}, [("ch01", {})], tmp_path))
    monkeypatch.setattr(b, "render_lock", lambda *_: nullcontext())
    monkeypatch.setattr(pagecheck, "check", lambda *_: [])
    monkeypatch.setattr(frozen_check, "check", lambda *_: True)
    monkeypatch.setattr(b, "probe_dur", lambda *_: 10)
    monkeypatch.setattr(b, "do_render", lambda *args, **kwargs: None)
    key = tmp_path / "ch01" / "silent.key"
    key.parent.mkdir()
    key.write_text("valid-before-check", encoding="utf-8")
    with pytest.raises(SystemExit, match="video đứng hình"):
        b.cmd_render("test")
    assert not key.exists()
