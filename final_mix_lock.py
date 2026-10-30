"""Khoá độc quyền toàn máy cho bước ghép cuối video dài (nối chương + trộn tiếng cả video + mux).

VÌ SAO: benchmark L_fs_tv05 trên Oracle (30/10/2026) — render chương dùng ~3,6 GB RAM nhưng
bước ghép cuối đẩy lên ~11 GB trong ~1 phút (nạp WAV cả video + nhạc + lớp tiếng động vào RAM).
Hai job ghép cùng lúc ≈ 22 GB trên máy 24 GB → nguy cơ OOM giết luôn render khác.

Cách khoá: `fcntl.flock(LOCK_EX)` trên MỘT file cố định, đường dẫn tuyệt đối không phụ thuộc
thư mục làm việc. Không dùng thẳng `registry_lock.FileLock` vì lớp đó chờ vô hạn, mở file bằng
"w" (xoá nội dung khi đang chờ) và đặt tên khoá theo file đích; ở đây cần chờ có hạn + ghi
metadata người giữ. Cùng ngữ nghĩa flock: kernel tự nhả khi tiến trình chết, không có khoá treo.

Biến môi trường:
    VIENEU_LOCK_DIR                   thư mục khoá (mặc định ~/.vieneu/locks), luôn đổi ra tuyệt đối.
    VIENEU_FINAL_MIX_LOCK_TIMEOUT_S   chờ tối đa (giây, mặc định 7200 = 2 giờ).
    VIENEU_FINAL_MIX_RAM_GATE=1       BẬT cổng RAM (mặc định TẮT): sau khi có khoá, chờ tới khi
                                      RAM trống >= VIENEU_FINAL_MIX_MIN_FREE_GB (mặc định 12).

Metadata (video, pid, máy, giờ lấy khoá) ghi vào chính file khoá SAU khi lấy được, chỉ để quan
sát; không thay flock. Không xoá file khoá khi nhả.
"""
from __future__ import annotations

import fcntl
import json
import os
import socket
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

LOCK_NAME = "final_mix.lock"
DEFAULT_TIMEOUT_S = 7200.0
POLL_S = 2.0
LOG_EVERY_S = 60.0


class FinalMixLockTimeout(RuntimeError):
    """Chờ khoá ghép cuối quá hạn; chưa ghi gì ra file đầu ra."""


def lock_path() -> Path:
    base = os.environ.get("VIENEU_LOCK_DIR") or str(Path.home() / ".vieneu" / "locks")
    return (Path(base).expanduser() / LOCK_NAME).resolve()


def _timeout_s() -> float:
    try:
        v = float(os.environ.get("VIENEU_FINAL_MIX_LOCK_TIMEOUT_S", "") or DEFAULT_TIMEOUT_S)
    except ValueError:
        return DEFAULT_TIMEOUT_S
    return v if v >= 0 else DEFAULT_TIMEOUT_S


def available_gb() -> float | None:
    """RAM còn dùng được (GB); None nếu không đo được. Không thêm dependency bắt buộc."""
    try:
        import psutil  # noqa: PLC0415
        return psutil.virtual_memory().available / 2**30
    except Exception:  # noqa: BLE001
        pass
    try:
        for ln in Path("/proc/meminfo").read_text().splitlines():
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) / 2**20
    except OSError:
        pass
    return None


def fmt_gb(v: float | None) -> str:
    return "?" if v is None else f"{v:.1f} GB"


def log(msg: str) -> None:
    print(f"[final_mix_lock] {msg}", file=sys.stderr, flush=True)


def _read_holder(fh) -> str:
    try:
        fh.seek(0)
        return fh.read().strip() or "không rõ"
    except OSError:
        return "không rõ"


def _ram_gate(video_id: str) -> None:
    if os.environ.get("VIENEU_FINAL_MIX_RAM_GATE") != "1":
        return
    need = float(os.environ.get("VIENEU_FINAL_MIX_MIN_FREE_GB", "12") or 12)
    deadline = time.monotonic() + _timeout_s()
    last = 0.0
    while True:
        free = available_gb()
        if free is None or free >= need:
            return
        now = time.monotonic()
        if now >= deadline:
            raise FinalMixLockTimeout(
                f"{video_id}: RAM trống {fmt_gb(free)} < {need:.0f} GB quá {_timeout_s():.0f} s -- chưa ghép, đầu ra cũ giữ nguyên")
        if now - last >= LOG_EVERY_S:
            log(f"{video_id}: chờ RAM trống >= {need:.0f} GB (đang {fmt_gb(free)})")
            last = now
        time.sleep(POLL_S)


@contextmanager
def final_mix_lock(video_id: str, timeout_s: float | None = None):
    """Giữ khoá ghép cuối trong khối `with`. Hết hạn -> FinalMixLockTimeout, chưa đụng đầu ra."""
    path = lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    limit = _timeout_s() if timeout_s is None else timeout_s
    log(f"{video_id}: khoá {path} | RAM trống trước khi chờ {fmt_gb(available_gb())}")
    fh = open(path, "a+", encoding="utf-8")   # a+: KHÔNG xoá metadata của người đang giữ
    try:
        start = time.monotonic()
        last = start
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                now = time.monotonic()
                if now - start >= limit:
                    raise FinalMixLockTimeout(
                        f"{video_id}: chờ khoá ghép cuối {path} quá {limit:.0f} s; đang giữ bởi: {_read_holder(fh)} "
                        "-- chưa ghép, đầu ra cũ giữ nguyên") from None
                if now - last >= LOG_EVERY_S:
                    log(f"{video_id}: đang chờ khoá ({now - start:.0f} s), giữ bởi: {_read_holder(fh)}")
                    last = now
                time.sleep(min(POLL_S, max(0.05, limit - (now - start))))
        meta = {"video_id": video_id, "pid": os.getpid(), "host": socket.gethostname(),
                "acquired_at": datetime.now().astimezone().isoformat(timespec="seconds")}
        fh.seek(0)
        fh.truncate()
        fh.write(json.dumps(meta, ensure_ascii=False))
        fh.flush()
        log(f"{video_id}: đã giữ khoá sau {time.monotonic() - start:.0f} s | RAM trống {fmt_gb(available_gb())}")
        try:
            _ram_gate(video_id)
            yield path
        finally:
            log(f"{video_id}: nhả khoá | RAM trống {fmt_gb(available_gb())}")
            fcntl.flock(fh, fcntl.LOCK_UN)
    finally:
        fh.close()
