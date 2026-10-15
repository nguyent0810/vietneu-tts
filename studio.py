"""HFS -- HyperFrames Shorts Studio: dựng short dọc có lời đọc cho MỌI kênh từ một file spec JSON.

    python studio.py devices                       # liệt kê thiết bị + metadata
    python studio.py themes                        # liệt kê theme
    python studio.py fonts                         # tải woff2 (có tiếng Việt) cho mọi theme -> render không cần mạng
    python studio.py build spec.json [--render] [--qa] [--strict] [--no-ledger]

Spec (xem .claude/skills/shorts-studio/references/spec.md):
    {"id","channel","theme","kicker","lines":[...],"scenes":[{"device","line",...}],
     "voice":{"wav","manifest"} | "tts":true, "loop":true, "out":"output/..."}
Mốc thời gian trong scene: [câu, "từ", lần] hoặc [câu, tỉ_lệ] hoặc số giây -> builder đổi ra GIÂY (thiếu -> dừng).
Mỗi cảnh thành <section class="clip scene" data-start data-duration> (runtime tự ẩn/hiện); engine inline + đóng dấu phiên bản.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HF = ROOT / "hyperframes_short"
ST = HF / "studio"
JOBS = HF / "jobs"
NODE = 'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1; export PRODUCER_BROWSER_GPU_MODE=hardware; '
HFV = "hyperframes@0.8.75"

# metadata thiết bị (khớp `meta` trong studio/devices/*.js) -- dùng cho luật đa dạng
DEVICES = {
    "hook_poster": dict(purpose="hook", framing="edge-band", axis="static", circle=0),
    "hook_slam":   dict(purpose="hook", framing="edge-band", axis="Z", circle=0),
    "split":       dict(purpose="compare", framing="stacked-split", axis="mask", circle=0),
    "myth_strike": dict(purpose="compare", framing="center-hero", axis="X", circle=0),
    "window":      dict(purpose="statement", framing="center-hero", axis="in-glyph", circle=0),
    "wheel":       dict(purpose="process", framing="center-hero", axis="3D", circle=1),
    "cycle_draw":  dict(purpose="process", framing="center-hero", axis="draw", circle=1),
    "calendar":    dict(purpose="time", framing="card-on-field", axis="3D", circle=0),
    "time_spine":  dict(purpose="time", framing="world-camera", axis="draw", circle=0),
    "stamp":       dict(purpose="statement", framing="edge-band", axis="X", circle=0),
    "source_card": dict(purpose="evidence", framing="card-on-field", axis="Y", circle=0),
    "ledger":      dict(purpose="list", framing="grid", axis="Y", circle=0),
    "list_build":  dict(purpose="list", framing="grid", axis="X", circle=0),
    "quote":       dict(purpose="quote", framing="center-hero", axis="in-glyph", circle=0),
    "close":       dict(purpose="close", framing="edge-band", axis="mask", circle=0),
    "pan_tour":    dict(purpose="evidence", framing="full-bleed", axis="camera", circle=0),
    "count_ring":  dict(purpose="number", framing="center-hero", axis="count", circle=1),
    "bars":        dict(purpose="number", framing="grid", axis="X", circle=0),
    "unit_grid":   dict(purpose="number", framing="grid", axis="Z", circle=0),
}
STAMP_KEYS = ("stampAt", "sealAt", "strikeAt")
LAND_KEYS = ("at", "litAt", "diffAt", "valueAt")


def engine_version() -> str:
    h = hashlib.sha1()
    for p in sorted([ST / "core.js", ST / "base.css", ST / "kit.css", *(ST / "devices").glob("*.js")]):
        h.update(p.read_bytes())
    return h.hexdigest()[:10]


def theme(tid: str) -> dict:
    return json.loads((ST / "themes" / f"{tid}.json").read_text(encoding="utf-8"))


# ---------------- thời gian từng từ ----------------
def line_words(wav: Path, segs: list[dict], lines: list[str]) -> list[dict]:
    import hf_align as A  # noqa: PLC0415
    env, hop = A.energy_envelope(wav)
    out = []
    for sg, text in zip(segs, lines):
        toks = text.split()
        ws = A.word_times(env, hop, sg["start"], sg["end"], [A.token_weight(t.replace("**", "")) for t in toks])
        out.append({"text": text, "start": round(sg["start"], 3), "end": round(sg["end"], 3),
                    "words": [{"w": t, "t": round(a, 3), "d": round(d, 3)} for t, (a, d) in zip(toks, ws)]})
    return out


def _norm(s: str) -> str:
    return re.sub(r"[^\w]", "", s.replace("**", "").lower(), flags=re.UNICODE)


def resolve(a, L, where):
    """[câu, "từ", lần] | [câu, tỉ lệ] | số -> giây. Thiếu từ -> lỗi (không âm thầm rơi về đầu câu)."""
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return float(a)
    i, w, *n = a
    ln = L[i]
    if isinstance(w, float) or (isinstance(w, int) and not isinstance(w, bool) and len(a) == 2 and w in (0, 1)):
        return round(ln["start"] + (ln["end"] - ln["start"]) * float(w), 3)
    k, want = 0, (n[0] if n else 1)
    for x in ln["words"]:
        if _norm(x["w"]).startswith(_norm(str(w))):
            k += 1
            if k == want:
                return x["t"]
    raise SystemExit(f"[spec] {where}: không thấy từ '{w}' (lần {want}) trong câu {i}: {ln['text']}")


def is_anchor(v, nlines):
    return (isinstance(v, list) and len(v) in (2, 3) and isinstance(v[0], int) and not isinstance(v[0], bool) and 0 <= v[0] < nlines
            and (isinstance(v[1], str) or isinstance(v[1], float) or (len(v) == 2 and v[1] in (0, 1))))


def resolve_tree(node, L, path="scene"):
    if isinstance(node, dict):
        return {k: (resolve(v, L, f"{path}.{k}") if is_anchor(v, len(L)) else resolve_tree(v, L, f"{path}.{k}")) for k, v in node.items()}
    if isinstance(node, list):
        return [resolve(v, L, f"{path}[{i}]") if is_anchor(v, len(L)) else resolve_tree(v, L, f"{path}[{i}]") for i, v in enumerate(node)]
    return node


# ---------------- luật đa dạng + sổ kênh ----------------
def variety(scenes: list[dict], channel: str, use_ledger: bool) -> list[str]:
    warn = []
    devs = [s["device"] for s in scenes]
    for d in devs:
        if d not in DEVICES:
            raise SystemExit(f"[spec] thiết bị không có: {d} (python studio.py devices)")
    fr = [DEVICES[d]["framing"] for d in devs]
    if len(set(fr)) < 3:
        warn.append(f"chỉ {len(set(fr))} khung khác nhau (cần >= 3): {fr}")
    for i in range(1, len(devs)):
        if fr[i] == fr[i - 1]:
            warn.append(f"cảnh {i - 1}->{i} cùng khung '{fr[i]}' ({devs[i - 1]} -> {devs[i]})")
        if DEVICES[devs[i]]["axis"] == DEVICES[devs[i - 1]]["axis"] and DEVICES[devs[i]]["axis"] != "static":
            warn.append(f"cảnh {i - 1}->{i} cùng trục chuyển động '{DEVICES[devs[i]]['axis']}'")
    if sum(DEVICES[d]["circle"] for d in devs) > 1:
        warn.append("quá 1 cơ chế tròn trong video (wheel/cycle_draw/count_ring)")
    if DEVICES[devs[0]]["purpose"] != "hook":
        warn.append(f"cảnh 0 nên là thiết bị móc (hook_*), đang là {devs[0]}")
    if use_ledger:
        led = ledger(channel)
        recent = led[-3:]
        if any(v.get("hook") == devs[0] for v in recent):
            warn.append(f"móc '{devs[0]}' đã dùng trong 3 video gần nhất của kênh {channel}")
    return warn


def ledger_path(channel: str) -> Path:
    return ROOT / "output" / "cl_staging" / channel / "studio_ledger.json"


def ledger(channel: str) -> list[dict]:
    p = ledger_path(channel)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def ledger_add(channel: str, rec: dict) -> None:
    p = ledger_path(channel)
    p.parent.mkdir(parents=True, exist_ok=True)
    led = [r for r in ledger(channel) if r["id"] != rec["id"]] + [rec]
    p.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------- dựng HTML ----------------
def font_faces(th: dict, job: Path | None, url_prefix: str | None = None) -> str:
    """@font-face cục bộ (woff2 có subset vietnamese, studio/fonts) cho đúng các họ font theme dùng -> render không cần mạng.
    Họ không có file (font hệ thống, vd CJK) -> local() để lint không báo font_family_without_font_face."""
    fams = set()
    for k, v in th["vars"].items():
        if k.startswith("font-"):
            fams |= set(re.findall(r'"([^"]+)"', v))
    faces = json.loads((ST / "fonts" / "faces.json").read_text(encoding="utf-8"))
    out, have = [], set()
    for f in faces:
        if f["family"] in fams:
            src = ST / f["file"]
            if url_prefix is not None:     # video dài: trỏ thẳng vào studio/fonts (cùng dự án HyperFrames), không chép
                out.append(f["css"].replace(f["file"], f"{url_prefix}/{f['file']}"))
                have.add(f["family"])
                continue
            dst = job / "assets" / "fonts" / src.parent.name / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                shutil.copy(src, dst)
            out.append(f["css"].replace(f["file"], f"assets/fonts/{src.parent.name}/{src.name}"))
            have.add(f["family"])
    out += [f'@font-face {{ font-family: "{x}"; src: local("{x}"); }}' for x in sorted(fams - have)]
    return "\n".join(out)


def compose(spec: dict, th: dict, lines: list[dict], dur: float, windows: list[tuple[float, float]], scenes: list[dict], job: Path) -> str:
    root_vars = ";".join(f"--{k}:{v}" for k, v in th["vars"].items())
    css = (ST / "base.css").read_text(encoding="utf-8") + (ST / "kit.css").read_text(encoding="utf-8")
    js = (ST / "core.js").read_text(encoding="utf-8") + "\n" + "\n".join(p.read_text(encoding="utf-8") for p in sorted((ST / "devices").glob("*.js")))
    data = {"engine": engine_version(), "dur": dur, "kicker": spec.get("kicker", ""), "lines": lines, "scenes": scenes,
            "motion": th["motion"], "seam": spec.get("seam", th.get("seam", "curve")), "capGroup": spec.get("capGroup", 5)}
    secs = "\n".join(f'  <section id="s{i}" class="clip scene" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="1" data-device="{s["device"]}"><div class="stage"></div></section>'
                     for i, ((a, b), s) in enumerate(zip(windows, scenes)))
    foot = spec.get("foot", th.get("foot", ""))
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<meta name="hfs-engine" content="{data['engine']}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
:root {{{root_vars}}}
{font_faces(th, job)}
{css}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="bg" data-layout-ignore><div id="bloom"></div>
    <svg id="grain" width="1080" height="1920"><filter id="gn"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 .1  0 0 0 0 .08  0 0 0 0 .06  0 0 0 .55 0"/></filter><rect width="100%" height="100%" filter="url(#gn)"/></svg>
    <div id="ghost"></div></div>
{secs}
  <div id="chrome"><div id="topbar"></div><div id="kicker"><i></i><span id="kick"></span></div><div id="foot">{foot}</div></div>
  <div id="cap"></div>
</div>
<script>
{js}
HFS.run({json.dumps(data, ensure_ascii=False)});
</script>
</body>
</html>
"""


def sfx_events(spec_scenes, windows, th, dur):
    sx = th["sfx"]
    ev = [(0.0, sx["open"][0], sx["open"][1]), (0.0, sx["open"][2], sx["open"][3])]
    for i, (s, (a, _b)) in enumerate(zip(spec_scenes, windows)):
        if i:
            ev.append((max(0, a - .3), sx["seam"], .35))
        def walk(n, key=""):
            if isinstance(n, dict):
                for k, v in n.items():
                    walk(v, k)
            elif isinstance(n, list):
                for v in n:
                    walk(v, key)
            elif isinstance(n, (int, float)) and not isinstance(n, bool):
                if key in STAMP_KEYS:
                    ev.append((float(n), sx["stamp"], .8))
                elif key == "flips":
                    ev.append((float(n) - .1, "paper", .7))
        walk(s)
        for st in s.get("stamps", []):
            ev.append((float(st["at"]), sx["stamp"], .85))
        if s["device"] == "wheel":
            for j in range(14):
                ev.append((a + 1.9 * (1 - (1 - (j + 1) / 14) ** .5), sx["tick"], .22))
            ev.append((a + 1.75, sx["stamp"], .6))
        if s["device"] in ("count_ring", "bars", "unit_grid", "ledger"):
            for k in LAND_KEYS:
                if isinstance(s.get(k), (int, float)):
                    ev.append((float(s[k]) + 1.3, sx["land"], .45))
    return [(t, n, g) for t, n, g in ev if 0 <= t < dur]


def mix_audio(job: Path, silent: Path, wav: Path, events, th, dur, out: Path, rid: str):
    import hf_music, hf_sfx  # noqa: E401, PLC0415
    mix = hf_sfx.Mix(dur, 11)
    p = mix.p
    make = {"bell": p.bell, "bowl": p.bowl, "chime": p.chime, "gong": p.gong, "woodblock": p.woodblock, "tick": p.tick,
            "whoosh": p.whoosh, "brush": p.brush, "paper": p.paper}
    for t, name, g in sorted(events):
        mix.put(t, make[name](), g)
    fx = job / "sfx.wav"
    mix.write(fx, dur)
    bgm, gain = hf_music.short_pick({"id": rid, "series": th.get("bgm", "fs"), "day": "2026-11-18", "slot": rid}, ROOT)
    gain = round(gain * th.get("bgm_scale", .8), 3)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-stream_loop", "-1", "-i", str(ROOT / bgm), "-i", str(fx),
                    "-filter_complex", f"[1:a]apad[v];[2:a]volume={gain},afade=t=out:st={dur - 1.2}:d=1.2[m];[v][m][3:a]amix=inputs=3:duration=first:normalize=0[a]",
                    "-map", "0:v", "-map", "[a]", "-t", str(dur), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    return bgm, gain


def hf(job: Path, args: str, timeout=1800) -> subprocess.CompletedProcess:
    return subprocess.run(["/bin/bash", "-lc", f'{NODE} cd "{job}" && npx --yes {HFV} {args}'], capture_output=True, text=True, timeout=timeout)


# ---------------- QA ----------------
def qa(job: Path, dur: float, windows, mp4: Path | None) -> dict:
    rep = {}
    p = hf(job, "lint --json", 300)
    try:
        lj = json.loads(p.stdout[p.stdout.find("{"):])
        rep["lint"] = {"ok": lj.get("ok"), "errors": [f.get("code") for f in lj.get("findings", []) if f.get("severity") == "error"],
                       "warnings": [f.get("code") for f in lj.get("findings", []) if f.get("severity") == "warning"]}
    except Exception:
        rep["lint"] = {"raw": (p.stdout + p.stderr)[-800:]}
    mids = ",".join(f"{(a + b) / 2:.2f}" for a, b in windows)
    p = hf(job, f"check --json --at {mids}", 600)
    try:
        cj = json.loads(p.stdout[p.stdout.find("{"):])
        rep["check"] = {"ok": cj.get("ok"), "runtime": cj.get("runtime", {}).get("errors", cj.get("runtime")),
                        "layout_errors": len([x for x in (cj.get("layout", {}) or {}).get("findings", []) if x.get("severity") == "error"]),
                        "contrast_errors": len([x for x in (cj.get("contrast", {}) or {}).get("findings", []) if x.get("severity") == "error"])}
    except Exception:
        rep["check"] = {"raw": (p.stdout + p.stderr)[-800:]}
    if mp4 and mp4.exists():
        sheet = job / "qa_sheet.jpg"
        frames = []
        for k in range(16):
            t = dur * k / 15.3
            f = job / f"_qa_{k:02d}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1", "-vf", "scale=270:480", str(f)], check=False)
            frames.append(f)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", str(job / "_qa_*.jpg"), "-vf", "tile=8x2", str(sheet)], check=False)
        for f in frames:
            f.unlink(missing_ok=True)
        rep["sheet"] = str(sheet)
    (job / "qa.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return rep


# ---------------- build ----------------
def build(spec_path: Path, render: bool, do_qa: bool, strict: bool, use_ledger: bool) -> None:
    import hf_batch_render as R  # noqa: PLC0415
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    rid, th = spec["id"], theme(spec["theme"])
    job = JOBS / rid
    (job / "assets").mkdir(parents=True, exist_ok=True)
    (job / "hyperframes.json").write_text(json.dumps({"paths": {"blocks": ".", "components": "components", "assets": "assets"}}), encoding="utf-8")
    texts = spec["lines"]
    wav = job / "assets" / "vo.wav"
    if spec.get("voice"):
        shutil.copy(spec["voice"]["wav"], wav)
        segs = json.loads(Path(spec["voice"]["manifest"]).read_text(encoding="utf-8"))["segments"]
    else:
        txt = job / "vo.txt"
        clean = [t.replace("**", "") for t in texts]
        txt.write_text("\n".join(clean) + "\n", encoding="utf-8")
        man_p = job / "assets" / "vo.json"
        if not wav.exists() or not man_p.exists() or json.loads(man_p.read_text(encoding="utf-8")).get("_text") != clean:
            assert R.render_tts(txt, wav, clean, R.voice_for(spec.get("voice_series", spec["channel"]))), "TTS hỏng"
            man = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8")); man["_text"] = clean
            wav.with_suffix(".json").write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")
        segs = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["segments"]
    L = line_words(wav, segs, texts)
    dur = round(L[-1]["end"] + spec.get("tail", 1.4), 2)

    scenes = []
    for i, s in enumerate(spec["scenes"]):
        s = copy.deepcopy(s)
        if s["device"] == "quote" and s.get("fromLine", True) and "text" not in s:
            s["text"] = texts[s["line"]]
        if s["device"] == "quote":
            s["wordTimes"] = [w["t"] for w in L[s["line"]]["words"]] if s.get("text") == texts[s["line"]] else None
        for k in ("img",):
            if s.get(k):
                src = Path(s[k]) if Path(s[k]).is_absolute() else ROOT / s[k]
                shutil.copy(src, job / "assets" / src.name); s[k] = f"assets/{src.name}"
        scenes.append(resolve_tree(s, L, f"scenes[{i}]"))
    warn = variety(scenes, spec["channel"], use_ledger)
    for w in warn:
        print("  !! đa dạng:", w)
    if strict and warn:
        raise SystemExit("dừng (--strict): sửa luật đa dạng trước khi render")

    loop = spec.get("loop", True)
    starts = [0.0] + [round(L[s["line"]]["start"] - .12, 3) for s in scenes[1:]]
    end_main = dur - (.45 if loop else 0)
    windows = [(starts[i], starts[i + 1] if i + 1 < len(starts) else end_main) for i in range(len(starts))]
    if loop:                                    # lặp: móc quay lại ở khung cuối (khung cuối ~ khung đầu)
        again = copy.deepcopy(scenes[0]); again["seam"] = "zoom"; again["static"] = True
        scenes.append(again); windows.append((end_main, dur))
    for (a, b), s in zip(windows[:-1] if loop else windows, scenes):
        if b - a < .8:
            raise SystemExit(f"[spec] cảnh {s['device']} quá ngắn ({b - a:.2f}s)")
    (job / "index.html").write_text(compose(spec, th, L, dur, windows, scenes, job), encoding="utf-8")
    (job / "plan.json").write_text(json.dumps({"engine": engine_version(), "theme": spec["theme"], "windows": windows,
                                               "devices": [s["device"] for s in scenes], "warn": warn}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  job {job.relative_to(ROOT)} | {dur}s | {len(scenes)} cảnh | engine {engine_version()}")
    out = ROOT / spec.get("out", f"output/cl_staging/studio_out/{rid}.mp4")
    mp4 = None
    if render:
        silent = job / "silent.mp4"
        p = hf(job, f'render . --output "{silent}" --quality looks --fps 30 --quiet')
        if p.returncode != 0 or not silent.exists():
            raise SystemExit((p.stdout + p.stderr)[-3000:])
        bgm, gain = mix_audio(job, silent, wav, sfx_events(scenes, windows, th, dur), th, dur, out, rid)
        (out.with_suffix(".render.json")).write_text(json.dumps({"ok": True, "duration_s": dur, "style": "studio:" + spec["theme"], "engine": engine_version(),
                                                                 "bgm": bgm, "bgm_gain": gain, "media_credits": spec.get("credits", [])}, ensure_ascii=False), encoding="utf-8")
        mp4 = out
        print("  ->", out.relative_to(ROOT))
        if use_ledger:
            ledger_add(spec["channel"], {"id": rid, "date": str(date.today()), "theme": spec["theme"], "hook": scenes[0]["device"],
                                         "devices": [s["device"] for s in scenes[:-1] if True], "engine": engine_version()})
    if do_qa:
        rep = qa(job, dur, windows[:-1] if loop else windows, mp4)
        print("  QA:", json.dumps({k: v for k, v in rep.items() if k != "sheet"}, ensure_ascii=False)[:600])
        if rep.get("sheet"):
            print("  bảng khung:", rep["sheet"])


def fetch_fonts() -> None:
    """Tải woff2 (subset vietnamese + latin + latin-ext) cho mọi họ font trong themes/*.json -> studio/fonts/ + faces.json."""
    import os, urllib.request, certifi  # noqa: E401, PLC0415
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": ua}), timeout=60).read()  # noqa: E731
    faces, seen = [], set()
    for t in sorted((ST / "themes").glob("*.json")):
        css = get(json.loads(t.read_text(encoding="utf-8"))["fonts"]).decode()
        for sub, body in re.findall(r"/\* ([a-z\-]+) \*/\s*@font-face \{(.*?)\}", css, re.S):
            if sub not in ("vietnamese", "latin", "latin-ext"):
                continue
            fam = re.search(r"font-family: '([^']+)'", body).group(1)
            src = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
            rel = f"fonts/{fam.replace(' ', '_')}/{hashlib.sha1(src.encode()).hexdigest()[:12]}.woff2"
            if (fam, sub, rel) in seen:
                continue
            seen.add((fam, sub, rel))
            p = ST / rel
            if not p.exists():
                p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(get(src))
            faces.append({"family": fam, "subset": sub, "file": rel,
                          "css": "@font-face {" + re.sub(r"src: url\([^)]+\) format\('woff2'\);", f"src: url('{rel}') format('woff2');", body) + "}"})
    (ST / "fonts" / "faces.json").write_text(json.dumps(faces, ensure_ascii=False, indent=1), encoding="utf-8")
    vi = sorted({f["family"] for f in faces if f["subset"] == "vietnamese"})
    allf = sorted({f["family"] for f in faces})
    print("họ font:", allf); print("THIẾU tiếng Việt:", [f for f in allf if f not in vi] or "không")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("devices"); sub.add_parser("themes"); sub.add_parser("fonts")
    b = sub.add_parser("build"); b.add_argument("spec"); b.add_argument("--render", action="store_true"); b.add_argument("--qa", action="store_true")
    b.add_argument("--strict", action="store_true"); b.add_argument("--no-ledger", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, str(ROOT))
    if a.cmd == "devices":
        for k, v in DEVICES.items():
            print(f"{k:12s} {v}")
    elif a.cmd == "fonts":
        fetch_fonts()
    elif a.cmd == "themes":
        for p in sorted((ST / "themes").glob("*.json")):
            t = json.loads(p.read_text(encoding="utf-8")); print(f"{t['id']:12s} {t['label']}")
    else:
        build(Path(a.spec), a.render, a.qa, a.strict, not a.no_ledger)
    return 0


if __name__ == "__main__":
    sys.exit(main())
