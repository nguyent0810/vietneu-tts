"""Gỡ lịch hẹn các video v2 CHƯA lên sóng của một kênh -> private, KHÔNG hẹn giờ.

    python scripts/unschedule.py --channel FS                         # chạy khô, liệt kê tất cả
    python scripts/unschedule.py --channel CK --slug ck-video         # chạy khô, chỉ slug này
    python scripts/unschedule.py --channel CK --slug ck-video --apply # gỡ thật

Không có ``--slug`` thì giữ nguyên hành vi cũ: xét mọi video v2 của kênh.
Có ``--slug`` thì mọi slug được nêu phải còn private và có publishAt ở tương
lai; nếu không, lệnh dừng trước khi gỡ bất cứ video nào.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from factory.console import utf8_console  # noqa: E402

utf8_console()  # console Windows cp1252 không in được tiếng Việt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from factory import channels, publish, store  # noqa: E402
from factory.channel import Channel  # noqa: E402


def _future_private(status: dict, now: datetime) -> bool:
    """True khi status YouTube còn private và publishAt nằm ở tương lai."""
    publish_at = status.get("publishAt")
    return bool(
        status.get("privacyStatus") == "private"
        and publish_at
        and datetime.fromisoformat(publish_at.replace("Z", "+00:00")) > now
    )


def select_scheduled(
    rows: dict[str, dict], videos: Iterable[dict], now: datetime, slugs: Iterable[str] = ()
) -> list[tuple[dict, dict]]:
    """Lọc video private có lịch tương lai, hoàn toàn không gọi API.

    ``rows`` là item trong store theo video_id, ``videos`` là phần ``items``
    trả về từ YouTube. Khi có slug, kiểm đủ tất cả slug trước khi trả kết quả;
    nhờ vậy caller không thể gỡ một phần danh sách rồi mới phát hiện slug lỗi.
    """
    wanted = list(dict.fromkeys(slugs))
    by_slug = {row["slug"]: row for row in rows.values()}
    missing = [slug for slug in wanted if slug not in by_slug]
    if missing:
        raise ValueError("không có trong store: " + ", ".join(missing))

    scoped_ids = set(rows) if not wanted else {
        row["video_id"] for slug, row in by_slug.items() if slug in wanted
    }
    eligible: dict[str, tuple[dict, dict]] = {}
    for video in videos:
        video_id = video.get("id")
        if video_id not in scoped_ids:
            continue
        status = video.get("status", {})
        if _future_private(status, now):
            row = rows[video_id]
            eligible[row["slug"]] = (row, status)

    if wanted:
        unavailable = [slug for slug in wanted if slug not in eligible]
        if unavailable:
            raise ValueError(
                "không còn private + publishAt tương lai (hoặc YouTube không trả video): "
                + ", ".join(unavailable)
            )
        return [eligible[slug] for slug in wanted]
    return sorted(eligible.values(), key=lambda item: item[0].get("publish_at") or "")


def video_ids_for_slugs(rows: dict[str, dict], slugs: Iterable[str]) -> list[str]:
    """ID cần hỏi YouTube; có slug thì không quét các item không liên quan."""
    wanted = list(dict.fromkeys(slugs))
    if not wanted:
        return list(rows)
    by_slug = {row["slug"]: row for row in rows.values()}
    missing = [slug for slug in wanted if slug not in by_slug]
    if missing:
        raise ValueError("không có trong store: " + ", ".join(missing))
    return [by_slug[slug]["video_id"] for slug in wanted]


def _args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", default="FS", choices=channels.CHANNELS)
    parser.add_argument("--slug", action="append", default=[], help="slug cần gỡ lịch (lặp được)")
    parser.add_argument("--apply", action="store_true", help="ghi thay đổi; mặc định chỉ chạy khô")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _args(argv)
    token = publish.access_token(json.loads(channels.creds_path(args.channel).read_text(encoding="utf-8")))
    with store.connect() as conn:
        rows = {
            row["video_id"]: dict(row)
            for row in conn.execute(
                "SELECT id, slug, video_id, publish_at FROM item "
                "WHERE channel=? AND video_id IS NOT NULL",
                (args.channel,),
            )
        }
    now = datetime.now(timezone.utc)
    videos: list[dict] = []
    try:
        ids = video_ids_for_slugs(rows, args.slug)
    except ValueError as exc:
        raise SystemExit(f"KHÔNG GỠ LỊCH: {exc}") from exc
    for offset in range(0, len(ids), 50):
        response = publish._api(token, "GET", "videos", {"part": "status", "id": ",".join(ids[offset:offset + 50])})
        videos.extend(response.get("items", []))
    try:
        todo = select_scheduled(rows, videos, now, args.slug)
    except ValueError as exc:
        raise SystemExit(f"KHÔNG GỠ LỊCH: {exc}") from exc

    print(f"{args.channel}: {len(rows)} video v2 trên kênh · {len(todo)} đang hẹn giờ chưa lên sóng")
    if todo:
        print(f"   từ {todo[0][0]['publish_at']} ({todo[0][0]['slug']}) "
              f"tới {todo[-1][0]['publish_at']} ({todo[-1][0]['slug']})")
    if not args.apply:
        print("CHẠY KHÔ — thêm --apply để gỡ lịch thật.")
        return

    reason = f"UNSCHEDULED {now:%Y-%m-%d}: thay bằng Short khác (GH-28)"
    with store.connect() as conn:
        channel = Channel.open(args.channel, conn)
        for done, (row, _status) in enumerate(todo, start=1):
            # Gỡ lịch = private không publishAt. Channel merge mọi trường status khác.
            channel.reschedule(row["video_id"], None)
            conn.execute(
                "UPDATE item SET stage='failed', attempts=99, error=?, updated_at=? WHERE id=?",
                (reason, now.strftime("%Y-%m-%dT%H:%M:%SZ"), row["id"]),
            )
            if done % 10 == 0:
                print(f"   đã gỡ {done}/{len(todo)}")
    print(f"ĐÃ GỠ LỊCH {len(todo)} video (private, không hẹn giờ).")


if __name__ == "__main__":
    main()
