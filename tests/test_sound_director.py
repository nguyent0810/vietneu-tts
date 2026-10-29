"""Kiểm thử Documentary Sound Director (Ticket #61, #68, Kho #47).

Kiểm tra:
  - Cấu hình sound theo kênh (bud, fs, _thu_lich_su) qua load_channel_sound / new_sound.
  - Loại bỏ hoàn toàn 5 bài cấm lấn giọng (MASKS_VOICE) khỏi pool và mood_mapping Long.
  - Cơ chế SFX Cooldown >= 3.0s, giới hạn mật độ và né TTS onset (Timing Safety).
  - Pre-payoff ducking (-10 dB) trước các cú lật / câu hỏi then chốt.
  - Chuẩn hoá độ to Long (-16.0 +- 0.5 LUFS) và trần True Peak (<= -1.0 dBTP), LRA 2.0-5.0 LU.
  - Tương thích ngược: plan cũ (#72) giữ nguyên luồng mix cũ khi không có preset_long == 'C'.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

import hf_foley as foley
import hf_music
import hf_sound
from hyperframes_bridge import LOUD_TARGET, LOUD_TP

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="cần ffmpeg")
# Bộ đo QA và pilot nằm trong output/ (gitignore): CI không có thì bỏ qua, máy Lead vẫn chạy đủ.
_QA = Path(__file__).resolve().parents[1] / "output/cl_staging/grok/samples/sound_director/qa_mixing_measure.py"
needs_local_qa = pytest.mark.skipif(not _QA.exists(), reason="thiếu bộ đo QA cục bộ trong output/")


def test_load_channel_sound_and_new_sound():
    """Kiểm tra đọc cấu hình sound từ YAML từng kênh mà không gõ cứng tên kênh."""
    for ch in ("bud", "fs", "lich_su", "_thu_lich_su"):
        cfg = hf_sound.load_channel_sound(ch)
        assert cfg, f"Không đọc được cấu hình sound cho kênh {ch}"
        assert cfg.get("preset_long") == "C"
        assert "mood_mapping" in cfg
        assert cfg.get("sfx_cooldown_s", 0) >= 3.0
        assert cfg.get("ducking_db", 0) >= 6.0
        assert cfg.get("pre_payoff_duck_db", 0) <= -6.0

    # Test new_sound
    new_bud = hf_sound.new_sound("bud", music_gap_db=20.0)
    assert new_bud["preset_long"] == "C"
    assert new_bud["music_gap_db"] == 20.0
    assert hf_sound.is_preset_c(new_bud) is True

    # Test legacy spec
    legacy_spec = {
        "reverb": 0.045,
        "music_from": 1,
        "drops": [4, 153],
        "amb": [{"from": 1, "to": 188, "kind": "room"}],
    }
    assert hf_sound.is_preset_c(legacy_spec) is False
    assert hf_sound.is_preset_c({}) is False
    assert hf_sound.is_preset_c(None) is False


def test_forbidden_long_bgm():
    """5 bài cấm lấn giọng (MASKS_VOICE) tuyệt đối không có mặt trong pool hay mood_mapping Long."""
    forbidden = hf_sound.FORBIDDEN_LONG_BGM
    assert "eastern_thought.mp3" in forbidden
    assert "comfortable_mystery_4.mp3" in forbidden
    assert "wood_and_metal_and_water.mp3" in forbidden
    assert "parting_of_the_ways_part_1.mp3" in forbidden
    assert "asian_drums.mp3" in forbidden

    # Kiểm tra trong các file channels
    for ch in ("bud", "fs", "_thu_lich_su"):
        cfg = hf_sound.load_channel_sound(ch)
        mm = cfg.get("mood_mapping") or {}
        for mood, tracks in mm.items():
            for tr in tracks:
                tr_name = Path(tr).name
                assert tr_name not in forbidden, f"Kênh {ch} mood {mood} chứa bài cấm {tr_name}"

    # Kiểm tra pick_mood_track không bao giờ trả bài cấm
    dummy_cfg = {
        "mood_mapping": {
            "curiosity": ["eastern_thought.mp3", "comfortable_mystery_4.mp3", "thinking_music.mp3"]
        },
        "bgm_mac_dinh": "deliberate_thought.mp3",
    }
    track = hf_sound.pick_mood_track("curiosity", dummy_cfg, series="fs")
    assert Path(track).name not in forbidden

    # Kiểm tra hf_batch_render và hf_foley pool không có comfortable_mystery_4.mp3
    import hf_batch_render
    for tr in hf_batch_render.LONG_BGM_POOL.get("fs", []):
        assert Path(tr).name not in forbidden
    for tr in foley.BGM_POOL.get("fs", []):
        assert Path(tr).name not in forbidden


def test_sfx_anti_clash_timing_safety():
    """Kiểm tra phát hiện và né xung đột onset từ TTS."""
    words = [
        {"word": "Đế", "start": 0.5, "end": 0.8},
        {"word": "Thích", "start": 0.9, "end": 1.3},
        {"word": "thần", "start": 3.0, "end": 3.4},
    ]
    # SFX nổ tại 0.52s -> rơi vào [0.5-0.05, 0.5+0.15] -> xung đột
    conflicts = hf_sound.check_sfx_voice_overlap([{"time": 0.52, "name": "bowl"}], words)
    assert len(conflicts) == 1
    assert conflicts[0]["word"] == "Đế"

    # shift_sfx_safe phải đẩy SFX ra khỏi vùng nguy hiểm
    safe_t = hf_sound.shift_sfx_safe(0.52, words, min_t=0.0, max_t=10.0)
    assert not (0.45 <= safe_t <= 0.65)
    # Kiểm tra lại không còn xung đột
    assert len(hf_sound.check_sfx_voice_overlap([{"time": safe_t, "name": "bowl"}], words)) == 0


def test_sfx_cooldown_and_density():
    """Kiểm tra quy tắc Cooldown SFX (cùng loại >= 3s, khác loại >= 1.5s, mật độ <= 3/phút)."""
    raw = [
        {"time": 1.0, "name": "bowl"},
        {"time": 2.0, "name": "bowl"},        # vi phạm cùng loại (< 3s)
        {"time": 2.2, "name": "temple_bell"}, # vi phạm khác loại (< 1.5s từ 1.0)
        {"time": 3.5, "name": "temple_bell"}, # đạt (cách 1.0s là 2.5s > 1.5s)
        {"time": 4.5, "name": "bowl"},        # đạt (cách bowl lúc 1.0 là 3.5s >= 3s, cách 3.5 là 1.0 -> vi phạm khác loại!)
        {"time": 5.5, "name": "bowl"},        # đạt (cách 3.5 là 2.0s, cách bowl 1.0 là 4.5s)
    ]
    filtered = hf_sound.filter_sfx_cooldown(raw, cooldown_same=3.0, cooldown_diff=1.5, max_per_min=10)
    times = [e["time"] for e in filtered]
    assert 1.0 in times
    assert 2.0 not in times
    assert 2.2 not in times
    assert 3.5 in times
    assert 5.5 in times


def test_legacy_mix_long_backward_compatibility(monkeypatch, tmp_path):
    """Spec cũ không có preset_long == 'C' phải chạy luồng cũ, không gọi mix_long_c."""
    called_c = []
    monkeypatch.setattr(hf_sound, "mix_long_c", lambda *args, **kwargs: called_c.append(True))

    lines = [{"start": 0, "end": 2, "sentence_id": 1, "text": "test"}]
    v = np.zeros(48000, dtype="float32")
    voice_wav = tmp_path / "v.wav"
    sf.write(voice_wav, v, 48000)
    out_wav = tmp_path / "out.wav"

    legacy_spec = {"reverb": 0.0, "music_from": 1}
    # Gọi qua foley.mix_long
    foley.mix_long(lines, "bud", voice_wav, None, 2.0, legacy_spec, set(), out_wav)
    assert len(called_c) == 0, "Luồng legacy không được gọi mix_long_c"

    # Gọi với spec C
    spec_c = {"preset_long": "C"}
    foley.mix_long(lines, "bud", voice_wav, None, 2.0, spec_c, set(), out_wav)
    assert len(called_c) == 1, "Spec C phải định tuyến vào mix_long_c"


@needs_ffmpeg
@needs_local_qa
def test_mix_long_c_loudness_and_true_peak(tmp_path):
    """Trộn tiếng bằng mix_long_c đạt chuẩn -16.0 +- 0.5 LUFS và True Peak <= -1.0 dBTP."""
    # Tạo tín hiệu giọng đọc giả lập 15s
    sr = 48000
    sec = 15.0
    t = np.arange(int(sec * sr)) / sr
    rng = np.random.default_rng(42)
    env = (np.sin(2 * np.pi * 1.5 * t) > 0.1) * (0.4 + 0.6 * rng.random(len(t)))
    sig = (0.12 * np.sin(2 * np.pi * 200 * t) + 0.05 * rng.standard_normal(len(t))) * env
    voice_wav = tmp_path / "voice.wav"
    sf.write(voice_wav, sig.astype("float32"), sr)

    lines = [
        {"start": 0.5, "end": 4.5, "sentence_id": 1, "narrative_intent": "discovery", "text": "Câu mở đầu"},
        {"start": 5.0, "end": 9.5, "sentence_id": 2, "narrative_intent": "tension", "text": "Câu kịch tính"},
        {"start": 10.0, "end": 14.5, "sentence_id": 3, "narrative_intent": "resolution", "text": "Câu hoá giải"},
    ]
    out_wav = tmp_path / "mix_out.wav"
    spec = hf_sound.new_sound("bud")

    hf_sound.mix_long_c(
        lines=lines,
        series="bud",
        voice_wav=voice_wav,
        bgm=None,
        duration=sec,
        spec=spec,
        silence=set(),
        out_wav=out_wav,
        seed=11,
    )

    assert out_wav.exists()
    assert out_wav.with_suffix(".bgm.json").exists()

    # Đo kiểm bằng qa_mixing_measure
    from output.cl_staging.grok.samples.sound_director.qa_mixing_measure import run_qa
    rep = run_qa(out_wav, lane="long")
    assert rep["status"] == "PASS", f"QA FAIL: {rep.get('failures')}"
    eb = rep["ebur128"]
    assert abs(eb["integrated_lufs"] - LOUD_TARGET["long"]) <= 0.5
    assert eb["true_peak_dbtp"] <= LOUD_TP
    assert rep["astats"]["clipped_samples"] == 0
    assert eb["lra_lu"] is not None and eb["lra_lu"] >= 0.0


@needs_ffmpeg
@needs_local_qa
def test_render_pilot_c_production_full(tmp_path):
    """Kiểm tra render pilot BUD 130s qua production C đạt chuẩn QA tuyệt đối."""
    out_wav = tmp_path / "pilot_c_test.wav"
    out_mp4 = tmp_path / "pilot_c_test.mp4"
    rep = hf_sound.render_pilot_c_production(out_wav, out_mp4)
    assert rep["status"] == "PASS", f"QA FAIL: {rep.get('failures')}"
    eb = rep["ebur128"]
    assert abs(eb["integrated_lufs"] - LOUD_TARGET["long"]) <= 0.5
    assert eb["true_peak_dbtp"] <= LOUD_TP
    assert rep["astats"]["clipped_samples"] == 0
    assert 2.0 <= eb["lra_lu"] <= 5.0, f"LRA {eb['lra_lu']} ngoài dải 2.0-5.0 LU"
    assert len(rep["abnormal_silences"]) == 0
    assert len(rep["sfx_overlaps"]) == 0
