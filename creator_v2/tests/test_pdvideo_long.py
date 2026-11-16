import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import floor
import pdvideo
import build_long


def test_commons_by_rejected(monkeypatch):
    monkeypatch.setattr(pdvideo.hf, "info", lambda ref: {"license": "CC BY 3.0"})
    with pytest.raises(ValueError, match="Commons"):
        pdvideo.checked_info("commons:File:example.webm")


def test_ia_community_rejected(monkeypatch):
    meta = {"identifier": "H-1518", "collection": ["opensource_movies"], "year": "1918",
            "licenseurl": "https://creativecommons.org/publicdomain/mark/1.0/"}
    monkeypatch.setattr(pdvideo.hf, "info", lambda ref: {"license": "Public Domain Mark 1.0"})
    monkeypatch.setattr(pdvideo.hf, "_json", lambda url: {"metadata": meta})
    with pytest.raises(ValueError, match="H-1518"):
        pdvideo.checked_info("ia:H-1518")


def test_prepare_credit_and_sidecar(monkeypatch, tmp_path):
    ref = "commons:File:example.webm"
    row = {"src": "commons", "license": "Public domain", "title": "Film", "date": "1918", "w": 640, "h": 480,
           "page": "https://commons.wikimedia.org/wiki/File:example.webm"}
    monkeypatch.setattr(pdvideo.hf, "info", lambda ref: row)
    monkeypatch.setattr(pdvideo.hf, "CACHE", tmp_path / "unused")
    def fetch(ref, start, dur, fit):
        assert fit == "blur"
        path = tmp_path / "mock.mp4"
        path.write_bytes(b"video")
        path.with_suffix(".json").write_text(json.dumps(row), encoding="utf-8")
        return path, "credit"
    monkeypatch.setattr(pdvideo.hf, "fetch", fetch)
    credits = {}
    path, label = pdvideo.prepare({"type": "broll", "pd": ref, "dur": 8}, tmp_path, credits)
    assert path.read_bytes() == b"video" and path.with_suffix(".json").exists()
    assert label == "TƯ LIỆU 1918"
    (tmp_path / "credits.json").write_text(json.dumps(credits), encoding="utf-8")
    line = pdvideo.credit_lines(tmp_path)[0]
    assert all(x in line for x in ("Film", "Wikimedia Commons", "Public domain", row["page"]))
    # nền video cho cảnh chữ (còn giữ "vid" cho các cổng): pd vẫn được chuẩn bị, nhãn do người gọi đặt
    path2, label2 = pdvideo.prepare({"type": "kinetic", "vid": "900001", "pd": ref, "dur": 8, "label": "TƯ LIỆU 1935"},
                                    tmp_path, credits)
    assert path2 == path and label2 == "TƯ LIỆU 1935"


def test_legacy_scene_and_floor():
    scene = {"type": "broll", "vid": "123", "at": 0}
    original = copy.deepcopy(scene)
    assert build_long.plan({"scenes": [scene]}, [], 5) == [
        {"type": "broll", "vid": "123", "t0": 0.0, "t1": 5}]
    assert floor.measure([("ch01", {"scenes": [scene]})])["vid_scenes"] == 1
    assert scene == original
    assert floor.measure([("ch01", {"scenes": [{"type": "broll", "pd": "nasa:test"}]})])["vid_scenes"] == 1
