"""Hook short: 3 tiêu đề stay thấp phải dính cờ, 3 tiêu đề stay cao phải qua."""
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "output" / "cl_staging" / "scoreboard" / "hook_lint.py"
import pytest as _pt  # noqa: E402
if not (Path(__file__).resolve().parents[1] / "output/cl_staging/scoreboard/hook_lint.py").exists():   # công cụ ở output/ (gitignore): CI không có
    _pt.skip("output/cl_staging/scoreboard/hook_lint.py chỉ có trên máy dựng", allow_module_level=True)
spec = importlib.util.spec_from_file_location("hook_lint", MODULE)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

TERMS = M.load_terms()

CATCH = [
    "Chánh niệm có phải là mặc kệ ngày mai?",
    "Thương con có phải là làm hết cho con?",
    "Thái cực sinh lưỡng nghi nghĩa là gì?",
    "Phong thủy, Tử Vi, Bát Tự có phải là một?",
]
PASS = [
    "Vì sao nhà sư cạo tóc?",
    "Địa ngục có phải là bản án vĩnh viễn?",
    "1984, 1985: mệnh Hải Trung Kim",
]
EDGE = "Vô thường có phải là mất mát?"


def _row(title, **extra):
    row = {"id": "t", "title": title, "script": [title]}
    row.update(extra)
    return row


def flags(title, **extra):
    return M.lint_row(_row(title, **extra), TERMS)["flags"]


def test_terms_include_the_named_concepts():
    needed = ["chánh niệm", "buông bỏ", "vô thường", "từ bi", "trung đạo", "nhân quả", "thái cực", "ngũ hành"]
    for word in needed:
        assert word in TERMS["concepts"]


def test_three_low_stay_titles_are_flagged():
    assert "TRUU_TUONG" in flags(CATCH[0])
    assert "KHONG_DANH_TU_CU_THE" in flags(CATCH[0])
    assert "TRUU_TUONG" in flags(CATCH[1])
    assert "TRUU_TUONG" in flags(CATCH[2])
    assert "KHONG_DANH_TU_CU_THE" in flags(CATCH[2])
    assert "TRUU_TUONG" in flags(CATCH[3])
    assert "KHONG_DANH_TU_CU_THE" in flags(CATCH[3])


def test_three_high_stay_titles_pass():
    for title in PASS:
        assert flags(title) == []


def test_vo_thuong_edge_is_flagged_as_abstract_pattern():
    """1.078 view không nằm trong bộ kiểm. 'vô thường' có trong danh sách và câu khớp 'có phải là'."""
    got = flags(EDGE)
    assert "TRUU_TUONG" in got
    assert "KHONG_DANH_TU_CU_THE" in got


def test_dia_nguc_pattern_is_not_abstract():
    hit = M.lint_row(_row(PASS[1]), TERMS)
    assert "TRUU_TUONG" not in hit["flags"]
    assert hit["flags"] == []


def test_first_sentence_can_flag_when_title_is_concrete():
    hit = M.lint_row(
        {
            "id": "s",
            "title": "Vì sao nhà sư cạo tóc?",
            "script": ["**Vô thường** có phải là mất mát?"],
        },
        TERMS,
    )
    assert hit["flags"] == ["TRUU_TUONG"]
    assert hit["where"]["TRUU_TUONG"] == ["câu đầu"]


def test_opening_frame_needs_an_image_or_a_year():
    word = {"visuals": {"1": {"type": "word", "text": "THÁI CỰC"}}}
    assert "KHUNG_DAU_TRONG" in flags(PASS[0], **word)
    year = {"visuals": {"1": {"type": "word", "text": "1984 · 1985"}}}
    assert flags(PASS[2], **year) == []
    pictured = {"image": "chunks_cache/museum/cma_128067.jpg", "visuals": {"2": {"type": "word", "text": "CHỮ"}}}
    assert flags(PASS[0], **pictured) == []
    later = {"media": {"2": {"kind": "image", "query": "monk shaving head"}}, "visuals": {"4": {"type": "illus", "scene": "lotus"}}}
    assert "KHUNG_DAU_TRONG" in flags(PASS[0], **later)
    listed = {"visuals": {"1": {"type": "list", "title": "BA LẠY", "items": []}}}
    assert "KHUNG_DAU_TRONG" not in flags(PASS[0], **listed)
    assert flags(PASS[0]) == []


def test_empty_visual_slot_and_slash_date_are_not_false_flags():
    calendar = _row(
        "24/10 Rằm tháng 9: ngày hoàng đạo hay hắc đạo?",
        media={},
        visuals={},
        style="daytable",
    )
    assert "KHUNG_DAU_TRONG" not in M.lint_row(calendar, TERMS)["flags"]
    assert flags("Thứ Hai 26/10: tuổi nào nên tránh, giờ nào tốt?") == []


def test_raft_and_precept_titles_are_not_the_banned_pattern():
    assert "TRUU_TUONG" in flags("Vì sao Phật ví giáo pháp như chiếc bè?")
    assert "TRUU_TUONG" in flags("Giới không uống rượu là để giữ điều gì?")


def test_high_stay_concepts_and_concrete_action_pass():
    for title in (
        "Hồi hướng công đức",
        "Trung đạo có phải là luôn đứng ở giữa?",
        "Vì sao nhà sư cạo tóc?",
    ):
        hit = M.lint_row(_row(title), TERMS)
        assert "TRUU_TUONG" not in hit["flags"]
        assert M.blocking_flags(hit["flags"]) == []


def test_noun_specificity_is_advisory_not_blocking():
    hit = M.lint_row(_row("Tại sao không nên ngồi quay lưng ra cửa?"), TERMS)
    assert "KHONG_DANH_TU_CU_THE" in hit["flags"]
    assert M.blocking_flags(hit["flags"]) == []


def test_cli_exit_code(tmp_path):
    good = tmp_path / "good.json"
    bad = tmp_path / "bad.json"
    good.write_text(json.dumps([_row(title, id=f"g{i}") for i, title in enumerate(PASS)]), encoding="utf-8")
    bad.write_text(json.dumps([_row(title, id=f"b{i}") for i, title in enumerate(CATCH + [EDGE])]), encoding="utf-8")
    ok = subprocess.run([sys.executable, str(MODULE), str(good)], capture_output=True, text=True)
    assert ok.returncode == 0
    assert "TỔNG: 3 bài, dính cờ chặn 0" in ok.stdout
    failed = subprocess.run([sys.executable, str(MODULE), str(bad)], capture_output=True, text=True)
    assert failed.returncode == 1
    assert "TỔNG: 5 bài, dính cờ chặn 5" in failed.stdout
    assert "TRUU_TUONG" in failed.stdout


def test_unpublished_skips_aired_and_replaced(tmp_path):
    bud = tmp_path / "bud"
    bud.mkdir()
    (bud / "plan_old.json").write_text(json.dumps([
        {"id": "old", "day": "2026-10-25", "slot": "11:00", "title": CATCH[0], "script": [CATCH[0]]},
        {"id": "past", "day": "2026-10-01", "slot": "11:00", "title": CATCH[2], "script": [CATCH[2]]},
    ]), encoding="utf-8")
    (bud / "plan_new.json").write_text(json.dumps([
        {
            "id": "new",
            "day": "2026-10-25",
            "slot": "11:00",
            "replaces": "old",
            "title": PASS[0],
            "script": [PASS[0]],
            "image": "a.jpg",
        },
    ]), encoding="utf-8")
    (tmp_path / "fs").mkdir()
    now = datetime(2026, 10, 22, tzinfo=timezone.utc)
    rows = M.unpublished_rows(tmp_path, now)
    assert [row["id"] for row in rows] == ["new"]
    at_slot = datetime(2026, 10, 25, 11, 0, tzinfo=timezone.utc)
    assert M.unpublished_rows(tmp_path, at_slot) == []
    just_before = datetime(2026, 10, 25, 10, 59, tzinfo=timezone.utc)
    assert [row["id"] for row in M.unpublished_rows(tmp_path, just_before)] == ["new"]
