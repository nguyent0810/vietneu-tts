"""Chuẩn hoá chữ viết -> chữ ĐỌC trước khi đưa vào TTS (video dài).

Lint `long_script_lint.py` chỉ CẢNH BÁO bẫy đọc (Pali, "1-3", "DN 16", %, ngoặc...). Module này sửa chúng tự động
để cùng một cụm luôn được đọc cùng một cách ở mọi video. Chỉ đổi chữ ĐỌC; phụ đề / manifest vẫn giữ chữ gốc.

- Tên Pali / Phạn -> tên Việt: bảng `tts_lexicon.json` (sửa tay được, khớp nguyên từ, không phân biệt hoa thường
  khi tên có dấu Pali; thêm tên mới = thêm một dòng, không cần sửa code).
- Mã kinh: "DN 16" -> "Trường Bộ kinh số mười sáu". Chỉ khớp mã VIẾT HOA kèm số (không đụng tên "An").
- Khoảng số "1-3" -> "1 đến 3" (TTS đọc "1-3" thành ngày tháng); ngày "12-7-2025" giữ nguyên.
- "%" -> "phần trăm", "&" -> "và"; ngoặc đơn -> dấu phẩy (TTS bỏ ngoặc mà không ngắt hơi); "..." -> dấu phẩy.

Thuần Python, không mạng. `apply(text)` luôn trả chuỗi; không khớp gì thì trả lại nguyên văn.
"""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

LEXICON_PATH = Path(__file__).with_name("tts_lexicon.json")

_BOOKS = {"DN": "Trường Bộ", "MN": "Trung Bộ", "SN": "Tương Ưng Bộ", "AN": "Tăng Chi Bộ", "Dhp": "Pháp Cú"}
# DN 16 / MN 7 / Dhp 113 / SN 12.2 (không dính chữ khác phía trước; \b để "AN" trong từ khác không khớp)
_CODE = re.compile(r"\b(DN|MN|SN|AN|Dhp)\s*(\d{1,3})(?:\.(\d{1,3}))?(?![\d.]\d)")
_RANGE = re.compile(r"(?<![\d/.:-])(\d{1,4})\s*[-–]\s*(\d{1,4})(?![\d/.:-])")
# speech_text (task 84/92a): số đứng riêng, gạch nối tên, phẩy trước liên từ
_INT = re.compile(r"(?<![\d/.:-])(\d{1,6})(?![\d/.:-])")
_HYPHEN = re.compile(r"\b[\wÀ-ỹA-Za-z]+(?:-[\wÀ-ỹA-Za-z]+){1,}\b")
_CONJ = re.compile(r"^(.*\S)\s+(vì|nên|nhưng|mà)\b(.*)$")


@lru_cache(maxsize=1)
def _names() -> list[tuple[re.Pattern, str]]:
    try:
        data = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    names = {k: v for k, v in data.get("names", {}).items() if not k.startswith("_")}
    for src, vi in list(names.items()):            # gõ không dấu Pali (Ananda) vẫn khớp
        names.setdefault(_fold(src), vi)
    # Tên dài trước để "Sāriputta" không bị "Sāri" nuốt mất.
    return [(re.compile(rf"(?<!\w){re.escape(src)}(?!\w)", re.I), names[src])
            for src in sorted(names, key=len, reverse=True)]


def _fold(s: str) -> str:
    """Bỏ dấu Pali (ā ṇ ṃ...) nhưng GIỮ dấu tiếng Việt: chỉ các ký tự Latin mở rộng ngoài bảng chữ Việt."""
    pali = "āīūṅñṭḍṇḷṃṁśṣĀĪŪ"
    return "".join(
        unicodedata.normalize("NFD", ch)[0] if ch in pali else ch for ch in s
    )


def _read_int(n: int) -> str:
    from long_script_lint import read_int  # noqa: PLC0415 -- nhập muộn: lint kéo theo hf_batch_render
    return read_int(n)


def _code(m: re.Match) -> str:
    book, a, b = _BOOKS[m.group(1)], int(m.group(2)), m.group(3)
    if b is None:
        return f"{book} kinh số {_read_int(a)}"
    return f"{book} {_read_int(a)}, kinh {_read_int(int(b))}"


def apply(text: str) -> str:
    s = text
    for pat, vi in _names():
        s = pat.sub(vi, s)
    s = _CODE.sub(_code, s)
    s = _RANGE.sub(r"\1 đến \2", s)
    s = s.replace("%", " phần trăm").replace("&", " và ")
    s = re.sub(r"\s*\(\s*", ", ", s)
    s = re.sub(r"\s*\)\s*", ", ", s)
    s = re.sub(r"\s*(\.\.\.|…)\s*", ", ", s)
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r",\s*([,.!?])", r"\1", s)        # ", ." sau khi thay ngoặc cuối câu
    s = re.sub(r"^\s*,\s*", "", s)
    return s.strip()


def speech_text(text: str, *, lexicon: bool = True) -> str:
    """Chữ đọc kiểu nói: lexicon (tuỳ chọn), số → chữ, gạch nối → khoảng, phẩy trước liên từ.

    Bật khi plan tts có ``text_mode: speech``. Phụ đề vẫn giữ chữ gốc; chỉ chuỗi đưa vào TTS đổi.
    """
    s = apply(text) if lexicon else text
    s = _HYPHEN.sub(lambda m: m.group(0).replace("-", " "), s)
    s = _INT.sub(lambda m: _read_int(int(m.group(1))), s)

    def comma(m: re.Match) -> str:
        left, word, rest = m.group(1), m.group(2), m.group(3)
        if len(left.split()) >= 6 and left[-1] not in ",;:":
            return f"{left}, {word}{rest}"
        return m.group(0)

    s = _CONJ.sub(comma, s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ,")
    if s and s[-1] not in ".?!…:":
        s += "."
    return s
