import importlib.util
import json
from pathlib import Path
import sys

import pytest

import uuid


@pytest.fixture
def tmp_path():
    path = Path.cwd() / ("gh516-test-" + uuid.uuid4().hex)
    path.mkdir()
    return path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fetch_broll.py"


def test_download_selects_landscape_and_writes_index(tmp_path, monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location("fetch_broll_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["fetch_broll.py", "topic"])
    chapter = tmp_path / "data/long/topic/ch01.json"
    chapter.parent.mkdir(parents=True)
    chapter.write_text(json.dumps({"scenes": [{"vid": 1}, {"vid": 2}, {"vid": 3}]}), encoding="utf-8")
    catalog = tmp_path / "output/long/other/broll/index.json"
    catalog.parent.mkdir(parents=True)
    entries = {"1": {"files": [
        {"w": 3840, "h": 2160, "link": "too-large"},
        {"w": 1080, "h": 1920, "link": "portrait"},
        {"w": 1280, "h": 720, "link": "small"},
        {"w": 1920, "h": 1080, "link": "best"}]},
        "2": {"files": [{"w": 1280, "h": 720, "link": "existing"}]}}
    catalog.write_text(json.dumps(entries), encoding="utf-8")
    dest = tmp_path / "output/long/topic/broll"
    dest.mkdir(parents=True)
    (dest / "2.mp4").write_bytes(b"x" * 11000)
    calls = []

    class Response:
        content = b"y" * 11000
        def raise_for_status(self):
            pass

    class Client:
        def __init__(self, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def get(self, url):
            calls.append(url)
            return Response()

    monkeypatch.setattr(mod.httpx, "Client", Client)
    assert mod.main() == 1
    assert calls == ["best"]
    assert (dest / "1.mp4").read_bytes() == b"y" * 11000
    assert (dest / "2.mp4").read_bytes() == b"x" * 11000
    assert json.loads((dest / "index.json").read_text(encoding="utf-8")) == entries
    assert "clip 3 ok 2 thiếu ['3']" in capsys.readouterr().out
