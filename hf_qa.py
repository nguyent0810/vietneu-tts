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


def run(comp_path: Path, vars_path: Path, times: list[float] | None = None) -> dict:
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
    variables = json.loads(vars_path.read_text(encoding="utf-8"))
    (proj / "index.html").write_text(_bake(comp_path.read_text(encoding="utf-8"), variables), encoding="utf-8")
    at = f" --at {','.join(f'{t:.2f}' for t in times)}" if times else ""
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


if __name__ == "__main__":
    t = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    rep = run(Path(sys.argv[1]), Path(sys.argv[2]), t)
    print(summarize(rep))
