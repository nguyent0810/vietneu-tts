import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "motion" / "long"))
import build_long as b
import pytest


@pytest.fixture
def project(tmp_path, monkeypatch):
    hf = tmp_path / "hf"
    out = tmp_path / "out"
    src = tmp_path / "data" / "long" / "t"
    src.mkdir(parents=True)
    engine = hf / "assets" / "engine"
    engine.mkdir(parents=True)
    (engine / "casewide.css").write_text("body{}", encoding="utf-8")
    comp = hf / "compositions" / "long"
    comp.mkdir(parents=True)
    for n in ("ch03", "ch07", "ch10"):
        (src / f"{n}.json").write_text(json.dumps({"lines": [n]}), encoding="utf-8")
        folder = out / n
        folder.mkdir(parents=True)
        (folder / "voice.wav").write_bytes(n.encode())
        (folder / "timing.json").write_text('{"duration": 10}', encoding="utf-8")
        img = hf / "assets" / "long" / "t" / "img" / f"{n}.jpg"
        img.parent.mkdir(parents=True, exist_ok=True)
        img.write_bytes(b"image")
        (folder / "data.js").write_text(f'window.CASE = {{"img":"assets/long/t/img/{n}.jpg"}};', encoding="utf-8")
        (comp / f"t_{n}.html").write_text('<link href="assets/engine/casewide.css">', encoding="utf-8")
    monkeypatch.setattr(b, "HF", hf)
    monkeypatch.setattr(b, "ROOT", tmp_path)
    return hf, out, src


def keys(out):
    return {n: b.render_key("t", n, out, False) for n in ("ch03", "ch07", "ch10")}


def test_other_chapter_and_unrelated_code(project, tmp_path):
    hf, out, src = project
    before = keys(out)
    (src / "ch07.json").write_text('{"lines": ["new words"]}', encoding="utf-8")
    (out / "ch07" / "voice.wav").write_bytes(b"new speech")
    (out / "ch07" / "timing.json").write_text('{"duration": 12}', encoding="utf-8")
    after = keys(out)
    assert after["ch03"] == before["ch03"]
    assert after["ch10"] == before["ch10"]
    assert after["ch07"] != before["ch07"]
    script = tmp_path / "scripts" / "unrelated.py"
    script.parent.mkdir()
    script.write_text("changed", encoding="utf-8")
    assert keys(out) == after


def test_used_css_and_image_change_key(project):
    hf, out, _ = project
    before = keys(out)
    (hf / "assets" / "long" / "t" / "img" / "ch07.jpg").write_bytes(b"IMAGE")
    after = keys(out)
    assert after["ch07"] != before["ch07"]
    assert after["ch03"] == before["ch03"]
    assert after["ch10"] == before["ch10"]
    (hf / "assets" / "engine" / "casewide.css").write_text("body{color:red}", encoding="utf-8")
    assert all(keys(out)[n] != after[n] for n in after)


def test_clip_same_size_and_missing_asset(project):
    hf, out, _ = project
    video = hf / "assets" / "long" / "t" / "broll" / "123.mp4"
    video.parent.mkdir(parents=True)
    video.write_bytes(b"1234")
    comp = hf / "compositions" / "long" / "t_ch07.html"
    comp.write_text(comp.read_text(encoding="utf-8") + '<video src="assets/long/t/broll/123.mp4">', encoding="utf-8")
    before = keys(out)
    video.write_bytes(b"5678")
    assert keys(out)["ch07"] != before["ch07"]
    video.unlink()
    with pytest.raises(FileNotFoundError):
        b.render_key("t", "ch07", out, False)
