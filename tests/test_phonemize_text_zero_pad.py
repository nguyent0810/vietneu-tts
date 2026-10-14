"""Audit kênh Hình Sự (2026-08-14) -- sea_g2p đọc số có "0" đệm đầu THEO
TỪNG CHỮ SỐ kể cả số 0 dẫn đầu: "03 năm" -> "không ba năm" thay vì "ba
năm", "01 đến 05 năm" -> "không một đến không năm năm" thay vì "một đến
năm năm". Real incident: short "Án treo có phải là trắng án không?"
(ANDAXU_ntreocphilmtloihnhphttrongLutH_01), xác nhận qua chính
output/shorts/Hình Sự/.../01_short.json đã render.

Fixed at this repo's own single normalization chokepoint (`PuncNormalizer`,
used by every TTS engine + both gradio apps) rather than inside the
third-party `sea_g2p` package -- patching an installed dependency isn't a
durable local fix. Mirrors the pattern already used for
`_sanitize_word_slash` (test_phonemize_text_word_slash.py).

VÒNG 2 (Cursor review): vòng 1 (bare "\\b0+([1-9]\\d?)\\b") was too broad --
it also collapsed short codes ("mã 012" -> wrongly read as "mười hai"/12
instead of digit-by-digit "không một hai") and phone-number groups ("090
123 4567" -> "90 123 4567", breaking the reading entirely). Narrowed with a
lookahead requiring the number to be immediately followed by a counting
unit word (năm/tháng/ngày/...) or by "đến" (range bridge, covers "01 đến
05 năm") -- codes/phone numbers are never followed by those words."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vieneu_utils.phonemize_text import _fix_zero_padded_numbers, PuncNormalizer


def test_real_incident_text_fixed():
    """The EXACT real production text that produced the bug (án treo
    short), reproduced verbatim."""
    text = "Tòa chỉ áp dụng khi mức án tù không quá 03 năm và có ít nhất 2 tình tiết giảm nhẹ."
    result = _fix_zero_padded_numbers(text)
    assert "03" not in result
    assert " 3 năm" in result

    text2 = "Người phạm tội phải trải qua thời gian thử thách từ 01 đến 05 năm."
    result2 = _fix_zero_padded_numbers(text2)
    assert "01" not in result2 and "05" not in result2
    assert "từ 1 đến 5 năm" in result2


def test_real_incident_end_to_end_through_puncnormalizer():
    """Same real incident text, through the ACTUAL production chokepoint
    (PuncNormalizer -> sea_g2p.Normalizer), not just the pure regex --
    confirms the fix actually changes what sea_g2p renders, not just what
    the intermediate text looks like."""
    sea_g2p = pytest.importorskip("sea_g2p")
    normalizer = PuncNormalizer()
    result = normalizer.normalize(
        "Người phạm tội phải trải qua thời gian thử thách từ 01 đến 05 năm.",
        punc_norm=False,
    )
    assert "không một" not in result
    assert "không năm" not in result
    assert "một đến năm năm" in result


@pytest.mark.parametrize("text,expected_substring", [
    ("ngày 05 tháng 3", "ngày 5 tháng 3"),
    ("thời hạn 099 ngày", "thời hạn 99 ngày"),
    ("phạt tiền từ 05 đến 50 triệu đồng", "phạt tiền từ 5 đến 50 triệu đồng"),
])
def test_leading_zeros_stripped_when_followed_by_unit_word_or_range_bridge(text, expected_substring):
    assert _fix_zero_padded_numbers(text) == expected_substring


@pytest.mark.parametrize("text", [
    "ngày 25/2/2005",                      # date -- 4-digit year, no bare small leading-zero token
    "giá 0 đồng",                          # bare zero -- not a leading-zero-padded number
    "còn 00 điểm",                         # all-zero token -- no non-zero digit to preserve
    "khoản 2 điều 65",                     # already-correct numbers -- pure no-op
    "phiên tòa kết thúc với 338 bị cáo",   # 3-digit number with no leading zero
    "mã 012",                              # SHORT CODE (round 2 finding): "012" is not followed by a
                                            # unit word/"đến" -- must stay digit-by-digit-readable, not
                                            # collapsed into "12"/"mười hai"
    "mã số 012345",
    "điện thoại 090 123 4567",             # PHONE NUMBER (round 2 finding): "090" not followed by a
                                            # unit word -- must not become "90"
    "giá 0.5 triệu",                       # decimal -- "0" here isn't a bare leading-zero token
    "tháng 01/2024",                       # slash-joined date -- "01" not followed by unit word/"đến"
    "lúc 09:30",                           # time -- "09" not followed by unit word/"đến"
    "điều 007 luật hình sự",               # accepted limitation: legal-keyword-BEFORE-number pattern
                                            # ("Điều N") is out of scope -- only number-BEFORE-unit-word
                                            # is fixed (real observed incidents were all this shape)
])
def test_non_target_numbers_left_untouched(text):
    """Must not touch dates, bare zeros, all-zero tokens, numbers that
    never had a leading zero, short codes, or phone numbers -- these must
    keep their original (correct, or at least not-actively-broken) reading."""
    assert _fix_zero_padded_numbers(text) == text


def test_long_zero_padded_codes_left_untouched():
    """A serial/ID/code number (vd "mã số 0123456") is READ DIGIT-BY-DIGIT
    on purpose -- must NOT be collapsed into a large cardinal number."""
    text = "mã số 0123456"
    assert _fix_zero_padded_numbers(text) == text


def test_no_leading_zero_is_a_pure_noop():
    text = "câu bình thường không có số nào cả."
    assert _fix_zero_padded_numbers(text) == text
