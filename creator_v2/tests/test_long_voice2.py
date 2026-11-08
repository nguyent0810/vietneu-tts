"""spec "voice2": giọng thứ hai cho câu trích {"q": 1}; vắng voice2 = khoá cache và hành vi y như cũ."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT / "motion" / "stier")]
import build_long as BL  # noqa: E402

LINES = [{"t": "Mở đầu."}, {"t": "Ông viết rằng thế.", "q": 1, "tr": 1}, {"t": "Hỏi?", "ask": 1}]


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    monkeypatch.setattr(BL, "VOICE", "Anh Khôi")
    monkeypatch.setattr(BL, "QUOTE_VOICE", "Minh Đức")
    monkeypatch.setattr(BL, "ASK_VOICE", "Phạm Tuyên")
    monkeypatch.setattr(BL, "VOICE2", None)
    monkeypatch.setattr(BL, "VOICE2_RADIO", True)


def _keys():
    return [BL._key(BL.spoken(BL.line_text(x)), 0, BL.line_voice(x)) for x in LINES]


def test_cache_key_unchanged_without_voice2():
    old = [BL._key(BL.spoken(BL.line_text(x)), 0, v) for x, v in zip(LINES, ["Anh Khôi", "Minh Đức", "Phạm Tuyên"])]
    assert _keys() == old


def test_cache_key_differs_only_for_q_lines_when_voice2_set(monkeypatch):
    base = _keys()
    monkeypatch.setattr(BL, "VOICE2", "Thanh Bình")
    new = _keys()
    assert new[0] == base[0] and new[2] == base[2]      # dẫn truyện và câu hỏi không đổi
    assert new[1] != base[1]                            # câu trích đổi khoá


def test_q_line_routes_to_voice2_and_others_do_not(monkeypatch):
    monkeypatch.setattr(BL, "VOICE2", "Thanh Bình")
    assert [BL.line_voice(x) for x in LINES] == ["Anh Khôi", "Thanh Bình", "Phạm Tuyên"]


def test_load_reads_voice2_block_and_default(monkeypatch, tmp_path):
    sd, od = tmp_path / "sd", tmp_path / "od"
    sd.mkdir()
    monkeypatch.setattr(BL, "paths", lambda topic: (sd, od))
    monkeypatch.setattr(BL.channel_table, "resolve_long_channel", lambda spec: "CL")
    monkeypatch.setattr(BL, "_channels", lambda: {"CL": {"voice": "Anh Khôi", "quote": "Minh Đức"}})
    monkeypatch.setattr(BL, "strip_ai_illustration_labels", lambda *a: False)

    def write(spec):
        (sd / "spec.json").write_text(json.dumps({"chapters": [], **spec}, ensure_ascii=False), encoding="utf-8")

    write({})
    BL.load("t")
    assert BL.VOICE2 is None
    write({"voice2": {"voice": "Quang Sơn", "radio": False}})
    BL.load("t")
    assert (BL.VOICE2, BL.VOICE2_RADIO) == ("Quang Sơn", False)
    write({"voice2": {}})
    BL.load("t")
    assert BL.VOICE2 == BL.VOICE2_DEFAULT and BL.VOICE2_RADIO is True


def _speak(monkeypatch, tmp_path):
    calls = []

    def fake(text, cache, take=0, voice=None):
        calls.append(voice)
        return np.ones(2400, dtype="float32") * 0.1, 24000

    monkeypatch.setattr(BL, "tts_line", fake)
    monkeypatch.setattr(BL, "radio", lambda a, sr: a * 0)
    seg = BL.speak(LINES, tmp_path, "ch00")
    return calls, seg


def test_speak_uses_voice2_for_q_lines(monkeypatch, tmp_path):
    monkeypatch.setattr(BL, "VOICE2", "Thanh Bình")
    calls, seg = _speak(monkeypatch, tmp_path)
    assert calls == ["Anh Khôi", "Thanh Bình", "Phạm Tuyên"]
    assert len(seg["segments"]) == 3


def test_speak_without_voice2_matches_legacy_voices(monkeypatch, tmp_path):
    calls, _ = _speak(monkeypatch, tmp_path)
    assert calls == ["Anh Khôi", "Minh Đức", "Phạm Tuyên"]
