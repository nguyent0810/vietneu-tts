"""Plan and packaging sidecar persistence."""

import json
from datetime import datetime, timezone
from pathlib import Path


def slot_utc(day: str, slot: str) -> str:
    """Normalize an ISO date and HH:MM slot as an explicit UTC timestamp."""
    return datetime.strptime(f"{day} {slot}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def write_plan(rows, plan_path, *, channel: str, packaging_dir=None, media_credits=None):
    rows = [dict(row) for row in rows]
    for row in rows:
        if row.get("day") and row.get("slot"):
            row.setdefault("slot_utc", slot_utc(row["day"], row["slot"]))
    path = Path(plan_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if packaging_dir is not None:
        target = Path(packaging_dir)
        target.mkdir(parents=True, exist_ok=True)
        credits = media_credits or {}
        for row in rows:
            target.joinpath(f"{row['id']}.json").write_text(
                json.dumps({"id": row["id"], "channel": channel,
                            "slot_utc": row.get("slot_utc"),
                            "media_credits": credits.get(row["id"], [])},
                           ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
