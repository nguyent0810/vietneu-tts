"""Atomic, retryable VSD render/upload queue. No credentials are read here."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(os.environ.get("VSD_PIPELINE_HOME", Path(__file__).resolve().parent))
QUEUED = BASE / "queue"
STATES = ("ready", "rendering", "rendered", "uploading", "uploaded", "failed")
LOG = BASE / "logs" / "vsd_pipeline.jsonl"
LEDGER = BASE / "uploaded.json"
MAX_UPLOADS_24H = 24
MIN_LEAD = timedelta(minutes=20)
DEFAULT_SLOTS = ("05:00", "12:00")
EXIT_OK, EXIT_EMPTY, EXIT_ITEM_FAIL = 0, 10, 20
EXIT_DEFERRED = 30
RENDER_TIMEOUT_MARGIN = 300
UPLOAD_SAFETY_WINDOW = timedelta(minutes=30)
MAX_ATTEMPTS = 2


def _state_dir(state: str) -> Path:
    path = QUEUED / state
    path.mkdir(parents=True, exist_ok=True)
    return path


def _lease(item: dict) -> dict:
    return {**item, "lease": {"claimed_at": now_utc().isoformat(), "pid": os.getpid(), "host": socket.gethostname()}}


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, ValueError):
        return False
    except PermissionError:
        return True


def recover_stale_leases(render_timeout: int = 7200) -> None:
    """Return dead/expired work to ready, or fail after two claims."""
    with queue_lock():
        now = now_utc()
        for state in ("rendering",):
            for path in sorted(_state_dir(state).glob("*.json")):
                item = _json(path, {})
                lease = item.get("lease") or {}
                claimed = lease.get("claimed_at") or item.get("claimed_at")
                age = timedelta.max
                try:
                    age = now - datetime.fromisoformat(claimed.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass
                expired = age > timedelta(seconds=render_timeout + RENDER_TIMEOUT_MARGIN) if state == "rendering" else age > UPLOAD_SAFETY_WINDOW
                dead = isinstance(lease.get("pid"), int) and not _pid_alive(lease["pid"])
                if not (expired or dead):
                    continue
                attempts = int(item.get("attempts", 0)) + 1
                item["attempts"] = attempts
                item.pop("lease", None)
                _atomic_json(path, item)
                target = "failed" if attempts >= MAX_ATTEMPTS else "ready"
                transition(path, target)
                log_event(state, path.stem, target, f"stale lease recovered after {attempts} attempt(s)")


def _terminate_process_group(proc: subprocess.Popen, grace: float = 5.0) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return fallback


def _atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def log_event(step: str, item_id: str | None, result: str, reason: str | None = None) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": now_utc().isoformat(), "step": step, "id": item_id, "result": result, "reason": reason}
    with LOG.open("a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)


@contextmanager
def queue_lock():
    QUEUED.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        (QUEUED / state).mkdir(parents=True, exist_ok=True)
    with (QUEUED / ".pipeline.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def claim(source: str, claimed: str) -> Path | None:
    with queue_lock():
        candidates = sorted((QUEUED / source).glob("*.json"), key=lambda p: (p.stat().st_mtime_ns, p.name))
        if not candidates:
            return None
        src = candidates[0]
        dst = QUEUED / claimed / src.name
        os.replace(src, dst)
        item = _json(dst, {})
        _atomic_json(dst, _lease(item))
        return dst


def transition(path: Path, state: str) -> Path:
    dest = QUEUED / state / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    os.replace(path, dest)
    return dest


def item_failure(path: Path, step: str, exc: BaseException) -> int:
    item_id = path.stem
    reason = f"{type(exc).__name__}: {exc}"
    try:
        transition(path, "failed")
        _atomic_json(QUEUED / "failed" / f"{item_id}.log.json", {"id": item_id, "step": step, "reason": reason, "ts": now_utc().isoformat()})
    except OSError:
        log_event(step, item_id, "system_error", reason)
        return 1
    log_event(step, item_id, "failed", reason)
    return EXIT_ITEM_FAIL


def _duration_probe(mp4: Path) -> tuple[float, bool]:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-show_entries",
                        "stream=codec_type,width,height", "-of", "json", str(mp4)],
                       capture_output=True, text=True, timeout=30, check=True)
    data = json.loads(p.stdout)
    streams = data.get("streams", [])
    duration = float(data["format"]["duration"])
    video_ok = any(s.get("codec_type") == "video" and s.get("width") == 1080 and s.get("height") == 1920 for s in streams)
    audio_ok = any(s.get("codec_type") == "audio" for s in streams)
    return duration, video_ok and audio_ok


def qa_render(spec: dict, mp4: Path) -> None:
    if not mp4.is_file() or mp4.stat().st_size <= 0:
        raise RuntimeError(f"render file missing/empty: {mp4}")
    report = _json(ROOT / "hyperframes_short" / "studio" / "jobs" / spec["id"] / "qa.json", {})
    # Studio's --qa may report individual checks; every explicit check must pass.
    checks = [v for v in report.values() if isinstance(v, dict) and "ok" in v]
    if not checks or any(v.get("ok") is not True for v in checks):
        raise RuntimeError(f"studio QA failed or missing: {report}")
    duration, streams_ok = _duration_probe(mp4)
    if not streams_ok:
        raise RuntimeError("ffprobe requires 1080x1920 video and an audio stream")
    if not 15 <= duration <= 60:
        raise RuntimeError(f"duration {duration:.2f}s outside 15–60s")


def next_render(timeout: int = 7200) -> int:
    recover_stale_leases(timeout)
    path = claim("ready", "rendering")
    if path is None:
        log_event("render", None, "empty", "no ready item")
        return EXIT_EMPTY
    item_id = path.stem
    try:
        item = _json(path, None)
        if not isinstance(item, dict) or item.get("id") != item_id:
            raise ValueError("queue filename and spec id must match")
        spec = {k: v for k, v in item.items() if k != "packaging"}
        if spec.get("channel") != "vsd" or spec.get("lane") not in {"vsd_su", "vsd_dia", "vsd_van"}:
            raise ValueError("invalid VSD channel/lane")
        tmp = path.with_suffix(".studio.json")
        _atomic_json(tmp, spec)
        env = os.environ.copy()
        env["PRODUCER_PAGE_NAVIGATION_TIMEOUT_MS"] = "300000"
        cmd = [sys.executable, str(ROOT / "studio.py"), "build", str(tmp), "--render", "--qa", "--strict", "--no-ledger"]
        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _terminate_process_group(proc)
            raise subprocess.TimeoutExpired(cmd, timeout)
        p = type("Completed", (), {"returncode": proc.returncode, "stdout": stdout, "stderr": stderr})()
        tmp.unlink(missing_ok=True)
        if p.returncode:
            raise RuntimeError(f"studio exited {p.returncode}: {(p.stdout + p.stderr)[-5000:]}")
        out = Path(spec.get("out", f"output/cl_staging/studio_out/{item_id}.mp4"))
        if not out.is_absolute():
            out = ROOT / out
        qa_render(spec, out)
        transition(path, "rendered")
        log_event("render", item_id, "ok")
        return EXIT_OK
    except subprocess.TimeoutExpired as exc:
        return item_failure(path, "render", TimeoutError(f"studio timeout after {exc.timeout}s"))
    except (Exception, SystemExit) as exc:
        return item_failure(path, "render", exc)


def parse_slot(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("publish_slot_utc must include timezone")
    return dt.astimezone(timezone.utc)


def configured_slots() -> tuple[str, ...]:
    raw = os.environ.get("VSD_PUBLISH_SLOTS_UTC", ",".join(DEFAULT_SLOTS))
    slots = tuple(x.strip() for x in raw.split(",") if x.strip())
    if any(len(s) != 5 or s[2] != ":" for s in slots):
        raise ValueError("VSD_PUBLISH_SLOTS_UTC must contain HH:MM values")
    return slots


def next_slot(now: datetime, occupied: set[str] | None = None, slots: tuple[str, ...] | None = None) -> datetime:
    occupied, slots = occupied or set(), slots or configured_slots()
    now = now.astimezone(timezone.utc)
    options = []
    for day in range(182):
        d = (now + timedelta(days=day)).date()
        for hm in slots:
            hour, minute = map(int, hm.split(":"))
            candidate = datetime(d.year, d.month, d.day, hour, minute, tzinfo=timezone.utc)
            if candidate - now < MIN_LEAD or candidate.isoformat(timespec="minutes")[:16] in occupied:
                continue
            options.append(candidate)
        if options:
            return min(options)
    raise RuntimeError("no publish slot available within 182 days")


def upload_ledger() -> list[dict]:
    return _json(LEDGER, [])


def uploads_last_24h(now: datetime | None = None) -> int:
    now = now or now_utc()
    return sum(1 for e in upload_ledger() if _recent(e.get("uploaded_at"), now))


def list_channel_uploads(credentials: str) -> list[dict]:
    """Recent channel uploads including private scheduled videos."""
    import hf_coverage
    import youtube_catalog
    ids, _, _ = hf_coverage.discover_ids(credentials)
    ids |= hf_coverage.discover_ids_deep(credentials, known=ids)
    rows = []
    ordered = sorted(ids)
    for offset in range(0, len(ordered), 50):
        data = youtube_catalog._get(credentials, youtube_catalog.VIDEOS_URL,
                                    {"part": "snippet,status", "id": ",".join(ordered[offset:offset + 50])})
        for video in data.get("items", []):
            snippet, status = video.get("snippet", {}), video.get("status", {})
            rows.append({"id": video["id"], "title": snippet.get("title"), "description": snippet.get("description", ""),
                         "tags": snippet.get("tags", []), "published_at": snippet.get("publishedAt"),
                         "publish_at": status.get("publishAt"), "privacy": status.get("privacyStatus")})
    return rows


def _remote_uploads(credentials: str) -> list[dict]:
    return list_channel_uploads(credentials)


def _remote_time(row: dict) -> str | None:
    return row.get("published_at") or row.get("when") or row.get("publish_at")


def _remote_recent_count(rows: list[dict], now: datetime) -> int:
    return sum(1 for row in rows if _recent(_remote_time(row), now))


def _combined_recent_count(local: list[dict], remote: list[dict], now: datetime) -> int:
    recent = {}
    for row in local:
        if _recent(row.get("uploaded_at"), now):
            recent[row.get("video_id") or row.get("id")] = True
    for row in remote:
        if _recent(_remote_time(row), now):
            marker = next((tag[4:] for tag in (row.get("tags") or []) if isinstance(tag, str) and tag.startswith("vsd-")), None)
            recent[marker or row.get("id") or row.get("video_id") or f"remote-{len(recent)}"] = True
    return len(recent)


def _reconcile_intents(credentials: str) -> bool:
    """Reconcile existing uploading intents; return False if upload must wait."""
    intents = sorted(_state_dir("uploading").glob("*.json"))
    if not intents:
        return True
    try:
        rows = _remote_uploads(credentials)
    except Exception as exc:
        log_event("reconcile", None, "deferred", f"channel lister failed: {exc}")
        return False
    for path in intents:
        intent = _json(path, {})
        item_id = intent.get("id", path.stem)
        marker = f"vsd-{item_id}"
        found = next((row for row in rows if marker in (row.get("tags") or []) or f"#vsd:{item_id}" in (row.get("description") or "")), None)
        if found:
            ledger = upload_ledger()
            if not any(e.get("id") == item_id for e in ledger):
                ledger.append({"id": item_id, "video_id": found.get("id"), "uploaded_at": _remote_time(found) or now_utc().isoformat(), "publish_at": intent.get("publish_at"), "path": intent.get("path")})
                _atomic_json(LEDGER, ledger)
            transition(path, "uploaded")
            log_event("reconcile", item_id, "reconciled", "marker found on channel")
            continue
        try:
            old = now_utc() - datetime.fromisoformat(intent["started_at"].replace("Z", "+00:00")) >= UPLOAD_SAFETY_WINDOW
        except (ValueError, KeyError):
            old = False
        if old and int(intent.get("attempt", 0)) < 2:
            item = _json(path, {})
            item["upload_attempt"] = int(item.get("attempt", 1))
            item.pop("started_at", None)
            item.pop("marker", None)
            item.pop("attempt", None)
            item.pop("lease", None)
            transition(path, "rendered")
            _atomic_json(QUEUED / "rendered" / path.name, item)
            log_event("reconcile", item_id, "retry_allowed", "marker absent after safety window")
            continue
        if old and int(intent.get("attempt", 0)) >= 2:
            transition(path, "failed")
            _atomic_json(_state_dir("failed") / f"{item_id}.log.json", {"id": item_id, "step": "upload", "reason": "marker absent after the single retry", "ts": now_utc().isoformat()})
            log_event("reconcile", item_id, "failed", "marker absent after the single retry")
            continue
        return False
    return True


def _recent(value: str | None, now: datetime) -> bool:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return timedelta(0) <= now - dt < timedelta(hours=24)
    except (ValueError, AttributeError):
        return False


def resolve_occupied(credentials: str) -> set[str]:
    if os.environ.get("VSD_DISABLE_OCCUPIED_SLOTS") == "1":
        return set()
    import hf_coverage
    return hf_coverage.occupied_slots(credentials)


def upload_short(*args, **kwargs):
    import short_upload
    return short_upload.upload_short(*args, **kwargs)


def _next_upload_locked(dry_run: bool = False, use_coverage: bool = True) -> int:
    recover_stale_leases()
    creds = os.environ.get("VSD_CREDS", "")
    if not dry_run:
        if not creds:
            log_event("upload", None, "deferred", "VSD_CREDS is required for upload")
            return EXIT_DEFERRED
        if not _reconcile_intents(creds):
            return EXIT_DEFERRED
    path = claim("rendered", "rendering")
    if path is None:
        log_event("upload", None, "empty", "no rendered item")
        return EXIT_EMPTY
    item_id = path.stem
    try:
        item = _json(path, {})
        packaging = item.get("packaging") or {}
        ledger = upload_ledger()
        if any(e.get("id") == item_id for e in ledger):
            raise ValueError(f"duplicate upload id: {item_id}")
        now = now_utc()
        remote_rows = []
        if not dry_run:
            try:
                remote_rows = _remote_uploads(creds)
            except Exception as exc:
                log_event("upload", item_id, "deferred", f"channel lister failed: {exc}")
                transition(path, "rendered")
                return EXIT_DEFERRED
        if _combined_recent_count(ledger, remote_rows, now) >= MAX_UPLOADS_24H:
            raise RuntimeError("rolling 24-hour upload limit reached")
        occupied = set()
        if use_coverage and creds and not dry_run:
            occupied = resolve_occupied(creds)
        publish = parse_slot(packaging["publish_slot_utc"]) if packaging.get("publish_slot_utc") else next_slot(now, occupied)
        if publish - now < MIN_LEAD:
            raise ValueError("publish slot is less than 20 minutes away")
        key = publish.isoformat(timespec="minutes")[:16]
        if key in occupied:
            raise ValueError(f"publish slot is already occupied: {key}")
        if dry_run:
            transition(path, "rendered")
            log_event("upload", item_id, "dry_run", None)
            return EXIT_OK
        mp4 = Path(item.get("out", f"output/cl_staging/studio_out/{item_id}.mp4"))
        if not mp4.is_absolute():
            mp4 = ROOT / mp4
        title = packaging["title"]
        marker = f"vsd-{item_id}"
        description = "\n".join([packaging.get("description_first_line", ""), " ".join(packaging.get("hashtags", [])), *packaging.get("sources", []), f"#vsd:{item_id}"]).strip()
        started = now_utc().isoformat()
        intent = {**item, "id": item_id, "attempt": int(item.get("upload_attempt", 0)) + 1, "started_at": started,
                  "title": title, "marker": marker, "publish_at": publish.isoformat(), "path": str(mp4),
                  "lease": {"claimed_at": started, "pid": os.getpid(), "host": socket.gethostname()}}
        intent_path = _state_dir("uploading") / path.name
        _atomic_json(intent_path, intent)
        path.unlink(missing_ok=True)
        video_id = upload_short(str(mp4), title, description, [*packaging.get("hashtags", []), marker], publish.isoformat().replace("+00:00", "Z"), creds,
                                language="vi", channel="vsd", lane=item.get("lane"))
        ledger.append({"id": item_id, "video_id": video_id, "uploaded_at": now_utc().isoformat(), "publish_at": publish.isoformat(), "path": str(mp4)})
        _atomic_json(LEDGER, ledger)
        transition(intent_path, "uploaded")
        log_event("upload", item_id, "ok")
        return EXIT_OK
    except (Exception, SystemExit) as exc:
        if (QUEUED / "uploading" / path.name).exists():
            log_event("upload", item_id, "deferred", f"upload outcome uncertain: {type(exc).__name__}: {exc}")
            return EXIT_DEFERRED
        return item_failure(path, "upload", exc)


def next_upload(dry_run: bool = False, use_coverage: bool = True) -> int:
    """Serialize slot/pacing checks with upload so overlapping n8n runs cannot overshoot."""
    BASE.mkdir(parents=True, exist_ok=True)
    with (BASE / ".upload.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            return _next_upload_locked(dry_run, use_coverage)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def status() -> dict:
    counts = {s: sum(1 for f in (QUEUED / s).glob("*.json") if not f.name.endswith(".log.json")) for s in STATES}
    events = []
    try:
        events = [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        pass
    failures = [e for e in events if e.get("result") in ("failed", "system_error")]
    return {"counts": counts, "uploads_last_24h": uploads_last_24h(), "latest_error": failures[-1] if failures else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipelines.vsd")
    subs = ap.add_subparsers(dest="command", required=True)
    r = subs.add_parser("next-render"); r.add_argument("--timeout", type=int, default=int(os.environ.get("VSD_RENDER_TIMEOUT", "7200")))
    u = subs.add_parser("next-upload"); u.add_argument("--dry-run", action="store_true"); u.add_argument("--no-coverage", action="store_true")
    subs.add_parser("status")
    args = ap.parse_args(argv)
    try:
        if args.command == "next-render":
            result = next_render(args.timeout)
        elif args.command == "next-upload":
            result = next_upload(args.dry_run, not args.no_coverage)
        else:
            recover_stale_leases()
            value = status()
            print(json.dumps({"code": EXIT_OK, "result": value}, ensure_ascii=False))
            return 0
        outcome = {EXIT_OK: "ok", EXIT_EMPTY: "no_work", EXIT_ITEM_FAIL: "item_failed", EXIT_DEFERRED: "deferred"}.get(result, "system_error")
        print(json.dumps({"code": outcome, "result": result}, ensure_ascii=False))
        return 0 if result in (EXIT_OK, EXIT_EMPTY, EXIT_ITEM_FAIL, EXIT_DEFERRED) else 1
    except Exception as exc:
        print(json.dumps({"code": "system_error", "result": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
