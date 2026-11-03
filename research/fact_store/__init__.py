"""Deterministic validator for Structured Fact Store v0.2."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VALIDATOR_VERSION = "0.2.0"


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _schema_errors(value, schema_path):
    schema = _read_json(schema_path)
    try:
        import jsonschema
    except ImportError:
        # Minimal fallback: structural top-level checks; semantic checks below remain active.
        req = schema.get("required", [])
        errs = [f"$ missing required property {key}" for key in req if key not in value]
        if not isinstance(value, dict):
            errs.append("$ must be an object")
        return errs
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in validator.iter_errors(value)]


def _predicate_table():
    return _read_json(ROOT / "predicates.json")["predicates"]


def _entity_type(entity_id, entities):
    ent = entities.get(entity_id)
    return ent.get("type") if ent else None


def validate_store(store):
    """Return a list of schema and semantic validation errors."""
    errors = _schema_errors(store, ROOT / "fact_store.schema.json")
    if not isinstance(store, dict):
        return errors
    predicates = _predicate_table()
    sources = {s.get("source_id"): s for s in store.get("sources", []) if isinstance(s, dict)}
    entities = {e.get("entity_id"): e for e in store.get("entities", []) if isinstance(e, dict)}
    facts = store.get("facts", [])
    fact_ids = {f.get("fact_id") for f in facts if isinstance(f, dict)}
    groups = defaultdict(list)
    comparable = defaultdict(list)

    for i, fact in enumerate(facts):
        if not isinstance(fact, dict):
            continue
        path = f"facts[{i}]"
        subj = fact.get("subject")
        if subj not in entities:
            errors.append(f"{path}.subject: unknown entity_id {subj!r}")
        pred_name = fact.get("predicate")
        pred = predicates.get(pred_name)
        if pred is None:
            errors.append(f"{path}.predicate: unknown predicate {pred_name!r}")
        elif pred_name == "other" and not fact.get("predicate_text"):
            errors.append(f"{path}.predicate_text: required when predicate='other'")
        else:
            stype = _entity_type(subj, entities)
            allowed = pred.get("subject", "any").split("|")
            if stype and "any" not in allowed and stype not in allowed:
                errors.append(f"{path}.subject: type {stype!r} not allowed for {pred_name}")
            needs = pred.get("needs", [])
            for need in needs:
                if need == "quantity" and not fact.get("quantity"):
                    errors.append(f"{path}: predicate {pred_name} requires quantity")
                elif need == "time" and not fact.get("time"):
                    errors.append(f"{path}: predicate {pred_name} requires time")
                elif need.startswith("qualifiers."):
                    cur = fact
                    for part in need.split("."):
                        cur = cur.get(part) if isinstance(cur, dict) else None
                    if cur is None:
                        errors.append(f"{path}: predicate {pred_name} requires {need}")
            if "object" in pred and fact.get("object_is_entity"):
                oid = fact.get("object")
                otype = _entity_type(oid, entities)
                if not otype:
                    errors.append(f"{path}.object: unknown entity_id {oid!r}")
                elif "any" not in pred["object"].split("|") and otype not in pred["object"].split("|"):
                    errors.append(f"{path}.object: type {otype!r} not allowed for {pred_name}")
            elif "object" in pred and pred["object"] != "any" and fact.get("object") is not None and not fact.get("object_is_entity"):
                if "literal" not in pred["object"].split("|"):
                    errors.append(f"{path}.object: predicate {pred_name} requires an entity object")

        q = fact.get("qualifiers", {})
        if fact.get("kind") == "attributed" and q.get("attributed_to") not in entities:
            errors.append(f"{path}.qualifiers.attributed_to: must reference an entity")
        if fact.get("kind") == "legend":
            if q.get("modality") != "legendary":
                errors.append(f"{path}.qualifiers.modality: legend requires 'legendary'")
            if not q.get("according_to_edition"):
                errors.append(f"{path}.qualifiers.according_to_edition: required for legend")
        if fact.get("kind") == "tradition" and q.get("modality") != "traditional":
            errors.append(f"{path}.qualifiers.modality: tradition requires 'traditional'")
        edition = q.get("according_to_edition")
        if edition and edition not in {ev.get("source_id") for ev in fact.get("evidence", [])}:
            errors.append(f"{path}.qualifiers.according_to_edition: must be an evidence source_id")
        for j, ev in enumerate(fact.get("evidence", [])):
            if ev.get("source_id") not in sources:
                errors.append(f"{path}.evidence[{j}].source_id: unknown source_id {ev.get('source_id')!r}")
        for ref in fact.get("conflicts_with", []):
            if ref not in fact_ids:
                errors.append(f"{path}.conflicts_with: unknown fact_id {ref!r}")
        if fact.get("variant_group"):
            groups[fact["variant_group"]].append(fact)
        if fact.get("comparable_group"):
            comparable[fact["comparable_group"]].append(fact)

    for name, members in groups.items():
        if len(members) < 2:
            errors.append(f"variant_group {name!r}: needs at least 2 facts")
    for name, members in comparable.items():
        if len(members) < 2:
            errors.append(f"comparable_group {name!r}: needs at least 2 facts")
        measures = {(f.get("quantity") or {}).get("measure") for f in members}
        units = {(f.get("quantity") or {}).get("unit") for f in members}
        if len(measures) > 1 or len(units) > 1:
            errors.append(f"comparable_group {name!r}: facts must share quantity.measure and unit")
    return errors


def _norm(s):
    s = unicodedata.normalize("NFC", s)
    s = s.translate(str.maketrans({"‘": "'", "’": "'", "‛": "'", "“": '"', "”": '"', "„": '"', "‐": "-", "‑": "-", "–": "-", "—": "-"}))
    return re.sub(r"\s+", " ", s).strip()


def _index_entry(sources_dir, source_id):
    index = _read_json(Path(sources_dir) / "sources_index.json")
    entries = index if isinstance(index, list) else index.get("sources", [])
    return next((e for e in entries if e.get("source_id") == source_id), None)


def span_match(fact, sources_dir):
    """Match evidence spans against byte-hash-verified snapshots; return span check records."""
    out = []
    root = Path(sources_dir)
    for ev in fact.get("evidence", []):
        sid = ev.get("source_id", "")
        entry = _index_entry(root, sid)
        span = _norm(ev.get("span", ""))
        base = {"method": "span_match", "result": "not_found", "source_id": sid, "snapshot_sha256": "", "offset": None, "at": datetime.now(timezone.utc).isoformat()}
        if not entry or len(span) < 12:
            out.append(base)
            continue
        name = entry.get("snapshot_path") or f"{sid}.txt"
        path = root / name
        try:
            raw = path.read_bytes()
        except OSError:
            out.append(base)
            continue
        digest = hashlib.sha256(raw).hexdigest()
        expected = entry.get("snapshot_sha256")
        base["snapshot_sha256"] = digest
        if not expected or digest != expected:
            out.append(base)
            continue
        text = raw.decode("utf-8")
        normalized = _norm(text)
        pos = normalized.find(span)
        if pos >= 0:
            base.update(result="supports", offset=pos)
        out.append(base)
    return out


def _check_results(checks):
    results = {c.get("result") for c in checks if c.get("method") != "span_match"}
    return results


def compute_verification(store, external_checks=None, sources_dir=None):
    errors = validate_store(store)
    checks_input = external_checks or []
    if isinstance(checks_input, dict):
        checks_input = checks_input.get("checks", [])
    extraction_models = {f.get("fact_id"): f.get("extraction", {}).get("by") for f in store.get("facts", [])}
    for c in checks_input:
        if c.get("method") == "independent_llm":
            fid = c.get("fact_id")
            em = extraction_models.get(fid)
            if not em or c.get("model") == em or c.get("extraction_model") == c.get("model"):
                errors.append(f"check {fid!r}: independent_llm model must differ from extraction.by")
            elif c.get("extraction_model") != em:
                errors.append(f"check {fid!r}: extraction_model must equal extraction.by ({em})")
        if c.get("fact_id") not in extraction_models:
            errors.append(f"check: unknown fact_id {c.get('fact_id')!r}")
        if c.get("method") == "cross_source":
            fact = next((f for f in store.get("facts", []) if f.get("fact_id") == c.get("fact_id")), {})
            original_ids = {e.get("source_id") for e in fact.get("evidence", [])}
            original_publishers = {s.get("publisher") for s in store.get("sources", []) if s.get("source_id") in original_ids and s.get("publisher")}
            cross_src = next((s for s in store.get("sources", []) if s.get("source_id") == c.get("source_id")), None)
            if not cross_src:
                errors.append(f"check {c.get('fact_id')!r}: cross_source source_id must exist in store.sources")
            elif c.get("source_id") in original_ids:
                errors.append(f"check {c.get('fact_id')!r}: cross_source source must differ from evidence source")
            if c.get("publisher") in original_publishers:
                errors.append(f"check {c.get('fact_id')!r}: cross_source publisher must differ from evidence publisher")
    if errors:
        raise ValueError("\n".join(errors))

    by_fact = defaultdict(list)
    for c in checks_input:
        by_fact[c["fact_id"]].append({k: v for k, v in c.items() if k != "fact_id"})
    facts = store.get("facts", [])
    groups = Counter(f.get("variant_group") for f in facts if f.get("variant_group"))
    ids = {f.get("fact_id"): f for f in facts}
    results = []
    now = datetime.now(timezone.utc).isoformat()
    for fact in facts:
        checks = span_match(fact, sources_dir) if sources_dir else []
        checks.extend(by_fact.get(fact["fact_id"], []))
        # Add local conflict/group semantics; comparable_group intentionally does not imply dispute.
        span_ok = any(c.get("method") == "span_match" and c.get("result") == "supports" for c in checks)
        nonspan = [c for c in checks if c.get("method") != "span_match"]
        vals = _check_results(nonspan)
        contradictory = "contradicts" in vals
        mixed = "supports" in vals and contradictory
        disputed = bool(fact.get("variant_group") or fact.get("conflicts_with") or mixed)
        if not span_ok or contradictory:
            status = "rejected"
        elif disputed:
            status = "disputed"
        elif any(c.get("result") == "supports" and c.get("method") in {"independent_llm", "human", "cross_source"} for c in nonspan):
            status = "verified"
        else:
            status = "unverified"
        hedged = fact.get("source_hedge", "none") != "none"
        certainty = "contested" if disputed else ("established" if status == "verified" and not hedged else ("uncertain" if status == "verified" else "unknown"))
        results.append({"fact_id": fact["fact_id"], "status": status, "certainty": certainty, "checks": checks})
    return {"schema_version": "0.2", "topic_id": store["topic_id"], "store_sha256": hashlib.sha256(json.dumps(store, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()).hexdigest(), "validator_version": VALIDATOR_VERSION, "results": results}
