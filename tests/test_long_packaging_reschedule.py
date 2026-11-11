import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from tools.long_packaging.reschedule import (
    normalize_target_time,
    reschedule_channel,
    reschedule_videos,
)


def test_normalize_target_time():
    assert normalize_target_time("11-12", year=2026, time_utc="13:00") == "2026-11-12T13:00"
    assert normalize_target_time("2026-11-14", year=2026, time_utc="13:00") == "2026-11-14T13:00"
    assert normalize_target_time("2026-11-14T15:30:00Z") == "2026-11-14T15:30"


def test_reschedule_occupied_slot_resolution():
    """Video 1 muốn sang slot của Video 2; Video 2 dời trước, Video 1 dời sau."""
    current_rows = {
        "V1": {"id": "id_1", "when": "2026-11-10T13:00:00Z", "title": "Vid 1"},
        "V2": {"id": "id_2", "when": "2026-11-12T13:00:00Z", "title": "Vid 2"},
    }
    # V1 muốn tới 11-12 (đang bị V2 chiếm), V2 muốn tới 11-14 (ô trống)
    target_map = {
        "V1": "11-12",
        "V2": "11-14",
    }

    mock_update = MagicMock()
    logs = reschedule_channel(
        ch="fs",
        target_map=target_map,
        current_rows=current_rows,
        creds_path="dummy_cred",
        confirm=True,
        update_fn=mock_update,
    )

    assert len(logs) == 2
    # V2 phải dời trước
    assert logs[0]["key"] == "V2"
    assert logs[0]["new"] == "2026-11-14T13:00:00Z"
    # Sau đó V1 mới dời vào 11-12
    assert logs[1]["key"] == "V1"
    assert logs[1]["new"] == "2026-11-12T13:00:00Z"
    assert mock_update.call_count == 2


def test_reschedule_cycle_resolution():
    """V1 ở ô A muốn sang ô B; V2 ở ô B muốn sang ô A (vòng lặp phụ thuộc)."""
    current_rows = {
        "V1": {"id": "id_1", "when": "2026-11-10T13:00:00Z", "title": "Vid 1"},
        "V2": {"id": "id_2", "when": "2026-11-12T13:00:00Z", "title": "Vid 2"},
    }
    target_map = {
        "V1": "11-12",
        "V2": "11-10",
    }
    mock_update = MagicMock()
    logs = reschedule_channel(
        ch="fs",
        target_map=target_map,
        current_rows=current_rows,
        creds_path="dummy_cred",
        confirm=True,
        update_fn=mock_update,
    )
    # Vòng lặp được phá bằng bước đệm tạm thời
    assert any(log.get("is_temp") for log in logs)
    # Cuối cùng cả hai đều đạt đích
    final_v1 = [l for l in logs if l["key"] == "V1"][-1]
    final_v2 = [l for l in logs if l["key"] == "V2"][-1]
    assert final_v1["new"] == "2026-11-12T13:00:00Z"
    assert final_v2["new"] == "2026-11-10T13:00:00Z"


def test_reschedule_dry_run_and_recovery_file(tmp_path: Path):
    current_data = {
        "fs": [
            {"key": "V1", "id": "id_1", "when": "2026-11-10T13:00:00Z", "title": "Vid 1"},
            {"key": "V2", "id": "id_2", "when": "2026-11-12T13:00:00Z", "title": "Vid 2"},
        ]
    }
    schedule_data = {
        "fs": {"V1": "11-14", "V2": "11-16"}
    }
    mock_update = MagicMock()
    recovery_file = tmp_path / "recovery.json"

    # 1. Dry run: không gọi update_fn
    reschedule_videos(
        schedule_data=schedule_data,
        current_data=current_data,
        confirm=False,
        recovery_file=recovery_file,
        update_fn=mock_update,
    )
    assert mock_update.call_count == 0
    assert not recovery_file.exists()

    # 2. Confirm: gọi update_fn và tạo recovery_file
    reschedule_videos(
        schedule_data=schedule_data,
        current_data=current_data,
        confirm=True,
        recovery_file=recovery_file,
        update_fn=mock_update,
    )
    assert mock_update.call_count == 2
    assert recovery_file.exists()
    rec_data = json.load(recovery_file.open())
    assert len(rec_data) == 2


def test_reschedule_subset_channel():
    """Kiểm tra Point 7: Cho phép dời lịch cho tập con video (không ép set(target) == set(current))."""
    current_rows = {
        "V1": {"id": "id_1", "when": "2026-11-10T13:00:00Z", "title": "Vid 1"},
        "V2": {"id": "id_2", "when": "2026-11-12T13:00:00Z", "title": "Vid 2"},
        "V3": {"id": "id_3", "when": "2026-11-14T13:00:00Z", "title": "Vid 3"},
    }
    # Chỉ dời V1 sang 11-16, giữ nguyên V2 và V3
    target_map = {"V1": "11-16"}

    mock_update = MagicMock()
    logs = reschedule_channel(
        ch="fs",
        target_map=target_map,
        current_rows=current_rows,
        creds_path="dummy_cred",
        confirm=True,
        update_fn=mock_update,
    )
    assert len(logs) == 1
    assert logs[0]["key"] == "V1"
    assert logs[0]["new"] == "2026-11-16T13:00:00Z"
    assert mock_update.call_count == 1


def test_reschedule_unknown_video_raises_value_error():
    """Kiểm tra Point 7: Video không tồn tại thì raise ValueError chứ không dùng assert / AssertionError."""
    current_rows = {
        "V1": {"id": "id_1", "when": "2026-11-10T13:00:00Z", "title": "Vid 1"},
    }
    target_map = {"V_UNKNOWN": "11-16"}

    with pytest.raises(ValueError, match="không tồn tại ở kênh"):
        reschedule_channel(
            ch="fs",
            target_map=target_map,
            current_rows=current_rows,
            creds_path="dummy_cred",
            confirm=False,
        )


def test_no_assert_in_reschedule_code():
    """Kiểm tra Point 7: Không dùng câu lệnh assert trong production code reschedule.py."""
    import inspect
    import tools.long_packaging.reschedule as mod
    source = inspect.getsource(mod)
    # Loại trừ docstrings hoặc comments
    code_lines = [
        line.strip() for line in source.splitlines()
        if not line.strip().startswith("#") and not line.strip().startswith('"""')
    ]
    assert not any(line.startswith("assert ") for line in code_lines), "Phát hiện câu lệnh assert trong production code!"


def test_reschedule_o_bi_chiem_co_dinh_bao_loi_ngay_khong_goi_api():
    """Ô đích có video không nằm trong danh sách dời -> ValueError ngay, không gọi API."""
    current_rows = {
        "V1": {"id": "id_1", "when": "2026-11-10T13:00:00Z", "title": "Vid 1"},
        "V2": {"id": "id_2", "when": "2026-11-16T13:00:00Z", "title": "Vid 2"},
    }
    mock_update = MagicMock()
    with pytest.raises(ValueError, match="không nằm trong danh sách dời"):
        reschedule_channel(ch="fs", target_map={"V1": "11-16"}, current_rows=current_rows,
                           creds_path="dummy_cred", confirm=True, update_fn=mock_update)
    assert mock_update.call_count == 0
