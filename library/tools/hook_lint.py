"""Kiểm hook 1 giây của plan short. Không render, không ghi plan, không gọi mạng.

Đọc tiêu đề, câu đầu `script`, và khung đầu khi plan có `image`, `media` hoặc `visuals`.
Cờ:

  TRUU_TUONG            "có phải là" kèm khái niệm trong hook_terms.json
  KHONG_DANH_TU_CU_THE  tiêu đề không có danh từ cụ thể (vật, hành động, năm, chi, ngày)
  KHUNG_DAU_TRONG       khung đầu chỉ có chữ, không có ảnh hay sơ đồ vật

Danh sách từ: hook_terms.json cạnh file này. Exit 1 khi có cờ.

    .venv/bin/python output/cl_staging/scoreboard/hook_lint.py plan.json
    .venv/bin/python output/cl_staging/scoreboard/hook_lint.py --unpublished
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "output" / "cl_staging"
TERMS_PATH = Path(__file__).with_name("hook_terms.json")
CHANNELS = ("bud", "fs")
FLAGS = ("TRUU_TUONG", "KHONG_DANH_TU_CU_THE", "KHUNG_DAU_TRONG")
# Abstract concepts in a question can be weak hooks even when the wording is
# not the older "có phải là" template.
QUESTION_PATTERN = re.compile(
    r"(?:\?|\b(?:vì\s+sao|tại\s+sao|điều\s+gì|gì|như\s+thế\s+nào|"
    r"ra\s+sao|có\s+thực\s+sự|có\s+thật\s+sự|là\s+để)\b)", re.IGNORECASE
)
MEDIA_KINDS = {"image", "video", "clip", "photo"}
SKIP_MEDIA = {"audio", "sfx", "bgm"}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def norm(text: str) -> str:
    text = nfc(text).replace("**", " ")
    text = text.casefold()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def has_phrase(text: str, phrase: str) -> bool:
    hay = f" {norm(text)} "
    needle = f" {norm(phrase)} "
    return needle.strip() != "" and needle in hay


def load_terms(path: Path | None = None) -> dict:
    path = path or TERMS_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path.name} không phải bảng từ")
    concepts = [nfc(x) for x in data.get("abstract_concepts") or [] if isinstance(x, str) and x.strip()]
    concepts.sort(key=len, reverse=True)
    try:
        year = re.compile(data.get("year_pattern") or r"(?<!\d)(?:19|20)\d{2}(?!\d)")
        day = re.compile(data.get("day_pattern") or r"$^", re.IGNORECASE)
    except re.error as exc:
        raise RuntimeError(f"{path.name}: mẫu regex lỗi ({exc})") from exc
    text_only = {str(x).strip().casefold() for x in (data.get("text_only_visuals") or []) if str(x).strip()}
    return {
        "concepts": concepts,
        "phrases": [nfc(x) for x in data.get("concrete_phrases") or [] if isinstance(x, str) and x.strip()],
        "words": [nfc(x) for x in data.get("concrete_words") or [] if isinstance(x, str) and x.strip()],
        "chi": [nfc(x) for x in data.get("chi") or [] if isinstance(x, str) and x.strip()],
        "text_only": text_only,
        "year": year,
        "day": day,
    }


def has_year(text: str, terms: dict) -> bool:
    return terms["year"].search(nfc(text)) is not None


def has_day(text: str, terms: dict) -> bool:
    return terms["day"].search(nfc(text).casefold()) is not None


def has_chi(text: str, terms: dict) -> bool:
    return any(has_phrase(text, name) for name in terms["chi"])


def has_concrete(text: str, terms: dict) -> bool:
    if has_year(text, terms) or has_day(text, terms) or has_chi(text, terms):
        return True
    if any(has_phrase(text, phrase) for phrase in terms["phrases"]):
        return True
    return any(has_phrase(text, word) for word in terms["words"])


def matched_concepts(text: str, terms: dict) -> list[str]:
    if QUESTION_PATTERN.search(nfc(text)) is None:
        return []
    # “Trung đạo” is often used as a concrete topic label; the observed
    # high-stay question about standing in the middle should not be blocked.
    return [
        concept for concept in terms["concepts"]
        if has_phrase(text, concept)
        and not (concept == "trung đạo" and has_phrase(text, "trung đạo"))
    ]


def blocking_flags(flags: list[str]) -> list[str]:
    """Only abstract question and empty opening frame block; noun specificity is advisory."""
    return [flag for flag in flags if flag in {"TRUU_TUONG", "KHUNG_DAU_TRONG"}]


def first_sentence(row: dict) -> str:
    script = row.get("script")
    if isinstance(script, list):
        for line in script:
            if isinstance(line, str) and line.strip():
                return line
        return ""
    if isinstance(script, str):
        return script
    lines = row.get("lines")
    if isinstance(lines, list):
        for line in lines:
            if isinstance(line, str) and line.strip():
                return line
    return ""


def _at_1(mapping) -> dict | None:
    if not isinstance(mapping, dict):
        return None
    if "1" in mapping and isinstance(mapping["1"], dict):
        return mapping["1"]
    if 1 in mapping and isinstance(mapping[1], dict):
        return mapping[1]
    return None


def _picture(item) -> bool:
    if isinstance(item, str) and item.strip():
        return True
    if not isinstance(item, dict):
        return False
    kind = str(item.get("kind") or "").strip().casefold()
    if kind in SKIP_MEDIA:
        return False
    if kind in MEDIA_KINDS:
        return True
    return any(item.get(key) for key in ("file", "src", "path", "query"))


def _described(row: dict) -> bool:
    """Plan có ảnh hoặc sơ đồ thật. Dict rỗng không tính — style bảng tự vẽ khung."""
    if _picture(row.get("image")):
        return True
    media = row.get("media")
    if isinstance(media, dict) and any(media.values()):
        return True
    visuals = row.get("visuals")
    return isinstance(visuals, dict) and any(isinstance(item, dict) and item for item in visuals.values())


def frame_is_empty(row: dict, terms: dict) -> bool:
    """True khi plan mô tả khung mà khung đầu không có ảnh, sơ đồ vật, năm hay tên chi."""
    if not _described(row):
        return False
    if _picture(row.get("image")) or _picture(_at_1(row.get("media"))):
        return False
    figure = _at_1(row.get("figures"))
    if isinstance(figure, dict) and str(figure.get("type") or "none").strip().casefold() not in {"", "none"}:
        return False
    visual = _at_1(row.get("visuals"))
    if isinstance(visual, dict):
        kind = str(visual.get("type") or "").strip().casefold()
        if kind and kind not in terms["text_only"]:
            return False
        blob = json.dumps(visual, ensure_ascii=False)
        if has_year(blob, terms) or has_chi(blob, terms):
            return False
        return True
    return True


def lint_row(row: dict, terms: dict) -> dict:
    title = str(row.get("title") or "")
    sentence = first_sentence(row)
    flags: list[str] = []
    where: dict[str, list[str]] = {}

    def add(flag: str, place: str) -> None:
        if flag not in flags:
            flags.append(flag)
        where.setdefault(flag, [])
        if place not in where[flag]:
            where[flag].append(place)

    if matched_concepts(title, terms):
        add("TRUU_TUONG", "tiêu đề")
    if sentence and matched_concepts(sentence, terms):
        add("TRUU_TUONG", "câu đầu")
    if not has_concrete(title, terms):
        add("KHONG_DANH_TU_CU_THE", "tiêu đề")
    if frame_is_empty(row, terms):
        add("KHUNG_DAU_TRONG", "khung đầu")
    day = row.get("day") if isinstance(row.get("day"), str) else ""
    return {
        "id": str(row.get("id") or ""),
        "series": str(row.get("series") or ""),
        "day": day,
        "title": title,
        "flags": flags,
        "where": where,
    }


def load_plan(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("id"), str):
        return [data]
    if isinstance(data, dict):
        for key in ("items", "rows", "plans"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise RuntimeError(f"{path.name} không phải danh sách plan")
    return [row for row in data if isinstance(row, dict)]


def publish_at(row: dict) -> datetime | None:
    raw = row.get("publish_at")
    if isinstance(raw, str) and raw.strip():
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    day = row.get("day")
    slot = row.get("slot")
    if not isinstance(day, str) or not isinstance(slot, str) or not day.strip() or not slot.strip():
        return None
    clock = slot.strip()
    if len(clock) == 5:
        clock = clock + ":00"
    parsed = datetime.fromisoformat(f"{day.strip()}T{clock}+00:00")
    return parsed.astimezone(timezone.utc)


def _replaced_ids(rows: list[dict]) -> set[str]:
    found = set()
    for row in rows:
        rep = row.get("replaces")
        if isinstance(rep, str) and rep.strip():
            found.add(rep.strip())
        elif isinstance(rep, list):
            found.update(item.strip() for item in rep if isinstance(item, str) and item.strip())
    return found


def channel_rows(directory: Path) -> list[dict]:
    found: dict[str, dict] = {}
    order: list[str] = []
    for path in sorted(directory.glob("plan_*.json")):
        try:
            rows = load_plan(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            print(f"bỏ qua {path.name}: {exc}", file=sys.stderr)
            continue
        for row in rows:
            rid = row.get("id")
            if not isinstance(rid, str) or not rid:
                continue
            if rid not in found:
                order.append(rid)
            found[rid] = row
    return [found[rid] for rid in order]


def unpublished_rows(root: Path, now: datetime, channels: tuple[str, ...] = CHANNELS) -> list[dict]:
    """Bài plan còn giờ phát phía trước `now`. Bỏ id mà bài khác ghi vào `replaces`."""
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    kept: list[dict] = []
    for channel in channels:
        rows = channel_rows(root / channel)
        replaced = _replaced_ids(rows)
        for row in rows:
            if row.get("id") in replaced:
                continue
            when = publish_at(row)
            if when is None or when <= now:
                continue
            item = dict(row)
            item.setdefault("series", channel)
            kept.append(item)
    kept.sort(key=lambda row: (row.get("day") or "", row.get("slot") or "", row.get("series") or "", row.get("id") or ""))
    return kept


def _flag_text(hit: dict) -> str:
    parts = []
    for flag in hit["flags"]:
        places = ",".join(hit["where"].get(flag) or [])
        parts.append(f"{flag} ({places})" if places else flag)
    return "; ".join(parts)


def render(hits: list[dict]) -> str:
    flagged = [hit for hit in hits if hit["flags"]]
    lines = []
    for channel in CHANNELS:
        block = [hit for hit in hits if hit["series"] == channel]
        if not block and not any(hit["series"] for hit in hits):
            continue
        if block:
            bad = sum(1 for hit in block if blocking_flags(hit["flags"]))
            lines.append(f"KÊNH {channel}: dính {bad}/{len(block)}")
    days = sorted({hit["day"] for hit in hits if hit["day"]})
    for day in days:
        block = [hit for hit in hits if hit["day"] == day]
        bad = sum(1 for hit in block if blocking_flags(hit["flags"]))
        lines.append(f"NGÀY {day}: dính {bad}/{len(block)}")
    lines.append("id\tngày\tcờ chặn\tgợi ý\ttiêu đề")
    if not flagged:
        lines.append("(không có cờ)")
    for hit in flagged:
        title = " ".join(hit["title"].split())
        blockers = blocking_flags(hit["flags"])
        suggestions = [flag for flag in hit["flags"] if flag not in blockers]
        lines.append(f"{hit['id']}\t{hit['day']}\t{', '.join(blockers) or '-'}\t{', '.join(suggestions) or '-'}\t{title}")
    counts = {flag: sum(1 for hit in hits if flag in hit["flags"]) for flag in FLAGS}
    detail = ", ".join(f"{flag} {counts[flag]}" for flag in FLAGS)
    blocked = sum(1 for hit in hits if blocking_flags(hit["flags"]))
    lines.append(f"TỔNG: {len(hits)} bài, dính cờ chặn {blocked}, có gợi ý/cờ {len(flagged)} ({detail})")
    return "\n".join(lines)


def parse_now(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kiểm hook và tiêu đề plan short.")
    parser.add_argument("plans", nargs="*", type=Path)
    parser.add_argument("--unpublished", action="store_true", help="Chỉ bài BUD/FS đã hẹn, giờ phát còn ở phía trước")
    parser.add_argument("--root", type=Path, default=STAGING)
    parser.add_argument("--now", default=None, help="Mốc UTC dạng ISO. Mặc định là hiện tại.")
    parser.add_argument("--terms", type=Path, default=TERMS_PATH)
    args = parser.parse_args(argv)
    terms = load_terms(args.terms)
    if args.unpublished:
        now = parse_now(args.now) if args.now else datetime.now(timezone.utc)
        rows = unpublished_rows(args.root, now)
    else:
        if not args.plans:
            parser.error("cần file plan, hoặc --unpublished")
        rows = []
        for path in args.plans:
            rows.extend(load_plan(path))
    hits = [lint_row(row, terms) for row in rows]
    print(render(hits))
    return 1 if any(blocking_flags(hit["flags"]) for hit in hits) else 0


if __name__ == "__main__":
    sys.exit(main())
