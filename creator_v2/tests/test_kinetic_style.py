import copy
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import kinetic_style as ks


def sample(n=40):
    return [{"type": "kinetic", "t0": i * 2., "t1": i * 2. + 2.,
             "items": [{"text": "word", "at": i * 2. + .4}]} for i in range(n)]


def test_rotation_deterministic_and_balanced():
    scenes = sample(); source = copy.deepcopy(scenes); other = copy.deepcopy(scenes)
    fx, styles = ks.apply("topic", "ch01", scenes, source, [])
    ks.apply("topic", "ch01", other, source, [])
    assert scenes == other
    chosen = [s["items"][0]["fx"] for s in scenes]
    assert len(fx) >= 4 and max(fx.values()) <= len(chosen) * .2
    assert all(a != b for a, b in zip(chosen, chosen[1:]))
    st = [s["items"][0]["typestyle"] for s in scenes]
    assert all(a != b for a, b in zip(st, st[1:]))
    assert len(styles) == len(ks.STYLES)


def test_legacy_and_manual_fields():
    original = sample(1); scenes = copy.deepcopy(original)
    ks.apply("old", "ch01", scenes, original, [], enabled=False)
    assert scenes == original
    original[0]["items"][0].update(fx="marker", style="personal")
    scenes = copy.deepcopy(original)
    ks.apply("new", "ch01", scenes, original, [])
    assert scenes[0]["items"][0]["fx"] == "marker"
    assert scenes[0]["items"][0]["style"] == "personal"
    assert "typestyle" not in scenes[0]["items"][0]


def test_negative_auto_strike():
    texts = ["KH\u00d4NG PH\u1ea2I X \u00b7 Y", "\u0110\u1eeaNG X \u00b7 Y", "SAI \u00b7 \u0110\u00daNG", "CH\u1eb2NG PH\u1ea2I X \u00b7 Y"]
    scenes = sample(4)
    for s, text in zip(scenes, texts): s["items"][0]["text"] = text
    ks.apply("topic", "ch01", scenes, copy.deepcopy(scenes), [])
    assert all(s["items"][0]["autoStrike"] for s in scenes)
    assert not ks._negative("\u0110\u00daNG")
    # C\u00e2u \u0111\u01a1n kh\u00f4ng c\u00f3 v\u1ebf \u0111\u1ed1i l\u1eadp th\u00ec kh\u00f4ng g\u1ea1ch: g\u1ea1ch "\u0110\u1eeaNG TIN L\u1edcI \u0110\u1ed2N" l\u00e0 ng\u01b0\u1ee3c ngh\u0129a (Lead 12/11).
    assert not ks._negative("\u0110\u1eeaNG TIN L\u1edcI \u0110\u1ed2N")
    assert not ks._negative("\u0110\u00daNG \u00b7 SAI")


def test_sync_requires_actual_word_times_and_tracks_emphasis():
    scenes = sample(1); q = scenes[0]["items"][0]
    q.update(text="hello world", em="world")
    words = [{"w": "hello", "t": .5}, {"w": "world", "t": .9}]
    counts = (Counter({v: 3 for v in ks.EFFECTS}), Counter())
    ks.apply("topic", "ch01", scenes, copy.deepcopy(scenes), [{"words": words}], counts=counts)
    assert q["fx"] == "sync" and q["wt"] == [.5, .9] and q["emw"] == [1]
    scenes = sample(1); scenes[0]["items"][0]["text"] = "hello missing"
    ks.apply("topic", "ch01", scenes, copy.deepcopy(scenes), [{"words": words}], counts=(Counter({v: 3 for v in ks.EFFECTS}), Counter()))
    assert scenes[0]["items"][0]["fx"] != "sync"


def test_slam_new_effect_and_manual_slam():
    scenes = [{"type": "slam", "text": "hello", "t0": 0, "t1": 2, "at": .5},
              {"type": "slam", "text": "manual", "t0": 2, "t1": 4, "at": 2.5, "fx": "glitch"}]
    ks.apply("topic", "ch01", scenes, copy.deepcopy(scenes), [])
    assert scenes[0]["fx"] in ks.EFFECTS[:8]
    assert scenes[0]["typestyle"] in ks.STYLES
    assert scenes[1]["fx"] == "glitch" and "typestyle" not in scenes[1]


def test_strike_preserves_manual_effect():
    scenes = sample(1)
    scenes[0]["items"][0].update(text="SAI · ĐÚNG", fx="flip")
    ks.apply("topic", "ch01", scenes, copy.deepcopy(scenes), [])
    assert scenes[0]["items"][0]["fx"] == "flip"
    assert scenes[0]["items"][0]["autoStrike"]
