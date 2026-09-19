"""Regression test cho quy tắc sản xuất chuẩn (2026-09-04): Short ĐẦU TIÊN
đăng mỗi ngày trên kênh Phong Thuỷ phải là nội dung Lịch Hoàng Đạo của
CHÍNH ngày đó (xem short_batch_runner.lich_hoang_dao_publish_slot()).

Khoá lại:
1. Episode đúng định dạng LICHYYYYMMDD_LichHoangDao -> slot CỐ ĐỊNH 23:00
   UTC ngày hôm TRƯỚC ngày mục tiêu (= 6h sáng ICT đúng ngày mục tiêu),
   sớm hơn cả 4 slot FS khác (15h/18h/19h30/21h ICT) -- tự động là Short
   đầu tiên trong ngày.
2. Episode KHÔNG khớp định dạng (nội dung FS khác, hoặc lỗi tên file) ->
   trả None, fail-closed về nhánh round-robin thường (next_available_slot),
   KHÔNG tự đoán ngày.
3. Ngày mục tiêu không hợp lệ (vd tháng 13) -> None, không crash.
"""
from datetime import date

import short_batch_runner as sbr


def test_valid_episode_returns_6am_ict_fixed_slot():
    iso, slot = sbr.lich_hoang_dao_publish_slot("LICH20260906_LichHoangDao")
    assert iso == "2026-09-05T23:00:00Z"  # 23:00 UTC 05/09 == 06:00 ICT 06/09
    assert slot["utc_time"] == sbr.LICH_HOANG_DAO_UTC_TIME
    assert "2026-09-06" in slot["label"]


def test_fixed_slot_earlier_ict_than_all_other_fs_slots():
    _, lich_slot = sbr.lich_hoang_dao_publish_slot("LICH20260906_LichHoangDao")
    lich_hh, lich_mm = map(int, lich_slot["utc_time"].split(":"))
    lich_ict_minutes = (lich_hh * 60 + lich_mm + 7 * 60) % (24 * 60)
    for other in sbr.PHONG_THUY_TIME_SLOTS:
        hh, mm = map(int, other["utc_time"].split(":"))
        other_ict_minutes = (hh * 60 + mm + 7 * 60) % (24 * 60)
        assert lich_ict_minutes < other_ict_minutes, (lich_slot, other)


def test_non_matching_episode_returns_none():
    assert sbr.lich_hoang_dao_publish_slot("KIENTHUC_Nmkinhinccaphongthy") is None
    assert sbr.lich_hoang_dao_publish_slot("CHUYENKE_Hailsngcchiu") is None
    assert sbr.lich_hoang_dao_publish_slot("LICH20260906_LichHoangDao_extra") is None
    assert sbr.lich_hoang_dao_publish_slot("LICH2026090_LichHoangDao") is None


def test_invalid_calendar_date_returns_none_not_crash():
    assert sbr.lich_hoang_dao_publish_slot("LICH20261332_LichHoangDao") is None
    assert sbr.lich_hoang_dao_publish_slot("LICH20260231_LichHoangDao") is None


def test_target_date_parsed_from_filename_matches_generator_naming():
    # Khớp đúng lich_hoang_dao_generator.write_short_bundle_file():
    # ep_prefix = f"LICH{target_date.strftime('%Y%m%d')}"
    target = date(2026, 9, 10)
    episode = f"LICH{target.strftime('%Y%m%d')}_LichHoangDao"
    iso, _ = sbr.lich_hoang_dao_publish_slot(episode)
    assert iso == "2026-09-09T23:00:00Z"
