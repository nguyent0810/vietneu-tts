"""Dọn dẹp AN TOÀN artifact local (wav/mp4/json/srt/subtitles/cache) của các
Short ĐÃ XÁC NHẬN đăng thành công.

Nguyên tắc BẮT BUỘC, kế thừa đúng bài học đã có trong cleanup_local.sh (xem
docstring file đó): KHÔNG BAO GIỜ xoá theo tuổi file (mtime) -- lần trước
dùng cách đó từng suýt xoá nhầm EP005/EP007 (2 tập Long đã render xong
nhưng CHƯA từng upload YouTube thành công, do lỗi/bỏ dở giữa chừng). Cơ chế
DUY NHẤT được tin ở đây là registry.json: chỉ dọn 1 segment khi
`status == "uploaded"` VÀ có `video_id` thật (2 điều kiện, không phải 1 --
phòng trường hợp status bị sửa tay/hỏng mà video_id rỗng). Đây CHÍNH LÀ
nguyên tắc long_batch_runner.py/finalize_episode.py's
cleanup_generation_cache() đã dùng cho Long-form, áp dụng lại cho Short
(short_batch_runner.py trước giờ CHƯA có cơ chế dọn nào sau upload -- phát
hiện thật khi output/ tăng lên 25GB sau 1 đợt batch lớn).

1 thư mục episode (`output/shorts/{topic}/{episode}/`) có thể chứa NHIỀU
segment (bundle nhiều `*** N`, vd BUD "08_Buông Bỏ..." có segment 03-21
trong CÙNG 1 thư mục) -- script CHỈ xoá đúng bộ file của TỪNG segment đã
uploaded, tuyệt đối không đụng file của segment khác (dù cùng thư mục) nếu
segment đó chưa uploaded. Thư mục episode/subtitles/cache con chỉ bị xoá
theo SAU, và chỉ khi đã rỗng hẳn (không còn segment nào khác đang chờ).

KHÔNG BAO GIỜ đụng tới registry.json -- đó là nguồn sự thật duy nhất về
việc gì đã đăng, xoá nhầm sẽ làm mất khả năng audit/resume.

Usage:
  python3 cleanup_short_output.py --topic "Phong Thủy"      # dry-run mặc định, chỉ liệt kê
  python3 cleanup_short_output.py --topic "Phong Thủy" --yes   # xoá thật
  python3 cleanup_short_output.py --yes                        # cả 3 kênh
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ALL_TOPICS = ("Hình Sự", "Phong Thủy", "Phật giáo")


def _registry_path(topic: str) -> Path:
    return PROJECT_ROOT / "output" / "shorts" / topic / "registry.json"


def _shorts_dir(topic: str) -> Path:
    return PROJECT_ROOT / "output" / "shorts" / topic


def segment_artifact_paths(seg_dir: Path, segment_index: int) -> list[Path]:
    """Toàn bộ file/thư mục local của ĐÚNG 1 segment trong `seg_dir` --
    khớp chính xác quy ước đặt tên đang dùng thật trong short_batch_runner.py
    (`wav_path = seg_dir / f"{segment_index:02d}_short.wav"`, `video_path`
    cùng tiền tố, json/srt/important_words suy ra qua `.with_suffix()` nên
    cùng giữ nguyên tiền tố `{N:02d}_short`) + render_short.py (thư mục
    `subtitles/` con, cùng tiền tố `{N:02d}_short_render.*`) + cache TTS
    riêng theo segment (`cache/seg{segment_index}`, KHÔNG zero-pad, khác
    với tiền tố file chính -- xác nhận qua thư mục thật trên đĩa và dòng
    gọi `run_tts(..., seg_dir / "cache" / f"seg{seg['segment_index']}", ...)`
    trong short_batch_runner.py). Glob theo tiền tố thay vì liệt kê cứng
    từng đuôi file -- vẫn đúng nếu sau này thêm loại file mới cùng tiền tố,
    không cần sửa lại hàm này."""
    n = f"{segment_index:02d}"
    paths = list(seg_dir.glob(f"{n}_short*"))
    subtitles_dir = seg_dir / "subtitles"
    if subtitles_dir.is_dir():
        paths.extend(subtitles_dir.glob(f"{n}_short_render.*"))
    cache_dir = seg_dir / "cache" / f"seg{segment_index}"
    if cache_dir.exists():
        paths.append(cache_dir)
    return paths


def _path_size(path: Path) -> int:
    if path.is_dir():
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    try:
        return path.stat().st_size
    except OSError:
        return 0


def cleanup_topic(topic: str, dry_run: bool) -> tuple[int, int, int]:
    """Trả (số segment đã/sẽ dọn, số segment bỏ qua, tổng byte giải phóng).
    CHỈ đọc registry.json, KHÔNG BAO GIỜ ghi lại (dọn file không đổi trạng
    thái đã published, registry vẫn là nguồn sự thật đầy đủ về việc đã đăng
    gì/khi nào để tra cứu sau này)."""
    reg_path = _registry_path(topic)
    if not reg_path.exists():
        print(f"[{topic}] Không có registry, bỏ qua.")
        return 0, 0, 0
    try:
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[{topic}] LỖI đọc registry ({exc}) -- bỏ qua topic này để an toàn.", file=sys.stderr)
        return 0, 0, 0

    shorts_dir = _shorts_dir(topic)
    cleaned = skipped = 0
    freed = 0
    touched_episode_dirs: set[Path] = set()

    for key, entry in registry.items():
        # ĐIỀU KIỆN KÉP bắt buộc: status đúng "uploaded" VÀ video_id thật --
        # không tin riêng 1 field (xem docstring module).
        if entry.get("status") != "uploaded" or not entry.get("video_id"):
            skipped += 1
            continue
        episode = entry.get("episode")
        segment_index = entry.get("segment_index")
        if not episode or not isinstance(segment_index, int):
            skipped += 1
            continue
        seg_dir = shorts_dir / episode
        if not seg_dir.is_dir():
            continue  # đã dọn từ lần chạy trước, không có gì để làm
        paths = segment_artifact_paths(seg_dir, segment_index)
        if not paths:
            continue  # đã dọn từ lần chạy trước
        size = sum(_path_size(p) for p in paths)
        freed += size
        cleaned += 1
        touched_episode_dirs.add(seg_dir)
        action = "sẽ xoá" if dry_run else "đã xoá"
        print(f"  [{key}] {action} {len(paths)} mục ({size / 1024 / 1024:.1f} MB)")
        if not dry_run:
            for p in paths:
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    p.unlink(missing_ok=True)

    # Dọn thư mục episode/subtitles/cache con NẾU đã rỗng hẳn sau khi xoá --
    # nghĩa là không còn segment nào khác (chưa uploaded) đang chờ trong đó.
    if not dry_run:
        for seg_dir in touched_episode_dirs:
            for sub_name in ("subtitles", "cache"):
                sub_dir = seg_dir / sub_name
                if sub_dir.is_dir() and not any(sub_dir.iterdir()):
                    sub_dir.rmdir()
            if seg_dir.is_dir() and not any(seg_dir.iterdir()):
                seg_dir.rmdir()

    return cleaned, skipped, freed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topic", choices=ALL_TOPICS, default=None, help="Chỉ dọn 1 kênh (mặc định: cả 3)")
    ap.add_argument("--yes", action="store_true", help="Xoá THẬT -- không có cờ này chỉ liệt kê (dry-run)")
    args = ap.parse_args()

    topics = [args.topic] if args.topic else list(ALL_TOPICS)
    dry_run = not args.yes

    print("=== Dọn local artifact Short ĐÃ ĐĂNG THÀNH CÔNG (status=uploaded + video_id thật) ===")
    if dry_run:
        print("(dry-run -- chỉ liệt kê, thêm --yes để xoá thật)")
    print()

    total_cleaned = total_skipped = total_freed = 0
    for topic in topics:
        print(f"--- {topic} ---")
        cleaned, skipped, freed = cleanup_topic(topic, dry_run)
        total_cleaned += cleaned
        total_skipped += skipped
        total_freed += freed
        print(f"  -> {cleaned} segment {'sẽ được' if dry_run else 'đã'} dọn, {skipped} segment bỏ qua (chưa uploaded/thiếu video_id)")
        print()

    print(f"=== TỔNG: {total_cleaned} segment, {'sẽ giải phóng' if dry_run else 'đã giải phóng'} {total_freed / 1024 / 1024 / 1024:.2f} GB ===")
    if dry_run and total_cleaned:
        print("Chạy lại với --yes để xoá thật.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
