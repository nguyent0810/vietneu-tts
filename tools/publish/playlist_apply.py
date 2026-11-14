"""Review/apply playlist plan in small batches. Dry-run is the default."""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from youtube_auth import get_valid_access_token
import urllib.parse
import urllib.request

PLAN = Path(__file__).resolve().parents[2] / "output/cl_staging/scoreboard/playlist_plan.json"
CREDS = {"fs": ".youtube_channels/phong_thuy.json", "bud": ".youtube_channels/phat_giao.json"}


def playlist_for_row(channel, row):
    cfg = json.loads(PLAN.read_text(encoding="utf-8"))["channels"][channel]
    key = cfg.get("lane_map", {}).get(str(row.get("lane") or ""))
    if not key and row.get("lane") == "long":
        title = str(row.get("title") or "").casefold()
        key = "jataka" if channel == "bud" and ("tiền thân" in title or "jātaka" in title or "jataka" in title) else cfg.get("series_map", {}).get(str(row.get("series") or channel))
    return next((p for p in cfg["playlists"] if p["key"] == key), None)


def api_get(token, endpoint, params):
    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/" + endpoint + "?" + urllib.parse.urlencode(params), headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def inventory(channel):
    token = get_valid_access_token(CREDS[channel])
    out, page = [], None
    while True:
        p = {"part": "snippet,contentDetails", "mine": "true", "maxResults": 50}
        if page: p["pageToken"] = page
        data = api_get(token, "playlists", p)
        for x in data.get("items", []):
            pl = {"id": x["id"], "title": x["snippet"].get("title", ""), "video_count": x.get("contentDetails", {}).get("itemCount", 0), "created_at": x["snippet"].get("publishedAt"), "videos": []}
            item_page, video_ids = None, []
            while True:
                ip = {"part": "snippet,contentDetails", "playlistId": x["id"], "maxResults": 50}
                if item_page: ip["pageToken"] = item_page
                items = api_get(token, "playlistItems", ip)
                for item in items.get("items", []):
                    video_ids.append(item["snippet"].get("resourceId", {}).get("videoId"))
                item_page = items.get("nextPageToken")
                if not item_page: break
            for start in range(0, len(video_ids), 50):
                chunk = [v for v in video_ids[start:start + 50] if v]
                if not chunk: continue
                vids = api_get(token, "videos", {"part": "snippet", "id": ",".join(chunk)})
                pl["videos"].extend({"id": v["id"], "title": v["snippet"].get("title", ""), "published_at": v["snippet"].get("publishedAt")} for v in vids.get("items", []))
            pl["last_video_published_at"] = max((v.get("published_at", "") for v in pl["videos"]), default=None)
            out.append(pl)
        page = data.get("nextPageToken")
        if not page: return out


def apply(channel, batch_size=10, offset=0, confirm=False):
    plan = json.loads(PLAN.read_text(encoding="utf-8"))["channels"][channel]
    token = get_valid_access_token(CREDS[channel])
    existing = inventory(channel)
    by_title = {x["title"].strip().casefold(): x["id"] for x in existing}
    members = {x["title"].strip().casefold(): {v["id"] for v in x.get("videos", [])} for x in existing}
    operations = []
    for pl in plan["playlists"]:
        pid = by_title.get(pl["title"].strip().casefold())
        missing = not pid
        already = members.get(pl["title"].strip().casefold(), set())
        count = sum(v["id"] not in already for v in pl.get("videos", []))
        operations.append((pl, pid, missing, count))
    inserts = sum(min(batch_size, max(0, x[3] - offset)) for x in operations)
    creates = sum(x[2] for x in operations)
    # YouTube Data API quota estimate; one playlists.list call plus one list per target
    # would be needed for a fully idempotent membership reconciliation.
    print(f"{channel}: {len(operations)} playlist; {inserts} mục chưa có trong đợt; tối đa {min(batch_size, inserts)} insert/lượt; quota ghi ước tính đợt này: {creates*50 + inserts*50} units (insert=50), chưa tính GET/đối chiếu.")
    for pl, pid, missing, count in operations:
        print(f"{'TẠO' if missing else 'DÙNG'} {pl['title']} | đợt này {min(batch_size, max(0, count - offset))} video chưa có / tổng {count} chưa có")
    if not confirm: return
    for pl, pid, missing, _ in operations:
        if missing:
            body = {"snippet": {"title": pl["title"], "description": "", "defaultLanguage": "vi"}, "status": {"privacyStatus": "public"}}
            req = urllib.request.Request("https://www.googleapis.com/youtube/v3/playlists?part=snippet,status", data=json.dumps(body).encode(), method="POST", headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r: pid = json.loads(r.read())["id"]
        present = members.get(pl["title"].strip().casefold(), set())
        candidates = [v for v in pl.get("videos", []) if v["id"] not in present]
        for v in candidates[offset:offset + batch_size]:
            body = {"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": v["id"]}}}
            req = urllib.request.Request("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet", data=json.dumps(body).encode(), method="POST", headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r: r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", choices=["fs", "bud"])
    ap.add_argument("--inventory", action="store_true", help="Chỉ đọc danh sách playlist hiện có")
    ap.add_argument("--confirm", action="store_true", help="Tạo playlist/thêm video thật")
    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--offset", type=int, default=0, help="Vị trí bắt đầu trong từng playlist để chạy đợt kế")
    args = ap.parse_args()
    if not 1 <= args.batch_size <= 50 or args.offset < 0: ap.error("batch-size phải trong 1..50 và offset không âm")
    if args.inventory: print(json.dumps(inventory(args.channel), ensure_ascii=False, indent=2))
    else: apply(args.channel, args.batch_size, args.offset, args.confirm)

if __name__ == "__main__": main()
