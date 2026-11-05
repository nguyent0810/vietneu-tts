"""Soát video dài TRƯỚC khi render: `hyperframes check` (runtime, bố cục, chuyển
động, tương phản chữ WCAG AA) tại giữa từng cảnh.

`check` chỉ soát index.html của một project, trong khi bridge render một
composition sinh ra + file biến. Nên dựng một project TẠM (chunks_cache/qa/):
symlink compositions/ và assets/, index.html = composition với biến đã nướng
vào giá trị mặc định, đường dẫn ./ đổi thành compositions/. Project chính
không bị đụng.

Bắt được đúng loại lỗi từng lọt qua mắt: phụ đề chữ mực tối trên bóng tối
dưới ảnh tràn khung (nền giấy, L_bud_03 bản đầu).

    python hf_qa.py <composition.html> <vars.json> [thời điểm,...]

Cổng tràn chữ cho short (25/10: tiêu đề vàng 18 ký tự ở 96 px và lưới năm 5 cột lọt
tới tận khung tĩnh). `check` xếp tràn chữ ở mức warning/info nên cổng `HF_QA=strict`
(chỉ chặn error) không dừng được; `overflows()` coi MỌI phát hiện *_overflow là lỗi.
Tràn có chủ đích (vệt sáng quét ngang) thì gắn `data-layout-allow-overflow`.

    python hf_qa.py --overflow <composition.html> [...]   # exit 1 nếu có tràn
    python hf_qa.py --contrast <composition.html> [...]   # exit 1 nếu chữ dưới chuẩn tương phản WCAG AA

Ba lỗi bố cục đo trên trang đã seek (Ticket #51). Mặc định là cảnh báo; --strict thì thành lỗi (exit 1).

    python hf_qa.py --scenes <index.html> <vars.json> [--strict] [--compositions <dir>]
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent
HF_PROJECT = ROOT / "hyperframes_short"
QA_DIR = ROOT / "chunks_cache" / "qa"


def _bake(comp_src: str, variables: dict) -> str:
    m = re.search(r"data-composition-variables='(.*?)'>", comp_src, re.S)
    if m:
        decl = json.loads(html.unescape(m.group(1)))
        for d in decl:
            if d["id"] in variables:
                d["default"] = variables[d["id"]]
        baked = html.escape(json.dumps(decl, ensure_ascii=False), quote=True).replace("&quot;", '"').replace("'", "&#39;")
        comp_src = comp_src[:m.start(1)] + baked + comp_src[m.end(1):]
    # composition nằm trong compositions/, index.html nằm ở gốc project tạm
    comp_src = comp_src.replace('href="./', 'href="compositions/').replace('src="./', 'src="compositions/')
    # Lint tĩnh chỉ đọc script inline, không thấy engine.js đăng ký timeline
    # (window.__timelines["main"] = tl) -> báo lỗi rồi dừng, không chạy tới phần
    # soát bố cục/tương phản. Khai báo inline; engine.js vẫn ghi đè lúc chạy.
    reg = '<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = window.__timelines["main"] || null;</script>'
    return comp_src.replace("</head>", reg + "\n</head>", 1)


def run(comp_path: Path, vars_path: Path | None = None, times: list[float] | None = None, *,
        samples: int | None = None, contrast: bool = True) -> dict:
    stem = comp_path.stem.replace(".render_", "")
    proj = QA_DIR / stem
    if proj.exists():
        shutil.rmtree(proj)
    proj.mkdir(parents=True)
    for name in ("compositions", "assets"):
        (proj / name).symlink_to(HF_PROJECT / name)
    for f in ("hyperframes.json", "package.json"):
        if (HF_PROJECT / f).exists():
            shutil.copy2(HF_PROJECT / f, proj / f)
    variables = json.loads(vars_path.read_text(encoding="utf-8")) if vars_path else {}
    (proj / "index.html").write_text(_bake(comp_path.read_text(encoding="utf-8"), variables), encoding="utf-8")
    at = f" --at {','.join(f'{t:.2f}' for t in times)}" if times else (f" --samples {samples}" if samples else "")
    at += "" if contrast else " --no-contrast"
    cmd = ('export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1 || exit 97; '
           f'cd {proj.as_posix()!r} && npx --yes hyperframes@0.8.75 check . --json --timeout 20000{at}')
    res = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=1800)
    out = res.stdout.strip()
    try:
        report = json.loads(out[out.index("{"):])
    except ValueError:
        return {"ok": False, "error": (res.stderr or out)[-1500:]}
    (proj / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


# Phát hiện CỐ Ý, không phải lỗi: số chương dạng viền rỗng (chữ trong suốt +
# text-stroke), dạ quang z-index -1 dưới chữ (cha đã isolation: isolate).
ALLOW = {("text_not_painted", "div.lf-chap-ghost"), ("negative_z_index", ".lf-marker")}
SECTIONS = ("lint", "runtime", "layout", "motion", "contrast")


def findings(report: dict) -> list[dict]:
    out = []
    for sec in SECTIONS:
        for f in (report.get(sec) or {}).get("findings") or []:
            if (f.get("code"), f.get("selector")) not in ALLOW:
                out.append({**f, "section": sec})
    return out


def summarize(report: dict) -> str:
    if "error" in report:
        return f"QA không chạy được: {report['error'][:400]}"
    fs = findings(report)
    errs = [f for f in fs if f.get("severity") == "error"]
    lines = [f"QA: {'ĐẠT' if not errs else 'CÓ LỖI'} -- {len(errs)} lỗi, {len(fs) - len(errs)} cảnh báo"]
    by = {}
    for f in fs:
        k = (f.get("severity"), f["section"], f.get("code"), f.get("selector"))
        by.setdefault(k, []).append(f.get("time"))
    for (sev, sec, code, sel), ts in sorted(by.items(), key=lambda x: (x[0][0] != "error", x[0][1])):
        lines.append(f"  {sev:7s} {sec}/{code} {sel} @ {', '.join(str(t) for t in ts[:6])}")
    return "\n".join(lines)


def overflows(report: dict) -> list[dict]:
    """Mọi phát hiện tràn (canvas_overflow, container_overflow, ...) ở mục layout, bất kể mức độ."""
    return [f for f in findings(report) if f["section"] == "layout" and str(f.get("code", "")).endswith("_overflow")]


def overflow_lines(report: dict) -> list[str]:
    """Gộp theo (mã, selector, chữ) để mỗi chỗ tràn in một dòng, kèm số px vượt lớn nhất."""
    by: dict[tuple, list] = {}
    for f in overflows(report):
        by.setdefault((f.get("code"), f.get("selector"), (f.get("text") or "")[:40]), []).append(f)
    out = []
    for (code, sel, text), fs in by.items():
        px = max((max((f.get("overflow") or {}).values(), default=0) for f in fs), default=0)
        ts = sorted({f.get("time") for f in fs if f.get("time") is not None})
        out.append(f"{code} {sel} {text!r} vượt {px:.0f}px @ {', '.join(str(t) for t in ts[:4])}")
    return out


def _standalone_project(comp_path: Path, tag: str, src: str | None = None) -> Path:
    """Project tạm cho một short tự đủ: index.html = composition (../studio/, ../assets/ đổi thành ./), symlink studio/ assets/."""
    proj = QA_DIR / f"{tag}_{comp_path.stem}"
    if proj.exists():
        shutil.rmtree(proj)
    proj.mkdir(parents=True)
    for name in ("assets", "studio"):
        if (HF_PROJECT / name).exists():
            (proj / name).symlink_to(HF_PROJECT / name)
    for f in ("hyperframes.json", "package.json"):
        if (HF_PROJECT / f).exists():
            shutil.copy2(HF_PROJECT / f, proj / f)
    src = comp_path.read_text(encoding="utf-8") if src is None else src
    (proj / "index.html").write_text(src.replace("../studio/", "studio/").replace("../assets/", "assets/"), encoding="utf-8")
    return proj


def _hf_json(proj: Path, args: str) -> dict:
    cmd = ('export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1 || exit 97; '
           f'cd {proj.as_posix()!r} && npx --yes hyperframes@0.8.75 {args}')
    res = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=600)
    out = res.stdout.strip()
    try:
        return json.loads(out[out.index("{"):])
    except ValueError:
        return {"ok": False, "error": (res.stderr or out)[-1500:]}


def inspect_layout(comp_path: Path, samples: int = 6) -> dict:
    """`hyperframes inspect` (chỉ bố cục) cho một short tự đủ (ảnh nhúng data URI, như short R-series).

    Không dùng `check`: lint của nó chạy trước và dừng hẳn khi gặp lỗi không liên quan bố cục (font dự phòng
    Noto Serif CJK không có @font-face, đường dẫn ../studio/), để lại layout 0 mẫu. Project tạm có studio/ và
    assets/ (đường dẫn ../ đổi thành ./) để đo bằng đúng font Be Vietnam Pro sẽ render.
    Trả về dạng report của `check` ({"layout": {"findings", "samples"}}) để dùng chung overflows().
    """
    proj = _standalone_project(comp_path, "ovf")
    rep = _hf_json(proj, f"inspect . --json --samples {samples} --timeout 20000")
    if "error" in rep:
        return rep
    (proj / "inspect.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ok": rep.get("ok"), "layout": {"findings": rep.get("issues") or [], "samples": len(rep.get("samples") or [])}}


def gate_overflow(comp_path: Path, samples: int = 6) -> list[str]:
    """Cổng trước render cho short: [] là đạt. Không đo được thì báo lỗi, không cho qua im lặng."""
    rep = inspect_layout(Path(comp_path), samples)
    if "error" in rep:
        raise RuntimeError(f"hyperframes inspect không chạy được cho {Path(comp_path).name}: {rep['error'][:400]}")
    if not rep["layout"]["samples"]:
        raise RuntimeError(f"hyperframes inspect không lấy được mẫu nào cho {Path(comp_path).name} (0 mẫu)")
    return overflow_lines(rep)


FONT_LINT = "font_family_without_font_face"


def _missing_fonts(rep: dict) -> list[str]:
    """Tên font lint kêu thiếu @font-face: '... declaration: noto serif cjk sc, songti sc.' -> danh sách tên."""
    out = []
    for f in (rep.get("lint") or {}).get("findings") or []:
        if f.get("code") == FONT_LINT and f.get("severity") == "error":
            m = re.search(r"declaration:\s*(.+?)\.(\s|$)", f.get("message") or "")
            if m:
                out += [x.strip() for x in m.group(1).split(",") if x.strip()]
    return list(dict.fromkeys(out))


def contrast_check(comp_path: Path, samples: int = 3) -> dict:
    """Pass tương phản WCAG AA của `hyperframes check` cho short tự đủ.

    Lint của `check` chạy trước và nếu có lỗi thì bỏ luôn phần đo (0 mẫu). Lỗi hay gặp là font dự phòng không
    khai báo @font-face (Noto Serif CJK SC ở thẻ tượng BUD): bản tạm được thêm @font-face src:local() cho đúng các
    font lint nêu rồi chạy lại một lần. File gốc không đổi.
    """
    comp_path = Path(comp_path)
    args = f"check . --json --samples {samples} --timeout 20000"
    rep = _hf_json(_standalone_project(comp_path, "ctr"), args)
    fonts = _missing_fonts(rep) if "error" not in rep else []
    if fonts:
        stub = "".join(f'@font-face{{font-family:"{f}";src:local("{f}");}}' for f in fonts)
        src = comp_path.read_text(encoding="utf-8").replace("<style>", "<style>" + stub, 1)
        rep = _hf_json(_standalone_project(comp_path, "ctr", src), args)
    return rep


def contrast_lines(report: dict) -> list[str]:
    """Phát hiện tương phản mức error/warning, gộp theo (selector, chữ), kèm tỉ lệ thấp nhất."""
    by: dict[tuple, list] = {}
    for f in (report.get("contrast") or {}).get("findings") or []:
        if f.get("severity") in ("error", "warning"):
            by.setdefault((f.get("selector"), (f.get("text") or "")[:40]), []).append(f)
    out = []
    for (sel, text), fs in by.items():
        ratios = [f.get("ratio") for f in fs if isinstance(f.get("ratio"), (int, float))]
        r = f"tỉ lệ {min(ratios):.2f}" if ratios else "dưới chuẩn"
        ts = sorted({f.get("time") for f in fs if f.get("time") is not None})
        out.append(f"contrast {sel} {text!r} {r} (AA cần 4.5) @ {', '.join(str(t) for t in ts[:4])}")
    return out


def gate_contrast(comp_path: Path, samples: int = 3) -> list[str]:
    """Cổng tương phản trước render cho short: [] là đạt. Không đo được (0 mẫu) thì báo lỗi, không cho qua im lặng."""
    rep = contrast_check(Path(comp_path), samples)
    if "error" in rep:
        raise RuntimeError(f"hyperframes check không chạy được cho {Path(comp_path).name}: {rep['error'][:400]}")
    if not (rep.get("contrast") or {}).get("samples"):
        lint = [f"{f.get('code')}: {str(f.get('message'))[:120]}" for f in (rep.get("lint") or {}).get("findings") or []
                if f.get("severity") == "error"]
        raise RuntimeError(f"hyperframes check không đo tương phản {Path(comp_path).name} (0 mẫu). Lint: {lint[:3]}")
    return contrast_lines(rep)


# ---------------------------------------------------------------------------
# Ticket #51: phụ đề bị che, khung cuối trống, vật che ảnh tràn.
# Hằng số là ngưỡng (81r), không phải toạ độ của một lỗi đã biết.
# Phụ đề: lấn <= 4px thì sạch, lấn 5px và diện tích giao >= 50px² thì báo
# (diện tích 45 sạch, 160 báo).
CAP_TOLERANCE_PX = 4.0
CAP_MIN_AREA_PX2 = 50.0
# Vòng trang trí mờ (opacity khoảng 0.2) không phải vật đè.
MIN_ELEMENT_OPACITY = 0.35
# Lớp gần kín khung (nền, cảnh, hạt) là khung hình, không phải vật che/đè.
FRAME_WRAP_MIN_COVER = 0.85
# Ảnh tràn: cả hai cạnh phủ >= 90% khung. Thẻ nổi (cao khoảng 2/3 khung) không tính.
FULLBLEED_MIN_AXIS = 0.90
# Che > 30% ảnh tràn thì báo. Nhãn ~2% và dải ~18% sạch; mảng 33% thì báo (81r).
OCCLUSION_MIN_COVER = 0.30
# Nền đặc: alpha kênh màu > 0.9. Gradient để computed background-color trong suốt.
SOLID_ALPHA_MIN = 0.9
# Khung trống CHỈ khi cuối trống hơn giữa (81r). Không chấm một khung tối đơn lẻ.
EMPTY_BG_END = 0.985
EMPTY_BG_DELTA = 0.015
EMPTY_EDGE_END = 0.01
EMPTY_EDGE_MID = 0.02
# Cắt theo tỉ lệ khung: bỏ ~12% đầu (đầu trang) và ~18% đáy (dải phụ đề), 10% mỗi bên.
EMPTY_CROP = (0.10, 0.12, 0.90, 0.82)
# 0.38s sau mốc giao (engine.js:420). Iris 0.7s ease power2 đo trên trang ra
# circle ~48%: đĩa của lớp sau phủ ~70% ảnh tràn. Cùng lúc, circle đó nếu cắt
# chính ảnh thì giấu ~30%; vệt quét 0.6s giấu dưới 20%.
HANDOVER_SAMPLE_S = 0.38
# Trước mốc giao 0.08s: cảnh ra chưa tween opacity (bắt đầu tại T hoặc T+0.1).
# Sau mốc này khung chỉ còn vòng nền, cả bản đã sửa cũng trông trống.
PRE_FADE_S = 0.08
# Cảnh cuối fade 0.5s từ DUR-0.5 (engine.js). Lấy mẫu trước đoạn fade đó.
OUTRO_GUARD_S = 0.55

_CIRCLE_RE = re.compile(
    r"circle\(\s*([0-9.]+)(px|%)(?:\s+at\s+([0-9.]+)(px|%)\s+([0-9.]+)(px|%))?\s*\)",
    re.I,
)
_INSET_RE = re.compile(r"inset\(\s*([^)]*)\)", re.I)
_LEN_RE = re.compile(r"^([0-9.]+)(px|%)$")


def _rect_area(r: dict) -> float:
    return max(0.0, float(r["w"])) * max(0.0, float(r["h"]))


def intersection_rect(a: dict, b: dict) -> dict | None:
    x1 = max(float(a["x"]), float(b["x"]))
    y1 = max(float(a["y"]), float(b["y"]))
    x2 = min(float(a["x"]) + float(a["w"]), float(b["x"]) + float(b["w"]))
    y2 = min(float(a["y"]) + float(a["h"]), float(b["y"]) + float(b["h"]))
    if x2 <= x1 or y2 <= y1:
        return None
    return {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}


def intersection_area(a: dict, b: dict) -> float:
    r = intersection_rect(a, b)
    return _rect_area(r) if r else 0.0


def union_rect(rects: list[dict]) -> dict | None:
    rects = [r for r in rects if r and _rect_area(r) > 0]
    if not rects:
        return None
    x1 = min(float(r["x"]) for r in rects)
    y1 = min(float(r["y"]) for r in rects)
    x2 = max(float(r["x"]) + float(r["w"]) for r in rects)
    y2 = max(float(r["y"]) + float(r["h"]) for r in rects)
    return {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}


def caption_hits(elements: list[dict], cap: dict | None, canvas: dict) -> list[dict]:
    """Phần tử nhìn thấy giao vùng phụ đề sâu hơn tolerance và đủ diện tích."""
    if not cap or _rect_area(cap) <= 0:
        return []
    canvas_area = _rect_area(canvas) or 1.0
    hits = []
    for el in elements:
        if el.get("in_caption"):
            continue
        if el.get("has_visual") is False:
            continue
        if el.get("uncertain"):
            continue
        if el.get("above_caption") is False:
            continue
        if float(el.get("opacity") or 0) < MIN_ELEMENT_OPACITY:
            continue
        # Tính phần nhìn thấy thật: giao với ancestor overflow và clip-path/mask
        rect = el.get("visible_rect")
        if rect is None:
            rect = el.get("rect") or {}
            if "clips" in el:
                for c in el.get("clips") or []:
                    if c.get("uncertain"):
                        el["uncertain"] = True
                        break
                    cbox = c.get("box")
                    if cbox:
                        rect = intersection_rect(rect, cbox) or {"x": 0, "y": 0, "w": 0, "h": 0}
        if el.get("uncertain"):
            continue
        if _rect_area(rect) <= 0:
            continue
        if _rect_area(rect) / canvas_area >= FRAME_WRAP_MIN_COVER:
            continue
        inter = intersection_rect(rect, cap)
        if not inter:
            continue
        area = _rect_area(inter)
        depth = min(inter["w"], inter["h"])
        if area < CAP_MIN_AREA_PX2 or depth <= CAP_TOLERANCE_PX:
            continue
        hits.append({
            "code": "caption_overlap",
            "selector": el.get("selector") or "",
            "area": round(area, 1),
            "depth": round(depth, 1),
        })
    return hits


def _axis_len(value: str, unit: str, ref_px: float) -> float:
    v = float(value)
    return v / 100.0 * ref_px if unit == "%" else v


def _parse_lengths(tokens: list[str], ref_w: float, ref_h: float) -> list[float]:
    """inset() nhận 1–4 cạnh. % theo cạnh tương ứng (trên/dưới = cao, trái/phải = rộng)."""
    nums = []
    for tok in tokens:
        m = _LEN_RE.match(tok)
        if not m:
            break
        nums.append((m.group(1), m.group(2)))
    if not nums:
        return []
    if len(nums) == 1:
        t = _axis_len(*nums[0], ref_h)
        r = _axis_len(nums[0][0], nums[0][1], ref_w)
        return [t, r, t, r]
    if len(nums) == 2:
        tb = _axis_len(*nums[0], ref_h)
        lr = _axis_len(*nums[1], ref_w)
        return [tb, lr, tb, lr]
    if len(nums) == 3:
        return [
            _axis_len(*nums[0], ref_h),
            _axis_len(*nums[1], ref_w),
            _axis_len(*nums[2], ref_h),
            _axis_len(nums[1][0], nums[1][1], ref_w),
        ]
    return [
        _axis_len(*nums[0], ref_h),
        _axis_len(*nums[1], ref_w),
        _axis_len(*nums[2], ref_h),
        _axis_len(*nums[3], ref_w),
    ]


def _shape_cover(clip: str, ref: dict, region: dict) -> float | None:
    """Phần diện tích `region` NẰM TRONG hình clip. None nếu không đọc được hình."""
    area = _rect_area(region)
    if area <= 0:
        return None
    circ = _CIRCLE_RE.search(clip or "")
    if circ:
        rw, rh = float(ref["w"]), float(ref["h"])
        # CSS: % bán kính so với sqrt((w²+h²)/2), tâm % so với cạnh hộp tham chiếu.
        radius_ref = (rw * rw + rh * rh) / 2.0
        radius_ref = radius_ref ** 0.5 if radius_ref > 0 else 1.0
        radius = _axis_len(circ.group(1), circ.group(2), radius_ref)
        if circ.group(3):
            cx = float(ref["x"]) + _axis_len(circ.group(3), circ.group(4), rw)
            cy = float(ref["y"]) + _axis_len(circ.group(5), circ.group(6), rh)
        else:
            cx = float(ref["x"]) + rw / 2.0
            cy = float(ref["y"]) + rh / 2.0
        # Lưới 4px: sai số diện tích dưới ~1% trên khung 1920×1080.
        step = 4.0
        inside = 0
        total = 0
        y = float(region["y"]) + step / 2.0
        y_end = float(region["y"]) + float(region["h"])
        x_end = float(region["x"]) + float(region["w"])
        r2 = radius * radius
        while y < y_end:
            x = float(region["x"]) + step / 2.0
            while x < x_end:
                total += 1
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= r2:
                    inside += 1
                x += step
            y += step
        if not total:
            return None
        return inside / total
    ins = _INSET_RE.search(clip or "")
    if ins:
        body = ins.group(1).split("round", 1)[0].strip()
        tokens = body.split()
        edges = _parse_lengths(tokens, float(ref["w"]), float(ref["h"]))
        if len(edges) != 4:
            return None
        top, right, bottom, left = edges
        visible = {
            "x": float(ref["x"]) + left,
            "y": float(ref["y"]) + top,
            "w": max(0.0, float(ref["w"]) - left - right),
            "h": max(0.0, float(ref["h"]) - top - bottom),
        }
        return intersection_area(visible, region) / area
    return None


def clip_hidden_fraction(clip: str, media: dict, ref: dict) -> float:
    """Phần media bị clip-path/mask giấu. 0 nếu không có hình hoặc không đọc được."""
    if not clip or str(clip).strip().lower() in ("", "none", "auto"):
        return 0.0
    region = intersection_rect(media, ref)
    if not region:
        return 0.0
    cover = _shape_cover(clip, ref, region)
    if cover is None:
        return 0.0
    return max(0.0, min(1.0, 1.0 - cover))


def circle_visible_cover(clip: str, media: dict, ref: dict) -> float | None:
    """Phần media nằm trong circle(). None nếu clip không phải hình tròn đọc được."""
    if not _CIRCLE_RE.search(clip or ""):
        return None
    region = intersection_rect(media, ref) or media
    if _rect_area(region) <= 0:
        return None
    cover = _shape_cover(clip, ref, region)
    if cover is None:
        return None
    return max(0.0, min(1.0, cover))


def _bleed_axes(rect: dict, canvas: dict) -> tuple[float, float]:
    inter = intersection_rect(rect, canvas)
    if not inter or canvas["w"] <= 0 or canvas["h"] <= 0:
        return 0.0, 0.0
    return inter["w"] / float(canvas["w"]), inter["h"] / float(canvas["h"])


def _paints_above(over: dict, media: dict) -> bool:
    if over.get("in_media"):
        return False
    if "above_orders" in over:
        return int(media.get("order") or 0) in over.get("above_orders", [])
    oz, mz = float(over.get("z") or 0), float(media.get("z") or 0)
    if oz != mz:
        return oz > mz
    return int(over.get("order") or 0) > int(media.get("order") or 0)


def occlusion_hits(elements: list[dict], canvas: dict) -> list[dict]:
    """Clip/mask hoặc lớp đặc che hơn ngưỡng một ảnh tràn khung."""
    hits = []
    for el in elements:
        if not el.get("is_media"):
            continue
        if float(el.get("opacity") or 0) < MIN_ELEMENT_OPACITY:
            continue
        rect = el.get("rect") or {}
        ax, ay = _bleed_axes(rect, canvas)
        if ax < FULLBLEED_MIN_AXIS or ay < FULLBLEED_MIN_AXIS:
            continue
        on_screen = intersection_rect(rect, canvas) or rect
        hidden = 0.0
        for c in el.get("clips") or []:
            shape = c.get("clip") or ""
            box = c.get("box") or rect
            if shape:
                hidden = max(hidden, clip_hidden_fraction(shape, on_screen, box))
        solid = 0.0
        disc = 0.0
        media_area = _rect_area(on_screen) or 1.0
        canvas_area = _rect_area(canvas) or 1.0
        for other in elements:
            if other is el or (other.get("selector") == el.get("selector") and other.get("order") == el.get("order")):
                continue
            if not _paints_above(other, el):
                continue
            # Đĩa: circle() của lớp sau phủ lên ảnh vẫn còn thấy. Vệt quét inset
            # là cảnh kế trượt vào, không tính — cùng ngưỡng 30% thì vệt đã phủ hơn đĩa.
            if float(other.get("opacity") or 0) >= MIN_ELEMENT_OPACITY:
                for c in other.get("clips") or []:
                    seen = circle_visible_cover(c.get("clip") or "", on_screen, c.get("box") or other.get("rect") or rect)
                    if seen is not None:
                        disc = max(disc, seen)
            if float(other.get("opacity") or 0) < SOLID_ALPHA_MIN:
                continue
            if float(other.get("bg_alpha") or 0) < SOLID_ALPHA_MIN:
                continue
            if other.get("uncertain"):
                continue
            orect = other.get("visible_rect") if other.get("visible_rect") is not None else (other.get("rect") or {})
            if _rect_area(orect) / canvas_area >= FRAME_WRAP_MIN_COVER:
                continue
            solid = max(solid, intersection_area(orect, on_screen) / media_area)
        cover = max(hidden, solid, disc)
        if cover <= OCCLUSION_MIN_COVER:
            continue
        hits.append({
            "code": "content_occlusion",
            "selector": el.get("selector") or "",
            "cover": round(cover, 4),
            "hidden": round(hidden, 4),
            "solid": round(solid, 4),
            "disc": round(disc, 4),
        })
    return hits


def frame_bg_and_edge(src) -> tuple[float, float]:
    """Tỉ lệ nền và mật độ cạnh của một khung.

    Nền = median luminance dải 4% trên và 4% dưới của vùng cắt. Điểm ảnh
    'có hình' lệch nền hơn 25 (sàn 50 khi nền tối). Cạnh = gradient > 12.
    """
    import numpy as np
    from PIL import Image

    im = src if isinstance(src, Image.Image) else Image.open(src)
    im = im.convert("RGB")
    w, h = im.size
    x0, y0, x1, y1 = EMPTY_CROP
    crop = im.crop((int(w * x0), int(h * y0), max(int(w * x0) + 1, int(w * x1)), max(int(h * y0) + 1, int(h * y1))))
    arr = np.asarray(crop, dtype="float32")
    lum = arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114
    ch = lum.shape[0]
    band = max(1, int(round(ch * 0.04)))
    peri = np.concatenate([lum[:band].ravel(), lum[-band:].ravel()])
    bg = float(np.median(peri))
    if bg < 128.0:
        active = lum > max(50.0, bg + 25.0)
    else:
        active = lum < (bg - 25.0)
    empty_ratio = 1.0 - float(active.mean())
    gy, gx = np.gradient(lum)
    edge = float((np.hypot(gx, gy) > 12.0).mean())
    return empty_ratio, edge


def empty_end(mid_bg: float, mid_edge: float, end_bg: float, end_edge: float) -> bool:
    """Cuối cảnh trống hơn giữa. Không có khung giữa thì không kết luận."""
    if (end_bg - mid_bg) > EMPTY_BG_DELTA and end_bg > EMPTY_BG_END:
        return True
    if end_edge < EMPTY_EDGE_END and mid_edge > EMPTY_EDGE_MID:
        return True
    return False


def handover_time(lines: list[dict], index: int) -> float | None:
    """Mốc giao cảnh sang câu kế, cùng công thức engine.js (khoảng nghỉ > 0.6s)."""
    if index < 0 or index + 1 >= len(lines):
        return None
    ln, nx = lines[index], lines[index + 1]
    if float(nx["start"]) - float(ln["end"]) > 0.6:
        return float(nx["start"]) - 0.34
    return max(float(ln["start"]) + 0.2, float(ln["end"]) - 0.34)


def scene_sample_times(lines: list[dict], duration: float) -> list[dict]:
    """Mỗi cảnh: giữa, cuối (trước fade outro), và một điểm trong lúc cảnh đang mở."""
    out = []
    guard = float(duration) - OUTRO_GUARD_S if duration else None
    for i, ln in enumerate(lines):
        start, end = float(ln["start"]), float(ln["end"])
        mid = (start + end) / 2.0
        end_t = end
        hand = handover_time(lines, i)
        if hand is not None:
            end_t = min(end_t, hand - PRE_FADE_S)
        if guard is not None:
            end_t = min(end_t, guard)
        if end_t <= start:
            end_t = mid
        samples = [
            {"scene": i, "phase": "mid", "t": round(mid, 3)},
            {"scene": i, "phase": "end", "t": round(end_t, 3)},
        ]
        if i > 0:
            t_hand = handover_time(lines, i - 1)
            if t_hand is not None:
                samples.append({"scene": i, "phase": "open", "t": round(t_hand + HANDOVER_SAMPLE_S, 3)})
        out.append({"scene": i, "start": start, "end": end, "samples": samples})
    return out


def score_sample(elements: list[dict], cap_rects: list[dict], canvas: dict) -> list[dict]:
    cap = union_rect(cap_rects or [])
    return caption_hits(elements, cap, canvas) + occlusion_hits(elements, canvas)


def score_scenes(measured: dict) -> list[dict]:
    """Ghép đo DOM + ảnh cuối/giữa thành danh sách phát hiện."""
    findings = []
    by_scene: dict[int, dict] = {}
    for sample in measured.get("samples") or []:
        scene = int(sample["scene"])
        bucket = by_scene.setdefault(scene, {})
        bucket[sample["phase"]] = sample
        for hit in score_sample(sample.get("elements") or [], sample.get("caption") or [], measured["canvas"]):
            findings.append({**hit, "scene": scene, "time": sample.get("t"), "phase": sample.get("phase")})
    for scene, bucket in by_scene.items():
        mid, end = bucket.get("mid"), bucket.get("end")
        if not mid or not end or not mid.get("shot") or not end.get("shot"):
            continue
        if abs(float(mid["t"]) - float(end["t"])) < 0.05:
            continue
        mid_bg, mid_edge = frame_bg_and_edge(mid["shot"])
        end_bg, end_edge = frame_bg_and_edge(end["shot"])
        if empty_end(mid_bg, mid_edge, end_bg, end_edge):
            findings.append({
                "code": "empty_frame",
                "scene": scene,
                "time": end.get("t"),
                "phase": "end",
                "selector": f"#scene{scene}",
                "mid_bg": round(mid_bg, 4),
                "end_bg": round(end_bg, 4),
                "mid_edge": round(mid_edge, 4),
                "end_edge": round(end_edge, 4),
            })
    return findings


def scene_summary(findings: list[dict], strict: bool = False) -> str:
    n = len(findings)
    if strict:
        head = f"QA Scenes: {'ĐẠT' if n == 0 else 'CÓ LỖI'} -- {n} lỗi, 0 cảnh báo"
    else:
        head = f"QA Scenes: {'ĐẠT' if n == 0 else 'CẢNH BÁO'} -- 0 lỗi, {n} cảnh báo"
    lines = [head]
    for f in findings:
        extra = ""
        if f["code"] == "caption_overlap":
            extra = f" diện tích {f['area']}px² sâu {f['depth']}px"
        elif f["code"] == "content_occlusion":
            extra = f" che {f['cover']:.0%}"
        elif f["code"] == "empty_frame":
            extra = f" nền {f['mid_bg']:.4f}->{f['end_bg']:.4f} cạnh {f['mid_edge']:.4f}->{f['end_edge']:.4f}"
        lines.append(f"  {'error' if strict else 'warning':7s} {f['code']} scene {f['scene']} {f.get('selector', '')} @ {f.get('time')}{extra}")
    return "\n".join(lines)


_PROBE_JS = r"""
const fs = require('fs');
const puppeteer = require(process.env.PUPPETEER_CORE);
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH,
    headless: true,
    args: ['--hide-scrollbars', '--force-device-scale-factor=1', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  const failures = [];
  page.on('pageerror', (err) => { failures.push(String(err)); console.error('PAGE', err); });
  page.on('console', (msg) => { if (msg.type() === 'error') console.error('CONSOLE', msg.text()); });
  page.on('requestfailed', (req) => console.error('REQ', req.url().slice(0, 180)));
  await page.setViewport({ width: spec.width, height: spec.height, deviceScaleFactor: 1 });
  await page.evaluateOnNewDocument((vars, w, h) => {
    window.__hyperframes = window.__hyperframes || {};
    window.__hyperframes.getVariables = () => vars;
    const style = document.createElement('style');
    style.textContent = `html,body,#root{width:${w}px !important;height:${h}px !important;overflow:hidden !important}`;
    if (document.head || document.documentElement) {
      (document.head || document.documentElement).appendChild(style);
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        (document.head || document.documentElement).appendChild(style);
      });
    }
  }, spec.variables, spec.width, spec.height);
  await page.goto(spec.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForFunction(
    () => window.__timelines && window.__timelines.main && typeof window.__timelines.main.seek === 'function',
    { timeout: 30000 },
  );
  try { await page.evaluate(() => document.fonts && document.fonts.ready); } catch (e) {}
  const samples = [];
  for (const sample of spec.samples) {
    await page.evaluate((t) => {
      const timelines = window.__timelines || {};
      Object.keys(timelines).forEach((key) => {
        const tl = timelines[key];
        if (!tl) return;
        if (typeof tl.pause === 'function') tl.pause();
        if (typeof tl.seek === 'function') tl.seek(t);
      });
      if (window.gsap && window.gsap.ticker && typeof window.gsap.ticker.tick === 'function') {
        window.gsap.ticker.tick();
      }
    }, sample.t);
    await new Promise((r) => setTimeout(r, 40));
    const dom = await page.evaluate(() => {
      function selectorOf(el) {
        if (!el || el.nodeType !== 1) return '';
        if (el.id) return '#' + CSS.escape(el.id);
        const tag = el.tagName.toLowerCase();
        const cls = Array.from(el.classList).slice(0, 4).map((c) => '.' + CSS.escape(c)).join('');
        return tag + cls;
      }
      const root = document.getElementById('root');
      const rb = root.getBoundingClientRect();
      const canvas = { x: rb.x, y: rb.y, w: rb.width, h: rb.height };
      const capRoot = document.getElementById('capzone');

      function toBox(r) {
        if (!r) return null;
        const x = r.x != null ? r.x : (r.left != null ? r.left : 0);
        const y = r.y != null ? r.y : (r.top != null ? r.top : 0);
        const w = r.w != null ? r.w : (r.width != null ? r.width : 0);
        const h = r.h != null ? r.h : (r.height != null ? r.height : 0);
        return { x, y, w, h };
      }

      function intersectBox(a, b) {
        const ba = toBox(a);
        const bb = toBox(b);
        if (!ba || !bb) return null;
        const x1 = Math.max(ba.x, bb.x);
        const y1 = Math.max(ba.y, bb.y);
        const x2 = Math.min(ba.x + ba.w, bb.x + bb.w);
        const y2 = Math.min(ba.y + ba.h, bb.y + bb.h);
        if (x2 <= x1 || y2 <= y1) return null;
        return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
      }

      function unionBox(rects) {
        if (!rects || !rects.length) return null;
        let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
        for (const raw of rects) {
          const r = toBox(raw);
          if (!r || r.w <= 0 || r.h <= 0) continue;
          x1 = Math.min(x1, r.x);
          y1 = Math.min(y1, r.y);
          x2 = Math.max(x2, r.x + r.w);
          y2 = Math.max(y2, r.y + r.h);
        }
        if (x2 <= x1 || y2 <= y1) return null;
        return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
      }

      function parseLength(tok, refPx) {
        if (!tok) return 0;
        const m = String(tok).trim().match(/^([0-9.]+)(px|%)?$/);
        if (!m) return 0;
        const val = parseFloat(m[1]);
        return m[2] === '%' ? (val / 100 * refPx) : val;
      }

      function parseClipBox(cp, ref) {
        if (!cp || cp === 'none') return null;
        const ins = cp.match(/inset\(\s*([^)]*)\)/i);
        if (ins) {
          const body = ins[1].split('round')[0].trim();
          const tokens = body.split(/\s+/).filter(Boolean);
          let t = 0, r = 0, b = 0, l = 0;
          if (tokens.length === 1) {
            t = b = parseLength(tokens[0], ref.height);
            r = l = parseLength(tokens[0], ref.width);
          } else if (tokens.length === 2) {
            t = b = parseLength(tokens[0], ref.height);
            r = l = parseLength(tokens[1], ref.width);
          } else if (tokens.length === 3) {
            t = parseLength(tokens[0], ref.height);
            r = l = parseLength(tokens[1], ref.width);
            b = parseLength(tokens[2], ref.height);
          } else if (tokens.length >= 4) {
            t = parseLength(tokens[0], ref.height);
            r = parseLength(tokens[1], ref.width);
            b = parseLength(tokens[2], ref.height);
            l = parseLength(tokens[3], ref.width);
          }
          return {
            x: ref.x + l,
            y: ref.y + t,
            w: Math.max(0, ref.width - l - r),
            h: Math.max(0, ref.height - t - b),
          };
        }
        const circ = cp.match(/circle\(\s*([0-9.]+)(px|%)(?:\s+at\s+([0-9.]+)(px|%)\s+([0-9.]+)(px|%))?\s*\)/i);
        if (circ) {
          const diag = Math.sqrt((ref.width * ref.width + ref.height * ref.height) / 2) || 1;
          const rad = circ[2] === '%' ? (parseFloat(circ[1]) / 100 * diag) : parseFloat(circ[1]);
          let cx = ref.x + ref.width / 2;
          let cy = ref.y + ref.height / 2;
          if (circ[3]) {
            cx = ref.x + (circ[4] === '%' ? (parseFloat(circ[3]) / 100 * ref.width) : parseFloat(circ[3]));
            cy = ref.y + (circ[6] === '%' ? (parseFloat(circ[5]) / 100 * ref.height) : parseFloat(circ[5]));
          }
          return {
            x: cx - rad,
            y: cy - rad,
            w: rad * 2,
            h: rad * 2,
          };
        }
        return null;
      }

      function parseMaskBox(cs, ref) {
        const maskImg = (cs.maskImage && cs.maskImage !== 'none' ? cs.maskImage : '') ||
                        (cs.webkitMaskImage && cs.webkitMaskImage !== 'none' ? cs.webkitMaskImage : '');
        const maskVal = maskImg || (cs.mask && cs.mask !== 'none' ? cs.mask : '') ||
                        (cs.webkitMask && cs.webkitMask !== 'none' ? cs.webkitMask : '');
        if (!maskVal) return { box: null, hasMask: false, uncertain: false };
        const maskSize = cs.maskSize || cs.webkitMaskSize || '';
        const mSize = maskSize.trim().match(/^([0-9.]+)(px|%)\s+([0-9.]+)(px|%)$/);
        if (mSize) {
          const mw = mSize[2] === '%' ? (parseFloat(mSize[1]) / 100 * ref.width) : parseFloat(mSize[1]);
          const mh = mSize[4] === '%' ? (parseFloat(mSize[3]) / 100 * ref.height) : parseFloat(mSize[3]);
          return { box: { x: ref.x, y: ref.y, w: mw, h: mh }, hasMask: true, uncertain: false };
        }
        return { box: null, hasMask: true, uncertain: true };
      }

      function computeVisibleRect(el) {
        const b = el.getBoundingClientRect();
        let x1 = b.x, y1 = b.y, x2 = b.x + b.width, y2 = b.y + b.height;
        let uncertain = false;

        let n = el;
        while (n && n.nodeType === 1) {
          const cs = getComputedStyle(n);
          if (n !== el) {
            const ox = cs.overflowX || cs.overflow || '';
            const oy = cs.overflowY || cs.overflow || '';
            const clipsX = (ox === 'hidden' || ox === 'clip' || ox === 'scroll' || ox === 'auto');
            const clipsY = (oy === 'hidden' || oy === 'clip' || oy === 'scroll' || oy === 'auto');
            if (clipsX || clipsY) {
              const pb = n.getBoundingClientRect();
              if (clipsX) {
                x1 = Math.max(x1, pb.x);
                x2 = Math.min(x2, pb.x + pb.width);
              }
              if (clipsY) {
                y1 = Math.max(y1, pb.y);
                y2 = Math.min(y2, pb.y + pb.height);
              }
            }
          }

          const cp = cs.clipPath && cs.clipPath !== 'none' ? cs.clipPath : '';
          if (cp) {
            const nb = n.getBoundingClientRect();
            const clipBox = parseClipBox(cp, nb);
            if (clipBox) {
              x1 = Math.max(x1, clipBox.x);
              y1 = Math.max(y1, clipBox.y);
              x2 = Math.min(x2, clipBox.x + clipBox.w);
              y2 = Math.min(y2, clipBox.y + clipBox.h);
            }
          }

          const maskInfo = parseMaskBox(cs, n.getBoundingClientRect());
          if (maskInfo.hasMask) {
            if (maskInfo.box) {
              x1 = Math.max(x1, maskInfo.box.x);
              y1 = Math.max(y1, maskInfo.box.y);
              x2 = Math.min(x2, maskInfo.box.x + maskInfo.box.w);
              y2 = Math.min(y2, maskInfo.box.y + maskInfo.box.h);
            }
            if (maskInfo.uncertain) {
              uncertain = true;
            }
          }

          if (n.id === 'root') break;
          n = n.parentElement;
        }

        if (x2 <= x1 || y2 <= y1) {
          return { rect: { x: 0, y: 0, w: 0, h: 0 }, uncertain };
        }
        return { rect: { x: x1, y: y1, w: x2 - x1, h: y2 - y1 }, uncertain };
      }

      function testPaintsAbove(elA, elB, inter) {
        const box = toBox(inter);
        if (!box || box.w < 1 || box.h < 1) return false;
        const xs = [0.25, 0.5, 0.75].map((f) => box.x + box.w * f);
        const ys = [0.25, 0.5, 0.75].map((f) => box.y + box.h * f);
        let aAboveB = 0;
        let bAboveA = 0;
        for (const x of xs) {
          for (const y of ys) {
            const stack = document.elementsFromPoint(x, y);
            const idxA = stack.findIndex((e) => e === elA || elA.contains(e));
            const idxB = stack.findIndex((e) => e === elB || elB.contains(e));
            if (idxA !== -1 && idxB !== -1) {
              if (idxA < idxB) aAboveB++;
              else if (idxB < idxA) bAboveA++;
            } else if (idxA !== -1 && idxB === -1) {
              aAboveB++;
            } else if (idxB !== -1 && idxA === -1) {
              bAboveA++;
            }
          }
        }
        return aAboveB >= bAboveA;
      }

      function composedOpacity(el) {
        let o = 1;
        let n = el;
        while (n && n.nodeType === 1) {
          const cs = getComputedStyle(n);
          if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
          o *= parseFloat(cs.opacity || '1');
          if (n.id === 'root') break;
          n = n.parentElement;
        }
        return o;
      }

      function clipsOf(el) {
        const clips = [];
        let n = el;
        while (n && n.nodeType === 1) {
          const cs = getComputedStyle(n);
          const cp = cs.clipPath && cs.clipPath !== 'none' ? cs.clipPath : '';
          const b = n.getBoundingClientRect();
          if (cp) {
            clips.push({ clip: cp, box: { x: b.x, y: b.y, w: b.width, h: b.height } });
          }
          const maskInfo = parseMaskBox(cs, b);
          if (maskInfo.hasMask) {
            clips.push({
              mask: cs.mask || cs.webkitMask || cs.maskImage || cs.webkitMaskImage || 'mask',
              box: maskInfo.box || { x: b.x, y: b.y, w: b.width, h: b.height },
              uncertain: maskInfo.uncertain,
            });
          }
          if (n.id === 'root') break;
          n = n.parentElement;
        }
        return clips;
      }

      const elements = [];
      const caption = [];
      const domNodes = [];
      let order = 0;
      const all = root.querySelectorAll('*');
      all.forEach((el) => {
        order += 1;
        const tag = el.tagName.toLowerCase();
        if (tag === 'script' || tag === 'style' || tag === 'br') return;
        const b = el.getBoundingClientRect();
        if (b.width < 1 || b.height < 1) return;
        const opacity = composedOpacity(el);
        if (opacity <= 0.02) return;
        const cs = getComputedStyle(el);
        const inCaption = !!(capRoot && capRoot.contains(el));
        const bg = cs.backgroundColor || '';
        const m = bg.match(/rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+(?:\s*,\s*([\d.]+))?\s*\)/);
        const bgAlpha = m ? (m[1] == null ? 1 : parseFloat(m[1])) : 0;
        // Gradient (linear/radial/conic) không phải ảnh. Chỉ url() hoặc thẻ img/video.
        const bgUrl = cs.backgroundImage && /url\(/i.test(cs.backgroundImage);
        const isMedia = tag === 'img' || tag === 'video' || bgUrl;
        const clips = clipsOf(el);
        const visInfo = computeVisibleRect(el);
        const hasText = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim().length > 0);
        const svgFill = cs.fill || el.getAttribute('fill') || '';
        const hasSvgFill = svgFill !== 'none' && svgFill !== 'transparent' && svgFill !== 'rgba(0, 0, 0, 0)';
        const isGraphic = tag === 'img' || tag === 'video' || tag === 'canvas' || tag === 'text' ||
                          ((tag === 'path' || tag === 'circle' || tag === 'rect' || tag === 'polygon') && hasSvgFill);
        const hasVisual = isMedia || bgAlpha >= 0.05 || hasText || isGraphic;
        const rec = {
          selector: selectorOf(el),
          rect: { x: b.x, y: b.y, w: b.width, h: b.height },
          visible_rect: visInfo.rect,
          uncertain: visInfo.uncertain,
          above_caption: null,
          above_orders: [],
          has_visual: hasVisual,
          opacity,
          z: parseFloat(cs.zIndex) || 0,
          order,
          in_caption: inCaption,
          is_media: isMedia,
          bg_alpha: Number.isFinite(bgAlpha) ? bgAlpha : 0,
          clips,
        };
        if (inCaption) caption.push(rec.rect);
        if (inCaption || b.width * b.height >= 50) {
          elements.push(rec);
          domNodes.push(el);
        }
      });

      // Kiểm tra thứ tự đè lớp bằng elementsFromPoint (xét stacking context)
      const probePe = document.createElement('style');
      probePe.textContent = '* { pointer-events: auto !important; }';
      (document.head || document.documentElement).appendChild(probePe);

      const mediaIndices = [];
      for (let i = 0; i < elements.length; i++) {
        if (elements[i].is_media) mediaIndices.push(i);
      }
      for (const mIdx of mediaIndices) {
        const mRec = elements[mIdx];
        const mEl = domNodes[mIdx];
        if (!mEl || !mRec.visible_rect || mRec.visible_rect.w <= 0 || mRec.visible_rect.h <= 0) continue;
        for (let j = 0; j < elements.length; j++) {
          if (j === mIdx) continue;
          const oRec = elements[j];
          if (!oRec.visible_rect || oRec.visible_rect.w <= 0 || oRec.visible_rect.h <= 0) continue;
          const oEl = domNodes[j];
          if (!oEl) continue;
          if (oEl.contains(mEl) || mEl.contains(oEl)) continue;
          const inter = intersectBox(oRec.visible_rect, mRec.visible_rect);
          if (!inter || inter.w < 2 || inter.h < 2) continue;
          if (testPaintsAbove(oEl, mEl, inter)) {
            oRec.above_orders.push(mRec.order);
          }
        }
      }

      // Soát đè phụ đề: nếu phụ đề có thẻ nền đặc (như .cap trong skin-studio) và thẻ nằm trên el
      const capPlates = Array.from(root.querySelectorAll('#capzone .cap, .cap, #cap'));
      if (capPlates.length > 0) {
        for (let i = 0; i < elements.length; i++) {
          const rec = elements[i];
          if (rec.in_caption || !rec.visible_rect || rec.visible_rect.w <= 0 || rec.visible_rect.h <= 0) continue;
          const el = domNodes[i];
          if (!el) continue;
          for (const plate of capPlates) {
            const plateBox = toBox(plate.getBoundingClientRect());
            const inter = intersectBox(rec.visible_rect, plateBox);
            if (!inter || inter.w < 2 || inter.h < 2) continue;
            const csPlate = getComputedStyle(plate);
            const m = (csPlate.backgroundColor || '').match(/rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+(?:\s*,\s*([\d.]+))?\s*\)/);
            const plateAlpha = m ? (m[1] == null ? 1 : parseFloat(m[1])) : 0;
            const hasSolidPlate = plateAlpha >= 0.8 && parseFloat(csPlate.opacity || '1') >= 0.8;
            const xs = [0.25, 0.5, 0.75].map((f) => inter.x + inter.w * f);
            const ys = [0.25, 0.5, 0.75].map((f) => inter.y + inter.h * f);
            let plateAboveEl = 0;
            let elAbovePlate = 0;
            for (const x of xs) {
              for (const y of ys) {
                const stack = document.elementsFromPoint(x, y);
                const idxEl = stack.findIndex((e) => e === el || el.contains(e));
                const idxPlate = stack.findIndex((e) => e === plate || plate.contains(e));
                if (idxEl !== -1 && idxPlate !== -1) {
                  if (idxEl < idxPlate) elAbovePlate++;
                  else if (idxPlate < idxEl) plateAboveEl++;
                }
              }
            }
            if (hasSolidPlate && plateAboveEl > elAbovePlate) {
              rec.above_caption = false;
            } else if (elAbovePlate > plateAboveEl) {
              rec.above_caption = true;
            }
          }
        }
      }

      probePe.remove();
      return { canvas, elements, caption };
    });
    let shot = null;
    if (sample.shot) {
      await page.screenshot({ path: sample.shot, clip: { x: 0, y: 0, width: spec.width, height: spec.height } });
      shot = sample.shot;
    }
    samples.push({ scene: sample.scene, phase: sample.phase, t: sample.t, shot, ...dom });
  }
  await browser.close();
  fs.writeFileSync(spec.out, JSON.stringify({ ok: true, failures, canvas: samples[0] && samples[0].canvas, samples }));
  process.exit(0);
})().catch((err) => {
  console.error(err && err.stack || err);
  process.exit(1);
});
"""


def _chrome_path() -> str:
    env_p = os.environ.get("HYPERFRAMES_BROWSER_PATH")
    if env_p and Path(env_p).is_file():
        return env_p
    if sys.platform == "darwin":
        mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if Path(mac).is_file():
            return mac
    found = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
    if not found:
        raise RuntimeError("Không thấy Chrome để đo trang")
    return found


def _puppeteer_core() -> str:
    home = Path.home()
    hits = sorted(home.glob(".npm/_npx/*/node_modules/puppeteer-core/package.json"))
    if not hits:
        raise RuntimeError("Không thấy puppeteer-core trong cache npx của hyperframes")
    return str(hits[-1].parent)


class _QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        # Bỏ qua BrokenPipeError / ConnectionReset khi browser đóng socket sớm
        pass


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return


def measure_scenes(index_html: Path, vars_path: Path, *, compositions: Path | None = None,
                   project_dir: Path | None = None) -> dict:
    """Dựng project tạm, seek timeline, đọc bbox + clip-path + ảnh khung.

    Seek cùng chuỗi hyperframes check dùng (cli.js seekCompositionTimeline ~130783):
    pause + seek trên window.__timelines rồi gsap.ticker.tick().
    """
    index_html = Path(index_html)
    variables = json.loads(Path(vars_path).read_text(encoding="utf-8"))
    lines = variables.get("lines")
    if isinstance(lines, str):
        lines = json.loads(lines or "[]")
    duration = float(variables.get("duration") or (lines[-1]["end"] if lines else 0))
    plan = scene_sample_times(lines, duration)
    samples = [s for row in plan for s in row["samples"]]
    proj = Path(project_dir) if project_dir else QA_DIR / f"scenes_{index_html.stem}"
    if not proj.exists():
        proj.mkdir(parents=True)
    comp_link = proj / "compositions"
    asset_link = proj / "assets"
    comp_target = (Path(compositions) if compositions else (HF_PROJECT / "compositions")).resolve()
    if not comp_link.exists():
        comp_link.symlink_to(comp_target)
    if not asset_link.exists() and (HF_PROJECT / "assets").exists():
        asset_link.symlink_to((HF_PROJECT / "assets").resolve())
    studio_link = proj / "studio"
    studio_src = (HF_PROJECT / "studio").resolve()
    if studio_src.is_dir() and not studio_link.exists():
        studio_link.symlink_to(studio_src)
    baked = _bake(index_html.read_text(encoding="utf-8"), variables)
    # Composition gốc nằm trong compositions/ nên trỏ ../studio. index.html của
    # project tạm nằm ở gốc, nên đưa studio lên cùng cấp.
    baked = baked.replace("../studio/", "studio/")
    # data-duration để trang đúng độ dài; engine đọc duration từ biến.
    baked = baked.replace('data-duration="30"', f'data-duration="{duration}"', 1)
    (proj / "index.html").write_text(baked, encoding="utf-8")
    shot_dir = proj / "shots"
    shot_dir.mkdir(exist_ok=True)
    for s in samples:
        if s["phase"] in ("mid", "end"):
            s["shot"] = str(shot_dir / f"s{s['scene']}_{s['phase']}.png")
    spec_path = proj / "probe_spec.json"
    out_path = proj / "probe_out.json"
    spec_path.write_text(json.dumps({
        "url": "http://127.0.0.1:8765/index.html",
        "variables": variables,
        "width": 1920,
        "height": 1080,
        "samples": samples,
        "out": str(out_path),
    }, ensure_ascii=False), encoding="utf-8")
    probe = proj / "dom_probe.cjs"
    probe.write_text(_PROBE_JS, encoding="utf-8")

    class _Handler(_QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(proj), **kwargs)

    server = _QuietServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    import threading
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["url"] = f"http://127.0.0.1:{port}/index.html"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    try:
        cmd = (
            'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; '
            'nvm use 22 >/dev/null 2>&1 || exit 97; '
            f'PUPPETEER_CORE={_puppeteer_core()!r} CHROME_PATH={_chrome_path()!r} '
            f'node {probe.as_posix()!r} {spec_path.as_posix()!r}'
        )
        res = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=900)
        if res.returncode != 0 or not out_path.is_file():
            raise RuntimeError((res.stderr or res.stdout or "probe fail")[-2000:])
        measured = json.loads(out_path.read_text(encoding="utf-8"))
        measured["lines"] = lines
        measured["duration"] = duration
        return measured
    finally:
        server.shutdown()
        server.server_close()


def audit_scenes(index_html: Path, vars_path: Path, *, compositions: Path | None = None,
                 project_dir: Path | None = None, strict: bool = False) -> dict:
    measured = measure_scenes(index_html, vars_path, compositions=compositions, project_dir=project_dir)
    findings = score_scenes(measured)
    return {"ok": True, "strict": strict, "findings": findings, "summary": scene_summary(findings, strict),
            "failures": measured.get("failures") or [], "canvas": measured.get("canvas")}


def _cli_scenes(argv: list[str]) -> int:
    strict = "--strict" in argv
    args = [a for a in argv if a != "--strict"]
    comp_dir = None
    if "--compositions" in args:
        i = args.index("--compositions")
        comp_dir = Path(args[i + 1])
        del args[i:i + 2]
    if len(args) < 2:
        print("thiếu html và vars", file=sys.stderr)
        return 2
    rep = audit_scenes(Path(args[0]), Path(args[1]), compositions=comp_dir, strict=strict)
    print(rep["summary"])
    for fail in rep["failures"][:5]:
        print("  pageerror " + str(fail)[:200])
    return 1 if strict and rep["findings"] else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--overflow", "--contrast"):
        gate, bad_word = (gate_overflow, "TRÀN") if sys.argv[1] == "--overflow" else (gate_contrast, "TƯƠNG PHẢN KÉM")
        bad = 0
        for f in sys.argv[2:]:
            issues = gate(Path(f))
            print(f"{Path(f).name}: {'ĐẠT' if not issues else bad_word}")
            for ln in issues:
                print("  " + ln)
            bad += bool(issues)
        sys.exit(1 if bad else 0)
    if len(sys.argv) > 1 and sys.argv[1] == "--scenes":
        sys.exit(_cli_scenes(sys.argv[2:]))
    t = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    rep = run(Path(sys.argv[1]), Path(sys.argv[2]), t)
    print(summarize(rep))
