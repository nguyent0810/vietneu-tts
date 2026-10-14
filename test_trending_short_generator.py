"""Test tự động cho trending_short_generator.py (audit 9 điểm mục #9,
MVP bán thủ công) -- trọng tâm: grounding chống hallucination (excerpt
PHẢI là substring thật của source_text), gate an toàn 2 bước draft/publish
TÁCH RIÊNG (không phụ thuộc 1 điểm lỗi phân loại mentions_real_person duy
nhất -- Codex review vòng 1, CRITICAL #1/#2), và path containment cho
output_dir_for_domain()."""
import json

import pytest

import content_categories
import trending_short_generator as tsg
from content_seo import ContentSeoError


def _fake_agy_json(payload):
    return json.dumps(payload, ensure_ascii=False)


# --- content_categories.TRENDING wiring ---

def test_trending_category_registered():
    assert content_categories.TRENDING in content_categories.CATEGORY_LABELS
    block = content_categories.category_rubric_block(content_categories.TRENDING)
    assert "mốc THỜI GIAN" in block
    assert "mentions_real_person" in block
    assert "still_developing" in block
    assert "khái niệm/thuật ngữ chuyên môn" in block  # source-only cho "góc nhìn kênh"


def test_strategy_c_is_source_only_no_background_knowledge():
    assert "TUYỆT ĐỐI KHÔNG được tự thêm giáo lý" in tsg._GENERATE_CANDIDATES_PROMPT
    assert "KHÔNG xuất hiện trong facts" in tsg._GENERATE_CANDIDATES_PROMPT


# --- output_dir_for_domain / write_short_bundle_file ---

def test_output_dir_for_domain_maps_all_3_channels(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    for domain, expected_topic in [("BUD", "Phật giáo"), ("FS", "Phong Thủy"), ("CL", "Hình Sự")]:
        out_dir = tsg.output_dir_for_domain(domain)
        assert out_dir == tmp_path / "drive_input" / "content_repo_staged" / expected_topic / "Short"


def test_output_dir_for_domain_rejects_unknown_domain():
    with pytest.raises(ContentSeoError):
        tsg.output_dir_for_domain("XX")


def test_output_dir_for_domain_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    monkeypatch.setattr(tsg, "load_domain_topics", lambda: {"BUD": "../../escaped"})
    with pytest.raises(ContentSeoError):
        tsg.output_dir_for_domain("BUD")


def test_output_dir_for_domain_rejects_absolute_path_topic(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    monkeypatch.setattr(tsg, "load_domain_topics", lambda: {"BUD": "/etc/escaped"})
    with pytest.raises(ContentSeoError):
        tsg.output_dir_for_domain("BUD")


def test_write_short_bundle_file_writes_to_correct_domain_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    out_path = tsg.write_short_bundle_file("CL", "Vu an gia", "Dòng 1\nDòng 2")
    assert out_path.exists()
    assert out_path.parent == tmp_path / "drive_input" / "content_repo_staged" / "Hình Sự" / "Short"
    assert out_path.read_text(encoding="utf-8") == "*** 1\n\nDòng 1\nDòng 2\n"


def test_write_short_bundle_file_dedups_on_collision(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    p1 = tsg.write_short_bundle_file("FS", "Cung tin", "A")
    p2 = tsg.write_short_bundle_file("FS", "Cung tin", "B")
    assert p1 != p2
    assert p1.exists() and p2.exists()


# --- extract_facts: schema strictness + grounding ---

_REAL_SOURCE = "Theo tin, cơ quan chức năng xác nhận sự việc xảy ra hôm qua tại địa phương, gây chú ý trong dư luận."


def test_extract_facts_returns_required_keys(monkeypatch):
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "cơ quan chức năng xác nhận sự việc xảy ra hôm qua",
        "summary": "Tóm tắt sự việc.",
        "mentions_real_person": False,
        "still_developing": True,
    }))
    facts = tsg.extract_facts("FS", "Phong Thủy", _REAL_SOURCE, "https://example.com/a", "2026-07-29")
    assert facts["mentions_real_person"] is False
    assert facts["still_developing"] is True
    assert facts["domain"] == "FS"
    assert facts["source_url"] == "https://example.com/a"
    assert facts["source_date"] == "2026-07-29"
    assert facts["source_text"] == _REAL_SOURCE  # nguồn gốc PHẢI được giữ nguyên cho judge đối chiếu


def test_extract_facts_raises_on_missing_key(monkeypatch):
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "cơ quan chức năng xác nhận sự việc", "summary": "...", "mentions_real_person": False,
        # thiếu "still_developing"
    }))
    with pytest.raises(ContentSeoError):
        tsg.extract_facts("BUD", "Phật giáo", _REAL_SOURCE, "https://x", "2026-07-29")


def test_extract_facts_rejects_excerpt_not_in_source(monkeypatch):
    """Codex review vòng 1, CRITICAL #1: excerpt KHÔNG khớp source_text (agy
    hallucinate lúc trích) PHẢI bị chặn bằng code, không được tin JSON hợp
    lệ là đủ."""
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "một chi tiết hoàn toàn không có trong nguồn thật",
        "summary": "Tóm tắt.", "mentions_real_person": False, "still_developing": False,
    }))
    with pytest.raises(ContentSeoError):
        tsg.extract_facts("FS", "Phong Thủy", _REAL_SOURCE, "https://x", "2026-07-29")


def test_extract_facts_accepts_excerpt_with_whitespace_differences(monkeypatch):
    """Chuẩn hoá khoảng trắng -- agy có thể đổi xuống dòng/khoảng trắng khi
    copy nhưng vẫn là excerpt THẬT -- không nên false-positive-reject."""
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "cơ quan   chức năng\nxác nhận sự việc",  # khoảng trắng/newline khác source thật
        "summary": "Tóm tắt.", "mentions_real_person": False, "still_developing": False,
    }))
    facts = tsg.extract_facts("FS", "Phong Thủy", _REAL_SOURCE, "https://x", "2026-07-29")
    assert facts["excerpt"]


@pytest.mark.parametrize("bad_value", [1, 0, "true", "false", None, "yes"])
def test_extract_facts_rejects_non_bool_mentions_real_person(monkeypatch, bad_value):
    """Codex review vòng 1: JSON có thể trả 0/1/"true" thay vì boolean thật
    -- phải bị chặn tường minh (type() is bool), không được coerce ngầm."""
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "cơ quan chức năng xác nhận sự việc",
        "summary": "...", "mentions_real_person": bad_value, "still_developing": False,
    }))
    with pytest.raises(ContentSeoError):
        tsg.extract_facts("FS", "Phong Thủy", _REAL_SOURCE, "https://x", "2026-07-29")


def test_extract_facts_rejects_non_bool_still_developing(monkeypatch):
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "cơ quan chức năng xác nhận sự việc",
        "summary": "...", "mentions_real_person": False, "still_developing": "chưa rõ",
    }))
    with pytest.raises(ContentSeoError):
        tsg.extract_facts("FS", "Phong Thủy", _REAL_SOURCE, "https://x", "2026-07-29")


def test_extract_facts_rejects_empty_excerpt(monkeypatch):
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "   ", "summary": "...", "mentions_real_person": False, "still_developing": False,
    }))
    with pytest.raises(ContentSeoError):
        tsg.extract_facts("FS", "Phong Thủy", _REAL_SOURCE, "https://x", "2026-07-29")


# --- 2-bước draft/publish TÁCH RIÊNG (Codex review vòng 1, CRITICAL #2) ---

def _mock_pipeline(monkeypatch, mentions_real_person, still_developing, hook_score=9.0, passed=True):
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "cơ quan chức năng xác nhận sự việc xảy ra hôm qua",
        "summary": "Tom tat su viec",
        "mentions_real_person": mentions_real_person, "still_developing": still_developing,
    }))
    # generate_verified_script() bên trong dùng _run_agy/_run_codex của
    # chính short_judge_panel_engine.py (import riêng) -- phải patch đúng
    # module đó, không phải reference của trending_short_generator.
    if passed:
        monkeypatch.setattr("short_judge_panel_engine._run_agy", lambda prompt: _fake_agy_json({
            "candidates": [
                {"strategy": "A", "script": "Câu 1.\nCâu 2.\nCâu 3.\nCâu 4."},
                {"strategy": "B", "script": "Câu 1 B.\nCâu 2 B.\nCâu 3 B.\nCâu 4 B."},
                {"strategy": "C", "script": "Câu 1 C.\nCâu 2 C.\nCâu 3 C.\nCâu 4 C."},
            ],
        }))
        monkeypatch.setattr("short_judge_panel_engine._run_codex", lambda prompt: _fake_agy_json({
            "fact_check": {"A": "PASS", "B": "PASS", "C": "PASS"},
            "winner": "A", "winner_script": "Câu 1.\nCâu 2.\nCâu 3.\nCâu 4.",
            "hook_score": hook_score, "feedback": "tốt",
        }))
    else:
        monkeypatch.setattr("short_judge_panel_engine._run_agy", lambda prompt: _fake_agy_json({
            "candidates": [
                {"strategy": "A", "script": "X.\nY.\nZ.\nW."},
                {"strategy": "B", "script": "X2.\nY2.\nZ2.\nW2."},
                {"strategy": "C", "script": "X3.\nY3.\nZ3.\nW3."},
            ],
        }))
        monkeypatch.setattr("short_judge_panel_engine._run_codex", lambda prompt: _fake_agy_json({
            "fact_check": {"A": "FAIL: bịa chi tiết", "B": "FAIL: bịa chi tiết", "C": "FAIL: bịa chi tiết"},
            "winner": "NONE", "winner_script": "", "hook_score": 0, "feedback": "không đạt",
        }))


def test_draft_never_writes_bundle_even_when_passed_and_no_real_person(tmp_path, monkeypatch):
    """Bất biến cốt lõi sau khi sửa: bước `draft` KHÔNG BAO GIỜ tự ghi file
    Short, bất kể mentions_real_person hay hook_score -- an toàn không còn
    phụ thuộc vào 1 lần phân loại của model."""
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    _mock_pipeline(monkeypatch, mentions_real_person=False, still_developing=False, hook_score=9.5)
    out_json = tmp_path / "draft.json"
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "draft", "--domain", "FS",
        "--source-text", _REAL_SOURCE,
        "--source-url", "https://example.com/tin", "--source-date", "2026-07-29",
        "--output-json", str(out_json),
    ])
    exit_code = tsg.main()
    assert exit_code == 0
    result = json.loads(out_json.read_text(encoding="utf-8"))
    assert result["passed"] is True
    assert result["needs_human_review"] is True  # LUÔN True ở bước draft
    out_dir = tmp_path / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
    assert not out_dir.exists() or not list(out_dir.glob("TRENDING_*"))  # KHÔNG ghi file Short


def test_publish_writes_bundle_after_explicit_confirmation(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    monkeypatch.setattr(tsg, "_run_codex", lambda prompt: _fake_agy_json({"verdict": "PASS", "reason": "khớp nguồn"}))
    draft_json = tmp_path / "draft.json"
    draft_json.write_text(json.dumps({
        "facts": {
            "domain": "FS", "summary": "Tin phong thuy", "excerpt": "cơ quan chức năng xác nhận sự việc",
            "source_text": _REAL_SOURCE, "mentions_real_person": False, "still_developing": False,
        },
        "script": "Câu 1.\nCâu 2.", "passed": True, "hook_score": 9.0,
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "publish", "--draft-json", str(draft_json), "--confirm-reviewed",
    ])
    exit_code = tsg.main()
    assert exit_code == 0
    out_dir = tmp_path / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
    assert len(list(out_dir.glob("TRENDING_*"))) == 1


def test_publish_rejects_tampered_script_even_with_valid_excerpt_and_passed_true(tmp_path, monkeypatch):
    """Codex review vòng 2, HIGH: chỉ "script" bị thay (excerpt/source_text/
    passed vẫn hợp lệ) PHẢI bị publish từ chối -- re-verify độc lập tại
    publish phải tự phát hiện script không còn khớp nguồn, không tin nhãn
    "passed": true cũ."""
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    monkeypatch.setattr(tsg, "_run_codex", lambda prompt: _fake_agy_json({
        "verdict": "FAIL", "reason": "script chứa chi tiết không có trong source_text",
    }))
    draft_json = tmp_path / "draft.json"
    draft_json.write_text(json.dumps({
        "facts": {
            "domain": "FS", "summary": "Tin phong thuy", "excerpt": "cơ quan chức năng xác nhận sự việc",
            "source_text": _REAL_SOURCE, "mentions_real_person": False, "still_developing": False,
        },
        # "script" bị thay bằng nội dung KHÔNG liên quan gì tới source_text,
        # nhưng "passed": True và excerpt/source_text vẫn y nguyên hợp lệ.
        "script": "Đây là nội dung hoàn toàn bịa, không liên quan gì tới nguồn tin gốc.",
        "passed": True, "hook_score": 9.0,
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "publish", "--draft-json", str(draft_json), "--confirm-reviewed",
    ])
    exit_code = tsg.main()
    assert exit_code == 1
    out_dir = tmp_path / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
    assert not out_dir.exists() or not list(out_dir.glob("TRENDING_*"))


def test_publish_rejects_non_bool_passed_true_string(tmp_path, monkeypatch):
    """Schema nghiêm: "passed": "true" (chuỗi) hoặc 1 (int) không được coi
    là bool True hợp lệ."""
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    draft_json = tmp_path / "draft.json"
    draft_json.write_text(json.dumps({
        "facts": {
            "domain": "FS", "summary": "x", "excerpt": "cơ quan chức năng xác nhận sự việc",
            "source_text": _REAL_SOURCE,
        },
        "script": "Câu 1.", "passed": "true",
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "publish", "--draft-json", str(draft_json), "--confirm-reviewed",
    ])
    exit_code = tsg.main()
    assert exit_code == 1
    out_dir = tmp_path / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
    assert not out_dir.exists()


def test_publish_requires_confirm_reviewed_flag(tmp_path, monkeypatch, capsys):
    draft_json = tmp_path / "draft.json"
    draft_json.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["trending_short_generator.py", "publish", "--draft-json", str(draft_json)])
    with pytest.raises(SystemExit):
        tsg.main()  # argparse required=True trên --confirm-reviewed -- thiếu cờ này PHẢI lỗi ngay


def test_publish_refuses_when_draft_not_passed(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    draft_json = tmp_path / "draft.json"
    draft_json.write_text(json.dumps({
        "facts": {"domain": "FS", "summary": "x", "excerpt": "y", "source_text": "y z"},
        "script": None, "passed": False,
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "publish", "--draft-json", str(draft_json), "--confirm-reviewed",
    ])
    exit_code = tsg.main()
    assert exit_code == 1
    out_dir = tmp_path / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
    assert not out_dir.exists()


def test_publish_reverifies_grounding_rejects_tampered_draft(tmp_path, monkeypatch):
    """Defense-in-depth: nếu draft.json bị sửa tay (excerpt không còn khớp
    source_text đã lưu) giữa bước draft và publish, publish PHẢI từ chối,
    không tin mù draft cũ."""
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    draft_json = tmp_path / "draft.json"
    draft_json.write_text(json.dumps({
        "facts": {
            "domain": "FS", "summary": "x", "excerpt": "chi tiết bịa không có trong nguồn",
            "source_text": _REAL_SOURCE, "mentions_real_person": False, "still_developing": False,
        },
        "script": "Câu 1.", "passed": True,
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "publish", "--draft-json", str(draft_json), "--confirm-reviewed",
    ])
    exit_code = tsg.main()
    assert exit_code == 1
    out_dir = tmp_path / "drive_input" / "content_repo_staged" / "Phong Thủy" / "Short"
    assert not out_dir.exists()


def test_draft_fails_extraction_when_excerpt_not_grounded(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: _fake_agy_json({
        "excerpt": "hoàn toàn không có trong nguồn", "summary": "x",
        "mentions_real_person": False, "still_developing": False,
    }))
    out_json = tmp_path / "draft.json"
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "draft", "--domain", "FS",
        "--source-text", _REAL_SOURCE,
        "--source-url", "https://example.com/x", "--source-date", "2026-07-29",
        "--output-json", str(out_json),
    ])
    exit_code = tsg.main()
    assert exit_code == 1
    assert not out_json.exists()


# --- CLI validation ---

def test_draft_requires_source_text_or_file_mutually_exclusive(monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "draft", "--domain", "FS",
        "--source-text", "a", "--source-file", "b",
        "--source-url", "https://example.com/x", "--source-date", "2026-07-29",
        "--output-json", "out.json",
    ])
    with pytest.raises(SystemExit):  # argparse mutually_exclusive_group
        tsg.main()


def test_draft_rejects_too_short_source_text(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "draft", "--domain", "FS",
        "--source-text", "quá ngắn",
        "--source-url", "https://example.com/x", "--source-date", "2026-07-29",
        "--output-json", str(tmp_path / "out.json"),
    ])
    assert tsg.main() == 1


def test_draft_rejects_non_http_url(monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "draft", "--domain", "FS",
        "--source-text", _REAL_SOURCE,
        "--source-url", "not-a-url", "--source-date", "2026-07-29",
        "--output-json", "out.json",
    ])
    assert tsg.main() == 1


def test_draft_rejects_invalid_date_format(monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "trending_short_generator.py", "draft", "--domain", "FS",
        "--source-text", _REAL_SOURCE,
        "--source-url", "https://example.com/x", "--source-date", "29-07-2026",
        "--output-json", "out.json",
    ])
    assert tsg.main() == 1
