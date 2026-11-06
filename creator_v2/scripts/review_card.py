"""Minimal review cards and append-only human decisions (research only)."""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _md(value: Any) -> str:
    """Escape untrusted values so they cannot create Markdown structure."""
    text = str(value if value is not None else "")
    return (text.replace("\\", "\\\\").replace("`", "\\`").replace("#", "\\#")
            .replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
            .replace("<", "&lt;").replace(">", "&gt;")
            .replace("\n", "<br>").replace("\r", ""))


def _candidate_list(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        candidates = data
    elif isinstance(data, dict):
        candidates = data.get("candidates", [])
    else:
        candidates = []
    if not isinstance(candidates, list) or any(not isinstance(x, dict) for x in candidates):
        raise ValueError("candidates phải là một danh sách object")
    return candidates


REVIEW_FORMAT_ERROR = "review_format_unrecognized"


def _review_state(review: Any) -> tuple[str, str, Any]:
    """Đọc đúng định dạng reviewer v2 (#127): review_status / failure_reason / sources_missing / candidates[]."""
    if review is None:
        return "review_missing", "Không có review.json", False
    if not isinstance(review, dict) or "review_status" not in review or not isinstance(review.get("candidates"), list):
        return REVIEW_FORMAT_ERROR, "review.json không đúng định dạng reviewer v2 (thiếu review_status hoặc candidates)", True
    status = str(review.get("review_status"))
    reason = str(review.get("failure_reason", ""))
    missing = bool(review.get("sources_missing"))
    if status != "ok":
        return "review_failed", reason or status, missing
    return "ok", reason, missing


def _review_flags(review: Any, cid: Any) -> list[Any] | None:
    """Trả None khi KHÔNG tìm được kết quả review cho phương án này (khác với 'có kết quả, không có cờ')."""
    if not isinstance(review, dict) or not isinstance(review.get("candidates"), list):
        return None
    rows = [r for r in review["candidates"] if isinstance(r, dict) and r.get("candidate_id") == cid]
    if len(rows) != 1 or not isinstance(rows[0].get("flags", []), list):
        return None
    return rows[0].get("flags", [])


def _flags_for_card(review: Any, cid: Any) -> list[Any]:
    flags = _review_flags(review, cid)
    if flags is None:
        return [{"code": "review_result_missing", "severity": "high", "explanation": "Không có kết quả review cho phương án này — phải xem kỹ thủ công."}]
    return flags


def _md_flags(flags: list[Any]) -> str:
    if not flags:
        return "- (reviewer không gắn cờ — KHÔNG có nghĩa là đã duyệt)"
    out = []
    for f in flags:
        if not isinstance(f, dict):
            out.append(f"- {_md(f)}"); continue
        line = f"- **{_md(f.get('code', ''))}** · {_md(f.get('severity', ''))} — {_md(f.get('explanation', ''))}"
        if f.get("quote_from_package"): line += f" «{_md(f.get('quote_from_package'))}»"
        for e in (f.get("evidence") or []):
            if isinstance(e, dict): line += f"\n  - ↳ {_md(e.get('source_id', ''))}: {_md(e.get('quote', ''))}"
        out.append(line)
    return "\n".join(out)


def render_card(candidates_json: str | Path, review_json: str | Path | None, out: str | Path, title_max: int | None = None) -> Path:
    """Write a compact HTML/Markdown review card; malformed input becomes an error card."""
    out = Path(out)
    errors: list[str] = []
    try:
        data = _load(candidates_json)
        candidates = _candidate_list(data)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        data, candidates = {}, []
        errors.append(f"Không đọc được candidates.json: {exc}")
    review = None
    if review_json is not None:
        try:
            review = _load(review_json)
            if not isinstance(review, dict):
                raise ValueError("review.json phải là object")
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            errors.append(f"Không đọc được review.json: {exc}")
            review = {"status": "review_failed", "reason": str(exc)}
    status, reason, missing = _review_state(review)
    meta = dict(data) if isinstance(data, dict) else {}
    if title_max is not None:
        meta["title_max"] = title_max
    esc = lambda x: html.escape(str(x if x is not None else ""))
    blocks = []
    for c in candidates:
        cid = c.get("candidate_id", "(thiếu mã)")
        flags = _flags_for_card(review, cid)
        flag_html = "".join(f'<li>{esc(f.get("code", f.get("flag", "")))} · {esc(f.get("level", f.get("severity", "")))} — {esc(f.get("explanation", f.get("reason", "")))}<br><q>{esc(f.get("quote_from_package", f.get("quote", "")))}</q>{"".join("<br>↳ " + esc(e.get("source_id", "")) + ": " + esc(e.get("quote", "")) for e in (f.get("evidence") or []) if isinstance(e, dict))}</li>' if isinstance(f, dict) else f'<li>{esc(f)}</li>' for f in flags) or "<li>Không có cờ reviewer</li>"
        title = str(c.get("title", ""))
        limit = meta.get("title_max", 60)
        count = f"{len(title)}/{limit} ký tự" + (" — CẢNH BÁO: vượt title_max" if len(title) > limit else "")
        thumb = c.get("thumbnail")
        media = ""
        if thumb:
            src = esc(os.path.relpath(ROOT / thumb, out.parent))
            media = (f'<iframe title="Thumbnail" src="{src}"></iframe><iframe title="Thumbnail 168 px" class="small" src="{src}"></iframe>' if str(thumb).lower().endswith('.html') else f'<img alt="Thumbnail" src="{src}"><img alt="Thumbnail 168 px" class="small" src="{src}">')
        claims = esc(json.dumps(c.get("claims", []), ensure_ascii=False))
        local_flags = esc(json.dumps(c.get("flags", []), ensure_ascii=False))
        blocks.append(f'''<article><h2>{esc(cid)} — {esc(c.get("title", ""))}</h2>
<p>{esc(count)}</p>{media}<div class="thumb"><span>{esc(c.get("thumbnail_text", ""))}</span></div><p>Claims: {claims}</p><p>Flags: {local_flags}</p>
<dl><dt>Khung 0–1 s</dt><dd>{esc(c.get("first_frame_0_1s", ""))}</dd>
<dt>Câu 0–3 s</dt><dd>{esc(c.get("voice_0_3s", ""))}</dd>
<dt>3–10 s</dt><dd>{esc(c.get("escalation_3_10s", ""))}</dd>
<dt>Payoff</dt><dd>{esc(c.get("payoff", ""))}</dd>
<dt>Why this angle</dt><dd>{esc(c.get("why_this_angle", ""))}</dd></dl>
<h3>Cờ reviewer</h3><ul>{flag_html}</ul></article>''')
    error_html = "".join(f"<p class='error'>{esc(e)}</p>" for e in errors)
    if out.suffix.lower() in {".html", ".htm"}:
        content = f'''<!doctype html><meta charset="utf-8"><title>Review {esc(meta.get("video_id", ""))}</title>
<style>body{{font:16px system-ui;background:#f3f4f6;color:#171717;margin:24px}}header{{background:#7f1d1d;color:white;padding:18px;border-radius:8px}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin-top:18px}}article{{background:white;border:1px solid #ddd;border-radius:8px;padding:16px}}.thumb{{height:168px;background:#171717;color:white;display:grid;place-items:center;font-size:24px;font-weight:bold;text-align:center}}img,iframe{{display:block;width:100%;height:auto;border:0}}iframe{{height:220px}}.small{{width:168px;height:auto}}iframe.small{{height:95px}}dt{{font-weight:bold;margin-top:12px}}dd{{margin:3px 0}}.error{{color:#b91c1c}}</style>
<header><h1>{esc(meta.get("video_id", "(thiếu video_id)"))}</h1><b>{esc(meta.get("channel", meta.get("channel_id", "(thiếu kênh)")))}</b> · Ngày đăng dự kiến: {esc(meta.get("planned_publish_date", meta.get("publish_date", "(chưa có)")))}<p>Trạng thái review: {esc(status)} — {esc(reason)}<br>sources_missing: {esc(json.dumps(missing, ensure_ascii=False))}</p>{error_html}</header><main>{''.join(blocks) or '<p>Không có phương án.</p>'}</main>'''
    else:
        content = f"# {_md(meta.get('video_id', '(thiếu video_id)'))}\n\nKênh: {_md(meta.get('channel', meta.get('channel_id', '(thiếu kênh)')))}  \nNgày đăng dự kiến: {_md(meta.get('planned_publish_date', meta.get('publish_date', '(chưa có)')))}  \n**Trạng thái review: {_md(status)} — {_md(reason)}**  \nsources_missing: `{_md(json.dumps(missing, ensure_ascii=False))}`\n\n" + "\n\n---\n\n".join(f"## {_md(c.get('candidate_id', '(thiếu mã)'))} — {_md(c.get('title', ''))}\n\nThumbnail: **{_md(c.get('thumbnail_text', ''))}** *(168 px, nền tối)*\n\n" + "\n".join(f"- **{_md(label)}:** {_md(c.get(key, ''))}" for label,key in [("Khung 0–1 s","first_frame_0_1s"),("Câu 0–3 s","voice_0_3s"),("3–10 s","escalation_3_10s"),("Payoff","payoff"),("Why this angle","why_this_angle")]) + "\n\nCờ reviewer:\n" + _md_flags(_flags_for_card(review, c.get('candidate_id'))) for c in candidates) + ("\n\n" + "\n".join(_md(e) for e in errors) if errors else "")
    if out.suffix.lower() not in {".html", ".htm"}:
        for c in candidates:
            title = str(c.get("title", ""))
            limit = meta.get("title_max", 60)
            warning = " — CẢNH BÁO: vượt title_max" if len(title) > limit else ""
            content += f"\n\n### {_md(c.get('candidate_id', ''))}: {len(title)}/{limit} ký tự{warning}\n"
            if c.get("thumbnail"):
                src = os.path.relpath(ROOT / c["thumbnail"], out.parent).replace("\\", "/")
                safe_src = html.escape(src, quote=True)
                preview = (f'<iframe src="{safe_src}" width="168" height="95" title="Thumbnail 168 px"></iframe>'
                           if str(c["thumbnail"]).lower().endswith(".html") else
                           f'<img src="{safe_src}" width="168" alt="Thumbnail 168 px">')
                content += f"\n[Thumbnail]({_md(src)})  \n{preview}\n"
            content += f"\nClaims: {_md(json.dumps(c.get('claims', []), ensure_ascii=False))}\nFlags: {_md(json.dumps(c.get('flags', []), ensure_ascii=False))}\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out


def record_decision(candidates_json: str | Path, action: str, candidate_id: str | None = None,
                    edits: dict[str, Any] | None = None, note: str = "", reviewer: str = "",
                    review_seconds: float | None = None, history_dir: str | Path | None = None,
                    out: str | Path | None = None) -> dict[str, Any]:
    data = _load(candidates_json)
    candidates = _candidate_list(data)
    action = action.upper()
    if action not in {"APPROVE", "REQUEST_CHANGES", "REJECT"}:
        raise ValueError("action phải là APPROVE, REQUEST_CHANGES hoặc REJECT")
    if action == "APPROVE" and not candidate_id:
        raise ValueError("APPROVE yêu cầu candidate_id")
    if action in {"REQUEST_CHANGES", "REJECT"} and not note.strip():
        raise ValueError(f"{action} yêu cầu note bắt buộc")
    if action != "APPROVE" and candidate_id is not None:
        raise ValueError("candidate_id chỉ dùng với APPROVE")
    chosen = None
    if action == "APPROVE":
        matches = [c for c in candidates if c.get("candidate_id") == candidate_id]
        if len(matches) != 1:
            raise ValueError("candidate_id phải khớp đúng một phương án")
        chosen = copy.deepcopy(matches[0])
        if edits:
            chosen.update(edits)
    raw_hash = _sha(Path(candidates_json).read_bytes())
    video_id = data.get("video_id") if isinstance(data, dict) else None
    if not video_id:
        raise ValueError("candidates.json thiếu video_id")
    hist = Path(history_dir) if history_dir else Path(candidates_json).parent / "decisions" / str(video_id)
    existing = sorted(hist.glob("v*.json"), key=lambda p: (p.stat().st_mtime_ns, p.name)) if hist.exists() else []
    history: list[tuple[int, str]] = []
    for p in existing:
        try:
            prior = _load(p)
            number_text = p.stem[1:].split("-", 1)[0] if p.stem.startswith("v") else ""
            number = int(number_text) if number_text.isdigit() else 0
            if number and isinstance(prior, dict) and isinstance(prior.get("candidates_file_sha256"), str):
                history.append((number, prior["candidates_file_sha256"]))
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            continue
    if history and history[-1][1] == raw_hash:
        version = history[-1][0]
    else:
        version = max((n for n, _ in history), default=0) + 1
    decision = {"video_id": video_id, "action": action, "candidate_id": candidate_id,
                "content_version": version, "content_sha256": _sha(_canonical(chosen)) if chosen is not None else None,
                "candidates_file_sha256": raw_hash, "reviewer": reviewer,
                "decided_at": datetime.now(timezone.utc).isoformat(), "review_seconds": review_seconds,
                "note": note, "edits": edits or {}}
    history_path = hist / f"v{version}.json"
    if history_path.exists():
        suffix = 2
        while (hist / f"v{version}-d{suffix}.json").exists():
            suffix += 1
        history_path = hist / f"v{version}-d{suffix}.json"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return decision


def verify_decision(candidates_json: str | Path, decision_json: str | Path) -> str:
    try:
        data, decision = _load(candidates_json), _load(decision_json)
        if not isinstance(data, dict) or not isinstance(decision, dict):
            return "invalid"
        candidates = _candidate_list(data)
        if not all(k in decision for k in ("video_id", "action", "content_version", "candidates_file_sha256")):
            return "invalid"
        if decision["action"] != "APPROVE":
            return "not_approved"
        matches = [c for c in candidates if c.get("candidate_id") == decision.get("candidate_id")]
        if len(matches) != 1:
            return "stale"
        chosen = copy.deepcopy(matches[0])
        edits = decision.get("edits", {})
        if not isinstance(edits, dict):
            return "invalid"
        chosen.update(edits)
        if decision.get("video_id") != data.get("video_id"):
            return "stale"
        if decision.get("candidates_file_sha256") != _sha(Path(candidates_json).read_bytes()):
            return "stale"
        if decision.get("content_sha256") != _sha(_canonical(chosen)):
            return "stale"
        return "ok"
    except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError):
        return "invalid"


def _paths(topic: str) -> tuple[Path, Path]:
    if not topic or topic in {".", ".."} or any(x in topic for x in ("/", "\\", ":")):
        raise ValueError("topic không hợp lệ")
    return ROOT / "data" / "long" / topic, ROOT / "output" / "long" / topic


def _channel_limit(spec: dict[str, Any], topic: str) -> tuple[str, int]:
    channel = spec.get("channel") or spec.get("kenh") or topic
    try:
        if str(ROOT.parent) not in sys.path:   # library/ nằm ở gốc repo, cạnh creator_v2/
            sys.path.insert(0, str(ROOT.parent))
        from library.tools import channel_profile
        channel = channel_profile.resolve(spec, slug=topic)
        limit = channel_profile.load(channel)["luat_noi_dung"]["title_max"]
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("title_max phải là số nguyên dương")
    except (ImportError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"cảnh báo: không đọc được title_max của kênh {channel}: {exc}; dùng mặc định 60", file=sys.stderr)
        limit = 60
    return channel, limit


def init_topic(topic: str) -> Path:
    data_dir, output_dir = _paths(topic)
    spec = _load(data_dir / "spec.json")
    titles = spec.get("youtube", {}).get("titles")
    if not isinstance(titles, list) or not titles or any(not isinstance(t, str) or not t for t in titles):
        raise ValueError("spec.youtube.titles phải là danh sách tiêu đề không rỗng")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    channel, limit = _channel_limit(spec, topic)
    thumbs = sorted(p for p in output_dir.glob("t*.jpg") if not p.stem.endswith("_small"))
    if not thumbs:
        thumbs = sorted((ROOT / "motion" / "long" / "thumbs").glob(f"{topic}_t*.html"))
    candidates = [{"candidate_id": f"c{i + 1}", "title": title,
                   "thumbnail": str(thumbs[i % len(thumbs)].relative_to(ROOT)).replace("\\", "/") if thumbs else None,
                   "claims": [], "flags": []} for i, title in enumerate(titles)]
    path = data_dir / "candidates.json"
    if path.exists():
        raise ValueError("candidates.json đã tồn tại; không ghi đè dữ liệu reviewer")
    path.write_text(json.dumps({"video_id": topic, "channel": channel, "title_max": limit,
                                "candidates": candidates}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from factory.console import utf8_console
    utf8_console()
    parser = argparse.ArgumentParser(description="Thẻ duyệt Long")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.add_argument("topic")
    p = sub.add_parser("render"); p.add_argument("topic")
    p = sub.add_parser("decide"); p.add_argument("topic")
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--approve"); action.add_argument("--request-changes", action="store_true"); action.add_argument("--reject", action="store_true")
    p.add_argument("--edits"); p.add_argument("--note", default=""); p.add_argument("--by", required=True); p.add_argument("--review-seconds", type=float)
    p = sub.add_parser("verify"); p.add_argument("topic")
    args = parser.parse_args(argv)
    try:
        data_dir, output_dir = _paths(args.topic)
        candidates = data_dir / "candidates.json"
        decision = data_dir / "decision.json"
        if args.command == "init":
            print(init_topic(args.topic))
        elif args.command == "render":
            review = data_dir / "review.json"
            _, limit = _channel_limit(_load(data_dir / "spec.json"), args.topic)
            for suffix in ("html", "md"):
                print(render_card(candidates, review if review.exists() else None, output_dir / f"review_card.{suffix}", title_max=limit))
        elif args.command == "decide":
            edits = _load(args.edits) if args.edits else None
            if edits is not None and not isinstance(edits, dict):
                raise ValueError("edits phải là object JSON")
            action = "APPROVE" if args.approve else "REQUEST_CHANGES" if args.request_changes else "REJECT"
            result = record_decision(candidates, action, args.approve, edits, args.note, args.by, args.review_seconds, out=decision)
            if action == "APPROVE":
                chosen = next(c for c in _candidate_list(_load(candidates)) if c.get("candidate_id") == args.approve).copy()
                chosen.update(result["edits"])
                print("Lead đặt youtube.titles[0] thành: " + json.dumps(chosen.get("title"), ensure_ascii=False))
        else:
            result = verify_decision(candidates, decision)
            print(result)
            return 0 if result == "ok" else 1
    except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError, ImportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
