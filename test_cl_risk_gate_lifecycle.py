"""Test cho cl_risk_gate_lifecycle.py (§1.13 Stage 3 Phase A(final)/C/D
groundwork, task #241). Mock L._run_agy/_run_codex đúng pattern
test_cl_claim_exposure_gate.py/test_cl_risk_gate_verification.py. Audio
chain-of-custody test dùng ffmpeg VENDORED THẬT (không mock) sinh fixture
WAV/MP4 nhỏ -- khớp tinh thần "test bằng ffmpeg thật" đã dùng ở
_evidence_hold_boundary.py/mix_bgm.py's test lịch sử."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cl_risk_gate as g  # noqa: E402
import cl_risk_gate_lifecycle as L  # noqa: E402


def _fake_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _named(name, role="convicted_perpetrator", alias=None):
    return g.NamedIndividual(canonical_name=name, identity_confidence="high", role=role, short_form_alias=alias)


def _candidate(named_individuals=None, core_facts=None, risk_review_draft="Draft gốc."):
    return g.CandidateCase(
        case_id="c1", case_key="k1", working_title="Test case",
        named_individuals=named_individuals or [], core_facts=core_facts or [],
        risk_review_draft=risk_review_draft,
    )


# =============================================================================
# Canonical serialization + hashing
# =============================================================================

def test_editorial_hash_stable_across_nfc_forms():
    """2 dạng Unicode tổ hợp khác nhau của CÙNG 1 chuỗi (NFC vs NFD) phải
    cho CÙNG 1 hash -- _canonicalize_value() phải NFC-normalize trước khi
    hash."""
    nfc = {"title": "Hà Nội", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}
    nfd = {"title": "Hà Nội", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}
    # nfd ở trên không thật sự NFD cho "Hà" -- dùng unicodedata trực tiếp để chắc chắn đúng test.
    import unicodedata
    nfd = {**nfc, "title": unicodedata.normalize("NFD", nfc["title"])}
    assert nfc["title"] != nfd["title"]  # xác nhận 2 dạng bytes khác nhau thật
    assert L.compute_editorial_hash(nfc) == L.compute_editorial_hash(nfd)


def test_editorial_hash_tags_order_independent():
    a = {"title": "t", "description": "d", "tags": ["z", "a", "m"], "thumbnail_brief": "b"}
    b = {"title": "t", "description": "d", "tags": ["m", "z", "a"], "thumbnail_brief": "b"}
    assert L.compute_editorial_hash(a) == L.compute_editorial_hash(b)


def test_editorial_hash_changes_when_title_changes():
    a = {"title": "Title A", "description": "d", "tags": [], "thumbnail_brief": "b"}
    b = {"title": "Title B", "description": "d", "tags": [], "thumbnail_brief": "b"}
    assert L.compute_editorial_hash(a) != L.compute_editorial_hash(b)


def test_editorial_hash_missing_field_serialized_as_explicit_null():
    """Field thiếu trong metadata phải serialize thành null RÕ RÀNG --
    khác với field KHÔNG có mặt trong dict truyền vào phải cho CÙNG hash
    với field=None tường minh (vì cả 2 đều .get() ra None)."""
    a = {"title": "t"}  # thiếu description/tags/thumbnail_brief
    b = {"title": "t", "description": None, "tags": None, "thumbnail_brief": None}
    assert L.compute_editorial_hash(a) == L.compute_editorial_hash(b)


def test_upload_policy_hash_independent_of_editorial_fields():
    """Đổi title KHÔNG được làm đổi upload_policy_hash -- 2 hash domain
    TÁCH BIỆT hoàn toàn (fixes round-7 Blocker B1 -- 'v7 does not
    currently require the same fields on both sides')."""
    meta_a = {"title": "A", "scheduling": "2026-01-01", "privacy_setting": "public", "channel_account_id": "ch1", "upload_operation_mode": "auto"}
    meta_b = {"title": "B", "scheduling": "2026-01-01", "privacy_setting": "public", "channel_account_id": "ch1", "upload_operation_mode": "auto"}
    assert L.compute_upload_policy_hash(meta_a) == L.compute_upload_policy_hash(meta_b)


def test_upload_policy_hash_changes_when_channel_changes():
    meta_a = {"scheduling": "2026-01-01", "privacy_setting": "public", "channel_account_id": "ch1", "upload_operation_mode": "auto"}
    meta_b = {**meta_a, "channel_account_id": "ch2"}
    assert L.compute_upload_policy_hash(meta_a) != L.compute_upload_policy_hash(meta_b)


def test_canonical_blob_rejects_non_dict_metadata():
    with pytest.raises(L.LifecycleError):
        L.compute_editorial_hash("not a dict")


def test_canonical_blob_rejects_non_list_tags():
    with pytest.raises(L.LifecycleError):
        L.compute_editorial_hash({"title": "t", "tags": "not a list"})


def test_upload_manifest_is_frozen():
    manifest = L.UploadManifest(
        run_id="r1", video_hash="v", audio_chain_manifest_hash="a", thumbnail_hash="t",
        canonical_metadata_version="v1", current_editorial_hash="e", reviewed_editorial_hash="e",
        upload_policy_hash="p", channel_account_id="ch1", staged_video_path="/tmp/v.mp4",
        staged_thumbnail_path="/tmp/t.png", editorial_values={}, upload_policy_values={},
    )
    with pytest.raises(Exception):
        manifest.run_id = "r2"


# =============================================================================
# Text-based person-reference check (§1.13 step 6)
# =============================================================================

def test_mechanical_scan_word_boundary_does_not_false_positive_on_substring():
    """'Nam' không được khớp khi nằm DÍNH LIỀN bên trong 1 từ khác không
    có ranh giới (vd 'NamDinh' viết liền) -- nhưng 'Nam' như 1 TỪ ĐỘC LẬP
    (có khoảng trắng/dấu câu bao quanh) PHẢI khớp. Word-boundary-aware,
    không phải substring scan thô."""
    candidate = _candidate(named_individuals=[_named("Nam")])
    assert L._mechanical_person_reference_scan("Anh ta quê ở NamDinh.", candidate) == []
    assert L._mechanical_person_reference_scan("Nam là nghi phạm chính.", candidate) == ["Nam"]


def test_mechanical_scan_matches_short_form_alias():
    candidate = _candidate(named_individuals=[_named("Trương Văn Cam", alias="Năm Cam")])
    found = L._mechanical_person_reference_scan("Năm Cam bị bắt năm 2001.", candidate)
    assert found == ["Trương Văn Cam"]


def test_text_person_reference_check_passes_when_all_resolved(monkeypatch):
    candidate = _candidate(named_individuals=[_named("Nguyễn Văn A")])
    monkeypatch.setattr(L, "_run_codex", lambda prompt: _fake_json({"references": [{"text": "Nguyễn Văn A", "inferred_name": "Nguyễn Văn A"}]}))
    passed, evidence, entries = L.run_text_person_reference_check("Nguyễn Văn A phạm tội.", candidate, "phase_a_text")
    assert passed is True
    assert all(e.status == "RESOLVED" for e in entries)


def test_text_person_reference_check_fails_on_unresolved_reference(monkeypatch):
    """Đúng kịch bản round 1's Blocker: 1 reference LLM tìm được nhưng
    KHÔNG map được về named_individuals đã biết -> phải escalate, không
    được âm thầm bỏ qua."""
    candidate = _candidate(named_individuals=[_named("Nguyễn Văn A")])
    monkeypatch.setattr(L, "_run_codex", lambda prompt: _fake_json({"references": [{"text": "người đàn ông bí ẩn", "inferred_name": None}]}))
    passed, evidence, entries = L.run_text_person_reference_check("Một người đàn ông bí ẩn xuất hiện.", candidate, "phase_a_text")
    assert passed is False
    assert entries[0].status == "UNVETTED"


def test_text_person_reference_check_fails_closed_on_malformed_llm_response(monkeypatch):
    monkeypatch.setattr(L, "_run_codex", lambda prompt: "not json {{{")
    candidate = _candidate(named_individuals=[_named("A")])
    with pytest.raises(L.LifecycleError):
        L.run_text_person_reference_check("Văn bản.", candidate, "phase_a_text")


def test_text_person_reference_check_fails_closed_on_non_dict_reference_element(monkeypatch):
    monkeypatch.setattr(L, "_run_codex", lambda prompt: _fake_json({"references": ["not a dict"]}))
    candidate = _candidate(named_individuals=[_named("A")])
    with pytest.raises(L.LifecycleError):
        L.run_text_person_reference_check("Văn bản.", candidate, "phase_a_text")


def test_text_person_reference_check_rejects_empty_text():
    candidate = _candidate(named_individuals=[_named("A")])
    with pytest.raises(L.LifecycleError):
        L.run_text_person_reference_check("", candidate, "phase_a_text")


# =============================================================================
# Phase A final review orchestrator (§1.13 bước 4-7)
# =============================================================================

def _pass_c4_c7(monkeypatch):
    monkeypatch.setattr(L, "_score_c4_adversarial_text", lambda text, candidate: g.CriterionResult("C4", True, "ok", "llm_adversarial_review"))
    monkeypatch.setattr(L, "_score_c7_adversarial_text", lambda text, candidate: g.CriterionResult("C7", True, "ok", "llm_adversarial_review"))


def test_phase_a_final_review_fails_on_c4_failure(monkeypatch):
    monkeypatch.setattr(L, "_score_c4_adversarial_text", lambda text, candidate: g.CriterionResult("C4", False, "fail", "llm_adversarial_review"))
    candidate = _candidate()
    result = L.run_phase_a_final_review(candidate, "final script text", {"title": "t"})
    assert result.passed is False
    assert result.reason_code == "PHASE_A_C4_FAILED"
    assert result.reviewed_editorial_hash is None


def test_phase_a_final_review_fails_on_claim_gate_failure(monkeypatch):
    _pass_c4_c7(monkeypatch)
    monkeypatch.setattr(L, "score_claim_exposure_gate", lambda candidate, text: type("R", (), {"passed": False, "reason_code": "CLAIM_LEDGER_UNMAPPED", "evidence": "e", "claim_ledger": []})())
    candidate = _candidate()
    result = L.run_phase_a_final_review(candidate, "final script text", {"title": "t"})
    assert result.passed is False
    assert "CLAIM_GATE_CLAIM_LEDGER_UNMAPPED" in result.reason_code
    assert result.reviewed_editorial_hash is None


def test_phase_a_final_review_full_pass_persists_hash(monkeypatch):
    _pass_c4_c7(monkeypatch)
    monkeypatch.setattr(L, "score_claim_exposure_gate", lambda candidate, text: type("R", (), {"passed": True, "reason_code": None, "evidence": "e", "claim_ledger": []})())
    monkeypatch.setattr(L, "run_text_person_reference_check", lambda text, candidate, phase: (True, "ok", []))
    candidate = _candidate(named_individuals=[])
    editorial = {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}
    result = L.run_phase_a_final_review(candidate, "final script text", editorial)
    assert result.passed is True
    assert result.reviewed_editorial_hash == L.compute_editorial_hash(editorial)


def test_phase_a_final_review_fails_on_unresolved_person_reference(monkeypatch):
    _pass_c4_c7(monkeypatch)
    monkeypatch.setattr(L, "score_claim_exposure_gate", lambda candidate, text: type("R", (), {"passed": True, "reason_code": None, "evidence": "e", "claim_ledger": []})())
    monkeypatch.setattr(L, "run_text_person_reference_check", lambda text, candidate, phase: (False, "unresolved", [g.FinalReferenceEntry("X", None, "llm_coreference", "UNVETTED", phase)]))
    candidate = _candidate()
    result = L.run_phase_a_final_review(candidate, "final script text", {"title": "t"})
    assert result.passed is False
    assert result.reason_code == "UNVETTED_PERSON_REFERENCE"
    assert result.reviewed_editorial_hash is None


def test_phase_a_final_review_reruns_c6_and_fails_if_c6_fails(monkeypatch):
    _pass_c4_c7(monkeypatch)
    monkeypatch.setattr(L, "score_claim_exposure_gate", lambda candidate, text: type("R", (), {"passed": True, "reason_code": None, "evidence": "e", "claim_ledger": []})())
    person = _named("Nguyễn Văn A", role="acquitted")  # role != convicted_perpetrator, chưa cross-verified -> C6 fail
    monkeypatch.setattr(L, "run_text_person_reference_check", lambda text, candidate, phase: (
        True, "ok", [g.FinalReferenceEntry("Nguyễn Văn A", "Nguyễn Văn A", "mechanical_alias_scan", "RESOLVED", phase)],
    ))
    candidate = _candidate(named_individuals=[person])
    result = L.run_phase_a_final_review(candidate, "final script text", {"title": "t"})
    assert result.passed is False
    assert result.reason_code == "PHASE_A_C6_FAILED"


def test_phase_a_final_review_rejects_empty_final_script():
    candidate = _candidate()
    result = L.run_phase_a_final_review(candidate, "", {"title": "t"})
    assert result.passed is False
    assert result.reason_code == "PHASE_A_INVALID_INPUT"


def test_phase_a_final_review_rejects_non_dict_editorial():
    candidate = _candidate()
    result = L.run_phase_a_final_review(candidate, "script", "not a dict")
    assert result.passed is False
    assert result.reason_code == "PHASE_A_INVALID_INPUT"


# =============================================================================
# Audio chain-of-custody -- ffmpeg THẬT (fixture WAV/MP4 nhỏ, tạo qua
# lavfi, không phải giả lập/mock).
# =============================================================================

FFMPEG_AVAILABLE = L.VENDORED_FFMPEG.exists() and L.VENDORED_FFPROBE.exists()
pytestmark_ffmpeg = pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="vendored ffmpeg/ffprobe không có mặt trong checkout này")


def _make_tone_wav(path: Path, freq: int, duration_s: float):
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-f", "lavfi",
        "-i", f"sine=frequency={freq}:duration={duration_s}",
        "-ar", "48000", "-ac", "1", str(path),
    ], check=True)


def _make_video_with_audio(path: Path, wav_path: Path, duration_s: float):
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-f", "lavfi",
        "-i", f"color=c=black:s=320x240:d={duration_s}", "-i", str(wav_path),
        "-c:v", "libx264", "-c:a", "aac", "-shortest", str(path),
    ], check=True)


@pytestmark_ffmpeg
def test_audio_chain_full_round_trip_passes(tmp_path):
    seg1 = tmp_path / "seg1.wav"
    seg2 = tmp_path / "seg2.wav"
    _make_tone_wav(seg1, 440, 1.0)
    _make_tone_wav(seg2, 880, 1.0)
    scripts = ["Câu đầu tiên.", "Câu thứ hai."]

    segments = L.record_expected_segments(scripts, [seg1, seg2])
    assert len(segments) == 2
    assert segments[0].script_text_hash == L._script_text_hash("Câu đầu tiên.")

    narration_stem_hash = L.compute_narration_stem_hash([seg1, seg2])
    concatenated = tmp_path / "narration.wav"
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-i", str(seg1), "-i", str(seg2),
        "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]", "-map", "[out]",
        "-ar", "48000", "-ac", "1", str(concatenated),
    ], check=True)
    ok, msg = L.verify_narration_stem_before_mix(concatenated, narration_stem_hash)
    assert ok, msg

    mixed = tmp_path / "mixed.mp4"
    _make_video_with_audio(mixed, concatenated, 2.0)
    mix_manifest = L.record_mix_manifest(narration_stem_hash, None, mixed, "test-mix-v1")

    final_video = mixed  # trong test này "mix" và "final" là 1 (không burn-in riêng)
    ok, msg = L.verify_phase_c_audio_chain(final_video, segments, mix_manifest, "Câu đầu tiên. Câu thứ hai.", narration_stem_hash)
    assert ok, msg


@pytestmark_ffmpeg
def test_audio_chain_detects_mismatched_mix_manifest_narration_stem(tmp_path):
    """Regression cho Blocker #2 (review độc lập agy/Gemini): mix_manifest
    thuộc 1 narration KHÁC (narration_stem_hash khác) với expected_segments
    đang xét PHẢI bị phát hiện -- kể cả khi final_audio_hash và script-to-
    segment binding riêng lẻ đều "khớp" (dựng bằng cùng seg1 để cô lập
    đúng 1 biến: narration_stem_hash bị làm giả)."""
    seg1 = tmp_path / "seg1.wav"
    _make_tone_wav(seg1, 440, 1.0)
    segments = L.record_expected_segments(["Câu gốc."], [seg1])
    real_narration_stem_hash = L.compute_narration_stem_hash([seg1])
    mixed = tmp_path / "mixed.mp4"
    _make_video_with_audio(mixed, seg1, 1.0)
    mix_manifest = L.record_mix_manifest(real_narration_stem_hash, None, mixed, "test-mix-v1")

    fake_expected_narration_stem_hash = "0" * 64  # giả lập "expected" thuộc 1 run/case khác hẳn
    ok, msg = L.verify_phase_c_audio_chain(mixed, segments, mix_manifest, "Câu gốc.", fake_expected_narration_stem_hash)
    assert not ok, "mix_manifest.narration_stem_hash lệch với expected_narration_stem_hash PHẢI bị phát hiện, không được PASS."


@pytestmark_ffmpeg
def test_audio_chain_detects_reordered_segments(tmp_path):
    """Đúng kịch bản round-5 Blocker B2's failure mode: 2 segment ĐỔI CHỖ
    (cùng tổng thời lượng) PHẢI bị phát hiện -- không phải duration-only."""
    seg1 = tmp_path / "seg1.wav"
    seg2 = tmp_path / "seg2.wav"
    _make_tone_wav(seg1, 440, 1.0)
    _make_tone_wav(seg2, 880, 1.0)
    scripts = ["Câu đầu tiên.", "Câu thứ hai."]
    segments = L.record_expected_segments(scripts, [seg1, seg2])
    narration_stem_hash = L.compute_narration_stem_hash([seg1, seg2])

    # Ghép SAI THỨ TỰ (seg2 trước seg1) -- cùng tổng thời lượng.
    reordered = tmp_path / "reordered.wav"
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-i", str(seg2), "-i", str(seg1),
        "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]", "-map", "[out]",
        "-ar", "48000", "-ac", "1", str(reordered),
    ], check=True)
    ok, msg = L.verify_narration_stem_before_mix(reordered, narration_stem_hash)
    assert not ok, "Reordered narration PHẢI bị phát hiện lệch hash, không được PASS."


@pytestmark_ffmpeg
def test_audio_chain_detects_script_segment_mismatch(tmp_path):
    """script-to-segment binding (fixes round-6 High H1): reviewed script
    KHÁC với script đã ghi trong expected_segments -> phải fail, dù audio
    hash vẫn khớp."""
    seg1 = tmp_path / "seg1.wav"
    _make_tone_wav(seg1, 440, 1.0)
    segments = L.record_expected_segments(["Câu gốc."], [seg1])
    narration_stem_hash = L.compute_narration_stem_hash([seg1])
    mixed = tmp_path / "mixed.mp4"
    _make_video_with_audio(mixed, seg1, 1.0)
    mix_manifest = L.record_mix_manifest(narration_stem_hash, None, mixed, "test-mix-v1")

    ok, msg = L.verify_phase_c_audio_chain(mixed, segments, mix_manifest, "Câu HOÀN TOÀN KHÁC.", narration_stem_hash)
    assert not ok, "Script khác script đã ghi PHẢI bị phát hiện (script-to-segment binding)."


def test_record_expected_segments_rejects_length_mismatch():
    with pytest.raises(L.LifecycleError):
        L.record_expected_segments(["a", "b"], ["/tmp/only_one.wav"])


def test_record_expected_segments_rejects_empty():
    with pytest.raises(L.LifecycleError):
        L.record_expected_segments([], [])


# =============================================================================
# Frame sampling + OCR (§1.13 step 10-11) -- ffmpeg/Tesseract THẬT.
# =============================================================================

@pytestmark_ffmpeg
def test_sample_frame_timestamps_excludes_exact_duration_boundary(tmp_path):
    """Bug thật tự bắt qua smoke test trước khi ship (không phải Codex
    round): timestamp == video_duration_s không có frame giải mã được --
    xác nhận sample_frame_timestamps() không bao giờ trả điểm đó nữa."""
    video = tmp_path / "plain.mp4"
    subprocess.run([str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-f", "lavfi",
                     "-i", "color=c=black:s=64x64:d=2", "-c:v", "libx264", str(video)], check=True)
    ts = L.sample_frame_timestamps(2.0, [], video)
    assert all(t < 2.0 for t in ts), f"Không được có timestamp >= video_duration_s trong {ts}"
    assert max(ts) > 1.9  # vẫn phải lấy mẫu SÁT cuối video, không cắt bớt quá tay


@pytestmark_ffmpeg
def test_sample_and_ocr_frames_reads_burned_in_text(tmp_path):
    """End-to-end thật: video có chữ burn-in -> OCR (Tesseract vie+eng)
    đọc lại đúng chữ đó trên MỌI frame lấy mẫu."""
    video = tmp_path / "text.mp4"
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-f", "lavfi",
        "-i", "color=c=white:s=640x360:d=1.5",
        "-vf", "drawtext=text='NGUYEN VAN A':fontcolor=black:fontsize=48:x=50:y=150",
        "-c:v", "libx264", str(video),
    ], check=True)
    ts = L.sample_frame_timestamps(1.5, [], video)
    samples = L.sample_and_ocr_frames(video, ts, tmp_path / "frames")
    assert samples
    assert all("NGUYEN VAN A" in s.ocr_text.upper() for s in samples)


def test_sample_frame_timestamps_rejects_non_positive_duration():
    with pytest.raises(L.LifecycleError):
        L.sample_frame_timestamps(0, [], "/tmp/x.mp4")


def test_run_visual_person_reference_check_escalates_unknown_name(monkeypatch):
    """Regression: bản đầu chỉ chạy mechanical scan (CHỈ tìm tên ĐÃ BIẾT
    -- không bao giờ có thể trả UNVETTED, PASS-oan cấu trúc, tự bắt qua
    test này trước khi ship). Giờ dùng chung run_text_person_reference_check
    (mechanical + LLM coreference thật) nên PHẢI phát hiện được tên MỚI."""
    candidate = _candidate(named_individuals=[_named("Nguyễn Văn A")])
    monkeypatch.setattr(L, "_run_codex", lambda prompt: _fake_json({"references": [{"text": "Trần Thị B", "inferred_name": "Trần Thị B"}]}))
    unknown_sample = L.FrameSample(timestamp_s=0.0, frame_path="/tmp/f.png", pixel_hash="h", ocr_text="Trần Thị B xuất hiện")
    passed, evidence, entries = L.run_visual_person_reference_check([unknown_sample], candidate)
    assert passed is False
    assert any(e.status == "UNVETTED" for e in entries)


def test_run_visual_person_reference_check_passes_for_known_individuals(monkeypatch):
    candidate = _candidate(named_individuals=[_named("Nguyễn Văn A")])
    monkeypatch.setattr(L, "_run_codex", lambda prompt: _fake_json({"references": [{"text": "Nguyễn Văn A", "inferred_name": "Nguyễn Văn A"}]}))
    sample = L.FrameSample(timestamp_s=0.0, frame_path="/tmp/f.png", pixel_hash="h", ocr_text="Nguyễn Văn A")
    passed, evidence, entries = L.run_visual_person_reference_check([sample], candidate)
    assert passed is True


def test_run_visual_person_reference_check_empty_ocr_text_short_circuits():
    """Không có text nào đọc được (mọi frame OCR ra rỗng) -> PASS ngay,
    KHÔNG gọi LLM (tránh phí request cho input rỗng vô nghĩa)."""
    candidate = _candidate(named_individuals=[])
    empty_sample = L.FrameSample(timestamp_s=0.0, frame_path="/tmp/f.png", pixel_hash="h", ocr_text="   ")
    passed, evidence, entries = L.run_visual_person_reference_check([empty_sample], candidate)
    assert passed is True
    assert entries == []


# =============================================================================
# Phase D -- §1.13 bước 14-20. Trước bản fix này CHƯA có test nào (gap
# thật, review độc lập agy/Gemini không bắt được vì nó review code chứ
# không tính coverage -- tự phát hiện khi rà lại trước khi ship).
# =============================================================================

def test_determine_revalidation_restart_text_change_routes_phase_a():
    assert L.determine_revalidation_restart({"title_changed": True}) == L.RESTART_PHASE_A


def test_determine_revalidation_restart_legal_status_change_routes_phase_a():
    """Regression cho High #3 (review độc lập agy/Gemini): legal_status/
    evidence/reference_inventory đổi PHẢI route Phase A, không rơi qua mọi
    nhánh rồi trả None."""
    assert L.determine_revalidation_restart({"legal_status_changed": True}) == L.RESTART_PHASE_A
    assert L.determine_revalidation_restart({"evidence_changed": True}) == L.RESTART_PHASE_A
    assert L.determine_revalidation_restart({"reference_inventory_changed": True}) == L.RESTART_PHASE_A


def test_determine_revalidation_restart_video_change_routes_phase_c_full():
    assert L.determine_revalidation_restart({"video_or_audio_changed": True}) == L.RESTART_PHASE_C_FULL


def test_determine_revalidation_restart_thumbnail_image_only_routes_phase_c_visual():
    assert L.determine_revalidation_restart({"thumbnail_image_changed": True}) == L.RESTART_PHASE_C_VISUAL


def test_determine_revalidation_restart_policy_change_routes_upload_policy_only():
    assert L.determine_revalidation_restart({"schedule_changed": True}) == L.RESTART_UPLOAD_POLICY_ONLY


def test_determine_revalidation_restart_no_change_returns_none():
    assert L.determine_revalidation_restart({"title_changed": False, "schedule_changed": False}) is None
    assert L.determine_revalidation_restart({}) is None


def test_determine_revalidation_restart_unknown_key_fails_closed():
    """Regression cho High #3's fail-closed fix: key KHÔNG xác định được
    (dù giá trị gì) PHẢI raise, không được âm thầm coi là vô hại."""
    with pytest.raises(L.LifecycleError):
        L.determine_revalidation_restart({"some_unknown_field_changed": True})
    with pytest.raises(L.LifecycleError):
        L.determine_revalidation_restart({"some_unknown_field_changed": False})


def test_determine_revalidation_restart_rejects_non_dict():
    with pytest.raises(L.LifecycleError):
        L.determine_revalidation_restart("not a dict")


def test_validate_upload_policy_passes_matching_channel():
    ok, msg = L.validate_upload_policy({"channel_account_id": "ch1"}, "ch1")
    assert ok is True


def test_validate_upload_policy_fails_wrong_channel():
    ok, msg = L.validate_upload_policy({"channel_account_id": "ch2"}, "ch1")
    assert ok is False


def test_validate_upload_policy_rejects_non_dict():
    ok, msg = L.validate_upload_policy("not a dict", "ch1")
    assert ok is False


def test_stage_artifacts_exclusive_and_assemble_manifest_round_trip(tmp_path):
    video_src = tmp_path / "video.mp4"
    thumb_src = tmp_path / "thumb.png"
    video_src.write_bytes(b"fake video bytes " * 1000)
    thumb_src.write_bytes(b"fake thumb bytes")
    staging_dir = tmp_path / "staging"

    staged_video, staged_thumb = L.stage_artifacts_exclusive("run1", video_src, thumb_src, staging_dir)
    assert Path(staged_video).exists()
    assert Path(staged_thumb).exists()
    # chmod read-only -- xác nhận thật (fixes §1.13 step 17's yêu cầu)
    assert not (os.access(staged_video, os.W_OK))

    editorial = {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}
    reviewed_hash = L.compute_editorial_hash(editorial)
    result = L.assemble_upload_manifest(
        "run1", staged_video, staged_thumb, "audiohash123",
        editorial, reviewed_hash,
        {"channel_account_id": "ch1", "scheduling": "s", "privacy_setting": "public", "upload_operation_mode": "auto"}, "ch1",
    )
    assert result.passed is True
    assert result.manifest.video_hash == L._hash_file_chunked(Path(staged_video))


def test_assemble_upload_manifest_fails_on_editorial_changed_since_review(tmp_path):
    """Regression cho Blocker #1's spirit -- Phase D's chính nó đóng vai
    trò lớp phòng thủ cuối nếu editorial bị đổi SAU khi Phase A review."""
    video_src = tmp_path / "video.mp4"
    thumb_src = tmp_path / "thumb.png"
    video_src.write_bytes(b"video")
    thumb_src.write_bytes(b"thumb")
    staged_video, staged_thumb = L.stage_artifacts_exclusive("run2", video_src, thumb_src, tmp_path / "staging")

    reviewed_hash = L.compute_editorial_hash({"title": "Title A"})
    current_editorial = {"title": "Title B (bị đổi sau review)"}  # khác bản đã review
    result = L.assemble_upload_manifest(
        "run2", staged_video, staged_thumb, "audiohash123",
        current_editorial, reviewed_hash,
        {"channel_account_id": "ch1"}, "ch1",
    )
    assert result.passed is False
    assert result.reason_code == "EDITORIAL_CHANGED_SINCE_REVIEW"


def test_stage_artifacts_exclusive_rejects_reuse_of_same_run_id(tmp_path):
    video_src = tmp_path / "video.mp4"
    thumb_src = tmp_path / "thumb.png"
    video_src.write_bytes(b"video")
    thumb_src.write_bytes(b"thumb")
    staging_dir = tmp_path / "staging"
    L.stage_artifacts_exclusive("dup_run", video_src, thumb_src, staging_dir)
    with pytest.raises(L.LifecycleError):
        L.stage_artifacts_exclusive("dup_run", video_src, thumb_src, staging_dir)


def test_stage_artifacts_exclusive_cleans_up_orphan_on_partial_failure(tmp_path):
    """Regression cho Medium #8 (review độc lập agy/Gemini): video stage
    THÀNH CÔNG nhưng thumbnail nguồn KHÔNG tồn tại -- file video đã tạo
    PHẢI được dọn dẹp, không để lại mồ côi khiến retry cùng run_id kẹt ở
    FileExistsError dù chưa có staging thành công trọn vẹn nào."""
    video_src = tmp_path / "video.mp4"
    video_src.write_bytes(b"video")
    missing_thumb_src = tmp_path / "does_not_exist.png"
    staging_dir = tmp_path / "staging"

    with pytest.raises(L.LifecycleError):
        L.stage_artifacts_exclusive("orphan_run", video_src, missing_thumb_src, staging_dir)

    leftover = list(staging_dir.glob("orphan_run_*")) if staging_dir.exists() else []
    assert leftover == [], f"Không được để lại file mồ côi sau staging thất bại: {leftover}"

    # Retry CÙNG run_id (bây giờ có thumbnail thật) PHẢI thành công -- xác
    # nhận trực tiếp rằng orphan cleanup thật sự mở khoá được retry.
    real_thumb_src = tmp_path / "thumb.png"
    real_thumb_src.write_bytes(b"thumb")
    staged_video, staged_thumb = L.stage_artifacts_exclusive("orphan_run", video_src, real_thumb_src, staging_dir)
    assert Path(staged_video).exists()
    assert Path(staged_thumb).exists()


def test_safe_upload_calls_upload_fn_with_verified_bytes(tmp_path):
    video_src = tmp_path / "video.mp4"
    thumb_src = tmp_path / "thumb.png"
    video_src.write_bytes(b"real video content")
    thumb_src.write_bytes(b"real thumb content")
    staged_video, staged_thumb = L.stage_artifacts_exclusive("upload_run", video_src, thumb_src, tmp_path / "staging")

    manifest = L.UploadManifest(
        run_id="upload_run", video_hash=L._hash_file_chunked(Path(staged_video)),
        audio_chain_manifest_hash="a", thumbnail_hash=__import__("hashlib").sha256(Path(staged_thumb).read_bytes()).hexdigest(),
        canonical_metadata_version="v1", current_editorial_hash="e", reviewed_editorial_hash="e",
        upload_policy_hash="p", channel_account_id="ch1",
        staged_video_path=staged_video, staged_thumbnail_path=staged_thumb,
        editorial_values={"title": "t"}, upload_policy_values={"channel_account_id": "ch1"},
    )
    captured = {}

    def fake_upload_fn(video_fileobj, thumbnail_bytes, editorial_values, upload_policy_values):
        captured["video_bytes"] = video_fileobj.read()
        captured["thumbnail_bytes"] = thumbnail_bytes
        return "fake_video_id"

    result = L.safe_upload(manifest, fake_upload_fn, tmp_path / "locks")
    assert result == "fake_video_id"
    assert captured["video_bytes"] == b"real video content"
    assert captured["thumbnail_bytes"] == b"real thumb content"


def test_safe_upload_fails_closed_on_thumbnail_hash_mismatch(tmp_path):
    """check-to-use gap thật: thumbnail bị đổi SAU khi manifest ghi hash
    (mô phỏng bằng cách cố tình đưa hash SAI trong manifest)."""
    video_src = tmp_path / "video.mp4"
    thumb_src = tmp_path / "thumb.png"
    video_src.write_bytes(b"video")
    thumb_src.write_bytes(b"thumb")
    staged_video, staged_thumb = L.stage_artifacts_exclusive("bad_run", video_src, thumb_src, tmp_path / "staging")

    manifest = L.UploadManifest(
        run_id="bad_run", video_hash=L._hash_file_chunked(Path(staged_video)),
        audio_chain_manifest_hash="a", thumbnail_hash="0" * 64,  # SAI cố tình
        canonical_metadata_version="v1", current_editorial_hash="e", reviewed_editorial_hash="e",
        upload_policy_hash="p", channel_account_id="ch1",
        staged_video_path=staged_video, staged_thumbnail_path=staged_thumb,
        editorial_values={}, upload_policy_values={},
    )
    with pytest.raises(L.LifecycleError):
        L.safe_upload(manifest, lambda *a: "should_not_reach_here", tmp_path / "locks")


# =============================================================================
# thumbnail_path=None (task #241 tiếp -- wiring vào short_batch_runner.py's
# CL Short): CL Short không có thumbnail asset riêng nào (khác Long-form,
# task #132), khác giả định ban đầu của Phase D. Regression cho adaptation
# này -- KHÔNG được lặng lẽ coi thumbnail "bị thiếu" giống lỗi thật.
# =============================================================================

def test_stage_artifacts_exclusive_with_thumbnail_none_stages_video_only(tmp_path):
    video_src = tmp_path / "video.mp4"
    video_src.write_bytes(b"video only, no thumbnail asset for this content type")
    staging_dir = tmp_path / "staging"

    staged_video, staged_thumb = L.stage_artifacts_exclusive("no_thumb_run", video_src, None, staging_dir)
    assert Path(staged_video).exists()
    assert staged_thumb is None
    assert list(staging_dir.glob("no_thumb_run_thumbnail*")) == []


def test_assemble_upload_manifest_with_thumbnail_none(tmp_path):
    video_src = tmp_path / "video.mp4"
    video_src.write_bytes(b"video")
    staged_video, staged_thumb = L.stage_artifacts_exclusive("no_thumb_manifest", video_src, None, tmp_path / "staging")
    assert staged_thumb is None

    editorial = {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}
    reviewed_hash = L.compute_editorial_hash(editorial)
    result = L.assemble_upload_manifest(
        "no_thumb_manifest", staged_video, staged_thumb, "audiohash123",
        editorial, reviewed_hash,
        {"channel_account_id": "ch1", "scheduling": "s", "privacy_setting": "private", "upload_operation_mode": "auto"}, "ch1",
    )
    assert result.passed is True
    assert result.manifest.thumbnail_hash is None
    assert result.manifest.staged_thumbnail_path is None


def test_safe_upload_with_thumbnail_none_passes_none_bytes_to_upload_fn(tmp_path):
    video_src = tmp_path / "video.mp4"
    video_src.write_bytes(b"real video content, no thumbnail")
    staged_video, staged_thumb = L.stage_artifacts_exclusive("no_thumb_upload", video_src, None, tmp_path / "staging")
    assert staged_thumb is None

    manifest = L.UploadManifest(
        run_id="no_thumb_upload", video_hash=L._hash_file_chunked(Path(staged_video)),
        audio_chain_manifest_hash="a", thumbnail_hash=None,
        canonical_metadata_version="v1", current_editorial_hash="e", reviewed_editorial_hash="e",
        upload_policy_hash="p", channel_account_id="ch1",
        staged_video_path=staged_video, staged_thumbnail_path=None,
        editorial_values={"title": "t"}, upload_policy_values={"channel_account_id": "ch1"},
    )
    captured = {}

    def fake_upload_fn(video_fileobj, thumbnail_bytes, editorial_values, upload_policy_values):
        captured["video_bytes"] = video_fileobj.read()
        captured["thumbnail_bytes"] = thumbnail_bytes
        return "fake_video_id_no_thumb"

    result = L.safe_upload(manifest, fake_upload_fn, tmp_path / "locks")
    assert result == "fake_video_id_no_thumb"
    assert captured["video_bytes"] == b"real video content, no thumbnail"
    assert captured["thumbnail_bytes"] is None


def test_stage_artifacts_exclusive_thumbnail_path_given_but_missing_still_fails_closed(tmp_path):
    """thumbnail_path=None nghĩa là 'content type này không có thumbnail'
    -- KHÁC HẲN 'truyền path nhưng file không tồn tại' (vẫn phải fail-closed
    như trước, không được lặng lẽ coi 2 trường hợp là một)."""
    video_src = tmp_path / "video.mp4"
    video_src.write_bytes(b"video")
    missing_thumb = tmp_path / "does_not_exist.png"
    with pytest.raises(L.LifecycleError):
        L.stage_artifacts_exclusive("still_fail_closed", video_src, missing_thumb, tmp_path / "staging")
