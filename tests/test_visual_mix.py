import copy

import pytest

import hf_batch_render as HBR
from tools import visual_mix as VM


def _scene(kind="photo", seconds=1, image=None, style=None):
    return dict(kind=kind, t0=0, t1=seconds, image=image, style=style)


def _levels(metrics, **kwargs):
    return [level for level, msg in VM.issues(metrics, is_new=True, is_long=True, **kwargs)
            if msg.startswith("chữ")]


@pytest.mark.parametrize("percent,levels", [(12, []), (12.01, ["WARN"]), (15, ["WARN"]), (15.01, ["ERROR"])])
def test_visual_mix_text_seconds_boundaries(percent, levels):
    # Deliberately two scenes: the budget is duration, never scene count.
    metrics = VM.measure([_scene("slam", percent), _scene("map", 100-percent)])
    assert _levels(metrics) == levels
    assert metrics["scenes"] == 2


@pytest.mark.parametrize("count,level", [(4, None), (5, "WARN"), (6, "WARN"), (7, "ERROR")])
def test_visual_mix_repeat_boundaries(count, level):
    metrics = VM.measure([_scene(image="a.jpg") for _ in range(count)])
    findings = [(severity, msg) for severity, msg in VM.issues(metrics, is_new=True, is_long=True)
                if msg.startswith("ảnh tĩnh")]
    assert [severity for severity, msg in findings] == ([level] if level else [])


def test_visual_mix_styles_are_separate_reuse_identities_but_not_new_files():
    metrics = VM.measure([_scene(image="./a.jpg") for _ in range(4)] +
                         [_scene(image="a.jpg", style="woodcut") for _ in range(4)] +
                         [_scene(image="a.jpg", style="papercut")])
    assert metrics["max_repeat"] == 4
    assert metrics["unique_images"] == 1
    assert not any("ảnh tĩnh" in msg for _, msg in VM.issues(metrics, is_new=True, is_long=True))


@pytest.mark.parametrize("is_new,is_long", [(False, True), (True, False), (False, False)])
def test_visual_mix_old_and_short_only_print_numbers(is_new, is_long):
    metrics = VM.measure([_scene("kinetic", 100)])
    assert VM.issues(metrics, is_new=is_new, is_long=is_long) == []
    assert "100.00%" in VM.format_table(metrics)


def test_visual_mix_reason_excuses_only_text_not_repeated_images():
    metrics = VM.measure([_scene("kinetic", 100)] + [_scene(image="a.jpg") for _ in range(7)])
    findings = VM.issues(metrics, is_new=True, is_long=True, reason="đọc nguyên văn")
    assert ("WARN", next(msg for _, msg in findings if msg.startswith("chữ"))) in findings
    assert ("ERROR", next(msg for _, msg in findings if msg.startswith("ảnh tĩnh"))) in findings
    assert _levels(metrics, reason="  ") == ["ERROR"]


def test_visual_mix_text_definition_and_data_graphics():
    kinds = ["kinetic", "slam", "quote", "question", "word", "ask", "chữ khoá", "list", "date", "counter"]
    graphics = ["chapter", "chương", "lookup", "ledger", "stat", "compare", "wheel", "bars", "map", "timeline"]
    metrics = VM.measure([_scene(k, 1) for k in kinds + graphics] +
                         [_scene("word", 100, "background.jpg")])
    assert metrics["text_seconds"] == len(kinds)
    assert metrics["by_kind"]["word"]["seconds"] == 101


def test_visual_mix_fullscreen_text_beds_do_not_evade_budget():
    metrics = VM.measure([_scene(k, 10, "bed.jpg") for k in VM.FULLSCREEN_TEXT_KINDS])
    assert metrics["text_share"] == 1
    assert metrics["max_repeat"] == 4


def test_visual_mix_no_images_density_is_warning_only_and_empty_is_safe():
    metrics = VM.measure([_scene("bars", 60)])
    assert VM.issues(metrics, is_new=True, is_long=True) == [("WARN", "0.00 ảnh khác nhau/phút (< 4)")]
    assert VM.measure([])["text_share"] == 0


def _segments(n, step=3):
    return [{"start": i*step, "end": (i+1)*step} for i in range(n)]


def test_visual_mix_fs_hold_overlay_visuals_video_and_no_mutation():
    row = {"script": ["Nội dung."] * 6,
           "media": {"1": {"kind": "local", "path": "a.jpg", "crop": [0, 0]},
                     "4": {"kind": "local", "path": "a.jpg", "cine": {}},
                     "6": {"kind": "local", "path": "movie.mp4"}},
           "visuals": {"2": {"type": "ask", "text": "Phủ ảnh", "overlay": True},
                       "5": {"type": "list", "items": []}}}
    before = copy.deepcopy(row)
    scenes = HBR.visual_mix_scenes(row, _segments(6))
    metrics = VM.measure(scenes)
    assert metrics["text_seconds"] == 3
    assert metrics["max_repeat"] == 2
    assert metrics["unique_images"] == 1
    assert metrics["scenes"] == 4  # held 1..3, new use 4, list 5, video 6
    assert row == before


def test_visual_mix_fs_visual_cont_heading_and_figures_are_not_text():
    row = {"script": ["**Chương**", "Một.", "Hai.", "Ba."],
           "visuals": {"2": {"type": "ledger", "until": 3}},
           "figures": {"4": {"type": "person"}}}
    metrics = VM.measure(HBR.visual_mix_scenes(row, _segments(4)))
    assert metrics["text_share"] == 0
    assert metrics["scenes"] == 3


@pytest.mark.parametrize("extra,new", [({"day": "2026-11-17"}, False),
                                      ({"day": "2026-11-18"}, True),
                                      ({}, False), ({"tts": {"pause_ctx": True}}, True),
                                      ({"pause_ctx": True}, True),
                                      ({"day": "2026-11-17", "pause_ctx": True}, False)])
def test_visual_mix_fs_newness(extra, new):
    assert HBR.visual_mix_is_new({"layout_policy": "v2", **extra}) is new
    assert not HBR.visual_mix_is_new(extra)


def test_visual_mix_fs_estimate_and_gate_prints_and_blocks(capsys):
    row = {"script": ["Đây là một **cụm từ**."], "lane": "long", "layout_policy": "v2", "day": VM.VISUAL_MIX_SINCE}
    assert HBR.visual_mix_scenes(row)[0]["t1"] == pytest.approx(5 / 185 * 60)
    assert HBR.visual_mix_check(row)
    assert "ước" in capsys.readouterr().out
    assert HBR.visual_mix_check({**row, "text_budget_reason": "trích đọc"}) == []
    assert HBR.visual_mix_check({**row, "lane": "short"}) == []
    with pytest.raises(ValueError, match="segments"):
        HBR.visual_mix_scenes(row, [])


def test_visual_mix_chapter_render_blocks_before_renderer_even_without_strict(tmp_path, monkeypatch):
    import json
    import soundfile
    row = {"id": "fake", "script": ["Câu **chữ khoá**."], "lane": "long",
           "layout_policy": "v2", "day": VM.VISUAL_MIX_SINCE}
    wav = tmp_path / "fake.wav"
    wav.with_suffix(".json").write_text(json.dumps({"segments": _segments(1), "duration_s": 3}), encoding="utf-8")
    monkeypatch.setattr(soundfile, "read", lambda *a, **kw: ([], 48000))
    monkeypatch.setattr(HBR, "layout_v2_choices", lambda *a: None)
    monkeypatch.setattr(HBR, "chapter_spans", lambda *a, **kw: [])
    monkeypatch.setattr(HBR, "pacing", lambda *a: ({}, []))
    monkeypatch.setattr(HBR.subprocess, "run", lambda *a, **kw: pytest.fail("renderer must not run"))
    ok, note = HBR.render_chapters(row, tmp_path, "draft", tmp_path / "fake.txt", wav, "")
    assert not ok and "visual_mix: chữ" in note
