#!/usr/bin/env python3
"""Read-only loop watchdog diagnostics and small runtime helpers for loop_v5."""
from __future__ import annotations

import argparse
import json
import os
import signal
import selectors
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GROK = ROOT / "output/cl_staging/grok"


def alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except ProcessLookupError:
        return False
    except OSError:
        return False


def lock_pid(path: Path) -> int | None:
    try:
        first = path.read_text(encoding="utf-8", errors="replace").split()[0]
        pid = int(first)
        return pid if pid > 0 else None
    except (OSError, ValueError, IndexError):
        return None


def sweep_stale(lock_dir: Path, log_path: Path) -> list[Path]:
    stale = lock_dir / "_stale"
    moved = []
    if not lock_dir.exists():
        return moved
    stale.mkdir(exist_ok=True)
    for lock in sorted(lock_dir.iterdir()):
        if lock.name == "_stale" or not lock.is_file():
            continue
        pid = lock_pid(lock)
        if pid is None or alive(pid):
            continue
        target = stale / lock.name
        suffix = 1
        while target.exists():
            target = stale / f"{lock.name}.{suffix}"
            suffix += 1
        lock.rename(target)
        line = f"{datetime.now().astimezone().isoformat(timespec='seconds')} khóa mồ côi {lock.name} pid={pid} -> _stale/{target.name}\n"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(line)
        moved.append(target)
    return moved


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def _task_type(queue_file: Path) -> str:
    try:
        text = queue_file.read_text(encoding="utf-8", errors="replace")[:3000]
    except OSError:
        return ""
    if not text.startswith("---"):
        return ""
    try:
        return text.split("---", 2)[1].split("type:", 1)[1].splitlines()[0].strip().strip("'\"").lower()
    except (IndexError, ValueError):
        return ""


def timeout_seconds(task_type: str) -> int:
    kind = task_type.lower()
    if any(k in kind for k in ("code", "fix", "feature")):
        return 90 * 60
    if "research" in kind:
        return 120 * 60
    if any(k in kind for k in ("media", "render")):
        return 240 * 60
    return 120 * 60


def timeout_for(queue_file: Path, override: str | None = None) -> int:
    value = override or os.environ.get("TASK_TIMEOUT")
    if value:
        try:
            return max(1, int(value))
        except ValueError:
            pass
    return timeout_seconds(_task_type(queue_file))


def record_timeout(root: Path, task: str, worker: str, seconds: int, started: str,
                   log: Path, exit_code: int = 124) -> None:
    report = root / "reports" / f"{task}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(f"# Báo cáo: {task}\n\nTHỢ TREO — Lead xem logs/{log.name} (hạn {seconds} giây).\n",
                      encoding="utf-8")
    ledger_script = ROOT / "scripts/agents/agent_ledger.py"
    subprocess.run([sys.executable, str(ledger_script), "end", task, worker, "--started-at", started,
                    "--log", str(log), "--report", str(report), "--exit-code", str(exit_code),
                    "--outcome", "timeout"], check=False)


def check(root: Path = GROK, now: float | None = None) -> tuple[list[str], list[str]]:
    now = time.time() if now is None else now
    errors: list[str] = []
    rows: list[str] = []
    heartbeat_dir = root / "heartbeat"
    heartbeats = []
    if heartbeat_dir.exists():
        for path in sorted(heartbeat_dir.glob("*.json")):
            data = _read_json(path)
            stamp = data.get("updated_at_epoch")
            age = now - float(stamp) if isinstance(stamp, (int, float)) else float("inf")
            state = "SỐNG" if age <= 300 and alive(int(data.get("loop_pid") or 0)) else "LỖI"
            rows.append(f"heartbeat {path.stem}: {state} | cũ {int(age) if age != float('inf') else 'không rõ'}s | pid {data.get('loop_pid', '?')}")
            heartbeats.append((path, data, age, state))
            if state == "LỖI":
                errors.append(f"heartbeat {path.stem} cũ quá 5 phút hoặc pid vòng đã chết")
    lock_dir = root / "queue/.running"
    dead_lock = False
    if lock_dir.exists():
        for lock in sorted(lock_dir.iterdir()):
            if not lock.is_file():
                continue
            pid = lock_pid(lock)
            if pid is None or not alive(pid):
                dead_lock = True
                rows.append(f"khóa {lock.name}: LỖI | pid {pid if pid is not None else 'không hợp lệ'} đã chết")
                errors.append(f"khóa {lock.name} có pid chết/không hợp lệ")
            else:
                rows.append(f"khóa {lock.name}: SỐNG | pid {pid}")
    # Stalled logs are reported only for an active heartbeat task without a report.
    for _path, hb, _age, state in heartbeats:
        task, worker = hb.get("task"), hb.get("worker")
        if state != "SỐNG" or not task or not worker:
            continue
        report = root / "reports" / f"{task}.md"
        log = root / "logs" / f"{task}.{worker}.log"
        if report.exists() or not log.exists():
            continue
        age = now - log.stat().st_mtime
        if age > 45 * 60:
            rows.append(f"log {task}.{worker}: LỖI | không đổi {int(age // 60)} phút")
            errors.append(f"log {task}.{worker} đứng hơn 45 phút, chưa có báo cáo")
    # During v4-to-v5 rollout, a live legacy lock still identifies its loop PID.
    live_lane = any(state == "SỐNG" for _, _, _, state in heartbeats)
    if lock_dir.exists():
        live_lane = live_lane or any(
            lock.is_file() and (pid := lock_pid(lock)) is not None and alive(pid)
            for lock in lock_dir.iterdir()
        )
    queued = False
    for task_file in sorted((root / "queue").glob("*.md")):
        task = task_file.stem
        if (root / "reports" / f"{task}.md").exists() or (lock_dir / task).exists():
            continue
        queued = True
        break
    if queued and not live_lane:
        rows.append("queue: LỖI | có task chờ nhận được nhưng không có làn nào sống")
        errors.append("queue có task chờ nhận được nhưng không làn nào sống")
    rows.extend(grokbot_rows(root.parent / "grokbot", now))
    if not rows:
        rows.append("không phát hiện heartbeat, khóa, log hoặc queue bất thường")
    return rows, errors


def heartbeat_loop(path: Path, state_path: Path, loop_pid: int, interval: int) -> None:
    while alive(loop_pid):
        state = _read_json(state_path)
        log = Path(state["log_path"]) if state.get("log_path") else None
        try:
            log_size = log.stat().st_size if log else 0
        except OSError:
            log_size = 0
        now = time.time()
        payload = {"lane": state.get("lane", path.stem), "loop_pid": loop_pid,
                   "task": state.get("task"), "worker": state.get("worker"),
                   "worker_pid": state.get("worker_pid"), "task_started_at": state.get("task_started_at"),
                   "log_size": log_size, "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "updated_at_epoch": now}
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(path)
        time.sleep(max(1, interval))


def run_worker(args: argparse.Namespace) -> int:
    command = args.argv
    if command and command[0] == "--":
        command = command[1:]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            start_new_session=True)
    if args.state:
        state = _read_json(args.state)
        state["worker_pid"] = proc.pid
        args.state.write_text(json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    deadline = time.monotonic() + args.timeout
    selector = selectors.DefaultSelector()
    if proc.stdout:
        selector.register(proc.stdout, selectors.EVENT_READ)
    with args.log.open("wb") as log:
        while True:
            for key, _ in selector.select(timeout=0.2):
                try:
                    chunk = os.read(key.fd, 65536)
                except OSError:
                    chunk = b""
                if chunk:
                    log.write(chunk); log.flush()
                else:
                    selector.unregister(key.fileobj)
            if proc.poll() is not None and time.monotonic() < deadline:
                selector.close()
                return int(proc.returncode or 0)
            if time.monotonic() >= deadline:
                # The process group can outlive its leader, so keep checking it
                # through the entire TERM grace period before escalating.
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                grace_deadline = time.monotonic() + 3
                try:
                    proc.wait(timeout=max(0, grace_deadline - time.monotonic()))
                except subprocess.TimeoutExpired:
                    pass
                while time.monotonic() < grace_deadline:
                    try:
                        os.killpg(proc.pid, 0)
                    except ProcessLookupError:
                        break
                    time.sleep(min(0.05, grace_deadline - time.monotonic()))
                try:
                    os.killpg(proc.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                proc.wait()
                selector.close()
                if args.task:
                    record_timeout(args.root, args.task, args.worker, args.timeout,
                                   args.started, args.log, 124)
                return 124


def grokbot_rows(grokbot_dir: Path, now: float | None = None) -> list[str]:
    now = time.time() if now is None else now
    rows = []
    if not grokbot_dir.exists():
        return rows
    for job in sorted(grokbot_dir.glob("*/job.json")):
        if (job.parent / "LEAD_DA_XEM").exists():
            continue
        data = _read_json(job)
        output_dir = Path(str(data.get("output_dir", ""))).expanduser()
        if not output_dir.is_absolute():
            output_dir = job.parent / output_dir
        has_output = (output_dir / "DONE.txt").is_file()
        if output_dir.is_dir() and not has_output:
            has_output = any(path.is_file() for path in output_dir.rglob("*"))
        if has_output:
            rows.append(f"GrokBot {job.parent.name} XONG – chờ Lead")
        else:
            try:
                age = now - job.stat().st_mtime
            except OSError:
                continue
            if age > 60 * 60:
                rows.append(f"GrokBot {job.parent.name} chưa trả | {int(age // 60)} phút")
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=GROK)
    parser.add_argument("--notify", action="store_true")
    sub = parser.add_subparsers(dest="mode")
    sub.add_parser("sweep")
    hb = sub.add_parser("heartbeat"); hb.add_argument("--path", type=Path, required=True); hb.add_argument("--state", type=Path, required=True); hb.add_argument("--pid", type=int, required=True); hb.add_argument("--interval", type=int, default=60)
    run = sub.add_parser("run"); run.add_argument("--timeout", type=int, required=True); run.add_argument("--log", type=Path, required=True); run.add_argument("--state", type=Path); run.add_argument("--task", default=""); run.add_argument("--worker", default=""); run.add_argument("--started", default=""); run.add_argument("argv", nargs=argparse.REMAINDER)
    timeout_report = sub.add_parser("timeout-report"); timeout_report.add_argument("--task", required=True); timeout_report.add_argument("--worker", required=True); timeout_report.add_argument("--seconds", type=int, required=True); timeout_report.add_argument("--started", required=True); timeout_report.add_argument("--log", type=Path, required=True); timeout_report.add_argument("--exit-code", type=int, default=124)
    args = parser.parse_args(argv)
    if args.mode == "sweep":
        moved = sweep_stale(args.root / "queue/.running", args.root / "logs/loop_v5.log")
        print(f"khóa mồ côi đã dời: {len(moved)}")
        return 0
    if args.mode == "heartbeat":
        heartbeat_loop(args.path, args.state, args.pid, args.interval); return 0
    if args.mode == "run":
        return run_worker(args) if args.argv else 2
    if args.mode == "timeout-report":
        record_timeout(args.root, args.task, args.worker, args.seconds, args.started, args.log, args.exit_code)
        return 0
    rows, errors = check(args.root)
    print("KIỂM TRA SỨC KHỎE VÒNG LẶP")
    for row in rows: print(row)
    if errors and args.notify and sys.platform == "darwin":
        message = "; ".join(errors).replace('"', "'")[:220]
        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "Vieneu loop health"'], check=False)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
