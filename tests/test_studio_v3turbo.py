import json
import sys
import types
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import studio


def test_vsd_profile_loads_and_short_config_selects_v3turbo():
    from library.tools.lib import load_profile

    profile = load_profile("vsd")
    assert profile["kenh"] == "Văn Sử Địa"
    assert [x["ten"] for x in profile["khuon"]] == ["vsd_su", "vsd_dia", "vsd_van"]
    assert studio.short_tts_config({"channel": "vsd", "lines": []}) == {
        "mode": "v3turbo", "voice": "Thục Đoan", "device": "cpu"
    }


def test_unconfigured_channel_keeps_legacy_standard(monkeypatch):
    import hf_batch_render
    monkeypatch.setattr(hf_batch_render, "voice_for", lambda channel: "legacy-voice")
    assert studio.short_tts_config({"channel": "fs"}) == {
        "mode": "standard", "voice": "legacy-voice", "device": "mps"
    }


def test_spec_overrides_tts_mode_and_voice(monkeypatch):
    assert studio.short_tts_config({"channel": "vsd", "tts_mode": "v3turbo", "voice": "Đoan Trang"}) == {
        "mode": "v3turbo", "voice": "Đoan Trang", "device": "cpu"
    }


def test_auto_device_uses_cpu_without_mps(monkeypatch):
    from library.tools import lib
    monkeypatch.setattr(lib, "load_profile", lambda channel: {"tts": {"mode": "v3turbo", "voice": "Ngọc Linh", "device": "auto"}})
    monkeypatch.setitem(sys.modules, "torch", types.SimpleNamespace(backends=types.SimpleNamespace(mps=types.SimpleNamespace(is_available=lambda: False))))
    assert studio.short_tts_config({"channel": "fake"})["device"] == "cpu"


def test_auto_v3turbo_ignores_mps_and_uses_cpu(monkeypatch):
    from library.tools import lib
    monkeypatch.setattr(lib, "load_profile", lambda channel: {"tts": {"mode": "v3turbo", "voice": "Ngọc Linh", "device": "auto"}})
    torch = types.SimpleNamespace(
        cuda=types.SimpleNamespace(is_available=lambda: False),
        backends=types.SimpleNamespace(mps=types.SimpleNamespace(is_available=lambda: True)),
    )
    monkeypatch.setitem(sys.modules, "torch", torch)
    assert studio.short_tts_config({"channel": "fake"})["device"] == "cpu"


def _run_cache_build(monkeypatch, tmp_path, config, manifest):
    import hf_batch_render as batch
    monkeypatch.setattr(studio, "JOBS", tmp_path / "jobs")
    monkeypatch.setattr(studio, "theme", lambda theme_id: {})
    monkeypatch.setattr(studio, "line_words", lambda wav, segs, texts: [{"end": 1}])
    monkeypatch.setattr(studio, "compose", lambda *args: "")
    monkeypatch.setattr(studio, "variety", lambda *args: [])
    monkeypatch.setattr(studio, "short_tts_config", lambda spec: config)
    monkeypatch.setattr(studio, "engine_version", lambda: "test")
    monkeypatch.setattr(studio, "qa", lambda *args: {})
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps({"id": "cache-test", "channel": "fs", "lane": "pilot", "theme": "x",
                                    "lines": ["same text"], "scenes": [], "voice": None, "loop": False}))
    job = tmp_path / "jobs" / "cache-test"
    assets = job / "assets"
    assets.mkdir(parents=True)
    wav = assets / "vo.wav"
    wav.write_bytes(b"cached")
    (assets / "vo.json").write_text(json.dumps(manifest))
    calls = []

    def render_tts(*args, **kwargs):
        calls.append((args, kwargs))
        Path(args[1]).write_bytes(b"new")
        Path(args[1]).with_suffix(".json").write_text(json.dumps({"segments": []}))
        return True

    monkeypatch.setattr(batch, "render_tts", render_tts)
    studio.build(spec_path, render=False, do_qa=False, strict=False, use_ledger=False)
    return calls, json.loads((assets / "vo.json").read_text())


def test_tts_cache_regenerates_when_mode_or_voice_changes(monkeypatch, tmp_path):
    new_config = {"mode": "v3turbo", "voice": "Thục Đoan", "device": "cpu"}
    calls, manifest = _run_cache_build(monkeypatch, tmp_path, new_config,
                                       {"segments": [], "_text": ["same text"], "_tts": {"mode": "standard", "voice": "Old Voice"}})
    assert len(calls) == 1
    assert calls[0][1]["mode"] == "v3turbo"
    assert manifest["_tts"] == {"mode": "v3turbo", "voice": "Thục Đoan"}


def test_legacy_tts_manifest_reuses_for_legacy_config(monkeypatch, tmp_path):
    config = {"mode": "standard", "voice": "Legacy Voice", "device": "mps"}
    calls, _ = _run_cache_build(monkeypatch, tmp_path, config,
                                {"segments": [], "_text": ["same text"]})
    assert calls == []


def test_relative_path_falls_back_to_absolute(tmp_path):
    external = tmp_path / "outside" / "job"
    assert studio.display_path(external) == str(external.resolve())
    assert not Path(studio.display_path(external)).is_relative_to(studio.ROOT)


def test_helper_passes_mode_device_without_constructing_model(monkeypatch, tmp_path):
    import hf_batch_render as batch
    calls = []

    class Proc:
        stderr = ""

    def fake_run(args, **kwargs):
        calls.append(args)
        wav = Path(args[args.index("--output-wav") + 1])
        wav.with_suffix(".json").write_text(json.dumps({"segments": []}))
        return Proc()

    monkeypatch.setattr(batch.subprocess, "run", fake_run)
    monkeypatch.setattr(batch, "runaway_segments", lambda *args: [])
    wav = tmp_path / "voice.wav"
    assert batch.render_tts(tmp_path / "input.txt", wav, [], "Ngọc Linh", mode="v3turbo", device="cpu")
    assert calls[0][calls[0].index("--mode") + 1] == "v3turbo"
    assert calls[0][calls[0].index("--device") + 1] == "cpu"
