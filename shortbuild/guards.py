"""Hard checks for short plans and generated HTML."""

import re
from collections.abc import Iterable, Mapping


class GuardError(ValueError):
    """Raised when a short violates a production invariant."""


_CREDIT = re.compile(r"\b(?:credit|credits|generated\s+by|made\s+with|chatgpt|grokbot|midjourney|stable\s+diffusion|openai|google\s+flow|ảnh\s+minh\s+hoạ\s+ai)\b", re.I)


def validate(rows: Iterable[Mapping], html: str | Iterable[str] = ()) -> None:
    """Validate BUD source provenance, experiment pairs, and declared durations."""
    rows = list(rows)
    docs = [html] if isinstance(html, str) else list(html)
    for doc in docs:
        if re.search(r'<[^>]+\bid\s*=\s*["\']cr["\']', doc, re.I):
            raise GuardError("on-screen credit element #cr is forbidden")
        styles = re.findall(r'<style\b[^>]*>(.*?)</style\s*>', doc, re.I | re.S)
        style_text = " ".join(styles)
        style_without_comments = re.sub(r"/\*.*?\*/", " ", style_text, flags=re.S)
        if re.search(r"#cr\b", style_without_comments, re.I):
            raise GuardError("CSS rule #cr is forbidden")
        if _CREDIT.search(re.sub(r"<[^>]*>", " ", doc)) or _CREDIT.search(style_text):
            raise GuardError("credit/AI/tool attribution text is forbidden in HTML")
    for row in rows:
        channel = str(row.get("channel", row.get("series", row.get("lane", "")))).lower()
        if channel in {"bud", "phật pháp", "phat_phap", "tuong", "phap_cu"} and not str(row.get("source", "")).strip():
            raise GuardError(f"{row.get('id', '<row>')}: BUD row requires source")
        declared = row.get("duration_band") or row.get("seconds_band")
        if declared:
            low, high = declared if not isinstance(declared, Mapping) else (declared["min"], declared["max"])
            duration = row.get("dur", row.get("duration_s"))
            if duration is not None and not float(low) <= float(duration) <= float(high):
                raise GuardError(f"{row.get('id', '<row>')}: duration outside declared band")
    by_cell = {}
    for row in rows:
        cell = row.get("test_cell")
        if cell:
            by_cell.setdefault(cell, []).append(row)
    for cell, pair in by_cell.items():
        if len(pair) > 1:
            kinds = {row.get("img_kind") for row in pair}
            if None in kinds or len(kinds) > 1:
                raise GuardError(f"experiment cell {cell}: paired rows must share img_kind")
