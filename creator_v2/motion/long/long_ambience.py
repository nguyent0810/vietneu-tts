"""Ambience cho Long (port từ hf_ambience.py của repo gốc, PR #238).

spec.json của topic (khoá tuỳ chọn; KHÔNG có = final trộn đúng như cũ):

    "ambience": [
        {"kind": "night_insects", "gain_db": -2},                       # cả video (mọi chương)
        {"chapter": "ch03", "kind": "rain"},                            # cả chương ch03 (thắng mục cả video)
        {"chapter": "ch05", "from": 12, "to": 20, "kind": "wind"},      # câu 12..20 của ch05 (chỉ số 0-based
                                                                        # trong chNN.json = "index" trong timing.json)
        {"chapter": "ch07", "kind": "none"}                             # ch07 không nền
    ],
    "amb_gap": 26, "amb_duck_db": 4, "amb_music_gap": 18                # tuỳ chọn, mặc định của hf_ambience

Ưu tiên: câu > chương > cả video; cùng mức khai sau thắng. Tổng hợp, mức chuẩn (giọng - 26 LU), lùi theo giọng
và trần dưới nhạc >= 3 LU đều do hf_ambience.layer lo; ở đây chỉ dịch plan sang "dòng" của chương rồi ghi
`<chương>/amb.wav` (48 kHz stereo). `final` trộn nó vào mixpad.wav.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

SR = 48000
ROOT_REPO = Path(__file__).resolve().parents[3]       # gốc repo (chứa hf_ambience.py)


def _load_amb():
    """hf_ambience nằm ở gốc repo. Chỉ NỐI vào cuối sys.path để không che module cùng tên của creator_v2."""
    root = str(ROOT_REPO)
    if root not in sys.path:
        sys.path.append(root)
    import hf_ambience
    return hf_ambience


def chapter_name(v) -> str:
    return f"ch{v:02d}" if isinstance(v, int) else str(v)


def validate(spec: dict, chapters: list[str], kinds) -> list[str]:
    """Lỗi khai báo (rỗng = ổn). Sai là báo, không lặng lẽ bỏ qua."""
    bad = []
    for i, e in enumerate(spec.get("ambience") or []):
        if not isinstance(e, dict):
            bad.append(f"ambience[{i}]: phải là object")
            continue
        if e.get("kind") not in kinds:
            bad.append(f"ambience[{i}]: kind '{e.get('kind')}' không có (dùng {'|'.join(kinds)})")
        if "gain_db" in e and not isinstance(e["gain_db"], (int, float)):
            bad.append(f"ambience[{i}]: gain_db phải là số")
        if "chapter" in e and chapter_name(e["chapter"]) not in chapters:
            bad.append(f"ambience[{i}]: chương '{e['chapter']}' không có trong spec.chapters")
        if ("from" in e or "to" in e) and "chapter" not in e:
            bad.append(f"ambience[{i}]: from/to cần kèm chapter (chỉ số câu tính trong chương)")
    return bad


def chapter_entries(entries: list[dict], name: str, n_lines: int) -> list[dict]:
    """Dịch plan sang dạng hf_ambience cho MỘT chương. Dòng 0 của chương mang heading nên mục `chapter`
    hf phủ cả chương (ưu tiên 1); mục from/to đổi sang sentence_id = chỉ số + 1 (ưu tiên 2)."""
    out = []
    for e in entries or []:
        if "chapter" in e and chapter_name(e["chapter"]) != name:
            continue
        row = {"kind": e["kind"]}
        if "gain_db" in e:
            row["gain_db"] = e["gain_db"]
        if "from" in e or "to" in e:
            row["from"] = int(e.get("from", 0)) + 1
            row["to"] = int(e.get("to", n_lines - 1)) + 1
        elif "chapter" in e:
            row["chapter"] = 1
        out.append(row)
    return out


def chapter_lines(segments: list[dict]) -> list[dict]:
    return [{"start": float(s["start"]), "sentence_id": i + 1, **({"heading": True} if i == 0 else {})}
            for i, s in enumerate(segments)]


def build_bed(spec: dict, name: str, segments: list[dict], voice: np.ndarray | None, voice_lufs: float,
              duration: float, amb=None) -> tuple[np.ndarray | None, list[str]]:
    """(N, 2) float32 bed 48 kHz cho một chương, hoặc (None, []) khi chương không có nền."""
    entries = chapter_entries(spec.get("ambience") or [], name, len(segments))
    if not entries or not segments:
        return None, []
    amb = amb or _load_amb()
    sub = {"ambience": entries}
    for k in ("amb_gap", "amb_duck_db"):
        if k in spec:
            sub[k] = spec[k]
    bed, used = amb.layer(chapter_lines(segments), sub, voice, voice_lufs, duration,
                          music_gap=float(spec.get("amb_music_gap", 18.0)))
    return (bed, used) if used else (None, [])


def _voice48(path: Path) -> np.ndarray:
    import soundfile as sf
    from math import gcd
    from scipy.signal import resample_poly
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    if sr != SR:
        g = gcd(SR, sr)
        x = resample_poly(x, SR // g, sr // g).astype("float32")
    return x


def bed_for_chapter(spec: dict, name: str, od: Path, duration: float, ff_dir: str | None = None, amb=None) -> Path | None:
    """Ghi od/<name>/amb.wav và trả đường dẫn; None nếu spec không khai ambience cho chương (mix y như cũ)."""
    import json
    import soundfile as sf
    if not spec.get("ambience"):
        return None
    tj = od / name / "timing.json"
    segments = json.loads(tj.read_text(encoding="utf-8"))["segments"]
    if not chapter_entries(spec["ambience"], name, len(segments)):
        return None
    amb = amb or _load_amb()
    voice = _voice48(od / name / "voice.wav")
    old = os.environ.get("PATH", "")
    if ff_dir:                      # hf_foley.lufs gọi `ffmpeg` trần: cho nó thấy ffmpeg của pipeline
        os.environ["PATH"] = ff_dir + os.pathsep + old
    try:
        from hf_foley import lufs
        bed, _used = build_bed(spec, name, segments, voice, float(lufs(voice)), duration, amb)
    finally:
        os.environ["PATH"] = old
    if bed is None:
        return None
    out = od / name / "amb.wav"
    sf.write(str(out), bed, SR, subtype="FLOAT")
    return out
