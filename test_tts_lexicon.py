"""tts_lexicon: chữ viết -> chữ đọc cho TTS."""
import pytest

import tts_lexicon as L


@pytest.mark.parametrize("src,want", [
    ("DN 16", "Trường Bộ kinh số mười sáu"),
    ("Kinh MN 7 dạy", "Kinh Trung Bộ kinh số bảy dạy"),
    ("Dhp 113", "Pháp Cú kinh số một trăm mười ba"),
    ("SN 12.2", "Tương Ưng Bộ mười hai, kinh hai"),
    ("AN 4.5", "Tăng Chi Bộ bốn, kinh năm"),
])
def test_sutta_codes(src, want):
    assert L.apply(src) == want


def test_name_an_is_not_a_sutta_code():
    assert L.apply("Anh An đi chợ") == "Anh An đi chợ"


def test_number_range_but_not_dates():
    assert L.apply("từ 1-3 lần") == "từ 1 đến 3 lần"
    assert L.apply("năm 1960–1972") == "năm 1960 đến 1972"
    assert L.apply("ngày 12-7-2025") == "ngày 12-7-2025"          # ngày tháng giữ nguyên
    assert L.apply("23:00-24:00") == "23:00-24:00"


def test_symbols_and_parentheses():
    assert L.apply("tăng 50%") == "tăng 50 phần trăm"
    assert L.apply("Trà & bánh") == "Trà và bánh"
    assert L.apply("Ngài (lúc đó) im lặng.") == "Ngài, lúc đó, im lặng."
    assert L.apply("Kết thúc (xem sau).") == "Kết thúc, xem sau."
    assert L.apply("Rồi... im lặng") == "Rồi, im lặng"


def test_pali_names_to_vietnamese_case_insensitive_and_longest_first():
    assert L.apply("Sāriputta và Ānanda") == "Xá Lợi Phất và A Nan"
    assert L.apply("sāriputta") == "Xá Lợi Phất"
    assert L.apply("Anāthapiṇḍika cúng dường") == "Cấp Cô Độc cúng dường"


def test_plain_text_untouched():
    s = "Ngày xưa có một người trồng sen."
    assert L.apply(s) == s
    assert L.apply("") == ""


def test_ascii_variants_and_new_names():
    assert L.apply("Ananda và Sariputta") == "A Nan và Xá Lợi Phất"
    assert L.apply("Aṅgulimāla gặp Ngài") == "Ương Quật Ma La gặp Ngài"
    assert L.apply("Truyện Jātaka kể") == "Truyện Tiền Thân kể"
    assert L.apply("Địa Tạng") == "Địa Tạng"                          # tiếng Việt có sẵn không bị đụng


def test_speech_text_numbers_hyphen_conjunction_and_period():
    assert L.speech_text("Mùa đông năm 1672, bên bờ lũy Trấn Ninh.") == (
        "Mùa đông năm một nghìn sáu trăm bảy mươi hai, bên bờ lũy Trấn Ninh.")
    assert L.speech_text("Ngày 9 tháng 11 dương lịch.") == "Ngày chín tháng mười một dương lịch."
    spoken = L.speech_text("Người châu Âu gọi hai xứ: Tông-kin ở phía Bắc, Cô-chin-chi-na ở phía Nam.")
    assert "Tông kin" in spoken and "Cô chin chi na" in spoken
    # ≥ 6 chữ trước liên từ, chưa có phẩy → thêm phẩy
    assert L.speech_text("Người đứng trên bờ sông nhìn xuống nhưng không nói gì") == (
        "Người đứng trên bờ sông nhìn xuống, nhưng không nói gì.")
    # câu đầu bằng liên từ: không thêm phẩy
    assert L.speech_text("Nhưng một trong ba tuổi ấy vừa hợp vừa phá.") == (
        "Nhưng một trong ba tuổi ấy vừa hợp vừa phá.")


def test_speech_text_skips_lexicon_when_asked():
    assert L.speech_text("Sāriputta hỏi", lexicon=False) == "Sāriputta hỏi."
    assert "Xá Lợi Phất" in L.speech_text("Sāriputta hỏi", lexicon=True)
    assert "một đến ba" in L.speech_text("hỏi từ 1-3 lần")


def test_lexicon_json_is_well_formed():
    import json
    d = json.loads(L.LEXICON_PATH.read_text(encoding="utf-8"))
    assert all(isinstance(k, str) and isinstance(v, str) and v for k, v in d["names"].items())
    # Mọi tên có dấu Pali phải đổi sang chữ KHÔNG còn ký tự Pali (nếu không lint vẫn báo và TTS vẫn đọc vỡ)
    import re
    assert not any(re.search(r"[āīūṅñṭḍṇḷṃṁśṣ]", v, re.I) for v in d["names"].values())
