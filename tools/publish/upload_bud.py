"""Đăng loạt short ngày 1 lên kênh Phật giáo: private + hẹn giờ.

Cùng khuôn với upload_oct.py của kênh Hình Sự, khác ba chỗ: credential của
kênh Phật giáo, lời miễn trừ riêng, và phần GHI CÔNG NGUỒN ẢNH -- loạt này
là loạt đầu dùng ảnh/clip Pexels nên mô tả phải dẫn nguồn.

Mặc định DRY-RUN. Đăng thật: python3 upload_bud.py --confirm
Chạy lại an toàn: mục nào đã đăng được ghi vào uploaded.json và bỏ qua.
"""
import argparse, glob, json, os, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
from short_upload import upload_short
from youtube_upload import QuotaExceededError

# YouTube từ chối publishAt đã qua; sát quá thì video có thể lên trước khi
# kịp xử lý xong. Khung nào gần hơn mức này thì để lại, không đăng.
MIN_LEAD = timedelta(minutes=20)
MAX_AHEAD_DAYS = 7
# 22/10: người dùng bảo "khoan" -- tắt chặn cuốn chiếu tới khi phân tích xong tỉ lệ thắng/thua dạng mới. Bật lại = True.
ROLLING_GUARD = False


def is_too_far(
    r: dict,
    when: datetime | str | None = None,
    now: datetime | None = None,
    max_ahead_days: int = MAX_AHEAD_DAYS,
) -> bool:
    """Kiểm tra khung publish_at có vượt quá ngưỡng cuốn chiếu (MAX_AHEAD_DAYS = 7 ngày) không.

    Ngoại lệ:
    - lane 'ngaytot': bài cưới hỏi cần đăng trước 3–5 tháng.
    - bài có 'allow_far': True trong plan.
    """
    if isinstance(r, (datetime, str)) and isinstance(when, dict):
        r, when = when, r
    if str(r.get("lane") or "").strip().lower() == "ngaytot" or bool(r.get("allow_far")):
        return False
    if when is None:
        if "publish_at" in r:
            pub = r["publish_at"]
        else:
            pub = f"{r['day']}T{r['slot']}:00Z"
        when = datetime.fromisoformat(pub.replace("Z", "+00:00"))
    elif isinstance(when, str):
        when = datetime.fromisoformat(when.replace("Z", "+00:00"))
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when - now > timedelta(days=max_ahead_days)


should_skip_far = is_too_far

HERE = ROOT / "output/cl_staging/bud"
OUT = HERE / "out"
LEDGER = HERE / "uploaded.json"
CREDS = ".youtube_channels/phat_giao.json"

BGM_CC = ('Nhạc nền: "Meditation Impromptu 01" by Kevin MacLeod (incompetech.com), '
          "licensed under Creative Commons: By Attribution 4.0 License "
          "(http://creativecommons.org/licenses/by/4.0/)")
def music_cc(rid: str) -> str:
    """Ghi nguồn ĐÚNG bài đã trộn (render.json): từ lịch 18/11 mỗi short một bài (hf_music.short_pick)."""
    f = OUT / f"{rid}.render.json"
    bgm = (json.loads(f.read_text(encoding="utf-8")).get("bgm") if f.exists() else "") or ""
    if not bgm:
        return BGM_CC
    import hf_music
    return hf_music.credit([bgm])  # KeyError = bài chưa có trong danh mục ghi nguồn -> dừng, không đăng thiếu


DISCLAIMER = ("Nội dung suy ngẫm, không thay cho việc học Phật pháp trực tiếp "
              "với thầy và tăng đoàn.")


def credits_for(rid: str) -> str:
    """Ghi công đọc từ kết quả render, không dựng lại. Pexels không bắt buộc
    ghi công, nhưng kênh công khai thì nên."""
    f = OUT / f"{rid}.render.json"
    if not f.exists():
        return ""
    try:
        lines = json.loads(f.read_text(encoding="utf-8")).get("media_credits") or []
    except (OSError, json.JSONDecodeError):
        return ""
    seen, uniq = set(), []
    for c in lines:
        if isinstance(c, dict):   # render mới ghi {credit, license, ...}; CC BY bắt buộc ghi công
            c = c.get("credit") or ""
        if c and c not in seen:
            seen.add(c); uniq.append(c)
    return "Hình ảnh trong video:\n" + "\n".join(uniq) if uniq else ""


HASHTAGS = ["#Shorts", "#phậtpháp", "#lờiphậtdạy"]
CTA = "Bạn đã từng gặp chuyện này chưa? Kể mình nghe ở phần bình luận nhé."


def description(r: dict) -> str:
    # Short v2 (04/10/2026): dòng đầu = câu trả lời một câu + hashtag có dấu (kiểu bài nguồn ngoài có
    # lượt đăng ký/1k view gấp đôi), thêm lời mời bình luận. Row cũ không có `insight` giữ khuôn cũ.
    if r.get("insight"):
        tags = r.get("hashtags") or HASHTAGS
        parts = [r["insight"] + " " + " ".join(tags), r.get("cta") or CTA]
    else:
        parts = [r["title"]]
    if r.get("source"):
        parts.append(r["source"])
    parts.append(DISCLAIMER)
    if (c := credits_for(r["id"])):
        parts.append(c)
    parts.append(music_cc(r["id"]))
    if not r.get("insight"):
        parts.append("#Shorts")
    # YouTube từ chối mô tả có < > (400 invalidDescription, lô thay 26/10: "->" trong dòng nguồn làm trống khung vài phút).
    return "\n\n".join(parts).replace("->", "→").replace("<", "‹").replace(">", "›")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true", help="Đăng thật (mặc định chỉ in kế hoạch)")
    ap.add_argument("--day", default=None, help="Chỉ đăng 1 ngày, vd 2026-09-29")
    ap.add_argument("--only", default=None, help="Chỉ đăng các id liệt kê, cách nhau bằng dấu phẩy")
    ap.add_argument("--playlist", action="store_true", help="Tự thêm video vào playlist theo lane (mặc định tắt)")
    args = ap.parse_args()

    rows = []
    for f in sorted(glob.glob(str(HERE / "plan_*.json"))):
        rows += json.loads(Path(f).read_text(encoding="utf-8"))
    # 03/11: đóng gói Lead điền nằm ở packaging/<id>.json (builder sinh lại plan làm mất); trường sidecar thắng.
    for r in rows:
        side = HERE / "packaging" / f"{r['id']}.json"
        if side.exists():
            r.update(json.loads(side.read_text(encoding="utf-8")))
    if args.day:
        # Nhiều ngày một lần chạy (vd 2026-10-29,2026-10-30): dò khung giờ (search.list,
        # 100 lượt/ngày) chỉ một lần thay vì mỗi ngày một lần.
        days = set(args.day.split(","))
        rows = [r for r in rows if r["day"] in days]
    if args.only:
        want = set(args.only.split(","))
        rows = [r for r in rows if r["id"] in want]
    rows.sort(key=lambda r: (r["day"], r["slot"]))

    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
    # Bài đã đăng thì mp4 đã được dọn khỏi out/ -- chỉ xét bài chưa đăng.
    missing = [r["id"] for r in rows if r["id"] not in ledger and not (OUT / f"{r['id']}.mp4").exists()]
    if missing:
        print(f"THIẾU {len(missing)} video chưa render: {', '.join(missing)}", file=sys.stderr)
        if args.confirm:
            return 1

    # Dò sâu MỌI khung đã có video trên kênh (kể cả video riêng tư của nguồn
    # đăng khác mà playlist bỏ sót) -- không đăng chồng lên khung nào.
    import hf_coverage
    taken = hf_coverage.occupied_slots(CREDS)
    mine_ids = set(ledger.values())
    print(f"  (đã dò {len(taken)} khung đang có video trên kênh)")

    n = 0
    would_post = 0
    for r in rows:
        from library.tools.lib import enforce_lane
        enforce_lane("bud", r.get("lane"))
        if r["id"] in ledger:
            print(f"  (đã đăng) {r['id']} -> {ledger[r['id']]}")
            continue
        mp4 = OUT / f"{r['id']}.mp4"
        publish_at = f"{r['day']}T{r['slot']}:00Z"
        when = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
        if publish_at[:16] in taken:
            print(f"  (bỏ qua) {r['id']} {publish_at} -- khung này ĐÃ CÓ video trên kênh")
            continue
        if when - datetime.now(timezone.utc) < MIN_LEAD:
            print(f"  (bỏ qua) {r['id']} {publish_at} -- khung giờ đã qua hoặc quá sát")
            continue
        if ROLLING_GUARD and is_too_far(r, when):
            print(f"  (bỏ qua) {r['id']} {publish_at} -- BỎ QUA (quá 7 ngày)")
            continue
        size = mp4.stat().st_size / 1e6 if mp4.exists() else 0
        print(f'{"ĐĂNG " if args.confirm else "[DRY]"} {publish_at} | {r["style"]:11s} | '
              f'{size:5.1f}MB | {r["title"]}')
        playlist = None
        if args.playlist:
            sys.path.insert(0, str(ROOT / "tools/publish"))
            from playlist_apply import playlist_for_row
            playlist = playlist_for_row("bud", r)
            print(f"       playlist: {playlist['title'] if playlist else '(chưa ánh xạ lane)'}")
        would_post += 1
        if not args.confirm:
            continue
        try:
            vid = upload_short(str(mp4), r["title"], description(r), r["tags"] + r.get("tags_vi", []), publish_at, CREDS, language="vi", channel="bud", lane=r.get("lane"))
        except QuotaExceededError:
            left = [x["id"] for x in rows if x["id"] not in ledger]
            print(f"\nHẾT QUOTA YouTube hôm nay -- dừng. Còn {len(left)} bài chờ: {', '.join(left)}")
            print("Quota reset lúc 00:00 giờ Thái Bình Dương; chạy lại lệnh này là đăng tiếp.")
            return 2
        ledger[r["id"]] = vid
        LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"   -> https://youtu.be/{vid}", flush=True)
        if playlist:
            from youtube_catalog import ensure_playlist_and_add
            ensure_playlist_and_add(CREDS, playlist["title"], vid, privacy_status="public", dry_run=False)
        n += 1
        time.sleep(2)
    print(f"\n{'Đã đăng' if args.confirm else 'Sẽ đăng'} {n if args.confirm else would_post} video.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
