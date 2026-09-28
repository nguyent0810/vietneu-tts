"""S8 -- Toàn vẹn văn bản (hard gate deterministic của tầng Script; ticket 11,
D62/D68/D88/D91).

Kiểm trên TEXT SẼ THẬT SỰ ĐƯỢC ĐỌC: đã bỏ emotion tag và `**` bằng đúng hàm
strip của bước render (`short_spoken_text`, dùng chung, không bản sao).

Loại finding:
- CHẶN: câu lặp (nguyên văn, hoặc sau khi chuẩn hoá: hạ chữ, bỏ dấu câu) --
  `SCR_REPEATED_SENTENCE`; markup/ký hiệu còn sót vào lời đọc (dấu sao, ngoặc
  vuông/nhọn/nhọn-ống, `#`, nhãn "Phương án X", mảnh JSON, URL, backtick) --
  `SCR_LEFTOVER_MARKUP`.
- KHÔNG CHẶN: câu cuối thiếu dấu kết câu -- `SCR_TRUNCATED` (script có thể cố
  ý kết bằng "…" hay câu hỏi, D91).

Hàm thuần, không phụ thuộc khoá Unix. Không chấm điểm, không ngưỡng chất
lượng: chỉ bắt lỗi chắc chắn.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from short_spoken_text import spoken_text

SCR_REPEATED_SENTENCE = "SCR_REPEATED_SENTENCE"
SCR_LEFTOVER_MARKUP = "SCR_LEFTOVER_MARKUP"
SCR_TRUNCATED = "SCR_TRUNCATED"

# Câu lặp chỉ tính khi đủ dài để không nhầm với câu đệm rất ngắn lặp tự nhiên
# ("Vâng.", "Đúng vậy."): câu < 3 từ lặp lại được ghi là finding KHÔNG chặn.
# Đây là định nghĩa phép đo, không phải ngưỡng chất lượng.
MIN_WORDS_BLOCKING_REPEAT = 3

_SENTENCE_RE = re.compile(r"[^.!?…\n]+(?:[.!?…]+[\"'”’»)]*)?")
_TERMINAL_RE = re.compile(r"[.!?…][\"'”’»)]*\s*$")

_MARKUP_PATTERNS = [
    ("asterisk", re.compile(r"\*+")),
    ("square_bracket", re.compile(r"[\[\]]")),
    ("angle_pipe_token", re.compile(r"<\||\|>")),
    ("hash", re.compile(r"#")),
    ("curly_brace", re.compile(r"[{}]")),
    ("backtick", re.compile(r"`")),
    ("json_key", re.compile(r"\"\w+\"\s*:")),
    ("candidate_label", re.compile(r"\bPhương án\s+[A-D]\b", re.IGNORECASE)),
    ("url", re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)),
]


@dataclass(frozen=True)
class IntegrityFinding:
    kind: str
    reason_code: str
    span: str
    position: int  # chỉ số câu (0-based) trong text đã strip
    blocking: bool


@dataclass
class IntegrityResult:
    spoken_text: str
    sentences: list[str]
    findings: list[IntegrityFinding] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return any(f.blocking for f in self.findings)

    @property
    def reason_codes(self) -> list[str]:
        return list(dict.fromkeys(f.reason_code for f in self.findings if f.blocking))


def split_sentences(text: str) -> list[str]:
    return [m.group(0).strip() for m in _SENTENCE_RE.finditer(text) if m.group(0).strip()]


def _normalized(sentence: str) -> str:
    s = unicodedata.normalize("NFC", sentence).lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def check(script: str) -> IntegrityResult:
    text = spoken_text(script or "")
    sentences = split_sentences(text)
    findings: list[IntegrityFinding] = []

    first_seen: dict[str, int] = {}
    for i, sentence in enumerate(sentences):
        norm = _normalized(sentence)
        if not norm:
            continue
        if norm in first_seen:
            blocking = len(norm.split()) >= MIN_WORDS_BLOCKING_REPEAT
            kind = "repeated_exact" if sentence == sentences[first_seen[norm]] else "repeated_normalized"
            findings.append(IntegrityFinding(kind, SCR_REPEATED_SENTENCE, sentence, i, blocking))
        else:
            first_seen[norm] = i

    for i, sentence in enumerate(sentences):
        for kind, pattern in _MARKUP_PATTERNS:
            for m in pattern.finditer(sentence):
                findings.append(IntegrityFinding(f"markup_{kind}", SCR_LEFTOVER_MARKUP, m.group(0), i, True))

    if sentences and not _TERMINAL_RE.search(sentences[-1]):
        findings.append(IntegrityFinding("no_terminal_punctuation", SCR_TRUNCATED, sentences[-1],
                                         len(sentences) - 1, False))

    return IntegrityResult(spoken_text=text, sentences=sentences, findings=findings)
