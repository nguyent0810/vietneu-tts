"""Hợp đồng semantic figure (ADR-0004): fixture là thước đo, không phải ví dụ.

Điểm quan trọng nhất trong file này là `test_hai_backend_dong_y`: repo có 2
đường validate (jsonschema chuẩn và bộ nội bộ dự phòng khi `uv sync` xoá mất
thư viện). Hai đường mà lệch nhau thì hợp đồng có 2 nghĩa -- đúng thứ ADR-0004
sinh ra để cấm.
"""
import json
from pathlib import Path

import pytest

import hf_figure_contract as contract

FIXTURES = Path(__file__).parent / "tests" / "fixtures" / "hf_figures"
VALID = sorted((FIXTURES / "valid").glob("*.json"))
INVALID = sorted((FIXTURES / "invalid").glob("*.json"))
BACKENDS = ["builtin"] + (["jsonschema"] if contract.validator_backend() == "jsonschema" else [])


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_co_du_fixture():
    assert len(VALID) >= 5, "phải phủ đủ 5 figure type hợp lệ"
    assert len(INVALID) >= 4


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.stem)
@pytest.mark.parametrize("backend", BACKENDS)
def test_fixture_hop_le_duoc_chap_nhan(path, backend):
    assert contract.validate(_load(path), backend=backend) == []


@pytest.mark.parametrize("path", INVALID, ids=lambda p: p.stem)
@pytest.mark.parametrize("backend", BACKENDS)
def test_fixture_sai_bi_tu_choi(path, backend):
    assert contract.validate(_load(path), backend=backend), \
        f"{path.name} phải bị từ chối bởi backend {backend}"


@pytest.mark.skipif(contract.validator_backend() != "jsonschema", reason="chưa cài jsonschema")
@pytest.mark.parametrize("path", VALID + INVALID, ids=lambda p: p.stem)
def test_hai_backend_dong_y(path):
    payload = _load(path)
    a = bool(contract.validate(payload, backend="jsonschema"))
    b = bool(contract.validate(payload, backend="builtin"))
    assert a == b, f"{path.name}: jsonschema nói {'sai' if a else 'đúng'}, builtin nói {'sai' if b else 'đúng'}"


@pytest.mark.skipif(contract.validator_backend() != "jsonschema", reason="chưa cài jsonschema")
def test_schema_tu_no_hop_le():
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(contract._SCHEMA)


def test_relation_tro_toi_chinh_minh_van_qua_schema_nhung_director_phai_chan():
    """Ghi lại giới hạn CÓ CHỦ ĐÍCH của hợp đồng: JSON Schema không diễn đạt
    được 'pairs_with phải khác chính câu này'. Ràng buộc đó thuộc về director
    (test_hf_director.py), không phải schema -- đừng 'sửa' schema cho việc này."""
    payload = {"figures": {"3": {"type": "flow", "source": "rule", "confidence": 0.8,
                                 "relation": {"pairs_with": 3, "role": "contrast"},
                                 "data": {"steps": [{"text": "A"}, {"text": "B"}]}}}}
    assert contract.validate(payload) == []


# --- Cổng đăng sau khi bỏ duyệt người (ADR-0005) --------------------------
def _row(rid, figures, **extra):
    return {"id": rid, "figures": figures, **extra}


def test_cong_cho_qua_khi_figure_dung_hop_dong():
    rows = [_row("ok", {
        "1": {"type": "range", "source": "rule", "confidence": 0.9,
              "data": {"from": {"value": 10000000, "unit": "đồng"},
                       "to": {"value": 50000000, "unit": "đồng"}}},
        "2": {"type": "none", "source": "rule", "confidence": 0.4},
    })]
    assert contract.publish_gate(rows) == [], "none không chắc KHÔNG còn chặn đăng (ADR-0005)"


def test_cong_van_chan_figure_sai_hop_dong():
    rows = [_row("hong", {"2": {"type": "threshhold", "source": "rule", "confidence": 0.9}})]
    assert contract.publish_gate(rows)


def test_muc_chua_chay_director_khong_bi_chan():
    assert contract.publish_gate([{"id": "cu", "title": "video quy trình cũ"}]) == []


def test_truong_needs_human_figure_da_bi_loai_khoi_hop_dong():
    """Trường đã chết thì phải chết hẳn: schema không còn mô tả nó nữa."""
    assert "needs_human_figure" not in contract._SCHEMA["$defs"]
    assert "needs_human_figure" not in contract._SCHEMA["properties"]
