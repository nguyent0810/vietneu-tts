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


def test_hoangdao_daily_sync_features():
    """Kiểm tra đồng bộ hoangdao_daily trong fs_calendar:
    - get_week_dates sinh đúng 7 ngày
    - viec_nen lọc bỏ 'cưới', 'đính hôn'
    - get_week_meta tạo tiêu đề task 34 và plan_item D-2
    - hoangdao_indep_check export thành công trong package
    """
    from fs_calendar import hoangdao_daily as HD
    import fs_calendar

    assert hasattr(fs_calendar, "hoangdao_indep_check")

    week = HD.get_week_dates("2026-10-22")
    assert len(week) == 7
    assert week[0] == "2026-10-22"
    assert week[-1] == "2026-10-28"

    f22 = HD.day_data(dt.date(2026, 10, 22))
    assert "viec_nen" in f22
    for v in f22["viec_nen"]:
        assert "cưới" not in v.lower()
        assert "đính hôn" not in v.lower()

    meta22 = HD.get_week_meta(dt.date(2026, 10, 22), day_idx=0)
    assert meta22["title"] == "Thứ Năm 22/10 Tam Nương: tuổi nào nên tránh, giờ nào tốt?"
    assert meta22["plan_item"]["day"] == "2026-10-20"
    assert meta22["plan_item"]["slot"] == "23:00"
    assert "cưới" not in meta22["insight"].lower()
    assert "đính hôn" not in meta22["insight"].lower()


def test_canchi_regression_1955():
    """Hồi quy can chi (task 99): 1955 là Ất Mùi, không phải Thân; và các năm mẫu."""
    assert C.can_chi(1955) == ("Ất", "Mùi")
    assert C.can_chi(1954) == ("Giáp", "Ngọ")
    assert C.can_chi(1956) == ("Bính", "Thân")
    assert C.can_chi(2026) == ("Bính", "Ngọ")
    assert C.can_chi(2027) == ("Đinh", "Mùi")


def test_tet_boundary_regression_1954_1956_2027():
    """Ranh giới Tết âm lịch cho các năm mẫu (task 99 & 99b): sinh trước Tết tính theo năm trước.
    Assert can chi năm âm cho ngày liền trước Tết và ngày Tết."""
    # 1955: Tết = 24/01/1955 (23/01/1955 -> Giáp Ngọ, 24/01/1955 -> Ất Mùi)
    assert A.lunar2solar(1, 1, 1955, 0) == (24, 1, 1955)
    d_pre_55 = A.solar2lunar(23, 1, 1955)
    d_tet_55 = A.solar2lunar(24, 1, 1955)
    assert d_pre_55 == (30, 12, 1954, 0)
    assert d_tet_55 == (1, 1, 1955, 0)
    assert C.can_chi(d_pre_55[2]) == ("Giáp", "Ngọ")
    assert C.can_chi(d_tet_55[2]) == ("Ất", "Mùi")

    # 1954: Tết = 03/02/1954 (02/02/1954 -> Quý Tỵ, 03/02/1954 -> Giáp Ngọ)
    assert A.lunar2solar(1, 1, 1954, 0) == (3, 2, 1954)
    d_pre_54 = A.solar2lunar(2, 2, 1954)
    d_tet_54 = A.solar2lunar(3, 2, 1954)
    assert d_pre_54 == (29, 12, 1953, 0)
    assert d_tet_54 == (1, 1, 1954, 0)
    assert C.can_chi(d_pre_54[2]) == ("Quý", "Tỵ")
    assert C.can_chi(d_tet_54[2]) == ("Giáp", "Ngọ")

    # 1956: Tết = 12/02/1956 (11/02/1956 -> Ất Mùi, 12/02/1956 -> Bính Thân)
    assert A.lunar2solar(1, 1, 1956, 0) == (12, 2, 1956)
    d_pre_56 = A.solar2lunar(11, 2, 1956)
    d_tet_56 = A.solar2lunar(12, 2, 1956)
    assert d_pre_56 == (30, 12, 1955, 0)
    assert d_tet_56 == (1, 1, 1956, 0)
    assert C.can_chi(d_pre_56[2]) == ("Ất", "Mùi")
    assert C.can_chi(d_tet_56[2]) == ("Bính", "Thân")

    # 2027: Tết = 06/02/2027 (05/02/2027 -> Bính Ngọ, 06/02/2027 -> Đinh Mùi)
    assert A.lunar2solar(1, 1, 2027, 0) == (6, 2, 2027)
    d_pre_27 = A.solar2lunar(5, 2, 2027)
    d_tet_27 = A.solar2lunar(6, 2, 2027)
    assert d_pre_27 == (29, 12, 2026, 0)
    assert d_tet_27 == (1, 1, 2027, 0)
    assert C.can_chi(d_pre_27[2]) == ("Bính", "Ngọ")
    assert C.can_chi(d_tet_27[2]) == ("Đinh", "Mùi")


def _check_yeartable_row_chi_safety(label: str, tag: str, years: list[int], source_id: str = ""):
    """Quy tắc kiểm nhãn hàng bảng yeartable:
    - Nếu nhãn là tên chi trần (1 trong 12 con giáp, không kèm 'KIM LÂU')
      thì mọi năm trong hàng phải đúng chi đó.
    - Nhãn có tiền tố rõ ràng như 'KIM LÂU THÂN' không bị nhầm là tên chi trần.
    """
    lbl = str(label).strip()
    if "KIM LÂU" in lbl.upper():
        return
    chi_set = set(C.CHI)
    if lbl.title() in chi_set:
        expected_chi = lbl.title()
        for y in years:
            can, chi = C.can_chi(y)
            assert chi == expected_chi, (
                f"Lỗi nhãn bảng ({source_id}): "
                f"Hàng '{label}' ({tag}) chứa năm {y} là tuổi {chi}, không phải {expected_chi}!"
            )


def test_yeartable_chi_label_safety():
    """Kiểm tra nhãn bảng yeartable (task 99 & 99b):
    - Đọc dữ liệu từ fixture trong repo: tests/fixtures/yeartable_rows.json.
    - assert danh sách đầu vào không rỗng.
    - Logic: nhãn chứa đúng tên 1 chi trần (không kèm 'KIM LÂU') thì mọi năm phải đúng chi đó.
    - Ca âm tính: nhãn trần 'THÂN' cũ kèm năm 1955 phạm lỗi PHẢI bị bắt (tái hiện lỗi cũ 99).
    """
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "yeartable_rows.json"
    assert fixture_path.is_file(), f"Không tìm thấy fixture {fixture_path}"

    items = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert isinstance(items, list), "Fixture phải là một list"
    assert len(items) > 0, "Danh sách items fixture không được rỗng"

    total_rows = 0
    for it in items:
        rows = it.get("rows", [])
        assert len(rows) > 0, f"Item {it.get('id')} không có rows"
        for r in rows:
            assert len(r) >= 3, f"Hàng không đủ cấu trúc [label, tag, years]: {r}"
            label, tag, years = r[0], r[1], r[2]
            assert isinstance(years, list) and len(years) > 0, f"Hàng {label} không có danh sách năm hợp lệ"
            _check_yeartable_row_chi_safety(label, tag, years, source_id=it.get("id", ""))
            total_rows += 1

    assert total_rows >= 15, f"Tổng số hàng kiểm tra phải >= 15 (thực tế: {total_rows})"

    # Ca âm tính (tái hiện lỗi cũ trước task 99):
    # Nhãn trần "THÂN" chứa năm 1955 (Ất Mùi, không phải Thân) PHẢI ném AssertionError
    with pytest.raises(AssertionError, match="tuổi Mùi"):
        _check_yeartable_row_chi_safety("THÂN", "DƯ 1 · KIM LÂU", [1955, 1964, 1973, 1982, 1991, 2000, 2009], source_id="old_bug_repro")


