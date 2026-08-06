"""Regression test cho G1 (Audio Generation remediation, finding A4/M1):
process_drive_queue.process_long_folder() KHÔNG được upload hay đánh dấu
hoàn tất (thêm vào existing_outputs, chuyển input vào processed/, tăng
n_rendered) trừ khi render, QA VÀ upload đều thành công. Job lỗi ở bất kỳ
bước nào phải giữ nguyên trạng thái pending để tự động thử lại ở lần chạy
sau -- không có "processed" giả ghi nhớ lỗi.

Trước fix: upload_paths_to_drive() được gọi VÔ ĐIỀU KIỆN ngay sau
render_text(), TRƯỚC khi check result.success (A4), và giá trị bool trả về
của nó bị bỏ qua hoàn toàn (M1). Test này khoá đúng hành vi sau fix bằng
cách tiêm lỗi ở từng bước: render (exception), QA (result.success=False),
upload (return False), output một phần (nhiều file, chỉ 1 file lỗi), và
mô phỏng restart tiến trình (gọi lại process_long_folder với session mới).

Round 2 (sau Codex review round 1, BLOCKED — finding High #1): thêm test
dùng upload_paths_to_drive() THẬT (không mock hàm này) + rclone giả ở tầng
drive_utils, chứng minh lỗ hổng "upload dở dang" đã được vá: nếu 1 lần
chạy upload được .wav nhưng .srt lỗi mạng giữa chừng, lần chạy SAU không
được coi là "đã xong" chỉ vì .wav đã có trên Drive -- phải thấy .srt/.json
còn thiếu và render+upload lại."""
from pathlib import Path

import pytest

import drive_utils
import process_drive_queue as pdq
from render_engine import RenderResult


class FakeSession:
    """Session giả: trả về 1 RenderResult (hoặc raise 1 Exception) cho mỗi
    lần render_text() được gọi, theo đúng thứ tự đã cấu hình."""

    def __init__(self, results):
        self._results = list(results)
        self.voice_name = "TestVoice"
        self.render_calls = []

    def render_text(self, text, out_path, cache_dir=None, manifest_extra=None):
        self.render_calls.append((text, out_path))
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def _result(success: bool) -> RenderResult:
    return RenderResult(
        out_path=Path("out.wav"),
        duration_s=1.0,
        n_chunks=1,
        n_retried=0,
        n_failed=0 if success else 1,
        success=success,
        srt_path=Path("out.srt"),
        manifest_path=Path("out.json"),
    )


def _write_txt(tmp_path: Path, name: str, content: str = "nội dung test") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # cache_dir/local_output_dir dùng path tương đối -- chạy trong tmp_path
    # để không đụng tới chunks_cache/ thật của repo.
    monkeypatch.chdir(tmp_path)


def test_qa_failure_never_uploads_and_leaves_item_retryable(tmp_path):
    src = _write_txt(tmp_path, "a.txt")
    session = FakeSession([_result(success=False)])

    def _upload_must_not_be_called(paths, remote):
        raise AssertionError("upload_paths_to_drive() KHÔNG được gọi khi QA fail")

    pdq_module_upload = pdq.upload_paths_to_drive
    try:
        pdq.upload_paths_to_drive = _upload_must_not_be_called
        n_rendered, n_skipped, n_failed = pdq.process_long_folder(
            session, "gdrive:in/", "gdrive:out/", local_source_files=[src]
        )
    finally:
        pdq.upload_paths_to_drive = pdq_module_upload

    assert (n_rendered, n_skipped, n_failed) == (0, 0, 1)


def test_upload_failure_blocks_completion_and_processed_move(tmp_path, monkeypatch):
    """Nguồn Drive thật (from_local=False): render+QA OK nhưng upload lỗi ->
    KHÔNG được gọi rclone moveto (input phải ở nguyên trong input_remote để
    thử lại)."""
    monkeypatch.setattr(pdq, "list_pending_files", lambda remote: ["a.txt"])
    monkeypatch.setattr(pdq, "list_files_in", lambda remote: set())

    rclone_calls = []

    def fake_rclone(*args, **kwargs):
        rclone_calls.append(args)
        if args[0] == "copyto":
            local_dest = Path(args[2])
            local_dest.parent.mkdir(parents=True, exist_ok=True)
            local_dest.write_text("nội dung test", encoding="utf-8")
        return type("R", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr(pdq, "rclone", fake_rclone)
    monkeypatch.setattr(pdq, "upload_paths_to_drive", lambda paths, remote: False)

    session = FakeSession([_result(success=True)])
    n_rendered, n_skipped, n_failed = pdq.process_long_folder(
        session, "gdrive:in/", "gdrive:out/"
    )

    assert (n_rendered, n_skipped, n_failed) == (0, 0, 1)
    moveto_calls = [c for c in rclone_calls if c[0] == "moveto"]
    assert moveto_calls == [], "upload lỗi nhưng vẫn moveto vào processed/ -- mất khả năng retry"


def test_full_success_uploads_and_marks_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(pdq, "list_pending_files", lambda remote: ["a.txt"])
    monkeypatch.setattr(pdq, "list_files_in", lambda remote: set())

    rclone_calls = []

    def fake_rclone(*args, **kwargs):
        rclone_calls.append(args)
        if args[0] == "copyto":
            local_dest = Path(args[2])
            local_dest.parent.mkdir(parents=True, exist_ok=True)
            local_dest.write_text("nội dung test", encoding="utf-8")
        return type("R", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr(pdq, "rclone", fake_rclone)
    upload_calls = []
    monkeypatch.setattr(
        pdq, "upload_paths_to_drive",
        lambda paths, remote: (upload_calls.append((paths, remote)), True)[1],
    )

    session = FakeSession([_result(success=True)])
    n_rendered, n_skipped, n_failed = pdq.process_long_folder(
        session, "gdrive:in/", "gdrive:out/"
    )

    assert (n_rendered, n_skipped, n_failed) == (1, 0, 0)
    assert len(upload_calls) == 1
    moveto_calls = [c for c in rclone_calls if c[0] == "moveto"]
    assert len(moveto_calls) == 1
    assert moveto_calls[0][1] == "gdrive:in/a.txt"
    assert moveto_calls[0][2] == "gdrive:in/processed/a.txt"


def test_render_exception_propagates_without_upload_or_completion(tmp_path):
    src = _write_txt(tmp_path, "a.txt")
    session = FakeSession([RuntimeError("TTS engine crash")])

    def _upload_must_not_be_called(paths, remote):
        raise AssertionError("upload_paths_to_drive() KHÔNG được gọi khi render raise")

    import process_drive_queue as pdq_mod
    orig_upload = pdq_mod.upload_paths_to_drive
    pdq_mod.upload_paths_to_drive = _upload_must_not_be_called
    try:
        with pytest.raises(RuntimeError, match="TTS engine crash"):
            pdq_mod.process_long_folder(
                session, "gdrive:in/", "gdrive:out/", local_source_files=[src]
            )
    finally:
        pdq_mod.upload_paths_to_drive = orig_upload


def test_partial_output_only_completes_the_successful_file(tmp_path, monkeypatch):
    """2 file trong batch: 1 thành công, 1 lỗi QA -- chỉ file thành công
    được upload/đánh dấu xong, file lỗi vẫn pending."""
    src_ok = _write_txt(tmp_path, "ok.txt")
    src_bad = _write_txt(tmp_path, "bad.txt")

    session = FakeSession([_result(success=True), _result(success=False)])
    upload_calls = []
    monkeypatch.setattr(
        pdq, "upload_paths_to_drive",
        lambda paths, remote: (upload_calls.append(remote), True)[1],
    )

    n_rendered, n_skipped, n_failed = pdq.process_long_folder(
        session, "gdrive:in/", "gdrive:out/", local_source_files=[src_ok, src_bad]
    )

    assert (n_rendered, n_skipped, n_failed) == (1, 0, 1)
    assert len(upload_calls) == 1, "chỉ file QA-pass mới được upload"


def test_process_restart_resumes_only_the_unfinished_item(tmp_path, monkeypatch):
    """Mô phỏng restart tiến trình: lần chạy 1 có 2 file, A thành công, B
    lỗi upload (transient). Lần chạy 2 (session MỚI, giống sau khi tiến
    trình bị kill/restart) chỉ cần B render lại -- A đã có trên Drive nên
    bị skip, KHÔNG render lại (idempotent), và B giờ thành công."""
    src_a = _write_txt(tmp_path, "a.txt")
    src_b = _write_txt(tmp_path, "b.txt")

    # --- Lần chạy 1: A OK, B upload lỗi ---
    upload_results_run1 = iter([True, False])
    monkeypatch.setattr(
        pdq, "upload_paths_to_drive",
        lambda paths, remote: next(upload_results_run1),
    )
    session1 = FakeSession([_result(success=True), _result(success=True)])
    n_rendered1, n_skipped1, n_failed1 = pdq.process_long_folder(
        session1, "gdrive:in/", "gdrive:out/", local_source_files=[src_a, src_b]
    )
    assert (n_rendered1, n_skipped1, n_failed1) == (1, 0, 1)

    # --- "Restart": session mới, A đã tồn tại trên Drive (existing_outputs
    # phản ánh đúng), B vẫn pending và giờ upload thành công ---
    monkeypatch.setattr(pdq, "list_files_in", lambda remote: {"a.wav", "a.srt", "a.json"})
    monkeypatch.setattr(pdq, "upload_paths_to_drive", lambda paths, remote: True)
    session2 = FakeSession([_result(success=True)])  # chỉ B được render lại
    n_rendered2, n_skipped2, n_failed2 = pdq.process_long_folder(
        session2, "gdrive:in/", "gdrive:out/", local_source_files=[src_a, src_b]
    )

    assert len(session2.render_calls) == 1, "A đã xong không được render lại"
    assert (n_rendered2, n_skipped2, n_failed2) == (1, 1, 0)


class _RealFileSession:
    """Session giả nhưng GHI FILE THẬT ra đĩa tại out_path/.srt/.json --
    cần thiết để test với upload_paths_to_drive() THẬT (hàm này check
    Path(p).exists() trước khi upload từng file)."""

    def __init__(self, success=True):
        self.success = success
        self.voice_name = "TestVoice"

    def render_text(self, text, out_path, cache_dir=None, manifest_extra=None):
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"RIFF....WAVEfmt ")
        srt_path = out_path.with_suffix(".srt")
        srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nx\n", encoding="utf-8")
        manifest_path = out_path.with_suffix(".json")
        manifest_path.write_text("{}", encoding="utf-8")
        return RenderResult(
            out_path=out_path, duration_s=1.0, n_chunks=1, n_retried=0,
            n_failed=0 if self.success else 1, success=self.success,
            srt_path=srt_path, manifest_path=manifest_path,
        )


def test_partial_artifact_upload_then_restart_reuploads_missing_files(tmp_path, monkeypatch):
    """Dùng upload_paths_to_drive() THẬT (không mock) + rclone giả ở tầng
    drive_utils: lần chạy 1 upload .wav thành công nhưng .srt lỗi mạng giữa
    chừng -> upload_ok=False, đúng như kỳ vọng, item KHÔNG bị đánh dấu xong.
    Lần chạy 2 (restart) -- existing_outputs phản ánh ĐÚNG những gì thật sự
    có trên Drive (chỉ .wav) -- item PHẢI được render+upload lại (không bị
    skip chỉ vì .wav đã tồn tại), và sau đó cả 3 file đều có mặt."""
    monkeypatch.setattr(drive_utils, "RCLONE_BIN", "/bin/echo")
    uploaded = set()
    monkeypatch.setattr(pdq, "list_files_in", lambda remote: set(uploaded))

    def fake_rclone_srt_fails(*args, **kwargs):
        result = type("R", (), {"returncode": 0, "stderr": ""})()
        if args[0] == "copy":
            src = Path(args[1])
            if src.suffix == ".srt":
                result = type("R", (), {"returncode": 1, "stderr": "network blip"})()
            else:
                uploaded.add(src.name)
        return result

    monkeypatch.setattr(drive_utils, "rclone", fake_rclone_srt_fails)

    src = _write_txt(tmp_path, "a.txt")

    n_rendered1, n_skipped1, n_failed1 = pdq.process_long_folder(
        _RealFileSession(success=True), "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )
    assert (n_rendered1, n_skipped1, n_failed1) == (0, 0, 1)
    assert uploaded == {"a.wav", "a.json"}, "wav+json lên được, chỉ .srt lỗi mạng như đã tiêm"

    def fake_rclone_all_ok(*args, **kwargs):
        if args[0] == "copy":
            uploaded.add(Path(args[1]).name)
        return type("R", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr(drive_utils, "rclone", fake_rclone_all_ok)

    n_rendered2, n_skipped2, n_failed2 = pdq.process_long_folder(
        _RealFileSession(success=True), "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )
    assert n_skipped2 == 0, "KHÔNG được skip chỉ vì .wav đã tồn tại -- .srt/.json còn thiếu"
    assert n_rendered2 == 1
    assert uploaded == {"a.wav", "a.srt", "a.json"}
