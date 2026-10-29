"""Giọng đọc video dài: TTS TỪNG CÂU bằng VieNeu v3, mỗi câu một giọng / tốc độ / khoảng nghỉ.

Khác `_short_tts_render.py` (đọc cả kịch bản một giọng, khoảng lặng do bộ tách câu
quyết định): video dài cần
  - khoảng nghỉ CÓ CHỦ ĐÍCH sau từng câu (sau câu đỉnh 1,2-1,5 giây, sau câu hỏi 0,6),
    học từ V2 (motion/long/RETENTION.md) -- im lặng là một nhịp kể;
  - giọng thứ hai cho câu trích kinh / cổ thư (người nghe nghe ra "đây là lời kinh");
  - nhịp chậm hơn cho kênh Phật giáo (atempo, giữ cao độ);
  - cache theo từng câu: sửa một câu chỉ đọc lại câu đó.

Ra wav 48 kHz + manifest .json cùng dạng manifest cũ (segments khớp 1-1 với dòng
kịch bản) -> bridge / hf_align dùng y như trước.

    spec = {"voice": "Binh", "engine": "standard", "tempo": 0.86,
            "alt": {"voice": "Quang Sơn", "engine": "v3", "style": "tu_nhien", "tempo": 0.88, "lines": [17]},
            "pause": 0.4, "pauses": {"4": 1.4}}
    synth(lines, spec, out_wav)

Cờ giọng D (task 92a) nằm trong plan tts / tts_ruleset.json, không gõ tên kênh trong code:
  temperature  -- lần thử đầu; cascade đọc lại = giá trị này rồi phần còn lại của dãy cũ
  donor        -- reference codes của preset khác, chỉ v3; giọng alt không thừa kế
  text_mode    -- "speech" (số→chữ, gạch nối, phẩy liên từ) hoặc "production"
Plan không có các khoá này giữ hành vi + khoá cache cũ (render lại #72).
"""
from __future__ import annotations

import hashlib
import os
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

import tts_lexicon

ROOT = Path(__file__).parent
CACHE = ROOT / "chunks_cache" / "voice_lines"
SR = 48000
VERSION = "1"
# Đổi phiên bản trọng số model (hoặc ghi chú bất kỳ làm cũ cache) mà không đụng code: đặt VIENEU_MODEL_TAG.
# Không đặt = khoá cache y hệt trước đây, cache hiện có còn dùng được.
MODEL_TAG = os.environ.get("VIENEU_MODEL_TAG", "")
FADE_S = 0.008          # fade đầu/cuối mỗi câu khi ghép -- chặn tiếng click ở chỗ nối
LEVEL_TARGET_DB = -23.0  # RMS đích khi bật spec["level"]
LEVEL_MAX_DB = 4.0       # không kéo một câu quá ±4 dB
RETRY_V3 = (0.8, 0.7, 0.9, 0.6)
RETRY_STD = (1.0, 0.9, 1.1, 0.8)
RULESET_PATH = ROOT / "tts_ruleset.json"


def clean(line: str) -> str:
    return line.replace("**", "").strip()


def default_pause(line: str, base: float, is_alt: bool = False, pause_ctx: bool = False) -> float:
    t = clean(line)
    if line.startswith("**") and line.endswith("**"):
        return max(base, 0.9)                  # tiêu đề chương: để thẻ chương thở
    if t.endswith("?"):
        return max(base, 0.6)
    if pause_ctx:
        if is_alt:
            return max(base, 0.7)              # câu trích kinh / giọng thứ hai: để lời kinh lắng
        if t.endswith(":") or t.endswith("…"):
            return max(base, 0.5)              # câu dẫn vào thoại / liệt kê: ngắt trước phần theo sau
    return base


def trim(a: np.ndarray, sr: int, pad: float = 0.04, thresh_db: float = -45) -> np.ndarray:
    """Cắt lặng hai đầu (TTS tự thêm lặng không đều) -> khoảng nghỉ do kịch bản quyết."""
    if not len(a):
        return a
    win = int(sr * 0.01)
    n = len(a) // win
    if n < 3:
        return a
    rms = np.sqrt((a[: n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
    loud = np.where(20 * np.log10(rms / (rms.max() + 1e-12)) > thresh_db)[0]
    if not len(loud):
        return a
    s = max(0, loud[0] * win - int(pad * sr))
    e = min(len(a), (loud[-1] + 1) * win + int(pad * sr))
    return a[s:e]


def tempo(a: np.ndarray, sr: int, k: float) -> np.ndarray:
    """Đổi nhịp giữ cao độ (ffmpeg atempo, WSOLA -- sạch hơn phase vocoder với giọng nói)."""
    if abs(k - 1.0) < 1e-3:
        return a
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "a.wav", Path(td) / "b.wav"
        sf.write(src, a, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"atempo={k}", str(dst)], check=True)
        b, _ = sf.read(dst, dtype="float32")
    return b


def suspect(text: str, a: np.ndarray, sr: int) -> str | None:
    """Đọc lồng / cụt: giọng Việt ~13-19 ký tự/giây."""
    dur, n = len(a) / sr, len(text)
    if dur > max(3.0, n / 13 * 2.2):
        return f"dài bất thường {dur:.1f}s cho {n} ký tự"
    if n > 12 and dur < n / 30:
        return f"ngắn bất thường {dur:.1f}s"
    return None


def pick_device() -> str:
    """VIENEU_DEVICE nếu có; không thì mps (Mac) > cuda > cpu."""
    env = os.environ.get("VIENEU_DEVICE")
    if env:
        return env
    try:
        import torch  # noqa: PLC0415
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
    except Exception:  # noqa: BLE001 -- không có torch / backend hỏng: rơi về cpu
        pass
    return "cpu"


def load_ruleset() -> dict:
    """Hồ sơ giọng theo kênh (dữ liệu). Không có file thì dict rỗng."""
    try:
        data = json.loads(RULESET_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: v for k, v in data.items() if not str(k).startswith("_") and isinstance(v, dict)}


def new_tts(channel: str, **fields) -> dict:
    """Spec tts cho render MỚI: ruleset kênh + voice/tempo/pause... Plan cũ không gọi hàm này."""
    spec = dict(load_ruleset().get(channel) or {})
    spec.update(fields)
    return spec


def retry_temps(engine: str, first: float | None = None) -> tuple[float, ...]:
    """Lần thử đầu = first (nếu có); cascade đọc lại = phần còn lại của dãy cũ, bỏ trùng."""
    base = RETRY_V3 if engine == "v3" else RETRY_STD
    if first is None:
        return base
    first = float(first)
    rest = tuple(t for t in base if abs(t - first) > 1e-9)
    return (first, *rest)


def mix_donor(preset: dict, donor_preset: dict) -> dict:
    """Giữ speaker_emb giọng kênh, lấy codes của donor (chỉ v3). Không sửa dict gốc."""
    out = dict(preset)
    out["codes"] = donor_preset["codes"]
    return out


def spoken_text(text: str, spec: dict) -> str:
    use_lexicon = spec.get("lexicon", True)
    if spec.get("text_mode") == "speech":
        return tts_lexicon.speech_text(text, lexicon=use_lexicon)
    return tts_lexicon.apply(text) if use_lexicon else text


def uses_new_cache(spec: dict) -> bool:
    """Có temperature / donor / text_mode trong spec → khoá cache mới. Vắng cả ba = khoá cũ."""
    return "temperature" in spec or "donor" in spec or "text_mode" in spec


def _seed_call(seed: int | None) -> None:
    if seed is None:
        return
    np.random.seed(int(seed))
    random.seed(int(seed))


def line_donor(spec: dict, idx: int, engine: str) -> str | None:
    """Donor chỉ v3. Giọng alt không thừa kế donor của giọng chính."""
    if engine != "v3":
        return None
    alt = spec.get("alt") or {}
    if idx in (alt.get("lines") or []):
        d = alt.get("donor")
        return str(d) if d else None
    d = spec.get("donor")
    return str(d) if d else None


def line_temperature(spec: dict, idx: int) -> float | None:
    alt = spec.get("alt") or {}
    if idx in (alt.get("lines") or []) and "temperature" in alt:
        return float(alt["temperature"])
    if "temperature" in spec:
        return float(spec["temperature"])
    return None


class Voices:
    """Hai model: "v3" (v3turbo 48 kHz, 14 giọng) và "standard" (24 kHz -- giọng các
    kênh đang dùng: Binh cho Phật giáo, Sơn cho Phong Thuỷ). Nạp model nào cần thì nạp."""

    def __init__(self):
        self.m: dict = {}
        self.retries = 0     # số lần phải đọc lại vì nghi lỗi (đếm theo lượt gọi say)

    def _model(self, engine: str):
        if engine not in self.m:
            from vieneu import Vieneu  # noqa: PLC0415
            dev = pick_device()
            self.m[engine] = (Vieneu() if engine == "v3" else
                              Vieneu(mode="standard", backbone_device=dev, codec_device=dev))
        return self.m[engine]

    def _payload(self, model, voice: str, donor: str | None, engine: str):
        me = model.get_preset_voice(voice)
        if not donor or engine != "v3":
            return me
        return mix_donor(me, model.get_preset_voice(donor))

    def _infer_once(self, v, text: str, payload, style: str, engine: str, temp: float, seed: int | None):
        from scipy.signal import resample_poly  # noqa: PLC0415
        kw = {"style": style} if engine == "v3" else {"skip_normalize": False}
        _seed_call(seed)
        if engine != "v3" and seed is not None:
            bb = getattr(v, "backbone", None)
            orig = getattr(bb, "__call__", None) if bb is not None else None
            if orig is not None:
                def _call(*a, **k):
                    k["seed"] = seed
                    return orig(*a, **k)
                bb.__call__ = _call
                try:
                    a = np.asarray(v.infer(text, voice=payload, temperature=temp, **kw), dtype="float32")
                finally:
                    bb.__call__ = orig
            else:
                a = np.asarray(v.infer(text, voice=payload, temperature=temp, **kw), dtype="float32")
        else:
            a = np.asarray(v.infer(text, voice=payload, temperature=temp, **kw), dtype="float32")
        if v.sample_rate != SR:
            a = resample_poly(a, SR, v.sample_rate).astype("float32")
        return a

    def say(self, text: str, voice: str, style: str, engine: str = "v3",
            temperature: float | None = None, donor: str | None = None,
            seed: int | None = None) -> tuple[np.ndarray, str | None]:
        """Trả (audio, lý_do_nghi_lỗi). lý_do = None nghĩa là đạt; khác None nghĩa là CẢ các lần thử đều nghi lỗi
        và audio trả về là lần cuối -- người gọi phải báo, KHÔNG được coi như đạt."""
        v = self._model(engine)
        payload = self._payload(v, voice, donor, engine)
        best, why = None, None
        for n, temp in enumerate(retry_temps(engine, temperature)):
            a = self._infer_once(v, text, payload, style, engine, temp,
                                 None if seed is None else int(seed) + n)
            best, why = a, suspect(text, a, SR)
            if why is None:
                return a, None
            self.retries += 1
            print(f"    nghi lỗi ({why}), đọc lại temp={temp}", file=sys.stderr, flush=True)
        return best, why


def line_cfg(spec: dict, idx: int) -> tuple[str, str, float, str]:
    alt = spec.get("alt") or {}
    src = alt if idx in (alt.get("lines") or []) else spec
    # "tempos": nhịp riêng cho từng câu (câu đỉnh chậm hơn) -- giọng có lên xuống, không đều một nhịp.
    k = (spec.get("tempos") or {}).get(str(idx), src.get("tempo", spec.get("tempo", 1.0)))
    return (src.get("voice", spec["voice"]), src.get("style", spec.get("style", "doc_truyen")),
            float(k), src.get("engine", "v3"))


def fade(a: np.ndarray, sr: int, secs: float = FADE_S) -> np.ndarray:
    """Fade đầu/cuối vài mili giây để chỗ nối câu không click. Không đổi độ dài."""
    n = min(int(secs * sr), len(a) // 2)
    if n < 2:
        return a
    a = a.copy()
    ramp = np.linspace(0.0, 1.0, n, dtype="float32")
    a[:n] *= ramp
    a[-n:] *= ramp[::-1]
    return a


def level(a: np.ndarray, target_db: float = LEVEL_TARGET_DB, max_db: float = LEVEL_MAX_DB) -> np.ndarray:
    """Đưa RMS phần có tiếng về target_db (dBFS), tối đa ±max_db; không để vượt đỉnh 0,98."""
    voiced = a[np.abs(a) > 0.01 * (np.abs(a).max() + 1e-12)]
    if not len(voiced):
        return a
    rms_db = 20 * np.log10(np.sqrt(np.mean(voiced.astype("float64") ** 2)) + 1e-12)
    gain_db = float(np.clip(target_db - rms_db, -max_db, max_db))
    g = 10 ** (gain_db / 20)
    peak = float(np.abs(a).max()) * g
    if peak > 0.98:
        g *= 0.98 / peak
    return (a * g).astype("float32")


def cache_key(engine: str, voice: str, style: str, k: float, spoken: str,
              temperature: float | None = None, donor: str | None = None,
              text_mode: str | None = None, seed: int | None = None) -> str:
    raw = f"{VERSION}|{engine}|{voice}|{style}|{k}|{spoken}"
    if temperature is not None or donor not in (None, "") or text_mode not in (None, ""):
        t = "" if temperature is None else f"{float(temperature):.2f}"
        raw += f"|{t}|{donor or ''}|{text_mode or ''}"
        if seed is not None:
            raw += f"|s{int(seed)}"
    if MODEL_TAG:
        raw += f"|{MODEL_TAG}"
    return hashlib.sha1(raw.encode()).hexdigest()[:20]


def synth(lines: list[str], spec: dict, out_wav: Path) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    eng = None
    parts, segs, t = [], [], 0.0
    qa_failed: list[dict] = []
    use_level = bool(spec.get("level", False))
    pause_ctx = bool(spec.get("pause_ctx", False))
    alt_lines = set((spec.get("alt") or {}).get("lines") or [])
    base = float(spec.get("pause", 0.35))
    pauses = {int(k): float(v) for k, v in (spec.get("pauses") or {}).items()}
    re_tts_suspect = bool(spec.get("qa_strict")) or os.environ.get("VIENEU_RETTS_SUSPECT") == "1"
    new_key = uses_new_cache(spec)
    text_mode = spec.get("text_mode") or None
    spec_seed = spec.get("seed")
    for i, line in enumerate(lines, 1):
        text = clean(line)
        spoken = spoken_text(text, spec)
        voice, style, k, engine = line_cfg(spec, i)
        donor = line_donor(spec, i, engine)
        first_temp = line_temperature(spec, i)
        line_seed = None if spec_seed is None else int(spec_seed) + i * 10
        if new_key:
            key = cache_key(engine, voice, style, k, spoken, temperature=first_temp,
                            donor=donor, text_mode=text_mode or "production", seed=line_seed)
        else:
            key = cache_key(engine, voice, style, k, spoken)
        cp = CACHE / f"{key}.wav"
        sp = CACHE / f"{key}.suspect"
        is_hit = cp.exists() and not (sp.exists() and re_tts_suspect)
        if is_hit:
            os.utime(cp)   # đánh dấu "vừa dùng" -- hf_cleanup chỉ dọn câu lâu không dùng
            a, _ = sf.read(cp, dtype="float32")
            if sp.exists():
                why = sp.read_text(encoding="utf-8").strip() or "nghi lỗi từ cache"
                qa_failed.append({"line": i, "reason": why, "text": text[:80], "from_cache": True})
        else:
            if eng is None:
                eng = Voices()
            a, why = eng.say(spoken, voice, style, engine, temperature=first_temp,
                             donor=donor, seed=line_seed)
            a = tempo(trim(a, SR), SR, k)
            # Ghi dấu .suspect TRƯỚC wav: bị ngắt giữa hai lệnh thì câu nghi lỗi không lọt vào cache như câu sạch
            # (ngược lại, câu sạch còn dấu cũ chỉ bị coi là nghi lỗi -- an toàn).
            if why is not None:
                sp.write_text(why, encoding="utf-8")
                qa_failed.append({"line": i, "reason": why, "text": text[:80], "from_cache": False})
            sf.write(cp, a, SR)        # câu nghi lỗi sau mọi lần thử VẪN ghi cache
            if why is None:
                sp.unlink(missing_ok=True)
            print(f"  [{i}/{len(lines)}] {voice} {len(a) / SR:.1f}s  {text[:50]}", flush=True)
        if a.ndim > 1:
            a = a.mean(axis=1)
        if use_level:
            a = level(a)
        a = fade(a, SR)
        seg = {"start": round(t, 3), "end": round(t + len(a) / SR, 3), "text": text, "voice": voice}
        if spoken != text:
            seg["spoken"] = spoken
        segs.append(seg)
        gap = pauses.get(i, default_pause(line, base, i in alt_lines, pause_ctx=pause_ctx)) if i < len(lines) else 0.6
        parts += [a, np.zeros(int(gap * SR), dtype="float32")]
        t += len(a) / SR + gap
    audio = np.concatenate(parts)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_wav, audio, SR)
    retried = eng.retries if eng else 0
    manifest = {"output_file": out_wav.name, "voice": spec["voice"], "duration_s": round(len(audio) / SR, 2),
                "n_chunks": len(lines), "n_retried": retried, "n_failed_qa": len(qa_failed),
                "qa_failed_lines": qa_failed, "segments": segs,
                "content_type": "Long", "tts": spec}
    if spec.get("asr_check", os.environ.get("VIENEU_ASR_CHECK") == "1"):
        # Nghe lại câu rủi ro bằng ASR (hf_asr_check) -- TẮT mặc định. Lỗi ASR (thiếu model, không tải được) không làm
        # hỏng TTS: ghi vào manifest và đi tiếp.
        try:
            import hf_asr_check  # noqa: PLC0415
            rep = hf_asr_check.check(out_wav, manifest, model_name=spec.get("asr_model", hf_asr_check.DEFAULT_MODEL),
                                     check_all=bool(spec.get("asr_all", False)), alt_lines=alt_lines)
            manifest["asr"] = {k: rep[k] for k in ("model", "n_checked", "n_cached", "asr_seconds", "audio_seconds", "xrt")}
            manifest["asr_failed_lines"] = [{"line": r["line"], "wer": r["wer"], "ref": r["ref"], "hyp": r["hyp"]}
                                            for r in rep["flagged"]]
            manifest["n_failed_qa"] += len(rep["flagged"])
        except Exception as exc:  # noqa: BLE001
            manifest["asr_error"] = f"{type(exc).__name__}: {exc}"[:300]
            print(f"CẢNH BÁO: ASR không chạy được ({manifest['asr_error']}) -- bỏ qua bước soát ASR.", file=sys.stderr)
    out_wav.with_suffix(".json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    # python hf_voice.py script.txt spec.json out.wav
    lines = [l.strip() for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
    spec = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    m = synth(lines, spec, Path(sys.argv[3]))
    for bad in m["qa_failed_lines"]:
        print(f"CẢNH BÁO QA: dòng {bad['line']} nghi lỗi sau mọi lần thử ({bad['reason']}): {bad['text']}", file=sys.stderr)
    for bad in m.get("asr_failed_lines", []):
        print(f"CẢNH BÁO QA: dòng {bad['line']} ASR lệch {bad['wer']:.0%} -- đáng lẽ: {bad['ref']} | nghe được: {bad['hyp']}",
              file=sys.stderr)
    print(json.dumps({"ok": True, "duration_s": m["duration_s"], "n_retried": m["n_retried"],
                      "n_failed_qa": m["n_failed_qa"]}))
    # qa_strict: dừng để người xem lại thay vì ghép tiếng hỏng vào video; mặc định chỉ cảnh báo (không chặn render).
    sys.exit(2 if (spec.get("qa_strict") and m["n_failed_qa"]) else 0)
