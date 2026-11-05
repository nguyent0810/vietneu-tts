"""Hồi quy luật hiển thị và mô tả ảnh AI Long của GH-147."""
import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT)]

import build_long as BL  # noqa: E402


def chapters(*scenes):
    return [("ch00", {"scenes": list(scenes)})]


def test_mim_ai_image_loses_only_illustration_label():
    scene = {"img": "ai01", "illus": "ẢNH MINH HỌA", "credit": False, "tone": "color"}
    changed = BL.strip_ai_illustration_labels(
        {"channel": "MIM", "imgs": {"ai01": "EXT:ai:ai_01"}}, chapters(scene), Path("unused"))

    assert changed is True
    assert "illus" not in scene
    assert scene["credit"] is False
    assert scene["tone"] == "color"


def test_real_image_illustration_label_is_preserved():
    scene = {"img": "archive", "illus": "ẢNH MINH HỌA · MÁY CÙNG LOẠI", "credit": False}
    BL.strip_ai_illustration_labels(
        {"channel": "CK", "imgs": {"archive": "File:machine.jpg"}}, chapters(scene), Path("unused"))

    assert scene["illus"] == "ẢNH MINH HỌA · MÁY CÙNG LOẠI"


def test_cl_keeps_its_existing_ai_illustration_label():
    scene = {"img": "ai01", "illus": "ẢNH MINH HỌA", "credit": False}
    changed = BL.strip_ai_illustration_labels(
        {"channel": "CL", "imgs": {"ai01": "EXT:ai:ai_01"}}, chapters(scene), Path("unused"))

    assert changed is False
    assert scene["illus"] == "ẢNH MINH HỌA"


def test_ai_sidecar_is_recognized_without_an_ai_named_key():
    scene = {"img": "painting", "illus": "ẢNH MINH HỌA", "credit": False}

    with patch.object(Path, "read_text", return_value='{"file": "EXT:ai:painting"}'):
        BL.strip_ai_illustration_labels({"channel": "MIM", "imgs": {}}, chapters(scene), Path("unused"))

    assert "illus" not in scene
    assert scene["credit"] is False


def test_non_dict_sidecar_is_not_ai(tmp_path):
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "x1.json").write_text("[1, 2]", encoding="utf-8")
    assert not BL._is_ai_image("x1", {}, tmp_path)
