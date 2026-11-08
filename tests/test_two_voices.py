"""Test phân giọng 2 giọng (người kể + nhân vật) cho kịch bản Long (Task 018).

Kiểm tra:
1. Phân giải giọng mặc định voice_ta:
   - standard engine mặc định 'Tuyen' (nam Bắc trầm ấm, điềm đạm).
   - v3 engine mặc định 'Phạm Tuyên'.
   - Giữ nguyên giọng chỉ định khi voice_ta khác None.
   - Chuẩn hoá alias giữa standard và v3.
2. Cấu hình dòng line_cfg theo role 'ke' | 'ta':
   - 'ke': nhận giọng người kể (spec['voice']).
   - 'ta': nhận giọng nhân vật (voice_ta hoặc mặc định).
   - Tương thích ngược: plan không có 'voices' vẫn theo spec['voice'] và alt['lines'].
3. Kiểm tra tính toàn vẹn integrity_issues:
   - Chặn nếu voices không phải danh sách.
   - Chặn nếu độ dài voices lệch script.
   - Chặn nếu có nhãn lạ ngoài 'ke' và 'ta'.
4. Trình tổng hợp synth phân bổ đúng giọng và role vào từng segment trong manifest.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import hf_batch_render as HBR
import hf_voice as V


def test_resolve_voice_ta_standard_defaults():
    # Khi voice_ta là None hoặc vắng mặt trên engine standard -> Tuyen (trầm hơn Binh)
    assert V.resolve_voice_ta({"engine": "standard"}) == "Tuyen"
    assert V.resolve_voice_ta({"engine": "standard", "voice_ta": None}) == "Tuyen"
    assert V.resolve_voice_ta({"engine": "standard", "voice_ta": ""}) == "Tuyen"


def test_resolve_voice_ta_standard_explicit():
    # Khi chỉ định rõ giọng khác
    assert V.resolve_voice_ta({"engine": "standard", "voice_ta": "Vinh"}) == "Vinh"
    assert V.resolve_voice_ta({"engine": "standard", "voice_ta": "Sơn"}) == "Sơn"
    # Chuẩn hoá tên v3 sang standard
    assert V.resolve_voice_ta({"engine": "standard", "voice_ta": "Phạm Tuyên"}) == "Tuyen"
    assert V.resolve_voice_ta({"engine": "standard", "voice_ta": "Xuân Vĩnh"}) == "Vinh"
    assert V.resolve_voice_ta({"engine": "standard", "voice_ta": "Thái Sơn"}) == "Sơn"


def test_resolve_voice_ta_v3_defaults():
    # Khi voice_ta là None hoặc vắng mặt trên engine v3 -> Phạm Tuyên
    assert V.resolve_voice_ta({"engine": "v3"}) == "Phạm Tuyên"
    assert V.resolve_voice_ta({"engine": "v3", "voice_ta": None}) == "Phạm Tuyên"
    # Chuẩn hoá tên standard sang v3
    assert V.resolve_voice_ta({"engine": "v3", "voice_ta": "Tuyen"}) == "Phạm Tuyên"
    assert V.resolve_voice_ta({"engine": "v3", "voice_ta": "Vinh"}) == "Xuân Vĩnh"
    assert V.resolve_voice_ta({"engine": "v3", "voice_ta": "Sơn"}) == "Thái Sơn"


def test_line_cfg_with_voices_list():
    spec = {
        "voice": "Binh",
        "engine": "standard",
        "tempo": 0.9,
        "voice_ta": None,
        "voices": ["ke", "ke", "ta", "ke"],
    }
    # Dòng 1: ke -> Binh
    v1, st1, k1, eng1 = V.line_cfg(spec, 1)
    assert v1 == "Binh"
    assert eng1 == "standard"
    assert k1 == 0.9

    # Dòng 2: ke -> Binh
    v2, _, _, _ = V.line_cfg(spec, 2)
    assert v2 == "Binh"

    # Dòng 3: ta -> Tuyen (mặc định)
    v3, st3, k3, eng3 = V.line_cfg(spec, 3)
    assert v3 == "Tuyen"
    assert eng3 == "standard"
    assert k3 == 0.9

    # Dòng 4: ke -> Binh
    v4, _, _, _ = V.line_cfg(spec, 4)
    assert v4 == "Binh"


def test_line_cfg_with_explicit_voice_ta():
    spec = {
        "voice": "Binh",
        "engine": "standard",
        "voice_ta": "Vinh",
        "voices": ["ke", "ta"],
    }
    assert V.line_cfg(spec, 1)[0] == "Binh"
    assert V.line_cfg(spec, 2)[0] == "Vinh"


def test_line_cfg_backward_compatibility():
    # Không có voices: giữ nguyên hành vi đơn giọng hoặc alt
    spec_plain = {
        "voice": "Binh",
        "engine": "standard",
        "tempo": 0.9,
    }
    assert V.line_cfg(spec_plain, 1)[0] == "Binh"
    assert V.line_cfg(spec_plain, 2)[0] == "Binh"

    spec_alt = {
        "voice": "Binh",
        "engine": "standard",
        "tempo": 0.9,
        "alt": {"voice": "Quang Sơn", "lines": [2]},
    }
    assert V.line_cfg(spec_alt, 1)[0] == "Binh"
    assert V.line_cfg(spec_alt, 2)[0] == "Quang Sơn"


def test_integrity_issues_voices_validation():
    # 1. voices không phải list
    row_bad_type = {
        "script": ["Câu một.", "Câu hai."],
        "voices": "ke, ta",
    }
    errs = HBR.integrity_issues(row_bad_type)
    assert any("khoá 'voices' phải là danh sách" in e for e in errs)

    # 2. Độ dài voices không khớp script
    row_bad_len = {
        "script": ["Câu một.", "Câu hai."],
        "voices": ["ke"],
    }
    errs = HBR.integrity_issues(row_bad_len)
    assert any("không khớp kịch bản" in e for e in errs)

    # 3. Nhãn không hợp lệ
    row_bad_tag = {
        "script": ["Câu một.", "Câu hai."],
        "voices": ["ke", "nguoi_ngoai"],
    }
    errs = HBR.integrity_issues(row_bad_tag)
    assert any("nhãn không hợp lệ" in e for e in errs)

    # 4. Hợp lệ
    row_ok = {
        "script": ["Câu một.", "Câu hai."],
        "voices": ["ke", "ta"],
    }
    errs = HBR.integrity_issues(row_ok)
    assert not any("voices" in e for e in errs)


def test_list_available_voices_catalog():
    voices_std = V.list_available_voices("standard")
    std_keys = [k for k, _ in voices_std]
    assert "Binh" in std_keys
    assert "Tuyen" in std_keys
    assert "Vinh" in std_keys
    assert "Sơn" in std_keys

    voices_v3 = V.list_available_voices("v3")
    v3_keys = [k for k, _ in voices_v3]
    assert "Thanh Bình" in v3_keys
    assert "Phạm Tuyên" in v3_keys
    assert "Xuân Vĩnh" in v3_keys
    assert "Thái Sơn" in v3_keys


def test_synth_manifest_assigns_segments_and_roles(tmp_path):
    lines = [
        "Đêm ở Vương Xá.",
        "Ta vẫn còn là người phải học.",
        "Ngài giữ niệm trên thân gần trọn đêm.",
    ]
    spec = {
        "voice": "Binh",
        "engine": "standard",
        "tempo": 1.0,
        "pause": 0.3,
        "voice_ta": "Tuyen",
        "voices": ["ke", "ta", "ke"],
    }
    out_wav = tmp_path / "test_out.wav"

    # Mock say để không cần chạy infer thực trong test đơn vị
    sr = 48000
    mock_audio = np.zeros(sr, dtype="float32")  # 1s mỗi câu

    with patch.object(V.Voices, "say", return_value=(mock_audio, None)):
        manifest = V.synth(lines, spec, out_wav)

    assert out_wav.exists()
    assert len(manifest["segments"]) == 3

    s1 = manifest["segments"][0]
    assert s1["voice"] == "Binh"
    assert s1["role"] == "ke"

    s2 = manifest["segments"][1]
    assert s2["voice"] == "Tuyen"
    assert s2["role"] == "ta"

    s3 = manifest["segments"][2]
    assert s3["voice"] == "Binh"
    assert s3["role"] == "ke"

    assert manifest["voice_ta"] == "Tuyen"
    assert manifest["voices_summary"] == {"ke": 2, "ta": 1}


def test_synth_manifest_records_default_voice_ta_when_none(tmp_path):
    lines = ["Đêm ở Vương Xá.", "Ta vẫn còn là người phải học."]
    spec = {
        "voice": "Binh",
        "engine": "standard",
        "tempo": 1.0,
        "pause": 0.3,
        "voice_ta": None,
        "voices": ["ke", "ta"],
    }
    out_wav = tmp_path / "test_out_null_ta.wav"
    mock_audio = np.zeros(48000, dtype="float32")
    with patch.object(V.Voices, "say", return_value=(mock_audio, None)):
        manifest = V.synth(lines, spec, out_wav)
    assert manifest["voice_ta"] == "Tuyen"
    assert manifest["segments"][1]["voice"] == "Tuyen"
