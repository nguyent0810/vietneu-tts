"""
Cầu nối giữa pipeline audio (repo này) và repo video-editor (`video_tool_clone/`
— pull-only, KHÔNG commit/push gì lên đó, cùng nguyên tắc đã áp dụng với
Content-Creator). video-editor dùng stack Python riêng (Python 3.11+ +
PySide6 + faster-whisper, version pin khác hẳn `uv`/torch của repo này) nên
chạy qua venv riêng (`video_tool_clone/.venv-video/`) + subprocess, không
import trực tiếp vào tiến trình này — tránh xung đột dependency giữa 2 stack.

Bridge script thật sự nằm ở `video_tool_clone/scripts/audio_tool_render.py`
(file cục bộ, thêm vào working tree của clone, không thuộc về repo
video-editor gốc). File này chỉ gọi nó qua subprocess và đọc lại kết quả JSON.

Usage (CLI, test thủ công):
    uv run python video_tool_bridge.py \\
        --audio output/topics/Phật giáo/Long/07_Người sống và người mất.wav \\
        --segments-json output/topics/Phật giáo/Long/07_Người sống và người mất.json \\
        --video /path/to/background_placeholder.mp4 \\
        --output output/video/07_Người sống và người mất.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

VIDEO_TOOL_ROOT = Path(__file__).parent / "video_tool_clone"
VIDEO_TOOL_VENV_PYTHON = VIDEO_TOOL_ROOT / ".venv-video" / "bin" / "python"
BRIDGE_SCRIPT = VIDEO_TOOL_ROOT / "scripts" / "audio_tool_render.py"

DEFAULT_TIMEOUT_S = 1800  # ffmpeg encode + burn-in cho 1 video dài có thể mất vài phút


class VideoToolUnavailableError(RuntimeError):
    pass


def render_video(
    audio_path: str,
    segments_json_path: str,
    output_path: str,
    video_path: str | None = None,
    shot_list_path: str | None = None,
    policy: str = "content_sync",
    timeout: int = DEFAULT_TIMEOUT_S,
) -> dict:
    """Gọi video-editor (qua venv/subprocess riêng) để ghép audio + nền hình
    ảnh thành 1 video hoàn chỉnh, đúng thời lượng audio, có phụ đề burn-in
    dựng từ chính JSON segments đã có (không dùng nhánh tự transcribe bằng
    Whisper của họ — segments của ta đã chính xác 100% vì build trực tiếp
    từ text đã biết, không phải đoán qua ASR).

    Truyền ĐÚNG 1 trong 2: `video_path` (Giai đoạn 1 — 1 video nền tĩnh) hoặc
    `shot_list_path` (Giai đoạn 2 — output của creative_director.py +
    asset_generation.py, ghép theo từng beat: ảnh+Ken Burns / video stock /
    typography card).

    Trả về payload JSON từ audio_tool_render.py: {ok, output_path, ass_path,
    duration_s, n_words, n_beats, warnings} khi thành công. Raise
    VideoToolUnavailableError nếu venv/script chưa setup hoặc render lỗi.
    """
    if not video_path and not shot_list_path:
        raise VideoToolUnavailableError("Cần truyền video_path (Giai đoạn 1) hoặc shot_list_path (Giai đoạn 2).")

    if not VIDEO_TOOL_VENV_PYTHON.exists():
        raise VideoToolUnavailableError(
            f"Chưa setup venv riêng cho video-editor tại {VIDEO_TOOL_VENV_PYTHON} "
            f"(python3.11 -m venv .venv-video && pip install -e . trong {VIDEO_TOOL_ROOT})."
        )
    if not BRIDGE_SCRIPT.exists():
        raise VideoToolUnavailableError(f"Thiếu bridge script: {BRIDGE_SCRIPT}")

    # subprocess chạy với cwd=VIDEO_TOOL_ROOT (script bên đó cần vậy để tự
    # sys.path.insert đúng) — phải tuyệt đối hoá path trước khi truyền qua,
    # nếu không path tương đối của caller sẽ bị hiểu nhầm theo cwd kia.
    args = [
        str(VIDEO_TOOL_VENV_PYTHON), str(BRIDGE_SCRIPT),
        "--audio", str(Path(audio_path).resolve()),
        "--segments-json", str(Path(segments_json_path).resolve()),
        "--output", str(Path(output_path).resolve()),
        "--policy", policy,
    ]
    if video_path:
        args += ["--video", str(Path(video_path).resolve())]
    if shot_list_path:
        args += ["--shot-list", str(Path(shot_list_path).resolve())]
    try:
        result = subprocess.run(args, cwd=VIDEO_TOOL_ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise VideoToolUnavailableError(f"video-editor render quá thời gian chờ ({timeout}s): {exc}")

    stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
    last_line = stdout_lines[-1] if stdout_lines else ""
    try:
        payload = json.loads(last_line)
    except json.JSONDecodeError:
        raise VideoToolUnavailableError(
            f"video-editor bridge không trả JSON hợp lệ (exit={result.returncode}).\n"
            f"stdout (cuối): {result.stdout[-2000:]}\nstderr (cuối): {result.stderr[-2000:]}"
        )

    if not payload.get("ok"):
        raise VideoToolUnavailableError(f"video-editor render lỗi ở bước '{payload.get('stage')}': {payload.get('error')}")

    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--video", default=None, help="Giai đoạn 1: 1 video nền tĩnh")
    ap.add_argument("--shot-list", default=None, help="Giai đoạn 2: output creative_director.py + asset_generation.py")
    ap.add_argument("--segments-json", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--policy", default="content_sync", choices=["content_sync", "visual_loop"])
    args = ap.parse_args()

    try:
        payload = render_video(
            args.audio, args.segments_json, args.output,
            video_path=args.video, shot_list_path=args.shot_list, policy=args.policy,
        )
    except VideoToolUnavailableError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1

    print(f"OK: {payload['output_path']}  duration={payload.get('duration_s')}s  n_words={payload.get('n_words')}  n_beats={payload.get('n_beats')}")
    if payload.get("warnings"):
        print("Cảnh báo:", payload["warnings"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
