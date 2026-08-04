"""Regression test cho batch_orchestration.py -- module retry/state/exit-
code TÁCH RIÊNG khỏi twice_weekly_batch.py để KHÔNG kéo theo closure ~36
file của pipeline sinh nội dung thật (xem docstring module đó + báo cáo
dependency-closure/Codex CLI adversarial review trong lịch sử phiên làm
việc, audit launchd 04/08). Test này khoá đúng:
  - 2 predicate đã sửa bug thật (should_persist_channel_state,
    aggregate_exit_code);
  - run_command() forward ĐÚNG cmd/cwd/timeout/capture_output/text, dry-run
    không bao giờ gọi subprocess thật, ghép + cắt output ĐÚNG cách cũ;
  - run_script() validate script tồn tại TRƯỚC khi subprocess (trừ nhánh
    dry-run), thông báo rõ ràng kèm tên runner + đường dẫn khi thiếu;
  - load_state/save_state round-trip + xử lý file thiếu/hỏng;
  - determine_leg/iso_week_key pin theo ngày biết trước (chống trôi hành
    vi so với bản gốc);
  - log_run ghi đúng shape JSONL.

Codex CLI review (trước khi implement) nhấn mạnh: test run_command() chỉ
chứng minh forward đúng, KHÔNG chứng minh run_short_batch()/run_long_batch()
trong twice_weekly_batch.py build đúng cmd -- phần đó được cover riêng ở
test_twice_weekly_batch.py (mới, bổ sung cùng đợt)."""
import json
import subprocess
from datetime import datetime
from pathlib import Path

import batch_orchestration as bo


# ─── should_persist_channel_state / aggregate_exit_code (2 bug thật) ──────

def test_should_persist_channel_state_only_on_success():
    assert bo.should_persist_channel_state(0) is True
    assert bo.should_persist_channel_state(1) is False
    assert bo.should_persist_channel_state(127) is False


def test_aggregate_exit_code_reflects_hard_failure():
    assert bo.aggregate_exit_code(True) == 1
    assert bo.aggregate_exit_code(False) == 0


# ─── run_command() ─────────────────────────────────────────────────────

def test_run_command_dry_run_never_invokes_subprocess(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("subprocess.run() KHÔNG được gọi khi dry_run=True")
    monkeypatch.setattr(subprocess, "run", _boom)

    exit_code, output = bo.run_command(
        ["some", "cmd"], cwd=Path("."), timeout=10, dry_run=True, dry_run_message="[DRY-RUN] msg"
    )
    assert exit_code == 0
    assert output == "[DRY-RUN] msg"


def test_run_command_real_invocation_forwards_exact_args(monkeypatch):
    captured = {}

    class FakeResult:
        returncode = 3
        stdout = "OUT"
        stderr = "ERR"

    def fake_run(cmd, cwd, capture_output, text, timeout):
        captured.update(cmd=cmd, cwd=cwd, capture_output=capture_output, text=text, timeout=timeout)
        return FakeResult()

    monkeypatch.setattr(subprocess, "run", fake_run)

    cmd = ["/venv/python3", "some_script.py", "--flag", "value"]
    exit_code, output = bo.run_command(cmd, cwd=Path("/proj"), timeout=999, dry_run=False, dry_run_message="unused")

    assert captured["cmd"] == cmd
    assert captured["cwd"] == Path("/proj")
    assert captured["capture_output"] is True
    assert captured["text"] is True
    assert captured["timeout"] == 999
    assert exit_code == 3
    assert output == "OUTERR"  # stdout TRƯỚC stderr, đúng thứ tự bản gốc


def test_run_command_truncates_to_last_2000_chars_after_concatenation(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "A" * 1500
        stderr = "B" * 1500

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())
    _, output = bo.run_command(["x"], cwd=Path("."), timeout=1, dry_run=False, dry_run_message="unused")
    assert len(output) == 2000
    assert output == ("A" * 1500 + "B" * 1500)[-2000:]


def test_run_command_handles_none_stdout_stderr(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = None
        stderr = None

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())
    exit_code, output = bo.run_command(["x"], cwd=Path("."), timeout=1, dry_run=False, dry_run_message="unused")
    assert exit_code == 0
    assert output == ""


# ─── run_script() -- "external entrypoint" runtime validation ────────────

def test_run_script_missing_script_fails_with_clear_message_no_subprocess(monkeypatch, tmp_path):
    def _boom(*a, **k):
        raise AssertionError("subprocess.run() KHÔNG được gọi khi script thiếu")
    monkeypatch.setattr(subprocess, "run", _boom)

    missing = tmp_path / "does_not_exist_runner.py"
    exit_code, message = bo.run_script(
        missing, ["--foo", "bar"], "python3", cwd=tmp_path, timeout=10,
        dry_run=False, dry_run_message="unused", runner_label="Short batch",
    )
    assert exit_code == 1
    assert "Short batch" in message
    assert str(missing) in message


def test_run_script_existing_script_forwards_exact_command(monkeypatch, tmp_path):
    real_script = tmp_path / "real_runner.py"
    real_script.write_text("x")
    captured = {}

    class FakeResult:
        returncode = 0
        stdout = "OK"
        stderr = ""

    def fake_run(cmd, cwd, capture_output, text, timeout):
        captured.update(cmd=cmd, cwd=cwd, timeout=timeout)
        return FakeResult()
    monkeypatch.setattr(subprocess, "run", fake_run)

    exit_code, output = bo.run_script(
        real_script, ["--a", "1"], "/venv/python3", cwd=tmp_path, timeout=42,
        dry_run=False, dry_run_message="unused",
    )
    assert exit_code == 0
    assert output == "OK"
    assert captured["cmd"] == ["/venv/python3", str(real_script), "--a", "1"]
    assert captured["cwd"] == tmp_path
    assert captured["timeout"] == 42


def test_run_script_dry_run_skips_existence_check_entirely(monkeypatch, tmp_path):
    """Dry-run PHẢI chạy được dù script không tồn tại -- checkout chưa có
    short_batch_runner.py/long_batch_runner.py vẫn phải dry-run được."""
    def _boom(*a, **k):
        raise AssertionError("subprocess.run() KHÔNG được gọi khi dry_run=True")
    monkeypatch.setattr(subprocess, "run", _boom)

    missing = tmp_path / "does_not_exist_runner.py"
    exit_code, message = bo.run_script(
        missing, [], "python3", cwd=tmp_path, timeout=10,
        dry_run=True, dry_run_message="[DRY-RUN] msg",
    )
    assert exit_code == 0
    assert message == "[DRY-RUN] msg"


# ─── load_state / save_state ───────────────────────────────────────────

def test_load_save_state_roundtrip(tmp_path):
    state_path = tmp_path / "state.json"
    bo.save_state(state_path, {"a": 1, "b": "hai"})
    assert bo.load_state(state_path) == {"a": 1, "b": "hai"}
    # atomic write: không để lại file .tmp mồ côi
    assert not state_path.with_suffix(".tmp").exists()


def test_load_state_missing_file_returns_empty_dict(tmp_path):
    assert bo.load_state(tmp_path / "does_not_exist.json") == {}


def test_load_state_corrupt_json_returns_empty_dict(tmp_path):
    state_path = tmp_path / "corrupt.json"
    state_path.write_text("{not valid json", encoding="utf-8")
    assert bo.load_state(state_path) == {}


def test_save_state_writes_ensure_ascii_false_indent_2(tmp_path):
    state_path = tmp_path / "state.json"
    bo.save_state(state_path, {"key": "tiếng Việt"})
    raw = state_path.read_text(encoding="utf-8")
    assert "tiếng Việt" in raw  # ensure_ascii=False -- không escape unicode
    assert "\n  " in raw  # indent=2


# ─── determine_leg / iso_week_key (pin theo ngày biết trước) ──────────

def test_determine_leg_tuesday_returns_wed_thu_fri():
    # 2026-08-04 là Thứ 3 thật (đã xác nhận trong phiên làm việc)
    tue = datetime(2026, 8, 4)
    leg, days = bo.determine_leg(tue)
    assert leg == "tue"
    assert days == ["2026-08-05", "2026-08-06", "2026-08-07"]


def test_determine_leg_friday_returns_sat_sun_mon_tue():
    fri = datetime(2026, 8, 7)
    leg, days = bo.determine_leg(fri)
    assert leg == "fri"
    assert days == ["2026-08-08", "2026-08-09", "2026-08-10", "2026-08-11"]


def test_determine_leg_other_weekday_returns_none():
    monday = datetime(2026, 8, 3)
    assert bo.determine_leg(monday) is None


def test_iso_week_key_format():
    assert bo.iso_week_key(datetime(2026, 8, 4)) == "2026-W32"


# ─── log_run ────────────────────────────────────────────────────────────

def test_log_run_writes_expected_jsonl_shape(tmp_path):
    log_path = tmp_path / "log.jsonl"
    bo.log_run(log_path, "2026-08-04T00:00:00Z", "FS", "short", "SUCCESS", "chi tiết", 0)
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry == {
        "run_at": "2026-08-04T00:00:00Z", "channel": "FS", "kind": "short",
        "status": "SUCCESS", "detail": "chi tiết", "exit_code": 0,
    }


def test_log_run_appends_multiple_entries(tmp_path):
    log_path = tmp_path / "log.jsonl"
    bo.log_run(log_path, "t1", "FS", "short", "A", "d1")
    bo.log_run(log_path, "t2", "BUD", "long", "B", "d2", 1)
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2


# ─── fetch_scheduled_counts_per_day (pagination/counting) ──────────────

def test_fetch_scheduled_counts_per_day_full_flow(monkeypatch):
    """Giả lập chuỗi gọi API thật: 1) lấy uploads playlist id; 2) phân
    trang playlistItems (2 trang, có pageToken); 3) đếm status theo batch
    50 ID -- chỉ đếm private + có publishAt rơi đúng ngày mục tiêu."""
    calls = []

    def fake_get(creds, url, params):
        calls.append((url, dict(params)))
        if url == bo.CHANNELS_URL:
            return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU_FAKE"}}}]}
        if url == bo.PLAYLIST_ITEMS_URL:
            if "pageToken" not in params:
                return {
                    "items": [{"contentDetails": {"videoId": f"v{i}"}} for i in range(50)],
                    "nextPageToken": "PAGE2",
                }
            return {
                "items": [{"contentDetails": {"videoId": "v_last"}}],
            }
        if url == bo.VIDEOS_URL:
            ids = params["id"].split(",")
            items = []
            for vid in ids:
                if vid == "v0":
                    items.append({"status": {"privacyStatus": "private", "publishAt": "2026-08-05T08:00:00Z"}})
                elif vid == "v1":
                    items.append({"status": {"privacyStatus": "private", "publishAt": "2026-08-06T08:00:00Z"}})
                elif vid == "v2":
                    items.append({"status": {"privacyStatus": "public", "publishAt": "2026-08-05T08:00:00Z"}})  # public -- KHÔNG đếm
                elif vid == "v3":
                    items.append({"status": {"privacyStatus": "private"}})  # thiếu publishAt -- KHÔNG đếm
                elif vid == "v4":
                    items.append({"status": {"privacyStatus": "private", "publishAt": "2099-01-01T00:00:00Z"}})  # ngoài target_days -- KHÔNG đếm
                else:
                    items.append({"status": {"privacyStatus": "private", "publishAt": "2026-08-05T08:00:00Z"}})
            return {"items": items}
        raise AssertionError(f"URL không mong đợi: {url}")

    monkeypatch.setattr(bo, "_get", fake_get)

    target_days = ["2026-08-05", "2026-08-06", "2026-08-07"]
    counts = bo.fetch_scheduled_counts_per_day("creds.json", target_days)

    assert counts["2026-08-05"] >= 1  # v0 + phần lớn video "khác" cũng rơi vào ngày này
    assert counts["2026-08-06"] == 1  # đúng v1
    assert counts["2026-08-07"] == 0
    # pageToken THẬT SỰ được truyền cho lần gọi phân trang thứ 2
    playlist_calls = [p for u, p in calls if u == bo.PLAYLIST_ITEMS_URL]
    assert len(playlist_calls) == 2
    assert playlist_calls[1].get("pageToken") == "PAGE2"
    # batching video status theo đúng 50 ID / lần gọi
    videos_calls = [p for u, p in calls if u == bo.VIDEOS_URL]
    assert all(len(p["id"].split(",")) <= 50 for p in videos_calls)


def test_fetch_scheduled_counts_per_day_stops_at_200_ids(monkeypatch):
    """Giữ đúng hành vi cũ: dừng phân trang khi đã gom >= 200 video ID,
    không gọi playlistItems vô hạn."""
    call_count = {"playlist_items": 0}

    def fake_get(creds, url, params):
        if url == bo.CHANNELS_URL:
            return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU_FAKE"}}}]}
        if url == bo.PLAYLIST_ITEMS_URL:
            call_count["playlist_items"] += 1
            return {
                "items": [{"contentDetails": {"videoId": f"v{call_count['playlist_items']}_{i}"}} for i in range(50)],
                "nextPageToken": f"PAGE{call_count['playlist_items'] + 1}",
            }
        if url == bo.VIDEOS_URL:
            return {"items": []}
        raise AssertionError(f"URL không mong đợi: {url}")

    monkeypatch.setattr(bo, "_get", fake_get)
    bo.fetch_scheduled_counts_per_day("creds.json", ["2026-08-05"])
    # 200 ID / 50 mỗi trang = ĐÚNG 4 lần gọi trước khi dừng (mỗi trang luôn
    # còn nextPageToken -- nếu dừng SỚM HƠN 4 thì đã có bug ở điều kiện
    # dừng, không chỉ "dừng trong giới hạn").
    assert call_count["playlist_items"] == 4
