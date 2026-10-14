"""Integration test cho bug THẬT phát hiện 2026-08-11 (đăng trùng trên
kênh BUD, xem duplicate_check.py docstring): xác nhận long_batch_runner.py
THẬT SỰ gọi duplicate_check.check_for_possible_duplicate() ngay trước
upload_video() và FAIL CLOSED (không upload) khi tìm thấy khả năng trùng --
không chỉ cảnh báo suông.

Dùng process_one_episode() trực tiếp với entry đã seed sẵn ở status
"seo_ready" (cùng convention test_thumbnail_generator.py's
test_thumbnail_failure_does_not_prevent_video_id_from_being_saved) -- các
bước audio/bible/asset/render/BGM/finalize/SEO trước đó không liên quan tới
fix này, bỏ qua bằng cách seed entry đã ở đúng status."""
import fcntl
import json
import shutil
import subprocess
import threading

import pytest

import duplicate_check as dc
import long_batch_runner as lbr

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


@pytest.fixture(autouse=True)
def _isolated_registry(tmp_path, monkeypatch):
    # Chỉ patch _output_dir (đúng convention test_thumbnail_generator.py) --
    # KHÔNG patch _REGISTRY_PRODUCTION_ROOT: giữ nguyên cây production THẬT
    # để _is_production_write_allowed() thấy path test (nằm dưới tmp_path,
    # ngoài cây production thật) là an toàn để ghi mà không cần
    # mark_production_entry() (xem registry_lock.py mục 4 / G1).
    fake_root = tmp_path / "output" / "long"
    monkeypatch.setattr(lbr, "_output_dir", lambda t: fake_root / t)
    monkeypatch.setattr(lbr, "VENDORED_FFPROBE", FFPROBE)
    return fake_root


def _seed_episode(tmp_path, topic, duration_sec):
    ep_dir = tmp_path / "ep"
    ep_dir.mkdir(parents=True, exist_ok=True)
    video_path = ep_dir / "with_bgm.mp4"
    wav_path = ep_dir / "source.wav"
    _make_media(video_path, duration_sec, "video")
    _make_media(wav_path, max(duration_sec - 0.1, 0.1), "audio")

    shot_list_path = ep_dir / "shot_list_final.json"
    shot_list_path.write_text(json.dumps({"beats": []}), encoding="utf-8")  # không có beat ảnh -- thumbnail tự bỏ qua, giữ test gọn

    entry = {
        "key": "EP_TEST", "episode_dir_name": "EP_TEST", "title": "Test Episode",
        "status": "seo_ready",
        "shot_list_path": str(shot_list_path),
        "video_bgm_path": str(video_path),
        "wav_path": str(wav_path),
        "seo": {"title": "Tiêu Đề Test", "description": "Mô tả test", "tags": ["test"]},
    }
    registry = {"EP_TEST": entry}
    lbr.save_registry(registry, topic)
    return video_path, wav_path


def _ep_arg():
    return {"episode_id": "EP_TEST", "episode_dir_name": "EP_TEST", "title": "Test Episode", "internal_dir": "/unused"}


def test_upload_is_blocked_when_a_likely_duplicate_exists_on_the_channel(tmp_path, monkeypatch):
    """Hình dạng ĐÚNG vụ EP005/EP007 thật: 1 video đã có sẵn trên kênh
    trùng thời lượng với bản SẮP upload -- PHẢI dừng lại TRƯỚC khi gọi
    upload_video(), KHÔNG được chỉ log cảnh báo rồi vẫn upload."""
    topic = "Test Topic Long"
    video_path, wav_path = _seed_episode(tmp_path, topic, duration_sec=6.0)

    existing_on_channel = dc.ChannelVideo("EXISTING_DUP_ID", "Tiêu Đề Khác Hoàn Toàn", 6.2, "2026-07-24T13:00:00Z")
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: [existing_on_channel])

    def _upload_should_never_be_called(*a, **kw):
        raise AssertionError("upload_video() KHÔNG được gọi khi đã phát hiện khả năng trùng -- fail-closed thật sự")
    monkeypatch.setattr(lbr, "upload_video", _upload_should_never_be_called)

    # tmp_path-based credentials path -- channel_upload_lock() (khoá kênh
    # mới thêm) tạo file khoá NGAY CẠNH đường dẫn credentials; dùng path
    # trong tmp_path để không rơi 1 file .lock mồ côi vào cwd thật (đã tự
    # phát hiện: "fake_creds.json.lock" từng bị tạo trong chính thư mục dự
    # án khi test dùng string tương đối trần).
    credentials_path = str(tmp_path / "fake_creds.json")
    result = lbr.process_one_episode(
        _ep_arg(), topic, credentials_path, None, "2026-08-20T13:00:00Z", dry_run=False, domain="BUD",
    )

    assert result["status"] == "possible_duplicate_detected"
    assert result["possible_duplicate"]["suspected_video_id"] == "EXISTING_DUP_ID"
    assert "video_id" not in result  # KHÔNG được có video_id thật -- chưa hề upload

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"]["status"] == "possible_duplicate_detected"
    assert on_disk["EP_TEST"]["possible_duplicate"]["suspected_video_id"] == "EXISTING_DUP_ID"

    # Status mới PHẢI nằm trong TERMINAL_STATUSES -- 1 lần main() chạy tiếp
    # theo KHÔNG được tự động thử render/upload lại episode này (cần người
    # thật xem xét trước, xem docstring TERMINAL_STATUSES).
    assert "possible_duplicate_detected" in lbr.TERMINAL_STATUSES


def test_upload_proceeds_normally_when_no_duplicate_is_found(tmp_path, monkeypatch):
    """Đối chứng: khi KHÔNG có video nào khớp duration trên kênh, luồng
    upload thật vẫn chạy bình thường -- fix này không chặn nhầm case hợp
    lệ (episode thật sự MỚI)."""
    topic = "Test Topic Long"
    _seed_episode(tmp_path, topic, duration_sec=6.0)

    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: [])  # kênh trống/không có video nào khớp
    monkeypatch.setattr(lbr, "upload_video", lambda *a, **kw: {"id": "REAL_NEW_UPLOAD_ID"})

    result = lbr.process_one_episode(
        _ep_arg(), topic, str(tmp_path / "fake_creds.json"), None, "2026-08-20T13:00:00Z", dry_run=False, domain="BUD",
    )

    assert result["status"] == "uploaded"
    assert result["video_id"] == "REAL_NEW_UPLOAD_ID"

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"]["status"] == "uploaded"
    assert on_disk["EP_TEST"]["video_id"] == "REAL_NEW_UPLOAD_ID"


def test_channel_upload_lock_is_actually_held_across_the_upload_call(tmp_path, monkeypatch):
    """Codex CLI adversarial review round 1, finding thật HIGH (race
    condition): kiểm tra trùng rồi upload TÁCH RỜI theo thời gian -- nếu 2
    tiến trình cùng đọc catalog kênh gần như đồng thời (vd 1 lần launchd
    theo lịch + 1 lần chạy tay chồng lấn), cả hai đều có thể thấy "chưa có
    bản nào khớp" rồi CẢ HAI đều upload, tạo bản TRÙNG THẬT. Test này xác
    nhận channel_upload_lock() THẬT SỰ giữ khoá liên-tiến-trình (fcntl.flock)
    xuyên suốt bước upload_video() -- không chỉ bọc quanh bước kiểm tra
    trùng rồi thả khoá ra trước khi upload."""
    topic = "Test Topic Long"
    _seed_episode(tmp_path, topic, duration_sec=6.0)
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", lambda credentials_path: [])

    credentials_path = tmp_path / "creds.json"
    credentials_path.write_text("{}", encoding="utf-8")
    lock_path = credentials_path.with_suffix(credentials_path.suffix + ".lock")

    def _upload_checks_lock_is_currently_held(*a, **kw):
        # Cố lấy khoá KHÔNG CHẶN (LOCK_NB) trên CHÍNH file khoá kênh -- nếu
        # process_one_episode() đang thật sự giữ khoá lúc gọi upload_video(),
        # thao tác này PHẢI thất bại (BlockingIOError).
        fh = open(lock_path, "w")
        try:
            with pytest.raises(BlockingIOError):
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            fh.close()
        return {"id": "REAL_NEW_UPLOAD_ID"}

    monkeypatch.setattr(lbr, "upload_video", _upload_checks_lock_is_currently_held)

    result = lbr.process_one_episode(
        _ep_arg(), topic, str(credentials_path), None, "2026-08-20T13:00:00Z", dry_run=False, domain="BUD",
    )
    assert result["status"] == "uploaded"

    # Sau khi xong (khoá đã giải phóng), lấy lại khoá PHẢI thành công NGAY
    # -- xác nhận khoá được thả đúng lúc (không leak/deadlock cho lần chạy
    # kế tiếp trên CÙNG kênh).
    fh2 = open(lock_path, "w")
    fcntl.flock(fh2, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fcntl.flock(fh2, fcntl.LOCK_UN)
    fh2.close()


def test_waiter_rereads_fresh_registry_after_acquiring_the_lock_and_does_not_re_upload(tmp_path, monkeypatch):
    """Codex CLI adversarial review round 2, finding thật HIGH còn sót lại
    SAU KHI thêm channel_upload_lock(): khoá kênh tuần tự hoá đúng thứ tự
    upload, nhưng tiến trình B (đang chờ khoá) vẫn cầm `entry` CŨ (status=
    'seo_ready', đọc TRƯỚC khi A upload xong) -- nếu B không đọc lại
    registry NGAY SAU KHI giành được khoá, B vẫn có thể upload TRÙNG dù
    thứ tự thực thi đã đúng. Dùng 2 THREAD thật (fcntl.flock chặn CHÉO
    theo file descriptor, hoạt động đúng giữa 2 thread trong CÙNG 1
    process y hệt giữa 2 process khác nhau) để tái hiện đúng race.

    Codex CLI adversarial review round 3, finding thật: bản trước dùng
    time.sleep(0.2) làm "khoảng đệm" để B kịp tới điểm chờ khoá -- không
    TẤT ĐỊNH (1 hệ thống chậm/tải cao có thể khiến B chưa tới kịp, khiến
    test PASS ngay cả khi bỏ hẳn bản vá fresh-reload, vì B sẽ bị chặn ở
    recheck_entry SỚM HƠN thay vì ở đúng điểm cần kiểm). Sửa: dùng
    _InstrumentedFileLock -- 1 subclass CỦA CHÍNH FileLock thật, tự phát
    tín hiệu (b_about_to_acquire) NGAY TRƯỚC khi gọi fcntl.flock() CHẶN
    thật -- thời điểm đó được xác nhận CHÍNH XÁC bằng chính luồng thực thi
    của B (không suy luận qua thời gian chờ), và A CHỈ được thả khoá SAU
    KHI quan sát được tín hiệu đó -- loại bỏ hoàn toàn phụ thuộc vào tốc độ
    máy."""
    topic = "Test Topic Long"
    credentials_path = tmp_path / "creds.json"
    credentials_path.write_text("{}", encoding="utf-8")
    _seed_episode(tmp_path, topic, duration_sec=6.0)

    a_holds_lock = threading.Event()
    b_about_to_acquire = threading.Event()
    duplicate_check_calls = []
    upload_calls = []

    real_file_lock = dc.FileLock

    class _InstrumentedFileLock(real_file_lock):
        """Phát tín hiệu CHÍNH XÁC ngay trước lệnh gọi chặn thật
        (fcntl.flock trong FileLock.__enter__() gốc) -- chỉ cho thread tên
        "B" (xem threading.Thread(..., name="B") bên dưới), để phân biệt
        với lần A tự giành khoá lúc KHÔNG bị cạnh tranh."""
        def __enter__(self):
            if threading.current_thread().name == "B":
                b_about_to_acquire.set()
            return super().__enter__()

    monkeypatch.setattr(dc, "FileLock", _InstrumentedFileLock)

    def fake_check_for_possible_duplicate(*a, **kw):
        duplicate_check_calls.append(1)
        # Chỉ A (giữ khoá TRƯỚC, không bị cạnh tranh) đi vào đây -- báo cho
        # main thread biết A đang ở TRONG khoá, rồi CHỜ tín hiệu THẬT (không
        # phải đoán qua thời gian) rằng B đã tới đúng điểm gọi fcntl.flock()
        # chặn -- CHỈ khi đó A mới trả về (rồi "upload" + nhả khoá).
        a_holds_lock.set()
        assert b_about_to_acquire.wait(timeout=5), "B không tới kịp điểm chờ khoá trong 5s -- có thể lỗi thiết lập test"
        return None

    def fake_upload_video(*a, **kw):
        upload_calls.append(1)
        return {"id": f"UPLOAD_FROM_A_{len(upload_calls)}"}

    monkeypatch.setattr(lbr, "check_for_possible_duplicate", fake_check_for_possible_duplicate)
    monkeypatch.setattr(lbr, "upload_video", fake_upload_video)

    results = {}

    def _run(label):
        results[label] = lbr.process_one_episode(
            _ep_arg(), topic, str(credentials_path), None, "2026-08-20T13:00:00Z", dry_run=False, domain="BUD",
        )

    thread_a = threading.Thread(target=_run, args=("A",), name="A")
    thread_a.start()
    # Chờ tín hiệu THẬT (A đã giành khoá + đang trong fake_check_for_possible_
    # duplicate()) thay vì đoán qua thời gian -- tất định, không phụ thuộc
    # tốc độ máy chạy test.
    assert a_holds_lock.wait(timeout=5), "A không giành được khoá trong 5s -- có thể lỗi thiết lập test"

    thread_b = threading.Thread(target=_run, args=("B",), name="B")
    thread_b.start()

    thread_a.join(timeout=10)
    thread_b.join(timeout=10)
    assert not thread_a.is_alive() and not thread_b.is_alive(), "1 trong 2 thread bị treo -- có thể deadlock trên channel_upload_lock()"

    # Bất biến QUAN TRỌNG NHẤT: chỉ upload ĐÚNG 1 LẦN, dù 2 "tiến trình"
    # cùng cố xử lý 1 episode.
    assert len(upload_calls) == 1, f"upload_video() phải chỉ được gọi 1 lần, thực tế {len(upload_calls)} lần -- TRÙNG THẬT"
    assert len(duplicate_check_calls) == 1, "check_for_possible_duplicate() phải chỉ được gọi 1 lần (bởi A) -- B phải bị chặn SỚM HƠN bởi fresh-registry recheck"

    assert results["A"]["status"] == "uploaded"
    assert results["B"]["status"] == "uploaded"
    assert results["A"]["video_id"] == results["B"]["video_id"] == "UPLOAD_FROM_A_1"

    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"]["video_id"] == "UPLOAD_FROM_A_1"


def test_dry_run_does_not_perform_the_duplicate_check_or_hit_the_network(tmp_path, monkeypatch):
    """dry-run vẫn phải hoạt động headless như trước -- không gọi
    fetch_channel_video_catalog() (không cần network) trong nhánh dry-run."""
    topic = "Test Topic Long"
    _seed_episode(tmp_path, topic, duration_sec=6.0)

    def _should_not_be_called(credentials_path):
        raise AssertionError("dry-run không được gọi YouTube API")
    monkeypatch.setattr(dc, "fetch_channel_video_catalog", _should_not_be_called)

    result = lbr.process_one_episode(
        _ep_arg(), topic, str(tmp_path / "fake_creds.json"), None, "2026-08-20T13:00:00Z", dry_run=True, domain="BUD",
    )
    assert result["status"] == "dry_run_done"
