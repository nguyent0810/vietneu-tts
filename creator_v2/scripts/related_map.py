"""Suggest Short-to-Long matches from a read-only production database."""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STOP = set("va la cua cho mot nhung cac nhung voi trong nay khi tai sao nhu the nao duoc video short long tap phan ve tu den mot ban nhung that su".split())


def words(value):
    value = unicodedata.normalize("NFD", str(value).lower().replace("đ", "d"))
    value = "".join(c for c in value if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]+", value) if len(w) > 1 and w not in STOP}


def read_json(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def metadata(root, channel, slug):
    bundle = read_json(root / "bundles" / channel / (slug + ".json"))
    render = bundle.get("render") or {}
    spec_path = render.get("spec") if isinstance(render, dict) else None
    spec = read_json(root / spec_path) if spec_path else {}
    # Some standalone specs have no bundle; both layouts occur in production.
    if not spec:
        for path in (root / "data" / "stier" / "specs" / (slug + ".json"), root / "data" / "stier" / slug / "spec.json", root / "data" / "long" / slug / "spec.json"):
            if path.exists():
                spec = read_json(path)
                break
    youtube = spec.get("youtube") or {}
    title = bundle.get("title") or spec.get("title") or (youtube.get("title") if isinstance(youtube, dict) else None) or slug
    topic = " ".join(str(x) for x in (bundle.get("topic", ""), spec.get("topic", ""), slug) if x)
    return {"title": title, "topic": topic,
            "long_target": spec.get("long_target") or bundle.get("long_target")}


def public_date(value, now):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc) <= now
    except (ValueError, TypeError, AttributeError):
        return False


def make_map(channel, db_path=ROOT / "state.sqlite", root=ROOT, now=None):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", channel):
        raise ValueError("Invalid channel")
    now = now or datetime.now(timezone.utc)
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute("SELECT slug, kind, publish_at, video_id FROM item WHERE channel = ? AND kind IN ('short', 'long')", (channel,))]
    for row in rows:
        row.update(metadata(Path(root), channel, row["slug"]))
    longs = [r for r in rows if r["kind"] == "long" and r["video_id"] and public_date(r["publish_at"], now)]
    longs.sort(key=lambda r: (datetime.fromisoformat(r["publish_at"].replace("Z", "+00:00")).replace(tzinfo=timezone.utc) if not re.search(r"(?:Z|[+-]\d\d:\d\d)$", r["publish_at"]) else datetime.fromisoformat(r["publish_at"].replace("Z", "+00:00")).astimezone(timezone.utc), r["slug"]), reverse=True)
    out = []
    for short in sorted((r for r in rows if r["kind"] == "short"), key=lambda r: r["slug"]):
        if not longs:
            out.append({"short_slug": short["slug"], "short_title": short["title"], "short_video_id": short["video_id"], "long_slug": None, "long_title": None, "long_video_id": None, "score": 0, "reason": "no public Long", "fallback": False})
            continue
        target = short["long_target"]
        explicit = next((r for r in longs if target and target in (r["slug"], r["video_id"])), None)
        # Never silently substitute another Long for an explicit but unavailable target.
        if target and not explicit:
            out.append({"short_slug": short["slug"], "short_title": short["title"], "short_video_id": short["video_id"], "long_slug": None, "long_title": None, "long_video_id": None, "score": 0, "reason": f"long_target unavailable: {target}", "fallback": False})
            continue
        short_words = words(short["title"] + " " + short["topic"])
        scores = [(len(short_words & words(r["title"] + " " + r["topic"])), r) for r in longs]
        score, chosen = max(scores, key=lambda pair: pair[0])
        if explicit:
            chosen, score, reason, fallback = explicit, len(short_words & words(explicit["title"] + " " + explicit["topic"])), "long_target", False
        elif score:
            reason, fallback = "keyword overlap", False
        else:
            chosen, reason, fallback = longs[0], "latest public Long", True
        out.append({"short_slug": short["slug"], "short_title": short["title"], "short_video_id": short["video_id"], "long_slug": chosen["slug"], "long_title": chosen["title"], "long_video_id": chosen["video_id"], "score": score, "reason": reason, "fallback": fallback})
    return {"channel": channel, "matches": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("channel")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    result = make_map(args.channel)
    print("Short\tTiêu đề Short\tLong\tĐiểm\tLý do")
    for row in result["matches"]:
        print(f"{row['short_slug']}\t{row['short_title']}\t{row['long_title'] or '-'} ({row['long_slug'] or '-'})\t{row['score']}\t{row['reason']}")
    if args.write:
        path = ROOT / "output" / "channels" / args.channel / "related_map.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
