"""P3 (E2E validation remediation) -- long_batch_runner.py's exception
handler now classifies a subprocess timeout distinctly from other errors
(`last_error_type: "timeout"` vs `"error"`), so an episode left in the
terminal `failed` state after a real ~27-minute episode's real
subprocess.TimeoutExpired incident (found live during the CL channel E2E
validation) can be triaged at a glance -- "worth just retrying" vs "needs
real investigation" -- without re-reading raw error text.

Uses the same monkeypatch-both-`_registry_path`-AND-`_REGISTRY_PRODUCTION_ROOT`
pattern as test_registry_production_guard_integration.py (G1) -- a fake
tree that LOOKS like production to the write-guard, never the real one."""
import json
import subprocess

import pytest

import long_batch_runner as lbr
import registry_lock as rl


@pytest.fixture(autouse=True)
def _isolated_registry(tmp_path, monkeypatch):
    fake_root = tmp_path / "output" / "long"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(lbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(lbr, "_registry_path", lambda topic: fake_path)
    return fake_path


def _run_main_with_process_one_episode(monkeypatch, fake_path, raising_exc, seed_entry=None, argv_extra=None):
    """`seed_entry` matches the REAL shape of the actual incident this fix
    targets: a real episode always already has a real `status` (from an
    earlier successfully-completed stage, e.g. CL's EP001 was at
    `assets_ready`) by the time it can reach the slow render step that
    timed out -- a genuinely brand-new, never-touched episode failing on
    its very first step is a DIFFERENT (real, but separate and NOT
    P3-scoped) registry-schema edge case, not reproduced here."""
    if seed_entry is None:
        seed_entry = {"key": "EP999", "status": "assets_ready"}
    fake_path.parent.mkdir(parents=True, exist_ok=True)
    fake_path.write_text(json.dumps({"EP999": seed_entry}), encoding="utf-8")

    monkeypatch.setattr(lbr, "run_audio_stage", lambda topic: None)
    monkeypatch.setattr(lbr, "discover_ready_episodes", lambda domain_id, topic: [{"episode_id": "EP999", "title": "Test"}])
    monkeypatch.setattr(lbr, "next_available_weekly_slot", lambda registry, days, hour: "2026-08-10T08:00:00Z")

    def fake_process_one_episode(*a, **kw):
        raise raising_exc

    monkeypatch.setattr(lbr, "process_one_episode", fake_process_one_episode)
    monkeypatch.setattr(
        "sys.argv",
        ["long_batch_runner.py", "--domain", "CL", "--topic", "Test Topic", "--count", "1", "--dry-run"] + (argv_extra or []),
    )
    lbr.main()
    return json.loads(fake_path.read_text(encoding="utf-8"))


def test_timeout_exception_classified_as_timeout(monkeypatch, tmp_path):
    fake_path = tmp_path / "output" / "long" / "Test Topic" / "registry.json"
    timeout_exc = subprocess.TimeoutExpired(cmd=["fake", "cmd"], timeout=10800)
    registry = _run_main_with_process_one_episode(monkeypatch, fake_path, timeout_exc)
    assert registry["EP999"]["last_error_type"] == "timeout"
    assert registry["EP999"]["error_count"] == 1
    assert registry["EP999"].get("status") != "failed", "must not be terminal after only 1 failure"


def test_generic_exception_classified_as_error(monkeypatch, tmp_path):
    fake_path = tmp_path / "output" / "long" / "Test Topic" / "registry.json"
    registry = _run_main_with_process_one_episode(monkeypatch, fake_path, RuntimeError("some real content-level bug"))
    assert registry["EP999"]["last_error_type"] == "error"


def test_timeout_still_reaches_terminal_failed_after_max_retries(monkeypatch, tmp_path):
    """The classification is additive, informational -- it does NOT change
    the existing retry-ceiling/fail-closed mechanism (G1's design): 3
    consecutive timeouts still end in terminal `failed`, same as 3
    consecutive generic errors always have."""
    fake_path = tmp_path / "output" / "long" / "Test Topic" / "registry.json"
    timeout_exc = subprocess.TimeoutExpired(cmd=["fake", "cmd"], timeout=10800)
    registry = _run_main_with_process_one_episode(
        monkeypatch, fake_path, timeout_exc, seed_entry={"key": "EP999", "error_count": 2, "status": "assets_ready"},
    )
    assert registry["EP999"]["error_count"] == 3
    assert registry["EP999"]["status"] == "failed"
    assert registry["EP999"]["last_error_type"] == "timeout"


def test_assets_ready_step_calls_symbol_asset_healer_before_render(monkeypatch, tmp_path):
    """P4b (E2E validation remediation): confirms process_one_episode()'s
    real body -- not a mocked stand-in -- actually calls
    heal_stale_symbol_asset_paths() at the assets_ready step, with the
    correct (shot_list_path, domain) args, BEFORE the render subprocess
    call. Stops the real body right after the render run_step() call (via
    a raised sentinel) so this stays scoped to just the wiring, not the
    full remaining cascade (bgm/finalize/seo/upload)."""
    calls = []

    def fake_heal(shot_list_path, domain_id):
        calls.append(("heal", shot_list_path, domain_id))
        return 0

    def fake_run_step(cmd, cwd=None, timeout=None):
        calls.append(("run_step",))
        raise StopIteration("stop right after the render call -- test boundary, not a real error")

    monkeypatch.setattr(lbr.creative_profiles, "heal_stale_symbol_asset_paths", fake_heal)
    monkeypatch.setattr(lbr, "run_step", fake_run_step)

    ep_dir = tmp_path / "output" / "long" / "Test Topic" / "EP999"
    ep_dir.mkdir(parents=True)
    shot_list_path = ep_dir / "shot_list_final.json"
    shot_list_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(lbr, "_output_dir", lambda topic: tmp_path / "output" / "long" / "Test Topic")
    monkeypatch.setattr(lbr, "load_registry", lambda topic: {
        "EP999": {"key": "EP999", "status": "assets_ready", "shot_list_path": str(shot_list_path), "wav_path": "w", "json_path": "j"},
    })
    monkeypatch.setattr(lbr, "save_registry", lambda registry, topic: None)

    ep = {"episode_id": "EP999", "episode_dir_name": "EP999_dir", "title": "Test", "internal_dir": tmp_path}
    with pytest.raises(StopIteration):
        lbr.process_one_episode(ep, "Test Topic", "creds.json", "Playlist", "2026-08-10T08:00:00Z", dry_run=True, domain="FS")

    assert calls == [("heal", str(shot_list_path), "FS"), ("run_step",)], (
        "healer must run before the render subprocess call, with the shot list path + resolved domain"
    )


def test_render_video_step_timeout_was_increased_from_original_7200s():
    """P3: modest, documented secondary mitigation for the first-attempt
    case (retries get their real speedup from audio_tool_render.py's own
    checkpoint-reuse fix, not from this alone) -- confirms the actual
    value shipped, not just that SOME number is present."""
    import inspect

    source = inspect.getsource(lbr.process_one_episode)
    assert "timeout=10800" in source, "Render video step's timeout must be the reasoned +50% value, not silently reverted"
    assert "timeout=7200" not in source.split("Render video")[1].split("Trộn BGM")[0], (
        "the render-video step specifically must no longer use the old 7200s value"
    )
