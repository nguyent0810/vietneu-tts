"""Production gates must fail closed and accept the existing pass cases."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from library.tools.production_gates import hook_lint_issues, long_script_issues, long_script_report  # noqa: E402
import hf_batch_render  # noqa: E402
import short_batch_runner  # noqa: E402
import library.tools.production_gates as production_gates  # noqa: E402


@pytest.mark.parametrize("row", [
    {"id": "ok", "title": "Vì sao nhà sư cạo tóc?", "script": ["Vì sao nhà sư cạo tóc?"]},
    {"id": "picture", "title": "Vì sao nhà sư cạo tóc?", "script": ["Vì sao nhà sư cạo tóc?"],
     "media": {"1": {"kind": "image", "query": "shaving head"}}},
])
def test_hook_gate_pass_fixtures(row):
    assert hook_lint_issues(row) == []


def test_hook_gate_fail_fixture():
    row = {"id": "bad", "title": "Chánh niệm có phải là mặc kệ ngày mai?",
           "script": ["Chánh niệm có phải là mặc kệ ngày mai?"]}
    assert hook_lint_issues(row)


def test_hook_gate_missing_tool_is_explicit(tmp_path):
    with pytest.raises(FileNotFoundError, match="Thiếu công cụ cổng hook_lint"):
        hook_lint_issues({"title": "Vì sao nhà sư cạo tóc?"}, root=tmp_path)


def test_long_gate_pass_fixture():
    assert long_script_issues({"id": "long_ok", "script": ["Người đi qua cánh đồng vào năm 2027."]}) == []


def test_long_gate_fail_fixture():
    row = {"id": "long_bad", "script": ["Tuổi Tý gồm những người sinh năm âm lịch 1960, 1972, 1984, 1996 và 2008."]}
    assert any("cau_dai" in issue for issue in long_script_issues(row))


def test_long_gate_keeps_existing_warnings_advisory():
    row = {"id": "long_warn", "script": ["Quý vị hãy ngồi xuống.", "Bạn hãy ngồi xuống lắng nghe?"]}
    assert long_script_issues(row) == []


def test_long_gate_includes_runner_retention_findings_as_warnings():
    row = {"id": "retention_warn", "script": ["Người kể chuyện đi qua con đường làng trong buổi sớm yên bình." for _ in range(8)]}
    errors, warnings = long_script_report(row)
    assert errors == []
    assert warnings


def test_long_gate_blocks_retention_error_fixture_before_tts(tmp_path, monkeypatch):
    row = {"id": "retention_error", "lane": "long", "series": "bud",
           "script": ["Đây là một câu rất dài có nhiều từ được nói liên tục để minh họa lỗi nhịp và vượt quá ba mươi lăm tiếng nhằm kiểm tra cổng retention trước khi hệ thống gọi TTS."]}
    monkeypatch.setattr(hf_batch_render, "render_tts", lambda *a, **kw: pytest.fail("TTS must not run"))
    ok, note = hf_batch_render.render_one(row, tmp_path, "draft")
    assert not ok
    assert "long_script_lint" in note and "cau_dai" in note
    assert not list(tmp_path.iterdir())


def test_long_gate_missing_tool_is_explicit(tmp_path):
    with pytest.raises(FileNotFoundError, match="Thiếu công cụ cổng long_script_lint"):
        long_script_issues({"id": "x", "script": ["Câu đủ nghĩa."]}, root=tmp_path)


@pytest.mark.parametrize("row", [
    {"id": "short_bad", "series": "bud", "style": "plain", "script": ["Chánh niệm có phải là mặc kệ ngày mai?"],
     "title": "Chánh niệm có phải là mặc kệ ngày mai?"},
    {"id": "long_bad", "series": "bud", "style": "plain", "lane": "long", "script": []},
])
def test_hf_batch_render_stops_before_tts_on_gate_failure(row, tmp_path, monkeypatch):
    monkeypatch.setattr(hf_batch_render, "render_tts", lambda *a, **kw: pytest.fail("TTS must not run"))
    ok, note = hf_batch_render.render_one(row, tmp_path, "draft")
    assert not ok
    assert "hook_lint" in note or "long_script_lint" in note
    assert not list(tmp_path.iterdir())


def test_short_batch_runner_stops_before_tts_on_hook_failure(tmp_path, monkeypatch):
    key = "fixture_short"
    entry = {"key": key, "episode": "ep", "segment_index": 1,
             "status": "scripted", "final_script": "Chánh niệm có phải là mặc kệ ngày mai?"}
    monkeypatch.setattr(short_batch_runner, "load_registry", lambda topic: {key: entry})
    monkeypatch.setattr(short_batch_runner, "save_registry", lambda *args, **kwargs: None)
    monkeypatch.setattr(production_gates, "hook_lint_issues", lambda row: ["TRUU_TUONG (tiêu đề)"])
    monkeypatch.setattr(short_batch_runner, "run_tts", lambda *a, **kw: pytest.fail("TTS must not run"))
    result = short_batch_runner.process_one_segment(
        {"key": key, "episode": "ep", "segment_index": 1}, tmp_path, "unused", [],
        {key: entry}, None, 8, False, "Phật giáo")
    assert result["status"] == "needs_review"
    assert "hook_lint" in result["needs_human_review_hook_lint"]


def test_hf_batch_render_allow_override_logs(tmp_path, capsys):
    row = {"id": "override", "series": "bud", "title": "Chánh niệm có phải là mặc kệ ngày mai?", "script": []}
    ok, note = hf_batch_render.render_one(row, tmp_path, "draft", allow_lint_fail=True)
    assert ok and "không có kịch bản" in note
    assert "--allow-lint-fail bỏ qua hook_lint" in capsys.readouterr().out


def test_hf_batch_render_missing_long_tool_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(production_gates, "long_script_report",
                        lambda row: (_ for _ in ()).throw(FileNotFoundError("Thiếu công cụ cổng long_script_lint")))
    row = {"id": "missing", "lane": "long", "series": "bud", "script": ["Câu hợp lệ."]}
    ok, note = hf_batch_render.render_one(row, tmp_path, "draft")
    assert not ok
    assert "không chạy được cổng" in note and "Thiếu công cụ" in note


def test_hf_batch_render_long_override_logs(tmp_path, capsys):
    row = {"id": "long_override", "lane": "long", "series": "bud", "script": []}
    ok, note = hf_batch_render.render_one(row, tmp_path, "draft", allow_lint_fail=True)
    assert ok and "không có kịch bản" in note
    assert "--allow-lint-fail bỏ qua long_script_lint" in capsys.readouterr().out
