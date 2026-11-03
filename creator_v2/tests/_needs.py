"""Điều kiện skip có lý do cho test cần file ngoài git (hợp nhất repo bước 2, ticket 108).

Mỗi skip nêu đúng file/gói thiếu; khi `data/`, font… được chuyển vào repo thì skip tự hết.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def needs_files(*rel: str, why: str = "chưa chuyển vào repo (ticket hợp nhất repo bước 2)"):
    """skipif khi một trong các đường dẫn (tính từ creator_v2/) không tồn tại."""
    missing = [r for r in rel if not (ROOT / r).exists()]
    return pytest.mark.skipif(bool(missing), reason=f"thiếu {', '.join(missing)}: {why}")


def needs_module(name: str, why: str = "gói chưa cài"):
    return pytest.mark.skipif(importlib.util.find_spec(name) is None, reason=f"thiếu gói {name}: {why}")
