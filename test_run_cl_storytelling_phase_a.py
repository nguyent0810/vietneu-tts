"""Test cho run_cl_storytelling_phase_a.py -- driver production DUY NHẤT
cho Phase A STORYTELLING (yêu cầu vá lỗi "CLOSE PRODUCTION BYPASS"). Trọng
tâm: (a) episode thiếu topic_meta sidecar KHÔNG BAO GIỜ chạm compute_phase_
a_result() (bypass regression), (b) Gardner case thật chạy qua ĐÚNG con
đường driver -> claim ledger thật trên đĩa -> Phase A, (c) legacy episode
(đã có sidecar cũ) không bị driver đụng tới lần nữa."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import run_cl_storytelling_phase_a as D  # noqa: E402
import criminal_law_storytelling_phase_a as S  # noqa: E402


def _write_episode(short_dir: Path, episode: str, script_text: str, topic_meta: dict | None):
    short_dir.mkdir(parents=True, exist_ok=True)
    (short_dir / f"{episode}_Short.txt").write_text(script_text, encoding="utf-8")
    if topic_meta is not None:
        (short_dir / f"{episode}_Short.topic_meta.json").write_text(json.dumps(topic_meta, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def short_dir(tmp_path, monkeypatch):
    d = tmp_path / "Short"
    d.mkdir()
    monkeypatch.setattr(D, "SHORT_DIR", d)
    monkeypatch.setattr(S, "cl_metadata_sidecar_path", lambda episode, topic: d / f"{episode}_Short.cl_meta.json")
    monkeypatch.setattr(D, "cl_metadata_sidecar_path", lambda episode, topic: d / f"{episode}_Short.cl_meta.json")
    monkeypatch.setattr(D, "cl_topic_meta_sidecar_path", lambda episode, topic: d / f"{episode}_Short.topic_meta.json")
    return d


# =============================================================================
# PART 9 -- BYPASS REGRESSION: thiếu topic_meta sidecar -> KHÔNG BAO GIỜ gọi
# compute_phase_a_result() (proof: monkeypatch raise nếu bị gọi)
# =============================================================================

def test_missing_topic_meta_never_calls_compute_phase_a_result(short_dir, monkeypatch):
    _write_episode(short_dir, "ANDAXU_TestEp", "Kịch bản không có topic_meta.", topic_meta=None)

    def boom(*a, **kw):
        raise AssertionError("compute_phase_a_result() KHÔNG được gọi khi thiếu topic_meta sidecar")
    monkeypatch.setattr(D, "compute_phase_a_result", boom)

    status, detail = D.run_one("ANDAXU_TestEp")
    assert status == "FACT_LEDGER_MISSING"
    assert not (short_dir / "ANDAXU_TestEp_Short.cl_meta.json").exists()


def test_missing_source_file_field_also_blocks(short_dir, monkeypatch):
    _write_episode(short_dir, "ANDAXU_TestEp2", "Kịch bản.", topic_meta={"title": "t", "excerpt": "e"})  # thiếu source_file

    def boom(*a, **kw):
        raise AssertionError("compute_phase_a_result() KHÔNG được gọi khi topic_meta thiếu source_file")
    monkeypatch.setattr(D, "compute_phase_a_result", boom)

    status, detail = D.run_one("ANDAXU_TestEp2")
    assert status == "FACT_LEDGER_MISSING"


def test_run_one_refuses_to_overwrite_existing_sidecar_even_when_explicitly_targeted(short_dir, monkeypatch):
    """Tự review đối kháng: --episodes chỉ đích danh 1 episode ĐÃ PASS
    không được phép chạy lại/ghi đè sidecar cũ một cách im lặng."""
    _write_episode(short_dir, "ANDAXU_AlreadyDone", "Kịch bản đã qua Phase A.", GARDNER_TOPIC_META)
    (short_dir / "ANDAXU_AlreadyDone_Short.cl_meta.json").write_text(json.dumps({"case_id": "x"}), encoding="utf-8")

    def boom(*a, **kw):
        raise AssertionError("compute_phase_a_result() KHÔNG được gọi lại cho episode đã có sidecar")
    monkeypatch.setattr(D, "compute_phase_a_result", boom)

    status, detail = D.run_one("ANDAXU_AlreadyDone")
    assert status == "SKIPPED_ALREADY_DONE"


def test_discover_pending_skips_episode_that_already_has_sidecar(short_dir):
    """PART 10 -- LEGACY REGRESSION: episode đã có .cl_meta.json (giả lập
    nội dung SINH TRƯỚC bản vá, đã PASS qua đường cũ) KHÔNG xuất hiện trong
    danh sách pending -- driver mới không đụng lại, không re-verify, không
    re-publish nó như nội dung mới."""
    _write_episode(short_dir, "ANDAXU_LegacyEp", "Kịch bản cũ.", topic_meta=None)
    (short_dir / "ANDAXU_LegacyEp_Short.cl_meta.json").write_text(json.dumps({
        "case_id": "STORY_ANDAXU_LegacyEp", "final_editorial": {}, "named_individuals": [], "phase_a_variant": "storytelling_v1",
        # KHÔNG có "fact_verification" -- đúng thực tế sidecar sinh trước bản vá này
    }), encoding="utf-8")
    _write_episode(short_dir, "ANDAXU_NewEp", "Kịch bản mới.", topic_meta=None)

    pending = D.discover_pending_storytelling_episodes()
    assert "ANDAXU_LegacyEp" not in pending
    assert "ANDAXU_NewEp" in pending

    # Sidecar cũ vẫn đọc được nguyên vẹn, không bị driver mới sửa/xoá:
    legacy_sidecar = json.loads((short_dir / "ANDAXU_LegacyEp_Short.cl_meta.json").read_text(encoding="utf-8"))
    assert legacy_sidecar.get("fact_verification") is None  # đúng nghĩa "chưa từng qua gate mới" -- không bị âm thầm gắn VERIFIED


# =============================================================================
# PART 8 -- GARDNER E2E qua ĐÚNG con đường production: driver -> topic_meta
# thật -> topic_id_from_source_file() thật -> claim ledger THẬT trên đĩa
# (creator_specs/CL_VERIFIED_CLAIM_LEDGER_v1.json, không mock). Chỉ mock các
# bước gọi LLM thật (C4/SEO/person-check/claim-classification) -- không có
# hạ tầng gọi subprocess thật trong test.
# =============================================================================

GARDNER_TOPIC_META = {
    "title": "81 phút đột nhập và vụ trộm tranh thế kỷ tại bảo tàng Gardner",
    "source_file": "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3.md",
    "excerpt": "Hai kẻ trộm dùng chính cảm biến chuyển động của bảo tàng để tránh bị phát hiện.",
}


def _mock_llm_steps(monkeypatch, c4_pass=True, seo_pass=True, person_pass=True):
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: type("R", (), {"passed": c4_pass, "evidence": "e"})())
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {
        "passed": seo_pass, "seo": {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}, "iterations_used": 1,
    })
    monkeypatch.setattr(S, "_run_storytelling_person_check", lambda text: (person_pass, "ok"))


def test_gardner_sensor_evasion_script_blocked_end_to_end(short_dir, monkeypatch):
    """Bản kế thừa lỗi từ excerpt gốc (claim đã bị CONTRADICTED trong ledger
    thật) phải bị chặn qua ĐÚNG driver production, không phải chỉ ở test
    đơn vị cl_claim_ledger.py."""
    episode = "ANDAXU_GardnerBad"
    bad_script = "Hai kẻ trộm dùng chính cảm biến chuyển động của bảo tàng để tránh bị phát hiện."
    _write_episode(short_dir, episode, bad_script, GARDNER_TOPIC_META)
    _mock_llm_steps(monkeypatch)
    monkeypatch.setattr(S.cl_claim_ledger, "classify_high_risk_claims", lambda text: [
        {"text": bad_script, "risk_class": "security_system"},
    ])

    status, detail = D.run_one(episode)

    assert status == "BLOCKED_FACT"
    assert "GARDNER_SENSOR_EVASION" in detail
    assert not (short_dir / f"{episode}_Short.cl_meta.json").exists()


def test_gardner_corrected_script_passes_end_to_end(short_dir, monkeypatch):
    """Bản đã sửa (claim VERIFIED P0 thật trong ledger) phải PASS qua ĐÚNG
    driver production, và sidecar ghi lại đúng fact_verification (topic_id
    Gardner thật, claim_id thật đã match)."""
    episode = "ANDAXU_GardnerGood"
    good_script = "Cảm biến chuyển động của bảo tàng ghi lại đường di chuyển của hai kẻ trộm qua các phòng trưng bày."
    good_meta = dict(GARDNER_TOPIC_META, excerpt=good_script)
    _write_episode(short_dir, episode, good_script, good_meta)
    _mock_llm_steps(monkeypatch)
    monkeypatch.setattr(S.cl_claim_ledger, "classify_high_risk_claims", lambda text: [
        {"text": good_script, "risk_class": "security_system"},
    ])

    status, detail = D.run_one(episode)

    assert status == "PASS"
    sidecar_path = short_dir / f"{episode}_Short.cl_meta.json"
    assert sidecar_path.exists()
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    fv = sidecar["fact_verification"]
    assert fv["state"] == "VERIFIED_CLAIM_LEDGER"
    assert fv["topic_id"] == "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3"
    assert "GARDNER_SENSOR_RECORDED" in fv["verified_claim_ids"]
    assert fv["ledger_version"] and fv["ledger_version"] != "MISSING"
