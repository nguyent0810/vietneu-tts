from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
import build as B


def test_preflight_warns_without_blocking(capsys):
    scene = {"type": "chart", "bars": [{"v": 1, "at": 0}], "note": "VÍ DỤ GIẢ ĐỊNH"}  # #270: chart cần bars
    spec = {"lines": ["lời kể " * 30], "theme": "ck", "scenes": [scene]}
    assert B.spec_preflight_errors("sample", spec) == []
    assert "cảnh 0 (chart)" in capsys.readouterr().out
    scene["hypo"] = True
    assert B.spec_preflight_errors("sample", spec) == []
    assert "CẢNH BÁO" not in capsys.readouterr().out


def test_css_uses_subtitle_size():
    css = (ROOT / "motion/hf/assets/engine/casefile.css").read_text(encoding="utf-8")
    assert re.search(r"\.cap\s*\{[^}]*font-size:\s*var\(--caption-size\)", css)
    assert re.search(r"\.hypo-label\s+\.hypo-title\s*\{[^}]*font-size:\s*var\(--caption-size\)", css)


def test_html_scene_labels_by_theme():
    # Run the real engine with a small DOM and a timeline stub; no video render.
    js = r"""
const fs = require("fs"), vm = require("vm");
const all = [];
function node() {
  const e = {style:{setProperty(k,v){this[k]=v}}, children:[], className:"", innerHTML:"", appendChild(c){this.children.push(c);},
             setAttribute(){}, querySelector(){return node();}, querySelectorAll(){return []}};
  all.push(e); return e;
}
const roots = {};
global.document = {createElement:node, createElementNS:node, documentElement:node(),
 querySelector(s){return roots[s] ||= node();}, getElementById(){return node();}};
const timeline = {set(){return this}, to(){return this}, fromTo(){return this}};
global.gsap = {timeline(){return timeline}, set(){}};
global.makeBeat = () => ({SLAM(){}, beat(){}});
global.window = {CASE:{dur:3,theme:JSON.parse(process.argv[2]),scenes:[
 {type:"kinetic",items:[],t0:0,t1:3,hypo:true,hypo_sub:"Minh hoạ"}],
 lines:[],imgs:{},kicker:"",acc:[]}};
vm.runInThisContext(fs.readFileSync(process.argv[1], "utf8"));
console.log(JSON.stringify(all.map(e=>({cls:e.className, html:e.innerHTML}))));
"""
    engine = str(ROOT / "motion/hf/assets/engine/casefile.js")
    for theme, cls in [({"cls": "theme-ck"}, "hypo-ribbon"),
                       ({"cls": "theme-mim"}, "hypo-bracket"),
                       ({}, "hypo-tape-wrap")]:
        result = subprocess.run(["node", "-e", js, engine, json.dumps(theme)],
                                check=True, capture_output=True, text=True, encoding="utf-8")
        nodes = json.loads(result.stdout)
        assert any(cls in n["cls"].split() for n in nodes)
        assert any(n["cls"] == "hypo-title" and n["html"] == "VÍ DỤ GIẢ ĐỊNH" for n in nodes)


def test_cards_layout_respects_label_and_subtitle():
    js = r"""
const fs = require("fs"), vm = require("vm"), all = [];
function node() {
  const e = {style:{setProperty(k,v){this[k]=v}}, children:[], className:"", innerHTML:"",
    appendChild(c){this.children.push(c)}, setAttribute(){}, querySelector(){return node()},
    querySelectorAll(){return this.children.filter(c => /^(c3t|c3 |bdnote)/.test(c.className))},
    get offsetTop(){return this.className.includes("hypo-label") ? 220 : parseFloat(this.style.top || 0)},
    get offsetHeight(){return this.className.includes("hypo-label") ? Number(process.argv[3]) :
      this.className === "c3t" ? 76 : parseFloat(this.style.height || 24)}};
  all.push(e); return e;
}
const roots = {};
global.document = {createElement:node, createElementNS:node, documentElement:node(),
 querySelector(s){return roots[s] ||= node()}, getElementById(){return node()}};
const timeline = {set(){return this}, to(){return this}, fromTo(){return this}};
global.gsap = {timeline(){return timeline}, set(){}};
global.makeBeat = () => ({SLAM(){}, beat(){}});
const scene = {type:"cards3d",title:"Title",cards:[{k:"A",v:"1",at:1},{k:"B",v:"2",at:2},{k:"C",v:"3",at:2}],t0:0,t1:3};
if (process.argv[2] === "yes") { scene.hypo = true; scene.hypo_sub = "Example"; }
global.window = {CASE:{dur:3,theme:{cls:"theme-ck"},scenes:[scene],lines:[],imgs:{},kicker:"",acc:[]}};
vm.runInThisContext(fs.readFileSync(process.argv[1], "utf8"));
const root = all.find(e => e.className.split(" ").includes("scene"));
console.log(JSON.stringify({cls:root.className, style:root.style, content:root.children.some(e=>e.className==="hypo-content")}));
"""
    engine = str(ROOT / "motion/hf/assets/engine/casefile.js")
    def run(hypo, height):
        result = subprocess.run(["node", "-e", js, engine, hypo, str(height)],
                                check=True, capture_output=True, text=True, encoding="utf-8")
        return json.loads(result.stdout)

    plain = run("no", 140)
    assert "has-hypo" not in plain["cls"].split()
    assert not plain["content"] and "--hypo-shift" not in plain["style"]
    for height in (140, 200):
        scene = run("yes", height)
        assert "has-hypo" in scene["cls"].split() and scene["content"]
        style = scene["style"]
        scale = float(style["--hypo-scale"])
        shift = float(style["--hypo-shift"].removesuffix("px"))
        assert style["--hypo-offset"] == f"{height}px"
        assert 304 * scale + shift >= 220 + height + 24
        assert (434 + 3 * 280 + 2 * 46 + 32) * scale + shift <= 1440.01


def test_hypo_font_weights_requested():
    source = (ROOT / "motion/stier/build.py").read_text(encoding="utf-8")
    assert "family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900" in source
    assert "family=JetBrains+Mono:wght@500;700;800" in source
