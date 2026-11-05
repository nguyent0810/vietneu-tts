"""Preset chữ theo nhịp (#59): opt-in, catalog khóa QA, hồ sơ chữ kênh."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "hyperframes_short/compositions/longform.js").read_text(encoding="utf-8")
PRESETS = (
    "kinetic_punch", "keyword_spotlight", "number_impact", "quote_reveal",
    "contrast_split", "decode_reveal", "image_text_fusion", "question_answer",
)
HOST = {
    "kinetic_punch": "word", "keyword_spotlight": "word", "decode_reveal": "word",
    "image_text_fusion": "word", "number_impact": "stat", "quote_reveal": "quote",
    "contrast_split": "compare", "question_answer": "ask",
}

spec = importlib.util.spec_from_file_location("scene_picker", ROOT / "library/tools/scene_picker.py")
sp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp)
CAT = sp.load_json(sp.CATALOG)


class KineticPresetTests(unittest.TestCase):
    def test_eight_presets_are_opt_in_on_existing_hosts(self):
        for name, host in HOST.items():
            self.assertIn(f'{name}: "{host}"', JS)
            self.assertIn(f'if (KINETIC.take(inner, ln, "{host}")) return;', JS)
        self.assertIn("kSimple(tl,", JS)
        self.assertIn("Thiếu mốc từ hoặc thiếu ảnh", JS)
        self.assertNotIn("back.out", JS[JS.index("const K_LEVEL"):JS.index("visuals.word =")])

    def test_catalog_entries_stay_locked(self):
        by_type = {x["type"]: x for x in CAT["scenes"]}
        for name, host in HOST.items():
            row = by_type[name]
            self.assertEqual(host, row["host"])
            self.assertEqual(name, row["preset"])
            self.assertTrue(row["y_nghia"])
            self.assertIn("dieu_kien", row)
            self.assertEqual("khoa", row["qa"]["trang_thai"])
            self.assertTrue(row["motion_label"])
            self.assertNotEqual(row["motion_label"], by_type[host]["motion_label"])

    def test_locked_preset_is_not_selected_until_qa_dat(self):
        text = "Đây là khái niệm chơi chữ dựa vào âm đọc."
        self.assertIn("khai_niem", {x["tag"] for x in sp.classify(text)})
        prof = {"window_k": 4, "forbidden_types": [], "tags": {
            "khai_niem": [{"type": "kinetic_punch", "requires": []}]}}
        row = {"id": "kin86", "series": "fs", "script": [text], "visuals": {}, "media": {}}
        out, log = sp.choose(row, prof, CAT)
        self.assertNotIn("kinetic_punch", [v.get("type") for v in out.values()])
        self.assertIn("khóa QA", str(log["decisions"][0]["candidates"]))
        unlocked = json.loads(json.dumps(CAT))
        next(x for x in unlocked["scenes"] if x["type"] == "kinetic_punch")["qa"]["trang_thai"] = "dat"
        out2, _ = sp.choose(row, prof, unlocked)
        self.assertEqual("kinetic_punch", out2["1"]["type"])

    def test_channel_typography_profiles(self):
        bud = json.loads((ROOT / "library/channels/bud.yaml").read_text(encoding="utf-8"))
        fs = json.loads((ROOT / "library/channels/fs.yaml").read_text(encoding="utf-8"))
        hist = json.loads((ROOT / "library/channels/_thu_lich_su.yaml").read_text(encoding="utf-8"))
        self.assertEqual("subtle", bud["typography"]["mac_dinh"])
        self.assertIs(False, bud["typography"]["decode"])
        self.assertIs(False, bud["typography"]["glitch"])
        self.assertIs(False, bud["typography"]["presets"]["decode_reveal"]["decode"])
        self.assertEqual("medium", fs["typography"]["mac_dinh"])
        self.assertIs(True, fs["typography"]["decode"])
        self.assertIs(False, fs["typography"]["glitch"])
        self.assertEqual("Fraunces", fs["typography"]["font_phu"])
        self.assertEqual("medium", hist["typography"]["mac_dinh"])
        self.assertEqual("Playfair Display", hist["typography"]["font_phu"])
        self.assertEqual("Lora", bud["typography"]["font_phu"])
        for prof in (bud, fs, hist):
            self.assertEqual(set(PRESETS), set(prof["typography"]["presets"]))
            self.assertIn("motion", prof)
            self.assertIn("canh", prof)

    def test_fake_yaml_typography_drives_presets_and_spec_overrides(self):
        """Task 86b Lỗi 1: Đổi level trong YAML giả -> tham số preset đổi; spec câu ghi đè được kênh."""
        import subprocess
        import hyperframes_bridge as HB
        js = (ROOT / "hyperframes_short/compositions/longform.js").read_text(encoding="utf-8")
        self.assertNotIn('kSeries() === "bud"', js, "Không được gõ cứng tên kênh trong longform.js")
        start = js.index("const K_LEVEL =")
        end = js.index("function kSimple(", start)
        code = js[start:end]

        def eval_kcfg(typo, spec):
            probe = f"""
            window = {{ __hyperframes: {{ getVariables: () => ({{ typography: {json.dumps(typo)} }}) }} }};
            {code}
            console.log(JSON.stringify(kCfg({json.dumps(spec)})));
            """
            out = subprocess.check_output(["node", "-e", probe], text=True)
            return json.loads(out)

        # 1. YAML giả mức subtle: travel 28, entrance 0.62
        fake_yaml_subtle = {
            "mac_dinh": "subtle",
            "decode": False,
            "presets": {
                "kinetic_punch": {"level": "subtle"}
            }
        }
        res_subtle = eval_kcfg(fake_yaml_subtle, {"preset": "kinetic_punch"})
        self.assertEqual("subtle", res_subtle["level"])
        self.assertEqual(28, res_subtle["travel"])
        self.assertEqual(0.62, res_subtle["entrance"])

        # 2. Đổi level trong YAML giả sang impact: tham số preset đổi (travel 90, entrance 0.36)
        fake_yaml_impact = {
            "mac_dinh": "subtle",
            "decode": False,
            "presets": {
                "kinetic_punch": {"level": "impact"}
            }
        }
        res_impact = eval_kcfg(fake_yaml_impact, {"preset": "kinetic_punch"})
        self.assertEqual("impact", res_impact["level"])
        self.assertEqual(90, res_impact["travel"])
        self.assertEqual(0.36, res_impact["entrance"])

        # 3. Spec câu ghi đè được kênh (kênh impact nhưng câu yêu cầu medium -> travel 64, entrance 0.46)
        res_override = eval_kcfg(fake_yaml_impact, {"preset": "kinetic_punch", "level": "medium"})
        self.assertEqual("medium", res_override["level"])
        self.assertEqual(64, res_override["travel"])
        self.assertEqual(0.46, res_override["entrance"])

        # 4. Bridge đọc cấu hình kênh qua load_channel_typography
        typo_fs = HB.load_channel_typography("fs")
        self.assertEqual("medium", typo_fs["mac_dinh"])
        self.assertIs(True, typo_fs["decode"])
        typo_bud = HB.load_channel_typography("bud")
        self.assertEqual("subtle", typo_bud["mac_dinh"])
        self.assertIs(False, typo_bud["decode"])

    def test_all_fromto_in_kinetic_have_immediaterender_false(self):
        """Task 86b Lỗi 2: Quét mọi fromTo trong nhánh kinetic; phải có immediateRender: false."""
        import re
        js = (ROOT / "hyperframes_short/compositions/longform.js").read_text(encoding="utf-8")
        start = js.index("const KINETIC =")
        end = js.index("visuals.word =", start)
        kinetic_block = js[start:end]

        matches = list(re.finditer(r"\.fromTo\s*\(", kinetic_block))
        self.assertGreaterEqual(len(matches), 15, "Nhánh kinetic phải có các tween fromTo")
        for m in matches:
            idx = m.start()
            chunk = kinetic_block[idx:idx + 350]
            self.assertIn("immediateRender: false", chunk, f"Thiếu immediateRender: false trong:\n{chunk[:150]}")


if __name__ == "__main__":
    unittest.main()
