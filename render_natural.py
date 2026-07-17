"""
CLI đứng riêng để render 1 file text -> 1 file audio. Lõi thực (chunk tự
nhiên, QA, retry, SRT/manifest) nằm ở render_engine.py — file này chỉ là
wrapper mỏng để dùng tay/debug hoặc gọi từ script khác qua subprocess khi
cần cô lập tiến trình (vd 1 job riêng biệt trên máy khác).

Lưu ý hiệu năng: mỗi lần chạy file này là 1 process mới -> load model từ
đầu (~6-9s). Nếu cần render NHIỀU file/đoạn liên tiếp, dùng thẳng
`render_engine.RenderSession` trong cùng 1 process (xem process_drive_queue.py
/ process_short_queue.py) để chỉ load model 1 lần.

Usage:
    uv run python render_natural.py content/03_AUDIO_SCRIPT_TTS.txt \
        --voice Binh --out output/final.wav
"""
import argparse
import sys
from pathlib import Path

from render_engine import RenderSession, upload_paths_to_drive

DEFAULT_DRIVE_REMOTE = "gdrive:TTS-Output/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("textfile")
    ap.add_argument("--voice", default="Binh")
    ap.add_argument("--out", default="output/render_natural.wav")
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--upload-drive", dest="upload_drive", action="store_true", default=True,
                     help="Tự upload wav+srt+json lên Drive qua rclone (mặc định: bật)")
    ap.add_argument("--no-upload-drive", dest="upload_drive", action="store_false")
    ap.add_argument("--drive-remote", default=DEFAULT_DRIVE_REMOTE,
                     help=f"Remote rclone đích để upload (mặc định: {DEFAULT_DRIVE_REMOTE})")
    args = ap.parse_args()

    text = Path(args.textfile).read_text(encoding="utf-8")
    out_path = Path(args.out)

    text_stem = Path(args.textfile).stem
    cache_dir = Path(args.cache_dir or f"chunks_cache/{args.voice}/{text_stem}")

    session = RenderSession(args.voice)
    result = session.render_text(text, out_path, cache_dir=cache_dir)

    if args.upload_drive:
        upload_paths_to_drive(
            [result.out_path, result.srt_path, result.manifest_path],
            args.drive_remote,
        )

    return 1 if not result.success else 0


if __name__ == "__main__":
    sys.exit(main())
