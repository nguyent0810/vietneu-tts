"""Bản tóm tắt hằng tuần cho kênh Phật giáo (bud) + Phong Thuỷ (fs): số liệu của chính kênh + nhu cầu bên ngoài,
để chọn chủ đề/góc kể cho Long và Short từ dữ liệu thay vì chọn tay.

Ý từ vòng phản hồi analytics của Youtube_Creator_V2 (factory/scoreboard.py, 05/10/2026), rút gọn cho repo này:
  ĐO   : mỗi video một cửa sổ 7 NGÀY PT tính từ ngày lên sóng (Analytics tính ngày theo giờ Thái Bình Dương; 7 chứ không
         3 vì "3 ngày PT" dài 51-71 giờ tuỳ giờ đăng). Chỉ đo khi Analytics đã có số của ngày cuối (trễ ~3 ngày).
         Kết quả đã đóng không đổi -> cache chunks_cache/brief/metrics_<kênh>.json.
  SO   : Short xếp hạng engagedViews TRONG CÙNG TUẦN (tuần ISO theo ngày PT), cùng kênh, chỉ tuần >= 15 short; hạng
         midrank 0..1. Tuần từ 05/10/2026 là "sạch"; tuần trước (dính cập nhật Shorts "original" 01/10) chỉ để THAM KHẢO.
         Long (2 video/tuần) không xếp hạng trong tuần: so với trung vị 8 Long gần nhất + giữ chân ở 2% đầu video.
  CẦU  : gợi ý tìm kiếm YouTube (miễn phí) + video nhiều view 30 ngày qua của ngách (search.list, 100 đơn vị/truy vấn,
         --no-search để bỏ) -> chủ đề, bỏ cái kênh đã làm (hf_novelty).
Không có: hồi quy, tự đổi chủ đề, tự đổi giờ -- dữ liệu sạch sau 01/10 chưa đủ (giống V2).

    python hf_brief.py                 # cả hai kênh -> output/cl_staging/briefs/<kênh>.md
    python hf_brief.py bud --no-search
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics as st
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from youtube_analytics import _query  # noqa: E402
from youtube_catalog import VIDEOS_URL, _get  # noqa: E402

CHANNELS = {"bud": ".youtube_channels/phat_giao.json", "fs": ".youtube_channels/phong_thuy.json"}
CACHE = ROOT / "chunks_cache" / "brief"
OUT = ROOT / "output" / "cl_staging" / "briefs"
PT, VN = ZoneInfo("America/Los_Angeles"), ZoneInfo("Asia/Ho_Chi_Minh")
CLEAN_FROM = date(2026, 10, 5)
MIN_WEEK = 15
METRICS = "views,engagedViews,averageViewDuration,averageViewPercentage,likes,subscribersGained"
SEEDS = {"bud": ["lời phật dạy", "phật dạy", "kinh phật", "nghiệp", "buông bỏ", "phật pháp"],
         "fs": ["phong thủy", "xem tuổi", "năm 2027", "xem ngày", "tử vi", "hợp tuổi", "mệnh"]}
SEARCH = {"bud": ["lời phật dạy", "phật pháp ứng dụng", "kinh phật giảng giải"],
          "fs": ["phong thủy nhà ở", "tử vi 2027", "phong thủy tuổi hợp"]}
# Kết quả search/gợi ý phải thuộc ngách (search "xem tuổi" từng kéo về phim review, video tiếng Hàn).
NICHE = {"bud": re.compile(r"(?i)phật|kinh|thiền|chùa|nghiệp|nhân quả|pháp|niệm|bồ tát|buông|tâm an|sân hận|giới|tu "),
         "fs": re.compile(r"(?i)phong th[uủ]y|tử vi|tuổi (?:tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi|hợp)|hợp tuổi|"
                          r"mệnh|ngũ hành|xem ngày|bát trạch|con giáp|năm 20\d\d|sinh năm|\b(19|20)\d\d hợp|màu hợp|hướng nhà")}


def _secs(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    return int(m[1] or 0) * 3600 + int(m[2] or 0) * 60 + int(m[3] or 0) if m else 0


def last_data_day(cred: str) -> date:
    end = date.today()
    r = _query(cred, {"ids": "channel==MINE", "startDate": str(end - timedelta(days=10)), "endDate": str(end),
                      "dimensions": "day", "metrics": "views"})
    return max(date.fromisoformat(x[0]) for x in r.get("rows", []))


def our_rows(ch: str) -> dict[str, dict]:
    """video_id -> row trong plan (short + long) của pipeline."""
    out = {}
    for lane in (ch, "long"):
        led = ROOT / f"output/cl_staging/{lane}/uploaded.json"
        if not led.exists():
            continue
        ids = json.loads(led.read_text(encoding="utf-8"))
        rows = {r["id"]: r for f in glob.glob(str(ROOT / f"output/cl_staging/{lane}/plan_*.json")) for r in json.load(open(f))}
        for rid, vid in ids.items():
            if rid in rows and rows[rid].get("series") == ch:
                out[vid] = rows[rid]
    return out


def videos(cred: str, ids: list[str]) -> dict[str, dict]:
    meta = {}
    for i in range(0, len(ids), 50):
        for v in _get(cred, VIDEOS_URL, {"part": "snippet,contentDetails,status", "id": ",".join(ids[i:i + 50])}).get("items", []):
            when = v["status"].get("publishAt") if v["status"].get("privacyStatus") != "public" else None
            when = when or v["snippet"]["publishedAt"]
            meta[v["id"]] = {"title": v["snippet"]["title"], "dur": _secs(v["contentDetails"]["duration"]),
                             "public": v["status"].get("privacyStatus") == "public",
                             "on_air": datetime.fromisoformat(when.replace("Z", "+00:00"))}
    return meta


def collect(ch: str) -> dict[str, dict]:
    """Đo mọi video đã đóng cửa sổ 7 ngày; cache những gì đã đóng (bất biến)."""
    cred = str(ROOT / CHANNELS[ch])
    CACHE.mkdir(parents=True, exist_ok=True)
    cf = CACHE / f"metrics_{ch}.json"
    done = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {}
    last = last_data_day(cred)
    start = last - timedelta(days=40)
    r = _query(cred, {"ids": "channel==MINE", "startDate": str(start), "endDate": str(last), "dimensions": "video",
                      "metrics": "views", "sort": "-views", "maxResults": 200})
    cand = {x[0] for x in r.get("rows", [])} | set(our_rows(ch))
    tf = ROOT / "chunks_cache" / "channel_titles" / f"{ch}.json"   # mọi video của kênh (hf_novelty refresh), kể cả bài ít view
    if tf.exists():
        cand |= {v["id"] for v in json.loads(tf.read_text(encoding="utf-8"))["videos"]}
    meta = videos(cred, sorted(cand - set(done)))
    groups: dict[date, list[str]] = {}
    for vid, m in meta.items():
        d0 = m["on_air"].astimezone(PT).date()
        if m["public"] and start <= d0 and d0 + timedelta(days=6) <= last:
            groups.setdefault(d0, []).append(vid)
    for d0, vids in sorted(groups.items()):
        for i in range(0, len(vids), 200):
            part = vids[i:i + 200]
            q = {"ids": "channel==MINE", "startDate": str(d0), "endDate": str(d0 + timedelta(days=6)), "dimensions": "video",
                 "filters": "video==" + ",".join(part), "maxResults": 200}
            try:
                rep = _query(cred, {**q, "metrics": METRICS})
            except Exception:  # noqa: BLE001 -- engagedViews bị từ chối: lưu NULL, KHÔNG chép views sang (không xếp hạng)
                rep = _query(cred, {**q, "metrics": METRICS.replace("engagedViews,", "")})
            hdr = [h["name"] for h in rep["columnHeaders"]]
            got = {row[0]: dict(zip(hdr, row)) for row in rep.get("rows", [])}
            for vid in part:
                m = meta[vid]
                a = got.get(vid, {"views": 0, "engagedViews": 0, "averageViewDuration": 0, "averageViewPercentage": 0,
                                  "likes": 0, "subscribersGained": 0})
                done[vid] = {**{k: a.get(k) for k in hdr if k != "video"}, "engagedViews": a.get("engagedViews"),
                             "title": m["title"], "dur": m["dur"], "day_pt": str(d0),
                             "vn": m["on_air"].astimezone(VN).strftime("%Y-%m-%d %H:%M")}
    cf.write_text(json.dumps(done, ensure_ascii=False, indent=0), encoding="utf-8")
    return done


def ranks(items: list[tuple[str, float]]) -> dict[str, float]:
    """Hạng phần trăm midrank 0..1 (hoà lấy hạng trung bình)."""
    xs = sorted(v for _, v in items)
    n = len(xs)
    out = {}
    for k, v in items:
        lo = sum(1 for x in xs if x < v)
        eq = sum(1 for x in xs if x == v)
        out[k] = (lo + (eq - 1) / 2) / (n - 1) if n > 1 else .5
    return out


def week_of(day_pt: str) -> str:
    y, w, _ = date.fromisoformat(day_pt).isocalendar()
    return f"{y}-W{w:02d}"


def score_shorts(m: dict[str, dict], ours: dict[str, dict]) -> tuple[list[dict], dict[str, int]]:
    shorts = {v: x for v, x in m.items() if x["dur"] <= 180 and x.get("engagedViews") is not None}
    weeks: dict[str, list[str]] = {}
    for v, x in shorts.items():
        weeks.setdefault(week_of(x["day_pt"]), []).append(v)
    out, sizes = [], {}
    for wk, vids in weeks.items():
        sizes[wk] = len(vids)
        if len(vids) < MIN_WEEK:
            continue
        rk = ranks([(v, shorts[v]["engagedViews"]) for v in vids])
        for v in vids:
            x, r = shorts[v], ours.get(v, {})
            out.append({**x, "vid": v, "rank": rk[v], "week": wk, "clean": date.fromisoformat(x["day_pt"]) >= CLEAN_FROM,
                        "rid": r.get("id"), "ours": bool(r), "style": r.get("style"), "hook": (r.get("script") or [""])[0],
                        "v2": bool(r.get("insight")), "hour": x["vn"][11:13] + "h"})
    return out, sizes


def group_table(rows: list[dict], key, label: str, min_n: int = 4) -> list[str]:
    g: dict[str, list[dict]] = {}
    for x in rows:
        k = key(x)
        if k is not None:
            g.setdefault(str(k), []).append(x)
    lines = [f"| {label} | n | hạng trung vị | view trung vị | % xem trung vị |", "|---|---|---|---|---|"]
    for k, xs in sorted(g.items(), key=lambda kv: -st.median(x["rank"] for x in kv[1])):
        if len(xs) >= min_n:
            lines.append(f"| {k} | {len(xs)} | {st.median(x['rank'] for x in xs):.2f} | {st.median(x['views'] for x in xs):.0f} | "
                         f"{st.median(x['averageViewPercentage'] for x in xs):.0f}% |")
    return lines if len(lines) > 2 else []


def dur_bucket(s: int) -> str:
    return next(lab for hi, lab in ((20, "<20s"), (27, "20-26s"), (33, "27-32s"), (61, "33-60s"), (999, ">60s")) if s < hi)


def long_section(ch: str, m: dict[str, dict], ours: dict[str, dict]) -> list[str]:
    longs = sorted(((v, x) for v, x in m.items() if x["dur"] > 180 and v in ours), key=lambda kv: kv[1]["day_pt"])
    if not longs:
        return ["_Chưa Long nào đóng cửa sổ 7 ngày._"]
    cred = str(ROOT / CHANNELS[ch])
    base = longs[-9:-1] if len(longs) > 1 else longs
    med = {k: st.median(x[k] for _, x in base) for k in ("views", "averageViewPercentage", "averageViewDuration")}
    out = [f"Trung vị {len(base)} Long trước: {med['views']:.0f} view 7 ngày, xem {med['averageViewPercentage']:.0f}%, "
           f"TB {med['averageViewDuration'] / 60:.1f} phút.", "",
           "| Long | lên sóng | view 7 ngày | so trung vị | % xem | TB phút | còn ở 2% đầu |", "|---|---|---|---|---|---|---|"]
    for v, x in longs[-8:]:
        try:
            rep = _query(cred, {"ids": "channel==MINE", "startDate": x["day_pt"],
                                "endDate": str(date.fromisoformat(x["day_pt"]) + timedelta(days=6)),
                                "dimensions": "elapsedVideoTimeRatio", "metrics": "audienceWatchRatio", "filters": f"video=={v}"})
            early = next((p[1] for p in rep.get("rows", []) if round(p[0], 2) == .02), None)
        except Exception:  # noqa: BLE001
            early = None
        out.append(f"| {x['title'][:60]} | {x['vn'][:10]} | {x['views']} | x{x['views'] / max(1, med['views']):.2f} | "
                   f"{x['averageViewPercentage']:.0f}% | {x['averageViewDuration'] / 60:.1f} | "
                   f"{'' if early is None else f'{early:.0%}'} |")
    return out


# ---------------- nhu cầu bên ngoài ----------------
def suggest(seed: str) -> list[str]:
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "ds": "yt", "hl": "vi", "gl": "VN", "q": seed})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as r:
            return json.loads(r.read().decode("utf-8", "replace"))[1]
    except Exception:  # noqa: BLE001
        return []


def demand_suggest(ch: str) -> list[tuple[str, int]]:
    """Cụm tìm kiếm hay gặp: gợi ý cho từng hạt giống + hạt giống kèm một chữ cái (a..y)."""
    score: dict[str, int] = {}
    for seed in SEEDS[ch]:
        for q in [seed] + [f"{seed} {c}" for c in "abcdghklmnpqstvxy"]:
            for i, s in enumerate(suggest(q)):
                score[s] = score.get(s, 0) + (10 - i)
            time.sleep(.15)
    junk = re.compile(r"(?i)karaoke|remix|lyric|vietsub|beat|tiktok|cover|\blive\b|nhạc|bài hát|không quảng cáo|audio|"
                      r"phần \d|tập \d|cố ninh thần|vành môi|nơi anh")   # tên bài hát, bản audio dài -- không phải chủ đề
    return sorted(((k, v) for k, v in score.items() if not junk.search(k) and NICHE[ch].search(k)), key=lambda kv: -kv[1])


def demand_search(ch: str) -> list[dict]:
    """Video nhiều view nhất 30 ngày qua của ngách (search.list 100 đơn vị/truy vấn) + view/ngày."""
    cred = str(ROOT / CHANNELS[ch])
    after = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = {}
    for q in SEARCH[ch]:
        r = _get(cred, "https://www.googleapis.com/youtube/v3/search",
                 {"part": "snippet", "q": q, "type": "video", "order": "viewCount", "regionCode": "VN",
                  "relevanceLanguage": "vi", "publishedAfter": after, "maxResults": 25})
        for it in r.get("items", []):
            found[it["id"]["videoId"]] = it["snippet"]["channelTitle"]
    out = []
    ids = list(found)
    for i in range(0, len(ids), 50):
        for v in _get(cred, VIDEOS_URL, {"part": "snippet,statistics,contentDetails", "id": ",".join(ids[i:i + 50])}).get("items", []):
            age = max(1.0, (datetime.now(timezone.utc) - datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))).days)
            views = int(v["statistics"].get("viewCount", 0))
            out.append({"title": v["snippet"]["title"], "channel": found[v["id"]], "views": views, "per_day": views / age,
                        "dur": _secs(v["contentDetails"]["duration"]), "id": v["id"]})
    return sorted((x for x in out if NICHE[ch].search(x["title"])), key=lambda x: -x["per_day"])


def brief(ch: str, search: bool = True) -> Path:
    import hf_novelty  # noqa: PLC0415
    m = collect(ch)
    ours = our_rows(ch)
    sc, sizes = score_shorts(m, ours)
    clean = [x for x in sc if x["clean"]]
    ref = [x for x in sc if not x["clean"]][-120:]
    L = [f"# Bản tóm tắt kênh {ch.upper()} — {date.today():%d/%m/%Y}", "",
         f"Số liệu Analytics tới {max((x['day_pt'] for x in m.values()), default='?')} (+6 ngày cửa sổ). "
         f"Tuần short: " + ", ".join(f"{w}: {n}" for w, n in sorted(sizes.items())[-6:]) + f" (xếp hạng khi >= {MIN_WEEK}).", ""]
    for label, rows in (("## Short — tuần sạch (từ 05/10/2026)", clean),
                        ("## Short — THAM KHẢO, tuần trước 05/10 (dính cập nhật Shorts 01/10, đăng dồn)", ref)):
        L += [label, ""]
        if not rows:
            L += ["_Chưa có tuần nào đủ điều kiện (tuần đầu tiên đóng khoảng 20/10)._", ""]
            continue
        for tab in (group_table(rows, lambda x: "pipeline" if x["ours"] else "nguồn ngoài", "nguồn"),
                    group_table(rows, lambda x: x["hour"], "giờ VN"),
                    group_table(rows, lambda x: dur_bucket(x["dur"]), "độ dài"),
                    group_table([x for x in rows if x["ours"]], lambda x: x["style"], "khung"),
                    group_table([x for x in rows if x["ours"]], lambda x: "v2" if x["v2"] else "cũ", "công thức")):
            L += tab + ([""] if tab else [])
        top = sorted(rows, key=lambda x: -x["rank"])
        for lab, xs in (("Cao nhất", top[:6]), ("Thấp nhất", top[-6:])):
            L += [f"**{lab}**", ""]
            L += [f"- {x['rank']:.2f} · {x['views']} view · {x['averageViewPercentage']:.0f}% · {x['dur']}s · {x['vn'][5:]} — "
                  f"{x['title'][:70]}" + (f"  \n  mở: _{x['hook'][:90]}_" if x["hook"] else "") for x in xs]
            L.append("")
    L += ["## Long", ""] + long_section(ch, m, ours) + [""]
    L += ["## Nhu cầu bên ngoài", "", "**Gợi ý tìm kiếm YouTube (điểm = tần suất × thứ tự)**", ""]
    sug = demand_suggest(ch)
    L += [f"- {s} ({n})" + ("  ← kênh đã có" if hf_novelty.duplicates(ch, s) else "") for s, n in sug[:40]]
    if search:
        L += ["", "**Video nhiều view/ngày trong ngách, 30 ngày qua** (search.list)", ""]
        for x in demand_search(ch)[:25]:
            dup = hf_novelty.duplicates(ch, x["title"])
            L.append(f"- {x['per_day']:.0f}/ngày · {x['views']} view · {'short' if x['dur'] <= 180 else f'{x['dur'] // 60} phút'} · "
                     f"{x['channel'][:24]} — {x['title'][:80]}" + ("  ← kênh đã có" if dup else ""))
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{ch}.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("channels", nargs="*", default=list(CHANNELS))
    ap.add_argument("--no-search", action="store_true")
    a = ap.parse_args()
    for ch in a.channels:
        print(brief(ch, not a.no_search))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
