"""Tự dọn file sinh ra của pipeline HyperFrames (kênh Phật Giáo + Phong Thủy) để ổ đĩa không phình.

Bốn nhóm, mỗi nhóm một luật an toàn riêng:
  1. Video ĐÃ ĐĂNG (shorts bud/fs + long): chỉ dọn khi id có trong uploaded.json VÀ YouTube xác nhận
     uploadStatus = processed, đúng kênh, đã công khai hoặc đã hẹn giờ. Dọn: .mp4 / .wav / thư mục _chapters.
     GIỮ: json, srt, txt (mục lục, phụ đề tải tay, kịch bản -- vài KB).
     Video riêng tư KHÔNG hẹn giờ (bản bị rút lại chờ sửa) -> bỏ qua, chỉ báo.
  2. Ảnh/clip tạm của mỗi lần render (hyperframes_short/assets, tên dạng <stem>_s<n>.* / _v<n>_bg...):
     render nào cũng tự chép lại -> dọn file không đụng tới quá 2 ngày.
  3. Cache giọng đọc từng câu (chunks_cache/voice_lines): hf_voice đánh dấu lần dùng -> dọn file > 30 ngày không dùng.
  4. Cache ảnh/clip stock (chunks_cache/beat_assets): bridge đánh dấu lần dùng -> dọn file > 45 ngày không dùng.
KHÔNG đụng: kênh Hình Sự (hyperframes_oct/sept, reel, *_video.mp4 rời), registry/ledger, video chưa đăng.

Chế độ: mặc định chỉ liệt kê (dry-run). --apply: chuyển vào Thùng rác (~/.Trash/vieneu_tu_don/<ngày>/)
-- dung lượng chỉ trả lại khi Thùng rác được dọn. --apply --delete: xoá hẳn.

  python hf_cleanup.py                   # xem sẽ dọn gì
  python hf_cleanup.py --apply           # dọn (vào Thùng rác)
  python hf_cleanup.py --apply --delete  # dọn hẳn
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
STAGING = ROOT / "output" / "cl_staging"
LANES = {  # thư mục -> credentials được phép xác nhận (chỉ BUD/FS)
    "bud": [".youtube_channels/phat_giao.json"],
    "fs": [".youtube_channels/phong_thuy.json"],
    "long": [".youtube_channels/phat_giao.json", ".youtube_channels/phong_thuy.json"],
}
HEAVY_SUFFIXES = (".mp4", ".wav", ".mov", ".webm")
HF_ASSETS = ROOT / "hyperframes_short" / "assets"
HF_ASSET_RE = re.compile(r"_(s\d+|v\d+_(bg|fg|sketch)|s\d+_(bg|fg))\.(jpg|jpeg|png|webp|mp4|webm|mov)$")
VOICE_CACHE = ROOT / "chunks_cache" / "voice_lines"
STOCK_CACHE = ROOT / "chunks_cache" / "beat_assets"
DAYS = {"hf_assets": 2, "voice": 30, "stock": 45}
LOG = ROOT / "output" / "cleanup_log.jsonl"


def size_of(p: Path) -> int:
    if p.is_dir():
        return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    return p.stat().st_size if p.exists() else 0


def heavy_artifacts(out: Path, rid: str) -> list[Path]:
    """Chỉ file nặng của ĐÚNG id này (không glob tiền tố -- f39_a không được kéo theo f39_ab)."""
    found = [out / f"{rid}{s}" for s in HEAVY_SUFFIXES if (out / f"{rid}{s}").exists()]
    if (out / f"{rid}_chapters").is_dir():
        found.append(out / f"{rid}_chapters")
    return found


def youtube_status(video_ids: list[str], creds_list: list[str]) -> dict[str, dict]:
    """{video_id: {processed, channel_ok, live_or_scheduled, privacy}} -- hỏi bằng creds của chính kênh."""
    import hf_coverage as H  # noqa: PLC0415
    get, channels_url, _, videos_url = H._api()
    res: dict[str, dict] = {}
    for creds in creds_list:
        me = get(creds, channels_url, {"part": "id", "mine": "true"})["items"][0]["id"]
        for i in range(0, len(video_ids), 50):
            d = get(creds, videos_url, {"part": "status,snippet", "id": ",".join(video_ids[i:i + 50])})
            for v in d.get("items", []):
                st = v["status"]
                if v["snippet"].get("channelId") != me:
                    continue
                res[v["id"]] = {"processed": st.get("uploadStatus") == "processed", "privacy": st.get("privacyStatus"),
                                "live_or_scheduled": st.get("privacyStatus") in ("public", "unlisted") or bool(st.get("publishAt"))}
    return res


def published_candidates() -> tuple[list[tuple[Path, str]], list[str]]:
    todo, notes = [], []
    for lane, creds in LANES.items():
        ledger_f, out = STAGING / lane / "uploaded.json", STAGING / lane / "out"
        if not ledger_f.exists() or not out.is_dir():
            continue
        ledger = json.loads(ledger_f.read_text(encoding="utf-8"))
        have = {rid: vid for rid, vid in ledger.items() if vid and heavy_artifacts(out, rid)}
        if not have:
            continue
        st = youtube_status(sorted(set(have.values())), creds)
        for rid, vid in sorted(have.items()):
            s = st.get(vid)
            if not s:
                notes.append(f"{lane}/{rid}: không thấy {vid} trên kênh -- giữ nguyên")
            elif not s["processed"]:
                notes.append(f"{lane}/{rid}: YouTube chưa xử lý xong -- giữ nguyên")
            elif not s["live_or_scheduled"]:
                notes.append(f"{lane}/{rid}: riêng tư, không hẹn giờ (bản rút lại?) -- giữ nguyên")
            else:
                todo += [(p, f"{lane}/{rid} đã đăng") for p in heavy_artifacts(out, rid)]
    return todo, notes


def stale(folder: Path, days: int, pattern: re.Pattern | None = None) -> list[Path]:
    if not folder.is_dir():
        return []
    cut = time.time() - days * 86400
    return [f for f in folder.iterdir() if f.is_file() and f.stat().st_mtime < cut and (pattern is None or pattern.search(f.name))]


def plan() -> tuple[list[tuple[Path, str]], list[str]]:
    todo, notes = published_candidates()
    todo += [(f, f"asset render > {DAYS['hf_assets']} ngày") for f in stale(HF_ASSETS, DAYS["hf_assets"], HF_ASSET_RE)]
    todo += [(f, f"cache giọng > {DAYS['voice']} ngày không dùng") for f in stale(VOICE_CACHE, DAYS["voice"])]
    todo += [(f, f"cache stock > {DAYS['stock']} ngày không dùng") for f in stale(STOCK_CACHE, DAYS["stock"])]
    return todo, notes


def apply(todo: list[tuple[Path, str]], delete: bool) -> int:
    bin_ = Path.home() / ".Trash" / "vieneu_tu_don" / dt.date.today().isoformat()
    freed = 0
    for p, _why in todo:
        n = size_of(p)
        if delete:
            shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
        else:
            dst = bin_ / p.relative_to(ROOT)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dst))
        freed += n
    return freed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="Dọn thật (mặc định chỉ liệt kê)")
    ap.add_argument("--delete", action="store_true", help="Cùng --apply: xoá hẳn thay vì chuyển vào Thùng rác")
    a = ap.parse_args(argv)
    todo, notes = plan()
    total = sum(size_of(p) for p, _ in todo)
    groups: dict[str, list[int]] = {}
    for p, why in todo:
        key = why.split(" ", 1)[1] if "/" in why.split(" ", 1)[0] else why
        g = groups.setdefault(key, [0, 0]); g[0] += 1; g[1] += size_of(p)
    for k, (n, b) in sorted(groups.items(), key=lambda x: -x[1][1]):
        print(f"  {k}: {n} mục, {b / 1e9:.2f} GB")
    for n in notes:
        print("  (giữ) " + n)
    print(f"Tổng: {len(todo)} mục, {total / 1e9:.2f} GB" + ("" if a.apply else " -- chỉ liệt kê, chưa dọn"))
    if a.apply and todo:
        freed = apply(todo, a.delete)
        mode = "xoá hẳn" if a.delete else "vào Thùng rác"
        print(f"Đã dọn {freed / 1e9:.2f} GB ({mode})")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"at": dt.datetime.now().isoformat(timespec="seconds"), "items": len(todo), "bytes": freed,
                                "mode": "delete" if a.delete else "trash", "notes": notes}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
