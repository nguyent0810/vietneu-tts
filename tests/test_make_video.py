"""Contract tests for the shared renderer entry point (subprocess mocked, nothing renders)."""
import hashlib
import json
import subprocess

import pytest

import make_video


class Runner:
    """Records subprocess.run calls; `codes` maps call index -> return code."""

    def __init__(self, codes=None):
        self.calls, self.codes = [], codes or {}

    def __call__(self, argv, cwd=None, check=None, **kw):
        self.calls.append((list(argv), cwd))
        return subprocess.CompletedProcess(argv, self.codes.get(len(self.calls) - 1, 0))


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


@pytest.fixture
def creator(tmp_path, monkeypatch):
    monkeypatch.setattr(make_video, "CREATOR", tmp_path / "creator_v2")
    return tmp_path / "creator_v2"


def _plan_dir(tmp_path, series, lane, rid):
    _write(tmp_path / "plans" / "plan_x.json", [{"id": rid, "lane": lane, "series": series, "script": ["Một câu."]}])
    return tmp_path / "plans"


# ---- đúng renderer / cwd / tham số cho từng kênh và loại -------------------

@pytest.mark.parametrize("channel,kind,engine", [
    ("mim", "long", "casewide"), ("ck", "long", "casewide"),
    ("mim", "short", "casefile"), ("ck", "short", "casefile"), ("cl", "short", "casefile"),
    ("bud", "long", "hf_batch"), ("bud", "short", "hf_batch"),
    ("fs", "long", "hf_batch"), ("fs", "short", "hf_batch"),
    ("vsd", "short", "studio"),
])
def test_each_channel_kind_picks_registered_engine(channel, kind, engine, tmp_path, creator):
    if engine == "casewide":
        src = _write(creator / "data/long/topic-1/spec.json", {"channel": channel.upper()})
    elif engine == "casefile":
        spec = {"channel": channel, **({} if channel == "cl" else {"theme": channel})}
        src = _write(creator / f"data/stier/specs/{channel}-one.json", spec)
    elif engine == "hf_batch":
        src = _plan_dir(tmp_path, channel, kind, f"{channel}9")
    else:
        src = _write(tmp_path / "s.json", {"channel": channel, "theme": "t", "lane": "short"})
    p = make_video.plan(kind, src, only=f"{channel}9" if engine == "hf_batch" else None)
    assert (p.channel, p.kind, p.engine) == (channel, kind, engine)
    first = p.steps[0]
    if engine == "casewide":
        assert p.cwd == creator
        assert [s[-1] for s in p.steps] == ["tts", "html", "render", "final"]
        assert all(s[-2] == "topic-1" and s[1].endswith("build_long.py") for s in p.steps)
        assert p.outdir == creator / "output/long/topic-1"
    elif engine == "casefile":
        assert p.cwd == creator
        assert first[1].endswith("build.py") and first[2:] == [f"{channel}-one", "--preflight"]
        assert p.steps[1][2:] == [f"{channel}-one"]
    elif engine == "hf_batch":
        assert p.cwd == make_video.ROOT and len(p.steps) == 1
        assert first[1].endswith("hf_batch_render.py") and first[-2:] == ["--only", f"{channel}9"]
    else:
        assert p.cwd == make_video.ROOT and first[1].endswith("studio.py")
        assert first[2:3] == ["build"] and first[-3:] == ["--render", "--qa", "--strict"]


def test_theme_comes_from_spec_then_profile(creator):
    spec = _write(creator / "data/stier/specs/mim-a.json", {"channel": "mim", "theme": "mim"})
    assert make_video.plan("short", spec).theme == "mim"
    long_spec = _write(creator / "data/long/t/spec.json", {"channel": "ck"})
    assert make_video.plan("long", long_spec).theme == "chart"   # từ hồ sơ ck.theme.long


# ---- kênh lạ / thiếu kênh -----------------------------------------------------

def test_unknown_channel_and_missing_channel_fail(creator):
    spec = _write(creator / "data/long/t/spec.json", {"channel": "khong-co"})
    with pytest.raises(ValueError, match="nhận diện được kênh"):
        make_video.plan("long", spec)
    bare = _write(creator / "data/stier/specs/abc.json", {"title": "x"})
    with pytest.raises(ValueError, match="nhận diện được kênh"):
        make_video.plan("short", bare)
    with pytest.raises(ValueError, match="nhận diện được kênh"):
        make_video.plan("short", bare, channel="khong-co")


def test_profile_without_engine_for_kind_fails(tmp_path):
    spec = _write(tmp_path / "s.json", {"channel": "vsd", "theme": "t"})
    with pytest.raises(ValueError, match="dung.long.engine"):
        make_video.plan("long", spec)   # VSD chưa có engine Long


def test_conflicting_channel_flag_fails(creator):
    spec = _write(creator / "data/stier/specs/x.json", {"channel": "ck", "theme": "ck"})
    with pytest.raises(ValueError, match="không khớp"):
        make_video.plan("short", spec, channel="mim")


def test_casefile_theme_rules(creator):
    spec = _write(creator / "data/stier/specs/mim-one.json", {"channel": "mim"})
    with pytest.raises(ValueError, match="mặc định 'case'"):
        make_video.plan("short", spec)
    _write(spec, {"channel": "mim", "theme": " "})
    with pytest.raises(ValueError, match="chuỗi không rỗng"):
        make_video.plan("short", spec)
    legacy = _write(creator / "data/stier/specs/legacy-1.json", {"title": "x"})
    assert make_video.plan("short", legacy, channel="CL").channel == "cl"


# ---- --only với thư mục plan --------------------------------------------------

def test_only_requires_exact_id_lane_and_series(tmp_path):
    d = tmp_path / "plans"
    _write(d / "plan_a.json", [{"id": "bud1", "lane": "short", "series": "bud", "script": ["a"]},
                               {"id": "bud12", "lane": "short", "series": "bud", "script": ["a"]},
                               {"id": "fs1", "lane": "short", "series": "bud", "channel": "fs", "script": ["a"]}])
    with pytest.raises(ValueError, match="--only"):
        make_video.plan("short", d)                       # thiếu --only: không dựng cả lô
    with pytest.raises(ValueError, match="tiền tố"):
        make_video.plan("short", d, only="bud1")          # bud1 cũng khớp bud12
    with pytest.raises(ValueError, match="lane"):
        make_video.plan("long", d, only="bud12")
    with pytest.raises(ValueError, match="series"):
        make_video.plan("short", d, only="fs1")           # channel fs nhưng series ghi bud
    ok = make_video.plan("short", d, only="bud12")
    assert ok.channel == "bud" and ok.steps[0][-2:] == ["--only", "bud12"]


def test_only_rejected_for_single_spec(tmp_path):
    spec = _write(tmp_path / "s.json", {"channel": "vsd", "theme": "t"})
    with pytest.raises(ValueError, match="chỉ dùng với thư mục plan"):
        make_video.plan("short", spec, only="x")


# ---- cổng Short: preflight + slot ---------------------------------------------

def _short_spec(creator):
    return _write(creator / "data/stier/specs/mim-s.json", {"channel": "mim", "theme": "mim"})


def test_short_runs_preflight_before_render_and_passes_slot(creator, monkeypatch):
    run = Runner()
    monkeypatch.setattr(make_video.subprocess, "run", run)
    assert make_video.main(["short", str(_short_spec(creator)), "--slot", "2026-11-06T19:00+07:00"]) == 0
    assert len(run.calls) == 2
    assert run.calls[0][0][-1] == "--preflight" and "--slot" not in run.calls[0][0]
    assert run.calls[1][0][-2:] == ["--slot", "2026-11-06T19:00+07:00"]
    assert "--preflight" not in run.calls[1][0]
    assert all(cwd == creator for _, cwd in run.calls)


def test_short_without_slot_has_no_slot_flag(creator, monkeypatch):
    run = Runner()
    monkeypatch.setattr(make_video.subprocess, "run", run)
    make_video.main(["short", str(_short_spec(creator))])
    assert "--slot" not in run.calls[1][0]


def test_failed_preflight_never_renders(creator, monkeypatch):
    run = Runner({0: 1})
    monkeypatch.setattr(make_video.subprocess, "run", run)
    assert make_video.main(["short", str(_short_spec(creator))]) == 1
    assert len(run.calls) == 1 and run.calls[0][0][-1] == "--preflight"


def test_slot_rejected_outside_casefile(tmp_path):
    spec = _write(tmp_path / "s.json", {"channel": "vsd", "theme": "t"})
    with pytest.raises(ValueError, match="--slot"):
        make_video.plan("short", spec, slot="2026-11-06T19:00+07:00")


# ---- exit code lan ra ngoài ----------------------------------------------------

@pytest.mark.parametrize("code", [2, 7])
def test_renderer_exit_code_propagates_and_stops(code, tmp_path, monkeypatch):
    run = Runner({0: code})
    monkeypatch.setattr(make_video.subprocess, "run", run)
    d = _plan_dir(tmp_path, "bud", "short", "bud9")
    assert make_video.main(["short", str(d), "--only", "bud9"]) == code
    p = make_video.Plan("mim", "long", "casewide", None, tmp_path,
                        [["x", "tts"], ["x", "html"]], outdir=tmp_path)
    run.calls.clear()
    assert make_video.run(p) == code and len(run.calls) == 1   # dừng ở bước lỗi


# ---- manifest Long -------------------------------------------------------------

def _long_plan(tmp_path):
    return make_video.Plan("mim", "long", "casewide", None, tmp_path, [["x", "final"]], outdir=tmp_path)


def _manifest(tmp_path, state, **extra):
    body = {"schema": 1, "run_id": "r1", "state": state, "error": "boom", **extra}
    (tmp_path / "final.run.json").write_text(json.dumps(body), encoding="utf-8")


@pytest.mark.parametrize("state", ["failed", "running"])
def test_long_manifest_not_ok_fails_even_if_final_exists(state, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(make_video.subprocess, "run", Runner())
    (tmp_path / "final.mp4").write_bytes(b"old")
    _manifest(tmp_path, state)
    assert make_video.run(_long_plan(tmp_path)) == 1
    assert state in capsys.readouterr().err


def test_long_manifest_ok_passes_and_tampered_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(make_video.subprocess, "run", Runner())
    final, cap = tmp_path / "final.mp4", tmp_path / "captions.vi.srt"
    final.write_bytes(b"video")
    cap.write_bytes(b"srt")

    def sha(b):
        return hashlib.sha256(b).hexdigest()

    _manifest(tmp_path, "ok", chapters={}, error=None,
              final={"size": 5, "sha256": sha(b"video")}, captions={"size": 3, "sha256": sha(b"srt")})
    assert make_video.run(_long_plan(tmp_path)) == 0
    final.write_bytes(b"VIDEO")   # cùng kích thước, khác nội dung
    assert make_video.run(_long_plan(tmp_path)) == 1


def test_long_final_step_failure_skips_manifest_check(tmp_path, monkeypatch):
    monkeypatch.setattr(make_video.subprocess, "run", Runner({0: 4}))
    monkeypatch.setattr(make_video, "final_problems", lambda od: pytest.fail("kiểm sau bước lỗi"))
    assert make_video.run(_long_plan(tmp_path)) == 4


# ---- dry-run -------------------------------------------------------------------

def test_dry_run_prints_and_executes_nothing(creator, monkeypatch, capsys):
    monkeypatch.setattr(make_video.subprocess, "run", lambda *a, **k: pytest.fail("renderer executed"))
    argv = ["short", str(_short_spec(creator)), "--dry-run", "--slot", "2026-11-06T19:00+07:00"]
    assert make_video.main(argv) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["channel"] == "mim" and out["theme"] == "mim" and out["cwd"] == str(creator)
    assert len(out["commands"]) == 2 and out["commands"][1][-2] == "--slot"


def test_bad_input_exits_nonzero_via_parser_error(tmp_path):
    with pytest.raises(SystemExit) as exc:
        make_video.main(["short", str(tmp_path / "nope.json"), "--dry-run"])
    assert exc.value.code == 2


# ---- hf_batch thoát 0 mà không dựng gì ------------------------------------------

def test_hf_placeholder_or_empty_script_rejected(tmp_path):
    for script in ([], make_video.PLACEHOLDER_SCRIPT, None):
        row = {"id": "bud9", "lane": "short", "series": "bud"}
        if script is not None:
            row["script"] = script
        _write(tmp_path / "plans" / "plan_x.json", [row])
        with pytest.raises(ValueError, match="script"):
            make_video.plan("short", tmp_path / "plans", only="bud9")


def test_placeholder_constant_matches_hf_batch_source():
    src = (make_video.ROOT / "hf_batch_render.py").read_text(encoding="utf-8")
    assert f"PLACEHOLDER_SCRIPT = {json.dumps(make_video.PLACEHOLDER_SCRIPT, ensure_ascii=False)}" in src


def test_hf_existing_output_refused_unless_allowed(tmp_path):
    d = _plan_dir(tmp_path, "bud", "short", "bud9")
    out = d / "out" / "bud9.mp4"
    out.parent.mkdir()
    out.write_bytes(b"old")
    with pytest.raises(ValueError, match="đã có"):
        make_video.plan("short", d, only="bud9")
    assert make_video.plan("short", d, only="bud9", allow_existing=True).allow_existing


def test_hf_exit_zero_without_fresh_output_fails(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(make_video.subprocess, "run", Runner())
    d = _plan_dir(tmp_path, "bud", "short", "bud9")
    p = make_video.plan("short", d, only="bud9")
    assert make_video.run(p) == 1                       # không có mp4
    out = d / "out" / "bud9.mp4"
    out.parent.mkdir()
    out.write_bytes(b"x")
    import os
    os.utime(out, (1, 1))                               # file cũ, renderer "bỏ qua"
    assert make_video.run(p) == 1
    assert "không được dựng lại" in capsys.readouterr().err
    os.utime(out, None)                                 # vừa ghi
    assert make_video.run(p) == 0
    os.utime(out, (1, 1))
    p.allow_existing = True
    assert make_video.run(p) == 0


# ---- theme casefile phải khớp hồ sơ ---------------------------------------------

def test_casefile_spec_theme_must_match_profile(creator):
    spec = _write(creator / "data/stier/specs/mim-t.json", {"channel": "mim", "theme": "ck"})
    with pytest.raises(ValueError, match="không khớp theme Short"):
        make_video.plan("short", spec)
    _write(spec, {"channel": "mim", "theme": "mim"})
    p = make_video.plan("short", spec)
    assert (p.theme_spec, p.theme_profile) == ("mim", "mim")
    cl = _write(creator / "data/stier/specs/x1.json", {"channel": "cl", "theme": "mim"})
    with pytest.raises(ValueError, match="không khớp theme Short"):
        make_video.plan("short", cl)


def test_casefile_theme_allowed_list(creator, monkeypatch):
    real = make_video.channel_profile.load
    monkeypatch.setattr(make_video.channel_profile, "load",
                        lambda i: {**real(i), "theme": {**real(i).get("theme", {}), "short_allowed": ["ck"]}})
    spec = _write(creator / "data/stier/specs/mim-t.json", {"channel": "mim", "theme": "ck"})
    assert make_video.plan("short", spec).theme_spec == "ck"


def test_dry_run_prints_both_themes(creator, monkeypatch, capsys):
    assert make_video.main(["short", str(_short_spec(creator)), "--dry-run"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["theme_spec"] == "mim" and out["theme_profile"] == "mim"


# ---- Long: chặn trước khi tốn TTS ----------------------------------------------

def _long_topic(creator, scenes, imgs=None):
    _write(creator / "data/long/tp/spec.json", {"channel": "mim", "imgs": imgs or {}})
    _write(creator / "data/long/tp/ch01.json", {"scenes": scenes})
    return creator / "data/long/tp/spec.json"


def test_long_without_reviewed_clip_sheet_blocks_before_tts(creator, monkeypatch, capsys):
    spec = _long_topic(creator, [{"type": "x", "vid": "123", "ms": 1}])
    p = make_video.plan("long", spec)
    assert any("clip: thiếu dấu" in b for b in p.blockers)
    run = Runner()
    monkeypatch.setattr(make_video.subprocess, "run", run)
    assert make_video.run(p) == 1 and run.calls == []   # chưa gọi bước nào, kể cả tts
    assert "CHẶN" in capsys.readouterr().err


def test_long_stale_and_current_clip_mark(creator):
    spec = _long_topic(creator, [{"type": "x", "vid": "123", "ms": 1}])
    clip = make_video._long_module("clip_sheet")
    mark = clip.ok_path(creator / "output/long/tp")
    mark.parent.mkdir(parents=True)
    mark.write_text("0" * 64, encoding="utf-8")
    assert any("đã cũ" in b for b in make_video.plan("long", spec).blockers)
    mark.write_text(clip.uses_hash(clip.clip_uses(creator / "data/long/tp")), encoding="utf-8")
    assert make_video.plan("long", spec).blockers == []


def test_long_unreviewed_images_block(creator):
    spec = _long_topic(creator, [{"type": "x", "img": "k"}], imgs={"k": "File:a.jpg"})
    assert any(b.startswith("ảnh: thiếu dấu") for b in make_video.plan("long", spec).blockers)


def test_long_takes_without_picks_blocks(creator):
    spec = _long_topic(creator, [{"type": "x"}])
    tts = creator / "output/long/tp/tts"
    tts.mkdir(parents=True)
    assert make_video.plan("long", spec).blockers == []   # chưa chấm take: pick không bắt buộc
    (tts / "takes.json").write_text("[]", encoding="utf-8")
    assert any("pick" in b for b in make_video.plan("long", spec).blockers)
    (tts / "picks.json").write_text("{}", encoding="utf-8")
    assert make_video.plan("long", spec).blockers == []


def test_dry_run_exits_1_when_blocked(creator, monkeypatch, capsys):
    spec = _long_topic(creator, [{"type": "x", "vid": "1"}])
    assert make_video.main(["long", str(spec), "--dry-run"]) == 1
    assert json.loads(capsys.readouterr().out)["blockers"]


def test_path_comparison_resolves_both_sides(tmp_path, monkeypatch):
    monkeypatch.setattr(make_video, "CREATOR", tmp_path / "x" / ".." / "creator_v2")
    spec = _write(tmp_path / "creator_v2/data/long/tp/spec.json", {"channel": "mim"})
    _write(tmp_path / "creator_v2/data/long/tp/ch01.json", {"scenes": []})
    assert make_video.plan("long", spec).channel == "mim"
