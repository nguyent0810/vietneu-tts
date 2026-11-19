"""Chạy tool Google Flow "Viết lời đọc" bằng Playwright, không tốn token LLM (#497).

    python scripts/flow_viet_loi.py login                      # mở Chrome hồ sơ riêng, chủ kênh đăng nhập Google một lần
    python scripts/flow_viet_loi.py find                       # tìm tool trong các project mới nhất, lưu link
    python scripts/flow_viet_loi.py probe                      # dò giao diện tool -> output/flow/probe/
    python scripts/flow_viet_loi.py run CL vidocq <thư-mục-input> [--phase ch00-01|full] [--title "..."]

- Link tool: `--url`, hoặc biến môi trường `FLOW_VIET_LOI_URL`, hoặc `output/flow/config.json` {"url": "..."}.
  Không có link (máy mới) hoặc link hỏng: script tự vào các project mới nhất, mở trang Tools, bấm
  "Viết lời đọc" và lưu link vào config.json. Không ghi link vào repo (repo public).
- Hồ sơ Chrome riêng ở `%LOCALAPPDATA%/creator_v2/flow_profile` (ngoài repo). Không in cookie, không ghi log phiên đăng nhập.
- Thư mục input chứa 4 file theo thứ tự tên: hồ sơ truyện, bảng dữ kiện, giọng mẫu, dàn chương
  (mẫu: `output/test_pack_viet_loi/1_ho_so_truyen.md` … `4_dan_chuong.txt`).
- Lượt `full` chạy cả hai nút: "Viết CH00 + CH01" rồi "Viết các chương còn lại".
- Kết quả lưu `output/script_inbox/<KÊNH>_<slug>_<YYYY-MM-DD>_<phần>.md` (đã có thì thêm _v2, _v3…),
  rồi chạy `scripts/prose_to_script.py` để kiểm định dạng.
- Chạy chậm như người, mỗi lần một bài: Google chặn "unusual activity" khi chạy dồn.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PROFILE = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "creator_v2" / "flow_profile"
CONFIG = ROOT / "output" / "flow" / "config.json"
PROBE = ROOT / "output" / "flow" / "probe"
INBOX = ROOT / "output" / "script_inbox"

# Nhãn trong tool (khớp mờ, không phân biệt hoa thường). Sửa ở đây nếu tool đổi chữ.
FIELDS = ["hồ sơ truyện", "bảng dữ kiện", "giọng mẫu", "dàn chương"]
BTN_FIRST = re.compile(r"viết (mở đầu|ch00)", re.I)
BTN_REST = re.compile(r"viết các chương còn lại", re.I)
BUSY = re.compile(r"đang viết", re.I)
TAB_RESULT = re.compile(r"kết quả", re.I)
TAB_INPUT = re.compile(r"màn hình nhập", re.I)
BTN_DOWNLOAD = re.compile(r"tải về|tải xuống|download", re.I)
WRITE_TIMEOUT = 45 * 60
HOME = "https://flow.google.com/"
TOOL_NAME = re.compile(r"viết lời đọc", re.I)


def tool_url(arg: str | None) -> str | None:
    url = arg or os.environ.get("FLOW_VIET_LOI_URL")
    if not url and CONFIG.is_file():
        url = json.loads(CONFIG.read_text(encoding="utf-8")).get("url")
    return url or None


def find_tool(page, max_projects: int = 6) -> str:
    """Không có link: vào trang chủ Flow, xét các project mới nhất, mở trang Tools và bấm "Viết lời đọc".
    Link tìm được lưu vào output/flow/config.json (gitignored) để lần sau mở thẳng."""
    page.goto(HOME)
    pause(12)
    ids = list(dict.fromkeys(re.findall(r"/project/([0-9a-f-]{36})", page.content())))
    if not ids:
        raise SystemExit("trang chủ Flow không có project nào (chưa đăng nhập? chạy lệnh login)")
    for pid in ids[:max_projects]:
        page.goto(f"{HOME}project/{pid}/tools")
        pause(10)
        hit = page.get_by_text(TOOL_NAME)
        if not hit.count():
            continue
        hit.last.click()
        t0 = time.time()
        while "/tool/" not in page.url and time.time() - t0 < 30:
            pause(1)
        if "/tool/" in page.url:
            url = page.url.split("?")[0]
            CONFIG.parent.mkdir(parents=True, exist_ok=True)
            CONFIG.write_text(json.dumps({"url": url}), encoding="utf-8")
            print(f"đã tìm thấy tool trong project {pid[:8]}…, lưu link vào {CONFIG.relative_to(ROOT)}")
            return url
    raise SystemExit(f"không thấy tool \"Viết lời đọc\" trong {min(len(ids), max_projects)} project mới nhất")


def open_tool(page, arg: str | None):
    """Mở tool và trả frame giao diện. Link lưu sẵn mà hỏng (tool bị dựng lại) thì tự tìm lại."""
    url = tool_url(arg)
    if url:
        page.goto(url)
        try:
            return applet(page, timeout=60)
        except SystemExit:
            if arg:
                raise
            print("link đã lưu không mở được tool, tìm lại trong các project mới nhất…")
    find_tool(page)
    return applet(page)


def browser(p, headless: bool = False):
    PROFILE.mkdir(parents=True, exist_ok=True)
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE), channel="chrome", headless=headless, accept_downloads=True,
        viewport={"width": 1600, "height": 1000}, args=["--disable-blink-features=AutomationControlled"])
    return ctx, (ctx.pages[0] if ctx.pages else ctx.new_page())


def pause(s: float = 1.5) -> None:
    time.sleep(s)


def applet(page, timeout: float = 90):
    """Khung chứa giao diện tool: frame (kể cả lồng nhau) có nút viết hoặc nhãn hồ sơ truyện."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        for fr in page.frames:
            if fr == page.main_frame:
                continue
            try:
                if fr.get_by_text(re.compile("hồ sơ truyện|viết lời đọc", re.I)).count():
                    return fr
            except Exception:
                pass
        pause(2)
    raise SystemExit("không thấy giao diện tool trong iframe (chưa đăng nhập, hoặc link sai?)")


def cmd_login(a) -> int:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx, page = browser(p)
        page.goto(tool_url(a.url) or HOME)
        print("Đăng nhập Google trong cửa sổ Chrome vừa mở, vào được trang chủ Flow thì đóng cửa sổ.")
        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
        ctx.close()
    return 0


def cmd_find(a) -> int:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx, page = browser(p, headless=a.headless)
        find_tool(page)
        applet(page)
        print("mở được giao diện tool")
        ctx.close()
    return 0


def cmd_probe(a) -> int:
    from playwright.sync_api import sync_playwright
    PROBE.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx, page = browser(p)
        fr = open_tool(page, a.url)
        pause(3)
        page.screenshot(path=str(PROBE / "page.png"))
        info = {"frames": [f.url.split("?")[0] for f in page.frames], "applet": fr.url.split("?")[0]}
        info["controls"] = fr.evaluate("""() => [...document.querySelectorAll(
            'button, textarea, input, select, [role=tab], [role=button], [contenteditable=true]')].map(e => ({
            tag: e.tagName.toLowerCase(), type: e.type || null, id: e.id || null,
            text: (e.innerText || e.value || e.placeholder || e.getAttribute('aria-label') || '').trim().slice(0, 80),
            options: e.tagName === 'SELECT' ? [...e.options].map(o => o.text) : undefined,
            label: (e.closest('section,div')?.querySelector('h1,h2,h3,h4,label,span')?.innerText || '').trim().slice(0, 60),
            visible: !!(e.offsetWidth || e.offsetHeight)}))""")
        (PROBE / "controls.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(info['controls'])} control -> {PROBE / 'controls.json'}")
        ctx.close()
    return 0


def fill_field(fr, label: str, text: str) -> None:
    """Điền textarea nằm dưới nhãn `label` (khối gần nhất chứa cả nhãn và một textarea)."""
    box = fr.locator("div,section").filter(has_text=re.compile(label, re.I)).filter(has=fr.locator("textarea")).last
    area = box.locator("textarea").first
    area.fill(text)
    pause()


def click(fr, pattern) -> None:
    fr.get_by_role("button", name=pattern).first.click()
    pause()


def wait_written(fr) -> None:
    t0 = time.time()
    pause(5)
    while time.time() - t0 < WRITE_TIMEOUT:
        if not fr.get_by_role("button", name=BUSY).count():
            return
        pause(10)
    raise SystemExit(f"tool viết quá {WRITE_TIMEOUT // 60} phút")


def take_result(page, fr) -> str:
    """Bấm tải về ở tab kết quả; không có nút tải thì đọc chữ trong ô kết quả."""
    try:
        fr.get_by_role("button", name=TAB_RESULT).first.click()
        pause(2)
    except Exception:
        pass
    btn = fr.get_by_role("button", name=BTN_DOWNLOAD)
    if btn.count():
        with page.expect_download(timeout=60_000) as dl:
            btn.first.click()
        return Path(dl.value.path()).read_text(encoding="utf-8")
    areas = fr.locator("textarea")
    texts = [areas.nth(i).input_value() for i in range(areas.count())]
    best = max(texts, key=lambda t: t.count("## CH"), default="")
    if "## CH" not in best:
        raise SystemExit("không lấy được kết quả: không có nút tải về và không ô nào chứa '## CH'")
    return best


def tidy(text: str) -> str:
    """Sửa lỗi định dạng hay gặp của tool, không đổi chữ: [PD] thứ hai khi thẻ đang mở = [/PD]; bỏ ** * _ in đậm/nghiêng."""
    out, open_ = [], False
    for part in re.split(r"(\[/?PD\])", text):
        if part == "[PD]":
            part = "[/PD]" if open_ else "[PD]"
            open_ = not open_
        elif part == "[/PD]":
            open_ = False
        out.append(part)
    text = "".join(out)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])[*_]([^*_\n]+?)[*_](?![\w*])", r"\1", text)
    return text


def save(channel: str, slug: str, phase: str, text: str) -> Path:
    INBOX.mkdir(parents=True, exist_ok=True)
    base = f"{channel}_{slug}_{dt.date.today().isoformat()}_{phase}"
    out, n = INBOX / f"{base}.md", 1
    while out.exists():
        n += 1
        out = INBOX / f"{base}_v{n}.md"
    out.write_text(tidy(text.replace("\r\n", "\n")), encoding="utf-8")
    return out


def cmd_run(a) -> int:
    from playwright.sync_api import sync_playwright
    files = sorted(p for p in Path(a.inputs).iterdir() if p.is_file())
    if len(files) < 4:
        raise SystemExit(f"{a.inputs}: cần 4 file (hồ sơ, dữ kiện, giọng mẫu, dàn chương), có {len(files)}")
    texts = [f.read_text(encoding="utf-8") for f in files[:4]]
    with sync_playwright() as p:
        ctx, page = browser(p, headless=a.headless)
        fr = open_tool(page, a.url)
        pause(3)
        try:
            fr.get_by_role("button", name=TAB_INPUT).first.click()
            pause()
        except Exception:
            pass
        sel = fr.locator("select").first
        opts = sel.locator("option").all_inner_texts()
        pick = next((o for o in opts if o.strip().upper().startswith(a.channel.upper())), None)
        if not pick:
            raise SystemExit(f"tool không có kênh {a.channel}: {opts}")
        sel.select_option(label=pick)
        pause()
        fr.locator("input[type=text], input:not([type])").first.fill(a.title or a.slug)
        pause()
        for label, text in zip(FIELDS, texts):
            fill_field(fr, label, text)
        click(fr, BTN_FIRST)
        wait_written(fr)
        if a.phase == "full":
            fr.get_by_role("button", name=TAB_INPUT).first.click() if fr.get_by_role("button", name=TAB_INPUT).count() else None
            pause(2)
            click(fr, BTN_REST)
            wait_written(fr)
        text = take_result(page, fr)
        ctx.close()
    out = save(a.channel.upper(), a.slug, a.phase, text)
    print(f"đã lưu {out.relative_to(ROOT)}")
    chk = ROOT / "output" / "flow" / "check_script.md"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "prose_to_script.py"), str(out), str(chk)],
                       capture_output=True, text=True, encoding="utf-8")
    print((r.stdout + r.stderr).strip()[-1500:])
    return r.returncode


def main() -> int:
    from factory.console import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("login", "find", "probe", "run"):
        s = sub.add_parser(name)
        s.add_argument("--url")
    sub.choices["find"].add_argument("--headless", action="store_true")
    r = sub.choices["run"]
    r.add_argument("channel")
    r.add_argument("slug", help="đề tài không dấu, vd vidocq")
    r.add_argument("inputs", help="thư mục 4 file input")
    r.add_argument("--phase", choices=["ch00-01", "full"], default="ch00-01")
    r.add_argument("--title", help="tên đề tài hiện trong tool (mặc định = slug)")
    r.add_argument("--headless", action="store_true")
    a = ap.parse_args()
    return {"login": cmd_login, "find": cmd_find, "probe": cmd_probe, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
