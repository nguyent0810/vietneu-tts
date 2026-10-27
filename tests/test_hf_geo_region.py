"""hf_geo_region: khung + phép chiếu, lọc nước hiện đại, mặt nạ biển, khoá cache, bake/profile.

Phần cần dữ liệu thật (DEM Copernicus) tự bỏ qua khi máy không có $VIENEU_GEO_DATA.
"""
import math
import re
from pathlib import Path

import numpy as np
import pytest

import hf_geo_region as R
import hyperframes_bridge as B

ROOT = Path(__file__).resolve().parents[1]
HAS_DEM = any((R.DATA / "copernicus").glob("*.tif"))
try:
    import rasterio  # noqa: F401 -- chỉ cần lúc nướng; CI không cài
except ImportError:
    HAS_DEM = False


def test_fit_bbox_ra_dung_ti_le_khung():
    for bbox in ([106.3, 17.25, 106.95, 17.75], [106.5, 17.0, 106.6, 18.0]):
        lon0, lat0, lon1, lat1 = R.fit_bbox(bbox)
        assert lon0 <= bbox[0] and lat0 <= bbox[1] and lon1 >= bbox[2] and lat1 >= bbox[3]
        k = math.cos(math.radians((lat0 + lat1) / 2))
        assert (lon1 - lon0) * k / (lat1 - lat0) == pytest.approx(16 / 9, rel=1e-3)


def test_projector_goc_khung():
    p = R.projector([106.0, 17.0, 107.0, 18.0], 3840, 2160)
    assert p(106.0, 18.0) == (0, 0)
    assert p(107.0, 17.0) == (3840, 2160)


def _way(tags, pts):
    return {"type": "way", "tags": tags, "geometry": [{"lon": x, "lat": y} for x, y in pts]}


def test_loc_nuoc_hien_dai():
    proj = R.projector([0, 0, 1, 1], 1000, 1000)
    big = [(0.1, 0.1), (0.5, 0.1), (0.5, 0.5), (0.1, 0.5)]
    tiny = [(0.1, 0.1), (0.101, 0.1), (0.101, 0.101)]
    els = [
        _way({"natural": "water", "water": "reservoir", "name": "Hồ X"}, big),   # hồ chứa: bỏ dù có tên
        _way({"natural": "water", "water": "pond"}, big),                         # ao: bỏ
        _way({"natural": "water"}, tiny),                                         # mặt nước nhỏ không tên: bỏ
        _way({"natural": "water", "name": "Phá Y"}, tiny),                        # có tên: giữ
        _way({"natural": "water"}, big),                                          # lớn không tên: giữ
        _way({"waterway": "canal", "name": "Kênh"}, [(0, 0), (1, 1)]),            # kênh: bỏ
        _way({"waterway": "river"}, [(0, 0), (0.01, 0.01)]),                      # rạch ngắn không tên: bỏ
        _way({"waterway": "river", "name": "Sông Z"}, [(0, 0), (0.01, 0.01)]),    # sông có tên: giữ
    ]
    polys, rivers = R.historic_water(els, proj, 1000, 1000)
    assert len(polys) == 2
    assert [named for _, named in rivers] == [True]


def test_mat_na_bien_bo_ao_trong_dat_lien():
    pytest.importorskip("scipy")
    z = np.full((200, 300), 20.0, "float32")
    z[:, 250:] = 0        # biển ở mép phải
    z[90:110, 90:110] = 0  # ao trũng giữa đất liền
    sea = R.sea_mask(z)
    assert sea[:, 260:].all()
    assert not sea[100, 100]


def test_khoa_cache_doi_theo_bbox_va_kieu():
    a = R.cache_key([106, 17, 107, 18], 3840, 2160, "giay")
    assert a == R.cache_key([106, 17, 107, 18], 3840, 2160, "giay")
    assert a != R.cache_key([106, 17, 107, 18.1], 3840, 2160, "giay")
    assert a != R.cache_key([106, 17, 107, 18], 5760, 3240, "giay")


def test_bake_toa_do_va_nhan():
    s = R.bake({"bbox": [106.3, 17.25, 106.95, 17.75],
                "camera": [{"center": [106.62, 17.46], "zoom": 2}],
                "pins": [{"name": "A", "lon": 106.62405, "lat": 17.46334}],
                "lines": [{"name": "L", "coords": [[106.60, 17.40], [106.60, 17.50]], "label": [106.5, 17.5]}],
                "areas": [{"name": "V", "center": [106.6, 17.45], "r_km": 2}]}, render=False)
    g = s["_geo"]
    assert (g["W"], g["H"]) == (3840, 2160)
    assert 0 < g["pins"][0]["x"] < g["W"] and 0 < g["pins"][0]["y"] < g["H"]
    ln = g["lines"][0]
    assert ln["km"] == pytest.approx(11.1, abs=0.2)          # 0,1 độ vĩ ≈ 11,1 km
    assert ln["d"].startswith("M") and ln["angle"] == pytest.approx(-90, abs=0.5)  # đi lên phía bắc
    lx, _ = R.projector(g["bbox"], 3840, 2160)(106.5, 17.5)
    assert ln["lx"] == pytest.approx(lx, abs=0.1)
    assert g["areas"][0]["r"] == pytest.approx(2 / R.km_per_px(g["bbox"], 3840), abs=0.2)


@pytest.mark.skipif(not HAS_DEM, reason="không có DEM Copernicus ở VIENEU_GEO_DATA")
def test_profile_dem_that():
    p = R.profile({"from": [106.45, 17.463], "to": [106.70, 17.463],
                   "marks": [{"label": "Quảng Bình Quan", "lon": 106.62405, "lat": 17.463}]})["_prof"]
    assert p["km"] == pytest.approx(26.5, abs=0.5)
    x0, y0, x1, y1 = p["box"]
    xs = [float(v) for v in re.findall(r"([\d.]+),[\d.]+", p["line"])]
    assert min(xs) >= x0 - .5 and max(xs) <= x1 + .5
    assert p["exag"] > 1 and p["marks"][0]["km"] == pytest.approx(18.6, abs=0.5)


def test_canh_dang_ky_va_longform_co_dinh_nghia():
    assert "region" in B.VISUAL_TYPES and "profile" in B.VISUAL_TYPES
    js = (ROOT / "hyperframes_short" / "compositions" / "longform.js").read_text(encoding="utf-8")
    assert "visuals.region = {" in js and "visuals.profile = {" in js
    reg = js[js.index("visuals.region = {"): js.index("visuals.profile = {")]
    assert "Math.random" not in reg and "Date" not in reg   # tất định khi tua
    assert "onUpdate" in reg                                 # camera = một tween tiến trình
    assert reg.index("opacity: 0 }, { opacity: 1, duration: .05") < reg.index("drawOn(tl, L.p")  # ẩn đầu nét trước khi vẽ
