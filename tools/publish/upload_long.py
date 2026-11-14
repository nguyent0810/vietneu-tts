"""Đăng video dài (HyperFrames, khổ 16:9) cho kênh Phật giáo và Phong Thuỷ.

Khác uploader short ở ba chỗ:
  * MỤC LỤC CHƯƠNG trong mô tả, lấy từ thời điểm thật của câu tiêu đề chương
    (câu in đậm trọn câu trong kịch bản). YouTube hiện thành chapter khi có
    >= 3 mốc, mốc đầu là 0:00, mỗi chương >= 10 giây.
  * Gắn thumbnail tuỳ chỉnh (short không có).
  * Mỗi kênh một bộ credential, lời miễn trừ, dòng ghi nguồn nhạc.

Dò sâu mọi khung giờ trước khi đăng (hf_coverage.occupied_slots) -- không đăng
chồng lên video nào đã hẹn giờ, kể cả của nguồn đăng khác.

Mặc định DRY-RUN. Đăng thật: python3 upload_long.py --confirm
"""
import argparse, glob, json, os, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
from youtube_upload import QuotaExceededError, VideoMetadata, upload_video, upload_thumbnail
import hf_coverage

HERE = ROOT / "output/cl_staging/long"
OUT = HERE / "out"
LEDGER = HERE / "uploaded.json"
MIN_LEAD = timedelta(minutes=20)
CHANNEL = {
    "bud": {"creds": ".youtube_channels/phat_giao.json",
            "disclaimer": "Nội dung suy ngẫm, không thay cho việc học Phật pháp trực tiếp với thầy và tăng đoàn.",
            "hashtags": "#LoiPhatDay #PhatPhap #ChuaLanh"},
    "fs": {"creds": ".youtube_channels/phong_thuy.json",
           "disclaimer": "Kiến thức truyền thống, để tham khảo — không phải kết luận khoa học.",
           "hashtags": "#12ConGiap #PhamThaiTue #PhongThuy"},
}
MUSIC = {  # tên file -> tên gốc bắt buộc ghi theo CC BY 4.0 (bgm/LICENSE.txt)
    "meditation_impromptu_01.mp3": "Meditation Impromptu 01",
    "meditation_impromptu_02.mp3": "Meditation Impromptu 02",
    "meditation_impromptu_03.mp3": "Meditation Impromptu 03",
    "comfortable_mystery_4.mp3": "Comfortable Mystery 4",
    "thinking_music.mp3": "Thinking Music",
    "deliberate_thought.mp3": "Deliberate Thought",
    "asian_drums.mp3": "Asian Drums",
}


def music_line(row: dict) -> str:
    """Ghi nguồn ĐÚNG track đã trộn vào video -- lấy từ kết quả render (runner
    chọn track theo pool), không từ plan: mục video dài có thể không ghi bgm."""
    f = OUT / f"{row['id']}.render.json"
    meta = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    # Nền nhạc theo chương phát nhiều bài -> ghi nguồn ĐỦ mọi bài đã vang lên (bgm_used, từ 04/10/2026).
    used = meta.get("bgm_used") or [meta.get("bgm") or row.get("bgm", "")]
    import hf_music
    return hf_music.credit(used)  # KeyError = track chưa có trong danh mục ghi nguồn -> dừng, không đăng thiếu


def ts(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


def chapters(row: dict) -> list[str]:
    m = json.loads((OUT / f"{row['id']}.json").read_text(encoding="utf-8"))
    segs = m.get("segments") or m.get("lines")
    out = ["0:00 Mở đầu"]
    for s, seg in zip(row["script"], segs):
        t = s.strip()
        if t.startswith("**") and t.endswith("**") and t.count("**") == 2:
            out.append(f"{ts(seg['start'])} {t.strip('*').rstrip('.')}")
    # Kịch bản mở bằng tiêu đề chương (F4): chương ấy đã ở 0:00 -> bỏ "Mở đầu", hai mốc 0:00 làm YouTube bỏ cả mục lục.
    if len(out) > 1 and out[1].startswith("0:0"):
        out.pop(0)
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out


def credits(rid: str, compact: bool = False) -> str:
    """Ghi công gọn (mô tả chỉ 5000 byte): tư liệu Commons theo tên ngắn + giấy phép, ảnh Pexels theo tên
    tác giả (giấy phép Pexels không bắt buộc ghi, ghi tên là lịch sự). Không bỏ sót nguồn nào."""
    import re as _re
    f = OUT / f"{rid}.render.json"
    if not f.exists():
        return ""
    commons, pexels, other, openv = {}, [], [], []
    authors: dict[str, list[str]] = {}       # bản gọn: giấy phép -> tác giả (CC BY/BY-SA bắt buộc ghi tác giả)
    for c in dict.fromkeys(json.loads(f.read_text(encoding="utf-8")).get("media_credits") or []):
        if not c:
            continue
        if c.endswith("Wikimedia Commons"):
            name, _, rest = c.partition(" — ")
            lic = rest.rsplit(", ", 2)[-2] if rest.count(", ") >= 1 else rest
            short = _re.sub(r"\.(jpe?g|png|tiff?)$", "", name, flags=_re.I)
            short = _re.sub(r",? (schist|DSC\d+|BM OA[\d.\-]+).*$", "", short)[:60].strip(" ,-")
            commons.setdefault(lic, []).append(short)
            who = rest.rsplit(", ", 2)[0].strip() if rest.count(", ") >= 2 else ""
            if who and who != lic:
                authors.setdefault(lic, []).append(who[:40])
        elif c.endswith(" via Openverse"):
            body = c.split(" — ", 1)[-1].replace(" via Openverse", "")
            openv.append(body)
        elif (m := _re.match(r"Ảnh: (.+?) — Pexels", c)):
            pexels.append(m.group(1).strip())
        else:
            other.append(c)
    def _series(names: list[str]) -> list[str]:
        """Gộp loạt ảnh cùng tên gốc: "Old Quarter, Hanoi (25) (3760...)", "(12) (...)" -> "Old Quarter, Hanoi (25, 12)"."""
        groups: dict[str, list[tuple[str, str]]] = {}
        for n in dict.fromkeys(names):
            m = _re.match(r"^(.*?)(?:[\s\-]*\(?(?:CN-)?(?<!\d)(\d{1,3})\)?)?(?: \((\d{6,})\))?$", n)
            groups.setdefault(m.group(1).strip(" ,-"), []).append((n, m.group(2) or ""))
        out = []
        for k, items in groups.items():
            nums = [x for _, x in items if x]
            if len(items) == 1:
                out.append(items[0][0])
            elif len(nums) == len(items):
                out.append(f"{k} ({', '.join(nums)})")
            else:                                  # loạt ảnh chỉ khác mã số Flickr
                out.append(f"{k} ({len(items)} ảnh)")
        return out

    parts = []
    for lic, names in commons.items():
        if compact:   # mô tả quá 5000 byte (tập 50+ phút, hàng trăm tư liệu): số tư liệu + tác giả theo giấy phép
            who = list(dict.fromkeys(authors.get(lic, [])))
            parts.append(f"Tư liệu Wikimedia Commons ({lic}): {len(set(names))} tư liệu" + (" -- tác giả: " + ", ".join(who[:25]) if who else ""))
        else:
            parts.append(f"Tư liệu Wikimedia Commons ({lic}): " + "; ".join(_series(names)))
    if openv:
        parts.append("Ảnh giấy phép mở qua Openverse: " + "; ".join(dict.fromkeys(openv)))
    if pexels:
        parts.append("Ảnh Pexels: " + ", ".join(dict.fromkeys(pexels)))
    if compact:
        parts += [c.split(" — ")[-1][:160] for c in dict.fromkeys(other)]
        parts.append("Tác giả, giấy phép của từng tư liệu ghi ngay trên khung hình.")
    else:
        parts += other
    return "Hình ảnh trong video:\n" + "\n".join(parts) if parts else ""


def description(row: dict) -> str:
    """SEO (học từ V2 motion/long/describe.py): 2 dòng đầu chứa từ khoá (YouTube chỉ hiện chừng ấy
    trước "xem thêm"), mục lục chương, phần tóm tắt giá trị (bảng 12 tuổi...), link xem tiếp, nguồn.
    YouTube giới hạn mô tả 5000 BYTE (tiếng Việt có dấu tốn 2-3 byte/ký tự) -> kiểm cứng."""
    ch = CHANNEL[row["series"]]
    seo = row.get("seo") or {}
    hook = "\n".join(seo["hook"]) if seo.get("hook") else " ".join(s.replace("**", "") for s in row["script"][:3])
    parts = [hook if seo.get("hook") else row["title"]]
    if not seo.get("hook"):
        parts.append(hook)
    parts.append("Mục lục:\n" + "\n".join(chapters(row)))
    if seo.get("summary"):
        parts.append(seo["summary"])
    if seo.get("more"):
        parts.append("Xem tiếp:\n" + "\n".join(seo["more"]))
    parts.append(ch["disclaimer"])
    if (c := credits(row["id"])):
        parts.append(c)
    parts.append(music_line(row))
    parts.append(seo.get("hashtags") or ch["hashtags"])
    out = "\n\n".join(parts)
    if len(out.encode("utf-8")) > 5000 and c:      # thử bản ghi nguồn gọn trước khi dừng
        parts[parts.index(c)] = credits(row["id"], compact=True)
        out = "\n\n".join(parts)
    if len(out.encode("utf-8")) > 5000:
        raise SystemExit(f"Mô tả {row['id']} dài {len(out.encode('utf-8'))} byte > 5000 -- rút gọn seo.summary/credits")
    return out


def srt(row: dict) -> str:
    """Phụ đề tiếng Việt từ mốc từng câu của TTS: câu dài cắt ở dấu phẩy / ~12 chữ, chia giờ theo số ký tự."""
    import re as _re
    m = json.loads((OUT / f"{row['id']}.json").read_text(encoding="utf-8"))
    cues = []
    for text, seg in zip(row["script"], m["segments"]):
        t = text.replace("**", "").strip()
        parts, cur = [], []
        for w in t.split():
            cur.append(w)
            if (_re.search(r"[,.;:?!]$", w) and len(cur) >= 5) or len(cur) >= 12:
                parts.append(" ".join(cur)); cur = []
        if cur:
            parts.append(" ".join(cur))
        total = sum(len(x) for x in parts) or 1
        t0, dur = float(seg["start"]), float(seg["end"]) - float(seg["start"])
        for x in parts:
            d = dur * len(x) / total
            cues.append((t0, t0 + d, x)); t0 += d

    def stamp(sec):
        ms = int(round(sec * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{i}\n{stamp(a)} --> {stamp(b)}\n{x}\n" for i, (a, b, x) in enumerate(cues, 1))


def upload_captions(vid: str, row: dict, creds: str) -> None:
    import urllib.request, uuid  # noqa: E401
    from youtube_auth import get_valid_access_token
    body_srt = srt(row).encode("utf-8")
    meta = json.dumps({"snippet": {"videoId": vid, "language": "vi", "name": "Tiếng Việt", "isDraft": False}}).encode()
    bnd = uuid.uuid4().hex
    body = (f"--{bnd}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode() + meta +
            f"\r\n--{bnd}\r\nContent-Type: application/x-subrip\r\n\r\n".encode() + body_srt + f"\r\n--{bnd}--".encode())
    req = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/captions?part=snippet&uploadType=multipart",
                                 data=body, method="POST",
                                 headers={"Authorization": f"Bearer {get_valid_access_token(creds)}",
                                          "Content-Type": f"multipart/related; boundary={bnd}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        json.loads(r.read())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--show", action="store_true", help="In đầy đủ mô tả")
    ap.add_argument("--only", default=None, help="Chỉ xử lý mục có id bắt đầu bằng chuỗi này")
    ap.add_argument("--playlist", action="store_true", help="Tự thêm video vào playlist theo series (mặc định tắt)")
    ap.add_argument("--seo-ok", action="store_true", help="Đăng dù seo_check báo ERROR (ticket 69)")
    args = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(str(HERE / "plan_*.json"))):
        rows += json.loads(Path(f).read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
    taken: dict[str, set[str]] = {}  # dò sâu MỘT lần mỗi kênh -- mỗi lần tốn lượt search/ngày
    if args.only:
        rows = [r for r in rows if r["id"].startswith(args.only)]
    for r in rows:
        if r.get("hold") and not args.only:
            print(f"  (giữ lại) {r['id']} -- {r['hold']}"); continue
        if r["id"] in ledger:
            print(f"  (đã đăng) {r['id']} -> {ledger[r['id']]}")
            if args.confirm and args.playlist:
                add_playlists(r, ledger[r["id"]])
            continue
        mp4, thumb = OUT / f"{r['id']}.mp4", HERE / "thumbs" / r["thumbnail"]
        if not mp4.exists() or not thumb.exists():
            print(f"  THIẾU {r['id']}: video={mp4.exists()} thumbnail={thumb.exists()}"); continue
        creds = CHANNEL[r["series"]]["creds"]
        publish_at = f"{r['day']}T{r['slot']}:00Z"
        if creds not in taken:
            taken[creds] = hf_coverage.occupied_slots(creds)
        if publish_at[:16] in taken[creds]:
            print(f"  (bỏ qua) {r['id']} {publish_at} -- khung này ĐÃ CÓ video"); continue
        if datetime.fromisoformat(publish_at.replace("Z", "+00:00")) - datetime.now(timezone.utc) < MIN_LEAD:
            print(f"  (bỏ qua) {r['id']} {publish_at} -- khung giờ đã qua hoặc quá sát"); continue
        if len(r["title"]) > 100 or "<" in r["title"] or ">" in r["title"]:   # YouTube: <= 100 ký tự, không < >
            raise SystemExit(f"Tiêu đề {r['id']} dài {len(r['title'])} ký tự (> 100) hoặc có < > -- rút gọn")
        desc = description(r)
        # Ticket 69: soát SEO trước khi đăng (keyword đầu tiêu đề/mô tả/lời 30 giây đầu, chương, hashtag, tag, thumbnail).
        sys.path.insert(0, str(ROOT))
        import seo_check  # noqa: PLC0415
        seo = seo_check.check_row(dict(r, description=desc), str(HERE / "plan.json"))
        for i in seo:
            print(f"       seo {i['level']} {i['code']}: {i['message']}")
        if any(i["level"] == "ERROR" for i in seo) and not args.seo_ok:
            print(f"  (dừng) {r['id']} -- seo_check báo ERROR; sửa plan hoặc chạy lại với --seo-ok"); continue
        print(f'{"ĐĂNG " if args.confirm else "[DRY]"} {publish_at} | {mp4.stat().st_size/1e6:5.1f}MB | {r["title"]}')
        if args.playlist:
            sys.path.insert(0, str(ROOT / "tools/publish"))
            from playlist_apply import playlist_for_row
            pl = playlist_for_row(r["series"], r)
            print(f"       playlist: {pl['title'] if pl else '(chưa ánh xạ series)'}")
        print("       " + " | ".join(chapters(r)))
        if args.show:
            print(desc)
        if not args.confirm:
            continue
        meta = VideoMetadata(title=r["title"], description=desc, tags=r["tags"], category_id="22",
                             privacy_status="private", publish_at=publish_at, language="vi")
        try:
            vid = upload_video(str(mp4), meta, creds)["id"]
        except QuotaExceededError:
            print("\nHẾT QUOTA YouTube hôm nay -- dừng. Quota reset lúc 00:00 giờ Thái Bình Dương; chạy lại là đăng tiếp.")
            return 2
        ledger[r["id"]] = vid
        LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"   -> https://youtu.be/{vid}", flush=True)
        try:
            upload_thumbnail(vid, thumb, creds)
            print("   -> đã gắn thumbnail")
        except Exception as e:  # noqa: BLE001 -- video đã lên, chỉ thiếu thumbnail
            print(f"   !! gắn thumbnail lỗi: {e}")
        if r.get("captions"):
            try:
                upload_captions(vid, r, creds)
                print("   -> đã tải phụ đề tiếng Việt")
            except Exception as e:  # noqa: BLE001 -- video đã lên; phụ đề thêm sau được
                print(f"   !! phụ đề lỗi: {str(e)[:200]}")
        if args.playlist:
            add_playlists(r, vid)
    return 0


def add_playlists(row: dict, vid: str) -> None:
    """Playlist tạo CÔNG KHAI: video riêng tư/hẹn giờ trong đó tự ẩn với người
    xem tới giờ lên sóng, nên không cần ai quay lại bật playlist."""
    creds = CHANNEL[row["series"]]["creds"]
    sys.path.insert(0, str(ROOT / "tools/publish"))
    from playlist_apply import playlist_for_row
    pl = playlist_for_row(row["series"], row)
    if not pl:
        print(f"   (không có ánh xạ playlist cho {row['series']}/{row.get('lane')})")
        return
    try:
        from youtube_catalog import ensure_playlist_and_add
        res = ensure_playlist_and_add(creds, pl["title"], vid, privacy_status="public")
        print(f"   -> playlist {pl['title']!r}: {res.get('action')}")
    except Exception as e:  # noqa: BLE001 -- chạy lại là thêm tiếp (hàm idempotent)
        print(f"   !! playlist {pl['title']!r} lỗi: {e}")


if __name__ == "__main__":
    sys.exit(main())
