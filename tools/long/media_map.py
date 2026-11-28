"""Gắn ảnh cho từng câu của plan Long (BUD/FS) theo luật cổng render, dùng chung cho mọi tập.

Rút từ pilot "so sánh hai" 15/11/2026 (FS C1/C2, BUD chay-mặn, A Xà Thế): mỗi luật dưới đây là một lần render bị chặn.
  1. Dòng 1 là ảnh có máy quay (cine object) — luật mở đầu PO 15/11, lint `mo_hinh_tinh`.
  2. Mọi câu trong ~135 giây đầu có ảnh riêng (cổng nhịp 120 giây: cảnh ≤ 4 giây); sau đó 2 câu một ảnh.
  3. 40 giây đầu ≥ 8 hình khác nhau (cổng O3).
  4. Một ảnh dùng lại trong cùng chương phải khác khung cắt (bridge chặn trùng byte); hết khung cắt thì sang ảnh thay thế.
  5. Câu nằm trong sơ đồ (visual có `until`) không có ảnh; câu ngay sau sơ đồ phải có ảnh (không thì engine lấy chữ đầu câu làm tiêu đề).
  6. 120 giây đầu không thẻ chữ trên nền trống (`quote`, `word`); thẻ khác chỉ giữ đúng một câu.
  7. Ảnh để `layout: full` + `cine` xoay vòng: khung nhỏ (frame/split) tự in chữ đầu câu làm tiêu đề, ra chữ cụt.
Thứ tự chọn ảnh mỗi câu: bảng chọn theo nghĩa `pick` (agent đọc kịch bản lập, xem `pick_prompt`) > từ khoá `kw_img` > ảnh của câu trước.

    .venv/bin/python tools/long/media_map.py prompt --plan plan.json --id L_x --catalog asset_needs.json --prefix ax_ --out pick_in.md
    .venv/bin/python tools/long/media_map.py apply --plan plan.json --id L_x --images-dir output/cl_staging/grokbot/lo/out \\
        --open ax_open --pick pick_L_x.json [--kw kw.json] [--alt alt.json]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from library.tools.image_similarity import near_duplicate

ROOT = Path(__file__).resolve().parents[2]
EVERY_LINE_S = 135
EARLY_S, EARLY_MIN_DISTINCT = 42, 8
CLEAN_S = 125
BLANK_TEXT = {"quote", "word"}
PD_LABEL = "PHỎNG DỰNG"
CAMS = ("push_in", "pan_left", "pull_out", "pan_right", "tilt_up", "dolly_parallax")
CROPS = [[fx, fy] for fy in (.3, .6, .45) for fx in (.2, .8, .5)]


def crop_for(k: int) -> list[float]:
    """Khung cắt thứ k (k >= 1) của một ảnh trong chương: 9 vị trí đẹp trước, sau đó dãy tỉ lệ vàng (không lặp)."""
    if k <= len(CROPS):
        return CROPS[k - 1]
    return [round(.15 + .7 * ((k * .6180339) % 1), 3), round(.2 + .6 * ((k * .4142135) % 1), 3)]


def heading(s: str) -> bool:
    s = s.strip()
    return s.startswith("**") and s.endswith("**") and len(s) > 4


def line_starts(script: list[str], segments: list[dict] | None = None, rate: float = 2.9) -> list[float]:
    """Giây bắt đầu từng câu: giây thật nếu out/<id>.json khớp số dòng, không thì ước `rate` tiếng/giây."""
    if segments and len(segments) == len(script):
        return [float(s["start"]) for s in segments]
    out, t = [], 0.0
    for x in script:
        out.append(t)
        t += max(1.2, len(re.sub(r"[*:,.?!]", " ", x).split()) / rate)
    return out


def clean_visuals(visuals: dict, starts: list[float]) -> dict:
    """Luật 6: bỏ thẻ chữ nền trống trong 120 giây đầu, các thẻ khác chỉ giữ một câu."""
    out = {}
    for k, v in visuals.items():
        i = int(k)
        if i <= len(starts) and starts[i - 1] < CLEAN_S and not v.get("suggested"):
            if v.get("type") in BLANK_TEXT:
                continue
            if "until" in v:
                v = {**v, "until": i}
        out[k] = v
    return out


def assign(script: list[str], *, open_img: str, path_of, visuals: dict | None = None, starts: list[float] | None = None,
           pick: dict | None = None, kw_img: list[tuple[str, str]] | None = None, alt: dict | None = None,
           pd: set[int] | None = None) -> dict:
    """Trả `media` {"<dòng>": spec}. `path_of(name)` -> đường dẫn ảnh (trong ai_media/ hoặc grokbot/).
    `pd`: các dòng phỏng dựng -> ảnh mang nhãn PHỎNG DỰNG (luật 16/11, #431 mục C); câu không ảnh riêng thì gắn ảnh mới."""
    visuals, pick, kw_img, alt, pd = visuals or {}, pick or {}, kw_img or [], alt or {}, pd or set()
    starts = starts or line_starts(script)
    pool = sorted({v for _, v in kw_img} | set(pick.values()) | {open_img}
                  | {x for values in alt.values() for x in values})
    covered = {j for k, v in visuals.items() for j in range(int(k), int(v.get("until", k)) + 1)}
    media: dict[str, dict] = {}
    used: dict[str, int] = {open_img: 1}
    early: set[str] = {open_img}
    last = open_img
    media["1"] = {"kind": "local", "path": path_of(open_img), "label": False, "cine": {"cam": "push_in", "depth": True}}
    for i, s in enumerate(script[1:], 2):
        if heading(s):
            used = {}
        if i in covered:
            continue
        every = 1 if starts[i - 1] < EVERY_LINE_S else 2
        if (i - 1) % every and not heading(s) and (i - 1) not in covered and i not in pd:
            continue
        name = pick.get(str(i)) or next((v for pat, v in kw_img if re.search(pat, s, re.I)), None) or last
        if starts[i - 1] < EARLY_S and str(i) not in pick:
            if name in early and len(early) < len(pool):
                name = next(x for x in pool if x not in early)
            early.add(name)
        # A semantic pick is editorial input. Automatic fallback among the local pool
        # skips a thumbnail-near-identical image to the preceding assigned scene.
        if str(i) not in pick and near_duplicate(path_of(last), path_of(name)):
            is_early = starts[i - 1] < EARLY_S
            ok = [c for c in pool if c != name and not (is_early and c in early)
                  and not near_duplicate(path_of(last), path_of(c))]
            if ok:
                if is_early:
                    early.discard(name)
                    early.add(ok[0])
                name = ok[0]
        if used.get(name, 0) > len(CROPS):
            alts = [a for a in alt.get(name, []) if used.get(a, 0) <= len(CROPS)]
            name = alts[0] if alts else min(pool, key=lambda x: used.get(x, 0))
        k = used.get(name, 0)
        used[name] = k + 1
        m = {"kind": "local", "path": path_of(name), "label": False, "layout": "full", "cine": {"cam": CAMS[i % len(CAMS)]}}
        if k:
            m["crop"] = crop_for(k)
        if i in pd:
            m.update(label=PD_LABEL, credit=" ")   # credit trắng: không in tên công cụ/ảnh AI lên hình (PO 04/11)
        media[str(i)] = m
        last = name
    return media


def duplicates(script: list[str], media: dict) -> list[tuple[int, int]]:
    """(dòng, dòng trước) có cùng ảnh + khung cắt trong một chương — phải rỗng trước khi render."""
    seen: dict = {}
    out = []
    for i, s in enumerate(script, 1):
        if heading(s):
            seen = {}
        m = media.get(str(i))
        if m:
            key = (m["path"], tuple(m.get("crop") or ()))
            if key in seen:
                out.append((i, seen[key]))
            seen[key] = i
    return out


def pick_prompt(script: list[str], media: dict, catalog: dict[str, str]) -> str:
    """Đầu vào cho agent chọn ảnh theo nghĩa: danh mục ảnh + kịch bản đánh dấu [ẢNH] ở dòng cần chọn."""
    lines = ["# Ảnh có sẵn:"] + [f"- {k}: {v}" for k, v in catalog.items()]
    lines += ["", "# Kịch bản (dòng | [ẢNH] nếu cần chọn | lời):"]
    lines += [f"{i} | {'[ẢNH]' if str(i) in media and i > 1 else ''} | {s}" for i, s in enumerate(script, 1)]
    return "\n".join(lines)


def _load_plan(path: Path, rid: str) -> tuple[list, dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else [rows]
    return rows, next(r for r in rows if r.get("id") == rid)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prompt", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--plan", type=Path, required=True)
        p.add_argument("--id", required=True)
        p.add_argument("--images-dir", type=Path, default=Path("."))
        p.add_argument("--open", default="")
        p.add_argument("--pick", type=Path)
        p.add_argument("--kw", type=Path, help='json [["regex", "ảnh"], ...]')
        p.add_argument("--alt", type=Path, help='json {"ảnh": ["ảnh thay", ...]}')
        p.add_argument("--pd", type=Path, help="json [số dòng phỏng dựng] -> nhãn PHỎNG DỰNG trên ảnh")
    sub.choices["prompt"].add_argument("--catalog", type=Path, required=True, help="asset_needs.json (items: filename, prompt)")
    sub.choices["prompt"].add_argument("--prefix", default="")
    sub.choices["prompt"].add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    rows, r = _load_plan(a.plan, a.id)
    script = r["script"]
    seg_p = a.plan.parent / "out" / f"{a.id}.json"
    starts = line_starts(script, json.loads(seg_p.read_text())["segments"] if seg_p.exists() else None)
    visuals = clean_visuals(r.get("visuals") or {}, starts)
    rel = lambda n: str((a.images_dir / f"{n}.png").resolve().relative_to(ROOT)) if (a.images_dir / f"{n}.png").resolve().is_relative_to(ROOT) else str(a.images_dir / f"{n}.png")
    kw = [tuple(x) for x in json.loads(a.kw.read_text())] if a.kw else []
    pick = json.loads(a.pick.read_text()) if a.pick and a.pick.exists() else {}
    alt = json.loads(a.alt.read_text()) if a.alt else {}
    pd = set(json.loads(a.pd.read_text())) if a.pd else set()
    media = assign(script, open_img=a.open or (kw[0][1] if kw else next(iter(pick.values()))), path_of=rel, visuals=visuals,
                   starts=starts, pick=pick, kw_img=kw, alt=alt, pd=pd)
    if a.cmd == "prompt":
        items = json.loads(a.catalog.read_text())["items"]
        cat = {x["filename"].rsplit(".", 1)[0]: x["prompt"].split(", painted")[0].split(", photorealistic")[0]
               for x in items if x["filename"].startswith(a.prefix) and "thumb" not in x["filename"]}
        a.out.write_text(pick_prompt(script, media, cat), encoding="utf-8")
        print(f"{a.out}: {sum(1 for k in media if k != '1')} dòng cần chọn ảnh")
        return 0
    dup = duplicates(script, media)
    if dup:
        print("TRÙNG ảnh+khung cắt trong chương:", dup)
        return 1
    r["media"], r["visuals"] = media, visuals
    a.plan.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.id}: {len(media)} ảnh, {len(visuals)} visual, {len({m['path'] for m in media.values()})} ảnh khác nhau")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
