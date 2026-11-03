from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ("title", "thumbnail_text", "first_frame_0_1s", "voice_0_3s", "escalation_3_10s", "payoff", "series_context")
REQUIRED = FIELDS[:-1]
NUM_RE = re.compile(r"(?<![\w])([+-]?\d[\d.,]*)(?:\s*)(%|km|cm|m|USD|ETH|năm|tỷ|triệu|nghìn)?(?![\w])", re.I)
UNIT = {"km": ("length", 1000), "m": ("length", 1), "cm": ("length", .01), "%": ("percent", .01), "tỷ": ("scalar", 1e9), "triệu": ("scalar", 1e6), "nghìn": ("scalar", 1e3), "usd": ("usd", 1), "eth": ("eth", 1), "năm": ("year", 1)}


def _norm(s):
    return unicodedata.normalize("NFC", s)


def _verified(verification):
    return {r.get("fact_id"): r for r in (verification or {}).get("results", []) if isinstance(r, dict)}


def _facts(store):
    return (store or {}).get("facts", []) if isinstance(store, dict) else []


def _text(pkg):
    return " ".join(pkg.get(f, "") for f in FIELDS if isinstance(pkg.get(f, ""), str))


def _number(s):
    # Vietnamese formatting: dots group thousands, comma marks decimal.
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _number_values(text):
    for m in NUM_RE.finditer(text):
        n = _number(m.group(1))
        if n is not None:
            u = (m.group(2) or "").lower()
            yield n, UNIT.get(u, ("scalar", 1))[0], UNIT.get(u, ("scalar", 1))[1], m.group(0)


def _fact_numbers(f):
    q = f.get("quantity") or f.get("time") or {}
    out = []
    if isinstance(q, dict) and isinstance(q.get("value"), (int, float)):
        unit = str(q.get("unit", "")).lower()
        mapped = {"kilometer": "km", "kilometers": "km", "metre": "m", "meter": "m", "meters": "m", "centimeter": "cm", "year": "năm", "years": "năm", "billion": "tỷ", "million": "triệu", "thousand": "nghìn", "percent": "%"}.get(unit, unit)
        kind, scale = UNIT.get(mapped, ("scalar", 1))
        out.append((float(q["value"]), kind, scale))
    for n, kind, scale, _ in _number_values(f.get("statement_vi", "")):
        out.append((n, kind, scale))
    for phrase in (f.get("source_span"),):
        if isinstance(phrase, str):
            out.extend((n, k, sc) for n, k, sc, _ in _number_values(phrase))
    for evidence in f.get("evidence", []) if isinstance(f.get("evidence"), list) else []:
        span = evidence.get("source_span", evidence.get("span", "")) if isinstance(evidence, dict) else ""
        out.extend((n, k, sc) for n, k, sc, _ in _number_values(span))
    return out


def _names_in(text, store):
    found = []
    names = []
    for entity in (store or {}).get("entities", []) if isinstance(store, dict) else []:
        for alias in [entity.get("name", ""), *(entity.get("aliases", []) or [])]:
            if isinstance(alias, str) and alias:
                names.append(_norm(alias))
    text = _norm(text)
    for name in set(names):
        if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text):
            found.append(name)
    return found


def certain_checks(pkg, store, verification):
    flags = []
    if not isinstance(pkg, dict) or any(not isinstance(pkg.get(k), str) for k in REQUIRED) or ("claims" in pkg and not isinstance(pkg["claims"], list)):
        return {"flags": [{"code": "invalid_package", "severity": "human_review"}], "ok": False}
    facts = _facts(store)
    statuses = _verified(verification)
    available = {f.get("fact_id"): f for f in facts if isinstance(f, dict)}
    for claim in pkg.get("claims", []):
        if not isinstance(claim, dict) or not isinstance(claim.get("fact_ids", []), list):
            flags.append({"code": "invalid_claim", "severity": "human_review"})
            continue
        for fid in claim.get("fact_ids", []):
            if fid not in available:
                flags.append({"code": "unknown_fact_id", "fact_id": fid})
            elif statuses.get(fid, {}).get("status") != "verified":
                flags.append({"code": "unverified_fact_id", "fact_id": fid})
    verified = [f for f in facts if isinstance(f, dict) and statuses.get(f.get("fact_id"), {}).get("status") == "verified"]
    for n, kind, scale, raw in _number_values(_text(pkg)):
        value = n * scale
        if not any(any(k == kind and abs(v * sc - value) <= max(1e-8, abs(value) * 1e-8) for v, k, sc in _fact_numbers(f)) for f in verified):
            flags.append({"code": "number_not_found", "value": raw})
    return {"flags": flags, "ok": not flags}


def select_sources(pkg, store, verification, k=16, max_chars=24000):
    facts = _facts(store)
    states = _verified(verification)
    byid = {f.get("fact_id"): f for f in facts if isinstance(f, dict)}
    eligible = {fid: f for fid, f in byid.items() if states.get(fid, {}).get("status") == "verified"}
    text = _text(pkg)
    entities = _names_in(text, store)
    chosen = set()
    for f in eligible.values():
        linked = set(f.get("entity_ids", [])) | {f.get("subject"), f.get("object")}
        entity_ids = {e.get("entity_id") for e in (store or {}).get("entities", []) if any(_norm(a) in entities for a in [e.get("name", ""), *(e.get("aliases", []) or [])])}
        if linked & entity_ids:
            chosen.add(f["fact_id"])
    if isinstance(pkg.get("claims"), list):
        chosen |= {fid for c in pkg["claims"] if isinstance(c, dict) for fid in c.get("fact_ids", []) if fid in eligible}
    # Include explicit variant/conflict/comparable neighbors, including non-verified rows as conflict context.
    frontier = list(chosen)
    for fid in frontier:
        f = byid[fid]
        neighbors = set(f.get("conflicts_with", []) if isinstance(f.get("conflicts_with"), list) else [])
        if f.get("variant_group"):
            neighbors |= {x for x, other in byid.items() if other.get("variant_group") == f["variant_group"]}
        if f.get("comparable_group"):
            neighbors |= {x for x, other in byid.items() if other.get("comparable_group") == f["comparable_group"]}
        chosen |= neighbors & eligible.keys()
    rows = []
    for fid in sorted(chosen, key=lambda x: list(byid).index(x)):
        f = byid[fid]
        spans = []
        for ev in f.get("evidence", []) if isinstance(f.get("evidence"), list) else []:
            if isinstance(ev, dict) and ev.get("span"):
                spans.append({"source_id": ev.get("source_id"), "source_span": ev["span"]})
        rows.append({"fact_id": fid, "statement_vi": f.get("statement_vi"), "kind": f.get("kind"), "modality": (f.get("qualifiers") or {}).get("modality", f.get("modality")), "attributed_to": f.get("attributed_to"), "condition": f.get("condition"), "certainty": states[fid].get("certainty", f.get("certainty")), "status": states[fid].get("status"), "evidence": spans or ([{"source_id": x.get("source_id"), "source_span": x.get("source_span")} for x in f.get("evidence", []) if isinstance(x, dict) and x.get("source_span")]), "source_id": next((x.get("source_id") for x in spans), None)})
    truncated = len(rows) > k
    rows = rows[:max(0, k)]
    while rows and len(json.dumps(rows, ensure_ascii=False)) > max_chars:
        rows.pop()
        truncated = True
    flags = (["sources_truncated"] if truncated else [])
    if not rows and any(_text(pkg).strip() for _ in FIELDS):
        flags.append("no_sources")
    return {"sources": rows, "flags": flags}


def _run_batch(items, cli, timeout):
    prompt = (HERE / "review_prompt_v1.md").read_text(encoding="utf-8") + "\n\nPACKAGES_WITH_SOURCES:\n" + json.dumps(items, ensure_ascii=False)
    proc = subprocess.run([cli, "exec", "--json", "--skip-git-repo-check", "-s", "read-only", "-"], input=prompt, text=True, capture_output=True, timeout=timeout, check=False)
    model, tokens, answer = None, None, None
    for line in proc.stdout.splitlines():
        try: event = json.loads(line)
        except ValueError: continue
        if event.get("type") == "turn.completed":
            model = event.get("model") or model
            # codex exec --json: usage nằm ở turn.completed.usage (input gồm cả phần cache; output gồm cả reasoning nếu có).
            u = event.get("usage") or {}
            if u.get("input_tokens") is not None:
                tokens = int(u.get("input_tokens", 0)) + int(u.get("output_tokens", 0)) + int(u.get("reasoning_output_tokens", 0))
        if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message": answer = event["item"].get("text")
        payload = event.get("payload", {})
        if payload.get("type") == "turn_context": model = payload.get("model") or model
        usage = payload.get("info", {}).get("total_token_usage", {})
        if usage.get("total_tokens") is not None: tokens = usage["total_tokens"]
    if proc.returncode: raise RuntimeError(proc.stderr[-1000:] or "review CLI failed")
    return json.loads(answer if answer is not None else proc.stdout.strip()), model or _configured_model(cli), tokens

def _configured_model(cli):
    """Event JSON của codex không ghi model; lấy từ cấu hình CLI (chỉ dòng model, không đọc gì khác)."""
    if cli != "codex": return "unknown"
    try:
        for line in (Path.home()/".codex"/"config.toml").read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("model ") or line.strip().startswith("model="): return "codex:"+line.split("=",1)[1].strip().strip('"')
    except OSError: pass
    return "codex:unknown"


def review_batch(packages_with_sources, cli="codex", batch_size=6, timeout=600, replay=None):
    replay_data = None
    if replay:
        replay_data = json.loads(Path(replay).read_text(encoding="utf-8"))
    entries, total_tokens, model = [], 0, "replay" if replay else None
    chunks = [packages_with_sources[i:i + batch_size] for i in range(0, len(packages_with_sources), max(1, batch_size))]
    for i, chunk in enumerate(chunks):
        if replay_data is not None:
            data = replay_data[i] if isinstance(replay_data, list) and replay_data and isinstance(replay_data[0], list) else replay_data
            md, tok = "replay", None
        else:
            data, md, tok = _run_batch(chunk, cli, timeout)
        if isinstance(data, dict):
            data = data.get("entries", data.get("reviews", []))
        if not isinstance(data, list): raise ValueError("review response must be array")
        model = md or model
        if isinstance(tok, int): total_tokens += tok
        for entry in data:
            if isinstance(entry, dict):
                entry = dict(entry); entry["model"] = md; entry["tokens"] = (tok // len(chunk) if isinstance(tok, int) and chunk else None)
            entries.append(entry)
    return {"entries": entries, "model": model or "unknown", "tokens": total_tokens if total_tokens else None}


def decide(certain, review_entry):
    if not isinstance(review_entry, dict): return {"verdict": "HUMAN_REVIEW", "reasons": ["missing or malformed review entry"]}
    verdict = review_entry.get("verdict")
    if verdict == "REJECT": return {"verdict": "REJECT", "reasons": review_entry.get("reasons", [])}
    if verdict not in ("ACCEPT", "HUMAN_REVIEW"): return {"verdict": "HUMAN_REVIEW", "reasons": ["invalid reviewer verdict"]}
    if verdict == "HUMAN_REVIEW": return {"verdict": verdict, "reasons": review_entry.get("reasons", [])}
    flags = {f.get("code") for f in certain.get("flags", []) if isinstance(f, dict)} if isinstance(certain, dict) else {"invalid_certain_result"}
    if flags & {"number_not_found", "unknown_fact_id", "unverified_fact_id", "invalid_package", "invalid_claim"}:
        return {"verdict": "HUMAN_REVIEW", "reasons": ["certain check flags require review"]}
    if not review_entry.get("citations"):
        return {"verdict": "HUMAN_REVIEW", "reasons": ["ACCEPT requires citations"]}
    return {"verdict": "ACCEPT", "reasons": review_entry.get("reasons", [])}


def _read(path): return json.loads(Path(path).read_text(encoding="utf-8"))


def run_items(items_path, stores, out, batch_size=6, timeout=600, replay=None, cli="codex"):
    p = Path(items_path)
    paths = sorted(p.glob("*.json")) if p.is_dir() else [p]
    packages, outcomes = [], []
    for path in paths:
        try:
            raw = _read(path)
        except (OSError, ValueError):
            outcomes.append({"package_id": path.stem, "certain": {"flags": [{"code": "invalid_package", "severity": "human_review"}], "ok": False}, "review": None, "decision": {"verdict": "HUMAN_REVIEW", "reasons": ["items JSON invalid or unreadable"]}})
            continue
        records = raw if isinstance(raw, list) else [raw]
        for ix, pkg in enumerate(records):
            topic = pkg.get("topic_id", path.stem)
            store_path = Path(stores) / f"{topic}.json"
            ver_path = Path(stores) / f"{topic}.verification.json"
            try: store, ver = _read(store_path), _read(ver_path)
            except (OSError, ValueError): store, ver = {}, {}
            pid = pkg.get("package_id", f"{path.stem}-{ix}")
            certain = certain_checks(pkg, store, ver)
            selected = select_sources(pkg, store, ver)
            packages.append({"package_id": pid, "package": pkg, **selected})
            outcomes.append({"package_id": pid, "certain": certain, "source_flags": selected["flags"]})
        for alt in raw.get("alternates", []) if isinstance(raw, dict) else []:
            topic = alt.get("topic_id", path.stem); store_path=Path(stores)/f"{topic}.json"; ver_path=Path(stores)/f"{topic}.verification.json"
            try: store,ver=_read(store_path),_read(ver_path)
            except (OSError,ValueError): store,ver={},{}
            pid=alt.get("package_id",f"{path.stem}-alt-{len(packages)}"); c=certain_checks(alt,store,ver); ss=select_sources(alt,store,ver)
            packages.append({"package_id":pid,"package":alt,**ss}); outcomes.append({"package_id":pid,"certain":c,"source_flags":ss["flags"]})
    try:
        reviews = review_batch(packages, cli, batch_size, timeout, replay)
    except (OSError, ValueError, subprocess.TimeoutExpired, RuntimeError):
        reviews = {"entries": [], "model": "unavailable", "tokens": None}
    counts = {}
    for e in reviews["entries"]:
        if isinstance(e, dict): counts[e.get("package_id")]=counts.get(e.get("package_id"),0)+1
    for outcome in outcomes:
        matches=[e for e in reviews["entries"] if isinstance(e,dict) and e.get("package_id")==outcome["package_id"]]
        entry=matches[0] if len(matches)==1 and counts.get(outcome["package_id"])==1 else None
        if entry is None and matches: entry={"verdict":"invalid"}
        outcome["review"]=entry
        outcome["decision"]=decide(outcome["certain"],entry)
    result={"items":outcomes,"review_model":reviews["model"],"review_tokens_total":reviews["tokens"]}
    Path(out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main(argv=None):
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True); r=sub.add_parser("run")
    r.add_argument("--items",required=True); r.add_argument("--stores",required=True); r.add_argument("--out",required=True); r.add_argument("--batch-size",type=int,default=6); r.add_argument("--timeout",type=int,default=600); r.add_argument("--replay"); r.add_argument("--cli",default="codex")
    a=p.parse_args(argv); run_items(a.items,a.stores,a.out,a.batch_size,a.timeout,a.replay,a.cli)


if __name__ == "__main__": main()
