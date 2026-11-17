"""Đổi tiêu đề Short đã hẹn lịch (GH-454, chủ kênh duyệt 17/11/2026).

Chỉ đổi snippet.title. Giữ nguyên mô tả, tag, danh mục, trạng thái private và publishAt.
Bỏ qua video không còn private hoặc không có publishAt (đã lên sóng: để yên).

    python scripts/retitle_shorts.py <titles.json>            # chạy thử, in bảng cũ -> mới
    python scripts/retitle_shorts.py <titles.json> --apply    # ghi lên YouTube

titles.json: {"<slug>": {"title": "..."}}. Nhật ký cũ/mới: output/retitle/applied.jsonl (để đo CTR).
Chi phí: videos.list 1 + videos.update 50 đơn vị mỗi video.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from factory.console import utf8_console  # noqa: E402

utf8_console()
from factory import channels  # noqa: E402
from factory.youtube_api import HttpYouTube  # noqa: E402

LOG = ROOT / "output" / "retitle" / "applied.jsonl"


def rows(db: Path, slugs: set[str]) -> list[dict]:
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    got = [dict(r) for r in conn.execute(
        "SELECT channel, slug, video_id, publish_at FROM item WHERE kind='short' AND video_id IS NOT NULL")]
    return [r for r in got if r["slug"] in slugs]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("titles")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--channel", help="chỉ một kênh (MIM/CK/CL)")
    a = ap.parse_args()
    titles = json.loads(Path(a.titles).read_text(encoding="utf-8"))
    bad = {s: v["title"] for s, v in titles.items() if not v.get("title") or len(v["title"]) > 60}
    if bad:
        print("tiêu đề rỗng hoặc > 60 ký tự:", bad)
        return 2
    items = rows(ROOT / "state.sqlite", set(titles))
    if a.channel:
        items = [r for r in items if r["channel"] == a.channel]
    missing = set(titles) - {r["slug"] for r in items}
    if missing and not a.channel:
        print("không thấy trong state:", sorted(missing))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    apis: dict[str, HttpYouTube] = {}
    done = skipped = 0
    for r in sorted(items, key=lambda r: (r["channel"], r["publish_at"])):
        api = apis.get(r["channel"])
        if api is None:
            creds = json.loads(channels.creds_path(r["channel"]).read_text(encoding="utf-8"))
            api = apis[r["channel"]] = HttpYouTube(creds)
        v = api.get_video(r["video_id"], "snippet,status")
        new = titles[r["slug"]]["title"]
        if not v:
            print(f"BỎ  {r['channel']} {r['video_id']} không tìm thấy")
            skipped += 1
            continue
        st, sn = v["status"], v["snippet"]
        if st.get("privacyStatus") != "private" or not st.get("publishAt") or st["publishAt"] <= now:
            print(f"BỎ  {r['channel']} {r['video_id']} đã/sắp lên sóng ({st.get('privacyStatus')}, {st.get('publishAt')})")
            skipped += 1
            continue
        old = sn["title"]
        if old == new:
            print(f"GIỮ {r['channel']} {r['video_id']} {old}")
            continue
        print(f"{'ĐỔI' if a.apply else 'THỬ'} {r['channel']} {r['video_id']} {st['publishAt']}\n     cũ: {old}\n     mới: {new}")
        if not a.apply:
            continue
        body = {"id": r["video_id"], "snippet": {k: sn[k] for k in
                ("title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage") if k in sn}}
        body["snippet"]["title"] = new
        api.update_video("snippet", body)
        after = api.get_video(r["video_id"], "snippet,status")
        ok = after["snippet"]["title"] == new and after["status"].get("publishAt") == st["publishAt"] \
            and after["status"].get("privacyStatus") == "private"
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now, "channel": r["channel"], "slug": r["slug"], "video_id": r["video_id"],
                                "publish_at": st["publishAt"], "old": old, "new": new, "verified": ok},
                               ensure_ascii=False) + "\n")
        if not ok:
            print("     !! kiểm lại sau khi ghi không khớp")
            return 1
        done += 1
    print(f"xong: đổi {done}, bỏ {skipped}, {'ĐÃ GHI' if a.apply else 'chạy thử'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
