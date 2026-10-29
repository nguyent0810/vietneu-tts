"""Documentary Sound Director — Production Module (Preset C).

Tuân thủ:
  - Ticket #61 (Documentary Sound Director): BGM theo narrative_intent,
    SFX cooldown >= 3.0s né onset giọng, ambience nơi chốn, pre-payoff ducking (-10 dB).
  - Ticket #68 & Kho #47: Âm học chuẩn EBU R128 (-16.0 LUFS Long, TP <= -1.0 dBTP, LRA 2.0-5.0 LU).
  - Loại bỏ hoàn toàn 5 bài cấm lấn giọng (MASKS_VOICE) khỏi Long.
  - Cấu hình hướng dữ liệu qua khoá "sound" trong library/channels/*.yaml, không gõ cứng tên kênh.
  - Tương thích ngược: chỉ kích hoạt khi spec có preset_long == 'C' (hoặc preset == 'C').
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter

import hf_foley as foley
from hyperframes_bridge import integrated_lufs, normalize_loudness, LOUD_TARGET, LOUD_TP

ROOT = Path(__file__).resolve().parent
CHANNELS_DIR = ROOT / "library" / "channels"
BGM_DIR = ROOT / "bgm"
SR = 48000

# 5 bài cấm lấn giọng khỏi Long (Ticket 68 + Sound Catalog P1)
FORBIDDEN_LONG_BGM = {
    "eastern_thought.mp3",
    "comfortable_mystery_4.mp3",
    "parting_of_the_ways_part_1.mp3",
    "wood_and_metal_and_water.mp3",
    "asian_drums.mp3",
}

MOODS = ("curiosity", "tension", "discovery", "reflective", "neutral", "resolution")


def _db(x: float) -> float:
    return float(10 ** (x / 20))


def _st(x: np.ndarray) -> np.ndarray:
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def _lp(x: np.ndarray, hi: float, order: int = 2) -> np.ndarray:
    b, a = butter(order, hi / (SR / 2), "low")
    return lfilter(b, a, x)


def _hp(x: np.ndarray, lo: float, order: int = 2) -> np.ndarray:
    b, a = butter(order, lo / (SR / 2), "high")
    return lfilter(b, a, x)


def load_channel_sound(channel: str, root: Path = ROOT) -> dict:
    """Đọc cấu hình 'sound' từ library/channels/{channel}.yaml (hướng dữ liệu)."""
    cdir = root / "library" / "channels"
    if not cdir.exists():
        return {}
    # 1. Thử file chính xác
    candidates = [
        cdir / f"{channel}.yaml",
        cdir / f"_{channel}.yaml",
    ]
    for p in candidates:
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return dict(data.get("sound") or {})
            except (OSError, ValueError):
                pass
    # 2. Quét các file tìm trường 'kenh' trùng khớp
    for p in cdir.glob("*.yaml"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("kenh") == channel:
                return dict(data.get("sound") or {})
        except (OSError, ValueError):
            continue
    return {}


def new_sound(channel: str, root: Path = ROOT, **overrides) -> dict:
    """Tạo cấu hình Sound Director C cho render MỚI từ hồ sơ kênh."""
    cfg = load_channel_sound(channel, root=root)
    spec = {
        "preset_long": cfg.get("preset_long", "C"),
        "bgm_mac_dinh": cfg.get("bgm_mac_dinh"),
        "ducking_db": float(cfg.get("ducking_db", 6.0)),
        "music_gap_db": float(cfg.get("music_gap_db", 18.0)),
        "pre_payoff_duck_db": float(cfg.get("pre_payoff_duck_db", -10.0)),
        "sfx_cooldown_s": float(cfg.get("sfx_cooldown_s", 3.0)),
        "sfx_density_per_min": int(cfg.get("sfx_density_per_min", 2)),
        "mood_mapping": dict(cfg.get("mood_mapping") or {}),
        "cam": list(cfg.get("cam") or []),
        "target_lufs": dict(cfg.get("target_lufs") or {"long": -16.0, "short": -14.0}),
        "max_true_peak_dbtp": float(cfg.get("max_true_peak_dbtp", -1.0)),
    }
    spec.update(overrides)
    return spec


def is_preset_c(spec: dict | None) -> bool:
    """Kiểm tra spec có yêu cầu preset âm thanh C không."""
    if not spec or not isinstance(spec, dict):
        return False
    return spec.get("preset_long") == "C" or spec.get("preset") == "C"


def extract_words(lines: list[dict], tts_json_path: Path | None = None) -> list[dict]:
    """Trích xuất danh sách từ và mốc thời gian từ lines hoặc file tts manifest."""
    words: list[dict] = []
    if lines:
        for ln in lines:
            if "words" in ln and isinstance(ln["words"], list):
                for w in ln["words"]:
                    words.append({
                        "word": w.get("word", w.get("text", "")),
                        "start": float(w.get("start", w.get("t", 0.0))),
                        "end": float(w.get("end", float(w.get("start", w.get("t", 0.0))) + 0.3)),
                    })
    if not words and tts_json_path and tts_json_path.exists():
        try:
            data = json.loads(tts_json_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for it in data:
                    if "words" in it:
                        words.extend(it["words"])
                    elif "start" in it and "word" in it:
                        words.append(it)
            elif isinstance(data, dict):
                if "words" in data:
                    words.extend(data["words"])
                elif "segments" in data:
                    for seg in data["segments"]:
                        if "words" in seg:
                            words.extend(seg["words"])
                        else:
                            words.append({
                                "word": seg.get("text", ""),
                                "start": float(seg.get("start", 0.0)),
                                "end": float(seg.get("end", 0.0)),
                            })
        except Exception:
            pass
    return words


def check_sfx_voice_overlap(sfx_events: list[dict], words: list[dict]) -> list[dict]:
    """Phát hiện SFX rơi vào khoảng onset từ [w_st - 0.05, w_st + 0.15]."""
    conflicts = []
    for ev in sfx_events:
        t_sfx = float(ev.get("time", ev.get("t", 0.0)))
        sfx_name = ev.get("name", ev.get("s", "sfx"))
        for w in words:
            w_st = float(w.get("start", 0.0))
            if (w_st - 0.05) <= t_sfx <= (w_st + 0.15):
                conflicts.append({
                    "sfx": sfx_name,
                    "sfx_time": round(t_sfx, 3),
                    "word": w.get("word", ""),
                    "word_start": round(w_st, 3),
                    "delta_ms": round((t_sfx - w_st) * 1000, 1),
                })
    return conflicts


def shift_sfx_safe(t_sfx: float, words: list[dict], min_t: float = 0.0, max_t: float = 1e9) -> float:
    """Dịch nhẹ SFX ra khỏi vùng nguy hiểm onset từ (né onset giọng)."""
    t_out = float(t_sfx)
    for w in words:
        w_st = float(w.get("start", 0.0))
        w_end = float(w.get("end", w_st + 0.3))
        if (w_st - 0.05) <= t_out <= (w_st + 0.15):
            # Nếu chạm onset: lùi trước 0.15s nếu có chỗ, hoặc đẩy sau khi dứt từ 0.05s
            if t_out < w_st and (w_st - 0.15) >= min_t:
                t_out = w_st - 0.15
            else:
                t_out = min(max_t, w_end + 0.05)
    return max(min_t, min(max_t, t_out))


def filter_sfx_cooldown(
    events: list[dict],
    cooldown_same: float = 3.0,
    cooldown_diff: float = 1.5,
    max_per_min: float = 3.0,
    dur: float = 0.0,
) -> list[dict]:
    """Áp dụng cooldown SFX: cùng loại >= 3s, khác loại >= 1.5s, mật độ <= max_per_min."""
    sorted_ev = sorted(events, key=lambda e: float(e.get("time", e.get("t", 0.0))))
    accepted: list[dict] = []
    last_same: dict[str, float] = {}
    last_any: float = -999.0

    for ev in sorted_ev:
        t = float(ev.get("time", ev.get("t", 0.0)))
        name = str(ev.get("name", ev.get("s", "sfx")))
        # Kiểm tra cooldown cùng loại
        if name in last_same and (t - last_same[name]) < cooldown_same:
            continue
        # Kiểm tra cooldown khác loại
        if (t - last_any) < cooldown_diff:
            continue
        # Kiểm tra mật độ cửa sổ 60s
        recent = [e for e in accepted if (t - float(e.get("time", e.get("t", 0.0)))) <= 60.0]
        if len(recent) >= max_per_min:
            continue

        accepted.append(ev)
        last_same[name] = t
        last_any = t

    return accepted


def resolve_mood_segments(lines: list[dict], dur: float, sound_cfg: dict) -> list[dict]:
    """Xác định các phân đoạn cảm xúc (mood segments) cho video.
    
    Ưu tiên:
      1. sound_cfg['mood_segments'] (nếu khai báo tường minh)
      2. lines có 'narrative_intent' / 'intent' / 'mood'
      3. lines có thẻ chương 'heading'
      4. fallback: 1 phân đoạn 'neutral' hoặc 'reflective'
    """
    if sound_cfg.get("mood_segments"):
        return list(sound_cfg["mood_segments"])

    # Kiểm tra intent trên lines
    annotated = []
    for ln in lines:
        intent = ln.get("narrative_intent") or ln.get("intent") or ln.get("mood")
        if intent:
            annotated.append((float(ln.get("start", 0.0)), float(ln.get("end", 0.0)), str(intent)))

    if annotated:
        # Nhóm các dòng liên tiếp cùng mood
        segs: list[dict] = []
        cur_mood = annotated[0][2]
        cur_st = annotated[0][0]
        cur_en = annotated[0][1]
        for st, en, mi in annotated[1:]:
            if mi == cur_mood:
                cur_en = en
            else:
                segs.append({"start": cur_st, "end": cur_en, "mood": cur_mood})
                cur_st, cur_en, cur_mood = st, en, mi
        segs.append({"start": cur_st, "end": max(dur, cur_en), "mood": cur_mood})
        if segs and segs[0]["start"] > 0:
            segs[0]["start"] = 0.0
        return segs

    # Kiểm tra thẻ chương
    headings = [float(ln.get("start", 0.0)) for ln in lines if ln.get("heading")]
    if len(headings) >= 2:
        cuts = [0.0] + [h for h in headings if 0 < h < dur] + [dur]
        cycle = ["curiosity", "reflective", "tension", "resolution"]
        segs = []
        for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
            segs.append({"start": a, "end": b, "mood": cycle[i % len(cycle)]})
        return segs

    # Fallback an toàn
    default_mood = "reflective" if "white_lotus" in str(sound_cfg.get("bgm_mac_dinh", "")) else "neutral"
    return [{"start": 0.0, "end": dur, "mood": default_mood}]


def pick_mood_track(mood: str, sound_cfg: dict, series: str, seed: int = 11, root: Path = ROOT) -> str:
    """Chọn bài nhạc phù hợp mood từ mood_mapping, loại bỏ bài thuộc FORBIDDEN_LONG_BGM."""
    mm = sound_cfg.get("mood_mapping") or {}
    candidates = mm.get(mood) or []
    # Lọc bỏ bài cấm
    safe = [c for c in candidates if Path(c).name not in FORBIDDEN_LONG_BGM]
    if safe:
        # Chọn tất định theo seed + hash mood
        idx = (seed + sum(ord(c) for c in mood)) % len(safe)
        return safe[idx]
    # Fallback
    fallback = sound_cfg.get("bgm_mac_dinh") or ("white_lotus.mp3" if series == "bud" else "thinking_music.mp3")
    if Path(fallback).name in FORBIDDEN_LONG_BGM:
        fallback = "white_lotus.mp3" if series == "bud" else "thinking_music.mp3"
    return str(fallback)


def build_bgm_layer(
    lines: list[dict],
    dur: float,
    sound_cfg: dict,
    series: str,
    voice_sig: np.ndarray,
    voice_lufs: float,
    root: Path = ROOT,
    seed: int = 11,
) -> tuple[np.ndarray, list[str]]:
    """Dựng lớp nhạc nền (BGM) đa sắc thái theo mood, crossfade, ducking giọng và pre-payoff ducking."""
    N = int(dur * SR)
    music = np.zeros((N, 2), dtype="float32")
    segs = resolve_mood_segments(lines, dur, sound_cfg)
    used_tracks: list[str] = []

    p_foley = foley.Foley(seed)

    for i, seg in enumerate(segs):
        st_s, en_s = float(seg["start"]), float(seg["end"])
        mood = seg.get("mood", "neutral")
        track_spec = seg.get("track") or pick_mood_track(mood, sound_cfg, series, seed=seed + i, root=root)
        used_tracks.append(Path(track_spec).name)

        s_idx = int(st_s * SR)
        e_idx = min(N, int(en_s * SR))
        seg_dur = (e_idx - s_idx) / SR
        if seg_dur <= 0.05:
            continue

        # Tạo tín hiệu nhạc cho đoạn
        if "drone" in track_spec:
            # Drone thủ tục
            root_freq = 73.42 if ("bud" in series or "bud" in track_spec) else 110.0
            dr = p_foley.drone(seg_dur, root=root_freq)[: int(seg_dur * SR)]
            seg_sig = np.stack([dr, dr], axis=1) * 0.7
        else:
            bgm_file = root / track_spec if not Path(track_spec).is_absolute() else Path(track_spec)
            if not bgm_file.exists() and not bgm_file.name.startswith("bgm/"):
                bgm_file = root / "bgm" / bgm_file.name
            if bgm_file.exists():
                seg_sig = foley._decode(bgm_file, seg_dur)[: int(seg_dur * SR)]
            else:
                # Fallback drone nếu thiếu file
                dr = p_foley.drone(seg_dur, root=73.42)[: int(seg_dur * SR)]
                seg_sig = np.stack([dr, dr], axis=1) * 0.5

        # Chuyển mềm (Crossfade) 1.5s - 2.0s
        fade_len = int(min(2.0, seg_dur / 2) * SR)
        if fade_len > 0:
            if i > 0:
                ramp_in = np.linspace(0, 1, fade_len, dtype="float32")[:, None]
                seg_sig[:fade_len] *= ramp_in
            if i < len(segs) - 1:
                ramp_out = np.linspace(1, 0, fade_len, dtype="float32")[:, None]
                seg_sig[-fade_len:] *= ramp_out

        music[s_idx: s_idx + len(seg_sig)] += seg_sig[: N - s_idx]

    # Chuẩn hoá độ to nền nhạc dưới giọng
    music_gap = float(sound_cfg.get("music_gap_db", 18.0))
    L_m = foley.lufs(music)
    if not np.isneginf(L_m) and L_m > -80:
        music *= _db(voice_lufs - music_gap - L_m)

    # 1. Ducking giọng nói
    duck_db = float(sound_cfg.get("ducking_db", 6.0))
    env = foley.envelope(voice_sig)
    env = np.pad(env, (0, max(0, N - len(env))))[:N]
    duck_voice = 1.0 - (1.0 - _db(-duck_db)) * env

    # 2. Pre-payoff ducking trước cú lật / câu hỏi then chốt
    payoff_duck = np.ones(N, dtype="float32")
    pre_duck_val = _db(float(sound_cfg.get("pre_payoff_duck_db", -10.0)))
    t_axis = np.arange(N) / SR

    # Điểm payoff từ sound_cfg hoặc lines
    payoff_times = []
    for ln in lines:
        if ln.get("payoff") or ln.get("twist") or ln.get("drop"):
            payoff_times.append(float(ln.get("start", 0.0)))
    for p_val in sound_cfg.get("payoffs") or sound_cfg.get("drops") or []:
        if isinstance(p_val, (int, float)):
            payoff_times.append(float(p_val))
    for win in sound_cfg.get("pre_payoff_windows") or []:
        if isinstance(win, dict) and "start" in win and "end" in win:
            w_st, w_en = float(win["start"]), float(win["end"])
            payoff_duck *= np.where((t_axis >= w_st) & (t_axis <= w_en), pre_duck_val, 1.0)

    for pt in payoff_times:
        # Hạ nhạc đón đầu trước 1.2s, tắt nhẹ 0.3s trước, hồi phục trong 2.0s
        t_pre = max(0.0, pt - 1.2)
        t_post = pt + 2.0
        mask_pre = (t_axis >= t_pre) & (t_axis <= pt)
        mask_post = (t_axis > pt) & (t_axis <= t_post)
        payoff_duck[mask_pre] *= pre_duck_val
        # Phục hồi dần
        if np.any(mask_post):
            ramp = np.linspace(pre_duck_val, 1.0, np.sum(mask_post), dtype="float32")
            payoff_duck[mask_post] *= ramp

    # Nhân tổng ducking
    duck_total = duck_voice * payoff_duck
    music *= duck_total[:, None]

    # Fade out cuối bài (2.0s)
    fade_end = np.clip((dur - t_axis) / 2.0, 0, 1)[:, None]
    music *= fade_end

    return music, list(dict.fromkeys(used_tracks))


def build_ambience_layer(
    lines: list[dict],
    dur: float,
    sound_cfg: dict,
    voice_lufs: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Dựng lớp không khí nơi chốn (Ambience) tổng hợp tự nhiên, mức -25 dB so với giọng."""
    N = int(dur * SR)
    amb = np.zeros(N, dtype="float32")
    specs = sound_cfg.get("amb") or []

    for a in specs:
        kind = a.get("kind", "river")
        st = float(a.get("from_s", a.get("from", 0.0)))
        en = float(a.get("to_s", a.get("to", dur)))
        st = max(0.0, st)
        en = min(dur, en)
        if en <= st:
            continue
        amb_dur = en - st
        sig = foley.ambience(kind, amb_dur, rng)
        # Fade in/out 2.0s
        fade_n = int(min(2.0, amb_dur / 2) * SR)
        if fade_n > 0:
            sig[:fade_n] *= np.linspace(0, 1, fade_n, dtype="float32")
            sig[-fade_n:] *= np.linspace(1, 0, fade_n, dtype="float32")
        i_st = int(st * SR)
        amb[i_st: i_st + len(sig)] += sig[: N - i_st]

    if np.abs(amb).max() > 0:
        amb_gap = float(sound_cfg.get("amb_gap_db", sound_cfg.get("amb_gap", 25.0)))
        L_a = foley.lufs(amb)
        if not np.isneginf(L_a) and L_a > -80:
            amb *= _db(voice_lufs - amb_gap - L_a)

    return _st(amb)


def build_sfx_layer(
    lines: list[dict],
    series: str,
    dur: float,
    sound_cfg: dict,
    voice_max: float,
    words: list[dict],
    seed: int = 11,
) -> tuple[np.ndarray, list[dict]]:
    """Dựng lớp hiệu ứng âm thanh (SFX) có cooldown, né onset từ và kiểm soát đỉnh."""
    N = int(dur * SR)
    sfx_bus = np.zeros((N, 2), dtype="float32")
    p_foley = foley.Foley(seed)

    # Thu thập sự kiện thô
    raw_events: list[dict] = []
    if sound_cfg.get("sfx_events"):
        for ev in sound_cfg["sfx_events"]:
            raw_events.append(dict(ev))
    else:
        # Lấy từ hf_foley.events
        for t, name, g, kw in foley.events(lines, series, sound_cfg, set()):
            raw_events.append({"time": t, "name": name, "gain": g, "kw": kw})

    # 1. Né TTS onset (Timing Safety)
    safe_events: list[dict] = []
    for ev in raw_events:
        t_orig = float(ev.get("time", ev.get("t", 0.0)))
        t_safe = shift_sfx_safe(t_orig, words, min_t=0.0, max_t=dur - 0.2)
        safe_ev = dict(ev)
        safe_ev["time"] = t_safe
        safe_events.append(safe_ev)

    # 2. Lọc theo quy tắc Cooldown & Density
    cooldown_same = float(sound_cfg.get("sfx_cooldown_s", 3.0))
    density = int(sound_cfg.get("sfx_density_per_min", 2))
    filtered_events = filter_sfx_cooldown(
        safe_events,
        cooldown_same=cooldown_same,
        cooldown_diff=1.5,
        max_per_min=float(density),
        dur=dur,
    )

    # 3. Tổng hợp âm thanh
    for k, ev in enumerate(filtered_events):
        t = float(ev.get("time", 0.0))
        name = str(ev.get("name", "bell"))
        gain = float(ev.get("gain", 0.4))
        kw = ev.get("kw") or {}

        if name == "temple_bell":
            sig = p_foley.temple_bell(dur=float(kw.get("dur", 8.0)))
        elif name == "bowl":
            sig = p_foley.bowl(f0=float(kw.get("f0", 196.0)), dur=float(kw.get("dur", 6.0)))
        elif name == "pluck":
            sig = p_foley.pluck(kw.get("f", 220.0), dur=float(kw.get("dur", 3.0)))
        elif name == "hooves":
            sig = p_foley.hooves(float(kw.get("dur", 3.0)))
        elif name == "ratchet":
            sig = p_foley.ratchet(int(kw.get("n", 10)))
        elif name == "motif":
            sig = foley.motif(p_foley, series == "fs")
        elif hasattr(p_foley, name):
            sig = getattr(p_foley, name)()
        else:
            sig = p_foley.bell()

        # Chuẩn hoá đỉnh sóng đơn vị về 1.0
        sig_pk = np.abs(sig).max()
        if sig_pk > 1e-6:
            sig = sig / sig_pk
        sig = sig * gain

        # Pan stereo nhẹ
        pan = float(kw.get("pan", ((k * 37) % 11 - 5) / 30))
        left = sig * np.clip(1.0 - pan, 0, 1)
        right = sig * np.clip(1.0 + pan, 0, 1)
        st_sig = np.stack([left, right], axis=1)

        i_st = int(t * SR)
        i_en = min(N, i_st + len(st_sig))
        if i_st < N:
            sfx_bus[i_st:i_en] += st_sig[: i_en - i_st]

    # 4. Kiểm soát đỉnh toàn lớp SFX (Chống nén sụt toàn bài)
    pk_total = np.abs(sfx_bus).max()
    if pk_total > 0:
        sfx_peak_ratio = float(sound_cfg.get("sfx_peak", 0.25))  # -12 dB so với đỉnh giọng
        target_sfx_pk = max(0.1, voice_max * sfx_peak_ratio)
        sfx_bus *= target_sfx_pk / pk_total

    return sfx_bus, filtered_events


def mix_long_c(
    lines: list[dict],
    series: str,
    voice_wav: Path,
    bgm: Path | None,
    duration: float,
    spec: dict,
    silence: set[int],
    out_wav: Path,
    seed: int = 11,
    pool: list[str] | None = None,
) -> Path:
    """Trộn 4 lớp âm thanh chuẩn Preset C theo kiến trúc Documentary Sound Director."""
    # Nạp cấu hình kênh và kết hợp với spec
    chan_cfg = load_channel_sound(series)
    sound_cfg = {**chan_cfg, **(spec or {})}
    sound_cfg["preset_long"] = "C"

    # Đọc giọng nói
    v, sr = sf.read(voice_wav, dtype="float32")
    if sr != SR:
        from scipy.signal import resample_poly
        v = resample_poly(v, SR, sr).astype("float32")
    if v.ndim == 2:
        v = v.mean(axis=1)

    N = int(duration * SR)
    v = np.pad(v, (0, max(0, N - len(v))))[:N]

    # Lọc EQ cho giọng kể (Highpass 70Hz, Lowpass 10.5kHz)
    if sound_cfg.get("voice_eq", True):
        v = _hp(v, 70.0)
        v = _lp(v, float(sound_cfg.get("voice_lp", 10500.0))).astype("float32")

    voice_lufs = foley.lufs(v)
    voice_max = float(np.abs(v).max())
    voice_st = np.stack([v, v], axis=1)

    # Lớp Reverb nếu có
    if sound_cfg.get("reverb"):
        from scipy.signal import fftconvolve
        ir = foley.reverb_ir(seed, float(sound_cfg.get("reverb_decay", 0.38)))
        wet = np.stack([fftconvolve(v, ir[:, c])[:N] for c in range(2)], axis=1)
        voice_st = voice_st + wet * float(sound_cfg["reverb"])

    # 1. BGM nền đa sắc thái theo mood
    music, used_bgm = build_bgm_layer(
        lines,
        duration,
        sound_cfg,
        series,
        v,
        voice_lufs,
        root=ROOT,
        seed=seed,
    )

    # 2. Không khí nơi chốn (Ambience)
    rng = np.random.default_rng(seed)
    amb = build_ambience_layer(lines, duration, sound_cfg, voice_lufs, rng)

    # 3. Hiệu ứng âm thanh (SFX)
    words = extract_words(lines, voice_wav.with_suffix(".json"))
    sfx, applied_sfx = build_sfx_layer(lines, series, duration, sound_cfg, voice_max, words, seed=seed)

    # Ghép 4 lớp
    mixed = voice_st + music + amb + sfx

    # Ghi nhận danh mục nhạc nền đã dùng vào .bgm.json
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    out_wav.with_suffix(".bgm.json").write_text(json.dumps(used_bgm, ensure_ascii=False), encoding="utf-8")

    # Chuẩn hoá độ to & giới hạn đỉnh thật theo quy chuẩn ITU-R BS.1770 / EBU R128
    target_lufs = float(sound_cfg.get("target_lufs", {}).get("long", LOUD_TARGET["long"]))
    with tempfile.TemporaryDirectory() as td:
        tmp_raw = Path(td) / "raw.wav"
        sf.write(tmp_raw, mixed.astype("float32"), SR, subtype="PCM_24")
        normalize_loudness(tmp_raw, out_wav, target_lufs)

    return out_wav


def render_pilot_c_production(
    out_wav: Path,
    out_mp4: Path | None = None,
    root: Path = ROOT,
) -> dict:
    """Render lại pilot BUD 130s qua đường production Sound Director C và trả về số đo."""
    from hyperframes_bridge import build_lines, mux_audio
    from output.cl_staging.grok.samples.sound_director.qa_mixing_measure import run_qa

    voice_wav = root / "output/cl_staging/long_lab/out/L_lab_bt01_tours.wav"
    txt_file = root / "output/cl_staging/long_lab/out/L_lab_bt01_tours.txt"
    manifest_json = root / "output/cl_staging/long_lab/out/L_lab_bt01_tours.json"
    silent_mp4 = root / "output/cl_staging/grok/samples/sound_director/pilot/silent.mp4"

    meta = json.loads(manifest_json.read_text(encoding="utf-8"))
    dur = float(meta.get("duration_s", 130.23))

    glines = build_lines(txt_file, manifest_json, align_audio=voice_wav)

    # Cấu hình Sound Director C chuẩn cho pilot BUD 130s
    bud_cfg = new_sound("bud", root=root)
    bud_cfg.update({
        "mood_segments": [
            {"start": 0.0, "end": 35.0, "mood": "discovery", "track": "bgm/starry.mp3"},
            {"start": 33.0, "end": 68.0, "mood": "reflective", "track": "bgm/white_lotus.mp3"},
            {"start": 67.0, "end": 94.0, "mood": "tension", "track": "drone_bud"},
            {"start": 93.0, "end": dur, "mood": "resolution", "track": "bgm/meditation_impromptu_03.mp3"},
        ],
        "pre_payoff_windows": [
            {"start": 67.5, "end": 70.0},
            {"start": 114.0, "end": 118.0},
        ],
        "amb": [
            {"from_s": 46.0, "to_s": 66.0, "kind": "river"},
            {"from_s": 68.0, "to_s": 88.0, "kind": "wind"},
            {"from_s": 110.0, "to_s": dur, "kind": "birds"},
        ],
        "sfx_events": [
            {"time": 0.5, "name": "bowl", "gain": 0.35, "kw": {"f0": 146.83, "dur": 6.0}},
            {"time": 34.5, "name": "temple_bell", "gain": 0.30, "kw": {"dur": 8.0}},
            {"time": 118.5, "name": "bowl", "gain": 0.35, "kw": {"f0": 196.0, "dur": 7.0}},
        ],
    })

    mix_long_c(
        lines=glines,
        series="bud",
        voice_wav=voice_wav,
        bgm=None,
        duration=dur,
        spec=bud_cfg,
        silence=set(),
        out_wav=out_wav,
        seed=17,
    )

    if out_mp4 and silent_mp4.exists():
        mux_audio(silent_mp4, out_wav, out_mp4, duration=dur, loudness=LOUD_TARGET["long"])

    # Đo kiểm QA Mixing
    target_to_measure = out_mp4 if (out_mp4 and out_mp4.exists()) else out_wav
    qa_result = run_qa(target_to_measure, tts_file=manifest_json, lane="long")
    return qa_result
