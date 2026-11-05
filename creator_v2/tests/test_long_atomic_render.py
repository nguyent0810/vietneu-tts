"""GH-170: hợp đồng đầu ra Long (docs/pm/tickets/GH-170-contract.md). Không render, không gọi TTS thật, chỉ thư mục tạm."""
import json
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT / "motion" / "stier"), str(ROOT),
                str(ROOT / "scripts")]
import audio_lint as AL  # noqa: E402
import build_long as bl  # noqa: E402
import long_output as LO  # noqa: E402

OK = SimpleNamespace(returncode=0, stdout="", stderr="")


def _raise(exc):
    def f(*a, **kw):
        raise exc
    return f


def _gates_off(monkeypatch, od):
    monkeypatch.setattr(bl.branch_gate, "refuse", lambda *a: None)
    for attr in ("_refuse_unreviewed_sheets", "_refuse_html_lint", "_refuse_floor", "_refuse_craft"):
        monkeypatch.setattr(bl, attr, lambda *a: None)
    monkeypatch.setattr(bl, "load", lambda *a: ({"channel": "MIM", "master": True}, [("ch01", {})], od))
    monkeypatch.setattr(bl, "render_key", lambda *a: "key")
    monkeypatch.setattr(bl, "render_lock", lambda *a, **kw: nullcontext())
    monkeypatch.setattr(bl, "probe_dur", lambda p: 10.0)
    monkeypatch.setattr(bl.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0, stdout="video\n"))


def _temp_of(cmd):
    return Path(cmd[cmd.index("-o") + 1])


def _render_ok(content=b"new video"):
    def run(cmd, **kw):
        _temp_of(cmd).write_bytes(content)
        return OK
    return run


def _lock_replace(monkeypatch, target_name):
    real = LO.os.replace

    def locked(src, dst):
        if Path(dst).name == target_name:
            raise PermissionError("locked")
        return real(src, dst)
    monkeypatch.setattr(LO.os, "replace", locked)


@pytest.fixture
def setup_render(tmp_path, monkeypatch):
    od = tmp_path
    (od / "ch01").mkdir()
    output = od / "ch01" / "silent.mp4"
    output.write_bytes(b"old good video")
    (od / "ch01" / "data.js").write_text('window.CASE = {"dur": 10};', encoding="utf-8")
    key = output.with_suffix(".key")
    key.write_text("key")
    _gates_off(monkeypatch, od)
    return output, key


# ---------------- render chương ----------------
def test_crash_mid_write_keeps_old_video_and_next_run_rerenders(setup_render, monkeypatch):
    output, key = setup_render
    calls = []

    def crash(cmd, **kw):
        calls.append(1)
        _temp_of(cmd).write_bytes(b"partial")
        raise KeyboardInterrupt
    monkeypatch.setattr(bl, "run", crash)
    with pytest.raises(KeyboardInterrupt):
        bl.do_render("demo", force=True)
    assert output.read_bytes() == b"old good video" and not key.exists()
    assert not list(output.parent.glob(".silent-*"))

    def ok(cmd, **kw):
        calls.append(2)
        return _render_ok()(cmd)
    monkeypatch.setattr(bl, "run", ok)
    bl.do_render("demo")                      # không --force: key đã mất nên KHÔNG được cache hit
    assert calls == [1, 2] and output.read_bytes() == b"new video" and key.read_text() == "key"


def test_hard_kill_leaves_stale_temp_and_no_key_so_no_cache_hit(setup_render, monkeypatch):
    output, key = setup_render
    key.unlink()                                  # trạng thái sau kill -9: key đã xoá, file tạm mồ côi
    stale = output.parent / ".silent-dead.mp4"
    stale.write_bytes(b"orphan")
    monkeypatch.setattr(bl, "run", _render_ok(b"new"))
    bl.do_render("demo")
    assert output.read_bytes() == b"new" and not stale.exists()


def test_failed_force_preserves_video_and_invalidates_old_key(setup_render, monkeypatch):
    output, key = setup_render

    def fail(cmd, **kw):
        _temp_of(cmd).write_bytes(b"incomplete")
        return SimpleNamespace(returncode=1, stdout="", stderr="ffmpeg died")
    monkeypatch.setattr(bl, "run", fail)
    with pytest.raises(SystemExit, match="render hỏng"):
        bl.do_render("demo", force=True)
    assert output.read_bytes() == b"old good video" and not key.exists()
    assert not list(output.parent.glob(".silent-*"))
    assert "render lại" in bl.chapter_problems("demo", "ch01", output.parent.parent)


def test_success_publishes_video_before_key(setup_render, monkeypatch):
    output, key = setup_render

    def succeed(cmd, **kw):
        assert output.read_bytes() == b"old good video" and not key.exists()
        return _render_ok()(cmd)
    monkeypatch.setattr(bl, "run", succeed)
    order = []
    real = LO.os.replace

    def spy(s, d):
        order.append(Path(d).name)
        return real(s, d)
    monkeypatch.setattr(LO.os, "replace", spy)
    bl.do_render("demo", force=True)
    assert order == ["silent.mp4", "silent.key"]
    assert output.read_bytes() == b"new video" and key.read_text() == "key"


def test_locked_output_is_clear_error_no_key_old_video_intact(setup_render, monkeypatch):
    output, key = setup_render
    monkeypatch.setattr(bl, "run", _render_ok())
    _lock_replace(monkeypatch, "silent.mp4")
    with pytest.raises(SystemExit, match="bản cũ giữ nguyên"):
        bl.do_render("demo", force=True)
    assert output.read_bytes() == b"old good video" and not key.exists()
    assert not list(output.parent.glob(".silent-*"))


def test_locked_key_after_video_published_is_loud_and_not_a_cache_hit(setup_render, monkeypatch):
    output, key = setup_render
    monkeypatch.setattr(bl, "run", _render_ok())
    _lock_replace(monkeypatch, "silent.key")
    with pytest.raises(SystemExit):
        bl.do_render("demo", force=True)
    assert not key.exists()
    assert bl.chapter_problems("demo", "ch01", output.parent.parent)


def test_invalid_duration_does_not_promote(setup_render, monkeypatch):
    output, key = setup_render
    monkeypatch.setattr(bl, "run", _render_ok(b"x"))
    monkeypatch.setattr(bl, "probe_dur", lambda p: 0.0)
    with pytest.raises(SystemExit, match="thời lượng"):
        bl.do_render("demo", force=True)
    assert output.read_bytes() == b"old good video" and not key.exists()


def test_short_but_readable_video_is_not_reused(setup_render, monkeypatch):
    output, key = setup_render
    monkeypatch.setattr(bl, "probe_dur", lambda p: 3.0 if Path(p) == output else 10.0)
    monkeypatch.setattr(bl, "run", _render_ok(b"replacement"))
    bl.do_render("demo")
    assert output.read_bytes() == b"replacement"


def test_audio_only_render_is_rejected(setup_render, monkeypatch):
    output, key = setup_render
    monkeypatch.setattr(bl, "run", _render_ok(b"a"))
    monkeypatch.setattr(bl.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0, stdout=""))
    with pytest.raises(SystemExit, match="thời lượng"):
        bl.do_render("demo", force=True)
    assert output.read_bytes() == b"old good video" and not key.exists()


def test_draft_av_ffmpeg_failure_is_reported_and_old_av_kept(setup_render, monkeypatch):
    output, key = setup_render
    od = output.parent
    (od / "mix.wav").write_bytes(b"m")
    (od / "draft_av.mp4").write_bytes(b"old av")

    def r(cmd, **kw):
        if "-o" in cmd:
            return _render_ok(b"draft")(cmd)
        Path(cmd[-1]).write_bytes(b"partial av")
        return SimpleNamespace(returncode=1, stdout="", stderr="boom")
    monkeypatch.setattr(bl, "run", r)
    with pytest.raises(SystemExit, match="ghép tiếng"):
        bl.do_render("demo", draft=True, force=True)
    assert (od / "draft_av.mp4").read_bytes() == b"old av"


# ---------------- final ----------------
@pytest.fixture
def setup_final(tmp_path, monkeypatch):
    od = tmp_path / "out"
    (od / "ch01").mkdir(parents=True)
    (od / "ch01" / "silent.mp4").write_bytes(b"video")
    (od / "ch01" / "silent.key").write_text("key")
    (od / "ch01" / "data.js").write_text('window.CASE = {"dur": 10};', encoding="utf-8")
    (od / "ch01" / "voice.wav").write_bytes(b"v")
    (od / "final.mp4").write_bytes(b"OLD FINAL")
    (od / "captions.vi.srt").write_text("OLD SRT", encoding="utf-8")
    (od / "final.commit").write_text("OLD COMMIT", encoding="utf-8")
    old = {"schema": 1, "run_id": "old", "state": "ok", "final": {"size": 9}, "captions": {"size": 7}}
    (od / LO.MANIFEST).write_text(json.dumps(old), encoding="utf-8")
    _gates_off(monkeypatch, od)
    monkeypatch.setattr(bl, "_write_final_commit", lambda out: LO.atomic_write_text(out / "final.commit", "NEW COMMIT"))
    monkeypatch.setattr(AL, "check_parts", lambda parts, sfx: [])
    monkeypatch.setattr(AL, "check_voices", lambda *a: ([], [], {}))
    monkeypatch.setattr(AL, "check_final", lambda p, ff: ([], {"tp": -1.5, "lufs": -14.0}))
    state = {"ffmpeg_rc": 0, "srt_rc": 0}

    def fake_run(cmd, **kw):
        if Path(str(cmd[1])).name == "srt.py":
            if state["srt_rc"] == 0:
                Path(cmd[cmd.index("--out") + 1]).write_text("NEW SRT", encoding="utf-8")
            return SimpleNamespace(returncode=state["srt_rc"], stdout="", stderr="srt boom")
        out = Path(cmd[-1])
        is_final = out.suffix == ".mp4" and out.name.startswith(".final")
        out.write_bytes(b"NEW FINAL" if is_final else b"mix")
        return SimpleNamespace(returncode=state["ffmpeg_rc"] if is_final else 0, stdout="", stderr="ffmpeg boom")
    monkeypatch.setattr(bl, "run", fake_run)
    return od, state


def _assert_old_kept_but_consumers_refuse(od, expect_state="failed"):
    assert (od / "final.mp4").read_bytes() == b"OLD FINAL"
    assert (od / "captions.vi.srt").read_text(encoding="utf-8") == "OLD SRT"
    assert (od / "final.commit").read_text(encoding="utf-8") == "OLD COMMIT"
    assert json.loads((od / LO.MANIFEST).read_text(encoding="utf-8"))["state"] == expect_state
    probs = LO.final_problems(od)
    assert probs and "KHÔNG phải kết quả lượt này" in probs[0]
    assert not [p for p in od.iterdir() if p.name.startswith(".")]      # không bỏ file tạm


def test_final_success_manifest_ok_and_valid(setup_final):
    od, _ = setup_final
    bl.do_final("demo")
    assert (od / "final.mp4").read_bytes() == b"NEW FINAL"
    assert (od / "captions.vi.srt").read_text(encoding="utf-8") == "NEW SRT"
    assert (od / "final.commit").read_text(encoding="utf-8") == "NEW COMMIT"
    m = json.loads((od / LO.MANIFEST).read_text(encoding="utf-8"))
    assert m["state"] == "ok" and m["chapters"] == {"ch01": "key"} and m["run_id"] != "old"
    assert LO.final_problems(od, full=True) == []


def test_final_ffmpeg_failure(setup_final):
    od, st = setup_final
    st["ffmpeg_rc"] = 1
    with pytest.raises(SystemExit, match="ghép final lỗi"):
        bl.do_final("demo")
    _assert_old_kept_but_consumers_refuse(od)


def test_final_subtitle_failure(setup_final):
    od, st = setup_final
    st["srt_rc"] = 1
    with pytest.raises(SystemExit, match="srt boom"):
        bl.do_final("demo")
    _assert_old_kept_but_consumers_refuse(od)


def test_final_audio_gate_failure_keeps_old_but_refused(setup_final, monkeypatch):
    od, _ = setup_final
    monkeypatch.setattr(AL, "check_final", lambda p, ff: (["true peak"], {"tp": -0.5, "lufs": -14.0}))
    with pytest.raises(SystemExit, match="audio_lint chặn"):
        bl.do_final("demo")
    _assert_old_kept_but_consumers_refuse(od)


def test_final_locked_target_final(setup_final, monkeypatch):
    od, _ = setup_final
    _lock_replace(monkeypatch, "final.mp4")
    with pytest.raises(SystemExit, match="bản cũ giữ nguyên"):
        bl.do_final("demo")
    _assert_old_kept_but_consumers_refuse(od)


def test_final_locked_captions_after_final_published(setup_final, monkeypatch):
    od, _ = setup_final
    _lock_replace(monkeypatch, "captions.vi.srt")
    with pytest.raises(SystemExit, match="bản cũ giữ nguyên"):
        bl.do_final("demo")
    assert (od / "captions.vi.srt").read_text(encoding="utf-8") == "OLD SRT"
    assert json.loads((od / LO.MANIFEST).read_text(encoding="utf-8"))["state"] == "failed"
    assert LO.final_problems(od)          # final.mp4 mới + srt cũ là cặp lệch: consumer vẫn bị chặn


def test_final_commit_failure_after_publish_is_failed(setup_final, monkeypatch):
    od, _ = setup_final
    monkeypatch.setattr(bl, "_write_final_commit", _raise(SystemExit("final: không đọc được Git")))
    with pytest.raises(SystemExit):
        bl.do_final("demo")
    assert LO.final_problems(od)


def test_final_floor_gate_failure_is_failed_not_stale_ok(setup_final, monkeypatch):
    od, _ = setup_final
    monkeypatch.setattr(bl, "_refuse_floor", _raise(SystemExit("floor chặn")))
    with pytest.raises(SystemExit, match="floor"):
        bl.do_final("demo")
    _assert_old_kept_but_consumers_refuse(od)


def test_final_rejects_stale_chapter(setup_final):
    od, _ = setup_final
    (od / "ch01" / "silent.key").unlink()
    with pytest.raises(SystemExit, match="render lại"):
        bl.do_final("demo")
    _assert_old_kept_but_consumers_refuse(od)


def test_final_variety_failure_is_failed(setup_final, monkeypatch):
    od, _ = setup_final
    monkeypatch.setattr(bl.variety, "audit", lambda t: ["trùng nhạc"])
    with pytest.raises(SystemExit, match="variety"):
        bl.do_final("demo", check_variety=True)
    _assert_old_kept_but_consumers_refuse(od)


def test_killed_run_leaves_running_manifest(setup_final, monkeypatch):
    od, _ = setup_final
    monkeypatch.setattr(bl, "_refuse_craft", _raise(KeyboardInterrupt()))
    monkeypatch.setattr(LO, "finish_failed", lambda *a: None)    # mô phỏng tiến trình chết trước khi kịp ghi `failed`
    with pytest.raises(KeyboardInterrupt):
        bl.do_final("demo")
    assert json.loads((od / LO.MANIFEST).read_text(encoding="utf-8"))["state"] == "running"
    assert LO.final_problems(od)


# ---------------- consumer ----------------
def test_final_problems_contract(tmp_path):
    assert LO.final_problems(tmp_path) == ["final.mp4 chưa có"]
    (tmp_path / "final.mp4").write_bytes(b"legacy")
    assert LO.final_problems(tmp_path) == []                       # legacy: chưa từng có manifest
    (tmp_path / LO.MANIFEST).write_text("{broken", encoding="utf-8")
    assert LO.final_problems(tmp_path)                             # manifest hỏng = fail closed
    (tmp_path / "captions.vi.srt").write_text("s", encoding="utf-8")
    m = {"state": "ok", "final": {"size": 6, "sha256": LO.sha256(tmp_path / "final.mp4")},
         "captions": {"size": 1, "sha256": LO.sha256(tmp_path / "captions.vi.srt")}}
    (tmp_path / LO.MANIFEST).write_text(json.dumps(m), encoding="utf-8")
    assert LO.final_problems(tmp_path, full=True) == []
    (tmp_path / "final.mp4").write_bytes(b"swap!!")                # cùng cỡ, khác nội dung
    assert LO.final_problems(tmp_path) == [] and LO.final_problems(tmp_path, full=True)
    (tmp_path / "final.mp4").write_bytes(b"other size")
    assert LO.final_problems(tmp_path)


def _od_with_manifest(tmp_path, state, chapters=None):
    od = tmp_path / "output" / "long" / "t"
    od.mkdir(parents=True)
    (od / "final.mp4").write_bytes(b"FINAL")
    (od / "captions.vi.srt").write_text("S", encoding="utf-8")
    m = {"run_id": "r1", "state": state, "error": "boom" if state == "failed" else None, "chapters": chapters or {},
         "final": {"size": 5, "sha256": LO.sha256(od / "final.mp4")}, "captions": {"size": 1, "sha256": LO.sha256(od / "captions.vi.srt")}}
    (od / LO.MANIFEST).write_text(json.dumps(m), encoding="utf-8")
    return od


class _Reached(Exception):
    pass


def _run_publish_main(monkeypatch, tmp_path):
    """Chạy publish_long.main thật trên thư mục tạm; mạng/credentials/store bị chặn bằng mock."""
    import floor
    import publish_long as PL
    (tmp_path / "data" / "long" / "t").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "long" / "t" / "spec.json").write_text(
        json.dumps({"channel": "MIM", "chapters": [], "approved": "ok", "youtube": {}}), encoding="utf-8")
    monkeypatch.setattr(PL, "ROOT", tmp_path)
    monkeypatch.setattr(PL.branch_gate, "refuse", lambda *a: None)
    monkeypatch.setattr(floor, "problems", lambda *a: [])
    import factcheck_lint
    monkeypatch.setattr(factcheck_lint, "lint", lambda *a: [])
    monkeypatch.setattr(PL.channels, "upload_mode", lambda ch: "manual")
    monkeypatch.setattr(PL, "long_bundle", _raise(_Reached()))      # qua cổng final thì tới đây: chưa chạm kho/mạng
    monkeypatch.setattr(PL, "register", _raise(AssertionError("không được vào kho")))
    monkeypatch.setattr(sys, "argv", ["publish_long.py", "t", "MIM", "2026-12-01T12:00:00Z"])
    PL.main()


@pytest.mark.parametrize("state", ["failed", "running"])
def test_publish_long_main_refuses_non_ok_manifest(tmp_path, monkeypatch, state):
    _od_with_manifest(tmp_path, state)
    with pytest.raises(SystemExit, match="final không hợp lệ"):
        _run_publish_main(monkeypatch, tmp_path)


def test_publish_long_main_refuses_changed_chapter_and_swapped_file(tmp_path, monkeypatch):
    od = _od_with_manifest(tmp_path, "ok", {"ch01": "k1"})
    (od / "ch01").mkdir()
    (od / "ch01" / "silent.key").write_text("k2")                    # chương render lại sau lượt final
    with pytest.raises(SystemExit, match="đã đổi sau lượt final"):
        _run_publish_main(monkeypatch, tmp_path)
    (od / "ch01" / "silent.key").write_text("k1")
    (od / "final.mp4").write_bytes(b"SWAPD")                          # cùng cỡ, khác nội dung: publish kiểm sha256
    with pytest.raises(SystemExit, match="sha256"):
        _run_publish_main(monkeypatch, tmp_path)


def test_publish_long_main_passes_gate_with_ok_manifest(tmp_path, monkeypatch):
    od = _od_with_manifest(tmp_path, "ok", {"ch01": "k1"})
    (od / "ch01").mkdir()
    (od / "ch01" / "silent.key").write_text("k1")
    with pytest.raises(_Reached):
        _run_publish_main(monkeypatch, tmp_path)


@pytest.mark.parametrize("state", ["failed", "running"])
def test_qa_mark_refuses_non_ok_manifest(tmp_path, state):
    import qa_mark
    od = _od_with_manifest(tmp_path, state)
    with pytest.raises(SystemExit, match="final không hợp lệ"):
        qa_mark.mark(["t"], root=tmp_path)
    assert not (od / "qa_ok").exists()


def test_qa_mark_ok_manifest_writes_hash(tmp_path):
    import qa_mark
    od = _od_with_manifest(tmp_path, "ok")
    qa_mark.mark(["t"], root=tmp_path)
    assert (od / "qa_ok").read_text(encoding="utf-8").strip() == LO.sha256(od / "final.mp4")


def test_final_problems_compares_chapter_keys(tmp_path):
    od = _od_with_manifest(tmp_path, "ok", {"ch01": "k1"})
    (od / "ch01").mkdir()
    (od / "ch01" / "silent.key").write_text("k1")
    assert LO.final_problems(od) == []
    (od / "ch01" / "silent.key").write_text("k2")
    assert any("ch01" in p for p in LO.final_problems(od))
    (od / "ch01" / "silent.key").unlink()                             # key bị xoá (render lại thất bại) cũng là lệch
    assert any("ch01" in p for p in LO.final_problems(od))


def test_sweep_removes_every_orphan_temp_pattern(setup_final, monkeypatch):
    od, _ = setup_final
    orphans = [od / ".final-aaaa1111.mp4", od / ".captions.vi-bbbb2222.srt", od / "..captions.vi-bbbb2222-cccc3333.srt",
               od / ".final.run-dddd4444.json", od / "ch01" / ".draft_av-eeee5555.mp4", od / "ch01" / ".silent-ffff6666.key",
               od / "ch01" / ".silent-1111aaaa.mp4"]
    for o in orphans:
        o.write_bytes(b"x")
    bl.do_final("demo")                    # final + manifest + srt
    monkeypatch.setattr(bl, "run", _render_ok())
    bl.do_render("demo", force=True)       # silent + key (sweep chạy trước render)
    assert not [o for o in orphans if o.exists()]
    assert (od / "final.mp4").exists() and (od / "captions.vi.srt").exists()


def test_run_chain_warns_when_final_not_checked():
    import run_chain as RC
    sh = "python motion/long/build_long.py $T final > f.log 2>&1 || exit 1\n[ -f final.mp4 ] || exit 1\n"
    assert any("long_output.py" in w for w in RC.check(sh))
    assert not any("long_output.py" in w for w in RC.check(sh + "python motion/long/long_output.py check $T || exit 1\n"))


# ---------------- cache TTS ----------------
def _engine(monkeypatch, samples=24000, calls=None):
    import numpy as np

    def infer(*a, **kw):
        if calls is not None:
            calls.append(1)
        return np.full(samples, 0.1, dtype="float32")
    monkeypatch.setattr(bl, "_engine", SimpleNamespace(infer=infer))


V = "voice-test"      # truyền giọng tường minh: bl.VOICE bị test khác đổi


def _wav(path, n=2400, sr=24000):
    import numpy as np
    import soundfile as sf
    sf.write(str(path), np.full(n, 0.1, dtype="float32"), sr)


def _cache_path(tmp_path, text="Câu bình thường."):
    return tmp_path / (bl._key(text, 0, V) + ".wav")


def test_interrupted_tts_write_does_not_create_cache(tmp_path, monkeypatch):
    import soundfile as sf
    _engine(monkeypatch)

    def fail(path, samples, rate):
        Path(path).write_bytes(b"RIFF partial")
        raise OSError("interrupted write")
    monkeypatch.setattr(sf, "write", fail)
    with pytest.raises(OSError, match="interrupted"):
        bl.tts_line("Câu bình thường.", tmp_path, 0, V)
    assert not list(tmp_path.iterdir())


def test_truncated_decodable_cache_is_not_a_hit(tmp_path, monkeypatch):
    p = _cache_path(tmp_path)
    _wav(p)
    p.write_bytes(p.read_bytes()[:1000])      # header khai ~4800 byte, còn ~1000: libsndfile vẫn giải mã được
    calls = []
    _engine(monkeypatch, calls=calls)
    a, sr = bl.tts_line("Câu bình thường.", tmp_path, 0, V)
    assert calls == [1] and len(a) == 24000 and LO.wav_complete(p)


def test_empty_cache_is_regenerated(tmp_path, monkeypatch):
    import numpy as np
    import soundfile as sf
    sf.write(str(_cache_path(tmp_path)), np.array([], dtype="float32"), 24000)
    calls = []
    _engine(monkeypatch, calls=calls)
    a, _ = bl.tts_line("Câu bình thường.", tmp_path, 0, V)
    assert calls == [1] and len(a) == 24000


def test_good_cache_is_byte_identical_and_engine_not_called(tmp_path, monkeypatch):
    p = _cache_path(tmp_path)
    _wav(p)
    before = p.read_bytes()
    calls = []
    _engine(monkeypatch, calls=calls)
    a, sr = bl.tts_line("Câu bình thường.", tmp_path, 0, V)
    assert calls == [] and p.read_bytes() == before and len(a) == 2400 and sr == 24000


def test_truncated_engine_output_is_not_cached(tmp_path, monkeypatch):
    import soundfile as sf
    _engine(monkeypatch)
    write = sf.write
    monkeypatch.setattr(sf, "write", lambda path, samples, rate: write(path, samples[:240], rate))
    with pytest.raises(ValueError, match="thiếu mẫu"):
        bl.tts_line("Câu bình thường.", tmp_path, 0, V)
    assert not list(tmp_path.iterdir())


def test_locked_tts_target_is_clear_error_and_no_cache(tmp_path, monkeypatch):
    _engine(monkeypatch)
    _lock_replace(monkeypatch, _cache_path(tmp_path).name)
    with pytest.raises(SystemExit, match="bản cũ giữ nguyên"):
        bl.tts_line("Câu bình thường.", tmp_path, 0, V)
    assert not list(tmp_path.iterdir())


def test_json_state_files_are_written_atomically(tmp_path, monkeypatch):
    f = tmp_path / "picks.json"
    f.write_text("{}", encoding="utf-8")
    _lock_replace(monkeypatch, "picks.json")
    with pytest.raises(SystemExit):
        LO.atomic_write_text(f, '{"a": 1}', "picks.json")
    assert f.read_text(encoding="utf-8") == "{}" and len(list(tmp_path.iterdir())) == 1
