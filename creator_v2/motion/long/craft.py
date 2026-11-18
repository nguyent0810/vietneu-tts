"""Chặn kịch bản đọc đều đều và cảnh lặp một kiểu.

Chỉ chạy khi spec ghi ``"craft": true`` (video mới). Video đã đăng không bật cờ này.
Âm tiết ở đây là số từ, cùng cách ``script_lines`` đang đếm.
"""
from __future__ import annotations

import re

_INTERRUPT = {
    "slam", "question", "counter", "date", "quote", "file", "photo", "map",
    "timeline", "print", "bars", "cards", "evidence", "ledger", "org", "split",
    "chapter", "brand",
}
_LIST = re.compile(r"^(Một là|Hai là|Ba là|Bốn là|Thứ nhất|Thứ hai|Thứ ba|Thứ tư|\d+[\.\)])")


def _text(line) -> str:
    return line if isinstance(line, str) else line.get("t", "")


OPEN_Q_LINES = 8
OPEN_Q_WORDS = 330   # ~90 giây ở 215 tiếng/phút: câu không giới hạn độ dài thì 8 câu có thể dài gấp đôi (#476)


def _early_question(lines) -> bool:
    """Câu hỏi đầu tiên nằm trong 8 câu đầu, hoặc trong khoảng 330 tiếng đầu (~90 giây)."""
    words = 0
    for i, line in enumerate(lines):
        t = _text(line)
        if "?" in t:
            return i < OPEN_Q_LINES or words < OPEN_Q_WORDS
        words += len(t.split())
    return False


def audio_problems(chapters) -> list[str]:
    """Kiểm tra nhịp kể; không giới hạn độ dài câu (chủ kênh 17/11/2026, #476)."""
    out: list[str] = []
    blob = []
    long_pause = False
    for ch in chapters:
        run = 0
        for i, line in enumerate(ch["lines"]):
            t = _text(line)
            blob.append(t)
            if "quý vị" in t.lower():
                out.append(f"{ch['name']} câu {i}: đang gọi 'quý vị', hãy gọi 'bạn'")
            if _LIST.match(t):
                run += 1
                if run == 4:
                    out.append(f"{ch['name']} câu {i}: liệt kê quá 3 mục")
            else:
                run = 0
            if isinstance(line, dict) and float(line.get("p") or 0) >= 0.9:
                long_pause = True
    if chapters:
        if not _early_question(chapters[0]["lines"]):
            out.append(f"{chapters[0]['name']}: chưa có câu hỏi trong {OPEN_Q_LINES} câu hay ~90 giây đầu")
        if "bạn" not in " ".join(blob).lower():
            out.append("cả kịch bản không gọi 'bạn'")
        if not long_pause:
            out.append("cả kịch bản không có nghỉ dài ‖")
    return out


def graphic_problems(name: str, scenes: list[dict]) -> list[str]:
    """Sáu cảnh cùng loại liên tiếp, hoặc cả chương không có một cảnh ngắt nhịp."""
    out: list[str] = []
    if not scenes:
        return [f"{name}: chưa có cảnh"]
    run = 1
    flagged = False
    for a, b in zip(scenes, scenes[1:]):
        if a.get("type") == b.get("type"):
            run += 1
            if run >= 6 and not flagged:
                out.append(f"{name}: {run} cảnh {a.get('type')} liên tiếp")
                flagged = True
        else:
            run = 1
            flagged = False
    if not any(s.get("type") in _INTERRUPT for s in scenes):
        out.append(f"{name}: không có cảnh ngắt (slam, question, date, counter, quote, file, photo)")
    return out
