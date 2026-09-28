"""Tín hiệu chẩn đoán bằng code + fingerprint (ticket 12): chỉ dữ liệu đo,
không điểm, không ngưỡng."""
import json

import pytest

import script_diagnostics as sd

SCRIPT = ("3 con giáp **Tuổi Thân**, **Tuổi Tý**, **Tuổi Thìn** được xem là thuận hoà hôm nay.\n"
          "Ngày 25/07/2026 là ngày Canh Tý, hành Kim.\n"
          "Theo lời kể của ông Nguyễn Văn An, người tuổi Ngọ nên thận trọng [cười].\n"
          "Chúc bạn một ngày an yên.")


def test_basic_counts_are_on_spoken_text():
    d = sd.diagnostics(SCRIPT)
    assert d["sentence_count"] == 4
    assert d["first_sentence_words"] == 16
    assert d["sentence_words"][0] == 16 and d["total_words"] == sum(d["sentence_words"])
    assert "**" not in json.dumps(d, ensure_ascii=False) and "cười" not in json.dumps(d, ensure_ascii=False)


def test_density_numbers_terms_names_per_sentence():
    dens = sd.diagnostics(SCRIPT)["density"]
    assert dens[0]["number_tokens"] == ["3"]
    assert dens[1]["number_tokens"] == ["25/07/2026"]
    assert set(dens[1]["term_tokens"]) == {"canh", "tý", "kim"}
    assert dens[1]["names"] == 0, "Can/Chi/hành là thuật ngữ, không phải tên"
    assert dens[2]["name_tokens"] == ["Nguyễn Văn An"]
    assert dens[3] == {"sentence": 3, "numbers": 0, "terms": 0, "names": 0,
                       "number_tokens": [], "term_tokens": [], "name_tokens": []}


def test_detection_is_versioned():
    assert sd.diagnostics(SCRIPT)["diagnostics_version"] == sd.DIAGNOSTICS_VERSION
    assert "số=" in sd.DIAGNOSTICS_VERSION


def test_fingerprint_is_stable_normalised_and_parametrised():
    a = sd.fingerprint("**Hôm nay**, con giáp NÀO may mắn nhất? Câu hai.")
    b = sd.fingerprint("Hôm nay con giáp nào   may mắn nhất?! Khác hẳn phần sau.")
    assert a == b == "hôm nay con giáp nào"
    assert sd.fingerprint("Hôm nay con giáp nào may", n_words=2) == "hôm nay"
    assert sd.diagnostics(SCRIPT, fingerprint_words=3)["fingerprint"] == "3 con giáp"
    with pytest.raises(ValueError):
        sd.fingerprint("x", n_words=0)


def test_time_to_hook_counts_words_before_span_at_two_rates():
    script = "Có một điều rất nhiều người không biết về ngày này. Hôm nay tuổi Tý gặp quý nhân."
    t = sd.time_to_hook(script, "tuổi Tý gặp quý nhân")
    assert t["words_before_hook"] == 13
    assert t["seconds_before_hook"] == {"170wpm": round(13 / 170 * 60, 2), "200wpm": round(13 / 200 * 60, 2)}


def test_time_to_hook_accepts_span_with_markers_and_rejects_invalid():
    assert sd.time_to_hook("**Tuổi Tý** may mắn.", "**Tuổi Tý**")["words_before_hook"] == 0
    with pytest.raises(ValueError, match="không có trong script"):
        sd.time_to_hook("Câu một.", "câu không tồn tại")
    with pytest.raises(ValueError, match="rỗng"):
        sd.time_to_hook("Câu một.", "  ")


def test_no_score_threshold_or_pass_flag_anywhere():
    d = sd.diagnostics(SCRIPT)
    blob = json.dumps(d).lower()
    for forbidden in ("score", "threshold", "pass", "fail", "ok"):
        assert f'"{forbidden}' not in blob
