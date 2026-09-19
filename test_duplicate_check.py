"""Regression test cho duplicate_check.py -- tái hiện ĐÚNG hình dạng vụ
đăng trùng thật phát hiện 2026-08-11 trên kênh BUD (xem duplicate_check.py
docstring cho toàn bộ điều tra):

  - EP005: 3 lần upload thật -- DmlFetbmhAw (2026-07-24), dxqNBmz2trw
    (2026-08-04), 2Tfwh3B-1SU (2026-08-06) -- 3 TIÊU ĐỀ KHÁC NHAU nhưng
    cùng nội dung/cùng thời lượng audio nguồn.
  - EP007: 2 lần upload thật -- TTsGD4f_bpM (2026-08-07), M_7WbvpNdHI
    (2026-08-10) -- cũng 2 tiêu đề khác nhau.

Test dùng file media THẬT (sinh bằng ffmpeg lavfi, ngắn để chạy nhanh)
thay vì giả lập duration bằng số nguyên tay -- probe_duration_seconds() gọi
ffprobe THẬT, không mock, đúng tinh thần "real code, real tests" của dự án
này (xem mix_bgm.py's test tương tự nếu có, và quy ước chung của bộ test
gốc: test chống lại hành vi ffprobe/ffmpeg THẬT thay vì 1 con số bịa)."""
import json
import shutil
import subprocess

import pytest

import duplicate_check as dc

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")
pytestmark = pytest.mark.skipif(not FFMPEG or not FFPROBE, reason="cần ffmpeg/ffprobe thật trong PATH")


def _make_media(path, duration_sec: float, kind: str) -> None:
    if kind == "audio":
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
               "-i", "anullsrc=r=8000:cl=mono", "-t", str(duration_sec), "-y", str(path)]
    else:
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
               "-i", f"color=c=black:s=64x64:d={duration_sec}", "-y", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# --- probe_duration_seconds() -- ffprobe THẬT ---------------------------


def test_probe_duration_seconds_reads_real_video_duration(tmp_path):
    video = tmp_path / "v.mp4"
    _make_media(video, 5.0, "video")
    duration = dc.probe_duration_seconds(video, FFPROBE)
    assert abs(duration - 5.0) < 0.2


def test_probe_duration_seconds_reads_real_audio_duration(tmp_path):
    audio = tmp_path / "a.wav"
    _make_media(audio, 12.3, "audio")
    duration = dc.probe_duration_seconds(audio, FFPROBE)
    assert abs(duration - 12.3) < 0.2


def test_probe_duration_seconds_missing_file_raises(tmp_path):
    with pytest.raises(dc.DuplicateCheckError, match="Không tìm thấy"):
        dc.probe_duration_seconds(tmp_path / "khong_ton_tai.mp4", FFPROBE)


def test_probe_duration_seconds_corrupt_file_raises_not_silently_zero(tmp_path):
    """BUG THẬT gặp lúc viết test: 1 file .mp4 rỗng/hỏng phải RAISE, không
    được âm thầm trả về 0.0 hay bất kỳ số nào -- nếu không, 1 file hỏng có
    thể trùng "duration=0" với video khác cũng lỗi, gây báo trùng sai."""
    bad = tmp_path / "hong.mp4"
    bad.write_bytes(b"khong phai video that")
    with pytest.raises(dc.DuplicateCheckError):
        dc.probe_duration_seconds(bad, FFPROBE)


# --- check_for_possible_duplicate() -- tái hiện EP005/EP007 -------------


def test_reproduces_real_ep005_incident_duration_catches_it_despite_different_titles(tmp_path, monkeypatch):
    """Tái hiện ĐÚNG hình dạng vụ EP005 thật: 1 bản render MỚI (lần thử
    upload thứ 3 CỦA SỐ LIỆU THẬT) có audio+video thời lượng khớp 2 video
    ĐÃ CÓ SẴN trên kênh (dù tiêu đề khác nhau) -- PHẢI bị chặn."""
    video = tmp_path / "with_bgm.mp4"
    audio = tmp_path / "source.wav"
    # Để test chạy nhanh (không sinh video dài thật ~25 phút như EP005
    # thật), tái hiện ĐÚNG HÌNH DẠNG của vụ thật ở 1 khung thời lượng ngắn
    # (7.2s) thay vì con số thật -- cơ chế so khớp chỉ quan tâm chênh lệch
    # tương đối, không quan tâm độ dài tuyệt đối.
    short_duration = 7.2
    _make_media(video, short_duration, "video")
    _make_media(audio, short_duration - 0.1, "audio")  # audio nguồn thường lệch nhẹ so với video final (fade biên) -- vẫn trong AUDIO_DURATION_TOLERANCE_SEC
    catalog = [
        dc.ChannelVideo("DmlFetbmhAw", "Nghiệp Duyên Là Gì? Góc Nhìn Phật Giáo", short_duration + 0.3, "2026-07-24T13:00:00Z"),
        dc.ChannelVideo("dxqNBmz2trw", "Vì Sao Ta Gặp Rồi Chia Ly", short_duration + 0.5, "2026-08-04T13:00:00Z"),
        dc.ChannelVideo("IktxS6H8UmU", "Địa Tạng Bồ Tát Là Ai?", short_duration + 200.0, "2026-07-27T13:00:00Z"),
    ]
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: catalog)

    result = dc.check_for_possible_duplicate(video, "fake_creds.json", FFPROBE, audio_path=audio)

    assert result is not None, "duration match phải bắt được khả năng trùng dù title khác hoàn toàn"
    assert result.suspected_video_id in ("DmlFetbmhAw", "dxqNBmz2trw")  # KHÔNG được khớp nhầm EP001 (lệch 200s)
    assert result.secondary_signal_available is True
    assert result.secondary_signal_matched is True  # audio nguồn cũng khớp -- 2 tín hiệu độc lập cùng đồng ý


def test_unrelated_video_with_coincidentally_similar_duration_is_not_falsely_flagged_when_outside_tolerance(tmp_path, monkeypatch):
    """Không phải MỌI chênh lệch nhỏ đều bỏ qua -- ngoài DURATION_TOLERANCE_SEC
    (2.0s) thì KHÔNG được coi là trùng, dù 'gần bằng'."""
    video = tmp_path / "v.mp4"
    _make_media(video, 10.0, "video")
    catalog = [dc.ChannelVideo("unrelated123", "Video Không Liên Quan", 13.5, "2026-01-01T00:00:00Z")]  # lệch 3.5s > 2.0s tolerance
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: catalog)

    result = dc.check_for_possible_duplicate(video, "fake_creds.json", FFPROBE)
    assert result is None


def test_duration_alone_still_flags_when_audio_source_unavailable(tmp_path, monkeypatch):
    """Tín hiệu phụ (audio) là CỦNG CỐ thêm, KHÔNG phải điều kiện bắt buộc
    -- nếu không có wav_path (vd tập rất cũ đã dọn cache), vẫn phải fail-
    closed theo tín hiệu duration đơn (đã đủ bắt được cả 3 vụ thật), chỉ
    đánh dấu secondary_signal_available=False để người xem biết mức tin cậy."""
    video = tmp_path / "v.mp4"
    _make_media(video, 6.0, "video")
    catalog = [dc.ChannelVideo("existing1", "Video Đã Có", 6.5, "2026-01-01T00:00:00Z")]
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: catalog)

    result = dc.check_for_possible_duplicate(video, "fake_creds.json", FFPROBE, audio_path=None)
    assert result is not None
    assert result.secondary_signal_available is False
    assert result.secondary_signal_matched is False


def test_available_but_mismatching_audio_signal_prevents_the_false_flag(tmp_path, monkeypatch):
    """Codex CLI adversarial review round 1, finding thật HIGH: bản vá
    trước đây TÍNH tín hiệu phụ (audio) nhưng KHÔNG BAO GIỜ dùng nó để
    quyết định -- luôn báo trùng ngay khi duration video khớp, kể cả khi
    audio nguồn rõ ràng KHÔNG khớp candidate đó. Đây chính là kịch bản
    "trùng NGẪU NHIÊN về duration" mà tín hiệu phụ được thiết kế để chặn
    (xem docstring module) -- PHẢI trả về None, không phải PossibleDuplicate."""
    video = tmp_path / "v.mp4"
    audio = tmp_path / "source.wav"
    _make_media(video, 10.0, "video")
    _make_media(audio, 40.0, "audio")  # audio nguồn của CHÍNH tập này lệch RẤT XA candidate -- rõ ràng không phải cùng nội dung
    catalog = [dc.ChannelVideo("coincidence_id", "Video Ngẫu Nhiên Trùng Độ Dài", 10.1, "2026-01-01T00:00:00Z")]
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: catalog)

    result = dc.check_for_possible_duplicate(video, "fake_creds.json", FFPROBE, audio_path=audio)
    assert result is None, "audio nguồn mâu thuẫn RÕ RÀNG với candidate duy nhất khớp duration -- không được flag"


def test_when_multiple_duration_candidates_exist_only_the_audio_corroborated_one_is_flagged(tmp_path, monkeypatch):
    """2 video khác nhau trên kênh vô tình cùng khớp duration video (cả
    hai trong tolerance) -- chỉ ứng viên MÀ audio nguồn CŨNG khớp mới được
    coi là khả năng trùng thật, KHÔNG PHẢI ứng viên gần nhất theo duration
    video đơn thuần (đúng finding Codex round 1: đừng chỉ kiểm audio với
    riêng ứng viên gần nhất theo video). Dùng audio_duration_tolerance_sec
    hẹp hơn mặc định để kết quả tất định, không phụ thuộc trùng hợp số."""
    video = tmp_path / "v.mp4"
    audio = tmp_path / "source.wav"
    _make_media(video, 10.0, "video")
    _make_media(audio, 8.75, "audio")
    # Codex CLI adversarial review round 2 phát hiện thật: bản trước của
    # test này có SỐ SAI -- "further_video_right_audio" (diff=1.3s) thực ra
    # GẦN local_video_duration HƠN "closer_video_wrong_audio" (diff=1.5s),
    # ngược hẳn với tên biến/mô tả, nên test đó KHÔNG thực sự phân biệt được
    # "chỉ kiểm audio với ứng viên gần nhất" (bug cũ) với "xét mọi ứng viên"
    # (bản đã sửa) -- cả 2 cách triển khai đều tình cờ ra cùng kết quả với
    # số liệu sai đó. Sửa lại đúng: closer_video_wrong_audio PHẢI THẬT SỰ
    # gần local_video_duration (10.0s) hơn, để 1 bản triển khai sai (chỉ
    # kiểm audio với ứng viên gần nhất) sẽ chọn NHẦM nó rồi thấy audio
    # KHÔNG khớp -> trả None sai, khác kết quả ĐÚNG (phải chọn
    # further_video_right_audio, vì nó CŨNG khớp duration trong tolerance
    # VÀ được audio xác nhận).
    catalog = [
        # Gần local_video_duration (10.0s) HƠN THẬT SỰ -- diff=0.3s, trong
        # tolerance video mặc định (2.0s) -- nhưng audio nguồn (8.75s) lệch
        # 1.55s so với candidate này, VƯỢT audio_duration_tolerance_sec=1.0
        # dùng ở test này -- KHÔNG được audio xác nhận.
        dc.ChannelVideo("closer_video_wrong_audio", "Gần hơn theo duration video nhưng audio KHÔNG khớp", 10.3, "2026-01-01T00:00:00Z"),
        # Xa local_video_duration hơn (diff=1.3s) nhưng VẪN trong tolerance
        # video -- và audio nguồn chỉ lệch 0.05s so với candidate này -- ĐƯỢC
        # audio xác nhận.
        dc.ChannelVideo("further_video_right_audio", "Xa hơn 1 chút theo duration video nhưng audio khớp SÁT", 8.7, "2026-01-02T00:00:00Z"),
    ]
    assert abs(10.3 - 10.0) < abs(8.7 - 10.0), "closer_video_wrong_audio phải THẬT SỰ gần local_video_duration hơn -- xem ghi chú trên"
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: catalog)

    result = dc.check_for_possible_duplicate(
        video, "fake_creds.json", FFPROBE, audio_path=audio, audio_duration_tolerance_sec=1.0,
    )
    assert result is not None
    assert result.suspected_video_id == "further_video_right_audio", (
        "phải chọn ứng viên audio nguồn XÁC NHẬN khớp, không phải ứng viên chỉ gần nhất theo duration video"
    )


def test_no_channel_videos_at_all_returns_none_not_a_crash(tmp_path, monkeypatch):
    video = tmp_path / "v.mp4"
    _make_media(video, 6.0, "video")
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: [])
    assert dc.check_for_possible_duplicate(video, "fake_creds.json", FFPROBE) is None


def test_exclude_video_id_skips_self_match(tmp_path, monkeypatch):
    """Nếu registry entry đã có video_id (vd resume 1 lần chạy dở, hiếm
    nhưng có thể xảy ra), KHÔNG được tự báo trùng với CHÍNH bản ghi của
    chính nó."""
    video = tmp_path / "v.mp4"
    _make_media(video, 8.0, "video")
    catalog = [dc.ChannelVideo("self_id", "Chính Tập Này", 8.1, "2026-01-01T00:00:00Z")]
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: catalog)

    result = dc.check_for_possible_duplicate(video, "fake_creds.json", FFPROBE, exclude_video_id="self_id")
    assert result is None


# --- fetch_channel_video_catalog() -- pagination/parsing thật -----------


def test_fetch_channel_video_catalog_parses_duration_and_paginates(monkeypatch):
    """Tái dùng ĐÚNG pagination đã chạy thật (list_playlist_video_ids tự
    phân trang qua nhiều page, get_videos_details tự chia batch 50 id) --
    giả lập ở tầng _get() giống hệt convention test_batch_orchestration.py's
    test_fetch_scheduled_counts_per_day_full_flow (không giả lập tầng cao
    hơn, để test THẬT tầng phân trang)."""
    calls = []

    def fake_get(creds, url, params):
        calls.append((url, dict(params)))
        if url == dc.CHANNELS_URL:
            return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU_FAKE"}}}]}
        if url == "https://www.googleapis.com/youtube/v3/playlistItems":
            if "pageToken" not in params:
                return {"items": [{"contentDetails": {"videoId": "v0"}}], "nextPageToken": "PAGE2"}
            return {"items": [{"contentDetails": {"videoId": "v1"}}]}
        if url == "https://www.googleapis.com/youtube/v3/videos":
            return {"items": [
                {"id": "v0", "snippet": {"title": "A", "publishedAt": "2026-01-01T00:00:00Z"}, "statistics": {}, "contentDetails": {"duration": "PT25M23S"}},
                {"id": "v1", "snippet": {"title": "B", "publishedAt": "2026-01-02T00:00:00Z"}, "statistics": {}, "contentDetails": {"duration": "PT1H2M3S"}},
            ]}
        raise AssertionError(f"URL không mong đợi: {url}")

    monkeypatch.setattr(dc, "_get", fake_get)
    import youtube_catalog as yc
    monkeypatch.setattr(yc, "_get", fake_get)

    catalog = dc.fetch_channel_video_catalog("fake_creds.json")

    by_id = {v.video_id: v for v in catalog}
    assert by_id["v0"].duration_seconds == 25 * 60 + 23
    assert by_id["v1"].duration_seconds == 3600 + 2 * 60 + 3
    # pageToken thật sự được dùng để lấy trang 2 (v1)
    playlist_calls = [p for u, p in calls if u == "https://www.googleapis.com/youtube/v3/playlistItems"]
    assert len(playlist_calls) == 2
    assert playlist_calls[1].get("pageToken") == "PAGE2"


def test_fetch_channel_video_catalog_empty_channel_returns_empty_list(monkeypatch):
    def fake_get(creds, url, params):
        if url == dc.CHANNELS_URL:
            return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU_EMPTY"}}}]}
        if url == "https://www.googleapis.com/youtube/v3/playlistItems":
            return {"items": []}
        raise AssertionError(f"URL không mong đợi: {url}")

    monkeypatch.setattr(dc, "_get", fake_get)
    import youtube_catalog as yc
    monkeypatch.setattr(yc, "_get", fake_get)
    assert dc.fetch_channel_video_catalog("fake_creds.json") == []
