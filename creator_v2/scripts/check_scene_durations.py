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
    for e in scene_params.validate_topic([(name, scenes)], None, B.THEME["name"])["errors"]:
        print(e); bad += 1
    # Các kiểm tra viết thẳng trong do_html (nhãn biểu đồ, prefix counter, dấu ~, ledger tràn thẻ).
    for k, sc in enumerate(scenes):
        if sc.get("type") == "chart" and isinstance(sc.get("label"), dict):
            print(f"{name}: chart#{k} label đè nhãn trục (chuyển sang unit)"); bad += 1
        if sc.get("type") == "counter" and any(c.isdigit() or c in "<>≈~" for c in str(sc.get("prefix") or "")) and sc.get("from", 0) != sc.get("to"):
            print(f"{name}: counter#{k} prefix {sc.get('prefix')!r} có số/dấu so sánh (đặt from = to)"); bad += 1
    import re as _re  # noqa: E402
    for t in _re.findall(r"~\s*\d[\d.,]*", json.dumps(scenes, ensure_ascii=False)):
        print(f"{name}: dấu ~ trước số {t!r} (dùng ≈)"); bad += 1
    for w in B.ledger_overflow(scenes, B.THEME["name"]):
        print(f"{name}: ledger tràn thẻ {w}"); bad += 1
    for e in B.bars_collide(scenes):                      # tiêu đề biểu đồ đè chú thích
        print(f"{name}: biểu đồ {e}"); bad += 1
    for k, sc in enumerate(scenes):                        # mốc chưa đổi ra giây
        for c in B.unresolved_cues(sc, f"{sc['type']}#{k}"):
            print(f"{name}: mốc chưa đổi ra giây {c}"); bad += 1
    for k, sc in enumerate(scenes):                        # clip phải dài hơn cảnh (+0,5s)
        if sc.get("vid"):
            src = od / "broll" / f"{sc['vid']}.mp4"
            if src.exists():
                need = sc["t1"] - sc["t0"] + 0.5
                have = B.probe_dur(src)
                if float(sc.get("ms", 0)) + need > have + 0.05:
                    print(f"{name} cảnh {k}: clip {sc['vid']} dài {have:.1f}s, cần {need:.1f}s"); bad += 1
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
