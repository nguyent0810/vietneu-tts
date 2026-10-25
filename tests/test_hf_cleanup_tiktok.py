"""hf_cleanup giữ short BUD trong cửa sổ chọn bài TikTok (quy trình 23/10/2026)."""
import importlib.util
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "hf_cleanup.py"
spec = importlib.util.spec_from_file_location("hf_cleanup", SRC)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

AIR = "2026-10-24T11:00:00Z"
T_AIR = 1792839600.0  # = AIR


def test_bud_kept_inside_window():
    assert C.waiting_for_tiktok("bud", "bud_x", AIR, set(), now=T_AIR + 3600) is True


def test_bud_released_after_window():
    assert C.waiting_for_tiktok("bud", "bud_x", AIR, set(), now=T_AIR + 73 * 3600) is False


def test_bud_released_once_scheduled_on_tiktok():
    assert C.waiting_for_tiktok("bud", "bud_x", AIR, {"bud_x"}, now=T_AIR + 3600) is False


def test_fs_never_waits():
    assert C.waiting_for_tiktok("fs", "fs_x", AIR, set(), now=T_AIR + 3600) is False
