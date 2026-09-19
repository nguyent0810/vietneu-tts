"""
Bước cuối sau khi render xong 1 tập video: đặt tên chuẩn "EPXXX - Tiêu đề",
upload lên Google Drive (mirror đúng cấu trúc thư mục đã dùng cho audio --
gdrive:TTS-Output/{chủ đề}/Video/), rồi dọn dẹp tài nguyên sinh ra trong lúc
render (ảnh ComfyUI, video Pexels tải về, clip typography Remotion -- toàn
bộ nằm ở chunks_cache/beat_assets/ + comfyui_local/output/) để không phình
ổ đĩa qua từng tập.

Dọn dẹp CHỈ chạy sau khi upload Drive thành công -- nếu upload lỗi, giữ
nguyên cache lại để có thể thử lại mà không phải sinh lại từ đầu (tốn
ComfyUI/Pexels API lần nữa). Không đụng tới:
  - chunks_cache/director_bibles/ -- cache Director Bible, nhỏ, dùng lại
    được nếu render lại cùng tập.
  - comfyui_local/ (trừ output/) -- chứa model checkpoint (~8GB), dùng
    chung cho mọi tập, không phải tài nguyên riêng của 1 tập.
"""
import argparse
import shutil
import sys
from pathlib import Path

from drive_utils import RCLONE_BIN, rclone

ASSET_CACHE_DIR = Path(__file__).parent / "chunks_cache" / "beat_assets"
COMFYUI_OUTPUT_DIR = Path(__file__).parent / "comfyui_local" / "output"
DRIVE_OUTPUT_ROOT = "gdrive:TTS-Output/"


def build_canonical_name(episode_id: str, title: str, suffix: str) -> str:
    """vd: build_canonical_name("EP007", "Người sống và người mất", ".mp4")
    -> "EP007 - Người sống và người mất.mp4" """
    ep = episode_id.upper()
    if not ep.startswith("EP"):
        ep = f"EP{ep}"
    return f"{ep} - {title}{suffix}"


def upload_episode_files(paths: list[Path], topic: str) -> bool:
    """Upload video (+ file đi kèm như .ass phụ đề) lên
    gdrive:TTS-Output/{topic}/Video/ -- mirror đúng convention Long/Short
    đã dùng cho audio trong process_topics.py."""
    remote = f"{DRIVE_OUTPUT_ROOT}{topic}/Video/"
    if not Path(RCLONE_BIN).exists() and shutil.which(RCLONE_BIN) is None:
        print("rclone chưa cài -- bỏ qua upload Drive.", file=sys.stderr)
        return False
    ok = True
    for p in paths:
        if p is None or not Path(p).exists():
            continue
        result = rclone("copy", str(p), remote)
        if result.returncode == 0:
            print(f"Upload Drive OK: {remote}{Path(p).name}", flush=True)
        else:
            print(f"Upload Drive LỖI ({Path(p).name}): {result.stderr.strip()}", file=sys.stderr)
            ok = False
    return ok


def cleanup_generation_cache() -> dict:
    """Xoá tài nguyên sinh ra trong lúc render 1 tập (ảnh/video/typography
    cache theo hash prompt -- có thể sinh lại được, không phải nguồn gốc
    duy nhất của thông tin gì). Trả về {n_files, freed_bytes} để log."""
    n_files = 0
    freed_bytes = 0
    for cache_dir in (ASSET_CACHE_DIR, COMFYUI_OUTPUT_DIR):
        if not cache_dir.exists():
            continue
        for item in cache_dir.rglob("*"):
            if item.is_file():
                freed_bytes += item.stat().st_size
                n_files += 1
                item.unlink()
        for sub in sorted(cache_dir.rglob("*"), reverse=True):
            if sub.is_dir() and not any(sub.iterdir()):
                sub.rmdir()
    return {"n_files": n_files, "freed_bytes": freed_bytes}


def finalize_episode(
    rendered_video_path: str,
    episode_id: str,
    title: str,
    topic: str,
    ass_path: str | None = None,
    output_dir: str | None = None,
    skip_cleanup: bool = False,
) -> dict:
    src = Path(rendered_video_path)
    if not src.exists():
        raise FileNotFoundError(f"Không tìm thấy video đã render: {src}")

    final_dir = Path(output_dir) if output_dir else src.parent
    final_dir.mkdir(parents=True, exist_ok=True)
    final_video = final_dir / build_canonical_name(episode_id, title, src.suffix)
    if src != final_video:
        shutil.copy2(src, final_video)

    upload_paths = [final_video]
    if ass_path and Path(ass_path).exists():
        final_ass = final_dir / build_canonical_name(episode_id, title, Path(ass_path).suffix)
        if Path(ass_path) != final_ass:
            shutil.copy2(ass_path, final_ass)
        upload_paths.append(final_ass)

    uploaded = upload_episode_files(upload_paths, topic)

    cleanup_stats = {"n_files": 0, "freed_bytes": 0, "skipped": True}
    if uploaded and not skip_cleanup:
        cleanup_stats = cleanup_generation_cache()
        cleanup_stats["skipped"] = False
    elif not uploaded:
        print("Upload chưa thành công -- GIỮ NGUYÊN cache sinh asset để có thể thử lại.", file=sys.stderr)

    return {
        "final_video": str(final_video),
        "uploaded": uploaded,
        "cleanup": cleanup_stats,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--ass", default=None)
    ap.add_argument("--episode-id", required=True, help='vd "EP007" hoặc "007"')
    ap.add_argument("--title", required=True)
    ap.add_argument("--topic", required=True, help='vd "Phật giáo" -- khớp tên thư mục Drive đã dùng cho audio')
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--skip-cleanup", action="store_true")
    args = ap.parse_args()

    result = finalize_episode(
        args.video, args.episode_id, args.title, args.topic,
        ass_path=args.ass, output_dir=args.output_dir, skip_cleanup=args.skip_cleanup,
    )
    print(f"Video cuối: {result['final_video']}")
    print(f"Upload Drive: {'OK' if result['uploaded'] else 'LỖI'}")
    c = result["cleanup"]
    if c.get("skipped"):
        print("Dọn dẹp cache: BỎ QUA")
    else:
        mb = c["freed_bytes"] / 1024 / 1024
        print(f"Dọn dẹp cache: xoá {c['n_files']} file, giải phóng {mb:.1f}MB")
    return 0 if result["uploaded"] else 1


if __name__ == "__main__":
    sys.exit(main())
