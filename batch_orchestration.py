"""Retry-safety/state-aggregation logic cho các job launchd định kỳ (2 lần/
tuần, ...) -- TÁCH RIÊNG khỏi twice_weekly_batch.py để module này KHÔNG phụ
thuộc (import lẫn subprocess-dispatch) vào short_batch_runner.py/
long_batch_runner.py hay bất kỳ file nào trong pipeline sinh nội dung thật
-- cho phép commit + test độc lập phần retry/state/exit-code mà không kéo
theo closure ~36 file của toàn bộ pipeline (xem báo cáo dependency-closure
+ Codex CLI adversarial review trong lịch sử phiên làm việc, audit launchd
04/08).

Caller (twice_weekly_batch.py) chịu trách nhiệm: biết PY/short_batch_runner.py/
long_batch_runner.py, build command spec thật, gọi run_command() ở đây để
thực thi + đo exit code, rồi dùng should_persist_channel_state()/
aggregate_exit_code() để quyết định ghi state gì. Module NÀY không biết gì
về pipeline sinh nội dung -- chỉ dependency thật là youtube_catalog.py (cho
fetch_scheduled_counts_per_day(), đối chiếu THẬT với YouTube API).

LƯU Ý (Codex CLI review trước khi implement): twice_weekly_batch.py phải
import TRỰC TIẾP tên hàm từ module này (`from batch_orchestration import
fetch_scheduled_counts_per_day`), KHÔNG gọi qua `batch_orchestration.foo(...)`
-- test hiện có (test_twice_weekly_batch.py) monkeypatch qua
`monkeypatch.setattr(twb, "fetch_scheduled_counts_per_day", ...)`, chỉ hoạt
động đúng nếu twice_weekly_batch.py giữ tên hàm trong namespace CỦA CHÍNH
NÓ."""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from youtube_catalog import _get, CHANNELS_URL, PLAYLIST_ITEMS_URL, VIDEOS_URL


def determine_leg(now: datetime) -> tuple[str, list[str]] | None:
    """Trả về (leg_key, [ngày mục tiêu ISO 'YYYY-MM-DD']) nếu hôm nay ĐÚNG
    Thứ 3 hoặc Thứ 6. Trả về None nếu KHÔNG phải 1 trong 2 ngày đó -- KHÔNG
    đoán chân nào để "chạy bù" (fail-closed theo đúng góp ý Codex round 1:
    tránh launchd chạy bù sau khi máy ngủ dậy trễ tính nhầm chân)."""
    weekday = now.isoweekday()  # 1=Mon .. 7=Sun
    if weekday == 2:  # Thứ 3
        days = [(now + timedelta(days=d)).strftime("%Y-%m-%d") for d in (1, 2, 3)]  # T4,T5,T6
        return "tue", days
    if weekday == 5:  # Thứ 6
        days = [(now + timedelta(days=d)).strftime("%Y-%m-%d") for d in (1, 2, 3, 4)]  # T7,CN,T2,T3
        return "fri", days
    return None


def iso_week_key(now: datetime) -> str:
    y, w, _ = now.isocalendar()
    return f"{y}-W{w:02d}"


def load_state(state_path: Path) -> dict:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(state_path)


def log_run(log_path: Path, run_at: str, channel: str, kind: str, status: str, detail: str, exit_code: int = 0) -> None:
    entry = {
        "run_at": run_at, "channel": channel, "kind": kind, "status": status,
        "detail": detail, "exit_code": exit_code,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[{channel}/{kind}] {status}: {detail}", flush=True)


def fetch_scheduled_counts_per_day(credentials_path: str, target_days: list[str]) -> dict:
    """Đối chiếu THẬT với YouTube API (không chỉ tin registry.json cục bộ)
    -- đếm số video privacyStatus=private có publishAt rơi đúng vào từng
    ngày mục tiêu (giờ UTC ngày đó, theo đúng field publishAt thật)."""
    counts = {d: 0 for d in target_days}
    ch_data = _get(credentials_path, CHANNELS_URL, {"part": "contentDetails", "mine": "true"})
    uploads_playlist_id = ch_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids, page_token = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": uploads_playlist_id, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        pdata = _get(credentials_path, PLAYLIST_ITEMS_URL, params)
        video_ids.extend(it["contentDetails"]["videoId"] for it in pdata.get("items", []))
        page_token = pdata.get("nextPageToken")
        if not page_token or len(video_ids) >= 200:
            break

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        vdata = _get(credentials_path, VIDEOS_URL, {"part": "status", "id": ",".join(batch)})
        for v in vdata.get("items", []):
            status = v.get("status", {})
            publish_at = status.get("publishAt")
            if status.get("privacyStatus") == "private" and publish_at:
                day = publish_at[:10]
                if day in counts:
                    counts[day] += 1
    return counts


def run_command(cmd: list[str], cwd: Path, timeout: int, dry_run: bool, dry_run_message: str) -> tuple[int, str]:
    """Dispatch generic -- KHÔNG biết gì về short_batch_runner.py/
    long_batch_runner.py cụ thể, chỉ nhận command list do caller build sẵn
    (caller là twice_weekly_batch.py, nơi DUY NHẤT biết tên script thật).

    CHỈ xử lý gracefully đúng 1 trường hợp qua run_script() bên dưới
    (script thiếu) -- KHÔNG bọc TimeoutExpired/PermissionError/thiếu
    python_bin hay OSError khác. Những lỗi đó vẫn thoát ra ngoài như
    exception thật (Codex CLI review nhấn mạnh: không được nhận vơ là "mọi
    lỗi dispatch đều graceful" khi chỉ 1 trường hợp cụ thể được xử lý)."""
    if dry_run:
        return 0, dry_run_message
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output[-2000:]


def run_script(script_path: Path, args: list[str], python_bin: str, cwd: Path, timeout: int,
                dry_run: bool, dry_run_message: str, runner_label: str = "Runner") -> tuple[int, str]:
    """Chạy 1 script Python của project như 1 "external entrypoint" --
    module NÀY không import short_batch_runner.py/long_batch_runner.py,
    chỉ nhận `script_path` như 1 tham số Path tường minh (caller quyết định
    đường dẫn thật, có thể cấu hình qua biến môi trường -- xem
    SHORT_BATCH_RUNNER_SCRIPT/LONG_BATCH_RUNNER_SCRIPT ở twice_weekly_batch.py).

    Validate `script_path.is_file()` NGAY TRƯỚC khi subprocess (SAU nhánh
    dry-run -- dry-run phải chạy được trên checkout KHÔNG có runner thật,
    xem báo cáo dependency-closure) -- nếu thiếu, trả lỗi RÕ RÀNG kèm tên
    runner + đường dẫn đầy đủ thay vì để lộ traceback OS mơ hồ từ chính
    interpreter con (vd "can't open file"). Lỗi này chảy đúng qua
    had_hard_failure/should_persist_channel_state hiện có -- không cần đổi
    logic đó.

    CHỈ graceful cho đúng 1 trường hợp: script thiếu. KHÔNG validate
    python_bin (nếu thiếu venv, vẫn crash FileNotFoundError thật -- lỗi
    hạ tầng khác hẳn "chưa thêm runner vào checkout", cố tình không che)."""
    if dry_run:
        return run_command([python_bin, str(script_path), *args], cwd=cwd, timeout=timeout,
                            dry_run=True, dry_run_message=dry_run_message)
    if not script_path.is_file():
        return 1, (
            f"{runner_label} script không tồn tại trong checkout này: {script_path}. "
            f"Đây là kỳ vọng nếu {script_path.name} chưa được thêm vào (xem báo cáo "
            f"dependency-closure, audit launchd 04/08) -- KHÔNG PHẢI lỗi cấu hình khác."
        )
    return run_command([python_bin, str(script_path), *args], cwd=cwd, timeout=timeout,
                        dry_run=False, dry_run_message=dry_run_message)


def should_persist_channel_state(exit_code: int) -> bool:
    """BUG THẬT phát hiện qua Codex CLI adversarial review độc lập (audit
    launchd 04/08): long_state_key (đánh dấu "đã thử Long cho kênh/tuần
    này") trước đây được ghi VÔ ĐIỀU KIỆN, kể cả khi run_long_batch() trả
    lỗi thật (exit_code != 0). Kết quả: 1 lần Long thất bại (network/API/
    render lỗi) tự khoá mất khả năng retry channel đó CẢ TUẦN, dù guard
    "tối đa 1 lần/kênh/tuần" chỉ nên áp dụng cho lần THỬ THÀNH CÔNG (SUCCESS
    hoặc NO_ELIGIBLE_CONTENT -- cả 2 đều exit_code=0, là kết quả hợp lệ,
    không phải lỗi). Chỉ ghi khi KHÔNG phải lỗi thật."""
    return exit_code == 0


def aggregate_exit_code(had_hard_failure: bool) -> int:
    """BUG THẬT phát hiện qua Codex CLI adversarial review độc lập (audit
    launchd 04/08): main() trước đây LUÔN return 0 dù had_hard_failure=True
    -- launchd/launchctl print/mọi giám sát bên ngoài nhìn vào exit code sẽ
    thấy job "thành công" ngay cả khi 1+ channel lỗi thật."""
    return 1 if had_hard_failure else 0
