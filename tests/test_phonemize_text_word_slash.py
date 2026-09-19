"""P4a (E2E validation remediation) -- "/" used as a word-level either/and
separator between two NON-NUMERIC terms (e.g. "Kinh Dịch / Đạo giáo") was
spoken by sea_g2p's Normalizer as the word "trên" ("over"), producing
nonsensical, meaning-changing output ("kinh dịch TRÊN đạo giáo"). Real
incident: found live during the FS channel E2E validation, in an actual
production Short's TTS-input text (KIENTHUC_BtQuiBngchcichungcacctrngphiph).

Confirmed via direct testing (this session) that sea_g2p's "/" -> "trên"
rule is CORRECT/intentional for a numeric ratio or fraction ("1/2" -> "một
trên hai", a real, legitimate reading) -- the bug is specifically the rule
applying unconditionally regardless of whether either side is numeric.

Fixed at this repo's own single normalization chokepoint
(`PuncNormalizer`, used by every TTS engine + both gradio apps) rather
than inside the third-party `sea_g2p` package -- patching an installed
dependency isn't a durable local fix."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vieneu_utils.phonemize_text import PuncNormalizer, _sanitize_word_slash


# --- _sanitize_word_slash() -- the pure pre-processing step -----------------


def test_real_incident_text_fixed():
    """The EXACT real production text that produced the bug, reproduced
    verbatim from the FS validation report."""
    text = "trong vũ trụ quan kinh dịch / đạo giáo, chúng biểu trưng cho các hiện tượng và lực cơ bản của tự nhiên."
    result = _sanitize_word_slash(text)
    assert "/" not in result
    assert "kinh dịch và đạo giáo" in result


def test_word_slash_with_capitalized_proper_nouns():
    text = "Kinh Dịch / Đạo giáo là hai trường phái."
    result = _sanitize_word_slash(text)
    assert result == "Kinh Dịch và Đạo giáo là hai trường phái."


def test_word_slash_without_surrounding_spaces_also_fixed():
    text = "anh trai/em gái đều tham gia."
    result = _sanitize_word_slash(text)
    assert "/" not in result
    assert "và" in result


@pytest.mark.parametrize("text", [
    "ngày 20/07/2026.",
    "một phần hai là 1/2.",
    "tỷ số 3/4 hiệp đấu.",
])
def test_numeric_ratio_fraction_date_slash_left_untouched(text):
    """Digit-adjacent slashes must NOT be touched -- sea_g2p's own "trên"
    reading (or its date-parsing) is correct there; this fix must not
    regress numeric usage."""
    assert _sanitize_word_slash(text) == text


def test_va_hoac_idiom_not_doubled():
    """The idiomatic compound "và/hoặc" ("and/or") must become "và hoặc",
    not the confusing literal "và và hoặc" the general rule alone would
    produce (left="à", right="h", neither a digit)."""
    result = _sanitize_word_slash("áp dụng và/hoặc kết hợp.")
    assert result == "áp dụng và hoặc kết hợp."
    assert "và và" not in result


def test_va_hoac_idiom_case_insensitive_and_preserves_leading_capital():
    result = _sanitize_word_slash("Và/hoặc chọn phương án khác.")
    assert result.startswith("Và hoặc")


def test_multiple_word_slashes_in_one_string():
    text = "A / B và C/D đều là ví dụ."
    result = _sanitize_word_slash(text)
    assert "/" not in result
    assert result == "A và B và C và D đều là ví dụ."


def test_no_slash_is_a_pure_noop():
    text = "câu bình thường không có dấu gạch chéo nào cả."
    assert _sanitize_word_slash(text) == text


# --- Full pipeline (PuncNormalizer -> real sea_g2p call) --------------------


def test_full_pipeline_no_longer_produces_tren_for_the_real_incident_text():
    """End-to-end: the actual TTS-bound normalize() call, using the real
    sea_g2p dependency (not mocked) -- proves the fix holds through the
    real call chain, not just the pre-processing step in isolation."""
    n = PuncNormalizer(lang="vi")
    text = "trong vũ trụ quan kinh dịch / đạo giáo, chúng biểu trưng cho các hiện tượng."
    result = n.normalize(text)
    assert "trên" not in result, f"the real bug must not recur: {result!r}"
    assert "và" in result


def test_full_pipeline_still_reads_a_real_fraction_as_tren():
    """Control case: the fix must NOT break sea_g2p's own correct
    numeric-ratio reading."""
    n = PuncNormalizer(lang="vi")
    result = n.normalize("một phần hai là 1/2.")
    assert "trên" in result


def test_normalize_batch_applies_the_same_fix():
    n = PuncNormalizer(lang="vi")
    results = n.normalize_batch([
        "kinh dịch / đạo giáo là ví dụ.",
        "một phần hai là 1/2.",
    ])
    assert "trên" not in results[0]
    assert "trên" in results[1]
