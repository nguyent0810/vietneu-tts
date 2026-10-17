"""Soát giọng đọc bằng ASR: nghe lại từng câu TTS và so với chữ ĐÃ ĐỊNH ĐỌC.

`hf_voice.suspect()` chỉ đo độ dài nên không bắt được câu bị nuốt chữ, đọc sai tên riêng hay sai số. Module này chạy
nhận dạng giọng (faster-whisper) trên từng câu trong wav đã ghép, so với chữ đáng lẽ được đọc, và gắn cờ câu lệch nhiều.

TẮT mặc định. Bật bằng `"asr_check": true` trong spec TTS (hf_voice), hoặc `VIENEU_ASR_CHECK=1`, hoặc chạy độc lập:

    python hf_asr_check.py output/.../L_bud_05.wav            # câu rủi ro (số, tên riêng, trích kinh)
    python hf_asr_check.py output/.../L_bud_05.wav --all      # mọi câu
    python hf_asr_check.py a.wav --model small --device cpu   # đo thời gian: in "xRT" (lần thời gian thực)

Thiết kế để KHÔNG làm chậm render:
  - mặc định chỉ kiểm câu rủi ro (có chữ số, tên viết hoa giữa câu, giọng thứ hai/trích kinh, từ lexicon vừa đổi);
  - kết quả nhận dạng cache theo (nội dung audio + model) trong chunks_cache/asr_check: render lại chỉ nghe câu mới;
  - model chỉ nạp khi có câu cần nghe.

So sánh theo ÂM TIẾT (tiếng Việt đơn âm tiết = từ): chữ số được đọc ra chữ ở cả hai phía (1983 và "một nghìn chín trăm
tám mươi ba" coi như nhau), bỏ dấu câu, và tính WER hai mức -- có dấu thanh và không dấu thanh. ASR hay sai thanh điệu
hơn là sai âm, nên CỜ chỉ dựa trên WER không dấu; WER có dấu chỉ để báo cáo.

Chưa đo được trên model thật trong môi trường dựng module này (không tải được trọng số): ngưỡng là điểm khởi đầu,
chỉnh sau khi chạy thật bằng `--report-only` rồi xem `<wav>.asr.json`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
CACHE = ROOT / "chunks_cache" / "asr_check"
ASR_SR = 16000
MIN_WORDS = 3            # câu ngắn hơn: WER nhảy theo từng chữ, không đáng tin
THRESHOLD = 0.30         # WER không dấu thanh vượt mức này -> cờ
THRESHOLD_RISKY = 0.20   # câu rủi ro (số, tên riêng, trích kinh) chặt hơn: sai một chữ cũng đáng nghe lại
DEFAULT_MODEL = "small"


def strip_tones(s: str) -> str:
    """Bỏ dấu thanh (sắc huyền hỏi ngã nặng), GIỮ dấu mũ/móc/trăng và đ -- chúng đổi âm, không chỉ đổi thanh."""
    out = []
    for ch in unicodedata.normalize("NFD", s):
        if unicodedata.category(ch) == "Mn" and ch in "̣̀́̃̉":
            continue
        out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


def _numbers_to_words(s: str) -> str:
    from long_script_lint import read_int  # noqa: PLC0415 -- nhập muộn: lint kéo theo hf_batch_render

    def conv(m: re.Match) -> str:
        raw = m.group(0).replace(".", "").replace(",", "")
        return " " + read_int(int(raw)) + " " if raw.isdigit() and len(raw) <= 12 else " " + raw + " "

    return re.sub(r"\d[\d.,]*\d|\d", conv, s)


def tokens(text: str, tones: bool = True) -> list[str]:
    s = unicodedata.normalize("NFC", text.lower())
    s = _numbers_to_words(s)
    s = s.replace("%", " phần trăm ").replace("&", " và ")
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE).replace("_", " ")
    toks = s.split()
    return toks if tones else [strip_tones(t) for t in toks]


def edit_distance(a: list[str], b: list[str]) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def wer(ref: str, hyp: str, tones: bool = True) -> float:
    r, h = tokens(ref, tones), tokens(hyp, tones)
    if not r:
        return 0.0 if not h else 1.0
    return edit_distance(r, h) / len(r)


def _has_proper_name(text: str) -> bool:
    """Có từ viết hoa chữ cái đầu NGOÀI vị trí đầu câu (tên người / địa danh / kinh)."""
    start = True
    for w in re.findall(r"[^\s]+", text.replace("**", "")):
        word = w.strip("\"'“”‘’()[],;:")
        if word and not start and word[0].isupper() and any(c.islower() for c in word[1:]):
            return True
        start = w[-1:] in ".!?…"
    return False




def is_risky(text: str, spoken: str | None = None, alt: bool = False) -> bool:
    """Câu đáng nghe lại: có chữ số, tên viết hoa giữa câu, lời trích kinh (giọng thứ hai), hoặc lexicon vừa đổi chữ."""
    return bool(alt or re.search(r"\d", text) or _has_proper_name(text) or (spoken and spoken != text))


class Whisper:
    """Bọc faster-whisper; nạp model muộn. `transcribe(audio_16k) -> str`."""

    def __init__(self, model: str | None = None, device: str | None = None, compute_type: str | None = None):
        self.name = model or os.environ.get("VIENEU_ASR_MODEL", DEFAULT_MODEL)
        self.device = device or os.environ.get("VIENEU_ASR_DEVICE", "auto")
        self.compute_type = compute_type or os.environ.get("VIENEU_ASR_COMPUTE", "int8")
        self._m = None

    def transcribe(self, audio: np.ndarray) -> str:
        if self._m is None:
            from faster_whisper import WhisperModel  # noqa: PLC0415
            self._m = WhisperModel(self.name, device=self.device, compute_type=self.compute_type)
        segs, _ = self._m.transcribe(audio, language="vi", beam_size=1, condition_on_previous_text=False,
                                     vad_filter=False)
        return " ".join(s.text.strip() for s in segs).strip()


def _to_16k(a: np.ndarray, sr: int) -> np.ndarray:
    from scipy.signal import resample_poly  # noqa: PLC0415
    from math import gcd
    g = gcd(ASR_SR, sr)
    return resample_poly(a, ASR_SR // g, sr // g).astype("float32")


def _cache_name(audio: np.ndarray, model: str) -> str:
    h = hashlib.sha1(audio.tobytes()).hexdigest()[:20]
    return hashlib.sha1((h + "|" + model).encode()).hexdigest()[:20] + ".json"


def check(wav_path: Path, manifest: dict, transcribe=None, model_name: str = DEFAULT_MODEL, check_all: bool = False,
          alt_lines: set[int] | None = None, cache_dir: Path | None = None) -> dict:
    """Nghe lại các câu trong `manifest["segments"]` của `wav_path`. `transcribe` tiêm được để test không cần model.

    Trả {"model", "n_checked", "n_cached", "asr_seconds", "audio_seconds", "xrt", "flagged": [...], "lines": [...]}."""
    import soundfile as sf  # noqa: PLC0415
    cache = cache_dir or CACHE
    audio, sr = sf.read(wav_path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    engine = transcribe if transcribe is not None else Whisper(model_name).transcribe
    alt_lines = alt_lines or set()
    lines, flagged = [], []
    n_checked = n_cached = 0
    t_asr = 0.0
    audio_s = 0.0
    for i, seg in enumerate(manifest.get("segments", []), 1):
        ref = seg.get("spoken") or seg["text"]
        risky = is_risky(seg["text"], seg.get("spoken"), i in alt_lines)
        if not (check_all or risky) or len(tokens(ref)) < MIN_WORDS:
            continue
        a = audio[int(seg["start"] * sr): int(seg["end"] * sr)]
        if not len(a):
            continue
        cp = cache / _cache_name(a, model_name)
        hyp = None
        if cp.exists():
            try:
                hyp = json.loads(cp.read_text(encoding="utf-8"))["hyp"]
                n_cached += 1
            except (OSError, ValueError, KeyError):
                hyp = None
        if hyp is None:
            t0 = time.time()
            hyp = engine(_to_16k(a, sr))
            t_asr += time.time() - t0
            audio_s += len(a) / sr
            cp.parent.mkdir(parents=True, exist_ok=True)
            cp.write_text(json.dumps({"hyp": hyp}, ensure_ascii=False), encoding="utf-8")
            n_checked += 1
        w_plain, w_tone = wer(ref, hyp, tones=False), wer(ref, hyp, tones=True)
        limit = THRESHOLD_RISKY if risky else THRESHOLD
        row = {"line": i, "wer": round(w_plain, 3), "wer_tone": round(w_tone, 3), "risky": risky,
               "ref": ref[:120], "hyp": hyp[:120], "flag": w_plain > limit}
        lines.append(row)
        if row["flag"]:
            flagged.append(row)
    return {"model": model_name, "n_checked": n_checked, "n_cached": n_cached, "asr_seconds": round(t_asr, 2),
            "audio_seconds": round(audio_s, 1), "xrt": round(audio_s / t_asr, 1) if t_asr else None,
            "flagged": flagged, "lines": lines}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("wav", type=Path)
    ap.add_argument("--manifest", type=Path, help="mặc định: <wav>.json cạnh wav")
    ap.add_argument("--all", action="store_true", help="kiểm mọi câu, không chỉ câu rủi ro")
    ap.add_argument("--model", default=os.environ.get("VIENEU_ASR_MODEL", DEFAULT_MODEL))
    ap.add_argument("--device", default=None)
    ap.add_argument("--strict", action="store_true", help="thoát mã 2 nếu có câu bị cờ")
    ap.add_argument("--report-only", action="store_true", help="không in cảnh báo, chỉ ghi <wav>.asr.json")
    args = ap.parse_args(argv)

    man_path = args.manifest or args.wav.with_suffix(".json")
    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    alt = set(((manifest.get("tts") or {}).get("alt") or {}).get("lines") or [])
    if args.device:
        os.environ["VIENEU_ASR_DEVICE"] = args.device
    rep = check(args.wav, manifest, model_name=args.model, check_all=args.all, alt_lines=alt)
    args.wav.with_suffix(".asr.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ASR {rep['model']}: nghe {rep['n_checked']} câu mới ({rep['n_cached']} từ cache), "
          f"{rep['asr_seconds']}s cho {rep['audio_seconds']}s âm thanh"
          + (f" ({rep['xrt']}x thời gian thực)" if rep["xrt"] else "") + f", {len(rep['flagged'])} câu bị cờ")
    if not args.report_only:
        for r in rep["flagged"]:
            print(f"CẢNH BÁO QA: dòng {r['line']} ASR lệch {r['wer']:.0%} -- đáng lẽ: {r['ref']} | nghe được: {r['hyp']}",
                  file=sys.stderr)
    return 2 if (args.strict and rep["flagged"]) else 0


if __name__ == "__main__":
    sys.exit(main())
