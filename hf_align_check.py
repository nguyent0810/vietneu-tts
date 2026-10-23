"""Kiểm chéo mốc từ của hf_align với khe năng lượng thấp thật trong wav.

So mỗi ranh giới từ với khe năng lượng thấp thật (true dips).
Gắn cờ nếu:
  1. Ranh giới lệch > 80 ms so với khe thật.
  2. Từ dài bất thường (> 0.85s đối với từ đơn hoặc > 0.70s/âm tiết).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import scipy.signal

import hf_align

ROOT = Path(__file__).resolve().parent
DRIFT_THRESHOLD_S = 0.080  # Ngưỡng lệch ranh giới: 80 ms
MAX_SYLLABLE_DUR_S = 0.70  # Ngưỡng thời lượng tối đa cho mỗi âm tiết
MAX_SINGLE_WORD_S = 0.85   # Ngưỡng thời lượng tối đa cho 1 từ đơn


def find_true_dips(env: np.ndarray, hop: float, prominence_ratio: float = 0.15) -> np.ndarray:
    """Tìm các mốc thời gian (giây) của khe năng lượng thấp thật (prominence rõ rệt)."""
    peak_val = float(env.max()) if len(env) > 0 else 0.0
    if peak_val <= 0:
        return np.array([], dtype=float)

    inv_env = peak_val - env
    prominence = peak_val * prominence_ratio
    peaks, _ = scipy.signal.find_peaks(inv_env, prominence=prominence)
    return peaks * hop


def is_word_abnormally_long(
    duration: float,
    weight: float,
    max_syllable_dur: float = MAX_SYLLABLE_DUR_S,
    max_single_dur: float = MAX_SINGLE_WORD_S,
) -> bool:
    """Kiểm tra từ dài bất thường (do TTS kéo dài hoặc chia tỷ lệ sai)."""
    if duration <= 0:
        return False
    if weight <= 1.5 and duration > max_single_dur:
        return True
    if weight > 0 and (duration / weight) > max_syllable_dur:
        return True
    return False


def check_sentence_boundaries(
    env: np.ndarray,
    hop: float,
    start: float,
    end: float,
    text: str,
    true_dips: np.ndarray | None = None,
    drift_threshold: float = DRIFT_THRESHOLD_S,
) -> dict[str, Any]:
    """Kiểm tra ranh giới từ và độ dài từ cho một câu."""
    words = text.split()
    if not words:
        return {
            "flagged": False,
            "text": text,
            "start": start,
            "end": end,
            "flags": [],
            "word_times": [],
        }

    weights = [hf_align.token_weight(w) for w in words]
    times = hf_align.word_times(env, hop, start, end, weights)

    # Tìm true dips nếu chưa truyền vào
    if true_dips is None:
        true_dips = find_true_dips(env, hop)

    peak_val = float(env.max()) if len(env) > 0 else 1.0
    thr_quiet = peak_val * 0.20

    flags: list[dict[str, Any]] = []

    # 1. So ranh giới từ với khe năng lượng thấp thật
    for k in range(len(words) - 1):
        w = words[k]
        t, d = times[k]
        b = round(t + d, 3)
        idx_b = min(len(env) - 1, max(0, int(b / hop)))
        val_b = float(env[idx_b])

        # Nếu ranh giới rơi vào chỗ có tiếng (năng lượng cao)
        if val_b > thr_quiet:
            if len(true_dips) > 0:
                dists = np.abs(true_dips - b)
                best_i = int(np.argmin(dists))
                nearest_dip = float(true_dips[best_i])
                drift = round(abs(b - nearest_dip), 3)
                if drift > drift_threshold:
                    flags.append({
                        "type": "drift",
                        "word": w,
                        "next_word": words[k + 1],
                        "boundary_s": b,
                        "nearest_dip_s": round(nearest_dip, 3),
                        "drift_ms": int(drift * 1000),
                        "energy_at_boundary": round(val_b, 4),
                    })

    # 2. Kiểm tra từ dài bất thường
    for k in range(len(words)):
        w = words[k]
        t, d = times[k]
        wt = weights[k]
        if is_word_abnormally_long(d, wt):
            flags.append({
                "type": "long_word",
                "word": w,
                "start_s": round(t, 3),
                "duration_s": round(d, 3),
                "weight": wt,
            })

    return {
        "flagged": len(flags) > 0,
        "text": text,
        "start": start,
        "end": end,
        "n_words": len(words),
        "flags": flags,
        "word_times": times,
    }


def check_rendered_video(
    json_path: str | Path,
    wav_path: str | Path | None = None,
    drift_threshold: float = DRIFT_THRESHOLD_S,
) -> dict[str, Any]:
    """Kiểm chéo toàn bộ các câu trong một video đã render từ file JSON và WAV."""
    p_json = Path(json_path).resolve()
    if not p_json.exists():
        raise FileNotFoundError(f"JSON not found: {p_json}")

    meta = json.loads(p_json.read_text(encoding="utf-8"))
    if wav_path is None:
        p_wav = p_json.parent / meta.get("output_file", f"{p_json.stem}.wav")
        if not p_wav.exists():
            p_wav = p_json.with_suffix(".wav")
    else:
        p_wav = Path(wav_path).resolve()

    if not p_wav.exists():
        raise FileNotFoundError(f"WAV not found: {p_wav}")

    env, hop = hf_align.energy_envelope(p_wav)
    true_dips = find_true_dips(env, hop)

    segments = meta.get("segments", [])
    sentence_results = []
    flagged_count = 0

    for seg in segments:
        res = check_sentence_boundaries(
            env=env,
            hop=hop,
            start=float(seg["start"]),
            end=float(seg["end"]),
            text=seg["text"],
            true_dips=true_dips,
            drift_threshold=drift_threshold,
        )
        if res["flagged"]:
            flagged_count += 1
        sentence_results.append(res)

    total = len(segments)
    ratio = round(flagged_count / max(1, total), 3)

    return {
        "file": p_json.name,
        "wav": p_wav.name,
        "total_sentences": total,
        "flagged_sentences": flagged_count,
        "flagged_ratio": ratio,
        "results": sentence_results,
    }


def audit_batch(
    items: list[tuple[str | Path, str | Path]],
    drift_threshold: float = DRIFT_THRESHOLD_S,
) -> dict[str, Any]:
    """Chạy kiểm chéo trên một danh sách các cặp (json_path, wav_path)."""
    batch_results = []
    for json_p, wav_p in items:
        res = check_rendered_video(json_p, wav_p, drift_threshold=drift_threshold)
        batch_results.append(res)
    return {
        "total_videos": len(batch_results),
        "videos": batch_results,
    }
