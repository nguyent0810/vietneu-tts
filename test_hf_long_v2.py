"""Video dài v2: TTS từng câu (hf_voice), cắt chương (hf_batch_render), âm thanh 4 lớp (hf_foley)."""
import numpy as np
import pytest

import hf_batch_render as R
import hf_foley as F
import hf_voice as V


def test_line_cfg_alt_and_per_line_tempo():
    spec = {"voice": "Binh", "engine": "standard", "tempo": 0.91, "tempos": {"4": 0.86},
            "alt": {"voice": "Quang Sơn", "engine": "v3", "style": "tu_nhien", "tempo": 0.92, "lines": [7]}}
    assert V.line_cfg(spec, 1) == ("Binh", "doc_truyen", 0.91, "standard")
    assert V.line_cfg(spec, 4)[2] == 0.86                 # câu đỉnh chậm riêng
    assert V.line_cfg(spec, 7) == ("Quang Sơn", "tu_nhien", 0.92, "v3")   # giọng đọc kinh


def test_default_pause_heading_and_question():
    assert V.default_pause("**Chương một**", .35) >= .9
    assert V.default_pause("Vì sao vậy?", .35) == .6
    assert V.default_pause("Câu thường.", .35) == .35


def test_trim_keeps_speech_drops_silence():
    sr = 48000
    a = np.concatenate([np.zeros(sr), np.sin(np.arange(sr) / 10) * .5, np.zeros(sr)]).astype("float32")
    b = V.trim(a, sr)
    assert 0.9 * sr < len(b) < 1.2 * sr


def _segs(n, gap=.5, dur=2.0):
    out, t = [], 0.0
    for _ in range(n):
        out.append({"start": t, "end": t + dur})
        t += dur + gap
    return out


def test_chapter_spans_cut_at_headings_on_frame_grid():
    lines = ["a", "b", "**Chương 1**", "c", "d", "**Chương 2**", "e"]
    segs = _segs(len(lines))
    total = segs[-1]["end"] + .6
    spans = R.chapter_spans(lines, segs, total)
    assert [(a, b) for a, b, _, _ in spans] == [(0, 2), (2, 5), (5, 7)]
    assert spans[0][2] == 0 and spans[-1][3] <= total
    for (_, _, t0, t1), nxt in zip(spans, spans[1:]):
        assert t1 == nxt[2]                                  # liền mạch, không hở không chồng
        assert abs(t1 * R.FPS - round(t1 * R.FPS)) < 1e-6    # đúng lưới khung hình
    # mốc cắt nằm trong khoảng lặng trước tiêu đề
    assert segs[1]["end"] <= spans[1][2] <= segs[2]["start"]


def test_remap_at_shifts_nested_line_numbers():
    spec = {"type": "wheel", "until": 12, "steps": [{"at": 10, "word": "x"}, {"at": 11}], "at": 10}
    out = R._remap_at(spec, 9)
    assert out["until"] == 3 and out["at"] == 1 and [s["at"] for s in out["steps"]] == [1, 2]
    assert spec["until"] == 12                               # không sửa bản gốc


def _line(i, t0, t1, **kw):
    return {"sentence_id": i, "start": t0, "end": t1, "words": [{"w": "chữ", "t": t0 + .2}], **kw}


def test_foley_material_sounds_per_channel():
    lines = [_line(1, 0, 2, visual={"type": "list", "items": [{"at": 1}]}),
             _line(2, 2.5, 4, heading=True),
             _line(3, 4.5, 6, visual={"type": "ledger", "rows": [{"at": 3}, {"at": 3}]})]
    bud = {e[1] for e in F.events(lines, "bud", {}, set())}
    fs = {e[1] for e in F.events(lines, "fs", {}, set())}
    assert {"bead", "temple_bell"} <= bud and "abacus" not in bud      # tràng hạt, đại hồng chung
    assert {"abacus", "gong"} <= fs and "bead" not in fs               # bàn tính, cồng


def test_foley_silence_line_has_no_sound():
    lines = [_line(1, 0, 2, visual={"type": "word"}), _line(2, 2.5, 4, visual={"type": "ask"})]
    ev = F.events(lines, "bud", {}, {2})
    assert all(t < 2.5 - .5 for t, *_ in ev)


def test_ambience_kinds_are_finite_and_nonsilent():
    rng = np.random.default_rng(1)
    for k in ("night", "wind", "dawn", "river", "room"):
        a = F.ambience(k, 3.0, rng)
        assert np.isfinite(a).all() and np.abs(a).max() > 0


@pytest.mark.parametrize("fs", [True, False])
def test_motif_is_deterministic(fs):
    a, b = F.motif(F.Foley(3), fs), F.motif(F.Foley(3), fs)
    assert np.allclose(a, b) and np.abs(a).max() > 0


def test_ngu_am_tho_is_cung():
    assert F.NGU_AM["Thổ"] == "C4"     # Cung ứng Thổ (truyền thống ngũ âm)


def test_chapter_key_tracks_only_its_own_lines():
    row = {"script": ["**A**", "x", "y", "**B**", "z"], "style": "inkwash_long", "kinetic": True,
           "visuals": {"2": {"type": "word"}, "5": {"type": "ask"}}, "media": {}}
    k = R.chapter_key(row, 0, 3, 0.0, 9.0, "looks")
    assert len(k) == 40 and k == R.chapter_key(row, 0, 3, 0.0, 9.0, "looks")
    other = dict(row, visuals={"2": {"type": "word"}, "5": {"type": "word"}})      # đổi sơ đồ chương sau
    assert R.chapter_key(other, 0, 3, 0.0, 9.0, "looks") == k
    mine = dict(row, visuals={"2": {"type": "word", "text": "X"}, "5": {"type": "ask"}})
    assert R.chapter_key(mine, 0, 3, 0.0, 9.0, "looks") != k



def test_chapter_key_kicker_keeps_old_keys_and_tracks_changes():
    # Nhãn góc riêng (F4 "PHONG THỦY NHÀ Ở") phải render lại chương; video không đặt kicker giữ nguyên băm cũ.
    row = {"script": ["**A**", "x"], "style": "lacquer_long", "kinetic": True, "visuals": {}, "media": {}}
    base = R.chapter_key(row, 0, 2, 0.0, 5.0, "looks")
    assert R.chapter_key(dict(row, kicker=""), 0, 2, 0.0, 5.0, "looks") == base
    k1 = R.chapter_key(dict(row, kicker="PHONG THỦY NHÀ Ở"), 0, 2, 0.0, 5.0, "looks")
    assert k1 != base and k1 != R.chapter_key(dict(row, kicker="KHÁC"), 0, 2, 0.0, 5.0, "looks")


def test_render_chapters_passes_kicker():
    import inspect
    assert '"--kicker", row["kicker"]' in inspect.getsource(R.render_chapters)

def test_render_chapters_stores_chapter_hash_not_loop_var():
    # Lỗi 02/10/2026: vòng `for key, flag in (("media",..),("visuals",..))` đè biến băm -> render.json lưu "visuals",
    # mọi lần chạy lại đều render lại toàn bộ chương.
    import inspect
    src = inspect.getsource(R.render_chapters)
    assert "for key," not in src and 'res["input_sha1"] = key' in src


def test_bridge_temp_names_unique_per_output():
    # Lỗi 02/10/2026: hai video cùng có chương ch01 render song song -> file tạm trùng tên, ch01 của B4 mang hình F4.
    import inspect
    import hyperframes_bridge as HB
    src = inspect.getsource(HB.render)
    assert 'uid = f"{output.stem}_{hashlib.sha1(' in src
    for bad in ('f".vars_{output.stem}', 'f".render_{output.stem}', 'HF_ASSETS / f"{output.stem}'):
        assert bad not in src, bad


def test_foley_ratchet_many_ticks():
    # Lỗi 03/10/2026: ratchet(n > 10) vượt bộ đệm -> ValueError khi trộn tiếng F5.
    import hf_foley as FO
    p = FO.Foley(seed=1)
    for n in (5, 12, 30, 60):
        assert len(p.ratchet(n)) > 0


# ---- hf_voice: QA trung thực, cache key, fade/level, nghỉ theo ngữ cảnh ----

def test_default_pause_context():
    assert V.default_pause("Ngài nói:", .35) == .5                   # câu dẫn vào phần theo sau
    assert V.default_pause("Lời kinh.", .35, is_alt=True) == .7      # trích kinh để lắng
    assert V.default_pause("Câu thường.", .35, is_alt=True) == .7
    assert V.default_pause("Câu thường.", .9) == .9                  # không bao giờ ngắn hơn base


def test_cache_key_stable_and_sensitive(monkeypatch):
    k = V.cache_key("v3", "Binh", "doc_truyen", 0.9, "xin chào")
    assert k == V.cache_key("v3", "Binh", "doc_truyen", 0.9, "xin chào")
    assert k != V.cache_key("v3", "Binh", "doc_truyen", 0.9, "xin chao")
    assert k != V.cache_key("standard", "Binh", "doc_truyen", 0.9, "xin chào")
    monkeypatch.setattr(V, "MODEL_TAG", "rev2")
    assert k != V.cache_key("v3", "Binh", "doc_truyen", 0.9, "xin chào")   # đổi model -> đọc lại


def test_cache_key_unchanged_without_model_tag(monkeypatch):
    import hashlib
    monkeypatch.setattr(V, "MODEL_TAG", "")
    legacy = hashlib.sha1("1|v3|Binh|s|0.9|abc".encode()).hexdigest()[:20]
    assert V.cache_key("v3", "Binh", "s", 0.9, "abc") == legacy        # cache cũ còn dùng được


def test_fade_edges_zero_keeps_length_and_middle():
    a = np.ones(4800, dtype="float32")
    b = V.fade(a, 48000)
    assert len(b) == len(a) and b[0] == 0 and b[-1] == 0 and b[2400] == 1
    assert a[0] == 1                                                     # không sửa bản gốc
    short = np.ones(3, dtype="float32")
    assert len(V.fade(short, 48000)) == 3


def test_level_clamped_and_no_clip():
    quiet = (np.sin(np.arange(48000) / 5) * 0.001).astype("float32")
    out = V.level(quiet)
    assert np.abs(out).max() <= np.abs(quiet).max() * 10 ** (V.LEVEL_MAX_DB / 20) * 1.001   # tối đa +4 dB
    loud = (np.sin(np.arange(48000) / 5) * 0.99).astype("float32")
    assert np.abs(V.level(loud)).max() <= 0.98 + 1e-6
    assert np.all(V.level(np.zeros(100, dtype="float32")) == 0)


def test_suspect_flags_runaway_and_truncated():
    sr = V.SR
    text = "Đây là một câu đủ dài để thử."
    ok = np.zeros(int(sr * len(text) / 15), dtype="float32")
    assert V.suspect(text, ok, sr) is None
    assert V.suspect(text, np.zeros(sr * 30, dtype="float32"), sr) is not None     # đọc lồng
    assert V.suspect(text, np.zeros(int(sr * 0.2), dtype="float32"), sr) is not None  # cụt


def test_pick_device_env_override(monkeypatch):
    monkeypatch.setenv("VIENEU_DEVICE", "cuda:1")
    assert V.pick_device() == "cuda:1"


def test_synth_reports_failed_qa_and_does_not_cache_it(tmp_path, monkeypatch):
    sr = V.SR
    monkeypatch.setattr(V, "CACHE", tmp_path / "cache")
    good = np.sin(np.arange(int(sr * 2)) / 20).astype("float32") * .3

    class FakeVoices:
        retries = 3

        def say(self, text, voice, style, engine="v3"):
            return (good, "dài bất thường") if "hỏng" in text else (good, None)

    monkeypatch.setattr(V, "Voices", FakeVoices)
    monkeypatch.setattr(V, "tempo", lambda a, sr, k: a)
    spec = {"voice": "Binh", "pause": .1}
    m = V.synth(["Câu tốt đầu tiên.", "Câu hỏng này.", "Câu tốt cuối."], spec, tmp_path / "o.wav")
    assert m["n_failed_qa"] == 1 and m["qa_failed_lines"][0]["line"] == 2
    assert m["n_retried"] == 3
    assert len(list((tmp_path / "cache").glob("*.wav"))) == 2          # câu hỏng không vào cache
    assert len(m["segments"]) == 3


def test_synth_uses_lexicon_for_speech_not_for_text(tmp_path, monkeypatch):
    monkeypatch.setattr(V, "CACHE", tmp_path / "cache")
    seen = []
    good = (np.sin(np.arange(96000) / 20) * .3).astype("float32")

    class FakeVoices:
        retries = 0

        def say(self, text, voice, style, engine="v3"):
            seen.append(text)
            return good, None

    monkeypatch.setattr(V, "Voices", FakeVoices)
    monkeypatch.setattr(V, "tempo", lambda a, sr, k: a)
    m = V.synth(["Ngài Sāriputta hỏi từ 1-3 lần."], {"voice": "Binh"}, tmp_path / "o.wav")
    assert seen == ["Ngài Xá Lợi Phất hỏi từ 1 đến 3 lần."]
    assert m["segments"][0]["text"] == "Ngài Sāriputta hỏi từ 1-3 lần."      # phụ đề giữ chữ gốc
    assert "spoken" in m["segments"][0]
