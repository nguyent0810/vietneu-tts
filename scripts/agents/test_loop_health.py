import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("loop_health.py")
SPEC = importlib.util.spec_from_file_location("loop_health", MODULE_PATH)
loop_health = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loop_health)


def root(tmp_path):
    path = tmp_path / "grok"
    for name in ("heartbeat", "queue/.running", "logs", "reports", "queue"):
        (path / name).mkdir(parents=True, exist_ok=True)
    return path


def test_stale_heartbeat_is_error(tmp_path):
    path = root(tmp_path)
    (path / "heartbeat/lane.json").write_text(json.dumps({
        "loop_pid": os.getpid(), "updated_at_epoch": time.time() - 301
    }))
    rows, errors = loop_health.check(path)
    assert any("heartbeat lane" in item for item in errors)
    assert any("LỖI" in row for row in rows)


def test_dead_lock_pid_is_error(tmp_path):
    path = root(tmp_path)
    (path / "queue/.running/task").write_text("999999999 2026-11-03 00:00:00")
    _, errors = loop_health.check(path)
    assert any("khóa task" in item for item in errors)


def test_stalled_log_without_report_is_error(tmp_path):
    path = root(tmp_path)
    now = time.time()
    (path / "heartbeat/lane.json").write_text(json.dumps({
        "loop_pid": os.getpid(), "updated_at_epoch": now, "task": "task", "worker": "agy"
    }))
    log = path / "logs/task.agy.log"
    log.write_text("worker output")
    os.utime(log, (now - 46 * 60, now - 46 * 60))
    _, errors = loop_health.check(path, now)
    assert any("đứng hơn 45 phút" in item for item in errors)


def test_sweep_moves_dead_lock_to_stale(tmp_path):
    path = root(tmp_path)
    lock = path / "queue/.running/task"
    lock.write_text("999999999 2026-11-03 00:00:00")
    moved = loop_health.sweep_stale(path / "queue/.running", path / "logs/loop.log")
    assert len(moved) == 1
    assert moved[0].parent.name == "_stale"
    assert not lock.exists()
    assert "khóa mồ côi" in (path / "logs/loop.log").read_text()


def test_idle_queue_without_live_lane_is_error(tmp_path):
    path = root(tmp_path)
    (path / "queue/waiting.md").write_text("ticket")
    _, errors = loop_health.check(path)
    assert any("queue có task chờ" in item for item in errors)


def test_live_legacy_lock_counts_as_lane_during_rollout(tmp_path):
    path = root(tmp_path)
    (path / "queue/waiting.md").write_text("ticket")
    (path / "queue/.running/busy").write_text(f"{os.getpid()} running")
    _, errors = loop_health.check(path)
    assert not any("queue có task chờ" in item for item in errors)


def test_timeout_kills_worker_and_records_report_and_ledger(tmp_path, monkeypatch):
    path = root(tmp_path)
    log = path / "logs/sleep.log"
    monkeypatch.setenv("AGENT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    child_pid_file = tmp_path / "child.pid"
    child_code = (
        "import os,signal,subprocess,sys,time; "
        "p=subprocess.Popen([sys.executable,'-c',"
        "'import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)']); "
        f"open({str(child_pid_file)!r},'w').write(str(p.pid)); time.sleep(60)"
    )
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--root", str(path), "run", "--timeout", "2",
         "--log", str(log), "--task", "sleep_task", "--worker", "agy",
         "--started", "2026-11-03T00:00:00Z", "--", sys.executable, "-c", child_code],
        timeout=9,
    )
    assert result.returncode == 124
    report = (path / "reports/sleep_task.md").read_text()
    assert "THỢ TREO" in report and "logs/sleep.log" in report
    record = json.loads((tmp_path / "ledger.jsonl").read_text().splitlines()[-1])
    assert record["outcome"] == "timeout"
    child_pid = int(child_pid_file.read_text())
    with pytest.raises(ProcessLookupError):
        os.kill(child_pid, 0)


def test_grokbot_done_job_waits_for_lead_then_is_suppressed(tmp_path):
    base = tmp_path / "grokbot/job-a"
    output = base / "out"
    output.mkdir(parents=True)
    (base / "job.json").write_text(json.dumps({"output_dir": str(output)}))
    (output / "result.txt").write_text("ready")
    assert loop_health.grokbot_rows(tmp_path / "grokbot") == ["GrokBot job-a XONG – chờ Lead"]
    (base / "LEAD_DA_XEM").touch()
    assert loop_health.grokbot_rows(tmp_path / "grokbot") == []


def test_grokbot_no_result_over_60_minutes_is_reported(tmp_path):
    base = tmp_path / "grokbot/job-b"
    base.mkdir(parents=True)
    job = base / "job.json"
    job.write_text(json.dumps({"output_dir": str(base / "out")}))
    old = time.time() - 3601
    os.utime(job, (old, old))
    assert loop_health.grokbot_rows(tmp_path / "grokbot") == ["GrokBot job-b chưa trả | 60 phút"]
