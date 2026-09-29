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
ZODIAC_ANIMAL = re.compile(r"(?<![.!?:]\s)(?<!^)\b(Chuột|Trâu|Hổ|Cọp|Mèo|Rồng|Rắn|Ngựa|Dê|Khỉ|Gà|Chó|Lợn|Heo)\b")


def zodiac_naming_errors(lines: list[str]) -> list[str]:
    """Các câu gọi con giáp bằng tên con vật thay vì tên chi."""
    bad = []
    for n, line in enumerate(lines, 1):
        text = line.replace("**", "")
        if ZODIAC_ANIMAL.search(text) or re.search(r"(?i)\btuổi (chuột|trâu|hổ|cọp|mèo|rồng|rắn|ngựa|dê|khỉ|gà|chó|lợn|heo)\b", text):
            bad.append(f"câu {n}: {text[:70]}")
    return bad


def render_one(row: dict, out_dir: Path, quality: str) -> tuple[bool, str]:
    rid = row["id"]
    if row.get("series") == "fs" and (bad := zodiac_naming_errors(row.get("script") or [])):
        return False, "gọi con giáp bằng tên con vật (phải dùng tên chi): " + " | ".join(bad[:3])
    mp4 = out_dir / f"{rid}.mp4"
    if mp4.exists():
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
    digest = hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()
    stamp = out_dir / f"{rid}.script.sha1"
    if wav.exists() and (not stamp.exists() or stamp.read_text(encoding="utf-8").strip() != digest):
        print(f"    kịch bản đã đổi kể từ lần TTS trước -- đọc lại", flush=True)
        wav.unlink(missing_ok=True)
    if not wav.exists() and not render_tts(txt, wav, lines, voice_for(row["series"])):
        return False, "TTS hỏng sau nhiều lần thử"
    stamp.write_text(digest + "\n", encoding="utf-8")

    bgm, gain = pick_bgm(row, wav)
    cmd = [sys.executable, "hyperframes_bridge.py",
           "--script", str(txt), "--wav", str(wav), "--series", row["series"],
           "--style", row["style"], "--badge", row.get("badge", ""),
           "--footer", FOOTER[row["series"]], "--bgm", bgm, "--bgm-gain", str(gain),
           "--output", str(mp4), "--quality", quality]
    if row.get("lane"):
        cmd += ["--lane", row["lane"]]
    # Figure và media do plan ghi sẵn -- runner chỉ chuyển tiếp nguyên vẹn,
    # không tự quyết định gì (ADR-0001).
    for key, flag in (("figures", "--figures"), ("figure_labels", "--figure-labels"),
                      ("media", "--media"), ("visuals", "--visuals")):
        if row.get(key):
            side = out_dir / f"{rid}.{key}.json"
            side.write_text(json.dumps(row[key], ensure_ascii=False), encoding="utf-8")
            cmd += [flag, str(side)]

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
