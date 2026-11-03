from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

from research.fact_store.simple import pipeline as simple

HERE = Path(__file__).resolve().parent
CODES = {"unsupported", "misattribution", "misleading_implication", "stale_timeframe", "conflicting_source", "modality_dropped", "missing_source"}
FIELDS = ("title", "thumbnail_text", "first_frame_0_1s", "voice_0_3s", "escalation_3_10s", "payoff", "series_context")


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def select_reviewer_sources(pkg, store, verification, k=32, max_chars=36000):
    """Select directly relevant facts plus all linked conflict/variant/comparable facts."""
    facts = simple._facts(store)
    states = simple._verified(verification)
    byid = {f.get("fact_id"): f for f in facts if isinstance(f, dict) and f.get("fact_id")}
    # Đầu vào là một video gồm nhiều phương án: gộp chữ và claims của mọi phương án.
    cands = [c for c in pkg.get("candidates", []) if isinstance(c, dict)] if isinstance(pkg.get("candidates"), list) else []
    text = " ".join([simple._text(pkg)] + [simple._text(c) for c in cands])
    entities = simple._names_in(text, store)
    entity_ids = {e.get("entity_id") for e in (store or {}).get("entities", []) if isinstance(e, dict) and any(simple._norm(a) in entities for a in [e.get("name", ""), *(e.get("aliases", []) or [])] if isinstance(a, str))}
    direct = set()
    for fid, fact in byid.items():
        linked = set(fact.get("entity_ids", []) or []) | {fact.get("subject"), fact.get("object")}
        if linked & entity_ids:
            direct.add(fid)
    claims = [c for owner in [pkg, *cands] for c in (owner.get("claims") if isinstance(owner.get("claims"), list) else [])]
    for claim in claims:
        if isinstance(claim, dict):
            ids = claim.get("fact_ids", [])
            ids = [ids] if isinstance(ids, str) else ids if isinstance(ids, list) else []  # creative đôi khi ghi chuỗi
            direct.update(fid for fid in ids if fid in byid)
    # Group expansion is transitive so a conflict's own variants are not lost.
    chosen, queue = set(direct), list(direct)
    while queue:
        fid = queue.pop()
        fact = byid[fid]
        neighbors = set(fact.get("conflicts_with", []) or [])
        for key in ("variant_group", "comparable_group"):
            group = fact.get(key)
            if group:
                neighbors.update(x for x, other in byid.items() if other.get(key) == group)
        for other in byid.values():
            if fid in (other.get("conflicts_with") or []):
                neighbors.add(other["fact_id"])
        for n in neighbors & byid.keys():
            if n not in chosen:
                chosen.add(n); queue.append(n)
    order = {fid: n for n, fid in enumerate(byid)}
    rows = []
    for fid in sorted(chosen, key=order.get):
        f = byid[fid]
        evs = f.get("evidence", []) if isinstance(f.get("evidence"), list) else []
        evidence = [{"source_id": e.get("source_id"), "quote": e.get("span", e.get("source_span"))} for e in evs if isinstance(e, dict) and (e.get("span") or e.get("source_span"))]
        status = states.get(fid, {}).get("status", "unverified")
        conflicting = any((n in chosen) for n in (f.get("conflicts_with") or [])) or any(
            any(fid in (other.get("conflicts_with") or []) for other in byid.values())
            or (f.get("variant_group") and other.get("variant_group") == f.get("variant_group") and other["fact_id"] != fid)
            or (f.get("comparable_group") and other.get("comparable_group") == f.get("comparable_group") and other["fact_id"] != fid)
            for other in byid.values())
        rows.append({"fact_id": fid, "statement_vi": f.get("statement_vi"), "kind": f.get("kind"), "modality": (f.get("qualifiers") or {}).get("modality", f.get("modality")), "attributed_to": f.get("attributed_to"), "condition": f.get("condition"), "certainty": states.get(fid, {}).get("certainty", f.get("certainty")), "status": status, "conflicting": bool(conflicting), "evidence": evidence})
    removed = []
    while len(rows) > k or (rows and len(json.dumps(rows, ensure_ascii=False)) > max_chars):
        removed.insert(0, rows.pop()["fact_id"])
    return {"sources": rows, "sources_truncated": removed, "sources_missing": not bool(rows)}


def _configured_model(cli="codex"):
    return simple._configured_model(cli)


def _run_batch(items, cli="codex", timeout=600):
    prompt = (HERE / "reviewer_prompt_v2.md").read_text(encoding="utf-8")
    prompt = prompt.replace("ghi ngày hiện tại sẽ được cung cấp", f"ngày hiện tại là {dt.date.today().isoformat()}")
    prompt += "\n\nINPUT_JSON:\n" + json.dumps({"videos": items}, ensure_ascii=False)
    start = time.monotonic()
    proc = subprocess.run([cli, "exec", "--json", "--skip-git-repo-check", "-s", "read-only", "-"], input=prompt, text=True, capture_output=True, timeout=timeout, check=False)
    seconds = time.monotonic() - start
    if proc.returncode:
        raise RuntimeError(proc.stderr[-1200:] or f"codex exec exited {proc.returncode}")
    answer, usage, model = None, {}, None
    for line in proc.stdout.splitlines():
        try: event = json.loads(line)
        except ValueError: continue
        if event.get("type") == "turn.completed":
            model = event.get("model") or model
            usage = event.get("usage") or usage
        if event.get("type") == "item.completed" and isinstance(event.get("item"), dict) and event["item"].get("type") == "agent_message":
            answer = event["item"].get("text")
    if answer is None:
        raise ValueError("CLI output had no agent_message")
    parsed = json.loads(answer)
    tokens = sum(int(usage.get(k) or 0) for k in ("input_tokens", "output_tokens", "reasoning_output_tokens")) or None
    return parsed, tokens, int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0), int(usage.get("reasoning_output_tokens") or 0), int(usage.get("cached_input_tokens") or 0), seconds, model or _configured_model(cli)


def _flag(code, field="", quote="", explanation="", severity="high", evidence=None):
    return {"code": code, "field": field, "quote_from_package": quote, "explanation": explanation, "severity": severity, "evidence": evidence or []}


def _review_one(video, sourceinfo, reply, stats, failed=None):
    candidates = video.get("candidates", []) if isinstance(video, dict) and isinstance(video.get("candidates"), list) else []
    out = {"video_id": video.get("video_id") if isinstance(video, dict) else None, "review_status": "review_failed" if failed else "ok", "sources_sent": [x["fact_id"] for x in sourceinfo["sources"]], "sources_truncated": sourceinfo["sources_truncated"], "sources_missing": sourceinfo["sources_missing"], "candidates": [], "tokens": stats[0], "input_tokens": stats[1], "output_tokens": stats[2], "reasoning_tokens": stats[3], "cached_input_tokens": stats[4], "seconds": stats[5], "model": stats[6]}
    if failed: out["failure_reason"] = str(failed)
    reply_candidates = reply.get("candidates", []) if isinstance(reply, dict) and isinstance(reply.get("candidates"), list) else []
    index = {}
    for item in reply_candidates:
        if isinstance(item, dict) and isinstance(item.get("candidate_id"), str): index.setdefault(item["candidate_id"], []).append(item)
    for candidate in candidates:
        cid = candidate.get("candidate_id") if isinstance(candidate, dict) else None
        rec = index.get(cid, [])
        flags = list(rec[0].get("flags", [])) if len(rec) == 1 and isinstance(rec[0].get("flags", []), list) else []
        note = rec[0].get("note", "") if len(rec) == 1 else ""
        if failed or len(rec) != 1:
            flags.append(_flag("review_failed", explanation=str(failed or "candidate missing or duplicated in reviewer response")))
            # Thiếu/trùng một phương án nghĩa là review của video không trọn vẹn: cả video phải báo review_failed.
            if out["review_status"] != "review_failed":
                out["review_status"] = "review_failed"
                out["failure_reason"] = f"candidate {cid!r} missing or duplicated in reviewer response"
        if sourceinfo["sources_missing"]:
            flags.append(_flag("missing_source", explanation="Không tìm thấy nguồn liên quan trong store."))
        valid_sources = {e.get("source_id") for s in sourceinfo["sources"] for e in s.get("evidence", []) if e.get("source_id")}
        for flag in flags:
            if not isinstance(flag, dict): continue
            if flag.get("code") not in CODES | {"review_failed"}: flag["unknown_code"] = True
            for ev in flag.get("evidence", []) if isinstance(flag.get("evidence"), list) else []:
                if not isinstance(ev, dict) or ev.get("source_id") not in valid_sources: ev["evidence_invalid"] = True
        out["candidates"].append({"candidate_id": cid, "flags": flags, "note": note})
    return out


def run(candidates_path, stores, out, batch=3, timeout=600, replay=None, cli="codex"):
    p = Path(candidates_path)
    paths = sorted(p.glob("*.json")) if p.is_dir() else [p]
    videos, outputs = [], []
    for path in paths:
        try: loaded = _read(path)
        except Exception as exc:
            outputs.append({"video_id": path.stem, "review_status": "review_failed", "failure_reason": f"input JSON error: {exc}", "sources_sent": [], "sources_truncated": [], "sources_missing": True, "candidates": [], "tokens": None, "cached_input_tokens": None, "seconds": 0, "model": _configured_model(cli)})
            continue
        rows = loaded if isinstance(loaded, list) else [loaded]
        for video in rows:
            if not isinstance(video, dict):
                outputs.append({"video_id": None, "review_status": "review_failed", "failure_reason": "record is not an object", "sources_sent": [], "sources_truncated": [], "sources_missing": True, "candidates": [], "tokens": None, "cached_input_tokens": None, "seconds": 0, "model": _configured_model(cli)}); continue
            vid = video.get("video_id")
            fail = None
            cands = video.get("candidates")
            if not isinstance(vid, str) or not vid: fail = "missing video_id"
            elif not isinstance(cands, list): fail = "candidates must be an array"
            else:
                ids = [c.get("candidate_id") for c in cands if isinstance(c, dict)]
                if len(ids) != len(cands): fail = "candidate record is not an object"
                elif any(not isinstance(x, str) or not x for x in ids): fail = "missing candidate_id"
                elif len(ids) != len(set(ids)): fail = "duplicate candidate_id"
            topic = video.get("topic_id", "")
            try:
                store = _read(Path(stores) / f"{topic}.json")
                ver = _read(Path(stores) / f"{topic}.verification.json")
                src = select_reviewer_sources(video, store, ver)
            except Exception as exc:
                src = {"sources": [], "sources_truncated": [], "sources_missing": True}
                fail = fail or f"store/verification error: {exc}"
            videos.append((video, src, fail))
    input_counts = {}
    for video, _, _ in videos:
        if isinstance(video.get("video_id"), str): input_counts[video["video_id"]] = input_counts.get(video["video_id"], 0) + 1
    videos = [(v, s, (f"duplicate input video_id: {v.get('video_id')}" if input_counts.get(v.get("video_id"), 0) > 1 else fail)) for v, s, fail in videos]
    replay_data = None
    if replay:
        try: replay_data = _read(replay)
        except Exception as exc:
            outputs.extend(_review_one(v, s, None, (None, None, None, None, None, 0, "replay"), f"replay JSON error: {exc}") for v, s, _ in videos)
    if not outputs:
        for offset in range(0, len(videos), max(1, batch)):
            chunk = videos[offset:offset + max(1, batch)]
            request = [{"video_id": v.get("video_id"), "candidates": v.get("candidates", []), "sources": s["sources"]} for v, s, _ in chunk]
            try:
                if replay_data is not None:
                    block = replay_data[offset // max(1, batch)] if isinstance(replay_data, list) and replay_data and isinstance(replay_data[0], (list, dict)) else replay_data
                    parsed = block if isinstance(block, dict) else {"videos": block}
                    stats = (None, None, None, None, None, 0, "replay")
                    stats_by_video = [stats] * len(chunk)
                    batch_totals = {}
                else:
                    parsed, tokens, inp, outtok, reason, cached, secs, model = _run_batch(request, cli, timeout)
                    # Allocate integer token counts without losing remainders. The batch
                    # totals are emitted once (on the first video's record) below.
                    n = max(1, len(chunk))
                    def shares(value):
                        if value is None: return [None] * n
                        q, r = divmod(value, n)
                        return [q + (i < r) for i in range(n)]
                    input_shares, output_shares, reasoning_shares, cached_shares = (
                        shares(inp), shares(outtok), shares(reason), shares(cached))
                    per_video = [
                        (None if input_shares[i] is None else input_shares[i] + output_shares[i] + reasoning_shares[i],
                         input_shares[i], output_shares[i], reasoning_shares[i], cached_shares[i])
                        for i in range(n)
                    ]
                    batch_totals = {"batch_tokens_total": tokens, "batch_input_tokens_total": inp,
                                    "batch_output_tokens_total": outtok, "batch_reasoning_tokens_total": reason,
                                    "batch_cached_input_tokens_total": cached}
                    stats_by_video = [( *per_video[i], secs / n, model) for i in range(n)]
                returned = parsed.get("videos") if isinstance(parsed, dict) else parsed
                if not isinstance(returned, list): raise ValueError("response missing videos array")
                seen = {}
                for r in returned:
                    if isinstance(r, dict) and isinstance(r.get("video_id"), str): seen.setdefault(r["video_id"], []).append(r)
                expected_videos = {v.get("video_id") for v, _, _ in chunk}
                unknown_videos = set(seen) - expected_videos
                for video_index, (video, src, initial_fail) in enumerate(chunk):
                    matches = seen.get(video.get("video_id"), [])
                    reason = initial_fail
                    if unknown_videos: reason = reason or f"unknown video_id in reviewer response: {', '.join(sorted(unknown_videos))}"
                    reply = matches[0] if len(matches) == 1 else None
                    if len(matches) > 1: reason = reason or "duplicate video_id in reviewer response"
                    elif not matches: reason = reason or "video_id missing from reviewer response"
                    if reply is not None:
                        response_candidates = reply.get("candidates")
                        if not isinstance(response_candidates, list):
                            reason = reason or "reviewer response candidates must be an array"
                        else:
                            got = []
                            malformed = False
                            for c in response_candidates:
                                if not isinstance(c, dict):
                                    malformed = True
                                elif not isinstance(c.get("candidate_id"), str) or not c["candidate_id"]:
                                    malformed = True
                                else:
                                    got.append(c["candidate_id"])
                            expected = {c.get("candidate_id") for c in video.get("candidates", []) if isinstance(c, dict)}
                            problems = []
                            if malformed: problems.append("malformed candidate record in reviewer response")
                            if len(got) != len(set(got)): problems.append("duplicate candidate_id in reviewer response")
                            if set(got) - expected: problems.append("unknown candidate_id in reviewer response")
                            if problems: reason = "; ".join(([reason] if reason else []) + problems)
                    stats = stats_by_video[video_index]
                    record = _review_one(video, src, reply, stats, reason)
                    if video_index == 0 and not replay_data:
                        record.update(batch_totals)
                    outputs.append(record)
            except subprocess.TimeoutExpired:
                outputs.extend(_review_one(v, s, None, (None, None, None, None, None, timeout, _configured_model(cli)), f"CLI timeout after {timeout}s") for v, s, _ in chunk)
            except Exception as exc:
                outputs.extend(_review_one(v, s, None, (None, None, None, None, None, 0, _configured_model(cli)), f"review CLI/JSON error: {exc}") for v, s, _ in chunk)
    Path(out).write_text(json.dumps(outputs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return outputs


def main(argv=None):
    ap = argparse.ArgumentParser(description="Flag-only packaging reviewer")
    ap.add_argument("candidates")
    ap.add_argument("--stores", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--replay")
    args = ap.parse_args(argv)
    try: run(args.candidates, args.stores, args.out, args.batch, args.timeout, args.replay)
    except Exception as exc:
        print(f"reviewer: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
