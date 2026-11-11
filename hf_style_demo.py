"""Bộ style bổ sung (#258, longform_styles.js): plan mẫu + xuất KHUNG TĨNH để soát mắt / đo tất định.

Ba cuộn mẫu (REELS), mỗi cuộn 3 cảnh style xen câu thường (đúng luật: <= 3 cảnh style một lần render,
không hai cảnh liền nhau). hf_showreel.py dùng lại REELS để render video khi đĩa còn chỗ.

    python hf_style_demo.py stills [s1|s2|s3] [--out DIR]   # PNG khung tĩnh, không render video (đĩa đầy)
    python hf_style_demo.py determinism                      # chụp cùng một mốc hai lần, so md5
    python hf_style_demo.py regress <compositions của main>  # plan cũ: khung y hệt main
    python hf_style_demo.py seekorder                        # seek lùi/tiến không theo thứ tự vẫn ra cùng khung

Không gọi `hyperframes render`: chặn đúng lệnh đó trong bridge (monkeypatch subprocess.run) để lấy HTML
+ biến đã nướng (HF_KEEP_HTML), rồi dựng project tạm như hf_qa và chụp bằng `hyperframes snapshot --at`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEP = 8.0
DEMO_OUT = ROOT / "output" / "research_tmp" / "anim_styles_demo"

# Mỗi cuộn: câu 1 là thẻ chương (in đậm trọn câu), cảnh style ở câu 2/4/6, câu thường ở 3/5/7.
REELS: dict[str, dict] = {
    "s1": {
        "lines": [
            "**Bộ style bổ sung — phần một**",
            "Mộc bản khắc gỗ: mực đen, son đỏ, nét đục thô trên giấy dó.",
            "Giữa hai điểm nhấn là một câu **thường** của video.",
            "Cắt giấy nhiều lớp: chùa, tháp, rồi trăng lên và cửa sáng đèn.",
            "Một câu **thường** nữa, để style không đứng liền nhau.",
            "Một nét vẽ liên tục: đoá sen, dãy núi, rồi vòng thiền khép lại.",
            "Hết phần một của bộ style.",
        ],
        "visuals": {
            "2": {"type": "woodcut", "text": "Mộc bản · Vĩnh Nghiêm", "motif": "lotus", "steps": [{"at": 2, "word": "son"}]},
            "4": {"type": "papercut", "scene": "pagoda", "time": "night", "text": "Chùa Dâu · thế kỷ thứ hai", "sub": "Cắt giấy nhiều lớp",
                  "steps": [{"at": 4, "word": "chùa"}, {"at": 4, "word": "cửa"}]},
            "6": {"type": "oneline", "title": "Một nét", "items": [
                {"motif": "lotus", "label": "đoá sen", "at": 6, "word": "sen"},
                {"motif": "mountain", "label": "dãy núi", "at": 6, "word": "núi"},
                {"motif": "enso", "label": "vòng thiền", "at": 6, "word": "vòng"}]},
        },
    },
    "s2": {
        "lines": [
            "**Bộ style bổ sung — phần hai**",
            "Phim tư liệu mười sáu li: hạt phim, vệt xước, thẻ tiêu đề khung kép.",
            "Một câu **thường** của video nằm giữa.",
            "Bản vẽ kỹ thuật: mặt cắt luỹ, đường kích thước, khung tên.",
            "Lại một câu **thường** nữa.",
            "Ký hoạ chì: dựng hình trước, đi nét, rồi tô bóng mái cong.",
            "Hết phần hai của bộ style.",
        ],
        "visuals": {
            "2": {"type": "film16", "kicker": "Phim tư liệu", "title": "Lũy Thầy", "sub": "Tập một · Đào Duy Từ", "year": 1631,
                  "leader": True, "caption": "Đồng Hới, 1631", "steps": [{"at": 2, "word": "thẻ"}]},
            "4": {"type": "blueprint", "scene": "wall", "title": "Luỹ Thầy · mặt cắt", "scale": "1 : 500", "code": "LT-01", "sub": "Đào Duy Từ đắp năm 1631"},
            "6": {"type": "pencil", "scene": "gate", "title": "Cổng thành", "sub": "ký hoạ chì",
                  "notes": [{"text": "mái cong", "x": 1480, "y": 352, "at": 6, "word": "mái"}]},
        },
    },
    "s3": {
        "lines": [
            "**Bộ style bổ sung — phần ba**",
            "Mộc bản bản tối: con số mười hai trong vòng khắc.",
            "Một câu **thường** của video.",
            "Biểu đồ cột kiểu bản vẽ: ba cột, kích thước ghi bên cạnh.",
            "Một câu **thường** nữa.",
            "Cắt giấy lúc rạng đông: thành cổ, cổng vòm sáng dần.",
            "Hết phần ba của bộ style.",
        ],
        "visuals": {
            "2": {"type": "woodcut", "tone": "dark", "value": 12, "text": "Mười hai · con giáp", "steps": [{"at": 2, "word": "vòng"}]},
            "4": {"type": "blueprint", "title": "Tỷ lệ người xem", "unit": "%", "scale": "—", "code": "CK-03",
                  "bars": [{"label": "MỞ ĐẦU", "value": 100, "at": 4, "word": "ba"}, {"label": "GIỮA", "value": 62, "at": 4, "word": "cột"}, {"label": "CUỐI", "value": 41, "at": 4, "word": "kích"}]},
            "6": {"type": "papercut", "scene": "citadel", "time": "dawn", "text": "Thành Đồng Hới · 1812", "steps": [{"at": 6, "word": "thành"}, {"at": 6, "word": "cổng"}]},
        },
    },
}


# Plan CŨ (không cảnh style): dùng để chứng minh module mới không đổi khung hình của cảnh sẵn có.
OLD_REEL = {
    "lines": [
        "**Kiểm hồi quy kho cảnh cũ**",
        "Người xưa xem năm xung là **lời nhắc thận trọng**, không phải một bản án.",
        "Ba điều cần nhớ khi bước sang năm mới.",
        "Con số lớn đếm lên cùng vòng.",
        "Hết đoạn kiểm.",
    ],
    "visuals": {
        "2": {"type": "quote", "source": "Tục ngữ"},
        "3": {"type": "list", "title": "BA ĐIỀU", "items": [{"at": 3, "text": "Giữ chữ tín"}, {"at": 3, "text": "Bớt nói"}, {"at": 3, "text": "Thăm người già"}]},
        "4": {"type": "stat", "value": 1288, "label": "NĂM BẠCH ĐẰNG", "at": 4},
    },
}


def cmd_regress(other_comp: Path, out_dir: Path) -> int:
    """Plan cũ: cùng HTML + biến đã nướng, chụp với compositions/ của nhánh này và của checkout khác
    (main) -> md5 từng khung phải trùng. Chỉ khác nhau ở thẻ <link>/<script> longform_styles (nhánh này có,
    main không) nên bỏ hai thẻ đó khỏi index.html của project main."""
    import hf_qa  # noqa: PLC0415
    REELS["old"] = OLD_REEL
    try:
        comp, vars_path, lines = build_reel("old", out_dir)
    finally:
        REELS.pop("old", None)
    proj_new = make_project(comp, vars_path, "regress_new")
    proj_old = hf_qa.QA_DIR / "styledemo_regress_old"
    if proj_old.exists():
        shutil.rmtree(proj_old)
    proj_old.mkdir(parents=True)
    (proj_old / "compositions").symlink_to(other_comp.resolve())
    for f in ("hyperframes.json", "package.json"):
        shutil.copy2(proj_new / f, proj_old / f)
    src = (proj_new / "index.html").read_text(encoding="utf-8")
    src_old = src.replace('<link rel="stylesheet" href="compositions/longform_styles.css" />\n', "").replace('<script src="compositions/longform_styles.js"></script>\n', "")
    assert "longform_styles" not in src_old, "chưa gỡ hết thẻ longform_styles"
    (proj_old / "index.html").write_text(src_old, encoding="utf-8")
    times = []
    for k in OLD_REEL["visuals"]:
        ln = lines[int(k) - 1]
        times += [round(float(ln["start"]) + 1.0, 2), round((float(ln["start"]) + float(ln["end"])) / 2, 2)]
    a, _ = snapshot(proj_new, times, out_dir / "_reg_new", software=True)
    b, _ = snapshot(proj_old, times, out_dir / "_reg_old", software=True)
    bad = 0
    for t, fa, fb in zip(times, a, b):
        same, note = _same_frame(fa, fb)
        bad += 0 if same else 1
        print(f"t={t}: {'TRÙNG' if same else 'KHÁC'} {note}", flush=True)
    print("PLAN CŨ KHÔNG ĐỔI: ĐẠT" if not bad else f"PLAN CŨ: {bad} khung khác")
    return 1 if bad else 0


def _hf_cmd(proj: Path, args: str) -> str:
    return ('export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1 || exit 97; '
            f'cd {proj.as_posix()!r} && npx --yes hyperframes@0.8.75 {args}')


def build_reel(reel: str, out_dir: Path) -> tuple[Path, Path, list[dict]]:
    """Chạy bridge tới hết bước dựng HTML (chặn lệnh render). Trả (composition.html, vars.json, lines)."""
    import hyperframes_bridge as HB  # noqa: PLC0415

    R = REELS[reel]
    work = out_dir / f"_work_{reel}"
    work.mkdir(parents=True, exist_ok=True)
    L = R["lines"]
    (work / "reel.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
    segs = [{"start": round(k * STEP, 3), "end": round(k * STEP + STEP - .15, 3), "text": l.replace("**", "")} for k, l in enumerate(L)]
    wav = work / "reel.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(len(L) * STEP), str(wav)], check=True)
    wav.with_suffix(".json").write_text(json.dumps({"duration_s": len(L) * STEP, "segments": segs}, ensure_ascii=False), encoding="utf-8")

    captured: dict[str, str] = {}
    real_run = HB.subprocess.run

    def fake_run(cmd, *a, **kw):
        if isinstance(cmd, list) and len(cmd) == 3 and "hyperframes@0.8.75 render" in cmd[2]:
            m = re.search(r"--output '([^']+)'", cmd[2])
            if m:
                Path(m.group(1)).write_bytes(b"")
            captured["cmd"] = cmd[2]
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return real_run(cmd, *a, **kw)

    os.environ["HF_KEEP_HTML"] = "1"
    HB.subprocess.run = fake_run
    try:
        res = HB.render(work / "reel.txt", wav, "fs", work / f"{reel}.mp4", lane="long", style="laban_long",
                        footer="Bộ style bổ sung — bản xem thử", quality="looks", visuals=json.loads(json.dumps(R["visuals"])),
                        opts={"video_only": True, "wordts": True})
    finally:
        HB.subprocess.run = real_run
    m = re.search(r"-c (\S+) --variables-file (\S+)", captured.get("cmd", ""))
    if not m:
        raise SystemExit(f"không bắt được lệnh render: {res}")
    comp = HB.HF_PROJECT / m.group(1)
    vars_path = HB.HF_PROJECT / m.group(2)
    (work / f"{reel}_silent.mp4").unlink(missing_ok=True)
    lines = json.loads(json.loads(vars_path.read_text(encoding="utf-8"))["lines"])
    return comp, vars_path, lines


def make_project(comp: Path, vars_path: Path, tag: str) -> Path:
    """Project tạm như hf_qa.run: index.html = composition đã nướng biến, symlink compositions/."""
    import hf_qa  # noqa: PLC0415
    proj = hf_qa.QA_DIR / f"styledemo_{tag}"
    if proj.exists():
        shutil.rmtree(proj)
    proj.mkdir(parents=True)
    (proj / "compositions").symlink_to(hf_qa.HF_PROJECT / "compositions")
    if (hf_qa.HF_PROJECT / "assets").exists():
        (proj / "assets").symlink_to(hf_qa.HF_PROJECT / "assets")
    for f in ("hyperframes.json", "package.json"):
        if (hf_qa.HF_PROJECT / f).exists():
            shutil.copy2(hf_qa.HF_PROJECT / f, proj / f)
    variables = json.loads(vars_path.read_text(encoding="utf-8"))
    (proj / "index.html").write_text(hf_qa._bake(comp.read_text(encoding="utf-8"), variables), encoding="utf-8")
    return proj


def snapshot(proj: Path, times: list[float], out: Path, *, software: bool = False) -> tuple[list[Path], float]:
    """Chụp PNG tại các mốc; trả (danh sách file theo thứ tự mốc, số giây chạy).
    software=True: --no-browser-gpu (SwiftShader) -- raster tất định bit-một-bit, dùng khi so khung."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    at = ",".join(f"{t:.2f}" for t in times)
    gpu = " --no-browser-gpu" if software else ""
    t0 = time.time()
    res = subprocess.run(["/bin/bash", "-lc", _hf_cmd(proj, f"snapshot . --at {at} --no-end --timeout 20000 --describe false{gpu} -o {out.as_posix()!r}")],
                         capture_output=True, text=True, timeout=1200)
    dt = time.time() - t0
    if res.returncode != 0:
        raise SystemExit(f"snapshot lỗi (exit {res.returncode}):\n{(res.stdout + res.stderr)[-2000:]}")
    files = sorted(out.glob("*.png"))
    return files, dt


def style_times(reel: str, lines: list[dict]) -> list[tuple[str, float]]:
    """Ba mốc mỗi cảnh style: sau 1 s, giữa, trước khi hết 1 s."""
    out = []
    for k, v in REELS[reel]["visuals"].items():
        ln = lines[int(k) - 1]
        s, e = float(ln["start"]), float(ln["end"])
        for tag, t in (("a", s + 1.0), ("b", (s + e) / 2), ("c", e - 1.0)):
            out.append((f"{v['type']}_{tag}", round(t, 2)))
    return out


def cmd_stills(reels: list[str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rep_path = out_dir / "stills_report.json"
    report = [r for r in (json.loads(rep_path.read_text(encoding="utf-8")) if rep_path.exists() else []) if r.get("reel") not in reels]
    for reel in reels:
        t0 = time.time()
        comp, vars_path, lines = build_reel(reel, out_dir)
        t_build = time.time() - t0
        proj = make_project(comp, vars_path, reel)
        shots = style_times(reel, lines)
        files, dt = snapshot(proj, [t for _, t in shots], out_dir / f"_snap_{reel}")
        names = []
        for (tag, t), f in zip(shots, files):
            dst = out_dir / f"{reel}_{tag}_{t:.1f}s.png"
            shutil.move(str(f), dst)
            names.append(dst.name)
        shutil.rmtree(out_dir / f"_snap_{reel}", ignore_errors=True)
        report.append({"reel": reel, "build_s": round(t_build, 1), "snapshot_s": round(dt, 1), "frames": len(files),
                       "s_per_frame": round(dt / max(1, len(files)), 2), "files": names})
        print(f"{reel}: dựng {t_build:.1f}s, chụp {len(files)} khung trong {dt:.1f}s", flush=True)
    rep_path.write_text(json.dumps(sorted(report, key=lambda r: r["reel"]), ensure_ascii=False, indent=1), encoding="utf-8")


def _frame_diff(fa: Path, fb: Path) -> tuple[str, float, int]:
    """(md5 a, % điểm ảnh khác, lệch tối đa /255). md5 trùng -> (md5, 0, 0)."""
    ha, hb = hashlib.md5(fa.read_bytes()).hexdigest(), hashlib.md5(fb.read_bytes()).hexdigest()
    if ha == hb:
        return ha, 0.0, 0
    from PIL import Image, ImageChops  # noqa: PLC0415
    ia, ib = Image.open(fa).convert("RGB"), Image.open(fb).convert("RGB")
    d = ImageChops.difference(ia, ib)
    px = sum(1 for p in d.getdata() if max(p) > 0)
    mx = max(max(p) for p in d.getdata())
    return ha, px / (ia.width * ia.height) * 100, mx


def _same_frame(fa: Path, fb: Path) -> tuple[bool, str]:
    """md5 trùng -> giống hệt. Khác -> đo số điểm ảnh lệch (PIL) để phân biệt lỗi logic với nhiễu raster."""
    ha, pct, mx = _frame_diff(fa, fb)
    if not pct and not mx:
        return True, f"md5 {ha[:10]}"
    return False, f"{pct:.3f}% điểm ảnh khác, lệch tối đa {mx}/255"


def cmd_seekorder(out_dir: Path) -> int:
    """Tất định khi seek KHÔNG theo thứ tự: cùng một trang, seek tới mốc giữa cảnh style rồi lùi/tiến qua các mốc khác
    và quay lại -> ảnh chụp phải giống hệt lần đầu; đồng thời giống trang mới seek thẳng tới mốc đó.
    Chạy node + playwright-core sẵn trong cache npx của hyperframes (không cài gì), trình duyệt Chrome của máy (channel chrome)."""
    pw = sorted(Path.home().glob(".npm/_npx/*/node_modules/playwright-core"))
    if not pw:
        raise SystemExit("không thấy playwright-core trong ~/.npm/_npx (chạy hyperframes một lần để npx tải)")
    out_dir.mkdir(parents=True, exist_ok=True)
    bad = 0
    for reel in ("s1", "s2"):
        comp, vars_path, lines = build_reel(reel, out_dir)
        proj = make_project(comp, vars_path, reel + "_seek")
        shots = style_times(reel, lines)
        mids, ends = shots[1::3], [t for _, t in shots[2::3]]   # mốc giữa 3 cảnh style; mốc cuối để nhảy qua rồi quay lại
        plan = [{"tag": tag, "t": t, "seq": [max(0.0, t - 8.0), t_end, ends[-1], 0.5, t], "file": str(out_dir / f"seek_{reel}_{tag}.png")}
                for (tag, t), t_end in zip(mids, ends)]
        (proj / "seek.cjs").write_text(SEEK_JS, encoding="utf-8")
        res = subprocess.run(["node", str(proj / "seek.cjs"), str(pw[-1]), (proj / "index.html").resolve().as_uri(), json.dumps(plan)],
                             capture_output=True, text=True, timeout=600)
        if res.returncode != 0:
            raise SystemExit(f"seek.cjs lỗi:\n{(res.stdout + res.stderr)[-2000:]}")
        for r in json.loads(res.stdout.strip().splitlines()[-1]):
            # Cùng trang, seek lùi/tiến rồi quay lại: phải trùng md5 (đây là điều kiện tất định theo thứ tự seek).
            # Trang mới: cùng md5, hoặc chỉ lệch raster chữ giữa hai trang (< 0,02 % điểm ảnh) -> coi là trùng, ghi rõ.
            same1 = r["first"] == r["back"]
            f1 = Path(r["file"])
            _h, pct, mx = _frame_diff(f1, f1.with_name(f1.stem + "_fresh.png"))
            same2 = pct == 0 and mx == 0
            near2 = (not same2) and (mx <= 2 or pct < 0.02)   # lệch ≤ 2/255 = khử răng cưa chữ giữa hai trang, không phải trạng thái
            bad += (0 if same1 else 1) + (0 if (same2 or near2) else 1)
            note2 = f"{pct:.3f}% điểm ảnh, lệch tối đa {mx}/255"
            print(f"{reel} {r['tag']} t={r['t']}: lùi-rồi-tiến {'TRÙNG' if same1 else 'KHÁC'} · trang mới "
                  f"{'TRÙNG' if same2 else ('~TRÙNG (nhiễu raster chữ: ' + note2 + ')' if near2 else 'KHÁC ' + note2)} md5 {r['first'][:10]}", flush=True)
    print("SEEK KHÔNG THỨ TỰ: ĐẠT" if not bad else f"SEEK KHÔNG THỨ TỰ: {bad} khung khác")
    return 1 if bad else 0


# Node: mở trang đã nướng, seek bằng chính timeline GSAP (tl.seek(t, false) để onUpdate chạy như lúc render),
# chụp lần đầu -> seek lùi/tiến lung tung -> quay lại -> chụp; và trang mới seek thẳng tới mốc.
SEEK_JS = r"""
const [,, PW, URL, PLAN] = process.argv;
const { chromium } = require(PW);
const crypto = require("crypto"), fs = require("fs");
const md5 = (b) => crypto.createHash("md5").update(b).digest("hex");
(async () => {
  const browser = await chromium.launch({ channel: "chrome", headless: true, args: ["--disable-gpu", "--force-device-scale-factor=1"] });
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    page.on("pageerror", (e) => console.error("[page]", e.message));
    page.on("console", (m) => { if (m.type() === "error") console.error("[console]", m.text().slice(0, 300)); });
    // Giả lập API biến của runtime HyperFrames (engine.js gọi window.__hyperframes.getVariables()):
    // trả đúng giá trị mặc định đã nướng vào data-composition-variables (hf_qa._bake).
    await page.addInitScript(() => {
      window.__hyperframes = { getVariables() {
        const el = document.querySelector("[data-composition-variables]"), out = {};
        if (el) JSON.parse(el.getAttribute("data-composition-variables")).forEach((d) => { out[d.id] = d.default; });
        return out;
      } };
    });
    await page.goto(URL);
    try {
      await page.waitForFunction(() => window.__timelines && window.__timelines.main && window.__timelines.main.duration() > 0, null, { timeout: 60000 });
    } catch (e) {
      console.error("diag:", await page.evaluate(() => JSON.stringify({ HF: typeof window.HF, tl: window.__timelines && Object.keys(window.__timelines), dur: window.__timelines && window.__timelines.main && window.__timelines.main.duration() })));
      throw e;
    }
    // Ép tải MỌI @font-face đã khai báo (trang mới vừa mở: font của cảnh chưa chắc đã được yêu cầu -> chữ fallback rồi đổi).
    await page.evaluate(() => Promise.all(Array.from(document.fonts).map((f) => f.load().catch(() => null))));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(1500);
    return page;
  };
  const shot = async (page, t) => {
    await page.evaluate((t) => { const tl = window.__timelines.main; tl.pause(); tl.seek(t, false); }, t);
    await page.evaluate(() => document.fonts.ready);                      // font của cảnh vừa seek tới phải nạp xong
    await page.waitForFunction(() => document.fonts.status === "loaded", null, { timeout: 30000 });
    await page.waitForTimeout(120);
    return await page.screenshot({ type: "png" });
  };
  const page = await open(), out = [];
  for (const sh of JSON.parse(PLAN)) {
    const first = await shot(page, sh.t);
    let back = null;
    for (const tt of sh.seq) back = await shot(page, tt);
    const fresh = await shot(await open(), sh.t);
    fs.writeFileSync(sh.file, first);
    fs.writeFileSync(sh.file.replace(/\.png$/, "_fresh.png"), fresh);
    out.push({ tag: sh.tag, t: sh.t, file: sh.file, first: md5(first), back: md5(back), fresh: md5(fresh) });
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch((e) => { console.error(e); process.exit(1); });
"""


def cmd_determinism(out_dir: Path) -> int:
    """Cùng một mốc, chụp hai lượt riêng (hai tiến trình trình duyệt) -> md5 phải trùng ở mọi style."""
    out_dir.mkdir(parents=True, exist_ok=True)
    bad = 0
    for reel in ("s1", "s2"):
        comp, vars_path, lines = build_reel(reel, out_dir)
        proj = make_project(comp, vars_path, reel + "_det")
        shots = style_times(reel, lines)[1::3]   # mốc giữa mỗi cảnh style
        times = [t for _, t in shots]
        a, _ = snapshot(proj, times, out_dir / f"_det_a_{reel}", software=True)
        b, _ = snapshot(proj, times, out_dir / f"_det_b_{reel}", software=True)
        for (tag, t), fa, fb in zip(shots, a, b):
            same, note = _same_frame(fa, fb)
            bad += 0 if same else 1
            print(f"{reel} {tag} t={t}: {'TRÙNG' if same else 'KHÁC'} {note}", flush=True)
        shutil.rmtree(out_dir / f"_det_a_{reel}", ignore_errors=True)
        shutil.rmtree(out_dir / f"_det_b_{reel}", ignore_errors=True)
    print("TẤT ĐỊNH: ĐẠT" if not bad else f"TẤT ĐỊNH: {bad} khung khác")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("stills", "determinism", "regress", "seekorder"):
        print(__doc__)
        return 2
    out_dir = DEMO_OUT
    if "--out" in argv:
        out_dir = Path(argv[argv.index("--out") + 1])
    if argv[0] == "stills":
        reels = [a for a in argv[1:] if a in REELS] or list(REELS)
        cmd_stills(reels, out_dir)
        return 0
    if argv[0] == "regress":
        return cmd_regress(Path(argv[1]), out_dir)
    if argv[0] == "seekorder":
        return cmd_seekorder(out_dir)
    return cmd_determinism(out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
