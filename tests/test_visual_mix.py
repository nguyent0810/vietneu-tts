import copy

import pytest

import hf_batch_render as HBR
from tools import visual_mix as VM


def _scene(kind="photo", seconds=1, image=None, style=None):
    return dict(kind=kind, t0=0, t1=seconds, image=image, style=style)


def _levels(metrics, **kwargs):
    return [level for level, msg in VM.issues(metrics, is_new=True, is_long=True, **kwargs)
            if msg.startswith("chữ")]


@pytest.mark.parametrize("percent,levels", [(10, []), (10.01, ["ERROR"]), (15, ["ERROR"]), (15.01, ["ERROR"])])
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


def test_visual_mix_tracks_stock_by_duration_and_prints_shares():
    scenes = [_scene("photo", 15, "stock.jpg"), _scene("video", 15), _scene("photo", 70)]
    scenes[0]["stock_kind"] = "image"
    scenes[1]["stock_kind"] = "video"
    metrics = VM.measure(scenes)
    assert metrics["stock_image_share"] == .15
    assert metrics["stock_video_share"] == .15
    assert "Pexels/stock video 15.00%" in VM.format_table(metrics)


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


def _video_findings(metrics, **kwargs):
    return [(level, msg) for level, msg in VM.issues(metrics, is_new=True, is_long=True, **kwargs)
            if msg.startswith(("video_share", "clip/pano"))]


def test_video_floor_12_minutes_one_clip_warns_only():
    metrics = VM.measure([_scene("video", 12), _scene("photo", 708, "a.jpg")])
    assert metrics["video_seconds"] == 12
    assert metrics["video_share"] == pytest.approx(12 / 720)
    assert metrics["clip_count"] == 1 and metrics["pano_count"] == 0
    findings = _video_findings(metrics)
    assert len(findings) == 2
    assert all(level == "WARN" for level, _ in findings)
    assert "< 4 cảnh" in findings[1][1]
    assert len(_video_findings(metrics, reason="trích đọc")) == 2


@pytest.mark.parametrize("seconds,clip_seconds,count,n_warn", [
    (599, 0, 0, 0), (600, 0, 0, 2), (720, 72, 4, 0),
    (720, 71.99, 4, 1), (720, 72, 3, 1), (721, 73, 4, 1),
])
def test_video_floor_duration_share_and_count_boundaries(seconds, clip_seconds, count, n_warn):
    scenes = [_scene("pano", clip_seconds / count, f"wide{i}.jpg") for i in range(count)]
    metrics = VM.measure(scenes + [_scene("photo", seconds - clip_seconds, "still.jpg")])
    assert len(_video_findings(metrics)) == n_warn
    assert metrics["clip_count"] == 0
    assert metrics["pano_count"] == count


@pytest.mark.parametrize("extra", [{"day": "2026-11-17"}, {"lane": "short"}])
def test_video_floor_old_or_short_not_warned(extra, capsys):
    row = {"script": ["Nội dung."], "media": {"1": {"kind": "local", "path": "a.jpg"}},
           "lane": "long", "layout_policy": "v2", "day": VM.VISUAL_MIX_SINCE, **extra}
    assert HBR.visual_mix_check(row, [{"start": 0, "end": 720}]) == []
    printed = capsys.readouterr().out
    assert "video_share 0.00%" in printed
    assert "visual_mix WARN: video_share" not in printed
    assert "visual_mix WARN: clip/pano" not in printed


def test_video_floor_l01_stills_push_in_not_video_and_never_blocks(capsys):
    row = {"script": ["Nội dung."] * 4, "lane": "long", "layout_policy": "v2", "day": VM.VISUAL_MIX_SINCE,
           "media": {str(i): {"kind": "local", "path": f"a{i}.jpg", "cine": {"cam": "push_in"}}
                     for i in range(1, 5)}}
    metrics = VM.measure(HBR.visual_mix_scenes(row, _segments(4, 180)))
    assert metrics["video_share"] == 0 and metrics["clip_count"] == 0
    assert HBR.visual_mix_check(row, _segments(4, 180)) == []
    printed = capsys.readouterr().out
    assert "visual_mix WARN: video_share" in printed
    assert "visual_mix WARN: clip/pano" in printed


@pytest.mark.parametrize("media", [{"kind": "local", "path": "rock.mp4"},
                                   {"kind": "pdvideo", "ref": "ia:rock"},
                                   {"kind": "commons", "ref": "File:Rock.webm"},
                                   {"kind": "video", "query": "rock"}])
def test_video_measurement_ignores_source_and_merges_held_clips(media):
    row = {"script": ["Một.", "Hai.", "Ba."], "media": {"1": media}}
    metrics = VM.measure(HBR.visual_mix_scenes(row, _segments(3)))
    assert metrics["video_seconds"] == 9
    assert metrics["video_share"] == 1
    assert metrics["clip_count"] == 1


def test_pano_counts_full_hold_and_still_identity_and_new_use():
    row = {"script": ["Một.", "Hai.", "Ba."],
           "media": {"1": {"kind": "local", "path": "wide.jpg", "pan": {"dir": "ltr", "stops": [{"line": 1, "x": 0}]}},
                     "3": {"kind": "local", "path": "wide.jpg", "pan": {"dir": "rtl", "stops": [{"line": 3, "x": 1}]}}}}
    metrics = VM.measure(HBR.visual_mix_scenes(row, _segments(3)))
    assert metrics["video_share"] == 1
    assert metrics["pano_count"] == 2 and metrics["clip_count"] == 0
    assert metrics["unique_images"] == 1 and metrics["max_repeat"] == 2


def test_video_measurement_overlay_preserves_clip_fullscreen_visual_interrupts():
    row = {"script": ["Một.", "Hai.", "Ba."], "media": {"1": {"kind": "local", "path": "rock.mp4"}},
           "visuals": {"2": {"type": "ask", "overlay": True}, "3": {"type": "map"}}}
    metrics = VM.measure(HBR.visual_mix_scenes(row, _segments(3)))
    assert metrics["video_seconds"] == 6
    assert metrics["clip_count"] == 1


def test_video_measurement_word_cuts_and_signed_url():
    row = {"script": ["Anh nhìn đá rơi."], "media": {"1": {"kind": "local", "path": "still.jpg", "cuts": [
        {"at": "đá", "kind": "local", "path": "https://example.com/Rock Fall.MP4?download=1"}]}}}
    segs = [{"start": 0, "end": 10, "words": [{"w": "Anh", "t": 0, "d": 2},
            {"w": "nhìn", "t": 2, "d": 2}, {"w": "đá", "t": 4, "d": 3}, {"w": "rơi", "t": 7, "d": 3}]}]
    metrics = VM.measure(HBR.visual_mix_scenes(row, segs))
    assert metrics["video_seconds"] == 6
    assert metrics["video_share"] == .6
    assert metrics["clip_count"] == 1


def test_parallax_counts_in_video_share():
    row = {"script": ["Một.", "Hai.", "Ba."],
           "media": {"1": {"kind": "local", "path": "a.jpg", "layout": "depth"},
                     "2": {"kind": "local", "path": "b.jpg", "cine": {"cam": "push_in"}},
                     "3": {"kind": "local", "path": "c.jpg", "cine": {"cam": "dolly_parallax"}}}}
    metrics = VM.measure(HBR.visual_mix_scenes(row, _segments(3)))
    assert metrics["parallax_count"] == 2 and metrics["clip_count"] == 0 and metrics["pano_count"] == 0
    assert metrics["video_share"] == pytest.approx(2 / 3)
