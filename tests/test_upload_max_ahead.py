"""Unit test cho cơ chế hẹn lịch cuốn chiếu <= 7 ngày (MAX_AHEAD_DAYS = 7).

Sử dụng hàm thuần is_too_far tách riêng từ upload_fs và upload_bud để không gọi API YouTube.
"""
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load_module(name: str, rel_path: str):
    path = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


import pytest as _pt  # noqa: E402
if not (Path(__file__).resolve().parents[1] / "output/cl_staging/fs/upload_fs.py").exists():   # công cụ ở output/ (gitignore): CI không có
    _pt.skip("output/cl_staging/fs/upload_fs.py chỉ có trên máy dựng", allow_module_level=True)
upload_fs = _load_module("upload_fs", "output/cl_staging/fs/upload_fs.py")
upload_bud = _load_module("upload_bud", "output/cl_staging/bud/upload_bud.py")


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_constant_max_ahead_days(mod):
    assert hasattr(mod, "MAX_AHEAD_DAYS")
    assert mod.MAX_AHEAD_DAYS == 7


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_within_7_days_allowed(mod):
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    r = {"id": "test_01", "lane": "kinhdich"}

    # Trong vòng 7 ngày
    assert mod.is_too_far(r, now + timedelta(days=1), now=now) is False
    assert mod.is_too_far(r, now + timedelta(days=6), now=now) is False
    # Đúng mốc 7 ngày (không > 7 ngày)
    assert mod.is_too_far(r, now + timedelta(days=7), now=now) is False


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_exceeding_7_days_blocked(mod):
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    r = {"id": "test_02", "lane": "kinhdich"}

    # Vừa quá 7 ngày
    assert mod.is_too_far(r, now + timedelta(days=7, seconds=1), now=now) is True
    # Quá 8 ngày, 14 ngày, 30 ngày
    assert mod.is_too_far(r, now + timedelta(days=8), now=now) is True
    assert mod.is_too_far(r, now + timedelta(days=14), now=now) is True
    assert mod.is_too_far(r, now + timedelta(days=30), now=now) is True


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_exception_lane_ngaytot(mod):
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    r = {"id": "nt_cuoi_2027_01", "lane": "ngaytot"}

    # Bài cưới hỏi trước 3-5 tháng (90 - 150 ngày) phải được phép (không chặn)
    assert mod.is_too_far(r, now + timedelta(days=90), now=now) is False
    assert mod.is_too_far(r, now + timedelta(days=150), now=now) is False
    assert mod.is_too_far(r, now + timedelta(days=365), now=now) is False


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_exception_allow_far(mod):
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)

    # Có allow_far: True
    r_allowed = {"id": "far_ok", "lane": "tuong", "allow_far": True}
    assert mod.is_too_far(r_allowed, now + timedelta(days=30), now=now) is False

    # allow_far: False hoặc None -> bị chặn nếu quá 7 ngày
    r_blocked = {"id": "far_no", "lane": "tuong", "allow_far": False}
    assert mod.is_too_far(r_blocked, now + timedelta(days=30), now=now) is True

    r_none = {"id": "far_none", "lane": "tuong"}
    assert mod.is_too_far(r_none, now + timedelta(days=30), now=now) is True


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_other_lanes_not_exempt(mod):
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    far_time = now + timedelta(days=10)

    for lane in ["tuoi", "nhao", "lich", "kinhdich", "phap", "niem", "doi", "tuong", "jataka", "hoangdao_daily"]:
        r = {"id": f"test_{lane}", "lane": lane}
        assert mod.is_too_far(r, far_time, now=now) is True


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_string_iso_publish_at(mod):
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    r = {"id": "str_test"}

    # Trong 7 ngày (ISO format)
    assert mod.is_too_far(r, "2026-10-25T12:00:00Z", now=now) is False
    # Quá 7 ngày
    assert mod.is_too_far(r, "2026-10-29T12:00:00Z", now=now) is True


@pytest.mark.parametrize("mod", [upload_fs, upload_bud])
def test_infer_when_from_row(mod):
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)

    r_near = {"id": "near", "day": "2026-10-25", "slot": "12:00"}
    assert mod.is_too_far(r_near, now=now) is False

    r_far = {"id": "far", "day": "2026-10-30", "slot": "12:00"}
    assert mod.is_too_far(r_far, now=now) is True


def test_parity_fs_and_bud():
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    test_cases = [
        ({"lane": "ngaytot"}, now + timedelta(days=100)),
        ({"allow_far": True}, now + timedelta(days=100)),
        ({"lane": "phap"}, now + timedelta(days=5)),
        ({"lane": "phap"}, now + timedelta(days=8)),
        ({"lane": "tuoi", "allow_far": False}, now + timedelta(days=15)),
    ]
    for r, when in test_cases:
        res_fs = upload_fs.is_too_far(r, when, now=now)
        res_bud = upload_bud.is_too_far(r, when, now=now)
        assert res_fs == res_bud
