import importlib.util
import json
import multiprocessing
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/agents/agent_ledger.py"
spec = importlib.util.spec_from_file_location("agent_ledger", MODULE_PATH)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


def stamp(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


@pytest.mark.skipif(not ledger.WORKER_STATUS.exists(), reason="worker_status.py chỉ có trên máy Lead (output/ không theo git)")
@pytest.mark.parametrize(
    "agent,line,expected,kind",
    [
        ("grok", "Payment Required: HTTP 402", "quota", "balance"),
        ("agy", "AGY_ERROR: 429", "quota", "rate"),
        ("agy", "HTTP 429 RESOURCE_EXHAUSTED", "quota", "rate"),
        ("agy", "RESOURCE_EXHAUSTED", "quota", "rate"),
        ("codex", "ordinary completed output", "ok", None),
    ],
)
def test_record_classifies_worker_status_signatures(tmp_path, monkeypatch, agent, line, expected, kind):
    log = tmp_path / "worker.log"
    log.write_text(line, encoding="utf-8")
    monkeypatch.setenv("AGENT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    row = ledger.record_run(ticket="sample", agent=agent, started_at=stamp(1000), ended_at=stamp(1060), log_path=str(log))
    assert row["outcome"] == expected
    assert row["quota_kind"] == kind
    assert row["model"] is None
    assert row["tokens"] is None


def test_codex_session_tokens_and_model_match_run_window(tmp_path, monkeypatch):
    sessions = tmp_path / ".codex" / "sessions"
    sessions.mkdir(parents=True)
    start, end = 1_800_000_000, 1_800_000_060
    session = sessions / "session.jsonl"
    session.write_text("\n".join(json.dumps(row) for row in [
        {"type": "session_meta", "payload": {"timestamp": stamp(start + 1), "cwd": str(ledger.ROOT)}},
        {"type": "turn_context", "payload": {"model": "gpt-test-model"}},
        {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 100, "cached_input_tokens": 70, "output_tokens": 20, "total_tokens": 120}}}},
    ]) + "\n", encoding="utf-8")
    monkeypatch.setattr(ledger.Path, "home", lambda: tmp_path)
    os.utime(session, (start + 2, start + 2))
    monkeypatch.setenv("AGENT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    row = ledger.record_run(ticket="sample", agent="codex", started_at=stamp(start), ended_at=stamp(end))
    assert row["model"] == "gpt-test-model"
    assert row["tokens"] == {"input_tokens": 100, "cached_input_tokens": 70, "output_tokens": 20, "total_tokens": 120}


def test_grok_usage_turn_tokens_match_run_window(tmp_path, monkeypatch):
    start, end = 1_800_000_000, 1_800_000_060
    usage = tmp_path / "usage.json"
    usage.write_text(json.dumps({"turns": [
        {"endedAt": stamp(start + 30), "inputTokens": 90, "outputTokens": 10, "totalTokens": 100, "primaryModelId": "grok-test"},
        {"endedAt": stamp(start - 600), "inputTokens": 999, "outputTokens": 99, "totalTokens": 1098, "primaryModelId": "old-model"},
    ]}), encoding="utf-8")
    os.utime(usage, (end, end))
    monkeypatch.setenv("GROK_USAGE_PATH", str(usage))
    monkeypatch.setenv("AGENT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    row = ledger.record_run(ticket="sample", agent="grok", started_at=stamp(start), ended_at=stamp(end))
    assert row["model"] == "grok-test"
    assert row["tokens"] == {"inputTokens": 90, "outputTokens": 10, "totalTokens": 100}


def test_missing_values_are_null(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    row = ledger.record_run(ticket="undetermined", agent="agy", started_at=stamp(1000), ended_at=stamp(1001))
    stored = json.loads((tmp_path / "ledger.jsonl").read_text(encoding="utf-8"))
    assert row["model"] is None and row["tokens"] is None
    assert stored["model"] is None and stored["tokens"] is None


def test_disabled_ledger_writes_nothing(tmp_path, monkeypatch):
    target = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("AGENT_LEDGER", "0")
    monkeypatch.setenv("AGENT_LEDGER_PATH", str(target))
    assert ledger.record_run(ticket="sample", agent="agy") is None
    assert not target.exists()


def test_write_failure_warns_without_raising(tmp_path, monkeypatch, capsys):
    target = tmp_path / "is-a-directory"
    target.mkdir()
    monkeypatch.setenv("AGENT_LEDGER_PATH", str(target))
    assert ledger.record_run(ticket="sample", agent="agy") is None
    assert "cảnh báo không ghi được sổ" in capsys.readouterr().err


def test_summary_counts_by_agent_and_type(tmp_path, monkeypatch):
    rows = [
        {"agent": "codex", "ticket": "review-1", "task_type": "review", "role": "reviewer", "started_at": "2026-11-02T08:00:00Z", "duration_seconds": 20, "outcome": "ok", "verdict": "ĐẠT"},
        {"agent": "codex", "ticket": "review-1", "task_type": "review", "role": "reviewer", "started_at": "2026-11-02T09:00:00Z", "duration_seconds": 40, "outcome": "quota", "verdict": "KHÔNG ĐẠT"},
        {"agent": "grok", "task_type": "research", "role": "worker", "started_at": "2026-11-01T09:00:00Z", "duration_seconds": None, "outcome": "ok", "verdict": None},
    ]
    report = ledger.summary(rows)
    assert "codex | review | 2 | 1 | 1 | 1 | 30.0 | 1/1 (100%)" in report
    assert "grok | research | 1 | 1 | 0 | 0 | — | —" in report


def _write_concurrent_records(path, worker_id, count):
    os.environ["AGENT_LEDGER_PATH"] = str(path)
    for index in range(count):
        ledger.record_run(ticket=f"{worker_id}-{index}", agent="agy", outcome="ok")


def test_concurrent_appends_are_complete_jsonl(tmp_path):
    target = tmp_path / "concurrent.jsonl"
    ctx = multiprocessing.get_context("fork")
    processes = [ctx.Process(target=_write_concurrent_records, args=(target, worker, 50)) for worker in range(8)]
    for process in processes:
        process.start()
    for process in processes:
        process.join(20)
        assert process.exitcode == 0
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 400
    assert all(isinstance(json.loads(line), dict) for line in lines)


def _wrapper_env(tmp_path, fake_codex):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    codex = bindir / "codex"
    codex.write_text(fake_codex, encoding="utf-8")
    codex.chmod(0o755)
    env = os.environ.copy()
    env.update(PATH=f"{bindir}:{env['PATH']}", AGENT_LEDGER_PATH=str(tmp_path / "ledger.jsonl"))
    return env


def test_codex_wrapper_preserves_exit_code_and_sends_eof(tmp_path):
    seen = tmp_path / "eof"
    fake = f"#!/bin/sh\nif IFS= read -r line; then exit 91; fi\nprintf eof > '{seen}'\nexit 7\n"
    env = _wrapper_env(tmp_path, fake)
    prompt = tmp_path / "prompt.md"
    prompt.write_text("review", encoding="utf-8")
    report = tmp_path / "report.md"
    result = subprocess.run([str(Path(__file__).resolve().parents[1] / "scripts/agents/codex_review.sh"), "test", str(report), str(prompt)], env=env, timeout=10)
    assert result.returncode == 7
    assert seen.read_text() == "eof"


def test_codex_wrapper_ledger_failure_preserves_exit_code(tmp_path):
    env = _wrapper_env(tmp_path, "#!/bin/sh\nexit 6\n")
    bad_ledger = tmp_path / "ledger-is-directory"
    bad_ledger.mkdir()
    env["AGENT_LEDGER_PATH"] = str(bad_ledger)
    prompt = tmp_path / "prompt.md"
    prompt.write_text("review", encoding="utf-8")
    result = subprocess.run(
        [str(Path(__file__).resolve().parents[1] / "scripts/agents/codex_review.sh"), "ledger-error", str(tmp_path / "report.md"), str(prompt)],
        env=env, timeout=10,
    )
    assert result.returncode == 6


def test_codex_wrapper_watchdog_kills_fake_codex_and_records_failure(tmp_path):
    env = _wrapper_env(tmp_path, "#!/bin/sh\nsleep 30\n")
    env["CODEX_REVIEW_TIMEOUT"] = "2"
    prompt = tmp_path / "prompt.md"
    prompt.write_text("review", encoding="utf-8")
    report = tmp_path / "report.md"
    started = time.monotonic()
    result = subprocess.run([str(Path(__file__).resolve().parents[1] / "scripts/agents/codex_review.sh"), "watchdog", str(report), str(prompt)], env=env, timeout=10)
    assert time.monotonic() - started < 8
    assert result.returncode != 0
    row = json.loads((tmp_path / "ledger.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert row["outcome"] == "failed"
    assert row["exit_code"] != 0


def test_ledger_failure_does_not_change_run_worker_status(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    loop_path = repo / "output/cl_staging/grok/loop_v4_ledger.sh"
    if not loop_path.exists():
        pytest.skip("loop_v4_ledger.sh chỉ có trên máy Lead (output/ không theo git)")
    loop = loop_path.read_text(encoding="utf-8")
    function = loop.split("run_worker() {", 1)[1].split("\n}\n\nworkers=", 1)[0]
    bindir = tmp_path / "bin"
    bindir.mkdir()
    agy = bindir / "agy"
    agy.write_text("#!/bin/sh\nexit 9\n", encoding="utf-8")
    agy.chmod(0o755)
    ws = bindir / "worker_status.py"
    ws.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    ws.chmod(0o755)
    bad_ledger = tmp_path / "ledger-is-directory"
    bad_ledger.mkdir()
    logdir = tmp_path / "logs"
    logdir.mkdir()
    harness = tmp_path / "run.sh"
    harness.write_text(
        "#!/bin/bash\n" +
        f"G='{tmp_path}'\nROOT='{repo}'\nPY='{repo}/.venv/bin/python'\nWS='{ws}'\nLEDGER='{repo}/scripts/agents/agent_ledger.py'\n" +
        f"PATH='{bindir}:'\"$PATH\"\n" +
        "prompt_for() { :; }\n" + "run_worker() {" + function + "\n}\nrun_worker agy sample\n",
        encoding="utf-8",
    )
    harness.chmod(0o755)
    env = os.environ.copy()
    env["AGENT_LEDGER_PATH"] = str(bad_ledger)
    result = subprocess.run([str(harness)], env=env, timeout=10)
    assert result.returncode == 9
