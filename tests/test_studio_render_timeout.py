"""Timeout render Studio theo thời lượng (17/11: Short VSD 41 s quá 1800 s cứng trên Oracle)."""
import studio


def test_render_timeout_scales_with_duration(monkeypatch):
    monkeypatch.delenv("STUDIO_RENDER_TIMEOUT", raising=False)
    assert studio.render_timeout(12) == 1800          # short ngắn giữ mức cũ
    assert studio.render_timeout(41) > 1800           # Cổ Loa 40,7 s từng chết ở 1800
    assert studio.render_timeout(60) == 5400


def test_render_timeout_env_override(monkeypatch):
    monkeypatch.setenv("STUDIO_RENDER_TIMEOUT", "7000")
    assert studio.render_timeout(30) == 7000


def test_render_call_uses_scaled_timeout():
    src = open(studio.__file__, encoding="utf-8").read()
    assert "--quiet', render_timeout(dur))" in src
