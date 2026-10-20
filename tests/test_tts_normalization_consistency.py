"""Mục 10 của audit: Short và Long phải cho CÙNG chữ đọc, và lexicon + normalizer không để lọt bẫy.

Short chuẩn hoá bằng `render_engine.normalize_preserving_paragraphs`, Long bằng `normalize_to_chunks` (qua
`Vieneu.infer`). Cả hai cùng gọi `normalizer.normalize_batch(..., punc_norm=True)` theo từng đoạn; test này khoá hợp đồng
đó để một bên đổi mà bên kia không đổi sẽ bị bắt. Cần `sea_g2p` (không có thì bỏ qua, như môi trường CI chỉ có core).
"""
import re

import pytest

pytest.importorskip("sea_g2p")

import render_engine  # noqa: E402
import tts_lexicon as L  # noqa: E402
from vieneu_utils.phonemize_text import _get_normalizer, normalize_to_chunks  # noqa: E402

LINES = [
    "Ngày xưa, có một người trồng sen bên hồ.",
    "Năm 1983, ông đã 35 tuổi.",
    "Mỗi ngày tụng 1-3 lần theo DN 16.",
    "Ông Sāriputta (Xá Lợi Phất) đến.",
    "Tăng 50% & giảm 3/4.",
    "Rồi... im lặng.",
    "Từ năm 1960-1972, kinh MN 7 và Dhp 113 được nhắc.",
]


def _flat(s: str) -> str:
    """Bỏ khác biệt vô hại: hoa/thường, khoảng trắng, dấu câu cuối (punc_norm chốt dấu câu từng chunk)."""
    return re.sub(r"[\s.,!?;:]+", " ", s.lower()).strip()


@pytest.mark.parametrize("line", LINES)
def test_short_and_long_normalize_to_same_spoken_text(line):
    short = render_engine.normalize_preserving_paragraphs(line)                # đường Short thật
    long = " ".join(normalize_to_chunks(line))                                 # đường Long (Vieneu.infer)
    assert _flat(short) == _flat(long)


@pytest.mark.parametrize("line", LINES)
def test_lexicon_is_idempotent(line):
    once = L.apply(line)
    assert L.apply(once) == once


# Những gì lexicon phải làm được SAU khi normalizer chạy -- đo thật trên sea_g2p, đúng thứ TTS sẽ nhận.
SPOKEN = [
    ("Mỗi ngày tụng 1-3 lần.", "một đến ba", "ngày một tháng ba"),
    ("Ông Sāriputta đến.", "xá lợi phất", "sariputta"),
    ("Theo DN 16 Ngài dạy.", "trường bộ kinh số mười sáu", "đê nờ"),
    ("Theo MN 7 Ngài dạy.", "trung bộ kinh số bảy", "mn"),
    ("Cấp Anāthapiṇḍika cúng dường.", "cô độc", "anathapindika"),
]


@pytest.mark.parametrize("src,must,must_not", SPOKEN)
def test_lexicon_then_normalizer_reads_correctly(src, must, must_not):
    spoken = _flat(_get_normalizer().normalize_batch([L.apply(src)], punc_norm=True)[0])
    assert must in spoken
    assert must_not not in spoken


def test_normalizer_alone_would_misread_these():
    """Chốt lý do lexicon tồn tại: test thẳng đầu ra tts_lexicon.apply cho các trường hợp bẫy đọc."""
    assert "1 đến 3" in L.apply("Mỗi ngày tụng 1-3 lần.")
    assert "Xá Lợi Phất" in L.apply("Ông Sāriputta đến.")
    assert "Trường Bộ kinh số mười sáu" in L.apply("Theo DN 16 Ngài dạy.")


def test_normalizer_strips_pali_diacritics_so_unknown_names_still_misread():
    """Tên Pali có hoặc không có dấu diacritic đều được lexicon chuyển sang tên Việt đúng."""
    assert "Xá Lợi Phất" in L.apply("Sāriputta")
    assert "Xá Lợi Phất" in L.apply("Sariputta")
    assert "A Nan" in L.apply("Ānanda")
    assert "A Nan" in L.apply("Ananda")
