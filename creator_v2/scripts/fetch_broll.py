"""Tải b-roll đã có trong danh mục về thư mục của bài."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    import sys
    sys.path.insert(0, str(ROOT))
    from factory.console import utf8_console
    utf8_console()
    parser = argparse.ArgumentParser()
    parser.add_argument("topic")
    args = parser.parse_args()
    vids = set()
    for path in (ROOT / "data" / "long" / args.topic).glob("ch*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        vids.update(str(scene["vid"]) for scene in data.get("scenes", []) if scene.get("vid"))

    catalog = {}
    for path in (ROOT / "output" / "long").glob("*/broll/index.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            for key, value in data.items():
                catalog.setdefault(str(key), value)

    dest = ROOT / "output" / "long" / args.topic / "broll"
    dest.mkdir(parents=True, exist_ok=True)
    index, missing = {}, []
    with httpx.Client(follow_redirects=True, timeout=120, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for vid in sorted(vids):
            entry = catalog.get(vid)
            if not isinstance(entry, dict):
                missing.append(vid)
                continue
            files = [f for f in entry.get("files", [])
                     if f.get("w") and f.get("h") and f.get("link")
                     and f["h"] <= f["w"] <= 1920]
            if not files:
                missing.append(vid)
                continue
            target = dest / f"{vid}.mp4"
            if not target.is_file() or target.stat().st_size <= 10 * 1024:
                try:
                    response = client.get(max(files, key=lambda f: f["w"])["link"])
                    response.raise_for_status()
                    target.write_bytes(response.content)
                except (httpx.HTTPError, OSError):
                    missing.append(vid)
                    continue
                if target.stat().st_size <= 10 * 1024:
                    missing.append(vid)
                    continue
            index[vid] = entry
    (dest / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"clip {len(vids)} ok {len(index)} thiếu {missing}", flush=True)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
