import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from gemini_chat import clean, stable_done, is_server_error, is_home_without_query, retry_thinking


def test_not_done_while_busy():
    assert not stable_done(["a", "a", "a", "a"], busy=True)


def test_not_done_while_text_changes():
    assert not stable_done(["a", "ab", "abc", "abcd"], busy=False)


def test_done_when_stable():
    assert stable_done(["x", "abc", "abc", "abc", "abc"], busy=False)


def test_empty_text_never_done():
    assert not stable_done(["", "", "", ""], busy=False)


def test_clean_strips_ui_label():
    assert clean("Gemini đã nói\n## CH00 · Mở\n\nVăn.") == "## CH00 · Mở\n\nVăn.\n"


def test_thinking_header_is_not_done():
    # 24/11 Dreyfus: "Figuring out chapter formatting requirements / Gemini said" lưu nhầm là câu trả lời (#529)
    t = "Figuring out chapter formatting requirements\nGemini said"
    assert not stable_done([t] * 5, busy=False)


def test_not_done_until_copy_button():
    assert not stable_done(["## CH00 · Mở\n\n" + "chữ " * 50] * 5, busy=False, copy_ready=False)


def test_short_answer_not_done_with_min_words():
    assert not stable_done(["vài chữ thôi"] * 5, busy=False, min_words=30)
    assert stable_done(["chữ " * 40] * 5, busy=False, min_words=30)


def test_chat_id():
    from gemini_chat import chat_id
    assert chat_id("https://gemini.google.com/app/8f2c1d3e4a5b6c7d?hl=vi") == "8f2c1d3e4a5b6c7d"
    assert chat_id("https://gemini.google.com/app") == ""


class FakeLocator:
    def __init__(self, text="", count=0):
        self.text, self.n = text, count

    @property
    def first(self):
        return self

    def inner_text(self):
        return self.text

    def count(self):
        return self.n


class FakePage:
    def __init__(self, body, url, composer="", queries=0):
        self.url = url
        self.body = body
        self.composer = composer
        self.queries = queries

    def locator(self, selector):
        if selector == "body":
            return FakeLocator(self.body)
        if selector == "rich-textarea div[contenteditable=true]":
            return FakeLocator(self.composer)
        if selector == "user-query":
            return FakeLocator(count=self.queries)
        raise AssertionError(selector)


def test_detects_gemini_error_copy():
    assert is_server_error(FakePage("An error occurred", "https://gemini.google.com/app"))
    assert is_server_error(FakePage("Đã xảy ra lỗi", "https://gemini.google.com/app"))


def test_detects_return_to_empty_home():
    assert is_home_without_query(FakePage("Where should we start?", "https://gemini.google.com/app", "", 0))
    assert not is_home_without_query(FakePage("", "https://gemini.google.com/app/abcdef123456", "", 0))


def test_retries_are_two_by_default_and_last_retry_downgrades():
    retries = 2
    attempts = retries + 1
    assert attempts == 3
    assert [retry_thinking("High", n, attempts) for n in range(1, attempts + 1)] == ["High", "High", "Medium"]
    assert retry_thinking("High", attempts, attempts, no_downgrade=True) == "High"


def test_retry_reason_resets_each_attempt():
    """Lượt 2 thành công sau lượt 1 lỗi không được coi là thất bại (review 153)."""
    src = (Path(__file__).resolve().parents[1] / "scripts" / "gemini_chat.py").read_text(encoding="utf-8")
    loop = src.split("for attempt in range(1, total + 1):", 1)[1]
    assert loop.lstrip().startswith('prev_reason, last_reason = last_reason, ""')


def test_server_error_checked_only_before_reply():
    src = (Path(__file__).resolve().parents[1] / "scripts" / "gemini_chat.py").read_text(encoding="utf-8")
    assert "page.locator(RESPONSE).count() <= before and is_server_error(page)" in src


class _Loc:
    def __init__(self, texts):
        self.texts = texts
    def count(self):
        return len(self.texts)
    def nth(self, i):
        return _Loc([self.texts[i]])
    def inner_text(self):
        return " ".join(self.texts)


class _Page:
    def __init__(self, body, queries=(), box=""):
        self.m = {"body": _Loc([body]), "user-query": _Loc(list(queries))}
        self.box = box
    def locator(self, sel):
        return self.m.get(sel, _Loc([self.box]))


def test_server_error_ignores_text_inside_prompt():
    q = "Viết bài: nếu thấy chữ An error occurred thì bỏ qua."
    assert not is_server_error(_Page("Gemini\n" + q, queries=[q]))
    assert is_server_error(_Page("Gemini\n" + q + "\nAn error occurred", queries=[q]))
