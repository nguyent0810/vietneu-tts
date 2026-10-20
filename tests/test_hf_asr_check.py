"""hf_asr_check: so sánh ASR với chữ định đọc. Không cần model: `transcribe` được tiêm giả."""
import json

import numpy as np
import pytest
import soundfile as sf

import hf_asr_check as A

SR = 48000


def test_tokens_expand_numbers_and_ignore_punct_case():
    assert A.tokens("Năm 1983, ông 35 tuổi!") == A.tokens("năm một nghìn chín trăm tám mươi ba ông ba mươi lăm tuổi")
    assert A.tokens("Tăng 50%") == ["tăng", "năm", "mươi", "phần", "trăm"]


def test_strip_tones_keeps_vowel_quality():
    assert A.strip_tones("Việt") == "Viêt"
    assert A.strip_tones("hỏi") == "hoi"
    assert A.strip_tones("đường") == "đương"          # đ và ơ/ư giữ nguyên, chỉ bỏ thanh
    assert A.strip_tones("tiếng") != "tieng"           # ê giữ nguyên
    assert A.strip_tones("tiếng") == "tiêng"


def test_wer_basic():
    assert A.wer("một hai ba bốn", "một hai ba bốn") == 0
    assert A.wer("một hai ba bốn", "một hai ba") == pytest.approx(0.25)    # nuốt một chữ
    assert A.wer("một hai ba bốn", "một hai năm bốn") == pytest.approx(0.25)
    assert A.wer("", "") == 0 and A.wer("", "x") == 1


def test_wer_tone_insensitive_forgives_tone_errors():
    ref, hyp = "ông ấy đã hỏi rồi", "ông ây đa hoi rôi"
    assert A.wer(ref, hyp, tones=False) < A.wer(ref, hyp, tones=True)
    assert A.wer(ref, hyp, tones=False) == 0


def test_proper_name_detection_ignores_sentence_start():
    assert not A._has_proper_name("Hôm nay trời đẹp. Gió nhẹ.")
    assert A._has_proper_name("Hôm nay ông gặp Xá Lợi Phất.")
    assert A._has_proper_name("Ông nói. Rồi gặp Ananda.")


def test_is_risky():
    assert A.is_risky("Năm 1983 ông đến.")
    assert A.is_risky("Hôm nay ông gặp Xá Lợi Phất trên đường.")          # tên viết hoa giữa câu
    assert not A.is_risky("Hôm nay trời đẹp và gió nhẹ.")                  # đầu câu viết hoa không tính
    assert A.is_risky("Câu thường ở đây thôi.", alt=True)                   # giọng thứ hai
    assert A.is_risky("Ngài Sāriputta đến.", spoken="Ngài Xá Lợi Phất đến.")   # lexicon vừa đổi


def _wav(tmp_path, n_lines=3, dur=2.0):
    a = (np.sin(np.arange(int(SR * dur)) / 30) * .3).astype("float32")
    parts, segs, t = [], [], 0.0
    for i in range(n_lines):
        segs.append({"start": t, "end": t + dur, "text": "x"})
        parts += [a * (1 + i * .1), np.zeros(int(.3 * SR), dtype="float32")]
        t += dur + .3
    p = tmp_path / "o.wav"
    sf.write(p, np.concatenate(parts), SR)
    return p, segs


def test_check_flags_bad_line_caches_and_skips_safe_lines(tmp_path):
    p, segs = _wav(tmp_path)
    segs[0]["text"] = "Năm 1983 ông đến chùa."            # rủi ro (số)
    segs[1]["text"] = "Hôm nay trời đẹp và gió nhẹ."      # an toàn -> không nghe
    segs[2]["text"] = "Năm 2027 ông đi chợ về."           # rủi ro
    calls = []
    answers = iter(["năm một nghìn chín trăm tám mươi ba ông đến chùa", "năm hai nghìn không trăm hai mươi bảy"])

    def fake(audio):
        calls.append(len(audio))
        return next(answers)

    rep = A.check(p, {"segments": segs}, transcribe=fake, model_name="t", cache_dir=tmp_path / "c")
    assert len(calls) == 2 and rep["n_checked"] == 2           # câu an toàn bị bỏ qua
    assert all(abs(n - 2.0 * 16000) < 50 for n in calls)       # cắt đúng câu, 16 kHz
    assert [r["line"] for r in rep["flagged"]] == [3]           # dòng 3 mất "ông đi chợ về" -> WER 0.33 > 0.20
    # lần hai: cùng audio -> lấy từ cache, không gọi lại model
    calls.clear()
    rep2 = A.check(p, {"segments": segs}, transcribe=lambda a: pytest.fail("không được gọi lại"), model_name="t",
                   cache_dir=tmp_path / "c")
    assert rep2["n_cached"] == 2 and rep2["n_checked"] == 0
    assert [r["line"] for r in rep2["flagged"]] == [3]


def test_check_all_and_min_words(tmp_path):
    p, segs = _wav(tmp_path, 2)
    segs[0]["text"] = "Hôm nay trời đẹp và gió nhẹ."
    segs[1]["text"] = "Vâng."                                  # < MIN_WORDS: bỏ qua dù --all
    seen = []
    rep = A.check(p, {"segments": segs}, transcribe=lambda a: seen.append(1) or "hôm nay trời đẹp và gió nhẹ",
                  model_name="t", check_all=True, cache_dir=tmp_path / "c")
    assert len(seen) == 1 and rep["flagged"] == []


def test_check_uses_spoken_text_as_reference(tmp_path):
    p, segs = _wav(tmp_path, 1)
    segs[0].update(text="Ngài Sāriputta đến.", spoken="Ngài Xá Lợi Phất đến.")
    rep = A.check(p, {"segments": segs}, transcribe=lambda a: "ngài xá lợi phất đến", model_name="t",
                  cache_dir=tmp_path / "c")
    assert rep["flagged"] == [] and rep["lines"][0]["wer"] == 0


def test_cli_writes_report_and_strict_exit(tmp_path, monkeypatch, capsys):
    p, segs = _wav(tmp_path, 1)
    segs[0]["text"] = "Năm 1983 ông đến chùa."
    p.with_suffix(".json").write_text(json.dumps({"segments": segs}), encoding="utf-8")
    monkeypatch.setattr(A, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(A.Whisper, "transcribe", lambda self, audio: "không liên quan gì cả")
    rc = A.main([str(p), "--strict"])
    assert rc == 2
    assert json.loads(p.with_suffix(".asr.json").read_text(encoding="utf-8"))["flagged"]
    assert "CẢNH BÁO QA" in capsys.readouterr().err
