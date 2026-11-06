import importlib.util
import json
import sys
import uuid
from pathlib import Path
from unittest.mock import Mock

import pytest

spec = importlib.util.spec_from_file_location("ai_img_request", Path(__file__).resolve().parents[1] / "scripts" / "ai_img_request.py")
request = importlib.util.module_from_spec(spec)
spec.loader.exec_module(request)


@pytest.fixture
def setup_request(monkeypatch, tmp_path):
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


def test_both_kinds_send_and_crop(setup_request, monkeypatch):
    root, share, prompts, run = setup_request
    prompts.write_text(prompts.read_text(encoding="utf-8") + "## vid_01.mp4\nvideo\n", encoding="utf-8")
    calls = []
    def send(req, timeout):
        payload = json.loads(req.data)
        calls.append(payload)
        out = share / "topic/out"
        if payload["task"] == "generate_images":
            for name in ("ai_01.png", "ai_02.png"):
                (out / name).write_bytes(b"image")
        else:
            (out / "vid_01.mp4").write_bytes(b"original")
        response = Mock()
        response.__enter__ = Mock(return_value=Mock(status=200))
        response.__exit__ = Mock(return_value=False)
        return response
    import webauto.videofix
    def crop(path, mode):
        assert mode == "crop"
        assert path.read_bytes() == b"original"
        assert path.parent != share / "topic/out"
        path.write_bytes(b"cropped")
    monkeypatch.setattr(webauto.videofix, "strip_video", crop)
    monkeypatch.setattr(request.urllib.request, "urlopen", send)
    monkeypatch.setattr(sys, "argv", ["ai_img_request.py", "topic", "--wait", "1"])
    assert request.main() == 0
    assert [item["task"] for item in calls] == ["generate_images", "generate_videos"]
    assert "ai_01.png" in calls[0]["instructions"]
    assert "vid_01.mp4" in calls[1]["instructions"]
    dest = root / "output/long/topic/broll"
    assert (dest / "900001.mp4").read_bytes() == b"cropped"   # id số: build_long chỉ nhận broll/(\d+)
    assert json.loads((dest / "900001.json").read_text(encoding="utf-8")) == {"ai_generated": True, "credit": False, "source_name": "vid_01.mp4"}
    assert (share / "topic/out/vid_01.mp4").read_bytes() == b"original"
    run.assert_called_once()


def test_videos_only_does_not_wait_for_images(setup_request, monkeypatch):
    root, share, prompts, run = setup_request
    prompts.write_text(prompts.read_text(encoding="utf-8") + "## vid_01.mp4\nvideo\n", encoding="utf-8")
    out = share / "topic/out"
    out.mkdir(parents=True)
    (out / "vid_01.mp4").write_bytes(b"video")
    import webauto.videofix
    crop = Mock()
    monkeypatch.setattr(webauto.videofix, "strip_video", crop)
    send = Mock(side_effect=AssertionError("webhook must not be called"))
    monkeypatch.setattr(request.urllib.request, "urlopen", send)
    monkeypatch.setattr(sys, "argv", ["ai_img_request.py", "topic", "--videos-only", "--no-send", "--wait", "1"])
    assert request.main() == 0
    assert (root / "output/long/topic/broll/900001.mp4").exists()
    crop.assert_called_once()
    send.assert_not_called()
    run.assert_not_called()
