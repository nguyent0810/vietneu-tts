"""Test bản đồ beat (hf_beatmap) bằng sóng tổng hợp: click track 120 BPM và sóng phẳng."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pytest
import soundfile as sf

import hf_beatmap


def make_click_track(bpm: float = 120.0, duration_s: float = 8.0, sr: int = 22050) -> np.ndarray:
    """Tạo click track tổng hợp với chu kỳ 60/BPM."""
    y = np.zeros(int(sr * duration_s), dtype=np.float32)
    step = 60.0 / bpm
    for t_click in np.arange(0.0, duration_s, step):
        idx = int(t_click * sr)
        click_len = int(sr * 0.015)
        if idx + click_len < len(y):
            t_c = np.linspace(0, 0.015, click_len, endpoint=False)
            y[idx : idx + click_len] = np.sin(2 * np.pi * 1200 * t_c) * np.exp(-t_c * 400)
    return y


def make_flat_signal(duration_s: float = 6.0, sr: int = 22050) -> np.ndarray:
    """Tạo sóng sin phẳng 440 Hz không có nhịp trống/onset."""
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False, dtype=np.float32)
    return 0.3 * np.sin(2 * np.pi * 440 * t)


def test_click_track_120bpm():
    sr = 22050
    y = make_click_track(bpm=120.0, duration_s=8.0, sr=sr)
    res = hf_beatmap.analyze_audio(y, sr=sr)

    assert res["status"] == "ok"
    assert res["confidence"] >= hf_beatmap.CONFIDENCE_THRESHOLD
    assert res["tempo"] is not None
    assert 110.0 <= res["tempo"] <= 130.0
    assert isinstance(res["beats"], list)
    assert len(res["beats"]) >= 10

    # Kiểm tra snap
    # Mốc 0.52 nằm gần beat 0.50
    snapped = hf_beatmap.snap(0.52, res["beats"], tol=0.12)
    assert snapped is not None
    assert abs(snapped - 0.50) <= 0.12

    # Mốc 0.75 nằm giữa 0.50 và 1.00 -> quá ngưỡng tol 0.12
    assert hf_beatmap.snap(0.75, res["beats"], tol=0.12) is None


def test_flat_signal_ambient():
    sr = 22050
    y = make_flat_signal(duration_s=6.0, sr=sr)
    res = hf_beatmap.analyze_audio(y, sr=sr)

    assert res["status"] == "không đủ nhịp"
    assert res["confidence"] < hf_beatmap.CONFIDENCE_THRESHOLD
    assert res["tempo"] is None
    assert res["beats"] == "không đủ nhịp"

    # Snap với nhạc không đủ nhịp phải trả về None
    assert hf_beatmap.snap(1.0, res["beats"], tol=0.12) is None


def test_snap_edge_cases():
    assert hf_beatmap.snap(1.0, "không đủ nhịp") is None
    assert hf_beatmap.snap(1.0, None) is None
    assert hf_beatmap.snap(1.0, []) is None

    beats = [1.0, 2.0, 3.0]
    assert hf_beatmap.snap(1.05, beats, tol=0.12) == 1.0
    assert hf_beatmap.snap(1.95, beats, tol=0.12) == 2.0
    assert hf_beatmap.snap(1.50, beats, tol=0.12) is None


def test_cache_file(tmp_path):
    wav_path = tmp_path / "test_track.wav"
    sr = 22050
    y = make_click_track(bpm=120.0, duration_s=3.0, sr=sr)
    sf.write(str(wav_path), y, sr)

    cache_dir = tmp_path / "cache"
    res1 = hf_beatmap.compute_beatmap(wav_path, cache_dir=cache_dir)
    assert (cache_dir / "test_track.wav.json").exists()

    # Lần 2 phải đọc từ cache
    res2 = hf_beatmap.compute_beatmap(wav_path, cache_dir=cache_dir)
    assert res1["duration_s"] == res2["duration_s"]
    assert res1["confidence"] == res2["confidence"]
