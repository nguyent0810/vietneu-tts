"""hf_voice: giọng D — temperature, donor, text_mode, khoá cache, ruleset (task 92a)."""
import hashlib
from pathlib import Path

import numpy as np
import pytest

import hf_voice as V
import tts_lexicon


def test_retry_temps_starts_at_configured_then_rest_of_old_order():
    assert V.retry_temps("v3") == (0.8, 0.7, 0.9, 0.6)
    assert V.retry_temps("standard") == (1.0, 0.9, 1.1, 0.8)
    assert V.retry_temps("v3", 0.7) == (0.7, 0.8, 0.9, 0.6)
    assert V.retry_temps("v3", 0.9) == (0.9, 0.8, 0.7, 0.6)
    assert V.retry_temps("standard", 0.9) == (0.9, 1.0, 1.1, 0.8)
    assert V.retry_temps("v3", 0.8) == (0.8, 0.7, 0.9, 0.6)


def test_cache_key_legacy_when_extras_absent(monkeypatch):
    monkeypatch.setattr(V, "MODEL_TAG", "")
    legacy = hashlib.sha1("1|v3|Binh|s|0.9|abc".encode()).hexdigest()[:20]
    assert V.cache_key("v3", "Binh", "s", 0.9, "abc") == legacy
    assert not V.uses_new_cache({"voice": "Binh", "engine": "standard"})


def test_cache_key_includes_temperature_donor_text_mode(monkeypatch):
    monkeypatch.setattr(V, "MODEL_TAG", "")
    base = V.cache_key("v3", "Thái Sơn", "doc_truyen", 0.96, "xin chào")
    d = V.cache_key("v3", "Thái Sơn", "doc_truyen", 0.96, "xin chào",
                    temperature=0.7, donor="Thanh Bình", text_mode="speech")
    t = V.cache_key("v3", "Thái Sơn", "doc_truyen", 0.96, "xin chào",
                    temperature=0.9, donor="Thanh Bình", text_mode="speech")
    n = V.cache_key("v3", "Thái Sơn", "doc_truyen", 0.96, "xin chào",
                    temperature=0.7, donor="", text_mode="speech")
    m = V.cache_key("v3", "Thái Sơn", "doc_truyen", 0.96, "xin chào",
                    temperature=0.7, donor="Thanh Bình", text_mode="production")
    assert d != base and d != t and d != n and d != m
    assert V.uses_new_cache({"temperature": 0.7})
    assert V.uses_new_cache({"donor": "Thanh Bình"})
    assert V.uses_new_cache({"text_mode": "speech"})


def test_spoken_text_speech_vs_production():
    line = "Mùa đông năm 1672, bên bờ lũy Trấn Ninh."
    prod = V.spoken_text(line, {"voice": "Thục Đoan"})
    speech = V.spoken_text(line, {"voice": "Thục Đoan", "text_mode": "speech"})
    assert prod == tts_lexicon.apply(line)
    assert "một nghìn sáu trăm bảy mươi hai" in speech
    assert speech == tts_lexicon.speech_text(line)


def test_line_donor_v3_only_and_alt_does_not_inherit():
    spec = {"voice": "Thái Sơn", "engine": "v3", "donor": "Thanh Bình",
            "alt": {"voice": "Quang Sơn", "engine": "v3", "lines": [3]}}
    assert V.line_donor(spec, 1, "v3") == "Thanh Bình"
    assert V.line_donor(spec, 3, "v3") is None
    assert V.line_donor(spec, 1, "standard") is None
    spec["alt"]["donor"] = "Ngọc Linh"
    assert V.line_donor(spec, 3, "v3") == "Ngọc Linh"


def test_mix_donor_keeps_emb_swaps_codes():
    me = {"speaker_emb": "A", "codes": "CA", "gender": "nam"}
    other = {"speaker_emb": "B", "codes": "CB", "gender": "nam"}
    out = V.mix_donor(me, other)
    assert out["speaker_emb"] == "A" and out["codes"] == "CB"
    assert me["codes"] == "CA"


def test_ruleset_has_approved_d_values_and_new_tts_merges():
    r = V.load_ruleset()
    assert r["bud"]["temperature"] == 0.9 and r["bud"]["text_mode"] == "production"
    assert "donor" not in r["bud"]
    assert r["fs"]["temperature"] == 0.7 and r["fs"]["donor"] == "Thanh Bình"
    assert r["fs"]["text_mode"] == "speech"
    assert r["his"]["temperature"] == 0.7 and r["his"]["text_mode"] == "speech"
    assert "donor" not in r["his"]
    spec = V.new_tts("fs", voice="Thái Sơn", style="doc_truyen", tempo=0.96)
    assert spec["donor"] == "Thanh Bình" and spec["voice"] == "Thái Sơn"
    locked = V.new_tts("fs", voice="Thái Sơn", temperature=0.8)  # fields sau đè ruleset
    assert locked["temperature"] == 0.8


def test_hf_voice_source_has_no_channel_hardcode():
    src = Path(V.__file__).read_text(encoding="utf-8")
    for name in ("Thanh Bình", "Thục Đoan", '"bud"', '"fs"', '"his"'):
        assert name not in src, name


def test_synth_speech_mode_and_new_cache_key(tmp_path, monkeypatch):
    monkeypatch.setattr(V, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(V, "MODEL_TAG", "")
    good = (np.sin(np.arange(48000) / 20) * .3).astype("float32")
    seen = []

    class FakeVoices:
        retries = 0

        def say(self, text, voice, style, engine="v3", temperature=None, donor=None, seed=None):
            seen.append({"text": text, "temperature": temperature, "donor": donor})
            return good, None

    monkeypatch.setattr(V, "Voices", FakeVoices)
    monkeypatch.setattr(V, "tempo", lambda a, sr, k: a)
    spec = {"voice": "Thái Sơn", "engine": "v3", "style": "doc_truyen", "tempo": 0.96,
            "pause": 0.1, "temperature": 0.7, "donor": "Thanh Bình", "text_mode": "speech"}
    m = V.synth(["Ngày 9 tháng 11 dương lịch."], spec, tmp_path / "o.wav")
    assert seen[0]["temperature"] == 0.7 and seen[0]["donor"] == "Thanh Bình"
    assert "chín" in seen[0]["text"] and "mười một" in seen[0]["text"]
    spoken = m["segments"][0]["spoken"]
    key = V.cache_key("v3", "Thái Sơn", "doc_truyen", 0.96, spoken,
                      temperature=0.7, donor="Thanh Bình", text_mode="speech")
    assert (tmp_path / "cache" / f"{key}.wav").exists()
    # khoá cũ không trùng — không tái dùng câu production
    old = V.cache_key("v3", "Thái Sơn", "doc_truyen", 0.96, spoken)
    assert old != key and not (tmp_path / "cache" / f"{old}.wav").exists()


def test_synth_legacy_spec_keeps_old_cache_and_no_donor(tmp_path, monkeypatch):
    monkeypatch.setattr(V, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(V, "MODEL_TAG", "")
    good = (np.sin(np.arange(48000) / 20) * .3).astype("float32")
    seen = []

    class FakeVoices:
        retries = 0

        def say(self, text, voice, style, engine="v3", temperature=None, donor=None, seed=None):
            seen.append({"temperature": temperature, "donor": donor, "text": text})
            return good, None

    monkeypatch.setattr(V, "Voices", FakeVoices)
    monkeypatch.setattr(V, "tempo", lambda a, sr, k: a)
    V.synth(["Ngày 9 tháng 11 dương lịch."], {"voice": "Binh", "pause": 0.1}, tmp_path / "o.wav")
    assert seen[0]["temperature"] is None and seen[0]["donor"] is None
    assert seen[0]["text"] == tts_lexicon.apply("Ngày 9 tháng 11 dương lịch.")
    spoken = tts_lexicon.apply("Ngày 9 tháng 11 dương lịch.")
    legacy = V.cache_key("v3", "Binh", "doc_truyen", 1.0, spoken)
    assert (tmp_path / "cache" / f"{legacy}.wav").exists()


def test_voices_say_live_path_donor_preset_and_temperature_cascade(monkeypatch):
    """Test đường chạy thật của Voices.say (task 92c):
    - donor lấy đúng preset từ model.get_preset_voice()
    - payload đưa vào model.infer() tráo đúng codes từ donor
    - nhiệt độ thử đầu = ruleset kênh (vd 0.7 cho fs, 0.9 cho bud)
    - cascade retry giữ đúng thứ tự khi lần đầu nghi lỗi (0.7 -> 0.8 -> 0.9 -> 0.6)
    - mock model, không gọi TTS thật.
    """
    calls = []

    class MockVieneuModel:
        sample_rate = 24000

        def __init__(self):
            self._presets = {
                "Thái Sơn": {"speaker_emb": "emb_TS", "codes": "codes_TS", "gender": "nam"},
                "Thanh Bình": {"speaker_emb": "emb_TB", "codes": "codes_TB", "gender": "nam"},
                "Binh": {"speaker_emb": "emb_Binh", "codes": "codes_Binh", "gender": "nam"},
            }

        def get_preset_voice(self, name: str) -> dict:
            return dict(self._presets.get(name, {"speaker_emb": f"emb_{name}", "codes": f"codes_{name}", "gender": "nam"}))

        def infer(self, text: str, voice: dict, temperature: float, **kw):
            calls.append({"text": text, "voice": dict(voice), "temp": temperature, "kw": kw})
            t = np.arange(24000) / 24000.0
            return (np.sin(2 * np.pi * 440 * t) * 0.3).astype(np.float32)

    mock_model = MockVieneuModel()
    eng = V.Voices()
    monkeypatch.setattr(eng, "_model", lambda engine: mock_model)

    # 1. Đường chạy FS: v3, voice='Thái Sơn', donor='Thanh Bình', temperature=0.7 (theo ruleset)
    # Lần 1 (temp=0.7) nghi lỗi; Lần 2 (temp=0.8) đạt.
    suspect_calls = []

    def fake_suspect(text, audio, sr):
        suspect_calls.append(len(suspect_calls))
        if len(suspect_calls) == 1:
            return "lặp âm"
        return None

    monkeypatch.setattr(V, "suspect", fake_suspect)

    audio, why = eng.say("Lời nói đầu tiên.", voice="Thái Sơn", style="doc_truyen",
                         engine="v3", temperature=0.7, donor="Thanh Bình")

    assert why is None
    assert eng.retries == 1
    assert len(calls) == 2

    # Xác nhận donor lấy đúng preset và payload tráo codes:
    assert calls[0]["voice"]["speaker_emb"] == "emb_TS"
    assert calls[0]["voice"]["codes"] == "codes_TB"  # donor Thanh Bình
    assert calls[1]["voice"]["speaker_emb"] == "emb_TS"
    assert calls[1]["voice"]["codes"] == "codes_TB"

    # Xác nhận nhiệt độ: thử đầu = 0.7, lần retry tiếp theo = 0.8
    assert calls[0]["temp"] == 0.7
    assert calls[1]["temp"] == 0.8

    # 2. Thử toàn bộ cascade retry khi tất cả các lần đều nghi lỗi
    calls.clear()
    suspect_calls.clear()
    monkeypatch.setattr(V, "suspect", lambda text, audio, sr: "cháy tiếng")
    eng.retries = 0

    audio, why = eng.say("Câu thử cascade.", voice="Thái Sơn", style="doc_truyen",
                         engine="v3", temperature=0.7, donor="Thanh Bình")
    assert why == "cháy tiếng"
    assert eng.retries == 4
    assert len(calls) == 4
    temps = [c["temp"] for c in calls]
    assert temps == [0.7, 0.8, 0.9, 0.6]  # thứ tự cascade chuẩn của v3 khi first=0.7

    # 3. Đường chạy BUD: standard, voice='Binh', temperature=0.9 (theo ruleset)
    calls.clear()
    suspect_calls.clear()
    monkeypatch.setattr(V, "suspect", lambda text, audio, sr: None)
    eng.retries = 0

    audio, why = eng.say("Kính lễ Thế Tôn.", voice="Binh", style="",
                         engine="standard", temperature=0.9)
    assert why is None
    assert len(calls) == 1
    assert calls[0]["temp"] == 0.9
    assert calls[0]["voice"]["speaker_emb"] == "emb_Binh"
    assert calls[0]["voice"]["codes"] == "codes_Binh"  # standard không donor

