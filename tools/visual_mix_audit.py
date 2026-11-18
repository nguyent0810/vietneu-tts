"""Read-only structural audit of FS/BUD/VSD plans and existing timing artifacts.

No rendering, probing, network, credentials, or gate changes. Run from a worktree:
  .venv/bin/python tools/visual_mix_audit.py --long --short --out audit.json
The production data root is discovered in ancestors, or supplied with --data-root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT))
from tools import visual_mix as VM

# These are content classes for this audit, not additions to production TEXT_KINDS.
STUDIO_TEXT = frozenset({"hook_poster", "hook_slam", "myth_strike", "window",
                         "stamp", "source_card", "quote", "close", "list_build"})
LOOKUP = frozenset({"yeartable", "daytable", "month_sheet", "thiep_cuoi",
                    "decade_grid", "decade_han_grid", "tet_calendar", "nguhanh_matrix",
                    "kinhdich_cungphi", "lookup", "month_hoangdao", "board", "table",
                    "ledger", "split", "budtable", "oai_nghi_table", "mudra_grid"})
GRAPHICS = frozenset({"wheel", "cycle_draw", "time_spine", "count_ring", "bars",
                      "unit_grid", "pan_tour", "calendar"})


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spoken_tokens(text):
    """TTS lowercases and strips display markup; punctuation is not new speech."""
    return re.findall(r"\w+", unicodedata.normalize("NFC", str(text)).casefold())


@lru_cache(maxsize=4096)
def normalized_tokens(text):
    # Same local number/abbreviation normalizer as render_engine; no TTS model.
    from vieneu_utils.phonemize_text import _get_normalizer
    normalized = _get_normalizer().normalize_batch([text.replace("**", "")], punc_norm=True)[0]
    return spoken_tokens(normalized)


def rows_in(path):
    data = read(path)
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    return data.get("videos", [data]) if isinstance(data, dict) else []


def channel(row):
    value = str(row.get("series") or row.get("channel") or "").lower()
    if value in {"bud", "fs", "vsd"}:
        return value.upper()
    for name in ("bud", "fs", "vsd"):
        if str(row.get("id", "")).lower().startswith(("l_" + name + "_", name + "_")):
            return name.upper()
    return None


def is_text(scene):
    refs = [scene.get("image"), *(scene.get("images") or [])]
    return scene["kind"] in VM.TEXT_KINDS and (
        scene["kind"] in VM.FULLSCREEN_TEXT_KINDS or not any(refs))


def metrics(scenes):
    result = VM.measure(scenes)
    active = [s for s in scenes if s["t1"] > s["t0"]]
    result["text_scenes"] = sum(is_text(s) for s in active)
    result["text_scene_share"] = result["text_scenes"] / len(active) if active else 0
    result["minutes"] = result["seconds"] / 60
    result["top6"] = list(result["by_kind"].items())[:6]
    result["lookup_seconds"] = sum(s["t1"] - s["t0"] for s in active if s.get("category") == "lookup")
    result["lookup_share"] = result["lookup_seconds"] / result["seconds"] if result["seconds"] else 0
    result["fullscreen_text_including_lookup_share"] = (
        result["text_seconds"] + result["lookup_seconds"]) / result["seconds"] if result["seconds"] else 0
    return result


def classify_studio(scene):
    """Classify actual device semantics, never a hook-gate whitelist.

    quote/close/source_card ignore img in their build(), so decorative img does
    not exempt them. hook_* renders an actual photo band: still text dominant.
    split is a deliberate comparison board, not two photographs in Studio.
    """
    device = scene.get("device", scene.get("type", ""))
    if device in LOOKUP:
        return "lookup", "lookup:" + device
    if device in STUDIO_TEXT:
        return "text", "quote" if device == "quote" else "kinetic"
    if device in GRAPHICS:
        return "media" if device == "pan_tour" else "graphic", device
    raise ValueError(f"unknown Studio device: {device}")


def studio_scenes(spec, plan):
    windows, devices = plan["windows"], plan["devices"]
    source = list(spec["scenes"])
    if spec.get("loop", True):
        source.append(source[0])
    if len(windows) != len(devices) or len(devices) != len(source):
        raise ValueError("Studio windows/devices/spec count mismatch")
    out, end = [], 0.0
    for window, device, scene in zip(windows, devices, source):
        if device != scene["device"]:
            raise ValueError("Studio cached device differs from current spec")
        a, b = map(float, window)
        if not all(map(math.isfinite, (a, b))) or abs(a - end) > 1e-6 or b <= a:
            raise ValueError("Studio windows must be contiguous, positive, start at zero")
        category, kind = classify_studio(scene)
        # hookPhoto is a band, not a media scene; quote ignores img entirely.
        image = scene.get("img") if device == "pan_tour" or device.startswith("hook_") else None
        image = (spec.get("imgs") or {}).get(image, image)
        out.append(dict(kind=kind, category=category, device=device, t0=a, t1=b, image=image))
        end = b
    return out


def aggregate(records):
    out = {}
    for ch in ("BUD", "FS", "VSD"):
        rs = [r for r in records if r.get("channel") == ch and r.get("metrics")]
        if not rs:
            out[ch] = {"n": 0}
            continue
        ms = [r["metrics"] for r in rs]
        total = sum(m["seconds"] for m in ms)
        scenes = sum(m["scenes"] for m in ms)
        out[ch] = dict(n=len(rs), seconds=total,
            text_share_weighted=sum(m["text_seconds"] for m in ms) / total,
            text_share_mean=statistics.mean(m["text_share"] for m in ms),
            text_share_median=statistics.median(m["text_share"] for m in ms),
            text_scene_share_weighted=sum(m["text_scenes"] for m in ms) / scenes,
            images_per_minute_weighted=sum(m["unique_images"] for m in ms) * 60 / total,
            max_repeat=max(m["max_repeat"] for m in ms),
            over_15=sum(m["text_share"] > .15 for m in ms),
            lookup_share_weighted=sum(m["lookup_seconds"] for m in ms) / total,
            timing_sources=dict(Counter(r["timing_basis"] for r in rs)))
    return out


class Audit:
    def __init__(self, root, cutoff, sample):
        self.root, self.cutoff, self.sample = Path(root), cutoff, sample
        self.inputs = {}
        self.plan_conflicts = []

    def load(self, path):
        self.inputs[self.rel(path)] = digest(path)
        return read(path)

    def rel(self, path):
        return str(Path(path).relative_to(self.root))

    def base(self, row, path):
        return dict(id=row["id"], channel=channel(row), plan=self.rel(path),
                    planned_day=row.get("day"), planned_slot=row.get("slot"),
                    published_day=None, published_day_note="uploaded.json has no verified publish date",
                    style=row.get("style"))

    def plans(self, paths):
        found = {}
        conflicts = set()
        for path in sorted(paths):
            self.load(path)
            for row in rows_in(path):
                if row.get("id") and channel(row):
                    if row["id"] in found and found[row["id"]][0] != row:
                        conflicts.add(row["id"])
                        self.plan_conflicts.append(dict(id=row["id"],
                            plans=[self.rel(found[row["id"]][1]), self.rel(path)],
                            reason="different rows with same id; all versions excluded"))
                    found[row["id"]] = (row, path)
        return [pair for rid, pair in found.items() if rid not in conflicts]

    def uploaded(self, folder):
        path = folder / "uploaded.json"
        return self.load(path) if path.exists() else {}

    def upload_info(self, record, uploads):
        value = uploads.get(record["id"])
        record["listed_in_uploaded"] = value is not None
        if isinstance(value, dict):
            for key in ("publishedAt", "publish_at", "published_at"):
                if value.get(key):
                    record["published_day"] = str(value[key])[:10]
                    record["published_day_note"] = f"uploaded.json:{key}"
                    break

    def manifest(self, row, folder):
        path = folder / (row["id"] + ".json")
        data = self.load(path)
        segs = data.get("segments")
        if not isinstance(segs, list) or not segs:
            raise ValueError("missing/non-list segments")
        if len(segs) != len(row.get("script") or []):
            raise ValueError(f"segment/script count mismatch: {len(segs)}/{len(row.get('script') or [])}")
        mismatches = [i + 1 for i, (seg, text) in enumerate(zip(segs, row["script"]))
                      if "text" in seg and spoken_tokens(seg["text"]) != spoken_tokens(text)
                      and spoken_tokens(seg["text"]) != normalized_tokens(text)]
        return path, data, mismatches

    def long(self):
        import hf_batch_render as HBR
        folder = self.root / "output/cl_staging/long"
        uploads = self.uploaded(folder)
        records = []
        for row, path in self.plans(folder.glob("plan_long_*.json")):
            record = self.base(row, path)
            record["nested_studio_devices"] = dict(Counter(v.get("device") for v in (row.get("visuals") or {}).values()
                                                          if v.get("type") == "studio"))
            self.upload_info(record, uploads)
            manifest = folder / "out" / (row["id"] + ".json")
            if not manifest.exists():
                record.update(status="excluded", reason="no existing segment manifest")
                records.append(record)
                continue
            try:
                manifest, data, mismatches = self.manifest(row, folder / "out")
                record.update(manifest=self.rel(manifest), text_mismatch_lines=mismatches)
                if mismatches:
                    raise ValueError(f"plan differs from spoken text at {len(mismatches)} lines; cannot infer rendered plan")
                render = folder / "out" / (row["id"] + ".render.json")
                evidence = self.load(render) if render.exists() else {}
                mp4 = folder / "out" / (row["id"] + ".mp4")
                if not evidence.get("ok") and not mp4.exists():
                    raise ValueError("segments exist but no ok render sidecar or local mp4")
                scenes = HBR.visual_mix_scenes(row, data["segments"])
                record.update(status="measured", timing_basis="TTS segments", scenes=scenes,
                              metrics=metrics(scenes), duration_s=data.get("duration_s"),
                              render_evidence=self.rel(render) if evidence.get("ok") else self.rel(mp4),
                              cuts_estimated=any(m.get("cuts") for m in (row.get("media") or {}).values())
                              and any(not s.get("words") for s in data["segments"]))
            except Exception as exc:  # per-video adapter failure belongs in the evidence
                record.update(status="excluded", reason=f"{type(exc).__name__}: {exc}")
            records.append(record)
        return dict(records=records, summary=aggregate(records),
                    note="Current plans + existing TTS, not pixel classification; unchanged script does not prove unchanged visuals.")

    def short(self):
        import hf_batch_render as HBR
        records, excluded, inventory = [], [], {}
        for ch in ("bud", "fs", "vsd"):
            folder = self.root / "output/cl_staging" / ch
            candidates = self.plans((folder / "specs").glob("*.json") if ch == "vsd" else folder.glob("plan*.json"))
            inventory[ch.upper()] = dict(plan_count=len(candidates))
            uploads = self.uploaded(folder)
            if ch != "vsd":
                candidates = [(r, p) for r, p in candidates if r.get("day") and str(r["day"]) <= self.cutoff]
            candidates.sort(key=lambda rp: (str(rp[0].get("day", "")), str(rp[0].get("slot", "")), rp[0]["id"]), reverse=True)
            measured = 0
            for row, path in candidates:
                if measured >= self.sample:
                    break
                record = self.base(row, path)
                self.upload_info(record, uploads)
                try:
                    job = self.root / "hyperframes_short/jobs" / row["id"] / "plan.json"
                    render = folder / "out" / (row["id"] + ".render.json")
                    if row.get("scenes"):
                        # Device inventory remains available even when timing is missing.
                        record["device_inventory"] = [dict(device=s["device"], category=classify_studio(s)[0]) for s in row["scenes"]]
                        if not job.exists():
                            raise ValueError("Studio spec exists but no cached job windows; no duration estimate substituted")
                        plan = self.load(job)
                        scenes = studio_scenes(row, plan)
                        record.update(timing_basis="Studio cached windows", timing_file=self.rel(job),
                                      render_verified=render.exists() and bool(self.load(render).get("ok")))
                    else:
                        if not render.exists():
                            raise ValueError("no ok render sidecar")
                        meta = self.load(render)
                        if not meta.get("ok"):
                            raise ValueError("render sidecar not ok")
                        style = row.get("style", "")
                        duration = float(meta["duration_s"])
                        if not math.isfinite(duration) or duration <= 0:
                            raise ValueError("invalid rendered duration")
                        record.update(render_evidence=self.rel(render), render_style=meta.get("style"))
                        if style in LOOKUP:
                            scenes = [dict(kind="lookup:" + style, category="lookup", t0=0, t1=duration)]
                            record.update(timing_basis="render duration; whole lookup template", classification_basis="declared lookup style, not pixel audit")
                        elif (folder / "out" / (row["id"] + ".json")).exists():
                            manifest, data, mismatches = self.manifest(row, folder / "out")
                            if mismatches:
                                raise ValueError("plan differs from spoken text")
                            scenes = HBR.visual_mix_scenes(row, data["segments"])
                            record.update(timing_basis="TTS segments", timing_file=self.rel(manifest),
                                          tail_unmeasured_s=duration - scenes[-1]["t1"])
                        else:
                            # Custom recipes are not the bridge despite identical style labels.
                            raise ValueError("custom HTML/render duration only; no scene timing adapter, cannot infer text share from style")
                    record.update(status="measured", scenes=scenes, metrics=metrics(scenes))
                    records.append(record)
                    measured += 1
                except Exception as exc:  # never guess after a production adapter error
                    record.update(status="excluded", reason=f"{type(exc).__name__}: {exc}")
                    excluded.append(record)
            inventory[ch.upper()].update(eligible_before_cutoff=len(candidates), measured=measured,
                                          target=self.sample, deficit=max(0, self.sample - measured))
        return dict(records=records, excluded=excluded, summary=aggregate(records), inventory=inventory)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--long", action="store_true")
    parser.add_argument("--short", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--cutoff", default="2026-11-18")
    parser.add_argument("--sample", type=int, default=20)
    args = parser.parse_args(argv)
    if not (args.long or args.short) or args.sample < 1:
        parser.error("select --long and/or --short; --sample must be positive")
    root = args.data_root or next((p for p in [CODE_ROOT, *CODE_ROOT.parents]
                                         if (p / "output/cl_staging/long").is_dir()), None)
    if root is None:
        parser.error("no local dataset; supply --data-root")
    audit = Audit(root.resolve(), args.cutoff, args.sample)
    result = dict(schema=1, cutoff=args.cutoff, data_root=str(audit.root), code_root=str(CODE_ROOT),
                  limitations=["Structural adapters, no rendered pixel audit", "Scheduled day is not verified published day",
                                "Most recent measurable samples, not random or all uploaded videos"],
                  policy=dict(text_warn=VM.TEXT_WARN, text_error=VM.TEXT_ERROR,
                              repeat_warn=VM.REPEAT_WARN, repeat_error=VM.REPEAT_ERROR,
                              min_images_per_minute=VM.MIN_IMAGES_PER_MINUTE))
    if args.long:
        result["long"] = audit.long()
    if args.short:
        result["short"] = audit.short()
        non_lookup = [r for r in result["short"]["records"]
                      if r["metrics"]["lookup_share"] < 1]
        result["short"]["summary_non_lookup_videos"] = aggregate(non_lookup)
    # Freeze the local comparison basis as well as the measured input hashes.
    catalogs = {}
    for label, names, pattern in (
        ("longform", ["hyperframes_short/compositions/longform.js"], r"visuals\.([a-z_]+)\s*="),
        ("styles258", ["hyperframes_short/compositions/longform_styles.js"], r'register\("([a-z0-9_]+)"'),
        ("studio", [str(p.relative_to(CODE_ROOT)) for p in sorted((CODE_ROOT / "hyperframes_short/studio/devices").glob("*.js"))], r'HFS\.device\("([a-z0-9_]+)"'),
        ("creator_casewide", ["creator_v2/motion/hf/assets/engine/casewide.js",
                              "creator_v2/motion/hf/assets/engine/lab.js",
                              "creator_v2/motion/hf/assets/engine/chart.js"], r"B\.([a-z0-9_]+)\s*="),
    ):
        names = [name for name in names if (CODE_ROOT / name).exists()]
        catalogs[label] = dict(paths=names, kinds=sorted({kind for name in names
            for kind in re.findall(pattern, (CODE_ROOT / name).read_text(encoding="utf-8"))}))
    result["engine_catalogs"] = catalogs
    result["proposed_policy_not_applied"] = dict(
        long=dict(channels=["BUD", "FS", "VSD"], warn=.12, review=.15,
                  distinct_images_per_minute_warning=4, repeat_warn=4, repeat_review=6),
        short_narrative=dict(channels=["BUD", "FS", "VSD"], target=.30, warn=.30, review=.40,
                             vsd_minimum_sample_before_enforcement=20),
        short_lookup=dict(filler_target=.15, intentional_lookup_max=1.0, final_hold_seconds=3),
        gates=dict(opening_seconds=40, opening_unique_images=8, pace_seconds=120,
                   pace_static_seconds=4, pace_moving_seconds=8, naked_seconds=1.5,
                   hook_latest_seconds=.8, hook_min_luma=50, long_lookup_by_seconds=45,
                   old_hold_seconds=25, styles_max=3))
    result["input_sha256"] = audit.inputs
    result["plan_conflicts"] = audit.plan_conflicts
    result["code_sha256"] = {p: digest(CODE_ROOT / p) for p in (
        "tools/visual_mix_audit.py", "tools/visual_mix.py", "hf_batch_render.py", "hyperframes_bridge.py", "studio.py")}
    for catalog in catalogs.values():
        result["code_sha256"].update({p: digest(CODE_ROOT / p) for p in catalog["paths"]})
    reference = "creator_v2/docs/pm/2026-11-17-chuan-hinh-anh-5-kenh.md"
    if (CODE_ROOT / reference).exists():
        result["issue467_local_reference"] = dict(path=reference, sha256=digest(CODE_ROOT / reference),
                                                 live_issue_verified=False, gh_result="HTTP 401 Requires authentication")
    checks_path = args.out.with_suffix(".checks.json")
    if checks_path.exists():
        result["recorded_verification"] = read(checks_path)
        result["recorded_verification_note"] = "Historical test runs from companion JSON; audit does not run tests."
        result["recorded_verification_sha256"] = digest(checks_path)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k]["summary"] for k in ("long", "short") if k in result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
