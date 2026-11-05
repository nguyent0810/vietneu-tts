"""BUD 138g wave 2 composition builder; does not invoke TTS or video rendering."""

from pathlib import Path

from shortbuild import bud_html, validate, write_plan


def build(rows, plan_path: Path, packaging_dir: Path, *, compositions_dir: Path,
          font_css: str, html=()):
    """Write production HTML A/B plus plan and sidecars from prepared input rows.

    Each row must carry ``times``, ``dur``, ``image_path`` and the fields consumed
    by ``shortbuild.bud_html``. Media/timing preparation stays with the caller.
    """
    rows = list(rows)
    validate(rows, html)
    compositions_dir = Path(compositions_dir)
    compositions_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        for candidate_b, suffix in ((False, ""), (True, "_b")):
            image_path = row.get("image_path_b", row["image_path"]) if candidate_b else row["image_path"]
            page = bud_html(row, row["times"], row["dur"], image_path,
                            font_css=font_css, candidate_b=candidate_b)
            (compositions_dir / f"_r_{row['id']}{suffix}.html").write_text(page, encoding="utf-8")
    plan_rows = [
        {key: value for key, value in row.items()
         if key not in {"times", "image_path", "image_path_b"}}
        for row in rows
    ]
    return write_plan(plan_rows, plan_path, channel="bud", packaging_dir=packaging_dir)
