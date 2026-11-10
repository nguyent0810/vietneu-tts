"""Dòng chữ ở đầu chương không được nhận scramble/type (ck-e6 ch00 10/11/2026: chữ rác kẹt suốt cảnh)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion"))
from beatfx import assign_beats  # noqa: E402


def _scene(at, sm=False):
    q = {"text": "ĐÓNG 10 NĂM", "at": at}
    if sm:
        q["sm"] = True
    return [{"type": "broll", "t0": 0.0, "kin": [q]}]


def test_number_line_at_zero_avoids_scramble():
    for key in ("a", "b", "c", "d", "e"):
        sc = _scene(0.07)
        assign_beats(sc, key, pools={"D": ["scramble"]})
        assert sc[0]["kin"][0]["fx"] not in ("scramble", "type")


def test_small_number_line_at_zero_avoids_type():
    for key in ("a", "b", "c", "d", "e"):
        sc = _scene(0.0, sm=True)
        assign_beats(sc, key, pools={"D": ["scramble"], "S": ["type", "rise"]})
        assert sc[0]["kin"][0]["fx"] not in ("scramble", "type")


def test_number_line_later_keeps_scramble_pool():
    sc = _scene(12.0)
    assign_beats(sc, "x", pools={"D": ["scramble"]})
    assert sc[0]["kin"][0]["fx"] == "scramble"


def test_spec_fx_is_kept():
    sc = _scene(0.0)
    sc[0]["kin"][0]["fx"] = "scramble"
    assign_beats(sc, "x")
    assert sc[0]["kin"][0]["fx"] == "scramble"
