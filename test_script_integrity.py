"""S8 Toàn vẹn văn bản (ticket 11): kiểm trên text sẽ được đọc (sau strip của
bước render), chặn câu lặp và markup sót, câu cụt chỉ là finding không chặn."""
import pytest

import content_quality_gate as cqg
import script_integrity as si


def _codes(result, blocking=True):
    return [f.reason_code for f in result.findings if f.blocking is blocking]


def test_clean_script_passes_without_findings():
    r = si.check("Hôm nay **Tuổi Thìn** được xem là thuận hoà.\nNgười tuổi Tuất nên thận trọng.\nChúc bạn một ngày an yên.")
    assert r.findings == [] and not r.failed


def test_sentence_repeated_three_times_is_blocking():
    s = "Hãy giữ tâm thế bình tĩnh và chủ động."
    r = si.check(f"Câu mở đầu hấp dẫn.\n{s}\n{s}\n{s}\nCâu kết.")
    rep = [f for f in r.findings if f.reason_code == si.SCR_REPEATED_SENTENCE]
    assert len(rep) == 2 and all(f.blocking for f in rep)
    assert [f.position for f in rep] == [2, 3] and rep[0].span == s
    assert r.failed and r.reason_codes == [si.SCR_REPEATED_SENTENCE]


def test_repeat_after_normalisation_is_caught():
    r = si.check("Ngày mai trời sẽ đẹp.\nNGÀY MAI, trời sẽ đẹp!\nKết thúc.")
    rep = [f for f in r.findings if f.reason_code == si.SCR_REPEATED_SENTENCE]
    assert rep and rep[0].kind == "repeated_normalized" and rep[0].blocking


def test_repeat_is_checked_after_importance_markers_are_stripped():
    r = si.check("**Tuổi Tý** gặp may hôm nay.\nTuổi Tý gặp may hôm nay.\nHết.")
    assert _codes(r) == [si.SCR_REPEATED_SENTENCE]


def test_every_repeated_sentence_blocks_even_very_short_ones():
    """D91: mọi câu lặp đều là lỗi chắc chắn -> chặn (không miễn câu ngắn)."""
    r = si.check("Vâng.\nĐây là nội dung chính.\nVâng.")
    assert _codes(r) == [si.SCR_REPEATED_SENTENCE] and r.failed


@pytest.mark.parametrize("script,needle", [
    ("Câu một có dấu * lẻ.\nCâu hai.", "*"),
    ("Câu một **chưa đóng.\nCâu hai.", "**"),
    ("Theo [nguồn 3] thì vậy.\nHết.", "["),
    ("Phần #2 bắt đầu.\nHết.", "#"),
    ("*** 1\nCâu một.", "***"),
    ("Phương án A: câu một.\nHết.", "Phương án A"),
    ('Kết quả {"script": "x"}.\nHết.', '"script":'),
    ("Xem thêm tại https://example.com ngay.\nHết.", "https://example.com"),
    ("Token <|endoftext|> lạ.\nHết.", "<|"),
])
def test_leftover_markup_is_blocking_with_span_evidence(script, needle):
    r = si.check(script)
    spans = [f.span for f in r.findings if f.reason_code == si.SCR_LEFTOVER_MARKUP]
    assert r.failed and any(needle in s or s in needle for s in spans), spans


def test_valid_emotion_tags_are_stripped_like_render_and_not_errors():
    r = si.check("Hôm nay trời đẹp [cười] thật.\nBạn thấy sao [thở dài]?\nHẹn gặp lại.")
    assert r.findings == []
    assert "[" not in r.spoken_text


def test_missing_final_punctuation_is_non_blocking_truncated():
    r = si.check("Câu một đầy đủ.\nCâu cuối bị cụt giữa chừng và")
    assert not r.failed
    assert _codes(r, blocking=False) == [si.SCR_TRUNCATED]
    assert r.findings[-1].position == 1


@pytest.mark.parametrize("ending", ["Bạn nghĩ sao?", "Còn tiếp…", "Thật tuyệt!", "Anh ấy nói: “Đi thôi.”"])
def test_intentional_endings_are_not_truncated(ending):
    assert si.check(f"Câu mở.\n{ending}").findings == []


def test_reason_codes_belong_to_the_closed_set():
    for code in (si.SCR_REPEATED_SENTENCE, si.SCR_LEFTOVER_MARKUP, si.SCR_TRUNCATED):
        assert code in cqg.REASON_CODES


def test_importing_s8_needs_no_render_engine_g2p_or_unix_locks():
    """S8 chạy cả trong python3 hệ thống của runner (không có sea_g2p): import
    không được kéo render_engine, vieneu_utils.phonemize_text, sea_g2p, fcntl."""
    import subprocess
    import sys
    from pathlib import Path
    code = ("import sys, script_integrity; bad = [m for m in ('fcntl', 'render_engine', 'registry_lock', "
            "'sea_g2p', 'vieneu_utils.phonemize_text') if m in sys.modules]; print(bad); sys.exit(1 if bad else 0)")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         cwd=str(Path(si.__file__).parent))
    assert out.returncode == 0, out.stdout + out.stderr


def test_emotion_tag_recognition_is_the_same_single_source_as_the_phonemizer():
    import vieneu_utils.emotion_tags as et
    import vieneu_utils.phonemize_text as pt
    assert pt._emotion_tag_token is et._emotion_tag_token and pt._EMOTION_SPLIT_RE is et._EMOTION_SPLIT_RE
