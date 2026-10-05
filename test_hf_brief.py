"""hf_brief: xếp hạng midrank trong tuần, chỉ tuần đủ short, tách tuần sạch/tham khảo."""
import hf_brief as B


def test_midrank_ties_and_bounds():
    r = B.ranks([("a", 10), ("b", 20), ("c", 20), ("d", 30)])
    assert r["a"] == 0 and r["d"] == 1 and r["b"] == r["c"] == 0.5


def test_score_shorts_needs_full_week_and_marks_clean():
    m = {}
    for k in range(15):
        m[f"v{k}"] = {"dur": 25, "engagedViews": k, "views": k, "averageViewPercentage": 50, "day_pt": "2026-10-06",
                      "vn": "2026-10-06 23:20", "title": "t"}
    for k in range(5):   # tuần chỉ 5 short -> không xếp hạng
        m[f"w{k}"] = {"dur": 25, "engagedViews": k, "views": k, "averageViewPercentage": 50, "day_pt": "2026-09-29",
                      "vn": "2026-09-29 10:30", "title": "t"}
    m["long"] = {"dur": 1800, "engagedViews": 999, "views": 999, "averageViewPercentage": 30, "day_pt": "2026-10-06",
                 "vn": "2026-10-06 20:00", "title": "L"}
    rows, sizes = B.score_shorts(m, {})
    assert {x["vid"] for x in rows} == {f"v{k}" for k in range(15)}          # Long và tuần thiếu bị loại
    assert all(x["clean"] for x in rows) and sizes[B.week_of("2026-09-29")] == 5
    assert max(rows, key=lambda x: x["rank"])["vid"] == "v14"
