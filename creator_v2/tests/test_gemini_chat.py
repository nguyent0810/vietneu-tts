import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from gemini_chat import clean, stable_done


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
