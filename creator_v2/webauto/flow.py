"""Google Flow (flow.google.com): generate images or videos (text-to-video, image-to-video) and download them.

Drives a Playwright persistent Chrome profile kept in ~/.webauto/profiles/flow (log in once with
`webauto flow login`). Google does not challenge it, unlike chatgpt.com.

On a server (no window to sign in, no Google Chrome on Linux ARM) export the session from a signed-in
profile with `webauto flow export-session` and pass it with `--session` (or WEBAUTO_FLOW_SESSION).

Selectors are English-UI selectors; the dedicated profile keeps Flow in English. Flow has no public
API, so these selectors are the fragile part: when the UI changes, fix them here.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

from . import auth
from .common import default_out, parse_prompts, profile_dir

FLOW_URL = "https://flow.google.com/"
EDITOR = "flow-rich-text-editor div[role=textbox]"
GENERATE = "flow-generate-icon-button button"
SETTINGS = "button[aria-label='Settings trigger']"
DEFAULT_MODEL = {"image": "Nano Banana Pro", "video": "Omni 1.1 Flash"}
NEW_PROJECT = re.compile("Dự án mới|New project")
VIDEO_DONE = "flow-video-tile img[alt='Generated video thumbnail']"
VIDEO_FAILED = "failed to generate"
IMAGE_TILE = "flow-grid-tile-container"
# Image tile menu > Download offers 1K (original, = the tile's preview src), 2K and 4K (upscaled).
# 2K is free on this account (0 credits, ~15 s) but only works with a Chrome window: headless,
# Flow answers "Upscaling failed!" (its reCAPTCHA check). 4K needs a higher plan ("Upgrade").
IMAGE_SIZES = ("1K", "2K")


# Google Chrome has no Linux ARM build; Playwright's own Chromium works for Flow there
CHANNEL = None if sys.platform.startswith("linux") else "chrome"
ARGS = ["--disable-blink-features=AutomationControlled"]
VIEWPORT = {"width": 1400, "height": 900}


def session_file(session=None):
    s = session or os.environ.get("WEBAUTO_FLOW_SESSION")
    return Path(s).expanduser() if s else None


def launch(p, headless=False, session=None):
    """Persistent profile, or a fresh context loaded from an exported session file. The browser behind a
    session context closes when sync_playwright() exits."""
    state = session_file(session)
    if state:
        if not state.exists():
            raise SystemExit(f"session file not found: {state} (make it with `webauto flow export-session`)")
        browser = p.chromium.launch(channel=CHANNEL, headless=headless, args=ARGS)
        return browser.new_context(storage_state=str(state), viewport=VIEWPORT, accept_downloads=True)
    return p.chromium.launch_persistent_context(
        str(profile_dir("flow")), channel=CHANNEL, headless=headless, accept_downloads=True,
        viewport=VIEWPORT, args=ARGS)


def login():
    """Open the profile so the owner can sign in to Google. Close the whole Chrome window when done:
    a Chrome left running keeps the profile locked and the next run cannot start."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        ctx = launch(p)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(FLOW_URL)
        print("Sign in to Google in the opened window, then close it.")
        page.wait_for_event("close", timeout=0)
        ctx.close()


def export_session(out):
    """Write the signed-in profile's cookies + storage to `out` (owner-only) for `--session` elsewhere.
    The file signs in as you: keep it private, never commit it."""
    from playwright.sync_api import sync_playwright

    out = Path(out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = launch(p, headless=True)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(FLOW_URL)
            page.wait_for_timeout(3000)
            if auth.url_is_login(page.url) or page.get_by_role("button", name=NEW_PROJECT).count() == 0:
                raise SystemExit("the flow profile is not signed in: run `webauto flow login` first")
            old = os.umask(0o077)
            try:
                ctx.storage_state(path=str(out))
            finally:
                os.umask(old)
        finally:
            ctx.close()
    out.chmod(0o600)
    print(f"session written to {out} (owner-only; it signs in as you, do not share or commit it)")


def new_project(page, headless=False):
    page.goto(FLOW_URL)
    page.wait_for_timeout(3000)

    def signed_in():
        return not auth.url_is_login(page.url) and page.get_by_role("button", name=NEW_PROJECT).count() > 0

    # the window is the owner's to sign in to (Google may also ask for 2-step); webauto only waits.
    # Headless has no window to sign in to, so fail at once: run `webauto flow login` first.
    auth.ensure_sync(signed_in, "Google Flow", FLOW_URL, wait_s=0 if headless else None)
    page.get_by_role("button", name=NEW_PROJECT).click(timeout=60000)
    page.wait_for_url(re.compile(r"/project/"), timeout=30000)
    page.wait_for_selector(EDITOR, timeout=30000)


def apply_settings(page, mode, model=None, count=1, duration=6, ratio=None, res=None):
    """Open the settings popup and set mode / ratio / (resolution, duration) / model / count."""
    # A one-off announcement dialog (cdk-overlay backdrop) can cover the editor on a new project:
    # dismiss it with Escape and retry instead of failing the whole batch (05/11).
    for attempt in range(3):
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
        try:
            page.locator(SETTINGS).click(timeout=10000)
            break
        except Exception:
            if attempt == 2:
                raise
    word = "Image" if mode == "image" else "Video"
    page.get_by_role("radio", name=re.compile(rf"^\s*(image|videocam)?\s*{word}\s*$")).click()
    # Model first: the ratio / resolution / duration radios depend on it (Omni 1.2 Flash has no
    # duration choice; picking 8s under 1.1 then switching to 1.2 gave "failed to generate", 06/11).
    page.get_by_role("button", name="Select model family").click()
    page.get_by_role("menuitem", name=re.compile(re.escape(model or DEFAULT_MODEL[mode]))).click()
    page.wait_for_timeout(500)
    if ratio:
        page.get_by_role("radio", name=re.compile(re.escape(ratio))).click()
    if mode == "video":
        if res:
            page.get_by_role("radio", name=re.compile(re.escape(res))).click()
        dur = page.get_by_role("radio", name=re.compile(rf"^{duration}s$"))
        if dur.count():
            dur.click()
        else:
            print(f"model has no {duration}s option here, using its own length")
    page.get_by_role("radio", name=f"x{count}", exact=True).click()
    page.wait_for_timeout(500)
    cost = page.get_by_text(re.compile(r"will use \d+ credits?")).all()
    print("settings:", page.locator(SETTINGS).inner_text().replace("\n", " "),
          "|", cost[0].inner_text() if cost else "cost not shown")
    page.keyboard.press("Escape")


def set_start_frame(page, image):
    """Video mode > Frames > Start slot > Upload media: use `image` as the first frame."""
    page.locator(SETTINGS).click()
    page.get_by_role("radio", name=re.compile("Frames")).click()
    page.keyboard.press("Escape")
    page.wait_for_timeout(800)
    page.get_by_role("button", name="Start", exact=True).click()
    with page.expect_file_chooser(timeout=30000) as fc:
        page.get_by_role("button", name="Upload media").click()  # get_by_text also matches a tooltip
    fc.value.set_files(str(image))
    # in Flow media picker, wait for the uploaded thumbnail button to appear and click it
    dialog = page.locator(".cdk-overlay-container")
    img_btn = None
    for _ in range(90):
        candidates = dialog.locator("button:has(img)")
        if candidates.count():
            img_btn = candidates.first
            break
        page.wait_for_timeout(1000)
    if not img_btn:
        raise TimeoutError("uploaded image thumbnail did not appear in media picker")
    img_btn.click()
    page.wait_for_timeout(1000)
    add = dialog.get_by_role("button", name="Add to prompt")
    if add.count() and add.first.is_enabled():
        add.first.click()
    page.wait_for_selector("text=Select a frame image", state="detached", timeout=30000)
    page.wait_for_timeout(1500)

    # verify that Start frame chip is populated
    chip = page.locator(".frame-trigger flow-image-ingredient-chip")
    if not chip.count():
        start_btn = page.locator(".frame-trigger button.empty-chip")
        if start_btn.count():
            start_btn.first.click()
            page.wait_for_timeout(1000)
            cand = dialog.locator("button:has(img)")
            if cand.count():
                cand.first.click()
                page.wait_for_timeout(1000)
                add = dialog.get_by_role("button", name="Add to prompt")
                if add.count() and add.first.is_enabled():
                    add.first.click()
            page.wait_for_selector("text=Select a frame image", state="detached", timeout=15000)
            page.wait_for_timeout(1000)
    print("Start frame chip verified:", page.locator(".frame-trigger flow-image-ingredient-chip").count() > 0)


def media_srcs(page):
    """media-id -> signed CDN url of every generated image tile on the page."""
    return dict(page.eval_on_selector_all(
        "img[data-media-id], video[data-media-id]", "els => els.map(e => [e.dataset.mediaId, e.currentSrc || e.src])"))


def image_size_for(size, headless):
    """Resolve `--image-size`: None means 2K with a window, 1K headless (upscaling fails there)."""
    if size is None:
        return "1K" if headless else "2K"
    if size not in IMAGE_SIZES:
        raise SystemExit(f"--image-size chỉ nhận {', '.join(IMAGE_SIZES)}")
    if size != "1K" and headless:
        raise SystemExit(f"--image-size {size} cần cửa sổ Chrome: chạy ẩn thì Flow báo "
                         "'Upscaling failed!'. Bỏ --headless hoặc dùng --image-size 1K")
    return size


def close_overlays(page):
    """Dismiss toasts ("...downloaded!"), banners and leftover menus."""
    for b in page.locator("button:has-text('Dismiss'), [aria-label*='dismiss' i], [aria-label*='close' i]").all():
        try:
            b.click(timeout=1000)
        except Exception:
            pass
    for _ in range(3):
        if page.locator(".cdk-overlay-backdrop").count() == 0:
            break
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)


def size_item_name(size):
    """Accessible name of a Download submenu item: "1K Original size", "2K Upscaled", ..."""
    return re.compile(rf"^\s*{re.escape(size)}\b")


def size_menu_item(page, size):
    """The `size` item of the open Download submenu (the last opened menu), else the first
    menuitem on the page whose name starts with `size`."""
    name = size_item_name(size)
    menus = page.get_by_role("menu")
    if menus.count():
        item = menus.last.get_by_role("menuitem", name=name)
        if item.count():
            return item.first
    return page.get_by_role("menuitem", name=name).first


def download_image(page, mid, size, timeout_s=180):
    """Tile menu > Download > `size` (2K = upscale, then Flow starts the download itself). Return the Download."""
    tile = page.locator(IMAGE_TILE).filter(has=page.locator(f"img[data-media-id='{mid}']"))
    tile.hover()
    tile.get_by_role("button", name="More options").click()
    page.get_by_role("menuitem", name=re.compile("Download")).click()
    got = []

    def on_download(d):  # Playwright needs a Python function, not a builtin like list.append
        got.append(d)

    page.on("download", on_download)
    try:
        size_menu_item(page, size).click()
        deadline = time.time() + timeout_s
        while not got:
            if page.get_by_text("Upscaling failed").count():
                raise RuntimeError(f"Flow: Upscaling failed ({size})")
            if time.time() > deadline:
                raise TimeoutError(f"no {size} download started")
            page.wait_for_timeout(500)
    finally:
        page.remove_listener("download", on_download)
    close_overlays(page)
    return got[0]


def generate_images(page, prompt, out, tag, timeout_s=240, strip_mark="crop", keep_raw=False, size="1K"):
    """Generate, then save every new tile. 1K fetches the tile's src (same bytes as menu > 1K);
    2K goes through the tile menu. The sparkle is then cropped by `finish_image`."""
    before = media_srcs(page)
    page.click(EDITOR)
    page.fill(EDITOR, prompt)
    page.click(GENERATE)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if set(media_srcs(page)) - set(before):
            time.sleep(3)  # let the other variants settle
            new = {k: v for k, v in media_srcs(page).items() if k not in before}
            saved = []
            for n, (mid, url) in enumerate(new.items(), 1):
                if size == "1K":
                    resp = page.context.request.get(url)
                    ext = ".jpg" if "jpeg" in resp.headers.get("content-type", "") else ".png"
                    f = out / f"{tag}_{n}_{mid[:8]}{ext}"
                    f.write_bytes(resp.body())
                else:
                    dl = download_image(page, mid, size)
                    f = out / f"{tag}_{n}_{mid[:8]}_{size}{Path(dl.suggested_filename).suffix or '.jpg'}"
                    dl.save_as(str(f))
                saved.append(finish_image(f, strip_mark, keep_raw))
            return saved
        time.sleep(2)
    raise TimeoutError("no new image appeared")


def finish_image(path, mode="crop", keep_raw=False):
    """Drop the corner sparkle on a file just downloaded.

    `off` does nothing. `fill` / `crop` are `imagefix.strip_mark` with
    `known_flow` set, because a fresh Flow download always has the sparkle
    in the fixed corner. `crop` therefore cuts that corner even when the
    detector misses it. `fill` still skips (and warns) when nothing is
    detected. With `keep_raw`, the untouched bytes are also written as
    `<stem>_raw<suffix>`, and only when the file actually changed.
    """
    path = Path(path)
    if mode == "off":
        return path
    original = path.read_bytes()
    try:
        from .imagefix import strip_mark as _strip
    except ImportError as e:
        raise SystemExit(
            "flow --strip-mark needs pillow and opencv-python-headless "
            "(pip install -e '.[webauto]')") from e
    _strip(path, mode, known_flow=True)
    if keep_raw and path.read_bytes() != original:
        path.with_name(path.stem + "_raw" + path.suffix).write_bytes(original)
    return path


def quality_item_name(quality):
    """Accessible name of a Download submenu quality item: "720p", "1080p", ..."""
    return re.compile(rf"^\s*{re.escape(quality)}\b", re.I)


def quality_menu_item(page, quality):
    """The `quality` item of the open Download submenu (the last opened menu), else the first
    menuitem on the page matching `quality`."""
    name = quality_item_name(quality)
    menus = page.get_by_role("menu")
    if menus.count():
        item = menus.last.get_by_role("menuitem", name=name)
        if item.count():
            return item.first
    return page.get_by_role("menuitem", name=name).first


def download_video_tile(page, tile, out_path, quality="720p", timeout_s=180):
    """Download a video tile via its More options menu > Download > quality."""
    tile.scroll_into_view_if_needed()
    tile.hover()
    page.wait_for_timeout(400)
    more_btn = tile.get_by_role("button", name=re.compile(r"More options|Tùy chọn khác|More", re.I))
    if not more_btn.count():
        more_btn = tile.locator("button[aria-label*='More'], button[aria-label*='options'], button[aria-label*='tùy chọn']")
    try:
        more_btn.first.click(timeout=8000)
    except Exception:
        tile.hover()
        more_btn.first.click(force=True, timeout=8000)
    page.wait_for_timeout(300)
    page.get_by_role("menuitem", name=re.compile(r"Download|Tải xuống", re.I)).first.click()
    with page.expect_download(timeout=timeout_s * 1000) as dl:
        quality_menu_item(page, quality).click()
    dl.value.save_as(str(out_path))
    close_overlays(page)
    return out_path


def generate_video(page, prompt, out, tag, quality="720p", timeout_s=900, strip_mark="crop", keep_raw=False):
    """Videos have no direct URL: use the tile menu > Download > quality (720p is the original, free)."""
    before = page.locator(VIDEO_DONE).count()
    failed_before = page.locator("flow-error-tile, .error-tile").count() + page.get_by_text(VIDEO_FAILED).count()
    page.click(EDITOR)
    page.fill(EDITOR, prompt)
    page.click(GENERATE)
    deadline = time.time() + timeout_s
    while page.locator(VIDEO_DONE).count() <= before:
        err_count = page.locator("flow-error-tile, .error-tile").count() + page.get_by_text(VIDEO_FAILED).count()
        if err_count > failed_before:
            err_msg = ""
            if page.locator("flow-error-tile").count():
                err_msg = page.locator("flow-error-tile").first.inner_text().replace("\n", " ")
            raise TimeoutError(f"Flow: video failed to generate ({err_msg or 'unknown error'})")
        if time.time() > deadline:
            raise TimeoutError("no new video appeared")
        time.sleep(5)
    time.sleep(2)
    saved = []
    for n in range(page.locator(VIDEO_DONE).count() - before):
        tile = page.locator("flow-video-tile").nth(n)  # newest tiles come first
        f = out / f"{tag}_{n + 1}_{quality}.mp4"
        try:
            download_video_tile(page, tile, f, quality=quality)
        finally:
            close_overlays(page)
        if strip_mark != "off":
            original = f.read_bytes() if keep_raw else None
            from .videofix import strip_video
            strip_video(f, strip_mark)
            if keep_raw and f.read_bytes() != original:
                f.with_name(f.stem + "_raw" + f.suffix).write_bytes(original)
        saved.append(f)
    return saved


def generate(prompts, out, mode="image", model=None, count=1, duration=6, ratio=None, res=None,
             quality="720p", image=None, timeout=None, headless=False, session=None, strip_mark="crop",
             keep_raw=False, image_size=None, max_per_project=2):
    """Generate for each (stem, prompt) in `prompts` inside Flow project(s); return saved files.

    `image` (video mode only) is uploaded once as the start frame, so every prompt animates that image.
    `strip_mark` applies to images (crop/fill/off) and videos (crop/delogo/off).
    `image_size` (image mode): 1K or 2K; None = 2K with a window, 1K headless.
    `max_per_project` (video mode): create a new project after N clips to avoid the 3rd-clip menu bug.
    """
    if image and mode != "video":
        raise SystemExit("--image needs --mode video")
    if mode == "video" and strip_mark == "fill":
        raise SystemExit("video --strip-mark chỉ nhận crop, delogo hoặc off")
    if mode == "image" and strip_mark == "delogo":
        raise SystemExit("image --strip-mark chỉ nhận crop, fill hoặc off")
    if mode == "image":
        image_size = image_size_for(image_size, headless)
        print("image size:", image_size)
    from playwright.sync_api import sync_playwright

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as p:
        ctx = launch(p, headless, session)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            new_project(page, headless)
            apply_settings(page, mode, model, count, duration, ratio, res)
            if image:
                set_start_frame(page, Path(image).resolve())
            clips_in_project = 0
            for stem, prompt in prompts:
                if mode == "video" and max_per_project and clips_in_project >= max_per_project:
                    print(f"[flow] reached {clips_in_project} clip(s) in project (max {max_per_project}), opening new project...")
                    new_project(page, headless)
                    apply_settings(page, mode, model, count, duration, ratio, res)
                    if image:
                        set_start_frame(page, Path(image).resolve())
                    clips_in_project = 0
                try:
                    if mode == "video":
                        got = generate_video(page, prompt, out, stem, quality, timeout or 900, strip_mark, keep_raw)
                        clips_in_project += len(got)
                    else:
                        got = generate_images(page, prompt, out, stem, timeout or 240, strip_mark, keep_raw,
                                              image_size)
                except TimeoutError:
                    (out / "fail.html").write_text(page.content(), encoding="utf-8")
                    try:
                        page.screenshot(path=str(out / "fail.png"), timeout=5000)  # can hang while a video plays
                    except Exception:
                        pass
                    raise
                print(f"{stem}: saved {len(got)} file(s)", *got, sep="\n  ")
                files += got
        finally:
            ctx.close()
    return files


def parse_shots_file(shots_path, default_ref=None):
    """Parse shots file: each line is 'name | prompt [| frame=<path>]'.

    Lines starting with '#' or empty lines are ignored.
    If frame is not specified, uses default_ref.
    """
    shots_file = Path(shots_path)
    if not shots_file.exists():
        raise SystemExit(f"shots file not found: {shots_path}")
    default_ref_path = Path(default_ref).resolve() if default_ref else None
    if default_ref_path and not default_ref_path.is_file():
        raise SystemExit(f"--ref file not found: {default_ref}")

    shots = []
    for line_num, raw_line in enumerate(shots_file.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if not parts or not parts[0]:
            continue
        name = parts[0]
        custom_frame = None
        prompt_parts = []
        for part in parts[1:]:
            if part.lower().startswith("frame="):
                custom_frame = part.split("=", 1)[1].strip()
            else:
                prompt_parts.append(part)
        prompt = " | ".join(prompt_parts) if prompt_parts else name

        if custom_frame:
            cf = Path(custom_frame)
            if cf.is_file():
                frame_path = cf.resolve()
            elif (shots_file.parent / custom_frame).is_file():
                frame_path = (shots_file.parent / custom_frame).resolve()
            else:
                raise SystemExit(f"line {line_num}: frame image not found: {custom_frame}")
        else:
            if not default_ref_path:
                raise SystemExit(f"line {line_num}: shot '{name}' has no frame= and no --ref provided")
            frame_path = default_ref_path

        shots.append({
            "name": name,
            "prompt": prompt,
            "frame": str(frame_path)
        })
    if not shots:
        raise SystemExit(f"no valid shots found in {shots_path}")
    return shots


def resolve_model_info(model_str):
    """Resolve model string to Flow UI model name, credit estimate, and default duration."""
    m = (model_str or "omni1.1").strip().lower()
    if "1.2" in m or "12" in m:
        return "Omni 1.2 Flash", 24, 8
    return "Omni 1.1 Flash", 10, 6


def shots_generate(shots, out, ref=None, model="omni1.1", ratio=None, res=None,
                   quality="720p", timeout=None, headless=False, session=None,
                   strip_mark="crop", keep_raw=False, max_per_project=2):
    """Generate image-to-video clips from a list of shots and write manifest.json."""
    from playwright.sync_api import sync_playwright

    model_name, est_credits_per_clip, duration = resolve_model_info(model)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    manifest_shots = []
    with sync_playwright() as p:
        ctx = launch(p, headless, session)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            current_frame = None
            clips_in_project = 0

            for shot in shots:
                name = shot["name"]
                prompt = shot["prompt"]
                frame = shot["frame"]
                target_file = out / f"{name}_1_{quality}.mp4"

                if target_file.is_file():
                    print(f"[shot] {name}: already exists ({target_file.name}), reusing")
                    manifest_shots.append({
                        "name": name,
                        "prompt": prompt,
                        "frame": str(frame),
                        "model": model_name,
                        "estimated_credits": est_credits_per_clip,
                        "file": target_file.name,
                        "ai_generated": True,
                    })
                    continue

                need_new_project = (
                    current_frame is None
                    or frame != current_frame
                    or (max_per_project and clips_in_project >= max_per_project)
                )

                if need_new_project:
                    if clips_in_project >= max_per_project and max_per_project:
                        print(f"[flow shots] reached {clips_in_project} clip(s) in project, starting fresh project...")
                    new_project(page, headless)
                    apply_settings(page, "video", model_name, count=1, duration=duration, ratio=ratio, res=res)
                    set_start_frame(page, Path(frame).resolve())
                    current_frame = frame
                    clips_in_project = 0

                try:
                    got = generate_video(page, prompt, out, name, quality=quality,
                                         timeout_s=timeout or 900, strip_mark=strip_mark,
                                         keep_raw=keep_raw)
                    clips_in_project += len(got)
                except TimeoutError:
                    (out / f"fail_{name}.html").write_text(page.content(), encoding="utf-8")
                    try:
                        page.screenshot(path=str(out / f"fail_{name}.png"), timeout=5000)
                    except Exception:
                        pass
                    raise

                saved_file = got[0] if got else None
                file_rel = str(saved_file.name) if saved_file else None
                manifest_shots.append({
                    "name": name,
                    "prompt": prompt,
                    "frame": str(frame),
                    "model": model_name,
                    "estimated_credits": est_credits_per_clip,
                    "file": file_rel,
                    "ai_generated": True,
                })
                print(f"[shot] {name}: saved {file_rel} (est. {est_credits_per_clip} credits)")

                # Save intermediate manifest
                manifest_data = {
                    "ref": str(Path(ref).resolve()) if ref else None,
                    "model": model_name,
                    "estimated_credits_per_clip": est_credits_per_clip,
                    "total_estimated_credits": len(manifest_shots) * est_credits_per_clip,
                    "ai_generated": True,
                    "shots": manifest_shots,
                }
                (out / "manifest.json").write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        finally:
            ctx.close()

    manifest_data = {
        "ref": str(Path(ref).resolve()) if ref else None,
        "model": model_name,
        "estimated_credits_per_clip": est_credits_per_clip,
        "total_estimated_credits": len(manifest_shots) * est_credits_per_clip,
        "ai_generated": True,
        "shots": manifest_shots,
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"manifest written to {manifest_path} (total {manifest_data['total_estimated_credits']} credits)")
    return manifest_shots


def add_parser(sub):
    ap = sub.add_parser("flow", help="Google Flow: generate images / videos (Playwright)")
    s = ap.add_subparsers(dest="cmd", required=True)
    s.add_parser("login", help="sign in to Google once in the webauto profile").set_defaults(func=lambda a: login())
    e = s.add_parser("export-session", help="save the signed-in profile's session to a file, for --session on a server")
    e.add_argument("--out", required=True)
    e.set_defaults(func=lambda a: export_session(a.out))
    g = s.add_parser("generate", help="generate and download")
    g.add_argument("--mode", choices=["image", "video"], default="image")
    src = g.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompts-file", help="'name | prompt' per line, '#' comments")
    g.add_argument("--out", default=str(default_out("flow")))
    g.add_argument("--model", help="substring of the model name (default Nano Banana Pro / Omni 1.1 Flash)")
    g.add_argument("--count", type=int, choices=[1, 2, 3, 4], default=1, help="outputs per prompt")
    g.add_argument("--duration", type=int, choices=[4, 6, 8, 10], default=6, help="video seconds")
    g.add_argument("--ratio", choices=["16:9", "4:3", "1:1", "3:4", "9:16"])
    g.add_argument("--res", choices=["360p", "720p"], help="video generation resolution")
    g.add_argument("--quality", choices=["720p", "1080p", "4K"], default="720p", help="video download quality")
    g.add_argument("--image-size", choices=list(IMAGE_SIZES),
                   help="image download size: 1K = original 1376 px (preview src), 2K = Flow upscale 2752 px "
                        "(free, ~15 s, needs a window). Default 2K, or 1K with --headless")
    g.add_argument("--image", help="video mode: start-frame image (image-to-video)")
    g.add_argument("--timeout", type=int, help="seconds per prompt (default 240 image / 900 video)")
    g.add_argument("--headless", action="store_true", help="no Chrome window (the profile must be signed in already)")
    g.add_argument("--session", help="session file from `flow export-session` instead of the profile "
                   "(default: WEBAUTO_FLOW_SESSION)")
    g.add_argument("--strip-mark", choices=["crop", "fill", "delogo", "off"], default="crop",
                   help="remove the Gemini sparkle. Image: crop/fill/off; crop cuts the known corner box even if "
                        "detection misses, keeping aspect (measured 1K/2K 16:9 and 9:16 cut right OR bottom, other "
                        "sizes right AND bottom); fill inpaints only a detected sparkle, else warns and leaves the "
                        "file. Video: crop (cut right and bottom, scale back) / delogo / off. Default crop")
    g.add_argument("--keep-raw", action="store_true",
                   help="also keep the untouched download as *_raw when a sparkle was removed")
    g.add_argument("--max-per-project", type=int, default=2,
                   help="max video clips per Flow project before creating a new one (default 2, avoids 3rd clip bug)")
    g.set_defaults(func=_run_generate)

    sh = s.add_parser("shots", help="generate video shots from reference image and shots file")
    sh.add_argument("--ref", required=True, help="reference character image (image-to-video)")
    sh.add_argument("--shots", required=True, help="path to shots file ('name | prompt [| frame=<path>]')")
    sh.add_argument("--out", default=str(default_out("flow")), help="output directory")
    sh.add_argument("--model", default="omni1.1", help="omni1.1 / Omni 1.1 Flash (default 10 credit/6s) or omni12 / Omni 1.2 Flash (24 credit/8s)")
    sh.add_argument("--ratio", choices=["16:9", "4:3", "1:1", "3:4", "9:16"])
    sh.add_argument("--res", choices=["360p", "720p"], help="video generation resolution")
    sh.add_argument("--quality", choices=["720p", "1080p", "4K"], default="720p", help="video download quality")
    sh.add_argument("--timeout", type=int, help="seconds per shot (default 900)")
    sh.add_argument("--headless", action="store_true", help="no Chrome window")
    sh.add_argument("--session", help="session file from `flow export-session`")
    sh.add_argument("--strip-mark", choices=["crop", "delogo", "off"], default="crop", help="remove the Gemini sparkle (default crop)")
    sh.add_argument("--keep-raw", action="store_true", help="also keep the untouched download as *_raw")
    sh.add_argument("--max-per-project", type=int, default=2, help="max clips per Flow project before creating a new one (default 2)")
    sh.set_defaults(func=_run_shots)


def _run_generate(a):
    prompts = [("p1", a.prompt)] if a.prompt else parse_prompts(a.prompts_file)
    generate(prompts, a.out, a.mode, a.model, a.count, a.duration, a.ratio, a.res, a.quality, a.image, a.timeout,
             a.headless, a.session, strip_mark=a.strip_mark, keep_raw=a.keep_raw, image_size=a.image_size,
             max_per_project=a.max_per_project)


def _run_shots(a):
    shots = parse_shots_file(a.shots, a.ref)
    shots_generate(shots, a.out, ref=a.ref, model=a.model, ratio=a.ratio, res=a.res,
                   quality=a.quality, timeout=a.timeout, headless=a.headless, session=a.session,
                   strip_mark=a.strip_mark, keep_raw=a.keep_raw, max_per_project=a.max_per_project)
