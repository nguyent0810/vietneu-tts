"""S10 (phần code) -- Tín hiệu chẩn đoán của tầng Script + fingerprint mở đầu
(ticket 12, D63/D68/D86).

CHỈ LÀ DỮ LIỆU ĐO: không có trường điểm, không ngưỡng, không cờ đạt/không
đạt. Mọi phép đo chạy trên text sẽ được đọc (`short_spoken_text.spoken_text`).

Cách nhận diện được ghi rõ và có version (`DIAGNOSTICS_VERSION`):
- số: token chứa chữ số (vd "25", "25/07/2026", "1,5");
- thuật ngữ: khớp từ điển `DOMAIN_TERMS` (Can, Chi, Ngũ hành, vài thuật ngữ
  phong thuỷ/lịch), không phân biệt hoa thường;
- tên: cụm từ viết hoa chữ cái đầu KHÔNG đứng đầu câu và KHÔNG thuộc từ điển
  thuật ngữ (heuristic cho tên riêng tiếng Việt).
"""
from __future__ import annotations

import re
import unicodedata

from script_integrity import split_sentences
from short_spoken_text import spoken_text

DIAGNOSTICS_VERSION = "diag-v1 (số=token có chữ số; thuật ngữ=DOMAIN_TERMS; tên=cụm viết hoa không đầu câu, ngoài thuật ngữ)"
DEFAULT_FINGERPRINT_WORDS = 5
WPM_RATES = (170, 200)

DOMAIN_TERMS = frozenset(t.lower() for t in [
    # Thiên Can
    "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý",
    # Địa Chi
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
    # Ngũ hành
    "Kim", "Mộc", "Thủy", "Thuỷ", "Hỏa", "Hoả", "Thổ",
    # Thuật ngữ lịch/phong thuỷ thường gặp
    "Can Chi", "Hoàng Đạo", "Hắc Đạo", "Tam Hợp", "Tứ Hành Xung", "Ngũ Hành", "Kinh Dịch", "Bát Quái",
])

_NUMBER_RE = re.compile(r"\S*\d\S*")
_WORD_RE = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _words(text: str) -> list[str]:
    return text.split()


def _terms_in(sentence: str) -> list[str]:
    low = _nfc(sentence).lower()
    found = []
    for term in sorted(DOMAIN_TERMS, key=len, reverse=True):
        for m in re.finditer(rf"(?<!\w){re.escape(term)}(?!\w)", low):
            if not any(m.start() < e and s < m.end() for s, e, _ in found):
                found.append((m.start(), m.end(), term))
    return [t for _, _, t in sorted(found)]


def _names_in(sentence: str) -> list[str]:
    tokens = _WORD_RE.findall(_nfc(sentence))
    names, current = [], []
    for i, tok in enumerate(tokens):
        capitalized = tok[:1].isupper() and i > 0 and tok.lower() not in DOMAIN_TERMS
        if capitalized:
            current.append(tok)
        elif current:
            names.append(" ".join(current))
            current = []
    if current:
        names.append(" ".join(current))
    return [n for n in names if n.lower() not in DOMAIN_TERMS]


def sentence_density(sentence: str) -> dict:
    return {
        "words": len(_words(sentence)),
        "numbers": _NUMBER_RE.findall(sentence),
        "terms": _terms_in(sentence),
        "names": _names_in(sentence),
    }


def fingerprint(script: str, n_words: int = DEFAULT_FINGERPRINT_WORDS) -> str:
    """N từ đầu đã chuẩn hoá (NFC, hạ chữ, bỏ dấu câu) của text sẽ được đọc."""
    if n_words < 1:
        raise ValueError("n_words phải >= 1")
    norm = re.sub(r"[^\w\s]", " ", _nfc(spoken_text(script or "")).lower())
    return " ".join(norm.split()[:n_words])


def time_to_hook(script: str, hook_span: str) -> dict:
    """Khoảng cách tới điểm móc: số từ đứng trước span chi tiết móc trong text
    sẽ được đọc, quy ra giây theo 170 và 200 wpm. Span không hợp lệ -> ValueError."""
    text = _nfc(spoken_text(script or ""))
    span = _nfc(spoken_text(hook_span or "")).strip()
    if not span:
        raise ValueError("span chi tiết móc rỗng")
    idx = text.find(span)
    if idx < 0:
        raise ValueError(f"span chi tiết móc không có trong script: {span[:80]!r}")
    words_before = len(text[:idx].split())
    return {"words_before_hook": words_before,
            "seconds_before_hook": {f"{wpm}wpm": round(words_before / wpm * 60, 2) for wpm in WPM_RATES}}


def diagnostics(script: str, *, fingerprint_words: int = DEFAULT_FINGERPRINT_WORDS) -> dict:
    """Mọi tín hiệu chẩn đoán bằng code của một script (không có điểm)."""
    text = spoken_text(script or "")
    sentences = split_sentences(text)
    per_sentence = [sentence_density(s) for s in sentences]
    return {
        "diagnostics_version": DIAGNOSTICS_VERSION,
        "sentence_count": len(sentences),
        "total_words": sum(d["words"] for d in per_sentence),
        "first_sentence_words": per_sentence[0]["words"] if per_sentence else 0,
        "sentence_words": [d["words"] for d in per_sentence],
        "density": [{"sentence": i, "numbers": len(d["numbers"]), "terms": len(d["terms"]),
                     "names": len(d["names"]), "number_tokens": d["numbers"], "term_tokens": d["terms"],
                     "name_tokens": d["names"]} for i, d in enumerate(per_sentence)],
        "fingerprint": fingerprint(script, fingerprint_words),
        "fingerprint_words": fingerprint_words,
    }
