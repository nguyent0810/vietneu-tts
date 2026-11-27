import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import describe  # noqa: E402


def test_pexels_by_caps_names():
    names = [f"Tác giả {i}" for i in range(20)]
    out = describe.pexels_by(names)
    assert out.count(",") == 7 and out.endswith("và 12 tác giả khác")
    assert describe.pexels_by(names[:3]) == " — quay bởi Tác giả 0, Tác giả 1, Tác giả 2"
    assert describe.pexels_by([]) == ""
