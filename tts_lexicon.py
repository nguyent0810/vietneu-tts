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
from functools import lru_cache
from pathlib import Path

LEXICON_PATH = Path(__file__).with_name("tts_lexicon.json")

_BOOKS = {"DN": "Trường Bộ", "MN": "Trung Bộ", "SN": "Tương Ưng Bộ", "AN": "Tăng Chi Bộ", "Dhp": "Pháp Cú"}
# DN 16 / MN 7 / Dhp 113 / SN 12.2 (không dính chữ khác phía trước; \b để "AN" trong từ khác không khớp)
_CODE = re.compile(r"\b(DN|MN|SN|AN|Dhp)\s*(\d{1,3})(?:\.(\d{1,3}))?(?![\d.]\d)")
_RANGE = re.compile(r"(?<![\d/.:-])(\d{1,4})\s*[-–]\s*(\d{1,4})(?![\d/.:-])")


@lru_cache(maxsize=1)
def _names() -> list[tuple[re.Pattern, str]]:
    try:
        data = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    # Tên dài trước để "Sāriputta" không bị "Sāri" nuốt mất.
    for src in sorted(data.get("names", {}), key=len, reverse=True):
        out.append((re.compile(rf"(?<!\w){re.escape(src)}(?!\w)", re.I), data["names"][src]))
    return out


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
