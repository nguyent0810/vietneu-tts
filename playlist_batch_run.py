"""Batch: backfill 35 Short (tuần này) vào đúng playlist YouTube.

Áp toàn bộ sửa đổi theo Codex review #5 (2 vòng NEEDS_REVISION):
- Xác nhận credentials đúng channel_id trước khi ghi (không chỉ tin đường dẫn file).
- exact-title abort nếu >1 playlist trùng tên (AmbiguousPlaylistError).
- Playlist ĐÃ CÓ: pin thẳng playlist_id (không tra cứu lại theo tên khi ghi thật).
- Playlist MỚI: tạo privacy_status="private" (staging) -- publish "public" là bước RIÊNG
  (--mode publish-new), chỉ chạy sau khi đã verify đủ thành viên.
- Single-writer lock theo từng channel (fcntl.flock, chặn 2 process cùng ghi 1 channel).
- Checkpoint/journal theo content_id (JSON lines, resumable) -- content_id đã "done" ở
  lần chạy trước thì bỏ qua, không gọi lại API.
- Canary: xử lý 1 item đầu tiên của mỗi channel riêng, verify qua API xong mới chạy tiếp
  phần còn lại của channel đó (fail-fast nếu canary lỗi thay vì lặp lỗi 34 lần).
- pin_existing_playlist_ids() gọi list_playlists() đúng 1 LẦN/channel (không phải 1 lần/item).
- Reconcile-before-retry cho playlists.insert/playlistItems.insert nằm trong
  youtube_catalog.py (_create_playlist_with_reconcile/_add_video_with_reconcile) -- không
  blind-retry thao tác ghi không idempotent (vòng 2 Codex).

Trạng thái vận hành (lock/checkpoint/manifest playlist mới) lưu tại .playlist_ops/ trong
repo (gitignored) -- không dùng thư mục scratch của phiên làm việc, để Codex/người review
sau này đọc lại được trực tiếp trong workdir.

Chạy:
  python3 playlist_batch_run.py --mode dry-run          (mặc định, không ghi gì)
  python3 playlist_batch_run.py --mode live              (ghi thật, playlist mới = private)
  python3 playlist_batch_run.py --mode publish-new       (chỉ đổi playlist MỚI vừa tạo sang public)
"""
import argparse
import fcntl
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from youtube_catalog import (
    ensure_playlist_and_add, find_playlist_by_exact_title, get_own_channel_id,
    update_playlist_privacy, AmbiguousPlaylistError, YouTubeCatalogError,
)
from playlist_mapping import BUD_PLAYLIST, FS_MAPPING, CL_MAPPING

CREDS = {
    "BUD": str(PROJECT_ROOT / ".youtube_channels" / "phat_giao.json"),
    "FS": str(PROJECT_ROOT / ".youtube_channels" / "phong_thuy.json"),
    "CL": str(PROJECT_ROOT / ".youtube_channels" / "hinh_su.json"),
}
# Channel_id thật đã xác nhận qua load_credentials() trước đó trong phiên -- nếu
# get_own_channel_id() trả về khác giá trị này, ABORT ngay (Codex: "credentials phải
# thuộc đúng channel_id; title playlist không đủ để ngăn ghi nhầm kênh").
EXPECTED_CHANNEL_ID = {
    "BUD": "UCQRsHSC8dBcLvCvrj7CLvKA",
    "FS": "UCabOUyNfseJfu-Xy_KXz2rw",
    "CL": "UCegnaVpCsJ8souFka7s1URw",
}
OPS_DIR = PROJECT_ROOT / ".playlist_ops"
LOCK_DIR = OPS_DIR / "locks"
CHECKPOINT_PATH = OPS_DIR / "playlist_backfill_checkpoint.jsonl"
NEW_PLAYLISTS_PATH = OPS_DIR / "playlist_backfill_new_playlists.json"
DRY_RUN_LOG_PATH = OPS_DIR / "playlist_backfill_dry_run_manifest.json"


def load_ledger_items():
    ledger = json.loads((PROJECT_ROOT / "creator_specs" / "WEEKLY_PUBLISHING_LEDGER_v1.json").read_text(encoding="utf-8"))
    items = ledger["items"] if "items" in ledger else ledger
    if isinstance(items, dict):
        items = list(items.values())
    return items


def build_plan_list():
    plans = []
    for it in load_ledger_items():
        cid = it["content_id"]
        vid = it["youtube_video_id"]
        if cid.startswith("BUD_"):
            channel, title = "BUD", BUD_PLAYLIST
        elif cid.startswith("FS_"):
            channel, title = "FS", FS_MAPPING.get(cid)
        elif cid.startswith("CL_"):
            channel, title = "CL", CL_MAPPING.get(cid)
        else:
            channel, title = None, None
        if not title:
            plans.append({"content_id": cid, "channel": channel, "error": "NO_MAPPING"})
            continue
        plans.append({"content_id": cid, "channel": channel, "playlist_title": title, "video_id": vid})
    return plans


def load_checkpoint() -> dict:
    """Trả về {content_id: record CUỐI CÙNG} cho MỌI content_id đã từng
    checkpoint (kể cả ERROR) -- nhưng chỉ record status="OK" mới được
    coi là "done" (bỏ qua khi resume). BUG THẬT phát hiện khi chạy live
    lần đầu (xem phiên làm việc): bản gốc coi TẤT CẢ record (kể cả
    ERROR) là "done", khiến item lỗi bị bỏ qua vĩnh viễn thay vì được
    retry ở lần chạy sau -- run_channel() phải tự lọc theo status."""
    records = {}
    if CHECKPOINT_PATH.exists():
        for line in CHECKPOINT_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            records[rec["content_id"]] = rec
    return records


def append_checkpoint(rec: dict) -> None:
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    with CHECKPOINT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class ChannelLock:
    """File lock theo TỪNG channel (fcntl.flock, non-blocking) -- chặn 2
    process cùng ghi 1 channel đồng thời (Codex review #5: race condition
    find->create / list->insert không nguyên tử -- giải pháp thực tế cho
    job 1 lần là single-writer lock, không cần hạ tầng phân tán)."""

    def __init__(self, channel: str):
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
        self.path = LOCK_DIR / f"{channel}.lock"
        self.fh = None

    def __enter__(self):
        self.fh = open(self.path, "w")
        try:
            fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(
                f"Channel lock '{self.path}' đang bị giữ bởi process khác -- "
                f"có process ghi playlist khác đang chạy đồng thời, dừng lại để tránh race condition."
            )
        return self

    def __exit__(self, *exc):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


def verify_channel_identity(channel: str) -> None:
    creds_path = CREDS[channel]
    real_id = get_own_channel_id(creds_path)
    expected = EXPECTED_CHANNEL_ID[channel]
    if real_id != expected:
        raise RuntimeError(
            f"KHÔNG KHỚP channel_id cho '{channel}': credentials={creds_path} trả về "
            f"channel_id thật={real_id}, nhưng mong đợi={expected}. ABORT -- không ghi "
            f"nhầm dữ liệu sang kênh khác."
        )


def pin_existing_playlist_ids(channel: str, titles: set) -> dict:
    """Tra cứu 1 LẦN cho mỗi title CHƯA BIẾT trong channel này -- trả về
    {title: playlist_id hoặc None nếu chưa tồn tại (sẽ cần tạo)}. Abort
    nếu 1 title khớp CHÍNH XÁC >1 playlist (AmbiguousPlaylistError, không
    tự chọn cái đầu tiên)."""
    pinned = {}
    for title in titles:
        matches = find_playlist_by_exact_title(CREDS[channel], title)
        if len(matches) > 1:
            raise AmbiguousPlaylistError(
                f"[{channel}] '{title}' khớp CHÍNH XÁC {len(matches)} playlist "
                f"(ids={[m['id'] for m in matches]}) -- cần giải quyết thủ công trước khi ghi."
            )
        pinned[title] = matches[0]["id"] if matches else None
    return pinned


def run_channel(channel: str, items: list, mode: str, done: dict, new_playlists: dict) -> list:
    results = []
    with ChannelLock(channel):
        verify_channel_identity(channel)
        print(f"[{channel}] channel_id xác nhận khớp -- bắt đầu xử lý {len(items)} item (mode={mode}).", flush=True)

        pending = [it for it in items if done.get(it["content_id"], {}).get("status") != "OK"]
        skipped_ct = len(items) - len(pending)
        if skipped_ct:
            print(f"[{channel}] bỏ qua {skipped_ct} item đã checkpoint 'done' từ lần chạy trước.", flush=True)
        if not pending:
            return results

        titles_needed = {it["playlist_title"] for it in pending}
        pinned_ids = pin_existing_playlist_ids(channel, titles_needed)

        # Canary: xử lý item ĐẦU TIÊN riêng, verify xong mới chạy tiếp phần còn lại.
        canary, rest = pending[0], pending[1:]
        for idx, it in enumerate([canary] + rest):
            label = "CANARY" if idx == 0 else f"{idx}/{len(pending) - 1}"
            hint = pinned_ids.get(it["playlist_title"])
            try:
                plan = ensure_playlist_and_add(
                    CREDS[channel], it["playlist_title"], it["video_id"],
                    privacy_status="private", dry_run=(mode == "dry-run"),
                    playlist_id_hint=hint,
                )
            except (YouTubeCatalogError, AmbiguousPlaylistError) as exc:
                rec = {"content_id": it["content_id"], "channel": channel, "status": "ERROR", "error": str(exc)}
                if mode != "dry-run":
                    append_checkpoint(rec)
                results.append(rec)
                print(f"[{channel}] {label} content_id={it['content_id']} LỖI: {exc}", flush=True)
                if idx == 0:
                    raise RuntimeError(f"[{channel}] Canary item thất bại -- dừng lại, KHÔNG chạy tiếp phần còn lại của channel này.") from exc
                continue

            if mode != "dry-run" and plan.get("will_create_playlist") and plan["playlist_id"] not in pinned_ids.values():
                pinned_ids[it["playlist_title"]] = plan["playlist_id"]
                new_playlists.setdefault(channel, {})[it["playlist_title"]] = plan["playlist_id"]

            rec = {"content_id": it["content_id"], "channel": channel, "status": "OK", "plan": plan}
            if mode != "dry-run":
                append_checkpoint(rec)
            results.append(rec)
            print(f"[{channel}] {label} content_id={it['content_id']} -> {plan.get('action')} (playlist={plan['playlist_id']})", flush=True)
    return results


def cmd_publish_new(dry_run: bool) -> None:
    if not NEW_PLAYLISTS_PATH.exists():
        print("Chưa có playlist mới nào được tạo (playlist_backfill_new_playlists.json không tồn tại).")
        return
    new_playlists = json.loads(NEW_PLAYLISTS_PATH.read_text(encoding="utf-8"))
    for channel, title_to_id in new_playlists.items():
        with ChannelLock(channel):
            verify_channel_identity(channel)
            for title, playlist_id in title_to_id.items():
                if dry_run:
                    print(f"[{channel}] SẼ publish (private->public): '{title}' ({playlist_id})")
                    continue
                result = update_playlist_privacy(CREDS[channel], playlist_id, "public", title)
                print(f"[{channel}] Đã publish '{title}' ({playlist_id}) -> {result['privacy_status']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dry-run", "live", "publish-new"], default="dry-run")
    args = ap.parse_args()

    if args.mode == "publish-new":
        cmd_publish_new(dry_run=False)
        return 0

    plans = build_plan_list()
    errors = [p for p in plans if p.get("error")]
    if errors:
        print(f"LỖI mapping thiếu cho {len(errors)} content_id: {[e['content_id'] for e in errors]}", file=sys.stderr)
        return 1

    by_channel = {}
    for p in plans:
        by_channel.setdefault(p["channel"], []).append(p)

    done = load_checkpoint() if args.mode == "live" else {}
    new_playlists = json.loads(NEW_PLAYLISTS_PATH.read_text(encoding="utf-8")) if NEW_PLAYLISTS_PATH.exists() else {}

    all_results = []
    try:
        for channel, items in by_channel.items():
            all_results.extend(run_channel(channel, items, args.mode, done, new_playlists))
    finally:
        if args.mode == "live" and new_playlists:
            OPS_DIR.mkdir(parents=True, exist_ok=True)
            NEW_PLAYLISTS_PATH.write_text(json.dumps(new_playlists, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = [r for r in all_results if r["status"] == "OK"]
    err = [r for r in all_results if r["status"] == "ERROR"]
    summary = f"TỔNG KẾT (mode={args.mode}): {len(ok)} OK, {len(err)} LỖI, {len(plans) - len(all_results)} bỏ qua (đã checkpoint)"
    print(f"\n=== {summary} ===")

    if args.mode == "dry-run":
        OPS_DIR.mkdir(parents=True, exist_ok=True)
        DRY_RUN_LOG_PATH.write_text(json.dumps(
            {"summary": summary, "results": all_results}, ensure_ascii=False, indent=2,
        ), encoding="utf-8")
        print(f"Đã lưu manifest dry-run vào {DRY_RUN_LOG_PATH} (để kiểm chứng độc lập).")

    if err:
        for e in err:
            print(f"  LỖI {e['content_id']}: {e['error']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
