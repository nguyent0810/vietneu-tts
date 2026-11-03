"""History features for the Creative LLM: the last N videos, described neutrally.

The goal is to let the model NOTICE repetition, not to forbid it. The summary
only counts what recent videos did and states it in plain Vietnamese
("7/10 mở bằng thẻ chữ"). It never emits rules or bans.

Input shapes accepted by ``load_packages``:
  * a single package dict (has "title"),
  * a list of package dicts,
  * a package dict with an "alternates" list.
``alternates`` are unpublished candidate angles, so they are ignored: only the
primary package of each input counts as a video.

Order: the list order is treated as chronological (oldest first); for a
directory, files are read in sorted file-name order. The last ``n`` packages
are kept. Packages carry no publish date, so pass them in publish order.

CLI:
    python -m research.hitl.history.history <packages.json|dir> [more ...] \
        --channel bud --out history.json [--n 10]
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys
import unicodedata
from typing import Any, Iterable

FEATURE_ORDER = ("mechanism", "opener_shape", "first_frame_type", "title_shape", "has_number")

# --- opener (voice_0_3s) -----------------------------------------------------

_QUOTE_CHARS = "\"'“‘«"
_DATE_LEAD = re.compile(r"^(năm|ngày|trưa|tháng|hồi|từ|vào|đêm|sáng|chiều|tối|in|on)\b", re.I)
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_DAY_MONTH = re.compile(r"\d{1,2}\s*/\s*\d{1,2}|\d{1,2}\s+tháng\s+\d|tháng\s+\d{1,2}\b", re.I)
_YEAR_LEAD = re.compile(r"^\d{3,4}\b")
_SCENE_LEAD = re.compile(
    r"^(ở|trong|tại|hình dung|bên trong|imagine|picture|inside|at|in|on|when|it'?s)\b", re.I
)

# --- first frame (first_frame_0_1s) -------------------------------------------

_MAP = re.compile(r"bản đồ|\bmap\b", re.I)
_TEXT_LEAD = re.compile(r"^(chữ|sơ đồ chữ|thẻ|dòng chữ|text|tiêu đề|số|con số|sơ đồ)\b", re.I)
_FRAME_SCENE_LEAD = re.compile(r"^(ảnh|cảnh|video|quay|khung cảnh|phân cảnh|scene|shot|footage)\b", re.I)
_TEXT_WORD = re.compile(r"chữ|thẻ|\btext\b|dòng chữ|tiêu đề|số liệu", re.I)
_PORTRAIT = re.compile(r"chân dung|khuôn mặt|gương mặt|mặt người|portrait|close-?up|nhà sư|\bthầy\b", re.I)
_SCENE = re.compile(
    r"cảnh|núi|sông|biển|rừng|phố|trời|sương|mây|cung|đền|chùa|phòng|thung lũng|đường|"
    r"bầu trời|đêm|sân|thành|landscape|sky|night|street|scene|room|sea",
    re.I,
)
_OBJECT = re.compile(
    r"chiếc|cái|vật|đồng xu|la bàn|hộp|tượng|lư hương|nén hương|\bbát\b|đồng hồ|"
    r"biểu tượng|\bcoin\b|\bobject\b|đồ vật|\bsách\b|bình|lọng",
    re.I,
)

# --- title ------------------------------------------------------------------

_TITLE_SPLIT = re.compile(r"\s*(?:,|:|\||—|–|\s-\s)\s*")


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return unicodedata.normalize("NFC", value).strip()


def _words(s: str) -> list[str]:
    return re.findall(r"\w+", s)


def _first_sentence(s: str) -> str:
    return re.split(r"(?<=[.?!])\s+", s, maxsplit=1)[0]


def _norm_mechanism(raw: Any) -> str:
    s = _text(raw).lower()
    s = re.sub(r"[\s\-]+", "_", s)
    if not s:
        return "unknown"
    if s.startswith("broken_expectations"):
        return "broken_expectations"
    return s


def _mechanism(pkg: dict) -> str:
    """Mechanism from ``tags_for_history`` when present, else ``angle.mechanism``.

    ``tags_for_history`` may be a dict with a "mechanism" key, or a list holding
    an entry such as "mechanism:moral_dilemma" (also "mech:" / "cơ chế:").
    """
    tags = pkg.get("tags_for_history")
    if isinstance(tags, dict) and tags.get("mechanism"):
        return _norm_mechanism(tags["mechanism"])
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and re.match(r"^\s*(mechanism|mech|cơ chế)\s*[:=]", tag, re.I):
                return _norm_mechanism(re.split(r"[:=]", tag, maxsplit=1)[1])
    angle = pkg.get("angle")
    if isinstance(angle, dict) and angle.get("mechanism"):
        return _norm_mechanism(angle["mechanism"])
    return "unknown"


def _is_date(first: str) -> bool:
    f = first.strip()
    if _YEAR_LEAD.match(f):
        return True
    return bool(_DATE_LEAD.match(f) and (_YEAR.search(f) or _DAY_MONTH.search(f)))


def opener_shape(voice: Any) -> str:
    """question / date / quote / scene / statement, from the 0-3 s voice line."""
    s = _text(voice)
    if not s:
        return "statement"
    if s[0] in _QUOTE_CHARS:
        return "quote"
    first = _first_sentence(s)
    if "?" in first:
        return "question"
    if _is_date(first):
        return "date"
    if _SCENE_LEAD.match(s):
        return "scene"
    return "statement"


def first_frame_type(frame: Any) -> str:
    """text_card / map / scene / object / portrait / unknown, keyword-based (vi + en).

    A frame led by a scene word ("Ảnh AI: ... chữ động ...") stays a scene even
    when it carries overlaid text; only text-led frames count as text cards.
    Diagrams ("sơ đồ chữ") fold into text_card.
    """
    f = _text(frame)
    if not f:
        return "unknown"
    if _MAP.search(f):
        return "map"
    scene_led = bool(_FRAME_SCENE_LEAD.match(f))
    if _TEXT_LEAD.match(f) or (not scene_led and _TEXT_WORD.search(f)):
        return "text_card"
    if _PORTRAIT.search(f):
        return "portrait"
    if _SCENE.search(f):
        return "scene"
    if _OBJECT.search(f):
        return "object"
    return "unknown"


def _is_two_clause(title: str) -> bool:
    parts = [p for p in _TITLE_SPLIT.split(title) if p and p.strip()]
    if len(parts) < 2:
        return False
    return len(_words(parts[0])) >= 2 and len(_words(parts[1])) >= 2


def title_shape(title: Any) -> str:
    """two_clause / question / number_led / plain (checked in that order)."""
    t = _text(title)
    if _is_two_clause(t):
        return "two_clause"
    if "?" in t:
        return "question"
    if re.match(r"^\s*\d", t):
        return "number_led"
    return "plain"


def has_number(title: Any) -> bool:
    return bool(re.search(r"\d", _text(title)))


def extract_features(pkg: dict) -> dict:
    """Features of one package. Missing fields degrade to "unknown"/empty values."""
    title = _text(pkg.get("title"))
    return {
        "package_id": pkg.get("package_id"),
        "topic_id": pkg.get("topic_id"),
        "title": title,
        "mechanism": _mechanism(pkg),
        "opener_shape": opener_shape(pkg.get("voice_0_3s")),
        "first_frame_type": first_frame_type(pkg.get("first_frame_0_1s")),
        "title_shape": title_shape(title),
        "has_number": has_number(title),
    }


# --- summary ---------------------------------------------------------------

_OBS_TEXT: dict[str, dict[str, str]] = {
    "mechanism": {"*": "{c}/{n} video dùng cùng cơ chế '{v}'"},
    "opener_shape": {
        "question": "{c}/{n} câu mở là câu hỏi",
        "date": "{c}/{n} câu mở bắt đầu bằng mốc thời gian",
        "quote": "{c}/{n} câu mở là lời trích",
        "scene": "{c}/{n} câu mở là một cảnh",
        "statement": "{c}/{n} câu mở là câu khẳng định",
    },
    "first_frame_type": {
        "text_card": "{c}/{n} mở bằng thẻ chữ",
        "map": "{c}/{n} mở bằng bản đồ",
        "scene": "{c}/{n} mở bằng cảnh",
        "object": "{c}/{n} mở bằng vật thể",
        "portrait": "{c}/{n} mở bằng chân dung",
    },
    "title_shape": {
        "two_clause": "{c}/{n} title hai vế",
        "question": "{c}/{n} title dạng câu hỏi",
        "number_led": "{c}/{n} title mở bằng số",
        "plain": "{c}/{n} title một vế",
    },
    "has_number": {"yes": "{c}/{n} title có chữ số"},
}


def _observations(items: list[dict], counts: dict[str, dict[str, int]]) -> list[str]:
    n = len(items)
    found: list[tuple[int, int, str]] = []
    for idx, feature in enumerate(FEATURE_ORDER):
        templates = _OBS_TEXT[feature]
        for value, c in counts[feature].items():
            # Only repetition worth noticing: at least 2 videos and at least half the window.
            if c < 2 or c * 2 < n or value == "unknown":
                continue
            template = templates.get(value, templates.get("*"))
            if template is None:
                continue
            found.append((-c, idx, template.format(c=c, n=n, v=value)))
    found.sort()
    return [text for _, _, text in found]


def summarize(items: list[dict]) -> dict:
    counts: dict[str, dict[str, int]] = {}
    for feature in FEATURE_ORDER:
        if feature == "has_number":
            c = collections.Counter("yes" if it["has_number"] else "no" for it in items)
        else:
            c = collections.Counter(it[feature] for it in items)
        counts[feature] = dict(c.most_common())
    return {
        "n_items": len(items),
        "counts": counts,
        "observations": _observations(items, counts),
    }


def build_history(packages: list[dict], channel: str, n: int = 10) -> dict:
    """Features for the last ``n`` packages (list order = oldest first) plus a summary."""
    window = packages[-n:] if n > 0 else list(packages)
    items = [extract_features(p) for p in window]
    return {
        "channel": channel,
        "n": n,
        "items": items,
        "summary": summarize(items),
    }


# --- loading ---------------------------------------------------------------

def _coerce(data: Any, source: str) -> list[dict]:
    """Return the primary package dicts from one parsed JSON document."""
    if isinstance(data, list):
        candidates = data
    elif isinstance(data, dict):
        candidates = [data]
    else:
        raise ValueError(f"{source}: expected a package object or a list of packages")
    packages = []
    for item in candidates:
        if not isinstance(item, dict) or "title" not in item:
            raise ValueError(f"{source}: entry is not a package (no 'title')")
        # "alternates" are unpublished candidates; keep only the primary package.
        packages.append({k: v for k, v in item.items() if k != "alternates"})
    return packages


def load_packages(paths: Iterable[str]) -> list[dict]:
    """Load packages from files or directories (directories: sorted *.json, non-packages skipped)."""
    out: list[dict] = []
    for path in paths:
        if os.path.isdir(path):
            for fname in sorted(glob.glob(os.path.join(path, "*.json"))):
                try:
                    with open(fname, encoding="utf-8") as fh:
                        out.extend(_coerce(json.load(fh), fname))
                except ValueError as exc:
                    print(f"skip: {exc}", file=sys.stderr)
        else:
            with open(path, encoding="utf-8") as fh:
                out.extend(_coerce(json.load(fh), path))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build last-N video history features.")
    ap.add_argument("paths", nargs="+", help="package JSON file(s) or directories")
    ap.add_argument("--channel", required=True, help="channel label written into the output")
    ap.add_argument("--n", type=int, default=10, help="window size (default 10)")
    ap.add_argument("--out", help="output JSON path (default: stdout)")
    args = ap.parse_args(argv)

    history = build_history(load_packages(args.paths), args.channel, n=args.n)
    text = json.dumps(history, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {args.out}: {history['summary']['n_items']} items, "
              f"{len(history['summary']['observations'])} observations")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
