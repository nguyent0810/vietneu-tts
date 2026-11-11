"""Ticket 035: gợi ý style #258 vào plan Long mới, không đụng plan cũ, không vượt trần."""
import importlib.util
import json
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
import hf_batch_render as HBR  # noqa: E402
import hf_style_suggest as HSS  # noqa: E402
import hyperframes_bridge as HB  # noqa: E402

STYLES = ("woodcut", "papercut", "oneline", "film16", "blueprint", "pencil")
PLANS = (
    ROOT / "output" / "cl_staging" / "long" / "plan_P4_thanglong.json",
    ROOT / "output" / "cl_staging" / "long" / "plan_P5_12canhcua.json",
)


def _line(i: int) -> str:
    base = " ".join(f"w{i}x{k}" for k in range(8))
    if i == 24:
        return f"** {base} **"
    if i == 36:
        return base + " mặt bằng thành"
    if i == 48:
        return base + " năm 1631"
    if i == 60:
        return base + " bia tư liệu toàn thư"
    return base


def _row(**kw) -> dict:
    row = {
        "id": "L_test_style",
        "series": "fs",
        "lane": "long",
        "script": [_line(i) for i in range(80)],
    }
    row.update(kw)
    return row


def _issues(props):
    return HB.style_scene_issues([(p["sid"], p["sid"], p["type"]) for p in props])


def test_goi_y_tat_dinh_dung_tran_dung_kenh():
    row = _row()
    a = HSS.suggest(row)
    b = HSS.suggest(row)
    assert a == b
    assert 1 <= len(a) <= 3
    assert _issues(a) == []
    allowed = set(HSS.CHANNEL_STYLES["fs"])
    for p in a:
        assert p["start"] >= HSS.OPENING_S
        assert p["type"] in allowed
        assert p["spec"]["type"] == p["type"]
        assert p["spec"]["suggested"] is True
    assert [p["type"] for p in a] == ["woodcut", "blueprint", "woodcut"]
    assert [p["why"] for p in a] == ["thẻ chương", "mặt bằng", "số liệu"]
    assert json.dumps(row, ensure_ascii=False) == json.dumps(_row(), ensure_ascii=False)


@pytest.mark.parametrize("series,channel", [
    ("bud", "bud"), ("phat", "bud"), ("fs", "fs"), ("phong_thuy", "fs"),
    ("vsd", "vsd"), ("Văn Sử Địa", "vsd"), ("cl", "cl"), ("Hình Sự", "cl"),
])
def test_kenh_va_bang_style(series, channel):
    props = HSS.suggest(_row(series=series))
    assert props
    allowed = set(HSS.CHANNEL_STYLES[channel])
    assert {p["type"] for p in props} <= allowed
    if channel == "bud":
        wood = next(p for p in props if p["type"] == "woodcut")
        assert wood["spec"]["tone"] == "paper"
        assert wood["spec"]["motif"] == "lotus"
    if channel == "fs":
        assert props[0]["spec"]["tone"] == "dark"


def test_khong_de_visual_cu_khong_lien_khong_vuot_tran():
    row = _row(visuals={
        "25": {"type": "woodcut", "text": "Có sẵn", "motif": "gate", "tone": "dark"},
        "37": {"type": "blueprint", "scene": "wall", "title": "Có sẵn"},
        "49": {"type": "papercut", "scene": "citadel", "text": "Có sẵn"},
    })
    assert HSS.suggest(row) == []
    assert HSS.apply_suggestions(row, adopt=True) == []

    one = _row(visuals={"25": {"type": "quote", "source": "x"}})
    before_keys = set(one["visuals"])
    added = HSS.apply_suggestions(one, adopt=True)
    assert 25 not in added
    assert one["visuals"]["25"]["type"] == "quote"
    assert before_keys <= set(one["visuals"])
    assert _issues([{"sid": int(k), "type": v["type"]} for k, v in one["visuals"].items() if v["type"] in STYLES]) == []


def test_apply_khong_sua_khi_khong_adopt_hoac_khong_phai_long():
    for row in (
        _row(),
        _row(legacy=True),
        _row(style_suggest=False),
        _row(lane="niem", style="laban"),
    ):
        snap = deepcopy(row)
        assert HSS.apply_suggestions(row, adopt=False) == []
        assert row == snap
    legacy = _row(legacy=True)
    assert HSS.apply_suggestions(legacy, adopt=True) == []
    assert "visuals" not in legacy
    opted = _row(style_suggest=False)
    assert HSS.suggest(opted) == []


def test_canh_bao_nhe_khong_chan():
    bare = _row()
    line = HSS.warning_line(bare)
    assert line and "CẢNH BÁO style" in line and "không chặn" in line and "câu 25 woodcut" in line
    styled = _row(visuals={"25": {"type": "woodcut", "motif": "gate"}})
    assert HSS.warning_line(styled) is None
    assert HSS.warning_line(_row(lane="short")) is None
    assert HSS.warning_line(_row(style_suggest=False)) is None
    assert HSS.warning_line(_row(series="mim")) is None


def test_save_plan_rows_chi_long_moi(tmp_path):
    plan = tmp_path / "plan.json"
    old = _row(id="L_cu", visuals={"3": {"type": "quote"}})
    plan.write_text(json.dumps([old], ensure_ascii=False), encoding="utf-8")
    again = _row(id="L_cu", visuals={})
    HBR.save_plan_rows(plan, again)
    saved_old = next(r for r in json.loads(plan.read_text(encoding="utf-8")) if r["id"] == "L_cu")
    assert saved_old["visuals"] == {}

    HBR.save_plan_rows(plan, _row(id="L_moi"))
    new = next(r for r in json.loads(plan.read_text(encoding="utf-8")) if r["id"] == "L_moi")
    types = [v["type"] for v in new["visuals"].values()]
    assert types == ["woodcut", "blueprint", "woodcut"]
    assert all(v.get("suggested") is True for v in new["visuals"].values())

    HBR.save_plan_rows(plan, {"id": "L_short_moi", "series": "fs", "script": ["Một câu ngắn."]})
    short = next(r for r in json.loads(plan.read_text(encoding="utf-8")) if r["id"] == "L_short_moi")
    assert "visuals" not in short or not any(
        isinstance(v, dict) and v.get("type") in STYLES for v in (short.get("visuals") or {}).values())


def test_warn_missing_style_khong_ghi(tmp_path, capsys):
    row = _row()
    HBR.warn_missing_style(row, tmp_path)
    err = capsys.readouterr().out
    assert "CẢNH BÁO style" in err
    (tmp_path / f"{row['id']}.mp4").write_bytes(b"x")
    HBR.warn_missing_style(row, tmp_path)
    assert capsys.readouterr().out == ""
    assert row.get("visuals") in (None, {})


def test_warn_missing_style_style_long_khong_can_lane(tmp_path, capsys):
    """Long nhận diện bằng style kết thúc `_long`, cùng luật với is_long_row."""
    row = _row(style="laban_long")
    row.pop("lane")
    HBR.warn_missing_style(row, tmp_path)
    assert "CẢNH BÁO style" in capsys.readouterr().out
    quiet = _row(style="laban")
    quiet.pop("lane")
    HBR.warn_missing_style(quiet, tmp_path)
    assert capsys.readouterr().out == ""


def test_html_for_giu_byte_khi_khong_style():
    path = ROOT / "creator_v2" / "motion" / "long" / "build_long.py"
    spec = importlib.util.spec_from_file_location("build_long_035", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.html_for() == mod.HTML
    assert mod.html_for(False) == mod.HTML
    styled = mod.html_for(True)
    assert styled.index("longform_styles.js") < styled.index("casewide.js")
    assert "longform_styles_boot.js" in styled
    assert "assets/engine/hf_styles.js" in styled
    assert "compositions/longform_styles.css" in styled


def test_style_files_khop_va_casewide_noi():
    src = ROOT / "hyperframes_short" / "compositions"
    dst = ROOT / "creator_v2" / "motion" / "hf" / "compositions"
    for name in ("longform_styles.js", "longform_styles.css"):
        assert (dst / name).read_bytes() == (src / name).read_bytes()
    casewide = (ROOT / "creator_v2/motion/hf/assets/engine/casewide.js").read_text(encoding="utf-8")
    adapter = (ROOT / "creator_v2/motion/hf/assets/engine/hf_styles.js").read_text(encoding="utf-8")
    assert "hfStyleScenes" not in casewide
    assert "window.chartScenes" in casewide
    for name in STYLES:
        assert name in adapter
    for html_name in ("laban_long.html", "inkwash_long.html"):
        html = (dst / html_name).read_text(encoding="utf-8")
        assert html.index("longform.js") < html.index("longform_styles.js")
        assert 'href="./longform_styles.css"' in html
    skill_v = (ROOT / ".claude/skills/long-video/SKILL.md").read_text(encoding="utf-8")
    skill_s = (ROOT / ".claude/skills/long-script/SKILL.md").read_text(encoding="utf-8")
    assert "hf_style_suggest.py" in skill_v and '"type": "woodcut"' in skill_v
    assert "style_suggest" in skill_s and "motion-library" in skill_s


def test_duong_dan_plan_tu_goc_repo():
    assert tuple(p.relative_to(ROOT).as_posix() for p in PLANS) == (
        "output/cl_staging/long/plan_P4_thanglong.json",
        "output/cl_staging/long/plan_P5_12canhcua.json",
    )


_HOOK_PROBE = r"""
const fs = require("fs");
const path = process.argv[2];
global.window = global;
let chartCalls = 0;
window.chartScenes = (ctx) => { chartCalls += 1; ctx.B._chart = chartCalls; };
eval(fs.readFileSync(path, "utf8"));
const B = {};
window.chartScenes({ B, tl: {}, el() { return { style: {} }; }, C: { lines: [] } });
if (chartCalls !== 1 || B._chart !== 1) process.exit(2);
const names = ["woodcut", "papercut", "oneline", "film16", "blueprint", "pencil"];
for (const n of names) if (typeof B[n] !== "function") process.exit(3);
let msg = "";
try { B.woodcut({ t0: 0, t1: 1, words: [] }, {}); }
catch (e) { msg = String(e && e.message || e); }
if (!msg.includes("thiếu HF_LONG.visuals.woodcut")) process.exit(4);
process.stdout.write("OK");
"""


def test_style_hook_qua_chartScenes_khong_sua_casewide(tmp_path):
    """casewide đã gọi chartScenes. Adapter bọc hook đó, không thêm dòng vào casewide."""
    casewide = (ROOT / "creator_v2/motion/hf/assets/engine/casewide.js").read_text(encoding="utf-8")
    assert "hfStyleScenes" not in casewide
    adapter = ROOT / "creator_v2/motion/hf/assets/engine/hf_styles.js"
    assert adapter.is_file()
    probe = tmp_path / "hook_probe.js"
    probe.write_text(_HOOK_PROBE, encoding="utf-8")
    ran = subprocess.run(
        ["node", str(probe), str(adapter)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert ran.stdout.strip() == "OK"


def test_dry_run_plan_p4_p5_khong_doi_byte(tmp_path, capsys):
    missing = [p for p in PLANS if not p.is_file()]
    if missing:
        pytest.skip("thiếu " + ", ".join(p.name for p in missing))
    before = {p: p.read_bytes() for p in PLANS}
    copies = []
    for p in PLANS:
        dest = tmp_path / p.name
        shutil.copy2(p, dest)
        copies.append(dest)
        rc = HSS.main([str(dest), "--dry-run"])
        assert rc == 0
    out = capsys.readouterr().out
    assert out.count("file gốc không đổi") == len(copies)
    assert "file gốc ĐÃ ĐỔI" not in out
    for p, raw in before.items():
        assert p.read_bytes() == raw
    for dest in copies:
        assert dest.read_bytes() == before[next(p for p in PLANS if p.name == dest.name)]


def test_style_text_khong_escape_hai_lan():
    js = (ROOT / "creator_v2/motion/hf/compositions/longform_styles.js").read_text(encoding="utf-8")
    assert "&amp;" not in js.split("const esc", 1)[1].split("\n", 1)[0]


def test_ke_nhau_tinh_span_that_cua_style_da_chon():
    import hf_style_suggest as HSS
    # style đã chọn ở câu 5 kéo tới câu 9 -> câu 10 kề, câu 12 không kề
    spans = [(5, 9, "x")]
    assert HSS._adjacent(10, spans)
    assert not HSS._adjacent(12, spans)
