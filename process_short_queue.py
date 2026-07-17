"""
Xử lý 1 hàng đợi "Short" (mỗi file input chứa nhiều đoạn ngắn ngăn cách bằng
dòng "*** N", mỗi đoạn render thành 1 file audio riêng). Cung cấp hàm
`process_short_folder()` tái sử dụng được (dùng trong process_topics.py) và
CLI đứng riêng để chạy trực tiếp trên SHORT/input/ / SHORT/output/ gốc (giữ
lại cho tương thích ngược / debug thủ công).

Nhận 1 `RenderSession` đã load sẵn — model chỉ load 1 lần, tái dùng cho MỌI
đoạn của MỌI file trong folder (trước đây mỗi đoạn là 1 subprocess riêng,
load lại model ~6-9s/đoạn — với 30 đoạn tốn 3-4 phút chỉ để load model).

Tất cả audio của CÙNG 1 file input được gộp vào 1 thư mục riêng:
<output_remote>{tên_file_gốc}/ — giống cách input được gom vào
<input_remote>processed/ sau khi xong.

Usage (đứng riêng):
    uv run python process_short_queue.py [--voice Binh]
"""
import argparse
import re
import sys
from pathlib import Path

from drive_utils import rclone, list_pending_files, list_files_in
from render_engine import RenderSession, upload_paths_to_drive

INPUT_REMOTE = "gdrive:SHORT/input/"
OUTPUT_REMOTE = "gdrive:SHORT/output/processed/"
LOCAL_STAGING = Path("drive_input/SHORT")
LOCAL_OUTPUT_DIR = Path("output/SHORT/processed")

MARKER_RE = re.compile(r"^\*\*\*\s*(\d+)\s*$", re.MULTILINE)


def split_segments(text: str) -> list[tuple[int, str]]:
    """Tách text theo dòng "*** N" -> [(N, nội_dung_đoạn), ...]."""
    matches = list(MARKER_RE.finditer(text))
    segments = []
    for i, m in enumerate(matches):
        idx = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            segments.append((idx, content))
    return segments


def process_short_folder(
    session: "RenderSession",
    input_remote: str,
    output_remote: str,
    local_staging: Path = LOCAL_STAGING,
    local_output_dir: Path = LOCAL_OUTPUT_DIR,
    label: str = "",
    manifest_extra: dict = None,
) -> tuple[int, int, int]:
    """Xử lý 1 folder Short. Trả về (n_rendered, n_skipped, n_failed)."""
    processed_remote = f"{input_remote}processed/"
    tag = f"[{label}] " if label else ""

    pending = list_pending_files(input_remote)
    if not pending:
        print(f"{tag}Không có file mới trong {input_remote}.", flush=True)
        return 0, 0, 0

    print(f"{tag}Tìm thấy {len(pending)} file mới: {pending}", flush=True)
    local_staging.mkdir(parents=True, exist_ok=True)

    n_rendered = n_skipped = n_failed = 0

    for name in pending:
        print(f"\n{tag}=== File nguồn: {name} ===", flush=True)
        stem = Path(name).stem
        out_folder_remote = f"{output_remote}{stem}/"
        out_folder_local = local_output_dir / stem

        local_src = local_staging / name
        dl = rclone("copyto", f"{input_remote}{name}", str(local_src))
        if dl.returncode != 0:
            print(f"{tag}LỖI tải {name}: {dl.stderr.strip()} — bỏ qua file này.", flush=True)
            n_failed += 1
            continue

        text = local_src.read_text(encoding="utf-8")
        segments = split_segments(text)
        if not segments:
            print(f"{tag}Không tìm thấy đoạn nào phân cách bởi '*** N' trong {name} — bỏ qua.", flush=True)
            n_failed += 1
            continue
        print(f"{tag}{len(segments)} đoạn được tách (đánh dấu *** 1.. *** {segments[-1][0]}).", flush=True)

        existing_outputs = list_files_in(f"{output_remote}{stem}/")
        print(f"{tag}{out_folder_remote} hiện có {len(existing_outputs)} file.", flush=True)

        file_had_failure = False
        for idx, content in segments:
            out_name = f"{idx}_{stem}.wav"
            print(f"\n{tag}--- Đoạn {idx}/{len(segments)}: {out_name} ---", flush=True)

            if out_name in existing_outputs:
                print(f"{tag}Đã có {out_name} trong {out_folder_remote} — bỏ qua tải/render.", flush=True)
                n_skipped += 1
                continue

            out_path = out_folder_local / out_name
            cache_dir = Path(f"chunks_cache/{session.voice_name}/{label.replace('/', '_') or 'root'}/{stem}/{idx}")

            extra = {"content_type": "Short", "source_file": name, "segment_index": idx}
            if manifest_extra:
                extra.update(manifest_extra)

            result = session.render_text(content, out_path, cache_dir=cache_dir, manifest_extra=extra)

            upload_paths_to_drive(
                [result.out_path, result.srt_path, result.manifest_path], out_folder_remote
            )

            if not result.success:
                print(f"{tag}LỖI QA đoạn {idx} của {name} (vẫn nghi lỗi sau retry).", flush=True)
                n_failed += 1
                file_had_failure = True
                continue

            existing_outputs.add(out_name)
            n_rendered += 1

        if file_had_failure:
            print(f"\n{tag}{name}: có đoạn lỗi — GIỮ NGUYÊN trong {input_remote} để chạy lại sau "
                  f"(các đoạn đã xong sẽ tự bỏ qua nhờ rule skip-if-exists).", flush=True)
            continue

        mv = rclone("moveto", f"{input_remote}{name}", f"{processed_remote}{name}")
        if mv.returncode != 0:
            print(f"{tag}CẢNH BÁO: xong hết đoạn nhưng không chuyển được {name} vào processed/ "
                  f"({mv.stderr.strip()}).", flush=True)
        else:
            print(f"\n{tag}{name}: TẤT CẢ {len(segments)} đoạn đã xong, input đã chuyển vào processed/.", flush=True)

    print(f"\n{tag}Hoàn tất: {n_rendered} đoạn render mới, {n_skipped} bỏ qua (đã có output), "
          f"{n_failed} lỗi.", flush=True)
    return n_rendered, n_skipped, n_failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="Binh")
    args = ap.parse_args()

    session = RenderSession(args.voice)
    n_rendered, n_skipped, n_failed = process_short_folder(session, INPUT_REMOTE, OUTPUT_REMOTE)
    return 1 if n_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
