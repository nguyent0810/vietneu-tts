"""UNIX_LOCK_TEST_MODULES (conftest.py) phải đủ: mọi module test mà việc import
cần `fcntl` đều phải có trong danh sách -- nếu không, Windows sẽ gặp lỗi
collection thay vì skip có lý do (ticket 01). Chạy được cả trên Linux: giả
lập máy không có fcntl bằng `sys.modules["fcntl"] = None` trong tiến trình con.
"""
import json
import subprocess
import sys
from pathlib import Path

import conftest

ROOT = Path(__file__).parent

_PROBE = r"""
import importlib.util, json, sys, traceback
from pathlib import Path
root = Path(sys.argv[1])
sys.path[:0] = [str(root), str(root / "src")]
sys.modules["fcntl"] = None  # import fcntl -> ModuleNotFoundError(name="fcntl")
paths = sorted(root.glob("test_*.py")) + sorted((root / "tests").glob("test_*.py"))
needs = []
for i, path in enumerate(paths):
    rel = path.relative_to(root).as_posix()
    spec = importlib.util.spec_from_file_location(f"_probe_mod_{i}", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except BaseException as exc:  # noqa: BLE001
        e = exc
        while e is not None:
            if isinstance(e, ModuleNotFoundError) and getattr(e, "name", None) == "fcntl":
                needs.append(rel)
                break
            e = e.__cause__ or e.__context__
print(json.dumps(needs))
"""


def test_every_test_module_that_imports_fcntl_is_listed():
    out = subprocess.run([sys.executable, "-c", _PROBE, str(ROOT)], capture_output=True, text=True,
                         encoding="utf-8", timeout=600, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr[-2000:]
    needs = set(json.loads(out.stdout.strip().splitlines()[-1]))
    missing = sorted(needs - conftest.UNIX_LOCK_TEST_MODULES)
    assert not missing, (
        f"Các module test sau import code cần fcntl nhưng chưa có trong UNIX_LOCK_TEST_MODULES "
        f"(conftest.py): {missing}"
    )
    assert needs, "probe không phát hiện module nào cần fcntl -- probe hỏng?"
