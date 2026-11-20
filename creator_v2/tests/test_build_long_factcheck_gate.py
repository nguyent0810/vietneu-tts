import sys
from contextlib import nullcontext
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import build_long as B  # noqa: E402


@pytest.fixture
def failed_factcheck(monkeypatch):
    calls = []
    def lint(topic):
        calls.append(topic)
        return ["missing source 2020"]
    monkeypatch.setattr(B.factcheck_lint, "lint", lint)
    return calls


def test_render_blocks_before_rendering(failed_factcheck, monkeypatch):
    monkeypatch.setattr(B, "late_report", lambda *args: pytest.fail("factcheck gate was passed"))
    with pytest.raises(SystemExit) as exc:
        B.cmd_render("sample")
    assert "missing source 2020" in str(exc.value)
    assert "data/long/sample/factcheck.md" in str(exc.value)
    assert "--allow-factcheck" in str(exc.value)
    assert failed_factcheck == ["sample"]


@pytest.mark.parametrize("flag", ["--draft", "--allow-factcheck"])
def test_render_override_reaches_mocked_render(flag, failed_factcheck, monkeypatch):
    rendered = []
    monkeypatch.setattr(B, "late_report", lambda *args: [])
    monkeypatch.setattr(B, "render_lock", lambda *args: nullcontext())
    monkeypatch.setattr(B, "pre_render_check", lambda *args: ([], None))
    monkeypatch.setattr(B, "do_render", lambda *args, **kwargs: rendered.append(kwargs))
    monkeypatch.setattr(B, "post_render_check", lambda *args, **kwargs: None)
    B.cmd_render("sample", rest=(flag,))
    assert len(rendered) == 1
    assert rendered[0]["draft"] == (flag == "--draft")


def test_final_blocks_before_lock(failed_factcheck, monkeypatch):
    monkeypatch.setattr(B, "render_lock", lambda *args: pytest.fail("factcheck gate was passed"))
    with pytest.raises(SystemExit, match="missing source 2020"):
        B.do_final("sample")


@pytest.mark.parametrize("flag", ["--draft", "--allow-factcheck"])
def test_final_override_reaches_lock(flag, failed_factcheck, monkeypatch):
    class ReachedLock(Exception):
        pass
    def lock(*args):
        raise ReachedLock
    monkeypatch.setattr(B, "render_lock", lock)
    with pytest.raises(ReachedLock):
        B.do_final("sample", rest=(flag,))
