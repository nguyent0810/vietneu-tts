"""Test cho publish-boundary fact_verification binding check trong
short_batch_runner.py's process_one_segment() CL branch (yêu cầu vá lỗi
"CLOSE PUBLISH-BOUNDARY BYPASS"). Câu hỏi cốt lõi cần chứng minh: sự tồn
tại của .cl_meta.json KHÔNG BAO GIỜ, tự nó, là bằng chứng đủ để publish 1
episode STORYTELLING -- consumer phải đối chiếu LẠI fact_verification với
ledger thật + ràng buộc với chính script đang publish.

Cùng quy ước fixture với test_short_batch_runner_cl_gate.py (đã có, không
tự chế lại): monkeypatch sbr._registry_path/sbr.PROJECT_ROOT/sd.PROJECT_ROOT,
_write_sidecar ghi trực tiếp xuống đĩa."""
import json

import pytest

import short_batch_runner as sbr
import cl_claim_ledger as L
import cl_risk_gate_lifecycle as CLL

CL_TOPIC = "Hình Sự"
GARDNER_TOPIC = "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3"
GOOD_SCRIPT = "Cảm biến chuyển động của bảo tàng ghi lại đường di chuyển của hai kẻ trộm qua các phòng trưng bày."
BAD_SCRIPT = "Hai kẻ trộm dùng chính cảm biến chuyển động của bảo tàng để tránh bị phát hiện."
UNRELATED_SCRIPT = "Băng đảng buôn ma túy xuyên biên giới bị cảnh sát triệt phá sau nhiều năm điều tra bí mật."


def _base_seg(episode="ANDAXU_GardnerTest", idx=1, text=GOOD_SCRIPT):
    return {"key": f"{episode}_{idx:02d}", "episode": episode, "segment_index": idx, "text": text}


def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **k: (_ for _ in ()).throw(AssertionError("run_tts KHÔNG được gọi khi fact_verification không hợp lệ (fail-closed PHẢI dừng trước đó)")))


def _write_sidecar(tmp_path, episode, sidecar: dict):
    sd_path = tmp_path / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short" / f"{episode}_Short.cl_meta.json"
    sd_path.parent.mkdir(parents=True, exist_ok=True)
    sd_path.write_text(json.dumps(sidecar, ensure_ascii=False), encoding="utf-8")
    return sd_path


def _mock_gardner_sensor_extraction(monkeypatch):
    """cl_claim_ledger.validate_fact_verification_binding() (round 2 fix,
    BLOCKER #2) giờ gọi LẠI verify_high_risk_claims_with_refs() TƯƠI trên
    final_script -- cần mock _run_codex/_run_agy để claim trích ra khớp
    ĐÚNG GOOD_SCRIPT/GARDNER_SENSOR_RECORDED thật trong ledger trên đĩa,
    tránh gọi LLM thật trong unit test (chậm, không xác định)."""
    import json

    def _dispatch(prompt):
        if "Trích MỌI khẳng định thực tế" in prompt:
            return json.dumps({"claims": [{"text": GOOD_SCRIPT, "risk_class": "security_system"}]})
        raise AssertionError(f"Test này không kỳ vọng gọi lượt xác minh subject/material: {prompt[:150]!r}")
    monkeypatch.setattr(L, "_run_codex", _dispatch)
    monkeypatch.setattr(L, "_run_agy", lambda prompt: json.dumps({"claims": []}))


def _real_verified_fact_verification():
    """fact_verification THẬT, đối chiếu ledger THẬT trên đĩa cho claim
    GARDNER_SENSOR_RECORDED (đã VERIFIED, P0) -- dùng làm nền cho case A/H
    (hợp lệ) và làm nguyên liệu forge cho case D/F/G."""
    return {
        "state": "VERIFIED_CLAIM_LEDGER", "topic_id": GARDNER_TOPIC,
        "ledger_version": L.ledger_version(), "verified_claim_ids": ["GARDNER_SENSOR_RECORDED"],
        "blocked_claim_ids": [], "checked_at": "2026-08-24T00:00:00+00:00",
    }


def _run_and_get_entry(tmp_path, seg, registry=None):
    registry = registry if registry is not None else {}
    return sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                    registry, None, 8, False, CL_TOPIC)


# =============================================================================
# Case A -- sidecar hợp lệ THẬT (như run_cl_storytelling_phase_a.py sẽ ghi)
# =============================================================================

def test_case_a_valid_new_sidecar_proceeds(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    _mock_gardner_sensor_extraction(monkeypatch)
    seg = _base_seg()
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc", "reviewed_script_hash": CLL._script_text_hash(seg["text"]),
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1",
        "fact_verification": _real_verified_fact_verification(),
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    class _Stop(Exception):
        pass
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **k: (_ for _ in ()).throw(_Stop()))
    with pytest.raises(_Stop):
        _run_and_get_entry(tmp_path, seg)
    # Không raise nghĩa là bị chặn TRƯỚC run_tts -- ở đây raise _Stop nghĩa là đã QUA hết gate, đúng kỳ vọng.


# =============================================================================
# Case B -- legacy sidecar (phase_a_variant=storytelling_v1, KHÔNG có fact_verification)
# =============================================================================

def test_case_b_legacy_sidecar_no_fact_verification_key_blocks(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    seg = _base_seg()
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc", "reviewed_script_hash": CLL._script_text_hash(seg["text"]),
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1",
        # KHÔNG có "fact_verification" -- đúng sidecar sinh TRƯỚC bản vá này
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"
    assert "fact_verification" in entry["needs_human_review_cl_gate"].lower()


# =============================================================================
# Case C -- scratchpad-style sidecar (fact_verification=None tường minh,
# mô phỏng sidecar ghi bởi write_claude_reviewed_sidecar.py -- script tạm
# đã dùng thật trong phiên làm việc khi codex/cursor down)
# =============================================================================

def test_case_c_scratchpad_style_sidecar_blocks(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    seg = _base_seg()
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc", "reviewed_script_hash": CLL._script_text_hash(seg["text"]),
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1",
        "verified_by": "claude_agent_review_2026-08-22_codex_cursor_quota_outage",  # dấu vết thật của script scratchpad
        "fact_verification": None,
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"


# =============================================================================
# Case D -- forged VERIFIED state (thiếu topic_id/ledger_version/verified_claim_ids)
# =============================================================================

def test_case_d_forged_verified_state_missing_fields_blocks(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    seg = _base_seg()
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc", "reviewed_script_hash": CLL._script_text_hash(seg["text"]),
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1",
        "fact_verification": {"state": "VERIFIED_CLAIM_LEDGER"},  # chỉ có state, không có gì khác
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"
    assert "topic_id" in entry["needs_human_review_cl_gate"]


# =============================================================================
# Case E -- script bị đổi SAU khi Phase A review (đã có hash check chung
# CHO MỌI sidecar CL -- test này xác nhận RÕ hành vi đó vẫn đúng cho
# sidecar dạng storytelling, không chỉ dạng case pipeline).
# =============================================================================

def test_case_e_script_modified_after_verification_blocks_via_hash_mismatch(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    original_text = GOOD_SCRIPT
    tampered_seg = _base_seg(text=original_text + " Câu bị thêm vào SAU khi Phase A đã review.")
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc",
        "reviewed_script_hash": CLL._script_text_hash(original_text),  # hash của bản GỐC, không phải bản đã sửa
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1",
        "fact_verification": _real_verified_fact_verification(),
    }
    _write_sidecar(tmp_path, tampered_seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, tampered_seg)
    assert entry["status"] == "needs_review"
    assert "đã bị đổi" in entry["needs_human_review_cl_gate"]


# =============================================================================
# Case F -- valid Gardner fact_verification NHƯNG script hoàn toàn không liên quan
# (hash tự tính đúng cho script MỚI -- qua được hash check cũ -- nhưng claim
# text không khớp script -- binding check MỚI phải chặn)
# =============================================================================

def test_case_f_wrong_topic_binding_claim_not_present_in_script_blocks(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    seg = _base_seg(text=UNRELATED_SCRIPT)  # script KHÔNG liên quan gì tới Gardner
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc",
        "reviewed_script_hash": CLL._script_text_hash(seg["text"]),  # tự tính ĐÚNG cho script mới -- qua được hash check
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1",
        "fact_verification": _real_verified_fact_verification(),  # nhưng fact_verification là của Gardner
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"
    assert "khớp" in entry["needs_human_review_cl_gate"].lower() or "copy" in entry["needs_human_review_cl_gate"].lower()


# =============================================================================
# Case G -- kịch bản sensor-evasion (đã bị CONTRADICTED) cố hoàn tất qua
# downstream: dùng fact_verification "hợp lệ về hình thức" của claim khác
# (GARDNER_SENSOR_RECORDED) nhưng gắn cho ĐÚNG bad script -- claim text
# (nói cảm biến GHI LẠI) không khớp bad script (nói cảm biến bị NÉ TRÁNH)
# => binding check chặn, KHÔNG BAO GIỜ tới publish-ready.
# =============================================================================

def test_case_g_contradicted_sensor_evasion_script_never_reaches_publish_ready(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    seg = _base_seg(text=BAD_SCRIPT)
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc",
        "reviewed_script_hash": CLL._script_text_hash(seg["text"]),
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1",
        "fact_verification": _real_verified_fact_verification(),  # claim "ghi lại" cố gán cho script "né tránh"
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"


# =============================================================================
# Review đối kháng #5 -- ledger_version CŨ (ledger đã đổi kể từ lúc Phase A
# chạy) phải bị coi STALE, chặn publish dù mọi field khác "hợp lệ".
# =============================================================================

def test_adversarial_stale_ledger_version_blocks(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    seg = _base_seg()
    fv = _real_verified_fact_verification()
    fv["ledger_version"] = "0" * 12  # chắc chắn khác ledger_version() thật hiện tại
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc", "reviewed_script_hash": CLL._script_text_hash(seg["text"]),
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1", "fact_verification": fv,
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"
    assert "ledger_version" in entry["needs_human_review_cl_gate"] or "ledger đã đổi" in entry["needs_human_review_cl_gate"]


# =============================================================================
# Review đối kháng #6 -- topic_id không tồn tại/sai trong ledger (claim_id
# thật của Gardner nhưng gán nhầm cho 1 topic_id không có entry nào).
# =============================================================================

def test_adversarial_wrong_nonexistent_topic_id_blocks(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    seg = _base_seg()
    fv = _real_verified_fact_verification()
    fv["topic_id"] = "TOPIC_KHONG_TON_TAI_TRONG_LEDGER"
    sidecar = {
        "case_id": "STORY_x", "reviewed_editorial_hash": "abc", "reviewed_script_hash": CLL._script_text_hash(seg["text"]),
        "final_editorial": {"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        "named_individuals": [], "phase_a_variant": "storytelling_v1", "fact_verification": fv,
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"
    assert "KHÔNG tồn tại" in entry["needs_human_review_cl_gate"]


# =============================================================================
# Review đối kháng #7 -- gọi compute_phase_a_result() trực tiếp (low-level,
# bỏ qua driver) với claim_ledger_topic_id=None -> LEGACY_UNVERIFIED ->
# sidecar ghi ra -> consumer THẬT vẫn phải chặn (composition đầy đủ 2 lớp
# phòng thủ: producer optional-arg + consumer validation).
# =============================================================================

def test_adversarial_direct_low_level_call_still_blocked_at_consumer(tmp_path, monkeypatch):
    import criminal_law_storytelling_phase_a as S

    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: type("R", (), {"passed": True, "evidence": "e"})())
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {
        "passed": True, "seo": {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}, "iterations_used": 1,
    })
    monkeypatch.setattr(S, "_run_storytelling_person_check", lambda text: (True, "ok"))

    result = S.compute_phase_a_result("EP_DirectCall", "Tiêu đề", "excerpt", GOOD_SCRIPT)  # claim_ledger_topic_id KHÔNG truyền -- None
    assert result.passed is True
    assert result.fact_verification["state"] == "LEGACY_UNVERIFIED"

    sidecar_path = tmp_path / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short" / "EP_DirectCall_Short.cl_meta.json"
    monkeypatch.setattr(S, "cl_metadata_sidecar_path", lambda ep, topic: sidecar_path)
    S.write_storytelling_sidecar("EP_DirectCall", result)

    _setup(tmp_path, monkeypatch)
    seg = _base_seg(episode="EP_DirectCall", text=GOOD_SCRIPT)
    entry = _run_and_get_entry(tmp_path, seg)
    assert entry["status"] == "needs_review"
    assert "LEGACY_UNVERIFIED" in entry["needs_human_review_cl_gate"]


# =============================================================================
# Case H -- full E2E: generator -> topic_meta -> Phase A driver THẬT ->
# verified sidecar -> short_batch_runner -> eligible (status=scripted).
# =============================================================================

def test_case_h_correct_gardner_version_full_path_reaches_scripted(tmp_path, monkeypatch):
    import run_cl_storytelling_phase_a as D
    import criminal_law_storytelling_phase_a as S

    short_dir = tmp_path / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short"
    short_dir.mkdir(parents=True)
    episode = "ANDAXU_GardnerGoodE2E"
    topic_meta = {
        "title": "81 phút đột nhập và vụ trộm tranh thế kỷ tại bảo tàng Gardner",
        "source_file": f"{GARDNER_TOPIC}.md", "excerpt": GOOD_SCRIPT,
    }
    (short_dir / f"{episode}_Short.txt").write_text(GOOD_SCRIPT, encoding="utf-8")
    (short_dir / f"{episode}_Short.topic_meta.json").write_text(json.dumps(topic_meta, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(D, "SHORT_DIR", short_dir)
    monkeypatch.setattr(S, "cl_metadata_sidecar_path", lambda ep, topic: short_dir / f"{ep}_Short.cl_meta.json")
    monkeypatch.setattr(D, "cl_metadata_sidecar_path", lambda ep, topic: short_dir / f"{ep}_Short.cl_meta.json")
    monkeypatch.setattr(D, "cl_topic_meta_sidecar_path", lambda ep, topic: short_dir / f"{ep}_Short.topic_meta.json")
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: type("R", (), {"passed": True, "evidence": "e"})())
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {
        "passed": True, "seo": {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}, "iterations_used": 1,
    })
    monkeypatch.setattr(S, "_run_storytelling_person_check", lambda text: (True, "ok"))
    monkeypatch.setattr(S.cl_claim_ledger, "classify_high_risk_claims", lambda text: [
        {"text": GOOD_SCRIPT, "risk_class": "security_system"},
    ])

    status, detail = D.run_one(episode)
    assert status == "PASS", detail

    # Bây giờ chạy ĐÚNG consumer thật (short_batch_runner.py) trên sidecar
    # VỪA được Phase A driver THẬT ghi ra -- không tự dựng sidecar tay.
    _setup(tmp_path, monkeypatch)
    seg = _base_seg(episode=episode, text=GOOD_SCRIPT)

    class _Stop(Exception):
        pass
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **k: (_ for _ in ()).throw(_Stop()))
    with pytest.raises(_Stop):
        _run_and_get_entry(tmp_path, seg)
