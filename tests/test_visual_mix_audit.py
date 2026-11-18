"""Audit semantics only: no assets, renderer, network, or production writes."""
import pytest

from tools.visual_mix_audit import Audit, aggregate, classify_studio, metrics, spoken_tokens, studio_scenes


@pytest.mark.parametrize("device", ["quote", "close", "source_card", "hook_slam"])
def test_fullscreen_words_do_not_hide_behind_decorative_photo(device):
    assert classify_studio({"device": device, "img": "photo.jpg"})[0] == "text"


@pytest.mark.parametrize("device", ["split", "board", "ledger", "month_sheet"])
def test_intentional_lookup_is_separate_from_filler(device):
    assert classify_studio({"device": device})[0] == "lookup"


def test_loop_and_unequal_durations_use_seconds_not_scene_counts():
    spec = {"scenes": [{"device": "quote"}, {"device": "split"}], "loop": True}
    plan = {"windows": [[0, 1], [1, 10], [10, 10.5]], "devices": ["quote", "split", "quote"]}
    m = metrics(studio_scenes(spec, plan))
    assert m["text_share"] == pytest.approx(1.5 / 10.5)
    assert m["text_scene_share"] == pytest.approx(2 / 3)
    assert m["lookup_share"] == pytest.approx(9 / 10.5)
    assert m["fullscreen_text_including_lookup_share"] == 1


def test_unknown_device_never_silently_becomes_media():
    with pytest.raises(ValueError, match="unknown"):
        classify_studio({"device": "unimplemented"})


@pytest.mark.parametrize("windows,devices", [([[0, 1]], ["quote"]),
    ([[0, 1], [2, 3]], ["quote", "split"]), ([[0, 1], [1, 3]], ["quote", "quote"])])
def test_stale_or_noncontiguous_studio_cache_is_rejected(windows, devices):
    spec = {"scenes": [{"device": "quote"}, {"device": "split"}], "loop": False}
    with pytest.raises(ValueError):
        studio_scenes(spec, {"windows": windows, "devices": devices})


def test_channel_weighting_does_not_average_percentages():
    a = metrics([dict(kind="quote", t0=0, t1=1)])
    b = metrics([dict(kind="photo", t0=0, t1=9, image="x")])
    out = aggregate([dict(channel="BUD", metrics=m, timing_basis="test") for m in (a, b)])
    assert out["BUD"]["text_share_mean"] == .5
    assert out["BUD"]["text_share_weighted"] == .1
    assert out["VSD"]["n"] == 0


def test_spoken_comparison_ignores_display_markup_case_and_punctuation():
    assert spoken_tokens("**LỆCH** khỏi dự tính!") == spoken_tokens("lệch khỏi dự tính.")
    assert spoken_tokens("ba người") != spoken_tokens("bốn người")


def test_conflicting_duplicate_ids_are_excluded_with_provenance(tmp_path):
    import json
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    for p, style in [(a, "quote"), (b, "photo")]:
        p.write_text(json.dumps([dict(id="x", series="bud", style=style)]), encoding="utf-8")
    audit = Audit(tmp_path, "2026-11-18", 20)
    assert audit.plans([a, b]) == []
    assert audit.plan_conflicts[0]["plans"] == ["a.json", "b.json"]
