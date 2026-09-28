"""Retention curve + traffic source (ticket 09): parse kết quả API theo từng
video, video thiếu dữ liệu ghi lý do, lỗi tạm thời được thử lại, lỗi vĩnh
viễn ghi lại và chạy tiếp. Giả lập hàm gọi API `youtube_get` như test sync."""
import json

import pytest

import baseline_analytics_fetch as baf
import youtube_sync as ys

RETENTION = {
    "columnHeaders": [{"name": "elapsedVideoTimeRatio"}, {"name": "audienceWatchRatio"},
                      {"name": "relativeRetentionPerformance"}],
    "rows": [[0.02, 0.91, 0.55], [0.01, 1.0, 0.6], [0.03, 0.8, None]],
}
TRAFFIC = {
    "columnHeaders": [{"name": "insightTrafficSourceType"}, {"name": "views"}, {"name": "estimatedMinutesWatched"}],
    "rows": [["SHORTS", 120, 30.5], ["SUBSCRIBER", 5, 1.0]],
}


def _fake_get(responses):
    """responses: {(video_id, dimension): [(status, payload), ...]} -- lần lượt."""
    calls = []

    def get(url, params, token):
        vid = params["filters"].split("==")[1]
        key = (vid, params["dimensions"])
        calls.append(key)
        status, payload = responses[key].pop(0)
        return status, payload, 1.0
    return get, calls


def test_parses_retention_curve_sorted_by_position(monkeypatch):
    get, _ = _fake_get({("v1", "elapsedVideoTimeRatio"): [(200, RETENTION)]})
    monkeypatch.setattr(ys, "youtube_get", get)
    points, status = ys.fetch_retention_curve("tok", "UC1", "v1", "2026-01-01", "2026-09-28")
    assert status == 200
    assert [p["elapsedVideoTimeRatio"] for p in points] == [0.01, 0.02, 0.03]
    assert points[0]["audienceWatchRatio"] == 1.0
    assert points[2]["relativeRetentionPerformance"] is None  # null giữ là thiếu, không thành 0


def test_parses_traffic_sources(monkeypatch):
    get, _ = _fake_get({("v1", "insightTrafficSourceType"): [(200, TRAFFIC)]})
    monkeypatch.setattr(ys, "youtube_get", get)
    sources, status = ys.fetch_traffic_sources("tok", "UC1", "v1", "2026-01-01", "2026-09-28")
    assert sources == {"SHORTS": {"views": 120, "estimatedMinutesWatched": 30.5},
                       "SUBSCRIBER": {"views": 5, "estimatedMinutesWatched": 1.0}}


def test_request_filters_by_video_and_logs_call_without_token(monkeypatch):
    seen = {}

    def get(url, params, token):
        seen.update(params)
        return 200, RETENTION, 1.0
    monkeypatch.setattr(ys, "youtube_get", get)
    stats = ys.SyncStats()
    ys.fetch_retention_curve("secret-token", "UC1", "v9", "2026-01-01", "2026-09-28", stats)
    assert seen["filters"] == "video==v9" and seen["ids"] == "channel==UC1"
    assert "secret-token" not in json.dumps(stats.api_calls)


def test_run_handles_ok_no_data_permanent_and_transient_per_video(monkeypatch):
    empty = {"columnHeaders": RETENTION["columnHeaders"], "rows": []}
    get, calls = _fake_get({
        ("ok", "elapsedVideoTimeRatio"): [(200, RETENTION)],
        ("ok", "insightTrafficSourceType"): [(200, TRAFFIC)],
        ("few_views", "elapsedVideoTimeRatio"): [(200, empty)],
        ("few_views", "insightTrafficSourceType"): [(200, {"rows": []})],
        ("gone", "elapsedVideoTimeRatio"): [(404, {})],
        ("gone", "insightTrafficSourceType"): [(400, {})],
        ("flaky", "elapsedVideoTimeRatio"): [(503, {}), (429, {}), (200, RETENTION)],
        ("flaky", "insightTrafficSourceType"): [(503, {}), (503, {}), (503, {})],
    })
    monkeypatch.setattr(ys, "youtube_get", get)
    sleeps = []
    rows = baf.fetch_for_videos(["ok", "few_views", "gone", "flaky"], token="t", channel_id="UC1",
                                start="2026-01-01", end="2026-09-28", sleep=sleeps.append)
    by_id = {r["youtube_video_id"]: r for r in rows}
    assert by_id["ok"]["retention_curve"]["status"] == "ok"
    assert by_id["ok"]["traffic_sources"]["data"]["SHORTS"]["views"] == 120
    assert by_id["few_views"]["retention_curve"] == {**by_id["few_views"]["retention_curve"],
                                                    "status": "missing", "reason": "no_data", "data": None}
    assert by_id["gone"]["retention_curve"]["reason"] == "permanent_http_404"
    assert len(by_id["gone"]["retention_curve"]["attempts"]) == 1, "lỗi vĩnh viễn không thử lại"
    assert by_id["flaky"]["retention_curve"]["status"] == "ok"
    assert len(by_id["flaky"]["retention_curve"]["attempts"]) == 3
    assert by_id["flaky"]["traffic_sources"]["status"] == "transient_failed"
    assert by_id["flaky"]["traffic_sources"]["reason"] == "transient_http_503"
    assert len(sleeps) == 4


def test_network_error_is_treated_as_transient(monkeypatch):
    def boom(*a, **k):
        raise ys.SyncError("mất mạng")
    monkeypatch.setattr(ys, "youtube_get", boom)
    rows = baf.fetch_for_videos(["v1"], token="t", channel_id="UC1", start="a", end="b", sleep=lambda s: None)
    assert rows[0]["retention_curve"]["status"] == "transient_failed"
    assert rows[0]["retention_curve"]["reason"] == "transient_network_error"


def test_output_has_version_timestamp_and_summary():
    rows = [{"youtube_video_id": "v", "retention_curve": {"status": "ok"}, "traffic_sources": {"status": "missing"}}]
    out = baf.build_output(rows, channel_label="phong_thuy", channel_id="UC1", start="a", end="b")
    assert out["output_version"] == baf.OUTPUT_VERSION and out["fetched_at"]
    assert out["summary"]["retention_curve"]["ok"] == 1 and out["summary"]["traffic_sources"]["missing"] == 1


@pytest.mark.parametrize("content,expected", [
    ("v1\nv2\n# comment\nv1\n", ["v1", "v2"]),
    (json.dumps(["a", "b"]), ["a", "b"]),
    (json.dumps({"items": [{"youtube_video_id": "x"}, {"youtube_video_id": None}, {"youtube_video_id": "y"}]}), ["x", "y"]),
])
def test_reads_video_ids_from_text_list_or_ledger(tmp_path, content, expected):
    p = tmp_path / "ids"
    p.write_text(content, encoding="utf-8")
    assert baf.read_video_ids(p) == expected


def test_default_output_dir_is_gitignored_baseline():
    assert baf.DEFAULT_OUT_DIR.parts[-2:] == ("baseline", "raw")
