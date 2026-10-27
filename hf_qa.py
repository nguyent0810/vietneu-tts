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
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
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
    t = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    rep = run(Path(sys.argv[1]), Path(sys.argv[2]), t)
    print(summarize(rep))
