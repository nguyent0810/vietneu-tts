import json
from pathlib import Path

import pytest

from library.tools import ai_image_batch as batch


def _plan(tmp_path, monkeypatch, backend="chatgpt"):
    monkeypatch.setattr(batch, "ROOT", tmp_path)
    needs = tmp_path / "needs.json"
    needs.write_text(json.dumps({"items": [{"filename": "a.png", "prompt": "A stone temple", "pham_vi": "chung", "tags": ["temple"]}]}))
    return batch.plan(needs, "demo", backend)


def test_plan_outputs_prompts_and_metadata(tmp_path, monkeypatch):
    out = _plan(tmp_path, monkeypatch)
    data = json.loads((out / "lo.json").read_text())
    assert data["items"][0]["prompt"] == "A stone temple"
    assert "## a.png" in (out / "prompts.md").read_text()
    assert "001 | A stone temple" in (out / "prompts.txt").read_text()


def test_send_command_does_not_print_secret(tmp_path, monkeypatch, capsys):
    out = _plan(tmp_path, monkeypatch)
    monkeypatch.setenv("GROKBOT_WEBHOOK_URL", "https://example.invalid/hook")
    monkeypatch.setenv("GROKBOT_WEBHOOK_KEY", "TOP_SECRET")
    command = batch.send_chatgpt(out)
    printed = capsys.readouterr().out
    assert "TOP_SECRET" not in command + printed
    assert "${GROKBOT_WEBHOOK_KEY}" in command
    assert "${GROKBOT_WEBHOOK_URL}" in command
    assert "example.invalid" not in command + printed


def test_run_flow_builds_expected_argv(tmp_path, monkeypatch):
    out = _plan(tmp_path, monkeypatch, "flow")
    monkeypatch.setenv("WEBAUTO_REPO", str(tmp_path / "v2"))
    calls = []
    argv = batch.run_flow(out, headless=True, runner=lambda args, **kw: calls.append((args, kw)))
    assert argv[argv.index("--strip-mark") + 1] == "crop"
    assert "--headless" in argv
    assert calls[0][1]["check"] is True


def test_wait_times_out(tmp_path, monkeypatch, capsys):
    out = _plan(tmp_path, monkeypatch)
    assert batch.wait_batch(out, timeout=0) is False
    assert "HẾT HẠN" in capsys.readouterr().out


def test_wait_both_needs_both_sources(tmp_path, monkeypatch):
    out = _plan(tmp_path, monkeypatch, "both")
    (out / "out").mkdir(exist_ok=True)
    (out / "out" / "a.png").write_bytes(b"png")
    assert batch.wait_batch(out, timeout=0) is False  # mới có ChatGPT, thiếu Flow
    (out / "raw").mkdir(exist_ok=True)
    (out / "raw" / "a.png").write_bytes(b"png")
    assert batch.wait_batch(out, timeout=0) is True


def test_ingest_requires_lead_review(tmp_path, monkeypatch):
    out = _plan(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="LEAD_DA_XEM"):
        batch.ingest(out)


def test_ingest_skips_excluded_and_sets_provenance(tmp_path, monkeypatch):
    from PIL import Image
    from library.tools import assets
    out = _plan(tmp_path, monkeypatch)
    monkeypatch.setattr(assets, "DEFAULT_MANIFEST", tmp_path / "manifest.jsonl")
    source = out / "out"; source.mkdir()
    Image.new("RGB", (2, 2), "red").save(source / "a.png")
    Image.new("RGB", (2, 2), "blue").save(source / "excluded.png")
    (out / "LEAD_DA_XEM").touch()
    (out / "LOAI_BO.txt").write_text("excluded.png\n")
    assert batch.ingest(out) == 1
    record = assets.load_manifest(tmp_path / "manifest.jsonl")[0]
    assert record["ai_generated"] is True
    assert record["source"]["type"] == "grokbot"
    assert "excluded.png" not in record["path"]
