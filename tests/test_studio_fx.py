"""fx opt-in của studio (ink, shimmer): spec không có fx thì JS của thiết bị không gọi fx; có fx thì có lời gọi đúng chỗ.

Kiểm tĩnh (không cần trình duyệt): render thật đã soát bằng hyperframes snapshot trên Oracle (PR).
"""
import re
from pathlib import Path

ST = Path(__file__).resolve().parents[1] / "hyperframes_short" / "studio"


def _src(name):
    return (ST / name).read_text(encoding="utf-8")


def test_core_exposes_fx_helpers_without_nondeterminism():
    core = _src("core.js")
    assert "shimmer(nodes, t" in core and "ink(parent, t" in core
    fx = core[core.index("// ---------- fx:"):core.index("    return C;")]
    # luật tất định của engine: không Math.random / Date / requestAnimationFrame / repeat vô hạn trong fx
    for bad in ("Math.random", "Date.", "requestAnimationFrame", "repeat: -1", "performance.now"):
        assert bad not in fx, bad
    assert "rng(key)" in fx            # giọt mực lấy từ rng có seed
    assert "tl.time()" in fx           # vẽ lại theo thời gian timeline ở mọi lần seek


def test_fx_is_opt_in_per_scene():
    hook = _src("devices/hook.js")
    quote = _src("devices/quote.js")
    assert re.search(r'fx\.includes\("ink"\)', hook)
    assert re.search(r'fx\.includes\("shimmer"\)', hook)
    assert re.search(r'\(s\.fx \|\| \[\]\)\.includes\("shimmer"\)', quote)
    # mọi lời gọi c.ink / c.shimmer đều nằm sau một nhánh kiểm fx
    for src in (hook, quote):
        for m in re.finditer(r"c\.(ink|shimmer)\(", src):
            line = src[src.rfind("\n", 0, m.start()) + 1: src.find("\n", m.start())]
            assert "if (" in line, line


def test_shimmer_css_keeps_text_colour_outside_band():
    kit = _src("kit.css")
    rule = kit[kit.index(".fx-sh"):]
    assert "currentColor 0%" in rule and "currentColor 100%" in rule
    assert "@keyframes" not in rule    # không CSS keyframes (không seek-safe)
