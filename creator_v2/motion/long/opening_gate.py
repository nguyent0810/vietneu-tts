"""Kiểm tra nhịp mở đầu Long; CLI cũng hỗ trợ ước lượng khi chưa TTS."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYLLABLES_PER_SECOND = 4.2
IP_LIMIT = 15.0
TITLE_LIMIT = 20.0
QUESTION_START = 36.0
QUESTION_END = 90.0
QUESTION_WINDOW = 20.0
VISUAL_LIMIT = 5.0
BARE_WINDOW = 40.0
BARE_FRACTION = 0.15
BIG_QUESTION_LIMIT = 45.0
TEXT_TYPES = {"kinetic", "slam", "question", "date", "quote", "file", "ledger", "timeline", "counter"}
VISUAL_TYPES = {"photo", "pano", "broll", "print", "split", "evidence", "map"}


def normalize(text):
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    return " ".join(re.findall(r"[^\W_]+", "".join(c for c in text if unicodedata.category(c) != "Mn")))


_NZ = []


def speech_words(text):
    """Số -> chữ bằng đúng bộ chuẩn hoá mà TTS dùng (vieneu `PuncNormalizer`): "100 Triệu" -> "một trăm triệu".
    Không nạp được vieneu thì trả nguyên văn (chỉ so được dạng chữ số hoặc chữ giống hệt)."""
    if not _NZ:
        try:
            from vieneu_utils.phonemize_text import PuncNormalizer
            _NZ.append(PuncNormalizer())
        except Exception:
            _NZ.append(None)
    nz = _NZ[0]
    if nz is not None and re.search(r"\d", text):
        try:
            text = nz.normalize(text)
        except Exception:
            pass
    return normalize(text)


def title_phrases(title):
    match = re.search(r"ngoài đời thật", title, re.I)
    if match:
        ip = title[:match.start()].strip(" :–—- ")
        rest = title[match.end():]
        phrases = [" ".join(ip.split()[:2])]
        if ":" in rest and "—" in rest.partition(":")[2]:   # khuôn [IP] Ngoài Đời Thật: [Tên] — [...]
            phrases.append(rest.partition(":")[2].split("—", 1)[0].strip())
        return phrases, IP_LIMIT
    # Chọn cụm số hoặc từ viết hoa trong tiêu đề.
    tokens = re.findall(r"[^\W_]+(?:[.,][0-9]+)*", title, re.UNICODE)
    groups, current = [], []
    for tok in tokens:
        if tok[0].isupper() or tok[0].isdigit():
            current.append(tok)
        elif current:
            groups.append(" ".join(current))
            current = []
    if current:
        groups.append(" ".join(current))
    numeric = re.findall(r"\d+(?:[.,]\d+)*(?:\s+[^\W\d_]+)?", title, re.UNICODE)
    return (numeric + [g for g in groups if not any(c.isdigit() for c in g)])[:2], TITLE_LIMIT


def estimated_lines(lines):
    result, now = [], 0.0
    for line in lines:
        text = line.get("t", "") if isinstance(line, dict) else line
        tokens = text.split()
        end = now + len(tokens) / SYLLABLES_PER_SECOND
        words = [{"w": tok, "t": now + i / SYLLABLES_PER_SECOND, "d": 1 / SYLLABLES_PER_SECOND} for i, tok in enumerate(tokens)]
        result.append({"text": text, "start": now, "end": end, "words": words})
        pause = line.get("p", 0.6 if text.rstrip().endswith("?") else 0.32) if isinstance(line, dict) else (0.6 if text.rstrip().endswith("?") else 0.32)
        now = end + pause
    return result, now + 0.9


def check(title, scenes, lines):
    errors = []
    phrases, limit = title_phrases(title)
    raw = " ".join(word["w"] for line in lines for word in line.get("words", []) if word["t"] < limit)
    spoken_digits = " " + normalize(raw) + " "          # lời còn để chữ số
    spoken = " " + speech_words(raw) + " "              # lời đã đọc thành chữ như TTS
    for phrase in phrases:
        target, target_words = normalize(phrase), speech_words(phrase)
        if not target:
            continue
        if f" {target} " in spoken_digits or f" {target} " in spoken or f" {target_words} " in spoken:
            continue
        errors.append(f"Từ khóa tiêu đề chưa nói trước {limit:g}s: {phrase}")
    questions = sorted(line["start"] for line in lines if "?" in line["text"])
    window_questions = [t for t in questions if QUESTION_START <= t <= QUESTION_END]
    if any(window_questions[i + 2] - t <= QUESTION_WINDOW for i, t in enumerate(window_questions[:-2])):
        errors.append("Có ít nhất 3 câu hỏi trong cửa sổ 20s thuộc đoạn 36–90s")
    visual = next((s["t0"] for s in sorted(scenes, key=lambda s: s["t0"]) if s.get("img") or s.get("vid") or s.get("type") in VISUAL_TYPES), None)
    if visual is None or visual > VISUAL_LIMIT:
        errors.append("Không có hình hoặc clip bắt đầu trong 5s đầu")
    bare = sum(max(0.0, min(s["t1"], BARE_WINDOW) - max(s["t0"], 0.0)) for s in scenes if s.get("type") in TEXT_TYPES and not (s.get("img") or s.get("vid") or s.get("bg")))
    if bare > BARE_WINDOW * BARE_FRACTION:
        errors.append(f"Cảnh chữ trống {bare:.1f}s trong 40s đầu, vượt 15%")
    if not any(0 <= t <= BIG_QUESTION_LIMIT for t in questions):
        errors.append("Không có câu hỏi trong 45s đầu")
    return errors


def problems(topic, root=None):
    sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
    build = sys.modules.get("build_long") or sys.modules.get("__main__")
    if not hasattr(build, "word_lines"):
        import build_long as build
    root = Path(root) if root else ROOT
    data = root / "data" / "long" / topic
    spec = json.loads((data / "spec.json").read_text(encoding="utf-8"))
    name = spec["chapters"][0]
    chapter = json.loads((data / f"{name}.json").read_text(encoding="utf-8"))
    out = root / "output" / "long" / topic / name
    timing = out / "timing.json"
    if timing.exists():
        t = json.loads(timing.read_text(encoding="utf-8"))
        lines = build.word_lines(t, out / "voice.wav")
        duration = float(t["duration"])
    else:
        lines, duration = estimated_lines(chapter["lines"])
    scenes = build.plan(chapter, lines, duration)
    return check(spec["youtube"]["titles"][0], scenes, lines)


def main():
    from factory.console import utf8_console
    utf8_console()
    args = sys.argv[1:]
    root = None
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    if len(args) != 1 or (root is None and "--root" in sys.argv):
        print("Cách dùng: python motion/long/opening_gate.py <topic> [--root <creator_v2>]", file=sys.stderr)
        return 2
    try:
        if root:
            sys.path[:0] = [root, str(Path(root) / "motion"), str(Path(root) / "motion" / "long")]
        errors = problems(args[0], root)
    except Exception as exc:
        print(f"Không kiểm được: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(error)
    if not errors:
        print("OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())
