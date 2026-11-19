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
