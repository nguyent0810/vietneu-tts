"""Regression test cho fix "isolate twice-weekly run logs from daily health
checks" (follow-up sau BLOCKING finding từ Codex CLI outgoing-range review,
xem báo cáo verification 04/08): twice_weekly_batch.py TỪNG ghi vô tình vào
đúng output/shorts/daily_run_log.jsonl mà short_health_check.py đọc để phát
hiện "sản xuất bị chặn đứng" -- record của nó không có field `n_done`, bị
đọc mặc định thành 0, khiến MỌI lần twice-weekly chạy kích hoạt cảnh báo
"production stalled" SAI trên daily log. Sửa bằng cách tách file hoàn toàn
(xem twice_weekly_batch.py: LOG_PATH giờ trỏ "twice_weekly_run_log.jsonl"),
không đổi gì ở phía health-check.

Đồng thời cover 1 bug thật khác phát hiện khi audit lại module này để làm
fix trên: check_missing_or_stale_run() áp cảnh báo cadence 26h VÔ ĐIỀU KIỆN
dựa trên plist tồn tại trên đĩa -- không đúng nếu daily job đã bị
`launchctl bootout` có chủ đích (retired, thay bằng twice_weekly_batch.py)
nhưng file plist chưa bị xoá. Sửa bằng _daily_job_registered() kiểm tra
đăng ký THẬT với launchd trước tiên.

Round 2 (Codex CLI follow-up review, BLOCKING): fix đầu tiên chỉ gate
check_missing_or_stale_run() -- check_recent_runs_for_stall() vẫn chạy VÔ
ĐIỀU KIỆN, độc lập với registration status, nên 2 dòng log CŨ (có n_done=0,
còn sót lại từ trước khi job retire hoặc từ chính lỗi ghi-nhầm-file gốc)
vẫn kích hoạt "production stalled" SAI mãi mãi sau khi job đã retired. Sửa:
cả 2 hàm check giờ nhận `daily_job_registered: bool` làm tham số tường
minh, xác định ĐÚNG 1 LẦN trong main()."""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

import short_health_check as shc
import twice_weekly_batch as twb


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture(autouse=True)
def _isolated_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(shc, "DAILY_LOG_PATH", tmp_path / "daily_run_log.jsonl")
    monkeypatch.setattr(shc, "LAUNCHD_PLIST_PATH", tmp_path / "com.vieneutts.dailyshortbatch.plist")


def _write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")


def test_default_log_path_is_dedicated_not_shared_with_daily():
    """twice_weekly_batch.py's LOG_PATH default (trước khi bất kỳ test nào
    monkeypatch nó) PHẢI là file riêng, KHÔNG trùng daily_run_log.jsonl --
    kiểm tra qua fresh import ở subprocess để tránh phụ thuộc thứ tự
    autouse fixture của test_twice_weekly_batch.py (đã override LOG_PATH
    trước khi bất kỳ test body nào trong file đó chạy)."""
    result = subprocess.run(
        [sys.executable, "-c", "import twice_weekly_batch as twb; print(twb.LOG_PATH.name)"],
        cwd=str(twb.PROJECT_ROOT), capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "twice_weekly_run_log.jsonl"
    assert result.stdout.strip() != "daily_run_log.jsonl"


def test_health_check_module_has_no_reference_to_twice_weekly_log():
    """"health-check bỏ qua HOÀN TOÀN log twice-weekly" -- dạng mạnh nhất:
    xác nhận module short_health_check.py không hề tham chiếu tên FILE
    hay SCHEMA của log twice-weekly (không có code path nào biết đọc/parse
    nó) -- không cấm nhắc TÊN twice_weekly_batch.py trong comment giải
    thích bối cảnh (retired job), chỉ cấm coupling chức năng thật."""
    source = shc.__file__
    with open(source, encoding="utf-8") as f:
        content = f.read()
    assert "twice_weekly_run_log" not in content
    assert "batch_orchestration" not in content
    assert "log_run" not in content


def test_health_check_ignores_twice_weekly_log_file_entirely(tmp_path):
    """Đặt 1 file "twice_weekly_run_log.jsonl" ngay cạnh DAILY_LOG_PATH,
    đầy record schema twice-weekly (không có n_done -- đúng dạng TỪNG gây
    báo động sai) -- DAILY_LOG_PATH có 2 record daily THẬT gần đây, đủ
    n_done > 0. Health-check phải hoàn toàn KHÔNG bị ảnh hưởng bởi file
    twice-weekly (không đọc nó, không suy diễn gì từ nó)."""
    now = datetime.now(timezone.utc)
    twice_weekly_log = tmp_path / "twice_weekly_run_log.jsonl"
    _write_jsonl(twice_weekly_log, [
        {"run_at": _iso(now), "channel": "FS", "kind": "long", "status": "SUCCESS", "detail": "...", "exit_code": 0}
        for _ in range(5)
    ])

    _write_jsonl(shc.DAILY_LOG_PATH, [
        {"run_at": _iso(now), "exit_code": 0, "n_done": 3, "n_failed": 0},
        {"run_at": _iso(now), "exit_code": 0, "n_done": 2, "n_failed": 0},
    ])

    stalled, reason = shc.check_recent_runs_for_stall(daily_job_registered=True)
    assert stalled is False, f"health-check bị ảnh hưởng bởi file twice-weekly cạnh đó: {reason}"

    missing, reason2 = shc.check_missing_or_stale_run(daily_job_registered=True)
    assert missing is False, f"health-check bị ảnh hưởng bởi file twice-weekly cạnh đó: {reason2}"


def test_two_daily_zero_done_records_still_report_stalled():
    """Đối chứng: hành vi phát hiện stall GỐC (2 lần chạy daily liên tiếp
    0 đoạn xong, job VẪN đăng ký) phải còn nguyên vẹn sau fix -- fix chỉ
    tách file + gate theo registration, không được làm yếu đi khả năng
    phát hiện stall THẬT của 1 daily job đang hoạt động."""
    now = datetime.now(timezone.utc)
    _write_jsonl(shc.DAILY_LOG_PATH, [
        {"run_at": _iso(now), "exit_code": 0, "n_done": 0, "n_failed": 0},
        {"run_at": _iso(now), "exit_code": 0, "n_done": 0, "n_failed": 0},
    ])

    stalled, reason = shc.check_recent_runs_for_stall(daily_job_registered=True)
    assert stalled is True
    assert "0 đoạn" in reason


def test_fresh_daily_record_is_not_flagged_stale():
    """Đối chứng: 1 record daily THẬT, run_at mới (trong 26h), job đăng ký
    -- không được báo stale (hoàn toàn bình thường)."""
    now = datetime.now(timezone.utc)
    _write_jsonl(shc.DAILY_LOG_PATH, [{"run_at": _iso(now), "exit_code": 0, "n_done": 3, "n_failed": 0}])

    missing, reason = shc.check_missing_or_stale_run(daily_job_registered=True)
    assert missing is False
    assert reason == ""


def test_old_daily_record_with_job_registered_still_reports_stale():
    """Đối chứng: nếu job daily VẪN đăng ký với launchd (chưa retire) nhưng
    log cuối đã quá cũ (>26h) -- vẫn phải báo stale như hành vi gốc. Đảm
    bảo tham số daily_job_registered=True không nuốt mất cảnh báo THẬT."""
    old = datetime.now(timezone.utc) - timedelta(hours=30)
    _write_jsonl(shc.DAILY_LOG_PATH, [{"run_at": _iso(old), "exit_code": 0, "n_done": 3, "n_failed": 0}])

    missing, reason = shc.check_missing_or_stale_run(daily_job_registered=True)
    assert missing is True
    assert "job có thể đã không chạy được" in reason


def test_unregistered_daily_job_reports_clear_retired_status_without_alert():
    """BUG THẬT đã sửa: nếu com.vieneutts.dailyshortbatch KHÔNG đăng ký với
    launchd (retired có chủ đích), health-check KHÔNG được báo động "stale"
    -- nhưng PHẢI trả về 1 lý do RÕ RÀNG phân biệt được với "job registered
    nhưng không chạy" (không suy diễn từ log twice-weekly -- test này thậm
    chí không tạo file twice-weekly nào, chứng minh quyết định không cần
    tới nó). Log daily thiếu hoàn toàn -- vẫn phải không báo động."""
    # DAILY_LOG_PATH không tồn tại (chưa từng ghi gì) -- trường hợp mạnh nhất.
    missing, reason = shc.check_missing_or_stale_run(daily_job_registered=False)
    assert missing is False, f"job đã retired có chủ đích không được báo động: {reason}"
    assert "không đăng ký" in reason or "retire" in reason.lower()
    assert reason != "", "phải có lý do rõ ràng, không được im lặng hoàn toàn"


def test_unregistered_daily_job_status_independent_of_stale_daily_log():
    """Cùng bug, biến thể mạnh hơn: dù DAILY_LOG_PATH CÓ record nhưng đã
    rất cũ (đáng lẽ kích hoạt stale-alert theo cadence 26h cũ) -- 1 khi
    xác nhận job KHÔNG đăng ký, vẫn phải ưu tiên trạng thái "retired rõ
    ràng" thay vì "stale"."""
    very_old = datetime.now(timezone.utc) - timedelta(days=30)
    _write_jsonl(shc.DAILY_LOG_PATH, [{"run_at": _iso(very_old), "exit_code": 0, "n_done": 1, "n_failed": 0}])

    missing, reason = shc.check_missing_or_stale_run(daily_job_registered=False)
    assert missing is False
    assert "không đăng ký" in reason or "retire" in reason.lower()


def test_unregistered_daily_job_suppresses_stall_alert_from_stale_historical_records():
    """BLOCKING finding round 2 (Codex CLI follow-up review): fix đầu tiên
    chỉ gate check_missing_or_stale_run() theo registration -- bỏ sót
    check_recent_runs_for_stall(), vốn chạy độc lập. Kịch bản THẬT: daily
    job đã retired, nhưng 2 dòng CUỐI CÙNG còn sót lại trong
    daily_run_log.jsonl (từ trước khi retire) có n_done=0 -- vì file không
    còn được ghi mới, 2 dòng đó MÃI MÃI là "2 lần chạy gần nhất", kích hoạt
    "production stalled" SAI vĩnh viễn nếu không gate đúng. Xác nhận:
    daily_job_registered=False -> check_recent_runs_for_stall() KHÔNG báo
    động, bất kể nội dung 2 dòng cuối."""
    now = datetime.now(timezone.utc)
    _write_jsonl(shc.DAILY_LOG_PATH, [
        {"run_at": _iso(now - timedelta(days=5)), "exit_code": 0, "n_done": 0, "n_failed": 0},
        {"run_at": _iso(now - timedelta(days=5)), "exit_code": 0, "n_done": 0, "n_failed": 0},
    ])

    stalled, stall_reason = shc.check_recent_runs_for_stall(daily_job_registered=False)
    assert stalled is False, (
        f"job đã retired -- 2 dòng log cũ n_done=0 KHÔNG được kích hoạt "
        f"'production stalled' vĩnh viễn: {stall_reason}"
    )

    missing, missing_reason = shc.check_missing_or_stale_run(daily_job_registered=False)
    assert missing is False
    assert "không đăng ký" in missing_reason or "retire" in missing_reason.lower()


def test_daily_job_registered_helper_uses_real_launchctl_subprocess(monkeypatch):
    """_daily_job_registered() phải gọi `launchctl list <label>` thật và
    map returncode -> bool đúng chiều (0 = có đăng ký)."""
    calls = []

    class FakeResult:
        def __init__(self, returncode):
            self.returncode = returncode

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return FakeResult(0 if "registered-label" in cmd else 1)

    monkeypatch.setattr(shc.subprocess, "run", fake_run)
    monkeypatch.setattr(shc, "DAILY_JOB_LABEL", "registered-label")
    assert shc._daily_job_registered() is True
    assert calls[-1] == ["launchctl", "list", "registered-label"]

    monkeypatch.setattr(shc, "DAILY_JOB_LABEL", "unregistered-label")
    assert shc._daily_job_registered() is False


def test_daily_job_registered_helper_fails_safe_to_true_on_error(monkeypatch):
    """Nếu launchctl không gọi được (OSError) hoặc timeout -- coi như CÓ
    đăng ký (an toàn hơn: vẫn áp cảnh báo daily bình thường thay vì im
    lặng bỏ qua staleness THẬT vì 1 sự cố tạm thời không liên quan)."""
    def raise_oserror(cmd, **kwargs):
        raise OSError("launchctl not found")

    monkeypatch.setattr(shc.subprocess, "run", raise_oserror)
    assert shc._daily_job_registered() is True

    def raise_timeout(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 5)

    monkeypatch.setattr(shc.subprocess, "run", raise_timeout)
    assert shc._daily_job_registered() is True
