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
import base64
import copy
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import time
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
    "month_sheet": dict(purpose="time", framing="grid", axis="draw", circle=0),
    "thiep_cuoi":  dict(purpose="statement", framing="card-on-field", axis="static", circle=0),
}
STAMP_KEYS = ("stampAt", "sealAt", "strikeAt")
LAND_KEYS = ("at", "litAt", "diffAt", "valueAt")


def display_path(path: Path) -> str:
    """Show repo-relative paths when possible and absolute paths otherwise."""
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def short_tts_config(spec: dict) -> dict:
    """Resolve short TTS settings; channels without a profile retain legacy standard."""
    from library.tools.lib import load_profile
    import hf_batch_render as R

    profile = load_profile(spec.get("channel", ""))
    configured = profile.get("tts") if isinstance(profile, dict) else None
    if not isinstance(configured, dict):
        return {"mode": "standard", "voice": spec.get("voice_name") or
                R.voice_for(spec.get("voice_series", spec["channel"])), "device": "mps"}
    mode = spec.get("tts_mode", configured.get("mode", "standard"))
    voice = spec.get("voice") if isinstance(spec.get("voice"), str) else None
    voice = voice or spec.get("voice_name") or configured.get("voice") or "Binh"
    device = configured.get("device", "mps")
    if device == "auto":
        device = "cpu"
        try:
            import torch
            if mode == "v3turbo":
                if torch.cuda.is_available():
                    device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
        except (ImportError, AttributeError):
            pass
    return {"mode": mode, "voice": voice, "device": device}


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
    with tempfile.TemporaryDirectory(prefix="studio-loudness-", dir=job) as tempdir:
        mixed = Path(tempdir) / "mix.wav"
        normalized = Path(tempdir) / "normalized.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-stream_loop", "-1", "-i", str(ROOT / bgm), "-i", str(fx),
                        "-filter_complex", f"[1:a]apad[v];[2:a]volume={gain},afade=t=out:st={dur - 1.2}:d=1.2[m];[v][m][3:a]amix=inputs=3:duration=first:normalize=0[a]",
                        "-map", "[a]", "-t", str(dur), "-c:a", "pcm_f32le", "-ar", "48000", "-ac", "2", str(mixed)], check=True)
        import hyperframes_bridge as HB
        norm_started = time.perf_counter()
        HB.normalize_loudness(mixed, normalized, HB.LOUD_TARGET["short"], true_peak=-1.5)
        print(f"Studio loudness normalization: {time.perf_counter() - norm_started:.3f}s for {dur:.1f}s clip", file=sys.stderr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(normalized),
                        "-map", "0:v", "-map", "1:a", "-t", str(dur), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    return bgm, gain


def hf(job: Path, args: str, timeout=1800) -> subprocess.CompletedProcess:
    browser_path = os.environ.get("HYPERFRAMES_BROWSER_PATH")
    b_env = f'export HYPERFRAMES_BROWSER_PATH={shlex.quote(browser_path)}; ' if browser_path else ''
    return subprocess.run(["/bin/bash", "-lc", f'{NODE} {b_env} cd "{job}" && npx --yes {HFV} {args}'], capture_output=True, text=True, timeout=timeout)


# ---------------- cổng 3 giây đầu (#253: BUD, FS, VSD) ----------------
MIN_IMG_LUMA = 50
HOOK_TEXT_LATEST = 0.8  # cổng 3 giây đầu: chữ hook hiện trễ quá 0.8 giây
HOOK_GATE_CHANNELS = {"bud", "fs", "vsd", "phat_phap", "phong_thuy", "van_su_dia", "văn sử địa", "phật giáo", "phong thủy"}
HOOK_VISUAL_TYPES = {
    "photo", "split", "counter", "hero", "doc", "evidence", "mug", "file", "crowd", "map",
    "chart", "cards3d", "board", "pan_tour", "cycle_draw", "wheel", "count_ring",
    "thiep_cuoi", "calendar", "month_sheet", "statue_cards", "ai_cards", "dustbeam",
    "lightfield", "silence", "inkwash", "mudra_grid", "oai_nghi_table"
}
HOOK_VISUAL_KEYS = ("img", "bg", "vid", "clip", "photo", "image")
HOOK_TEXT_KEYS = (
    "head", "title", "text", "label", "name", "desc", "date", "prefix", "suffix", "sub",
    "k", "tag", "items", "rows", "bars", "to", "kick", "big", "num", "chip", "badge",
    "groups", "cards", "title_html"
)
HOOK_TIME_KEYS = ("headAt", "dayAt", "labelAt", "signAt", "markAt", "stampAt", "sealAt", "strikeAt", "litAt", "diffAt", "valueAt")


def is_hook_gate_channel(spec: dict) -> bool:
    """Xác định spec có thuộc kênh BUD, FS, hoặc Văn Sử Địa (VSD) hay không."""
    ch = str(spec.get("channel") or spec.get("series") or spec.get("voice_series") or "").strip().lower()
    tokens = set(re.split(r"[-_\s/]+", ch))
    return (
        ch in HOOK_GATE_CHANNELS
        or bool(tokens & {"bud", "fs", "vsd", "phat", "phong"})
        or any(c in ch for c in ("van_su", "văn sử", "phật giáo", "phong thủy", "phật", "phong thuỷ"))
    )


def dark_image_errors(img_paths: list[Path | str], root_dir: Path | None = None) -> list[str]:
    """Ảnh quá tối (mean grayscale < MIN_IMG_LUMA): quét pixel trung bình xám."""
    from PIL import Image, ImageStat
    root = root_dir or ROOT
    out = []
    for ref in img_paths:
        p = None
        if isinstance(ref, str) and ref.startswith("data:"):
            try:
                raw = base64.b64decode(ref.split(",", 1)[-1])
                im = Image.open(io.BytesIO(raw))
            except Exception:
                continue
        else:
            ref_str = str(ref)
            if ref_str.startswith("local:"):
                ref_str = ref_str[6:]
            candidates = [Path(ref_str)]
            if not Path(ref_str).is_absolute():
                candidates.extend([
                    root / ref_str,
                    HF / ref_str,
                    HF / "assets" / ref_str,
                    root / "output" / ref_str,
                ])
            for c in candidates:
                if c.exists() and c.is_file():
                    p = c
                    break
            if p is None:
                continue
            try:
                im = Image.open(p)
            except Exception:
                continue
        with im:
            if im.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", im.size, (10, 20, 38))
                im = im.convert("RGBA")
                bg.paste(im, mask=im.split()[-1])
                im = bg
            luma = ImageStat.Stat(im.convert("L")).mean[0]
        if luma < MIN_IMG_LUMA:
            out.append(f"ảnh đầu quá tối (độ sáng {luma:.0f} < {MIN_IMG_LUMA}): thay ảnh sáng hơn")
    return out


def _hook_first_text_time(scene: dict, L: list[dict] | None = None) -> float:
    """Mốc chữ đầu tiên của cảnh mở xuất hiện. Mặc định 0.0 nếu chữ tĩnh hiện từ đầu."""
    if scene.get("device") in ("hook_poster", "counter"):
        return 0.0

    # Chữ tĩnh thuần túy (không có timing delay trong spec short)
    for pk in ("title", "text", "desc", "name", "sub", "k", "kick", "big", "num", "chip", "badge", "title_html"):
        val = scene.get(pk)
        if val is not None and str(val).strip():
            return 0.0

    # Chữ có thể animate: nếu có chữ mà không có timing key (hoặc timing <= 0.0) -> chữ tĩnh từ 0.0s
    text_time_pairs = {
        "head": "headAt", "label": "labelAt", "date": "dayAt", "day": "dayAt",
        "sign": "signAt", "mark": "markAt", "stamp": "stampAt", "seal": "sealAt",
        "strike": "strikeAt", "lit": "litAt", "diff": "diffAt", "value": "valueAt",
    }
    for tk, ak in text_time_pairs.items():
        val = scene.get(tk)
        if val is not None and str(val).strip():
            at_val = scene.get(ak)
            if at_val is None or (isinstance(at_val, (int, float)) and not isinstance(at_val, bool) and float(at_val) <= 0.0):
                return 0.0

    times = []
    for key in HOOK_TIME_KEYS:
        if scene.get(key) is not None:
            val = scene[key]
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                times.append(float(val))
            elif L and is_anchor(val, len(L)):
                try:
                    times.append(resolve(val, L, f"scene.{key}"))
                except Exception:
                    pass
    for key in ("items", "rows", "bars", "groups", "cards"):
        for it in scene.get(key) or []:
            if isinstance(it, str) and it.strip():
                return 0.0
            if isinstance(it, dict):
                at_val = it.get("at")
                if at_val is not None:
                    if isinstance(at_val, (int, float)) and not isinstance(at_val, bool):
                        times.append(float(at_val))
                    elif L and is_anchor(at_val, len(L)):
                        try:
                            times.append(resolve(at_val, L, f"scene.{key}[].at"))
                        except Exception:
                            pass
                else:
                    # Item không có 'at' mà có nội dung chữ -> hiện từ 0.0s
                    if any(it.get(k) is not None and str(it.get(k)).strip() for k in ("text", "head", "title", "label", "name", "val", "value")):
                        return 0.0

    return min(times) if times else 0.0


def hook_errors(spec: dict, job_dir: Path | None = None, L: list[dict] | None = None,
                assets_dir: Path | None = None, slug: str = "") -> list[str]:
    """Cổng 3 giây đầu (#253) cho Short BUD/FS/VSD:
    - ảnh đầu tối (luma < 50);
    - câu 1 chữ trần (cảnh mở chỉ có chữ trên nền trống);
    - chữ hook hiện trễ quá 0,8 giây.
    """
    job = job_dir or assets_dir
    out = []
    scenes = spec.get("scenes") or []

    # Dạng plan row (chưa dựng scenes nhưng có style, media, script)
    if not scenes and (spec.get("style") or spec.get("media")):
        style = spec.get("style", "")
        media = spec.get("media", {})
        has_media = bool(media.get("1") or media.get("0") or spec.get("img"))
        if not has_media and style not in HOOK_VISUAL_TYPES:
            out.append(f"cảnh mở ({style}) chỉ có chữ trên nền trống: dùng ảnh/clip/photo/split/counter hoặc thêm img/bg/vid")
        m1 = media.get("1") or media.get("0") or spec.get("img")
        if m1:
            p = m1.get("file") or m1.get("path") or m1.get("src") if isinstance(m1, dict) else str(m1)
            if p:
                out += dark_image_errors([p])
        kicker = spec.get("kicker") or spec.get("chip") or spec.get("badge") or spec.get("title")
        if not kicker:
            out.append("cảnh mở không có chữ hook trên màn hình (kicker/sub/head/text/label)")
        return out

    if not scenes:
        return ["cảnh mở: spec không có cảnh nào"]

    s0 = scenes[0]
    ty = s0.get("device") or s0.get("type") or ""

    # (a) Cổng câu 1 chữ trần
    has_media = any(s0.get(k) for k in HOOK_VISUAL_KEYS)
    if s0.get("img") and s0.get("img") in (spec.get("imgs") or {}):
        has_media = True
    if any(isinstance(s0.get(k), dict) and any(s0[k].get(vk) for vk in HOOK_VISUAL_KEYS) for k in ("a", "b", "mug")):
        has_media = True
    if not has_media and ty not in HOOK_VISUAL_TYPES:
        out.append(f"cảnh mở ({ty}) chỉ có chữ trên nền trống: dùng ảnh/clip/photo/split/counter hoặc thêm img/bg/vid")

    # (b) Cổng ảnh đầu quá tối
    img_candidates = []
    for k in ("img", "photo", "bg", "image"):
        if s0.get(k):
            val = s0[k]
            if isinstance(val, str) and spec.get("imgs") and val in spec["imgs"]:
                val = spec["imgs"][val]
            img_candidates.append(val)
    if job:
        resolved = []
        for c in img_candidates:
            if isinstance(c, str) and not c.startswith("data:"):
                fname = Path(c).name
                if (job / "assets" / fname).exists():
                    resolved.append(job / "assets" / fname)
                    continue
                elif (job / fname).exists():
                    resolved.append(job / fname)
                    continue
            resolved.append(c)
        img_candidates = list(dict.fromkeys(resolved))
    else:
        img_candidates = list(dict.fromkeys(img_candidates))
    if img_candidates:
        out += dark_image_errors(img_candidates)

    # (c) Cổng chữ hook trên màn hình & mốc thời gian
    on_screen = bool(str(spec.get("kicker") or "").strip() or str(spec.get("sub") or "").strip())
    on_screen = on_screen or any(s0.get(k) not in (None, "", [], {}) for k in HOOK_TEXT_KEYS)
    if not on_screen:
        out.append("cảnh mở không có chữ hook trên màn hình (kicker/sub/head/text/label)")

    if s0.get("line") is not None and s0.get("line") > 0:
        out.append(f"cảnh mở bắt đầu ở câu {s0['line']}: phải bắt đầu ở câu 0 (0,0s)")
    if s0.get("at") is not None:
        at_val = s0["at"]
        if isinstance(at_val, (int, float)) and float(at_val) > 0.0:
            out.append(f"cảnh mở bắt đầu lúc {float(at_val):.2f}s: phải bắt đầu ở 0,0s")

    t_text = _hook_first_text_time(s0, L)
    if t_text > HOOK_TEXT_LATEST:
        out.append(f"chữ đầu của cảnh mở hiện lúc {t_text:.2f}s (> {HOOK_TEXT_LATEST}s)")

    return out


# ---------------- QA ----------------
def qa(job: Path, dur: float, windows, mp4: Path | None, hook_errs: list[str] | None = None) -> dict:
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
    plan_f = job / "plan.json"
    h_warn = list(hook_errs) if hook_errs is not None else []
    if not h_warn and plan_f.exists():
        try:
            pj = json.loads(plan_f.read_text(encoding="utf-8"))
            h_warn = pj.get("hook_warn", [])
        except Exception:
            pass
    rep["hook"] = {"ok": len(h_warn) == 0, "warnings": h_warn}
    (job / "qa.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return rep


def qa_ok(rep: dict) -> bool:
    """QA đạt khi lint và check đều báo ok là True; thiếu/không đọc được (raw) tính là không đạt."""
    return (rep.get("lint") or {}).get("ok") is True and (rep.get("check") or {}).get("ok") is True


def qa_gate(job: Path, dur: float, windows, mp4: Path | None, strict: bool,
            strict_hook: bool = False, hook_errs: list[str] | None = None) -> bool:
    """Chạy QA, in kết quả; chỉ trả False khi (--strict và QA không đạt) hoặc (--strict-hook và vi phạm hook)."""
    rep = qa(job, dur, windows, mp4, hook_errs=hook_errs)
    print("  QA:", json.dumps({k: v for k, v in rep.items() if k != "sheet"}, ensure_ascii=False)[:600])
    if rep.get("sheet"):
        print("  bảng khung:", rep["sheet"])
    if strict and not qa_ok(rep):
        print("  LỖI (--strict): QA lint/check không đạt", flush=True)
        return False
    if strict_hook and not rep.get("hook", {}).get("ok", True):
        print(f"  LỖI (--strict-hook): vi phạm cổng 3 giây đầu: {' | '.join(rep.get('hook', {}).get('warnings', []))}", flush=True)
        return False
    return True


# ---------------- build ----------------
def build(spec_path: Path, render: bool, do_qa: bool, strict: bool, use_ledger: bool,
          allow_retire: bool = False, strict_hook: bool = False) -> bool:
    """Trả False chỉ khi --strict và QA không đạt; mọi trường hợp khác True."""
    sys.path.insert(0, str(ROOT))
    from library.tools.lib import enforce_lane
    import hf_batch_render as R  # noqa: PLC0415
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    enforce_lane(spec.get("channel"), spec.get("lane"), allow_retire)
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
        tts_cfg = short_tts_config(spec)
        tts_identity = {"mode": tts_cfg["mode"], "voice": tts_cfg["voice"]}
        cached_manifest = json.loads(man_p.read_text(encoding="utf-8")) if man_p.exists() else {}
        cached_tts_identity = cached_manifest.get("_tts", {"mode": "standard", "voice": tts_cfg["voice"]})
        if (not wav.exists() or not man_p.exists() or cached_manifest.get("_text") != clean
                or cached_tts_identity != tts_identity):
            assert R.render_tts(txt, wav, clean, tts_cfg["voice"],
                                mode=tts_cfg["mode"], device=tts_cfg["device"]), "TTS hỏng"
            man = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))
            man["_text"] = clean
            man["_tts"] = tts_identity
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

    # ---------------- kiểm cổng 3 giây đầu (hook gate #253) ----------------
    hook_errs = []
    if is_hook_gate_channel(spec):
        hook_errs = hook_errors(spec, job, L)
        for err in hook_errs:
            print(f"  !! CẢNH BÁO hook (3s đầu): {err}")

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
                                               "devices": [s["device"] for s in scenes], "warn": warn,
                                               "hook_warn": hook_errs}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  job {display_path(job)} | {dur}s | {len(scenes)} cảnh | engine {engine_version()}")
    out = ROOT / spec.get("out", f"output/cl_staging/studio_out/{rid}.mp4")
    mp4 = None
    if render:
        if strict_hook and hook_errs:
            if not do_qa:
                raise SystemExit(f"dừng (--strict-hook): vi phạm cổng 3 giây đầu: {' | '.join(hook_errs)}")
            print(f"  bỏ qua render do vi phạm (--strict-hook): {' | '.join(hook_errs)}")
        else:
            silent = job / "silent.mp4"
            p = hf(job, f'render . --output "{silent}" --quality looks --fps 30 --quiet')
            if p.returncode != 0 or not silent.exists():
                raise SystemExit((p.stdout + p.stderr)[-3000:])
            bgm, gain = mix_audio(job, silent, wav, sfx_events(scenes, windows, th, dur), th, dur, out, rid)
            (out.with_suffix(".render.json")).write_text(json.dumps({"ok": True, "duration_s": dur, "style": "studio:" + spec["theme"], "engine": engine_version(),
                                                                     "bgm": bgm, "bgm_gain": gain, "media_credits": spec.get("credits", [])}, ensure_ascii=False), encoding="utf-8")
            mp4 = out
            print("  ->", display_path(out))
            if use_ledger:
                ledger_add(spec["channel"], {"id": rid, "date": str(date.today()), "theme": spec["theme"], "hook": scenes[0]["device"],
                                             "devices": [s["device"] for s in scenes[:-1] if True], "engine": engine_version()})
    if do_qa:
        return qa_gate(job, dur, windows[:-1] if loop else windows, mp4, strict, strict_hook, hook_errs)
    if strict_hook and hook_errs:
        raise SystemExit(f"dừng (--strict-hook): vi phạm cổng 3 giây đầu: {' | '.join(hook_errs)}")
    return True


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
    b.add_argument("--strict-hook", action="store_true", help="Chặn build nếu vi phạm cổng 3 giây đầu (mặc định chỉ CẢNH BÁO)")
    b.add_argument("--cho-phep-retire", action="store_true", help="Lead vượt khuôn retire có lý do")
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
        if build(Path(a.spec), a.render, a.qa, a.strict, not a.no_ledger, a.cho_phep_retire, getattr(a, "strict_hook", False)) is False:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
