"""Ghi nguồn Pexels kiểu #537 ("Pexels: tên (url)") phải được gom theo tên, bản gọn giữ 12 tên."""
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load():
    cwd = os.getcwd()
    spec = importlib.util.spec_from_file_location("upload_long", ROOT / "tools/publish/upload_long.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)  # module chdir về gốc repo khi nạp
    return mod


def _render(tmp_path, rid, n):
    credits = [f"Pexels: Tác giả {i} (https://www.pexels.com/video/clip-{i}/)" for i in range(n)]
    credits.append(credits[0])  # trùng phải gộp
    (tmp_path / f"{rid}.render.json").write_text(json.dumps({"media_credits": credits}), encoding="utf-8")


def test_pexels_url_format_grouped_by_name(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setattr(mod, "OUT", tmp_path)
    _render(tmp_path, "L_x", 3)
    text = mod.credits("L_x")
    assert "Ảnh Pexels: Tác giả 0, Tác giả 1, Tác giả 2" in text
    assert "https://" not in text


def test_compact_keeps_twelve_names(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setattr(mod, "OUT", tmp_path)
    _render(tmp_path, "L_y", 30)
    text = mod.credits("L_y", compact=True)
    assert "(30 tác giả)" in text and "và 18 tác giả khác" in text
    assert "Tác giả 12" not in text


def test_http_and_parenthesised_names(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setattr(mod, "OUT", tmp_path)
    credits = ["Pexels: Stephen (Why Steve) Jacobs (https://www.pexels.com/photo/a-1/)",
               "Pexels: An Bình (http://www.pexels.com/video/b-2/)"]
    (tmp_path / "L_z.render.json").write_text(json.dumps({"media_credits": credits}), encoding="utf-8")
    text = mod.credits("L_z")
    assert "Ảnh Pexels: Stephen (Why Steve) Jacobs, An Bình" in text
    assert "http" not in text
