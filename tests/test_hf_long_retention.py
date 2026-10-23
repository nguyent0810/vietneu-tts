"""hf_long_retention: dữ liệu giả, không gọi mạng."""
import json
import socket
from datetime import datetime, timezone

import pytest

import hf_long_retention as M
import youtube_analytics
import youtube_catalog

NOW = datetime(2026, 10, 21, 10, 0, tzinfo=timezone.utc)
OLD = "2026-09-01T12:00:00Z"


def _curve(points):
    return {
        "columnHeaders": [{"name": "elapsedVideoTimeRatio"}, {"name": "audienceWatchRatio"}],
        "rows": [[ratio, awr] for ratio, awr in points],
    }


def _metrics(views, avd, avp):
    return {
        "columnHeaders": [
            {"name": "views"},
            {"name": "averageViewDuration"},
            {"name": "averageViewPercentage"},
        ],
        "rows": [[views, avd, avp]],
    }


def _sources(pairs):
    return {
        "columnHeaders": [{"name": "insightTrafficSourceType"}, {"name": "views"}],
        "rows": [[name, views] for name, views in pairs],
    }


def _video(vid, *, privacy="public", published=OLD, duration="PT30M10S", title="Tên", publish_at=""):
    status = {"privacyStatus": privacy}
    if publish_at:
        status["publishAt"] = publish_at
    return {
        "id": vid,
        "snippet": {"title": title, "publishedAt": published},
        "status": status,
        "contentDetails": {"duration": duration},
    }


def _world(videos, curves, metrics, sources):
    calls = []

    def query(cred, params):
        calls.append((cred, params))
        vid = params["filters"].split("==", 1)[1]
        assert params["ids"] == "channel==MINE"
        assert "," not in vid
        if params.get("dimensions") == "elapsedVideoTimeRatio":
            assert params["metrics"] == "audienceWatchRatio"
            return curves[vid]
        if params.get("dimensions") == "insightTrafficSourceType":
            assert params["metrics"] == "views"
            return sources[vid]
        assert params["metrics"] == "views,averageViewDuration,averageViewPercentage"
        assert "dimensions" not in params
        return metrics[vid]

    def catalog(cred, url, params):
        calls.append((cred, params))
        assert url == youtube_catalog.VIDEOS_URL
        assert params["part"] == "snippet,contentDetails,status"
        ids = params["id"].split(",")
        return {"items": [videos[i] for i in ids if i in videos]}

    return query, catalog, calls


def _run(tmp_path, uploaded, videos, *, curves=None, metrics=None, sources=None, now=NOW, channel="fs", pauses=(0, 0)):
    query, catalog, calls = _world(videos, curves or {}, metrics or {}, sources or {})
    result = M.collect(
        channel,
        now=now,
        uploaded=uploaded,
        query=query,
        catalog=catalog,
        ledger_path=tmp_path / "retention_ledger.json",
        pauses=pauses,
    )
    return result, calls


def test_credentials_only_fs_and_bud():
    assert M.CHANNELS == {
        "fs": ".youtube_channels/phong_thuy.json",
        "bud": ".youtube_channels/phat_giao.json",
    }
    assert M.credentials_for("fs").name == "phong_thuy.json"
    assert M.credentials_for("bud").name == "phat_giao.json"
    assert M.LEDGER == M.ROOT / "output/cl_staging/long/retention_ledger.json"
    assert "hinh_su" not in json.dumps(M.CHANNELS)
    with pytest.raises(ValueError):
        M.credentials_for("hinh_su")


def test_nearest_point_tie_picks_earlier_ratio():
    curve = M.as_dicts(_curve([(0.07, 0.40), (0.05, 0.80)]))
    # Phút 1 của video 1000 giây là ratio 0.06, cách đều 0.05 và 0.07.
    assert M.watch_pct(curve, 1000, at_sec=60) == 80.0
    assert M.watch_pct(list(reversed(curve)), 1000, at_sec=60) == 80.0


def test_marks_and_short_video_and_over_100():
    curve = M.as_dicts(_curve([(0.01, 1.01), (0.25, 0.40), (0.50, 0.20), (1.0, 0.10)]))
    assert M.watch_pct(curve, 30, at_sec=60) is None
    assert M.watch_pct(curve, 30, at_sec=120) is None
    assert M.watch_pct(curve, 600, at_ratio=0.25) == 40.0
    assert M.watch_pct(curve, 600, at_ratio=0.50) == 20.0
    assert M.watch_pct(curve, 600, at_sec=6) == 101.0
    assert M.watch_pct([], 600, at_sec=60) is None
    assert M.watch_pct(curve, 0, at_ratio=0.25) is None


def test_suggested_share_is_related_video_only():
    assert M.suggested_share(M.as_dicts(_sources([("RELATED_VIDEO", 25), ("YT_SEARCH", 75)]))) == 25.0
    assert M.suggested_share(M.as_dicts(_sources([("YT_SEARCH", 10)]))) == 0.0
    assert M.suggested_share(M.as_dicts(_sources([("RELATED_VIDEO", 0)]))) is None
    assert M.suggested_share([]) is None
    assert M.suggested_share(M.as_dicts(_sources([("related_video", 10)]))) == 0.0


def test_age_is_vietnam_calendar():
    # 18/10 18:00 UTC = 19/10 01:00 VN. Tới 21/10 16:00 UTC vẫn là 2 ngày lịch, dù đã ~70 giờ.
    published = M.parse_utc("2026-10-18T18:00:00Z")
    now = datetime(2026, 10, 21, 16, 0, tzinfo=timezone.utc)
    assert M.age_days(published, now) == 2
    assert M.age_days(M.parse_utc("2026-10-18T00:30:00Z"), datetime(2026, 10, 21, 0, 30, tzinfo=timezone.utc)) == 3


def test_window_utc_start_and_pacific_end():
    published = M.parse_utc("2026-09-01T12:00:00Z")
    assert M.analytics_window(published, datetime(2026, 10, 21, 2, 0, tzinfo=timezone.utc)) == ("2026-08-31", "2026-10-20")
    assert M.analytics_window(published, datetime(2026, 10, 21, 10, 0, tzinfo=timezone.utc)) == ("2026-08-31", "2026-10-21")


def test_median_is_five_newest_not_oldest():
    rows = []
    for i, views in enumerate((10, 20, 30, 40, 50, 60), start=1):
        rows.append({
            "rid": f"L_fs_{i:02d}",
            "published_at": f"2026-09-{i:02d}T00:00:00Z",
            "views": views,
            "average_view_duration_s": views,
            "average_view_percentage": float(views),
            "ret_min1": float(views),
            "ret_min2": float(views),
            "ret_25": float(views),
            "ret_50": float(views),
            "suggested_pct": float(views),
        })
    med = M.median5(rows)
    assert med["n"] == 5
    assert med["rids"] == ["L_fs_06", "L_fs_05", "L_fs_04", "L_fs_03", "L_fs_02"]
    assert med["views"] == 40.0
    assert M.deltas(rows[-1], med)["views"] == 20.0
    assert M.deltas(rows[0], med)["views"] == -30.0


def test_collect_measures_public_old_only_and_compares(tmp_path):
    uploaded = {
        "L_bud_01": "bud",
        "L_fs_06_v1_rut_lich": "old",
        "L_fs_new": "new",
        "L_fs_priv": "priv",
        "L_fs_miss": "miss",
        "other": "x",
    }
    videos = {
        "old": _video("old", title="Bản cũ | rút", published="2026-09-01T00:00:00Z", duration="PT10M"),
        "new": _video("new", title="Mới", published="2026-10-19T12:00:00Z"),
        "priv": _video("priv", privacy="private", publish_at="2026-10-25T00:00:00Z"),
    }
    curves = {"old": _curve([(60 / 600, 0.70), (120 / 600, 0.50), (0.25, 0.40), (0.50, 0.20)])}
    metrics = {"old": _metrics(100, 180, 30)}
    sources = {"old": _sources([("RELATED_VIDEO", 40), ("YT_SEARCH", 60)])}
    result, calls = _run(tmp_path, uploaded, videos, curves=curves, metrics=metrics, sources=sources)
    assert [row["rid"] for row in result["rows"]] == ["L_fs_06_v1_rut_lich"]
    row = result["rows"][0]
    assert row["views"] == 100
    assert row["average_view_duration_s"] == 180.0
    assert row["average_view_percentage"] == 30.0
    assert row["ret_min1"] == 70.0
    assert row["ret_min2"] == 50.0
    assert row["ret_25"] == 40.0
    assert row["ret_50"] == 20.0
    assert row["suggested_pct"] == 40.0
    assert row["curve_n"] == 4
    assert row["window_start"] == "2026-08-31"
    assert row["vs_median5"]["views"] == 0.0
    assert {item["rid"]: item["reason"] for item in result["skipped"]} == {
        "L_fs_miss": "không thấy trên YouTube",
        "L_fs_new": "chưa đủ 3 ngày (lên 2026-10-19)",
        "L_fs_priv": "chưa công khai (private, hẹn 2026-10-25)",
    }
    creds = {call[0] for call in calls}
    assert len(creds) == 1
    assert next(iter(creds)).endswith(".youtube_channels/phong_thuy.json")
    assert "hinh_su" not in next(iter(creds))
    analytics = [params for _, params in calls if "metrics" in params]
    assert len(analytics) == 3
    text = M.render_table(result)
    assert "| Long | Tên | Lên sóng | Tuổi | Dài | View | Δview | AVD phút | ΔAVD | % xem | Δ% | Phút 1 | Δ1 | Phút 2 | Δ2 | 25% | Δ25 | 50% | Δ50 | Đề xuất | Δđx |" in text
    assert "Bản cũ / rút" in text
    assert "L_fs_new: chưa đủ 3 ngày" in text
    assert "Δ = video − trung vị 1 Long mới nhất cùng kênh." in text


def test_ledger_appends_by_day_and_replaces_same_day(tmp_path):
    uploaded = {"L_fs_01": "a", "L_bud_01": "b"}
    videos = {"a": _video("a", title="Tuổi Tý"), "b": _video("b", title="Kinh")}
    base_curve = _curve([(0.1, 0.5), (0.25, 0.4), (0.5, 0.2)])
    query, catalog, _ = _world(
        videos,
        {"a": base_curve, "b": base_curve},
        {"a": _metrics(10, 60, 10), "b": _metrics(8, 60, 10)},
        {"a": _sources([("RELATED_VIDEO", 1), ("YT_SEARCH", 1)]), "b": _sources([("RELATED_VIDEO", 1), ("YT_SEARCH", 1)])},
    )
    path = tmp_path / "retention_ledger.json"
    kw = dict(uploaded=uploaded, query=query, catalog=catalog, ledger_path=path, pauses=(0, 0))
    M.collect("fs", now=NOW, **kw)
    M.collect("bud", now=NOW, **kw)
    query2, catalog2, _ = _world(
        videos,
        {"a": base_curve},
        {"a": _metrics(11, 60, 10)},
        {"a": _sources([("RELATED_VIDEO", 1), ("YT_SEARCH", 1)])},
    )
    M.collect("fs", now=NOW, uploaded=uploaded, query=query2, catalog=catalog2, ledger_path=path, pauses=(0, 0))
    later = datetime(2026, 10, 22, 10, 0, tzinfo=timezone.utc)
    M.collect("fs", now=later, uploaded=uploaded, query=query2, catalog=catalog2, ledger_path=path, pauses=(0, 0))
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert [(s["measured_on"], s["channel"]) for s in saved["snapshots"]] == [
        ("2026-10-21", "bud"),
        ("2026-10-21", "fs"),
        ("2026-10-22", "fs"),
    ]
    day_fs = saved["snapshots"][1]
    assert day_fs["rows"][0]["views"] == 11
    assert day_fs["rows"][0]["title"] == "Tuổi Tý"
    assert saved["snapshots"][0]["rows"][0]["views"] == 8
    assert saved["snapshots"][2]["rows"][0]["views"] == 11


def test_young_or_private_does_not_query_analytics_or_write(tmp_path):
    uploaded = {"L_fs_01": "new"}
    videos = {"new": _video("new", published="2026-10-20T00:00:00Z")}
    result, calls = _run(tmp_path, uploaded, videos)
    assert result["rows"] == []
    assert result["skipped"][0]["reason"].startswith("chưa đủ 3 ngày")
    assert all("metrics" not in params for _, params in calls)
    assert not (tmp_path / "retention_ledger.json").exists()


def test_empty_analytics_is_skipped(tmp_path):
    uploaded = {"L_fs_01": "a"}
    videos = {"a": _video("a")}
    empty = {"columnHeaders": [{"name": "views"}], "rows": []}
    result, _ = _run(
        tmp_path, uploaded, videos,
        curves={"a": empty}, metrics={"a": empty}, sources={"a": empty},
    )
    assert result["rows"] == []
    assert result["skipped"][0]["reason"] == "Analytics chưa có số"
    assert not (tmp_path / "retention_ledger.json").exists()


def test_one_video_error_does_not_drop_the_other(tmp_path):
    uploaded = {"L_fs_01": "ok", "L_fs_02": "bad"}
    videos = {
        "ok": _video("ok", published="2026-09-01T00:00:00Z", title="Ổn"),
        "bad": _video("bad", published="2026-09-02T00:00:00Z", title="Lỗi"),
    }

    def query(cred, params):
        vid = params["filters"].split("==", 1)[1]
        if vid == "bad":
            raise youtube_analytics.YouTubeAnalyticsError("YouTube Analytics API lỗi (400): video hỏng")
        if params.get("dimensions") == "elapsedVideoTimeRatio":
            return _curve([(0.25, 0.5), (0.5, 0.2)])
        if params.get("dimensions") == "insightTrafficSourceType":
            return _sources([("RELATED_VIDEO", 1)])
        return _metrics(5, 30, 10)

    def catalog(cred, url, params):
        return {"items": [videos[i] for i in params["id"].split(",")]}

    result = M.collect(
        "fs", now=NOW, uploaded=uploaded, query=query, catalog=catalog,
        ledger_path=tmp_path / "retention_ledger.json", pauses=(0, 0),
    )
    assert [row["rid"] for row in result["rows"]] == ["L_fs_01"]
    assert result["skipped"][0]["rid"] == "L_fs_02"
    assert result["skipped"][0]["reason"].startswith("Analytics lỗi:")


def test_auth_error_aborts_instead_of_skipping(tmp_path):
    uploaded = {"L_fs_01": "a"}
    videos = {"a": _video("a")}

    def query(cred, params):
        raise youtube_analytics.YouTubeAnalyticsError("Refresh access_token thất bại: invalid_grant")

    def catalog(cred, url, params):
        return {"items": [videos["a"]]}

    with pytest.raises(youtube_analytics.YouTubeAnalyticsError):
        M.collect("fs", now=NOW, uploaded=uploaded, query=query, catalog=catalog, ledger_path=tmp_path / "x.json", pauses=(0, 0))


def test_retry_only_transient(monkeypatch):
    monkeypatch.setattr(M.time, "sleep", lambda _s: None)
    state = {"n": 0}

    def query(cred, params):
        state["n"] += 1
        if state["n"] < 3:
            raise youtube_analytics.YouTubeAnalyticsError("YouTube Analytics API lỗi (503): tạm")
        return {"columnHeaders": [], "rows": []}

    assert M.call_query(query, "cred", {"ids": "channel==MINE"}, pauses=(0, 0))["rows"] == []
    assert state["n"] == 3

    def bad(cred, params):
        raise youtube_analytics.YouTubeAnalyticsError("YouTube Analytics API lỗi (400): sai")

    with pytest.raises(youtube_analytics.YouTubeAnalyticsError):
        M.call_query(bad, "cred", {}, pauses=(0, 0))


def test_corrupt_ledger_is_not_overwritten(tmp_path):
    path = tmp_path / "retention_ledger.json"
    path.write_text("{", encoding="utf-8")
    uploaded = {"L_fs_01": "a"}
    videos = {"a": _video("a")}
    query, catalog, _ = _world(
        videos,
        {"a": _curve([(0.5, 0.2)])},
        {"a": _metrics(1, 1, 1)},
        {"a": _sources([("RELATED_VIDEO", 1)])},
    )
    with pytest.raises(RuntimeError):
        M.collect("fs", now=NOW, uploaded=uploaded, query=query, catalog=catalog, ledger_path=path, pauses=(0, 0))
    assert path.read_text(encoding="utf-8") == "{"


def test_fake_run_does_not_open_sockets_or_touch_real_ledger(tmp_path, monkeypatch):
    def blocked(*_a, **_k):
        raise AssertionError("đã gọi mạng")

    monkeypatch.setattr(socket, "create_connection", blocked)
    before = M.LEDGER.read_bytes() if M.LEDGER.exists() else None
    uploaded = {"L_fs_01": "a", "L_bud_09": "b"}
    videos = {"a": _video("a", title="Tuổi Tý 2027")}
    _run(
        tmp_path, uploaded, videos,
        curves={"a": _curve([(0.25, 0.3), (0.5, 0.1)])},
        metrics={"a": _metrics(3, 90, 12.2)},
        sources={"a": _sources([("RELATED_VIDEO", 1), ("SUBSCRIBER", 2)])},
    )
    after = M.LEDGER.read_bytes() if M.LEDGER.exists() else None
    assert before == after


def test_cli_json_uses_injected_query(tmp_path, monkeypatch, capsys):
    cred = tmp_path / "phong_thuy.json"
    cred.write_text("{}", encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    monkeypatch.setattr(M, "credentials_for", lambda channel: cred)
    monkeypatch.setattr(M, "LEDGER", ledger)
    videos = {"a": _video("a", title="Tuổi Tý")}

    def query(cred_path, params):
        assert "hinh_su" not in str(cred_path)
        if params.get("dimensions") == "elapsedVideoTimeRatio":
            return _curve([(0.25, 0.4), (0.5, 0.2)])
        if params.get("dimensions") == "insightTrafficSourceType":
            return _sources([("RELATED_VIDEO", 2), ("YT_SEARCH", 2)])
        return _metrics(9, 120, 15)

    def catalog(cred_path, url, params):
        return {"items": [videos["a"]]}

    class Frozen(M.datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr(M, "datetime", Frozen)
    monkeypatch.setattr(M, "default_query", query)
    monkeypatch.setattr(M, "default_catalog", catalog)
    monkeypatch.setattr(M, "UPLOADED", tmp_path / "uploaded.json")
    (tmp_path / "uploaded.json").write_text(json.dumps({"L_fs_01": "a"}), encoding="utf-8")
    assert M.main(["fs", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["channel"] == "fs"
    assert payload["rows"][0]["rid"] == "L_fs_01"
    assert payload["rows"][0]["suggested_pct"] == 50.0
    saved = json.loads(ledger.read_text(encoding="utf-8"))
    assert saved["snapshots"][0]["rows"][0]["video_id"] == "a"


def test_safe_err_redacts_token_shapes():
    text = M.safe_err('lỗi access_token=ya29.secret và Bearer abc.def\nchưa xong')
    assert "ya29" not in text
    assert "abc.def" not in text
    assert "access_token=…" in text
