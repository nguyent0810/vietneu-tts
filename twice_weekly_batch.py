"""Batch điều phối 2 lần/tuần (Thứ 3 + Thứ 6, 8h30 sáng giờ local) cho cả
3 kênh (FS/BUD/CL) -- thay thế daily_short_batch.sh (chỉ BUD, chạy hằng
ngày, không có gate, không có --dry-run thật).

An toàn theo đúng bài học thực tế đã xảy ra trong phiên xây dựng script
này (không suy đoán, đều là sự cố có thật):
- --dry-run THẬT: CHỈ đọc + in kế hoạch ra stdout, KHÔNG gọi bất kỳ runner
  nào, KHÔNG ghi registry/log/lock file nào -- bài học từ daily_short_batch.sh
  không hề có --dry-run, khiến 1 lần test tưởng an toàn hoá ra chạy thật
  (TTS+render thật cho 1 short ngoài kế hoạch).
- Gate đếm THEO TỪNG NGÀY cụ thể trong khung mục tiêu (không gộp tổng --
  gộp tổng có thể để lọt 1 ngày trống trong khi ngày khác dư).
- Gate đối chiếu THẬT với YouTube API (không chỉ tin registry.json cục bộ
  -- registry có thể lệch thực tế, như video Ted Bundy từng bị agent tự
  upload sai rồi bị huỷ lịch thủ công NGOÀI quy trình registry).
- 1 lock DUY NHẤT bao trọn toàn bộ transaction đọc-quyết định-sinh cho mỗi
  kênh (không chỉ khoá quanh bước sinh) -- tránh chạy tay + cron trùng giờ
  cùng sinh dư (race condition Codex chỉ ra khi review thiết kế).
- Guard "đã chạy đúng chân này trong tuần ISO chưa" -- tránh launchd chạy
  bù sau khi máy ngủ dậy trễ khiến date +%u trả về sai thứ, script tính
  nhầm chân Thứ 3/Thứ 6. Nếu ngày chạy KHÔNG phải đúng Thứ 3/Thứ 6, thoát
  ngay (fail-closed), không đoán chân nào để chạy bù.
- CL: KHÔNG tự sinh Short (không có generator an toàn -- chọn case cần
  con người/agent đọc research draft + review Codex an toàn nhiều vòng,
  bằng chứng thật: đúng 1 lần giao tự động, agent CL đã chọn nhầm case
  Ted Bundy có nạn nhân vị thành niên, phải phát hiện + huỷ lịch thủ
  công). Script chỉ LOG số slot còn thiếu để người dùng/agent biết cần
  làm gì trong tuần, không tự chọn case.
- Long (cả 3 kênh): gọi long_batch_runner.py --count 1 NHƯNG trước đó
  giới hạn tối đa 1 lần/kênh/tuần qua state marker riêng (tránh đăng dư
  nếu script chạy lại), KHÔNG kiểm tra trùng-nội-dung với upload thủ công
  cũ qua pipeline khác (long_batch_runner.py tự quản lý registry theo
  episode -- nếu 1 EP đã "uploaded" trong chính registry của nó, nó tự bỏ
  qua; đây là hạn chế đã biết, không mới do script này tạo ra) -- backlog
  rỗng ("0 xử lý") được coi là kết quả bình thường, không phải lỗi.

KHÔNG xây dựng: state-machine transaction đầy đủ (PLANNED->RESERVED->...)
hay hệ thống approval-artifact có chữ ký cho CL -- đây là mức độ kỹ thuật
enterprise không tương xứng quy mô 1 người vận hành vài video/tuần; phần
resumability thật sự cần thiết đã có sẵn ở tầng short_batch_runner.py/
long_batch_runner.py (registry theo trạng thái, TERMINAL_STATUSES,
MAX_RETRIES_PER_SEGMENT) -- không xây lại ở tầng wrapper này.

State/retry/exit-code nguyên thuỷ giờ sống ở batch_orchestration.py (module
KHÔNG phụ thuộc gì vào short_batch_runner.py/long_batch_runner.py -- tách
ra để phần logic ĐÃ CÓ 2 bug thật được sửa (long_state_key ghi vô điều
kiện, exit code luôn 0) test được độc lập, không kéo theo closure ~36 file
của toàn bộ pipeline sinh nội dung). Import TRỰC TIẾP tên hàm từ
batch_orchestration (không qua `batch_orchestration.foo(...)`) để giữ đúng
seam monkeypatch của test_twice_weekly_batch.py (patch qua
`twb.fetch_scheduled_counts_per_day`).

SHORT/LONG_BATCH_RUNNER_SCRIPT coi 2 runner như "external entrypoint" cấu
hình được qua biến môi trường (Codex CLI review round 2, trước khi tích
hợp file này vào commit thật): KHÔNG bắt buộc tồn tại lúc import file này
-- run_script() (batch_orchestration.py) validate NGAY TRƯỚC khi gọi thật,
trả lỗi rõ ràng nếu thiếu thay vì traceback OS mơ hồ. File NÀY giờ CÓ THỂ
commit cùng batch_orchestration.py mà KHÔNG cần short_batch_runner.py/
long_batch_runner.py cũng có mặt trong checkout -- xem báo cáo dependency-
closure trong lịch sử phiên làm việc, audit launchd 04/08. run_script()
CHỈ graceful cho đúng trường hợp "script thiếu"; timeout/permission/thiếu
venv python vẫn crash như exception thật (cố tình không che các lớp lỗi
khác)."""
import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import certifi  # noqa: E402
import os  # noqa: E402
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from youtube_catalog import YouTubeCatalogError  # noqa: E402
from registry_lock import FileLock  # noqa: E402
from batch_orchestration import (  # noqa: E402
    determine_leg, iso_week_key, load_state, save_state, log_run,
    fetch_scheduled_counts_per_day, run_script, should_persist_channel_state,
    aggregate_exit_code,
)

PY = str(PROJECT_ROOT / ".venv" / "bin" / "python3")
SHORTS_PER_DAY = 5
STATE_PATH = PROJECT_ROOT / "output" / "twice_weekly_state.json"
# BUG THẬT (release-verification range audit trước khi push, phát hiện qua
# Codex CLI): trước đây trỏ CHUNG vào "daily_run_log.jsonl" -- đúng file
# scripts/daily_short_batch.sh ghi và short_health_check.py đọc để phát
# hiện "sản xuất bị chặn đứng"/"job không chạy". log_run() (batch_
# orchestration.py) ghi record schema KHÁC (channel/kind/status/detail,
# KHÔNG có n_done) -- health-check đọc "n_done" mặc định 0 cho record
# thiếu field này, nên MỌI lần twice-weekly chạy sẽ làm 2 dòng log cuối
# thành "0 đoạn xong" giả, kích hoạt cảnh báo "production stalled" SAI.
# Sửa: dùng file RIÊNG hoàn toàn -- health-check không cần biết gì về
# schema/tồn tại của file này (xem short_health_check.py, không đổi gì).
LOG_PATH = PROJECT_ROOT / "output" / "shorts" / "twice_weekly_run_log.jsonl"
LOCK_DIR = PROJECT_ROOT / "output" / "locks"

# "External entrypoint" runtime-configured (Codex CLI review trước khi
# implement, xem báo cáo dependency-closure audit launchd 04/08): SHORT/
# LONG_BATCH_RUNNER_SCRIPT KHÔNG bắt buộc phải tồn tại lúc import -- chỉ là
# Path object, chỉ được kiểm tra tồn tại lúc GỌI THẬT trong run_script()
# (batch_orchestration.py). Cho phép override qua biến môi trường (khác
# checkout/máy có thể đặt runner ở nơi khác) -- mặc định đúng vị trí hiện
# tại trong repo.
SHORT_BATCH_RUNNER_SCRIPT = Path(os.environ.get(
    "SHORT_BATCH_RUNNER_SCRIPT", str(PROJECT_ROOT / "short_batch_runner.py")))
LONG_BATCH_RUNNER_SCRIPT = Path(os.environ.get(
    "LONG_BATCH_RUNNER_SCRIPT", str(PROJECT_ROOT / "long_batch_runner.py")))

CHANNELS = {
    "FS": {"topic": "Phong Thủy", "credentials": ".youtube_channels/phong_thuy.json", "short_mode": "auto_discover"},
    "BUD": {"topic": "Phật giáo", "credentials": ".youtube_channels/phat_giao.json", "short_mode": "episodes_06"},
    "CL": {"topic": "Hình Sự", "credentials": ".youtube_channels/hinh_su.json", "short_mode": "manual_only"},
}
LONG_DOMAIN_MAP = {"FS": "FS", "BUD": "BUD", "CL": "CL"}

# Playlist Long series (nếu có) -- truyền TƯỜNG MINH qua --playlist thay vì
# để long_batch_runner.py tự dùng default cứng riêng của nó (trước đây default
# đó là tên playlist CỦA BUD, áp nhầm cho mọi channel -- vô hại với FS/CL vì
# tên không khớp playlist nào bên đó nên add_video_to_playlist() no-op, nhưng
# vẫn là lỗi cấu hình thật). None = chưa có playlist Long series cho channel đó.
LONG_PLAYLIST_BY_CHANNEL = {
    "FS": None,
    "BUD": "GIẢI MÃ KINH ĐỊA TẠNG | Địa Tạng Vương Bồ Tát, Nhân Quả, Hiếu Đạo Và Con Đường Chuyển Hóa",
    "CL": None,
}

# Playlist cho Short LOẠI "episodes_06" (trích từ tập Long cùng chủ đề) --
# CỐ Ý KHÁC playlist Long ở trên, không dùng chung (phát hiện thật: 30 Short
# từng bị gộp lẫn vào playlist Long "GIẢI MÃ KINH ĐỊA TẠNG", làm playlist đó
# không còn thuần các tập Long nữa -- đã tách ra playlist riêng
# "-- Video Ngắn" ngày 04/08, xem output/playlist_migration_20260804.json).
# Short thường (auto_discover/manual_only) KHÔNG dùng field này -- những
# Short đó đã có cơ chế gán playlist theo category riêng (xem
# playlist_mapping.py cho ví dụ; generator mới cần playlist thì set thủ công
# tương tự, ngoài phạm vi field channel-wide này).
SHORT_EXTRACT_PLAYLIST_BY_CHANNEL = {
    "FS": None,
    "BUD": "GIẢI MÃ KINH ĐỊA TẠNG — Video Ngắn",
    "CL": None,
}


def run_short_batch(channel: str, topic: str, credentials_path: str, mode: str, count: int, dry_run: bool) -> tuple[int, str]:
    dry_run_message = f"[DRY-RUN] sẽ gọi short_batch_runner.py --topic \"{topic}\" count={count} mode={mode}"
    args = ["--topic", topic, "--credentials", str(PROJECT_ROOT / credentials_path), "--count", str(count)]
    if mode == "auto_discover":
        args += ["--auto-discover"]
    elif mode == "episodes_06":
        args += ["--episodes", "06"]
        # CHỈ mode episodes_06 (trích từ tập Long) mới gán playlist channel-wide
        # ở đây -- KHÔNG dùng playlist Long series (xem SHORT_EXTRACT_PLAYLIST_BY_CHANNEL
        # ở trên, lý do tách). Short auto_discover/manual_only có cơ chế gán
        # playlist riêng theo category, không đụng ở đây.
        short_playlist = SHORT_EXTRACT_PLAYLIST_BY_CHANNEL.get(channel)
        if short_playlist:
            args += ["--playlist", short_playlist]
    return run_script(SHORT_BATCH_RUNNER_SCRIPT, args, PY, cwd=PROJECT_ROOT, timeout=7200,
                       dry_run=dry_run, dry_run_message=dry_run_message, runner_label="Short batch")


def run_long_batch(channel: str, topic: str, credentials_path: str, dry_run: bool) -> tuple[int, str]:
    domain = LONG_DOMAIN_MAP[channel]
    dry_run_message = f"[DRY-RUN] sẽ gọi long_batch_runner.py --domain {domain} --topic \"{topic}\" --count 1"
    args = ["--domain", domain, "--topic", topic,
            "--credentials", str(PROJECT_ROOT / credentials_path), "--count", "1"]
    # Truyền TƯỜNG MINH theo channel thay vì để long_batch_runner.py tự dùng
    # default cứng của nó (trước đây là 1 tên playlist riêng của BUD áp cho
    # MỌI channel -- xem LONG_PLAYLIST_BY_CHANNEL). None = generator tự bỏ
    # qua bước gán playlist (chưa có playlist Long series cho channel đó).
    long_playlist = LONG_PLAYLIST_BY_CHANNEL.get(channel)
    if long_playlist:
        args += ["--playlist", long_playlist]
    return run_script(LONG_BATCH_RUNNER_SCRIPT, args, PY, cwd=PROJECT_ROOT, timeout=14400,
                       dry_run=dry_run, dry_run_message=dry_run_message, runner_label="Long batch")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="CHỈ tính toán + in kế hoạch, không gọi runner nào, không ghi log/state/lock.")
    ap.add_argument("--force-leg", choices=["tue", "fri"], default=None, help="Bỏ qua kiểm tra thứ trong tuần thật -- CHỈ dùng để test thủ công, KHÔNG dùng trong launchd.")
    args = ap.parse_args()

    now = datetime.now()
    run_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.force_leg:
        leg = args.force_leg
        days = ([(now + timedelta(days=d)).strftime("%Y-%m-%d") for d in (1, 2, 3)] if leg == "tue"
                else [(now + timedelta(days=d)).strftime("%Y-%m-%d") for d in (1, 2, 3, 4)])
    else:
        result = determine_leg(now)
        if result is None:
            print(f"Hôm nay ({now.strftime('%A')}) không phải Thứ 3/Thứ 6 -- KHÔNG đoán chân để chạy bù, thoát ngay (fail-closed).", flush=True)
            return 0
        leg, days = result

    week_key = iso_week_key(now)
    run_key = f"{week_key}-{leg}"

    state = load_state(STATE_PATH)
    if not args.dry_run and state.get("last_run_key") == run_key:
        print(f"Đã chạy chân '{run_key}' rồi (guard chống chạy bù trùng lặp) -- thoát, không sinh gì thêm.", flush=True)
        return 0

    # Xem docstring should_persist_channel_state()/aggregate_exit_code() ở
    # batch_orchestration.py cho lý do 2 bug thật đã sửa (audit launchd
    # 04/08, Codex CLI review): last_run_key/long_state_key KHÔNG được ghi
    # vô điều kiện, và exit code phải phản ánh đúng có lỗi thật hay không.
    had_hard_failure = False

    print(f"=== Chân: {leg} | tuần: {week_key} | ngày mục tiêu: {days} | dry_run={args.dry_run} ===", flush=True)

    for channel, cfg in CHANNELS.items():
        topic, creds_rel, mode = cfg["topic"], cfg["credentials"], cfg["short_mode"]
        creds_full = str(PROJECT_ROOT / creds_rel)

        try:
            counts = fetch_scheduled_counts_per_day(creds_full, days)
        except YouTubeCatalogError as exc:
            # Fail-closed: không đọc được trạng thái thật trên YouTube ->
            # KHÔNG sinh bù mù quáng, chỉ báo lỗi và bỏ qua kênh này (đúng
            # góp ý Codex: không nên fail-open khi reconcile thất bại).
            if not args.dry_run:
                log_run(LOG_PATH, run_at, channel, "gate_check", "FAILED", f"Không đọc được trạng thái YouTube thật: {exc}", 1)
                had_hard_failure = True
            else:
                print(f"[{channel}] [DRY-RUN] gate_check sẽ FAIL nếu API lỗi: {exc}")
            continue

        deficit_by_day = {d: max(0, SHORTS_PER_DAY - counts[d]) for d in days}
        total_deficit = sum(deficit_by_day.values())
        print(f"[{channel}] Đếm thật theo ngày: {counts} -> thiếu: {deficit_by_day} (tổng {total_deficit})", flush=True)

        if total_deficit == 0:
            if not args.dry_run:
                log_run(LOG_PATH, run_at, channel, "short", "NO_CONTENT_NEEDED", "Đã đủ 5 short/ngày cho mọi ngày mục tiêu.")
            continue

        if mode == "manual_only":
            msg = f"CL cần review thủ công tuần này -- còn thiếu {total_deficit} slot theo ngày {deficit_by_day}. KHÔNG tự sinh (an toàn nội dung cần con người chọn case)."
            if not args.dry_run:
                log_run(LOG_PATH, run_at, channel, "short", "BLOCKED_REVIEW", msg)
            else:
                print(f"[{channel}] [DRY-RUN] {msg}")
            continue

        lock_path = LOCK_DIR / f"twice_weekly_{channel}"
        if args.dry_run:
            print(f"[{channel}] [DRY-RUN] sẽ khoá lock {lock_path}, sinh {total_deficit} short (mode={mode}).")
        else:
            # BUG THẬT phát hiện qua Codex CLI review trước khi commit (audit
            # launchd 04/08): LOCK_DIR.mkdir() trước đây chạy VÔ ĐIỀU KIỆN,
            # kể cả khi dry_run=True -- vi phạm đúng lời hứa "--dry-run
            # KHÔNG ghi bất kỳ file nào" đã ghi rõ ở docstring đầu file. Di
            # chuyển vào nhánh KHÔNG dry-run.
            LOCK_DIR.mkdir(parents=True, exist_ok=True)
            with FileLock(lock_path):
                # Đọc lại số liệu THẬT trong lúc giữ lock (không dùng số đã
                # tính ở ngoài) -- thu hẹp cửa sổ race, dù không loại trừ
                # tuyệt đối 100% (chạy tay đúng khoảnh khắc giữa 2 lần đọc
                # API vẫn có thể trùng -- rủi ro dư ở đây là sinh dư TỐI ĐA
                # vài short, không phải sự cố an toàn nội dung nghiêm trọng
                # như trường hợp CL, nên chấp nhận đánh đổi này thay vì xây
                # transaction phân tán đầy đủ).
                try:
                    counts2 = fetch_scheduled_counts_per_day(creds_full, days)
                except YouTubeCatalogError as exc:
                    log_run(LOG_PATH, run_at, channel, "short", "FAILED", f"Không đọc lại được trạng thái YouTube trong lock: {exc}", 1)
                    had_hard_failure = True
                    continue
                deficit2 = sum(max(0, SHORTS_PER_DAY - counts2[d]) for d in days)
                if deficit2 == 0:
                    log_run(LOG_PATH, run_at, channel, "short", "NO_CONTENT_NEEDED", "Đã đủ (xác nhận lại trong lock, có thể do chạy tay vừa lấp).")
                    continue
                exit_code, output = run_short_batch(channel, topic, creds_full, mode, deficit2, args.dry_run)
                status = "SUCCESS" if exit_code == 0 else "PARTIAL"
                if exit_code != 0:
                    had_hard_failure = True
                log_run(LOG_PATH, run_at, channel, "short", status, output, exit_code)

    # BUG THẬT phát hiện qua Codex CLI review trước khi commit (audit
    # launchd 04/08): nhánh Long trước đây KHÔNG hề khoá gì (khác hẳn nhánh
    # Short đã có FileLock từ trước) -- 2 lần gọi main() chồng nhau (chạy
    # tay + launchd trùng giờ, hoặc launchd catch-up sau khi máy ngủ dậy
    # trễ) có thể cùng đọc state CHƯA có long_state_key, cùng chạy Long
    # batch SONG SONG (vi phạm "tối đa 1 lần/kênh/tuần" thật sự), rồi save
    # đè state CŨ lên nhau (mất update của nhau vì save_state() ghi đè
    # thẳng, không merge). Bug này CÓ SẴN TỪ TRƯỚC đợt refactor retry/state
    # -- sửa luôn vì cùng chủ đề "retry safety".
    #
    # Dùng ĐÚNG 1 lock DUY NHẤT bao trọn CẢ vòng lặp 3 channel (không phải
    # 1 lock riêng mỗi channel) -- state.json là 1 file DÙNG CHUNG cho cả 3
    # channel; khoá riêng từng channel vẫn để lọt race TRÊN CHÍNH FILE STATE
    # giữa 2 channel khác nhau (channel A giữ lock A đọc-sửa-ghi state cùng
    # lúc channel B giữ lock B khác cũng đọc-sửa-ghi state -- 2 lock riêng
    # không loại trừ lẫn nhau). 1 lock DUY NHẤT bao cả vòng lặp đơn giản hơn
    # hẳn (đúng tinh thần "không xây transaction phân tán đầy đủ" đã ghi ở
    # đầu file) và loại bỏ HOÀN TOÀN race trên state.json, không chỉ thu
    # hẹp cửa sổ.
    if args.dry_run:
        for channel in CHANNELS:
            print(f"[{channel}] [DRY-RUN] sẽ gọi long_batch_runner.py (nếu chưa thử trong tuần {week_key}).")
    else:
        long_lock_path = LOCK_DIR / "twice_weekly_long"
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
        with FileLock(long_lock_path):
            state = load_state(STATE_PATH)  # đọc lại MỚI NHẤT ngay khi vào lock, dùng cho CẢ vòng lặp
            for channel, cfg in CHANNELS.items():
                long_state_key = f"long_{channel}_{week_key}"
                if state.get(long_state_key):
                    print(f"[{channel}] Long đã thử THÀNH CÔNG trong tuần {week_key} rồi -- bỏ qua (tối đa 1 lần/kênh/tuần, xác nhận lại trong lock).", flush=True)
                    continue
                exit_code, output = run_long_batch(channel, cfg["topic"], cfg["credentials"], args.dry_run)
                no_content = "0 tập" in output or "không có tập" in output.lower() or "0 episode" in output.lower()
                status = "NO_ELIGIBLE_CONTENT" if (exit_code == 0 and no_content) else ("SUCCESS" if exit_code == 0 else "FAILED")
                if exit_code != 0:
                    had_hard_failure = True
                log_run(LOG_PATH, run_at, channel, "long", status, output, exit_code)
                if should_persist_channel_state(exit_code):
                    state[long_state_key] = run_at
                    save_state(STATE_PATH, state)

            # BUG THẬT phát hiện qua Codex CLI review (round 3, sau khi đã
            # sửa Long sang 1 lock duy nhất): ghi last_run_key NGOÀI lock
            # -- kể cả có "đọc lại state ngay trước khi ghi" -- KHÔNG loại
            # trừ race, vì đọc-rồi-ghi đó không atomic với 1 tiến trình khác
            # đang giữ CHÍNH lock Long này. Kịch bản mất update thật: tiến
            # trình B giữ lock Long, đọc state (chưa có last_run_key của A);
            # tiến trình A (ngoài lock) đọc lại + ghi last_run_key; B sau đó
            # save() state đã load TRƯỚC đó (không có last_run_key của A) ->
            # đè mất update của A. Sửa: ghi last_run_key ở NGAY TRONG lock
            # Long, dùng chung biến `state` đã đọc khi vào lock (không cần
            # đọc lại lần nữa -- không tiến trình nào khác có thể ghi
            # state.json trong lúc lock này còn giữ, vì đây là lock DUY NHẤT
            # bảo vệ toàn bộ file).
            if had_hard_failure:
                print(f"Có ít nhất 1 lỗi thật trong lần chạy này -- KHÔNG ghi last_run_key, để lần gọi kế tiếp (launchd catch-up hoặc chạy tay) có thể thử lại. An toàn vì fetch_scheduled_counts_per_day() đọc lại trạng thái THẬT mỗi lần (idempotent).", flush=True)
            else:
                state["last_run_key"] = run_key
                save_state(STATE_PATH, state)

    return aggregate_exit_code(had_hard_failure)


if __name__ == "__main__":
    sys.exit(main())
