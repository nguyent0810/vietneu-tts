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
    local_source_files: list = None,
) -> tuple[int, int, int]:
    """Xử lý 1 folder Long: mỗi file .txt -> 1 file .wav (+ .srt + .json)
    trong output_remote. Trả về (n_rendered, n_skipped, n_failed).

    Nếu ``local_source_files`` được truyền (list[Path]) — dùng cho nguồn
    pull-only như Content-Creator repo — bỏ qua hoàn toàn bước liệt kê/tải
    từ input_remote và bước chuyển vào processed/ (không có khái niệm
    processed/ ở nguồn pull-only, "đã xử lý" được suy ra lại mỗi lần từ việc
    output đã tồn tại hay chưa, giống hệt cách nguồn Drive vẫn hoạt động)."""
    tag = f"[{label}] " if label else ""
    from_local = local_source_files is not None
    processed_remote = f"{input_remote}processed/"

    if from_local:
        pending = [Path(p).name for p in local_source_files]
        source_paths = {Path(p).name: Path(p) for p in local_source_files}
    else:
        pending = list_pending_files(input_remote)
        source_paths = {}

    if not pending:
        print(f"{tag}Không có file mới trong {'nguồn local' if from_local else input_remote}.", flush=True)
        return 0, 0, 0

    print(f"{tag}Tìm thấy {len(pending)} file mới: {pending}", flush=True)
    if not from_local:
        local_staging.mkdir(parents=True, exist_ok=True)

    existing_outputs = list_files_in(output_remote)
    print(f"{tag}{output_remote} hiện có {len(existing_outputs)} file.", flush=True)

    n_rendered = n_skipped = n_failed = 0

    for name in pending:
        print(f"\n{tag}=== Xử lý: {name} ===", flush=True)
        stem = Path(name).stem

        expected_output_name = stem + ".wav"
        expected_srt_name = stem + ".srt"
        expected_manifest_name = stem + ".json"
        # G1 (bịt lỗ hổng Codex review round 1 phát hiện): CHỈ coi là "đã
        # xong" khi CẢ 3 file (wav+srt+json) đều có trên Drive. Trước đây
        # chỉ check riêng .wav -- nếu 1 lần chạy trước upload thất bại giữa
        # chừng (vd wav lên được, srt/json lỗi mạng), lần chạy sau vẫn thấy
        # wav đã tồn tại và coi như xong hẳn, mất luôn cơ hội upload nốt
        # srt/json còn thiếu (M1 vẫn còn "sống" qua lần retry dù lần upload
        # gốc đã bị chặn không cho đánh dấu hoàn tất).
        if (expected_output_name in existing_outputs
                and expected_srt_name in existing_outputs
                and expected_manifest_name in existing_outputs):
            print(f"{tag}Đã có đủ {expected_output_name}/.srt/.json trong {output_remote} — bỏ qua tải/render"
                  + ("." if from_local else ", chuyển thẳng input vào processed/."), flush=True)
            if not from_local:
                mv = rclone("moveto", f"{input_remote}{name}", f"{processed_remote}{name}")
                if mv.returncode != 0:
                    print(f"{tag}CẢNH BÁO: không chuyển được {name} vào processed/ ({mv.stderr.strip()}).", flush=True)
            n_skipped += 1
            continue

        if from_local:
            local_path = source_paths[name]
        else:
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

        # G1 (Audio Generation remediation, sửa finding A4): QA PHẢI pass
        # TRƯỚC khi upload -- trước đây upload chạy VÔ ĐIỀU KIỆN rồi mới
        # check result.success, nghĩa là audio nghi lỗi VẪN lên Drive. Lần
        # chạy sau, output đã "tồn tại" trên Drive nên bị coi là xong vĩnh
        # viễn (xem nhánh skip-if-exists phía trên) dù CHƯA BAO GIỜ pass QA
        # -- vô hiệu hoá đúng cơ chế "giữ lại để retry" mà code định làm.
        if not result.success:
            print(f"{tag}LỖI QA {name} (vẫn nghi lỗi sau retry) — KHÔNG upload"
                  + ("" if from_local else f", GIỮ NGUYÊN trong {input_remote} để thử lại lần sau.")
                  + (" — sẽ thử lại ở lần chạy sau (nguồn local, không có processed/ để giữ)." if from_local else ""),
                  flush=True)
            n_failed += 1
            continue

        # G1 (sửa finding M1): PHẢI check kết quả upload -- trước đây bool
        # trả về bị bỏ qua hoàn toàn, nên upload thất bại (mạng lỗi, rclone
        # lỗi...) vẫn khiến input bị coi là "đã xử lý" và chuyển vào
        # processed/ dù output THẬT SỰ không có trên Drive -- mất artifact
        # âm thầm, không bao giờ tự retry.
        upload_ok = upload_paths_to_drive(
            [result.out_path, result.srt_path, result.manifest_path], output_remote
        )
        if not upload_ok:
            print(f"{tag}LỖI upload {name} lên Drive — KHÔNG đánh dấu hoàn tất"
                  + ("" if from_local else f", GIỮ NGUYÊN trong {input_remote} để thử lại lần sau.")
                  + (" — sẽ thử lại ở lần chạy sau." if from_local else ""),
                  flush=True)
            n_failed += 1
            continue

        # tránh trùng nếu batch có tên lặp; thêm đủ cả 3 tên để lần check
        # skip phía trên (yêu cầu đủ wav+srt+json) hoạt động đúng ngay
        # trong cùng batch này.
        existing_outputs.add(expected_output_name)
        existing_outputs.add(expected_srt_name)
        existing_outputs.add(expected_manifest_name)

        if from_local:
            print(f"{tag}Xong: {name} -> {out_path} -> {output_remote}", flush=True)
        else:
            mv = rclone("moveto", f"{input_remote}{name}", f"{processed_remote}{name}")
            if mv.returncode != 0:
                print(f"{tag}CẢNH BÁO: render xong nhưng không chuyển được {name} vào processed/ "
                      f"({mv.stderr.strip()}) — file sẽ bị xử lý lại lần sau, tự kiểm tra thủ công.", flush=True)
            else:
                print(f"{tag}Xong: {name} -> {out_path} -> {output_remote}, input đã chuyển vào processed/", flush=True)
        n_rendered += 1

    print(f"\n{tag}Hoàn tất: {n_rendered} render mới, {n_skipped} bỏ qua (đã có output), "
          f"{n_failed} lỗi.", flush=True)
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
