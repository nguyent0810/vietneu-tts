"""Nền nhạc theo chương: không còn hụt về im ở chỗ nối lặp, chỉ đổi bản ở thẻ chương."""
from pathlib import Path

import numpy as np

import hf_foley as F
import hf_sutta as T


def test_bed_switches_only_at_chapters_and_has_no_holes(monkeypatch):
    sr = F.SR
    fake = {n: np.full((int(100 * sr), 2), .1 * (k + 1), dtype="float32") for k, n in enumerate(F.BGM_POOL["bud"])}
    monkeypatch.setattr(F, "_trimmed", lambda p: fake[str(p.relative_to(Path("/r")))])
    starts = [60.0 * k for k in range(1, 10)]           # thẻ chương mỗi 60 giây, bản dài 100 giây
    bed, used = F.music_bed(Path(F.BGM_POOL["bud"][1]), "bud", starts, 600.0, Path("/r"))
    assert used[0] == Path(F.BGM_POOL["bud"][1]).name and len(used) >= 5
    level = np.abs(bed[:, 0]).reshape(-1, sr // 2).mean(axis=1)
    assert level.min() > .03                              # không nửa giây nào im
    change = np.where(np.abs(np.diff(level)) > .02)[0] / 2.0
    assert all(min(abs(t - s) for s in starts) <= F.XFADE for t in change)


def test_sutta_citation_mapping():
    assert T.cite("Tăng Chi Bộ 11.15 · Kinh Lợi Ích") == "an11.15"
    assert T.cite("Trung Bộ 7 · Kinh Ví Dụ Tấm Vải") == "mn7"
    assert T.uid_for("dhp113") == "dhp100-115"
