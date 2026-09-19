"""Audit kênh Hình Sự (2026-08-14) -- 2 bug thật phát hiện trong content_seo.py
khi audit thumbnail xấu/nhiều chữ của EP001 CL:

(1) Thiếu field "thumbnail_text" trong schema JSON -- thumbnail_generator.py
luôn kỳ vọng 1 tiêu đề RIÊNG rút gọn cho thumbnail, nhưng chưa từng được
sinh ra, nên long_batch_runner.py's fallback `entry["seo"].get("thumbnail_text")
or entry["seo"]["title"]` LUÔN dùng tiêu đề video ĐẦY ĐỦ (thường 10-12 từ) --
xác nhận qua chính EP001: thumbnail thật tràn 3 dòng.

(2) Prompt content_seo.py hard-code "kênh Phật giáo/tâm linh" bất kể domain
THẬT gọi nó -- module không hề nhận domain_id, nên FS/CL cũng bị gán vai
"chuyên gia SEO Phật giáo". CL EP001's output thực tế tình cờ vẫn đúng chủ
đề (LLM ưu tiên script/brief thật) nhưng đây là hành vi KHÔNG được đảm bảo."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import content_seo


def test_context_label_resolves_per_domain():
    assert content_seo._context_label_for_domain("BUD") == "Phật giáo/tâm linh"
    assert content_seo._context_label_for_domain("FS") == "Phong Thuỷ/huyền học phương Đông"
    assert content_seo._context_label_for_domain("CL") == "Hình sự/pháp lý"


def test_context_label_defaults_to_bud_for_unknown_domain():
    """Backward-compat guard: any legacy call-site that doesn't pass
    domain_id (or passes something unexpected) must keep getting the
    original BUD-flavored prompt, not crash or silently produce an empty
    label."""
    assert content_seo._context_label_for_domain("NOT_A_REAL_DOMAIN") == "Phật giáo/tâm linh"


def test_draft_prompt_uses_domain_specific_context_label_not_hardcoded_bud():
    prompt_cl = content_seo._DRAFT_PROMPT_TEMPLATE.format(
        brief="(test)", script="(test)", revision_note="",
        context_label=content_seo._context_label_for_domain("CL"),
    )
    assert "Hình sự/pháp lý" in prompt_cl
    assert "Phật giáo" not in prompt_cl


def test_draft_prompt_default_domain_preserves_original_bud_wording():
    """Regression guard: existing BUD call sites (or any caller that omits
    domain_id) must render byte-identical context wording to before this
    fix."""
    prompt_bud = content_seo._DRAFT_PROMPT_TEMPLATE.format(
        brief="(test)", script="(test)", revision_note="",
        context_label=content_seo._context_label_for_domain("BUD"),
    )
    assert "chuyên gia SEO YouTube cho kênh Phật giáo/tâm linh tiếng Việt" in prompt_bud


def test_draft_prompt_schema_includes_thumbnail_text_field():
    prompt = content_seo._DRAFT_PROMPT_TEMPLATE.format(
        brief="(test)", script="(test)", revision_note="",
        context_label="(test)",
    )
    assert '"thumbnail_text"' in prompt
    assert "6-8 từ" in prompt


def test_review_prompt_checks_thumbnail_text_too():
    prompt = content_seo._REVIEW_PROMPT_TEMPLATE.format(
        brief="(test)", draft="{}", context_label="(test)",
    )
    assert "thumbnail_text" in prompt


def test_thumbnail_text_problem_missing_field():
    assert content_seo._thumbnail_text_problem({"titles": ["a"]}) is not None


def test_thumbnail_text_problem_empty_string():
    assert content_seo._thumbnail_text_problem({"titles": ["a"], "thumbnail_text": "   "}) is not None


def test_thumbnail_text_problem_too_many_words():
    long_text = "một hai ba bốn năm sáu bảy tám chín mười mười_một"
    assert content_seo._thumbnail_text_problem({"titles": [], "thumbnail_text": long_text}) is not None


def test_thumbnail_text_problem_duplicate_of_a_title():
    title = "Bị Tình Nghi Hay Có Tội?"  # short enough to pass the word-count check on its own
    draft = {"titles": [title], "thumbnail_text": title}
    problem = content_seo._thumbnail_text_problem(draft)
    assert problem is not None
    assert "TRÙNG" in problem


def test_thumbnail_text_problem_none_for_valid_short_text():
    draft = {"titles": ["Vì Sao Kênh Không Gọi Ai Là Hung Thủ?"], "thumbnail_text": "Bị Tình Nghi Hay Có Tội?"}
    assert content_seo._thumbnail_text_problem(draft) is None


def test_generate_seo_with_review_hard_fails_before_calling_llm_review_when_thumbnail_text_missing(monkeypatch):
    """The hard programmatic check must reject a structurally-bad draft
    WITHOUT spending a review_seo_content() (Codex) call on it -- and must
    feed the specific violation back as revision_feedback so the next
    draft attempt actually knows what to fix."""
    calls = {"draft": 0, "review": 0}

    def fake_draft(brief, script, revision_feedback=None, domain_id="BUD"):
        calls["draft"] += 1
        if calls["draft"] == 1:
            return {"titles": ["Tiêu đề dài"], "description": "d", "tags": ["x"]}  # missing thumbnail_text
        assert revision_feedback and "thumbnail_text" in revision_feedback
        return {"titles": ["Tiêu đề dài"], "thumbnail_text": "Ngắn Gọn Rồi", "description": "d", "tags": ["x"]}

    def fake_review(draft, brief, domain_id="BUD"):
        calls["review"] += 1
        return {"verdict": "PASS", "feedback": ""}

    monkeypatch.setattr(content_seo, "draft_seo_content", fake_draft)
    monkeypatch.setattr(content_seo, "review_seo_content", fake_review)
    monkeypatch.setattr(content_seo, "_read_text", lambda p: "(test)")

    result = content_seo.generate_seo_with_review("brief.md", "script.md")
    assert result["passed"] is True
    assert result["iterations_used"] == 2
    assert calls["draft"] == 2
    assert calls["review"] == 1  # NOT called on iteration 1 -- hard check short-circuited it


def test_draft_seo_content_and_review_seo_content_accept_domain_id(monkeypatch):
    """Wiring guard: domain_id must actually reach the formatted prompt
    sent to the LLM call, not just exist as an unused parameter."""
    captured = {}

    def fake_run_agy(prompt):
        captured["draft_prompt"] = prompt
        return '{"titles": ["t"], "thumbnail_text": "t ngắn", "description": "d", "tags": ["x"]}'

    def fake_run_codex(prompt):
        captured["review_prompt"] = prompt
        return '{"verdict": "PASS", "feedback": ""}'

    monkeypatch.setattr(content_seo, "_run_agy", fake_run_agy)
    monkeypatch.setattr(content_seo, "_run_codex", fake_run_codex)

    content_seo.draft_seo_content("brief text", "script text", domain_id="CL")
    assert "Hình sự/pháp lý" in captured["draft_prompt"]

    content_seo.review_seo_content({"titles": ["t"]}, "brief text", domain_id="CL")
    assert "Hình sự/pháp lý" in captured["review_prompt"]
