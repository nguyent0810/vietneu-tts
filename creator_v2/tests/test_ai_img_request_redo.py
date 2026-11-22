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


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ai_img_request.py"


def load():
    spec = importlib.util.spec_from_file_location("ai_img_request_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_redo_archives_both_copies_and_only_requests_redo(tmp_path, monkeypatch):
    mod = load()
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    share = tmp_path / "share"
    monkeypatch.setenv("GROKBOT_SHARE_DIR", str(share))
    monkeypatch.setattr(mod, "env", lambda name: "https://example.test" if name.endswith("URL") else "test-key")
    prompt = tmp_path / "data/long/topic/ai_prompts.md"
    prompt.parent.mkdir(parents=True)
    prompt.write_text("## ai_01.png\n## ai_02.png\n## ai_03.png\n", encoding="utf-8")
    out = tmp_path / "motion/hf/assets/long/topic/img/ai"
    shared = share / "topic/out"
    out.mkdir(parents=True)
    shared.mkdir(parents=True)
    for name in ("ai_01.png", "ai_02.png", "ai_03.png"):
        (out / name).write_bytes(b"local-old")
        (shared / name).write_bytes(b"shared-old")
    sent = []

    class Response:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    def send(request, timeout):
        sent.append(json.loads(request.data))
        for name in ("ai_01.png", "ai_03.png"):
            (shared / name).write_bytes(b"new")
        return Response()

    monkeypatch.setattr(mod.urllib.request, "urlopen", send)
    monkeypatch.setattr(mod.time, "sleep", lambda _: None)
    monkeypatch.setattr(mod.subprocess, "run", lambda *args, **kwargs: type("Result", (), {"returncode": 0})())
    monkeypatch.setattr(sys, "argv", ["ai_img_request.py", "topic", "--redo", "ai_01,ai_03.png"])
    assert mod.main() == 0
    assert len(sent) == 1
    assert "ai_01.png, ai_03.png" in sent[0]["instructions"]
    assert "ai_02.png" not in sent[0]["instructions"]
    for directory, old in ((out, b"local-old"), (shared, b"shared-old")):
        for name in ("ai_01.png", "ai_03.png"):
            assert next((directory / "_old").glob(f"*/{name}")).read_bytes() == old
            assert (directory / name).read_bytes() == b"new"
        assert (directory / "ai_02.png").read_bytes() == old


def test_redo_rejects_no_send_before_touching_files(tmp_path, monkeypatch, capsys):
    mod = load()
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["ai_img_request.py", "topic", "--redo", "ai_01", "--no-send"])
    with pytest.raises(SystemExit) as error:
        mod.main()
    assert error.value.code == 2
    assert "--redo không thể dùng cùng --no-send" in capsys.readouterr().err
    assert not list(tmp_path.iterdir())
