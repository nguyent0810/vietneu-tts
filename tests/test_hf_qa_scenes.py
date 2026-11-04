"""Hình học phụ đề / vật che / khung trống và đo trang DOM thật."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hf_qa  # noqa: E402

try:
    _CHROME_PATH = hf_qa._chrome_path()
except Exception:
    _CHROME_PATH = None

requires_chrome = pytest.mark.skipif(not _CHROME_PATH, reason="Cần Chrome để đo trang")


CANVAS = {"x": 0, "y": 0, "w": 1920, "h": 1080}
CAP = {"x": 64, "y": 900, "w": 1792, "h": 120}


def _el(rect, **kw):
    base = {
        "selector": "div.item",
        "rect": rect,
        "opacity": 1,
        "z": 0,
        "order": 1,
        "in_caption": False,
        "is_media": False,
        "bg_alpha": 0,
        "clips": [],
    }
    base.update(kw)
    return base


def test_phu_de_lan_4px_thi_sach_5px_thi_bao():
    shallow = _el({"x": 200, "y": 860, "w": 800, "h": 44})  # đáy chạm 4px vào vùng phụ đề
    deep = _el({"x": 200, "y": 860, "w": 800, "h": 45})  # lấn 5px
    assert hf_qa.caption_hits([shallow], CAP, CANVAS) == []
    hits = hf_qa.caption_hits([deep], CAP, CANVAS)
    assert len(hits) == 1 and hits[0]["code"] == "caption_overlap"


def test_dien_tich_giao_45_sach_160_bao():
    small = _el({"x": 400, "y": 910, "w": 9, "h": 5})  # 45
    big = _el({"x": 400, "y": 910, "w": 32, "h": 5})  # 160, sâu 5px
    assert hf_qa.caption_hits([small], CAP, CANVAS) == []
    assert len(hf_qa.caption_hits([big], CAP, CANVAS)) == 1


def test_vong_mo_va_lop_kin_khung_khong_tinh_la_de_phu_de():
    ring = _el({"x": 0, "y": 900, "w": 400, "h": 80}, opacity=0.2)
    wrap = _el({"x": 0, "y": 0, "w": 1920, "h": 1080})
    cap_child = _el({"x": 400, "y": 920, "w": 800, "h": 80}, in_caption=True)
    assert hf_qa.caption_hits([ring, wrap, cap_child], CAP, CANVAS) == []


def test_circle_nho_che_nhieu_circle_lon_khong_che():
    box = {"x": 0, "y": 0, "w": 1920, "h": 1080}
    small = hf_qa.clip_hidden_fraction("circle(30% at 50% 45%)", box, box)
    big = hf_qa.clip_hidden_fraction("circle(78% at 50% 45%)", box, box)
    assert 0.60 < small < 0.75
    assert big < 0.02


def test_inset_giau_dung_mot_nua():
    box = {"x": 0, "y": 0, "w": 1920, "h": 1080}
    hidden = hf_qa.clip_hidden_fraction("inset(0% 50% 0% 0%)", box, box)
    assert hidden == pytest.approx(0.5, abs=0.01)


def test_khong_doc_duoc_clip_thi_khong_bia_ty_le():
    box = {"x": 0, "y": 0, "w": 100, "h": 100}
    assert hf_qa.clip_hidden_fraction("polygon(0 0, 10 0, 10 10)", box, box) == 0
    assert hf_qa.clip_hidden_fraction("none", box, box) == 0


def test_vat_che_chi_khi_anh_tran_va_bi_giau_qua_nguong():
    full = _el(
        {"x": 0, "y": 0, "w": 1920, "h": 1080},
        is_media=True,
        clips=[{"clip": "circle(20% at 50% 50%)", "box": {"x": 0, "y": 0, "w": 1920, "h": 1080}}],
    )
    card = _el(
        {"x": 400, "y": 80, "w": 700, "h": 740},
        is_media=True,
        clips=[{"clip": "circle(10% at 50% 50%)", "box": {"x": 400, "y": 80, "w": 700, "h": 740}}],
    )
    open_full = _el({"x": 0, "y": 0, "w": 1920, "h": 1080}, is_media=True, clips=[])
    hits = hf_qa.occlusion_hits([full, card, open_full], CANVAS)
    assert [h["selector"] for h in hits] == ["div.item"]
    assert hits[0]["cover"] > 0.30


def test_lop_dac_33_phan_tram_thi_bao_nhan_nho_thi_khong():
    media = _el({"x": 0, "y": 0, "w": 1920, "h": 1080}, is_media=True, order=1, selector="div.media")
    label = _el({"x": 100, "y": 100, "w": 200, "h": 80}, bg_alpha=1, order=2, selector="div.label")
    panel = _el({"x": 0, "y": 0, "w": 1920, "h": 360}, bg_alpha=1, order=3, selector="div.panel")
    assert hf_qa.occlusion_hits([media, label], CANVAS) == []
    hits = hf_qa.occlusion_hits([media, panel], CANVAS)
    assert len(hits) == 1 and hits[0]["solid"] > 0.30


def test_nen_sau_anh_khong_tinh_la_vat_che():
    bed = _el({"x": 0, "y": 0, "w": 1920, "h": 1080}, bg_alpha=1, order=1, selector="div.bed")
    media = _el({"x": 0, "y": 0, "w": 1920, "h": 1080}, is_media=True, order=2, selector="div.media")
    assert hf_qa.occlusion_hits([bed, media], CANVAS) == []


def test_khung_trong_chi_khi_cuoi_trong_hon_giua():
    assert hf_qa.empty_end(0.9704, 0.0252, 0.9925, 0.0033) is True
    assert hf_qa.empty_end(0.9372, 0.0395, 0.9962, 0.0020) is True
    assert hf_qa.empty_end(0.9674, 0.0279, 0.9576, 0.0382) is False
    assert hf_qa.empty_end(0.9372, 0.0395, 0.9416, 0.0388) is False
    # một khung tối, không có giữa: hàm bắt buộc đủ bốn số; nền cao nhưng không tăng thì không báo
    assert hf_qa.empty_end(0.9825, 0.0028, 0.9825, 0.0028) is False


def test_anh_nen_toi_va_anh_co_net():
    from PIL import Image, ImageDraw
    navy = Image.new("RGB", (320, 180), (11, 17, 48))
    busy = navy.copy()
    draw = ImageDraw.Draw(busy)
    draw.ellipse((40, 40, 280, 140), outline=(240, 210, 120), width=3)
    draw.rectangle((120, 70, 200, 110), fill=(212, 169, 58))
    empty_bg, empty_edge = hf_qa.frame_bg_and_edge(navy)
    busy_bg, busy_edge = hf_qa.frame_bg_and_edge(busy)
    assert empty_bg > 0.985 and empty_edge < 0.01
    assert busy_edge > empty_edge
    assert hf_qa.empty_end(busy_bg, busy_edge, empty_bg, empty_edge) is True
    assert hf_qa.empty_end(busy_bg, busy_edge, busy_bg, busy_edge) is False


def test_moc_giao_canh_theo_khoang_nghi():
    lines = [
        {"start": 0.0, "end": 3.35},
        {"start": 3.5, "end": 6.85},
        {"start": 10.0, "end": 13.0},
    ]
    assert hf_qa.handover_time(lines, 0) == pytest.approx(3.01)
    assert hf_qa.handover_time(lines, 1) == pytest.approx(9.66)
    assert hf_qa.handover_time(lines, 2) is None


def test_mau_cuoi_truoc_fade_outro():
    lines = [{"start": 42.0, "end": 45.35}, {"start": 0.0, "end": 3.35}]
    last = hf_qa.scene_sample_times([{"start": 42.0, "end": 45.35}], 45.5)[0]
    end = next(s for s in last["samples"] if s["phase"] == "end")
    assert end["t"] <= 45.5 - 0.55
    first = hf_qa.scene_sample_times(lines[:1], 45.5)
    assert first[0]["samples"][0]["phase"] == "mid"


# ---------------------------------------------------------------------------
# Test DOM thật qua measure_scenes / audit_scenes (HTTP server + Chrome)
# ---------------------------------------------------------------------------


def _write_qa_fixture(folder: Path, body_inner: str) -> tuple[Path, Path]:
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script>
  window.__timelines = {{
    main: {{ seek: function(t) {{}}, pause: function() {{}} }}
  }};
</script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body, html {{ width: 1920px; height: 1080px; overflow: hidden; }}
  #root {{ position: relative; width: 1920px; height: 1080px; }}
  #capzone {{ position: absolute; left: 0; top: 900px; width: 1920px; height: 180px; }}
  .cap {{ position: absolute; left: 100px; top: 20px; width: 1720px; height: 100px; background: rgba(0,0,0,0.9); color: white; }}
</style>
</head>
<body data-duration="5">
  <div id="root">
{body_inner}
  </div>
</body>
</html>"""
    h_file = folder / "index.html"
    v_file = folder / "vars.json"
    h_file.write_text(html, encoding="utf-8")
    v_file.write_text(json.dumps({
        "duration": 5.0,
        "lines": [{"start": 0.0, "end": 4.5, "text": "Dòng phụ đề mẫu"}]
    }), encoding="utf-8")
    return h_file, v_file


@requires_chrome
def test_real_fixture_phu_de_bi_de(tmp_path):
    """Fixture thật 1: Phụ đề bị đè bởi phần tử có nền/chữ, audit_scenes phải báo caption_overlap."""
    body = (
        '    <div class="badge" style="position: absolute; left: 200px; top: 910px; '
        'width: 300px; height: 80px; background: red; z-index: 10;">Nút đè phụ đề</div>\n'
        '    <div id="capzone"><div class="cap">Dòng phụ đề mẫu</div></div>'
    )
    h_file, v_file = _write_qa_fixture(tmp_path, body)
    rep = hf_qa.audit_scenes(h_file, v_file, project_dir=tmp_path / "proj")
    overlaps = [f for f in rep["findings"] if f.get("code") == "caption_overlap"]
    assert len(overlaps) >= 1
    assert any(f.get("selector") == "div.badge" for f in overlaps)
    assert overlaps[0]["area"] >= 50
    assert overlaps[0]["depth"] >= 5


@requires_chrome
def test_real_fixture_phan_tu_bi_cat_boi_cha_overflow_khong_bao(tmp_path):
    """Fixture thật 2: Bbox thô chạm phụ đề nhưng bị cha overflow:hidden cắt, không được báo lỗi."""
    body = (
        '    <div class="clipper" style="position: absolute; left: 200px; top: 100px; '
        'width: 400px; height: 300px; overflow: hidden;">\n'
        '      <div class="child" style="position: absolute; left: 0; top: 800px; '
        'width: 400px; height: 100px; background: blue;">Bị cha cắt khỏi màn hình</div>\n'
        '    </div>\n'
        '    <div id="capzone"><div class="cap">Dòng phụ đề mẫu</div></div>'
    )
    h_file, v_file = _write_qa_fixture(tmp_path, body)
    rep = hf_qa.audit_scenes(h_file, v_file, project_dir=tmp_path / "proj")
    assert rep["findings"] == []


@requires_chrome
def test_real_fixture_stacking_context_dao_thu_tu_dung_lop(tmp_path):
    """Fixture thật 3: Stacking context đảo thứ tự z-index; hit-testing elementsFromPoint nhận diện đúng lớp thật."""
    # ctx-high có z-index: 2, con .overlay-card chỉ có z-index: 1
    # ctx-low có z-index: 1, bên trong capzone có .cap z-index: 9999
    # Vì ctx-high ở trên ctx-low, .overlay-card thực sự vẽ đè lên .cap
    body = (
        '    <div class="ctx-low" style="position: relative; z-index: 1;">\n'
        '      <div id="capzone">\n'
        '        <div class="cap" style="position: absolute; left: 100px; top: 20px; '
        'width: 1720px; height: 120px; background: rgba(0,0,0,0.95); z-index: 9999;">Dòng phụ đề</div>\n'
        '      </div>\n'
        '    </div>\n'
        '    <div class="ctx-high" style="position: relative; z-index: 2;">\n'
        '      <div class="overlay-card" style="position: absolute; left: 200px; top: 910px; '
        'width: 400px; height: 100px; background: red; z-index: 1;">Card đè phụ đề dù z cục bộ = 1</div>\n'
        '    </div>'
    )
    h_file, v_file = _write_qa_fixture(tmp_path, body)
    rep = hf_qa.audit_scenes(h_file, v_file, project_dir=tmp_path / "proj")
    overlaps = [f for f in rep["findings"] if f.get("code") == "caption_overlap"]
    assert len(overlaps) >= 1
    assert any(f.get("selector") == "div.overlay-card" for f in overlaps)
