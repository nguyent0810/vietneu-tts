"""Test cho record_existing_upload.py -- công cụ backfill registry entry
Long khi 1 video đã được upload THỦ CÔNG ngoài luồng long_batch_runner.py
(chiều CÒN LẠI của lỗ hổng gây ra vụ đăng trùng thật 2026-08-11, xem
duplicate_check.py + record_existing_upload.py docstring).

Trọng tâm test: các lớp bảo vệ chống LẠM DỤNG (Codex CLI review yêu cầu rà
đúng câu hỏi này) -- công cụ này ghi trực tiếp status="uploaded" vào
registry (bỏ qua toàn bộ luồng render/upload thật), nên PHẢI có rào chắn rõ
ràng, không thể dùng để "che" 1 tập chưa từng thực sự tồn tại trên YouTube."""
import shutil
import subprocess

import pytest

import long_batch_runner as lbr
import record_existing_upload as reu

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")
pytestmark = pytest.mark.skipif(not FFMPEG or not FFPROBE, reason="cần ffmpeg/ffprobe thật trong PATH")

FAKE_OWN_CHANNEL_ID = "UC_OWN_CHANNEL"


def _make_audio(path, duration_sec: float) -> None:
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
           "-i", "anullsrc=r=8000:cl=mono", "-t", str(duration_sec), "-y", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.fixture(autouse=True)
def _isolated_registry(tmp_path, monkeypatch):
    # Cùng convention test_thumbnail_generator.py / test_long_batch_runner_
    # duplicate_guard.py -- chỉ patch _output_dir, giữ nguyên
    # _REGISTRY_PRODUCTION_ROOT thật để write-guard tự cho phép (path test
    # nằm ngoài cây production thật).
    fake_root = tmp_path / "output" / "long"
    monkeypatch.setattr(lbr, "_output_dir", lambda t: fake_root / t)
    monkeypatch.setattr(reu, "get_own_channel_id", lambda credentials_path: FAKE_OWN_CHANNEL_ID)
    return fake_root


def _mock_video_lookup(monkeypatch, video_id, title, duration_seconds, channel_id=FAKE_OWN_CHANNEL_ID, published_at="2026-07-24T13:00:00Z"):
    total = int(duration_seconds)
    iso = f"PT{total // 60}M{total % 60}S"

    def fake_get(credentials_path, url, params):
        assert url == reu.VIDEOS_URL
        assert params["id"] == video_id
        return {"items": [{
            "id": video_id,
            "snippet": {"title": title, "channelId": channel_id, "publishedAt": published_at},
            "contentDetails": {"duration": iso},
        }]}
    monkeypatch.setattr(reu, "_get", fake_get)


def _seed_entry(topic, extra=None):
    entry = {"key": "EP_TEST", "episode_dir_name": "EP_TEST", "title": "Test Episode", "status": "possible_duplicate_detected"}
    if extra:
        entry.update(extra)
    lbr.save_registry({"EP_TEST": entry}, topic)
    return entry


def test_backfill_records_video_id_and_marks_uploaded(tmp_path, monkeypatch):
    """Đường THÀNH CÔNG thật: có wav_path cục bộ VÀ duration khớp -- xác
    minh được tự động, không cần --force."""
    topic = "Test Topic Long"
    wav_path = tmp_path / "source.wav"
    _make_audio(wav_path, 300.0)
    _seed_entry(topic, extra={"wav_path": str(wav_path)})
    _mock_video_lookup(monkeypatch, "REAL_EXISTING_ID", "Tiêu đề thật trên YouTube", 300.0)

    entry = reu.record_existing_upload(
        topic, "EP_TEST", "REAL_EXISTING_ID", str(tmp_path / "fake_creds.json"),
        reason="Xác nhận đúng là bản đã upload thủ công hồi tháng 7.",
        ffprobe_path=FFPROBE,
    )

    assert entry["video_id"] == "REAL_EXISTING_ID"
    assert entry["status"] == "uploaded"
    assert entry["backfilled_manual_upload"] is True
    assert entry["backfill_reason"].startswith("Xác nhận")
    assert entry["backfill_duration_check"]["performed"] is True
    assert entry["backfill_duration_check"]["matched"] is True
    assert "possible_duplicate" not in entry  # cờ nghi trùng cũ phải được xoá

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"]["video_id"] == "REAL_EXISTING_ID"
    assert on_disk["EP_TEST"]["status"] == "uploaded"


def test_refuses_when_duration_cannot_be_verified_at_all_without_force(tmp_path, monkeypatch):
    """Codex CLI adversarial review round 1, finding thật mục D: bản vá
    trước đây cho phép backfill THÀNH CÔNG NGAY khi KHÔNG thể đối chiếu
    duration (thiếu wav_path/ffprobe) -- không cần --force. Đây là lỗ hổng
    thật: "video tồn tại + đúng kênh + lý do bất kỳ" đủ để che 1 tập chưa
    từng thực sự upload. PHẢI đòi --force khi không xác minh được, không
    chỉ khi xác minh được nhưng lệch."""
    topic = "Test Topic Long"
    _seed_entry(topic)  # KHÔNG có wav_path -- không thể xác minh
    _mock_video_lookup(monkeypatch, "UNVERIFIABLE_ID", "Video không xác minh được", 300.0)

    with pytest.raises(reu.RecordExistingUploadError, match="KHÔNG THỂ tự đối chiếu"):
        reu.record_existing_upload(
            topic, "EP_TEST", "UNVERIFIABLE_ID", str(tmp_path / "fake_creds.json"), reason="test", ffprobe_path=FFPROBE,
        )

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"].get("video_id") is None  # KHÔNG được ghi khi chưa xác minh được


def test_force_bypasses_unverifiable_duration_but_records_performed_false(tmp_path, monkeypatch):
    topic = "Test Topic Long"
    _seed_entry(topic)  # vẫn không có wav_path
    _mock_video_lookup(monkeypatch, "UNVERIFIABLE_ID", "Video không xác minh được", 300.0)

    entry = reu.record_existing_upload(
        topic, "EP_TEST", "UNVERIFIABLE_ID", str(tmp_path / "fake_creds.json"),
        reason="Tự nghe lại video trên YouTube, xác nhận đúng nội dung tập này -- không còn wav gốc cục bộ.",
        ffprobe_path=FFPROBE, force=True,
    )
    assert entry["video_id"] == "UNVERIFIABLE_ID"
    assert entry["backfill_duration_check"]["performed"] is False


def test_missing_ffprobe_path_also_counts_as_unverifiable_and_needs_force(tmp_path, monkeypatch):
    """Có wav_path nhưng KHÔNG truyền --ffprobe -- vẫn là "không xác minh
    được", không phải "đã xác minh khớp"."""
    topic = "Test Topic Long"
    wav_path = tmp_path / "source.wav"
    _make_audio(wav_path, 300.0)
    _seed_entry(topic, extra={"wav_path": str(wav_path)})
    _mock_video_lookup(monkeypatch, "REAL_ID", "Video đúng tập này", 300.0)

    with pytest.raises(reu.RecordExistingUploadError, match="KHÔNG THỂ tự đối chiếu"):
        reu.record_existing_upload(topic, "EP_TEST", "REAL_ID", str(tmp_path / "fake_creds.json"), reason="test")  # KHÔNG truyền ffprobe_path


def test_refuses_when_channel_id_is_missing_from_youtube_response_without_force(tmp_path, monkeypatch):
    """Codex CLI adversarial review round 1, finding thật mục D: nếu
    videos.list KHÔNG trả về channelId, bản vá trước đây ÂM THẦM coi là
    'đã xác nhận đúng kênh' -- sai, "không biết" khác hẳn "đã xác nhận"."""
    topic = "Test Topic Long"
    wav_path = tmp_path / "source.wav"
    _make_audio(wav_path, 300.0)
    _seed_entry(topic, extra={"wav_path": str(wav_path)})
    _mock_video_lookup(monkeypatch, "NO_CHANNEL_ID", "Video thiếu channelId", 300.0, channel_id=None)

    with pytest.raises(reu.RecordExistingUploadError, match="KHÔNG trả về channelId"):
        reu.record_existing_upload(
            topic, "EP_TEST", "NO_CHANNEL_ID", str(tmp_path / "fake_creds.json"), reason="test", ffprobe_path=FFPROBE,
        )

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"].get("video_id") is None


def test_force_allows_missing_channel_id(tmp_path, monkeypatch):
    topic = "Test Topic Long"
    wav_path = tmp_path / "source.wav"
    _make_audio(wav_path, 300.0)
    _seed_entry(topic, extra={"wav_path": str(wav_path)})
    _mock_video_lookup(monkeypatch, "NO_CHANNEL_ID", "Video thiếu channelId", 300.0, channel_id=None)

    entry = reu.record_existing_upload(
        topic, "EP_TEST", "NO_CHANNEL_ID", str(tmp_path / "fake_creds.json"),
        reason="Tự mở link video, xác nhận đúng là kênh của mình dù API không trả channelId.",
        ffprobe_path=FFPROBE, force=True,
    )
    assert entry["video_id"] == "NO_CHANNEL_ID"


def test_refuses_when_video_id_belongs_to_a_different_channel(tmp_path, monkeypatch):
    """Chặn nhầm --credentials/nhầm video_id sang kênh khác -- không được
    âm thầm backfill vào registry của kênh A bằng 1 video thật ra thuộc
    kênh B."""
    topic = "Test Topic Long"
    _seed_entry(topic)
    _mock_video_lookup(monkeypatch, "OTHER_CHANNEL_VIDEO", "Video kênh khác", 300.0, channel_id="UC_SOME_OTHER_CHANNEL")

    with pytest.raises(reu.RecordExistingUploadError, match="KHÔNG PHẢI kênh"):
        reu.record_existing_upload(topic, "EP_TEST", "OTHER_CHANNEL_VIDEO", str(tmp_path / "fake_creds.json"), reason="test")

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"]["status"] == "possible_duplicate_detected"  # KHÔNG bị ghi đè


def test_refuses_to_silently_overwrite_a_different_existing_video_id_without_force(tmp_path, monkeypatch):
    """entry đã có status=uploaded với video_id KHÁC -- không được âm thầm
    thay thế (có thể chính video_id cũ đó là bằng chứng của 1 vụ trùng cần
    biết, không phải thứ để xoá dấu vết)."""
    topic = "Test Topic Long"
    _seed_entry(topic, extra={"status": "uploaded", "video_id": "OLD_VIDEO_ID"})
    _mock_video_lookup(monkeypatch, "NEW_VIDEO_ID", "Video mới", 300.0)

    with pytest.raises(reu.RecordExistingUploadError, match="ĐÃ có status='uploaded'"):
        reu.record_existing_upload(topic, "EP_TEST", "NEW_VIDEO_ID", str(tmp_path / "fake_creds.json"), reason="test")

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"]["video_id"] == "OLD_VIDEO_ID"  # không đổi


def test_force_allows_overwriting_existing_video_id_and_records_the_replaced_one(tmp_path, monkeypatch):
    topic = "Test Topic Long"
    _seed_entry(topic, extra={"status": "uploaded", "video_id": "OLD_VIDEO_ID"})
    _mock_video_lookup(monkeypatch, "NEW_VIDEO_ID", "Video mới", 300.0)

    entry = reu.record_existing_upload(
        topic, "EP_TEST", "NEW_VIDEO_ID", str(tmp_path / "fake_creds.json"), reason="Xác nhận OLD_VIDEO_ID là bản lỗi, đây mới là đúng.", force=True,
    )

    assert entry["video_id"] == "NEW_VIDEO_ID"
    assert entry["backfill_replaced_video_id"] == "OLD_VIDEO_ID"


def test_refuses_when_local_audio_duration_does_not_match_real_video_duration(tmp_path, monkeypatch):
    """Lớp bảo vệ CHÍNH chống lạm dụng: nếu registry entry còn wav_path
    cục bộ và nó KHÔNG khớp duration thật của video_id đang backfill, từ
    chối -- video_id có thể không phải bản của đúng tập này."""
    topic = "Test Topic Long"
    wav_path = tmp_path / "source.wav"
    _make_audio(wav_path, 5.0)
    _seed_entry(topic, extra={"wav_path": str(wav_path)})
    _mock_video_lookup(monkeypatch, "MISMATCHED_ID", "Video không liên quan", 300.0)  # 300s thật >> 5s audio nguồn

    with pytest.raises(reu.RecordExistingUploadError, match="LỆCH"):
        reu.record_existing_upload(
            topic, "EP_TEST", "MISMATCHED_ID", str(tmp_path / "fake_creds.json"), reason="test", ffprobe_path=FFPROBE,
        )

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"].get("video_id") is None  # KHÔNG được ghi khi chưa xác nhận


def test_force_bypasses_duration_mismatch_but_still_records_the_check_result(tmp_path, monkeypatch):
    topic = "Test Topic Long"
    wav_path = tmp_path / "source.wav"
    _make_audio(wav_path, 5.0)
    _seed_entry(topic, extra={"wav_path": str(wav_path)})
    _mock_video_lookup(monkeypatch, "MISMATCHED_ID", "Video không liên quan", 300.0)

    entry = reu.record_existing_upload(
        topic, "EP_TEST", "MISMATCHED_ID", str(tmp_path / "fake_creds.json"),
        reason="Audio nguồn đã bị thay bằng bản edit khác sau khi video này lên sóng -- xác nhận thủ công đúng tập.",
        ffprobe_path=FFPROBE, force=True,
    )

    assert entry["video_id"] == "MISMATCHED_ID"
    assert entry["backfill_duration_check"]["performed"] is True
    assert entry["backfill_duration_check"]["matched"] is False


def test_matching_audio_duration_passes_without_needing_force(tmp_path, monkeypatch):
    topic = "Test Topic Long"
    wav_path = tmp_path / "source.wav"
    _make_audio(wav_path, 300.0)  # khớp đúng duration video giả lập bên dưới
    _seed_entry(topic, extra={"wav_path": str(wav_path)})
    _mock_video_lookup(monkeypatch, "REAL_ID", "Video đúng tập này", 300.0)

    entry = reu.record_existing_upload(
        topic, "EP_TEST", "REAL_ID", str(tmp_path / "fake_creds.json"), reason="test", ffprobe_path=FFPROBE,
    )
    assert entry["video_id"] == "REAL_ID"
    assert entry["backfill_duration_check"]["performed"] is True
    assert entry["backfill_duration_check"]["matched"] is True


def test_video_id_not_found_on_youtube_refuses_blind_backfill(tmp_path, monkeypatch):
    topic = "Test Topic Long"
    _seed_entry(topic)

    def fake_get_empty(credentials_path, url, params):
        return {"items": []}
    monkeypatch.setattr(reu, "_get", fake_get_empty)

    with pytest.raises(reu.RecordExistingUploadError, match="không trả về video nào"):
        reu.record_existing_upload(topic, "EP_TEST", "GHOST_ID", str(tmp_path / "fake_creds.json"), reason="test")


# --- CLI wiring (main()) -------------------------------------------------


def test_cli_main_success_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(reu, "mark_production_entry", lambda: None)
    monkeypatch.setattr(reu, "record_existing_upload", lambda *a, **kw: {
        "video_id": "X", "backfilled_video_title": "T", "backfill_duration_check": {"performed": False},
    })
    monkeypatch.setattr("sys.argv", [
        "record_existing_upload.py", "--topic", "T", "--episode-id", "EP1",
        "--video-id", "X", "--credentials", "c.json", "--reason", "r",
    ])
    assert reu.main() == 0


def test_cli_main_error_exit_code_and_message(monkeypatch, capsys):
    monkeypatch.setattr(reu, "mark_production_entry", lambda: None)

    def _boom(*a, **kw):
        raise reu.RecordExistingUploadError("lý do lỗi cụ thể")
    monkeypatch.setattr(reu, "record_existing_upload", _boom)
    monkeypatch.setattr("sys.argv", [
        "record_existing_upload.py", "--topic", "T", "--episode-id", "EP1",
        "--video-id", "X", "--credentials", "c.json", "--reason", "r",
    ])
    assert reu.main() == 1
    assert "lý do lỗi cụ thể" in capsys.readouterr().err
