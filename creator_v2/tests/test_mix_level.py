import numpy as np
import pytest
import soundfile as sf

from motion.long import build_long as mix
from pathlib import Path

# Các test đo thật qua ffmpeg của build_long (đường dẫn máy local); CI không có -> bỏ qua đúng các test đó.
needs_ffmpeg = pytest.mark.skipif(not Path(str(mix.FFMPEG)).exists(), reason="cần ffmpeg của build_long.FFMPEG")


@pytest.fixture
def audio(tmp_path, monkeypatch):
    monkeypatch.setattr(mix, "CHAN", {}, raising=False)
    cd = tmp_path / "topic" / "ch01"
    cd.mkdir(parents=True)
    (cd.parent / "bgm").mkdir()
    sr = 48000
    t = np.arange(sr * 6) / sr
    sf.write(cd / "voice.wav", .18 * np.sin(2 * np.pi * 220 * t), sr, subtype="FLOAT")
    sf.write(cd / "sfx.wav", np.zeros(len(t)), sr, subtype="FLOAT")
    for amplitude in (.05, .2, .8):
        sf.write(cd.parent / "bgm" / f"{amplitude}.wav",
                 amplitude * np.sin(2 * np.pi * 440 * t), sr, subtype="FLOAT")
    return cd


@needs_ffmpeg
@pytest.mark.parametrize("amplitude", [.05, .2, .8])
def test_calibration_and_real_sidechain(audio, amplitude):
    levels = {"gain": .17, "threshold": .05, "ratio": 4}
    item = {"file": f"{amplitude}.wav", "start": 0, "end": 6, "fin": 0, "fout": 0}
    gain = mix.calibrated_bgm_gain(audio / "voice.wav", audio.parent / "bgm" / item["file"],
                                   item, 6, levels, master=False)
    mix.mix_chapter({}, audio, 6, master=False, items=[item], levels=levels, measure_music=True)
    result = mix.measure_mix_level(audio / "voice_level.wav", audio / "music_level.wav")
    assert result["music_minus_voice_db"] == pytest.approx(-14, abs=.2)
    assert gain * amplitude == pytest.approx(.18 * 10 ** (-14 / 20) * 4 ** .75, rel=.5)


@needs_ffmpeg
def test_gain_overrides_are_multipliers(audio):
    item = {"file": "0.2.wav", "start": 0, "end": 6, "fin": 0, "fout": 0}
    levels = {"gain": .17, "threshold": .05, "ratio": 4}
    args = (audio / "voice.wav", audio.parent / "bgm" / item["file"])
    baseline = mix.calibrated_bgm_gain(*args, item, 6, levels, master=False)
    assert mix.calibrated_bgm_gain(*args, {**item, "gain": .06}, 6, levels, master=False) == pytest.approx(baseline / 2, rel=.02)
    assert mix.calibrated_bgm_gain(*args, item, 6, {**levels, "gain": .34}, master=False) == pytest.approx(baseline * 2, rel=.02)


@needs_ffmpeg
def test_legacy_mix_does_not_calibrate(audio, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("legacy audio must not be calibrated")
    monkeypatch.setattr(mix, "calibrated_bgm_gain", fail)
    mix.mix_chapter({}, audio, 6, master=False, items=[{"file": "0.2.wav", "start": 0, "end": 6}],
                    levels={"gain": .16, "threshold": .03, "ratio": 6}, measure_music=False)
    assert (audio / "mix.wav").exists()


@pytest.mark.parametrize("db, expected", [(-18.01, "nh\u1ea1c nh\u1ecf"), (-18, None), (-14, None),
                                           (-8, None), (-7.99, "nh\u1ea1c to h\u01a1n m\u1ee9c cho ph\u00e9p"),
                                           (float("nan"), "kh\u00f4ng \u0111o \u0111\u01b0\u1ee3c")])
def test_check_mix_level_bounds(db, expected):
    result = mix.check_mix_level({"music_minus_voice_db": db, "blocks": 1})
    assert (result is None) if expected is None else expected in result


@needs_ffmpeg
def test_calibration_rejects_silent_music(audio):
    sf.write(audio.parent / "bgm" / "silent.wav", np.zeros(48000 * 6), 48000)
    with pytest.raises(ValueError, match="kh\u00f4ng c\u00f3 \u0111o\u1ea1n gi\u1ecdng v\u00e0 nh\u1ea1c"):
        mix.calibrated_bgm_gain(audio / "voice.wav", audio.parent / "bgm" / "silent.wav",
                                {"start": 0, "end": 6}, 6,
                                {"gain": .17, "threshold": .05, "ratio": 4}, master=False)
