"""Regression test cho G1 (Codex review round 2, finding Medium #2):
RenderSession.render_text() phải LUÔN trả ``srt_path`` khác None khi
``write_srt_file=True``, kể cả khi input rỗng/toàn khoảng trắng dẫn tới
0 chunks (0 timings) sau normalize -- trước đây điều kiện ``if
write_srt_file and timings:`` khiến ``srt_path=None`` trong trường hợp
này dù ``write_srt_file=True`` và ``result.success=True`` (0 chunks -> 0
lỗi QA). ``upload_paths_to_drive()`` coi path None là "không có gì để
upload" và trả ``True`` -- nếu srt_path cứ None thì caller
(``process_drive_queue.py``/``process_short_queue.py``) sẽ đánh dấu hoàn
tất dù thiếu hẳn file .srt trên Drive, vi phạm bất biến "đủ cả
wav+srt+json" mà G1 (round 1) vừa thêm vào completeness check.

Không cần load model TTS thật -- trường hợp 0 chunks không bao giờ gọi
``self.v.infer()``/``self.voice``, nên bypass ``__init__`` (tránh load
model) và chỉ set đúng 2 attribute ``render_text()`` thực sự cần trong
nhánh này: ``sample_rate``, ``voice_name``."""
from pathlib import Path

import pytest

from render_engine import RenderSession


def _bare_session(sample_rate=24000, voice_name="TestVoice") -> RenderSession:
    session = object.__new__(RenderSession)
    session.sample_rate = sample_rate
    session.voice_name = voice_name
    return session


@pytest.mark.parametrize("text", ["", "   \n\n   ", "\n"])
def test_whitespace_only_input_still_produces_srt_path(tmp_path, text):
    session = _bare_session()
    out_path = tmp_path / "empty.wav"

    result = session.render_text(text, out_path)

    assert result.success is True  # 0 chunks -> 0 lỗi QA, đúng hành vi hiện tại
    assert result.n_chunks == 0
    assert result.srt_path is not None, "write_srt_file=True mặc định -- srt_path KHÔNG được là None"
    assert result.srt_path.exists()
    assert result.manifest_path is not None
    assert result.manifest_path.exists()


def test_write_srt_file_false_still_leaves_srt_path_none(tmp_path):
    """Đối chứng: khi caller CHỦ ĐỘNG tắt write_srt_file, srt_path vẫn phải
    là None như cũ -- fix round 2 chỉ bỏ điều kiện phụ thuộc `timings`,
    không đổi hành vi của cờ `write_srt_file` tự thân."""
    session = _bare_session()
    out_path = tmp_path / "no_srt.wav"

    result = session.render_text("  ", out_path, write_srt_file=False)

    assert result.srt_path is None
