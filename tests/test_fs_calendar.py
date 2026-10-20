"""Kiểm tra package fs_calendar:
- Tự kiểm 7 ngày verified (từ calendar_facts_verified.json)
- Tết 2027 âm lịch = 06/02/2027 dương lịch
- 21/10/2026 = Mậu Thìn, trực Phá, sao Thanh Long
- Hoang Ốc 2027: đúng 31 năm sinh phạm Hoang Ốc xấu trong giai đoạn 1950-2010
- Tam Tai 2027: đúng 15 năm sinh phạm Tam Tai (nhóm Hợi - Mão - Mùi) trong giai đoạn 1950-2010
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import pytest

from fs_calendar import amlich as A
from fs_calendar import canchi as C
from fs_calendar import tuvi_year as T
from fs_calendar import ngaytot as N


def test_verified_7_days():
    """Tự kiểm 7 ngày verified đối chiếu ngày đẹp / âm lịch chuẩn."""
    verified_file = Path(__file__).resolve().parent.parent / "fs_calendar" / "calendar_facts_verified.json"
    assert verified_file.is_file(), f"Không tìm thấy {verified_file}"
    ver = json.loads(verified_file.read_text(encoding="utf-8"))
    assert len(ver) == 7

    for iso, want in ver.items():
        y, m, d = (int(x) for x in iso.split("-"))
        f = N.fact(dt.date(y, m, d))
        assert f["am"] == want["am_lich"]
        assert f["ngay"] == want["ngay"]
        assert f["than"] == want["than"]
        assert f["truc"] == want["truc"]
        assert f["xung"] == want["xung"]
        want_hoang = want["hoang_hac"] == "hoàng đạo"
        assert f["hoang"] == want_hoang


def test_tet_2027():
    """Tết Nguyên Đán Đinh Mùi 2027 (mùng 1 tháng Giêng âm lịch) = 06/02/2027 dương lịch."""
    # Mùng 1 Tết Đinh Mùi 2027: ngày 1, tháng 1, năm 2027 âm lịch, không nhuận (0)
    day, month, year = A.lunar2solar(1, 1, 2027, 0)
    assert (day, month, year) == (6, 2, 2027)

    # Chiều ngược lại: ngày 06/02/2027 đổi sang âm lịch phải là 1/1/2027
    l_day, l_month, l_year, leap = A.solar2lunar(6, 2, 2027)
    assert (l_day, l_month, l_year, leap) == (1, 1, 2027, 0)


def test_mau_thin_20261021():
    """Ngày 21/10/2026 dương lịch: can chi Mậu Thìn, trực Phá, sao Thanh Long (Hoàng đạo)."""
    f = N.fact(dt.date(2026, 10, 21))
    assert f["ngay"] == "Mậu Thìn"
    assert f["truc"] == "Phá"
    assert f["than"] == "Thanh Long"
    assert f["hoang"] is True


def test_hoang_oc_2027_31_years():
    """Năm 2027: kiểm tra đúng 31 năm sinh phạm Hoang Ốc xấu (Tam Địa Sát, Ngũ Thọ Tử, Lục Hoang Ốc) trong dải 1950-2010."""
    bad_years = []
    for y in range(1950, 2011):
        age = T.tuoi(y, 2027)
        ho = T.hoang_oc(age)
        if ho in T.HO_XAU:
            bad_years.append(y)

    assert len(bad_years) == 31
    expected_bad_years = [
        1950, 1953, 1954, 1956, 1959, 1962, 1963, 1965, 1968, 1971,
        1972, 1974, 1977, 1978, 1980, 1981, 1983, 1986, 1987, 1989,
        1990, 1992, 1995, 1996, 1998, 1999, 2001, 2004, 2005, 2007, 2010
    ]
    assert bad_years == expected_bad_years


def test_tam_tai_2027_15_years():
    """Năm 2027 (Đinh Mùi): nhóm tam hợp Hợi - Mão - Mùi phạm Tam Tai năm thứ 3.
    Trong dải 1950-2010 có đúng 15 năm sinh phạm Tam Tai."""
    tt_years = []
    for y in range(1950, 2011):
        chi = C.can_chi(y)[1]
        if "Mùi" in T.tam_tai_years(chi):
            tt_years.append(y)

    assert len(tt_years) == 15
    expected_tt_years = [
        1951, 1955, 1959, 1963, 1967, 1971, 1975, 1979, 1983, 1987,
        1991, 1995, 1999, 2003, 2007
    ]
    assert tt_years == expected_tt_years
