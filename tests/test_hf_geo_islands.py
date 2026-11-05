"""Lớp Hoàng Sa / Trường Sa (#72): các ca không cần cache Natural Earth thật."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hf_geo  # noqa: E402


def _ident(lon, lat):
    # proj giả: toạ độ đầu vào đã là px
    return lon, lat


@pytest.fixture
def fake_islands(monkeypatch):
    def use(rings):
        monkeypatch.setattr(hf_geo, "_ISLANDS", [("Paracel Is.", "Quần đảo Hoàng Sa (Việt Nam)", rings)])
    return use


def test_dao_cat_mep_khung_khong_dinh_nao_trong_khung_van_duoc_ve(fake_islands):
    # tam giác thò qua góc phải trên: cả 3 đỉnh ngoài khung, một cạnh cắt khung
    fake_islands([[(1850, -50), (1990, 60), (2050, -50)]])
    out = hf_geo.island_layer(_ident, 1920, 1080)
    assert len(out) == 1 and out[0]["d"].startswith("M")


def test_khung_nam_tron_trong_dao_van_tinh_la_thay(fake_islands):
    fake_islands([[(-100, -100), (2100, -100), (2100, 1200), (-100, 1200)]])
    assert len(hf_geo.island_layer(_ident, 1920, 1080)) == 1


def test_dao_ngoai_khung_bi_bo(fake_islands):
    fake_islands([[(2100, 100), (2200, 100), (2150, 180)]])
    assert hf_geo.island_layer(_ident, 1920, 1080) == []


def test_cum_dao_duoi_phu_de_co_o_phong_to_tren_capzone(fake_islands):
    fake_islands([[(900, 960), (960, 960), (930, 1010)], [(1000, 1000), (1004, 1000), (1002, 1004)]])
    (isl,) = hf_geo.island_layer(_ident, 1920, 1080)
    b = isl["inset"]
    # đáy ô sau khi sân khấu phóng 1.04 vẫn trên #capzone; nhãn ngồi trên ô
    assert 540 + (b["y"] + b["h"] - 540) * 1.04 <= hf_geo.CAP_TOP
    assert isl["ly"] < b["y"] and 36 <= b["x"] and b["x"] + b["w"] <= 1884
    # mọi đỉnh của cụm sau transform nằm trọn trong ô
    tx, ty = map(float, b["tf"][len("translate("):b["tf"].index(")")].split(","))
    for ring in hf_geo._ISLANDS[0][2]:
        for x, y in ring:
            X, Y = tx + b["s"] * x, ty + b["s"] * y
            assert b["x"] <= X <= b["x"] + b["w"] and b["y"] <= Y <= b["y"] + b["h"]


def test_cum_dao_tren_phu_de_khong_can_o_phong_to(fake_islands):
    fake_islands([[(900, 400), (960, 400), (930, 450)]])
    (isl,) = hf_geo.island_layer(_ident, 1920, 1080)
    assert "inset" not in isl


def test_thieu_cache_va_khong_tai_duoc_thi_bao_loi_khong_im_lang_bo_dao(monkeypatch, tmp_path):
    monkeypatch.setattr(hf_geo, "_ISLANDS", None)
    monkeypatch.setattr(hf_geo, "ISLANDS_CACHE", tmp_path / "geo" / "missing.geojson")

    def offline(*a, **k):
        raise OSError("offline")
    monkeypatch.setattr(hf_geo.urllib.request, "urlopen", offline)
    with pytest.raises(OSError):
        hf_geo.island_layer(_ident, 1920, 1080)


def test_cache_sai_sha256_thi_bao_loi(monkeypatch, tmp_path):
    bad = tmp_path / "bad.geojson"
    bad.write_text('{"features": []}', encoding="utf-8")
    monkeypatch.setattr(hf_geo, "_ISLANDS", None)
    monkeypatch.setattr(hf_geo, "ISLANDS_CACHE", bad)
    with pytest.raises(RuntimeError):
        hf_geo.island_layer(_ident, 1920, 1080)


def _overlap(a, b):
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def test_nhan_dao_tranh_the_ten_ghim():
    isl = [{"label": "Quần đảo Hoàng Sa (Việt Nam)", "lx": 985.0, "ly": 868.0}]
    pins = [{"name": "Giao Châu", "sub": "Hà Nội nay", "x": 806, "y": 806}]  # k=0 -> thẻ bên phải
    hf_geo._dodge_pin_cards(isl, pins)
    assert not _overlap(hf_geo._island_box(isl[0]), hf_geo._pin_card_box(pins[0], 0))


def test_nhan_dao_tranh_nhieu_the_ghim_va_trong_khung():
    isl = [{"label": "Quần đảo Hoàng Sa (Việt Nam)", "lx": 1500.0, "ly": 700.0}]
    pins = [{"name": "Một", "x": 1300, "y": 700, "side": "right"},
            {"name": "Hai Hai Hai", "x": 1500, "y": 700, "side": "right"}]
    hf_geo._dodge_pin_cards(isl, pins)
    box = hf_geo._island_box(isl[0])
    assert 36 <= box[0] and box[2] <= 1884
    assert not any(_overlap(box, hf_geo._pin_card_box(p, k)) for k, p in enumerate(pins))


def test_du_lieu_that_l_fs_27_cau_172_o_phong_to_bao_tron_hoang_sa(monkeypatch):
    """Tích hợp: hình Natural Earth thật (cần cache) ở khung bản đồ L_fs_27 câu 172."""
    if not hf_geo.ISLANDS_CACHE.exists():
        pytest.skip("chưa có cache Natural Earth; các test trên vẫn chạy không cần cache")
    monkeypatch.setattr(hf_geo, "_ISLANDS", None)
    bbox = [99.0, 19.0, 112.0, 32.5]
    g = hf_geo.bake({"countries": ["China"], "context": ["Vietnam"], "bbox": bbox,
                     "pins": [{"name": "Giao Châu", "sub": "Hà Nội nay", "lon": 105.85, "lat": 21.03}]})["_geo"]
    (isl,) = g["islands"]
    assert isl["label"] == "Quần đảo Hoàng Sa (Việt Nam)"
    b = isl["inset"]
    tx, ty = map(float, b["tf"][len("translate("):b["tf"].index(")")].split(","))
    proj = hf_geo._projector(bbox)
    rings = [r for n, _, rs in hf_geo._island_records() if n == "Paracel Is." for r in rs]
    for ring in rings:
        for lon, lat in ring:
            x, y = proj(lon, lat)
            X, Y = tx + b["s"] * x, ty + b["s"] * y
            # chấm r=5.5px + nét 2.4px vẫn trong ô
            assert b["x"] + 4 <= X <= b["x"] + b["w"] - 4 and b["y"] + 4 <= Y <= b["y"] + b["h"] - 4
    assert 540 + (b["y"] + b["h"] - 540) * 1.04 <= hf_geo.CAP_TOP
