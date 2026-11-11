import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from tools.long_packaging.apply_meta import (
    apply_metadata,
    prepare_metadata_update,
)


def test_prepare_metadata_update():
    snippet = {
        "description": "Câu mở đầu cũ.\n\n00:00 Mở đầu\n02:15 Chương 1\n\nMiễn trừ trách nhiệm...",
        "tags": ["tag_cu1", "tag_cu2"],
    }
    title = "Tiêu Đề Mới Hút View: Câu Hỏi Là Gì?"
    desc_head = "Đây là 2 câu mô tả mới chuẩn SEO. Giải thích rõ ràng nội dung."
    new_tags = ["tag_moi1", "tag_moi2", "tag_cu1"]

    new_t, new_d, final_tags = prepare_metadata_update(snippet, title, desc_head, new_tags)

    assert new_t == title
    assert new_d.startswith(desc_head)
    assert "00:00 Mở đầu" in new_d
    assert "Miễn trừ trách nhiệm..." in new_d
    assert final_tags[:2] == ["tag_moi1", "tag_moi2"]
    assert "tag_cu1" in final_tags


def test_prepare_metadata_validation_errors():
    snippet = {"description": "desc", "tags": []}

    # Tiêu đề quá 100 ký tự
    long_title = "A" * 101
    with pytest.raises(ValueError, match="vượt quá 100 ký tự"):
        prepare_metadata_update(snippet, long_title, "desc_head", [])

    # Tiêu đề chứa ký tự < hoặc >
    with pytest.raises(ValueError, match="không hợp lệ"):
        prepare_metadata_update(snippet, "Title with <invalid> tag", "desc_head", [])


def test_apply_metadata_dry_run_and_confirm(tmp_path: Path):
    mock_fetch = MagicMock(return_value={
        "snippet": {
            "title": "Tiêu đề cũ",
            "description": "Mô tả cũ.\n\n00:00 Giới thiệu",
            "tags": ["old_tag"],
        }
    })
    mock_update = MagicMock()
    mock_refresh = MagicMock(return_value="mock_creds")

    items = [{
        "key": "L_fs_18",
        "video_id": "test_vid_123",
        "title": "Màu Sắc Hợp Mệnh: Chọn Màu Sơn Nhà",
        "desc_head": "Hướng dẫn chọn màu sắc chuẩn phong thủy.",
        "tags": ["mau phong thuy", "mau son"],
    }]

    # 1. Chạy khô (dry-run): không được gọi update_fn
    res_dry = apply_metadata(
        items,
        confirm=False,
        fetch_fn=mock_fetch,
        update_fn=mock_update,
        refresh_fn=mock_refresh,
    )
    assert res_dry["confirm"] is False
    assert mock_update.call_count == 0

    # 2. Chạy confirm: phải gọi update_fn và ghi backup
    backup_path = tmp_path / "backup.json"
    res_confirm = apply_metadata(
        items,
        confirm=True,
        backup_file=backup_path,
        fetch_fn=mock_fetch,
        update_fn=mock_update,
        refresh_fn=mock_refresh,
    )
    assert res_confirm["confirm"] is True
    assert mock_update.call_count == 1
    args, kwargs = mock_update.call_args
    assert args[0] == "test_vid_123"
    assert kwargs["title"] == "Màu Sắc Hợp Mệnh: Chọn Màu Sơn Nhà"
    assert "00:00 Giới thiệu" in kwargs["description"]
    assert "publish_at" not in kwargs  # Không sửa lịch hẹn

    # File backup tồn tại và chứa tiêu đề cũ
    assert backup_path.exists()
    backup_data = json.load(backup_path.open())
    assert len(backup_data) == 1
    assert backup_data[0]["title"] == "Tiêu đề cũ"


def test_prepare_metadata_update_with_none_tags():
    """Kiểm tra Point 6: Không văng TypeError khi tags trong snippet hoặc new_tags là None."""
    snippet = {
        "description": "Mô tả cũ.\n\n00:00 Mở đầu",
        "tags": None,  # YouTube API trả về None khi video không có tags
    }
    title = "Tiêu Đề Không Lỗi Khi Tags None"
    desc_head = "Mô tả mở đầu mới."

    # Không được raise TypeError
    new_t, new_d, final_tags = prepare_metadata_update(snippet, title, desc_head, ["tag1", "tag2"])
    assert final_tags == ["tag1", "tag2"]

    # Thử trường hợp new_tags cũng là None/rỗng
    _, _, final_tags_empty = prepare_metadata_update(snippet, title, desc_head, None)
    assert final_tags_empty == []


def test_apply_metadata_main_with_dict_current_schedule(tmp_path: Path):
    """Kiểm tra Point 8: main() hỗ trợ file current.json dạng dict theo kênh mà không văng AttributeError."""
    from unittest.mock import patch
    from tools.long_packaging.apply_meta import main

    titles_file = tmp_path / "titles.json"
    titles_file.write_text(json.dumps({"L_fs_18": "Tiêu Đề Mới Cho FS18"}), encoding="utf-8")

    draft_file = tmp_path / "draft.json"
    draft_file.write_text(
        json.dumps([{"key": "L_fs_18", "desc_head": "Mô tả mở đầu mới.", "tags": ["tag1"]}]),
        encoding="utf-8",
    )

    current_file = tmp_path / "current.json"
    # Dạng dict theo kênh như chuẩn của reschedule.py
    current_file.write_text(
        json.dumps({
            "fs": [{"key": "L_fs_18", "id": "vid_fs18", "when": "2026-11-19T13:00:00Z"}],
            "bud": [{"key": "L_bud_25", "id": "vid_bud25", "when": "2026-11-14T13:00:00Z"}],
        }),
        encoding="utf-8",
    )

    with patch("youtube_upload._refresh_or_raise", return_value="dummy_token"), \
         patch("youtube_upload._fetch_video_snippet_status", return_value={"title": "Old", "description": "Old desc", "tags": []}):
        exit_code = main([
            "--titles", str(titles_file),
            "--draft", str(draft_file),
            "--current", str(current_file),
        ])
    assert exit_code == 0


def test_prepare_metadata_update_description_none():
    """YouTube trả description None -> không văng AttributeError."""
    snippet = {"description": None, "tags": None}
    new_t, new_d, _ = prepare_metadata_update(snippet, "Tiêu Đề", "Mở đầu mới.", ["a"])
    assert new_d.startswith("Mở đầu mới.")
