import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from library.tools.plan_enrich import enrich_long_plan, main


class PlanEnrichTests(unittest.TestCase):
    def test_existing_visual_and_media_are_preserved_and_skipped(self):
        row = {"id": "editor", "lane": "long", "script": ["a", "b", "c"],
               "visuals": {"1": {"type": "photo"}},
               "media": {"2": {"kind": "image", "preset": "slow_zoom"}}}
        result = enrich_long_plan(row, "fs")
        self.assertEqual(row["visuals"], {k: result["visuals"][k] for k in row["visuals"]})
        self.assertEqual(row["media"]["2"], result["media"]["2"])
        self.assertEqual("editor", result["scene_decision"]["1"]["source"])
        self.assertEqual("editor", result["scene_decision"]["2"]["source"])

    def test_empty_lines_get_scene_and_motion(self):
        row = {"id": "fs-golden", "lane": "long", "series": "fs",
               "script": ["Vì sao người Việt thích nhà hướng Nam?", "Câu nối tiếp."]}
        result = enrich_long_plan(row, "fs")
        picked = [v for v in result["scene_decision"].values() if v["source"] == "picker"]
        self.assertTrue(picked)
        self.assertTrue(all("scene" in v and "motion" in v for v in picked))
        self.assertTrue(result["visuals"])

    def test_bud_forbidden_scene_and_repeatability(self):
        row = {"id": "bud-golden", "lane": "long", "series": "bud",
               "script": ["Nạp âm theo tuổi Tý và quẻ dịch được nhắc đến." ]}
        first = enrich_long_plan(row, "bud")
        self.assertEqual(first, enrich_long_plan(row, "bud"))
        forbidden = set(__import__("library.tools.scene_picker", fromlist=["load_profile"]).load_profile(None, "bud").get("forbidden_types", []))
        self.assertFalse(forbidden & {v.get("type") for v in first["visuals"].values()})

    def test_cli_dry_run_and_write(self):
        row = {"id": "fs-cli", "lane": "long", "series": "fs", "script": ["Một câu về Hà Nội."]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.json"
            original = json.dumps(row)
            path.write_text(original, encoding="utf-8")
            with patch("sys.argv", ["plan_enrich", str(path), "--channel", "fs", "--dry-run"]):
                self.assertEqual(0, main())
            self.assertEqual(original, path.read_text(encoding="utf-8"))
            with patch("sys.argv", ["plan_enrich", str(path), "--channel", "fs", "--write"]):
                self.assertEqual(0, main())
            self.assertIn("scene_decision", json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
