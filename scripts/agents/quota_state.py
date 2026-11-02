#!/usr/bin/env python3
"""Read local agent quota telemetry and emit a sanitized snapshot (no network)."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/cl_staging/grok/quota_state.json"
UTC = dt.timezone.utc
# Only files touched recently can hold a fresh (<6h) window; history beyond this is not needed.
MAX_AGE_DAYS = 14


def recent_files(root, pattern, now_epoch=None):
    root = Path(root)
    if not root.exists(): return []
    cutoff = (now_epoch or time.time()) - MAX_AGE_DAYS * 86400
    out = []
    for path in root.rglob(pattern):
        try:
            if path.stat().st_mtime >= cutoff: out.append(path)
        except OSError: continue
    return out


def iso(ts):
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return dt.datetime.fromtimestamp(ts, UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    try:
        return dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    except ValueError:
        return None


def elapsed_pct(observed, reset, duration_minutes):
    try:
        now = dt.datetime.fromisoformat(iso(observed).replace("Z", "+00:00"))
        end = dt.datetime.fromisoformat(iso(reset).replace("Z", "+00:00"))
        start = end - dt.timedelta(minutes=float(duration_minutes))
        return min(100.0, max(0.0, (now - start).total_seconds() / (end - start).total_seconds() * 100))
    except (ValueError, TypeError, AttributeError):
        return None


def make_window(name, used, reset, source, observed, duration=None):
    return {"name": name, "used_pct": float(used) if isinstance(used, (int, float)) else None,
            "resets_at": iso(reset), "source": source, "observed_at": iso(observed),
            **({"window_minutes": duration} if duration is not None else {})}


def read_codex(sessions_dir):
    events = []
    for path in recent_files(sessions_dir, "*.jsonl"):
        try:
            for line in path.open(encoding="utf-8", errors="replace"):
                if "rate_limits" not in line: continue
                try: row = json.loads(line)
                except ValueError: continue
                if not isinstance(row, dict): continue
                payload = row.get("payload")
                if not isinstance(payload, dict): continue
                limits = payload.get("rate_limits") if row.get("type") == "event_msg" and payload.get("type") == "token_count" else None
                if not isinstance(limits, dict): continue
                stamp = row.get("timestamp")
                if not isinstance(stamp, str): continue
                for key in ("primary", "secondary"):
                    w = limits.get(key)
                    if isinstance(w, dict) and isinstance(w.get("used_percent"), (int, float)):
                        events.append(make_window(f"{key}_{w.get('window_minutes')}m", w["used_percent"], w.get("resets_at"), "codex rate_limits", stamp, w.get("window_minutes")))
        except OSError: continue
    latest = {}
    for w in events:
        old = latest.get(w["name"])
        if old is None or (w["observed_at"] or "") > (old["observed_at"] or ""): latest[w["name"]] = w
    return list(latest.values())


CLAUDE_RE = re.compile(r"(usage limit|weekly limit|5-hour limit|hit your limit|limit reached)", re.I)


def claude_reset(content, stamp, local_tz=None):
    """Absolute reset time from a Claude notice, or None when it cannot be pinned down.

    Clock times in notices are wall-clock in the named zone (or the machine zone), not UTC;
    a clock already past at observation time means the next day, a date already past means next year."""
    try: observed = dt.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except ValueError: return None
    if observed.tzinfo is None: return None
    zone = re.search(r"\(([A-Za-z_]+/[A-Za-z_]+)\)", content)
    try: tz = ZoneInfo(zone.group(1)) if zone else (local_tz or dt.datetime.now().astimezone().tzinfo)
    except Exception: return None
    local = observed.astimezone(tz)
    m = re.search(r"continuing automatically at (\d{1,2}(?::\d\d)?\s*[ap]m)", content, re.I)
    if m:
        clock = parse_clock(m.group(1))
        if clock is None: return None
        reset = dt.datetime.combine(local.date(), clock, tz)
        if reset <= local: reset += dt.timedelta(days=1)
        return reset.isoformat()
    m = re.search(r"resets?\s+(?:on\s+)?([A-Z][a-z]{2,8})\s+(\d{1,2})(?:\s+at\s+(\d{1,2}(?::\d\d)?\s*[ap]m))?", content, re.I)
    if m:
        try: day = dt.datetime.strptime(f"{m.group(1)[:3]} {m.group(2)} {local.year}", "%b %d %Y").date()
        except ValueError: return None
        clock = parse_clock(m.group(3)) if m.group(3) else dt.time(0, 0)
        if clock is None: return None
        reset = dt.datetime.combine(day, clock, tz)
        if reset < local - dt.timedelta(days=180): reset = reset.replace(year=reset.year + 1)
        return reset.isoformat()
    m = re.search(r"resets?\s+(?:at\s+)?(\d{1,2}(?::\d\d)?\s*[ap]m)", content, re.I)
    if m:
        clock = parse_clock(m.group(1))
        if clock is None: return None
        reset = dt.datetime.combine(local.date(), clock, tz)
        if reset <= local: reset += dt.timedelta(days=1)
        return reset.isoformat()
    return None


def parse_clock(text):
    text = text.replace(" ", "").lower()
    for fmt in ("%I:%M%p", "%I%p"):
        try: return dt.datetime.strptime(text, fmt).time()
        except ValueError: continue
    return None


def read_claude(projects_dir, local_tz=None):
    events = []; seen = set()
    for path in recent_files(projects_dir, "*.jsonl"):
        try:
            for line in path.open(encoding="utf-8", errors="replace"):
                if '"informational"' not in line: continue
                try: row = json.loads(line)
                except ValueError: continue
                if not isinstance(row, dict): continue
                # Claude emits quota notices as system/notice rows. User, assistant,
                # and tool content can quote old notices and must not count as events.
                if row.get("type") != "system" or row.get("subtype") != "informational" or row.get("level") != "notice": continue
                content = row.get("content") or ""
                if isinstance(content, list): content = " ".join(str(x.get("text", "")) for x in content if isinstance(x, dict))
                match = CLAUDE_RE.search(str(content))
                if not match: continue
                stamp = row.get("timestamp")
                if not isinstance(stamp, str): continue
                label = "weekly" if "week" in str(content).lower() else "short"
                key = (stamp, label, str(content)[:180])
                if key in seen: continue
                seen.add(key)
                reset = claude_reset(str(content), stamp, local_tz)
                events.append(make_window(label, None, reset, "Claude transcript limit notice", stamp))
        except OSError: continue
    # Notices prove an exhausted state but contain no used percentage.
    return events


def read_worker_logs(log_dir):
    found = {"agy": [], "grok": []}
    root = Path(log_dir)
    for path in root.glob("*.log") if root.exists() else []:
        name = path.name.lower()
        agent = "agy" if ".agy." in name else "grok" if ".grok." in name else None
        if not agent: continue
        try: lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError: continue
        for i, line in enumerate(lines):
            if agent == "agy" and "RESOURCE_EXHAUSTED" in line and "Resets in" in line:
                duration = re.search(r"Resets in ([0-9hms]+)", line)
                if duration:
                    d = parse_duration(duration.group(1))
                    # Sanitized AGY_ERROR summaries omit the original log timestamp;
                    # file mtime is the available observation time in this format.
                    observed = path.stat().st_mtime
                    found[agent].append(make_window("quota reset", None, observed+d, "worker log RESOURCE_EXHAUSTED", observed))
            elif agent == "grok" and ("402" in line or "weekly limit" in line.lower()):
                found[agent].append(make_window("balance/weekly", None, None, "worker log 402/weekly", path.stat().st_mtime))
    return found


def parse_duration(value):
    return sum(int(n) * scale for n, scale in re.findall(r"(\d+)([hms])", value) for scale in [{"h":3600,"m":60,"s":1}[scale]])


def read_grok_usage(usage_dir):
    # Usage files have token totals, not quota limits; timestamps indicate latest observation only.
    latest = None
    root = Path(usage_dir)
    for path in root.glob("*/usage.json") if root.exists() else []:
        try: data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError): continue
        turns = data.get("turns") if isinstance(data, dict) else None
        for turn in turns if isinstance(turns, list) else []:
            stamp = turn.get("endedAt") if isinstance(turn, dict) else None
            if isinstance(stamp, str) and (latest is None or stamp > latest): latest = stamp
    return latest


def state_for(windows, now):
    if not windows: return "UNKNOWN", None, False
    fresh = [w for w in windows if w.get("observed_at") and now.timestamp() - iso_epoch(w["observed_at"]) <= 6*3600]
    if not fresh: return "UNKNOWN", None, True
    considered = []
    for w in fresh:
        reset = iso_epoch(w.get("resets_at")) if w.get("resets_at") else 0
        # An expired reset window cannot establish a current exhausted state.
        if reset and reset <= now.timestamp(): continue
        considered.append(w)
    if not considered: return "UNKNOWN", None, False
    pct_values = [w["used_pct"] for w in considered if w["used_pct"] is not None]
    # A Claude notice only proves exhaustion when its reset was pinned to a future instant.
    if any(w["used_pct"] is None and (w["resets_at"] or "402" in w["source"] or "RESOURCE_EXHAUSTED" in w["source"]) for w in considered): state = "exhausted"
    elif pct_values and max(pct_values) >= 100: state = "exhausted"
    elif pct_values and max(pct_values) >= 80: state = "low"
    elif pct_values: state = "ok"
    else: state = "UNKNOWN"
    pressures = []
    for w in windows:
        if w["used_pct"] is None: continue
        if not w.get("observed_at") or now.timestamp() - iso_epoch(w["observed_at"]) > 6*3600: continue
        duration = w.get("window_minutes")
        elapsed = elapsed_pct(w["observed_at"], w["resets_at"], duration) if duration else None
        if elapsed is not None and elapsed > 0: pressures.append(w["used_pct"] / elapsed)
    latest = max((iso_epoch(w["observed_at"]) for w in windows if w["observed_at"]), default=None)
    stale = latest is None or now.timestamp() - latest > 6*3600
    return state, max(pressures) if pressures else None, stale


def iso_epoch(value):
    try: return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError): return 0


def build_snapshot(home=None, root=ROOT, now=None):
    home = Path(home or Path.home()); now = now or dt.datetime.now(UTC)
    codex = read_codex(home/".codex/sessions")
    claude = read_claude(home/".claude/projects")
    workers = read_worker_logs(root/"output/cl_staging/grok/logs")
    grok_stamp = read_grok_usage(home/".grok/sessions"/os.environ.get("GROK_WORKSPACE_KEY", ""))
    agents = {"codex": codex, "claude": claude, "agy": workers["agy"], "grok": workers["grok"]}
    agents["gemini_cli"] = []; agents["grokbot"] = []
    result = {"generated_at": iso(now.timestamp()), "agents": {}}
    for agent, windows in agents.items():
        state, pressure, stale = state_for(windows, now)
        for w in windows:
            w["age_hours"] = round(max(0, (now.timestamp()-iso_epoch(w["observed_at"]))/3600), 2) if w.get("observed_at") else None
            w["stale"] = w["age_hours"] is None or w["age_hours"] > 6
        result["agents"][agent] = {"windows": windows, "state": state, "pressure": pressure, "stale": stale}
        exhausted_events = [w for w in windows if w.get("used_pct") is None and
                            (w.get("resets_at") or "402" in w.get("source", "") or
                             "RESOURCE_EXHAUSTED" in w.get("source", "") or
                             "Claude transcript" in w.get("source", ""))]
        result["agents"][agent]["last_exhausted_at"] = max(
            (w.get("observed_at") for w in exhausted_events if w.get("observed_at")), default=None)
    # Transcript limit events without reset parsing still indicate a historical event, but not current quota.
    if grok_stamp and not result["agents"]["grok"]["windows"]:
        result["agents"]["grok"]["usage_observed_at"] = iso(grok_stamp)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(); data = build_snapshot(); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("agent | state | pressure | stale | windows")
    for name, a in data["agents"].items(): print(f"{name} | {a['state']} | {a['pressure'] if a['pressure'] is not None else '—'} | {'yes' if a['stale'] else 'no'} | {len(a['windows'])}")
    print(f"saved {args.output}")

if __name__ == "__main__": main()
