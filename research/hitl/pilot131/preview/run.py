"""Pilot #131 overnight: render preview SS tier+ trên Oracle, tuần tự, có đo thời gian/RAM, QA mỗi video.
Chạy: nohup ~/vietneu-tts/.venv/bin/python ~/pilot131/run.py [id...] > ~/pilot131/run.log 2>&1 &
Không upload, không ghi ledger production (studio --no-ledger; Long dùng plan dir riêng ~/pilot131/long)."""
import json, os, shutil, subprocess, sys, threading, time
from pathlib import Path

R = Path("/home/ubuntu/pilot131")
REPO = Path("/home/ubuntu/vietneu-tts")
PY = str(REPO / ".venv/bin/python")
META = json.loads((R / "meta.json").read_text())
BROWSER = os.environ.get("P131_BROWSER", "/usr/bin/chromium")  # bench Long 30/10 chạy được với chromium hệ thống
ENV = dict(os.environ, HYPERFRAMES_BROWSER_PATH=BROWSER, HF_RENDER_TIMEOUT_X="20",
           PRODUCER_PAGE_NAVIGATION_TIMEOUT_MS="300000")

JOBS = [  # (id, loại, topic)
    ("p131_vsd_bach_dang_c1v1", "short", "vsd_bach_dang_1288"),
    ("p131_vsd_thanh_nha_ho_c3v1", "short", "vsd_thanh_nha_ho"),
    ("p131_fs_quet_nha_c1v2", "short", "fs_quet_nha_mung1_tet"),
    ("L_p131_fs_mauthan_c2v2", "long", "fs_mau_than_1968_2027"),
    ("L_p131_bud_vessantara_c3v2", "long", "bud_vessantara"),
    ("p131_bud_angulimala_c1v1", "short", "bud_angulimala"),  # render lại sau QA lần 1 (nhãn đè kicker, quote tràn)
]
VOICE = {  # giọng D theo kênh (tts_ruleset.json) cho short BUD/FS; VSD dùng hồ sơ kênh (v3turbo Thục Đoan) của studio
    "bud": {"voice": "Binh", "engine": "standard", "tempo": 0.9, "pause": 0.5, "temperature": 0.9, "text_mode": "production"},
    "fs": {"voice": "Thái Sơn", "style": "doc_truyen", "tempo": 0.98, "pause": 0.35, "temperature": 0.7, "donor": "Thanh Bình", "text_mode": "speech"},
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Sampler(threading.Thread):
    def __init__(self, path):
        super().__init__(daemon=True); self.path, self.stop = path, False; self.peak = 0

    def run(self):
        with open(self.path, "w") as f:
            while not self.stop:
                mem = open("/proc/meminfo").read().split("\n")
                tot = int(mem[0].split()[1]); avail = int([l for l in mem if l.startswith("MemAvailable")][0].split()[1])
                used = (tot - avail) // 1024; self.peak = max(self.peak, used)
                f.write(f"{int(time.time())} used_mb={used} load={open('/proc/loadavg').read().split()[0]}\n"); f.flush()
                time.sleep(10)


def sh(cmd, logf, cwd=REPO, timeout=None):
    with open(logf, "a") as lf:
        lf.write(f"\n$ {cmd}\n"); lf.flush()
        p = subprocess.run(["bash", "-c", cmd], cwd=cwd, env=ENV, stdout=lf, stderr=subprocess.STDOUT, timeout=timeout)
    return p.returncode


def probe(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
                          "-of", "json", str(mp4)], capture_output=True, text=True).stdout
    return json.loads(out)


def loudness(mp4):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    vals = {}
    for key, tag in (("I", "integrated_lufs"), ("Peak", "true_peak_dbfs")):
        for line in tail.splitlines():
            if line.strip().startswith(key + ":"):
                try: vals[tag] = float(line.split(":")[1].split()[0])
                except ValueError: pass
    return vals


def blackdetect(mp4):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp4), "-vf", "blackdetect=d=0.5:pix_th=0.08", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [l.split("black_start:")[1].split()[0] for l in p.stderr.splitlines() if "black_start:" in l]


def contact_sheet(mp4, dur, out, n=12, cols=4):
    d = out.parent / "_frames"; d.mkdir(exist_ok=True)
    for i in range(n):
        t = 0.05 + (dur - 0.3) * i / (n - 1)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
                        "-vf", f"scale=480:-2,drawtext=text='{t:.1f}s':x=10:y=10:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6",
                        str(d / f"f{i:02d}.jpg")])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(d / "f%02d.jpg"), "-vf", f"tile={cols}x{(n + cols - 1) // cols}:padding=6:color=white",
                    "-frames:v", "1", str(out)])
    first = out.parent / "first_frame.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.05", "-i", str(mp4), "-frames:v", "1", str(first)])
    shutil.rmtree(d, ignore_errors=True)


def run_short(jid, topic, od, logf):
    spec = json.loads((R / "shorts" / f"{jid}.json").read_text())
    ch = spec["channel"]
    t0 = time.time()
    if ch in VOICE:
        wav = od / "voice.wav"
        vs = od / "voice_spec.json"; vs.write_text(json.dumps(VOICE[ch], ensure_ascii=False))
        if sh(f"{PY} {R}/tts_short.py {R}/shorts/{jid}.json {vs} {wav}", logf) != 0 or not wav.exists():
            return "FAILED", "TTS lỗi", {}
        spec["voice"] = {"wav": str(wav), "manifest": str(wav.with_suffix(".json"))}
    else:
        spec["tts"] = True
    t_tts = time.time() - t0
    sp = od / "spec.json"; sp.write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    t1 = time.time()
    rc = sh(f"{PY} {R}/studio_runner.py build {sp} --render --qa --no-ledger", logf, timeout=5 * 3600)
    t_render = time.time() - t1
    mp4 = Path(spec["out"])
    if rc != 0 or not mp4.exists():
        return "FAILED", f"studio rc={rc}", {"tts_s": round(t_tts), "render_s": round(t_render)}
    job = REPO / "hyperframes_short" / "jobs" / spec["id"]
    for f, dst in (("plan.json", "studio_plan.json"), ("qa.json", "studio_qa.json"), ("qa_sheet.jpg", "studio_qa_sheet.jpg")):
        if (job / f).exists(): shutil.copy(job / f, od / dst)
    timing = {"lines": spec["lines"]}
    man = Path(spec["voice"]["manifest"]) if isinstance(spec.get("voice"), dict) else (job / "voice.json")
    if man.exists():
        timing["voice_segments"] = json.loads(man.read_text()).get("segments")
    if (job / "plan.json").exists():
        timing["scenes"] = json.loads((job / "plan.json").read_text()).get("scenes")
    (od / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1))
    return "RENDERED", "", {"tts_s": round(t_tts), "render_s": round(t_render)}


def run_long(jid, topic, od, logf):
    t1 = time.time()
    rc = sh(f"{PY} hf_batch_render.py {R}/long --only {jid}", logf, timeout=8 * 3600)
    t = time.time() - t1
    src = R / "long" / "out" / f"{jid}.mp4"
    if rc != 0 or not src.exists():
        return "FAILED", f"hf_batch_render rc={rc}", {"render_s": round(t)}
    shutil.copy(src, od / "final_preview.mp4")
    timing = {}
    for suf in ("tts.json", "render.json", "json"):
        f = R / "long" / "out" / f"{jid}.{suf}"
        if f.exists():
            try: timing[suf] = json.loads(f.read_text())
            except json.JSONDecodeError: pass
    (od / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1))
    return "RENDERED", "", {"render_s_total": round(t)}


def main(only):
    summary = R / "out" / "summary.json"
    S = json.loads(summary.read_text()) if summary.exists() else {}
    for jid, kind, topic in JOBS:
        if only and jid not in only:
            continue
        od = R / "out" / jid; od.mkdir(parents=True, exist_ok=True)
        logf = od / "render.log"
        smp = Sampler(od / "mem_samples.txt"); smp.start()
        log("START", jid)
        t0 = time.time()
        try:
            status, err, times = (run_short if kind == "short" else run_long)(jid, topic, od, logf)
        except Exception as e:  # noqa: BLE001 -- một video hỏng không dừng cả đêm
            status, err, times = "FAILED", repr(e)[:300], {}
        smp.stop = True
        rec = dict(META[topic], job_id=jid, kind=kind, render_status=status, error=err, times=times,
                   wall_s=round(time.time() - t0), peak_ram_mb=smp.peak, host="oracle vieneu-worker (A1 2 OCPU/12 GB)")
        mp4 = od / "final_preview.mp4"
        if status == "RENDERED" and mp4.exists():
            pr = probe(mp4); dur = float(pr["format"]["duration"])
            contact_sheet(mp4, dur, od / "contact_sheet.jpg")
            rec["probe"] = pr; rec["duration_s"] = round(dur, 1); rec["loudness"] = loudness(mp4); rec["black_segments_start_s"] = blackdetect(mp4)
        (od / "status.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
        S[jid] = {k: rec.get(k) for k in ("topic", "candidate_id", "version", "content_sha256", "approval_status", "render_status", "error",
                                          "wall_s", "peak_ram_mb", "duration_s", "loudness")}
        summary.write_text(json.dumps(S, ensure_ascii=False, indent=1))
        log("END", jid, status, err, rec.get("wall_s"), "s peak", smp.peak, "MB")
    log("ALL DONE")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
