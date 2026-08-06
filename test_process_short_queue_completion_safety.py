"""Regression test cho G1 (Audio Generation remediation, finding A4/M1) áp
dụng cho nhánh Short: process_short_queue.process_short_folder() KHÔNG
được upload hay đánh dấu 1 đoạn hoàn tất (existing_outputs, n_rendered)
trừ khi render, QA VÀ upload của đoạn đó đều thành công. Đoạn lỗi phải giữ
nguyên trạng thái pending để tự thử lại ở lần chạy sau (rule skip-if-exists
sẵn có), và KHÔNG được kéo theo việc chuyển cả file nguồn vào processed/
(file_had_failure).

Round 2 (sau Codex review round 1, BLOCKED — finding High #1): thêm test
dùng upload_paths_to_drive() THẬT (không mock) + rclone giả ở tầng
drive_utils, chứng minh lỗ hổng "upload dở dang" đã được vá cho từng đoạn
Short y hệt Long."""
from pathlib import Path

import pytest

import drive_utils
import process_short_queue as psq
from render_engine import RenderResult


class FakeSession:
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


SEGMENT_TEXT = "*** 1\nĐoạn một.\n*** 2\nĐoạn hai.\n"


def _write_segments(tmp_path: Path, name: str, text: str = SEGMENT_TEXT) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_qa_failure_never_uploads_and_leaves_segment_retryable(tmp_path, monkeypatch):
    src = _write_segments(tmp_path, "a.txt", "*** 1\nĐoạn một.\n")
    monkeypatch.setattr(psq, "list_files_in", lambda remote: set())

    def _upload_must_not_be_called(paths, remote):
        raise AssertionError("upload_paths_to_drive() KHÔNG được gọi khi QA fail")
    monkeypatch.setattr(psq, "upload_paths_to_drive", _upload_must_not_be_called)

    session = FakeSession([_result(success=False)])
    n_rendered, n_skipped, n_failed = psq.process_short_folder(
        session, "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )

    assert (n_rendered, n_skipped, n_failed) == (0, 0, 1)


def test_upload_failure_blocks_completion_marking(tmp_path, monkeypatch):
    src = _write_segments(tmp_path, "a.txt", "*** 1\nĐoạn một.\n")
    monkeypatch.setattr(psq, "list_files_in", lambda remote: set())
    monkeypatch.setattr(psq, "upload_paths_to_drive", lambda paths, remote: False)

    session = FakeSession([_result(success=True)])
    n_rendered, n_skipped, n_failed = psq.process_short_folder(
        session, "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )

    assert (n_rendered, n_skipped, n_failed) == (0, 0, 1)


def test_full_success_uploads_and_marks_segment_complete(tmp_path, monkeypatch):
    src = _write_segments(tmp_path, "a.txt", "*** 1\nĐoạn một.\n")
    monkeypatch.setattr(psq, "list_files_in", lambda remote: set())
    upload_calls = []
    monkeypatch.setattr(
        psq, "upload_paths_to_drive",
        lambda paths, remote: (upload_calls.append(remote), True)[1],
    )

    session = FakeSession([_result(success=True)])
    n_rendered, n_skipped, n_failed = psq.process_short_folder(
        session, "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )

    assert (n_rendered, n_skipped, n_failed) == (1, 0, 0)
    assert len(upload_calls) == 1


def test_render_exception_propagates_without_upload_or_completion(tmp_path, monkeypatch):
    src = _write_segments(tmp_path, "a.txt", "*** 1\nĐoạn một.\n")
    monkeypatch.setattr(psq, "list_files_in", lambda remote: set())

    def _upload_must_not_be_called(paths, remote):
        raise AssertionError("upload_paths_to_drive() KHÔNG được gọi khi render raise")
    monkeypatch.setattr(psq, "upload_paths_to_drive", _upload_must_not_be_called)

    session = FakeSession([RuntimeError("TTS engine crash")])
    with pytest.raises(RuntimeError, match="TTS engine crash"):
        psq.process_short_folder(
            session, "gdrive:in/", "gdrive:out/", local_source_files=[src]
        )


def test_partial_output_only_completes_the_successful_segment(tmp_path, monkeypatch):
    """File có 2 đoạn: đoạn 1 thành công, đoạn 2 lỗi QA -- chỉ đoạn 1 được
    upload/đánh dấu xong; file KHÔNG được coi là hoàn tất toàn bộ (không
    chuyển vào processed/) vì file_had_failure=True."""
    src = _write_segments(tmp_path, "a.txt")  # 2 đoạn
    monkeypatch.setattr(psq, "list_files_in", lambda remote: set())
    upload_calls = []
    monkeypatch.setattr(
        psq, "upload_paths_to_drive",
        lambda paths, remote: (upload_calls.append(remote), True)[1],
    )

    session = FakeSession([_result(success=True), _result(success=False)])
    n_rendered, n_skipped, n_failed = psq.process_short_folder(
        session, "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )

    assert (n_rendered, n_skipped, n_failed) == (1, 0, 1)
    assert len(upload_calls) == 1, "chỉ đoạn QA-pass mới được upload"


def test_process_restart_resumes_only_the_unfinished_segment(tmp_path, monkeypatch):
    """Mô phỏng restart: lần chạy 1, đoạn 1 OK, đoạn 2 upload lỗi (transient).
    Lần chạy 2 (session MỚI) -- đoạn 1 đã có trên Drive nên skip (không
    render lại), đoạn 2 render lại và giờ thành công."""
    src = _write_segments(tmp_path, "a.txt")  # *** 1, *** 2
    monkeypatch.setattr(psq, "list_files_in", lambda remote: set())

    upload_results_run1 = iter([True, False])
    monkeypatch.setattr(
        psq, "upload_paths_to_drive",
        lambda paths, remote: next(upload_results_run1),
    )
    session1 = FakeSession([_result(success=True), _result(success=True)])
    n_rendered1, n_skipped1, n_failed1 = psq.process_short_folder(
        session1, "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )
    assert (n_rendered1, n_skipped1, n_failed1) == (1, 0, 1)

    # "Restart": đoạn 1 giờ tồn tại trên Drive, đoạn 2 upload thành công.
    monkeypatch.setattr(psq, "list_files_in", lambda remote: {"1_a.wav", "1_a.srt", "1_a.json"})
    monkeypatch.setattr(psq, "upload_paths_to_drive", lambda paths, remote: True)
    session2 = FakeSession([_result(success=True)])  # chỉ đoạn 2 được render lại
    n_rendered2, n_skipped2, n_failed2 = psq.process_short_folder(
        session2, "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )

    assert len(session2.render_calls) == 1, "đoạn 1 đã xong không được render lại"
    assert (n_rendered2, n_skipped2, n_failed2) == (1, 1, 0)


class _RealFileSession:
    """Session giả nhưng GHI FILE THẬT ra đĩa tại out_path/.srt/.json --
    cần cho test dùng upload_paths_to_drive() THẬT."""

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
    """upload_paths_to_drive() THẬT + rclone giả: đoạn 1 upload .wav OK
    nhưng .srt lỗi mạng -> KHÔNG được đánh dấu xong. Lần chạy 2 (restart)
    PHẢI thấy .srt/.json còn thiếu trên Drive và render+upload lại đoạn đó,
    không skip chỉ vì .wav đã tồn tại."""
    src = _write_segments(tmp_path, "a.txt", "*** 1\nĐoạn một.\n")
    monkeypatch.setattr(drive_utils, "RCLONE_BIN", "/bin/echo")
    uploaded = set()
    monkeypatch.setattr(psq, "list_files_in", lambda remote: set(uploaded))

    def fake_rclone_srt_fails(*args, **kwargs):
        if args[0] == "copy":
            src_path = Path(args[1])
            if src_path.suffix == ".srt":
                return type("R", (), {"returncode": 1, "stderr": "network blip"})()
            uploaded.add(src_path.name)
        return type("R", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr(drive_utils, "rclone", fake_rclone_srt_fails)

    n_rendered1, n_skipped1, n_failed1 = psq.process_short_folder(
        _RealFileSession(success=True), "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )
    assert (n_rendered1, n_skipped1, n_failed1) == (0, 0, 1)
    assert uploaded == {"1_a.wav", "1_a.json"}, "wav+json lên được, chỉ .srt lỗi mạng như đã tiêm"

    def fake_rclone_all_ok(*args, **kwargs):
        if args[0] == "copy":
            uploaded.add(Path(args[1]).name)
        return type("R", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr(drive_utils, "rclone", fake_rclone_all_ok)

    n_rendered2, n_skipped2, n_failed2 = psq.process_short_folder(
        _RealFileSession(success=True), "gdrive:in/", "gdrive:out/", local_source_files=[src]
    )
    assert n_skipped2 == 0, "KHÔNG được skip chỉ vì .wav đã tồn tại -- .srt/.json còn thiếu"
    assert n_rendered2 == 1
    assert uploaded == {"1_a.wav", "1_a.srt", "1_a.json"}
