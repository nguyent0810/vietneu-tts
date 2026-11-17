"""075b: contract errors block; editorial guesses remain visible advice."""
import pytest

import audio_script_rules as A
import hf_batch_render as H
import long_script_lint as L
from library.tools import hook_lint as K
from shortbuild import GuardError, validate


def findings(row, code):
    return [lv for lv, c, _ in L.lint(row)["issues"] if c == code]


def row(**extra):
    return {"id": "audio-fixture", "lane": "long", "series": "bud",
            "script": ["Ông đứng bên cửa,", "Rồi ông quay về."], **extra}


def test_lint_comma_legacy_warns_and_pause_ctx_blocks():
    assert findings(row(), "cau_tron") == [L.WARN]
    assert findings(row(pause_ctx=True), "cau_tron") == [L.ERROR]
    assert findings(row(tts={"pause_ctx": True}), "cau_tron") == [L.ERROR]


@pytest.mark.parametrize("field", ["day", "publish_at", "effective_date"])
def test_lint_comma_merge_cutoff_uses_existing_date_fields(monkeypatch, field):
    monkeypatch.setattr(A, "AUDIO_SCRIPT_FROM", "2026-11-21")
    assert findings(row(**{field: "2026-11-20T19:00:00+07:00"}), "cau_tron") == [L.WARN]
    assert findings(row(**{field: "2026-11-21T00:00:00+07:00"}), "cau_tron") == [L.ERROR]


@pytest.mark.parametrize("text", ['Ông nói: “Chờ tôi,”', 'Ông nói: "Chờ tôi,"'])
def test_lint_comma_handles_closing_quote(text):
    assert findings(row(script=[text], pause_ctx=True), "cau_tron") == [L.ERROR]


@pytest.mark.parametrize("text", [
    "Nguồn https://example.org/kinh.", "Tra www.example.org.",
    'Ông nói "source": "note".', "Ông quay về. {pd}", "Ông đứng lại. [PAUSE]",
])
def test_lint_markup_leak_blocks_legacy_and_new(text):
    assert findings(row(script=[text]), "markup_leak") == [L.ERROR]


def test_lint_bold_and_silent_metadata_do_not_leak():
    assert findings(row(script=["Ông **quay về**."]), "markup_leak") == []
    assert findings(row(script=["[PAUSE]"], silence=[1]), "markup_leak") == []


@pytest.mark.parametrize("fmt,codes", [
    ("tra_cuu", {"tra_cuu_bang_muon", "hua_bang_cuoi"}),
    ("tuyen_tap", {"tuyen_tap_truyen1_muon", "tuyen_tap_ly_thuyet_truoc_truyen1"}),
])
def test_lint_editorial_lookup_and_collection_are_warnings(fmt, codes):
    script = (["**Dẫn nhập**"] + ["Người kể chuyện chờ ở cửa sân trong buổi sáng hôm ấy." for _ in range(30)]
              + ["**Truyện thứ nhất**", "Cuối video sẽ có bảng tra cho bạn."])
    found = [(lv, c) for lv, c, _ in L.lint(row(format=fmt, script=script))["issues"] if c in codes]
    assert {c for _, c in found} == codes
    # Lead 17/11: bảng tra ≤45s (PO 05/11) đo tất định -> vẫn LỖI; phần còn lại chỉ cảnh báo
    assert all(lv == (L.ERROR if c == "tra_cuu_bang_muon" else L.WARN) for lv, c in found)


def test_lint_cta_over_two_warns_and_night_is_separate():
    r = row(script=["Hãy đăng ký kênh."] * 3)
    assert findings(r, "cta_nhieu") == [L.WARN]
    assert not any(c == "cta_nhieu" for _, c, _ in L.lint(r, kind="night")["issues"])


def test_retention_counts_spoken_years_and_is_advisory():
    r = row(script=["Tuổi Tý gồm những người sinh năm âm lịch 1960, 1972, 1984, 1996, 2008 và 2020."])
    assert L.tokens(r["script"][0]) < 35 < L.syllables(r["script"][0])
    assert not any("câu nói" in x for x in H.retention_issues(r))   # PO 17/11: không đo độ dài câu


@pytest.mark.parametrize("extra", [{}, {"kind": "night"}, {"format": "tra_cuu"}])
def test_retention_no_short_sentence_quota_for_night_or_lookup(extra):
    r = row(script=["Người kể chuyện đứng bên cánh cửa và nhìn ra sân."] * 4, **extra)
    assert not any("câu ngắn <= 6" in x for x in H.retention_issues(r))


def test_hook_abstract_is_advice_and_existing_frame_gate_stays():
    assert K.blocking_flags(["TRUU_TUONG", "KHONG_DANH_TU_CU_THE"]) == []
    assert K.blocking_flags(["KHUNG_DAU_TRONG"]) == ["KHUNG_DAU_TRONG"]


def short(**extra):
    return {"id": "lookup-12s", "series": "fs", "day": "2026-12-01", "lane": "lookup",
            "style": "board", "audio_profile": A.SHORT_WIN_PROFILE,
            "dur": 12, "duration_band": [9, 18], "novelty_ok": "fixture",
            "script": ["Theo truyền thống, bạn tra năm sinh ở bảng này.", "Bạn có thể lưu lại để tham khảo."], **extra}


def test_script_lookup_twelve_seconds_passes_without_v2_token_floor(monkeypatch):
    import studio
    monkeypatch.setattr(studio, "hook_errors", lambda r: pytest.fail("story hook must not apply to lookup profile"))
    r = short()
    assert H.short_v2_warnings(r) == []
    validate([r])
    # Direct HBR API also resolves daytable, rather than relying on the guard exemption.
    assert A.short_audio_profile(short(style="daytable", audio_profile="short_v2")) == A.SHORT_WIN_PROFILE
    assert H.short_v2_warnings(short(style="daytable", audio_profile="short_v2")) == []


def test_script_v2_and_tone_are_advisory_but_still_reported():
    r = short(audio_profile="short_v2", title="Một câu chuyện chấn động", script=["Mở đầu.", "Được gọi là một câu chuyện."])
    assert H.short_v2_issues(r) == H.short_tone_issues(r) == []
    assert H.short_v2_warnings(r) and H.short_tone_warnings(r)
    assert H.short_tone_warnings(short(title="Phát tài lớn theo tử vi truyền thống, để tham khảo")) == []


def test_script_source_hedge_is_advisory_for_story():
    r = short(lane="truyen", script=["Theo kinh, ông quay về.", "Chú giải kể ông đứng bên cửa."])
    assert H.short_story_issues(r) == []
    assert H.short_source_warnings(r)
    validate([r])


@pytest.mark.parametrize("extra", [{}, {"day": "", "publish_at": "2026-12-01T10:00:00Z"}, {"day": ""}])
def test_script_short_comma_gate_keeps_date_scope(extra):
    r = short(script=['Ông nói: “Chờ tôi,”'], **extra)
    assert H.short_story_issues(r)
    r["day"], r["publish_at"] = "2026-11-28", ""
    assert H.short_story_issues(r) == []


@pytest.mark.parametrize("script,match", [
    (["Tra https://example.org."], "integrity"),
    (["Ông bước qua cửa sân.", "Ông bước qua cửa sân."], "lặp nguyên văn"),
    (["Tý Sửu Dần Mão cùng xuất hiện."], "crowded_chi"),
    (["Người tuổi Lợn quay về."], "zodiac_naming"),
])
def test_script_profile_retains_deterministic_guards(script, match):
    with pytest.raises(GuardError, match=match):
        validate([short(script=script)])


def test_script_bud_profile_keeps_source_requirement():
    with pytest.raises(GuardError, match="source"):
        validate([short(series="bud")])
