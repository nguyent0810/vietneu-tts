"""Regression test cho G3 (Audio Generation remediation, finding D2):
RenderSession.render_text(..., already_normalized=True) PHẢI bỏ qua bước
tự gọi normalize_preserving_paragraphs() và dùng ``text`` NGUYÊN VĂN làm
input chunking -- đây là cơ chế đảm bảo "1 canonical normalized token
stream duy nhất" mà _short_tts_render.py dựa vào (tự normalize TRƯỚC để
tính important_indices, rồi truyền lại chính text đó, KHÔNG được normalize
lần 2 -- dù thực nghiệm cho thấy normalize 2 lần cho kết quả giống lần 1
trong đa số trường hợp, đây KHÔNG phải hợp đồng được đảm bảo, và với
already_normalized=True thì lời hứa đó không cần dựa vào nữa)."""
from pathlib import Path

import numpy as np
import pytest

from render_engine import RenderSession

SR = 24000


class _FakeVieneu:
    def __init__(self):
        self.calls: list[str] = []

    def infer(self, chunk, voice=None, skip_normalize=True, temperature=1.0):
        self.calls.append(chunk)
        n_samples = max(1, int(0.055 * len(chunk) * SR))
        return np.full(n_samples, 0.2, dtype=np.float32)


def _fake_session() -> tuple[RenderSession, _FakeVieneu]:
    session = object.__new__(RenderSession)
    fake_v = _FakeVieneu()
    session.v = fake_v
    session.mode = "standard"
    session.voice_name = "TestVoice"
    session.voice = None
    session.sample_rate = SR
    return session, fake_v


def test_already_normalized_true_skips_normalization(tmp_path, monkeypatch):
    import render_engine

    def _must_not_be_called(text):
        raise AssertionError("normalize_preserving_paragraphs() KHÔNG được gọi khi already_normalized=True")

    monkeypatch.setattr(render_engine, "normalize_preserving_paragraphs", _must_not_be_called)

    session, fake_v = _fake_session()
    # Text CHỨA số (123) -- nếu lỡ bị normalize lần nữa sẽ bị mở rộng
    # thành "một trăm hai mươi ba", khác hẳn với việc dùng nguyên văn.
    pre_normalized_text = "đây là văn bản đã normalize sẵn 123 giữ nguyên"
    session.render_text(pre_normalized_text, tmp_path / "out.wav", already_normalized=True)

    assert fake_v.calls == [pre_normalized_text], (
        "already_normalized=True phải đưa text NGUYÊN VĂN cho TTS, không qua normalize lần 2"
    )


def test_already_normalized_false_default_still_normalizes(tmp_path, monkeypatch):
    """Đối chứng: hành vi mặc định (already_normalized=False, không truyền)
    PHẢI vẫn tự normalize như trước -- fix round này không đổi hành vi cũ
    của mọi caller khác (process_drive_queue.py, process_short_queue.py,
    render_natural.py...)."""
    import render_engine

    calls = []
    real_normalize = render_engine.normalize_preserving_paragraphs

    def _spy(text):
        calls.append(text)
        return real_normalize(text)

    monkeypatch.setattr(render_engine, "normalize_preserving_paragraphs", _spy)

    session, fake_v = _fake_session()
    session.render_text("Có 123 con mèo", tmp_path / "out.wav")

    assert calls == ["Có 123 con mèo"]
    # Được normalize thật -- "123" phải bị mở rộng trước khi tới infer().
    assert fake_v.calls == ["có một trăm hai mươi ba con mèo."]
