"""Kiểm thời lượng cảnh sau khi plan theo timing TTS thật, giống bước html (scene_params.validate_topic).
Dùng: python scripts/check_scene_durations.py <topic> [--out D:/.../output/long/<topic>]
`--out` cho worktree không có output/ (TTS nằm ở checkout sản xuất)."""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT)]
import build_long as B, scene_params, kinetic_style  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("topic"); ap.add_argument("--out")
a = ap.parse_args()
spec, chs, od = B.load(a.topic)
od = Path(a.out) if a.out else od
bad = 0
for name, ch in chs:
    t = json.loads((od / name / "timing.json").read_text(encoding="utf-8"))
    lines = B.word_lines(t, od / name / "voice.wav")
    scenes = B.plan(ch, lines, float(t["duration"]))
    kinetic_style.apply(a.topic, name, scenes, ch.get("scenes", []), lines, spec.get("look") or "classic")
    for e in scene_params.validate_topic([(name, scenes)], None, spec.get("theme") or "noir")["errors"]:
        print(e); bad += 1
    for e in B.late_first(scenes, name):   # cổng nhịp cảnh của bước html
        print(e); bad += 1
print(f"TỔNG LỖI: {bad}")
sys.exit(1 if bad else 0)
