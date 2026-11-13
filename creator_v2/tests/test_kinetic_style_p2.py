import copy
import json
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import kinetic_style as ks
from motion.long import build_long as b


def make_scene(i, kind="kinetic"):
    base = {"type": kind, "t0": i * 3, "t1": i * 3 + 3}
    if kind == "kinetic":
        base["items"] = [{"text": "SAI \u00b7 \u0110\u00daNG", "at": i * 3 + .4}]
    else:
        base.update(text="SAI \u00b7 \u0110\u00daNG", at=i * 3 + .4, typeDur=1.5)
    return base


def test_quotes_are_slow_safe_deterministic_and_manual_is_preserved():
    source = [make_scene(i, "quote") for i in range(10)]
    source[0]["fx"] = "custom-manual"
    scenes = copy.deepcopy(source)
    again = copy.deepcopy(source)
    ks.apply("topic", "ch01", scenes, source, [])
    ks.apply("topic", "ch01", again, source, [])
    assert scenes == again
    assert scenes[0]["fx"] == "custom-manual"
    assert all(s["quoteKinetic"] and "autoStrike" not in s for s in scenes)
    assert all(s["fx"] in ks.QUOTE_EFFECTS for s in scenes[1:])
    js = Path("motion/hf/assets/engine/casewide.js").read_text(encoding="utf-8")
    assert "Math.max(1, s.typeDur || 1)" in js
    assert "if (s.quoteKinetic)" in js and "else {\n      const spans" in js


def test_automatic_rotation_meets_quota_for_constrained_and_mixed_scenes():
    for n in range(5, 37):
        source = [make_scene(i, ("quote", "slam", "kinetic")[i % 3]) for i in range(n)]
        for scene in source:
            if scene["type"] == "kinetic":
                scene["items"][0]["em"] = "SAI \u00b7"
        scenes = copy.deepcopy(source)
        dist, _ = ks.apply("topic", "chapter", scenes, source, [])
        assert len(dist) >= 4
        assert max(dist.values()) * 5 <= n
        assert ks.distribution_warning(scenes, source, dist) is None
        again = copy.deepcopy(source)
        ks.apply("topic", "chapter", again, source, [])
        assert scenes == again


def test_uniform_quote_and_emphasis_chapters_meet_limits():
    for n in range(5, 21):
        for kind in ("quote", "kinetic"):
            source = [make_scene(i, kind) for i in range(n)]
            if kind == "kinetic":
                for scene in source:
                    scene["items"][0]["em"] = "SAI \u00b7"
            scenes = copy.deepcopy(source)
            dist, _ = ks.apply("uniform", "chapter", scenes, source, [])
            assert len(dist) >= 4 and max(dist.values()) * 5 <= n


def test_multi_line_scenes_count_once_for_the_chapter():
    source = [make_scene(i) for i in range(10)]
    for scene in source:
        scene["items"].append({"text": "second line", "at": scene["t0"] + 1})
        scene["items"].append({"text": "third line", "at": scene["t0"] + 1.5})
    scenes = copy.deepcopy(source)
    dist, _ = ks.apply("t", "c", scenes, source, [])
    assert sum(dist.values()) == len(scenes)
    assert max(dist.values()) * 5 <= len(scenes)
    assert all(len({item["fx"] for item in s["items"]}) == 1 for s in scenes)
    assert ks.distribution_warning(scenes, source, dist) is None


def test_warnings_distinguish_short_and_manual():
    source = [make_scene(i) for i in range(4)]
    scenes = copy.deepcopy(source)
    dist, _ = ks.apply("t", "c", scenes, source, [])
    assert "fewer than five" in ks.distribution_warning(scenes, source, dist)
    source = [make_scene(i) for i in range(10)]
    for scene in source[:7]:
        scene["items"][0]["fx"] = "marker"
    scenes = copy.deepcopy(source)
    dist, _ = ks.apply("t", "c", scenes, source, [])
    assert all(s["items"][0]["fx"] == "marker" for s in scenes[:7])
    assert "manual" in ks.distribution_warning(scenes, source, dist)


def test_marker_uses_separate_seekable_underline_with_legacy_path():
    js = Path("motion/hf/assets/engine/beat.js").read_text(encoding="utf-8")
    css = Path("motion/hf/assets/engine/beat.css").read_text(encoding="utf-8")
    assert "if (q.markerUnderline)" in js and 'const s = inner(e, "mk")' in js
    assert 'el("i", "mk-line", null, text)' in js
    assert 'tl.fromTo(line, { scaleX: 0 }, { scaleX: 1' in js
    assert ".kin .mk-line" in css and "top:100%" in css and "transform-origin:0 50%" in css
    assert "marker" in ks.EFFECTS
    source = [make_scene(i) for i in range(130)]
    scenes = copy.deepcopy(source)
    ks.apply("marker", "ch01", scenes, source, [])
    markers = [s["items"][0] for s in scenes if s["items"][0]["fx"] == "marker"]
    assert markers and all(x["markerUnderline"] for x in markers)


def test_real_legacy_topic_build_never_calls_selector():
    topics = json.loads((b.ROOT / "data/long/_legacy_topics.json").read_text(encoding="utf-8"))
    topic = next(t for t in topics if (b.ROOT / "data/long" / t / "spec.json").exists())
    assert b.is_legacy_topic(topic)
    scene = make_scene(0, "quote")
    chapter = {"scenes": [copy.deepcopy(scene)], "lines": []}
    spec = {"title": "test", "channel": "CL", "chapters": ["ch01"], "imgs": {}}
    writes = {}
    def record(path, text, **kwargs):
        writes[str(path)] = text
        return len(text)
    with patch.object(b, "is_legacy_topic", return_value=True), \
         patch.object(ks, "apply", side_effect=AssertionError("legacy called selector")), \
         patch.object(b, "load", return_value=(spec, [("ch01", chapter)], Path("tmp_dry/legacy_case"))), \
         patch.object(b, "_refuse_html_lint"), patch.object(b, "_refuse_craft"), patch.object(b, "_refuse_opening"), \
         patch.object(b.variety, "resolve_bgm"), patch.object(b.variety, "look", return_value={}), \
         patch.object(b.variety, "fonts_url", return_value=""), patch.object(b, "word_lines", return_value=[]), \
         patch.object(b, "plan", side_effect=lambda *args: [copy.deepcopy(scene)]), \
         patch.object(b.sfx_long, "build"), patch.object(b, "mix_chapter"), patch.object(b, "late_first", return_value=[]), \
         patch.object(Path, "read_text", return_value='{"duration": 3}'), patch.object(Path, "write_text", record), \
         patch.object(Path, "mkdir"), patch.object(Path, "exists", return_value=False):
        b.do_html(topic)
    data = next(value for path, value in writes.items() if path.endswith("data.js"))
    assert json.loads(data.split("=", 1)[1].strip().rstrip(";"))["scenes"] == [scene]
