"""Attach reviewed Short-to-Long mappings in Studio; selectors require live verification."""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .browsentic import browser, run

# Studio markup and labels are provisional; fail closed when a control is missing.
# Selector đo trên Studio thật 13/11/2026 (Lead, Browsentic): ô "Related video" -> hộp "Choose specific video"
# -> ô tìm "Search your videos" -> thẻ ytcp-entity-card (role option) -> Save.
LINK = "#linked-video-editor-link"
SEARCH = "#search-yours"
CARD = "ytcp-entity-card"
SAVE = "#save"
UNDO = "#discard"  # nút "Undo changes": bỏ thay đổi dở để chuyển trang không bật hộp "Leave site?"
TIMEOUT = 20
# Mỗi kênh ở một tài khoản Google khác trong cùng Chrome (đo 13/11/2026). Trang sửa video chỉ mở được đúng authuser.
AUTHUSER = {"CK": 0, "MIM": 1, "CL": 2}
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def read_done(path):
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("done"), dict):
        raise ValueError(f"Invalid ledger: {path}")
    return data["done"]


LEVELS = {"high": 0, "medium": 1, "low": 2}


def plan(channel, map_path, done_path, limit=None, min_conf="high"):
    data = json.loads(Path(map_path).read_text(encoding="utf-8"))
    if data.get("channel") != channel or not isinstance(data.get("matches"), list):
        raise ValueError("Map channel does not match or matches is missing")
    if limit is not None and limit < 1:
        raise ValueError("--limit must be positive")
    done = read_done(done_path)
    result = []
    seen = set()
    for row in data["matches"]:
        short, long = row.get("short_video_id"), row.get("long_video_id")
        if not short or not long or short in done or short in seen:
            continue
        if LEVELS.get(row.get("confidence", "high"), 9) > LEVELS[min_conf]:
            continue
        if not VIDEO_ID.fullmatch(short) or not VIDEO_ID.fullmatch(long) or short == long:
            raise ValueError(f"Invalid video IDs in mapping: {row.get('short_title') or short}")
        if not row.get("long_title"):
            raise ValueError(f"long_title missing for {short}: needed to pick the card in Studio")
        seen.add(short)
        result.append(row)
    return result[:limit] if limit is not None else result


def save_done(path, done):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"done": done}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


async def call(b, tool, **kwargs):
    return await asyncio.wait_for(b.call(tool, **kwargs), timeout=TIMEOUT)


async def first(b, tool, selectors, **kwargs):
    last = None
    for selector in selectors:
        try:
            return await call(b, tool, target={"selector": selector}, **kwargs)
        except (RuntimeError, asyncio.TimeoutError) as exc:
            last = exc
    raise RuntimeError(f"{tool}: controls not found: {selectors}") from last


def _key(title):
    """40 ký tự đầu của tiêu đề Long: thẻ trong hộp chọn và ô Related video đều chứa tiêu đề đầy đủ."""
    return title[:40].rstrip()


async def linked_text(b, want=None, wait=15):
    """Nội dung ô Related video; nếu có `want` thì chờ tới `wait` giây cho tới khi thấy (trang Studio nạp chậm)."""
    await call(b, "page_waitForElement", target={"selector": LINK}, state="attached", timeoutMs=15000)
    text = ""
    for _ in range(wait if want else 1):
        text = (await call(b, "page_extractText", target={"selector": LINK})).get("content", "")
        if not want or want in text:
            break
        await asyncio.sleep(1)
    return text


async def attach(b, row, authuser=None):
    """Trả "already" nếu Short đã trỏ đúng Long, "saved" khi lưu xong và đọc lại thấy đúng."""
    short, title = row["short_video_id"], row["long_title"]
    key = _key(title)
    q = f"?authuser={authuser}" if authuser is not None else ""
    await call(b, "page_navigate", url=f"https://studio.youtube.com/video/{short}/edit{q}")
    try:
        await asyncio.sleep(2)
        if key in await linked_text(b, key, wait=3):
            return "already"
        await call(b, "page_clickElement", target={"selector": LINK})
        await call(b, "page_waitForElement", target={"selector": SEARCH}, timeoutMs=15000)
        await call(b, "page_typeText", target={"selector": SEARCH}, text=key, speed="instant", pressEnter=True)
        await call(b, "page_waitForElement", target={"selector": CARD, "text": key}, timeoutMs=15000)
        await asyncio.sleep(1)
        await call(b, "page_clickElement", target={"selector": CARD, "text": key})
        if key not in await linked_text(b, key, wait=8):
            raise RuntimeError(f"Related video chưa đổi sang {key!r}")
        await call(b, "page_clickElement", target={"selector": SAVE})
        await asyncio.sleep(5)
        # Đọc lại sau khi tải lại trang: chỉ ghi sổ khi Studio thật sự lưu.
        await call(b, "page_navigate", action="reload")
        await asyncio.sleep(3)
        if key not in await linked_text(b, key, wait=15):
            raise RuntimeError("Lưu xong nhưng tải lại không thấy Related video")
        return "saved"
    except Exception:
        # Thay đổi chưa lưu + chuyển trang = hộp "Leave site?" chặn cả tab (13/11: treo extension). Bỏ thay đổi trước.
        for target in ({"selector": UNDO}, {"text": "Undo changes", "role": "button"}):
            try:
                await call(b, "page_clickElement", target=target)
                break
            except Exception:
                pass
        try:
            shot = await call(b, "page_screenshot", save=True, filename=f"related-fail-{short}")
            print(f"Ảnh lỗi {short}: {shot.get('savedTo') if isinstance(shot, dict) else shot}")
        except Exception as exc:
            print(f"Không chụp được ảnh lỗi {short}: {exc!r}")
        raise


async def execute(rows, ledger, authuser=None):
    done = read_done(ledger)
    fails = 0
    async with browser() as b:
        # Tab riêng: không chiếm tab chủ kênh đang xem (13/11). Các lệnh page_* chạy trên tab đang active = tab này.
        tab = await call(b, "page_openTab", url="https://studio.youtube.com/")
        try:
            await _run_rows(b, rows, ledger, done, authuser)
        finally:
            if isinstance(tab, dict) and tab.get("tabId"):
                try:
                    await call(b, "page_closeTab", tabId=tab["tabId"])
                except Exception:
                    pass


async def _run_rows(b, rows, ledger, done, authuser=None):
    fails = 0
    if True:
        for row in rows:
            try:
                state = await attach(b, row, authuser)
                fails = 0
            except Exception as exc:
                print(f"LỖI {row['short_video_id']}: {exc!r}", flush=True)
                fails += 1
                if fails >= 3:
                    # 13/11: Chrome thu nhỏ -> mọi lượt hỏng; dừng thay vì chạy cả loạt lỗi.
                    raise SystemExit("3 lỗi liên tiếp: dừng. Kiểm cửa sổ Chrome (không thu nhỏ) và hộp 'Leave site?'.")
                continue
            done[row["short_video_id"]] = {"long_video_id": row["long_video_id"], "state": state,
                                           "saved_at": datetime.now(timezone.utc).isoformat()}
            save_done(ledger, done)
            print(f"{state} {row['short_video_id']} {row.get('short_title', '')[:40]} -> {row['long_title'][:40]}", flush=True)


def run_related(args):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.channel):
        raise ValueError("Invalid channel")
    ledger = Path("output") / "channels" / args.channel / "related_done.json"
    rows = plan(args.channel, args.map, ledger, args.limit, args.min_conf)
    for row in rows:
        print(f"{row['short_video_id']} {row.get('short_title', '')[:40]} -> {row['long_video_id']} {row['long_title'][:40]}")
    print(f"Planned: {len(rows)}")
    if not args.dry_run and rows:
        run(execute(rows, ledger, args.authuser if args.authuser is not None else AUTHUSER.get(args.channel)))


def add_parser(sub):
    p = sub.add_parser("related", help="attach reviewed Short-to-Long mappings in Studio")
    p.add_argument("channel")
    p.add_argument("--map", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int)
    p.add_argument("--authuser", type=int, help="tài khoản Google trong Chrome sở hữu kênh (mặc định theo AUTHUSER)")
    p.add_argument("--min-conf", choices=["high", "medium", "low"], default="high")
    p.set_defaults(func=run_related)
