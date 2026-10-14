"""
Trộn nhạc nền (BGM) vào video ĐÃ RENDER XONG (đã có lời đọc + phụ đề burn-in
+ ảnh/video từng beat) -- bước cuối cùng, tách riêng khỏi audio_tool_render.py
để không đụng vào pipeline hình ảnh/phụ đề đã test kỹ, chỉ thay track audio.

Nguồn nhạc: bgm/ (tải từ incompetech.com, Kevin MacLeod, CC BY 4.0 -- xem
bgm/LICENSE.txt). Track mặc định "Meditation Impromptu 01" -- piano chậm,
sáng tác riêng cho nội dung thiền định, chọn vì hợp tông "an ủi, chuyển hoá"
của nội dung thay vì quá buồn/u ám.

Hiệu chỉnh âm lượng: đo trực tiếp bằng ffmpeg volumedetect (không đoán mù)
-- lời đọc mean_volume ~-17.4dB, BGM gốc ~-27.1dB, thêm volume=-10dB để đạt
khoảng cách ~20dB dưới lời đọc (mức "nền" rõ ràng nhưng không bao giờ cạnh
tranh với giọng đọc). amix dùng normalize=0 -- mặc định amix TỰ GIẢM MỘT
NỬA âm lượng mỗi input khi trộn 2 nguồn, sẽ vô tình làm nhỏ luôn cả lời đọc
nếu không tắt.

Loop: dùng -stream_loop -1 trên input BGM rồi cắt về đúng độ dài video --
với tập dài (Meditation Impromptu 01 chỉ ~3.5 phút, tập có thể 18+ phút),
sẽ có vài chỗ nối (loop seam) nghe được nếu chú ý kỹ, nhưng ở mức âm lượng
nền thấp (~-37dB) hầu như không đáng chú ý -- đánh đổi hợp lý so với việc
tự dựng crossfade phức tạp cho độ dài bất kỳ.
"""
import json
import subprocess
import sys
from pathlib import Path

BGM_DIR = Path(__file__).parent / "bgm"
DEFAULT_BGM_TRACK = BGM_DIR / "meditation_impromptu_01.mp3"
DEFAULT_BGM_VOLUME_DB = -10.0  # cộng thêm vào mức gốc của track -- xem docstring
DEFAULT_FADE_SEC = 3.0

ATTRIBUTION_TEXT = (
    "Nhạc nền: \"Meditation Impromptu 01\" by Kevin MacLeod (incompetech.com)\n"
    "Licensed under Creative Commons: By Attribution 4.0 License\n"
    "http://creativecommons.org/licenses/by/4.0/"
)


class MixBgmError(RuntimeError):
    pass


def _run_ffmpeg(args: list[str], ffmpeg_path: str) -> None:
    result = subprocess.run([ffmpeg_path, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise MixBgmError(f"ffmpeg lỗi (exit {result.returncode}): {result.stderr[-2000:]}")


def _probe_duration(video_path: Path, ffprobe_path: str) -> float:
    result = subprocess.run(
        [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise MixBgmError(f"ffprobe lỗi khi đọc thời lượng video: {result.stderr[-500:]}")
    return float(json.loads(result.stdout)["format"]["duration"])


def mix_bgm_into_video(
    video_path: str | Path,
    output_path: str | Path,
    ffmpeg_path: str,
    ffprobe_path: str,
    bgm_track: str | Path = DEFAULT_BGM_TRACK,
    bgm_volume_db: float = DEFAULT_BGM_VOLUME_DB,
    fade_sec: float = DEFAULT_FADE_SEC,
) -> Path:
    video_path = Path(video_path)
    bgm_track = Path(bgm_track)
    if not video_path.exists():
        raise MixBgmError(f"Không tìm thấy video: {video_path}")
    if not bgm_track.exists():
        raise MixBgmError(
            f"Không tìm thấy file BGM: {bgm_track} -- cần tải trước (xem bgm/LICENSE.txt để biết nguồn)."
        )

    duration = _probe_duration(video_path, ffprobe_path)
    fade_out_start = max(0.0, duration - fade_sec)

    filter_complex = (
        f"[1:a]volume={bgm_volume_db}dB,atrim=0:{duration:.6f},"
        f"afade=t=in:st=0:d={fade_sec},afade=t=out:st={fade_out_start:.6f}:d={fade_sec}[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:normalize=0[aout]"
    )

    output_path = Path(output_path)
    _run_ffmpeg([
        "-y", "-i", str(video_path), "-stream_loop", "-1", "-i", str(bgm_track),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(output_path),
    ], ffmpeg_path)
    return output_path


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--ffmpeg", required=True, help="Đường dẫn ffmpeg (vendored, có libass)")
    ap.add_argument("--ffprobe", required=True)
    ap.add_argument("--bgm-track", default=str(DEFAULT_BGM_TRACK))
    ap.add_argument("--bgm-volume-db", type=float, default=DEFAULT_BGM_VOLUME_DB)
    ap.add_argument("--fade-sec", type=float, default=DEFAULT_FADE_SEC)
    args = ap.parse_args()

    try:
        result = mix_bgm_into_video(
            args.video, args.output, args.ffmpeg, args.ffprobe,
            bgm_track=args.bgm_track, bgm_volume_db=args.bgm_volume_db, fade_sec=args.fade_sec,
        )
    except MixBgmError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1
    print(f"OK: {result}")
    print(f"\nNHỚ thêm vào mô tả video:\n{ATTRIBUTION_TEXT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
