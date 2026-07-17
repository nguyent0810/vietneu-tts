"""
Tự động quét các thư mục CHỦ ĐỀ trong gdrive:TTS-Input/ (mỗi thư mục con là 1
chủ đề, vd "Phật giáo", "Phong Thủy", "Hình Sự"...). Mỗi chủ đề có 2 kiểu nội
dung:
  TTS-Input/{Chủ đề}/Long/*.txt   -> mỗi file = 1 audio dài
  TTS-Input/{Chủ đề}/Short/*.txt  -> mỗi file chứa nhiều đoạn "*** N", tách
                                      thành nhiều audio ngắn

Output tương ứng (mỗi file .wav kèm .srt + .json — xem render_engine.py):
  TTS-Output/{Chủ đề}/Long/{tên}.wav(+.srt/.json)
  TTS-Output/{Chủ đề}/Short/processed/{tên}/{N}_{tên}.wav(+.srt/.json)

Giọng đọc được chọn tự động theo chủ đề (topic_voices.json) — không cần sửa
code khi thêm chủ đề mới, chỉ cần thêm dòng vào file JSON nếu muốn giọng
riêng (mặc định dùng "_default").

Model được LOAD 1 LẦN CHO MỖI GIỌNG (không phải mỗi file/đoạn) — nếu 2 chủ đề
dùng chung 1 giọng, chỉ load model đúng 1 lần rồi tái dùng cho cả 2.

Chỉ cho phép 1 tiến trình chạy cùng lúc (file lock) — tránh 2 lần chạy chồng
nhau (vd cron + chạy tay, hoặc trigger từ tool khác) cùng tải/render 1 file.

Usage:
    uv run python process_topics.py                # cả Long + Short, mọi chủ đề
    uv run python process_topics.py --long          # chỉ Long/
    uv run python process_topics.py --short          # chỉ Short/
    uv run python process_topics.py --topic "Phật giáo"   # chỉ 1 chủ đề
    uv run python process_topics.py --voice Tuyen    # ép 1 giọng cho mọi chủ đề
"""
import argparse
import fcntl
import json
import sys
from pathlib import Path

from drive_utils import list_dirs_in
from process_drive_queue import process_long_folder
from process_short_queue import process_short_folder
from render_engine import RenderSession

INPUT_ROOT = "gdrive:TTS-Input/"
OUTPUT_ROOT = "gdrive:TTS-Output/"
TOPIC_VOICES_FILE = Path(__file__).parent / "topic_voices.json"
LOCK_FILE = Path(__file__).parent / ".process_topics.lock"


class AlreadyRunningError(RuntimeError):
    pass


class _PipelineLock:
    """flock trên 1 file — tự giải phóng nếu process chết (khác PID-file thủ
    công dễ để lock rác khi crash)."""

    def __init__(self, path: Path):
        self.path = path
        self._fh = None

    def __enter__(self):
        self._fh = open(self.path, "w")
        try:
            fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._fh.close()
            raise AlreadyRunningError(
                f"Đã có tiến trình process_topics.py khác đang chạy (lock: {self.path}). "
                f"Chờ nó xong hoặc kiểm tra tiến trình bị treo."
            )
        return self

    def __exit__(self, *exc):
        if self._fh:
            fcntl.flock(self._fh, fcntl.LOCK_UN)
            self._fh.close()


def load_topic_voices() -> tuple[dict, str]:
    if not TOPIC_VOICES_FILE.exists():
        return {}, "Binh"
    data = json.loads(TOPIC_VOICES_FILE.read_text(encoding="utf-8"))
    return data.get("voices", {}), data.get("_default", "Binh")


def voice_for(topic: str, voices: dict, default_voice: str, override: str = None) -> str:
    if override:
        return override
    return voices.get(topic, default_voice)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--long", action="store_true", help="Chỉ xử lý Long/")
    ap.add_argument("--short", action="store_true", help="Chỉ xử lý Short/")
    ap.add_argument("--topic", default=None, help="Chỉ xử lý 1 chủ đề cụ thể")
    ap.add_argument("--voice", default=None,
                     help="Ép 1 giọng cho MỌI chủ đề, bỏ qua topic_voices.json (mặc định: tự chọn theo chủ đề)")
    args = ap.parse_args()

    try:
        with _PipelineLock(LOCK_FILE):
            return _run(args)
    except AlreadyRunningError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1


def _run(args) -> int:
    run_long = args.long or not args.short
    run_short = args.short or not args.long

    topic_voices, default_voice = load_topic_voices()

    topics = list_dirs_in(INPUT_ROOT)
    if args.topic:
        if args.topic not in topics:
            print(f"Không tìm thấy chủ đề '{args.topic}' trong {INPUT_ROOT}. "
                  f"Các chủ đề hiện có: {topics}", file=sys.stderr)
            return 1
        topics = [args.topic]

    if not topics:
        print(f"Không có thư mục chủ đề nào trong {INPUT_ROOT}.", flush=True)
        return 0

    print(f"Chủ đề tìm thấy: {topics}", flush=True)
    topic_voice_map = {}
    for t in topics:
        v = voice_for(t, topic_voices, default_voice, args.voice)
        topic_voice_map[t] = v
        known = "ép bằng --voice" if args.voice else ("đã cấu hình" if t in topic_voices else f"mặc định (chưa cấu hình riêng cho '{t}')")
        print(f"  - {t}: giọng {v} ({known})", flush=True)

    # Load model 1 LẦN CHO MỖI GIỌNG DUY NHẤT, tái dùng giữa các chủ đề dùng
    # chung giọng — tránh load lại model nhiều lần trong cùng 1 lần chạy.
    unique_voices = sorted(set(topic_voice_map.values()))
    print(f"\nSố giọng cần load: {len(unique_voices)} ({unique_voices})", flush=True)
    sessions: dict[str, RenderSession] = {}
    for v in unique_voices:
        sessions[v] = RenderSession(v)

    total_rendered = total_skipped = total_failed = 0

    for topic in topics:
        voice = topic_voice_map[topic]
        session = sessions[voice]
        safe_topic = topic  # giữ nguyên tên có dấu cho path Drive

        if run_long:
            print(f"\n{'='*60}\nChủ đề: {topic} / Long  (giọng: {voice})\n{'='*60}", flush=True)
            r, s, f = process_long_folder(
                session,
                input_remote=f"{INPUT_ROOT}{safe_topic}/Long/",
                output_remote=f"{OUTPUT_ROOT}{safe_topic}/Long/",
                local_staging=Path(f"drive_input/topics/{safe_topic}/Long"),
                local_output_dir=Path(f"output/topics/{safe_topic}/Long"),
                label=f"{topic}/Long",
                manifest_extra={"topic": topic},
            )
            total_rendered += r; total_skipped += s; total_failed += f

        if run_short:
            print(f"\n{'='*60}\nChủ đề: {topic} / Short  (giọng: {voice})\n{'='*60}", flush=True)
            r, s, f = process_short_folder(
                session,
                input_remote=f"{INPUT_ROOT}{safe_topic}/Short/",
                output_remote=f"{OUTPUT_ROOT}{safe_topic}/Short/processed/",
                local_staging=Path(f"drive_input/topics/{safe_topic}/Short"),
                local_output_dir=Path(f"output/topics/{safe_topic}/Short/processed"),
                label=f"{topic}/Short",
                manifest_extra={"topic": topic},
            )
            total_rendered += r; total_skipped += s; total_failed += f

    print(f"\n{'='*60}\nTổng kết tất cả chủ đề: {total_rendered} render mới, "
          f"{total_skipped} bỏ qua, {total_failed} lỗi.\n{'='*60}", flush=True)
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
