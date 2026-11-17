import hf_voice as V


def test_pause_context_punctuation_and_peak_sentence():
    base = 0.5
    assert V.default_pause("Vế còn tiếp,", base, pause_ctx=True) == 0.2
    assert V.default_pause("Vế còn tiếp;", base, pause_ctx=True) == 0.2
    assert V.default_pause("Vế còn tiếp", base, pause_ctx=True) == 0.2
    assert V.default_pause("Câu kết.", base, pause_ctx=True) == base
    assert V.default_pause("Câu kết!", base, pause_ctx=True) == base
    assert V.default_pause("Đó là lời đáp.", base, pause_ctx=True,
                           previous_line="Một câu kể dài có nhiều hơn sáu tiếng.") == 0.8
    assert V.default_pause("Đây là một câu kết dài hơn sáu tiếng.", base, pause_ctx=True,
                           previous_line="Một câu kể dài có nhiều hơn sáu tiếng.") == base


def test_pause_context_off_keeps_legacy_values():
    assert V.default_pause("Vế còn tiếp,", 0.5) == 0.5
    assert V.default_pause("Đó là lời đáp.", 0.5,
                           previous_line="Một câu kể dài có nhiều hơn sáu tiếng.") == 0.5


def test_pause_context_default_for_new_long_tts():
    assert V.new_tts("fs")["pause_ctx"] is True
    assert V.apply_long_narrator("unknown", {"voice": "Binh"})["pause_ctx"] is True


def test_closing_quote_counts_as_full_stop():
    """Lead 17/11: câu kết bằng ngoặc kép không bị coi là vế còn tiếp."""
    assert V.default_pause('Ngài nói: “Hãy tự mình thắp đuốc.”', 0.5, pause_ctx=True) == 0.5
    assert V.default_pause("Rồi bà thề một lời (ở trước điện),", 0.5, pause_ctx=True) == 0.2
