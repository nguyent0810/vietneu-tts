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
    uv run python process_topics.py                # cả Long + Short, mọi chủ đề (nguồn Drive)
    uv run python process_topics.py --long          # chỉ Long/
    uv run python process_topics.py --short          # chỉ Short/
    uv run python process_topics.py --topic "Phật giáo"   # chỉ 1 chủ đề
    uv run python process_topics.py --voice Tuyen    # ép 1 giọng cho mọi chủ đề
    uv run python process_topics.py --content-repo   # THÊM nguồn Content-Creator repo
                                                       # (pull trực tiếp, không qua Drive cho input;
                                                       #  output vẫn lên Drive như cũ — xem content_repo.py)
"""
import argparse
import fcntl
import json
import sys
import time
from pathlib import Path

from drive_utils import list_dirs_in
from process_drive_queue import process_long_folder
from process_short_queue import process_short_folder
from render_engine import RenderSession
from content_repo import (
    ContentRepoUnavailableError,
    ensure_content_repo,
    load_domain_topics,
    stage_ready_episodes,
    load_github_credentials,
)

INPUT_ROOT = "gdrive:TTS-Input/"
OUTPUT_ROOT = "gdrive:TTS-Output/"
TOPIC_VOICES_FILE = Path(__file__).parent / "topic_voices.json"
LOCK_FILE = Path(__file__).parent / ".process_topics.lock"
LOCK_ACQUIRE_TIMEOUT_SECONDS = 1800  # 30 phút -- đợi tiến trình khác tự nhả khoá thay vì fail ngay
LOCK_POLL_INTERVAL_SECONDS = 15


class AlreadyRunningError(RuntimeError):
    pass


class _PipelineLock:
    """flock trên 1 file — tự giải phóng nếu process chết (khác PID-file thủ
    công dễ để lock rác khi crash).

    Khoá vẫn CHỈ CHO 1 tiến trình chạy tại 1 thời điểm trên TOÀN REPO (không
    bỏ khoá -- lý do chính đáng: tránh 2 tiến trình cùng tải model/tranh
    GPU-RAM, không chỉ tránh ghi đè file). Nhưng thay vì fail ngay lập tức
    (LOCK_NB thuần) khi có tiến trình khác đang giữ khoá, giờ ĐỢI CÓ GIỚI HẠN
    (poll LOCK_NB mỗi LOCK_POLL_INTERVAL_SECONDS) -- 2 lần trigger gần nhau
    (vd 2 kênh cùng lên lịch cách nhau vài phút) sẽ tự xếp hàng chạy tuần tự
    thay vì 1 bên bị huỷ hẳn; chỉ raise AlreadyRunningError nếu chờ quá
    LOCK_ACQUIRE_TIMEOUT_SECONDS (khoá thật sự bị kẹt/treo, không phải đang
    xếp hàng bình thường)."""

    def __init__(self, path: Path, timeout_seconds: float = LOCK_ACQUIRE_TIMEOUT_SECONDS,
                 poll_interval_seconds: float = LOCK_POLL_INTERVAL_SECONDS):
        self.path = path
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self._fh = None

    def __enter__(self):
        self._fh = open(self.path, "w")
        deadline = time.monotonic() + self.timeout_seconds
        announced_wait = False
        while True:
            try:
                fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    self._fh.close()
                    raise AlreadyRunningError(
                        f"Tiến trình process_topics.py khác vẫn giữ khoá sau {self.timeout_seconds:.0f}s chờ "
                        f"(lock: {self.path}). Có thể khoá bị kẹt/treo -- kiểm tra tiến trình thật, đừng tự ý xoá lock file."
                    )
                if not announced_wait:
                    print(f"[process_topics] Tiến trình khác đang giữ khoá {self.path} -- xếp hàng đợi "
                          f"(tối đa {self.timeout_seconds:.0f}s)...", file=sys.stderr)
                    announced_wait = True
                time.sleep(self.poll_interval_seconds)
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
    ap.add_argument("--content-repo", action="store_true",
                     help="THÊM nguồn từ Content-Creator repo (pull trực tiếp, không qua Drive cho input). "
                          "Mặc định TẮT — không ảnh hưởng luồng Drive hiện có nếu không truyền cờ này.")
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

    # Nguồn Content-Creator (opt-in qua --content-repo) — lỗi ở bước này
    # (mạng, token thiếu/sai...) KHÔNG được làm sập cả run, chỉ bỏ qua nguồn
    # này và tiếp tục xử lý phần Drive như bình thường.
    staged: dict = {}
    if args.content_repo:
        try:
            token, repo_url = load_github_credentials()
            repo_root = ensure_content_repo(token, repo_url)
            domain_topics = load_domain_topics()
            staged = stage_ready_episodes(repo_root, domain_topics)
            for t in staged:
                if t not in topics:
                    topics.append(t)
        except ContentRepoUnavailableError as e:
            print(f"LỖI Content-Creator (bỏ qua nguồn này, vẫn tiếp tục phần Drive): {e}", file=sys.stderr)

    if args.topic:
        if args.topic not in topics:
            print(f"Không tìm thấy chủ đề '{args.topic}' trong {INPUT_ROOT}"
                  + (" hoặc Content-Creator" if args.content_repo else "") + ". "
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
        topic_staged = staged.get(topic, {"long": [], "short": []})

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

            if topic_staged["long"]:
                print(f"\n{'='*60}\nChủ đề: {topic} / Long (Content-Creator)  (giọng: {voice})\n{'='*60}", flush=True)
                r, s, f = process_long_folder(
                    session,
                    input_remote=f"{INPUT_ROOT}{safe_topic}/Long/",  # không dùng khi local_source_files có giá trị
                    output_remote=f"{OUTPUT_ROOT}{safe_topic}/Long/",
                    local_output_dir=Path(f"output/topics/{safe_topic}/Long"),
                    label=f"{topic}/Long(CC)",
                    manifest_extra={"topic": topic, "source": "content-creator"},
                    local_source_files=topic_staged["long"],
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

            if topic_staged["short"]:
                print(f"\n{'='*60}\nChủ đề: {topic} / Short (Content-Creator)  (giọng: {voice})\n{'='*60}", flush=True)
                r, s, f = process_short_folder(
                    session,
                    input_remote=f"{INPUT_ROOT}{safe_topic}/Short/",  # không dùng khi local_source_files có giá trị
                    output_remote=f"{OUTPUT_ROOT}{safe_topic}/Short/processed/",
                    local_output_dir=Path(f"output/topics/{safe_topic}/Short/processed"),
                    label=f"{topic}/Short(CC)",
                    manifest_extra={"topic": topic, "source": "content-creator"},
                    local_source_files=topic_staged["short"],
                )
                total_rendered += r; total_skipped += s; total_failed += f

    print(f"\n{'='*60}\nTổng kết tất cả chủ đề: {total_rendered} render mới, "
          f"{total_skipped} bỏ qua, {total_failed} lỗi.\n{'='*60}", flush=True)
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
