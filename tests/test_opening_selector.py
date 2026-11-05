"""test_opening_selector.py — Tests for opening hook library selector (Ticket #54)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from library.opening_library.selector import OpeningSelector


def test_selector_fs_shocking_number():
    sel = OpeningSelector("fs")
    res = sel.select_opening(
        hook_text="Năm 2027 có 354 ngày âm lịch",
        hook_type="so_thoi_gian",
        available_assets={"images": []},
        recent_patterns=[]
    )
    assert res["selected_pattern"] == "shocking_number"
    assert res["method"] == "B_hyperframes"
    assert res["score"] >= 80


def test_selector_bud_forbidden_number():
    sel = OpeningSelector("bud")
    # bud cấm shocking_number
    res = sel.select_opening(
        hook_text="Năm 2027 có 354 ngày âm lịch",
        hook_type="so_thoi_gian",
        available_assets={"images": []},
        recent_patterns=[]
    )
    assert res["selected_pattern"] != "shocking_number"


def test_selector_anti_repetition():
    sel = OpeningSelector("fs")
    # Cấm tuyệt đối chọn lại mẫu vừa dùng ở video trước (kể cả khi hook khớp hoàn hảo)
    res = sel.select_opening(
        hook_text="Năm 2027 có 354 ngày âm lịch",
        hook_type="so_thoi_gian",
        available_assets={"images": ["img1", "img2"]},
        recent_patterns=["shocking_number"]
    )
    assert res["selected_pattern"] != "shocking_number"


def test_selector_strictly_forbids_recent_even_without_alternative():
    sel = OpeningSelector("fs")
    # Khi shocking_number vừa dùng ở video trước, tuyệt đối không chọn lại dù available_assets rỗng
    res = sel.select_opening(
        hook_text="Năm 2027 có 354 ngày âm lịch",
        hook_type="so_thoi_gian",
        available_assets={"images": []},
        recent_patterns=["shocking_number"]
    )
    assert res["selected_pattern"] != "shocking_number"


def test_selector_map_dive_history():
    sel = OpeningSelector("lich_su")
    res = sel.select_opening(
        hook_text="Chiến lũy Lũy Thầy",
        hook_type="dia_danh",
        available_assets={"images": [], "coordinates": (106.6, 17.47)},
        recent_patterns=[]
    )
    assert res["selected_pattern"] == "map_dive"
    assert res["method"] == "B_hyperframes"
