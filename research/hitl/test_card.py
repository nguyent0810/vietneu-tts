import json

import pytest

from research.hitl.card import record_decision, render_card, verify_decision


def sample(tmp_path):
    path = tmp_path / "candidates.json"
    data = {"video_id": "vid1", "channel": "MIM", "planned_publish_date": "2026-12-01",
            "candidates": [{"candidate_id": f"c{i}", "title": f"Title {i}", "thumbnail_text": f"Thumb {i}",
                            "first_frame_0_1s": "frame", "voice_0_3s": "voice", "escalation_3_10s": "rise",
                            "payoff": "answer", "why_this_angle": "reason"} for i in range(3)]}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path, data


def test_render_three_candidates_and_failed_review(tmp_path):
    candidates, _ = sample(tmp_path)
    review = tmp_path / "review.json"
    # Định dạng reviewer v2 (#127).
    review.write_text(json.dumps({"review_status": "review_failed", "failure_reason": "timeout", "sources_missing": True,
                                  "candidates": [{"candidate_id": "c1", "flags": [{"code": "F2", "severity": "high",
                                                  "explanation": "Check claim", "quote_from_package": "quote"}]}]}))
    out = render_card(candidates, review, tmp_path / "card.html").read_text()
    assert all(f"c{i}" in out for i in range(3))
    assert "review_failed" in out and "timeout" in out and "sources_missing" in out
    assert "168px" in out and "đã xác minh" not in out


def test_bad_json_renders_error_card(tmp_path):
    broken = tmp_path / "broken.json"; broken.write_text("{")
    result = render_card(broken, None, tmp_path / "bad.html").read_text()
    assert "Không đọc được candidates.json" in result
    assert verify_decision(broken, tmp_path / "missing.json") == "invalid"


def test_markdown_escapes_untrusted_content(tmp_path):
    candidates, data = sample(tmp_path)
    data["channel"] = "evil\n## injected | [link](x)"
    data["candidates"][0]["title"] = "title\n# forged"
    candidates.write_text(json.dumps(data), encoding="utf-8")
    output = render_card(candidates, None, tmp_path / "card.md").read_text()
    assert "evil<br>\\#\\# injected \\| \\[link\\](x)" in output
    assert "title<br>\\# forged" in output


def test_approve_requires_candidate(tmp_path):
    candidates, _ = sample(tmp_path)
    with pytest.raises(ValueError, match="candidate_id"):
        record_decision(candidates, "APPROVE", reviewer="r")


def test_edit_after_approval_is_stale(tmp_path):
    candidates, data = sample(tmp_path)
    decision = record_decision(candidates, "APPROVE", "c0", reviewer="r", history_dir=tmp_path / "history")
    dec_path = tmp_path / "decision.json"; dec_path.write_text(json.dumps(decision))
    data["candidates"][0]["title"] = "Changed"
    candidates.write_text(json.dumps(data))
    assert verify_decision(candidates, dec_path) == "stale"


def test_tampered_decision_edits_are_stale(tmp_path):
    candidates, _ = sample(tmp_path)
    decision = record_decision(candidates, "APPROVE", "c0", edits={"title": "Edited title"},
                               reviewer="r", history_dir=tmp_path / "history")
    dec_path = tmp_path / "decision.json"
    dec_path.write_text(json.dumps(decision), encoding="utf-8")
    assert verify_decision(candidates, dec_path) == "ok"
    decision["edits"]["title"] = "Different title"
    dec_path.write_text(json.dumps(decision), encoding="utf-8")
    assert verify_decision(candidates, dec_path) == "stale"


@pytest.mark.parametrize("action,note", [("REQUEST_CHANGES", "need edit"), ("REJECT", "bad")])
def test_non_approve_never_ok(tmp_path, action, note):
    candidates, _ = sample(tmp_path)
    decision = record_decision(candidates, action, note=note, reviewer="r", history_dir=tmp_path / action)
    dec_path = tmp_path / f"{action}.json"; dec_path.write_text(json.dumps(decision))
    assert verify_decision(candidates, dec_path) == "not_approved"


def test_versions_increase_and_history_is_append_only(tmp_path):
    candidates, data = sample(tmp_path)
    hist = tmp_path / "decisions"
    first = record_decision(candidates, "APPROVE", "c0", reviewer="r", history_dir=hist)
    data["candidates"][0]["title"] = "Changed"
    candidates.write_text(json.dumps(data))
    second = record_decision(candidates, "APPROVE", "c0", reviewer="r", history_dir=hist)
    assert (first["content_version"], second["content_version"]) == (1, 2)
    assert (hist / "v1.json").exists() and (hist / "v2.json").exists()
    assert json.loads((hist / "v1.json").read_text())["content_sha256"] == first["content_sha256"]


def test_version_tracks_candidate_content_not_decisions(tmp_path):
    candidates, data = sample(tmp_path)
    hist = tmp_path / "decisions"
    first = record_decision(candidates, "APPROVE", "c0", reviewer="r", history_dir=hist)
    second = record_decision(candidates, "APPROVE", "c1", reviewer="r", history_dir=hist)
    assert first["content_version"] == second["content_version"] == 1
    assert len(list(hist.glob("v*.json"))) == 2
    data["candidates"][0]["title"] = "Changed"
    candidates.write_text(json.dumps(data))
    third = record_decision(candidates, "APPROVE", "c0", reviewer="r", history_dir=hist)
    assert third["content_version"] == 2



def _write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8"); return p


def test_card_reads_reviewer_v2_flags_and_never_hides_missing_results(tmp_path):
    # Hợp đồng ghép nối với reviewer #127: review_status + candidates[].flags + evidence.
    from research.hitl.card import render_card
    cands = _write(tmp_path / "c.json", {"video_id": "v1", "channel": "vsd", "publish_date": "2026-11-20",
        "candidates": [{"candidate_id": "c1", "title": "A"}, {"candidate_id": "c2", "title": "B"}, {"candidate_id": "c3", "title": "C"}]})
    review = _write(tmp_path / "r.json", {"video_id": "v1", "review_status": "ok", "sources_missing": False, "candidates": [
        {"candidate_id": "c1", "flags": [{"code": "modality_dropped", "severity": "medium", "explanation": "giả thuyết bị nói như sự thật",
                                           "quote_from_package": "đang nâng lên", "evidence": [{"source_id": "s1", "quote": "possible reason"}]}]},
        {"candidate_id": "c2", "flags": []}]})
    html_text = render_card(cands, review, tmp_path / "card.html").read_text(encoding="utf-8")
    assert "modality_dropped" in html_text and "s1" in html_text          # cờ thật được hiện
    assert "review_result_missing" in html_text                            # c3 không có kết quả → báo rõ
    bad = _write(tmp_path / "bad.json", {"flags": []})                       # định dạng lạ
    html_bad = render_card(cands, bad, tmp_path / "bad.html").read_text(encoding="utf-8")
    assert "review_format_unrecognized" in html_bad and "Không có cờ reviewer" not in html_bad


def test_markdown_card_shows_flags_and_missing_results(tmp_path):
    from research.hitl.card import render_card
    cands = _write(tmp_path / "c.json", {"video_id": "v1", "candidates": [{"candidate_id": "c1", "title": "A"}, {"candidate_id": "c2", "title": "B"}]})
    review = _write(tmp_path / "r.json", {"video_id": "v1", "review_status": "ok", "sources_missing": False, "candidates": [
        {"candidate_id": "c1", "flags": [{"code": "unsupported", "severity": "medium", "explanation": "x", "evidence": [{"source_id": "s9", "quote": "q"}]}]}]})
    md = render_card(cands, review, tmp_path / "card.md").read_text(encoding="utf-8")
    assert "unsupported" in md and "s9" in md
    assert "review_result_missing" in md and "null" not in md
