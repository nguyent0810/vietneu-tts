"""Khung hình tại các câu có visual + vài câu ảnh -> sheet 4 cột để soát render Long.

    .venv/bin/python tools/long/qa_sheet.py L_fs_t11_ty /path/qa_ty.jpg
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "output/cl_staging/long"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan_id")
    parser.add_argument("output")
    args = parser.parse_args(argv)
    from PIL import Image, ImageDraw

    pid, out = args.plan_id, args.output
    r = json.loads((DATA / f"plan_{pid}.json").read_text(encoding="utf-8"))[0]
    tts = json.loads((DATA / f"out/{pid}.json").read_text(encoding="utf-8"))
    segs = tts.get("segments") or tts.get("lines") or []
    starts = [float(s.get("start", s.get("t0", 0))) if isinstance(s, dict) else 0.0 for s in segs]
    want = sorted({1, 3, 8, 14} | {int(k) for k in r["visuals"]}
                  | {int(k) for k, v in r["media"].items() if isinstance(v, dict) and v.get("pan")})
    tiles = []
    with tempfile.TemporaryDirectory() as tmp:
        for ln in want:
            if ln - 1 >= len(starts):
                continue
            f = Path(tmp) / f"{ln}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{starts[ln - 1] + 1.2:.2f}", "-i", str(DATA / f"out/{pid}.mp4"),
                            "-frames:v", "1", "-vf", "scale=480:-1", str(f)], check=False)
            if f.exists():
                im = Image.open(f).copy()
                ImageDraw.Draw(im).text((6, 6), f"{ln} {r['visuals'].get(str(ln), {}).get('type', '')}", fill="yellow")
                tiles.append(im)
    rows = max(1, (len(tiles) + 3) // 4)
    sheet = Image.new("RGB", (4 * 484, rows * 274), "black")
    for k, im in enumerate(tiles):
        sheet.paste(im, ((k % 4) * 484, (k // 4) * 274))
    sheet.save(out)
    print(len(tiles), want)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
