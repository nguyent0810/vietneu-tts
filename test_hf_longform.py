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
