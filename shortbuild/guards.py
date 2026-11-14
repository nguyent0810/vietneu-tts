"""Hard checks for short plans and generated HTML."""

import re
from collections.abc import Iterable, Mapping


class GuardError(ValueError):
    """Raised when a short violates a production invariant."""


# Dạng lịch hằng ngày (bảng ngày ~10 giây) cố ý ngắn, mở bằng bảng: miễn cổng
# công thức v2 và cổng mở, vẫn giữ cổng tên con giáp / giọng (PO duyệt 13/11).
DAILY_STYLES = frozenset({"daytable"})

_CREDIT = re.compile(r"\b(?:credit|credits|generated\s+by|made\s+with|chatgpt|grokbot|midjourney|stable\s+diffusion|openai|google\s+flow|ảnh\s+minh\s+hoạ\s+ai)\b", re.I)


def validate(rows: Iterable[Mapping], html: str | Iterable[str] = ()) -> None:
    """Validate short production invariants using the render-time gates."""
    import hf_batch_render
    import studio
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
        if row.get("lane") == "long":
            continue
        errors = []
        script = row.get("script") or []
        if row.get("series") == "fs":
            errors.extend("zodiac_naming_errors: " + x for x in hf_batch_render.zodiac_naming_errors(script))
        errors.extend("crowded_chi_lines: " + x for x in hf_batch_render.crowded_chi_lines(script))
        daily = row.get("style") in DAILY_STYLES
        if not daily:
            errors.extend("short_v2_issues: " + x for x in hf_batch_render.short_v2_issues(dict(row)))
        errors.extend("short_tone_issues: " + x for x in hf_batch_render.short_tone_issues(dict(row)))
        for hint in hf_batch_render.short_hook_hints(dict(row)):
            print(f"{row.get('id', '<row>')}: short_hook_hints: {hint}")
        if not daily and row.get("series") in ("bud", "fs", "vsd") and (row.get("scenes") or row.get("style") or row.get("media")):
            errors.extend("hook_errors: " + x for x in studio.hook_errors(dict(row)))
        if errors:
            raise GuardError(f"{row.get('id', '<row>')}: " + " | ".join(errors))
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
