"""Video dài: sơ đồ (apply_visuals), tên con giáp kênh FS, nhạc nền theo giọng.

Phản hồi sau 2 long đầu (29/09/2026): nhạc to, hình lặp một kiểu suốt video,
và script gọi "tuổi Lợn", "tuổi Dê" thay vì tên chi."""
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
COMP = ROOT / "hyperframes_short" / "compositions"


def _bridge(*names):
    # Bóc hàm bằng ast thay vì import: import bridge kéo theo kiểm external_bin.
    tree = ast.parse((ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8"))
    keep = [n for n in tree.body
            if (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names)
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in names for t in n.targets))]
    ns: dict = {"__name__": "bridge", "Path": Path}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "bridge", "exec"), ns)
    return ns


def _lines(n):
    return [{"sentence_id": i + 1, "start": i * 5.0, "end": (i + 1) * 5.0} for i in range(n)]


def test_so_do_chiem_cac_cau_toi_buoc_cuoi():
    ns = _bridge("apply_visuals", "HyperFramesError", "VISUAL_TYPES")
    lines = _lines(8)
    ns["apply_visuals"](lines, {"2": {"type": "wheel", "steps": [{"at": 3}, {"at": 5}]}}, {})
    assert lines[1]["visual"]["type"] == "wheel"
    assert [ln.get("visual_cont") for ln in lines] == [None, None, 2, 2, 2, None, None, None]


def test_so_do_until_ro_rang_va_khong_de_len_anh():
    ns = _bridge("apply_visuals", "HyperFramesError", "VISUAL_TYPES")
    lines = _lines(8)
    with pytest.raises(ns["HyperFramesError"], match="vừa có ảnh"):
        ns["apply_visuals"](lines, {"2": {"type": "list", "items": [{"at": 2}], "until": 4}}, {"3": {"query": "x"}})


def test_so_do_loai_la_va_buoc_ngoai_khoang_bi_chan():
    ns = _bridge("apply_visuals", "HyperFramesError", "VISUAL_TYPES")
    with pytest.raises(ns["HyperFramesError"], match="loại sơ đồ lạ"):
        ns["apply_visuals"](_lines(4), {"1": {"type": "globe"}}, {})
    with pytest.raises(ns["HyperFramesError"], match="phải nằm trong"):
        ns["apply_visuals"](_lines(8), {"4": {"type": "wheel", "steps": [{"at": 2}]}}, {})


def test_so_do_chong_nhau_bi_chan():
    ns = _bridge("apply_visuals", "HyperFramesError", "VISUAL_TYPES")
    with pytest.raises(ns["HyperFramesError"], match="chồng nhau"):
        ns["apply_visuals"](_lines(8), {"2": {"type": "wheel", "until": 5},
                                         "4": {"type": "list", "until": 6}}, {})


def test_nhac_nen_cach_giong_dung_khoang_dat():
    ns = _bridge("relative_bgm_gain", "BGM_GAP_DB")
    lufs = {"voice.wav": -20.5, "music.mp3": -15.3}
    ns["integrated_lufs"] = lambda p: lufs[str(p)]
    g = ns["relative_bgm_gain"]("voice.wav", "music.mp3", gap_db=21.0)
    # nhạc -15.3 LUFS * g phải ra đúng -20.5 - 21 = -41.5 LUFS
    import math
    assert abs(-15.3 + 20 * math.log10(g) - (-41.5)) < 0.01


def test_ten_con_giap_phai_la_ten_chi():
    import hf_batch_render as h
    assert h.zodiac_naming_errors(["Tuổi Sửu gặp xung.", "Sửu cùng nhóm tam hợp với hai tuổi Tỵ và Dậu."]) == []
    bad = h.zodiac_naming_errors(["Người tuổi Dê bước vào năm Mùi.", "tức Rắn, Gà và Trâu.", "Tuổi Lợn gồm năm 1971."])
    assert len(bad) == 3
    # tên con vật đứng đầu câu, không phải tên tuổi -> không bắt nhầm
    assert h.zodiac_naming_errors(["Gà trống gáy sáng."]) == []


def test_style_video_dai_nap_longform():
    for f in ("laban_long.html", "inkwash_long.html"):
        html = (COMP / f).read_text(encoding="utf-8")
        assert "longform.js" in html and "longform.css" in html, f
        assert html.index("engine.js") < html.index("longform.js") < html.index("HF.build()"), f


def test_engine_goi_vao_longform():
    js = (COMP / "engine.js").read_text(encoding="utf-8")
    for hook in ("window.HF_LONG", "ln.visual_cont", "LONG.chapter", "layoutOf("):
        assert hook in js, hook


def test_style_video_dai_xin_anh_ngang():
    # laban_long từng xin ảnh DỌC vì điều kiện chỉ xét đuôi "_wide".
    src = (ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8")
    ns = _bridge("LONG_STYLES")
    assert 'style.endswith(("_wide", "_long"))' in src
    assert all(s.endswith("_long") for s in ns["LONG_STYLES"])


def test_bo_cuc_tu_dong_khong_lap_lien_va_du_bo():
    ns = _bridge("auto_layouts", "LAYOUT_POOL", "VIDEO_LAYOUT_POOL")
    media = {str(k): {"kind": "image", "query": "x"} for k in range(1, 25)}
    out = ns["auto_layouts"](media, "L_fs_04")
    seq = [out[k] for k in sorted(out)]
    assert all(a != b for a, b in zip(seq, seq[1:])), "hai ảnh liền nhau cùng bố cục"
    assert set(seq) == set(ns["LAYOUT_POOL"]), "có bố cục không bao giờ được dùng"
    counts = [seq.count(p) for p in ns["LAYOUT_POOL"]]
    assert max(counts) - min(counts) <= 1, "phân bố lệch"
    assert out == ns["auto_layouts"](media, "L_fs_04"), "render lại phải ra y hệt"
    assert out != ns["auto_layouts"](media, "L_fs_05"), "video khác phải ra thứ tự khác"


def test_bo_cuc_ghi_tay_duoc_ton_trong_va_video_uu_tien_tran_khung():
    ns = _bridge("auto_layouts", "LAYOUT_POOL", "VIDEO_LAYOUT_POOL")
    out = ns["auto_layouts"]({"1": {"kind": "image", "layout": "split"}, "2": {"kind": "video"}}, "x")
    assert out[1] == "split" and out[2] in ns["VIDEO_LAYOUT_POOL"]


def test_chu_tach_tung_tu_khong_dinh_lien():
    # Khoảng trắng cuối inline-block bị bỏ: showreel ra "SƠĐỒNGŨHÀNH".
    css = (COMP / "longform.css").read_text(encoding="utf-8")
    js = (COMP / "longform.js").read_text(encoding="utf-8")
    assert ".lf-word { display: inline-block; margin-right:" in css
    assert ".lf-callout .tx span { display: inline-block; margin-right:" in css
    assert 'wd + " "' not in js and 'w + " "' not in js


def test_phase_a_tat_dinh_va_khong_hien_som():
    js = (COMP / "longform.js").read_text(encoding="utf-8")
    assert "Math.random(" not in js, "render phải tất định: dùng HF.rng hạt giống"
    # hạt không khí: một tween tiến trình, không đặt tween ở thời điểm âm
    assert "tl.to(clock, { t: DUR" in js and "-phase)" not in js
    # chùm hạt thẻ chương + vệt sáng: set+to, không fromTo (fromTo vẽ trạng thái đầu từ giây 0)
    assert 'tl.set(ps, { x: 0, y: 0, opacity: 1' in js and 'tl.set(leak,' in js
    # đo vị trí nét vẽ tay lúc DỰNG (trước tween), không lúc chạy
    assert "measure(inner, ln)" in js


def test_phase_a_dang_ky_trong_bridge_va_engine():
    ns = _bridge("VISUAL_TYPES", "MEDIA_LAYOUTS", "LAYOUT_POOL")
    assert "quote" in ns["VISUAL_TYPES"] and "pinned" in ns["MEDIA_LAYOUTS"] and "pinned" in ns["LAYOUT_POOL"]
    assert "LONG.ambient(" in (COMP / "engine.js").read_text(encoding="utf-8")


def test_trich_dan_khong_dung_class_chu_phu_de_va_khong_do_toa_do():
    # .w là chữ phụ đề trong base.css (trắng, gạch chân) -> chữ trích dẫn trên
    # trang giấy ra màu trắng, gần như không đọc được.
    js = (COMP / "longform.js").read_text(encoding="utf-8")
    assert 'el("span", "w"' not in js and '"qw"' in js
    # đo toạ độ lúc dựng lệch khi font nạp xong sau -> nét vẽ/dạ quang phải là phần tử con
    assert "getBoundingClientRect" not in js
