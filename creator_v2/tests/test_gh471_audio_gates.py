import warnings

import pytest

from motion.long import script_lines
from motion.stier import build


def long_gate(line, date=None):
    spec = {"youtube": {"publish_at": date}} if date else {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        errors = script_lines.gate([{"name": "ch00", "lines": [line]}], spec=spec)
    return errors, [str(w.message) for w in caught]


def test_long_comma_boundary_and_clean_line():
    assert not long_gate("Một câu trọn.", "2026-11-18")[0]
    assert any("CAU_TRON" in x for x in long_gate("Một câu,", "2026-11-18")[0])
    for date in (None, "2026-11-17"):
        errors, notes = long_gate("Một câu,", date)
        assert not errors and any("CAU_TRON" in x for x in notes)


def test_parsed_marks_are_removed_before_comma_check():
    chs = script_lines.parse("## CH00 · Mở\n[TRÍCH DỊCH] Một câu, {beat: x} {pd}\n")
    errors = script_lines.gate(chs, spec={"youtube": {"publish_at": "2026-11-18"}})
    assert any("CAU_TRON" in x for x in errors)
    assert not any("MARKUP_LEAK" in x for x in errors)


@pytest.mark.parametrize("line", ["https://example.com", "www.example.com", '"key": 1',
                                  "Câu {pd}", "Câu {beat: x}", "Câu [PAUSE]", "**Câu**", "[Câu](url)"])
def test_long_markup_blocks_even_legacy(line):
    assert any("MARKUP_LEAK" in x for x in long_gate(line)[0])


def test_short_comma_boundary():
    assert build.ear_issues({"lines": ["Câu xong."], "publish_at": "2026-11-29"}) == ([], [])
    assert build.ear_issues({"lines": ["Câu, {pd}"], "publish_at": "2026-11-29"})[0]
    errors, notes = build.ear_issues({"lines": ["Câu,"], "publish_at": "2026-11-28"})
    assert not errors and len(notes) == 1
    assert build.ear_issues({"lines": ["Câu,"]})[0]
