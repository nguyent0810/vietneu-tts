"""Regression test cho 2 bug thật phát hiện qua Codex CLI adversarial review
độc lập (audit launchd 04/08, xem twice_weekly_batch.py):

1. long_state_key (f"long_{channel}_{week_key}") trước đây bị ghi VÔ ĐIỀU
   KIỆN dù run_long_batch() thất bại thật -- khoá mất khả năng retry channel
   đó cả tuần dù lần thử đầu chỉ lỗi mềm (network/API thoáng qua).
2. main() trước đây LUÔN return 0 dù có lỗi thật (had_hard_failure=True) --
   launchd/monitoring không thể phát hiện job đã lỗi qua exit code.
3. Nhánh Long không hề khoá gì (khác Short đã có FileLock) -- 2 lần chạy
   chồng nhau có thể race, mất update của nhau (Codex CLI review round 3).
4. LOCK_DIR.mkdir() chạy vô điều kiện kể cả dry-run, vi phạm lời hứa
   "không ghi file nào" (Codex CLI review round 3, minor).

Mock toàn bộ I/O thật (YouTube API, subprocess runner) -- test này CHỈ khoá
đúng logic ghi state + exit code, không gọi bất kỳ dependency ngoài nào."""
import json
import sys

import pytest

import twice_weekly_batch as twb


@pytest.fixture(autouse=True)
def _isolated_state(tmp_path, monkeypatch):
    monkeypatch.setattr(twb, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(twb, "LOG_PATH", tmp_path / "log.jsonl")
    monkeypatch.setattr(twb, "LOCK_DIR", tmp_path / "locks")
    # Không channel nào cần sinh Short (deficit=0 mọi ngày) -- cô lập test
    # này CHỈ vào nhánh Long, không chạm short_batch_runner thật.
    monkeypatch.setattr(twb, "fetch_scheduled_counts_per_day",
                         lambda creds, days: {d: twb.SHORTS_PER_DAY for d in days})
    monkeypatch.setattr(sys, "argv", ["twice_weekly_batch.py", "--force-leg", "tue"])


def test_failed_long_run_does_not_write_state_key_or_block_retry(monkeypatch):
    """run_long_batch() trả lỗi thật (exit_code=1) -> long_{channel}_{week}
    KHÔNG được ghi -- lần gọi kế tiếp trong cùng tuần phải thử lại được,
    không bị guard 'tối đa 1 lần/kênh/tuần' chặn nhầm."""
    monkeypatch.setattr(twb, "run_long_batch", lambda channel, topic, creds, dry_run: (1, "lỗi thật giả lập"))

    exit_code = twb.main()

    # Trường hợp lỗi hoàn toàn: không channel nào ghi được gì -> STATE_PATH
    # có thể chưa từng được tạo (_save_state không được gọi lần nào).
    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8")) if twb.STATE_PATH.exists() else {}
    week_key = twb.iso_week_key(__import__("datetime").datetime.now())
    for channel in twb.CHANNELS:
        assert f"long_{channel}_{week_key}" not in state, \
            f"long_state_key cho {channel} bị ghi dù run thất bại -- sẽ chặn nhầm retry tuần này"
    assert "last_run_key" not in state, "last_run_key không được ghi khi có had_hard_failure"
    assert exit_code != 0, "main() phải trả về exit code khác 0 khi có lỗi thật (had_hard_failure)"


def test_successful_long_run_writes_state_key_and_exits_zero(monkeypatch):
    """Đối chứng: khi run_long_batch() thành công (exit_code=0), state key
    PHẢI được ghi (giữ đúng guard tối đa 1 lần/kênh/tuần cho lần THÀNH CÔNG),
    và main() trả về 0."""
    monkeypatch.setattr(twb, "run_long_batch", lambda channel, topic, creds, dry_run: (0, "OK"))

    exit_code = twb.main()

    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8"))
    week_key = twb.iso_week_key(__import__("datetime").datetime.now())
    for channel in twb.CHANNELS:
        assert f"long_{channel}_{week_key}" in state
    assert state.get("last_run_key") == f"{week_key}-tue"
    assert exit_code == 0


def test_failed_short_run_does_not_write_last_run_key(monkeypatch):
    """Đối chứng cho nhánh Short (Codex CLI review chỉ ra: test cũ chỉ cover
    Long, chưa cover Short thất bại độc lập) -- FS dùng mode auto_discover
    nên sẽ đi vào nhánh gọi run_short_batch() thật (không phải manual_only
    như CL). Cho deficit > 0 CHỈ ở FS, run_short_batch() trả lỗi thật ->
    last_run_key KHÔNG được ghi, exit code khác 0."""
    def fake_counts(creds, days):
        # FS thiếu slot (deficit > 0), BUD/CL đã đủ -- cô lập lỗi vào đúng FS.
        if "phong_thuy" in creds:
            return {d: 0 for d in days}
        return {d: twb.SHORTS_PER_DAY for d in days}
    monkeypatch.setattr(twb, "fetch_scheduled_counts_per_day", fake_counts)
    monkeypatch.setattr(twb, "run_short_batch", lambda channel, topic, creds, mode, count, dry_run: (1, "lỗi short thật giả lập"))
    monkeypatch.setattr(twb, "run_long_batch", lambda channel, topic, creds, dry_run: (0, "OK"))

    exit_code = twb.main()

    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8")) if twb.STATE_PATH.exists() else {}
    assert "last_run_key" not in state, "last_run_key không được ghi khi Short thất bại thật"
    assert exit_code != 0


# ─── Command construction (Codex CLI review round 2: run_short_batch()/
# run_long_batch() giờ gọi run_script() -- mock THẲNG twb.run_script, assert
# TỪNG tham số riêng (script_path/args/python_bin/cwd/timeout/dry_run/
# dry_run_message) thay vì 1 cmd list đã lắp sẵn, đúng chữ ký hàm mới) ────

def test_run_short_batch_auto_discover_builds_correct_args(monkeypatch):
    captured = {}
    monkeypatch.setattr(twb, "run_script", lambda script_path, args, python_bin, cwd, timeout, dry_run, dry_run_message, runner_label=None: captured.update(
        script_path=script_path, args=args, python_bin=python_bin, cwd=cwd, timeout=timeout,
        dry_run=dry_run, dry_run_message=dry_run_message, runner_label=runner_label) or (0, "ok"))

    twb.run_short_batch("FS", "Phong Thủy", str(twb.PROJECT_ROOT / ".youtube_channels/phong_thuy.json"), "auto_discover", 3, False)

    assert captured["script_path"] == twb.SHORT_BATCH_RUNNER_SCRIPT
    assert captured["args"] == [
        "--topic", "Phong Thủy", "--credentials",
        str(twb.PROJECT_ROOT / ".youtube_channels/phong_thuy.json"), "--count", "3", "--auto-discover",
    ]
    assert captured["python_bin"] == twb.PY
    assert captured["cwd"] == twb.PROJECT_ROOT
    assert captured["timeout"] == 7200
    assert captured["dry_run"] is False
    assert captured["runner_label"] == "Short batch"
    assert "short_batch_runner.py" in captured["dry_run_message"]
    assert "Phong Thủy" in captured["dry_run_message"]


def test_run_short_batch_episodes_06_includes_short_playlist(monkeypatch):
    captured = {}
    monkeypatch.setattr(twb, "run_script", lambda script_path, args, python_bin, cwd, timeout, dry_run, dry_run_message, runner_label=None: captured.update(args=args) or (0, "ok"))

    twb.run_short_batch("BUD", "Phật giáo", "creds.json", "episodes_06", 5, False)

    args = captured["args"]
    assert "--episodes" in args and args[args.index("--episodes") + 1] == "06"
    assert "--playlist" in args
    assert args[args.index("--playlist") + 1] == twb.SHORT_EXTRACT_PLAYLIST_BY_CHANNEL["BUD"]


def test_run_short_batch_episodes_06_no_playlist_for_channel_without_one(monkeypatch):
    captured = {}
    monkeypatch.setattr(twb, "run_script", lambda script_path, args, python_bin, cwd, timeout, dry_run, dry_run_message, runner_label=None: captured.update(args=args) or (0, "ok"))

    twb.run_short_batch("FS", "Phong Thủy", "creds.json", "episodes_06", 1, False)

    assert "--playlist" not in captured["args"]


def test_run_short_batch_dry_run_forwards_dry_run_flag(monkeypatch):
    captured = {}
    monkeypatch.setattr(twb, "run_script", lambda script_path, args, python_bin, cwd, timeout, dry_run, dry_run_message, runner_label=None: captured.update(dry_run=dry_run) or (0, "ok"))

    twb.run_short_batch("FS", "Phong Thủy", "creds.json", "auto_discover", 1, True)
    assert captured["dry_run"] is True


def test_run_long_batch_with_playlist_channel(monkeypatch):
    captured = {}
    monkeypatch.setattr(twb, "run_script", lambda script_path, args, python_bin, cwd, timeout, dry_run, dry_run_message, runner_label=None: captured.update(
        script_path=script_path, args=args, timeout=timeout, dry_run_message=dry_run_message, runner_label=runner_label) or (0, "ok"))

    twb.run_long_batch("BUD", "Phật giáo", ".youtube_channels/phat_giao.json", False)

    assert captured["script_path"] == twb.LONG_BATCH_RUNNER_SCRIPT
    args = captured["args"]
    assert "--domain" in args and args[args.index("--domain") + 1] == "BUD"
    assert "--playlist" in args and args[args.index("--playlist") + 1] == twb.LONG_PLAYLIST_BY_CHANNEL["BUD"]
    assert captured["timeout"] == 14400
    assert captured["runner_label"] == "Long batch"
    assert "long_batch_runner.py" in captured["dry_run_message"]


def test_run_long_batch_without_playlist_channel(monkeypatch):
    captured = {}
    monkeypatch.setattr(twb, "run_script", lambda script_path, args, python_bin, cwd, timeout, dry_run, dry_run_message, runner_label=None: captured.update(args=args) or (0, "ok"))

    twb.run_long_batch("FS", "Phong Thủy", "creds.json", False)
    assert "--playlist" not in captured["args"]

    twb.run_long_batch("CL", "Hình Sự", "creds.json", False)
    assert "--playlist" not in captured["args"]


# ─── Missing-runner "external entrypoint" scenarios (Codex CLI review
# round 2, thiết kế trước khi implement): short_batch_runner.py/
# long_batch_runner.py THẬT SỰ có thể tồn tại trên đĩa máy dev (untracked,
# không phải không có mặt) -- KHÔNG được dựa vào việc chúng "tình cờ vắng
# mặt". Trỏ thẳng SHORT/LONG_BATCH_RUNNER_SCRIPT sang đường dẫn tmp_path
# CHẮC CHẮN không tồn tại, để chạy THẬT xuyên suốt main() ->
# run_short_batch()/run_long_batch() -> run_script() (KHÔNG mock 2 hàm đó),
# chứng minh toàn chuỗi đúng mà không cần pipeline thật.  ──────────────

def test_missing_short_runner_fails_closed_end_to_end(monkeypatch, tmp_path):
    def fake_counts(creds, days):
        # FS thiếu slot -- bắt buộc đi vào nhánh gọi run_short_batch() thật
        # (mode auto_discover); BUD/CL đã đủ để cô lập lỗi đúng vào FS.
        if "phong_thuy" in creds:
            return {d: 0 for d in days}
        return {d: twb.SHORTS_PER_DAY for d in days}
    monkeypatch.setattr(twb, "fetch_scheduled_counts_per_day", fake_counts)
    monkeypatch.setattr(twb, "SHORT_BATCH_RUNNER_SCRIPT", tmp_path / "definitely_missing_short_runner.py")
    monkeypatch.setattr(twb, "run_long_batch", lambda channel, topic, creds, dry_run: (0, "OK"))

    exit_code = twb.main()

    log_lines = twb.LOG_PATH.read_text(encoding="utf-8").splitlines()
    assert any("Short batch" in line and "không tồn tại" in line for line in log_lines), \
        "Log phải chứa thông báo rõ ràng 'Short batch ... không tồn tại', không phải traceback OS mơ hồ"
    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8")) if twb.STATE_PATH.exists() else {}
    assert "last_run_key" not in state
    assert exit_code != 0


def test_missing_long_runner_fails_closed_end_to_end(monkeypatch, tmp_path):
    monkeypatch.setattr(twb, "LONG_BATCH_RUNNER_SCRIPT", tmp_path / "definitely_missing_long_runner.py")

    exit_code = twb.main()

    log_lines = twb.LOG_PATH.read_text(encoding="utf-8").splitlines()
    assert any("Long batch" in line and "không tồn tại" in line for line in log_lines)
    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8")) if twb.STATE_PATH.exists() else {}
    week_key = twb.iso_week_key(__import__("datetime").datetime.now())
    for channel in twb.CHANNELS:
        assert f"long_{channel}_{week_key}" not in state
    assert "last_run_key" not in state
    assert exit_code != 0


def test_mixed_outcome_keeps_successful_channel_state_but_not_last_run_key(monkeypatch):
    """1 channel Long thành công, channel khác thất bại thật trong CÙNG 1
    lần chạy -- long_state_key của channel THÀNH CÔNG vẫn phải được giữ lại
    (tiến triển từng phần hợp lệ), nhưng last_run_key (áp dụng cho CẢ chân)
    không được ghi vì có ít nhất 1 lỗi thật."""
    def fake_run_long_batch(channel, topic, creds, dry_run):
        if channel == "FS":
            return 0, "OK"
        return 1, "lỗi thật giả lập"
    monkeypatch.setattr(twb, "run_long_batch", fake_run_long_batch)

    exit_code = twb.main()

    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8"))
    week_key = twb.iso_week_key(__import__("datetime").datetime.now())
    assert f"long_FS_{week_key}" in state, "channel THÀNH CÔNG (FS) phải giữ được state key"
    assert f"long_BUD_{week_key}" not in state, "channel THẤT BẠI (BUD) không được ghi state key"
    assert f"long_CL_{week_key}" not in state, "channel THẤT BẠI (CL) không được ghi state key"
    assert "last_run_key" not in state, "last_run_key không được ghi khi có BẤT KỲ lỗi thật nào trong lần chạy"
    assert exit_code != 0


def test_retry_after_partial_failure_only_retries_failed_channels(monkeypatch):
    """Chứng minh retry AN TOÀN xuyên 2 lần gọi main() với CÙNG state trên
    đĩa: lần 1 FS thành công + BUD/CL thất bại; lần 2 (retry) TẤT CẢ thành
    công -- FS (đã ghi state key từ lần 1) KHÔNG được gọi lại
    run_long_batch(), còn BUD/CL (chưa ghi) PHẢI được gọi lại."""
    calls = []

    def fake_run_long_batch_attempt1(channel, topic, creds, dry_run):
        calls.append(channel)
        return (0, "OK") if channel == "FS" else (1, "lỗi thật giả lập")
    monkeypatch.setattr(twb, "run_long_batch", fake_run_long_batch_attempt1)
    exit_code_1 = twb.main()
    assert exit_code_1 != 0
    assert calls == ["FS", "BUD", "CL"], "Lần 1: cả 3 channel đều được thử (chưa có state nào)"

    calls.clear()

    def fake_run_long_batch_attempt2(channel, topic, creds, dry_run):
        calls.append(channel)
        return 0, "OK"
    monkeypatch.setattr(twb, "run_long_batch", fake_run_long_batch_attempt2)
    exit_code_2 = twb.main()
    assert exit_code_2 == 0
    assert calls == ["BUD", "CL"], "Lần 2 (retry): CHỈ BUD/CL được thử lại -- FS đã có state key, bỏ qua đúng như guard 'tối đa 1 lần/kênh/tuần'"

    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8"))
    week_key = twb.iso_week_key(__import__("datetime").datetime.now())
    for channel in twb.CHANNELS:
        assert f"long_{channel}_{week_key}" in state
    assert state.get("last_run_key") == f"{week_key}-tue"


# ─── Concurrency-safety (Codex CLI review round 3, HIGH finding): nhánh
# Long trước đây KHÔNG hề khoá gì -- bug thật CÓ SẴN TỪ TRƯỚC đợt refactor
# retry/state, sửa luôn vì cùng chủ đề "retry safety" (xem comment tại
# chính vị trí sửa trong twice_weekly_batch.py). Thiết kế cuối: ĐÚNG 1 lock
# bao trọn CẢ vòng lặp Long (không phải 1 lock/channel) -- 1 file
# state.json dùng chung cho cả 3 channel, lock riêng từng channel vẫn để
# lọt race TRÊN CHÍNH FILE STATE giữa 2 channel khác nhau. Với 1 lock duy
# nhất, 2 tiến trình THẬT chạy chồng nhau tự động SERIALIZE hoàn toàn ở
# đúng đoạn này (tiến trình sau BLOCK tới khi tiến trình trước xong, không
# chỉ "graceful" mà THẬT SỰ không thể race) -- không cần giả lập ghi đè
# giữa chừng (không có nơi nào khác trong codebase ghi state.json ngoài
# đúng kỷ luật khoá này). Test dưới đây xác nhận: state ĐÃ CÓ SẴN trên đĩa
# (do 1 lần main() TRƯỚC ghi, mô phỏng qua ghi tay trước khi gọi main())
# được đọc lại ĐÚNG khi vào lock -- không dùng bản `state` nạp lúc đầu
# main() (trước cả vòng lặp Short), chứng minh guard "tối đa 1 lần/kênh/
# tuần" phản ánh đúng trạng thái MỚI NHẤT. ──────────────────────────────

def test_long_loop_picks_up_state_written_just_before_lock_entry(monkeypatch):
    """State ban đầu nạp ở ĐẦU main() (biến `state` module-level trước
    vòng lặp Short) KHÔNG được dùng cho quyết định Long -- phải đọc lại
    NGAY khi vào lock. Ghi tay long_FS_<week> vào đĩa để mô phỏng "đã có
    sẵn từ trước" (không phải do chính main() gọi này ghi) -- FS phải bị
    bỏ qua, BUD/CL vẫn được thử."""
    week_key = twb.iso_week_key(__import__("datetime").datetime.now())
    twb.STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    twb.STATE_PATH.write_text(json.dumps({f"long_FS_{week_key}": "2026-08-01T00:00:00Z"}, ensure_ascii=False, indent=2), encoding="utf-8")

    calls = []
    monkeypatch.setattr(twb, "run_long_batch", lambda channel, topic, creds, dry_run: (calls.append(channel), (0, "OK"))[1])

    exit_code = twb.main()

    assert calls == ["BUD", "CL"], "FS đã có state key SẴN trên đĩa TRƯỚC khi gọi main() -- phải bị bỏ qua"
    state = json.loads(twb.STATE_PATH.read_text(encoding="utf-8"))
    assert f"long_FS_{week_key}" in state, "state key có sẵn từ trước phải được GIỮ LẠI, không bị xoá"
    assert f"long_BUD_{week_key}" in state
    assert f"long_CL_{week_key}" in state
    assert exit_code == 0


def test_dry_run_does_not_create_lock_dir(monkeypatch):
    """BUG THẬT đã sửa (Codex CLI review): LOCK_DIR.mkdir() trước đây chạy
    vô điều kiện, kể cả dry-run -- vi phạm đúng lời hứa 'KHÔNG ghi bất kỳ
    file nào' đã ghi ở docstring đầu file."""
    monkeypatch.setattr(twb, "fetch_scheduled_counts_per_day", lambda creds, days: {d: 0 for d in days})
    monkeypatch.setattr(sys, "argv", ["twice_weekly_batch.py", "--dry-run", "--force-leg", "tue"])

    twb.main()

    assert not twb.LOCK_DIR.exists(), "dry-run KHÔNG được tạo LOCK_DIR"


# ─── Regression cho HIGH finding round 3 (Codex CLI review): ghi
# last_run_key NGOÀI lock Long -- kể cả có "đọc lại state ngay trước khi
# ghi" -- không loại trừ race với 1 tiến trình khác đang giữ CHÍNH lock đó
# (đọc-rồi-ghi ngoài lock không atomic với read-modify-write của tiến trình
# kia bên trong lock). Sửa: ghi last_run_key NGAY TRONG lock Long, dùng
# chung state đã đọc khi vào lock. Test dưới đây không mô phỏng race thật
# (khó làm quyết định trong unit test đơn luồng) mà xác nhận TRỰC TIẾP thứ
# tự sự kiện: lệnh ghi last_run_key phải xảy ra giữa lúc lock Long được
# __enter__ và __exit__, không phải sau khi đã __exit__. ──────────────────

def test_last_run_key_write_happens_inside_long_lock(monkeypatch):
    """Bọc FileLock/save_state để ghi lại thứ tự sự kiện thật, xác nhận
    save_state(last_run_key=...) nằm GIỮA enter và exit của lock Long --
    không phải sau khi lock đã được thả."""
    events = []
    real_file_lock = twb.FileLock
    long_lock_path = str(twb.LOCK_DIR / "twice_weekly_long")

    class RecordingLock:
        def __init__(self, path):
            self._inner = real_file_lock(path)
            self._path = str(path)

        def __enter__(self):
            self._inner.__enter__()
            events.append(("enter", self._path))
            return self

        def __exit__(self, *exc_info):
            events.append(("exit", self._path))
            return self._inner.__exit__(*exc_info)

    real_save_state = twb.save_state

    def recording_save_state(path, state):
        if "last_run_key" in state:
            events.append(("save_last_run_key", None))
        real_save_state(path, state)

    monkeypatch.setattr(twb, "FileLock", RecordingLock)
    monkeypatch.setattr(twb, "save_state", recording_save_state)
    monkeypatch.setattr(twb, "run_long_batch", lambda channel, topic, creds, dry_run: (0, "OK"))

    exit_code = twb.main()

    assert exit_code == 0
    enter_idx = events.index(("enter", long_lock_path))
    exit_idx = events.index(("exit", long_lock_path))
    save_idx = events.index(("save_last_run_key", None))
    assert enter_idx < save_idx < exit_idx, (
        "last_run_key phải được ghi TRONG lúc còn giữ lock Long (giữa enter "
        f"và exit), không phải sau khi lock đã thả -- events thực tế: {events}"
    )
