"""Test tự động cho bgm_tracks.py (audit 9 điểm mục #4 -- thêm nhiều track/
kênh + xoay vòng). Kiểm: file thật tồn tại, rotation dùng đúng
pick_and_commit_next() (atomic, không lặp liên tiếp), bgm_for_topic()
(legacy) không đổi state."""
from pathlib import Path

import bgm_tracks
import rotation_state


def test_all_configured_tracks_exist_as_real_files():
    for topic, tracks in bgm_tracks.BGM_BY_TOPIC.items():
        assert len(tracks) >= 1, f"topic={topic} không có track nào"
        for t in tracks:
            path = Path(t["path"])
            assert path.exists(), f"topic={topic}: file BGM không tồn tại: {path}"
            assert path.stat().st_size > 100_000, f"topic={topic}: file BGM quá nhỏ, khả năng tải lỗi: {path}"
            assert t["attribution"], f"topic={topic}: thiếu attribution cho {path.name}"


def test_bgm_for_topic_legacy_does_not_rotate(tmp_path, monkeypatch):
    """bgm_for_topic() (legacy) PHẢI trả về CÙNG 1 track (track đầu tiên)
    mỗi lần gọi, không đổi state -- vẫn được short_batch_runner.py dùng
    làm fallback cho registry entry cũ (xem docstring bgm_tracks.py)."""
    state_path = tmp_path / "unused_state.json"
    monkeypatch.setattr(bgm_tracks, "BGM_ROTATION_STATE_PATH", state_path)
    first = bgm_tracks.bgm_for_topic("Phật giáo")
    for _ in range(5):
        again = bgm_tracks.bgm_for_topic("Phật giáo")
        assert again["path"] == first["path"]
    assert not state_path.exists(), "bgm_for_topic() (legacy) không được ghi state"


def test_pick_bgm_for_topic_rotates_through_all_tracks(tmp_path, monkeypatch):
    state_path = tmp_path / "bgm_rotation_state.json"
    monkeypatch.setattr(bgm_tracks, "BGM_ROTATION_STATE_PATH", state_path)

    n_tracks = len(bgm_tracks.BGM_BY_TOPIC["Phật giáo"])
    picks = [bgm_tracks.pick_bgm_for_topic("Phật giáo")["path"].name for _ in range(n_tracks * 2)]
    expected_cycle = [Path(t["path"]).name for t in bgm_tracks.BGM_BY_TOPIC["Phật giáo"]]
    assert picks == expected_cycle + expected_cycle, f"không xoay vòng đúng chu kỳ: {picks}"


def test_pick_bgm_for_topic_unconfigured_returns_none(tmp_path, monkeypatch):
    state_path = tmp_path / "bgm_rotation_state.json"
    monkeypatch.setattr(bgm_tracks, "BGM_ROTATION_STATE_PATH", state_path)
    assert bgm_tracks.pick_bgm_for_topic("Chủ đề chưa cấu hình") is None


def test_pick_bgm_topics_independent(tmp_path, monkeypatch):
    """BUD và FS rotate độc lập -- chọn của kênh này không ảnh hưởng kênh
    kia dù dùng CHUNG 1 state file (cùng thiết kế đã áp cho symbol variant,
    xem test_symbol_assets.py::test_bat_quai_and_ngu_hanh_rotation_independent)."""
    state_path = tmp_path / "bgm_rotation_state.json"
    monkeypatch.setattr(bgm_tracks, "BGM_ROTATION_STATE_PATH", state_path)

    bud_picks = [bgm_tracks.pick_bgm_for_topic("Phật giáo")["path"].name for _ in range(3)]
    fs_picks = [bgm_tracks.pick_bgm_for_topic("Phong Thủy")["path"].name for _ in range(3)]

    assert bud_picks == ["meditation_impromptu_01.mp3", "meditation_impromptu_02.mp3", "meditation_impromptu_03.mp3"]
    assert fs_picks == ["asian_drums.mp3", "comfortable_mystery_4.mp3", "asian_drums.mp3"]


def test_legacy_single_track_topics_excludes_cl():
    """Codex review điểm #4 (bug thật): CL ("Hình Sự") có 0 track TRƯỚC
    migration này -- entry Short CL cũ thiếu entry["bgm"] KHÔNG được coi
    là "có BGM track đầu tiên" (short_batch_runner.py bước 5 chỉ fallback
    về bgm_for_topic() cho topic trong tập này). BUD/FS PHẢI có mặt (đã có
    sẵn đúng 1 track trước migration, fallback an toàn); "Hình Sự" PHẢI
    vắng mặt."""
    assert bgm_tracks.LEGACY_SINGLE_TRACK_TOPICS == {"Phật giáo", "Phong Thủy"}
    assert "Hình Sự" not in bgm_tracks.LEGACY_SINGLE_TRACK_TOPICS


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
