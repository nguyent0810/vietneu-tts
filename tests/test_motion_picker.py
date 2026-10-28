"""Bộ chọn motion preset (#52): tất định, chống lặp, không chọn pan/highlight khi thiếu focus."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("motion_picker", ROOT / "library/tools/motion_picker.py")
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)


def _lines(n, step=5.0):
    return [{"sentence_id": i + 1, "start": i * step, "end": (i + 1) * step} for i in range(n)]


def _profile(**presets):
    base = {
        "window_k": 3, "hold_split_s": 8, "max_shots": 3, "min_shot_s": 2.5,
        "presets": presets or {
            "slow_zoom": {"min_s": 4, "max_s": 18, "scale_from": 1.0, "scale_to": 1.08, "pan": 0.35, "needs_focus": False},
            "pan_focus": {"min_s": 3.5, "max_s": 16, "scale_from": 1.04, "scale_to": 1.12, "pan": 1, "needs_focus": True},
            "push_detail": {"min_s": 3, "max_s": 12, "scale_from": 1.04, "scale_to": 1.18, "pan": 1, "needs_focus": False},
            "parallax": {"min_s": 4, "max_s": 18, "needs_focus": False},
            "highlight": {"min_s": 3, "max_s": 14, "scale_from": 1.04, "scale_to": 1.06, "pan": 0.7, "needs_focus": True},
            "reveal": {"min_s": 2.8, "max_s": 12, "scale_from": 1.16, "scale_to": 1.06, "pan": 0.15, "needs_focus": False},
        },
    }
    return base


class MotionPickerTests(unittest.TestCase):
    def test_no_focus_skips_pan_and_highlight(self):
        row = {"id": "a", "lines": _lines(6), "media": {str(i): {"kind": "image"} for i in range(1, 7)}}
        patch, log = mp.choose(row, _profile())
        names = [x["preset"] for x in log]
        self.assertTrue(names)
        self.assertNotIn("pan_focus", names)
        self.assertNotIn("highlight", names)
        self.assertTrue(all(a != b for a, b in zip(names, names[1:])))
        self.assertEqual(mp.choose(row, _profile()), (patch, log))

    def test_window_blocks_recent(self):
        row = {"id": "a", "lines": _lines(4), "media": {str(i): {"kind": "image"} for i in range(1, 5)}}
        _, log = mp.choose(row, _profile())
        names = [x["preset"] for x in log]
        for i, name in enumerate(names):
            self.assertNotIn(name, names[max(0, i - 3):i])

    def test_long_hold_splits_on_sentence_bounds(self):
        row = {"id": "a", "lines": _lines(4), "media": {"1": {"kind": "local"}}}
        patch, log = mp.choose(row, _profile())
        shots = patch["1"]["shots"]
        self.assertGreaterEqual(len(shots), 2)
        self.assertLessEqual(len(shots), 3)
        self.assertEqual(len({s["preset"] for s in shots}), len(shots))
        self.assertNotIn("parallax", [s["preset"] for s in shots])
        ats = [s["at"] for s in shots]
        self.assertEqual(ats[0], 1)
        self.assertTrue(all(a < b for a, b in zip(ats, ats[1:])))
        self.assertEqual([x["focus"] for x in log], [False] * len(log))

    def test_focus_allows_pan_and_records_box(self):
        focus = [0.2, 0.1, 0.4, 0.5]
        prof = _profile(**{
            "pan_focus": {"min_s": 3, "max_s": 16, "needs_focus": True, "scale_to": 1.12},
            "highlight": {"min_s": 3, "max_s": 14, "needs_focus": True, "scale_to": 1.06},
        })
        row = {"id": "a", "lines": _lines(1, step=5), "media": {"1": {"kind": "commons", "focus": focus}}}
        patch, log = mp.choose(row, prof)
        self.assertEqual(patch["1"]["preset"], "pan_focus")
        self.assertEqual(patch["1"]["focus"], focus)
        self.assertTrue(log[0]["focus"])
        self.assertIn("scale_to", patch["1"]["shots"][0])

    def test_short_shot_respects_min_duration(self):
        row = {"id": "a", "lines": _lines(1, step=3), "media": {"1": {"kind": "image", "focus": [0.2, 0.2, 0.3, 0.3]}}}
        patch, _ = mp.choose(row, _profile())
        self.assertEqual(patch["1"]["preset"], "push_detail")

    def test_custom_profile_without_code_change(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "kenh.yaml"
            p.write_text(json.dumps({"kenh": "ao", "motion": _profile(**{
                "highlight": {"min_s": 2, "max_s": 10, "needs_focus": True},
            })}), encoding="utf-8")
            loaded = mp.load_profile(str(p), "ao")
            self.assertEqual(list(loaded["presets"]), ["highlight"])
            row = {"id": "a", "lines": _lines(1), "media": {"1": {"kind": "image", "focus": [0.3, 0.3, 0.2, 0.2]}}}
            patch, _ = mp.choose(row, loaded)
            self.assertEqual(patch["1"]["preset"], "highlight")

    def test_fake_channel_profile_runs(self):
        loaded = mp.load_profile(None, "_thu_lich_su")
        self.assertIn("slow_zoom", loaded["presets"])
        self.assertNotIn("canh", loaded)
        row = {"id": "thu", "lines": _lines(2), "media": {"1": {"kind": "image"}, "2": {"kind": "video"}}}
        patch, log = mp.choose(row, loaded)
        self.assertIn("1", patch)
        self.assertNotIn("2", patch)
        self.assertEqual(log[-1]["reason"], "không phải ảnh tĩnh")

    def test_jsonl_has_preset_reason_focus(self):
        row = {"id": "a", "lines": _lines(1), "media": {"1": {"kind": "museum"}}}
        with tempfile.TemporaryDirectory() as td:
            logp = Path(td) / "m.jsonl"
            plan = Path(td) / "plan.json"
            plan.write_text(json.dumps(row), encoding="utf-8")
            prof = Path(td) / "p.yaml"
            prof.write_text(json.dumps({"motion": _profile()}), encoding="utf-8")
            subprocess.run(
                [str(ROOT / ".venv/bin/python"), str(ROOT / "library/tools/motion_picker.py"),
                 "--plan", str(plan), "--profile", str(prof), "--log", str(logp)],
                check=True, cwd=ROOT,
            )
            rec = json.loads(logp.read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("preset", rec)
            self.assertIn("reason", rec)
            self.assertIn("focus", rec)

    def test_pose_stays_inside_image(self):
        js = (ROOT / "hyperframes_short/compositions/longform.js").read_text(encoding="utf-8")
        node = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const m = src.match(/\/\* MOTION_PURE_START \*\/([\s\S]*?)\/\* MOTION_PURE_END \*\//);
if (!m) process.exit(2);
eval(m[1]);
const focuses = [null, [0.05, 0.05, 0.2, 0.3], [0.7, 0.6, 0.25, 0.3], [0.4, 0.4, 0.2, 0.2]];
const scales = [[1, 1.08], [1.04, 1.18], [1.16, 1.06], [1.04, 1.06]];
for (const [s0, s1] of scales) {
  for (const f of focuses) {
    for (const k of [0.4, 1]) {
      const start = targetPose(s0, s0, 1, f, 1);
      const end = targetPose(s0, s1, 1, f, k);
      for (const p of [start, end]) {
        const budget = (p.scale - 1) * 50 + 1e-6;
        if (p.scale < 1 || p.scale > 1.22) process.exit(3);
        if (Math.abs(p.xPercent) > budget || Math.abs(p.yPercent) > budget) process.exit(4);
      }
    }
  }
}
const op = objectPositionFor(3000, 2000, 1920, 1080, 0.2, 0.4);
if (!/^\d/.test(op)) process.exit(5);
process.stdout.write('POSE_OK ' + op);
"""
        res = subprocess.run(["node", "-e", node, str(ROOT / "hyperframes_short/compositions/longform.js")],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("POSE_OK", res.stdout)


if __name__ == "__main__":
    unittest.main()
