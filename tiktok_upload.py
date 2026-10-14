"""
Đăng video lên TikTok qua Content Posting API (Direct Post, FILE_UPLOAD) --
dùng chung credentials với tiktok_auth.py. Viết mới hoàn toàn, gọi thẳng
REST API TikTok bằng urllib (không phụ thuộc SDK ngoài), theo đúng tài
liệu chính thức developers.tiktok.com (đã tra cứu trực tiếp, không suy
đoán field name).

QUAN TRỌNG -- rào chắn an toàn tự nhiên của chính TikTok, không phải code
tự đặt ra: app CHƯA qua audit (sandbox/unaudited) bị TikTok tự động giới
hạn MỌI bài đăng ở privacy_level SELF_ONLY (chỉ chủ tài khoản xem được),
bất kể tham số --privacy truyền vào là gì -- module này LUÔN LUÔN đọc
privacy_level_options thật từ creator_info/query() trước khi đăng, không
bao giờ hard-code "PUBLIC_TO_EVERYONE" làm mặc định, và sẽ báo lỗi rõ ràng
nếu privacy_level yêu cầu không nằm trong danh sách TikTok thật sự cho
phép -- không cố "lách" giới hạn này.

Luồng (đúng theo tài liệu chính thức, 4 bước):
    1. query_creator_info() -- lấy privacy_level_options/username/avatar
       thật của tài khoản (bắt buộc hiển thị trước khi đăng theo UX
       guideline của TikTok).
    2. init_video_post() -- POST .../video/init/, trả về publish_id +
       upload_url (hiệu lực 1 giờ).
    3. upload_video_file() -- PUT toàn bộ file lên upload_url (1 chunk duy
       nhất cho video Short nhỏ, xem docstring hàm).
    4. wait_for_publish_status() -- poll .../status/fetch/ tới khi
       PUBLISH_COMPLETE hoặc FAILED.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from tiktok_auth import TikTokAuthError, get_valid_access_token

API_BASE = "https://open.tiktokapis.com/v2/post/publish"
CREATOR_INFO_URL = f"{API_BASE}/creator_info/query/"
INIT_URL = f"{API_BASE}/video/init/"
STATUS_URL = f"{API_BASE}/status/fetch/"

# TikTok giới hạn tần suất gọi creator_info/query (20/phút) và status/fetch
# (30/phút) theo access_token -- không liên quan tới việc đăng 1 video test
# đơn lẻ ở đây, nhưng ghi lại để không ai vô tình poll dồn dập nếu mở rộng
# sau này thành batch nhiều video.
STATUS_POLL_INTERVAL_S = 3
STATUS_POLL_TIMEOUT_S = 120


class TikTokUploadError(RuntimeError):
    pass


def _api_call(url: str, access_token: str, body: dict) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise TikTokUploadError(f"Gọi {url} thất bại (HTTP {exc.code}): {exc.read().decode('utf-8', 'replace')}")
    error = data.get("error", {})
    if error.get("code") not in (None, "ok"):
        raise TikTokUploadError(f"TikTok API trả lỗi tại {url}: {error!r}")
    return data.get("data", {})


def query_creator_info(credentials_path: str | Path) -> dict:
    """BẮT BUỘC gọi trước khi đăng -- trả về privacy_level_options THẬT
    (vd chỉ có "SELF_ONLY" nếu app chưa qua audit), username, avatar,
    max_video_post_duration_sec, và cờ bật/tắt duet/stitch/comment."""
    access_token = get_valid_access_token(credentials_path)
    return _api_call(CREATOR_INFO_URL, access_token, {})


def init_video_post(
    credentials_path: str | Path, video_path: str | Path, title: str,
    privacy_level: str, disable_comment: bool = False, disable_duet: bool = True,
    disable_stitch: bool = True, is_aigc: bool = True, video_cover_timestamp_ms: int | None = None,
) -> tuple[str, str]:
    """Trả về (publish_id, upload_url). is_aigc=True mặc định vì toàn bộ
    nội dung kênh này do TTS+pipeline tự động tạo -- TikTok yêu cầu gắn cờ
    trung thực cho nội dung AI-generated, KHÔNG được tắt cờ này để "trông
    tự nhiên hơn".

    video_cover_timestamp_ms: TikTok KHÔNG hỗ trợ upload ảnh cover riêng
    (đã tra cứu tài liệu chính thức developers.tiktok.com/doc/content-
    posting-api-reference-direct-post -- chỉ có đúng field này, chọn 1
    frame TỪ CHÍNH video làm cover). Nếu None, TikTok tự lấy frame ĐẦU
    TIÊN -- với video có beat typography/title-card ở đầu (đúng cấu trúc
    render_short.py hiện dùng), frame đầu thường ĐÃ là card chữ rõ ràng,
    nên mặc định này thường đã ổn; chỉ cần chỉnh tay nếu xem thử thấy cover
    xấu."""
    access_token = get_valid_access_token(credentials_path)

    creator_info = query_creator_info(credentials_path)
    allowed = creator_info.get("privacy_level_options", [])
    if privacy_level not in allowed:
        raise TikTokUploadError(
            f"privacy_level='{privacy_level}' KHÔNG nằm trong danh sách TikTok thực sự cho phép "
            f"cho tài khoản này: {allowed!r}. (Nếu app chưa qua audit, TikTok chỉ cho phép "
            f"'SELF_ONLY' -- đây là giới hạn phía TikTok, không phải lỗi code.)"
        )

    video_size = Path(video_path).stat().st_size
    post_info = {
        "title": title[:2200],  # TikTok giới hạn 2200 UTF-16 code unit
        "privacy_level": privacy_level,
        "disable_duet": disable_duet,
        "disable_stitch": disable_stitch,
        "disable_comment": disable_comment,
        "is_aigc": is_aigc,
    }
    if video_cover_timestamp_ms is not None:
        post_info["video_cover_timestamp_ms"] = video_cover_timestamp_ms
    body = {
        "post_info": post_info,
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,   # 1 chunk duy nhất -- đủ cho Short (<300s, thường vài MB)
            "total_chunk_count": 1,
        },
    }
    data = _api_call(INIT_URL, access_token, body)
    publish_id, upload_url = data.get("publish_id"), data.get("upload_url")
    if not publish_id or not upload_url:
        raise TikTokUploadError(f"init trả về thiếu publish_id/upload_url: {data!r}")
    return publish_id, upload_url


def upload_video_file(upload_url: str, video_path: str | Path) -> None:
    """PUT toàn bộ file trong 1 chunk -- upload_url chỉ sống 1 giờ kể từ
    lúc init(), phải gọi ngay sau init_video_post(), không được trì hoãn."""
    video_bytes = Path(video_path).read_bytes()
    req = urllib.request.Request(
        upload_url, data=video_bytes, method="PUT",
        headers={
            "Content-Type": "video/mp4",
            "Content-Length": str(len(video_bytes)),
            "Content-Range": f"bytes 0-{len(video_bytes) - 1}/{len(video_bytes)}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        raise TikTokUploadError(f"Upload file lên TikTok thất bại (HTTP {exc.code}): {exc.read().decode('utf-8', 'replace')}")


def wait_for_publish_status(credentials_path: str | Path, publish_id: str) -> dict:
    """Poll status/fetch tới khi PUBLISH_COMPLETE/FAILED hoặc hết
    STATUS_POLL_TIMEOUT_S -- KHÔNG coi timeout là thành công, trả về
    trạng thái cuối cùng thật sự nhận được, để caller tự quyết định."""
    access_token = get_valid_access_token(credentials_path)
    deadline = time.monotonic() + STATUS_POLL_TIMEOUT_S
    last_status = None
    while time.monotonic() < deadline:
        data = _api_call(STATUS_URL, access_token, {"publish_id": publish_id})
        last_status = data
        status = data.get("status")
        print(f"  trạng thái: {status}", file=sys.stderr, flush=True)
        if status in ("PUBLISH_COMPLETE", "FAILED", "SEND_TO_USER_INBOX"):
            return data
        time.sleep(STATUS_POLL_INTERVAL_S)
    return last_status or {}


def post_video(
    credentials_path: str | Path, video_path: str | Path, title: str,
    privacy_level: str | None = None, is_aigc: bool = True, video_cover_timestamp_ms: int | None = None,
) -> dict:
    """Luồng đầy đủ 1 video test: query creator info -> init -> upload ->
    poll status. Nếu privacy_level=None, TỰ ĐỘNG dùng lựa chọn RIÊNG TƯ
    NHẤT trong danh sách thật TikTok trả về (ưu tiên "SELF_ONLY" nếu có) --
    an toàn mặc định cho video TEST, không tự ý chọn công khai."""
    creator_info = query_creator_info(credentials_path)
    allowed = creator_info.get("privacy_level_options", [])
    if not allowed:
        raise TikTokUploadError(f"creator_info không trả privacy_level_options nào: {creator_info!r}")

    if privacy_level is None:
        privacy_level = "SELF_ONLY" if "SELF_ONLY" in allowed else allowed[0]
        print(f"privacy_level không truyền vào -- tự chọn an toàn nhất từ danh sách thật: '{privacy_level}' (danh sách đầy đủ: {allowed!r})", flush=True)

    print(f"Creator: {creator_info.get('creator_username')!r}, tùy chọn privacy_level thật: {allowed!r}", flush=True)

    publish_id, upload_url = init_video_post(
        credentials_path, video_path, title, privacy_level, is_aigc=is_aigc,
        video_cover_timestamp_ms=video_cover_timestamp_ms,
    )
    print(f"OK init: publish_id={publish_id}", flush=True)

    upload_video_file(upload_url, video_path)
    print("OK: đã upload xong file, đang chờ TikTok xử lý...", flush=True)

    final_status = wait_for_publish_status(credentials_path, publish_id)
    if final_status.get("status") != "PUBLISH_COMPLETE" and final_status.get("status") != "SEND_TO_USER_INBOX":
        print(
            f"CẢNH BÁO: chưa xác nhận PUBLISH_COMPLETE sau {STATUS_POLL_TIMEOUT_S}s "
            f"(trạng thái cuối: {final_status!r}) -- KHÔNG coi là thành công, cần tự kiểm tra lại thủ công.",
            file=sys.stderr,
        )
    return {"publish_id": publish_id, "privacy_level": privacy_level, "final_status": final_status}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--credentials", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--privacy-level", default=None, help='vd "SELF_ONLY" -- để trống thì tự chọn an toàn nhất')
    ap.add_argument("--cover-timestamp-ms", type=int, default=None, help="chọn frame làm cover -- để trống thì TikTok tự lấy frame đầu")
    args = ap.parse_args()

    try:
        result = post_video(
            args.credentials, args.video, args.title, privacy_level=args.privacy_level,
            video_cover_timestamp_ms=args.cover_timestamp_ms,
        )
    except (TikTokAuthError, TikTokUploadError) as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
