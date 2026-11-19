"""Chat với Gemini web (gemini.google.com) bằng Playwright, không tốn token API.

    python scripts/gemini_chat.py login                         # mở Chrome hồ sơ riêng, chủ kênh đăng nhập Google một lần
    python scripts/gemini_chat.py ask <prompt.md> --out <kết quả.md> [--model Neon] [--thinking High] [--chat <url>]

- Hồ sơ Chrome riêng ở `~/creator_v2/gemini_profile` (ngoài repo, tách khỏi Chrome thường nên không giành tab
  với GrokBot / Browsentic). Không in cookie, không ghi log phiên đăng nhập.
- `ask` mở cuộc chat MỚI (mặc định) hoặc tiếp cuộc chat ở `--chat <url>` (vd viết tiếp CH02–CH08 sau CH00–CH01),
  dán nguyên file prompt, chờ Gemini viết xong (nút Dừng tắt và chữ đứng yên), lấy bản Markdown gốc qua nút
  "Sao chép" (giữ `##`), lưu `--out` và in link cuộc chat để lần sau dùng `--chat`.
- Mặc định chọn Neon · thinking High: so 7 tổ hợp trên cùng prompt Long FS 19/11, Neon bám brief tốt nhất
  (Hydrogen nhẹ hơn, Auto bỏ sót ý bắt buộc). Hydrogen nhanh hơn ~2 lần, dùng khi cần nháp nhanh.
- Chạy chậm như người, mỗi lần một prompt.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

PROFILE = Path(os.environ.get("GEMINI_PROFILE") or Path.home() / "creator_v2" / "gemini_profile")
HOME = "https://gemini.google.com/app"
INPUT = "rich-textarea div[contenteditable=true]"
RESPONSE = "model-response"
STOP = re.compile(r"dừng|stop", re.I)
COPY = re.compile(r"sao chép|copy", re.I)


def browser(p, headless: bool = False):
    PROFILE.mkdir(parents=True, exist_ok=True)
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE), channel="chrome", headless=headless,
        viewport={"width": 1400, "height": 1000}, permissions=["clipboard-read", "clipboard-write"],
        args=["--disable-blink-features=AutomationControlled"])
    return ctx, (ctx.pages[0] if ctx.pages else ctx.new_page())


def stable_done(samples: list[str], busy: bool, need: int = 4) -> bool:
    """Xong khi không còn nút Dừng và `need` lần đọc cuối giống nhau, khác rỗng."""
    if busy or len(samples) < need:
        return False
    tail = samples[-need:]
    return bool(tail[-1].strip()) and all(s == tail[-1] for s in tail)


MODE_BTN = "[data-test-id='bard-mode-menu-button']"


def pick_mode(page, model: str | None, thinking: str | None) -> str:
    """Chọn model (Auto / Hydrogen / Neon…) và mức Thinking (Low / Medium / High) theo chữ trên menu.
    Trả về nhãn đã chọn để ghi vào kết quả. Không truyền gì thì giữ lựa chọn hiện có của tài khoản."""
    btn = page.locator(MODE_BTN).first
    if model:
        btn.click()
        time.sleep(1)
        opt = page.locator("[data-test-id^='bard-mode-option-']").filter(has_text=re.compile(model, re.I))
        if not opt.count():
            page.keyboard.press("Escape")
            raise SystemExit(f"menu không có model khớp '{model}'")
        opt.first.click()
        time.sleep(1)
    if thinking:
        btn.click()
        time.sleep(1)
        page.get_by_text(re.compile(r"^\s*(thinking level|mức suy nghĩ)", re.I)).first.click()
        time.sleep(1)
        lvl = page.get_by_text(re.compile(rf"^\s*{re.escape(thinking)}\s*$", re.I))
        if not lvl.count():
            page.keyboard.press("Escape")
            raise SystemExit(f"menu Thinking không có mức '{thinking}'")
        lvl.first.click()
        time.sleep(1)
        page.keyboard.press("Escape")
    label = model or btn.inner_text().strip()
    return label + (f" · thinking {thinking}" if thinking else "")


def clean(text: str) -> str:
    """Bỏ nhãn giao diện Gemini đôi khi dính vào bản chép."""
    text = re.sub(r"^\s*Gemini (đã nói|said)\s*\n", "", text)
    return text.strip() + "\n"


def cmd_login(a) -> int:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx, page = browser(p)
        page.goto(HOME)
        print("Đăng nhập Google trong cửa sổ Chrome vừa mở, thấy ô chat Gemini thì đóng cửa sổ.")
        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
        ctx.close()
    return 0


def cmd_ask(a) -> int:
    from playwright.sync_api import sync_playwright
    prompt = Path(a.prompt).read_text(encoding="utf-8")
    with sync_playwright() as p:
        ctx, page = browser(p, headless=a.headless)
        page.goto(a.chat or HOME)
        try:
            page.wait_for_selector(INPUT, timeout=60_000)
        except Exception:
            ctx.close()
            raise SystemExit("không thấy ô chat Gemini: chưa đăng nhập? chạy `gemini_chat.py login`")
        mode = pick_mode(page, a.model, a.thinking)
        print(f"model: {mode}")
        before = page.locator(RESPONSE).count()
        box = page.locator(INPUT).first
        box.click()
        box.fill(prompt)
        time.sleep(1.5)
        box.press("Enter")
        t0 = time.time()
        while page.locator(RESPONSE).count() <= before:
            if time.time() - t0 > 120:
                ctx.close()
                raise SystemExit("Gemini không nhận prompt (không có câu trả lời mới sau 120 s)")
            time.sleep(2)
        last = page.locator(RESPONSE).last
        samples: list[str] = []
        while True:
            if time.time() - t0 > a.timeout:
                ctx.close()
                raise SystemExit(f"quá {a.timeout} s mà Gemini chưa viết xong")
            busy = page.get_by_role("button", name=STOP).count() > 0
            samples.append(last.inner_text())
            if stable_done(samples, busy):
                break
            time.sleep(3)
        text = ""
        try:
            last.hover()
            last.get_by_role("button", name=COPY).last.click()
            time.sleep(1)
            text = page.evaluate("() => navigator.clipboard.readText()")
        except Exception as e:
            print(f"không chép được bản Markdown ({type(e).__name__}), lấy chữ hiển thị", file=sys.stderr)
        text = clean(text or samples[-1])
        url = page.url
        ctx.close()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"đã lưu {out} ({len(text.split())} chữ)")
    print(f"chat: {url}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login").set_defaults(fn=cmd_login)
    q = sub.add_parser("ask")
    q.add_argument("prompt")
    q.add_argument("--out", required=True)
    q.add_argument("--chat", help="link cuộc chat cũ để viết tiếp")
    q.add_argument("--model", default="Neon", help="chữ trên menu model: Neon (mặc định, thắng lượt so 19/11), Hydrogen, Auto; '' = giữ như tài khoản")
    q.add_argument("--thinking", default="High", help="Low / Medium / High (mặc định High); '' = giữ như tài khoản")
    q.add_argument("--timeout", type=int, default=900)
    q.add_argument("--headless", action="store_true")
    q.set_defaults(fn=cmd_ask)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
