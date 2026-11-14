"""007b: dựng lại 15 short FS bị chặn (màu mệnh + ngày tốt) từ BUILDER đã sửa.

- Nguồn: build_007_fs.py (3 video) và build_fs_dot2_1622.py (12 video); màu/ngày từ fs_mau_ngay.py.
- Xuất mp4 + txt/srt/render.json vào render_007b/ cùng id cũ. KHÔNG đụng render_007_fs / render_fs_dot2
  (video đạt đã hẹn giờ), KHÔNG đăng, KHÔNG hẹn giờ.
- Plan/packaging: chỉ cập nhật các id bị sửa (plan: chỉ các khoá đã có sẵn trong plan; packaging: chỉ id sửa).

Cách dùng:
    .venv/bin/python output/cl_staging/grok/build_007b_fs_fix.py --plan-only      # chỉ cập nhật plan/packaging
    .venv/bin/python output/cl_staging/grok/build_007b_fs_fix.py [--only id ...]  # render (cần ~ 1-2 phút / video)
    .venv/bin/python output/cl_staging/grok/build_007b_fs_fix.py --preview-only
"""
from __future__ import annotations

import argparse
from shortbuild import validate
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_007_fs as B7  # noqa: E402
import build_fs_dot2_1622 as B2  # noqa: E402

OUT = HERE / "render_007b"

FIX = {
    "fs_007_09_1": B7, "fs_007_12_1": B7, "fs_007_15_1": B7,
    "fs_d2_18_1": B2, "fs_d2_19_1": B2, "fs_d2_19_2": B2, "fs_d2_19_3": B2,
    "fs_d2_20_1": B2, "fs_d2_20_2": B2, "fs_d2_20_3": B2, "fs_d2_20_4": B2,
    "fs_d2_21_1": B2, "fs_d2_21_2": B2, "fs_d2_22_1": B2, "fs_d2_22_2": B2,
}
FORBIDDEN = {"fs_007_13_1"}  # đã đăng


def selected(ids: list[str] | None):
    out = []
    for mod in (B7, B2):
        plan = mod.make_plan()
        mod.plan_guard(plan)
        for it in plan:
            if it["id"] in FIX and FIX[it["id"]] is mod and (not ids or it["id"] in ids):
                assert it["id"] not in FORBIDDEN
                out.append((mod, it))
    out.sort(key=lambda x: (x[1]["day"], x[1]["slot"]))
    validate([it for _, it in out])
    return out


def update_plan_files(sel, with_dur: bool) -> None:
    """Chỉ thay các khoá đã có trong plan hiện hành của id bị sửa; các id khác giữ nguyên byte."""
    for mod in (B7, B2):
        mine = [it for m, it in sel if m is mod]
        if not mine:
            continue
        old = json.loads(mod.PLAN_FILE.read_text(encoding="utf-8"))
        byid = {it["id"]: it for it in old}
        for it in mine:
            tgt = byid[it["id"]]
            for k in list(tgt):
                if k == "dur":
                    mf = OUT / f"{it['id']}.render.json"
                    if with_dur and mf.exists():
                        tgt["dur"] = round(json.loads(mf.read_text(encoding="utf-8"))["duration_s"], 2)
                elif k in it:
                    tgt[k] = it[k]
        mod.PLAN_FILE.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")
        print("plan cập nhật:", mod.PLAN_FILE.name, [it["id"] for it in mine])


def export_preview(sel) -> None:
    cw, ch = 270, 480
    n = len(sel)
    cols = 8
    rows_n = (n + cols - 1) // cols
    cell_h = ch * 3 + 30
    sheet = Image.new("RGB", (cw * cols, cell_h * rows_n), (10, 12, 18))
    dr = ImageDraw.Draw(sheet)
    for i, (_, it) in enumerate(sel):
        rid = it["id"]
        x0, y0 = (i % cols) * cw, (i // cols) * cell_h
        dr.text((x0 + 6, y0 + 8), f"{rid} {it['day'][5:]} {it['slot']}", fill=(253, 230, 138))
        for row, kind in enumerate(("0", "mid", "last")):
            f = OUT / f"frame_{kind}_1080_{rid}.png"
            if f.exists():
                sheet.paste(Image.open(f).convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS),
                            (x0, y0 + 30 + row * ch))
    sheet.save(OUT / "preview_007b.jpg", quality=90)
    print("preview ->", OUT / "preview_007b.jpg")
    w_168 = 168 * cols
    h_168 = round(cell_h * rows_n * (168 / cw))
    sheet.resize((w_168, h_168), Image.Resampling.LANCZOS).save(OUT / "preview_007b_168.jpg", quality=90)
    print("preview 168 ->", OUT / "preview_007b_168.jpg")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--preview-only", action="store_true")
    a = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    for mod in (B7, B2):  # đổi thư mục xuất của builder sang render_007b
        mod.RENDER_DIR = OUT
        mod.ROOT_RENDER_DIR = OUT

    sel = selected(a.only)
    print(f"007b: {len(sel)} video -> {OUT}")
    if a.preview_only:
        export_preview(sel)
        raise SystemExit(0)
    for mod in (B7, B2):
        mod.write_packaging([it for m, it in sel if m is mod])
    update_plan_files(sel, with_dur=False)
    if a.plan_only:
        raise SystemExit(0)
    for mod, it in sel:
        mod.render_one(it)
    update_plan_files(sel, with_dur=True)
    export_preview(sel)
