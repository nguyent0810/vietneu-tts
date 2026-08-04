"""Khoá file ngắn hạn dùng chung cho thao tác đọc-sửa-ghi registry.json
(short_batch_runner.py, long_batch_runner.py).

BUG THẬT (audit tự động hoá đa kênh, mục C): registry được load 1 lần vào bộ
nhớ rồi giữ NGUYÊN trong suốt cả quá trình xử lý (có thể mất nhiều phút/giờ,
qua nhiều bước TTS/render/SEO/upload) -- nếu 1 tiến trình KHÁC (cùng topic,
cùng loại nội dung) chạy song song và save trước, tiến trình sau vẫn giữ bản
ghi nhớ CŨ, save_registry() ghi đè TRẮNG cả file, XOÁ MẤT các entry mà tiến
trình kia vừa thêm/sửa cho các key KHÁC.

Sửa: mỗi lần save, giữ khoá NGẮN HẠN (chỉ quanh bước đọc-ghi JSON, KHÔNG giữ
suốt thời gian xử lý), đọc lại bản MỚI NHẤT trên đĩa, MERGE với bản trong bộ
nhớ (bộ nhớ thắng cho các key nó có -- phản ánh đúng thay đổi tiến trình này
vừa làm; các key CHỈ có trên đĩa, do tiến trình khác thêm, được GIỮ LẠI thay
vì bị xoá). Không giải quyết hoàn toàn trường hợp 2 tiến trình CÙNG lúc xử lý
CÙNG 1 key (xem ghi chú riêng ở nơi gọi save_registry lần đầu cho 1 mục) --
đó là rủi ro hẹp hơn, cần thêm bước "claim" riêng ở phía gọi."""
import fcntl
from pathlib import Path


class FileLock:
    def __init__(self, path: Path):
        self._lock_path = path.with_suffix(path.suffix + ".lock")
        self._fh = None

    def __enter__(self):
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._lock_path, "w")
        fcntl.flock(self._fh, fcntl.LOCK_EX)  # blocking -- giao dịch này luôn rất ngắn (đọc/ghi JSON registry)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self._fh, fcntl.LOCK_UN)
        self._fh.close()
