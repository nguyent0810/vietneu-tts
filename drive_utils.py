"""
Helper dùng chung cho mọi thao tác rclone trong pipeline — tập trung 1 nơi
thay vì lặp lại `rclone()` ở từng file, có retry-với-backoff cho lỗi mạng
thoáng qua (transient), vì khi có nhiều tool cùng gọi Drive (content tool,
tool này, tool video...) khả năng va lỗi mạng ngắn hạn sẽ cao hơn.
"""
import subprocess
import time

RETRY_ATTEMPTS = 3
RETRY_BACKOFF_S = 2.0


def rclone(*args: str, retries: int = RETRY_ATTEMPTS) -> subprocess.CompletedProcess:
    """Chạy 1 lệnh rclone, tự retry với backoff nếu lỗi (trừ khi lỗi rõ ràng
    là "không tồn tại" — rclone trả returncode 3 cho trường hợp đó, không
    đáng retry)."""
    last_result = None
    for attempt in range(retries):
        result = subprocess.run(["rclone", *args], capture_output=True, text=True)
        if result.returncode == 0:
            return result
        if result.returncode == 3:  # directory/file not found — retry vô ích
            return result
        last_result = result
        if attempt < retries - 1:
            time.sleep(RETRY_BACKOFF_S * (attempt + 1))
    return last_result


def list_pending_files(input_remote: str, suffix: str = ".txt") -> list[str]:
    """Liệt kê file ở tầng gốc của input_remote (không đệ quy, bỏ qua processed/)."""
    result = rclone("lsf", input_remote, "--files-only")
    if result.returncode != 0:
        return []
    names = [n.strip() for n in result.stdout.splitlines() if n.strip()]
    return [n for n in names if n.lower().endswith(suffix)]


def list_files_in(remote: str) -> set[str]:
    """Liệt kê tên file (không đệ quy) trong 1 remote path. Trả về set rỗng
    nếu thư mục chưa tồn tại."""
    result = rclone("lsf", remote, "--files-only")
    if result.returncode != 0:
        return set()
    return {n.strip() for n in result.stdout.splitlines() if n.strip()}


def list_dirs_in(remote: str) -> list[str]:
    result = rclone("lsf", remote, "--dirs-only")
    if result.returncode != 0:
        return []
    return sorted(n.strip().rstrip("/") for n in result.stdout.splitlines() if n.strip())
