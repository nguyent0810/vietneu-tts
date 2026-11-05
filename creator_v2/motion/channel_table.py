"""Cầu nối từ code Long của creator_v2 tới hồ sơ kênh chung ``library/channels`` (#159 PR 2).

Nạp ``library/tools/channel_profile.py`` THEO ĐƯỜNG DẪN FILE, không chèn gốc repo vào ``sys.path``:
gốc repo có ``hf_geo.py``/``hf_align.py`` trùng tên với bản trong ``creator_v2/motion/``; chèn gốc repo
lên đầu ``sys.path`` sẽ làm build_long lặng lẽ import nhầm bản BUD/FS (review Lead 05/11).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("_creator_channel_profile",
                                               REPO_ROOT / "library" / "tools" / "channel_profile.py")
channel_profile = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(channel_profile)

LONG_ENGINE = "casewide"   # engine Long của creator_v2; kênh nào khai dung.long.engine này thì build_long phục vụ


def load_long_profiles() -> dict[str, dict]:
    """Hồ sơ các kênh dựng Long bằng casewide, khoá viết hoa như bảng cũ (CL/MIM/CK)."""
    out = {}
    for ident in channel_profile.ids():
        profile = channel_profile.load(ident)
        if ((profile.get("dung") or {}).get("long") or {}).get("engine") == LONG_ENGINE:
            out[ident.upper()] = profile
    return out


def resolve_long_channel(spec: dict) -> str:
    """Kênh khai trong spec; KHÔNG có mặc định CL. Kênh không dựng Long bằng casewide thì báo lỗi."""
    code = channel_profile.resolve({"channel": spec.get("channel")}).upper()
    if code not in load_long_profiles():
        raise ValueError(f"kênh {code} không dựng Long bằng {LONG_ENGINE}")
    return code
