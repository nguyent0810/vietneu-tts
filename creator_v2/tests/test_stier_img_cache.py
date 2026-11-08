"""Cache ảnh Short theo nguồn + cổng ảnh quá tối của --preflight."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
import build as B  # noqa: E402


def _img(path, value):
    from PIL import Image
    Image.new("RGB", (32, 32), (value,) * 3).save(path)


def test_changed_source_same_key_refetches(tmp_path, monkeypatch):
    """Cùng khoá i2, đổi nguồn local: -> phải làm lại ảnh, không dùng i2.jpg cũ."""
    from PIL import Image
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.setattr(B, "ROOT", root)
    _img(root / "dark.png", 5)
    _img(root / "bright.png", 200)
    dst = tmp_path / "cases" / "s" / "i2.jpg"
    B.fetch_img("local:dark.png", dst)
    assert Image.open(dst).getpixel((0, 0))[0] < 20
    B.fetch_img("local:bright.png", dst)
    assert Image.open(dst).getpixel((0, 0))[0] > 180
    assert json.loads(dst.with_suffix(".json").read_text(encoding="utf-8"))["source"] == "local:bright.png"


def test_commons_cache_invalidated_on_source_change_only(tmp_path, monkeypatch):
    """Commons: nguồn khớp thì giữ cache (không gọi mạng); nguồn đổi thì xoá cache và tải lại."""
    import urllib.request
    dst = tmp_path / "i2.jpg"
    _img(dst, 5)
    dst.with_suffix(".json").write_text(json.dumps({"credit": "x", "source": "File:Old.jpg"}), encoding="utf-8")

    def boom(*a, **k):
        raise RuntimeError("fetch")
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    monkeypatch.setattr(B.time, "sleep", lambda s: None)
    B.fetch_img("File:Old.jpg", dst)            # khớp -> không tải
    assert dst.exists()
    try:
        B.fetch_img("File:New.jpg", dst)
    except RuntimeError:
        pass
    assert not dst.exists()                      # đã bỏ ảnh cũ và cố tải lại


def test_dark_image_preflight(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.setattr(B, "ROOT", root)
    _img(root / "dark.png", 20)
    _img(root / "bright.png", 180)
    adir = tmp_path / "cases"
    adir.mkdir()
    _img(adir / "i3.jpg", 10)                   # Commons đã tải, tối
    spec = {"imgs": {"i1": "local:bright.png", "i2": "local:dark.png",
                     "i3": "File:X.jpg", "i4": "File:NotDownloaded.jpg"}}
    errs = B.dark_image_errors("s", spec, adir)
    assert len(errs) == 2
    assert any(e.startswith("ảnh i2 quá tối") and f"< {B.MIN_IMG_LUMA}" in e for e in errs)
    assert any(e.startswith("ảnh i3 quá tối") for e in errs)
    assert B.MIN_IMG_LUMA == 50
