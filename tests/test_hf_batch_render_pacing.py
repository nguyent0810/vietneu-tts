"""pacing() tách nhãn ảnh/clip theo loại media (23/10/2026): tư liệu / stock / ảnh AI.

Long thử Cao Biền 23/10 báo gộp "ảnh/clip 33%" nên không đo được tỉ lệ tư liệu thật so với stock, ảnh AI.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hf_batch_render as B  # noqa: E402


def _row(media, n=6, **kw):
    script = [f"Câu số {i + 1} kể chuyện." for i in range(n)]
    segs = [{"start": i * 5.0, "end": i * 5.0 + 4.8} for i in range(n)]
    return {"script": script, "media": media, "visuals": {}, "kinetic": True, **kw}, segs


def test_media_label_theo_kind():
    for k in ("commons", "museum", "ext", "openverse", "pdvideo"):
        assert B.media_label({"kind": k}) == "tư liệu"
    assert B.media_label({"kind": "image"}) == "stock"
    assert B.media_label({"kind": "video"}) == "stock"
    assert B.media_label({}) == "stock"            # resolve_media mặc định kind "video"
    assert B.media_label({"kind": "LOCAL"}) == "ảnh AI"
    assert B.media_label({"kind": "la"}) == "ảnh/clip"


def test_ti_le_tach_theo_loai_va_dong_giu_anh_theo_chu():
    row, segs = _row({"1": {"kind": "commons", "ref": "x"}, "3": {"kind": "local", "path": "a.png"},
                      "5": {"kind": "image", "query": "rain"}})
    rep, _ = B.pacing(row, segs)
    share = rep["tỉ lệ"]
    assert "ảnh/clip" not in share
    # mỗi ảnh giữ tiếp câu sau (media_holds) -> 2 câu mỗi loại (câu cuối ngắn hơn 0,2 s)
    assert abs(share["tư liệu"] - 33.6) < .2 and abs(share["ảnh AI"] - 33.6) < .2 and abs(share["stock"] - 32.9) < .2
    assert abs(sum(share.values()) - 100) < .5


def test_nguong_chan_giu_nguyen_cho_moi_loai_anh():
    # Trước đây "ảnh/clip" > 25% không bị chặn; các nhãn mới cũng vậy.
    for kind in ("commons", "local", "video"):
        row, segs = _row({str(i + 1): {"kind": kind} for i in range(6)})
        _, bad = B.pacing(row, segs)
        assert not [x for x in bad if "chiếm" in x], (kind, bad)
