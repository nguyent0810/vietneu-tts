import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("knowledge", ROOT / "library/tools/knowledge.py")
knowledge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(knowledge)


class KnowledgeInventoryTests(unittest.TestCase):
    def test_defects_are_aggregated_by_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            defects = root / "output/cl_staging/grok/improve/defects.jsonl"
            defects.parent.mkdir(parents=True)
            defects.write_text("\n".join([
                json.dumps({"ngay":"2026-10-01","khau":"hinh","loi":"tràn chữ"}),
                json.dumps({"ngay":"2026-10-03","khau":"hinh","loi":"tương phản thấp"}),
                json.dumps({"ngay":"2026-10-02","khau":"nguon","loi":"nguồn bịa"}),
            ]) + "\n", encoding="utf-8")
            items = knowledge.scan(root)["items"]
            lessons = [x for x in items if x["loai"] == "bai_hoc"]
            by_name = {x["ten"]: x for x in lessons}
            self.assertEqual(len(lessons), 2)
            self.assertEqual(by_name["Bài học khâu hinh"]["so_lieu"]["so_lan"], 2)
            self.assertEqual(by_name["Bài học khâu hinh"]["so_lieu"]["ngay_gan_nhat"], "2026-10-03")

    def test_inventory_ids_are_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = knowledge.scan(Path(tmp))["items"]
        ids = [x["id"] for x in items]
        self.assertEqual(len(ids), len(set(ids)))

    def test_card_ids_are_unique_across_types(self):
        cards = ROOT / "library/cards"
        found = {}
        for path in cards.rglob("*.md"):
            match = re.match(r"\A---\s*\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
            if not match:
                continue
            data = json.loads(match.group(1))
            card_id = data["id"]
            self.assertNotIn(card_id, found, f"{card_id}: {found.get(card_id)} / {path}")
            found[card_id] = path


if __name__ == "__main__":
    unittest.main()
