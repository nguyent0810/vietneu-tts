import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from pipelines.vsd import pipeline as p


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "BASE", tmp_path)
    monkeypatch.setattr(p, "QUEUED", tmp_path / "queue")
    monkeypatch.setattr(p, "LOG", tmp_path / "logs" / "vsd_pipeline.jsonl")
    monkeypatch.setattr(p, "LEDGER", tmp_path / "uploaded.json")
    for state in p.STATES:
        (p.QUEUED / state).mkdir(parents=True)


def item(i="a", **extra):
    obj = {"id": i, "channel": "vsd", "lane": "vsd_su", "theme": "x", "lines": [], "scenes": [], "out": f"out/{i}.mp4",
           "packaging": {"title": "title", "description_first_line": "desc", "hashtags": ["#vsd"], "sources": []}}
    obj.update(extra)
    return obj


def put(state, obj):
    (p.QUEUED / state).mkdir(parents=True, exist_ok=True)
    f = p.QUEUED / state / f"{obj['id']}.json"
    f.write_text(json.dumps(obj))
    return f


def test_claim_oldest_and_transition():
    a = put("ready", item("a")); b = put("ready", item("b"))
    a.touch(); b.touch()
    claimed = p.claim("ready", "rendering")
    assert claimed == p.QUEUED / "rendering" / "a.json"
    assert not a.exists() and b.exists()
    assert p.transition(claimed, "rendered").exists()


def test_concurrent_claims_do_not_take_same_item():
    put("ready", item("a")); put("ready", item("b"))
    with ThreadPoolExecutor(max_workers=2) as pool:
        claimed = list(pool.map(lambda _: p.claim("ready", "rendering"), range(2)))
    assert {x.name for x in claimed} == {"a.json", "b.json"}


def test_render_exit_codes_and_fail_reason(monkeypatch):
    assert p.next_render() == 10
    put("ready", item())
    monkeypatch.setattr(p.subprocess, "Popen", lambda *a, **kw: type("P", (), {"pid": 1, "returncode": 7, "communicate": lambda self, **kw: ("", "bad")})())
    assert p.next_render() == 20
    assert (p.QUEUED / "failed" / "a.json").exists()
    assert "studio exited 7" in (p.QUEUED / "failed" / "a.log.json").read_text()


def test_render_success_runs_qa(monkeypatch):
    put("ready", item())
    monkeypatch.setattr(p.subprocess, "Popen", lambda *a, **kw: type("P", (), {"pid": 1, "returncode": 0, "communicate": lambda self, **kw: ("", "")})())
    monkeypatch.setattr(p, "qa_render", lambda spec, mp4: None)
    assert p.next_render() == 0
    assert (p.QUEUED / "rendered" / "a.json").exists()


def test_rolling_limit_duplicate_and_upload_dry_run(monkeypatch):
    now = datetime.now(timezone.utc)
    p._atomic_json(p.LEDGER, [{"id": f"old{i}", "uploaded_at": (now - timedelta(hours=1)).isoformat()} for i in range(24)])
    put("rendered", item())
    assert p.next_upload(dry_run=True, use_coverage=False) == 20
    assert (p.QUEUED / "failed" / "a.json").exists()
    p._atomic_json(p.LEDGER, [{"id": "a", "uploaded_at": now.isoformat()}])
    put("rendered", item())
    assert p.next_upload(dry_run=True, use_coverage=False) == 20


def test_slot_selection_occupied_and_min_lead():
    now = datetime(2026, 11, 3, 4, 50, tzinfo=timezone.utc)
    slot = p.next_slot(now, set(), ("05:00", "12:00"))
    assert slot == datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)
    taken = p.next_slot(now, {"2026-11-03T12:00"}, ("05:00", "12:00"))
    assert taken == datetime(2026, 11, 4, 5, 0, tzinfo=timezone.utc)


def test_dry_run_never_calls_uploader(monkeypatch, capsys):
    put("rendered", item())
    monkeypatch.setattr(p, "upload_short", lambda *a, **k: pytest.fail("must not upload"))
    assert p.next_upload(dry_run=True, use_coverage=False) == 0
    assert capsys.readouterr().out == ""
    assert (p.QUEUED / "rendered" / "a.json").exists()


def test_real_upload_mocked_writes_ledger(monkeypatch):
    put("rendered", item())
    monkeypatch.setenv("VSD_CREDS", "/fake/not-read.json")
    monkeypatch.setattr(p, "resolve_occupied", lambda _credentials: set())
    monkeypatch.setattr(p, "_remote_uploads", lambda _credentials: [])
    calls = []
    monkeypatch.setattr(p, "upload_short", lambda *a, **k: calls.append((a, k)) or "vid123")
    assert p.next_upload(use_coverage=True) == 0
    assert len(calls) == 1
    assert calls[0][1]["channel"] == "vsd"
    assert (p.QUEUED / "uploaded" / "a.json").exists()
    assert json.loads(p.LEDGER.read_text())[0]["video_id"] == "vid123"


def test_status_json_counts():
    put("ready", item())
    assert p.status()["counts"]["ready"] == 1


def test_crash_after_upload_is_reconciled_without_second_upload(monkeypatch):
    monkeypatch.setenv("VSD_CREDS", "/fake/not-read.json")
    started = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    put("uploading", {**item(), "started_at": started, "attempt": 1, "marker": "vsd-a", "title": "title", "path": "out/a.mp4", "publish_at": started})
    monkeypatch.setattr(p, "_remote_uploads", lambda _credentials: [{"id": "vid123", "tags": ["vsd-a"], "description": "#vsd:a", "published_at": datetime.now(timezone.utc).isoformat()}])
    monkeypatch.setattr(p, "upload_short", lambda *a, **k: pytest.fail("must reconcile first"))
    assert p.next_upload() == p.EXIT_EMPTY
    assert json.loads(p.LEDGER.read_text())[0]["video_id"] == "vid123"
    assert (p.QUEUED / "uploaded" / "a.json").exists()


def test_old_unmatched_intent_allows_exactly_one_retry(monkeypatch):
    monkeypatch.setenv("VSD_CREDS", "/fake/not-read.json")
    old = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    intent = {**item(), "started_at": old, "attempt": 1, "marker": "vsd-a", "title": "title", "path": "out/a.mp4", "publish_at": old}
    put("uploading", intent)
    monkeypatch.setattr(p, "_remote_uploads", lambda _credentials: [])
    monkeypatch.setattr(p, "resolve_occupied", lambda _credentials: set())
    calls = []
    monkeypatch.setattr(p, "upload_short", lambda *a, **k: calls.append(1) or "retry-id")
    assert p.next_upload() == 0
    assert len(calls) == 1
    assert (p.QUEUED / "uploaded" / "a.json").exists()


def test_stale_rendering_lease_recovery_and_attempt_cap(monkeypatch):
    past = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    put("rendering", {**item(), "lease": {"claimed_at": past, "pid": os.getpid(), "host": "here"}})
    p.recover_stale_leases(10)
    ready = json.loads((p.QUEUED / "ready" / "a.json").read_text())
    assert ready["attempts"] == 1
    put("rendering", {**ready, "lease": {"claimed_at": past, "pid": os.getpid(), "host": "here"}})
    p.recover_stale_leases(10)
    assert (p.QUEUED / "failed" / "a.json").exists()


def test_remote_uploads_count_toward_daily_cap(monkeypatch):
    monkeypatch.setenv("VSD_CREDS", "/fake/not-read.json")
    now = datetime.now(timezone.utc).isoformat()
    put("rendered", item())
    monkeypatch.setattr(p, "_remote_uploads", lambda _credentials: [{"published_at": now} for _ in range(24)])
    monkeypatch.setattr(p, "upload_short", lambda *a, **k: pytest.fail("daily cap must block upload"))
    assert p.next_upload() == p.EXIT_ITEM_FAIL


def test_remote_lister_failure_defers_without_failing_item(monkeypatch):
    monkeypatch.setenv("VSD_CREDS", "/fake/not-read.json")
    put("rendered", item())
    monkeypatch.setattr(p, "_remote_uploads", lambda _credentials: (_ for _ in ()).throw(RuntimeError("offline")))
    assert p.next_upload() == p.EXIT_DEFERRED
    assert (p.QUEUED / "rendered" / "a.json").exists()


def test_process_group_kill_uses_term_then_kill(monkeypatch):
    class Proc:
        pid = 123
        def __init__(self): self.calls = []
        def wait(self, timeout=None):
            self.calls.append(timeout)
            if timeout is not None: raise p.subprocess.TimeoutExpired("cmd", timeout)
    proc = Proc(); sent = []
    monkeypatch.setattr(p.os, "killpg", lambda pid, sig: sent.append((pid, sig)))
    p._terminate_process_group(proc, 0.1)
    assert sent == [(123, p.signal.SIGTERM), (123, p.signal.SIGKILL)]


def test_cli_expected_outcome_json_and_zero_exit(monkeypatch, capsys):
    monkeypatch.setattr(p, "next_render", lambda _timeout: p.EXIT_EMPTY)
    assert p.main(["next-render"]) == 0
    assert json.loads(capsys.readouterr().out) == {"code": "no_work", "result": p.EXIT_EMPTY}
