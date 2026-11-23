import datetime as dt
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runway = load("short_runway", "tools/short_runway.py")
review_due = load("review_due", "tools/review_due.py")


def test_runway_streak_and_first_missing_day():
    start = dt.date(2026, 11, 23)
    coverage = {"2026-11-23": 5, "2026-11-24": 7, "2026-11-25": 4,
                "2026-11-26": 9}
    summary = runway.summarize(coverage, start, 4, 5)
    assert summary["days_covered"] == 2
    assert summary["first_missing_day"] == "2026-11-25"
    assert list(summary["coverage"].values()) == [5, 7, 4, 9]


def test_review_due_warns_for_short_runway_and_stale_cache(tmp_path):
    path = tmp_path / "short_runway.json"
    path.write_text(json.dumps({
        "measured_at": "2026-11-20T09:00:00+07:00",
        "channels": {"FS": {"days_covered": 4}, "BUD": {"days_covered": 12}},
    }))
    warnings = review_due.runway_warnings(dt.date(2026, 11, 23), path)
    assert any("FS còn 4 ngày" in warning for warning in warnings)
    assert any("cũ 3 ngày" in warning for warning in warnings)
    assert all("CẢNH BÁO ĐỎ" in warning for warning in warnings)


def test_review_due_main_prints_runway_warnings(monkeypatch, tmp_path, capsys):
    cache = tmp_path / "short_runway.json"
    old_day = dt.date.today() - dt.timedelta(days=3)
    cache.write_text(json.dumps({
        "measured_at": old_day.isoformat() + "T09:00:00+07:00",
        "channels": {"BUD": {"days_covered": 2}},
    }))
    monkeypatch.setattr(review_due, "RUNWAY", cache)
    monkeypatch.setattr(review_due, "ROOT", tmp_path)
    monkeypatch.setattr(review_due, "LOG", tmp_path / "review_log.json")
    monkeypatch.setattr(review_due, "HERE", tmp_path)
    monkeypatch.setattr(review_due, "BRIEFS", tmp_path / "briefs")
    assert review_due.main([]) == 0
    output = capsys.readouterr().out
    assert "CẢNH BÁO ĐỎ: BUD còn 2 ngày phủ Short" in output
    assert "CẢNH BÁO ĐỎ: cache Short runway cũ 3 ngày" in output


def test_offline_uses_cache_without_network_or_measure(monkeypatch, tmp_path, capsys):
    payload = {"measured_at": "2026-11-23T09:00:00+07:00", "target": 5,
               "channels": {"FS": {"days_covered": 1, "first_missing_day": "2026-11-24",
                                    "coverage": {"2026-11-23": 5, "2026-11-24": 0}}}}
    cache = tmp_path / "short_runway.json"
    cache.write_text(json.dumps(payload))
    monkeypatch.setattr(runway, "CACHE", cache)
    monkeypatch.setattr(runway, "measure", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("measure called")))
    monkeypatch.setattr(runway, "coverage_from_hf", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network called")))
    assert runway.main(["--offline"]) == 0
    assert "ngày đầu thiếu: 2026-11-24" in capsys.readouterr().out
