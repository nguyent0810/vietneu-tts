import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from library.tools.plan_enrich import (
    _cold_lines, apply_to_new_long_plan, ask_cap, enrich_long_plan, main, tie_key,
)


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


class AskCapAndKineticTests(unittest.TestCase):
    def _tts(self, path: Path, n: int, step: float) -> None:
        segs = [{"start": i * step, "end": (i + 1) * step} for i in range(n)]
        path.write_text(json.dumps({"segments": segs}), encoding="utf-8")

    def test_handwritten_visuals_stay_identical(self):
        visuals = {"1": {"type": "ask", "overlay": True}, "3": {"type": "photo", "file": "a.jpg"}}
        row = {"id": "old-plan", "lane": "long", "series": "bud",
               "script": ["Vì sao cậu đứng im?", "Câu nối.", "Một câu khác."],
               "visuals": visuals, "media": {"2": {"kind": "image"}}}
        result = enrich_long_plan(row, "bud")
        self.assertEqual(visuals["1"], result["visuals"]["1"])
        self.assertEqual(visuals["3"], result["visuals"]["3"])
        self.assertEqual(row["media"]["2"], result["media"]["2"])
        self.assertNotIn("_ask_mix", result)
        self.assertTrue(all(item["line"] not in (1, 3) for item in result["kinetic_suggest"]))

    def test_ask_cap_converts_picker_cards(self):
        n = 30
        with tempfile.TemporaryDirectory() as tmp:
            tts = Path(tmp) / "tts.json"
            self._tts(tts, n, 20.0)
            row = {"id": "ask-cap", "lane": "long", "series": "bud", "_tts_json": str(tts),
                   "script": ["Vì sao cậu đứng im?" for _ in range(n)],
                   "visuals": {}, "media": {}}
            result = enrich_long_plan(row, "bud")
        counts = {}
        for spec in result["visuals"].values():
            counts[spec["type"]] = counts.get(spec["type"], 0) + 1
        n_vis = sum(counts.values())
        cap, time_cap, frac_cap = ask_cap(n * 20.0, n_vis)
        self.assertEqual(cap, min(time_cap, frac_cap))
        self.assertLessEqual(counts.get("ask", 0), cap)
        self.assertGreater(n_vis - counts.get("ask", 0), 0)
        forbidden = {"napam", "hexagram", "cuudieu", "luoshu", "compass", "bagua", "chiwheel", "wheel", "elements"}
        self.assertFalse(forbidden & set(counts))
        locked = {"kinetic_punch", "keyword_spotlight", "number_impact", "quote_reveal",
                  "contrast_split", "decode_reveal", "image_text_fusion", "question_answer"}
        self.assertFalse(locked & set(counts))

    def test_deterministic_and_seed_tie_break(self):
        row = {"id": "seed-a", "lane": "long", "series": "fs",
               "script": ["Mười sáu năm im lặng.", "Câu nối không có số.", "Kinh ghi rằng hãy tự thắp đuốc."]}
        self.assertEqual(enrich_long_plan(row, "fs"), enrich_long_plan(row, "fs"))
        same_distance = tie_key("video-a", 8, 10)[0] == tie_key("video-a", 12, 10)[0]
        self.assertTrue(same_distance)
        self.assertNotEqual(tie_key("video-a", 8, 10)[1], tie_key("video-b", 8, 10)[1])

    def test_kinetic_opt_in_skips_hand_and_cold_open(self):
        lines = [
            "Mười sáu năm im lặng.",
            "Vì sao cậu đứng im?",
            "Câu nối trong mở đầu.",
            "Vẫn còn trong mở đầu.",
            "**Đêm thành**",
            "Câu nối sau thẻ.",
            "Câu nối nữa cho đủ nhịp.",
            "Mười sáu năm im lặng.",
            "Câu nối giữa chương.",
            "Kinh ghi rằng hãy tự thắp đuốc.",
            "Câu nối giữa chương.",
            "Cậu không đi nhưng vua cha vẫn đứng chờ.",
            "Câu nối giữa chương.",
            "Vì sao cậu đứng im?",
            "Câu nối giữa chương.",
            "Điều cậu giữ là **im lặng** suốt mùa mưa.",
            "Câu nối giữa chương.",
            "Im lặng chính là câu trả lời.",
        ]
        n = len(lines)
        with tempfile.TemporaryDirectory() as tmp:
            tts = Path(tmp) / "tts.json"
            self._tts(tts, n, 8.0)
            row = {"id": "kin-1", "lane": "long", "series": "bud", "_tts_json": str(tts),
                   "script": lines, "clips": {"1": "C1"},
                   "visuals": {"12": {"type": "quote", "source": "tay"}}, "media": {}}
            result = enrich_long_plan(row, "bud")
        self.assertEqual(result["visuals"]["12"], {"type": "quote", "source": "tay"})
        kin = result["kinetic_suggest"]
        self.assertGreaterEqual(len(kin), 3)
        self.assertLessEqual(len(kin), 6)
        lines_picked = [item["line"] for item in kin]
        self.assertEqual(lines_picked, sorted(lines_picked))
        self.assertTrue(all(b - a >= 2 for a, b in zip(lines_picked, lines_picked[1:])))
        self.assertNotIn(12, lines_picked)
        self.assertTrue(all(item["line"] > 4 for item in kin))
        self.assertTrue(all(item["opt_in"] is True for item in kin))
        self.assertTrue(all("preset" not in spec for spec in result["visuals"].values()))
        presets = {item["preset"] for item in kin}
        self.assertIn("number_impact", presets)
        self.assertIn("quote_reveal", presets)
        self.assertNotIn("contrast_split", presets)

    def _picked(self, lines: list[str], clips: dict, step: float) -> list[int]:
        with tempfile.TemporaryDirectory() as tmp:
            tts = Path(tmp) / "tts.json"
            self._tts(tts, len(lines), step)
            row = {"id": "cold-kin", "lane": "long", "series": "bud", "_tts_json": str(tts),
                   "script": lines, "clips": clips, "visuals": {}, "media": {}}
            result = enrich_long_plan(row, "bud")
        return [item["line"] for item in result["kinetic_suggest"]]

    def test_kinetic_skips_clip_cold_open_without_a_heading(self):
        # Không thẻ chương. C1 = câu 1–5. Mỗi câu 8 giây → câu 1–5 bắt đầu trước 40 giây.
        filler = "Câu nối không có mốc."
        lines = [filler] * 16
        lines[1] = "Mười sáu năm im lặng."
        lines[2] = "Vì sao cậu đứng im?"
        lines[3] = "Kinh ghi rằng hãy tự thắp đuốc."
        lines[4] = "Im lặng chính là câu trả lời."
        lines[8] = "16 năm im lặng."
        lines[10] = "Vì sao vẫn còn đứng?"
        lines[12] = "Kinh ghi rằng hãy tự thắp đuốc."
        lines[14] = "Im lặng chính là lựa chọn."
        picked = self._picked(lines, {"1": "C1", "6": "C2"}, 8.0)
        self.assertTrue({2, 3, 4, 5}.isdisjoint(picked))
        self.assertTrue(picked)
        self.assertTrue(all(line >= 6 for line in picked))

    def test_later_clip_inside_forty_seconds_can_take_kinetic(self):
        # Mỗi câu 3 giây. C1 chỉ tới câu 3. Câu 8 bắt đầu ở giây 21 và là clip sau.
        filler = "Câu nối không có mốc."
        lines = [filler] * 12
        lines[0] = "Mười sáu năm im lặng."
        lines[7] = "16 năm im lặng."
        picked = self._picked(lines, {"1": "C1", "3": "C2", "8": "C3"}, 3.0)
        self.assertIn(8, picked)
        self.assertNotIn(1, picked)

    def test_lone_clip_blocks_kinetic_inside_forty_seconds(self):
        # Không thẻ, một clip trơ. Mỗi câu 8 giây → câu 2–5 bắt đầu trước 40 giây.
        filler = "Câu nối không có mốc."
        lines = [filler] * 12
        lines[1] = "Mười sáu năm im lặng."
        lines[8] = "16 năm im lặng."
        picked = self._picked(lines, {"1": "C1"}, 8.0)
        self.assertNotIn(2, picked)
        self.assertIn(9, picked)

    def test_line_before_first_clip_is_blocked_at_second_zero(self):
        # Clip đầu ở câu 2. Câu 1 bắt đầu ở giây 0 và phải thuộc cold open.
        filler = "Câu nối không có mốc."
        lines = [filler] * 10
        lines[0] = "Mười sáu năm im lặng."
        lines[7] = "16 năm im lặng."
        picked = self._picked(lines, {"2": "C1", "6": "C2"}, 8.0)
        self.assertNotIn(1, picked)
        self.assertIn(8, picked)

    def test_opening_heading_without_next_card_blocks_early_kinetic(self):
        filler = "Câu nối không có mốc."
        lines = [filler] * 10
        lines[0] = "**Mở đầu**"
        lines[1] = "Mười sáu năm im lặng."
        lines[7] = "16 năm im lặng."
        picked = self._picked(lines, {}, 8.0)
        self.assertNotIn(2, picked)
        self.assertIn(8, picked)

    def test_opening_heading_on_line_1_blocks_until_the_next_card(self):
        # Mỗi câu 4 giây. Thẻ dòng 1 là mở đầu; thẻ dòng 8 mới là chương.
        # Câu 6 (giây 20) vẫn trong cold open. Câu 9 (giây 32) đã qua thẻ.
        filler = "Câu nối không có mốc."
        lines = [filler] * 14
        lines[0] = "**Mở đầu**"
        lines[5] = "Mười sáu năm im lặng."
        lines[7] = "**Ngày thứ nhất**"
        lines[8] = "16 năm im lặng."
        picked = self._picked(lines, {"2": "C1", "5": "C2"}, 4.0)
        self.assertNotIn(6, picked)
        self.assertIn(9, picked)


class ColdOpenSpanTests(unittest.TestCase):
    def test_clip_span_stops_at_the_next_clip(self):
        lines = ["Câu nối không có mốc."] * 12
        cold = _cold_lines(lines, {"1": "C1", "6": "C2", "30": "C3"})
        self.assertEqual(cold, set(range(1, 6)))

    def test_heading_on_line_1_uses_the_next_heading(self):
        lines = ["**Mở đầu**", "a", "b", "c", "**Ngày thứ nhất**", "d"]
        self.assertEqual(_cold_lines(lines, {"2": "C1", "6": "C2"}), {1, 2, 3, 4})

    def test_first_heading_after_line_1_is_the_bound(self):
        lines = ["a", "b", "**Đêm thành**", "c"]
        self.assertEqual(_cold_lines(lines, {"1": "C1"}), {1, 2})

    def test_clip_span_includes_the_preamble_before_the_first_marker(self):
        lines = ["a"] * 12
        self.assertEqual(_cold_lines(lines, {"2": "C1", "6": "C2"}), set(range(1, 6)))

    def test_lone_clip_without_heading_covers_the_whole_script(self):
        self.assertEqual(_cold_lines(["a", "b", "c"], {"1": "C1"}), {1, 2, 3})

    def test_opening_heading_without_a_next_card_covers_the_script(self):
        self.assertEqual(_cold_lines(["**Mở đầu**", "a", "b"], None), {1, 2, 3})

    def test_opening_heading_without_a_next_card_covers_script_even_with_clips(self):
        lines = ["**Mở đầu**", "a", "b", "c", "d"]
        self.assertEqual(_cold_lines(lines, {"2": "C1", "4": "C2"}), {1, 2, 3, 4, 5})


class ApplyToNewLongPlanTests(unittest.TestCase):
    def test_missing_file_is_enriched_and_written_as_one_element_list(self):
        row = {"id": "new-long", "lane": "long", "series": "fs",
               "script": ["Vì sao người Việt thích nhà hướng Nam?", "Câu nối tiếp."]}
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "plan.json"
            got = apply_to_new_long_plan(row, "fs", dest)
            on_disk = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(got, on_disk)
            self.assertEqual([row["id"]], [item["id"] for item in got])
            self.assertIn("scene_decision", got[0])
            self.assertIn("kinetic_suggest", got[0])
            self.assertNotIn("scene_decision", row)

    def test_existing_file_is_kept_and_enrich_is_not_called(self):
        kept = [{"id": "kept", "lane": "long", "script": ["Câu cũ."]}]
        raw = json.dumps(kept, ensure_ascii=False, indent=1)
        fresh = {"id": "new-long", "lane": "long", "series": "fs",
                 "script": ["Vì sao người Việt thích nhà hướng Nam?"]}
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "plan.json"
            dest.write_text(raw, encoding="utf-8")
            with patch("library.tools.plan_enrich.enrich_long_plan") as mocked:
                got = apply_to_new_long_plan(fresh, "fs", dest)
            mocked.assert_not_called()
            self.assertEqual(raw, dest.read_text(encoding="utf-8"))
            self.assertEqual(kept, got)

    def test_list_plan_is_written_without_an_extra_wrap(self):
        row = {"id": "listed", "lane": "long", "series": "fs", "script": ["Một câu về Hà Nội."]}
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "plan.json"
            got = apply_to_new_long_plan([row], "fs", dest)
            self.assertEqual(1, len(got))
            self.assertEqual("listed", got[0]["id"])
            self.assertIn("scene_decision", got[0])

    def test_string_dest_missing_file_is_enriched_and_written(self):
        row = {"id": "new-long", "lane": "long", "series": "fs",
               "script": ["Vì sao người Việt thích nhà hướng Nam?", "Câu nối tiếp."]}
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "plan.json"
            got = apply_to_new_long_plan(row, "fs", str(dest))
            on_disk = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(got, on_disk)
            self.assertIn("scene_decision", got[0])
            self.assertNotIn("scene_decision", row)

    def test_string_dest_existing_file_is_kept(self):
        kept = [{"id": "kept", "lane": "long", "script": ["Câu cũ."]}]
        raw = json.dumps(kept, ensure_ascii=False, indent=1)
        fresh = {"id": "new-long", "lane": "long", "series": "fs",
                 "script": ["Vì sao người Việt thích nhà hướng Nam?"]}
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "plan.json"
            dest.write_text(raw, encoding="utf-8")
            with patch("library.tools.plan_enrich.enrich_long_plan") as mocked:
                got = apply_to_new_long_plan(fresh, "fs", str(dest))
            mocked.assert_not_called()
            self.assertEqual(raw, dest.read_text(encoding="utf-8"))
            self.assertEqual(kept, got)

    def test_without_dest_enriches_in_memory_only(self):
        row = {"id": "mem", "lane": "long", "series": "bud",
               "script": ["Nạp âm theo tuổi Tý được nhắc đến."]}
        got = apply_to_new_long_plan(row, "bud")
        self.assertIsInstance(got, dict)
        self.assertEqual("mem", got["id"])
        self.assertIn("scene_decision", got)
        self.assertNotIn("scene_decision", row)


if __name__ == "__main__":
    unittest.main()
