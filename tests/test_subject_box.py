"""Hộp chủ thể: không chắc thì không trả focus."""
import importlib.util
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("subject_box", ROOT / "tools/subject_box.py")
sb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sb)


def _mask(w, h, box, value=255):
    im = Image.new("L", (w, h), 0)
    x, y, bw, bh = box
    for yy in range(y, y + bh):
        for xx in range(x, x + bw):
            im.putpixel((xx, yy), value)
    return im


class SubjectBoxTests(unittest.TestCase):
    def test_bbox_inside(self):
        found = sb.bbox_from_mask(_mask(200, 100, (40, 20, 50, 40)))
        self.assertEqual(found["source"], "vision")
        x, y, w, h = found["focus"]
        self.assertAlmostEqual(x, 0.2, places=3)
        self.assertAlmostEqual(y, 0.2, places=3)
        self.assertAlmostEqual(w, 0.25, places=3)
        self.assertAlmostEqual(h, 0.4, places=3)

    def test_too_small_or_full_frame_or_three_edges_is_none(self):
        self.assertIsNone(sb.bbox_from_mask(_mask(200, 100, (10, 10, 8, 8))))
        self.assertIsNone(sb.bbox_from_mask(_mask(100, 100, (0, 0, 100, 100))))
        self.assertIsNone(sb.bbox_from_mask(_mask(100, 100, (0, 0, 40, 100))))

    def test_empty_mask_is_none(self):
        self.assertIsNone(sb.bbox_from_mask(Image.new("L", (80, 80), 0)))


if __name__ == "__main__":
    unittest.main()
