"""Khoá ghép cuối video dài (final_mix_lock): hai job, kill người giữ, hết hạn, exception, remix_long."""
import fcntl
import json
import os
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import final_mix_lock as FML  # noqa: E402

HOLDER = textwrap.dedent("""
    import sys, time
    sys.path.insert(0, {root!r})
    import final_mix_lock as FML
    with FML.final_mix_lock(sys.argv[1]):
        print("HELD", flush=True)
        time.sleep(float(sys.argv[2]))
""")


@pytest.fixture
def lock_dir(tmp_path, monkeypatch):
    d = tmp_path / "locks"
    monkeypatch.setenv("VIENEU_LOCK_DIR", str(d))
    monkeypatch.delenv("VIENEU_FINAL_MIX_RAM_GATE", raising=False)
    monkeypatch.delenv("VIENEU_FINAL_MIX_LOCK_TIMEOUT_S", raising=False)
    return d


def start_holder(video_id, seconds, env_dir):
    env = dict(os.environ, VIENEU_LOCK_DIR=str(env_dir))
    p = subprocess.Popen([sys.executable, "-c", HOLDER.format(root=str(ROOT)), video_id, str(seconds)],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env)
    assert p.stdout.readline().strip() == "HELD"
    return p


def lock_is_held(path: Path) -> bool:
    with open(path, "a+") as fh:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(fh, fcntl.LOCK_UN)
        return False


def test_path_absolute_and_independent_of_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VIENEU_LOCK_DIR", "rel/locks")
    p = FML.lock_path()
    assert p.is_absolute() and p == (tmp_path / "rel/locks/final_mix.lock").resolve()
    monkeypatch.delenv("VIENEU_LOCK_DIR")
    assert FML.lock_path() == (Path.home() / ".vieneu/locks/final_mix.lock").resolve()


def test_second_job_waits_for_first(lock_dir):
    p = start_holder("L_a", 2.0, lock_dir)
    t0 = time.monotonic()
    with FML.final_mix_lock("L_b"):
        waited = time.monotonic() - t0
    p.wait(10)
    assert waited >= 1.0, waited


def test_killed_holder_releases_lock(lock_dir):
    p = start_holder("L_kill", 60, lock_dir)
    meta = json.loads(FML.lock_path().read_text())
    assert meta["pid"] == p.pid and meta["video_id"] == "L_kill"
    os.kill(p.pid, signal.SIGKILL)
    p.wait(10)
    t0 = time.monotonic()
    with FML.final_mix_lock("L_after", timeout_s=5):
        pass
    assert time.monotonic() - t0 < 3


def test_timeout_raises_with_holder_and_keeps_metadata(lock_dir):
    p = start_holder("L_holder", 30, lock_dir)
    try:
        with pytest.raises(FML.FinalMixLockTimeout) as e:
            with FML.final_mix_lock("L_waiter", timeout_s=0.5):
                pytest.fail("không được vào khối khi hết hạn")
        assert "L_holder" in str(e.value) and str(p.pid) in str(e.value)
        # người chờ không xoá metadata của người đang giữ (mở a+, không phải w)
        assert json.loads(FML.lock_path().read_text())["video_id"] == "L_holder"
    finally:
        p.kill()
        p.wait(10)


def test_timeout_from_env(lock_dir, monkeypatch):
    monkeypatch.setenv("VIENEU_FINAL_MIX_LOCK_TIMEOUT_S", "0.3")
    p = start_holder("L_env", 30, lock_dir)
    try:
        with pytest.raises(FML.FinalMixLockTimeout):
            with FML.final_mix_lock("L_w"):
                pass
    finally:
        p.kill()
        p.wait(10)


def test_exception_releases_lock_and_file_kept(lock_dir):
    with pytest.raises(ValueError):
        with FML.final_mix_lock("L_err"):
            assert lock_is_held(FML.lock_path())
            raise ValueError("lỗi giữa chừng")
    assert FML.lock_path().exists()          # không unlink khi nhả
    assert not lock_is_held(FML.lock_path())


def test_metadata_written_after_acquire(lock_dir):
    with FML.final_mix_lock("L_meta"):
        meta = json.loads(FML.lock_path().read_text())
    assert meta["video_id"] == "L_meta" and meta["pid"] == os.getpid() and meta["acquired_at"]


def test_ram_gate_off_by_default(lock_dir, monkeypatch):
    monkeypatch.setattr(FML, "available_gb", lambda: 0.5)
    t0 = time.monotonic()
    with FML.final_mix_lock("L_ram_off", timeout_s=5):
        pass
    assert time.monotonic() - t0 < 1


def test_ram_gate_on_times_out(lock_dir, monkeypatch):
    monkeypatch.setattr(FML, "available_gb", lambda: 0.5)
    monkeypatch.setenv("VIENEU_FINAL_MIX_RAM_GATE", "1")
    monkeypatch.setenv("VIENEU_FINAL_MIX_LOCK_TIMEOUT_S", "0.3")
    with pytest.raises(FML.FinalMixLockTimeout, match="RAM trống"):
        with FML.final_mix_lock("L_ram_on"):
            pytest.fail("không được vào khối khi RAM thiếu")
    assert not lock_is_held(FML.lock_path())


# ---------------- remix_long: khoá bao trọn build_lines -> mix_long -> mux_audio ----------------
@pytest.fixture
def remix_env(tmp_path, lock_dir, monkeypatch):
    import hf_batch_render as HBR
    import hyperframes_bridge as HB
    import hf_foley
    out = tmp_path / "out"
    cdir = out / "L_x_chapters"
    cdir.mkdir(parents=True)
    (out / "L_x.txt").write_text("a\n", encoding="utf-8")
    (out / "L_x.wav").write_bytes(b"wav")
    (out / "L_x.json").write_text(json.dumps({"duration_s": 3.0}), encoding="utf-8")
    (cdir / "silent.mp4").write_bytes(b"silent")
    (out / "L_x.mp4").write_bytes(b"OLD-FINAL")
    calls = []

    def held(tag):
        calls.append((tag, lock_is_held(FML.lock_path())))

    monkeypatch.setattr(HBR, "pick_bgm", lambda row, wav: ("", 0))
    monkeypatch.setattr(HBR, "long_pool", lambda row: None)
    monkeypatch.setattr(HBR, "note_bgm", lambda row, mixed: ["x.mp3"])
    monkeypatch.setattr(HB, "build_lines", lambda *a, **k: (held("build_lines"), [])[1])
    monkeypatch.setattr(HB, "apply_visuals", lambda *a, **k: None)
    monkeypatch.setattr(hf_foley, "mix_long", lambda *a, **k: held("mix_long"))

    def mux(silent, mixed, tmp, **k):
        held("mux_audio")
        Path(tmp).write_bytes(b"NEW-FINAL")
    monkeypatch.setattr(HB, "mux_audio", mux)
    return HBR, out, calls


def test_remix_long_holds_lock_through_mix_and_mux(remix_env):
    HBR, out, calls = remix_env
    ok, _ = HBR.remix_long({"id": "L_x", "series": "fs"}, out)
    assert ok and calls == [("build_lines", True), ("mix_long", True), ("mux_audio", True)]
    assert (out / "L_x.mp4").read_bytes() == b"NEW-FINAL"
    assert not lock_is_held(FML.lock_path())


def test_remix_long_timeout_keeps_old_output(remix_env, lock_dir, monkeypatch):
    HBR, out, calls = remix_env
    monkeypatch.setenv("VIENEU_FINAL_MIX_LOCK_TIMEOUT_S", "0.3")
    p = start_holder("L_other", 30, lock_dir)
    try:
        ok, msg = HBR.remix_long({"id": "L_x", "series": "fs"}, out)
    finally:
        p.kill()
        p.wait(10)
    assert not ok and "chờ khoá ghép cuối" in msg
    assert calls == [] and (out / "L_x.mp4").read_bytes() == b"OLD-FINAL"


def test_render_chapters_lock_wraps_concat_mix_and_mux():
    src = (ROOT / "hf_batch_render.py").read_text(encoding="utf-8")
    body = src[src.index("def render_chapters("):]
    body = body[:body.index("\ndef ", 10)]
    i_lock = body.index("with final_mix_lock(rid):")
    for step in ('"-f", "concat"', "HB.build_lines(", "hf_foley.mix_long(", "HB.mux_audio(", '.render.json").write_text'):
        assert body.index(step) > i_lock, step
    assert "except FinalMixLockTimeout" in body
