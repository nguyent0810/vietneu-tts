"""Regression test cho short_segment_discovery.py -- tách ra khỏi
short_batch_runner.py để health-check không phải kéo theo toàn bộ runner
(xem docstring module đó). Nội dung/logic giữ NGUYÊN VẸN so với bản gốc --
test này khoá đúng hành vi cũ, đặc biệt 2 bug thật đã sửa trước đây (dedup
collision qua seen_files, không suy đoán loại nội dung sai)."""
from pathlib import Path

import short_segment_discovery as sd


def _write_short_file(dir_: Path, name: str, content: str) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    p = dir_ / name
    p.write_text(content, encoding="utf-8")
    return p


def test_discover_segments_parses_markers_and_full_record_shape(tmp_path, monkeypatch):
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    source_dir = tmp_path / "drive_input" / "content_repo_staged" / "Phật giáo" / "Short"
    _write_short_file(source_dir, "06_ABC_Short.txt", "*** 1\nĐoạn một.\n*** 2\nĐoạn hai.\n")

    segments = sd.discover_segments(["06"], "Phật giáo")

    assert segments == [
        {"key": "06_ABC_01", "episode": "06_ABC", "segment_index": 1, "text": "Đoạn một."},
        {"key": "06_ABC_02", "episode": "06_ABC", "segment_index": 2, "text": "Đoạn hai."},
    ]


def test_discover_segments_skips_empty_trailing_segment(tmp_path, monkeypatch):
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    source_dir = tmp_path / "drive_input" / "content_repo_staged" / "T" / "Short"
    _write_short_file(source_dir, "X_Y_Short.txt", "*** 1\nCó nội dung.\n*** 2\n   \n")

    segments = sd.discover_segments(["X"], "T")
    assert len(segments) == 1
    assert segments[0]["segment_index"] == 1


def test_discover_segments_no_markers_returns_empty(tmp_path, monkeypatch):
    # BUG THẬT trong bản test đầu tiên (Codex CLI review round 2): tên file
    # "X_Short.txt" KHÔNG khớp glob "X_*_Short.txt" -- test cũ vô tình đi
    # vào nhánh "không tìm thấy file" thay vì "file có nhưng không có
    # marker". Sửa đúng tên file để thật sự exercise nhánh cần test.
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    source_dir = tmp_path / "drive_input" / "content_repo_staged" / "T" / "Short"
    _write_short_file(source_dir, "X_Y_Short.txt", "Không có marker nào ở đây.")

    assert sd.discover_segments(["X"], "T") == []


def test_discover_segments_missing_prefix_warns_and_continues(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    (tmp_path / "drive_input" / "content_repo_staged" / "T" / "Short").mkdir(parents=True)

    segments = sd.discover_segments(["KHONG_TON_TAI"], "T")
    assert segments == []
    assert "CẢNH BÁO" in capsys.readouterr().err


def test_discover_segments_dedups_nested_prefix_collision(tmp_path, monkeypatch):
    """BUG THẬT đã sửa (xem docstring discover_segments): prefix "A" và
    "A_B" cùng khớp file "A_B_C_Short.txt" -- phải xử lý file đó ĐÚNG 1
    LẦN, không sinh 2 segment trùng key."""
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    source_dir = tmp_path / "drive_input" / "content_repo_staged" / "T" / "Short"
    _write_short_file(source_dir, "A_B_C_Short.txt", "*** 1\nNội dung.\n")

    segments = sd.discover_segments(["A", "A_B"], "T")
    assert len(segments) == 1
    assert segments[0]["key"] == "A_B_C_01"


def test_discover_segments_multiple_files_same_prefix_all_processed(tmp_path, monkeypatch):
    """BUG THẬT đã sửa: generator xoay vòng evergreen (vd western_zodiac)
    có nhiều file cùng khớp 1 prefix rút gọn -- TẤT CẢ phải được xử lý,
    không chỉ file đầu tiên."""
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    source_dir = tmp_path / "drive_input" / "content_repo_staged" / "T" / "Short"
    _write_short_file(source_dir, "CUNGHD_XuNu_Short.txt", "*** 1\nXử Nữ.\n")
    _write_short_file(source_dir, "CUNGHD_KimNguu_Short.txt", "*** 1\nKim Ngưu.\n")

    segments = sd.discover_segments(["CUNGHD"], "T")
    keys = sorted(s["key"] for s in segments)
    assert keys == ["CUNGHD_KimNguu_01", "CUNGHD_XuNu_01"]


def test_discover_all_episode_prefixes_derives_correct_prefixes(tmp_path, monkeypatch):
    # discover_all_episode_prefixes() bỏ đi CỤM CUỐI (loại nội dung) sau khi
    # bỏ hậu tố "_Short.txt" -- "06_ABC_Short.txt" -> prefix "06" (bỏ "ABC"),
    # "CUNGHD_XuNu_Short.txt" -> prefix "CUNGHD" (bỏ "XuNu"). Đây ĐÚNG hành
    # vi gốc đã ghi trong docstring, không phải lỗi.
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    source_dir = tmp_path / "drive_input" / "content_repo_staged" / "T" / "Short"
    _write_short_file(source_dir, "06_ABC_Short.txt", "*** 1\nx\n")
    _write_short_file(source_dir, "CUNGHD_XuNu_Short.txt", "*** 1\nx\n")

    prefixes = sd.discover_all_episode_prefixes("T")
    assert prefixes == sorted(["06", "CUNGHD"])


def test_discover_all_episode_prefixes_empty_dir_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    (tmp_path / "drive_input" / "content_repo_staged" / "T" / "Short").mkdir(parents=True)
    assert sd.discover_all_episode_prefixes("T") == []
