"""Lấy retention curve + traffic source cho từng Short đã đăng vào baseline
raw LOCAL (ticket 09, D20/D36/D50).

Người vận hành chạy (cần OAuth YouTube hiện có ở máy này, qua youtube_auth --
không tự làm lại OAuth, không in token):

    uv run python baseline_analytics_fetch.py --channel phong_thuy \\
        --video-ids-file ids.txt --start 2026-01-01 --end 2026-09-28

`--video-ids-file`: mỗi dòng một video id, hoặc file JSON (list id, hoặc
ledger có `items[].youtube_video_id`).

Kết quả ghi vào `.scratch/improve-short-content-pipeline/baseline/raw/`
(gitignore), có version và thời điểm lấy. KHÔNG đẩy lên Hub (D50).

Xử lý lỗi dùng cùng cách phân loại của luồng sync (`is_transient_status`):
lỗi tạm thời được thử lại vài lần; hết lượt vẫn lỗi → ghi `transient_failed`
(chạy lại để lấp). Lỗi vĩnh viễn (400/404) → ghi thiếu kèm lý do. Video không
có dữ liệu (quá ít view) → ghi thiếu `no_data`. Không video nào làm hỏng cả
lần chạy.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

import youtube_sync as ys

OUTPUT_VERSION = 1
DEFAULT_OUT_DIR = Path(__file__).parent / ".scratch" / "improve-short-content-pipeline" / "baseline" / "raw"
MAX_ATTEMPTS = 3
BACKOFF_S = (2.0, 8.0)

Fetcher = Callable[..., tuple]


def _fetch_with_retry(fetch: Fetcher, *args, sleep: Callable[[float], None] = time.sleep) -> dict:
    """Gọi 1 báo cáo; phân loại kết quả thành bản ghi có trạng thái rõ ràng."""
    attempts = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            data, status = fetch(*args)
        except ys.SyncError as exc:  # lỗi mạng: coi là tạm thời
            data, status, error = None, None, str(exc)
        else:
            error = None
        attempts.append({"attempt": attempt, "httpStatus": status, "error": error})
        if status is not None and status < 400:
            if not data:
                return {"status": "missing", "reason": "no_data", "data": None, "attempts": attempts}
            return {"status": "ok", "reason": None, "data": data, "attempts": attempts}
        if status is not None and not ys.is_transient_status(status):
            return {"status": "missing", "reason": f"permanent_http_{status}", "data": None, "attempts": attempts}
        if attempt < MAX_ATTEMPTS:
            sleep(BACKOFF_S[min(attempt - 1, len(BACKOFF_S) - 1)])
    last = attempts[-1]
    reason = f"transient_http_{last['httpStatus']}" if last["httpStatus"] is not None else "transient_network_error"
    return {"status": "transient_failed", "reason": reason, "data": None, "attempts": attempts}


def fetch_for_videos(video_ids: list[str], *, token: str, channel_id: str, start: str, end: str,
                     sleep: Callable[[float], None] = time.sleep) -> list[dict]:
    rows = []
    for vid in video_ids:
        rows.append({
            "youtube_video_id": vid,
            "retention_curve": _fetch_with_retry(ys.fetch_retention_curve, token, channel_id, vid, start, end,
                                                 sleep=sleep),
            "traffic_sources": _fetch_with_retry(ys.fetch_traffic_sources, token, channel_id, vid, start, end,
                                                 sleep=sleep),
        })
    return rows


def build_output(rows: list[dict], *, channel_label: str, channel_id: str, start: str, end: str) -> dict:
    def count(kind):
        return {s: sum(1 for r in rows if r[kind]["status"] == s) for s in ("ok", "missing", "transient_failed")}
    return {
        "output_version": OUTPUT_VERSION,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "channel_label": channel_label,
        "channel_id": channel_id,
        "window": {"start": start, "end": end},
        "summary": {"videos": len(rows), "retention_curve": count("retention_curve"),
                    "traffic_sources": count("traffic_sources")},
        "videos": rows,
    }


def read_video_ids(path: Path) -> list[str]:
    text = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, list):
        ids = [str(x) for x in data]
    elif isinstance(data, dict) and isinstance(data.get("items"), list):
        ids = [str(i["youtube_video_id"]) for i in data["items"] if isinstance(i, dict) and i.get("youtube_video_id")]
    else:
        ids = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    return list(dict.fromkeys(ids))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lấy retention curve + traffic source vào baseline raw local.")
    ap.add_argument("--channel", required=True, help="label kênh trong .youtube_channels/")
    ap.add_argument("--video-ids-file", required=True)
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--end", default=date.today().isoformat())
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args(argv)

    from youtube_auth import get_valid_access_token, load_credentials
    creds_path = ys.CHANNELS_DIR / f"{args.channel}.json"
    channel_id = load_credentials(creds_path)["channel_id"]
    token = get_valid_access_token(creds_path)
    ys.verify_channel_identity(args.channel, token, channel_id)

    video_ids = read_video_ids(Path(args.video_ids_file))
    rows = fetch_for_videos(video_ids, token=token, channel_id=channel_id, start=args.start, end=args.end)
    out = build_output(rows, channel_label=args.channel, channel_id=channel_id, start=args.start, end=args.end)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"youtube_analytics_{args.channel}_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(rows)} video -> {path}")
    print(json.dumps(out["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
