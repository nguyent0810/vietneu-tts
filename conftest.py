"""Cấu hình pytest dùng chung cho toàn repo.

1. Binary giả cho `external_bin`: module này resolve codex/npx/node/rclone/
   osascript/git NGAY khi import và fail-closed nếu thiếu. Test không bao giờ
   chạy binary thật (agy/Codex được giả lập ở cấp hàm gọi CLI), nhưng máy
   CI Ubuntu và máy dev Windows không có osascript/codex nên import đã lỗi
   trước khi test kịp chạy. Chỉ binary THỰC SỰ thiếu mới được thêm stub,
   binary có thật trên máy vẫn được dùng như cũ. Stub chỉ trả lời
   `--version`; mọi lệnh khác thoát mã 127 để test nào vô tình gọi binary
   thật sẽ thấy lỗi, không bao giờ "thành công" giả (vd upload rclone).

2. Nhóm test `unix_lock`: test phụ thuộc khoá chỉ có trên Unix (`fcntl`, qua
   registry_lock/rotation_state/...) được skip kèm cùng một lý do trên máy
   không có fcntl (Windows), thay vì lỗi collection:
   - module test import code cần fcntl → cả module bị skip tự động;
   - test lỗi lúc chạy vì code production import fcntl trễ → skip tự động;
   - test cần khoá nhưng không lỗi import (vd kiểm tra hành vi khoá) → gắn
     `@pytest.mark.unix_lock`.
   Chạy nhóm này trên CI Ubuntu hoặc trong container (xem tests/README.md).
"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

_STUB_BINARIES = ("git", "rclone", "node", "codex", "npx", "osascript")

UNIX_LOCK_SKIP_REASON = (
    "cần khoá chỉ có trên Unix (fcntl) — chạy trên CI Ubuntu hoặc container, xem tests/README.md"
)


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
    os.environ["PATH"] = str(stub_dir) + os.pathsep + os.environ.get("PATH", "")


_install_missing_binary_stubs()


def _has_fcntl() -> bool:
    try:
        import fcntl  # noqa: F401
    except ImportError:
        return False
    return True


@pytest.fixture(autouse=True)
def _isolated_quality_record_store(tmp_path, monkeypatch):
    """Không test nào được ghi Quality record vào kho thật (output/quality_records):
    mọi đường gọi S1 trong test mặc định ghi vào thư mục tạm của test đó."""
    monkeypatch.setenv("VIETNEU_QUALITY_RECORD_DIR", str(tmp_path / "_quality_records"))


def pytest_configure(config):
    config.addinivalue_line("markers", f"unix_lock: {UNIX_LOCK_SKIP_REASON}")


def pytest_collection_modifyitems(config, items):
    if _has_fcntl():
        return
    skip = pytest.mark.skip(reason=UNIX_LOCK_SKIP_REASON)
    for item in items:
        if "unix_lock" in item.keywords:
            item.add_marker(skip)


def _is_missing_fcntl(excinfo) -> bool:
    return (
        excinfo is not None
        and excinfo.errisinstance(ModuleNotFoundError)
        and getattr(excinfo.value, "name", None) == "fcntl"
    )


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Test import được nhưng code production chỉ import fcntl lúc chạy (import
    trễ trong hàm) → skip cùng lý do thay vì FAIL trên máy không có fcntl."""
    report = yield
    if report.failed and not _has_fcntl() and _is_missing_fcntl(call.excinfo):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), None, f"Skipped: {UNIX_LOCK_SKIP_REASON}")
    return report


@pytest.hookimpl(wrapper=True)
def pytest_make_collect_report(collector):
    """Trên máy không có fcntl, module test import (trực tiếp hay gián tiếp)
    code production cần fcntl sẽ lỗi ngay lúc import. Chuyển đúng lỗi đó
    thành skip có lý do thống nhất; mọi lỗi collection khác giữ nguyên."""
    report = yield
    if report.failed and not _has_fcntl() and "No module named 'fcntl'" in str(report.longrepr):
        report.outcome = "skipped"
        report.longrepr = (str(collector.path), None, f"Skipped: {UNIX_LOCK_SKIP_REASON}")
    return report
