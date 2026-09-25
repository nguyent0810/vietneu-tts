"""Hợp đồng semantic figure — lớp Python đọc `hf_figure_schema.json`.

Đây KHÔNG phải nơi định nghĩa hợp đồng (xem ADR-0004): file schema mới là
nguồn sự thật, module này chỉ đọc nó. Tách riêng khỏi `hf_director.py` để
cổng chặn đăng và test import được mà không kéo theo phần gọi Gemini.

Validator: ưu tiên thư viện `jsonschema` nếu import được; nếu không thì rơi
về bộ kiểm tra nội bộ phủ ĐÚNG tập cấu trúc mà file schema đang dùng. Lý do
có 2 đường: `jsonschema` hiện được cài bằng `uv pip install` (không nằm
trong pyproject vì lock của repo đang hỏng ở 1 wheel win_amd64 không liên
quan), nên một lần `uv sync` có thể xoá nó — pipeline chạy không người
trông không được phép chết vì chuyện đó. `test_hf_figure_contract.py` bắt
hai đường phải cho cùng kết quả trên mọi fixture.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "hf_figure_schema.json"
_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

FIGURE_TYPES = ("none", "threshold", "range", "flow", "timeline", "stat")

# Giữ lại làm mốc tham chiếu cho rule (câu nào rule không đạt ngưỡng này thì
# ra `none`). Từ ADR-0005 nó KHÔNG còn chặn đăng nữa -- không còn bước duyệt.
CONFIDENCE_THRESHOLD = 0.6


class FigureContractError(ValueError):
    """Dữ liệu figure không khớp hợp đồng."""


# --------------------------------------------------------------------------
# Đường 1: jsonschema chuẩn
# --------------------------------------------------------------------------
def _validate_with_jsonschema(payload: dict) -> list[str]:
    import jsonschema  # noqa: PLC0415 -- optional, xem docstring module

    validator = jsonschema.Draft202012Validator(_SCHEMA)
    errors = []
    for err in sorted(validator.iter_errors(payload), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "(gốc)"
        errors.append(f"{where}: {err.message}")
    return errors


# --------------------------------------------------------------------------
# Đường 2: bộ kiểm tra nội bộ (chỉ phủ cấu trúc schema này thực sự dùng)
# --------------------------------------------------------------------------
def _defs() -> dict:
    return _SCHEMA["$defs"]


def _resolve(node: dict) -> dict:
    while "$ref" in node:
        ref = node["$ref"]
        if not ref.startswith("#/$defs/"):
            raise FigureContractError(f"Chỉ hỗ trợ $ref nội bộ #/$defs/*, gặp: {ref}")
        node = _defs()[ref.split("/")[-1]]
    return node


def _check(node: dict, value, where: str, out: list[str]) -> None:
    node = _resolve(node)
    if not node:                       # schema rỗng {} -> chấp nhận mọi thứ
        return

    if "oneOf" in node:
        matches = [i for i, sub in enumerate(node["oneOf"]) if not _errors_of(sub, value, where)]
        if len(matches) != 1:
            # Báo lỗi của nhánh khớp "type" nếu đoán được, cho thông báo hữu ích
            t = value.get("type") if isinstance(value, dict) else None
            picked = next((sub for sub in node["oneOf"]
                           if _resolve(sub).get("properties", {}).get("type", {}).get("const") == t), None)
            if picked is not None:
                out.extend(_errors_of(picked, value, where))
            else:
                out.append(f"{where}: không khớp đúng 1 nhánh oneOf (khớp {len(matches)})")
        return

    if "enum" in node and value not in node["enum"]:
        out.append(f"{where}: {value!r} không thuộc {node['enum']}")
        return
    if "const" in node and value != node["const"]:
        out.append(f"{where}: phải là {node['const']!r}, gặp {value!r}")
        return

    typ = node.get("type")
    if typ == "object":
        if not isinstance(value, dict):
            out.append(f"{where}: phải là object"); return
        for key in node.get("required", []):
            if key not in value:
                out.append(f"{where}: thiếu field bắt buộc '{key}'")
        props = node.get("properties", {})
        name_rule = node.get("propertyNames", {}).get("pattern")
        extra_rule = node.get("additionalProperties", True)
        for key, val in value.items():
            if name_rule and not re.fullmatch(name_rule, str(key)):
                out.append(f"{where}/{key}: tên khoá không khớp /{name_rule}/")
            if key in props:
                _check(props[key], val, f"{where}/{key}", out)
            elif isinstance(extra_rule, dict):
                _check(extra_rule, val, f"{where}/{key}", out)
            elif extra_rule is False:
                out.append(f"{where}: field lạ '{key}' (schema cấm additionalProperties)")
        return

    if typ == "array":
        if not isinstance(value, list):
            out.append(f"{where}: phải là array"); return
        if "minItems" in node and len(value) < node["minItems"]:
            out.append(f"{where}: cần >= {node['minItems']} phần tử, có {len(value)}")
        if "maxItems" in node and len(value) > node["maxItems"]:
            out.append(f"{where}: cần <= {node['maxItems']} phần tử, có {len(value)}")
        if node.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            out.append(f"{where}: phần tử phải khác nhau")
        for i, item in enumerate(value):
            _check(node.get("items", {}), item, f"{where}/{i}", out)
        return

    if typ == "string":
        if not isinstance(value, str):
            out.append(f"{where}: phải là string"); return
        if "minLength" in node and len(value) < node["minLength"]:
            out.append(f"{where}: ngắn hơn {node['minLength']} ký tự")
        if "maxLength" in node and len(value) > node["maxLength"]:
            out.append(f"{where}: dài hơn {node['maxLength']} ký tự")
        if "pattern" in node and not re.fullmatch(node["pattern"], value):
            out.append(f"{where}: không khớp /{node['pattern']}/")
        return

    if typ in ("number", "integer"):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            out.append(f"{where}: phải là số"); return
        if typ == "integer" and not float(value).is_integer():
            out.append(f"{where}: phải là số nguyên")
        for key, ok in (("minimum", lambda v, b: v >= b), ("maximum", lambda v, b: v <= b),
                        ("exclusiveMinimum", lambda v, b: v > b), ("exclusiveMaximum", lambda v, b: v < b)):
            if key in node and not ok(value, node[key]):
                out.append(f"{where}: vi phạm {key}={node[key]} (giá trị {value})")
        return

    if typ == "boolean" and not isinstance(value, bool):
        out.append(f"{where}: phải là boolean")


def _errors_of(node: dict, value, where: str) -> list[str]:
    out: list[str] = []
    _check(node, value, where, out)
    return out


def _validate_builtin(payload: dict) -> list[str]:
    return _errors_of(_SCHEMA, payload, "(gốc)")


# --------------------------------------------------------------------------
# API công khai
# --------------------------------------------------------------------------
def validator_backend() -> str:
    try:
        import jsonschema  # noqa: F401,PLC0415
        return "jsonschema"
    except ImportError:
        return "builtin"


def validate(payload: dict, *, backend: str | None = None) -> list[str]:
    """Trả về danh sách lỗi (rỗng = hợp lệ). `payload` là object có thể chứa
    `figures` và/hoặc `needs_human_figure` -- thường là chính 1 mục trong plan."""
    chosen = backend or validator_backend()
    if chosen == "jsonschema":
        return _validate_with_jsonschema(payload)
    return _validate_builtin(payload)


def assert_valid(payload: dict) -> None:
    errors = validate(payload)
    if errors:
        raise FigureContractError("Figure không hợp lệ:\n  - " + "\n  - ".join(errors))


def publish_gate(rows: list[dict]) -> list[str]:
    """Cổng đăng — chỉ còn KIỂM HỢP ĐỒNG, không còn duyệt người (ADR-0005).

    ADR-0003 từng chặn ở đây khi director không chắc. Bỏ rồi: cổng đó chỉ bắt
    được lúc director *tự biết mình không chắc*, trong khi lỗi nguy hiểm là lúc
    nó chắc mà sai — và lớp lỗi đó giờ được chặn bằng ràng buộc trong chính
    rule (dải giá trị không được đọc thành ngưỡng), có test đi kèm.

    Vẫn fail-closed với thứ máy kiểm được: figure sai schema là chặn, plan
    không parse được là chặn. Mục chưa chạy director thì không thuộc phạm vi.
    """
    blocks: list[str] = []
    for row in rows:
        rid = row.get("id", "(không id)")
        figures = row.get("figures")
        if figures is None:
            continue
        errors = validate({"figures": figures, "figure_labels": row.get("figure_labels") or {}})
        if errors:
            blocks.append(f"{rid}: figure sai hợp đồng -- {errors[0]}")
    return blocks
