"""media kind "local": ảnh / clip AI tải về kho research/ai_media (Long thử Cao Biền 23/10/2026)."""
import pytest

import hyperframes_bridge as HB


@pytest.fixture
def kho(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    lib = root / "output" / "cl_staging" / "long" / "research" / "ai_media" / "gpt"
    lib.mkdir(parents=True)
    monkeypatch.setattr(HB, "PROJECT_ROOT", root)
    monkeypatch.setattr(HB, "HF_ASSETS", tmp_path / "assets")
    return root, lib


def test_local_chi_nhan_file_trong_kho(kho):
    root, _ = kho
    (root / "ngoai.png").write_bytes(b"x")
    with pytest.raises(HB.HyperFramesError):
        HB.resolve_media({"kind": "local", "path": "ngoai.png"}, 3, "t")
    with pytest.raises(HB.HyperFramesError):
        HB.resolve_media({"kind": "local", "path": "output/cl_staging/long/research/ai_media/gpt/khong_co.png"}, 3, "t")


def test_local_clip_giu_duoi_va_ghi_cong(kho):
    _, lib = kho
    (lib / "v.mp4").write_bytes(b"fake")
    local, name, credit, grade = HB.resolve_media(
        {"kind": "local", "path": "output/cl_staging/long/research/ai_media/gpt/v.mp4", "credit": "Minh hoạ AI"}, 5, "t")
    assert local.suffix == ".mp4" and local.exists()
    assert (name, credit, grade) == ("v.mp4", "Minh hoạ AI", "")
