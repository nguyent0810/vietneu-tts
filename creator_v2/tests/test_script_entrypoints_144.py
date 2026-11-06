"""#144: chạy trực tiếp các script motion/ không được lỗi ModuleNotFoundError: 'factory'.

Mỗi script chạy trong subprocess với PYTHONPATH bị xóa. Wrapper giống `python <file>`
(sys.path[0] = thư mục của file) và dừng ngay khi script import `factory`:
  - nếu `factory` tìm thấy được -> in FACTORY_IMPORT_OK và thoát (không chạy main(),
    nên không render, không gọi mạng, không ghi file);
  - nếu không -> Python báo ModuleNotFoundError như khi chạy thật.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

WRAPPER = r'''
import importlib.abc, importlib.machinery, os, runpy, sys
f = os.path.abspath(sys.argv[1])
sys.path[0] = os.path.dirname(f)
class _Stop(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name == "factory" or name.startswith("factory."):
            if importlib.machinery.PathFinder.find_spec("factory", sys.path) is not None:
                print("FACTORY_IMPORT_OK", flush=True)
                sys.exit(0)
        return None
sys.meta_path.insert(0, _Stop())
sys.argv = [f]
runpy.run_path(f, run_name="__main__")
'''

SCRIPTS = [
    "motion/stier/script_lint.py",
    "motion/stier/bang_tra_look.py",
    "motion/stier/bud_variety.py",
    "motion/stier/build.py",
    "motion/long/commons_find.py",
    "motion/long/dryplan.py",
    "motion/long/still.py",
    "motion/long/thumb.py",
    "motion/long/brand_sting.py",
    "motion/long/chart_demo.py",
    "motion/long/diacritics_gallery.py",
]


@pytest.mark.parametrize("rel", SCRIPTS)
def test_script_imports_factory_without_pythonpath(rel: str) -> None:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    proc = subprocess.run(
        [sys.executable, "-c", WRAPPER, rel],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        stdin=subprocess.DEVNULL,
    )
    out = proc.stdout + proc.stderr
    assert "ModuleNotFoundError" not in out, out[-2000:]
    assert "FACTORY_IMPORT_OK" in out, out[-2000:]
