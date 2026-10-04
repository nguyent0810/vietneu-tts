"""Dựng cả loạt Short từ một thư mục plan: kịch bản -> TTS -> HyperFrames.

Thay cho bản `run_batch.py` vẫn được sao chép theo từng đợt (tháng 9 một bản,
tháng 10 một bản) -- hai bản đã kịp lệch nhau: bản tháng 10 biết truyền
`--figures`, bản tháng 9 thì chưa. Một script trong repo, nhận thư mục plan
làm tham số, là hết chuyện lệch.

Chạy lại được nhiều lần: mục nào đã có .mp4 thì bỏ qua, nên dừng giữa chừng
rồi chạy tiếp không tốn lại công render.

Usage:
    python3 hf_batch_render.py output/cl_staging/hyperframes_sept
    python3 hf_batch_render.py <thư mục> --only d26_a --quality draft
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
# Giọng suy ra từ topic của kênh (topic_voices.json), không hardcode: kênh
# Phật giáo dùng giọng khác kênh Hình Sự.
SERIES_TOPIC = {"law": "Hình Sự", "scam": "Hình Sự", "case": "Hình Sự", "tale": "Hình Sự",
                "bud": "Phật giáo", "fs": "Phong Thủy"}


def voice_for(series: str) -> str:
    topic = SERIES_TOPIC.get(series, "Hình Sự")
    cfg = json.loads((PROJECT_ROOT / "topic_voices.json").read_text(encoding="utf-8"))
    return cfg["voices"].get(topic, cfg.get("_default", "Binh"))
TTS_HELPER = PROJECT_ROOT / "_short_tts_render.py"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"

BGM = {"law": ("bgm/deliberate_thought.mp3", 0.17),
       "scam": ("bgm/thinking_music.mp3", 0.24),
       "case": ("bgm/deliberate_thought.mp3", 0.17),
       "tale": ("bgm/thinking_music.mp3", 0.20),
       # gain_db -9.7 của meditation_impromptu_01 trong bgm_tracks.py
       "bud": ("bgm/meditation_impromptu_01.mp3", 0.33),
       "fs": ("bgm/asian_drums.mp3", 0.2)}
FOOTER = {"law": "Phổ biến kiến thức pháp luật",
          "scam": "Nhận ra kịch bản trước khi chuyển tiền",
          "case": "Dẫn theo hồ sơ công khai",
          "tale": "Truyện hư cấu — nhân vật và tình tiết do tưởng tượng",
          "bud": "Nội dung suy ngẫm — không thay cho việc học Phật pháp trực tiếp",
          "fs": "Kiến thức truyền thống — để tham khảo"}

PLACEHOLDER_SCRIPT = ["(đã render trước, giữ nguyên file)"]
MAX_TTS_ATTEMPTS = 3
# Giọng đọc tiếng Việt rơi vào khoảng 13-19 ký tự/giây. Một câu dài hơn 3 lần
# mức đó là dấu hiệu TTS "đọc lồng" -- đã gặp thật: một câu ngắn bị đọc thành
# 32 giây, kéo cả video thành 55 giây và runner cũ chỉ lặng lẽ bỏ qua cả mục.
SEC_PER_CHAR_RUNAWAY = 3 / 13


def load_rows(plan_dir: Path) -> list[dict]:
    rows = []
    for f in sorted(glob.glob(str(plan_dir / "plan_*.json"))):
        rows += json.loads(Path(f).read_text(encoding="utf-8"))
    return rows


def runaway_segments(manifest_path: Path, script_lines: list[str]) -> list[int]:
    """Trả về chỉ số (1-based) các câu bị đọc dài bất thường."""
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    segments = data.get("segments") or []
    bad = []
    for i, seg in enumerate(segments, start=1):
        if i > len(script_lines):
            break
        expected = max(1.5, len(script_lines[i - 1]) * SEC_PER_CHAR_RUNAWAY)
        if (seg["end"] - seg["start"]) > expected:
            bad.append(i)
    if data.get("n_failed_qa"):
        bad = bad or [0]
    return bad


def render_tts(txt: Path, wav: Path, script_lines: list[str], voice: str = "Tuyen") -> bool:
    """TTS kèm thử lại khi phát hiện đọc lồng. Trả False nếu vẫn hỏng."""
    for attempt in range(1, MAX_TTS_ATTEMPTS + 1):
        for stale in (wav, wav.with_suffix(".json")):
            stale.unlink(missing_ok=True)
        proc = subprocess.run(
            [str(VENV_PYTHON), str(TTS_HELPER), "--text-file", str(txt),
             "--voice", voice, "--output-wav", str(wav)],
            cwd=PROJECT_ROOT, capture_output=True, text=True)
        manifest = wav.with_suffix(".json")
        if not manifest.is_file():
            print(f"    TTS lỗi (lần {attempt}): {proc.stderr[-200:]}", file=sys.stderr, flush=True)
            continue
        bad = runaway_segments(manifest, script_lines)
        if not bad:
            return True
        print(f"    TTS đọc lồng ở câu {bad} (lần {attempt}/{MAX_TTS_ATTEMPTS}) -- render lại",
              file=sys.stderr, flush=True)
    return False


# Video dài xoay vòng nhạc theo tâm trạng kênh -- một track chạy mọi video
# thì người xem quen tai. Chọn theo hash id (tất định, không cần sổ trạng thái):
# render lại cùng một video luôn ra cùng một track, nên ghi nguồn không lệch.
LONG_BGM_POOL = {"bud": ["bgm/meditation_impromptu_01.mp3", "bgm/meditation_impromptu_02.mp3",
                         "bgm/meditation_impromptu_03.mp3"],
                 "fs": ["bgm/comfortable_mystery_4.mp3", "bgm/thinking_music.mp3",
                        "bgm/deliberate_thought.mp3"]}


def pick_bgm(row: dict, wav: Path) -> tuple[str, float]:
    """(track, hệ số) cho một mục. Short giữ bảng BGM cố định như cũ; video dài
    chọn track trong pool và tính hệ số theo loudness đo thật của giọng đọc."""
    bgm, gain = BGM[row["series"]]
    if row.get("lane") != "long":
        return row.get("bgm", bgm), row.get("bgm_gain", gain)
    pool = LONG_BGM_POOL.get(row["series"]) or [bgm]
    bgm = row.get("bgm") or pool[int(hashlib.sha1(row["id"].encode()).hexdigest(), 16) % len(pool)]
    if row.get("bgm_gain") is not None:
        return bgm, row["bgm_gain"]
    from hyperframes_bridge import relative_bgm_gain  # noqa: PLC0415
    return bgm, relative_bgm_gain(wav, PROJECT_ROOT / bgm)


def remix_audio(row: dict, out_dir: Path) -> tuple[bool, str]:
    """Trộn lại tiếng cho video đã render (giữ nguyên hình, chép luồng video) --
    đổi nhạc/âm lượng mất vài giây thay vì render lại 10 phút."""
    rid = row["id"]
    mp4, wav = out_dir / f"{rid}.mp4", out_dir / f"{rid}.wav"
    if not mp4.exists() or not wav.exists():
        return True, "bỏ qua (chưa render)"
    from hyperframes_bridge import mux_audio  # noqa: PLC0415
    bgm, gain = pick_bgm(row, wav)
    dur = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["duration_s"]
    tmp = mp4.with_name(f"{rid}.remix.mp4")
    mux_audio(mp4, wav, tmp, bgm=PROJECT_ROOT / bgm, bgm_gain=gain, duration=dur)
    tmp.replace(mp4)
    rj = out_dir / f"{rid}.render.json"
    if rj.exists():
        meta = json.loads(rj.read_text(encoding="utf-8"))
        meta.update(bgm=str(PROJECT_ROOT / bgm), bgm_gain=gain)
        rj.write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")
    return True, f"trộn lại: {Path(bgm).name} x{gain}"


# Kênh Phong Thuỷ gọi con giáp bằng TÊN CHI của 12 con giáp Việt Nam (Tý, Sửu,
# Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi) -- không dịch ra con vật.
# "Tuổi Lợn", "tuổi Dê" lọt vào L_fs_01 và bị người xem chê. Tên con vật viết
# HOA giữa câu chỉ xuất hiện khi dùng làm tên tuổi, nên bắt theo cách đó.
# "Bạch Hổ" là linh vật trấn phương Tây (tứ linh), không phải cách gọi tuổi -> không chặn.
ZODIAC_ANIMAL = re.compile(r"(?<![.!?:]\s)(?<!^)(?<!Bạch\s)\b(Chuột|Trâu|Hổ|Cọp|Mèo|Rồng|Rắn|Ngựa|Dê|Khỉ|Gà|Chó|Lợn|Heo)\b")


def zodiac_naming_errors(lines: list[str]) -> list[str]:
    """Các câu gọi con giáp bằng tên con vật thay vì tên chi."""
    bad = []
    for n, line in enumerate(lines, 1):
        text = line.replace("**", "")
        if ZODIAC_ANIMAL.search(text) or re.search(r"(?i)\btuổi (chuột|trâu|hổ|cọp|mèo|rồng|rắn|ngựa|dê|khỉ|gà|chó|lợn|heo)\b", text):
            bad.append(f"câu {n}: {text[:70]}")
    return bad


CHI_NAME = re.compile(r"\b(Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)\b")


def crowded_chi_lines(lines: list[str], limit: int = 4) -> list[str]:
    """Câu nhắc >= 4 tên chi: TTS đọc lồng, hỏng cả 3 lần thử (f35_a, f36_a, f36_e ngày
    30/09/2026 -- mỗi lần mất 5-11 phút). Chặn trước khi tốn TTS: tách câu, tối đa 3 tên."""
    return [f"câu {n}: {l[:60]}" for n, l in enumerate(lines, 1)
            if len(CHI_NAME.findall(l.replace("**", ""))) >= limit]


def bare_lines(row: dict) -> list[int]:
    """Video dài: câu không sơ đồ, không ảnh (kể cả ảnh giữ từ câu trước), không chữ khoá **...**.
    Engine sẽ lấy mấy chữ ĐẦU câu làm tiêu đề lớn ("CÓ HAI CHIẾC CHÌA") -- lỗi F1/B1 01/10/2026."""
    import hyperframes_bridge as HB  # noqa: PLC0415
    script = row.get("script") or []
    lines = [{"sentence_id": i + 1, "start": i * 3.0, "end": i * 3.0 + 2.5, "words": [],
              "heading": t.startswith("**") and t.endswith("**") and t.count("**") == 2} for i, t in enumerate(script)]
    media = row.get("media") or {}
    HB.apply_visuals(lines, row.get("visuals") or {}, media)
    holds = HB.media_holds(lines, {int(k) for k in media})
    held = {k for i, j in holds.items() for k in range(i + 1, j + 1)}
    return [i + 1 for i, ln in enumerate(lines)
            if not ln.get("visual") and not ln.get("visual_cont") and str(i + 1) not in media
            and i not in held and not ln["heading"] and "**" not in script[i]]


def reveal_issues(row: dict) -> list[str]:
    """Sơ đồ hiện từng dòng theo {at, word}: engine bắt LẦN ĐẦU từ ấy xuất hiện trong câu. Lỗi F10 03/10/2026:
    "cửa nhà" (dòng 2) có chữ "nhà" sớm hơn "ngõ" (dòng 1) -> dòng 2 hiện trước; bảng có dòng đầu ở câu sau
    -> khung trống cả một câu. Chỉ cảnh báo, không chặn."""
    script = row.get("script") or []

    def pos(at: int, word: str | None) -> tuple[int, int]:
        if not word or not 0 < at <= len(script):
            return at, 0
        t = re.findall(r"\w+", script[at - 1].replace("**", "").lower())
        w = re.findall(r"\w+", word.lower())
        return at, next((i for i in range(len(t)) if t[i:i + len(w)] == w), 999)

    out = []
    for k, v in sorted((row.get("visuals") or {}).items(), key=lambda x: int(x[0])):
        seq = next((v[key] for key in ("rows", "items", "steps", "turns", "pins") if isinstance(v.get(key), list)), [])
        seq = [x for x in seq if isinstance(x, dict) and isinstance(x.get("at"), int)]
        seq += [v[s] for s in ("left", "right") if isinstance(v.get(s), dict) and isinstance(v[s].get("at"), int)]
        if not seq:
            continue
        ps = [pos(x["at"], x.get("word")) for x in seq]
        if any(p[1] == 999 for p in ps):
            out.append(f"câu {k} ({v.get('type')}): không thấy chữ {[x.get('word') for x in seq if pos(x['at'], x.get('word'))[1] == 999]}")
        elif ps != sorted(ps):
            out.append(f"câu {k} ({v.get('type')}): dòng hiện sai thứ tự {[x.get('word') for x in seq]}")
        if min(ps)[0] > int(k) and len(script[int(k) - 1].split()) > 14:
            out.append(f"câu {k} ({v.get('type')}): khung trống cả câu, dòng đầu ở câu {min(ps)[0]}")
    return out


# Công thức short v2 (đánh giá 28 ngày tới 03/10/2026, hf_shorts_report.py): short nào cũng dừng ở ~900-1.000 view
# (vòng thử của feed Shorts); bài bứt lên là bài xem hết > 90%. Bài yếu rơi người xem ở 20-50% thời lượng, đúng câu 2
# khi câu 2 là định nghĩa/thuật ngữ ("Nhà Phật gọi đó là tập khí", "Thái cực sinh lưỡng nghi"). Bài < 20 giây
# (FS) chỉ trung vị 122 view; 21-27 giây tốt nhất. Áp cho short lên lịch từ ngày dưới (short cũ đã đăng hết).
SHORT_V2_FROM = "2026-11-14"
# Giọng FS đọc chậm hơn: f40 102 tiếng = 33 giây; BUD b44 99 tiếng = 28 giây.
SHORT_V2_SYLLABLES = {"bud": (80, 102), "fs": (68, 88)}
DEFINE_OPENER = re.compile(r"(?i)^(\*\*)?(nhà phật|đạo phật|kinh [^ ]+|phật giáo|người xưa|phong thủy|kinh dịch)?\s*(gọi (đó|nó|đây) là|gọi là|được gọi là|nghĩa là|có nghĩa là|là (một|tên)|định nghĩa)")
DEFINE_IN2 = re.compile(r"(?i)\b(gọi (đó|nó|đây|là)|được gọi là|có nghĩa là|nghĩa là gì)\b")


def short_v2_issues(row: dict) -> list[str]:
    """Lỗi công thức short v2 (chặn render): câu 2 là định nghĩa, độ dài lệch SHORT_V2_SYLLABLES (~21-27 giây;
    b28_c 101 tiếng = 26 giây, short Phase D ~63 tiếng = 17 giây), thiếu `insight` (dòng đầu mô tả)."""
    if row.get("lane") == "long" or row.get("series") not in ("bud", "fs") or row.get("day", "") < SHORT_V2_FROM:
        return []
    script = [x.replace("**", "") for x in row.get("script") or []]
    out = []
    if len(script) >= 2 and (DEFINE_OPENER.search(script[1]) or DEFINE_IN2.search(script[1])):
        out.append(f"câu 2 là định nghĩa/thuật ngữ (người xem rơi ở đây) -- đưa thuật ngữ xuống câu 3: {script[1][:60]}")
    mute = set(row.get("silence") or [])   # câu hỏi lặng (ask) không có tiếng đọc
    n = sum(len(x.split()) for i, x in enumerate(script, 1) if i not in mute)
    lo, hi = SHORT_V2_SYLLABLES[row["series"]]
    if not lo <= n <= hi:
        out.append(f"{n} tiếng -- cần {lo}-{hi} (~21-27 giây; < 20 giây không được feed đẩy)")
    if len(script[0].split()) > 22 if script else False:
        out.append(f"câu 1 dài {len(script[0].split())} tiếng -- móc câu <= 22 tiếng")
    if not row.get("insight"):
        out.append("thiếu `insight` (câu trả lời một câu, dòng đầu mô tả)")
    return out


def render_one(row: dict, out_dir: Path, quality: str) -> tuple[bool, str]:
    rid = row["id"]
    if row.get("lane") == "long":
        for w in reveal_issues(row):
            print(f"    !! sơ đồ: {w}", flush=True)
    if row.get("lane") == "long" and (bare := bare_lines(row)):
        return False, (f"{len(bare)} câu trần (không sơ đồ/ảnh/chữ khoá) -- engine sẽ lấy chữ đầu câu làm tiêu đề: "
                       f"câu {bare[:12]} -- đánh **chữ khoá** hoặc gắn sơ đồ")
    if row.get("series") == "fs" and (bad := zodiac_naming_errors(row.get("script") or [])):
        return False, "gọi con giáp bằng tên con vật (phải dùng tên chi): " + " | ".join(bad[:3])
    if (v2 := short_v2_issues(row)):
        return False, "công thức short v2: " + " | ".join(v2)
    if (crowded := crowded_chi_lines(row.get("script") or [])):
        return False, "câu có >= 4 tên chi (TTS sẽ đọc lồng) -- tách câu: " + " | ".join(crowded[:3])
    mp4 = out_dir / f"{rid}.mp4"
    if mp4.exists() and not row.get("chapters"):   # video theo chương: từng chương tự quyết (băm đầu vào)
        return True, "đã có"
    lines = row.get("script") or []
    if not lines or lines == PLACEHOLDER_SCRIPT:
        return True, "bỏ qua (không có kịch bản)"

    txt = out_dir / f"{rid}.txt"
    txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    wav = out_dir / f"{rid}.wav"

    # Kịch bản đổi mà wav cũ còn đó là cái bẫy im lặng: số câu vẫn bằng số
    # segment nên không có lỗi nào nổ ra, video ra đời với TIẾNG CŨ ghép vào
    # CHỮ MỚI. Ghim hash kịch bản cạnh wav để bắt việc đó.
    digest = hashlib.sha1(("\n".join(lines) + json.dumps(row.get("tts") or {}, sort_keys=True)).encode("utf-8")).hexdigest()
    stamp = out_dir / f"{rid}.script.sha1"
    if wav.exists() and (not stamp.exists() or stamp.read_text(encoding="utf-8").strip() != digest):
        print(f"    kịch bản đã đổi kể từ lần TTS trước -- đọc lại", flush=True)
        wav.unlink(missing_ok=True)
    if not wav.exists() and row.get("tts"):
        # Video dài: TTS từng câu (hf_voice) -- giọng/tốc độ/khoảng nghỉ theo câu, giọng thứ hai cho lời trích.
        side = out_dir / f"{rid}.tts.json"
        side.write_text(json.dumps(row["tts"], ensure_ascii=False), encoding="utf-8")
        proc = subprocess.run([str(VENV_PYTHON), "hf_voice.py", str(txt), str(side), str(wav)],
                              cwd=PROJECT_ROOT, capture_output=True, text=True)
        if proc.returncode != 0 or not wav.exists():
            return False, f"TTS từng câu lỗi: {(proc.stdout + proc.stderr)[-300:]}"
    if not wav.exists() and not render_tts(txt, wav, lines, voice_for(row["series"])):
        return False, "TTS hỏng sau nhiều lần thử"
    stamp.write_text(digest + "\n", encoding="utf-8")

    bgm, gain = pick_bgm(row, wav)
    if row.get("chapters"):
        return render_chapters(row, out_dir, quality, txt, wav, bgm)
    cmd = [sys.executable, "hyperframes_bridge.py",
           "--script", str(txt), "--wav", str(wav), "--series", row["series"],
           "--style", row["style"], "--badge", row.get("badge", ""),
           "--footer", FOOTER[row["series"]], "--bgm", bgm, "--bgm-gain", str(gain),
           "--output", str(mp4), "--quality", quality]
    if row.get("lane"):
        cmd += ["--lane", row["lane"]]
    if row.get("kicker"):
        cmd += ["--kicker", row["kicker"]]
    # Figure và media do plan ghi sẵn -- runner chỉ chuyển tiếp nguyên vẹn,
    # không tự quyết định gì (ADR-0001).
    for key, flag in (("figures", "--figures"), ("figure_labels", "--figure-labels"),
                      ("media", "--media"), ("visuals", "--visuals")):
        if row.get(key):
            side = out_dir / f"{rid}.{key}.json"
            side.write_text(json.dumps(row[key], ensure_ascii=False), encoding="utf-8")
            cmd += [flag, str(side)]

    # Phase D (tiếng động bám cảnh, phụ đề cụm chữ, kết vòng lặp, câu hỏi lặng).
    opts = {k: row[k] for k in ("caps", "loop", "silence", "sfx", "sfx_gain", "sound", "kinetic") if k in row}
    if opts:
        side = out_dir / f"{rid}.opts.json"
        side.write_text(json.dumps(opts, ensure_ascii=False), encoding="utf-8")
        cmd += ["--opts", str(side)]

    # Video dài: HyperFrames nhiều worker mặc định ghi TỪNG khung hình ra đĩa rồi
    # mới mã hoá -- 5 phút cần hơn 8 GB tạm, đĩa gần đầy là hỏng (L_bud_03,
    # 29/09/2026). Bật luồng thẳng vào bộ mã hoá: không tốn đĩa, và nhanh hơn
    # (4,5 phút so với ~10 phút cho cùng video).
    env = dict(os.environ)
    if row.get("lane") == "long":
        env.setdefault("HF_CAPTURE_PARALLEL_STREAM", "true")
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        return False, f"render lỗi: {(proc.stdout + proc.stderr)[-300:]}"

    # Ghi công nguồn ảnh chỉ tồn tại trong kết quả của bridge. Không giữ lại
    # thì lúc soạn mô tả video phải dựng lại từ đầu -- mà dựng lại nghĩa là
    # viết lần thứ hai cùng một logic, rồi hai bản lệch nhau.
    for line in reversed((proc.stdout or "").strip().splitlines()):
        if line.startswith("{"):
            try:
                (out_dir / f"{rid}.render.json").write_text(line + "\n", encoding="utf-8")
            except OSError:
                pass
            break
    return True, "xong"


FPS = 30


def _engine_sig() -> str:
    """Băm mã dựng hình: sửa engine/longform/CSS/style thì mọi chương render lại (không đoán tay)."""
    comp = PROJECT_ROOT / "hyperframes_short" / "compositions"
    h = hashlib.sha1()
    for f in sorted(comp.glob("*.js")) + sorted(comp.glob("*.css")) + sorted(comp.glob("*_long.html")):
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _remap_at(spec, shift: int):
    """Đổi số câu tuyệt đối (at/until) trong một sơ đồ sang số câu trong chương."""
    if isinstance(spec, dict):
        return {k: (v - shift if k in ("at", "until") and isinstance(v, int) else _remap_at(v, shift)) for k, v in spec.items()}
    if isinstance(spec, list):
        return [_remap_at(x, shift) for x in spec]
    return spec


def chapter_spans(lines: list[str], segs: list[dict], total: float) -> list[tuple[int, int, float, float]]:
    """[(câu đầu, câu sau cuối, giây đầu, giây cuối)] -- cắt ở tiêu đề chương (câu in đậm trọn câu),
    mốc cắt nằm giữa khoảng lặng trước tiêu đề và ĐÚNG khung hình (1/30 s) để nối không lệch tiếng."""
    heads = [i for i, l in enumerate(lines) if i and l.startswith("**") and l.endswith("**") and l.count("**") == 2]
    firsts = [0] + heads
    out = []
    for c, a in enumerate(firsts):
        b = firsts[c + 1] if c + 1 < len(firsts) else len(lines)
        t0 = 0.0 if a == 0 else round((segs[a - 1]["end"] + segs[a]["start"]) / 2 * FPS) / FPS
        t1 = (round((segs[b - 1]["end"] + segs[b]["start"]) / 2 * FPS) / FPS) if b < len(lines) else int(total * FPS) / FPS
        out.append((a, b, t0, t1))
    return out


def pacing(row: dict, segs: list[dict]) -> tuple[dict, list[str]]:
    """Nhịp hình (SS-tier): % thời lượng theo kiểu cảnh, độ dài cảnh. Ngưỡng rút từ đo F1/B1 01/10/2026
    (68% ba sơ đồ lặp khuôn; 35% chữ khoá trên nền trơn; cảnh đứng 64 giây)."""
    import collections  # noqa: PLC0415
    import hyperframes_bridge as HB  # noqa: PLC0415
    script, n = row["script"], len(row["script"])
    lines = [{"sentence_id": i + 1, "start": segs[i]["start"], "end": segs[i]["end"], "words": [],
              "heading": script[i].startswith("**") and script[i].endswith("**") and script[i].count("**") == 2} for i in range(n)]
    media = row.get("media") or {}
    HB.apply_visuals(lines, row.get("visuals") or {}, media)
    holds = HB.media_holds(lines, {int(k) for k in media})
    held = {k for i, j in holds.items() for k in range(i + 1, j + 1)}
    sec, shots, prev, cur = collections.Counter(), [], None, 0.0
    for i, ln in enumerate(lines):
        d = (segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]) - ln["start"]
        if ln["heading"]:
            k = "chương"
        elif ln.get("visual"):
            k = ln["visual"]["type"]
        elif ln.get("visual_cont"):
            k = lines[ln["visual_cont"] - 1]["visual"]["type"]
        elif str(i + 1) in media or i in held:
            k = "ảnh/clip"
        else:
            k = "chữ khoá"
        sec[k] += d
        if k != prev or not ln.get("visual_cont"):
            if prev is not None:
                shots.append(cur)
            cur = 0.0
        cur += d
        prev = k
    shots.append(cur)
    tot = sum(sec.values()) or 1
    share = {k: v / tot for k, v in sec.items()}
    rep = {"phút": round(tot / 60, 1), "cảnh": len(shots), "TB giây/cảnh": round(tot / len(shots), 1),
           "dài nhất": round(max(shots), 1), "tỉ lệ": {k: round(v * 100, 1) for k, v in sorted(share.items(), key=lambda x: -x[1])}}
    # Cảnh mang ẢNH khác nhau (bảo tàng, nạp âm, tư liệu) không phải "lặp khuôn" -- mỗi lần một hình mới.
    bad = [f"{k} chiếm {v * 100:.0f}% (> 25%)" for k, v in share.items()
           if v > .25 and k not in ("ảnh/clip", "museum", "napam", "doc", "photo", "relic")]
    if share.get("chữ khoá", 0) > .15 and not row.get("kinetic"):
        bad.append(f"chữ khoá đứng yên {share['chữ khoá'] * 100:.0f}% (> 15%) -- bật \"kinetic\" hoặc thêm hình")
    if max(shots) > 25:
        bad.append(f"có cảnh đứng {max(shots):.0f}s (> 25s) -- chèn nhịp cắt")
    return rep, bad


def chapter_key(row: dict, a: int, b: int, t0: float, t1: float, quality: str) -> str:
    """Băm đầu vào một chương (câu a+1..b): đổi chữ/sơ đồ/ảnh/khung giờ/engine thì render lại."""
    subs = {kind: {str(int(k) - a): _remap_at(v, a) for k, v in (row.get(kind) or {}).items() if a < int(k) <= b}
            for kind in ("media", "visuals")}
    return hashlib.sha1(json.dumps([row["script"][a:b], subs, row["style"], round(t0, 3), round(t1, 3), quality, _engine_sig()]
                                   + ([True] if row.get("kinetic") else [])
                                   + ([{"kicker": row["kicker"]}] if row.get("kicker") else []),
                                   ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def render_chapters(row: dict, out_dir: Path, quality: str, txt: Path, wav: Path, bgm: str) -> tuple[bool, str]:
    """Video 30+ phút: render từng chương (chạy lại được từng chương), nối hình, trộn tiếng MỘT lần."""
    import soundfile as sf  # noqa: PLC0415
    rid = row["id"]
    lines = row["script"]
    man = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))
    segs, total = man["segments"], float(man["duration_s"])
    audio, sr = sf.read(wav, dtype="float32")
    cdir = out_dir / f"{rid}_chapters"
    cdir.mkdir(exist_ok=True)
    spans = chapter_spans(lines, segs, total)
    rep, bad = pacing(row, segs)
    print(f"    nhịp hình: {rep}", flush=True)
    for x in bad:
        print(f"    !! nhịp hình: {x}", flush=True)
    if bad and row.get("pacing") == "strict":
        return False, "nhịp hình chưa đạt: " + "; ".join(bad)
    silence = [int(x) for x in row.get("silence") or []]
    credits, parts = [], []
    changed = False
    env = dict(os.environ, HF_CAPTURE_PARALLEL_STREAM="true")
    for c, (a, b, t0, t1) in enumerate(spans):
        name = f"ch{c:02d}"
        mp4 = cdir / f"{name}.mp4"
        parts.append(mp4)
        meta = cdir / f"{name}.render.json"
        key = chapter_key(row, a, b, t0, t1, quality)
        if mp4.exists() and meta.exists():
            m0 = json.loads(meta.read_text(encoding="utf-8"))
            if m0.get("input_sha1") == key:
                credits += m0.get("media_credits", [])
                continue
            print(f"    {name}: nội dung/engine đã đổi -- render lại", flush=True)
        changed = True
        ctxt, cwav = cdir / f"{name}.txt", cdir / f"{name}.wav"
        ctxt.write_text("\n".join(lines[a:b]) + "\n", encoding="utf-8")
        sf.write(cwav, audio[int(round(t0 * sr)):int(round(t1 * sr))], sr)
        cman = dict(man, duration_s=round(t1 - t0, 4), output_file=cwav.name,
                    segments=[dict(sg, start=round(sg["start"] - t0, 3), end=round(sg["end"] - t0, 3)) for sg in segs[a:b]])
        cwav.with_suffix(".json").write_text(json.dumps(cman, ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, "hyperframes_bridge.py", "--script", str(ctxt), "--wav", str(cwav), "--series", row["series"],
               "--style", row["style"], "--badge", row.get("badge", ""), "--footer", FOOTER[row["series"]],
               "--bgm", bgm, "--bgm-gain", "0", "--output", str(mp4), "--quality", quality, "--lane", "long"]
        if row.get("kicker"):   # nhãn góc riêng của video (mặc định theo lane: "12 CON GIÁP · 2027" chỉ hợp F2/F3)
            cmd += ["--kicker", row["kicker"]]
        for kind, flag in (("media", "--media"), ("visuals", "--visuals")):   # KHÔNG dùng tên `key` -- đè băm chương
            sub = {str(int(k) - a): _remap_at(v, a) for k, v in (row.get(kind) or {}).items() if a < int(k) <= b}
            if sub:
                side = cdir / f"{name}.{kind}.json"
                side.write_text(json.dumps(sub, ensure_ascii=False), encoding="utf-8")
                cmd += [flag, str(side)]
        base = sum(1 for l in lines[:a] if l.startswith("**") and l.endswith("**") and l.count("**") == 2)
        opts = {"video_only": True, "seg_off": t0, "seg_total": total, "chapter_base": base, "kinetic": bool(row.get("kinetic")),
                "silence": [x - a for x in silence if a < x <= b]}
        side = cdir / f"{name}.opts.json"
        side.write_text(json.dumps(opts), encoding="utf-8")
        cmd += ["--opts", str(side)]
        t = time.time()
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, env=env)
        if proc.returncode != 0 or not mp4.exists():
            return False, f"chương {name} lỗi: {(proc.stdout + proc.stderr)[-400:]}"
        for ln in reversed((proc.stdout or "").strip().splitlines()):
            if ln.startswith("{"):
                res = json.loads(ln)
                res["input_sha1"] = key
                meta.write_text(json.dumps(res, ensure_ascii=False) + "\n", encoding="utf-8")
                credits += res.get("media_credits", [])
                break
        print(f"    {name}: câu {a + 1}-{b}, {t1 - t0:.0f}s, render {time.time() - t:.0f}s", flush=True)

    if not changed and (out_dir / f"{rid}.mp4").exists():
        return True, "đã có"
    # Nối hình (cùng bộ mã hoá, cùng thông số -> chép luồng), rồi trộn tiếng cả video một lần.
    lst = cdir / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    silent = cdir / "silent.mp4"
    res = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)],
                         capture_output=True, text=True)
    if res.returncode != 0:
        return False, f"nối chương lỗi: {res.stderr[-300:]}"
    import hyperframes_bridge as HB  # noqa: PLC0415
    import hf_foley  # noqa: PLC0415
    glines = HB.build_lines(txt, wav.with_suffix(".json"), align_audio=wav)
    HB.apply_visuals(glines, row.get("visuals") or {}, row.get("media") or {})
    for ln in glines:
        if str(ln["sentence_id"]) in (row.get("media") or {}):
            ln["media"] = {"query": ""}
    mixed = cdir / "mix.wav"
    hf_foley.mix_long(glines, row["series"], wav, PROJECT_ROOT / bgm if bgm else None, total, row.get("sound") or {},
                      set(silence), mixed, seed=hashlib.sha1(rid.encode()).digest()[0])
    mp4 = out_dir / f"{rid}.mp4"
    HB.mux_audio(silent, mixed, mp4, duration=total)
    (out_dir / f"{rid}.render.json").write_text(json.dumps(
        {"ok": True, "output": str(mp4), "duration_s": total, "style": row["style"], "chapters": len(spans),
         "media_credits": list(dict.fromkeys(c for c in credits if c)), "bgm": str(PROJECT_ROOT / bgm) if bgm else "",
         "sound": "foley-v1"}, ensure_ascii=False) + "\n", encoding="utf-8")
    return True, "xong"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_dir", help="Thư mục chứa plan_*.json (và thư mục out/)")
    ap.add_argument("--only", default=None, help="Chỉ dựng mục có id bắt đầu bằng chuỗi này")
    ap.add_argument("--quality", default="looks", choices=["draft", "looks", "delivery"])
    ap.add_argument("--remix-audio", action="store_true",
                    help="Chỉ trộn lại tiếng (nhạc nền theo chính sách hiện tại) cho video đã render")
    args = ap.parse_args()

    plan_dir = Path(args.plan_dir)
    out_dir = plan_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [r for r in load_rows(plan_dir) if not args.only or r["id"].startswith(args.only)]
    print(f"{len(rows)} mục trong {plan_dir}\n", flush=True)

    failed = []
    for i, row in enumerate(rows, start=1):
        t0 = time.time()
        ok, note = (remix_audio(row, out_dir) if args.remix_audio
                    else render_one(row, out_dir, args.quality))
        nfig = sum(1 for f in (row.get("figures") or {}).values() if f.get("type") != "none")
        mark = "✓" if ok else "✗"
        print(f"[{i}/{len(rows)}] {mark} {row['id']:8s} {row.get('style','?'):13s} "
              f"{time.time()-t0:5.1f}s {nfig} fig  {note if note != 'xong' else row.get('title','')[:42]}",
              flush=True)
        if not ok:
            failed.append((row["id"], note))

    done = len(list(out_dir.glob("*.mp4")))
    print(f"\nXong: {done} video trong {out_dir}", flush=True)
    for rid, note in failed:
        print(f"  HỎNG {rid}: {note}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
