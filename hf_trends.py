"""Nghiên cứu chủ đề Long đang hút trong ngách BUD / FS: kênh đối thủ + gợi ý tìm kiếm (06/10/2026).

Bài học từ kênh CL của V2: "BẾN THƯỢNG HẢI ngoài đời thật" (~790 view/ngày) gấp 5 lần Long thường -- chủ đề bám vào thứ
khán giả Việt ĐÃ BIẾT (phim, nhân vật, địa danh). Công cụ này tìm những thứ như vậy trong ngách Phật giáo / Phong thủy:
  1. discover: search.list (video dài/trung bình, 120 ngày, VN, xếp theo view) -> kênh xuất hiện nhiều nhất = đối thủ
     -> chunks_cache/brief/competitors_<kênh>.json (làm lại khi --rediscover).
  2. scan: mỗi kênh đối thủ 50 video mới nhất (playlistItems 1 đơn vị + videos.list 1 đơn vị) -> Long > 8 phút,
     120 ngày, xếp theo view/ngày; đánh dấu chủ đề kênh mình đã có (hf_novelty).
  3. gợi ý tìm kiếm cho các mẫu "neo": "... ngoài đời thật", "sự thật về ...", "tiểu sử ...", "bí ẩn ...".
Kết quả: output/cl_staging/briefs/<kênh>_trends.md. Chỉ đọc. Quota: discover ~800 đơn vị, scan ~2 đơn vị/kênh đối thủ.

    python hf_trends.py bud [--rediscover]
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from youtube_catalog import VIDEOS_URL, _get  # noqa: E402

import hf_brief as B  # noqa: E402

API = "https://www.googleapis.com/youtube/v3"
DISCOVER_Q = {"bud": ["lời phật dạy", "phật pháp", "chuyện phật giáo", "thiền sư"],
              "fs": ["phong thủy", "tử vi 2027", "xem tuổi", "tâm linh việt nam"]}
ANCHOR_SEEDS = {"bud": ["ngoài đời thật phật", "sự thật về đức phật", "tiểu sử thiền sư", "bí ẩn chùa", "đường tăng huyền trang",
                        "tây du ký ngoài đời thật", "phật hoàng trần nhân tông", "chuyện tiền thân đức phật"],
                "fs": ["thầy tả ao", "sự thật về phong thủy", "bí ẩn kinh thành huế", "phong thủy hà nội xưa", "tiểu sử thầy phong thủy",
                       "bí ẩn lăng mộ", "phong thủy lăng vua", "ngoài đời thật tử vi"]}


def _secs(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    return int(m[1] or 0) * 3600 + int(m[2] or 0) * 60 + int(m[3] or 0) if m else 0


def _me(cred: str) -> str:
    return _get(cred, f"{API}/channels", {"part": "id", "mine": "true"})["items"][0]["id"]


def discover(ch: str) -> list[dict]:
    cred = str(ROOT / B.CHANNELS[ch])
    after = (datetime.now(timezone.utc) - timedelta(days=120)).strftime("%Y-%m-%dT%H:%M:%SZ")
    me = _me(cred)
    count: dict[str, dict] = {}
    for q in DISCOVER_Q[ch]:
        for dur in ("long", "medium"):
            r = _get(cred, f"{API}/search", {"part": "snippet", "q": q, "type": "video", "order": "viewCount", "regionCode": "VN",
                                              "relevanceLanguage": "vi", "publishedAfter": after, "videoDuration": dur, "maxResults": 50})
            for it in r.get("items", []):
                cid, title = it["snippet"]["channelId"], it["snippet"]["title"]
                if cid == me or not B.NICHE[ch].search(title + " " + it["snippet"].get("description", "")):
                    continue
                c = count.setdefault(cid, {"id": cid, "title": it["snippet"]["channelTitle"], "hits": 0})
                c["hits"] += 1
    comp = sorted(count.values(), key=lambda c: -c["hits"])[:20]
    (B.CACHE / f"competitors_{ch}.json").write_text(json.dumps(comp, ensure_ascii=False, indent=1), encoding="utf-8")
    return comp


def scan(ch: str, comp: list[dict]) -> list[dict]:
    cred = str(ROOT / B.CHANNELS[ch])
    now = datetime.now(timezone.utc)
    ids = list(dict.fromkeys(c["id"] for c in comp))
    info = {}
    for i in range(0, len(ids), 50):
        for c in _get(cred, f"{API}/channels", {"part": "contentDetails,statistics,snippet", "id": ",".join(ids[i:i + 50])}).get("items", []):
            info[c["id"]] = {"up": c["contentDetails"]["relatedPlaylists"]["uploads"], "subs": int(c["statistics"].get("subscriberCount", 0) or 0),
                             "name": c["snippet"]["title"]}
    vids = []
    for cid, inf in info.items():
        try:
            r = _get(cred, f"{API}/playlistItems", {"part": "contentDetails", "playlistId": inf["up"], "maxResults": 50})
        except Exception:  # noqa: BLE001
            continue
        vid_ids = [x["contentDetails"]["videoId"] for x in r.get("items", [])]
        for v in _get(cred, VIDEOS_URL, {"part": "snippet,statistics,contentDetails", "id": ",".join(vid_ids)}).get("items", []) if vid_ids else []:
            dur = _secs(v["contentDetails"].get("duration", "PT0S"))
            pub = datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
            age = max(1.0, (now - pub).total_seconds() / 86400)
            if dur < 480 or age > 120:
                continue
            views = int(v["statistics"].get("viewCount", 0))
            vids.append({"title": v["snippet"]["title"], "channel": inf["name"], "subs": inf["subs"], "views": views,
                         "per_day": views / age, "per_sub": views / max(1, inf["subs"]), "dur": dur, "age": round(age), "id": v["id"]})
        time.sleep(.2)
    return sorted(vids, key=lambda x: -x["per_day"])


def anchors(ch: str) -> list[tuple[str, int]]:
    score: dict[str, int] = {}
    for seed in ANCHOR_SEEDS[ch]:
        for i, s in enumerate(B.suggest(seed)):
            score[s] = score.get(s, 0) + (10 - i)
        time.sleep(.15)
    return sorted(score.items(), key=lambda kv: -kv[1])


def report(ch: str, rediscover: bool = False) -> Path:
    import hf_novelty  # noqa: PLC0415
    cf = B.CACHE / f"competitors_{ch}.json"
    comp = discover(ch) if rediscover or not cf.exists() else json.loads(cf.read_text(encoding="utf-8"))
    vids = scan(ch, comp)
    L = [f"# Chủ đề Long đang hút · {ch.upper()} · {datetime.now():%d/%m/%Y}", "",
         f"Đối thủ ({len(comp)} kênh, tìm theo: {', '.join(DISCOVER_Q[ch])}): " + ", ".join(c["title"][:28] for c in comp[:12]), "",
         "## Long > 8 phút, 120 ngày, xếp theo view/ngày", "",
         "| view/ngày | view | view/sub | phút | kênh | tiêu đề | kênh mình |", "|---|---|---|---|---|---|---|"]
    for x in vids[:40]:
        dup = "đã có" if hf_novelty.duplicates(ch, x["title"]) else ""
        L.append(f"| {x['per_day']:.0f} | {x['views']} | {x['per_sub']:.1f} | {x['dur'] // 60} | {x['channel'][:22]} | {x['title'][:85]} | {dup} |")
    L += ["", "## Gợi ý tìm kiếm cho chủ đề \"neo\" (nhân vật, địa danh, phim khán giả đã biết)", ""]
    L += [f"- {s} ({n})" for s, n in anchors(ch)[:30]]
    out = B.OUT / f"{ch}_trends.md"
    B.OUT.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    for ch in [x for x in a if not x.startswith("--")] or ["bud", "fs"]:
        print(report(ch, "--rediscover" in a))
