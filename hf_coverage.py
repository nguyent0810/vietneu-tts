"""Đếm độ phủ video theo ngày của một kênh — hỏi theo ID, không tin playlist.

Vì sao phải viết lại: bản cũ duyệt playlist uploads theo trang rồi đếm. Ngay
sau một đợt upload lớn, playlist XÊ DỊCH trong lúc duyệt (video mới chèn vào
đầu, video tới giờ đổi sang public), nên kết quả vừa **lặp** vừa **sót**.
Trong một buổi nó đã báo sai hai lần: "25/09 có 8 video" (thực tế 5, ba video
bị đếm hai lần) và "30/09 chỉ còn 2" (thực tế 5, ba video bị bỏ qua) — lần thứ
hai suýt làm tưởng video bị gỡ khỏi kênh.

Cách làm ở đây:
  1. DÒ: duyệt playlist, khử trùng theo video_id, lặp lại tới khi hai lượt
     liên tiếp cho cùng một tập ID.
  2. BẢO ĐẢM: hợp thêm (a) mọi video_id trong các sổ `uploaded.json`, và
     (b) SỔ ID BỀN VỮNG — mọi ID từng thấy, lưu ở `output/.video_index.json`.
     Bước (b) là bắt buộc: đo thực tế cho thấy playlist bỏ sót cùng một video
     ở CẢ HAI lượt, nên "hai lượt giống nhau" không chứng minh được gì. Đã
     thấy một lần thì không bao giờ quên nữa.
  3. XÁC NHẬN: `videos.list` theo ID (lô 50) lấy trạng thái thật. ID nào API
     báo không còn thì bị gỡ khỏi sổ — xoá thật vẫn phản ánh được.

Playlist chỉ còn dùng để DÒ; con số cuối luôn đến từ hỏi theo ID.

Usage:
    python3 hf_coverage.py                          # 16 ngày từ hôm nay
    python3 hf_coverage.py --from 2026-10-01 --days 14 --target 5
    python3 hf_coverage.py --json
"""
from __future__ import annotations

import argparse
import collections
import datetime
import glob
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DEFAULT_CREDENTIALS = PROJECT_ROOT / ".youtube_channels" / "hinh_su.json"
LEDGER_GLOB = "output/cl_staging/*/uploaded.json"
INDEX_PATH = "output/.video_index.json"
MAX_DISCOVERY_PASSES = 4
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
# search.list tốn 100 đơn vị quota/lần (playlistItems chỉ 1), nên chỉ chạy
# khi được yêu cầu. Bù lại nó là MỘT CHỈ MỤC KHÁC của YouTube: video mà
# playlistItems bỏ sót vẫn có thể xuất hiện ở đây, và ngược lại.


def ledger_ids(pattern: str = LEDGER_GLOB) -> dict[str, str]:
    """{video_id: nguồn} từ mọi sổ đã đăng."""
    out = {}
    for f in sorted(glob.glob(str(PROJECT_ROOT / pattern))):
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        label = Path(f).parent.name
        for vid in data.values():
            out[vid] = label
    return out


def _read_index(path: str):
    try:
        return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def load_index(path: str = INDEX_PATH, channel: str | None = None) -> set[str]:
    """Sổ ID bền vững: mọi video từng thấy trên kênh.

    Sổ TÁCH THEO KÊNH ({channel_id: [id...]}). Bản cũ là một danh sách phẳng
    dùng chung cho cả ba kênh, và việc tỉa "ID không còn trên kênh" khi quét
    kênh này đã xoá sạch video riêng tư của hai kênh kia khỏi sổ. Danh sách
    phẳng cũ (nếu còn) được giữ dưới khoá "_legacy" làm ứng viên cho mọi kênh."""
    raw = _read_index(path)
    if isinstance(raw, list):
        return set(raw)
    if not isinstance(raw, dict):
        return set()
    if channel is None:
        return set().union(*(set(v) for v in raw.values())) if raw else set()
    return set(raw.get(channel, [])) | set(raw.get("_legacy", []))


def save_index(ids: set[str], path: str = INDEX_PATH, channel: str | None = None) -> None:
    p = PROJECT_ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if channel is None:
        payload = sorted(ids)
    else:
        raw = _read_index(path)
        if isinstance(raw, list):
            raw = {"_legacy": raw}
        elif not isinstance(raw, dict):
            raw = {}
        raw[channel] = sorted(ids)
        # ID đã được kênh này nhận là của mình thì rời khỏi bể chung.
        legacy = set(raw.get("_legacy", [])) - set(ids)
        if legacy:
            raw["_legacy"] = sorted(legacy)
        else:
            raw.pop("_legacy", None)
        payload = raw
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    tmp.replace(p)


def own_channel_index(path: str, channel: str) -> set[str]:
    """Chỉ phần sổ đã xác nhận thuộc kênh này -- dùng để báo 'đã mất'. Không
    lấy bể chung, vì video riêng tư của kênh khác trong đó sẽ trông như mất."""
    raw = _read_index(path)
    return set(raw.get(channel, [])) if isinstance(raw, dict) else set()


def rows_of_channel(rows: list[dict], channel: str) -> list[dict]:
    """Sổ đăng và bể ID gộp cả ba kênh. Video CÔNG KHAI của kênh khác vẫn trả
    về khi hỏi theo ID -- không lọc thì bị đếm nhầm sang kênh đang xét."""
    return [r for r in rows if r.get("channel") == channel]


def count_by_day(rows: list[dict]) -> collections.Counter:
    """rows: [{'when': ISO8601, ...}] -> đếm theo ngày."""
    return collections.Counter(r["when"][:10] for r in rows)


def discovery_stabilised(passes: list[set[str]]) -> bool:
    """Playlist coi là đứng yên khi hai lượt liên tiếp cho cùng tập ID."""
    return len(passes) >= 2 and passes[-1] == passes[-2]


# --------------------------------------------------------------------------
# Phần chạm mạng
# --------------------------------------------------------------------------
def _api():
    sys.path.insert(0, str(PROJECT_ROOT))
    from youtube_catalog import _get, CHANNELS_URL, PLAYLIST_ITEMS_URL, VIDEOS_URL
    return _get, CHANNELS_URL, PLAYLIST_ITEMS_URL, VIDEOS_URL


def discover_ids(credentials: str) -> tuple[set[str], bool, int]:
    _get, CHANNELS_URL, PLAYLIST_ITEMS_URL, _ = _api()
    uploads = _get(credentials, CHANNELS_URL, {"part": "contentDetails", "mine": "true"})[
        "items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    passes: list[set[str]] = []
    while len(passes) < MAX_DISCOVERY_PASSES:
        found, token = set(), None
        while True:
            params = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
            if token:
                params["pageToken"] = token
            data = _get(credentials, PLAYLIST_ITEMS_URL, params)
            found.update(x["contentDetails"]["videoId"] for x in data["items"])
            token = data.get("nextPageToken")
            if not token:
                break
        passes.append(found)
        if discovery_stabilised(passes):
            break
    union = set().union(*passes)
    return union, discovery_stabilised(passes), len(passes)


def discover_ids_deep(credentials: str, known: set[str] | None = None) -> set[str]:
    """Nguồn dò thứ hai: search.list forMine=true (trả cả video private của
    chính mình). Dùng khi cần lấp những video playlistItems không chịu trả.

    Mỗi trang tốn 100 đơn vị quota VÀ một lượt trong hạn mức riêng 100 lượt
    search/ngày -- quét trọn kênh ~1.500 video là ~30 lượt. Truyền `known` (sổ
    ID của lần quét trọn trước) thì dừng sau HAI trang liền không có ID mới:
    kết quả xếp theo ngày tạo, video lạ chỉ có thể nằm ở đầu danh sách."""
    _get, _, _, _ = _api()
    found, token, stale = set(), None, 0
    while True:
        params = {"part": "id", "forMine": "true", "type": "video",
                  "order": "date", "maxResults": 50}
        if token:
            params["pageToken"] = token
        data = _get(credentials, SEARCH_URL, params)
        page = {x["id"]["videoId"] for x in data.get("items", []) if x["id"].get("videoId")}
        found |= page
        token = data.get("nextPageToken")
        if not token:
            break
        if known:
            stale = stale + 1 if page <= known else 0
            if stale >= 2:
                break
    return found


def fetch_status(credentials: str, ids: list[str]) -> list[dict]:
    _get, _, _, VIDEOS_URL = _api()
    rows = []
    for i in range(0, len(ids), 50):
        data = _get(credentials, VIDEOS_URL, {"part": "status,snippet", "id": ",".join(ids[i:i + 50])})
        for v in data.get("items", []):
            st = v["status"]
            rows.append({"id": v["id"],
                         "channel": v["snippet"].get("channelId"),
                         "scheduled": bool(st.get("publishAt")),
                         "when": st.get("publishAt") or v["snippet"]["publishedAt"],
                         "privacy": st["privacyStatus"],
                         "title": v["snippet"]["title"]})
    return rows


def slots_taken(rows: list[dict]) -> set[str]:
    """Khung giờ (YYYY-MM-DDTHH:MM) đã có video sẽ phát hoặc đã phát. Video
    riêng tư KHÔNG hẹn giờ thì không chiếm khung nào."""
    return {r["when"][:16] for r in rows if not (r.get("privacy") == "private" and not r.get("scheduled"))}


def occupied_slots(credentials: str) -> set[str]:
    """Mọi khung giờ đã có video của CHÍNH kênh này -- dò CẢ playlist lẫn
    search.list. Chỉ dựa vào playlist từng bỏ sót 256 video đã hẹn giờ của
    nguồn đăng khác, và kết quả là 29 khung phát hai video cùng lúc
    (28/09/2026). Uploader phải gọi hàm này trước khi đăng."""
    _get, CHANNELS_URL, _, _ = _api()
    me = _get(credentials, CHANNELS_URL, {"part": "id", "mine": "true"})["items"][0]["id"]
    found, _, _ = discover_ids(credentials)
    index = load_index(channel=me)
    found |= discover_ids_deep(credentials, known=index)
    found |= index
    rows = rows_of_channel(fetch_status(credentials, sorted(found)), me)
    save_index({r["id"] for r in rows}, channel=me)
    return slots_taken(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--credentials", default=str(DEFAULT_CREDENTIALS))
    ap.add_argument("--from", dest="start", default=None, help="Ngày bắt đầu YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--days", type=int, default=16)
    ap.add_argument("--target", type=int, default=5, help="Số video mong muốn mỗi ngày")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--deep", action="store_true",
                    help="Dò thêm bằng search.list (tốn quota, dùng khi nghi ngờ thiếu video)")
    args = ap.parse_args()

    discovered, stable, passes = discover_ids(args.credentials)
    if args.deep:
        deep = discover_ids_deep(args.credentials)
        print(f"dò sâu bằng search.list: {len(deep)} video, "
              f"{len(deep - discovered)} cái playlist không trả", file=sys.stderr)
        discovered |= deep
    _get, CHANNELS_URL, _, _ = _api()
    me = _get(args.credentials, CHANNELS_URL, {"part": "id", "mine": "true"})["items"][0]["id"]
    ledger = ledger_ids()
    index = load_index(channel=me)
    own_before = own_channel_index(INDEX_PATH, me)
    ids = sorted(discovered | set(ledger) | index)
    all_rows = fetch_status(args.credentials, ids)
    rows = rows_of_channel(all_rows, me)
    foreign = len(all_rows) - len(rows)
    alive = {r["id"] for r in rows}
    missed = sorted(((set(ledger) | index) & alive) - discovered)   # playlist bỏ sót
    gone = sorted((own_before | discovered) - alive)                 # không còn trên kênh
    save_index(alive, channel=me)
    counts = count_by_day(rows)

    start = (datetime.date.fromisoformat(args.start) if args.start
             else datetime.date.today())
    days = [(start + datetime.timedelta(days=k)).isoformat() for k in range(args.days)]
    coverage = {d: counts.get(d, 0) for d in days}
    first_gap = next((d for d, n in coverage.items() if n == 0), None)

    if args.json:
        print(json.dumps({"coverage": coverage, "first_gap": first_gap,
                          "playlist_stable": stable, "playlist_passes": passes,
                          "missed_by_playlist": missed, "gone": gone,
                          "videos_checked": len(rows), "foreign_skipped": foreign}, ensure_ascii=False, indent=1))
        return 0

    if foreign:
        print(f"  bỏ qua {foreign} video công khai của KÊNH KHÁC có trong sổ chung", file=sys.stderr)
    print(f"Hỏi trạng thái {len(rows)} video theo ID "
          f"(dò playlist {passes} lượt, {'đứng yên' if stable else 'CHƯA đứng yên'})")
    if missed:
        print(f"  {len(missed)} video playlist BỎ SÓT, lấy được nhờ sổ ID bền vững "
              f"— đây đúng là lý do không đếm bằng playlist", file=sys.stderr)
    if gone:
        print(f"  {len(gone)} ID trong sổ không còn trên kênh, đã gỡ khỏi sổ: "
              f"{', '.join(gone[:5])}", file=sys.stderr)
    print("\nngày         số video")
    for d in days:
        n = coverage[d]
        flag = "" if n == args.target else ("   <<< TRỐNG" if n == 0 else f"   <<< {n} (khác {args.target})")
        print(f"  {d}   {n}{flag}")
    print(f"\nngày trống đầu tiên: {first_gap or 'không có trong khoảng này'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
