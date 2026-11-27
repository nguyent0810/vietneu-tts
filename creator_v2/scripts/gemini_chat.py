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
import random
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROFILE = Path(os.environ.get("GEMINI_PROFILE") or Path.home() / "creator_v2" / "gemini_profile")
HOME = "https://gemini.google.com/app"
INPUT = "rich-textarea div[contenteditable=true]"
RESPONSE = "model-response"
QUERY = "user-query"
STOP = re.compile(r"dừng|stop", re.I)
COPY = re.compile(r"sao chép|copy", re.I)
SERVER_ERROR = re.compile(r"an error occurred|something went wrong|đã xảy ra lỗi|có lỗi xảy ra", re.I)


def is_server_error(page) -> bool:
    """True when Gemini displays one of its server-side error messages.

    Text of the user's own prompt (user-query, composer) is removed first, so a prompt that
    happens to contain "An error occurred" is not mistaken for a Gemini error (review 153)."""
    try:
        body = page.locator("body").inner_text()
        for sel in (QUERY, INPUT):
            for i in range(page.locator(sel).count()):
                body = body.replace(page.locator(sel).nth(i).inner_text(), "")
        return bool(SERVER_ERROR.search(body))
    except Exception:
        return False


def is_home_without_query(page) -> bool:
    """Detect a failed chat reset: home URL and an empty composer with no query."""
    try:
        home_url = not re.search(r"/app/[0-9a-f]{8,}", page.url or "", re.I)
        empty_box = not page.locator(INPUT).first.inner_text().strip()
        return home_url and empty_box and page.locator(QUERY).count() == 0
    except Exception:
        return False


NEW_CHAT = re.compile(r"new chat|cuộc trò chuyện mới|chat mới", re.I)


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip()


def ensure_fresh(page) -> None:
    """27/11: mở HOME đôi khi hiện lại cuộc chat cũ (có sẵn câu hỏi + trả lời) -> bấm Chat mới;
    vẫn còn chat cũ thì dừng, không gửi (tránh chép nhầm câu trả lời cũ)."""
    time.sleep(3)
    if page.locator(QUERY).count() == 0 and page.locator(RESPONSE).count() == 0:
        return
    for role in ("link", "button"):
        btn = page.get_by_role(role, name=NEW_CHAT)
        if btn.count():
            btn.first.click()
            break
    time.sleep(3)
    if page.locator(QUERY).count() or page.locator(RESPONSE).count():
        raise SystemExit(f"không mở được chat mới (trang vẫn là chat cũ {page.url}); không gửi prompt")


def query_matches(page, prompt: str) -> bool:
    """Câu hỏi cuối trong chat phải là prompt vừa gửi (so 80 ký tự đầu, bỏ khoảng trắng)."""
    try:
        q = _norm(page.locator(QUERY).last.inner_text())
    except Exception:
        return False
    head = _norm(prompt)[:80]
    return bool(head) and head[:60] in q


def retry_thinking(level: str | None, attempt: int, retries: int, no_downgrade: bool = False) -> str | None:
    """Lower High to Medium on the final attempt after a retryable failure."""
    if no_downgrade or attempt != retries or not level:
        return level
    return {"high": "Medium", "medium": "Low"}.get(level.lower(), level)


def browser(p, headless: bool = False):
    PROFILE.mkdir(parents=True, exist_ok=True)
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE), channel="chrome", headless=headless,
        viewport={"width": 1400, "height": 1000}, permissions=["clipboard-read", "clipboard-write"],
        args=["--disable-blink-features=AutomationControlled"])
    return ctx, (ctx.pages[0] if ctx.pages else ctx.new_page())


THINKING_ONLY = re.compile(r"^\s*(?:[^\n]{0,120}\n)?\s*Gemini (?:đã nói|said)\s*$", re.I)


def looks_like_thinking(text: str) -> bool:
    """Gemini đang nghĩ chỉ hiện tiêu đề "Figuring out…" + "Gemini said" (#529, 24/11)."""
    return bool(THINKING_ONLY.match(text.strip()))


def stable_done(samples: list[str], busy: bool, need: int = 4, copy_ready: bool = True, min_words: int = 0) -> bool:
    """Xong khi: không còn nút Dừng, khung trả lời đã có nút Sao chép (giao diện chỉ hiện khi viết xong),
    `need` lần đọc cuối giống nhau, đủ `min_words` chữ và không phải chỉ tiêu đề đang-nghĩ.
    #529: giao diện mới bỏ tên nút Dừng nên chỉ dựa vào chữ đứng yên thì lưu nhầm tiêu đề thinking."""
    if busy or not copy_ready or len(samples) < need:
        return False
    tail = samples[-need:]
    text = tail[-1]
    if not text.strip() or looks_like_thinking(text) or len(text.split()) < min_words:
        return False
    return all(s == text for s in tail)


def chat_id(url: str) -> str:
    """Mã cuộc chat trong link gemini.google.com/app/<id> (rỗng nếu là chat mới)."""
    m = re.search(r"/app/([0-9a-f]{8,})", url or "")
    return m.group(1) if m else ""


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
        if a.chat and chat_id(a.chat) and chat_id(page.url) != chat_id(a.chat):
            # #529: bị chuyển sang chat khác -> viết tiếp nhầm đề tài. Dừng, không gửi.
            ctx.close()
            raise SystemExit(f"không mở được đúng cuộc chat {a.chat} (đang ở {page.url}); không gửi prompt")
        if not a.chat:
            ensure_fresh(page)
        total = a.retries + 1
        text = url = ""
        last_reason = ""
        for attempt in range(1, total + 1):
            prev_reason, last_reason = last_reason, ""  # mỗi lượt tính lại; lượt sau thành công không bị coi là lỗi
            if attempt > 1:
                print(f"Thử lần {attempt}/{total}: mở chat mới; chờ 60–120 giây sau lỗi Gemini ({prev_reason})")
                page.goto(HOME)
                time.sleep(random.uniform(60, 120))
                ensure_fresh(page)
            level = retry_thinking(a.thinking, attempt, total, a.no_downgrade)
            if attempt == total and level != a.thinking:
                print(f"Thử lần {attempt}/{total}: hạ thinking {a.thinking} → {level}")
            mode = pick_mode(page, a.model, level)
            print(f"Lần thử {attempt}/{total}: gửi prompt ({mode})")
            before = page.locator(RESPONSE).count()
            asked = page.locator(QUERY).count()
            box = page.locator(INPUT).first
            box.click()
            box.fill(prompt)
            time.sleep(1.5)
            box.press("Enter")
            t0 = time.time()
            samples: list[str] = []
            last = None
            while True:
                # Chỉ dò chữ lỗi khi Gemini CHƯA trả lời: bài viết hay tiêu đề chat có thể chứa "đã xảy ra lỗi".
                if page.locator(RESPONSE).count() <= before and is_server_error(page):
                    last_reason = "thông báo lỗi phía Gemini"
                    break
                # Gemini sometimes discards the request and returns to its empty home page.
                if time.time() - t0 > 10 and is_home_without_query(page) and page.locator(QUERY).count() <= asked:
                    last_reason = "quay về trang chủ, prompt không còn trong chat"
                    break
                if page.locator(RESPONSE).count() > before:
                    last = page.locator(RESPONSE).last
                    busy = page.get_by_role("button", name=STOP).count() > 0
                    copy_ready = last.get_by_role("button", name=COPY).count() > 0
                    samples.append(last.inner_text())
                    if stable_done(samples, busy, copy_ready=copy_ready, min_words=a.min_words):
                        break
                else:
                    accepted = page.locator(QUERY).count() > asked or page.get_by_role("button", name=STOP).count() > 0
                    if not accepted and time.time() - t0 > 120:
                        # 27/11: Gemini có lúc tạo chat rồi bỏ lượt mà không hiện chữ lỗi -> thử lại như lỗi phía Gemini.
                        last_reason = "câu hỏi không vào chat sau 120 s"
                        break
                if time.time() - t0 > a.timeout:
                    ctx.close()
                    raise SystemExit(f"quá {a.timeout} s mà Gemini chưa viết xong")
                if last is None or not samples or not stable_done(samples, page.get_by_role("button", name=STOP).count() > 0,
                                                                   copy_ready=last.get_by_role("button", name=COPY).count() > 0,
                                                                   min_words=a.min_words):
                    time.sleep(2)
            if last_reason:
                print(f"Lần thử {attempt}/{total} thất bại: {last_reason}")
                if attempt < total:
                    continue
                ctx.close()
                raise SystemExit(f"Gemini không trả lời sau {total} lần (lần cuối: {last_reason})")
            if not query_matches(page, prompt):
                ctx.close()
                raise SystemExit("câu trả lời không thuộc prompt vừa gửi (trang đang ở chat khác): không lưu")
            text = ""
            try:
                last.hover()
                last.get_by_role("button", name=COPY).last.click()
                time.sleep(1)
                text = page.evaluate("() => navigator.clipboard.readText()")
            except Exception as e:
                print(f"không chép được bản Markdown ({type(e).__name__}), lấy chữ hiển thị", file=sys.stderr)
            if text and _norm(text)[:120] and _norm(text)[:120][:60] not in _norm(samples[-1]):
                print("bản chép từ clipboard không khớp câu trả lời đang hiện: dùng chữ hiển thị", file=sys.stderr)
                text = ""
            text = clean(text or samples[-1])
            url = page.url
            break
        ctx.close()
    if looks_like_thinking(text) or len(text.split()) < a.min_words:
        raise SystemExit(f"câu trả lời chỉ có {len(text.split())} chữ (tiêu đề đang nghĩ?): không lưu")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"đã lưu {out} ({len(text.split())} chữ)")
    print(f"chat: {url}")
    return 0


def main() -> int:
    from factory.console import utf8_console
    utf8_console()
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
    q.add_argument("--min-words", type=int, default=30, help="câu trả lời ngắn hơn thì coi là chưa xong / lỗi (#529)")
    q.add_argument("--headless", action="store_true")
    q.add_argument("--retries", type=int, default=2, help="số lần thử lại sau lỗi Gemini (mặc định 2)")
    q.add_argument("--no-downgrade", action="store_true", help="không hạ thinking ở lần thử cuối")
    q.set_defaults(fn=cmd_ask)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
