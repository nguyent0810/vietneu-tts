"""Bản đồ beat cho sổ nhạc nền (hf_music.CATALOG).

Mượn ý pdoom-video: dò tempo, mốc beat, mốc nhấn mạnh (onsets/downbeat), và RMS envelope.
Hàm snap(t, beats, tol=0.12) để engine nắn mốc chuyển cảnh, sen nở, dấu son.
Nhạc thiền không trống (confidence < 0.50): trả về "không đủ nhịp" thay vì bịa mốc.
Kết quả được lưu tại chunks_cache/beatmap/<file>.json theo mtime file gốc.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

import hf_music

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "chunks_cache" / "beatmap"
CONFIDENCE_THRESHOLD = 0.50
TOLERANCE = 0.12
SAMPLE_RATE = 22050
RMS_HOP_S = 0.05


def analyze_audio(y: np.ndarray, sr: int = SAMPLE_RATE) -> dict[str, Any]:
    """Phân tích nhịp, độ tin cậy, mốc beat, onsets và RMS envelope từ mảng âm thanh."""
    import librosa  # noqa: PLC0415

    dur = float(len(y) / sr)
    if dur <= 0:
        return {
            "status": "không đủ nhịp",
            "confidence": 0.0,
            "tempo": None,
            "beats": "không đủ nhịp",
            "onsets": [],
            "rms_envelope": {"hop_s": RMS_HOP_S, "values": []},
        }

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # Tín hiệu phẳng (flat signal / drone): onset_env hầu như không biến thiên
    if float(onset_env.std()) < 0.015 or float(onset_env.max()) < 0.05:
        rms = librosa.feature.rms(y=y, hop_length=int(sr * RMS_HOP_S))[0]
        return {
            "status": "không đủ nhịp",
            "confidence": 0.0,
            "tempo": None,
            "beats": "không đủ nhịp",
            "onsets": [],
            "rms_envelope": {
                "hop_s": RMS_HOP_S,
                "values": [round(float(v), 4) for v in rms],
            },
        }

    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units="time")
    tempo_arr, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    bpm = float(np.atleast_1d(tempo_arr)[0])
    raw_beats = librosa.frames_to_time(beat_frames, sr=sr)

    # 1. Tỉ lệ beats rơi trúng onset (trong vòng 120ms)
    if len(raw_beats) > 0 and len(onsets) > 0:
        hits = [np.min(np.abs(onsets - b)) <= 0.12 for b in raw_beats]
        hit_ratio = float(np.mean(hits))
    else:
        hit_ratio = 0.0

    # 2. Tỉ lệ năng lượng onset tại beat so với nền
    valid_frames = beat_frames[beat_frames < len(onset_env)]
    if len(valid_frames) > 0:
        b_ratio = float(onset_env[valid_frames].mean() / max(float(onset_env.mean()), 1e-6))
    else:
        b_ratio = 1.0

    # 3. Tempogram max/mean ratio (độ nét của xung nhịp)
    tg = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
    tg_ratio = float(tg.max(axis=0).mean() / max(float(tg.mean()), 1e-6))

    # Tính confidence score (0.00 -> 1.00)
    c1 = np.clip((hit_ratio - 0.30) / 0.40, 0.0, 1.0)
    c2 = np.clip((b_ratio - 1.5) / 2.5, 0.0, 1.0)
    c3 = np.clip((tg_ratio - 4.0) / 6.0, 0.0, 1.0)
    conf = round(float(0.4 * c1 + 0.4 * c2 + 0.2 * c3), 2)

    has_beat = conf >= CONFIDENCE_THRESHOLD
    beats_res: list[float] | str = (
        [round(float(b), 3) for b in raw_beats] if has_beat else "không đủ nhịp"
    )
    tempo_res: float | None = round(bpm, 1) if has_beat else None
    status_res = "ok" if has_beat else "không đủ nhịp"

    # RMS envelope
    rms = librosa.feature.rms(y=y, hop_length=int(sr * RMS_HOP_S))[0]
    rms_values = [round(float(v), 4) for v in rms]

    return {
        "status": status_res,
        "confidence": conf,
        "tempo": tempo_res,
        "beats": beats_res,
        "onsets": [round(float(o), 3) for o in onsets],
        "rms_envelope": {
            "hop_s": RMS_HOP_S,
            "values": rms_values,
        },
    }


def compute_beatmap(
    audio_path: str | Path,
    cache_dir: Path = CACHE_DIR,
    force: bool = False,
    max_duration: float | None = None,
) -> dict[str, Any]:
    """Tính toán hoặc đọc beatmap từ cache (theo mtime)."""
    p = Path(audio_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Audio file not found: {p}")

    cache_file = cache_dir / f"{p.name}.json"
    mtime = p.stat().st_mtime

    if not force and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("mtime") == mtime:
                return cached
        except Exception:
            pass

    import librosa  # noqa: PLC0415
    y, sr = librosa.load(str(p), sr=SAMPLE_RATE, duration=max_duration)
    result = analyze_audio(y, sr)

    full_record = {
        "file": p.name,
        "path": str(p),
        "mtime": mtime,
        "duration_s": round(float(len(y) / sr), 2),
        **result,
    }

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(full_record, ensure_ascii=False, indent=2), encoding="utf-8")
    return full_record


def get_beatmap(track_name_or_path: str | Path, cache_dir: Path = CACHE_DIR) -> dict[str, Any]:
    """Lấy beatmap cho bài hát trong bgm/ hoặc đường dẫn tuỳ ý."""
    p = Path(track_name_or_path)
    if not p.is_file():
        p_bgm = ROOT / "bgm" / p.name
        if p_bgm.is_file():
            p = p_bgm
    return compute_beatmap(p, cache_dir=cache_dir)


def snap(t: float, beats: list[float] | str | None, tol: float = TOLERANCE) -> float | None:
    """Nắn mốc t về mốc beat gần nhất trong ngưỡng tol.

    Nếu beats là 'không đủ nhịp', None, rỗng, hoặc khoảng cách > tol: trả về None.
    """
    if not isinstance(beats, (list, tuple, np.ndarray)) or len(beats) == 0:
        return None
    b_arr = np.asarray(beats, dtype=float)
    idx = int(np.argmin(np.abs(b_arr - t)))
    nearest = float(b_arr[idx])
    if abs(nearest - t) <= tol:
        return round(nearest, 3)
    return None


def build_all_catalog(root: Path = ROOT, cache_dir: Path = CACHE_DIR) -> dict[str, dict[str, Any]]:
    """Tính và cache toàn bộ bài trong hf_music.CATALOG (bud + fs)."""
    results = {}
    for genre, tracks in hf_music.CATALOG.items():
        for fname, title in tracks:
            fpath = root / "bgm" / fname
            if fpath.exists():
                res = compute_beatmap(fpath, cache_dir=cache_dir)
                results[fname] = res
    return results


if __name__ == "__main__":
    print(f"--- BẮT ĐẦU TÍNH BEATMAP CHO CATALOG (Ngưỡng tin cậy: {CONFIDENCE_THRESHOLD}) ---")
    results = build_all_catalog()
    print(f"{'Thể loại':8} | {'Tên file':30} | {'BPM':6} | {'Độ tin cậy':11} | {'Trạng thái':14}")
    print("-" * 78)
    for genre, tracks in hf_music.CATALOG.items():
        for fname, title in tracks:
            r = results.get(fname)
            if not r:
                continue
            bpm_str = f"{r['tempo']:.1f}" if r["tempo"] is not None else "-"
            print(
                f"{genre.upper():8} | {fname:30} | {bpm_str:>6} | {r['confidence']:>10.2f} | {r['status']:<14}"
            )
