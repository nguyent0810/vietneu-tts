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

ROOT = Path(__file__).parent
CACHE = ROOT / "chunks_cache" / "voice_lines"
SR = 48000
VERSION = "1"


def clean(line: str) -> str:
    return line.replace("**", "").strip()


def default_pause(line: str, base: float) -> float:
    t = clean(line)
    if line.startswith("**") and line.endswith("**"):
        return max(base, 0.9)                  # tiêu đề chương: để thẻ chương thở
    if t.endswith("?"):
        return max(base, 0.6)
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


class Voices:
    """Hai model: "v3" (v3turbo 48 kHz, 14 giọng) và "standard" (24 kHz -- giọng các
    kênh đang dùng: Binh cho Phật giáo, Sơn cho Phong Thuỷ). Nạp model nào cần thì nạp."""

    def __init__(self):
        self.m: dict = {}

    def _model(self, engine: str):
        if engine not in self.m:
            from vieneu import Vieneu  # noqa: PLC0415
            self.m[engine] = (Vieneu() if engine == "v3" else
                              Vieneu(mode="standard", backbone_device="mps", codec_device="mps"))
        return self.m[engine]

    def say(self, text: str, voice: str, style: str, engine: str = "v3") -> np.ndarray:
        from scipy.signal import resample_poly  # noqa: PLC0415
        v = self._model(engine)
        best = None
        for temp in ((0.8, 0.7, 0.9, 0.6) if engine == "v3" else (1.0, 0.9, 1.1, 0.8)):
            kw = {"style": style} if engine == "v3" else {"skip_normalize": False}
            a = np.asarray(v.infer(text, voice=v.get_preset_voice(voice), temperature=temp, **kw), dtype="float32")
            if v.sample_rate != SR:
                a = resample_poly(a, SR, v.sample_rate).astype("float32")
            best = a
            if suspect(text, a, SR) is None:
                return a
            print(f"    nghi lỗi ({suspect(text, a, SR)}), đọc lại temp={temp}", file=sys.stderr, flush=True)
        return best


def line_cfg(spec: dict, idx: int) -> tuple[str, str, float, str]:
    alt = spec.get("alt") or {}
    src = alt if idx in (alt.get("lines") or []) else spec
    # "tempos": nhịp riêng cho từng câu (câu đỉnh chậm hơn) -- giọng có lên xuống, không đều một nhịp.
    k = (spec.get("tempos") or {}).get(str(idx), src.get("tempo", spec.get("tempo", 1.0)))
    return (src.get("voice", spec["voice"]), src.get("style", spec.get("style", "doc_truyen")),
            float(k), src.get("engine", "v3"))


def synth(lines: list[str], spec: dict, out_wav: Path) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    eng = None
    parts, segs, t = [], [], 0.0
    base = float(spec.get("pause", 0.35))
    pauses = {int(k): float(v) for k, v in (spec.get("pauses") or {}).items()}
    for i, line in enumerate(lines, 1):
        text = clean(line)
        voice, style, k, engine = line_cfg(spec, i)
        key = hashlib.sha1(f"{VERSION}|{engine}|{voice}|{style}|{k}|{text}".encode()).hexdigest()[:20]
        cp = CACHE / f"{key}.wav"
        if cp.exists():
            os.utime(cp)   # đánh dấu "vừa dùng" -- hf_cleanup chỉ dọn câu lâu không dùng
            a, _ = sf.read(cp, dtype="float32")
        else:
            if eng is None:
                eng = Voices()
            a = eng.say(text, voice, style, engine)
            a = tempo(trim(a, SR), SR, k)
            sf.write(cp, a, SR)
            print(f"  [{i}/{len(lines)}] {voice} {len(a) / SR:.1f}s  {text[:50]}", flush=True)
        if a.ndim > 1:
            a = a.mean(axis=1)
        segs.append({"start": round(t, 3), "end": round(t + len(a) / SR, 3), "text": text, "voice": voice})
        gap = pauses.get(i, default_pause(line, base)) if i < len(lines) else 0.6
        parts += [a, np.zeros(int(gap * SR), dtype="float32")]
        t += len(a) / SR + gap
    audio = np.concatenate(parts)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_wav, audio, SR)
    manifest = {"output_file": out_wav.name, "voice": spec["voice"], "duration_s": round(len(audio) / SR, 2),
                "n_chunks": len(lines), "n_retried": 0, "n_failed_qa": 0, "segments": segs,
                "content_type": "Long", "tts": spec}
    out_wav.with_suffix(".json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    # python hf_voice.py script.txt spec.json out.wav
    lines = [l.strip() for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
    m = synth(lines, json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")), Path(sys.argv[3]))
    print(json.dumps({"ok": True, "duration_s": m["duration_s"]}))
