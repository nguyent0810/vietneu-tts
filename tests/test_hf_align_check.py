"""Test kiểm chéo mốc từ (hf_align_check) với khe năng lượng thấp trong wav."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pytest
import soundfile as sf

import hf_align
import hf_align_check


def test_is_word_abnormally_long():
    # Từ bình thường: 1 âm tiết, 300ms
    assert not hf_align_check.is_word_abnormally_long(0.30, 1.0)
    # Từ dài bất thường: 1 âm tiết nhưng dài 950ms (> 850ms)
    assert hf_align_check.is_word_abnormally_long(0.95, 1.0)

    # Số 1979 đọc 7 âm tiết, dài 1.5s -> trung bình 0.21s/âm tiết -> bình thường
    assert not hf_align_check.is_word_abnormally_long(1.50, 7.0)
    # Số đọc quá dài: 7 âm tiết nhưng kéo dài 6s -> > 0.70s/âm tiết -> bất thường
    assert hf_align_check.is_word_abnormally_long(6.0, 7.0)


def test_find_true_dips_synthetic():
    # Tạo envelope giả lập: 2 xung âm thanh có 1 khe sâu ở giữa
    hop = 0.005
    n_samples = 200  # 1.0 giây
    env = np.ones(n_samples, dtype=float) * 0.3
    # Xung 1: từ 0.1s đến 0.4s (năng lượng cao 0.8)
    env[20:80] = 0.8
    # Khe sâu: từ 0.4s đến 0.6s (năng lượng tụt xuống 0.05, đáy tại 0.5s tức mẫu 100)
    env[80:120] = np.linspace(0.8, 0.05, 20).tolist() + np.linspace(0.05, 0.8, 20).tolist()
    # Xung 2: từ 0.6s đến 0.9s (năng lượng cao 0.8)
    env[120:180] = 0.8

    dips = hf_align_check.find_true_dips(env, hop, prominence_ratio=0.15)
    assert len(dips) >= 1
    # Khe sâu nhất phải nằm gần 0.50s (mẫu 100 * 0.005 = 0.50s)
    best_dip = dips[np.argmin(np.abs(dips - 0.50))]
    assert abs(best_dip - 0.50) <= 0.03


def test_check_sentence_boundaries_synthetic(tmp_path):
    # Tạo wav 2 âm tiết: "đi chùa"
    # Tiếng 1: 0.1s - 0.4s (tần số 300Hz)
    # Khe tĩnh lặng: 0.4s - 0.6s (khe thật ở 0.50s)
    # Tiếng 2: 0.6s - 0.9s (tần số 400Hz)
    sr = 22050
    duration = 1.0
    y = np.zeros(int(sr * duration), dtype=np.float32)
    t = np.linspace(0, duration, len(y), endpoint=False)

    idx_s1 = int(0.1 * sr)
    idx_e1 = int(0.4 * sr)
    y[idx_s1:idx_e1] = 0.5 * np.sin(2 * np.pi * 300 * t[idx_s1:idx_e1])

    idx_s2 = int(0.6 * sr)
    idx_e2 = int(0.9 * sr)
    y[idx_s2:idx_e2] = 0.5 * np.sin(2 * np.pi * 400 * t[idx_s2:idx_e2])

    wav_path = tmp_path / "test_align.wav"
    sf.write(str(wav_path), y, sr)

    env, hop = hf_align.energy_envelope(wav_path)
    # Kiểm tra câu "đi chùa"
    res = hf_align_check.check_sentence_boundaries(
        env=env,
        hop=hop,
        start=0.0,
        end=1.0,
        text="đi chùa",
        drift_threshold=0.080,
    )
    # Ranh giới chia đều 2 từ có trọng số bằng nhau:
    # Voiced từ 0.1s đến 0.9s -> ranh giới lý thuyết ~ 0.50s
    # Khe thật ở ~ 0.50s -> không bị lệch quá 80ms!
    assert res["n_words"] == 2
    assert not res["flagged"]


def test_check_rendered_video_json(tmp_path):
    # Giả lập file JSON và WAV
    sr = 22050
    y = np.zeros(int(sr * 2.0), dtype=np.float32)
    # Giọng liên tục không có khe rõ rệt, từ dài bất thường
    y[int(sr * 0.1) : int(sr * 1.9)] = 0.5 * np.sin(2 * np.pi * 250 * np.linspace(0, 1.8, int(sr * 1.8)))
    wav_path = tmp_path / "video.wav"
    sf.write(str(wav_path), y, sr)

    json_path = tmp_path / "video.json"
    meta = {
        "output_file": "video.wav",
        "segments": [
            {
                "start": 0.0,
                "end": 2.0,
                # 1 từ duy nhất dài 2.0s -> chắc chắn bị cờ từ dài bất thường
                "text": "chùa",
            }
        ],
    }
    json_path.write_text(json.dumps(meta), encoding="utf-8")

    res = hf_align_check.check_rendered_video(json_path, wav_path)
    assert res["total_sentences"] == 1
    assert res["flagged_sentences"] == 1
    assert res["flagged_ratio"] == 1.0
    assert res["results"][0]["flags"][0]["type"] == "long_word"
