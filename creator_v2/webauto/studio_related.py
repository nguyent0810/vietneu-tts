"""Attach reviewed Short-to-Long mappings in Studio; selectors require live verification."""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .browsentic import browser, run

# Studio markup and labels are provisional; fail closed when a control is missing.
RELATED = ("[aria-label='Video liên quan']", "[aria-label='Related video']",
           "ytcp-video-metadata-editor-shorts-related-video")
DIALOG = "[role='dialog']"
SEARCH = ("[role='dialog'] input[type='search']", "[role='dialog'] input")
RESULT = "[role='dialog'] a[href*='{}']"
CONFIRM = ("[role='dialog'] button[aria-label='Xong']", "[role='dialog'] button[aria-label='Done']")
SAVE = ("#save", "button[aria-label='Lưu']", "button[aria-label='Save']")
TIMEOUT = 20
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def read_done(path):
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("done"), dict):
        raise ValueError(f"Invalid ledger: {path}")
    return data["done"]


def plan(channel, map_path, done_path, limit=None):
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
        if not VIDEO_ID.fullmatch(short) or not VIDEO_ID.fullmatch(long) or short == long:
            raise ValueError(f"Invalid video IDs in mapping: {row.get('short_slug')}")
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


async def attach(b, row):
    short, long = row["short_video_id"], row["long_video_id"]
    tab = await call(b, "page_openTab", url=f"https://studio.youtube.com/video/{short}/edit")
    try:
        await first(b, "page_waitForElement", RELATED)
        await first(b, "page_clickElement", RELATED)
        await call(b, "page_waitForElement", target={"selector": DIALOG})
        await first(b, "page_fillInput", SEARCH, value=long)
        # Select only a result whose link contains the exact requested video ID.
        selector = RESULT.format(long)
        await call(b, "page_waitForElement", target={"selector": selector})
        await call(b, "page_clickElement", target={"selector": selector})
        await first(b, "page_clickElement", CONFIRM)
        # Require a visible reference to the selected ID before saving anything.
        await call(b, "page_waitForElement", target={"selector": f"a[href*='{long}']"})
        await first(b, "page_clickElement", SAVE)
        # An explicit saved notification prevents recording an unconfirmed submit.
        for _ in range(TIMEOUT):
            content = (await call(b, "page_extractText")).get("content", "")
            if "Changes saved" in content or "Đã lưu các thay đổi" in content:
                return
            await asyncio.sleep(1)
        raise TimeoutError("Save confirmation did not appear")
    except Exception:
        # Browsentic saves screenshots through its screenshot tool; report failures too.
        try:
            shot = await call(b, "page_screenshot")
            print(f"Screenshot for {short}: {shot}")
        except Exception as exc:
            print(f"Screenshot failed for {short}: {exc}")
        raise
    finally:
        if tab.get("tabId"):
            await call(b, "page_closeTab", tabId=tab["tabId"])


async def execute(rows, ledger):
    done = read_done(ledger)
    async with browser() as b:
        for row in rows:
            await attach(b, row)
            done[row["short_video_id"]] = {"long_video_id": row["long_video_id"], "short_slug": row["short_slug"], "saved_at": datetime.now(timezone.utc).isoformat()}
            save_done(ledger, done)
            print(f"Saved {row['short_slug']} -> {row['long_slug']}")


def run_related(args):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.channel):
        raise ValueError("Invalid channel")
    ledger = Path("output") / "channels" / args.channel / "related_done.json"
    rows = plan(args.channel, args.map, ledger, args.limit)
    for row in rows:
        print(f"{row['short_slug']} ({row['short_video_id']}) -> {row['long_slug']} ({row['long_video_id']})")
    print(f"Planned: {len(rows)}")
    if not args.dry_run and rows:
        run(execute(rows, ledger))


def add_parser(sub):
    p = sub.add_parser("related", help="attach reviewed Short-to-Long mappings in Studio")
    p.add_argument("channel")
    p.add_argument("--map", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=run_related)
