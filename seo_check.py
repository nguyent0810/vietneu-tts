"""Pre-upload SEO checks for local long/short plan JSON files.

This is a proposal checker only. It does not call YouTube or mutate upload plans.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        if isinstance(value.get("videos"), list):
            return _rows(value["videos"])
        if isinstance(value.get("rows"), list):
            return _rows(value["rows"])
        return [value]
    return []


def _description(row: dict[str, Any]) -> str:
    if isinstance(row.get("description"), str):
        return row["description"]
    seo = row.get("seo") or {}
    parts = []
    parts.extend(seo.get("hook") or [])
    if seo.get("summary"):
        parts.append(seo["summary"])
    if seo.get("chapters"):
        parts.extend(seo["chapters"])
    if seo.get("hashtags"):
        parts.append(seo["hashtags"])
    if row.get("insight"):
        parts.append(row["insight"])
    if row.get("hashtags"):
        parts.append(" ".join(row["hashtags"]))
    return "\n".join(str(x) for x in parts)


def _keyword(row: dict[str, Any]) -> str:
    seo = row.get("seo") or {}
    return str(seo.get("keyword") or row.get("keyword") or row.get("primary_keyword") or "").strip()


def _spoken_first_30(row: dict[str, Any]) -> str:
    script = row.get("script") or []
    # Plan files generally store each sentence as one list item. Three items are
    # an explicit approximation; exact timing is unavailable before rendering.
    return " ".join(str(x) for x in script[:3]) if isinstance(script, list) else str(script)


def check_row(row: dict[str, Any], plan_path: str = "") -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    def add(level: str, code: str, message: str) -> None:
        issues.append({"level": level, "code": code, "message": message})

    title = str(row.get("title") or "")
    keyword = _keyword(row)
    description = _description(row)
    tags = row.get("tags") or []
    hashtags = re.findall(r"(?<!\w)#[\wÀ-ỹ]+", description)
    hashtags += [str(x) for x in (row.get("hashtags") or []) if str(x).startswith("#")]
    # De-duplicate if hashtags are already included in description.
    hashtags = list(dict.fromkeys(hashtags))
    # Short plans also carry ``dur``. Long plans carry a thumbnail and SEO
    # block, which is a more reliable format discriminator for this repo.
    long_form = bool(row.get("series") in {"bud", "fs"} and ("thumbnail" in row or "seo" in row))
    if len(title) > 60:
        add("WARN", "TITLE_OVER_60", f"Tiêu đề {len(title)} ký tự (>60; 60 chỉ là ngưỡng đề xuất).")
    if not keyword:
        add("WARN", "KEYWORD_MISSING", "Plan chưa khai báo keyword chính; không tự đoán để chấm.")
    else:
        if keyword.casefold() not in " ".join(title.split()[:4]).casefold():
            add("ERROR", "KEYWORD_NOT_EARLY", "Keyword không xuất hiện trong 4 từ đầu tiêu đề.")
        pos = description.casefold().find(keyword.casefold())
        if pos < 0 or pos >= 150:
            add("ERROR", "KEYWORD_NOT_IN_DESCRIPTION", "Keyword thiếu trong 150 ký tự đầu mô tả.")
        if keyword.casefold() not in _spoken_first_30(row).casefold():
            add("WARN", "KEYWORD_NOT_SPOKEN", "Không thấy keyword trong 3 câu đầu (xấp xỉ 30 giây; cần kiểm thời lượng thật).")
    if long_form and not re.search(r"(?m)^\d{1,2}:\d{2}\s+\S", description):
        chapters = (row.get("chapters") or (row.get("seo") or {}).get("chapters") or [])
        if not chapters:
            add("WARN", "CHAPTERS_MISSING", "Long chưa có timestamp chương trong mô tả/plan.")
    if len(hashtags) > 5:
        add("WARN", "HASHTAGS_OVER_5", f"Có {len(hashtags)} hashtag (>5; ngưỡng khuyến nghị).")
    if len(hashtags) > 15:
        add("WARN", "HASHTAGS_OVER_15", f"Có {len(hashtags)} hashtag (>15; ngưỡng biên tập, YouTube bỏ qua hashtag khi quá 60).")
    if len(hashtags) > 60:
        add("ERROR", "HASHTAGS_OVER_60", f"Có {len(hashtags)} hashtag (>60; YouTube bỏ qua toàn bộ hashtag).")
    if len(tags) < 8:
        add("WARN", "TAGS_UNDER_8", f"Có {len(tags)} tag (<8; YouTube nói tag thường là tín hiệu phụ).")
    if keyword and tags and str(tags[0]).casefold() != keyword.casefold():
        add("WARN", "FIRST_TAG_MISMATCH", "Tag đầu không trùng chính xác keyword.")
    if long_form and row.get("thumbnail"):
        thumb = Path(plan_path).parent / str(row["thumbnail"]) if plan_path else Path(str(row["thumbnail"]))
        if not thumb.exists():
            # Common project convention: long plan thumbnails live in ../thumbs.
            if plan_path:
                thumb = Path(plan_path).parent / "thumbs" / str(row["thumbnail"])
        if not thumb.exists():
            add("WARN", "THUMBNAIL_MISSING", f"Không tìm thấy thumbnail cục bộ: {row['thumbnail']}.")
        else:
            try:
                from PIL import Image
                with Image.open(thumb) as im:
                    if im.size != (1280, 720):
                        add("ERROR", "THUMBNAIL_SIZE", f"Thumbnail {im.width}×{im.height}, cần 1280×720.")
                if thumb.stat().st_size > 2 * 1024 * 1024:
                    add("ERROR", "THUMBNAIL_OVER_2MB", f"Thumbnail {thumb.stat().st_size} byte (>2 MiB).")
            except ImportError:
                add("WARN", "THUMBNAIL_UNCHECKED", "Thiếu Pillow; chưa đo được kích thước thumbnail.")
    return issues


def check_plan(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return [{"id": row.get("id"), "title": row.get("title"), "issues": check_row(row, str(path))}
            for row in _rows(data)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plans", nargs="+", help="Long/short plan JSON paths")
    args = parser.parse_args()
    failed = False
    for plan in args.plans:
        results = check_plan(plan)
        print(f"PLAN {plan}: {len(results)} mục")
        for result in results:
            issues = result["issues"]
            print(f"  {result['id'] or '?'}: " + (", ".join(f"{i['level']} {i['code']}" for i in issues) if issues else "OK"))
            failed |= any(i["level"] == "ERROR" for i in issues)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
