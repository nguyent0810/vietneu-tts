"""Enrich Long rows with deterministic scene and motion suggestions.

``scene_decision`` is indexed by 1-based script line (string keys). Each entry
contains ``scene`` (picker payload and reason/candidates), ``motion`` (preset
and reason), and ``source`` (``picker`` or ``editor``). Existing visuals/media
keys are editorial choices and are retained without running either picker for
that line.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from library.tools import motion_picker, scene_picker


def _line_count(row: dict[str, Any]) -> int:
    lines = row.get("script") or row.get("sentences") or row.get("lines") or []
    return len(lines) if isinstance(lines, list) else 0


def _keys(mapping: Any) -> set[int]:
    if not isinstance(mapping, dict):
        return set()
    return {int(key) for key in mapping if str(key).isdigit()}


def enrich_long_plan(plan: Any, channel: str) -> Any:
    """Return enriched copy; accept a plan row or a list of rows."""
    rows = plan if isinstance(plan, list) else [plan]
    out = copy.deepcopy(rows)
    scene_profile = scene_picker.load_profile(None, channel)
    motion_profile = motion_picker.load_profile(None, channel)
    catalog = scene_picker.load_json(scene_picker.CATALOG)
    forbidden = set(scene_profile.get("forbidden_types") or [])

    for row in out:
        if not isinstance(row, dict) or row.get("lane") != "long":
            continue
        visuals = row.setdefault("visuals", {})
        media = row.setdefault("media", {})
        edited = _keys(visuals) | _keys(media)
        scene_input = copy.deepcopy(row)
        # Selectors regard these keys as occupied. Retain editor selections and
        # temporarily expose only the remaining lines to scene_picker.
        scene_input["visuals"] = {k: v for k, v in visuals.items() if str(k).isdigit() and int(k) in edited}
        scene_input["media"] = {k: v for k, v in media.items() if str(k).isdigit() and int(k) in edited}
        scene_patch, scene_log = scene_picker.choose(scene_input, scene_profile, catalog)

        # Motion picker consumes media entries. Add newly picked scenes to a
        # temporary media view before merging visuals, so they are not blocked.
        motion_input = copy.deepcopy(row)
        motion_media = copy.deepcopy(media)
        for key, spec in scene_patch.items():
            if int(key) not in edited:
                motion_media[key] = {"kind": "image", "scene": spec}
        motion_input["media"] = motion_media
        motion_input["visuals"] = copy.deepcopy(visuals)
        motion_patch, motion_log = motion_picker.choose(motion_input, motion_profile)

        decisions: dict[str, dict[str, Any]] = {}
        scene_by_line = {d["sentence"]: d for d in scene_log["decisions"]}
        motion_by_line: dict[int, list[dict[str, Any]]] = {}
        for decision in motion_log:
            motion_by_line.setdefault(int(decision["sentence"]), []).append(decision)

        for index in range(1, _line_count(row) + 1):
            key = str(index)
            if index in edited:
                decisions[key] = {"source": "editor"}
                continue
            if key not in scene_patch:
                continue
            scene_decision = scene_by_line.get(index, {})
            if scene_patch[key].get("type") in forbidden:
                raise AssertionError(f"scene picker returned forbidden type on line {index}")
            motion_decision = motion_by_line.get(index, [])
            motion_payload = motion_patch.get(key, {})
            motion_choice = motion_payload.get("preset") or (motion_decision[0].get("preset") if motion_decision else None)
            motion_reason = "; ".join(dict.fromkeys(d.get("reason", "") for d in motion_decision if d.get("reason")))
            decisions[key] = {
                "scene": {"picked": scene_patch[key], "ly_do": scene_decision.get("reason", ""),
                          "ung_vien": scene_decision.get("candidates", [])},
                "motion": {"preset": motion_choice, "ly_do": motion_reason,
                           **({"picked": motion_payload} if motion_payload else {})},
                "source": "picker",
            }
            visuals.setdefault(key, scene_patch[key])
            if key in motion_patch:
                for field, value in motion_patch[key].items():
                    media.setdefault(key, {}).setdefault(field, value)
        row["scene_decision"] = decisions
    return out if isinstance(plan, list) else out[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", type=Path)
    ap.add_argument("--channel", choices=("bud", "fs"), required=True)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    original = json.loads(args.plan.read_text(encoding="utf-8"))
    enriched = enrich_long_plan(original, args.channel)
    if args.write:
        args.plan.write_text(json.dumps(enriched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = enriched if isinstance(enriched, list) else [enriched]
    selected = sum(1 for row in rows if isinstance(row, dict) for v in (row.get("scene_decision") or {}).values() if v.get("source") == "picker")
    print(json.dumps({"rows": len(rows), "filled_lines": selected,
                      "mode": "write" if args.write else "dry-run"}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
