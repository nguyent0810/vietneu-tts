"""G3 (Video Generation remediation) -- test the fix for CL (Hình Sự)
Long-form visual generation collapse: 34/36 image beats in a real episode
(output/long/Hình Sự/EP001/shot_list_final.json) were forced onto the SAME
1 static symbol_library asset because 9 GENERIC legal-vocabulary aliases
("hình phạt", "phạm tội", "bản án"...) were mixed into
phap_luat_can_can_cong_ly's real-person-name safety-trigger alias list --
almost every sentence of crime-documentary narration matches one of those
generic terms.

Fix: the 2 compounding root causes are fixed INDEPENDENTLY --
1. Generic legal terms moved OUT of symbol_library aliases into a new
   domain-level `video_unsafe_terms` list (domain_creative_profiles.json) +
   `is_video_unsafe_topic()` (domain_creative_profiles.py) -- beats matching
   these are excluded from Treatment.VIDEO selection ONLY (preserving the
   original, still-valid reason this existed: avoid Pexels catalog bias for
   generic legal topics), but are NO LONGER forced onto the static symbol
   asset -- they proceed through normal IMAGE/TYPOGRAPHY ratio-based
   classification, generating fresh per-beat visuals via ComfyUI.
2. symbol_library's `aliases` for phap_luat_can_can_cong_ly/phap_luat_toa_an
   now contain ONLY real-person-name safety triggers (unchanged behavior
   for those -- see test_cl_real_person_safety.py, all 12 tests there still
   pass unmodified).

Does NOT publish or overwrite the real episode -- reads
output/long/Hình Sự/EP001/shot_list_final.json READ-ONLY as a regression
fixture, never writes to it."""
import json
from pathlib import Path
from unittest.mock import patch

import domain_creative_profiles as cp
from creative_director import Beat, Treatment, _build_shot_list_by_ratio

REAL_HINH_SU_SHOT_LIST = Path(__file__).parent / "output" / "long" / "Hình Sự" / "EP001" / "shot_list_final.json"


# ─── is_video_unsafe_topic() / resolve_symbol() config correctness ──────

def test_generic_legal_terms_no_longer_resolve_to_static_symbol():
    profile = cp.load_profile("CL")
    generic_sentences = [
        "toà tuyên án hai mươi năm tù giam cho bị cáo",
        "mức án này bị coi là quá nhẹ so với hành vi phạm tội",
        "sau thời gian thử thách, bị cáo được hưởng án treo",
        "hình phạt cao nhất cho tội danh này là tử hình",
    ]
    for text in generic_sentences:
        assert cp.resolve_symbol(profile, text) is None, f"generic legal text must NOT force the static symbol: {text!r}"


def test_generic_legal_terms_are_flagged_video_unsafe():
    profile = cp.load_profile("CL")
    generic_sentences = [
        "toà tuyên án hai mươi năm tù giam cho bị cáo",
        "mức án này bị coi là quá nhẹ so với hành vi phạm tội",
        "sau thời gian thử thách, bị cáo được hưởng án treo",
        "hình phạt cao nhất cho tội danh này là tử hình",
        "phiên tòa diễn ra trong ba ngày liên tiếp",
    ]
    for text in generic_sentences:
        assert cp.is_video_unsafe_topic(profile, text), f"generic legal text must still be excluded from VIDEO: {text!r}"


def test_real_person_names_still_resolve_to_static_symbol_unchanged():
    """Regression: bug fix KHÔNG được làm yếu cơ chế chặn an toàn tên
    người thật -- xem thêm test_cl_real_person_safety.py (12 test, không
    đổi 1 dòng nào, vẫn PASS sau bản vá này)."""
    profile = cp.load_profile("CL")
    entry = cp.resolve_symbol(profile, "người gây án tên là lê văn luyện, sinh năm 1993")
    assert entry is not None
    assert entry["key"] == "phap_luat_can_can_cong_ly"

    entry2 = cp.resolve_symbol(profile, "vậy, simpson có tội hay không có tội?")
    assert entry2 is not None
    assert entry2["key"] == "phap_luat_can_can_cong_ly"


def test_video_unsafe_terms_only_configured_for_cl():
    for domain_id in ("BUD", "FS"):
        profile = cp.load_profile(domain_id)
        assert not cp.is_video_unsafe_topic(profile, "hình phạt tù giam"), (
            f"video_unsafe_terms is CL-specific, must not leak into {domain_id}"
        )


def test_non_legal_text_is_neither_symbol_nor_video_unsafe():
    profile = cp.load_profile("CL")
    text = "buổi sáng hôm đó trời mưa rất to ở khu vực trung tâm thành phố"
    assert cp.resolve_symbol(profile, text) is None
    assert not cp.is_video_unsafe_topic(profile, text)


# ─── real-data regression fixture (read-only, never overwrites) ────────

def test_real_hinh_su_episode_no_longer_collapses_to_one_static_image():
    """G3's own required regression fixture: re-check the REAL beat text
    from the episode that exhibited the actual 34/36 collapse (audit
    finding) against the FIXED resolve_symbol() -- confirm the collapse is
    gone. Skips gracefully if the fixture file isn't present (e.g. a
    checkout without this specific production episode)."""
    if not REAL_HINH_SU_SHOT_LIST.exists():
        import pytest
        pytest.skip(f"real fixture not present: {REAL_HINH_SU_SHOT_LIST}")

    data = json.loads(REAL_HINH_SU_SHOT_LIST.read_text(encoding="utf-8"))
    beats = data["beats"]
    profile = cp.load_profile("CL")

    original_symbol_beats = [b for b in beats if b.get("symbol_key")]
    assert len(original_symbol_beats) == 36, (
        "sanity check on the fixture itself -- if this changes, the fixture file changed underneath us"
    )

    still_forced_to_symbol = 0
    for b in beats:
        text = b.get("text") or b.get("content_hint") or ""
        if cp.resolve_symbol(profile, text) is not None:
            still_forced_to_symbol += 1

    assert still_forced_to_symbol < 10, (
        f"expected the fix to reduce the forced-symbol count from 36 to a small number of genuine "
        f"real-name mentions, got {still_forced_to_symbol} -- collapse may not be fixed"
    )
    assert still_forced_to_symbol < len(beats) * 0.5, "must not still be a majority collapse"


# ─── end-to-end classification test (mocked scoring, real classification logic) ─

CL_TREATMENT_RATIO = {"video": 0.6, "image": 0.2, "typography": 0.2}


def _sentence(start, text):
    return {"start": start, "end": start + 5.0, "text": text}


def _make_cl_sentences():
    """20 câu mô phỏng ĐÚNG cấu trúc gây bug thật: 2 câu nhắc tên người
    thật (PHẢI vẫn về symbol), 12 câu chủ đề pháp lý CHUNG CHUNG (PHẢI
    không VIDEO nhưng KHÔNG collapse về symbol), 6 câu hoàn toàn không liên
    quan pháp lý (đối chứng, không bị ảnh hưởng bởi bản vá này)."""
    sentences = []
    t = 0.0
    for i in range(2):
        sentences.append(_sentence(t, f"câu số {i} nhắc tên lê văn luyện là người gây án"))
        t += 5.0
    for i in range(12):
        sentences.append(_sentence(t, f"câu số {i} nói về mức án và hình phạt cho hành vi phạm tội"))
        t += 5.0
    for i in range(6):
        sentences.append(_sentence(t, f"câu số {i} mô tả khung cảnh thành phố về đêm yên tĩnh"))
        t += 5.0
    return sentences


def test_build_shot_list_by_ratio_no_longer_collapses_for_cl_pattern(tmp_path):
    """Test tích hợp CHÍNH của G3: dựng 1 tập hợp câu MÔ PHỎNG đúng cấu
    trúc gây bug thật (nhiều câu chủ đề pháp lý chung chung + vài câu tên
    người thật), chạy qua ĐÚNG hàm phân loại thật (_build_shot_list_by_ratio,
    không mock phần logic loại trừ video-unsafe), chỉ mock các lệnh gọi agy/
    Gemini bên ngoài (batch_score_*/batch_translate_*) để tất định. Xác
    nhận: (a) 2 câu tên người thật vẫn về đúng symbol, (b) 12 câu pháp lý
    chung chung KHÔNG bị collapse về symbol (bug cũ) VÀ không bị chọn
    Treatment.VIDEO (mục đích gốc), (c) tổng thể KHÔNG collapse -- có nhiều
    beat IMAGE khác biệt (không phải toàn bộ đều là 1 symbol_key)."""
    sentences = _make_cl_sentences()
    profile = cp.load_profile("CL")

    def fake_typo_scores(beats, core_insight):
        return {i: 0.1 for i in range(len(beats))}  # never favored for typography, keep test focused on video/image

    def fake_video_scores(beats, bible):
        # score by index so ranking is deterministic; real suitability content doesn't matter for this test
        return {i: 1.0 - (i * 0.001) for i in range(len(beats))}

    def fake_visual_hints(beats, bible, context_label=""):
        return {i: f"hint {i}" for i in range(len(beats))}

    def fake_video_keywords(beats):
        return {i: f"keyword {i}" for i in range(len(beats))}

    with patch("creative_director.batch_score_typography_suitability", side_effect=fake_typo_scores), \
         patch("creative_director.batch_score_video_suitability", side_effect=fake_video_scores), \
         patch("creative_director.batch_translate_visual_hints", side_effect=fake_visual_hints), \
         patch("creative_director.batch_translate_video_keywords", side_effect=fake_video_keywords):
        beats = _build_shot_list_by_ratio(
            sentences, 5.0, CL_TREATMENT_RATIO, "", "", {}, ["static"],
            str(tmp_path / "test_shot_list_output.json"), profile=profile,
        )

    # group_segments_into_beats() may merge adjacent short sentences toward
    # target_beat_sec -- don't assert an exact beat COUNT (fewer beats than
    # input sentences is a normal grouping outcome, not a bug in this fix);
    # instead assert on which SENTENCES' text ends up in which kind of beat.
    all_beat_text = " ".join(b.text for b in beats)
    for i in range(2):
        assert f"câu số {i} nhắc tên lê văn luyện" in all_beat_text, "no sentence must be dropped by grouping"
    for i in range(12):
        assert f"câu số {i} nói về mức án" in all_beat_text, "no sentence must be dropped by grouping"

    real_name_beats = [b for b in beats if "lê văn luyện" in b.text]
    assert len(real_name_beats) >= 1
    for b in real_name_beats:
        assert b.symbol_key == "phap_luat_can_can_cong_ly", "real-person-name beats must still resolve to the safety symbol"
        assert b.treatment == "image"

    generic_legal_beats = [b for b in beats if "hình phạt" in b.text]
    assert len(generic_legal_beats) >= 1
    for b in generic_legal_beats:
        assert b.symbol_key is None, (
            f"generic legal-topic beat must NOT collapse to the static symbol (the actual G3 bug): {b.text!r}"
        )
        assert b.treatment != "video", (
            f"generic legal-topic beat must still be excluded from VIDEO (original Pexels-bias-avoidance intent): {b.text!r}"
        )

    # No collapse: every generic-legal beat must land on a REAL per-beat
    # classification outcome (IMAGE or TYPOGRAPHY, never a shared symbol_key)
    # -- not just "not video" (Codex review round 1 finding #3: the previous
    # `assert len(generic_treatments) >= 1` here was tautological, since
    # `generic_legal_beats` was already asserted non-empty two lines above,
    # so its treatment set is trivially >= 1 by construction and proves
    # nothing about diversity).
    generic_treatments = {b.treatment for b in generic_legal_beats}
    assert generic_treatments <= {"image", "typography"}, (
        f"generic legal-topic beats must only ever land on IMAGE or TYPOGRAPHY "
        f"(never VIDEO, never a hardcoded symbol asset), got {generic_treatments!r}"
    )
    assert all(b.symbol_key is None for b in generic_legal_beats)

    unrelated_beats = [b for b in beats if "thành phố" in b.text]
    assert len(unrelated_beats) >= 1
    # unrelated beats ARE eligible for video (unaffected by this fix) -- at
    # least some should land on video given the 60% ratio and no exclusion.
    assert any(b.treatment == "video" for b in unrelated_beats + generic_legal_beats) or any(
        b.treatment == "video" for b in beats
    ), "the video quota must still be fulfillable from eligible (non-legal-topic) beats -- ratio isn't silently zeroed out"


# ─── real-data end-to-end classification (Codex review round 1 finding #2) ──
#
# The two tests above (`test_real_hinh_su_episode_no_longer_collapses_to_
# one_static_image`, resolve_symbol()-only re-check; and
# `test_build_shot_list_by_ratio_no_longer_collapses_for_cl_pattern`, real
# classification but SYNTHETIC sentences) each cover half of the real
# end-to-end guarantee but not both halves together. This test closes that
# gap: it feeds the REAL episode's beat text through the REAL
# `_build_shot_list_by_ratio()` classification function (only the external
# agy/Gemini scoring calls are mocked, same as the synthetic test above --
# the exclusion logic itself is never mocked).

def test_real_hinh_su_episode_through_real_classification_never_selects_video_for_unsafe_beats():
    """Codex review round 1 finding #2: re-run the REAL episode's beat text
    through the REAL `_build_shot_list_by_ratio()` (not just a re-check of
    resolve_symbol() against static fixture data) -- confirms end-to-end
    that (a) the forced-static-symbol count is still small (not a 36-beat
    collapse) and (b) NO beat whose real text matches video_unsafe_terms
    ever comes out the other end classified as Treatment.VIDEO."""
    if not REAL_HINH_SU_SHOT_LIST.exists():
        import pytest
        pytest.skip(f"real fixture not present: {REAL_HINH_SU_SHOT_LIST}")

    data = json.loads(REAL_HINH_SU_SHOT_LIST.read_text(encoding="utf-8"))
    real_beats = data["beats"]
    profile = cp.load_profile("CL")

    # Real beat dicts already have start/end/text -- exactly the shape
    # `_build_shot_list_by_ratio()`'s `sentences` argument expects (it calls
    # group_segments_into_beats(sentences, ...) directly on this shape).
    sentences = [{"start": b["start"], "end": b["end"], "text": b["text"]} for b in real_beats]

    def fake_typo_scores(beats, core_insight):
        return {i: 0.1 for i in range(len(beats))}

    def fake_video_scores(beats, bible):
        return {i: 1.0 - (i * 0.001) for i in range(len(beats))}

    def fake_visual_hints(beats, bible, context_label=""):
        return {i: f"hint {i}" for i in range(len(beats))}

    def fake_video_keywords(beats):
        return {i: f"keyword {i}" for i in range(len(beats))}

    with patch("creative_director.batch_score_typography_suitability", side_effect=fake_typo_scores), \
         patch("creative_director.batch_score_video_suitability", side_effect=fake_video_scores), \
         patch("creative_director.batch_translate_visual_hints", side_effect=fake_visual_hints), \
         patch("creative_director.batch_translate_video_keywords", side_effect=fake_video_keywords):
        classified_beats = _build_shot_list_by_ratio(
            sentences, 20.0, CL_TREATMENT_RATIO, "", "", {}, ["static"],
            str(Path(__file__).parent / "_test_scratch_real_cl_shot_list.json"), profile=profile,
        )

    forced_to_symbol = [b for b in classified_beats if b.symbol_key is not None]
    assert len(forced_to_symbol) < 10, (
        f"real episode re-classified end-to-end must not collapse back to a small handful of "
        f"forced-symbol beats being the majority -- got {len(forced_to_symbol)}/{len(classified_beats)}"
    )

    unsafe_but_classified_video = [
        b for b in classified_beats
        if b.treatment == "video" and cp.is_video_unsafe_topic(profile, b.text)
    ]
    assert unsafe_but_classified_video == [], (
        f"beats matching video_unsafe_terms must NEVER come out of real end-to-end classification "
        f"as Treatment.VIDEO: {[b.text for b in unsafe_but_classified_video]!r}"
    )

    # cleanup the scratch output this test writes (Beat classification writes
    # its shot-list JSON as a side effect; never touches the real fixture).
    scratch = Path(__file__).parent / "_test_scratch_real_cl_shot_list.json"
    if scratch.exists():
        scratch.unlink()


# ─── non-ratio branch coverage (Codex review round 1 finding #1) ───────────

def test_build_shot_list_non_ratio_branch_also_excludes_video_unsafe_beats(tmp_path):
    """Codex review round 1 finding #1 (real bug): `build_shot_list()` has
    TWO branches -- the fixed-ratio branch (`_build_shot_list_by_ratio()`,
    used by long_batch_runner.py for the real automated pipeline, covered by
    the tests above) and a separate non-ratio branch (`treatment_ratio=None`
    -- reachable e.g. by invoking creative_director.py's own CLI directly
    without --video-ratio/--image-ratio/--typography-ratio, a supported
    path). Before this fix, `is_video_unsafe_topic()` was ONLY checked in
    the ratio branch -- a CL beat matching video_unsafe_terms could still
    be classified Treatment.VIDEO via classify_beat_rule_based()'s
    `not has_imagery and video_eligible` rule in the non-ratio branch. This
    test forces video_eligible=True for every beat (worst case) and
    confirms the guard added to build_shot_list()'s grouped-beat loop
    downgrades any video_unsafe_terms beat away from VIDEO regardless."""
    from creative_director import build_shot_list

    segments = [{
        "start": 0.0, "end": 8.0,
        "text": "sau thời gian thử thách, bị cáo được hưởng án treo tại nhà riêng theo quy định của tòa án",
    }]
    segments_json = tmp_path / "segments.json"
    segments_json.write_text(json.dumps({"segments": segments}, ensure_ascii=False), encoding="utf-8")
    output_path = tmp_path / "shot_list_out.json"

    profile = cp.load_profile("CL")

    def fake_video_eligibility(beats, pexels_hints, context_label=""):
        return set(range(len(beats)))  # force video_eligible=True for every beat -- worst case for the guard

    def fake_visual_hints(beats, bible, context_label=""):
        return {i: f"hint {i}" for i in range(len(beats))}

    def fake_video_keywords(beats):
        return {i: f"keyword {i}" for i in range(len(beats))}

    with patch("creative_director.batch_judge_video_eligibility", side_effect=fake_video_eligibility), \
         patch("creative_director.batch_translate_visual_hints", side_effect=fake_visual_hints), \
         patch("creative_director.batch_translate_video_keywords", side_effect=fake_video_keywords):
        beats = build_shot_list(
            str(segments_json), str(output_path), episode_planner_path=None,
            gemini_api_key=None, bible={}, treatment_ratio=None, creative_profile=profile,
        )

    unsafe_beats = [b for b in beats if cp.is_video_unsafe_topic(profile, b.text)]
    assert len(unsafe_beats) >= 1, "sanity: fixture sentence must actually match video_unsafe_terms"
    for b in unsafe_beats:
        assert b.treatment != "video", (
            f"video_unsafe_terms beat must never reach Treatment.VIDEO via the NON-ratio "
            f"classification branch either (Codex review round 1 finding #1): {b.text!r} -> {b.treatment}"
        )
