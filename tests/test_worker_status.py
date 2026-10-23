"""Luật điều phối thợ: không gọi lặp thợ đang cạn (output/cl_staging/grok/worker_status.py)."""
import importlib.util
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "output/cl_staging/grok/worker_status.py"
import pytest as _pt  # noqa: E402
if not (Path(__file__).resolve().parents[1] / "output/cl_staging/grok/worker_status.py").exists():   # công cụ ở output/ (gitignore): CI không có
    _pt.skip("output/cl_staging/grok/worker_status.py chỉ có trên máy dựng", allow_module_level=True)


@pytest.fixture
def ws(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("worker_status", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
    calls = []
    monkeypatch.setattr(mod, "probe", lambda w: calls.append(w) or False)
    mod._probe_calls = calls
    return mod


AGY_LOG = 'AGY_ERROR: {"short_error":"RESOURCE_EXHAUSTED (code 429): Individual quota reached. Resets in 75h18m53s."}'
GROK_LOG = 'Error: Internal error: {"message": "API error (status 402 Payment Required): Grok Build usage balance exhausted"}'


def test_classify_kinds(ws):
    assert ws.classify("agy", AGY_LOG, 1000)[:2] == ("quota", "reset")
    assert ws.classify("agy", AGY_LOG, 1000)[2] == 1000 + 75 * 3600 + 18 * 60 + 53
    assert ws.classify("grok", GROK_LOG, 1000)[:2] == ("quota", "balance")
    assert ws.classify("codex", "ERROR: status 429 Too Many Requests", 1000)[:2] == ("quota", "rate")
    assert ws.classify("grok", "báo cáo: media 95/402 đạt", 1000)[0] == "ok"   # số 402 trong nội dung không tính


def test_reset_kind_never_called_before_reset(ws, tmp_path):
    log = tmp_path / "a.log"; log.write_text(AGY_LOG)
    ws.record("agy", str(log))
    base = log.stat().st_mtime
    for h in (1, 5, 24, 75):                     # bản cũ thử lại mỗi giờ -> 3 task trượt
        assert ws.available("agy", now=base + h * 3600) is False
    assert ws._probe_calls == []                 # không cả thử nhẹ
    assert ws.available("agy", now=base + 76 * 3600) is True   # qua giờ reset: giao task thật


def test_balance_backoff_grows(ws, tmp_path):
    t = 10_000.0
    rec = ws.set_quota("grok", "balance", None, "402", now=t)
    assert rec["next_try"] == t + 3600
    rec = ws.set_quota("grok", "balance", None, "402", now=t)
    assert rec["next_try"] == t + 2 * 3600
    for _ in range(10):
        rec = ws.set_quota("grok", "balance", None, "402", now=t)
    assert rec["next_try"] == t + 12 * 3600      # trần 12 giờ
    assert ws.available("grok", now=t + 3600) is False
    assert ws._probe_calls == []
    ws.available("grok", now=t + 13 * 3600)
    assert ws._probe_calls == ["grok"]           # tới giờ mới thử nhẹ


def test_user_reset_clears(ws):
    ws.set_quota("grok", "balance", None, "402", now=1.0)
    ws.reset("grok")
    assert ws.available("grok") is True


def test_success_after_balance_resets_backoff(ws, tmp_path):
    ws.set_quota("grok", "balance", None, "402", now=1.0)
    ws.set_quota("grok", "balance", None, "402", now=1.0)
    ok = tmp_path / "g.log"; ok.write_text("Đã ghi báo cáo.")
    ws.record("grok", str(ok))
    assert ws.load()["grok"]["state"] == "ok"
    rec = ws.set_quota("grok", "balance", None, "402", now=5.0)
    assert rec["next_try"] == 5.0 + 3600         # đếm lại từ đầu
