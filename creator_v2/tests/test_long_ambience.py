"""spec "ambience": lớp nền dưới giọng + nhạc trộn ở final; vắng khoá = mix y như cũ. Không TTS, không ffmpeg."""
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT / "motion" / "stier")]
import long_ambience as LA  # noqa: E402

SR = LA.SR
SEGS = [{"index": i, "start": 2.0 * i, "end": 2.0 * i + 1.5} for i in range(10)]


class FakeAmb:
    """Thay hf_ambience: ghi lại plan nhận được; nền = nhiễu, thấp hơn đỉnh giọng 26 dB."""
    KINDS = ("rain", "wind", "night_insects", "none")

    def __init__(self):
        self.calls = []

    def layer(self, lines, spec, voice, voice_lufs, duration, seed=11, music_gap=18.0):
        self.calls.append((lines, spec, voice_lufs, music_gap))
        n = int(duration * SR)
        peak = np.abs(voice).max() * 10 ** (-26 / 20)
        return (np.random.default_rng(1).uniform(-1, 1, (n, 2)) * peak).astype("float32"), ["rain"]


def test_validate_flags_bad_entries():
    ch = ["ch00", "ch03"]
    assert LA.validate({"ambience": [{"chapter": "ch03", "kind": "rain"}, {"kind": "wind"}]}, ch, FakeAmb.KINDS) == []
    bad = LA.validate({"ambience": [{"chapter": "ch09", "kind": "rain"}, {"kind": "x"}, {"from": 1, "kind": "rain"}]}, ch, FakeAmb.KINDS)
    assert len(bad) == 3


def test_chapter_entries_translation():
    plan = [{"kind": "wind"}, {"chapter": "ch03", "kind": "rain", "gain_db": -2},
            {"chapter": "ch05", "from": 12, "to": 20, "kind": "night_insects"}]
    assert LA.chapter_entries(plan, "ch03", 30) == [{"kind": "wind"}, {"kind": "rain", "gain_db": -2, "chapter": 1}]
    assert LA.chapter_entries(plan, "ch05", 30) == [{"kind": "wind"}, {"kind": "night_insects", "from": 13, "to": 21}]
    assert LA.chapter_entries([{"chapter": 5, "kind": "rain"}], "ch05", 3) == [{"kind": "rain", "chapter": 1}]


def test_no_ambience_key_leaves_mix_untouched(tmp_path):
    assert LA.bed_for_chapter({"title": "x"}, "ch03", tmp_path, 20.0) is None
    assert LA.bed_for_chapter({"ambience": []}, "ch03", tmp_path, 20.0) is None
    (tmp_path / "ch01").mkdir()
    (tmp_path / "ch01" / "timing.json").write_text(json.dumps({"segments": SEGS}), encoding="utf-8")
    spec = {"ambience": [{"chapter": "ch03", "kind": "rain"}]}      # có plan nhưng không chạm chương này
    assert LA.bed_for_chapter(spec, "ch01", tmp_path, 20.0, amb=FakeAmb()) is None
    assert LA.build_bed({}, "ch01", SEGS, None, -23.0, 20.0, FakeAmb()) == (None, [])


def test_ambience_adds_bed_below_voice(monkeypatch, tmp_path):
    import soundfile as sf
    d = tmp_path / "ch03"
    d.mkdir()
    (d / "timing.json").write_text(json.dumps({"segments": SEGS}), encoding="utf-8")
    t = np.arange(int(20 * 24000)) / 24000
    sf.write(str(d / "voice.wav"), (0.3 * np.sin(2 * np.pi * 180 * t)).astype("float32"), 24000)
    fake = FakeAmb()
    monkeypatch.setitem(sys.modules, "hf_foley", types.SimpleNamespace(lufs=lambda x: -23.0))
    spec = {"ambience": [{"chapter": "ch03", "kind": "rain"}], "amb_music_gap": 20}
    out = LA.bed_for_chapter(spec, "ch03", tmp_path, 20.0, amb=fake)
    assert out == d / "amb.wav" and out.exists()
    lines, sub, lufs, gap = fake.calls[0]
    assert sub["ambience"] == [{"kind": "rain", "chapter": 1}] and lines[0]["heading"] and lufs == -23.0 and gap == 20.0
    bed, sr = sf.read(str(out), dtype="float32")
    voice, _ = sf.read(str(d / "voice.wav"), dtype="float32")
    assert sr == SR and bed.shape == (20 * SR, 2)
    assert 0 < np.abs(bed).max() < 0.3 * 10 ** (-20 / 20)          # đỉnh nền thấp hơn đỉnh giọng >= 20 dB
    assert np.sqrt((bed ** 2).mean()) < np.sqrt((voice ** 2).mean()) * 0.1


def test_real_hf_ambience_layer_is_quieter_than_voice(monkeypatch):
    """hf_ambience thật (numpy thuần, bỏ đo LUFS): nền dưới giọng >= 20 LU; chương không khai = không nền."""
    try:
        amb = LA._load_amb()
    except Exception as e:      # noqa: BLE001
        pytest.skip(f"không nạp được hf_ambience: {e}")
    monkeypatch.setattr(amb, "tile_lufs", lambda kind, seed=11: -30.0)
    monkeypatch.setitem(sys.modules, "hf_foley", types.SimpleNamespace(
        envelope=lambda x: np.zeros(len(x)), lufs=lambda x: -23.0))
    dur = 8.0
    voice = np.zeros(int(dur * SR), dtype="float32")
    bed, used = LA.build_bed({"ambience": [{"chapter": "ch00", "kind": "rain"}]}, "ch00", SEGS[:4], voice, -23.0, dur, amb)
    assert used == ["rain"] and bed.shape == (int(dur * SR), 2)
    assert 20 * np.log10(np.sqrt((bed ** 2).mean()) + 1e-12) < -23.0 - 20
    other = LA.build_bed({"ambience": [{"chapter": "ch07", "kind": "rain"}]}, "ch00", SEGS[:4], voice, -23.0, dur, amb)
    assert other == (None, [])


def _final_cmds(monkeypatch, tmp_path, spec_extra, bed):
    import build_long as BL
    from tests import test_final_audio_gate as G
    od = G._prepare_final(monkeypatch, tmp_path)
    monkeypatch.setattr(BL, "load", lambda topic: ({"channel": "MIM", "master": True, **spec_extra}, [("ch00", {})], od))
    import audio_lint
    monkeypatch.setattr(audio_lint, "check_voices", lambda *a: ([], [], {}))
    monkeypatch.setattr(BL.LAMB, "bed_for_chapter", lambda *a, **k: bed)
    inner = BL.run
    cmds = []
    monkeypatch.setattr(BL, "run", lambda cmd, **k: (cmds.append(list(cmd)), inner(cmd, **k))[1])
    BL.do_final("demo")
    return [c for c in cmds if str(c[-1]).endswith("mixpad.wav")]


def test_final_mixes_bed_only_when_ambience_present(monkeypatch, tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    off = _final_cmds(monkeypatch, tmp_path / "a", {}, None)[0]
    assert "-af" in off and "-filter_complex" not in off
    on = _final_cmds(monkeypatch, tmp_path / "b", {"ambience": [{"chapter": "ch00", "kind": "rain"}]}, tmp_path / "amb.wav")[0]
    assert "-filter_complex" in on and str(tmp_path / "amb.wav") in on
    assert "amix=inputs=2" in on[on.index("-filter_complex") + 1]
