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


def _img(path, w, h):
    from PIL import Image
    Image.new("RGB", (w, h), (200, 120, 40)).save(path)


def test_local_anh_doc_thanh_khung_ngang(kho):
    from PIL import Image
    _, lib = kho
    _img(lib / "mat.png", 500, 940)
    local, *_ = HB.resolve_media({"kind": "local", "path": "output/cl_staging/long/research/ai_media/gpt/mat.png"},
                                 4, "t", orientation="landscape")
    w, h = Image.open(local).size
    assert abs(w / h - 16 / 9) < .01            # không để khung ngang cắt chân dung


def test_local_crop_ra_hinh_khac_trong_cung_chuong(kho):
    from PIL import Image
    _, lib = kho
    im = Image.linear_gradient("L").resize((1600, 900)).convert("RGB")
    im.save(lib / "canh.png")
    spec = {"kind": "local", "path": "output/cl_staging/long/research/ai_media/gpt/canh.png"}
    a, *_ = HB.resolve_media(spec, 6, "t", orientation="landscape")
    b, *_ = HB.resolve_media(dict(spec, crop=[0, 0]), 7, "t", orientation="landscape")
    assert a.read_bytes() != b.read_bytes()
    assert Image.open(b).size == Image.open(a).size


def test_chapter_key_doi_khi_noi_dung_file_doi(kho, monkeypatch):
    import hf_batch_render as B
    root, lib = kho
    monkeypatch.setattr(B, "PROJECT_ROOT", root)
    monkeypatch.setattr(B, "_engine_sig", lambda: "x")
    _img(lib / "a.png", 64, 36)
    row = {"script": ["Câu một.", "Câu hai."], "style": "ember_long",
           "media": {"1": {"kind": "local", "path": "output/cl_staging/long/research/ai_media/gpt/a.png"}}}
    k1 = B.chapter_key(row, 0, 2, 0, 5, "looks")
    assert B.chapter_key(row, 0, 2, 0, 5, "looks") == k1
    _img(lib / "a.png", 64, 37)                   # thay ảnh, giữ tên
    assert B.chapter_key(row, 0, 2, 0, 5, "looks") != k1
    assert "_sig" not in row["media"]["1"]        # không ghi bẩn plan
