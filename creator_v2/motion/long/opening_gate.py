"""Kiểm tra nhịp mở đầu Long; CLI cũng hỗ trợ ước lượng khi chưa TTS."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
import warnings
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


# Bộ chuẩn hoá đọc "1,2 tỷ" thành "một phẩy hai tỷ". Lời nói thường lại là "một tỷ hai",
# và "1,5 triệu" là "một triệu rưỡi" hoặc "một triệu năm".
_NUM_CONT = {
    "khong", "mot", "hai", "ba", "bon", "nam", "sau", "bay", "tam", "chin",
    "muoi", "tram", "nghin", "ngan", "trieu", "ty", "ti", "lam", "tu", "le", "linh",
    "ruoi", "phay",
}
O2B_LIMIT = 3.0
META_PHRASES = ("trong video này", "video hôm nay", "chương một", "hãy cùng", "đăng ký kênh")


def _phrase_in(hay, needle):
    """needle là cụm đã normalize. Không khớp khi nó chỉ là đầu của một số dài hơn ("hai" + "mươi")."""
    hay = f" {' '.join(hay.split())} "
    needle = " ".join(needle.split())
    if not needle:
        return False
    token = f" {needle} "
    start = 0
    while True:
        i = hay.find(token, start)
        if i < 0:
            return False
        rest = hay[i + len(token):].strip()
        nxt = rest.split(" ", 1)[0] if rest else ""
        if nxt not in _NUM_CONT:
            return True
        start = i + 1


def colloquial_decimals(phrase):
    """'1,2 tỷ' -> 'một tỷ hai'; '1,5 triệu' -> 'một triệu năm' và 'một triệu rưỡi'."""
    out = []
    for match in re.finditer(r"(\d+),(\d)\s+([^\W\d_]+)", phrase, re.UNICODE):
        whole, frac, unit = match.group(1), match.group(2), match.group(3)
        head, tail, unit_n = speech_words(str(int(whole))), speech_words(frac), normalize(unit)
        if not (head and tail and unit_n):
            continue
        out.append(f"{head} {unit_n} {tail}")
        if frac == "5":
            out.append(f"{head} {unit_n} {normalize('rưỡi')}")
    return out


def bare_runs(scenes, window=BARE_WINDOW):
    """Các đoạn chữ trên nền trống liên tục trong `window` giây đầu (cảnh TEXT_TYPES không img/vid/bg)."""
    spans = []
    for scene in scenes:
        if scene.get("type") not in TEXT_TYPES or scene.get("img") or scene.get("vid") or scene.get("bg"):
            continue
        start = max(float(scene.get("t0", 0.0)), 0.0)
        end = min(float(scene.get("t1", 0.0)), window)
        if end > start:
            spans.append((start, end))
    spans.sort()
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1] + 1e-6:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def early_speech(lines, limit=BARE_WINDOW):
    tokens = []
    for line in lines:
        words = line.get("words") or []
        if words:
            tokens.extend(word.get("w", "") for word in words if float(word.get("t", 0.0)) < limit)
        elif float(line.get("start", 0.0)) < limit:
            tokens.extend(str(line.get("text", "")).split())
    return speech_words(" ".join(tokens))


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


def retention_findings(title, lines):
    """Heuristic chỉ gợi ý O1; người duyệt xác nhận ý nghĩa và ngoại lệ."""
    first, early = early_speech(lines, 5), early_speech(lines, 15)
    people = r"\b(ban|nguoi|ong|ba|co|anh|chi|ho|gia dinh|khach hang|nha dau tu)\b"
    money = r"\b(tien|dong|trieu|ty|mat|lo|rui ro|no|phi|thue)\b"
    situation = r"\b(khi|neu|vi|bi|phai|co|mat|lo|tra|tang|giam|vao|trong|truoc|sau)\b"
    names = [normalize(p) for p in title_phrases(title)[0] if len(normalize(p).split()) >= 2 and not re.search(r"\d", p)]
    out = []
    if not (re.search(people, first) or any(_phrase_in(first, n) for n in names) or (re.search(money, first) and re.search(situation, first))):
        out.append("O1: chưa nhận diện người chịu tác động hoặc tiền/rủi ro kèm tình huống trong 5s")
    progress = r"\b(da|bi|mat|lo|tang|giam|nhung|ket qua|bang chung|cho thay|theo|vi|khien|dan den|duoc|tra|phai|xay ra)\b|\d"
    terms = {w for w in normalize(title).split() if len(w) >= 4 and w not in {'ngoai', 'that', 'nhung'}}
    if not re.search(progress, early) or not (terms & set(early.split())):
        out.append("O1: chưa nhận diện bằng chứng hoặc diễn biến gắn lời hứa tiêu đề trước 15s")
    return out


ROADMAP_30 = (
    r"\b(?:xin chao|chao (?:cac ban|ban|mung))\b",
    r"\b(?:chao mung (?:ban|cac ban)|gioi thieu (?:kenh|video)|kenh (?:cua chung toi|hom nay)|(?:minh|toi|chung toi) la kenh)\b",
    r"\b(?:trong (?:video|bai) nay|video hom nay|hom nay (?:chung ta|ta|toi) se|"
    r"chung ta se (?:tim hieu|kham pha|cung|di qua)|dau tien .{0,60} sau do|"
    r"(?:gom|qua) (?:ba|bon|nam|3|4|5) (?:phan|chuong|buoc|cau hoi))\b",
)


def is_legacy(topic, root):
    path = Path(root) / "data" / "long" / "_legacy_topics.json"
    return topic in json.loads(path.read_text(encoding="utf-8")) if path.exists() else False


def check(title, scenes, lines, legacy=True):
    errors = []
    phrases, limit = title_phrases(title)
    raw = " ".join(word["w"] for line in lines for word in line.get("words", []) if word["t"] < limit)
    spoken_digits = " " + normalize(raw) + " "          # lời còn để chữ số
    spoken = " " + speech_words(raw) + " "              # lời đã đọc thành chữ như TTS
    for phrase in phrases:
        target, target_words = normalize(phrase), speech_words(phrase)
        if not target:
            continue
        if (f" {target} " in spoken_digits or f" {target} " in spoken or f" {target_words} " in spoken
                or any(_phrase_in(spoken, alias) for alias in colloquial_decimals(phrase))):
            continue
        message = f"Từ khóa tiêu đề chưa nói trước {limit:g}s: {phrase}"
        if legacy:
            errors.append(message)
        else:
            warnings.warn(message, stacklevel=2)
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
    runs = bare_runs(scenes)
    if runs:
        longest = max(end - start for start, end in runs)
        if longest > O2B_LIMIT:
            errors.append(f"O2b chữ trên nền trống liên tục {longest:.1f}s trong 40s đầu (> {O2B_LIMIT:.1f}s)")
    heard = early_speech(lines, BARE_WINDOW if legacy else 30.0)
    for phrase in META_PHRASES:
        if _phrase_in(heard, normalize(phrase)):
            errors.append(f"O6 lời meta trong {40 if legacy else 30}s đầu: {phrase}")
    if not legacy:
        for pattern in ROADMAP_30:
            if re.search(pattern, heard):
                errors.append("O6 chào, giới thiệu kênh hoặc lộ trình trước 30s")
                break
        for note in retention_findings(title, lines):
            warnings.warn(note, stacklevel=2)
    if not any(0 <= t <= BIG_QUESTION_LIMIT for t in questions):
        if legacy:
            errors.append("Không có câu hỏi trong 45s đầu")
        else:
            warnings.warn("Không có câu hỏi trong 45s đầu; người duyệt kiểm mạch kể", stacklevel=2)
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
    return check(spec["youtube"]["titles"][0], scenes, lines, legacy=is_legacy(topic, root))


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
