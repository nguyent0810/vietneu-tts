"""CL Risk Gate Stage 3 (task #241) -- test cho CL branch wiring vào
short_batch_runner.py's process_one_segment() (bước 1 sidecar-gate, bước 4
skip-SEO-regenerate, bước 5 Phase C/D wrap) + _run_cl_phase_c_d_and_upload()
(N=1 audio custody chain composition thật). KHÔNG re-test lại nội bộ
cl_risk_gate_lifecycle.py's primitives (đã có 58 test riêng, real ffmpeg/
Tesseract) -- chỉ test GLUE code mới của increment này."""
import json
import subprocess
from pathlib import Path

import pytest

import short_batch_runner as sbr
import cl_risk_gate_lifecycle as L


CL_TOPIC = "Hình Sự"


def _base_seg(episode="CLGATE_case001", idx=1):
    return {"key": f"{episode}_{idx:02d}", "episode": episode, "segment_index": idx, "text": "Câu một. Câu hai."}


def _seed_registry_on_disk(tmp_path, registry: dict):
    """process_one_segment() so known_status với load_registry(topic) TƯƠI
    trên đĩa (chống 2 tiến trình cùng đụng 1 đoạn, xem docstring hàm đó) --
    test PHẢI seed registry THẬT trên đĩa, không chỉ truyền dict trong bộ
    nhớ, nếu không sẽ bị nhánh guard đó coi là 'tiến trình khác vừa đổi
    status' và bail ra ngay (fresh_status=None do file rỗng != known_status)."""
    (tmp_path / "registry.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")


def _write_sidecar(tmp_path, episode, sidecar: dict):
    sd_path = tmp_path / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short" / f"{episode}_Short.cl_meta.json"
    sd_path.parent.mkdir(parents=True, exist_ok=True)
    sd_path.write_text(json.dumps(sidecar, ensure_ascii=False), encoding="utf-8")
    return sd_path


# =============================================================================
# Bước 1 -- sidecar gate (fail-closed nếu thiếu/hỏng, khác hẳn nhánh
# "topic != DEFAULT_TOPIC" chung dùng thẳng seg["text"]).
# =============================================================================

def test_step1_cl_no_sidecar_fails_closed_to_needs_review(tmp_path, monkeypatch):
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")

    def _fail_if_called(*a, **k):
        raise AssertionError("run_tts KHÔNG được gọi khi sidecar thiếu (fail-closed PHẢI dừng ở bước 1)")
    monkeypatch.setattr(sbr, "run_tts", _fail_if_called)

    seg = _base_seg()
    registry = {}
    entry = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                     registry, None, 8, False, CL_TOPIC)

    assert entry["status"] == "needs_review"
    assert "sidecar" in entry["needs_human_review_cl_gate"].lower()


def test_step1_cl_sidecar_missing_required_field_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **k: (_ for _ in ()).throw(AssertionError("không được gọi")))
    seg = _base_seg()
    _write_sidecar(tmp_path, seg["episode"], {"case_id": "case001", "final_editorial": {}})  # thiếu reviewed_editorial_hash/named_individuals
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    # cl_metadata_sidecar_path đọc từ short_segment_discovery's PROJECT_ROOT
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    entry = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                     {}, None, 8, False, CL_TOPIC)
    assert entry["status"] == "needs_review"
    assert "thiếu field" in entry["needs_human_review_cl_gate"]


def test_step1_cl_script_hash_mismatch_fails_closed(tmp_path, monkeypatch):
    """Regression THẬT cho HIGH #1 (review độc lập Cursor/Grok): reviewed_
    editorial_hash CHỈ cover title/description/tags/thumbnail_brief, KHÔNG
    cover final_script -- nếu file .txt bundle bị đổi SAU KHI cl_case_batch.py
    ghi sidecar (thủ công/nhầm lẫn), trước fix vẫn qua được gate vì sidecar
    "hợp lệ". Giờ so khớp TRỰC TIẾP hash script."""
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **k: (_ for _ in ()).throw(AssertionError("không được gọi")))
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    seg = _base_seg()
    sidecar = {
        "case_id": "case001", "reviewed_editorial_hash": "abc123",
        "reviewed_script_hash": L._script_text_hash("Script GỐC đã qua Phase A review."),
        "final_editorial": {"title": "T", "description": "D", "tags": ["a"], "thumbnail_brief": "B"},
        "named_individuals": [],
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)
    # seg["text"] (từ _base_seg()) KHÁC hẳn script đã hash trong sidecar --
    # mô phỏng file .txt bundle bị đổi SAU khi sidecar được ghi.

    entry = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                     {}, None, 8, False, CL_TOPIC)
    assert entry["status"] == "needs_review"
    assert "KHÔNG khớp reviewed_script_hash" in entry["needs_human_review_cl_gate"]


def test_step1_cl_valid_sidecar_persists_fields_and_advances_to_scripted(tmp_path, monkeypatch):
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    seg = _base_seg()
    sidecar = {
        "case_id": "case001", "reviewed_editorial_hash": "abc123",
        "reviewed_script_hash": L._script_text_hash(seg["text"]),
        "final_editorial": {"title": "T", "description": "D", "tags": ["a"], "thumbnail_brief": "B"},
        "named_individuals": [{"canonical_name": "Nguyễn Văn A", "short_form_alias": None, "role": "victim"}],
    }
    _write_sidecar(tmp_path, seg["episode"], sidecar)

    class _StopAfterStep1(Exception):
        pass

    def _run_tts_marker(*a, **k):
        raise _StopAfterStep1("step1 xong, dừng tại đây có chủ đích")
    monkeypatch.setattr(sbr, "run_tts", _run_tts_marker)

    registry = {}
    with pytest.raises(_StopAfterStep1):
        sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                 registry, None, 8, False, CL_TOPIC)

    entry = registry[seg["key"]]
    assert entry["status"] == "scripted"
    assert entry["final_script"] == seg["text"]
    assert entry["cl_case_id"] == "case001"
    assert entry["cl_reviewed_editorial_hash"] == "abc123"
    assert entry["cl_reviewed_script_hash"] == sidecar["reviewed_script_hash"]
    assert entry["cl_final_editorial"] == sidecar["final_editorial"]
    assert entry["cl_named_individuals"] == sidecar["named_individuals"]
    assert entry["needs_human_review_hook"] is False


# =============================================================================
# Bước 4 -- SEO KHÔNG được regenerate cho CL (dùng thẳng cl_final_editorial
# đã qua Phase A review, giữ NGUYÊN VĂN không nối attribution BGM).
# =============================================================================

def test_step4_cl_does_not_regenerate_seo_and_keeps_editorial_verbatim(tmp_path, monkeypatch):
    """Regression cho bug thật tự bắt: block phòng thủ CHUNG ở bước 5 ("bổ
    sung ghi nguồn BGM còn thiếu") chạy VÔ ĐIỀU KIỆN trước increment này --
    với CL, nó mutate entry["seo"]["description"] TRƯỚC khi Phase D hash-
    check, làm current_editorial_hash lệch reviewed_editorial_hash cho MỌI
    CL Short có BGM (false EDITORIAL_CHANGED_SINCE_REVIEW). Test này xác
    nhận cả 2: SEO không regenerate (bước 4) VÀ entry["seo"] vẫn nguyên văn
    ngay tại điểm gọi Phase C/D (bước 5), không bị patch BGM ở giữa."""
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "_asset_safety_block_reason", lambda seg_dir, video_path: None)
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    def _fail_if_called(*a, **k):
        raise AssertionError("generate_short_seo_with_review KHÔNG được gọi cho CL (đã qua Phase A review)")
    monkeypatch.setattr(sbr, "generate_short_seo_with_review", _fail_if_called)

    def _run_video_render_marker(*a, **k):
        raise AssertionError("không nên tới render lại -- status đã video_ready")
    monkeypatch.setattr(sbr, "run_video_render", _run_video_render_marker)

    captured = {}
    def _fake_phase_c_d(entry, seg_dir, wav_path, video_path, credentials_path, publish_at):
        captured["seo_snapshot"] = dict(entry["seo"])
        return True, "mocked pass", "fake_video_id"
    monkeypatch.setattr(sbr, "_run_cl_phase_c_d_and_upload", _fake_phase_c_d)

    final_editorial = {"title": "T", "description": "D (không có attribution)", "tags": ["a", "b"], "thumbnail_brief": "B"}
    seg = _base_seg()
    reviewed_script_hash = L._script_text_hash(seg["text"])
    registry = {seg["key"]: {
        "key": seg["key"], "episode": seg["episode"], "segment_index": seg["segment_index"],
        "status": "video_ready", "final_script": seg["text"], "video_path": str(tmp_path / "v.mp4"),
        "cl_case_id": "case001", "cl_reviewed_editorial_hash": "abc123",
        "cl_reviewed_script_hash": reviewed_script_hash,
        "cl_final_editorial": final_editorial, "cl_named_individuals": [],
        "bgm": {"path": "/x.mp3", "attribution": "Nhạc nền: X"},
    }}
    (tmp_path / "v.mp4").write_bytes(b"fake")
    _seed_registry_on_disk(tmp_path, registry)
    _write_sidecar(tmp_path, seg["episode"], {
        "case_id": "case001", "reviewed_editorial_hash": "abc123", "reviewed_script_hash": reviewed_script_hash,
        "final_editorial": final_editorial, "named_individuals": [],
    })

    entry = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                     registry, None, 8, False, CL_TOPIC)

    assert entry["status"] == "uploaded"
    assert entry["seo"] == final_editorial, "entry['seo'] phải giữ NGUYÊN VĂN cl_final_editorial ngay sau bước 4"
    assert captured["seo_snapshot"] == final_editorial, (
        "entry['seo'] bị mutate (vd nối attribution BGM) TRƯỚC khi gọi Phase C/D -- "
        "sẽ làm current_editorial_hash lệch reviewed_editorial_hash"
    )
    assert entry["needs_human_review_seo"] is False


# =============================================================================
# Bước 5 -- upload thật cho CL PHẢI đi qua _run_cl_phase_c_d_and_upload(),
# không gọi upload_short() trực tiếp.
# =============================================================================

def _seo_ready_entry(seg, tmp_path):
    editorial = {"title": "T", "description": "D", "tags": ["a"], "thumbnail_brief": "B"}
    return {
        "key": seg["key"], "episode": seg["episode"], "segment_index": seg["segment_index"],
        "status": "seo_ready", "final_script": seg["text"], "video_path": str(tmp_path / "v.mp4"),
        "seo": dict(editorial),
        "cl_case_id": "case001", "cl_reviewed_editorial_hash": "abc123",
        "cl_reviewed_script_hash": L._script_text_hash(seg["text"]),
        "cl_final_editorial": editorial,
        "cl_named_individuals": [], "needs_human_review_hook": False, "needs_human_review_seo": False,
        "bgm": None,
    }


def _seed_matching_sidecar(tmp_path, seg, entry):
    """Bước 5 giờ re-check sidecar TRỰC TIẾP ngay trước Phase C/D (MEDIUM
    #1 fix) -- test PHẢI ghi 1 sidecar THẬT khớp entry, không chỉ seed
    registry, nếu không sẽ bị nhánh re-check này chặn trước khi tới được
    phần đang test (_run_cl_phase_c_d_and_upload mock)."""
    _write_sidecar(tmp_path, seg["episode"], {
        "case_id": entry["cl_case_id"], "reviewed_editorial_hash": entry["cl_reviewed_editorial_hash"],
        "reviewed_script_hash": entry["cl_reviewed_script_hash"],
        "final_editorial": entry["cl_final_editorial"], "named_individuals": entry["cl_named_individuals"],
    })


def test_step5_cl_success_wraps_phase_c_d_and_does_not_call_upload_short_directly(tmp_path, monkeypatch):
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "_asset_safety_block_reason", lambda seg_dir, video_path: None)
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    def _fail_if_called(*a, **k):
        raise AssertionError("upload_short() KHÔNG được gọi trực tiếp cho CL -- phải qua _run_cl_phase_c_d_and_upload()/safe_upload()")
    monkeypatch.setattr(sbr, "upload_short", _fail_if_called)

    captured = {}
    def _fake_phase_c_d(entry, seg_dir, wav_path, video_path, credentials_path, publish_at):
        captured["args"] = (entry["key"], credentials_path, publish_at)
        return True, "mocked pass", "fake_video_id"
    monkeypatch.setattr(sbr, "_run_cl_phase_c_d_and_upload", _fake_phase_c_d)

    seg = _base_seg()
    (tmp_path / "v.mp4").write_bytes(b"fake")
    entry_seed = _seo_ready_entry(seg, tmp_path)
    registry = {seg["key"]: entry_seed}
    _seed_registry_on_disk(tmp_path, registry)
    _seed_matching_sidecar(tmp_path, seg, entry_seed)

    entry = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                     registry, None, 8, False, CL_TOPIC)

    assert entry["status"] == "uploaded"
    assert entry["video_id"] == "fake_video_id"
    assert captured["args"][0] == seg["key"]
    assert captured["args"][1] == "creds.json"


def test_step5_cl_failure_fails_closed_to_needs_review_no_video_id(tmp_path, monkeypatch):
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "_asset_safety_block_reason", lambda seg_dir, video_path: None)
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: (_ for _ in ()).throw(AssertionError("không được gọi")))
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)

    def _fake_phase_c_d_fail(entry, seg_dir, wav_path, video_path, credentials_path, publish_at):
        return False, "OCR phát hiện person-reference chưa xác định", None
    monkeypatch.setattr(sbr, "_run_cl_phase_c_d_and_upload", _fake_phase_c_d_fail)

    seg = _base_seg()
    (tmp_path / "v.mp4").write_bytes(b"fake")
    entry_seed = _seo_ready_entry(seg, tmp_path)
    registry = {seg["key"]: entry_seed}
    _seed_registry_on_disk(tmp_path, registry)
    _seed_matching_sidecar(tmp_path, seg, entry_seed)

    entry = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                     registry, None, 8, False, CL_TOPIC)

    assert entry["status"] == "needs_review"
    assert "video_id" not in entry
    assert "OCR" in entry["needs_human_review_cl_gate"]


def test_step5_cl_sidecar_removed_before_phase_c_d_fails_closed(tmp_path, monkeypatch):
    """Regression THẬT cho MEDIUM #1 (review độc lập Cursor/Grok): registry
    có đủ field cl_* "tự khớp" nhưng sidecar KHÔNG còn tồn tại (bị xoá/chưa
    từng có, entry được plant thủ công) -- PHẢI fail-closed NGAY TRƯỚC
    Phase C/D, không được tin registry suông."""
    monkeypatch.setattr(sbr, "_registry_path", lambda t: tmp_path / "registry.json")
    monkeypatch.setattr(sbr, "_asset_safety_block_reason", lambda seg_dir, video_path: None)
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: (_ for _ in ()).throw(AssertionError("không được gọi")))
    monkeypatch.setattr(sbr, "_run_cl_phase_c_d_and_upload", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Phase C/D KHÔNG được gọi khi sidecar-recheck fail")))

    seg = _base_seg()
    (tmp_path / "v.mp4").write_bytes(b"fake")
    registry = {seg["key"]: _seo_ready_entry(seg, tmp_path)}
    _seed_registry_on_disk(tmp_path, registry)
    # KHÔNG ghi sidecar -- mô phỏng bị xoá/entry plant thủ công.

    entry = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", sbr.time_slots_for_topic(CL_TOPIC),
                                     registry, None, 8, False, CL_TOPIC)

    assert entry["status"] == "needs_review"
    assert "video_id" not in entry
    assert "Sidecar" in entry["needs_human_review_cl_gate"]


# =============================================================================
# _run_cl_phase_c_d_and_upload() -- composition thật (ffmpeg thật, LLM/OCR
# mocked -- đã có 58 test riêng cho cl_risk_gate_lifecycle.py's primitives).
# Regression THẬT cho bug tự bắt: final_script NHIỀU CÂU (script CL thật)
# không được làm hỏng audio custody chain check N=1 (verify_phase_c_audio_
# chain() gốc sẽ LUÔN fail vì tách lại script theo câu).
# =============================================================================

FFMPEG_AVAILABLE = L.VENDORED_FFMPEG.exists() and L.VENDORED_FFPROBE.exists()
pytestmark_ffmpeg = pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="vendored ffmpeg/ffprobe không có mặt trong checkout này")


def _make_wav(path: Path, duration_s: float = 1.5):
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=440:duration={duration_s}", "-ar", "48000", "-ac", "1", str(path),
    ], check=True)


def _make_video_with_audio(path: Path, wav_path: Path, duration_s: float = 1.5):
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-f", "lavfi",
        "-i", f"color=c=black:s=320x240:d={duration_s}", "-i", str(wav_path),
        "-c:v", "libx264", "-c:a", "aac", "-shortest", str(path),
    ], check=True)


def _persisted_cl_hashes(final_script, wav_path, video_path):
    """Mô phỏng ĐÚNG những gì process_one_segment() bước 2 (TTS)/bước 3
    (render) persist vào entry thật trên registry -- _run_cl_phase_c_d_and_
    upload() giờ BẮT BUỘC 3 field này (fail-closed nếu thiếu, xem HIGH #1/#2
    fix từ review độc lập Cursor/Grok)."""
    return {
        "cl_reviewed_script_hash": L._script_text_hash(final_script),
        "cl_narration_stem_hash": L.compute_narration_stem_hash([wav_path]),
        "cl_video_audio_hash": L._decode_pcm_hash(video_path),
    }


@pytestmark_ffmpeg
def test_run_cl_phase_c_d_and_upload_multisentence_script_passes(tmp_path, monkeypatch):
    final_script = "Đây là câu đầu tiên trong script. Đây là câu thứ hai! Và đây là câu thứ ba, dài hơn một chút?"
    wav_path = tmp_path / "audio.wav"
    _make_wav(wav_path)
    video_path = tmp_path / "video.mp4"
    _make_video_with_audio(video_path, wav_path)

    monkeypatch.setattr(L, "run_visual_person_reference_check", lambda frame_samples, candidate: (True, "mocked pass", []))
    monkeypatch.setattr(L, "sample_and_ocr_frames", lambda video_path, timestamps, out_dir: [])
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)

    final_editorial = {"title": "T", "description": "D", "tags": ["a", "b"], "thumbnail_brief": "B"}
    reviewed_hash = L.compute_editorial_hash(final_editorial)
    entry = {
        "key": "CLGATE_case001_01", "final_script": final_script, "seo": dict(final_editorial),
        "cl_reviewed_editorial_hash": reviewed_hash, "cl_case_id": "case001",
        "cl_final_editorial": final_editorial, "cl_named_individuals": [], "bgm": None,
        **_persisted_cl_hashes(final_script, wav_path, video_path),
    }
    captured = {}
    def _fake_upload_short(video_path_str, title, description, tags, publish_at, credentials_path):
        captured["args"] = (video_path_str, title, description, tags, publish_at, credentials_path)
        return "fake_video_id"
    monkeypatch.setattr(sbr, "upload_short", _fake_upload_short)

    ok, reason, video_id = sbr._run_cl_phase_c_d_and_upload(
        entry, tmp_path, wav_path, video_path, "creds.json", "2099-01-01T00:00:00Z",
    )
    assert ok is True, reason
    assert video_id == "fake_video_id"
    assert captured["args"][1] == "T"
    assert captured["args"][2] == "D"  # KHÔNG có attribution nối thêm (bgm=None)


@pytestmark_ffmpeg
def test_run_cl_phase_c_d_and_upload_fails_closed_on_unvetted_person_reference(tmp_path, monkeypatch):
    final_script = "Một câu bất kỳ."
    wav_path = tmp_path / "audio.wav"
    _make_wav(wav_path)
    video_path = tmp_path / "video.mp4"
    _make_video_with_audio(video_path, wav_path)

    monkeypatch.setattr(L, "run_visual_person_reference_check", lambda frame_samples, candidate: (False, "UNVETTED_PERSON_REFERENCE: 'ông X'", []))
    monkeypatch.setattr(L, "sample_and_ocr_frames", lambda video_path, timestamps, out_dir: [])
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: (_ for _ in ()).throw(AssertionError("KHÔNG được gọi khi Phase C fail")))

    final_editorial = {"title": "T", "description": "D", "tags": ["a"], "thumbnail_brief": "B"}
    entry = {
        "key": "CLGATE_case002_01", "final_script": final_script, "seo": dict(final_editorial),
        "cl_reviewed_editorial_hash": L.compute_editorial_hash(final_editorial), "cl_case_id": "case002",
        "cl_final_editorial": final_editorial, "cl_named_individuals": [], "bgm": None,
        **_persisted_cl_hashes(final_script, wav_path, video_path),
    }
    ok, reason, video_id = sbr._run_cl_phase_c_d_and_upload(
        entry, tmp_path, wav_path, video_path, "creds.json", "2099-01-01T00:00:00Z",
    )
    assert ok is False
    assert video_id is None
    assert "UNVETTED_PERSON_REFERENCE" in reason


@pytestmark_ffmpeg
def test_run_cl_phase_c_d_and_upload_fails_closed_on_editorial_drift(tmp_path, monkeypatch):
    """entry["seo"] bị đổi SAU khi reviewed_editorial_hash được tính (Phase
    A) -- Phase D PHẢI chặn, không upload nội dung chưa từng qua review."""
    final_script = "Một câu bất kỳ."
    wav_path = tmp_path / "audio.wav"
    _make_wav(wav_path)
    video_path = tmp_path / "video.mp4"
    _make_video_with_audio(video_path, wav_path)

    monkeypatch.setattr(L, "run_visual_person_reference_check", lambda frame_samples, candidate: (True, "mocked pass", []))
    monkeypatch.setattr(L, "sample_and_ocr_frames", lambda video_path, timestamps, out_dir: [])
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: (_ for _ in ()).throw(AssertionError("KHÔNG được gọi khi editorial drift")))

    reviewed_editorial = {"title": "Title đã review", "description": "D", "tags": ["a"], "thumbnail_brief": "B"}
    drifted_seo = {"title": "Title BỊ ĐỔI sau review", "description": "D", "tags": ["a"], "thumbnail_brief": "B"}
    entry = {
        "key": "CLGATE_case003_01", "final_script": final_script, "seo": drifted_seo,
        "cl_reviewed_editorial_hash": L.compute_editorial_hash(reviewed_editorial), "cl_case_id": "case003",
        "cl_final_editorial": reviewed_editorial, "cl_named_individuals": [], "bgm": None,
        **_persisted_cl_hashes(final_script, wav_path, video_path),
    }
    ok, reason, video_id = sbr._run_cl_phase_c_d_and_upload(
        entry, tmp_path, wav_path, video_path, "creds.json", "2099-01-01T00:00:00Z",
    )
    assert ok is False
    assert video_id is None
    assert "EDITORIAL_CHANGED_SINCE_REVIEW" in reason


@pytestmark_ffmpeg
def test_run_cl_phase_c_d_and_upload_missing_persisted_hashes_fails_closed(tmp_path, monkeypatch):
    """entry cũ/thiếu field cl_narration_stem_hash/cl_video_audio_hash/
    cl_reviewed_script_hash (vd registry từ TRƯỚC increment này) -- PHẢI
    fail-closed, không được ngầm coi 'thiếu' là 'khớp'."""
    final_script = "Một câu bất kỳ."
    wav_path = tmp_path / "audio.wav"
    _make_wav(wav_path)
    video_path = tmp_path / "video.mp4"
    _make_video_with_audio(video_path, wav_path)
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: (_ for _ in ()).throw(AssertionError("KHÔNG được gọi")))

    final_editorial = {"title": "T", "description": "D", "tags": ["a"], "thumbnail_brief": "B"}
    entry = {
        "key": "CLGATE_case004_01", "final_script": final_script, "seo": dict(final_editorial),
        "cl_reviewed_editorial_hash": L.compute_editorial_hash(final_editorial), "cl_case_id": "case004",
        "cl_final_editorial": final_editorial, "cl_named_individuals": [], "bgm": None,
        # KHÔNG có cl_reviewed_script_hash/cl_narration_stem_hash/cl_video_audio_hash
    }
    ok, reason, video_id = sbr._run_cl_phase_c_d_and_upload(
        entry, tmp_path, wav_path, video_path, "creds.json", "2099-01-01T00:00:00Z",
    )
    assert ok is False
    assert video_id is None
    assert "Thiếu hash custody" in reason


@pytestmark_ffmpeg
def test_run_cl_phase_c_d_and_upload_detects_wav_tampered_after_tts(tmp_path, monkeypatch):
    """Regression THẬT cho HIGH #2 (review độc lập Cursor/Grok): trước fix,
    hash được tính rồi tự so với chính nó TRONG CÙNG 1 lần gọi -- không thể
    bắt được wav bị thay SAU TTS. Giờ persisted hash (giả lập bước 2 TTS đã
    ghi) PHẢI khác hash thật của wav ĐÃ BỊ THAY -- fail-closed."""
    final_script = "Một câu bất kỳ."
    wav_path = tmp_path / "audio.wav"
    _make_wav(wav_path, duration_s=1.0)
    video_path = tmp_path / "video.mp4"
    _make_video_with_audio(video_path, wav_path, duration_s=1.0)

    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: (_ for _ in ()).throw(AssertionError("KHÔNG được gọi khi custody chain đứt")))

    final_editorial = {"title": "T", "description": "D", "tags": ["a"], "thumbnail_brief": "B"}
    entry = {
        "key": "CLGATE_case005_01", "final_script": final_script, "seo": dict(final_editorial),
        "cl_reviewed_editorial_hash": L.compute_editorial_hash(final_editorial), "cl_case_id": "case005",
        "cl_final_editorial": final_editorial, "cl_named_individuals": [], "bgm": None,
        **_persisted_cl_hashes(final_script, wav_path, video_path),
    }

    # Mô phỏng wav bị thay SAU khi TTS/hash đã persist (vd tiến trình khác
    # ghi đè, đĩa hỏng...) -- tần số khác hẳn, cùng path.
    subprocess.run([
        str(L.VENDORED_FFMPEG), "-v", "error", "-y", "-f", "lavfi",
        "-i", "sine=frequency=880:duration=1.0", "-ar", "48000", "-ac", "1", str(wav_path),
    ], check=True)

    ok, reason, video_id = sbr._run_cl_phase_c_d_and_upload(
        entry, tmp_path, wav_path, video_path, "creds.json", "2099-01-01T00:00:00Z",
    )
    assert ok is False
    assert video_id is None
    assert "narration wav hiện tại khác hash" in reason


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
