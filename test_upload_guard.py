"""Sổ upload BUD/FS: giữ chỗ trước byte đầu, hỏi lại phiên khi đứt, trần 24 upload/24 giờ, CL không đổi."""
from datetime import datetime, timedelta, timezone

import pytest

import youtube_upload as U


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(U, "UPLOAD_LOG", tmp_path / "log.json")
    monkeypatch.setattr(U, "_refresh_or_raise", lambda c: "tok")
    vid = tmp_path / "a.mp4"
    vid.write_bytes(b"x" * 100)
    calls = {"init": 0}

    def init(*a, **k):
        calls["init"] += 1
        return "https://upload/session1"
    monkeypatch.setattr(U, "_init_resumable_session", init)
    return vid, calls, monkeypatch


def test_interrupted_upload_resumes_instead_of_new_video(env):
    vid, calls, mp = env
    mp.setattr(U, "_upload_chunks", lambda *a, **k: (_ for _ in ()).throw(U.YouTubeUploadError("mất mạng")))
    with pytest.raises(U.YouTubeUploadError):
        U.upload_video(vid, U.VideoMetadata(title="t"), ".youtube_channels/phat_giao.json")
    assert U._log_load()[next(iter(U._log_load()))]["session"] == "https://upload/session1"   # giữ trước byte đầu
    mp.setattr(U, "_query_session", lambda url, n: ("done", {"id": "VID1"}))                 # thật ra đã tạo xong
    assert U.upload_video(vid, U.VideoMetadata(title="t"), ".youtube_channels/phat_giao.json")["id"] == "VID1"
    assert calls["init"] == 1                                                                 # không mở phiên thứ hai
    with pytest.raises(U.YouTubeUploadError, match="đã upload"):
        U.upload_video(vid, U.VideoMetadata(title="t"), ".youtube_channels/phat_giao.json")


def test_dead_session_needs_human(env):
    vid, calls, mp = env
    mp.setattr(U, "_upload_chunks", lambda *a, **k: (_ for _ in ()).throw(U.YouTubeUploadError("x")))
    with pytest.raises(U.YouTubeUploadError):
        U.upload_video(vid, U.VideoMetadata(title="t"), ".youtube_channels/phong_thuy.json")
    mp.setattr(U, "_query_session", lambda url, n: ("dead", 404))
    with pytest.raises(U.UploadInDoubt):
        U.upload_video(vid, U.VideoMetadata(title="t"), ".youtube_channels/phong_thuy.json")
    assert U.forget(vid) == 1


def test_pacing_cap_24_per_24h_by_upload_time():
    now = datetime(2026, 10, 5, 12, tzinfo=timezone.utc)
    log = {f"phat_giao.json|/v{i}|1": {"key": "phat_giao.json", "ts": (now - timedelta(hours=1, minutes=i)).isoformat()}
           for i in range(24)}
    until = U.pacing_hold_until("phat_giao.json", log, now)
    assert until and until > now
    log.popitem()
    assert U.pacing_hold_until("phat_giao.json", log, now) is None


def test_other_channels_untouched(env):
    vid, calls, mp = env
    mp.setattr(U, "_upload_chunks", lambda *a, **k: {"id": "CL1"})
    assert U.upload_video(vid, U.VideoMetadata(title="t"), ".youtube_channels/hinh_su.json")["id"] == "CL1"
    assert not U.UPLOAD_LOG.exists()
