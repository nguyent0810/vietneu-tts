"""Sàn nhịp hình trong hf_batch_render.pacing: chỉ cảnh báo, không vào danh sách chặn render."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hf_batch_render as HBR  # noqa: E402

_TYPES = ["wheel", "elements", "years", "list", "timeline", "compare", "map", "illus",
          "doc", "photo", "clock", "ledger", "museum", "napam"]


def _segs(n, step=2.0):
    return [{"start": i * step, "end": i * step + 1.5} for i in range(n)]


def test_san_duoi_14_loai_chu_nen_trong_va_ba_canh_lien():
    row = {"script": ["Một câu.", "Hai câu.", "Ba câu."], "kinetic": True}
    rep, bad = HBR.pacing(row, _segs(3))
    san = rep["sàn"]
    assert any("loại cảnh" in x and "14" in x for x in san)
    assert any("nền trống" in x for x in san)
    assert any("3 cảnh liền cùng loại 'chữ khoá'" in x for x in san)
    assert not set(san) & set(bad)


def test_san_du_14_loai_thi_khong_bao_thieu_loai():
    script = [f"Câu số {i}." for i in range(14)]
    row = {"script": script, "visuals": {str(i + 1): {"type": t} for i, t in enumerate(_TYPES)}}
    rep, bad = HBR.pacing(row, _segs(14))
    assert rep["loại cảnh"] >= 14
    assert not any("loại cảnh" in x for x in rep["sàn"])
    assert not any("nền trống" in x for x in rep["sàn"])
    assert not any("liền cùng loại" in x for x in rep["sàn"])
    assert not set(rep["sàn"]) & set(bad)


def test_ba_anh_lien_khong_bi_canh_bao_cung_loai():
    script = ["Ảnh một.", "Ảnh hai.", "Ảnh ba."]
    row = {"script": script, "media": {"1": {"src": "a"}, "2": {"src": "b"}, "3": {"src": "c"}}}
    rep, bad = HBR.pacing(row, _segs(3))
    assert not any("ảnh/clip" in x for x in rep["sàn"])
    assert not set(rep["sàn"]) & set(bad)


def test_ba_quote_lien_la_canh_bao():
    script = ["Câu một.", "Câu hai.", "Câu ba."]
    row = {"script": script, "visuals": {str(i): {"type": "quote"} for i in range(1, 4)}}
    rep, _bad = HBR.pacing(row, _segs(3))
    assert any("3 cảnh liền cùng loại 'quote'" in x for x in rep["sàn"])
