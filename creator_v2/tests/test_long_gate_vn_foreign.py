import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import long_gate as g


def test_vietnamese_words_without_diacritics_are_not_foreign():
    for w in ("Thanh", "Long", "Phong", "Trung", "Huy", "Kinh", "Quan", "Nghia", "Trong"):
        assert g.VN_SYL.match(w), w


def test_real_foreign_names_still_flagged():
    for w in ("Welchman", "Bletchley", "Macartney", "Portsmouth", "William", "Britannica", "McMahon"):
        assert not g.VN_SYL.match(w), w
