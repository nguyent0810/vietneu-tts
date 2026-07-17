"""
Xử lý 1 hàng đợi "Long" (mỗi file input = 1 file audio output). Cung cấp hàm
`process_long_folder()` tái sử dụng được (dùng trong process_topics.py) và
CLI đứng riêng để chạy trực tiếp trên TTS-Input/ / TTS-Output/ gốc (giữ lại
cho tương thích ngược / debug thủ công).

Nhận 1 `RenderSession` đã load sẵn (model chỉ load 1 lần, tái dùng cho mọi
file trong folder) thay vì subprocess ra `render_natural.py` cho từng file.

Rule:
  - Bỏ qua file đã có sẵn output tương ứng (không tải/render lại)
  - Sau khi render+upload xong, chuyển input vào <input_remote>processed/
    để không bị quét lại lần sau

Usage (đứng riêng):
    uv run python process_drive_queue.py [--voice Binh]
"""
import argparse
import sys
from pathlib import Path

from drive_utils import rclone, list_pending_files, list_files_in
from render_engine import RenderSession, upload_paths_to_drive

INPUT_REMOTE = "gdrive:TTS-Input/"
OUTPUT_REMOTE = "gdrive:TTS-Output/"
LOCAL_STAGING = Path("drive_input")
LOCAL_OUTPUT_DIR = Path("output")


def process_long_folder(
    session: "RenderSession",
    input_remote: str,
    output_remote: str,
    local_staging: Path = LOCAL_STAGING,
    local_output_dir: Path = LOCAL_OUTPUT_DIR,
    label: str = "",
    manifest_extra: dict = None,
) -> tuple[int, int, int]:
    """Xử lý 1 folder Long: mỗi file .txt trong input_remote -> 1 file .wav
    (+ .srt + .json) trong output_remote. Trả về (n_rendered, n_skipped, n_failed)."""
    processed_remote = f"{input_remote}processed/"
    tag = f"[{label}] " if label else ""

    pending = list_pending_files(input_remote)
    if not pending:
        print(f"{tag}Không có file mới trong {input_remote}.", flush=True)
        return 0, 0, 0

    print(f"{tag}Tìm thấy {len(pending)} file mới: {pending}", flush=True)
    local_staging.mkdir(parents=True, exist_ok=True)

    existing_outputs = list_files_in(output_remote)
    print(f"{tag}{output_remote} hiện có {len(existing_outputs)} file.", flush=True)

    n_rendered = n_skipped = n_failed = 0

    for name in pending:
        print(f"\n{tag}=== Xử lý: {name} ===", flush=True)
        stem = Path(name).stem

        expected_output_name = stem + ".wav"
        if expected_output_name in existing_outputs:
            print(f"{tag}Đã có {expected_output_name} trong {output_remote} — bỏ qua tải/render, "
                  f"chuyển thẳng input vào processed/.", flush=True)
            mv = rclone("moveto", f"{input_remote}{name}", f"{processed_remote}{name}")
            if mv.returncode != 0:
                print(f"{tag}CẢNH BÁO: không chuyển được {name} vào processed/ ({mv.stderr.strip()}).", flush=True)
            n_skipped += 1
            continue

        local_path = local_staging / name
        dl = rclone("copyto", f"{input_remote}{name}", str(local_path))
        if dl.returncode != 0:
            print(f"{tag}LỖI tải {name}: {dl.stderr.strip()} — bỏ qua file này.", flush=True)
            n_failed += 1
            continue

        text = local_path.read_text(encoding="utf-8")
        out_path = local_output_dir / expected_output_name
        cache_dir = Path(f"chunks_cache/{session.voice_name}/{label.replace('/', '_') or 'root'}/{stem}")

        extra = {"content_type": "Long", "source_file": name}
        if manifest_extra:
            extra.update(manifest_extra)

        result = session.render_text(text, out_path, cache_dir=cache_dir, manifest_extra=extra)

        upload_paths_to_drive([result.out_path, result.srt_path, result.manifest_path], output_remote)

        if not result.success:
            print(f"{tag}LỖI QA {name} (vẫn nghi lỗi sau retry) — GIỮ NGUYÊN trong {input_remote} "
                  f"để thử lại lần sau.", flush=True)
            n_failed += 1
            continue

        existing_outputs.add(expected_output_name)  # tránh trùng nếu batch có tên lặp

        mv = rclone("moveto", f"{input_remote}{name}", f"{processed_remote}{name}")
        if mv.returncode != 0:
            print(f"{tag}CẢNH BÁO: render xong nhưng không chuyển được {name} vào processed/ "
                  f"({mv.stderr.strip()}) — file sẽ bị xử lý lại lần sau, tự kiểm tra thủ công.", flush=True)
        else:
            print(f"{tag}Xong: {name} -> {out_path} -> {output_remote}, input đã chuyển vào processed/", flush=True)
        n_rendered += 1

    print(f"\n{tag}Hoàn tất: {n_rendered} render mới, {n_skipped} bỏ qua (đã có output), "
          f"{n_failed} lỗi (còn lại trong {input_remote} để thử lại).", flush=True)
    return n_rendered, n_skipped, n_failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="Binh")
    args = ap.parse_args()

    session = RenderSession(args.voice)
    n_rendered, n_skipped, n_failed = process_long_folder(session, INPUT_REMOTE, OUTPUT_REMOTE)
    return 1 if n_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
