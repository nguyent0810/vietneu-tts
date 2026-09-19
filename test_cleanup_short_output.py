"""Test cleanup_short_output.py -- khoá nguyên tắc AN TOÀN bắt buộc (xem
docstring module): chỉ xoá đúng segment có status=="uploaded" VÀ video_id
thật, không đụng segment khác cùng thư mục, không đụng registry.json,
không xoá gì dựa trên tuổi file."""
import json
from pathlib import Path

import cleanup_short_output as cleanup


def _touch(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_segment_files(seg_dir: Path, n: int, with_cache: bool = True, with_subtitles: bool = True) -> None:
    prefix = f"{n:02d}_short"
    _touch(seg_dir / f"{prefix}.wav", "wav" * 100)
    _touch(seg_dir / f"{prefix}.json", "{}")
    _touch(seg_dir / f"{prefix}.srt", "1\n00:00:00,000 --> 00:00:01,000\nx\n")
    _touch(seg_dir / f"{prefix}.important_words.json", "[]")
    _touch(seg_dir / f"{prefix}_render.mp4", "mp4" * 1000)
    if with_subtitles:
        _touch(seg_dir / "subtitles" / f"{prefix}_render.ass", "ass")
        _touch(seg_dir / "subtitles" / f"{prefix}_render.srt", "srt")
    if with_cache:
        _touch(seg_dir / "cache" / f"seg{n}" / "chunk_0000.wav", "chunk")


def _write_registry(topic_dir: Path, entries: dict) -> None:
    (topic_dir).mkdir(parents=True, exist_ok=True)
    (topic_dir / "registry.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def _patch_root(monkeypatch, tmp_path: Path) -> Path:
    monkeypatch.setattr(cleanup, "PROJECT_ROOT", tmp_path)
    return tmp_path


def test_segment_artifact_paths_finds_all_files_for_one_segment(tmp_path):
    seg_dir = tmp_path / "EP01"
    _make_segment_files(seg_dir, 1)
    paths = cleanup.segment_artifact_paths(seg_dir, 1)
    names = {p.name for p in paths if p.is_file()}
    assert "01_short.wav" in names
    assert "01_short_render.mp4" in names
    assert "01_short.important_words.json" in names
    assert any(p.name == "seg1" for p in paths if p.is_dir())


def test_segment_artifact_paths_does_not_touch_other_segment_in_same_dir(tmp_path):
    seg_dir = tmp_path / "EP01"
    _make_segment_files(seg_dir, 1)
    _make_segment_files(seg_dir, 2)
    paths = cleanup.segment_artifact_paths(seg_dir, 1)
    names = {p.name for p in paths if p.is_file()}
    assert all("02_" not in n for n in names)
    cache_names = {p.name for p in paths if p.is_dir()}
    assert cache_names == {"seg1"}


def test_uploaded_segment_with_video_id_gets_cleaned(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    topic_dir = tmp_path / "output" / "shorts" / "Phong Thủy"
    _write_registry(topic_dir, {
        "EP01_01": {"episode": "EP01", "segment_index": 1, "status": "uploaded", "video_id": "abc123"},
    })
    _make_segment_files(topic_dir / "EP01", 1)

    cleaned, skipped, freed = cleanup.cleanup_topic("Phong Thủy", dry_run=True)
    assert cleaned == 1 and skipped == 0 and freed > 0
    # dry-run: KHÔNG được xoá gì thật
    assert (topic_dir / "EP01" / "01_short.wav").exists()

    cleaned, skipped, freed = cleanup.cleanup_topic("Phong Thủy", dry_run=False)
    assert cleaned == 1
    assert not (topic_dir / "EP01" / "01_short.wav").exists()
    assert not (topic_dir / "EP01" / "01_short_render.mp4").exists()
    # Thư mục episode rỗng hẳn -> phải bị xoá theo
    assert not (topic_dir / "EP01").exists()
    # registry.json KHÔNG BAO GIỜ bị đụng tới
    assert (topic_dir / "registry.json").exists()


def test_non_uploaded_segment_is_never_touched(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    topic_dir = tmp_path / "output" / "shorts" / "Phong Thủy"
    for status in ("scripted", "seo_ready", "audio_ready", "needs_review", "failed", "dry_run_done"):
        _write_registry(topic_dir, {"EP01_01": {"episode": "EP01", "segment_index": 1, "status": status, "video_id": "abc123"}})
        _make_segment_files(topic_dir / "EP01", 1)
        cleaned, skipped, freed = cleanup.cleanup_topic("Phong Thủy", dry_run=False)
        assert cleaned == 0, f"status={status} không phải 'uploaded', KHÔNG được dọn"
        assert (topic_dir / "EP01" / "01_short.wav").exists()


def test_uploaded_without_video_id_is_skipped(monkeypatch, tmp_path):
    # Điều kiện KÉP: status=="uploaded" MÀ video_id rỗng/thiếu -- fail-closed,
    # không tin riêng 1 field (phòng status bị sửa tay/hỏng).
    _patch_root(monkeypatch, tmp_path)
    topic_dir = tmp_path / "output" / "shorts" / "Phong Thủy"
    _write_registry(topic_dir, {
        "EP01_01": {"episode": "EP01", "segment_index": 1, "status": "uploaded", "video_id": None},
        "EP02_01": {"episode": "EP02", "segment_index": 1, "status": "uploaded"},  # thiếu hẳn field
    })
    _make_segment_files(topic_dir / "EP01", 1)
    _make_segment_files(topic_dir / "EP02", 1)

    cleaned, skipped, freed = cleanup.cleanup_topic("Phong Thủy", dry_run=False)
    assert cleaned == 0 and skipped == 2
    assert (topic_dir / "EP01" / "01_short.wav").exists()
    assert (topic_dir / "EP02" / "01_short.wav").exists()


def test_multi_segment_folder_only_cleans_uploaded_segment_keeps_pending_one(monkeypatch, tmp_path):
    """Đúng kịch bản thật (vd BUD "08_Buông Bỏ..."): 1 thư mục nhiều segment,
    chỉ 1 segment đã uploaded -- segment kia (đang scripted/pending) và cả
    thư mục cha PHẢI còn nguyên sau khi dọn."""
    _patch_root(monkeypatch, tmp_path)
    topic_dir = tmp_path / "output" / "shorts" / "Phật giáo"
    _write_registry(topic_dir, {
        "BUNDLE_01": {"episode": "BUNDLE", "segment_index": 1, "status": "uploaded", "video_id": "vid1"},
        "BUNDLE_02": {"episode": "BUNDLE", "segment_index": 2, "status": "scripted"},
    })
    _make_segment_files(topic_dir / "BUNDLE", 1)
    _make_segment_files(topic_dir / "BUNDLE", 2)

    cleaned, skipped, freed = cleanup.cleanup_topic("Phật giáo", dry_run=False)
    assert cleaned == 1 and skipped == 1
    seg_dir = topic_dir / "BUNDLE"
    assert not (seg_dir / "01_short.wav").exists()
    assert not (seg_dir / "01_short_render.mp4").exists()
    # Segment 2 (chưa uploaded) phải còn NGUYÊN VẸN
    assert (seg_dir / "02_short.wav").exists()
    assert (seg_dir / "02_short_render.mp4").exists()
    assert (seg_dir / "cache" / "seg2" / "chunk_0000.wav").exists()
    # Thư mục episode CHƯA rỗng (còn segment 2) -> KHÔNG được xoá thư mục cha
    assert seg_dir.exists()


def test_already_cleaned_segment_is_idempotent_second_run(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    topic_dir = tmp_path / "output" / "shorts" / "Phong Thủy"
    _write_registry(topic_dir, {
        "EP01_01": {"episode": "EP01", "segment_index": 1, "status": "uploaded", "video_id": "abc123"},
    })
    _make_segment_files(topic_dir / "EP01", 1)

    cleaned1, _, freed1 = cleanup.cleanup_topic("Phong Thủy", dry_run=False)
    assert cleaned1 == 1 and freed1 > 0
    # Chạy lại lần 2 (đã dọn từ trước) -- không lỗi, không đếm lại
    cleaned2, skipped2, freed2 = cleanup.cleanup_topic("Phong Thủy", dry_run=False)
    assert cleaned2 == 0 and freed2 == 0


def test_missing_registry_is_skipped_without_crashing(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    cleaned, skipped, freed = cleanup.cleanup_topic("Hình Sự", dry_run=True)
    assert (cleaned, skipped, freed) == (0, 0, 0)


def test_corrupt_registry_json_fails_closed_without_crashing(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    topic_dir = tmp_path / "output" / "shorts" / "Phong Thủy"
    topic_dir.mkdir(parents=True)
    (topic_dir / "registry.json").write_text("{not valid json", encoding="utf-8")
    cleaned, skipped, freed = cleanup.cleanup_topic("Phong Thủy", dry_run=True)
    assert (cleaned, skipped, freed) == (0, 0, 0)
