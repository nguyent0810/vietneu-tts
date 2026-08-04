"""Giám sát định kỳ hệ thống Short -- KHÔNG cần phiên Claude còn mở, chạy
qua launchd độc lập giống short_batch_runner.py (dùng lại đúng pattern
subprocess gọi agy/codex đã có sẵn trong content_seo.py -- soạn/phản biện
không nhất thiết phải là "tôi" trong phiên chat, chỉ cần gọi đúng 2 CLI
đó qua subprocess, y hệt cách content_seo.py/short_content_planner.py đã
làm suốt phiên làm việc này).

Việc làm mỗi lần chạy:
  1. Đọc registry.json + daily_run_log.jsonl (thuần đọc file, không cần AI).
  2. Kéo view thật của các short đã public (đã qua publish_at) từ YouTube
     Analytics -- so hiệu suất slot "đã chứng minh" vs "giả thuyết".
  3. agy soạn nhận định + Codex phản biện (CÙNG MÔ HÌNH short_content_planner.py,
     tái dùng thẳng, không viết lại) -- nếu có đủ dữ liệu để nói gì đó.
  4. Ghi log JSON. Nếu phát hiện vấn đề NGHIÊM TRỌNG (lỗi liên tiếp nhiều
     ngày, quota cạn kéo dài, hết nguồn nội dung), gửi thông báo macOS
     TRỰC TIẾP (osascript) -- không qua Claude, luôn hoạt động.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import certifi  # noqa: E402
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from content_seo import _run_agy, _run_codex, _extract_json, ContentSeoError  # noqa: E402
from youtube_catalog import get_videos_details  # noqa: E402
# discover_segments() giờ sống ở short_segment_discovery.py (module thuần
# đọc file, không phụ thuộc review/SEO/upload/registry/bgm/youtube_catalog
# như short_batch_runner.py) -- health-check chỉ cần đúng phần đọc file
# này, không cần toàn bộ runner (xem báo cáo dependency-closure + Codex
# CLI adversarial review trong lịch sử phiên làm việc, audit launchd 04/08).
from short_segment_discovery import discover_segments  # noqa: E402
from external_bin import OSASCRIPT_BIN  # noqa: E402

TOPIC = "Phật giáo"  # PHẢI khớp --topic dùng trong scripts/daily_short_batch.sh (mặc định không truyền = topic này)
REGISTRY_PATH = PROJECT_ROOT / "output" / "shorts" / TOPIC / "registry.json"
DAILY_LOG_PATH = PROJECT_ROOT / "output" / "shorts" / "daily_run_log.jsonl"
HEALTH_LOG_PATH = PROJECT_ROOT / "output" / "shorts" / "health_check_log.jsonl"
CREDENTIALS_PATH = PROJECT_ROOT / ".youtube_channels" / "phat_giao.json"
SOURCE_EPISODES = ["06"]  # PHẢI khớp --episodes dùng trong scripts/daily_short_batch.sh

CONSECUTIVE_ZERO_DONE_ALERT_THRESHOLD = 2  # 2 lần chạy liên tiếp 0 short xong -> báo động
LAUNCHD_PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.vieneutts.dailyshortbatch.plist"
STALE_LOG_ALERT_HOURS = 26  # lịch chạy 1 lần/ngày (03:17 giờ hệ thống); >26h không có log mới = ít nhất 1 lần chạy đã không xảy ra hoặc không ghi được log

_ANALYSIS_PROMPT = """Bạn là chuyên gia phân tích hiệu suất YouTube Shorts. Dựa trên dữ liệu THẬT dưới đây (đã public, có view thật), nhận định NGẮN GỌN (3-5 câu) xu hướng đang thấy -- CHỈ nói những gì dữ liệu THỰC SỰ chứng minh được, nếu mẫu còn quá ít thì nói rõ "chưa đủ mẫu để kết luận", không suy đoán.

=== HIỆU SUẤT THEO SLOT (short đã public, có view thật) ===
{slot_data}

Trả về CHỈ 1 JSON object:
{{"finding": "nhận định 3-5 câu", "sample_size_adequate": true/false}}"""

_CRITIQUE_PROMPT = """Phản biện nhận định dưới đây -- có đang suy diễn quá xa dữ liệu không?

=== DỮ LIỆU GỐC ===
{slot_data}

=== NHẬN ĐỊNH CẦN PHẢN BIỆN ===
{finding}

Trả về CHỈ 1 JSON object:
{{"verdict": "PASS" hoặc "FAIL", "feedback": "nếu FAIL, chỉ rõ chỗ suy diễn quá xa; nếu PASS để rỗng"}}"""


def _notify_macos(title: str, message: str) -> None:
    script = f'display notification "{message}" with title "{title}" sound name "Basso"'
    subprocess.run([OSASCRIPT_BIN, "-e", script], check=False)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def check_registry_health() -> dict:
    # BUG ĐÃ SỬA: n_pending trước đây chỉ đếm entry ĐÃ CÓ TRONG registry
    # (status không phải uploaded/failed) -- các đoạn CHƯA TỪNG được
    # batch runner đụng tới (chưa có key trong registry) bị bỏ sót hoàn
    # toàn, khiến "còn 19/30 đoạn chưa xử lý" hiện ra thành n_pending=0,
    # kích hoạt cảnh báo giả "hết nguồn nội dung" (xác nhận thật khi test
    # trực tiếp: 11 đoạn uploaded, tưởng hết nguồn dù còn 19 đoạn khả dụng).
    # Sửa: lấy TỔNG số đoạn khả dụng thật từ discover_segments() (đọc file
    # nguồn *_Short.txt, không phụ thuộc registry), trừ đi uploaded/failed.
    total_segments = len(discover_segments(SOURCE_EPISODES, TOPIC))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else {}
    n_uploaded = sum(1 for v in registry.values() if v.get("status") == "uploaded")
    n_failed = sum(1 for v in registry.values() if v.get("status") == "failed")
    n_pending = max(total_segments - n_uploaded - n_failed, 0)
    failed_keys = [k for k, v in registry.items() if v.get("status") == "failed"]
    return {"n_uploaded": n_uploaded, "n_failed": n_failed, "n_pending": n_pending, "total_segments": total_segments, "failed_keys": failed_keys, "registry": registry}


def check_recent_runs_for_stall() -> tuple[bool, str]:
    """True nếu 2 lần chạy gần nhất liên tiếp đều 0 đoạn xong -- dấu hiệu
    sản xuất bị chặn đứng (quota cạn dài ngày, hoặc lỗi hệ thống)."""
    runs = load_jsonl(DAILY_LOG_PATH)
    if len(runs) < CONSECUTIVE_ZERO_DONE_ALERT_THRESHOLD:
        return False, ""
    recent = runs[-CONSECUTIVE_ZERO_DONE_ALERT_THRESHOLD:]
    if all(r.get("n_done", 0) == 0 for r in recent):
        return True, f"{len(recent)} lần chạy liên tiếp gần nhất đều 0 đoạn hoàn thành."
    return False, ""


def check_missing_or_stale_run() -> tuple[bool, str]:
    """True nếu KHÔNG có dòng log mới nào trong khoảng thời gian đáng lẽ phải
    có -- phát hiện cả trường hợp job không chạy được GÌ CẢ (vd lỗi launchd
    exit 126 xảy ra ở tầng hệ điều hành, trước khi script kịp ghi bất kỳ log
    ứng dụng nào). Khác với check_recent_runs_for_stall(), vốn chỉ đọc NỘI
    DUNG của các dòng log đã có sẵn -- nếu log rỗng hoàn toàn, hàm đó trả về
    False (im lặng) thay vì báo động, đúng lỗ hổng thật đã xảy ra."""
    now = datetime.now(timezone.utc)
    runs = load_jsonl(DAILY_LOG_PATH)
    if runs:
        last_run_at_raw = runs[-1].get("run_at")
        try:
            last_run_at = datetime.fromisoformat(str(last_run_at_raw).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return True, f"Dòng log cuối có run_at không hợp lệ: {last_run_at_raw!r}."
        age_hours = (now - last_run_at).total_seconds() / 3600
        if age_hours > STALE_LOG_ALERT_HOURS:
            return True, f"Log gần nhất cách đây {age_hours:.1f}h (>{STALE_LOG_ALERT_HOURS}h) -- job có thể đã không chạy được ít nhất 1 lần theo lịch."
        return False, ""

    # Chưa từng có dòng log nào -- chỉ báo động nếu plist đã tồn tại đủ lâu để
    # lẽ ra đã phải có ít nhất 1 lần chạy (tránh báo giả ngay sau khi mới cài).
    if not LAUNCHD_PLIST_PATH.exists():
        return False, ""
    plist_age_hours = (now - datetime.fromtimestamp(LAUNCHD_PLIST_PATH.stat().st_mtime, tz=timezone.utc)).total_seconds() / 3600
    if plist_age_hours > STALE_LOG_ALERT_HOURS:
        return True, (f"plist đã tồn tại {plist_age_hours:.1f}h nhưng CHƯA TỪNG có dòng log nào trong "
                       f"{DAILY_LOG_PATH.name} -- job launchd nhiều khả năng chưa từng chạy thành công lần nào.")
    return False, ""


def analyze_slot_performance(registry: dict) -> dict | None:
    now = datetime.now(timezone.utc)
    published = [
        v for v in registry.values()
        if v.get("status") == "uploaded" and v.get("publish_at")
        and datetime.fromisoformat(v["publish_at"].replace("Z", "+00:00")) < now
    ]
    if len(published) < 3:
        return None  # quá ít để phân tích, không gọi agy/codex tốn công vô ích

    video_ids = [v["video_id"] for v in published if v.get("video_id")]
    try:
        details = get_videos_details(str(CREDENTIALS_PATH), video_ids)
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Không lấy được video details: {exc}"}

    views_by_id = {d["id"]: d["view_count"] for d in details}
    slot_lines = []
    for v in published:
        views = views_by_id.get(v.get("video_id"), 0)
        slot_lines.append(f"{v.get('publish_at')} | slot={v.get('slot_label', '?')} | views={views} | {v.get('seo', {}).get('title', '?')}")
    slot_data = "\n".join(slot_lines)

    try:
        finding = _extract_json(_run_agy(_ANALYSIS_PROMPT.format(slot_data=slot_data)))
        critique = _extract_json(_run_codex(_CRITIQUE_PROMPT.format(slot_data=slot_data, finding=finding.get("finding", ""))))
    except ContentSeoError as exc:
        return {"error": f"agy/codex lỗi: {exc}"}

    return {"n_samples": len(published), "finding": finding.get("finding"),
            "sample_size_adequate": finding.get("sample_size_adequate"),
            "critique_verdict": critique.get("verdict"), "critique_feedback": critique.get("feedback")}


def main() -> int:
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    reg_health = check_registry_health()
    stalled, stall_reason = check_recent_runs_for_stall()
    missing_run, missing_run_reason = check_missing_or_stale_run()
    performance = analyze_slot_performance(reg_health.get("registry", {}))

    entry = {
        "checked_at": checked_at,
        "n_uploaded": reg_health["n_uploaded"], "n_failed": reg_health["n_failed"], "n_pending": reg_health["n_pending"],
        "failed_keys": reg_health["failed_keys"], "production_stalled": stalled, "stall_reason": stall_reason,
        "run_missing_or_stale": missing_run, "run_missing_or_stale_reason": missing_run_reason,
        "performance": performance,
    }
    HEALTH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HEALTH_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if missing_run:
        _notify_macos("Short batch: job không ghi log đúng hạn", missing_run_reason)
    if stalled:
        _notify_macos("Short batch: sản xuất bị chặn đứng", stall_reason)
    if reg_health["n_failed"] > 0:
        _notify_macos("Short batch: có đoạn lỗi", f"{reg_health['n_failed']} đoạn ở trạng thái failed: {', '.join(reg_health['failed_keys'])}")
    if reg_health["n_pending"] == 0 and reg_health["n_uploaded"] > 0:
        _notify_macos("Short batch: hết nguồn nội dung", f"Đã upload {reg_health['n_uploaded']}, không còn đoạn nào pending -- cần bổ sung tập mới.")

    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
