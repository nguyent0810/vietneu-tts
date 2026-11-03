#!/usr/bin/env python3
"""Append-only ledger for worker and reviewer runs."""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import statistics
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = ROOT / "output/cl_staging/grok/agent_ledger.jsonl"
WORKER_STATUS = ROOT / "output/cl_staging/grok/worker_status.py"
VERDICT_RE = re.compile(r"KHÔNG ĐẠT|ĐẠT CÓ ĐIỀU KIỆN|ĐẠT", re.I)


def ledger_path() -> Path:
    return Path(os.environ.get("AGENT_LEDGER_PATH", DEFAULT_LEDGER)).expanduser()


def _utc(value: float | None = None) -> str:
    d = dt.datetime.fromtimestamp(value, dt.timezone.utc) if value is not None else dt.datetime.now(dt.timezone.utc)
    return d.isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_time(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return None


def _classify(agent: str, log_text: str) -> tuple[str, str | None]:
    """Reuse worker_status.classify signatures; do not maintain a second copy."""
    import importlib.util

    if not WORKER_STATUS.exists():
        return "unknown", None
    spec = importlib.util.spec_from_file_location("agent_ledger_worker_status", WORKER_STATUS)
    if spec is None or spec.loader is None:
        return "unknown", None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if agent not in module.QUOTA_SIG:
        return "ok", None
    state, kind, _until, _note = module.classify(agent, log_text)
    return ("quota" if state == "quota" else "ok"), kind


def _codex_session_data(started: float, ended: float) -> tuple[dict | None, str | None]:
    sessions = Path.home() / ".codex" / "sessions"
    if not sessions.exists():
        return None, None
    candidates: list[tuple[float, dict[str, int | float], str | None]] = []
    for file in sessions.rglob("*.jsonl"):
        try:
            if not (started - 120 <= file.stat().st_mtime <= ended + 300):
                continue
            meta_time = None
            cwd = None
            latest = None
            model = None
            with file.open(encoding="utf-8", errors="replace") as stream:
                for line in stream:
                    try:
                        event = json.loads(line)
                    except (ValueError, TypeError):
                        continue
                    payload = event.get("payload") or {}
                    if event.get("type") == "session_meta":
                        meta_time = _parse_time(payload.get("timestamp") or event.get("timestamp"))
                        cwd = payload.get("cwd")
                    elif event.get("type") == "event_msg" and (payload.get("info") or {}).get("total_token_usage"):
                        latest = payload["info"]["total_token_usage"]
                    elif event.get("type") == "turn_context" and payload.get("model"):
                        model = str(payload["model"])
            if cwd and Path(cwd).resolve() == ROOT.resolve() and meta_time is not None and started - 120 <= meta_time <= ended + 300 and latest:
                totals = {key: value for key, value in latest.items() if isinstance(value, (int, float))}
                candidates.append((abs(meta_time - started), totals, model))
        except (OSError, ValueError):
            continue
    if not candidates:
        return None, None
    _distance, totals, model = min(candidates, key=lambda item: item[0])
    return totals or None, model


def _grok_session_data(started: float, ended: float) -> tuple[dict | None, str | None]:
    """Read Grok CLI usage.json turn totals from sessions overlapping this run."""
    configured = os.environ.get("GROK_USAGE_PATH")
    folder = Path(configured).expanduser() if configured else Path.home() / ".grok" / "sessions" / quote(str(ROOT), safe="")
    usage_files = [folder] if configured and folder.is_file() else list(folder.glob("*/usage.json")) if folder.exists() else []
    candidates: list[tuple[float, dict[str, int | float], str | None]] = []
    for path in usage_files:
        try:
            if not (started - 120 <= path.stat().st_mtime <= ended + 300):
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            turns = data.get("turns", []) if isinstance(data, dict) else []
            for turn in turns:
                when = _parse_time(turn.get("endedAt"))
                if when is None or not (started - 120 <= when <= ended + 300):
                    continue
                turn_totals: dict[str, int | float] = {}
                for key in ("inputTokens", "outputTokens", "cachedReadTokens", "cacheCreationTokens", "reasoningTokens", "totalTokens", "modelCalls"):
                    value = turn.get(key)
                    if isinstance(value, (int, float)):
                        turn_totals[key] = value
                model = str(turn["primaryModelId"]) if turn.get("primaryModelId") else None
                if turn_totals:
                    candidates.append((abs(when - ended), turn_totals, model))
        except (OSError, ValueError, TypeError):
            continue
    if not candidates:
        return None, None
    _distance, totals, model = min(candidates, key=lambda item: item[0])
    return totals, model


def record_run(*, ticket: str, agent: str, role: str = "worker", started_at: str | None = None,
               ended_at: str | None = None, model: str | None = None, tokens=None,
               outcome: str | None = None, quota_kind: str | None = None,
               task_type: str | None = None, verdict: str | None = None,
               log_path: str | None = None, report_path: str | None = None, exit_code: int | None = None,
               extra: dict | None = None) -> dict | None:
    """Append one sanitized run record. Logging failures warn and never escape."""
    if os.environ.get("AGENT_LEDGER", "1") == "0":
        return None
    start_s = started_at or _utc()
    end_s = ended_at or _utc()
    model = model or None
    start_epoch, end_epoch = _parse_time(start_s), _parse_time(end_s)
    log_text = ""
    if log_path:
        try:
            log_text = "\n".join(Path(log_path).read_text(encoding="utf-8", errors="replace").splitlines()[-60:])
        except OSError:
            pass
    if outcome is None:
        try:
            outcome, quota_kind = _classify(agent, log_text)
        except Exception:
            outcome, quota_kind = "unknown", None
        # A non-zero exit is a failure even when the log has no recognisable signature.
        if outcome in ("ok", "unknown") and exit_code not in (None, 0):
            outcome = "failed"
    if agent == "codex" and start_epoch is not None and end_epoch is not None:
        codex_tokens, codex_model = _codex_session_data(start_epoch, end_epoch)
        if tokens is None:
            tokens = codex_tokens
        if model is None:
            model = codex_model
    if tokens is None and agent == "grok" and start_epoch is not None and end_epoch is not None:
        grok_tokens, grok_model = _grok_session_data(start_epoch, end_epoch)
        tokens = grok_tokens
        if model is None:
            model = grok_model
    if verdict is None and report_path:
        try:
            match = VERDICT_RE.search(Path(report_path).read_text(encoding="utf-8", errors="replace"))
            verdict = match.group(0) if match else None
        except OSError:
            pass
    duration = max(0.0, end_epoch - start_epoch) if start_epoch is not None and end_epoch is not None else None
    row = {
        "run_id": str(uuid.uuid4()), "ticket": ticket, "agent": agent, "role": role,
        "task_type": task_type or infer_task_type(ticket), "started_at": start_s, "ended_at": end_s,
        "duration_seconds": round(duration, 3) if duration is not None else None,
        "model": model, "tokens": tokens, "outcome": outcome, "quota_kind": quota_kind,
        "exit_code": exit_code,
        "verdict": verdict,
    }
    if extra:
        # Do not accept arbitrary fields which could carry prompt/report/account data.
        for key in ("source",):
            if key in extra:
                row[key] = extra[key]
    try:
        dest = ledger_path()
        dest.parent.mkdir(parents=True, exist_ok=True)
        # flock the ledger itself so every writer coordinates on the same inode.
        with dest.open("a", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            stream.flush()
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        return row
    except Exception as exc:  # ledger failures must not fail a worker run
        print(f"agent_ledger: cảnh báo không ghi được sổ: {type(exc).__name__}", file=sys.stderr)
        return None


def infer_task_type(ticket: str) -> str:
    t = ticket.lower()
    if re.search(r"review|audit|nhìn lại", t): return "review"
    if re.search(r"fix|sửa|bug|patch|lỗi", t): return "code_fix"
    if re.search(r"research|nghiên cứu|benchmark|khảo sát", t): return "research"
    if re.search(r"render|media|thumb|video|short|ảnh|image|motion|tts", t): return "media/render"
    if re.search(r"script|kịch bản|docs?|prompt|content", t): return "docs/content"
    if re.search(r"code|engine|tool|generator|studio|qa|pipeline|module", t): return "feature_code"
    return "other"


def _read_rows(path: Path | None = None) -> list[dict]:
    p = path or ledger_path()
    rows = []
    try:
        with p.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                    if isinstance(row, dict): rows.append(row)
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return rows


def summary(rows: list[dict] | None = None) -> str:
    rows = _read_rows() if rows is None else rows
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(str(row.get("agent") or "unknown"), str(row.get("task_type") or "other"))].append(row)
    lines = ["agent | loại việc | lượt | ngày | thất bại | quota | median giây | first-pass review", "---|---|---:|---:|---:|---:|---:|---:"]
    for (agent, kind), items in sorted(groups.items()):
        days = len({(r.get("started_at") or "")[:10] for r in items if r.get("started_at")})
        failed = sum(r.get("outcome") in ("failed", "quota", "unknown") for r in items)
        quota = sum(r.get("outcome") == "quota" for r in items)
        durations = [float(r["duration_seconds"]) for r in items if isinstance(r.get("duration_seconds"), (int, float))]
        reviews_by_ticket: dict[str, list[dict]] = defaultdict(list)
        for row in items:
            if row.get("role") == "reviewer" and row.get("verdict"):
                reviews_by_ticket[str(row.get("ticket") or row.get("run_id"))].append(row)
        first_reviews = [sorted(group, key=lambda r: r.get("started_at") or "")[0] for group in reviews_by_ticket.values()]
        pass_count = sum(str(r["verdict"]).upper() in ("ĐẠT", "ĐẠT CÓ ĐIỀU KIỆN") for r in first_reviews)
        first_pass = f"{pass_count}/{len(first_reviews)} ({pass_count / len(first_reviews):.0%})" if first_reviews else "—"
        median = f"{statistics.median(durations):.1f}" if durations else "—"
        lines.append(f"{agent} | {kind} | {len(items)} | {days} | {failed} | {quota} | {median} | {first_pass}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start"); start.add_argument("ticket"); start.add_argument("agent"); start.add_argument("--role", default="worker")
    end = sub.add_parser("end"); end.add_argument("ticket"); end.add_argument("agent"); end.add_argument("--role", default="worker"); end.add_argument("--started-at"); end.add_argument("--log"); end.add_argument("--report"); end.add_argument("--model"); end.add_argument("--verdict"); end.add_argument("--exit-code", type=int); end.add_argument("--outcome")
    summ = sub.add_parser("summary"); summ.add_argument("--path")
    args = parser.parse_args(argv)
    if args.command == "start":
        print(_utc())
    elif args.command == "end":
        record_run(ticket=args.ticket, agent=args.agent, role=args.role, started_at=args.started_at,
                   ended_at=_utc(), log_path=args.log, report_path=args.report, model=args.model, verdict=args.verdict, exit_code=args.exit_code, outcome=args.outcome)
    else:
        print(summary(_read_rows(Path(args.path).expanduser()) if args.path else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
