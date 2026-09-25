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
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VOICE = "Tuyen"
TTS_HELPER = PROJECT_ROOT / "_short_tts_render.py"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"

BGM = {"law": ("bgm/deliberate_thought.mp3", 0.17),
       "scam": ("bgm/thinking_music.mp3", 0.24),
       "case": ("bgm/deliberate_thought.mp3", 0.17),
       "tale": ("bgm/thinking_music.mp3", 0.20)}
FOOTER = {"law": "Phổ biến kiến thức pháp luật",
          "scam": "Nhận ra kịch bản trước khi chuyển tiền",
          "case": "Dẫn theo hồ sơ công khai",
          "tale": "Truyện hư cấu — nhân vật và tình tiết do tưởng tượng"}

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


def render_tts(txt: Path, wav: Path, script_lines: list[str]) -> bool:
    """TTS kèm thử lại khi phát hiện đọc lồng. Trả False nếu vẫn hỏng."""
    for attempt in range(1, MAX_TTS_ATTEMPTS + 1):
        for stale in (wav, wav.with_suffix(".json")):
            stale.unlink(missing_ok=True)
        proc = subprocess.run(
            [str(VENV_PYTHON), str(TTS_HELPER), "--text-file", str(txt),
             "--voice", VOICE, "--output-wav", str(wav)],
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


def render_one(row: dict, out_dir: Path, quality: str) -> tuple[bool, str]:
    rid = row["id"]
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
    if not wav.exists() and not render_tts(txt, wav, lines):
        return False, "TTS hỏng sau nhiều lần thử"
    stamp.write_text(digest + "\n", encoding="utf-8")

    bgm, gain = BGM[row["series"]]
    cmd = [sys.executable, "hyperframes_bridge.py",
           "--script", str(txt), "--wav", str(wav), "--series", row["series"],
           "--style", row["style"], "--badge", row.get("badge", ""),
           "--footer", FOOTER[row["series"]], "--bgm", bgm, "--bgm-gain", str(gain),
           "--output", str(mp4), "--quality", quality]
    # Figure do hf_director.py ghi sẵn vào plan -- runner chỉ chuyển tiếp
    # nguyên vẹn, không tự quyết định gì (ADR-0001).
    for key, flag in (("figures", "--figures"), ("figure_labels", "--figure-labels")):
        if row.get(key):
            side = out_dir / f"{rid}.{key}.json"
            side.write_text(json.dumps(row[key], ensure_ascii=False), encoding="utf-8")
            cmd += [flag, str(side)]

    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, f"render lỗi: {(proc.stdout + proc.stderr)[-300:]}"
    return True, "xong"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_dir", help="Thư mục chứa plan_*.json (và thư mục out/)")
    ap.add_argument("--only", default=None, help="Chỉ dựng mục có id bắt đầu bằng chuỗi này")
    ap.add_argument("--quality", default="looks", choices=["draft", "looks", "delivery"])
    args = ap.parse_args()

    plan_dir = Path(args.plan_dir)
    out_dir = plan_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [r for r in load_rows(plan_dir) if not args.only or r["id"].startswith(args.only)]
    print(f"{len(rows)} mục trong {plan_dir}\n", flush=True)

    failed = []
    for i, row in enumerate(rows, start=1):
        t0 = time.time()
        ok, note = render_one(row, out_dir, args.quality)
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
