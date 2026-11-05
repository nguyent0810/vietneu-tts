"""Phân tích dữ liệu thô của analytics_pull_183.py (đọc data/analytics/<KÊNH>/183/). Chỉ đọc file.

    python <đường dẫn>/analytics_analyze_183.py [--channel CK] [--section tong|long|short|slot|all]

In bảng markdown ra stdout. Loại video: Short nếu thời lượng <= 180 giây
(ngưỡng Shorts hiện hành của YouTube); Long còn lại.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
D = Path("data/analytics")
VN = timezone(timedelta(hours=7))


def secs(iso):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    h, mi, s = (int(x or 0) for x in m.groups()) if m else (0, 0, 0)
    return h * 3600 + mi * 60 + s


def J(ch, name):
    p = D / ch / "183" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    f = int(k)
    return xs[f] + (xs[min(f + 1, len(xs) - 1)] - xs[f]) * (k - f)


def load(ch):
    vids = {v["id"]: v for v in J(ch, "videos.json")}
    for v in vids.values():
        v["sec"] = secs(v["duration"])
        v["kind"] = "S" if v["sec"] <= 180 else "L"
        v["pub"] = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
    return vids


def win(ch, key):
    return {r["video"]: r for r in J(ch, f"byvideo_{key}.json")["rows"]}


def tong(ch, vids):
    cw = J(ch, "channel_windows.json")
    print(f"\n### {ch} tổng theo kỳ")
    for k, label in (("d28", "28 ngày 07/10–03/11"), ("d7", "7 ngày"), ("d365", "365 ngày")):
        t = cw[k]["total"]
        bt = cw[k]["by_type"]
        print(f"- {label}: tổng {t['rows'][0] if t['ok'] and t['rows'] else t}")
        if bt["ok"]:
            for r in bt["rows"]:
                print(f"  - {r['creatorContentType']}: views {r['views']}, giờ xem {r['estimatedMinutesWatched']/60:.1f}, "
                      f"AVD {r['averageViewDuration']:.0f}s, sub +{r['subscribersGained']}")
    # giờ xem 365 ngày chỉ Long công khai (theo thời lượng) để đối chiếu Earn
    w = win(ch, "d365")
    L = sum(r["estimatedMinutesWatched"] for i, r in w.items() if i in vids and vids[i]["kind"] == "L")
    S = sum(r["estimatedMinutesWatched"] for i, r in w.items() if i in vids and vids[i]["kind"] == "S")
    print(f"- 365 ngày theo video (hiện còn trên kênh): Long {L/60:.1f} giờ, Short {S/60:.1f} giờ")


def fmt_avd(s):
    return f"{int(s)//60}:{int(s)%60:02d}"


def long_tab(ch, vids):
    w28, w365 = win(ch, "d28"), win(ch, "d365")
    src = J(ch, "video_x_source.json") or {}
    rows = []
    for i, v in vids.items():
        if v["kind"] != "L" or v["privacy"] != "public":
            continue
        r = w28.get(i, {})
        r365 = w365.get(i, {})
        s = {x["insightTrafficSourceType"]: x for x in (src.get(i, {}).get("d28", {}).get("rows") or [])}
        tot = sum(x["views"] for x in s.values()) or 1
        top = sorted(s.items(), key=lambda kv: -kv[1]["estimatedMinutesWatched"])[:3]
        rows.append((r.get("estimatedMinutesWatched", 0) / 60, i, v, r, r365, top, tot))
    rows.sort(key=lambda x: -x[0])
    print(f"\n### {ch} Long công khai ({len(rows)}), xếp theo giờ xem 28 ngày")
    print("| # | video | đăng (VN) | views28 | giờ28 | AVD | AVP% | sub | giờ365 | nguồn kéo giờ xem (giờ, % view) |")
    print("|--|--|--|--:|--:|--|--:|--:|--:|--|")
    for n, (h, i, v, r, r365, top, tot) in enumerate(rows, 1):
        ts = "; ".join(f"{k} {x['estimatedMinutesWatched']/60:.1f}h {x['views']/tot:.0%}" for k, x in top)
        print(f"| {n} | {v['title'][:60]} | {v['pub'].astimezone(VN):%d/%m %H:%M} | {r.get('views',0)} | {h:.1f} | "
              f"{fmt_avd(r.get('averageViewDuration',0))} | {r.get('averageViewPercentage',0):.0f} | "
              f"{r.get('subscribersGained',0)} | {r365.get('estimatedMinutesWatched',0)/60:.1f} | {ts} |")


def short_tab(ch, vids):
    w28 = win(ch, "d28")
    ss = [(i, v, w28.get(i)) for i, v in vids.items() if v["kind"] == "S" and v["privacy"] == "public"]
    ss28 = [(i, v, r) for i, v, r in ss if r]
    views = [r["views"] for _, _, r in ss28]
    print(f"\n### {ch} Short: {len(ss)} công khai, {len(ss28)} có view trong 28 ngày")
    if views:
        print(f"- views 28 ngày: median {st.median(views):.0f}, p25 {pct(views,.25):.0f}, p75 {pct(views,.75):.0f}, "
              f"max {max(views)}, tổng {sum(views)}, sub +{sum(r['subscribersGained'] for _,_,r in ss28)}")
        stay = [r["engagedViews"] / r["views"] for _, _, r in ss28 if r["views"] >= 100 and r.get("engagedViews") is not None]
        if stay:
            print(f"- engagedViews/views (video >=100 view, n={len(stay)}): median {st.median(stay):.1%}, "
                  f"p25 {pct(stay,.25):.1%}, p75 {pct(stay,.75):.1%}")
    top = sorted(ss28, key=lambda x: -x[2]["views"])[:10]
    print("| top Short | views | AVP% | ở lại | sub |\n|--|--:|--:|--:|--:|")
    for i, v, r in top:
        e = r.get("engagedViews")
        print(f"| {v['title'][:60]} | {r['views']} | {r['averageViewPercentage']:.0f} | "
              f"{(e/r['views']):.0%} | {r['subscribersGained']} |")
    sub = sorted([x for x in ss28 if x[2]["subscribersGained"] > 0], key=lambda x: -x[2]["subscribersGained"])[:8]
    print("| top sub | sub | views |\n|--|--:|--:|")
    for i, v, r in sub:
        print(f"| {v['title'][:60]} | {r['subscribersGained']} | {r['views']} |")
    # theo tuần đăng
    wk = {}
    for i, v, r in ss:
        k = v["pub"].astimezone(VN).date()
        wk.setdefault(k, []).append(r["views"] if r else 0)
    return ss


def slots(ch, vids):
    day = J(ch, "video_x_day.json") or {}
    rows = []
    for i, d in day.items():
        v = vids.get(i)
        if not v or not d.get("ok") or v["pub"] < datetime(2026, 10, 1, tzinfo=timezone.utc) or v["pub"] > datetime(2026, 10, 31, tzinfo=timezone.utc):
            continue
        pt_day = (v["pub"] - timedelta(hours=7)).date()  # ngày Thái Bình Dương (PDT) của lúc đăng
        tot = 0
        for r in d["rows"]:
            dd = datetime.fromisoformat(r["day"]).date()
            if 0 <= (dd - pt_day).days <= 2:
                tot += r["views"]
        hv = v["pub"].astimezone(VN)
        rows.append((v["kind"], hv.hour, tot, hv))
    print(f"\n### {ch} slot giờ đăng (VN) theo views 3 ngày đầu (ngày PT 0–2), đăng 01–31/10")
    for kind in ("L", "S"):
        sel = [r for r in rows if r[0] == kind]
        if not sel:
            continue
        by = {}
        for _, h, t, _ in sel:
            by.setdefault(h, []).append(t)
        print(f"- {'Long' if kind=='L' else 'Short'} (n={len(sel)})")
        print("| giờ VN | n | median 3d | mean 3d |\n|--:|--:|--:|--:|")
        for h in sorted(by):
            print(f"| {h:02d}h | {len(by[h])} | {st.median(by[h]):.0f} | {st.mean(by[h]):.0f} |")
        # nhóm khung
        bands = {"00-05": range(0, 6), "06-10": range(6, 11), "11-13": range(11, 14), "14-17": range(14, 18), "18-20": range(18, 21), "21-23": range(21, 24)}
        print("| khung | n | median | mean |\n|--|--:|--:|--:|")
        for b, rg in bands.items():
            xs = [t for _, h, t, _ in sel if h in rg]
            if xs:
                print(f"| {b} | {len(xs)} | {st.median(xs):.0f} | {st.mean(xs):.0f} |")


def weekly(ch, vids):
    """Short theo tuần đăng (VN): median views trọn đời tới nay và views 7 ngày đầu (ngày PT 0–6)."""
    day = J(ch, "video_x_day.json") or {}
    wk = {}
    for i, d in day.items():
        v = vids.get(i)
        if not v or v["kind"] != "S" or not d.get("ok"):
            continue
        pt_day = (v["pub"] - timedelta(hours=7)).date()
        t = sum(r["views"] for r in d["rows"] if 0 <= (datetime.fromisoformat(r["day"]).date() - pt_day).days <= 6)
        d0 = v["pub"].astimezone(VN).date()
        mon = d0 - timedelta(days=d0.weekday())
        wk.setdefault(mon, []).append((t, v["views_life"], v["pub"] + timedelta(days=7) <= datetime.now(timezone.utc)))
    print(f"\n### {ch} Short theo tuần đăng (thứ Hai VN): views 7 ngày đầu và views trọn đời (tới nay)")
    print("| tuần | n | median 7d | p25 | p75 | median trọn đời | đủ 7 ngày tuổi |\n|--|--:|--:|--:|--:|--:|--:|")
    for k in sorted(wk):
        xs = [t for t, _, _ in wk[k]]
        lf = [l for _, l, _ in wk[k]]
        print(f"| {k:%d/%m} | {len(xs)} | {st.median(xs):.0f} | {pct(xs,.25):.0f} | {pct(xs,.75):.0f} | "
              f"{st.median(lf):.0f} | {sum(1 for _,_,o in wk[k] if o)}/{len(xs)} |")


if __name__ == "__main__":
    from factory.console import utf8_console  # noqa: E402
    utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", action="append")
    ap.add_argument("--section", default="all")
    a = ap.parse_args()
    for ch in a.channel or ["MIM", "CK", "CL"]:
        vids = load(ch)
        print(f"\n## {ch}")
        for name, fn in (("tong", tong), ("long", long_tab), ("short", short_tab), ("slot", slots), ("tuan", weekly)):
            if a.section in ("all", name):
                fn(ch, vids)
