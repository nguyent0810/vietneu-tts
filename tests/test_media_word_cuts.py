"""Word-cut shots share one clock between pacing, layout, captions and render."""
import copy
import json
from pathlib import Path

import pytest

import hf_batch_render as B
import hyperframes_bridge as HB


def sample():
    text = " ".join(f"tiếng{i}" for i in range(40))
    words = [{"w": f"tiếng{i}", "t": 10 + i * .325, "d": .325} for i in range(40)]
    row = {"id": "test_cuts", "script": [text], "series": "bud", "lane": "long",
           "media": {"1": {"kind": "local", "path": "base.jpg", "layout": "full", "cuts": [
               {"at": f"tiếng{i}", "kind": "local", "path": f"{i}.jpg", "layout": "full"}
               for i in (10, 20, 30)]}}}
    return row, [{"start": 10., "end": 23., "words": words}]


def test_forty_syllables_at_second_ten_three_cuts_pass_and_uncut_fails():
    row, segs = sample()
    before = copy.deepcopy(row)
    assert B.pace_gate_issues(row, segs) == []
    shots = B.visual_mix_scenes(row, segs)
    assert [s["t1"] - s["t0"] for s in shots] == pytest.approx([3.25] * 4)
    assert len({s["image"] for s in shots}) == 4
    assert row == before
    row["media"]["1"].pop("cuts")
    assert any("tĩnh dài 13.0s" in e for e in B.pace_gate_issues(row, segs))


def test_real_word_timing_and_estimate_are_explicit_and_no_overlapping_shots():
    row, segs = sample()
    segs[0]["words"][10]["t"] = 13.1879  # deliberately different from proportional clock
    lines, media = B._shot_plan(row, segs)
    assert [ln["sentence_id"] for ln in lines] == [1, 2, 3, 4]
    assert [ln["source_sentence_id"] for ln in lines] == [1] * 4
    assert lines[1]["start"] == segs[0]["words"][10]["t"]
    assert max(abs(ln["start"] - segs[0]["words"][i]["t"])
               for ln, i in zip(lines[1:], [10, 20, 30])) <= 1/30
    assert all(a["end"] == b["start"] for a, b in zip(lines, lines[1:]))
    assert all(ln["word_timing_source"] == "manifest" for ln in lines)
    assert all(len(ln["caption_words"]) == 40 for ln in lines)
    assert HB.media_holds(lines, {int(k) for k in media}, media_specs=media) == {i: i for i in range(4)}
    segs[0].pop("words")
    estimated, _ = B._shot_plan(row, segs)
    assert estimated[1]["start"] == pytest.approx(13.25, abs=1/30)
    assert estimated[0]["word_timing_source"] == "estimated_syllables"


@pytest.mark.parametrize("cuts", ["bad", [{"at": "missing", "kind": "image", "query": "q"}],
                                   [{"at": "tiếng0"}], [{"at": "tiếng20"}, {"at": "tiếng10"}],
                                   [{"at": 3}], [{"at": "tiếng10", "cuts": []}]])
def test_invalid_anchors_fail_closed(cuts):
    row, segs = sample()
    row["media"]["1"]["cuts"] = cuts
    with pytest.raises(HB.HyperFramesError):
        B._shot_plan(row, segs)


def test_repeated_words_and_phrases_match_after_previous_anchor():
    row = {"script": ["Nghe Lá, **rơi** qua lá rơi bên lá rơi."],
           "media": {1: {"kind": "image", "query": "a", "cuts": [
               {"at": "lá rơi", "kind": "image", "query": "b"},
               {"at": "LÁ RƠI", "kind": "image", "query": "c"}]}}}
    lines, _ = B._shot_plan(row, [{"start": 0, "end": 8}])
    assert [ln["words"][0]["w"] for ln in lines] == ["Nghe", "Lá,", "lá"]
    assert lines[1]["start"] < lines[2]["start"]


def test_last_shot_holds_and_following_visual_and_pan_references_remap():
    row, segs = sample()
    row["script"] += ["Tiếp theo.", "Mở sơ đồ.", "Đóng sơ đồ."]
    row["visuals"] = {"3": {"type": "list", "items": [{"at": 4, "text": "mục"}], "until": 4}}
    segs += [{"start": 23, "end": 24}, {"start": 24, "end": 25}, {"start": 25, "end": 26}]
    lines, media = B._shot_plan(row, segs)
    assert HB.media_holds(lines, {int(k) for k in media}, media_specs=media)[3] == 4
    assert lines[5]["visual"]["items"][0]["at"] == 7
    assert lines[5]["visual"]["until"] == 7
    assert lines[6]["visual_cont"] == 6
    scenes = B.visual_mix_scenes(row, segs)
    assert scenes[3]["t1"] == 24
    assert scenes[-1]["t1"] == 26


def test_each_subshot_gets_v2_and_presets_survive_chapter_handoff(tmp_path):
    row, segs = sample()
    row["layout_policy"] = "v2"
    for spec in [row["media"]["1"], *row["media"]["1"]["cuts"]]:
        spec.pop("layout")
    chosen = B.layout_v2_choices(row, segs)
    assert len(chosen[1]["cuts"]) == 3
    assert "4 ảnh" in HB.layout_report(chosen, row["media"])
    assert all(c["layout"] in {"full", "depth"} for c in [chosen[1], *chosen[1]["cuts"]])
    lines, media = B._shot_plan(row, segs)
    script, manifest = tmp_path / "script.txt", tmp_path / "tts.json"
    script.write_text(row["script"][0])
    manifest.write_text(json.dumps({"segments": segs}))
    opts = B.layout_v2_opts({}, row, chosen)
    auto, cine = HB._resolve_render_layouts(media, "demo", "inkwash_long", opts,
                                           script, manifest, {}, "bud", lines=lines)
    assert len(auto) == 4
    for ln, choice in zip(lines, [chosen[1], *chosen[1]["cuts"]]):
        assert auto[ln["sentence_id"]] == choice["layout"]
    shifted = B._shift_word_segment(segs[0], 10)
    assert shifted["words"][10]["t"] == pytest.approx(3.25)
    assert segs[0]["words"][10]["t"] == 13.25


def test_actual_timestamps_reach_build_lines(tmp_path):
    row, segs = sample()
    script, manifest = tmp_path / "script.txt", tmp_path / "tts.json"
    script.write_text(row["script"][0])
    manifest.write_text(json.dumps({"segments": segs}))
    lines = HB.build_lines(script, manifest)
    assert lines[0]["words"][10]["t"] == segs[0]["words"][10]["t"]
    assert lines[0]["word_timing_source"] == "manifest"


def test_mixed_clip_static_moving_limits_and_source_line_errors():
    row, segs = sample()
    cut = row["media"]["1"]["cuts"][0]
    cut.update(path="clip.mp4")
    for i in range(10, 20):
        segs[0]["words"][i]["t"] = 13.25 + (i - 10) * .475
    for i in range(20, 30):
        segs[0]["words"][i]["t"] = 18 + (i - 20) * .175
    assert not any("có chuyển động" in e for e in B.pace_gate_issues(row, segs))
    cut["path"] = "still.jpg"
    assert not any("tĩnh dài" in e for e in B.pace_gate_issues(row, segs))


def test_byte_duplicate_cut_rejected_in_bridge(tmp_path, monkeypatch):
    from PIL import Image
    project = tmp_path / "hf"
    compositions = project / "compositions"
    compositions.mkdir(parents=True)
    source = Path(HB.__file__).parent / "hyperframes_short/compositions/inkwash_long.html"
    (compositions / "inkwash_long.html").write_text(source.read_text())
    assets = project / "assets"
    assets.mkdir()
    image = assets / "same.jpg"
    Image.new("RGB", (160, 90), "green").save(image)
    monkeypatch.setattr(HB, "HF_PROJECT", project)
    monkeypatch.setattr(HB, "HF_ASSETS", assets)
    monkeypatch.setattr(HB, "resolve_media", lambda *args, **kwargs: (image, "same", "test", ""))
    row, segs = sample()
    script, wav = tmp_path / "script.txt", tmp_path / "audio.wav"
    script.write_text(row["script"][0])
    wav.with_suffix(".json").write_text(json.dumps({"segments": segs, "duration_s": 23}))
    with pytest.raises(HB.HyperFramesError, match="trùng hệt"):
        HB.render(script, wav, "bud", tmp_path / "test.mp4", style="inkwash_long", lane="long", media=row["media"])


@pytest.mark.parametrize("short_shots,cam", [(False, "push_in"), (True, "rack_focus"), (True, "pan_left")])
def test_real_engine_camera_tweens_never_overlap_or_cross_the_next_shot(short_shots, cam):
    import os
    import subprocess
    nodes = sorted((Path.home() / ".nvm/versions/node").glob("v22.*/bin/node"))
    modules = list((Path.home() / ".npm/_npx").glob("*/node_modules/linkedom"))
    local_dom = Path(HB.__file__).parent / "output/079_media_word_cuts/node/node_modules/linkedom"
    if local_dom.is_dir():
        modules.append(local_dom)
    if not nodes or not modules:
        pytest.skip("Node 22 + cached HyperFrames DOM dependency required")
    row, segs = sample()
    if short_shots:
        segs[0]["end"] = 12
        for i, word in enumerate(segs[0]["words"]):
            word.update(t=10 + i*.05, d=.05)
    lines, _ = B._shot_plan(row, segs)
    for ln in lines:
        ln["media"] = {"layout": "full"}
    lines[1]["media"]["cine"] = {"cam": cam, "transition_in": "cut"}
    lines[3]["media"]["layout"] = "polaroid"
    # Final shot holds into a normal narration line: no second camera on it.
    hold_end = segs[0]["end"] + 2
    lines[-1]["media_end"] = hold_end
    lines.append({"sentence_id": 5, "start": segs[0]["end"], "end": hold_end, "words": [], "media_cont": 4})
    proc = subprocess.run([str(nodes[-1]), str(Path(__file__).parent / "fixtures/media_word_cuts_engine.cjs")],
                          input=json.dumps({"lines": lines, "root": str(Path(HB.__file__).parent)}),
                          text=True, capture_output=True, env={**os.environ, "HF_TEST_LINKEDOM": str(modules[0])})
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["captions"][:4] == [40, 0, 0, 0]
    cameras = data["cameras"]
    assert {c["target"] for c in cameras} == {f"mediaclip{i}" for i in range(1, 5)}
    for camera in cameras:
        owner = lines[int(camera["target"].replace("mediaclip", "")) - 1]
        assert camera["start"] >= owner["start"]
        assert camera["end"] <= owner.get("media_end", owner["end"]) + 1e-8
    for i, a in enumerate(cameras):
        for b in cameras[i + 1:]:
            common = set(a["props"]) & set(b["props"]) & {"scale", "x", "y", "xPercent", "yPercent", "rotation"}
            if a["target"] == b["target"] and common:
                assert min(a["end"], b["end"]) <= max(a["start"], b["start"]) + 1e-8


def test_opening_counts_cut_images_and_checks_refs():
    row, segs = sample()
    errors, _ = B.opening_gate(row, segs)
    assert any("O3:" in e and "4 hình" in e for e in errors)
    row["media"]["1"]["cuts"][1]["path"] = "images/refs/actor.jpg"
    errors, _ = B.opening_gate(row, segs)
    assert any("O5:" in e for e in errors)


def test_chapter_cache_tracks_cut_bytes_and_word_clock(tmp_path, monkeypatch):
    row, segs = sample()
    row["style"] = "inkwash_long"
    monkeypatch.setattr(B, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(B, "_engine_sig", lambda: "test")
    cut = row["media"]["1"]["cuts"][0]
    asset = tmp_path / "image.jpg"
    asset.write_bytes(b"first image")
    cut["path"] = "image.jpg"
    key = B.chapter_key(row, 0, 1, 10, 23, "looks", segments=segs)
    asset.write_bytes(b"new image")
    key2 = B.chapter_key(row, 0, 1, 10, 23, "looks", segments=segs)
    assert key != key2
    segs[0]["words"][10]["t"] += .05
    assert B.chapter_key(row, 0, 1, 10, 23, "looks", segments=segs) != key2
    assert "_sig" not in cut


def test_prepare_only_builds_four_real_media_tags_and_preserves_subtitles(tmp_path, monkeypatch):
    from PIL import Image
    project = tmp_path / "hf"
    compositions = project / "compositions"
    compositions.mkdir(parents=True)
    source = Path(HB.__file__).parent / "hyperframes_short/compositions/inkwash_long.html"
    (compositions / "inkwash_long.html").write_text(source.read_text())
    assets = project / "assets"
    assets.mkdir()
    for i, color in enumerate(["red", "green", "blue", "yellow"], 1):
        Image.new("RGB", (160, 90), color).save(assets / f"{i}.jpg")
    monkeypatch.setattr(HB, "HF_PROJECT", project)
    monkeypatch.setattr(HB, "HF_ASSETS", assets)
    monkeypatch.setattr(HB, "resolve_media", lambda spec, sid, *a, **k: (assets / f"{sid}.jpg", str(sid), "test", ""))
    # No renderer, audio generator or network may run in prepare_only.
    monkeypatch.setattr(HB.subprocess, "run", lambda *a, **k: pytest.fail("prepare_only launched subprocess"))
    row, segs = sample()
    script, wav = tmp_path / "script.txt", tmp_path / "audio.wav"
    script.write_text(row["script"][0])
    wav.with_suffix(".json").write_text(json.dumps({"segments": segs, "duration_s": 23}))
    result = HB.render(script, wav, "bud", tmp_path / "test.mp4", style="inkwash_long", lane="long",
                       media=row["media"], opts={"prepare_only": True})
    html = Path(result["composition"]).read_text()
    variables = json.loads(Path(result["variables"]).read_text())
    lines = json.loads(variables["lines"])
    assert html.count('id="mediaclip') == 4
    assert result["prepared"] and not (tmp_path / "test.mp4").exists()
    assert [ln["start"] for ln in lines] == [10, 13.25, 16.5, 19.75]
    assert lines[0]["caption_end"] == 23
    assert all(len(ln["caption_words"]) == 40 for ln in lines)


def test_media_sheet_includes_every_cut(tmp_path, monkeypatch):
    import hf_media_sheet as sheet
    row, _ = sample()
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps([row]))
    seen = []
    monkeypatch.setattr(sheet, "preview", lambda spec, domain: (seen.append(spec["path"]), "test"))
    monkeypatch.setattr(sheet, "sheet", lambda items, out: items)
    items = sheet.plan_sheet(plan, row["id"])
    assert len(items) == 4 and len(set(seen)) == 4
