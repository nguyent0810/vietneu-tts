import unittest
from datetime import date

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ck_stop_rule_180 import assess, date_range, decision, report


def video(identifier="a", published="2026-10-28T18:00:00Z", duration="PT3M", privacy="public"):
    return {"id": identifier, "title": "Tiêu đề | thử", "published_at": published, "duration": duration, "privacy": privacy}


def days(*pairs):
    return {"ok": True, "rows": [{"day": day, "views": views} for day, views in pairs]}


class StopRuleTest(unittest.TestCase):
    def test_vietnam_day_and_exact_window(self):
        data = {"a": days(("2026-10-28", 100), ("2026-10-29", 1), ("2026-10-30", 2), ("2026-10-31", 3), ("2026-11-01", 200))}
        result = assess([video()], data, 3)[0]
        self.assertEqual(result["published"], date(2026, 10, 29))
        self.assertEqual(result["views"], 6)
        self.assertEqual(assess([video("x", duration="PT3M1S"), video("y", privacy="private")], data, 3), [])
        self.assertEqual(len(assess([video(), video()], data, 3)), 1)

    def test_immature_and_missing_days_excluded(self):
        items = assess([video("a"), video("b")], {"a": days(("2026-10-29", 1), ("2026-10-30", 2)), "b": days(("2026-10-29", 1), ("2026-10-31", 3))}, 3)
        self.assertEqual([x["status"] for x in items], ["chưa đủ tuổi", "thiếu ngày dữ liệu"])
        self.assertTrue(all(x["views"] is None for x in items))

    def test_both_sides_and_equality(self):
        items = [{"views": 193} for _ in range(20)]
        self.assertEqual(decision(items, 193.2), "DỪNG: quay về 2–3/ngày")
        self.assertEqual(decision(items, 193), "GIỮ 5/ngày")
        self.assertEqual(decision(items, 192), "GIỮ 5/ngày")

    def test_fewer_than_twenty(self):
        self.assertEqual(decision([{"views": 1}] * 19, 193.2), "chưa đủ dữ liệu")
        items = assess([video()], {"a": days(("2026-10-29", 1), ("2026-10-30", 2), ("2026-10-31", 3))}, 3)
        output = report(items, date_range("2026-10-29:2026-11-11"), date_range("2026-10-20:2026-10-26"), 322, .6, 3, "fake")
        self.assertIn("chưa đủ dữ liệu", output)
        self.assertIn("Tiêu đề \\| thử", output)


if __name__ == "__main__":
    unittest.main()
