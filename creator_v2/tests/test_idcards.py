import copy
import json
from pathlib import Path
import subprocess

from motion.long import idcards, floor


def chapters(n=300, positions=range(0, 150, 5)):
    selected = set(positions)
    return [("ch00", {"scenes": [{"type": "file", "name": "A", "img": "portrait"} if i in selected else {"type": "photo"} for i in range(n)]})]


def test_determinism_spacing_and_distribution():
    a = chapters(); b = copy.deepcopy(a)
    spec = {"idcards": True, "channel": "CL", "era": 1910}
    counts = idcards.assign("topic", spec, a)
    assert counts == idcards.assign("topic", spec, b)
    assert a == b and len(counts) >= 8
    assert max(counts.values()) / 300 <= .04
    assert idcards.problems(a) == []


def test_legacy_and_manual():
    a = chapters(30, [0, 10]); before = copy.deepcopy(a)
    assert not idcards.assign("legacy", {}, a) and a == before
    a[0][1]["scenes"][0]["style"] = "passport"
    idcards.assign("new", {"idcards": True}, a)
    assert a[0][1]["scenes"][0]["style"] == "passport"


def test_context_and_conviction():
    assert "telegram" in idcards.candidates({"channel": "CL", "era": 1910}, {})
    assert "telegram" not in idcards.candidates({"channel": "CL", "era": 1700}, {})
    assert "terminal" in idcards.candidates({"channel": "MIM"}, {"hint": "tech"})
    assert "edict_scroll" in idcards.candidates({"channel": "CL", "era": "ancient China"}, {})
    assert "edict_scroll" not in idcards.candidates({"channel": "CL", "era": 1700}, {})
    assert "verdict" not in idcards.candidates({"channel": "CL"}, {})
    assert "verdict" in idcards.candidates({"channel": "CL"}, {"convicted": True, "conviction_source": "https://example.org/case"})


def test_floor_catches_spacing_share_and_unsafe_manual_style():
    a = chapters(20, [0, 1, 2]); a[0][1]["scenes"][0].update(style="verdict")
    idcards.assign("new", {"idcards": True}, a)
    result = idcards.problems(a)
    assert any("12%" in x for x in result)
    assert any("4%" in x for x in result)
    assert any("cách 4 cảnh" in x for x in result)
    assert any("bằng chứng" in x for x in result)
    assert all(x in floor.problems(a, "CL", None, True) for x in result)


def test_mata_hari_copy_if_available():
    path = Path("data/long/mata-hari")
    if not path.exists():
        import pytest
        pytest.skip("No local Mata Hari data")
    spec = json.loads((path / "spec.json").read_text(encoding="utf-8"))
    spec["idcards"] = True
    source = [(p.stem, json.loads(p.read_text(encoding="utf-8"))) for p in sorted(path.glob("ch*.json"))]
    a = copy.deepcopy(source)
    counts = idcards.assign("mata-hari", spec, a)
    cards = [s for _, ch in a for s in ch["scenes"] if s["type"] == "file"]
    assert sum(counts.values()) == 31 and len(counts) >= 8
    assert max(counts.values()) / len(cards) <= .25
    assert not any("l\u1eb7p trong 6" in x for x in idcards.problems(a))
    assert sum(bool(s.get("img_borrowed")) for s in cards) > 0
    assert source != a


def test_image_styles_require_scene_image():
    for channel in ("CL", "MIM", "CK"):
        spec = {"channel": channel, "era": 1910}
        assert not (set(idcards.candidates(spec, {})) & idcards.IMAGE_STYLES)
        assert "lower_third" in idcards.candidates(spec, {"img": "portrait"})
    a = chapters(20, [0])
    a[0][1]["scenes"][0] = {"type": "file", "style": "polaroid"}
    assert any("cần img" in p for p in idcards.problems(a))


def test_vietnamese_title_css_and_fonts():
    import re
    from motion.long.lint_html import KIN_FONTS
    css = Path("motion/hf/assets/engine/casewide.css").read_text(encoding="utf-8")
    for selector in (".id-name", ".id2-title", ".id2-news .id2-title", ".id2-receipt .id2-title", ".id2-museum-label .id2-title"):
        match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
        assert match, selector
        declarations = match.group(1)
        height = re.search(r"(?:line-height:\s*|\d+px/)([\d.]+)", declarations)
        assert height and float(height.group(1)) >= 1.2, selector
    assert not ({"Comic Sans MS", "Courier New"} & KIN_FONTS.keys())


def test_eight_layouts_and_row_cues():
    source = Path("motion/hf/assets/engine/casewide.js").resolve()
    script = r"""
const fs = require('fs'), vm = require('vm');
const nodes = [], calls = [];
const node = (tag='div') => { const n = {tag, attrs:{}, style:{setProperty(){}}, classList:{add(){}}, children:[], appendChild(c){this.children.push(c)}, setAttribute(k,v){this.attrs[k]=v}, getTotalLength(){return 100}}; nodes.push(n); return n; };
const root=node(), stage=node();
const doc = {createElement:node, createElementNS:(_, tag)=>node(tag), getElementById:()=>root, querySelector:()=>stage, documentElement:node()};
const timeline = {set(...a){calls.push(['set',...a]);return this},to(...a){calls.push(['to',...a]);return this},fromTo(...a){calls.push(['fromTo',...a]);return this}};
const scene = process.argv[2];
const sandbox = {document:doc, window:{CASE:{dur:6, imgs:{p:{src:'image.jpg', w:1920, h:1080}}, scenes:[{type:'file',style:scene,t0:0,t1:6,img:'p',focus:[.25,.5],name:'CÂU CHUYỆN MẪU',date:'1910',desc:'Vai trò',rows:[{k:'TỔNG',v:'100',at:2.5}]}], hud:{}, lines:[]}}, gsap:{timeline:()=>timeline}, makeBeat:()=>({}), getComputedStyle:()=>({color:'#fff'}), console};
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), sandbox);
const classes = nodes.map(n=>n.className || '');
const cue = calls.some(c=>c[0]==='fromTo' && c[c.length-1]===2.5);
const circle = nodes.find(n=>n.tag==='circle');
console.log(JSON.stringify({classes,cue,circle:circle && circle.attrs, graphic:nodes.filter(n=>n.innerHTML==='ĐỒ HỌA').length, images:nodes.filter(n=>n.tag==='img').map(n=>n.className)}));
"""
    expected = {"lower_third": "id2-lower", "callout": "id2-callout-label", "news_clip": "id2-news",
                "telegram": "id2-telegram-strip", "polaroid": "id2-polaroid", "edict_scroll": "id2-scroll-sheet",
                "receipt": "id2-receipt", "museum_label": "id2-museum-label",
                "index_card": "id3-index", "fingerprint": "id3-fingerprint", "passport": "id3-passport",
                "verdict": "id3-verdict", "wanted": "id3-wanted", "envelope": "id3-envelope",
                "seal_slip": "id3-bamboo", "case_divider": "id3-divider", "terminal": "id3-terminal",
                "spec_sheet": "id3-blueprint", "app_card": "id3-phone", "slate": "id3-slate"}
    for style, marker in expected.items():
        result = subprocess.run(["node", "-e", script, str(source), style], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        assert marker in data["classes"], style
        assert data["graphic"] == (1 if style in {"news_clip", "telegram", "edict_scroll", "fingerprint", "passport", "verdict", "wanted", "envelope", "seal_slip"} else 0)
        if style in {"news_clip", "telegram", "edict_scroll", "receipt", "museum_label"}:
            assert data["cue"], style
        if style == "callout":
            assert float(data["circle"]["cx"]) == 480 and float(data["circle"]["cy"]) == 540
        if style == "receipt":
            assert "id2-receipt-row total" in data["classes"]
        if style in idcards.IMAGE_STYLES:
            assert data["images"], style


def test_js_handles_optional_fields():
    source = Path("motion/hf/assets/engine/casewide.js").resolve()
    script = r"""
const fs = require('fs'), vm = require('vm');
const node = () => ({style: {setProperty(){}}, classList: {add(){}}, appendChild(){}, setAttribute(){}, getTotalLength(){return 100;}});
const doc = {createElement: node, createElementNS: node, getElementById: node, querySelector: node, documentElement: node()};
const timeline = {set(){return this}, to(){return this}, fromTo(){return this}};
const scene = process.argv[2];
const sandbox = {document:doc, window:{CASE:{dur:5, imgs:{}, scenes:[{type:'file',style:scene,t0:0,t1:5}], hud:{}, lines:[]}}, gsap:{timeline:()=>timeline}, makeBeat:()=>({}), getComputedStyle:()=>({color:'#fff'}), console};
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), sandbox);
"""
    for style in idcards.STYLES:
        result = subprocess.run(["node", "-e", script, str(source), style], capture_output=True, text=True)
        assert result.returncode == 0, (style, result.stderr)


def test_borrow_nearest_declared_image_and_chapter_boundary():
    spec = {"idcards": True, "imgs": {"old": "File:old.jpg", "new": "File:new.jpg", "ai": "EXT:ai:1", "film": "File:film promo.jpg"}}
    data = [("one", {"scenes": [{"type": "photo", "img": "old"}, {"type": "split", "a": {"img": "old"}, "b": {"img": "new"}}, {"type": "photo", "img": "ai"}, {"type": "photo", "img": "film"}, {"type": "file", "style": "polaroid"}]}), ("two", {"scenes": [{"type": "file", "style": "callout"}]})]
    idcards.assign("topic", spec, data)
    assert data[0][1]["scenes"][-1]["img"] == "new"
    assert data[0][1]["scenes"][-1]["img_borrowed"] is True
    assert "img" not in data[1][1]["scenes"][0]


def test_all_idcard_text_font_declarations_have_line_height():
    import re
    css = Path("motion/hf/assets/engine/casewide.css").read_text(encoding="utf-8")
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if not re.search(r"\.id[23-]", selectors):
            continue
        for declaration in body.split(";"):
            if re.match(r"\s*font\s*:", declaration):
                value = declaration.split(":", 1)[1].strip()
                if value == "inherit":
                    continue
                match = re.search(r"\d+(?:\.\d+)?px/([\d.]+)", value)
                assert match and float(match.group(1)) >= 1.2, (selectors, value)


def test_twenty_demo_styles_and_fonts():
    demo = Path("motion/long/idcards_demo.py").read_text(encoding="utf-8")
    from motion.variety import fonts_url
    assert len(idcards.STYLES) == 21 and "slate" in idcards.STYLES
    assert "IBM+Plex+Mono" in fonts_url("classic") and "family=Itim" in fonts_url("classic")
    assert "IBM+Plex+Mono" in demo and "family=Itim" in demo
    assert "Nguy\u1ec5n Th\u1ecb Ng\u1ecdc \u1ea8n" in demo
