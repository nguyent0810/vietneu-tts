"""Báo cáo short tuần/tháng cho kênh Phật Giáo (bud) + Phong Thủy (fs): view, % xem hết, đăng ký, so bài
của pipeline HyperFrames với bài nguồn ngoài, theo lane/style/độ dài, và đường giữ chân của bài tốt/kém.

    python hf_shorts_report.py 2026-09-27 2026-10-03            # bảng tóm tắt
    python hf_shorts_report.py 2026-09-27 2026-10-03 --curves   # + đường giữ chân 5 bài đầu/cuối của pipeline
    python hf_shorts_report.py ... --json out.json

Chỉ đọc (Analytics + videos.list, vài đơn vị quota). Short = video <= 180 giây.
Kết luận đợt 04/10/2026 nằm trong hf_batch_render.short_v2_issues (công thức short v2).
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from youtube_analytics import _query  # noqa: E402
from youtube_catalog import VIDEOS_URL, _get  # noqa: E402

CHANNELS = {"bud": ".youtube_channels/phat_giao.json", "fs": ".youtube_channels/phong_thuy.json"}
METRICS = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,shares,comments,subscribersGained"


def _secs(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)M)?(?:(\d+)S)?", iso)
    return int(m[1] or 0) * 60 + int(m[2] or 0) if m else 0


def collect(ch: str, start: str, end: str) -> list[dict]:
    cred = str(ROOT / CHANNELS[ch])
    ledger = json.loads((ROOT / f"output/cl_staging/{ch}/uploaded.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for f in glob.glob(str(ROOT / f"output/cl_staging/{ch}/plan_*.json")) for r in json.load(open(f))}
    rid_of = {v: k for k, v in ledger.items()}
    rep = _query(cred, {"ids": "channel==MINE", "startDate": start, "endDate": end, "dimensions": "video",
                        "metrics": METRICS, "sort": "-views", "maxResults": 200})
    hdr = [h["name"] for h in rep["columnHeaders"]]
    stats = {r[0]: dict(zip(hdr, r)) for r in rep.get("rows", [])}
    ids, meta = list(stats), {}
    for i in range(0, len(ids), 50):
        for v in _get(cred, VIDEOS_URL, {"part": "snippet,contentDetails", "id": ",".join(ids[i:i + 50])})["items"]:
            meta[v["id"]] = {"title": v["snippet"]["title"], "pub": v["snippet"]["publishedAt"][:16],
                             "dur": _secs(v["contentDetails"]["duration"])}
    out = []
    for vid, a in stats.items():
        rid = rid_of.get(vid)
        r = rows.get(rid, {})
        out.append({**a, **meta.get(vid, {"dur": 999}), "rid": rid, "ours": bool(rid), "style": r.get("style"), "lane": r.get("lane")})
    return [v for v in out if v["dur"] <= 180]


def curve(ch: str, vid: str, start: str, end: str) -> list[float]:
    rep = _query(str(ROOT / CHANNELS[ch]), {"ids": "channel==MINE", "startDate": start, "endDate": end,
                                            "dimensions": "elapsedVideoTimeRatio", "metrics": "audienceWatchRatio",
                                            "filters": f"video=={vid}"})
    pts = {round(x[0], 2): x[1] for x in rep.get("rows", [])}
    return [pts.get(k, 0.0) for k in (0.01, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0)]


def line(label: str, g: list[dict]) -> str:
    v = sum(x["views"] for x in g) or 1
    return (f"  {label:24} n={len(g):3}  view trung vị {st.median(x['views'] for x in g):6.0f}  "
            f"xem hết trung vị {st.median(x['averageViewPercentage'] for x in g):4.0f}%  "
            f"đăng ký/1k {1000 * sum(x['subscribersGained'] for x in g) / v:4.1f}  like/1k {1000 * sum(x['likes'] for x in g) / v:4.1f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("start"); ap.add_argument("end")
    ap.add_argument("--curves", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    dump = {}
    for ch in CHANNELS:
        sh = collect(ch, a.start, a.end)
        dump[ch] = sh
        ours = [x for x in sh if x["ours"]]
        print(f"===== {ch}: {len(sh)} short có view")
        for lab, g in (("pipeline HyperFrames", ours), ("nguồn ngoài", [x for x in sh if not x["ours"]])):
            if g:
                print(line(lab, g))
        for key in ("lane", "style"):
            for k in sorted({x[key] for x in ours if x[key]}):
                g = [x for x in ours if x[key] == k]
                if len(g) >= 3:
                    print(line(f"{key} {k}", g))
        for lo, hi in ((0, 20), (20, 27), (27, 32), (32, 181)):
            g = [x for x in sh if lo <= x["dur"] < hi]
            if len(g) >= 3:
                print(line(f"dài {lo}-{hi - 1}s", g))
        if a.curves and ours:
            ranked = sorted(ours, key=lambda x: -x["averageViewPercentage"])
            print("  đường giữ chân (1% 10% 20% 30% 50% 70% 100%):")
            for x in ranked[:5] + ranked[-5:]:
                c = curve(ch, x["video"], a.start, a.end)
                print(f"   {x['rid']:7} {x['averageViewPercentage']:4.0f}% " + " ".join(f"{p:.2f}" for p in c) + f"  {x['title'][:40]}")
    if a.json:
        Path(a.json).write_text(json.dumps(dump, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
