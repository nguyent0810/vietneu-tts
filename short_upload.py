"""Upload 1 Short lên YouTube -- lớp mỏng quanh youtube_upload.py, chỉ
khác Long ở chỗ category mặc định và không cần thêm playlist "Giải Mã
Kinh Địa Tạng" (Short không thuộc series đó theo cùng cách Long thuộc).

QUAN TRỌNG: bất kỳ script nào gọi module này (hoặc youtube_upload.py trực
tiếp) đều cần set biến môi trường SSL_CERT_FILE trỏ tới bundle cert của
certifi trước khi chạy, nếu không sẽ dính SSLCertVerificationError -- xem
ghi chú trong batch runner.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_upload import VideoMetadata, upload_video  # noqa: E402


def upload_short(video_path: str, title: str, description: str, tags: list[str],
                  publish_at: str, credentials_path: str) -> str:
    """Trả về video_id. category_id=22 (People & Blogs) giống Long -- nhất
    quán với cách kênh đã phân loại nội dung trước đây."""
    metadata = VideoMetadata(
        title=title, description=description, tags=tags,
        category_id="22", privacy_status="private", publish_at=publish_at,
    )
    result = upload_video(video_path, metadata, credentials_path)
    return result["id"]
