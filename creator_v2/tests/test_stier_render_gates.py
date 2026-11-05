"""#145: lỗi JS lúc render, đứng hình, lead time. Mỗi cổng có test đơn vị + test tích hợp trên composition tổng hợp nhỏ (320x480)."""
import datetime
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
import build as B  # noqa: E402

FFMPEG = shutil.which("ffmpeg")
NPX = shutil.which("npx.cmd") or shutil.which("npx")


def _online() -> bool:
    try:
        urllib.request.urlopen("https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js", timeout=8).close()
        return True
    except OSError:
        return False


needs_render = pytest.mark.skipif(not (NPX and FFMPEG and _online()), reason="cần npx, ffmpeg và mạng (gsap CDN)")


# ---------- đơn vị ----------

def test_render_js_errors_reads_only_hyperframes_page_errors():
    log = "\n".join([
        "[Browser:WARN] font chậm",
        "[non-blocking] Failed to load resource",
        "[Browser:PAGEERROR] loại cảnh lạ: clip",
        "[Browser:PAGEERROR] loại cảnh lạ: clip",
        "[HyperFrames] composition script error: main Error: thiếu ảnh",
        "render xong",
    ])
    assert B.render_js_errors(log, "") == [
        "[Browser:PAGEERROR] loại cảnh lạ: clip",
        "[HyperFrames] composition script error: main Error: thiếu ảnh",
    ]
    assert B.render_js_errors("", "[Browser:WARN] chỉ cảnh báo") == []


SC = [{"type": "kinetic", "t0": 0, "t1": 10}, {"type": "table", "t0": 10, "t1": 25}, {"type": "chart", "t0": 25, "t1": 35}]


def test_freeze_findings_threshold_scene_and_table_exception():
    assert B.freeze_findings([(1.0, 4.4)], SC) == []                       # 3,4 s: mức hợp lệ đã đo (max 3,13 s)
    bad = B.freeze_findings([(1.0, 6.5)], SC)                              # 5,5 s trong cảnh kinetic
    assert bad and "cảnh 0 (kinetic)" in bad[0]
    assert B.freeze_findings([(10.0, 25.0)], SC) == []                     # bảng tra đứng yên cả cảnh: không báo
    assert B.freeze_findings([(6.0, 25.0)], SC) == []                      # phần ngoài bảng chỉ 4 s < 5 s
    assert B.freeze_findings([(2.0, 25.0)], SC)                            # 8 s ngoài bảng: báo
    assert B.freeze_findings([(26.0, 35.0)], SC)                           # đứng tới hết video ngoài bảng: báo
    assert "ngoài mọi cảnh" in B.freeze_findings([(40.0, 46.0)], SC)[0]


def test_lead_time_warning():
    now = datetime.datetime(2026, 11, 5, 12, 0, tzinfo=datetime.timezone.utc)
    assert B.lead_time_warning("2026-11-05T14:30+00:00", now)              # 2,5 giờ
    assert B.lead_time_warning("2026-11-05T15:00+00:00", now) is None      # đúng 3 giờ
    assert B.lead_time_warning("2026-11-06T19:00+00:00", now) is None
    assert B.lead_time_warning("2026-11-05T10:00+00:00", now)              # đã qua giờ hẹn
    with pytest.raises(SystemExit):
        B.lead_time_warning("mai 7 giờ tối", now)


# ---------- tích hợp: composition tổng hợp ----------

TPL = """<!doctype html><html><head><meta charset="UTF-8"/><meta name="viewport" content="width=320, height=480"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="8" data-width="320" data-height="480" data-fps="30">
<div id="box" style="position:absolute;left:0;top:0;width:100px;height:100px;background:red"></div>{extra}</div>
<script>window.__timelines=window.__timelines||{{}};
var tl=gsap.timeline({{paused:true}}); {tl}
{js}
window.__timelines["main"]=tl;</script></body></html>
"""
MOVE = 'tl.to("#box",{x:200,duration:8,ease:"none"});'
CASES = {
    "ok": dict(tl=MOVE, js="", extra=""),
    "throw": dict(tl=MOVE, js='setTimeout(function(){ throw new Error("BOOM_THROW"); },10);', extra=""),
    "console": dict(tl=MOVE, js='console.error("BOOM_CONSOLE");', extra=""),
    "reject": dict(tl=MOVE, js='Promise.reject(new Error("BOOM_REJ"));', extra=""),
    "asset": dict(tl=MOVE, js="", extra='<img src="missing.png" style="position:absolute;top:200px"/>'),
    "freeze": dict(tl='tl.to("#box",{x:0,duration:8});', js="", extra=""),   # timeline không chuyển động: video đứng hình
}


def _project(root: Path, name: str) -> Path:
    d = root / name
    d.mkdir(parents=True)
    shutil.copy(B.HF / "hyperframes.json", d / "hyperframes.json")
    (d / "index.html").write_text(TPL.format(**CASES[name]), encoding="utf-8")
    return d


def _fake_hf(tmp_path: Path, monkeypatch) -> Path:
    hf = tmp_path / "hf"
    (hf / "assets" / "engine").mkdir(parents=True)
    (hf / "assets" / "engine" / "x.css").write_text("", encoding="utf-8")
    (hf / "assets" / "cases" / "syn").mkdir(parents=True)
    (hf / "assets" / "cases" / "syn" / "data.js").write_text("window.CASE={};\n", encoding="utf-8")
    shutil.copy(B.HF / "hyperframes.json", hf / "hyperframes.json")
    monkeypatch.setattr(B, "HF", hf)
    (tmp_path / "od").mkdir()
    return tmp_path / "od"


@needs_render
@pytest.mark.parametrize("name,needle", [("throw", "BOOM_THROW"), ("console", "BOOM_CONSOLE"), ("reject", "BOOM_REJ"), ("asset", "missing.png")])
def test_check_gate_runtime_only_blocks_js_and_asset_errors(tmp_path, monkeypatch, name, needle):
    od = _fake_hf(tmp_path, monkeypatch)
    comp = tmp_path / "comp.html"
    comp.write_text(TPL.format(**CASES[name]), encoding="utf-8")
    with pytest.raises(SystemExit, match=needle):
        B.check_gate("syn", comp, [{"t0": 0, "t1": 8, "type": "kinetic"}], od, strict=True, runtime_only=True)


@needs_render
def test_check_gate_runtime_only_passes_clean_composition(tmp_path, monkeypatch):
    od = _fake_hf(tmp_path, monkeypatch)
    comp = tmp_path / "comp.html"
    comp.write_text(TPL.format(**CASES["ok"]), encoding="utf-8")
    rep = B.check_gate("syn", comp, [{"t0": 0, "t1": 8, "type": "kinetic"}], od, strict=True, runtime_only=True)
    assert not rep["runtime"] and not rep["lint"]


def _render(proj: Path, out: Path):
    return subprocess.run([NPX, "-y", "-p", "node@22", "-p", "hyperframes@0.8.75", "hyperframes", "render", ".", "-o", str(out),
                           "--fps", "30", "--quiet", "-q", "draft"], cwd=proj, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)


@needs_render
def test_real_render_js_error_and_freeze_pass_exit_zero_but_gates_catch_them(tmp_path):
    scenes = [{"type": "kinetic", "t0": 0, "t1": 8}]
    # 1) trang ném lỗi: renderer vẫn thoát 0 (lý do của ticket) nhưng render_js_errors thấy
    r = _render(_project(tmp_path, "throw"), tmp_path / "throw.mp4")
    assert r.returncode == 0 and (tmp_path / "throw.mp4").exists()
    assert any("BOOM_THROW" in e for e in B.render_js_errors(r.stdout, r.stderr))
    # 2) composition bình thường: không lỗi JS, không đứng hình
    r = _render(_project(tmp_path, "ok"), tmp_path / "ok.mp4")
    assert r.returncode == 0 and B.render_js_errors(r.stdout, r.stderr) == []
    B.freeze_gate("syn", tmp_path / "ok.mp4", scenes, ffmpeg=FFMPEG)
    assert (tmp_path / "ok.mp4").exists()
    # 3) video đứng hình: renderer thoát 0, freeze_gate chặn và xoá file
    r = _render(_project(tmp_path, "freeze"), tmp_path / "freeze.mp4")
    assert r.returncode == 0 and (tmp_path / "freeze.mp4").exists()
    shutil.copy(tmp_path / "freeze.mp4", tmp_path / "freeze_table.mp4")
    with pytest.raises(SystemExit, match="đứng hình"):
        B.freeze_gate("syn", tmp_path / "freeze.mp4", scenes, ffmpeg=FFMPEG)
    assert not (tmp_path / "freeze.mp4").exists()
    # cảnh bảng tra phủ cả video: đứng hình có chủ đích, không chặn
    B.freeze_gate("syn", tmp_path / "freeze_table.mp4", [{"type": "table", "t0": 0, "t1": 8}], ffmpeg=FFMPEG)
    assert (tmp_path / "freeze_table.mp4").exists()


@pytest.mark.skipif(not FFMPEG, reason="cần ffmpeg")
def test_freeze_runs_open_ended_and_fail_closed(tmp_path):
    v = tmp_path / "red.mp4"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=red:s=64x64:d=8:r=10", str(v)], check=True)
    runs = B.freeze_runs(v, FFMPEG)
    assert runs and runs[0][0] == 0 and runs[0][1] >= 7.9              # đứng hình tới hết video vẫn có đoạn
    with pytest.raises(SystemExit, match="đứng hình"):
        B.freeze_gate("syn", v, [{"type": "kinetic", "t0": 0, "t1": 8}], ffmpeg=FFMPEG)
    assert not v.exists()
    bad = tmp_path / "bad.mp4"
    bad.write_bytes(b"not a video")
    with pytest.raises(SystemExit, match="không kiểm được"):
        B.freeze_gate("syn", bad, [], ffmpeg=FFMPEG)
    assert not bad.exists()
