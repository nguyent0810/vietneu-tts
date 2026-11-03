"""Đăng ĐÚNG MỘT hồ sơ S-tier lên kênh CL hoặc CK, với giờ hẹn chỉ định.

    python motion/stier/upload_one.py <slug> "2026-10-05 18:30"     # giờ VN
    python motion/stier/upload_one.py <slug> "2026-10-05 18:30" --dry
    python motion/stier/upload_one.py <slug> "2026-11-03 19:00" --channel CK --dry
    python motion/stier/upload_one.py <slug> "2026-11-03 19:00" --channel CK --wait

VÌ SAO CÓ FILE NÀY (04/10/2026): ngày 30/09 kênh CL nhận 61 video trong một ngày
(~53 video trong 47 phút, lô S-tier upload hàng loạt) và 1-2 ngày sau YouTube ngừng
đẩy short của kênh lên feed. Từ nay mỗi lần chỉ upload MỘT video, cách nhau vài giờ,
thường là trong ngày phát sóng -- không bao giờ đổ cả lô lên kênh.

- CL dùng slug "cl-hs-<slug>", giống enqueue.py. CK giữ nguyên slug trong
  spec CK. Cả hai không upload trùng nếu đã có video_id.
- Chống trùng tiêu đề với toàn bộ video trên kênh (Channel + channel_titles + novelty).
- Không bao giờ public ngay.
- Upload đi qua factory/channel.py: luật 3 giờ/lần của CL áp cho MỌI đường đăng
  (cả publish_batch), sổ upload_log thay cho output/stier/uploads.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from factory import channels, publish, store  # noqa: E402
from factory.bundle import Bundle  # noqa: E402
from factory.channel import Channel, PacingHold, Upload, upload_when_free  # noqa: E402
from factory.lines import novelty  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enqueue import FOOT, OUT, SPECS  # noqa: E402


def _args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("vn", help="giờ VN: YYYY-MM-DD HH:MM")
    parser.add_argument("--channel", choices=("CL", "CK"), default="CL")
    parser.add_argument("--dry", action="store_true", help="kiểm tra, không ghi store hoặc upload")
    parser.add_argument("--wait", action="store_true", help="chờ đúng lượt giãn nhịp thay vì thoát")
    return parser.parse_args(argv)


def _cl_bundle(s: str, when: str) -> tuple[Bundle, Path]:
    spec = json.loads((SPECS / f"{s}.json").read_text(encoding="utf-8"))
    fin = OUT / s / "final.mp4"
    if not fin.exists():
        raise SystemExit(f"chưa có {fin}")
    slug = f"cl-hs-{s}"
    tags = spec.get("hashtags") or FOOT.split("\n\n")[-1]
    if spec.get("fiction"):        # truyện hư cấu: không có nguồn/ảnh Commons
        desc = spec["description"] + "\n\n" + tags
    else:
        desc = (spec["description"] + "\n\nNguồn: " + "; ".join(spec.get("sources", [])) + "\n\n"
                + FOOT.split("\n\n")[0].replace("dưới đây", "trên") + "\n\n" + tags)
    bundle = Bundle(channel="CL", kind="short", slug=slug, script=" ".join(spec["lines"]), title=spec["title"][:100],
                    description=desc[:5000], tags=spec.get("tags", [])[:12], thumbnail_text=spec["title"][:60],
                    publish_at=when, voice="Anh Khôi", bgm="", broll_queries=[],
                    render={"engine": "casefile", "spec": f"data/stier/specs/{s}.json"},
                    source_note="; ".join(spec.get("sources", [])))
    return bundle, fin


def _ck_bundle(s: str, vn: str) -> tuple[Bundle, Path]:
    # enqueue_ck là nơi giữ các luật CK: theme, miễn trừ, credits và âm nhạc.
    from enqueue_ck import OUT as ck_out, bundle_for  # noqa: E402

    bundle = bundle_for(s, vn)
    fin = ck_out / s / "final.mp4"
    if not fin.exists():
        raise SystemExit(f"chưa có {fin}")
    return bundle, fin


def build_bundle(channel: str, slug: str, vn: str, when: str) -> tuple[Bundle, Path]:
    """Tạo Bundle đã validate theo luật từng kênh, chưa ghi store hay gọi API."""
    bundle, fin = _ck_bundle(slug, vn) if channel == "CK" else _cl_bundle(slug, when)
    bundle.validate()
    return bundle, fin


def main(argv: list[str] | None = None):
    args = _args(argv)
    s, vn, channel, dry = args.slug, args.vn, args.channel, args.dry
    when = (datetime.strptime(vn, "%Y-%m-%d %H:%M") - timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    scheduled = datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if scheduled < datetime.now(timezone.utc) + timedelta(minutes=30):
        raise SystemExit(f"giờ hẹn {vn} VN đã quá sát hoặc đã qua -- chọn giờ muộn hơn")
    b, fin = build_bundle(channel, s, vn, when)
    slug = b.slug
    print(f"{vn} VN ({when})  {slug}  {b.title}")
    if dry:
        print(b.description)
        print("CHẠY KHÔ: không ghi store hoặc upload")
        return
    with store.connect() as conn:
        row = conn.execute("SELECT stage, video_id FROM item WHERE channel=? AND slug=?", (channel, slug)).fetchone()
        if row and row["video_id"]:
            raise SystemExit(f"{slug} đã đăng rồi: {row['video_id']}")
        dup = novelty.duplicate_on_channel(channel, b.title)
        if dup:
            raise SystemExit(f"TRÙNG CHỦ ĐỀ với video đã có: '{dup['title']}'")
        if not row:
            store.save_bundle(b)
            store.enqueue(b, conn)
        store.mark(conn, b.id, "assembled", video_path=str(fin))
        creds = json.loads(channels.creds_path(channel).read_text(encoding="utf-8"))
        tok = publish.access_token(creds)
        chan = Channel.open(channel, conn, channel_titles=publish.channel_titles(publish.uploads_playlist_id(tok), tok))
        try:
            upload = Upload(slug=slug, video=fin, title=b.title, description=b.description,
                            tags=tuple(b.tags), kind="short", publish_at=when)
            res = upload_when_free(chan, upload) if args.wait else chan.upload(upload)
        except PacingHold as exc:       # tiến trình khác vừa giành slot
            raise SystemExit(f"CHƯA TỚI LƯỢT: {exc}")
        store.mark(conn, b.id, "published", video_id=res.video_id)
    print(f"OK {res.url}  hẹn {res.publish_at}")


if __name__ == "__main__":
    from factory.console import utf8_console  # noqa: E402
    utf8_console()  # console Windows cp1252 không in được tiếng Việt (retro 2 mục 7)
    main()
