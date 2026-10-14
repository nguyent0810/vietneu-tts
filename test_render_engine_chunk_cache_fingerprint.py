"""Regression test cho G2 (Audio Generation remediation, finding B1 +
M2/B3): cache audio theo chunk phải định danh THEO NỘI DUNG (fingerprint =
hash(text đã normalize + giọng + mode + sample_rate + CHUNK_CACHE_VERSION)),
KHÔNG còn theo index vị trí như trước (``chunk_{i:04d}.wav``).

Trước fix: sửa text tại đúng 1 vị trí, hoặc đảo thứ tự 2 đoạn, sẽ khiến
lần render sau ĐỌC NHẦM audio cache của vị trí đó -- không có cách nào
phát hiện vì cache chỉ biết "đây là chunk số mấy", không biết "đây là
chunk của câu nào". Cũng không phân biệt sample_rate của file cache với
sample_rate hiện tại (M2/B3) -- đọc _sr ra rồi bỏ, dùng self.sample_rate
vô điều kiện.

Phần 1: unit test trực tiếp trên ``chunk_cache_fingerprint()`` (logic hash
thuần, không cần model).
Phần 2: test tích hợp trên ``RenderSession.render_text()`` THẬT (không
reimplement), với ``self.v`` giả (không load model TTS thật -- khớp
pattern ``test_render_engine_empty_input_srt.py``), chứng minh: input
giống hệt vẫn hit cache; sửa text không tái dùng audio cũ; đảo thứ tự
không lẫn lộn; cache sai sample_rate không bị âm thầm chấp nhận."""
from pathlib import Path

import numpy as np
import pytest

from render_engine import (
    CHUNK_CACHE_VERSION,
    RenderSession,
    chunk_cache_fingerprint,
)

SR = 24000


# ─── Phần 1: chunk_cache_fingerprint() thuần ──────────────────────────

def test_fingerprint_deterministic_for_identical_inputs():
    a = chunk_cache_fingerprint("xin chào", "Binh", "standard", SR)
    b = chunk_cache_fingerprint("xin chào", "Binh", "standard", SR)
    assert a == b


@pytest.mark.parametrize("vary", ["text", "voice", "mode", "sample_rate"])
def test_fingerprint_changes_when_any_dimension_changes(vary):
    base = dict(chunk_text="xin chào", voice_name="Binh", mode="standard", sample_rate=SR)
    changed = dict(base)
    if vary == "text":
        changed["chunk_text"] = "xin chào bạn"
    elif vary == "voice":
        changed["voice_name"] = "Khanh"
    elif vary == "mode":
        changed["mode"] = "fast"
    elif vary == "sample_rate":
        changed["sample_rate"] = 22050

    fp_base = chunk_cache_fingerprint(**base)
    fp_changed = chunk_cache_fingerprint(**changed)
    assert fp_base != fp_changed, f"đổi {vary} nhưng fingerprint KHÔNG đổi"


def test_fingerprint_serialization_is_unambiguous_across_field_boundaries():
    """Codex review round 1 (G2) phát hiện bản gốc nối chuỗi bằng
    ``"\\x1f".join(...)`` KHÔNG injective -- 2 input logic khác nhau có
    thể cho ra CÙNG payload nếu 1 field "tràn" byte phân cách sang field
    kế bên. Test này khoá đúng ví dụ phản chứng Codex đã chạy thật để xác
    nhận collision tồn tại trước khi fix."""
    fp1 = chunk_cache_fingerprint("a\x1fb", "c", "standard", SR)
    fp2 = chunk_cache_fingerprint("a", "b\x1fc", "standard", SR)
    assert fp1 != fp2, "2 input logic khác nhau (field bị 'tràn' byte phân cách) tạo fingerprint TRÙNG"


def test_fingerprint_reacts_to_cache_version_bump(monkeypatch):
    """CHUNK_CACHE_VERSION là escape hatch để invalidate toàn bộ cache cũ
    thủ công khi logic synthesis đổi -- xác nhận nó thực sự nằm trong hash."""
    import render_engine

    fp_v1 = chunk_cache_fingerprint("xin chào", "Binh", "standard", SR)
    monkeypatch.setattr(render_engine, "CHUNK_CACHE_VERSION", "v2-test")
    fp_v2 = render_engine.chunk_cache_fingerprint("xin chào", "Binh", "standard", SR)
    assert fp_v1 != fp_v2


# ─── Phần 2: render_text() thật + self.v giả (không load model) ──────

class _FakeVieneu:
    """self.v giả: sinh audio TỔNG HỢP xác định (deterministic) theo đúng
    text -- đủ dài để qua chunk_is_suspect() (không bị nghi lỗi giả), đủ
    khác nhau giữa các text khác nhau để phân biệt được trong assertion."""

    def __init__(self):
        self.calls: list[str] = []

    def infer(self, chunk, voice=None, skip_normalize=True, temperature=1.0):
        self.calls.append(chunk)
        # Biên độ 0.2 (> ngưỡng RMS 0.0015) để không bị coi là "khoảng lặng
        # nội bộ"; thời lượng khớp đúng SEC_PER_CHAR*len(text) để không bị
        # coi là "duration bất thường".
        from render_engine import SEC_PER_CHAR
        n_samples = max(1, int(SEC_PER_CHAR * len(chunk) * SR))
        # Giá trị phụ thuộc hash(chunk) để audio của 2 text khác nhau khác
        # nhau thật sự (không phải toàn hằng số 0.2 giống hệt nhau).
        seed = abs(hash(chunk)) % (2**31)
        rng = np.random.default_rng(seed)
        return (rng.uniform(0.15, 0.25, n_samples)).astype(np.float32)


def _fake_session(voice_name="TestVoice", mode="standard") -> tuple[RenderSession, _FakeVieneu]:
    session = object.__new__(RenderSession)
    fake_v = _FakeVieneu()
    session.v = fake_v
    session.mode = mode
    session.voice_name = voice_name
    session.voice = None
    session.sample_rate = SR
    return session, fake_v


def test_identical_rerun_hits_cache_no_new_infer_calls(tmp_path):
    session, fake_v = _fake_session()
    cache_dir = tmp_path / "cache"
    text = "Hello world one.\nHello world two."

    r1 = session.render_text(text, tmp_path / "out1.wav", cache_dir=cache_dir)
    assert len(fake_v.calls) == 2  # 2 câu -> 2 chunk, cả 2 đều cache-miss lần đầu

    fake_v.calls.clear()
    r2 = session.render_text(text, tmp_path / "out2.wav", cache_dir=cache_dir)
    assert fake_v.calls == [], "input giống hệt PHẢI hit cache hoàn toàn, không gọi infer() lần nào"
    assert r2.n_chunks == r1.n_chunks == 2


def test_edited_text_at_same_position_does_not_reuse_stale_audio(tmp_path):
    session, fake_v = _fake_session()
    cache_dir = tmp_path / "cache"

    session.render_text(
        "Hello world one.\nHello world two.", tmp_path / "out1.wav", cache_dir=cache_dir
    )
    fake_v.calls.clear()

    # Sửa CÂU ĐẦU (vẫn ở "vị trí 0" như bản gốc) -- bản cũ (index-based)
    # sẽ đọc nhầm audio cache cũ của "hello world one." cho câu mới này.
    session.render_text(
        "Hello world one edited.\nHello world two.", tmp_path / "out2.wav", cache_dir=cache_dir
    )

    assert len(fake_v.calls) == 1, "chỉ đúng 1 câu bị sửa -- chỉ nó cần render lại"
    assert fake_v.calls[0] == "hello world one edited."
    assert "hello world two." not in fake_v.calls  # câu 2 KHÔNG đổi -- vẫn hit cache


def test_reordered_identical_chunks_reuse_cache_without_cross_contamination(tmp_path):
    session, fake_v = _fake_session()
    cache_dir = tmp_path / "cache"

    r1 = session.render_text(
        "Hello world one.\nHello world two.", tmp_path / "out1.wav", cache_dir=cache_dir
    )
    fake_v.calls.clear()

    # Đảo thứ tự 2 câu -- fingerprint theo NỘI DUNG nên mỗi câu vẫn tìm
    # đúng cache CỦA CHÍNH NÓ dù đổi vị trí, KHÔNG lẫn sang audio của câu
    # còn lại (đây là bug B1 gốc: cache index-based sẽ gán nhầm audio của
    # "câu 1 cũ" cho "câu 1 mới" dù nội dung đã đảo).
    r2 = session.render_text(
        "Hello world two.\nHello world one.", tmp_path / "out2.wav", cache_dir=cache_dir
    )

    assert fake_v.calls == [], "đảo thứ tự nhưng nội dung từng câu không đổi -- vẫn phải hit cache"
    # Audio ghép ra phải đúng thứ tự MỚI (câu "two" trước) -- không phải
    # ghép nhầm audio cũ theo thứ tự cũ.
    import soundfile as sf
    audio2, _ = sf.read(tmp_path / "out2.wav")
    audio1, _ = sf.read(tmp_path / "out1.wav")
    assert not np.array_equal(audio1, audio2), "thứ tự đảo ngược phải cho ra file audio khác thứ tự"


def test_stale_sample_rate_cache_triggers_regeneration_not_silent_reuse(tmp_path):
    """M2/B3: file cache tồn tại đúng tên fingerprint nhưng ở sample_rate
    KHÁC -- trước đây sẽ bị đọc và dùng self.sample_rate vô điều kiện cho
    timing/QA (sai). Giờ phải bị coi là cache lỗi và render lại."""
    import soundfile as sf

    session, fake_v = _fake_session()
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True)

    chunk_text = "hello world one."
    fp = chunk_cache_fingerprint(chunk_text, session.voice_name, session.mode, session.sample_rate)
    stale_path = cache_dir / f"chunk_{fp}.wav"
    # Ghi 1 file "cache" giả ở sample_rate SAI (16000 thay vì 24000).
    sf.write(stale_path, np.full(8000, 0.2, dtype=np.float32), 16000)

    session.render_text("Hello world one.", tmp_path / "out.wav", cache_dir=cache_dir)

    assert fake_v.calls == [chunk_text], "sample_rate cache lệch phải bị coi là miss, render lại"
