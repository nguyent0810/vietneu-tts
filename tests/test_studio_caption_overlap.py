"""Phụ đề Studio: nhóm chữ trước phải tắt đúng lúc nhóm sau hiện, không chồng khung (lỗi Quét nhà 05/11)."""
import re
from pathlib import Path

CORE = Path(__file__).resolve().parents[1] / "hyperframes_short" / "studio" / "core.js"


def _caption_block() -> str:
    src = CORE.read_text(encoding="utf-8")
    start = src.index("// ---------- phụ đề")
    return src[start:src.index("window.__timelines", start)]


def test_next_group_shows_when_previous_hides():
    block = _caption_block()
    lead = re.search(r"LEAD = ([\d.]+)", block)
    assert lead, "thiếu hằng LEAD cho độ hiện sớm của nhóm phụ đề"
    # nhóm giữa câu tắt ở (chữ đầu nhóm sau - LEAD), đúng lúc nhóm sau hiện ở (t0 - LEAD)
    assert "ws[k + n].t - LEAD" in block
    assert "t0 - LEAD" in block
    assert "t0 - .05" not in block and "t0 - 0.05" not in block


def test_overlap_free_on_sample_timing():
    lead = 0.05
    words = [0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0]
    n, end = 5, 3.3
    spans = []
    for k in range(0, len(words), n):
        t0 = words[k]
        t1 = end + .1 if k + n >= len(words) else max(t0, words[k + n] - lead)
        spans.append((max(0, t0 - lead), t1))
    for (a0, a1), (b0, _) in zip(spans, spans[1:]):
        assert a1 <= b0, f"nhóm chồng nhau: tắt {a1} > hiện {b0}"
