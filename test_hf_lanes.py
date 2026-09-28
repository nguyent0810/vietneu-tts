"""Chữ trên cùng khung hình đổi theo dòng nội dung (lane), không cố định.

Kênh Phật giáo từng in "SUY NGẪM" cho mọi bài, và in thêm tên style
(THUỶ MẶC, ÁNH SÁNG...) như thể đó là thông tin cho người xem. Test chốt
hai điều: lane nào cũng có chữ, và runner thật sự truyền lane xuống bridge.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _lanes():
    # Đọc bằng ast thay vì import: import bridge kéo theo kiểm external_bin.
    tree = ast.parse((ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SERIES_LANES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("không tìm thấy SERIES_LANES")


def test_bud_co_lane():
    assert {"niem", "phap", "doi"} <= set(_lanes()["bud"])


def test_lane_nao_cung_co_chu():
    for series, lanes in _lanes().items():
        for lane, kicker in lanes.items():
            assert kicker and kicker == kicker.upper(), (series, lane, kicker)


def test_khong_con_suy_ngam_lam_chu_mac_dinh_cho_lane():
    assert "SUY NGẪM" not in _lanes()["bud"].values()


def test_runner_truyen_lane():
    src = (ROOT / "hf_batch_render.py").read_text(encoding="utf-8")
    assert '"--lane", row["lane"]' in src


def test_bridge_nhan_lane():
    src = (ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--lane"', src)
    assert "lane=args.lane" in src
