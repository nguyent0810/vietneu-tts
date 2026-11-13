"""Kiểm thời lượng cảnh sau khi plan theo timing TTS thật, giống bước html (scene_params.validate_topic).
Dùng: python scripts/check_scene_durations.py <topic> [--out D:/.../output/long/<topic>]
`--out` cho worktree không có output/ (TTS nằm ở checkout sản xuất)."""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT)]
import build_long as B, scene_params, kinetic_style  # noqa: E402
from factory.console import utf8_console  # noqa: E402
utf8_console()

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
for e in B.collect_html_lint(a.topic, None):   # lint html (tiêu đề thẻ, bản đồ...) như bước html
    print("html:", e); bad += 1
if spec.get("craft"):   # cổng craft của bước html: câu > 35 âm tiết, câu hỏi 8 câu đầu, gọi "bạn", nghỉ dài
    import craft, script_lines  # noqa: E402,E401
    md = B.ROOT / "data" / "long" / a.topic / "script.md"
    probs = craft.audio_problems(script_lines.parse(md.read_text(encoding="utf-8"))) if md.exists() else []
    for name, ch in chs:
        probs.extend(craft.graphic_problems(name, ch["scenes"]))
    for e in probs:
        print("craft:", e); bad += 1
import floor  # noqa: E402  (cổng floor của render/final, gồm họ thẻ #276 khi spec bật idcards)
for e in floor.problems(chs, spec.get("channel", "CL"), a.topic, idcards_enabled=bool(spec.get("idcards", not B.is_legacy_topic(a.topic)))):
    print("floor:", e); bad += 1
print(f"TỔNG LỖI: {bad}")
sys.exit(1 if bad else 0)
