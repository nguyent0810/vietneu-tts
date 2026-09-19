"""Audit kênh Hình Sự (2026-08-14) -- EP001 THẬT đo được editing_rhythm =
{"target_beat_sec": 18, "pacing_notes": "chậm rãi chiêm nghiệm... tuyệt đối
không dựng nhanh"} do LLM tự chọn khi sinh Director Bible, dù đây là nội
dung điều tra hình sự chứ không phải suy ngẫm tâm linh -- nguyên nhân là
`_BIBLE_PROMPT_TEMPLATE` trước đây KHÔNG có bất kỳ hướng dẫn nào phân biệt
nhịp dựng theo thể loại/domain (chỉ có genre_label chung chung), nên LLM mặc
định thiên về nhịp chậm giống phần lớn nội dung BUD đã sinh trước đó. Trung
bình 70 beat của EP001 dài 22.8s/beat (18-33s), quá chậm cho thể loại này.

Fixed: thêm field `pacing_guidance` theo domain trong
`domain_creative_profiles.json`, nối vào `_BIBLE_PROMPT_TEMPLATE` qua
`build_director_bible()` -- CL được hướng dẫn tường minh dùng nhịp NHANH
(10-15s/beat), BUD/FS giữ nguyên hành vi chậm/vừa đã có từ trước."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import director_bible
import domain_creative_profiles as creative_profiles


def _render_prompt(domain_id: str) -> str:
    profile = creative_profiles.load_profile(domain_id)
    return director_bible._BIBLE_PROMPT_TEMPLATE.format(
        genre_label=profile.get("bible_genre_label"),
        planner="(test)", brief="(test)", script="(test)", registry="(test)",
        pacing_guidance=profile.get("pacing_guidance"),
    )


def test_all_three_domains_have_pacing_guidance_configured():
    for domain_id in ("BUD", "FS", "CL"):
        profile = creative_profiles.load_profile(domain_id)
        assert profile.get("pacing_guidance"), f"{domain_id} thiếu pacing_guidance"


def test_cl_prompt_instructs_fast_pacing_not_contemplative():
    prompt = _render_prompt("CL")
    assert "target_beat_sec" in prompt.split("=== NHỊP DỰNG")[1]
    assert "ngưỡng THẤP" in prompt or "NHANH" in prompt
    # Must NOT carry over BUD's contemplative wording into CL's section specifically.
    cl_section = prompt.split("=== NHỊP DỰNG")[1]
    assert "chiêm nghiệm" not in cl_section.split("Trả về CHỈ")[0] or "KHÔNG" in cl_section


def test_bud_prompt_keeps_contemplative_pacing_unchanged():
    prompt = _render_prompt("BUD")
    cl_section = prompt.split("=== NHỊP DỰNG")[1]
    assert "CHẬM" in cl_section and "chiêm nghiệm" in cl_section


def test_fs_prompt_uses_moderate_pacing():
    prompt = _render_prompt("FS")
    cl_section = prompt.split("=== NHỊP DỰNG")[1]
    assert "VỪA PHẢI" in cl_section


def test_prompt_template_still_requires_all_bible_keys():
    """Regression guard: adding the new placeholder must not break the
    existing required-key contract build_director_bible() validates
    against."""
    prompt = _render_prompt("CL")
    for key in ("creative_vision", "emotion_curve", "color_palette", "camera_language",
                "editing_rhythm", "typography_policy", "image_policy", "ai_video_policy",
                "pexels_acceptance_policy", "transition_style", "consistency_rules"):
        assert f'"{key}"' in prompt


def test_default_bible_itself_stays_bud_flavored():
    """DEFAULT_BIBLE (the raw constant) is documented as BUD-appropriate --
    out of scope to change here; only the override applied inside
    build_director_bible()'s fallback branch (tested below) must vary by
    domain."""
    bud_rhythm = director_bible.DEFAULT_BIBLE["editing_rhythm"]
    assert bud_rhythm["target_beat_sec"] == 20
    assert "chậm" in bud_rhythm["pacing_notes"]


def test_fallback_branch_actually_returns_domain_specific_pacing_for_cl(monkeypatch, tmp_path):
    """Round-2 Cursor review finding: the previous test only asserted on
    the DEFAULT_BIBLE constant, never exercised the actual fallback branch
    inside build_director_bible() (Gemini + agy both unavailable). This
    calls it for real with domain_id="CL" and confirms target_beat_sec
    lands in CL's 10-15s range, not the blanket 16s the first version of
    this fix used (16 is FS-ish, not CL-appropriate)."""
    monkeypatch.setattr(director_bible, "DIRECTOR_BIBLE_CACHE_DIR", tmp_path)
    monkeypatch.setattr(director_bible, "_call_gemini_api", lambda *a, **k: None)
    monkeypatch.setattr(director_bible, "_call_agy", lambda *a, **k: None)

    bible = director_bible.build_director_bible(
        "EP_TEST", creative_profile=creative_profiles.load_profile("CL"),
        domain_id="CL", gemini_api_key=None,
    )
    assert 10 <= bible["editing_rhythm"]["target_beat_sec"] <= 15
    # pacing_notes legitimately MENTIONS "chiêm nghiệm" while explicitly
    # disclaiming it ("KHÔNG áp nhịp chiêm nghiệm...") -- the real contract
    # is the numeric target above, not the wording.
    assert "KHÔNG áp nhịp chiêm nghiệm" in bible["editing_rhythm"]["pacing_notes"]


def test_bible_schema_no_longer_hard_excludes_10_to_13():
    """Round-2 Cursor review finding (main blocker): the JSON schema shown
    to the LLM said target_beat_sec must be <14-30>, directly contradicting
    CL's guidance to aim for 10-15 -- an LLM prioritizing schema over prose
    would never actually pick 10-13. Confirms the schema range was widened
    and no longer says "<14-30>"."""
    prompt = _render_prompt("CL")
    assert "<14-30>" not in prompt
    assert "10-30" in prompt or "10, 30" in prompt
