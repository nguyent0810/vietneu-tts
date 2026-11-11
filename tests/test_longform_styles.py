"""Bộ style bổ sung (#258): longform_styles.js / .css chỉ THÊM cảnh mới, opt-in, tất định.

Kiểm tĩnh (luôn chạy): danh sách type khớp giữa JS, bridge và skill; không Math.random/Date; mọi fromTo
có immediateRender:false; không bộ chọn nào (pick/variantOf/LAYOUT_POOL) nhắc tới style mới; luật trần và
liền nhau của bridge + hf_batch_render.
Kiểm render (chỉ khi HF_STYLE_RENDER=1, cần node 22 + hyperframes): cùng mốc chụp hai lần ra md5 giống nhau.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "hyperframes_short" / "compositions"
JS = (COMP / "longform_styles.js").read_text(encoding="utf-8")
CSS = (COMP / "longform_styles.css").read_text(encoding="utf-8")
LONGFORM = (COMP / "longform.js").read_text(encoding="utf-8")
SKILL = (ROOT / ".claude" / "skills" / "motion-library" / "SKILL.md").read_text(encoding="utf-8")
STYLES = ("woodcut", "papercut", "oneline", "film16", "blueprint", "pencil")
LONG_HTML = ("laban_long", "inkwash_long", "lacquer_long", "moon_long", "dongho_long", "ember_long", "studio_long")

sys.path.insert(0, str(ROOT))
import hyperframes_bridge as HB  # noqa: E402
import hf_batch_render as HBR  # noqa: E402


def test_danh_sach_type_khop_ba_noi():
    registered = re.findall(r'register\("([a-z0-9]+)"', JS)
    assert tuple(registered) == STYLES
    assert HB.STYLE_VISUAL_TYPES == STYLES
    assert set(STYLES) <= set(HB.VISUAL_TYPES)
    frozen = re.search(r"HF_LONG_STYLES = Object\.freeze\(\[(.+?)\]\)", JS)
    assert frozen and tuple(re.findall(r'"([a-z0-9]+)"', frozen.group(1))) == STYLES
    for s in STYLES:
        assert f"`{s}`" in SKILL, f"skill motion-library thiếu mục {s}"


def test_khong_de_len_canh_cu():
    # Tên mới không trùng cảnh nào của longform.js; register() từ chối ghi đè.
    old = set(re.findall(r"^\s*visuals\.([a-z0-9]+)\s*=", LONGFORM, re.M))
    assert not (old & set(STYLES))
    assert "if (!VIS[name]) VIS[name] = withCamera(def)" in JS
    # Không sửa longform.js để nạp style: module được nạp bằng thẻ script riêng trong HTML style dài.
    assert "longform_styles" not in LONGFORM


def test_opt_in_khong_co_duong_tu_dong():
    # Bộ chọn biến thể / bố cục của kho không biết tới style mới -> không thể tự chèn.
    for s in STYLES:
        assert s not in LONGFORM, f"longform.js nhắc tới {s}"
    code = re.sub(r"//.*", "", re.sub(r"/\*.*?\*/", "", JS, flags=re.S))   # bỏ chú thích
    assert "pick(" not in code  # không gọi bộ chọn luân phiên
    assert "LAYOUT_POOL" not in code and "variantOf" not in code
    for name in LONG_HTML:
        src = (COMP / f"{name}.html").read_text(encoding="utf-8")
        assert src.count('<script src="./longform_styles.js"></script>') == 1, name
        assert src.count('href="./longform_styles.css"') == 1, name
        assert src.index("longform.js") < src.index("longform_styles.js"), f"{name}: style phải nạp SAU longform.js"


def test_tat_dinh_tinh():
    code = re.sub(r"//.*", "", re.sub(r"/\*.*?\*/", "", JS, flags=re.S))   # bỏ chú thích
    for bad in ("Math.random", "Date.now", "new Date", "performance.now", "setTimeout", "setInterval", "requestAnimationFrame"):
        assert bad not in code, bad
    assert "HF.rng(HF.hashSeed(" in JS
    # fromTo nào cũng immediateRender:false -> không hiện sớm từ giây 0 (bẫy motion-scene-dev).
    for m in re.finditer(r"tl\.fromTo\((.+)", JS):
        assert "immediateRender: false" in m.group(1), m.group(0)[:120]
    # Không ease nảy (SPEC chống mùi AI).
    assert not re.findall(r'"(?:back|bounce|elastic)\.', JS)
    # CSS không transition/animation (mọi chuyển động phải trên timeline).
    assert "transition:" not in CSS and "animation:" not in CSS and "@keyframes" not in CSS


def test_luat_tran_va_lien_nhau_bridge():
    ok = [(2, 2, "woodcut"), (5, 6, "papercut"), (9, 9, "pencil")]
    assert HB.style_scene_issues(ok) == []
    assert any("> 3" in s for s in HB.style_scene_issues(ok + [(12, 12, "film16")]))
    adj = HB.style_scene_issues([(2, 3, "woodcut"), (4, 4, "oneline")])
    assert adj and "liền nhau" in adj[0]
    assert HB.style_scene_issues([]) == []
    # apply_visuals chặn: hai style liền nhau trong một lần render
    lines = [{"sentence_id": i + 1, "start": i * 3.0, "end": i * 3.0 + 2.5, "words": []} for i in range(6)]
    with pytest.raises(HB.HyperFramesError, match="liền nhau"):
        HB.apply_visuals(lines, {"2": {"type": "woodcut"}, "3": {"type": "pencil"}}, {})
    # cách một câu thường thì được
    lines = [{"sentence_id": i + 1, "start": i * 3.0, "end": i * 3.0 + 2.5, "words": []} for i in range(6)]
    HB.apply_visuals(lines, {"2": {"type": "woodcut"}, "4": {"type": "pencil"}}, {})
    assert lines[1]["visual"]["type"] == "woodcut" and lines[3]["visual"]["type"] == "pencil"


def _lines(n):
    return [{"sentence_id": i + 1, "start": i * 3.0, "end": i * 3.0 + 2.5, "words": []} for i in range(n)]


def test_until_gop_du_bon_danh_sach():
    # oneline có items ở câu 3–5 -> chiếm 3..5: visual_cont = 3 ở câu 4, 5; until = 5.
    spec = {"type": "oneline", "items": [{"motif": "lotus", "at": 3}, {"motif": "mountain", "at": 4}, {"motif": "enso", "at": 5}]}
    assert HB.style_until(3, spec) == 5
    lines = _lines(7)
    HB.apply_visuals(lines, {"3": spec}, {})
    assert lines[2]["visual"]["type"] == "oneline" and lines[3]["visual_cont"] == 3 and lines[4]["visual_cont"] == 3
    assert "visual_cont" not in lines[5]
    # pencil có cả steps (câu 2) lẫn notes (câu 4): until = 4 (không đoản mạch ở steps)
    pen = {"type": "pencil", "scene": "gate", "steps": [{"at": 2}], "notes": [{"text": "x", "x": 1, "y": 1, "at": 4}]}
    assert HB.style_until(2, pen) == 4 and HB.style_ats(pen) == [2, 4]
    assert HB.style_until(2, {"type": "blueprint", "bars": [{"label": "a", "value": 1, "at": 6}]}) == 6


def test_canh_style_keo_dai_roi_canh_style_ngay_sau_bi_chan():
    # style câu 2 kéo tới câu 4 (items), style khác ở câu 5 -> liền nhau -> chặn (cả bridge lẫn hf_batch_render)
    vis = {"2": {"type": "oneline", "items": [{"motif": "lotus", "at": 2}, {"motif": "enso", "at": 4}]}, "5": {"type": "woodcut", "text": "x"}}
    with pytest.raises(HB.HyperFramesError, match="liền nhau"):
        HB.apply_visuals(_lines(8), vis, {})
    bad = HBR.style_scene_issues({"lane": "long", "visuals": vis})
    assert bad and "liền nhau" in bad[0]
    # pencil steps câu 2 + notes câu 4, film16 câu 5 -> cũng liền nhau
    vis2 = {"2": {"type": "pencil", "steps": [{"at": 2}], "notes": [{"text": "x", "x": 1, "y": 1, "at": 4}]}, "5": {"type": "film16", "title": "x"}}
    assert any("liền nhau" in s for s in HBR.style_scene_issues({"lane": "long", "visuals": vis2}))
    # cách một câu thì được
    vis3 = {"2": {"type": "oneline", "items": [{"motif": "lotus", "at": 2}, {"motif": "enso", "at": 4}]}, "6": {"type": "woodcut", "text": "x"}}
    HB.apply_visuals(_lines(8), vis3, {})
    assert HBR.style_scene_issues({"lane": "long", "visuals": vis3}) == []


def test_bon_canh_style_mot_lan_render_bi_chan():
    vis = {"2": {"type": "woodcut"}, "4": {"type": "pencil", "scene": "gate"}, "6": {"type": "film16"}, "8": {"type": "blueprint"}}
    with pytest.raises(HB.HyperFramesError, match="> 3"):
        HB.apply_visuals(_lines(10), vis, {})
    with pytest.raises(HB.HyperFramesError, match="> 3"):
        HB.apply_visuals(_lines(10), {**vis, "4": {"type": "quote"}, "9": {"type": "oneline"}}, {})  # vẫn 4 style


def test_cong_ca_video_hf_batch_render():
    row = {"lane": "long", "visuals": {"2": {"type": "woodcut"}, "10": {"type": "quote"}, "20": {"type": "pencil"}}}
    assert HBR.style_scene_issues(row) == []
    row["visuals"].update({"30": {"type": "film16"}, "40": {"type": "oneline"}})
    assert any("> 3" in s for s in HBR.style_scene_issues(row))
    assert HBR.style_scene_issues({"lane": "long", "visuals": {"3": {"type": "wheel"}}}) == []


def test_plan_cu_khong_doi_hop_dong_bridge():
    # Mọi type cũ vẫn trong VISUAL_TYPES (chỉ thêm, không bớt); bố cục ảnh giữ nguyên.
    old = ("wheel", "elements", "years", "list", "timeline", "compare", "stat", "quote", "map", "word", "illus", "endcard",
           "doc", "photo", "clock", "ask", "shadow", "hexagram", "luoshu", "ledger", "breath", "museum", "napam", "cuudieu",
           "eclipse", "lookup", "annot", "relic", "chiwheel", "pie", "compass", "teaser", "clues", "stamp", "scroll", "dialog",
           "wind", "bagua", "studio", "region", "profile")
    assert HB.VISUAL_TYPES[:len(old)] == old
    assert HB.MEDIA_LAYOUTS == ("full", "card3d", "split", "split_r", "polaroid", "pinned", "depth")
    # Khung mẫu của hf_style_demo tuân luật (3 style/cuộn, xen câu thường).
    import hf_style_demo
    for reel, R in hf_style_demo.REELS.items():
        spans = [(int(k), int(k), v["type"]) for k, v in R["visuals"].items()]
        assert HB.style_scene_issues(spans) == [], reel


def test_chu_tieng_viet_font_co_dau():
    # Font nhập trong CSS đều có bộ tiếng Việt (OFL): Anton, Yeseva One, Cormorant, Dancing Script, Itim, IBM Plex Mono.
    for f in ("Anton", "Yeseva+One", "Cormorant:", "Dancing+Script", "Itim", "IBM+Plex+Mono"):
        assert f in CSS, f
    for bad in ("Caveat", "Special+Elite", "Courier+Prime", "Bangers"):
        assert bad not in CSS, f"{bad} thiếu dấu tiếng Việt"
    # KHÔNG khai báo lại họ font kho đã nạp (longform.css, style HTML, WORDTS_FONTS): @font-face kép làm lệch raster
    # chữ của cảnh cũ (10/11: kicker JetBrains Mono lệch 0,1% điểm ảnh khi so khung với main).
    for dup in ("Oswald", "Playfair", "Charm", "Patrick", "JetBrains", "Cormorant+Garamond", "Lora", "Be+Vietnam", "League", "Fraunces"):
        assert dup not in CSS.split("\n")[0], f"{dup} đã được kho nạp, không nhập lại"


def test_khong_tl_to_tren_dom_va_neo_tai_t0():
    # Mọi tl.to chỉ trên proxy (boil/clock/prog); DOM dùng fromTo + immediateRender:false. Proxy có tl.set tại t0.
    for m in re.finditer(r"tl\.to\((\w+)", JS):
        assert m.group(1) in ("boil", "clock", "prog"), m.group(0)
    assert "tl.set(boil, { k: 0, onUpdate: applyBoil }, t0)" in JS
    assert "tl.set(clock, { t: 0, onUpdate: paint }, t0)" in JS
    assert "tl.set(prog, { L: 0, onUpdate: apply }, t0)" in JS
    assert not re.search(r"tl\.set\([^)]*\),\s*0\)", JS), "không neo tl.set ở giây 0 toàn cục"


@pytest.mark.skipif(not os.environ.get("HF_STYLE_RENDER"), reason="đặt HF_STYLE_RENDER=1 (cần Chrome + playwright, ~1-2 phút)")
def test_tat_dinh_seek_khong_theo_thu_tu(tmp_path):
    res = subprocess.run([sys.executable, str(ROOT / "hf_style_demo.py"), "seekorder", "--out", str(tmp_path)],
                         capture_output=True, text=True, cwd=ROOT, timeout=900)
    assert res.returncode == 0, res.stdout[-1500:] + res.stderr[-1500:]
    assert "SEEK KHÔNG THỨ TỰ: ĐẠT" in res.stdout


@pytest.mark.skipif(not os.environ.get("HF_STYLE_RENDER"), reason="đặt HF_STYLE_RENDER=1 (cần node 22 + hyperframes, ~2-4 phút)")
def test_tat_dinh_render_hai_lan_giong_nhau(tmp_path):
    res = subprocess.run([sys.executable, str(ROOT / "hf_style_demo.py"), "determinism", "--out", str(tmp_path)],
                         capture_output=True, text=True, cwd=ROOT, timeout=1500)
    assert res.returncode == 0, res.stdout[-1500:] + res.stderr[-1500:]
    assert "TẤT ĐỊNH: ĐẠT" in res.stdout
