"""Cấu hình pytest dùng chung cho toàn repo.

1. Nhóm test `unix_lock`: module test cần khoá chỉ có trên Unix (`fcntl`, qua
   registry_lock/rotation_state/..., trực tiếp hay gián tiếp) được liệt kê
   TƯỜNG MINH trong `UNIX_LOCK_TEST_MODULES` (một nguồn duy nhất -- thêm file
   vào đây khi viết test mới cần fcntl). Mọi test trong các module đó mang
   marker `unix_lock` (`pytest -m unix_lock` chọn đúng nhóm này). Trên máy
   không có fcntl (Windows), CHỈ các module trong danh sách được skip kèm
   cùng một lý do; một module NGOÀI danh sách mà lỗi `fcntl` vẫn là lỗi thật
   (bắt được regression "module an toàn cho Windows bắt đầu import fcntl").
   Chạy nhóm này trên CI Ubuntu hoặc trong container (xem tests/README.md).

2. Binary giả cho `external_bin` -- trên Windows (máy dev) mặc định bật, nơi
   khác CHỈ khi đặt `VIETNEU_TEST_STUB_BINARIES=1` (CI của nhánh feat/**; job
   của `main` không đặt nên giữ nguyên hành vi cũ). Đặt `=0` để tắt hẳn.
   `external_bin` resolve codex/npx/node/rclone/osascript/git NGAY khi import
   và fail-closed nếu thiếu; test không bao giờ chạy binary thật. Chỉ binary
   không có trên PATH mới được thêm stub. Stub chỉ trả lời `--version`; gọi
   thật thoát mã 127 nên không test nào "thành công" giả. Khi stub bật, test
   kiểm tra binary THẬT đã cài (`TestResolvedConstants`) bị skip có lý do
   thay vì pass nhờ stub.

3. Mọi test ghi Quality record vào thư mục tạm, không đụng kho thật.
"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent

UNIX_LOCK_SKIP_REASON = (
    "cần khoá chỉ có trên Unix (fcntl) — chạy trên CI Ubuntu hoặc container, xem tests/README.md"
)

# Đường dẫn tương đối gốc repo (dấu "/").
UNIX_LOCK_TEST_MODULES = frozenset({
    "test_asset_safety_integration.py",
    "test_bgm_loudness_normalization.py",
    "test_bgm_tracks.py",
    "test_cl_case_batch.py",
    "test_cl_case_generation.py",
    "test_cl_claim_exposure_gate.py",
    "test_cl_claim_ledger.py",
    "test_cl_ledger_alias_sync.py",
    "test_cl_real_person_safety.py",
    "test_cl_risk_gate.py",
    "test_cl_risk_gate_lifecycle.py",
    "test_cl_risk_gate_orchestrator.py",
    "test_cl_risk_gate_verification.py",
    "test_cl_story_fact_pack.py",
    "test_cl_story_plan_and_generation.py",
    "test_cl_video_collapse_fix.py",
    "test_criminal_law_storytelling_phase_a.py",
    "test_director_bible_cache_identity.py",
    "test_duplicate_check.py",
    "test_fs_broll_query_sanitizer.py",
    "test_fs_generators_quality_gate.py",
    "test_long_batch_runner_duplicate_guard.py",
    "test_long_batch_runner_timeout_classification.py",
    "test_long_batch_runner_topic_arg.py",
    "test_record_existing_upload.py",
    "test_registry_lock_safety.py",
    "test_registry_production_guard_integration.py",
    "test_run_cl_storytelling_phase_a.py",
    "test_short_batch_runner_bgm.py",
    "test_short_batch_runner_cl_gate.py",
    "test_short_batch_runner_content_gate.py",
    "test_short_batch_runner_lich_hoang_dao_slot.py",
    "test_short_batch_runner_provenance_gate.py",
    "test_short_batch_runner_silence_override.py",
    "test_short_batch_runner_storytelling_binding.py",
    "test_short_health_check.py",
    "test_symbol_asset_path_healing.py",
    "test_symbol_assets.py",
    "test_thumbnail_generator.py",
    "test_twice_weekly_batch.py",
    "tests/test_content_repo_cl_hook_citation.py",
    "tests/test_content_seo_domain_and_thumbnail.py",
    "tests/test_director_bible_pacing.py",
})

STUB_ENV = "VIETNEU_TEST_STUB_BINARIES"
_STUB_BINARIES = ("git", "rclone", "node", "codex", "npx", "osascript")
_STUBBED: list[str] = []


def _install_missing_binary_stubs() -> None:
    missing = [name for name in _STUB_BINARIES if shutil.which(name) is None]
    if not missing:
        return
    stub_dir = Path(tempfile.mkdtemp(prefix="vieneu-test-bin-"))
    for name in missing:
        if os.name == "nt":
            (stub_dir / f"{name}.cmd").write_text(
                f'@if "%~1"=="--version" (echo {name} test-stub& exit /b 0)\r\n'
                f"@echo {name} test-stub: binary that khong co tren may nay 1>&2\r\n"
                "@exit /b 127\r\n",
                encoding="ascii",
            )
        else:
            path = stub_dir / name
            path.write_text(
                "#!/bin/sh\n"
                f'if [ "$1" = "--version" ]; then echo "{name} test-stub"; exit 0; fi\n'
                f'echo "{name} test-stub: binary thật không có trên máy này" >&2\n'
                "exit 127\n",
                encoding="utf-8",
            )
            path.chmod(0o755)
    _STUBBED.extend(missing)
    os.environ["PATH"] = str(stub_dir) + os.pathsep + os.environ.get("PATH", "")


# Windows (máy dev) luôn bật; nơi khác chỉ khi đặt biến. Job CI của main
# (Ubuntu, không đặt biến) giữ nguyên hành vi fail-closed của external_bin.
if os.environ.get(STUB_ENV) == "1" or (os.name == "nt" and os.environ.get(STUB_ENV) != "0"):
    _install_missing_binary_stubs()


def _has_fcntl() -> bool:
    try:
        import fcntl  # noqa: F401
    except ImportError:
        return False
    return True


def _rel(path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _is_unix_lock_module(path) -> bool:
    return _rel(path) in UNIX_LOCK_TEST_MODULES


@pytest.fixture(autouse=True)
def _isolated_quality_record_store(tmp_path, monkeypatch):
    """Không test nào được ghi Quality record vào kho thật (output/quality_records):
    mọi đường gọi S1 trong test mặc định ghi vào thư mục tạm của test đó."""
    monkeypatch.setenv("VIETNEU_QUALITY_RECORD_DIR", str(tmp_path / "_quality_records"))


def pytest_configure(config):
    config.addinivalue_line("markers", f"unix_lock: {UNIX_LOCK_SKIP_REASON}")


def pytest_collection_modifyitems(config, items):
    skip = None if _has_fcntl() else pytest.mark.skip(reason=UNIX_LOCK_SKIP_REASON)
    stub_skip = pytest.mark.skip(reason=f"{STUB_ENV}=1: binary giả đang thay {_STUBBED} -- không kiểm được binary thật")
    for item in items:
        if _is_unix_lock_module(item.path):
            item.add_marker(pytest.mark.unix_lock)
        if skip is not None and "unix_lock" in item.keywords:
            item.add_marker(skip)
        if _STUBBED and _rel(item.path) == "tests/test_external_bin.py" and "TestResolvedConstants" in item.nodeid:
            item.add_marker(stub_skip)


def _is_missing_fcntl(excinfo) -> bool:
    return (
        excinfo is not None
        and excinfo.errisinstance(ModuleNotFoundError)
        and getattr(excinfo.value, "name", None) == "fcntl"
    )


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Test trong nhóm unix_lock mà code production chỉ import fcntl lúc chạy
    (import trễ trong hàm) → skip cùng lý do trên máy không có fcntl. Test
    NGOÀI nhóm vẫn FAIL như thường."""
    report = yield
    if (report.failed and not _has_fcntl() and "unix_lock" in item.keywords
            and _is_missing_fcntl(call.excinfo)):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), None, f"Skipped: {UNIX_LOCK_SKIP_REASON}")
    return report


@pytest.hookimpl(wrapper=True)
def pytest_make_collect_report(collector):
    """Module trong nhóm unix_lock lỗi `fcntl` lúc import (máy không có fcntl)
    → skip cùng lý do. Mọi lỗi collection khác, và lỗi fcntl của module NGOÀI
    nhóm, giữ nguyên là lỗi."""
    report = yield
    if (report.failed and not _has_fcntl() and _is_unix_lock_module(collector.path)
            and "No module named 'fcntl'" in str(report.longrepr)):
        report.outcome = "skipped"
        report.longrepr = (str(collector.path), None, f"Skipped: {UNIX_LOCK_SKIP_REASON}")
    return report
