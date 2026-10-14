"""Test cho cl_case_batch.py (task #241 -- driver nối Stage 1/2/3 với
bundle+sidecar cho short_batch_runner.py's CL branch). CHỈ test phần logic
thuần (serialize + ghi file) -- prepare_candidates()/main() cần LLM thật
(agy/Codex), không test ở đây (khớp giới hạn đã ghi trong docstring module:
script này chủ đích chạy thủ công, không phải unit-test-able end-to-end)."""
import json

import cl_case_batch as cb
import cl_risk_gate as g


def _named_individual(canonical_name, short_form_alias=None, role="named_relative_or_associate"):
    return g.NamedIndividual(canonical_name=canonical_name, identity_confidence="high", role=role, short_form_alias=short_form_alias)


def test_serialize_named_individuals_keeps_only_fields_phase_c_reads():
    people = [_named_individual("Nguyễn Văn A", short_form_alias="A", role="victim")]
    result = cb._serialize_named_individuals(people)
    assert result == [{"canonical_name": "Nguyễn Văn A", "short_form_alias": "A", "role": "victim"}]


def test_write_bundle_and_sidecar_produces_files_discover_segments_can_read(tmp_path, monkeypatch):
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    candidate = g.CandidateCase(
        case_id="case001", case_key="case001", working_title="Vụ án X",
        named_individuals=[_named_individual("Nguyễn Văn A")],
    )

    class _FakeGenResult:
        final_script = "Câu một. Câu hai."
        final_editorial = {"title": "T", "description": "D", "tags": ["a"], "thumbnail_brief": "B"}

    class _FakeReviewResult:
        reviewed_editorial_hash = "hash123"

    out_dir = tmp_path / "drive_input" / "content_repo_staged" / cb.CL_TOPIC / "Short"
    bundle_path = cb.write_bundle_and_sidecar(candidate, _FakeGenResult(), _FakeReviewResult(), out_dir)

    assert bundle_path.exists()
    assert bundle_path.read_text(encoding="utf-8") == "*** 1\nCâu một. Câu hai.\n"

    segments = sd.discover_segments(["CLGATE"], cb.CL_TOPIC)
    assert len(segments) == 1
    assert segments[0]["text"] == "Câu một. Câu hai."

    sidecar_path = sd.cl_metadata_sidecar_path(segments[0]["episode"], cb.CL_TOPIC)
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["case_id"] == "case001"
    assert sidecar["reviewed_editorial_hash"] == "hash123"
    assert sidecar["reviewed_script_hash"] == cb._script_text_hash(_FakeGenResult.final_script)
    assert sidecar["final_editorial"] == _FakeGenResult.final_editorial
    assert sidecar["named_individuals"] == [{"canonical_name": "Nguyễn Văn A", "short_form_alias": None, "role": "named_relative_or_associate"}]


def test_write_bundle_and_sidecar_uses_atomic_replace_no_tmp_leftover(tmp_path, monkeypatch):
    """Regression cho MEDIUM #2 (review độc lập Cursor/Grok): ghi qua file
    tạm + os.replace(), không để lại .tmp* mồ côi sau khi ghi xong."""
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    candidate = g.CandidateCase(case_id="case002", case_key="case002", working_title="Vụ án Y", named_individuals=[])

    class _FakeGenResult:
        final_script = "Một câu."
        final_editorial = {"title": "T", "description": "D", "tags": [], "thumbnail_brief": "B"}

    class _FakeReviewResult:
        reviewed_editorial_hash = "hash456"

    out_dir = tmp_path / "drive_input" / "content_repo_staged" / cb.CL_TOPIC / "Short"
    cb.write_bundle_and_sidecar(candidate, _FakeGenResult(), _FakeReviewResult(), out_dir)

    leftover_tmp = list(out_dir.glob("*.tmp*"))
    assert leftover_tmp == [], f"File tạm còn sót lại sau atomic write: {leftover_tmp}"


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
