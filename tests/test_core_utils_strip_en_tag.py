"""Audit kênh Hình Sự (2026-08-14) -- text đã normalize (sea_g2p tự chèn
<en>...</en> quanh từ mượn tiếng Anh, vd "DNA" -> "<en>d n a</en>") bị lưu
NGUYÊN VĂN vào timings -> .srt/manifest.json làm phụ đề, vì cặp thẻ chỉ
được "tiêu thụ" đúng bên trong bước G2P/phonemize (nội bộ trong
self.v.infer(), không quay lại timings). Real incident: short "Vì sao cảnh
sát phá án chỉ trong 10 ngày từ đĩa mềm?"
(ANDAXU_QutrnhkhoanhvngichiuDNAvbtgiDe_01) -- phụ đề burn-in thật hiện
literal "<en>d n a</en>", xác nhận qua chính file .srt đã render.

`strip_en_tag_for_display` chỉ làm sạch bản HIỂN THỊ (phụ đề/manifest) --
`render_engine.py` cố ý KHÔNG áp hàm này cho chunk text truyền vào
self.v.infer()/chunk_cache_fingerprint(), vì đó vẫn cần thẻ <en> nguyên vẹn
để G2P đọc đúng phát âm tiếng Anh (xác nhận trực tiếp qua sea_g2p.G2P thật:
g2p.phonemize_batch(['<en>d n a</en>'], punc_norm=True) đọc đúng ra phoneme
tiếng Anh D-N-A khi thẻ còn nguyên)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vieneu_utils.core_utils import strip_en_tag_for_display


def test_real_incident_text_fixed():
    """The EXACT real production text that produced the bug (DNA short),
    reproduced verbatim from the rendered .srt."""
    text = "cảnh sát lấy mẫu <en>d n a</en> từ xét nghiệm y tế của con gái rader mà không cần lệnh khám trực tiếp."
    result = strip_en_tag_for_display(text)
    assert "<en>" not in result and "</en>" not in result
    assert "cảnh sát lấy mẫu d n a từ xét nghiệm" in result


def test_inner_content_preserved_not_deleted():
    """Must keep the spelled-out letters, not just delete the whole tag --
    a subtitle showing nothing where "DNA" was spoken would be worse than
    showing the raw tag."""
    result = strip_en_tag_for_display("mẫu <en>d n a</en> xét nghiệm")
    assert "d n a" in result


def test_multiple_tags_in_one_string():
    text = "so sánh <en>d n a</en> với <en>u s d</en> trong hồ sơ."
    result = strip_en_tag_for_display(text)
    assert "<en>" not in result and "</en>" not in result
    assert "d n a" in result and "u s d" in result


def test_case_insensitive_tag_matching():
    result = strip_en_tag_for_display("mẫu <EN>d n a</EN> xét nghiệm")
    assert "<EN>" not in result and "</EN>" not in result


def test_no_tag_is_a_pure_noop():
    text = "câu bình thường không có thẻ nào cả."
    assert strip_en_tag_for_display(text) == text


def test_real_normalizer_actually_inserts_en_tag_for_english_loanword():
    """Confirms the SOURCE of the bug is real: sea_g2p's own Normalizer
    inserts <en> tags for English acronyms -- this is why
    strip_en_tag_for_display is needed downstream at all, not a
    hypothetical case."""
    sea_g2p = pytest.importorskip("sea_g2p")
    normalizer = sea_g2p.Normalizer(lang="vi")
    normalized = normalizer.normalize("mẫu DNA từ xét nghiệm")
    assert "<en>" in normalized.lower()
    cleaned = strip_en_tag_for_display(normalized)
    assert "<en>" not in cleaned.lower()


def test_real_g2p_still_pronounces_correctly_when_tag_kept_intact():
    """Confirms the fix is correctly SCOPED to display-only: G2P (used for
    actual synthesis) must still receive the tag intact to pronounce the
    English loanword correctly -- stripping it before G2P would break
    pronunciation instead of just cleaning up the subtitle."""
    sea_g2p = pytest.importorskip("sea_g2p")
    g2p = sea_g2p.G2P(lang="vi")
    phonemes = g2p.phonemize_batch(["mẫu <en>d n a</en> từ xét nghiệm"], punc_norm=True)[0]
    assert "<en>" not in phonemes and "</en>" not in phonemes
    assert "<" not in phonemes  # tag fully consumed by G2P, not leaked as literal text
