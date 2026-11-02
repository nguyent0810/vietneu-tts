import datetime as dt
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("quota_state", Path(__file__).parents[1] / "scripts/agents/quota_state.py")
q = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(q)


def test_codex_multiple_windows_and_missing(tmp_path):
    f = tmp_path / "x.jsonl"
    f.write_text("\n".join(json.dumps(x) for x in [
        {"type":"event_msg","timestamp":"2026-11-02T00:00:00Z","payload":{"type":"token_count","rate_limits":{"primary":{"window_minutes":300,"used_percent":50,"resets_at":1793606400},"secondary":{"window_minutes":10080,"used_percent":25,"resets_at":1794000000}}}},
        {"type":"event_msg","timestamp":"2026-11-02T01:00:00Z","payload":{"type":"token_count","rate_limits":{"primary":{"window_minutes":300,"used_percent":60,"resets_at":1793606400}}}},
    ]))
    windows = q.read_codex(tmp_path)
    assert len(windows) == 2
    assert next(w for w in windows if w["name"].startswith("primary"))["used_pct"] == 60
    assert q.read_codex(tmp_path / "absent") == []


def test_claude_limit_notice_fixture(tmp_path):
    f = tmp_path / "transcript.jsonl"
    f.write_text(json.dumps({"type":"system","subtype":"informational","level":"notice","timestamp":"2026-10-07T05:15:57Z","content":"You've hit your weekly limit · resets Oct 12 at 7am (Asia/Saigon)"}))
    rows = q.read_claude(tmp_path)
    assert len(rows) == 1 and rows[0]["name"] == "weekly" and rows[0]["used_pct"] is None


def test_claude_quoted_limit_in_user_or_tool_is_ignored(tmp_path):
    f = tmp_path / "transcript.jsonl"
    rows = [
        {"type":"user","timestamp":"2026-11-02T02:18:21Z","content":"Usage limit reached · continuing automatically at 10:30am"},
        {"type":"tool_result","timestamp":"2026-11-02T02:18:22Z","content":"Usage limit reached"},
    ]
    f.write_text("\n".join(json.dumps(row) for row in rows))
    assert q.read_claude(tmp_path) == []


def test_worker_log_agy_grok_and_missing(tmp_path):
    (tmp_path / "sample.agy.log").write_text("I1022 07:12:00 ERROR RESOURCE_EXHAUSTED Individual quota reached, Resets in 96h40m37s\n")
    (tmp_path / "sample.grok.log").write_text("402 Payment Required: balance exhausted\n")
    got = q.read_worker_logs(tmp_path)
    assert len(got["agy"]) == len(got["grok"]) == 1
    assert q.read_worker_logs(tmp_path / "none")["agy"] == []


def test_pressure_formula_and_old_measurement():
    now = dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc)
    start = now - dt.timedelta(hours=2.5)
    w = q.make_window("5h", 50, now.timestamp()+9000, "fixture", now.timestamp(), 300)
    # At halfway through a 5-hour window, 50% used means pressure exactly 1.
    state, pressure, stale = q.state_for([w], now)
    assert state == "ok" and abs(pressure - 1.0) < 1e-6 and not stale
    old = q.make_window("5h", 20, now.timestamp()+9000, "fixture", (now-dt.timedelta(hours=7)).timestamp(), 300)
    assert q.state_for([old], now)[2] is True


def test_stale_exhaustion_is_unknown_with_last_exhausted_reference():
    now = dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc)
    old = q.make_window("short", None, "2026-11-01T12:00:00Z", "Claude transcript limit notice",
                        (now-dt.timedelta(days=1)).timestamp())
    assert q.state_for([old], now)[0] == "UNKNOWN"
    with patch.object(q, "read_claude", return_value=[old]):
        snap = q.build_snapshot(home=Path("/nonexistent-home"), root=Path("/nonexistent-root"), now=now)
    assert snap["agents"]["claude"]["state"] == "UNKNOWN"
    assert snap["agents"]["claude"]["last_exhausted_at"] == old["observed_at"]


def test_expired_or_unparseable_reset_does_not_mean_exhausted():
    now = dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc)
    expired = q.make_window("short", None, "2026-11-01T12:00:00Z", "Claude transcript limit notice", now.timestamp())
    unparseable = q.make_window("weekly", None, "Oct 12", "Claude transcript limit notice", now.timestamp())
    assert q.state_for([expired], now)[0] == "UNKNOWN"
    assert q.state_for([unparseable], now)[0] == "UNKNOWN"
    missing = q.make_window("short", None, None, "Claude transcript limit notice", now.timestamp())
    assert q.state_for([missing], now)[0] == "UNKNOWN"


def test_claude_reset_timezone_midnight_and_year():
    saigon = dt.timezone(dt.timedelta(hours=7))
    # 23:50 local, "continuing at 1:00am" -> next local day, not earlier the same day in UTC.
    got = q.claude_reset("Usage limit reached · continuing automatically at 1:00am", "2026-11-01T16:50:00Z", saigon)
    assert dt.datetime.fromisoformat(got) == dt.datetime(2026, 11, 2, 1, 0, tzinfo=saigon)
    # Named zone wins over machine zone; "Jan 3" seen in late December is next year.
    got = q.claude_reset("You've hit your weekly limit · resets Jan 3 at 7am (Asia/Saigon)", "2026-12-30T00:00:00Z", dt.timezone.utc)
    assert got.startswith("2027-01-03T07:00:00+07:00")
    assert q.claude_reset("limit reached, try later", "2026-11-02T00:00:00Z", saigon) is None
    assert q.claude_reset("resets Foo 12", "2026-11-02T00:00:00Z", saigon) is None


def test_notice_with_future_reset_is_exhausted(tmp_path):
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    stamp = now.isoformat().replace("+00:00", "Z")
    (tmp_path / "t.jsonl").write_text(json.dumps({"type":"system","subtype":"informational","level":"notice","timestamp":stamp,
                                                 "content":"Usage limit reached · continuing automatically at 10:30am"}))
    rows = q.read_claude(tmp_path)
    assert len(rows) == 1 and rows[0]["resets_at"]
    assert q.state_for(rows, now)[0] == "exhausted"


def test_unexpected_json_shapes_do_not_crash(tmp_path):
    (tmp_path / "a.jsonl").write_text("\n".join(["[1,2]", "null", json.dumps({"type":"event_msg","payload":[],"rate_limits":1}),
                                                 json.dumps({"type":"system","subtype":"informational","level":"notice","timestamp":None,"content":"limit reached"})]))
    assert q.read_codex(tmp_path) == []
    assert q.read_claude(tmp_path) == []
    (tmp_path / "s").mkdir(); (tmp_path / "s/usage.json").write_text(json.dumps({"turns": [None, 3, {"endedAt": "2026-11-02T00:00:00Z"}]}))
    assert q.read_grok_usage(tmp_path) == "2026-11-02T00:00:00Z"
    (tmp_path / "s/usage.json").write_text("[]")
    assert q.read_grok_usage(tmp_path) is None


def test_unknown_agents_when_data_missing(tmp_path):
    snap = q.build_snapshot(home=tmp_path, root=tmp_path, now=dt.datetime(2026,11,2,tzinfo=dt.timezone.utc))
    for agent in ("codex", "claude", "agy", "grok", "gemini_cli", "grokbot"):
        assert snap["agents"][agent]["state"] == "UNKNOWN"
