from hf_short_retention import analyze_video, normalize_curve, steepest_drop


def test_normalize_sorts_and_converts_api_rows():
    assert normalize_curve([[0.5, 0.4], [0.1, 0.8]]) == [
        {"elapsed": 0.1, "audience": 0.8}, {"elapsed": 0.5, "audience": 0.4}]


def test_steepest_drop_returns_largest_adjacent_drop():
    curve = normalize_curve([[0.0, 1.0], [0.2, 0.9], [0.5, 0.4]])
    assert steepest_drop(curve) == {"from": 0.2, "to": 0.5, "drop": 0.5,
                                   "drop_percentage_points": 50.0}


def test_analyze_video_queries_retention_dimensions():
    seen = {}
    def query(credentials, params):
        seen.update(params)
        return {"rows": [[0.0, 1.0], [1.0, 0.2]]}
    result = analyze_video(query, "creds", "video", "2026-10-01", "2026-10-03")
    assert result["steepest_drop"]["drop_percentage_points"] == 80.0
    assert seen["dimensions"] == "elapsedVideoTimeRatio"
    assert seen["metrics"] == "audienceWatchRatio"
