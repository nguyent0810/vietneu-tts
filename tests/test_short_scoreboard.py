"""Bảng điểm short: ngưỡng, 48 giờ, kill-switch, lane=? . Không gọi mạng."""
import importlib.util
import json
import socket
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "output" / "cl_staging" / "scoreboard" / "short_scoreboard.py"
import pytest as _pt  # noqa: E402
if not (Path(__file__).resolve().parents[1] / "output/cl_staging/scoreboard/short_scoreboard.py").exists():   # công cụ ở output/ (gitignore): CI không có
    _pt.skip("output/cl_staging/scoreboard/short_scoreboard.py chỉ có trên máy dựng", allow_module_level=True)
spec = importlib.util.spec_from_file_location("short_scoreboard", MODULE)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

NOW = datetime(2026, 10, 22, 0, 0, tzinfo=timezone.utc)
SINCE = datetime(2026, 10, 7, tzinfo=timezone.utc).date()


def test_grade_thresholds():
    cases = [
        ("fs", 799, "THUA"),
        ("fs", 800, "GIỮA"),
        ("fs", 999, "GIỮA"),
        ("fs", 1000, "ĐẠT"),
        ("fs", 1999, "ĐẠT"),
        ("fs", 2000, "THẮNG"),
        ("fs", 5000, "THẮNG"),
        ("bud", 719, "THUA"),
        ("bud", 720, "GIỮA"),
        ("bud", 899, "GIỮA"),
        ("bud", 900, "ĐẠT"),
        ("bud", 1799, "ĐẠT"),
        ("bud", 1800, "THẮNG"),
    ]
    for channel, views, expected in cases:
        assert M.grade(channel, views, eligible=True) == expected
    assert M.thresholds("fs")["thang"] == 2000
    assert M.thresholds("bud")["thang"] == 1800


def test_under_48h_is_not_graded():
    assert M.grade("fs", 100000, eligible=False) is None
    assert M.grade("bud", 1, eligible=False) is None
    assert M.grade("fs", None, eligible=True) is None


def _row(rid, published, grade, lane="tuoi"):
    return {"id": rid, "published_at": published, "grade": grade, "lane": lane, "eligible": grade is not None}


def test_kill_switch_three_consecutive_by_publish_time():
    scrambled = [
        _row("c", "2026-10-20T00:00:00Z", "THUA"),
        _row("a", "2026-10-18T00:00:00Z", "THUA"),
        _row("b", "2026-10-19T00:00:00Z", "THUA"),
    ]
    info = M.kill_info(scrambled)
    assert info["kill_switch"] is True
    assert info["kill_tail"] is True
    assert info["kill_runs"] == [["a", "b", "c"]]

    broken = [
        _row("a", "2026-10-18T00:00:00Z", "THUA"),
        _row("b", "2026-10-19T00:00:00Z", "ĐẠT"),
        _row("c", "2026-10-20T00:00:00Z", "THUA"),
        _row("d", "2026-10-21T00:00:00Z", "THUA"),
    ]
    assert M.kill_info(broken)["kill_switch"] is False

    only_two = [
        _row("a", "2026-10-18T00:00:00Z", "THUA"),
        _row("b", "2026-10-19T00:00:00Z", "THUA"),
    ]
    assert M.kill_info(only_two)["kill_switch"] is False

    young_is_not_a_loss = [
        _row("a", "2026-10-18T00:00:00Z", "THUA"),
        _row("b", "2026-10-19T00:00:00Z", "THUA"),
        _row("c", "2026-10-21T12:00:00Z", None),
    ]
    assert M.kill_info(young_is_not_a_loss)["kill_switch"] is False

    other_lane = scrambled + [_row("x", "2026-10-18T00:00:00Z", "THUA", lane="khac")]
    lanes = {row["lane"]: M.kill_info([item for item in other_lane if item["lane"] == row["lane"]]) for row in other_lane}
    assert lanes["khac"]["kill_switch"] is False
    assert lanes["tuoi"]["kill_switch"] is True


def test_lane_unknown_without_plan_field():
    assert M.lane_of(None) == "?"
    assert M.lane_of({"title": "1984, 1985: mệnh Kim"}) == "?"
    assert M.lane_of({"lane": "  ", "title": "nạp âm"}) == "?"
    assert M.lane_of({"lane": "napam", "title": "ba tuổi hợp nhất"}) == "napam"


def _video(video_id, title, published, views, duration="PT24S", privacy="public"):
    return {
        "id": video_id,
        "snippet": {"title": title, "publishedAt": published},
        "status": {"privacyStatus": privacy},
        "statistics": {"viewCount": str(views)},
        "contentDetails": {"duration": duration},
    }


def _world(videos, metrics):
    calls = []

    def query(cred, params):
        calls.append(("query", str(cred), dict(params)))
        assert "hinh_su" not in str(cred)
        if params.get("dimensions") == "day":
            return {"columnHeaders": [{"name": "day"}, {"name": "views"}], "rows": [["2026-10-21", 10]]}
        rows = []
        for video_id in params["filters"].split("video==", 1)[1].split(","):
            if video_id in metrics:
                item = metrics[video_id]
                rows.append([
                    video_id,
                    item["views"],
                    item["engagedViews"],
                    item["averageViewPercentage"],
                    item["subscribersGained"],
                    item["likes"],
                ])
        return {
            "columnHeaders": [
                {"name": "video"},
                {"name": "views"},
                {"name": "engagedViews"},
                {"name": "averageViewPercentage"},
                {"name": "subscribersGained"},
                {"name": "likes"},
            ],
            "rows": rows,
        }

    def catalog(cred, url, params):
        calls.append(("catalog", str(cred), url, dict(params)))
        assert "playlist" not in url
        assert params["part"] == "snippet,statistics,contentDetails,status"
        found = []
        for video_id in params["id"].split(","):
            if video_id in videos:
                found.append(videos[video_id])
        return {"items": found}

    return query, catalog, calls


def _run():
    videos = {
        "win": _video("win", "Năm 2027 ba tuổi", "2026-10-18T00:00:00Z", 2500),
        "dat": _video("dat", "Bảng hạn", "2026-10-19T00:00:00Z", 1000),
        "mid": _video("mid", "Giữa ngưỡng", "2026-10-19T03:00:00Z", 800),
        "l1": _video("l1", "thua 1", "2026-10-18T01:00:00Z", 100),
        "l2": _video("l2", "thua 2", "2026-10-19T01:00:00Z", 100),
        "l3": _video("l3", "thua 3", "2026-10-20T00:00:00Z", 100),
        "young": _video("young", "mới đăng", "2026-10-21T12:00:00Z", 10),
        "ghost": _video("ghost", "1984, 1985: mệnh Kim", "2026-10-18T02:00:00Z", 5000),
        "nolane": _video("nolane", "có plan nhưng không có làn", "2026-10-18T04:00:00Z", 500),
        "edge": _video("edge", "đúng mốc ngày VN", "2026-10-06T17:00:00Z", 100),
        "before": _video("before", "trước since", "2026-10-06T16:00:00Z", 99999),
        "old": _video("old", "quá cũ", "2026-10-01T00:00:00Z", 99999),
        "priv": _video("priv", "hẹn giờ", "2026-10-20T00:00:00Z", 1, privacy="private"),
        "long": _video("long", "bản dài", "2026-10-18T05:00:00Z", 50, duration="PT10M"),
        "miss_an": _video("miss_an", "chưa có analytics", "2026-10-18T06:00:00Z", 1000),
    }
    metrics = {
        "win": {"views": 2400, "engagedViews": 1000, "averageViewPercentage": 80, "subscribersGained": 5, "likes": 10},
        "dat": {"views": 900, "engagedViews": 400, "averageViewPercentage": 70, "subscribersGained": 1, "likes": 2},
        "mid": {"views": 700, "engagedViews": 200, "averageViewPercentage": 60, "subscribersGained": 0, "likes": 1},
        "l1": {"views": 80, "engagedViews": 20, "averageViewPercentage": 40, "subscribersGained": 0, "likes": 0},
        "l2": {"views": 80, "engagedViews": 20, "averageViewPercentage": 40, "subscribersGained": 0, "likes": 0},
        "l3": {"views": 80, "engagedViews": 20, "averageViewPercentage": 40, "subscribersGained": 0, "likes": 0},
        "young": {"views": 5, "engagedViews": 1, "averageViewPercentage": 10, "subscribersGained": 0, "likes": 0},
        "ghost": {"views": 4000, "engagedViews": 2000, "averageViewPercentage": 90, "subscribersGained": 8, "likes": 4},
        "nolane": {"views": 400, "engagedViews": 100, "averageViewPercentage": 55, "subscribersGained": 0, "likes": 0},
        "edge": {"views": 90, "engagedViews": 30, "averageViewPercentage": 50, "subscribersGained": 0, "likes": 0},
        "miss_an": {"views": 1, "engagedViews": None, "averageViewPercentage": 1, "subscribersGained": 0, "likes": 0},
    }
    # miss_an cố tình không có hàng Analytics.
    metrics.pop("miss_an")
    plans = {
        "f_win": {"id": "f_win", "lane": "tuoi", "slot": "15:00", "test_cell": "F3", "title": "Năm 2027 ba tuổi"},
        "f_dat": {"id": "f_dat", "lane": "tuoi", "day": "2026-10-19"},
        "f_mid": {"id": "f_mid", "lane": "tuoi", "day": "2026-10-19"},
        "f_l1": {"id": "f_l1", "lane": "napam", "day": "2026-10-18"},
        "f_l2": {"id": "f_l2", "lane": "napam", "day": "2026-10-19"},
        "f_l3": {"id": "f_l3", "lane": "napam", "day": "2026-10-20"},
        "f_young": {"id": "f_young", "lane": "napam", "day": "2026-10-21"},
        "f_nolane": {"id": "f_nolane", "title": "1984, 1985: mệnh Kim", "day": "2026-10-18"},
        "f_an": {"id": "f_an", "lane": "tuoi", "day": "2026-10-18"},
        "f_edge": {"id": "f_edge", "lane": "lich", "day": "2026-10-07"},
        "f_before": {"id": "f_before", "lane": "lich", "day": "2026-10-06"},
        "f_old": {"id": "f_old", "lane": "tuoi", "day": "2026-10-01"},
        "f_priv": {"id": "f_priv", "lane": "tuoi", "day": "2026-10-20"},
        "f_long": {"id": "f_long", "lane": "tuoi", "day": "2026-10-18"},
        "f_miss": {"id": "f_miss", "lane": "tuoi", "day": "2026-10-18"},
    }
    uploaded = {
        "f_win": "win",
        "f_dat": "dat",
        "f_mid": "mid",
        "f_l1": "l1",
        "f_l2": "l2",
        "f_l3": "l3",
        "f_young": "young",
        "ghost": "ghost",
        "f_nolane": "nolane",
        "f_an": "miss_an",
        "f_edge": "edge",
        "f_before": "before",
        "f_old": "old",
        "f_priv": "priv",
        "f_long": "long",
        "f_miss": "missing-id",
    }
    query, catalog, calls = _world(videos, metrics)
    result = M.collect(
        ["fs"],
        SINCE,
        now=NOW,
        query=query,
        catalog=catalog,
        uploaded={"fs": uploaded},
        plans={"fs": plans},
        pauses=(0, 0),
    )
    return result, calls


def test_collect_groups_kill_switch_and_unknown_lane(tmp_path):
    result, calls = _run()
    block = result["channels"]["fs"]
    by_id = {video["id"]: video for video in block["videos"]}
    assert "f_before" not in by_id
    assert "f_old" not in by_id
    assert by_id["f_edge"]["published_vn"] == "2026-10-07 00:00"
    assert by_id["f_win"]["grade"] == "THẮNG"
    assert by_id["f_win"]["lane"] == "tuoi"
    assert by_id["f_win"]["test_cell"] == "F3"
    assert by_id["f_win"]["publish_hour"] == "07:00"
    assert by_id["f_win"]["slot"] == "15:00"
    assert by_id["f_win"]["views"] == 2500
    assert by_id["f_win"]["analytics_views"] == 2400
    assert by_id["f_win"]["engagedViews"] == 1000
    assert by_id["f_win"]["stay"] == round(1000 / 2400, 6)
    assert by_id["f_win"]["stay_data"] == 0.4
    assert by_id["f_dat"]["grade"] == "ĐẠT"
    assert by_id["f_mid"]["grade"] == "GIỮA"
    assert by_id["f_young"]["grade"] is None
    assert by_id["f_young"]["eligible"] is False
    assert by_id["ghost"]["lane"] == "?"
    assert "nạp" not in by_id["ghost"]["lane"]
    assert by_id["ghost"]["title"].startswith("1984")
    assert by_id["f_nolane"]["lane"] == "?"
    assert "f_miss" not in by_id
    assert "f_before" not in by_id
    assert by_id["f_edge"]["lane"] == "lich"
    assert by_id["f_win"]["likes"] == 10
    assert by_id["f_win"]["subscribersGained"] == 5
    assert by_id["f_win"]["averageViewPercentage"] == 80.0 or by_id["f_win"]["averageViewPercentage"] == 80
    assert by_id["f_dat"]["stay"] == round(400 / 900, 6)
    assert by_id["f_dat"]["stay_data"] == round(400 / 1000, 6)
    assert by_id["f_an"]["engagedViews"] is None
    assert by_id["f_an"]["stay"] is None
    assert by_id["f_an"]["grade"] == "ĐẠT"

    lanes = {lane["lane"]: lane for lane in block["lanes"]}
    assert lanes["napam"]["n"] == 3
    assert lanes["napam"]["under_48h"] == 1
    assert lanes["napam"]["kill_switch"] is True
    assert lanes["napam"]["kill_runs"] == [["f_l1", "f_l2", "f_l3"]]
    assert lanes["napam"]["pct_dat"] == 0
    assert lanes["tuoi"]["n"] == 4  # win, dat, mid, miss_an
    assert lanes["tuoi"]["grades"]["THẮNG"] == 1
    assert lanes["tuoi"]["grades"]["ĐẠT"] == 2
    assert lanes["tuoi"]["grades"]["GIỮA"] == 1
    assert "?" in lanes
    assert lanes["?"]["n"] == 2  # ghost THẮNG, nolane THUA
    assert all(video["id"] != "f_young" or video["grade"] is None for video in block["videos"])
    skipped = {item["id"]: item["reason"] for item in block["skipped"]}
    assert skipped["f_priv"].startswith("chưa công khai")
    assert skipped["f_long"].startswith("dài hơn 180")
    assert skipped["f_miss"] == "không thấy trên YouTube"
    assert "f_old" not in skipped
    text = M.render_markdown(result)
    assert "| Làn | n | trung vị view | trung vị stay | trung vị AVP | sub/1.000 view | % đạt nền | kill-switch | chưa đủ 48 giờ |" in text
    assert "| napam | 3 |" in text
    napam_line = next(line for line in text.splitlines() if line.startswith("| napam |"))
    assert "| có, đang cuối |" in napam_line
    assert napam_line.endswith("| 1 |")
    assert "f_l1, f_l2, f_l3" in text
    line = M.summary_line("fs", block, result["measured_on"], result["since"])
    assert line.startswith("TỔNG fs:")
    assert "kill-switch: napam" in line
    assert "chưa " in line
    creds = {call[1] for call in calls}
    assert creds == {str(M.credentials_for("fs"))}
    assert all(call[0] != "catalog" or call[2].endswith("/videos") for call in calls)
    json_path, md_path = M.write_scoreboard(result, tmp_path)
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    saved_video = saved["channels"]["fs"]["videos"][0]
    assert saved_video["views"] == by_id[saved_video["id"]]["views"]
    assert "chưa đủ 48 giờ" in md_path.read_text(encoding="utf-8")
    assert json_path.parent == tmp_path


def test_engaged_views_rejected_stays_null(monkeypatch):
    import youtube_analytics

    def query(cred, params):
        if params.get("dimensions") == "day":
            return {"columnHeaders": [{"name": "day"}, {"name": "views"}], "rows": [["2026-10-21", 3]]}
        if "engagedViews" in params.get("metrics", ""):
            raise youtube_analytics.YouTubeAnalyticsError("YouTube Analytics API lỗi (400): engagedViews")
        return {
            "columnHeaders": [
                {"name": "video"}, {"name": "views"}, {"name": "averageViewPercentage"},
                {"name": "subscribersGained"}, {"name": "likes"},
            ],
            "rows": [["vid", 10, 50, 1, 2]],
        }

    def catalog(cred, url, params):
        return {"items": [_video("vid", "1984, 1985: mệnh", "2026-10-10T00:00:00Z", 1000)]}

    result = M.collect(
        ["bud"],
        SINCE,
        now=NOW,
        query=query,
        catalog=catalog,
        uploaded={"bud": {"only": "vid"}},
        plans={"bud": {}},
        pauses=(0, 0),
    )
    video = result["channels"]["bud"]["videos"][0]
    assert video["lane"] == "?"
    assert video["views"] == 1000
    assert video["grade"] == "ĐẠT"
    assert video["engagedViews"] is None
    assert video["stay"] is None
    assert video["analytics_views"] == 10
    assert result["channels"]["bud"]["engaged_views_available"] is False


def test_fake_run_does_not_open_sockets(monkeypatch):
    def blocked(*_args, **_kwargs):
        raise AssertionError("đã gọi mạng")

    monkeypatch.setattr(socket, "create_connection", blocked)
    result, _calls = _run()
    assert result["channels"]["fs"]["totals"]["n"] > 0


def test_credentials_only_fs_and_bud():
    assert M.credentials_for("fs").name == "phong_thuy.json"
    assert M.credentials_for("bud").name == "phat_giao.json"
    with pytest.raises(ValueError):
        M.credentials_for("hinh_su")
    assert "hinh_su" not in str(M.credentials_for("fs"))
    assert "hinh_su" not in str(M.credentials_for("bud"))
