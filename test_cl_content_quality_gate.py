"""CL sidecar gate + Phase A (storytelling) đi qua Content Quality Gate (S1)
(ticket 05a). Reject của C4 không còn chỉ in ra màn hình: record lưu script,
đoạn trích, case_id, các câu bị chặn và timestamp. Codex giả lập ở cấp hàm
gọi CLI (`_run_codex`)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cl_risk_gate_lifecycle as L  # noqa: E402
import cl_risk_gate_verification as V  # noqa: E402
import content_quality_gate as cqg  # noqa: E402
import criminal_law_storytelling_phase_a as S  # noqa: E402
import run_cl_storytelling_phase_a as D  # noqa: E402
import short_batch_runner as sbr  # noqa: E402

CL_TOPIC = "Hình Sự"
SCRIPT = "Năm 1990, hai kẻ trộm lấy đi 13 tác phẩm.\nVụ án chưa có lời giải."
EXCERPT = "Năm 1990, hai kẻ trộm đã lấy đi 13 tác phẩm nghệ thuật khỏi bảo tàng."


# --------------------------------------------------------------------------
# Sidecar gate của runner
# --------------------------------------------------------------------------

@pytest.fixture
def runner_env(tmp_path, monkeypatch):
    reg = tmp_path / "registry.json"
    reg.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sbr, "_registry_path", lambda t: reg)
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    return tmp_path


def _seg(text=SCRIPT, episode="CLGATE_case001"):
    return {"key": f"{episode}_01", "episode": episode, "segment_index": 1, "text": text}


def _write_sidecar(root, episode, sidecar):
    p = root / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short" / f"{episode}_Short.cl_meta.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sidecar, ensure_ascii=False), encoding="utf-8")


def _run(root, seg, monkeypatch):
    class _Stop(Exception):
        pass

    def tts(*a, **k):
        raise _Stop()
    monkeypatch.setattr(sbr, "run_tts", tts)
    registry = {}
    try:
        return sbr.process_one_segment(seg, root / "out", "creds.json", [], registry, None, 8, False, CL_TOPIC), False
    except _Stop:
        return registry[seg["key"]], True


def test_missing_sidecar_is_recorded_with_its_own_reason_code(runner_env, monkeypatch):
    entry, reached_tts = _run(runner_env, _seg(), monkeypatch)
    assert not reached_tts and entry["status"] == "needs_review"
    rec = cqg.read_records("CL")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.SAF_CL_SIDECAR_MISSING])
    assert rec["source_outcome"]["source"] == cqg.SOURCE_CL_SIDECAR_GATE
    assert rec["script"] == SCRIPT
    assert entry["quality_record_id"] == rec["quality_record_id"]


@pytest.mark.parametrize("sidecar,code", [
    ({"case_id": "case001"}, cqg.SAF_CL_SIDECAR_INCOMPLETE),
    ({"case_id": "case001", "reviewed_editorial_hash": "e", "final_editorial": {}, "named_individuals": [],
      "reviewed_script_hash": "khong-khop"}, cqg.SAF_CL_SCRIPT_HASH_MISMATCH),
])
def test_each_sidecar_failure_kind_has_a_reason_code(runner_env, monkeypatch, sidecar, code):
    _write_sidecar(runner_env, "CLGATE_case001", sidecar)
    entry, reached_tts = _run(runner_env, _seg(), monkeypatch)
    assert not reached_tts
    rec = cqg.read_records("CL")[-1]
    assert rec["reason_codes"] == [code]
    assert rec["identity"]["case_id"] == "case001"


def test_valid_sidecar_is_pass_record_with_case_id_and_reviewed_hashes(runner_env, monkeypatch):
    sidecar = {"case_id": "case001", "reviewed_editorial_hash": "abc", "reviewed_script_hash": L._script_text_hash(SCRIPT),
               "final_editorial": {"title": "T"}, "named_individuals": []}
    _write_sidecar(runner_env, "CLGATE_case001", sidecar)
    entry, reached_tts = _run(runner_env, _seg(), monkeypatch)
    assert reached_tts and entry["status"] == "scripted"
    rec = cqg.read_records("CL")[-1]
    assert rec["gate_status"] == cqg.PASS
    assert rec["identity"]["case_id"] == "case001"
    raw = rec["source_outcome"]["raw"]
    assert raw["reviewed_script_hash"] == sidecar["reviewed_script_hash"] and raw["reviewed_editorial_hash"] == "abc"


def test_sidecar_pass_but_record_write_failure_blocks_tts(runner_env, monkeypatch):
    sidecar = {"case_id": "case001", "reviewed_editorial_hash": "abc", "reviewed_script_hash": L._script_text_hash(SCRIPT),
               "final_editorial": {"title": "T"}, "named_individuals": []}
    _write_sidecar(runner_env, "CLGATE_case001", sidecar)
    blocker = runner_env / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(blocker / "qr"))
    entry, reached_tts = _run(runner_env, _seg(), monkeypatch)
    assert not reached_tts and entry["status"] == "needs_review"


# --------------------------------------------------------------------------
# Phase A storytelling (driver production)
# --------------------------------------------------------------------------

TOPIC_META = {"title": "Vụ trộm tranh", "source_file": "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3.md", "excerpt": EXCERPT}


@pytest.fixture
def short_dir(tmp_path, monkeypatch):
    d = tmp_path / "Short"
    d.mkdir()
    monkeypatch.setattr(D, "SHORT_DIR", d)
    monkeypatch.setattr(S, "cl_metadata_sidecar_path", lambda episode, topic: d / f"{episode}_Short.cl_meta.json")
    monkeypatch.setattr(D, "cl_metadata_sidecar_path", lambda episode, topic: d / f"{episode}_Short.cl_meta.json")
    monkeypatch.setattr(D, "cl_topic_meta_sidecar_path", lambda episode, topic: d / f"{episode}_Short.topic_meta.json")
    return d


def _episode(short_dir, episode, topic_meta=TOPIC_META):
    (short_dir / f"{episode}_Short.txt").write_text(SCRIPT, encoding="utf-8")
    if topic_meta is not None:
        (short_dir / f"{episode}_Short.topic_meta.json").write_text(json.dumps(topic_meta, ensure_ascii=False), encoding="utf-8")


def _c4_codex(verdict_first):
    lines = SCRIPT.split("\n")
    return lambda prompt: json.dumps({"claims": [
        {"sentence": lines[0], "verdict": verdict_first, "materiality": True, "reason": "không có trong căn cứ"},
        {"sentence": lines[1], "verdict": "HARMLESS_NARRATIVE", "materiality": False, "reason": "khung dẫn"},
    ]}, ensure_ascii=False)


def test_c4_fail_record_keeps_script_excerpt_case_id_and_blocked_sentences(short_dir, monkeypatch):
    _episode(short_dir, "ANDAXU_TranhGardner")
    monkeypatch.setattr(V, "_run_codex", _c4_codex("UNSUPPORTED"))
    status, _ = D.run_one("ANDAXU_TranhGardner")
    assert status == "FAIL"
    rec = cqg.read_records("CL")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.ACC_C4_BLOCKED])
    assert rec["script"] == SCRIPT and rec["source_excerpt"] == EXCERPT
    assert rec["identity"]["case_id"] and rec["identity"]["content_id"] == "ANDAXU_TranhGardner_01"
    assert rec["created_at"]
    blocked = rec["evidence"][0]["blocked_sentences"]
    assert [b["sentence"] for b in blocked] == [SCRIPT.split("\n")[0]]
    assert blocked[0]["verdict"] == "UNSUPPORTED"
    assert rec["source_outcome"]["raw"]["reason_code"] == "STORYTELLING_C4_FAILED"


def test_c4_scoring_logic_unchanged_passing_claims_still_pass(monkeypatch):
    monkeypatch.setattr(V, "_run_codex", _c4_codex("ENTAILED"))
    cand = S._build_minimal_candidate("ANDAXU_X", "t", EXCERPT)
    result = V._score_c4_adversarial_text(SCRIPT, cand)
    assert result.passed is True
    assert result.details == {"blocking_claims": [], "n_claims": 2}


def test_phase_a_pass_is_recorded_before_sidecar(short_dir, monkeypatch):
    _episode(short_dir, "ANDAXU_Pass")
    monkeypatch.setattr(V, "_run_codex", _c4_codex("ENTAILED"))
    monkeypatch.setattr(S.cl_claim_ledger, "classify_high_risk_claims", lambda text: [])
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {
        "passed": True, "seo": {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}, "iterations_used": 1})
    monkeypatch.setattr(S, "_run_storytelling_person_check", lambda text: (True, "ok"))
    status, _ = D.run_one("ANDAXU_Pass")
    assert status == "PASS"
    rec = cqg.read_records("CL")[-1]
    assert rec["gate_status"] == cqg.PASS
    assert rec["source_outcome"]["raw"]["reviewed_script_hash"] == L._script_text_hash(SCRIPT)
    assert (short_dir / "ANDAXU_Pass_Short.cl_meta.json").exists()


def test_phase_a_pass_but_record_write_failure_writes_no_sidecar(short_dir, monkeypatch, tmp_path):
    _episode(short_dir, "ANDAXU_Pass2")
    monkeypatch.setattr(V, "_run_codex", _c4_codex("ENTAILED"))
    monkeypatch.setattr(S.cl_claim_ledger, "classify_high_risk_claims", lambda text: [])
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {
        "passed": True, "seo": {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}, "iterations_used": 1})
    monkeypatch.setattr(S, "_run_storytelling_person_check", lambda text: (True, "ok"))
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(blocker / "qr"))
    status, _ = D.run_one("ANDAXU_Pass2")
    assert status == "FAIL"
    assert not (short_dir / "ANDAXU_Pass2_Short.cl_meta.json").exists()


def test_missing_topic_meta_is_recorded_as_needs_review(short_dir):
    _episode(short_dir, "ANDAXU_NoMeta", topic_meta=None)
    status, _ = D.run_one("ANDAXU_NoMeta")
    assert status == "FACT_LEDGER_MISSING"
    rec = cqg.read_records("CL")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.NEEDS_REVIEW, [cqg.SRC_FACT_LEDGER_MISSING])


@pytest.mark.parametrize("reason_code,status,code", [
    ("STORYTELLING_BLOCKED_FACT", cqg.FAIL, cqg.ACC_CLAIM_LEDGER_BLOCKED),
    ("STORYTELLING_PROVENANCE_FAILED", cqg.FAIL, cqg.ACC_PROVENANCE_FAILED),
    ("STORYTELLING_UNVETTED_PERSON_REFERENCE", cqg.FAIL, cqg.SAF_UNVETTED_PERSON_REFERENCE),
    ("STORYTELLING_SEO_FAILED", cqg.NEEDS_REVIEW, cqg.STR_SEO_FAILED),
    ("STORYTELLING_CLAIM_LEDGER_ERROR", cqg.NEEDS_REVIEW, cqg.INTERNAL_CLAIM_LEDGER_ERROR),
    ("STORYTELLING_PHASE_A_UNEXPECTED_ERROR", cqg.NEEDS_REVIEW, cqg.INTERNAL_PHASE_A_ERROR),
    ("STORYTELLING_SOMETHING_NEW", cqg.NEEDS_REVIEW, cqg.INTERNAL_UNMAPPED),
])
def test_phase_a_reason_codes_map_without_guessing(reason_code, status, code):
    result = S.StorytellingPhaseAResult(False, reason_code, "e", draft_script="nháp")
    decision = cqg.decide(S.content_quality_outcome("ANDAXU_Y", result, script="nháp", excerpt="x", generator="g"))
    assert (decision.gate_status, decision.reason_codes) == (status, [code])


# --------------------------------------------------------------------------
# Sửa theo review: mọi loại lỗi sidecar qua đúng call site, C4 drift
# (provenance) lưu các câu bị chặn, script nháp giữ ở nhánh exception.
# --------------------------------------------------------------------------

def test_unreadable_sidecar_kind_through_runner(runner_env, monkeypatch):
    p = runner_env / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short" / "CLGATE_case001_Short.cl_meta.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{không phải json", encoding="utf-8")
    entry, reached_tts = _run(runner_env, _seg(), monkeypatch)
    assert not reached_tts
    assert cqg.read_records("CL")[-1]["reason_codes"] == [cqg.SAF_CL_SIDECAR_UNREADABLE]


def _valid_sidecar(**extra):
    return {"case_id": "case001", "reviewed_editorial_hash": "abc", "reviewed_script_hash": L._script_text_hash(SCRIPT),
            "final_editorial": {"title": "T"}, "named_individuals": [], **extra}


def test_fact_verification_invalid_kind_through_runner(runner_env, monkeypatch):
    _write_sidecar(runner_env, "CLGATE_case001", _valid_sidecar(phase_a_variant="storytelling_v1", fact_verification=None))
    monkeypatch.setattr(sbr.cl_claim_ledger, "validate_fact_verification_binding", lambda fv, text: (False, "thiếu"))
    entry, reached_tts = _run(runner_env, _seg(), monkeypatch)
    assert not reached_tts
    assert cqg.read_records("CL")[-1]["reason_codes"] == [cqg.SAF_CL_FACT_VERIFICATION_INVALID]


def test_provenance_invalid_kind_through_runner(runner_env, monkeypatch):
    _write_sidecar(runner_env, "CLGATE_case001", _valid_sidecar(phase_a_variant="storytelling_provenance_v1"))
    monkeypatch.setattr(sbr, "_validate_provenance_binding", lambda episode, topic, text: "binding lệch pack")
    entry, reached_tts = _run(runner_env, _seg(), monkeypatch)
    assert not reached_tts
    assert cqg.read_records("CL")[-1]["reason_codes"] == [cqg.SAF_CL_PROVENANCE_INVALID]


def _provenance_fixtures(monkeypatch):
    import cl_story_fact_pack as fp
    import cl_story_plan_and_generation as spg
    pack = fp.StoryFactPack(topic_id="T1", source_file="src.md", excerpt_hash="h", ledger_version_at_build="v",
                            facts=[fp.StoryFact(fact_id="F001", proposition="Năm 1990 có 13 tác phẩm bị lấy.")])
    plan = spg.StoryPlan(topic_id="T1", fact_pack_hash=pack.pack_hash(),
                         segments=[spg.PlanSegment(segment_id="S1", role="HOOK", fact_ids=["F001"])])
    prose = "Năm 1990, kẻ trộm là cựu bảo vệ."
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": prose, "pack_hash_at_generation": pack.pack_hash()}]
    monkeypatch.setattr(S.cl_story_fact_pack, "get_or_build_fact_pack", lambda *a, **k: pack)
    monkeypatch.setattr(S.spg, "build_story_plan", lambda p: plan)
    monkeypatch.setattr(S.spg, "generate_bound_script", lambda pl, p: (prose, bindings))
    monkeypatch.setattr(V, "_run_codex", lambda prompt: json.dumps({"claims": [
        {"sentence": prose, "verdict": "UNSUPPORTED", "materiality": True, "reason": "cựu bảo vệ không có trong fact"}]},
        ensure_ascii=False))
    return prose


def test_provenance_drift_fail_records_blocked_sentences_and_draft(tmp_path, monkeypatch):
    import criminal_law_provenance_generator as prov
    prose = _provenance_fixtures(monkeypatch)
    monkeypatch.setattr(prov, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(prov.cl_claim_ledger, "topic_id_from_source_file", lambda s: "T1")
    status, _ = prov.run_one({"title": "Vụ tranh", "excerpt": EXCERPT, "source_file": "src.md"})
    assert status == "FAIL"
    rec = cqg.read_records("CL")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.ACC_PROVENANCE_FAILED])
    assert rec["script"] == prose
    blocked = rec["evidence"][0]["blocked_sentences"]
    assert blocked == [{"sentence": prose, "verdict": "UNSUPPORTED", "materiality": True,
                        "reason": "cựu bảo vệ không có trong fact", "segment_id": "S1"}]


def test_provenance_exception_after_script_keeps_draft(monkeypatch):
    prose = _provenance_fixtures(monkeypatch)
    monkeypatch.setattr(S.spg, "run_deterministic_guards", lambda b, p: (_ for _ in ()).throw(RuntimeError("hỏng")))
    result, *_ = S.compute_phase_a_result_provenance("ANDAXU_X", "T1", "src.md", EXCERPT)
    assert result.reason_code == "STORYTELLING_PHASE_A_UNEXPECTED_ERROR"
    assert result.draft_script == prose
