"""#145: build() chạy các cổng đúng thứ tự (bước nặng là stub), --slot, cache registry, clip thiếu."""
import contextlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
import build as B  # noqa: E402

from .test_stier_render_gates import MOVE, TPL, _fake_hf, needs_render  # noqa: E402


class Harness:
    """build() thật trên spec thật (bản sao trong thư mục tạm); TTS, sfx, clip, ảnh, render, mux, sổ đa dạng đều là stub."""

    def __init__(self, tmp_path, monkeypatch, slug):
        import themes
        import looks
        import bud_variety
        import clips
        from PIL import Image
        self.calls, self.slug = [], slug
        self.js_log, self.freeze = "", []
        specs = tmp_path / "specs"
        specs.mkdir()
        shutil.copy(B.SPECS / f"{slug}.json", specs / f"{slug}.json")
        hf = tmp_path / "hf"
        hf.mkdir()
        shutil.copytree(B.HF / "assets" / "engine", hf / "assets" / "engine")
        shutil.copy(B.HF / "hyperframes.json", hf / "hyperframes.json")
        music = tmp_path / "music"
        music.mkdir()
        for th in ("mim", "ck", "bud", "case"):
            for f in themes.tracks(themes.theme({"theme": th})):
                (music / f).write_bytes(b"")
        mp = monkeypatch
        real_specs = B.SPECS
        mp.setattr(B, "SPECS", specs)
        mp.setattr(B, "HF", hf)
        mp.setattr(B, "OUT", tmp_path / "out")
        mp.setattr(themes, "MUSIC_DIR", music)
        mp.setattr(themes, "pick_track", lambda slug, pool, ledger=None: sorted(pool)[0])
        mp.setattr(themes, "track_offset", lambda *a, **k: 0)
        mp.setattr(looks, "LEDGER", tmp_path / "looks.json")
        mp.setattr(bud_variety, "LEDGER", tmp_path / "bud_variety.json")
        mp.setattr(bud_variety, "apply", lambda slug, spec: spec)
        import script_lint   # so với kịch bản cũ trong kho: không thuộc phạm vi test này
        mp.setattr(script_lint, "lint", lambda *a, **k: ([], []))

        def speak(lines, wav, tj, **kw):
            ls, dur = B.estimated_word_lines(lines)
            wav.write_bytes(b"")
            return {"duration": dur, "segments": [{"text": l["text"], "start": l["start"], "end": l["end"]} for l in ls]}
        mp.setattr(B, "speak", speak)
        mp.setattr(B, "word_lines", lambda t, wav, say=None: B.estimated_word_lines([x["text"] for x in t["segments"]])[0])

        def fetch_img(file, dst, mode="pd"):
            dst.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (1280, 720)).save(dst)
            dst.with_suffix(".json").write_text(json.dumps({"credit": "stub"}), encoding="utf-8")
            return {"w": 1280, "h": 720}
        mp.setattr(B, "fetch_img", fetch_img)
        mp.setattr(clips, "ensure", lambda ref, ffmpeg="ffmpeg", slot=None: {"src": "assets/clips/x.mp4", "dur": 60.0, "credit": "stub"})
        mp.setattr(B.sfx, "build", lambda *a, **k: self.calls.append("sfx"))
        mp.setattr(B, "render_lock", lambda *a, **k: contextlib.nullcontext())
        mp.setattr(B, "check_gate", self._check)
        mp.setattr(B, "run", self._run)
        mp.setattr(B, "freeze_runs", lambda video, ffmpeg=None, **k: self.freeze)
        mp.setattr(B, "audio_gate", lambda *a, **k: self.calls.append("audio_gate"))
        mp.setattr(B, "qa_short", lambda *a, **k: [])
        orig_js, orig_fg = B.render_js_errors, B.freeze_gate
        mp.setattr(B, "render_js_errors", lambda o, e: (self.calls.append("js_errors"), orig_js(o, e))[1])
        mp.setattr(B, "freeze_gate", lambda *a, **k: (self.calls.append("freeze_gate"), orig_fg(*a, **k))[1])
        self.od = tmp_path / "out" / slug

    def _check(self, slug, comp, scenes, od, strict=True, runtime_only=False):
        self.calls.append(f"check(runtime_only={runtime_only})")

    def _run(self, cmd, **kw):
        if "render" in cmd:
            self.calls.append("render")
            Path(cmd[cmd.index("-o") + 1]).write_bytes(b"mp4")
            return subprocess.CompletedProcess(cmd, 0, self.js_log, "")
        self.calls.append("mux")
        Path(cmd[-1]).write_bytes(b"mp4")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def checks(self):
        return [c for c in self.calls if c.startswith("check")]


CK_SPEC, BUD_V2_SPEC = "ck-uoc-luong-lai-tra-gop", "bud-bd-20-11-thay-tro-v3"
need_ck = pytest.mark.skipif(not (B.SPECS / f"{CK_SPEC}.json").exists(), reason="thiếu spec mẫu")
need_bud = pytest.mark.skipif(not (B.SPECS / f"{BUD_V2_SPEC}.json").exists(), reason="thiếu spec bud v2 mẫu")


@need_ck
def test_build_gate_order(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch, CK_SPEC)
    B.build(CK_SPEC, render=True)
    gates = [c for c in h.calls if c not in ("sfx", "audio_gate")]
    assert gates == ["check(runtime_only=True)", "render", "js_errors", "freeze_gate", "mux"]


@need_ck
def test_build_js_error_deletes_silent_and_never_muxes(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch, CK_SPEC)
    h.js_log = "[Browser:PAGEERROR] BOOM_THROW"
    with pytest.raises(SystemExit, match="BOOM_THROW"):
        B.build(CK_SPEC, render=True)
    assert "mux" not in h.calls and "freeze_gate" not in h.calls
    assert not (h.od / "silent.mp4").exists()


@need_ck
def test_build_freeze_deletes_silent_and_never_muxes(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch, CK_SPEC)
    h.freeze = [(0.0, 30.0)]
    with pytest.raises(SystemExit, match="đứng hình"):
        B.build(CK_SPEC, render=True)
    assert "mux" not in h.calls and "audio_gate" not in h.calls
    assert not (h.od / "silent.mp4").exists() and not (h.od / "final.mp4").exists()


@need_ck
def test_build_no_render_skips_check_and_render_for_non_bud(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch, CK_SPEC)
    B.build(CK_SPEC, render=False)
    assert not any(c.startswith("check") or c in ("render", "mux") for c in h.calls)


@need_bud
def test_build_bud_v2_checks_exactly_once_with_full_check(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch, BUD_V2_SPEC)
    B.build(BUD_V2_SPEC, render=True)
    assert h.checks() == ["check(runtime_only=False)"]


@need_bud
def test_build_bud_v2_no_render_still_runs_full_check_once(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch, BUD_V2_SPEC)
    B.build(BUD_V2_SPEC, render=False)
    assert h.checks() == ["check(runtime_only=False)"]    # hành vi cũ của bud v2 giữ nguyên


def test_pop_slot_forms_and_errors():
    assert B.pop_slot(["a", "--slot", "2026-11-06T19:00+07:00", "--draft", "b"]) == (["a", "--draft", "b"], "2026-11-06T19:00+07:00")
    assert B.pop_slot(["a", "--slot=2026-11-06T19:00+07:00"]) == (["a"], "2026-11-06T19:00+07:00")
    assert B.pop_slot(["a", "--draft"]) == (["a", "--draft"], None)
    for bad in (["a", "--slot"], ["a", "--slot="], ["a", "--slot", "--draft"], ["--slot=x", "--slot", "y"]):
        with pytest.raises(SystemExit, match="slot"):
            B.pop_slot(bad)


def test_registry_cached_and_missing_node_is_runtimeerror(monkeypatch):
    B._REGISTRY_CACHE.clear()
    calls = []
    real = subprocess.run
    monkeypatch.setattr(B.subprocess, "run", lambda *a, **k: (calls.append(1), real(*a, **k))[1])
    first = B.engine_registry()
    assert B.engine_registry() == first and B.hfs_devices() and len(calls) == 1
    B._REGISTRY_CACHE.clear()

    def no_node(*a, **k):
        raise FileNotFoundError("node")
    monkeypatch.setattr(B.subprocess, "run", no_node)
    with pytest.raises(RuntimeError, match="node"):
        B.engine_registry()
    B._REGISTRY_CACHE.clear()


def test_check_gate_missing_clip_names_the_clip(tmp_path, monkeypatch):
    od = _fake_hf(tmp_path, monkeypatch)
    comp = tmp_path / "comp.html"
    comp.write_text(TPL.format(tl=MOVE, js="", extra='<video src="assets/clips/pexels-999.mp4"></video>'), encoding="utf-8")
    with pytest.raises(SystemExit, match="pexels-999.mp4"):
        B.check_gate("syn", comp, [{"t0": 0, "t1": 8, "type": "kinetic"}], od, strict=True, runtime_only=True)
