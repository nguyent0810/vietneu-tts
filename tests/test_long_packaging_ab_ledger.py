from pathlib import Path
import pytest
from tools.long_packaging.ab_ledger import (
    add_entry,
    get_entry,
    load_ledger,
    update_entry,
)


def test_ab_ledger_lifecycle(tmp_path: Path):
    ledger_file = tmp_path / "packaging_ab.jsonl"

    # 1. Thêm bản ghi mới
    entry = {
        "video_id": "vid123",
        "key": "L_fs_tv06",
        "variants": {"A": "Title A", "B": "Title B"},
        "start_date": "2026-11-12",
        "rule": "L1",
        "notes": "Test thử L1",
    }
    rec = add_entry(entry, ledger_path=ledger_file)
    assert rec["video_id"] == "vid123"
    assert rec["winner"] == "PENDING"

    # Đọc lại
    entries = load_ledger(ledger_path=ledger_file)
    assert len(entries) == 1
    assert entries[0]["key"] == "L_fs_tv06"

    # 2. Lấy chi tiết
    found = get_entry("L_fs_tv06", ledger_path=ledger_file)
    assert found is not None
    assert found["video_id"] == "vid123"

    # 3. Cập nhật kết quả thắng
    updates = {
        "winner": "B",
        "end_date": "2026-11-20",
        "impressions": {"A": 5000, "B": 5200},
        "ctr": {"A": 7.2, "B": 8.4},
        "notes": "B thắng rõ rệt",
    }
    updated = update_entry("vid123", updates, ledger_path=ledger_file)
    assert updated["winner"] == "B"
    assert updated["ctr"]["B"] == 8.4
    assert updated["impressions"]["A"] == 5000

    # Kiểm tra load_ledger sau khi đóng
    entries_after = load_ledger(ledger_path=ledger_file)
    assert len(entries_after) == 1
    assert entries_after[0]["winner"] == "B"


def test_ab_ledger_validation(tmp_path: Path):
    ledger_file = tmp_path / "packaging_ab.jsonl"
    with pytest.raises(ValueError):
        add_entry({"rule": "L1"}, ledger_path=ledger_file)

    with pytest.raises(KeyError):
        update_entry("non_existent", {"winner": "A"}, ledger_path=ledger_file)
