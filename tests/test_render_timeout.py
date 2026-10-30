"""HF_RENDER_TIMEOUT_X: hạn chờ render chỉnh được, mặc định giữ đúng công thức cũ (× 6) của Mac."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hyperframes_bridge as HB  # noqa: E402


def test_mac_default_unchanged(monkeypatch):
    monkeypatch.delenv("HF_RENDER_TIMEOUT_X", raising=False)
    assert HB.render_timeout(136.0) == int(136.0 * 6) + 600   # 1416, đúng công thức trước
    assert HB.render_timeout(10.0) == HB.DEFAULT_TIMEOUT_S    # short: sàn 900 giây giữ nguyên


def test_factor_from_env(monkeypatch):
    monkeypatch.setenv("HF_RENDER_TIMEOUT_X", "20")
    assert HB.render_timeout(136.0) == 136 * 20 + 600


@pytest.mark.parametrize("raw", ["abc", "0", "-3", "nan", ""])
def test_bad_values_fall_back_to_default(monkeypatch, raw):
    monkeypatch.setenv("HF_RENDER_TIMEOUT_X", raw)
    assert HB.render_timeout(136.0) == int(136.0 * 6) + 600


def test_render_uses_helper():
    src = Path(HB.__file__).read_text(encoding="utf-8")
    assert "timeout = render_timeout(duration, timeout)" in src
    assert "int(duration * 6)" not in src
