"""Kéo số liệu YouTube Analytics API cho 3 kênh (issue #183). CHỈ ĐỌC.

    python <đường dẫn>/analytics_pull_183.py [--channel MIM] [--end 2026-11-04]

Chạy từ thư mục creator_v2 có data/ (cwd quyết định nơi ghi):
    data/analytics/<KÊNH>/183/*.json  (gitignore)

Lấy: danh sách video (videos.list), theo video (28 ngày, 7 ngày, 365 ngày,
trọn đời), video x nguồn traffic (từng video, vì API không cho gộp hai chiều
video + insightTrafficSourceType), video x ngày quanh giờ đăng, kênh x ngày,
kênh x creatorContentType x nguồn. Thử các metric impressions / shown in feed
và ghi lại API từ chối hay không (probe.json). Không suy ngược metric thiếu.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factory import channels  # noqa: E402
from factory.analytics import ANALYTICS, HttpAnalytics, ReportRejected  # noqa: E402

BASE = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained"
PLAYLIST = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEOS = "https://www.googleapis.com/youtube/v3/videos"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"


def rows_of(d: dict) -> list[dict]:
    names = [h["name"] for h in d.get("columnHeaders", [])]
    return [dict(zip(names, r)) for r in d.get("rows") or []]


class Puller:
    def __init__(self, ch: str, out: Path):
        self.ch, self.out = ch, out
        self.a = HttpAnalytics.open(ch)
        self.http = self.a._http
        out.mkdir(parents=True, exist_ok=True)

    def q(self, **p) -> list[dict]:
        p.setdefault("ids", "channel==MINE")
        d = self.http.get_json(ANALYTICS + "?" + urllib.parse.urlencode(p))
        return rows_of(d)

    def q_all(self, **p) -> list[dict]:
        """Đi hết trang (startIndex)."""
        out, idx, size = [], 1, 200
        while True:
            got = self.q(maxResults=size, startIndex=idx, **p)
            out += got
            if len(got) < size:
                return out
            idx += len(got)

    def q_videos(self, ids: list[str], **p) -> list[dict]:
        """Báo cáo dimensions=video theo lô id. API không cho lật trang (startIndex) báo cáo top video
        quá 200 dòng (HTTP 400 "query is not supported", CL 651 video, 06/11) -> lọc video==id1,id2,... từng lô."""
        out = []
        for i in range(0, len(ids), 150):
            out += self.q(filters="video==" + ",".join(ids[i:i + 150]), maxResults=200, **p)
        return out

    def try_q(self, **p):
        try:
            return {"ok": True, "rows": self.q(**p)}
        except ReportRejected as e:
            return {"ok": False, "reason": "HTTP 400: " + str(e).split('"message":')[-1][:120].strip()}
        except Exception as e:  # lỗi tạm: ghi lý do, không làm hỏng cả lần chạy
            return {"ok": False, "reason": f"{type(e).__name__}: {str(e)[:120]}"}

    def save(self, name: str, obj):
        (self.out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── danh sách video ──
    def video_list(self) -> list[dict]:
        ch = self.http.get_json(CHANNELS_URL + "?" + urllib.parse.urlencode(
            {"part": "contentDetails,statistics,snippet", "mine": "true"}))["items"][0]
        up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
        self.save("channel.json", {"title": ch["snippet"]["title"], "statistics": ch["statistics"]})
        ids, tok = [], None
        while True:
            p = {"part": "contentDetails", "playlistId": up, "maxResults": 50}
            if tok:
                p["pageToken"] = tok
            d = self.http.get_json(PLAYLIST + "?" + urllib.parse.urlencode(p))
            ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
            tok = d.get("nextPageToken")
            if not tok:
                break
        vids = []
        for i in range(0, len(ids), 50):
            d = self.http.get_json(VIDEOS + "?" + urllib.parse.urlencode(
                {"part": "snippet,status,contentDetails,statistics", "id": ",".join(ids[i:i + 50])}))
            for it in d.get("items", []):
                sn, st = it["snippet"], it["status"]
                vids.append({"id": it["id"], "title": sn["title"], "published_at": sn["publishedAt"],
                             "publish_at": st.get("publishAt"), "privacy": st["privacyStatus"],
                             "duration": it["contentDetails"]["duration"],
                             "views_life": int(it.get("statistics", {}).get("viewCount", 0))})
        self.save("videos.json", vids)
        return vids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", action="append")
    ap.add_argument("--end", default=(date.today() - timedelta(days=1)).isoformat())
    ap.add_argument("--out", default="data/analytics")
    args = ap.parse_args()
    end = date.fromisoformat(args.end)
    W = {"d28": ("2026-10-07", "2026-11-03"),
         "d7": ((end - timedelta(days=6)).isoformat(), end.isoformat()),
         "d365": ((end - timedelta(days=364)).isoformat(), end.isoformat())}
    for ch in args.channel or ["MIM", "CK", "CL"]:
        P = Puller(ch, Path(args.out) / ch / "183")
        print(f"== {ch}", flush=True)
        vids = P.video_list()
        print(f"  {len(vids)} video", flush=True)
        probe = {}
        S = dict(startDate=W["d28"][0], endDate=W["d28"][1])
        for name, m in {"impressions": "views,videoThumbnailImpressions,videoThumbnailImpressionsClickRate",
                        "shownInFeed": "views,shownInFeed", "shortsFeed": "views,shortsFeedImpressions",
                        "engagedViews": "views,engagedViews"}.items():
            probe[name] = {k: v for k, v in P.try_q(metrics=m, dimensions="video", sort="-views", maxResults=2, **S).items()
                           if k != "rows"}
        probe["video_x_source"] = {k: v for k, v in P.try_q(
            metrics="views", dimensions="video,insightTrafficSourceType", sort="-views", maxResults=2, **S).items() if k != "rows"}
        probe["hour"] = {k: v for k, v in P.try_q(metrics="views", dimensions="hour", **S).items() if k != "rows"}
        P.save("probe.json", probe)
        # theo video, các cửa sổ
        for key, (s, e) in W.items():
            rows = P.q_videos([v["id"] for v in vids], startDate=s, endDate=e, metrics=BASE + ",engagedViews",
                              dimensions="video", sort="-views")
            P.save(f"byvideo_{key}.json", {"start": s, "end": e, "rows": rows})
            print(f"  {key}: {len(rows)} dòng video", flush=True)
        # kênh: tổng, theo ngày, theo loại nội dung, nguồn x loại
        chan = {}
        for key, (s, e) in W.items():
            chan[key] = {"total": P.try_q(startDate=s, endDate=e, metrics=BASE + ",subscribersLost,engagedViews"),
                         "by_type": P.try_q(startDate=s, endDate=e, metrics=BASE + ",engagedViews",
                                            dimensions="creatorContentType"),
                         "type_x_source": P.try_q(startDate=s, endDate=e, metrics="views,estimatedMinutesWatched,averageViewDuration",
                                                  dimensions="creatorContentType,insightTrafficSourceType"),
                         "by_day_type": P.try_q(startDate=s, endDate=e, metrics="views,estimatedMinutesWatched,subscribersGained",
                                                dimensions="day,creatorContentType", sort="day")}
        P.save("channel_windows.json", chan)
        # video x nguồn: mọi video có views trong 28 ngày hoặc trọn đời; Long và Short đều lấy (Short rẻ, ~1 s/video)
        d28 = {r["video"]: r for r in json.loads((P.out / "byvideo_d28.json").read_text(encoding="utf-8"))["rows"]}
        d365 = {r["video"]: r for r in json.loads((P.out / "byvideo_d365.json").read_text(encoding="utf-8"))["rows"]}
        want = [v for v in vids if v["privacy"] == "public" and (v["id"] in d28 or v["id"] in d365)]
        src, day = {}, {}
        for n, v in enumerate(want, 1):
            pub = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
            start = (pub - timedelta(days=1)).date()
            stop = min(end, (pub + timedelta(days=8)).date())
            src[v["id"]] = {
                "d28": P.try_q(startDate=W["d28"][0], endDate=W["d28"][1], dimensions="insightTrafficSourceType",
                               metrics="views,estimatedMinutesWatched,averageViewDuration", filters=f"video=={v['id']}"),
                "life": P.try_q(startDate=max(start, date(2025, 1, 1)).isoformat(), endDate=end.isoformat(),
                                dimensions="insightTrafficSourceType",
                                metrics="views,estimatedMinutesWatched,averageViewDuration", filters=f"video=={v['id']}")}
            if start <= stop:
                day[v["id"]] = P.try_q(startDate=start.isoformat(), endDate=stop.isoformat(), dimensions="day",
                                       metrics="views,estimatedMinutesWatched,subscribersGained", sort="day",
                                       filters=f"video=={v['id']}")
            if n % 25 == 0:
                print(f"  video x nguồn/ngày {n}/{len(want)}", flush=True)
        P.save("video_x_source.json", src)
        P.save("video_x_day.json", day)
        P.save("meta.json", {"fetched_at": datetime.now(timezone.utc).isoformat(), "windows": W, "end": end.isoformat()})
        print("  xong", flush=True)


if __name__ == "__main__":
    from factory.console import utf8_console  # noqa: E402
    utf8_console()
    main()
