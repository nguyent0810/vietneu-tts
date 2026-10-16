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
"""
from __future__ import annotations

import hashlib
import os
import json
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


def clean(line: str) -> str:
    return line.replace("**", "").strip()


def default_pause(line: str, base: float, is_alt: bool = False) -> float:
    t = clean(line)
    if line.startswith("**") and line.endswith("**"):
        return max(base, 0.9)                  # tiêu đề chương: để thẻ chương thở
    if t.endswith("?"):
        return max(base, 0.6)
    if is_alt:
        return max(base, 0.7)                  # câu trích kinh / giọng thứ hai: để lời kinh lắng
    if t.endswith(":") or t.endswith("…"):
        return max(base, 0.5)                  # câu dẫn vào thoại / liệt kê: ngắt trước phần theo sau
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

    def say(self, text: str, voice: str, style: str, engine: str = "v3") -> tuple[np.ndarray, str | None]:
        """Trả (audio, lý_do_nghi_lỗi). lý_do = None nghĩa là đạt; khác None nghĩa là CẢ các lần thử đều nghi lỗi
        và audio trả về là lần cuối -- người gọi phải báo, KHÔNG được coi như đạt."""
        from scipy.signal import resample_poly  # noqa: PLC0415
        v = self._model(engine)
        best, why = None, None
        for n, temp in enumerate((0.8, 0.7, 0.9, 0.6) if engine == "v3" else (1.0, 0.9, 1.1, 0.8)):
            kw = {"style": style} if engine == "v3" else {"skip_normalize": False}
            a = np.asarray(v.infer(text, voice=v.get_preset_voice(voice), temperature=temp, **kw), dtype="float32")
            if v.sample_rate != SR:
                a = resample_poly(a, SR, v.sample_rate).astype("float32")
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


def cache_key(engine: str, voice: str, style: str, k: float, spoken: str) -> str:
    raw = f"{VERSION}|{engine}|{voice}|{style}|{k}|{spoken}"
    if MODEL_TAG:
        raw += f"|{MODEL_TAG}"
    return hashlib.sha1(raw.encode()).hexdigest()[:20]


def synth(lines: list[str], spec: dict, out_wav: Path) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    eng = None
    parts, segs, t = [], [], 0.0
    qa_failed: list[dict] = []
    use_lexicon = spec.get("lexicon", True)
    use_level = bool(spec.get("level", False))
    alt_lines = set((spec.get("alt") or {}).get("lines") or [])
    base = float(spec.get("pause", 0.35))
    pauses = {int(k): float(v) for k, v in (spec.get("pauses") or {}).items()}
    for i, line in enumerate(lines, 1):
        text = clean(line)
        spoken = tts_lexicon.apply(text) if use_lexicon else text
        voice, style, k, engine = line_cfg(spec, i)
        cp = CACHE / f"{cache_key(engine, voice, style, k, spoken)}.wav"
        if cp.exists():
            os.utime(cp)   # đánh dấu "vừa dùng" -- hf_cleanup chỉ dọn câu lâu không dùng
            a, _ = sf.read(cp, dtype="float32")
        else:
            if eng is None:
                eng = Voices()
            a, why = eng.say(spoken, voice, style, engine)
            a = tempo(trim(a, SR), SR, k)
            if why is None:
                sf.write(cp, a, SR)        # câu nghi lỗi KHÔNG vào cache -- lần chạy sau còn được đọc lại
            else:
                qa_failed.append({"line": i, "reason": why, "text": text[:80]})
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
        gap = pauses.get(i, default_pause(line, base, i in alt_lines)) if i < len(lines) else 0.6
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
    out_wav.with_suffix(".json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    # python hf_voice.py script.txt spec.json out.wav
    lines = [l.strip() for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
    spec = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    m = synth(lines, spec, Path(sys.argv[3]))
    for bad in m["qa_failed_lines"]:
        print(f"CẢNH BÁO QA: dòng {bad['line']} nghi lỗi sau mọi lần thử ({bad['reason']}): {bad['text']}", file=sys.stderr)
    print(json.dumps({"ok": True, "duration_s": m["duration_s"], "n_retried": m["n_retried"],
                      "n_failed_qa": m["n_failed_qa"]}))
    # qa_strict: dừng để người xem lại thay vì ghép tiếng hỏng vào video; mặc định chỉ cảnh báo (không chặn render).
    sys.exit(2 if (spec.get("qa_strict") and m["n_failed_qa"]) else 0)
