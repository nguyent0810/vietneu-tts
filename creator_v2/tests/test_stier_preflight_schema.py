"""Schema cảnh được kiểm tra trước khi plan hoặc render."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion")]
import build


class FakeSpecPath:
    def __init__(self, spec):
        self.spec = spec

    def __truediv__(self, _):
        return self

    def read_text(self, encoding):
        assert encoding == "utf-8"
        return json.dumps(self.spec, ensure_ascii=False)


def run_preflight(monkeypatch, scene):
    spec = {"lines": ["một " * 100], "theme": "case", "title": "thử",
            "scenes": [scene], "hooks": ["Bạn mất tiền", "Tiền gặp rủi ro"]}
    monkeypatch.setattr(build, "SPECS", FakeSpecPath(spec))
    monkeypatch.setattr(build, "dark_image_errors", lambda *_: [])
    return build.preflight("schema", allow_hook=True)[0]


def test_timeline_rows_bi_chan_truoc_plan(monkeypatch):
    errors = run_preflight(monkeypatch, {"type": "timeline", "rows": [{"y": "1900", "text": "mốc", "at": 0}]})
    assert any("cảnh 0 (timeline)" in e and "items" in e and "rows" in e for e in errors)


def test_evidence_title_chi_canh_bao(monkeypatch, capsys):
    errors = run_preflight(monkeypatch, {"type": "evidence", "img": "anh", "title": "bỏ qua"})
    assert not errors
    warning = capsys.readouterr().out
    assert "cảnh 0 (evidence)" in warning and "title" in warning and "bỏ qua" in warning


def test_timeline_hop_le_qua(monkeypatch):
    errors = run_preflight(monkeypatch, {"type": "timeline", "items": [{"year": "1900", "text": "mốc", "at": 0}]})
    assert not errors


@pytest.mark.parametrize("scene, field", [
    ({"type": "timeline", "items": [{"year": "1900", "text": "mốc"}]}, "items[0]"),
    ({"type": "kinetic", "items": [{"at": 0}]}, "text"),
    ({"type": "split", "a": {"img": "a"}, "b": {}}, "img"),
    ({"type": "chart", "kind": "line", "bars": []}, "points"),
    ({"type": "table", "cols": ["một"], "rows": [{"k": "x", "v": 2}]}, "v"),
])
def test_canh_sai_bao_truong(scene, field):
    assert any(field in error for error in build.scene_schema_errors({"scenes": [scene], "hooks": ["Bạn mất tiền", "Tiền gặp rủi ro"]}))
