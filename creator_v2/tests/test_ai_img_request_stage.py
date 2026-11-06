import importlib.util
import json
import sys
import uuid
from pathlib import Path
from unittest.mock import Mock

import pytest

spec = importlib.util.spec_from_file_location("ai_img_request", Path(__file__).with_name("ai_img_request.py"))
request = importlib.util.module_from_spec(spec)
spec.loader.exec_module(request)


@pytest.fixture
def setup_request(monkeypatch):
    tmp_path = Path(__file__).resolve().parents[1] / "data/long/gh198-test-temp" / uuid.uuid4().hex
    tmp_path.mkdir(parents=True)
    root = tmp_path / "repo"
    prompts = root / "data/long/topic/ai_prompts.md"
    prompts.parent.mkdir(parents=True)
    prompts.write_text("## ai_01.png\nfirst\n## ai_02.png\nsecond\n", encoding="utf-8")
    share = tmp_path / "shared"
    monkeypatch.setattr(request, "ROOT", root)
    monkeypatch.setenv("GROKBOT_SHARE_DIR", str(share))
    monkeypatch.setenv("GROKBOT_WEBHOOK_URL", "https://example.invalid/hook")
    monkeypatch.setenv("GROKBOT_WEBHOOK_KEY", "test-secret")
    monkeypatch.setattr(request.time, "sleep", lambda _: None)
    run = Mock(return_value=Mock(returncode=0))
    monkeypatch.setattr(request.subprocess, "run", run)
    return root, share, prompts, run


def test_stages_payload_and_copies_only_requested_images(setup_request, monkeypatch):
    root, share, prompts, run = setup_request
    dest = root / "motion/hf/assets/long/topic/img/ai"
    dest.mkdir(parents=True)
    (dest / "ai_01.png").write_bytes(b"existing")
    captured = {}

    def fake_urlopen(req, timeout):
        captured.update(json.loads(req.data))
        out = share / "topic/out"
        (out / "ai_01.png").write_bytes(b"replacement")
        (out / "ai_02.png").write_bytes(b"new")
        (out / "ai_99.png").write_bytes(b"unrequested")
        response = Mock()
        response.__enter__ = Mock(return_value=Mock(status=200))
        response.__exit__ = Mock(return_value=False)
        return response

    monkeypatch.setattr(request.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(sys, "argv", ["ai_img_request.py", "topic", "--wait", "1"])
    assert request.main() == 0
    assert (share / "topic/ai_prompts.md").read_bytes() == prompts.read_bytes()
    assert captured["prompt_file"] == str((share / "topic/ai_prompts.md").resolve())
    assert captured["output_dir"] == str((share / "topic/out").resolve())
    assert (dest / "ai_01.png").read_bytes() == b"existing"
    assert (dest / "ai_02.png").read_bytes() == b"new"
    assert (share / "topic/out/ai_02.png").exists()
    assert not (dest / "ai_99.png").exists()
    run.assert_called_once()


def test_no_send_waits_and_copies_without_credentials(setup_request, monkeypatch):
    root, share, _, run = setup_request
    out = share / "topic/out"
    out.mkdir(parents=True)
    for name in ("ai_01.png", "ai_02.png"):
        (out / name).write_bytes(name.encode())
    monkeypatch.delenv("GROKBOT_WEBHOOK_URL")
    monkeypatch.delenv("GROKBOT_WEBHOOK_KEY")
    send = Mock(side_effect=AssertionError("webhook must not be called"))
    monkeypatch.setattr(request.urllib.request, "urlopen", send)
    monkeypatch.setattr(sys, "argv", ["ai_img_request.py", "topic", "--no-send", "--wait", "1"])
    assert request.main() == 0
    send.assert_not_called()
    assert (root / "motion/hf/assets/long/topic/img/ai/ai_02.png").read_bytes() == b"ai_02.png"
    run.assert_called_once()
