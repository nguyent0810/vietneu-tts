"""Cổng giữ chân Short MIM/CK/CL trong preflight (GH-248)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
import script_lint as SL  # noqa: E402
import build as B  # noqa: E402


def spec(**patch):
    base = {
        "theme": "mim",
        "title": "Cách giữ một chiếc khóa cửa",
        "lines": [" ".join(["từ"] * 8), "Máy mở khóa trong một nhịp."],
    }
    base.update(patch)
    return base


def test_script_lint_sentence_one_over_14_is_error():
    assert SL.short_retention(spec(lines=[" ".join(["từ"] * 14), "Máy chạy."]))[0] == []
    errors, warns = SL.short_retention(spec(lines=[" ".join(["từ"] * 15), "Máy chạy."]))
    assert errors and "15 từ" in errors[0]
    assert warns == []


def test_script_lint_sentence_two_definition_is_warning():
    for second in ("CPU là một con chip.", "Thứ này được gọi là khóa.", "Nghĩa là máy tự bấm."):
        errors, warns = SL.short_retention(spec(lines=["Máy mở khóa.", second]))
        assert errors == []
        assert warns and "định nghĩa" in warns[0]
    errors, warns = SL.short_retention(spec(lines=["Máy mở khóa.", "Nó mở cửa sau một nhịp."]))
    assert not any("định nghĩa" in w for w in warns)


def test_script_lint_abstract_question_title_is_warning():
    errors, warns = SL.short_retention(spec(title="Hạnh phúc là gì?"))
    assert errors == []
    assert any("trừu tượng" in w for w in warns)
    assert not any("trừu tượng" in w for w in SL.short_retention(spec(title="Gửi 1,2 tỷ còn bao nhiêu?"))[1])
    assert not any("trừu tượng" in w for w in SL.short_retention(spec(title="George Smith đã làm gì?"))[1])
    assert not any("trừu tượng" in w for w in SL.short_retention(spec(title="AI có thay bạn không?"))[1])
    assert not any("trừu tượng" in w for w in SL.short_retention(spec(title="Cách giữ một chiếc khóa cửa"))[1])


def test_script_lint_runs_for_mim_ck_cl_not_bud():
    line = [" ".join(["từ"] * 15), "Máy chạy."]
    assert SL.short_retention(spec(theme="ck", lines=line))[0]
    assert SL.short_retention(spec(theme="case", lines=line))[0]
    assert SL.short_retention(spec(theme="bud", lines=line)) == ([], [])


def test_script_lint_preflight_respects_allow_hook(tmp_path, monkeypatch, capsys):
    specs = tmp_path / "specs"
    specs.mkdir()
    slug = "mim-demo"
    body = spec(
        title="Hạnh phúc là gì?",
        lines=[" ".join(["từ"] * 15), "Đây là một khái niệm rộng.", " ".join(["chữ"] * 80)],
        scenes=[{"type": "kinetic", "at": 0}],
        kicker="A",
        sub="B",
    )
    (specs / f"{slug}.json").write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(B, "SPECS", specs)
    monkeypatch.setattr(B, "plan", lambda *a, **k: None)
    monkeypatch.setattr(B, "hook_errors", lambda *a, **k: [])
    monkeypatch.setattr(B, "dark_image_errors", lambda *a, **k: [])
    errors, _info = B.preflight(slug, allow_hook=False)
    out = capsys.readouterr().out
    assert any("> 14" in error for error in errors)
    assert "định nghĩa" in out and "trừu tượng" in out
    errors, _info = B.preflight(slug, allow_hook=True)
    out = capsys.readouterr().out
    assert not any("> 14" in error for error in errors)
    assert "định nghĩa" not in out and "trừu tượng" not in out
