"""Fail-closed adapters for the short hook and long script production gates."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_module(name: str, path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Thiếu công cụ cổng {name}: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Không nạp được công cụ cổng {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hook_lint_issues(row: dict, *, root: Path = ROOT) -> list[str]:
    """Return blocking hook findings; missing/broken tool is an explicit error."""
    path = root / "library/tools/hook_lint.py"
    module = _load_module("hook_lint", path)
    terms_path = path.with_name("hook_terms.json")
    if not terms_path.is_file():
        raise FileNotFoundError(f"Thiếu dữ liệu cho cổng hook_lint: {terms_path}")
    hit = module.lint_row(row, module.load_terms(terms_path))
    blockers = module.blocking_flags(hit["flags"])
    return [f"{flag} ({', '.join(hit['where'].get(flag, []))})" for flag in blockers]


def long_script_issues(row: dict, *, root: Path = ROOT) -> list[str]:
    """Return strict long-script errors, matching `long_script_lint --strict`.

    The lint report also carries the runner's retention findings. They are
    evaluated here too: retention findings remain warnings unless the strict
    lint independently classifies the same condition as an ERROR.
    """
    errors, runner_warnings = long_script_report(row, root=root)
    return errors


def long_script_report(row: dict, *, root: Path = ROOT) -> tuple[list[str], list[str]]:
    """Return blocking strict errors and advisory runner retention findings."""
    module = _load_module("long_script_lint", root / "long_script_lint.py")
    try:
        report = module.lint(row)
    except SystemExit as exc:
        return [f"lint dừng: {exc}"], []
    errors = [f"{code}: {message}" for level, code, message in report["issues"]
              if level == module.ERROR]
    runner = report.get("runner")
    if runner is None:
        raise RuntimeError("Thiếu kết quả retention trong báo cáo long_script_lint (runner)")
    return errors, [str(message) for message in runner]
