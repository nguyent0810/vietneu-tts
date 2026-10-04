"""Xem trước tư liệu của một plan video dài TRƯỚC khi render (theo V2: contact sheet đánh số, chọn bằng mắt).

Với mỗi mục `media` trong plan: lấy ĐÚNG tài sản sẽ dùng (Commons / bảo tàng / ảnh stock / khung hình clip stock),
dựng lưới đánh số theo số câu + query, để loại ảnh sai ngữ cảnh (tôn giáo khác, người nước ngoài trong cảnh
gia đình Việt, chữ/logo, vật sai...). Tìm ứng viên mới: `python hf_media_sheet.py find "<query>" [--by]`.

    python hf_media_sheet.py plan output/cl_staging/long/plan_long_w50.json L_fs_15 [out.jpg]
    python hf_media_sheet.py find "wiki:vi:Chùa Bút Tháp" --by   # chỉ ảnh trong bài Wikipedia (vi/en)
    python hf_media_sheet.py find "Hoi An old town" --by      # Commons + Openverse + Wellcome/AIC/Europeana (X) + bảo tàng CC0 (Cleveland, AIC)
"""
from __future__ import annotations

import json
import subprocess
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
CELL_W, CELL_H, COLS = 384, 216, 5


def _font(size: int):
    for f in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def preview(spec: dict, domain: str) -> tuple[Image.Image | None, str]:
    """Trả (ảnh xem trước, ghi chú). Không ném lỗi: lỗi ghi vào ghi chú để sheet vẫn dựng được."""
    import hyperframes_bridge as HB  # noqa: PLC0415
    kind = (spec.get("kind") or "video").lower()
    try:
        if kind == "commons":
            import hf_commons  # noqa: PLC0415
            p, credit = hf_commons.fetch(spec["file"], allow_by=bool(spec.get("by")))
            return Image.open(p).convert("RGB"), "COMMONS · " + credit.split(" — ")[-1][:60]
        if kind == "openverse":
            import hf_openverse  # noqa: PLC0415
            p, credit = hf_openverse.fetch(spec["ref"])
            return Image.open(p).convert("RGB"), "OPENVERSE · " + credit.split(" — ")[-1][:60]
        if kind == "ext":
            import hf_extmedia  # noqa: PLC0415
            p, credit = hf_extmedia.fetch(spec["ref"])
            return Image.open(p).convert("RGB"), "TƯ LIỆU · " + credit.split(" — ")[-1][:60]
        if kind == "museum":
            import hf_museum  # noqa: PLC0415
            p, credit = hf_museum.fetch(spec["ref"])
            return Image.open(p).convert("RGB"), "BẢO TÀNG · " + credit[:60]
        q = HB.sanitize_query(spec.get("query", ""), domain)
        if kind == "image":
            import stock_image  # noqa: PLC0415
            p = stock_image.get_or_fetch_stock_image(q, "landscape")
            if p is None:
                return None, f"KHÔNG CÓ ẢNH · {q}"
            return Image.open(p).convert("RGB"), "ẢNH · " + q
        import asset_generation  # noqa: PLC0415
        clip = asset_generation.get_or_fetch_stock_video(q)
        if clip is None:
            return None, f"KHÔNG CÓ CLIP · {q}"
        out = ROOT / "chunks_cache" / "sheet_frames"
        out.mkdir(parents=True, exist_ok=True)
        fr = out / (Path(clip).stem + ".jpg")
        if not fr.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-ss", "1.5", "-i", str(clip), "-frames:v", "1", "-vf", "scale=640:-1", "-y", str(fr)], check=True)
        return Image.open(fr).convert("RGB"), "VIDEO · " + q
    except Exception as e:  # noqa: BLE001
        return None, f"LỖI {kind}: {str(e)[:70]}"


def sheet(items: list[tuple[str, Image.Image | None, str]], out: Path) -> Path:
    rows = (len(items) + COLS - 1) // COLS
    canvas = Image.new("RGB", (COLS * CELL_W, rows * (CELL_H + 44)), (16, 16, 20))
    d = ImageDraw.Draw(canvas)
    f1, f2 = _font(20), _font(14)
    for k, (label, im, note) in enumerate(items):
        x, y = (k % COLS) * CELL_W, (k // COLS) * (CELL_H + 44)
        if im is not None:
            im = im.copy()
            im.thumbnail((CELL_W - 8, CELL_H - 8))
            canvas.paste(im, (x + (CELL_W - im.width) // 2, y + (CELL_H - im.height) // 2))
        else:
            d.rectangle([x + 4, y + 4, x + CELL_W - 4, y + CELL_H - 4], outline=(200, 60, 60), width=3)
        d.text((x + 8, y + 6), label, fill=(255, 220, 90), font=f1)
        d.text((x + 6, y + CELL_H + 4), note[:52], fill=(230, 230, 230), font=f2)
        d.text((x + 6, y + CELL_H + 22), note[52:104], fill=(170, 170, 170), font=f2)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=86)
    return out


def plan_sheet(plan: Path, rid: str, out: Path | None = None) -> Path:
    row = next(r for r in json.loads(plan.read_text(encoding="utf-8")) if r["id"] == rid)
    domain = "BUD" if row.get("series") == "bud" else "FS"
    items = []
    for k, spec in sorted(row.get("media", {}).items(), key=lambda x: int(x[0])):
        im, note = preview(spec, domain)
        items.append((f"#{k}", im, note))
        print(f"#{k:>4} {note}")
    return sheet(items, out or plan.parent / "out" / f"{rid}_media_sheet.jpg")


def find(query: str, allow_by: bool = False, out: Path | None = None) -> Path:
    import urllib.request  # noqa: PLC0415
    import io  # noqa: PLC0415
    import hf_commons  # noqa: PLC0415
    import hf_museum  # noqa: PLC0415
    items, label = [], query
    if query.startswith("wiki:"):        # wiki:vi:Chùa Bút Tháp | wiki:Lo Shu Square -> chỉ ảnh trong bài Wikipedia đó
        rest = query[5:]
        lang, title = (rest.split(":", 1) if re.match(r"^[a-z]{2}:", rest) else ("en", rest))
        cands, query = hf_commons.article_images(title, lang, allow_by)[:30], ""
    else:
        cands = hf_commons.search(query, 30, allow_by=allow_by)[:15]
    for c in cands:
        try:
            req = urllib.request.Request(c["thumb"], headers=hf_commons.UA)
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
        except Exception:  # noqa: BLE001
            im = None
        items.append((f"C{len(items) + 1}", im, f"{c['license']} · {c['file']}"))
        print(f"C{len(items)} {c['license']:<16} {c['file']}")
    import hf_openverse  # noqa: PLC0415
    try:
        ovs = hf_openverse.search(query, 15)[:15] if query else []
    except Exception as e:  # noqa: BLE001 -- Openverse quá tải/giới hạn: vẫn dựng sheet với nguồn khác
        print("openverse lỗi:", e)
        ovs = []
    for c in ovs:
        try:
            req = urllib.request.Request(c["thumb"], headers=hf_openverse.UA)
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
        except Exception:  # noqa: BLE001
            im = None
        items.append((f"O{len(items) + 1}", im, f"{c['license']} · {c['source']} · {c['ref']} · {c['title']}"))
        print(f"O{len(items)} {c['license']:<12} {c['source']:<10} {c['ref']} {c['title'][:60]}")
    import hf_extmedia  # noqa: PLC0415   -- Wellcome / AIC / Europeana (V2 media_search.py)
    for c in (hf_extmedia.search(query, limit=6) if query else []):
        try:
            req = urllib.request.Request(c["thumb"], headers=hf_extmedia.UA)
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
        except Exception:  # noqa: BLE001
            im = None
        items.append((f"X{len(items) + 1}", im, f"{c['license']} · {c['ref']} · {c['title']}"))
        print(f"X{len(items)} {c['license']:<12} {c['ref']} {c['title'][:60]}")
    for m in (hf_museum.search(query, 8, sources=("cma",))[:8] if query else []):  # Met API 410; AIC đã có ở nhóm X (hf_extmedia)
        try:
            p, _ = hf_museum.fetch(m["ref"])
            im = Image.open(p).convert("RGB")
        except Exception:  # noqa: BLE001
            im = None
        items.append((f"M{len(items) + 1}", im, f"{m['ref']} · {m['title']}"))
        print(f"M{len(items)} {m['ref']} {m['title']}")
    safe = "".join(ch if ch.isalnum() else "_" for ch in label)[:40]
    return sheet(items, out or ROOT / "chunks_cache" / "find_sheets" / f"{safe}.jpg")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "plan":
        print(plan_sheet(Path(a[1]), a[2], Path(a[3]) if len(a) > 3 else None))
    elif len(a) >= 2 and a[0] == "find":
        print(find(" ".join(x for x in a[1:] if x != "--by"), allow_by="--by" in a))
    else:
        print(__doc__)
