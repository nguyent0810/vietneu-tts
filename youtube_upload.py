"""
Upload video lên YouTube (resumable upload, YouTube Data API v3) -- viết
mới hoàn toàn bằng urllib, headless 100% miễn đã bootstrap credentials 1
lần (xem youtube_auth.py để biết lý do không tái dùng được code Electron
của app YTM, và thuật toán gốc đã tham khảo).

Hỗ trợ:
  - upload_video()  : 1 video, chunk resumable (8MB/chunk), tự retry với
                       backoff, tự refresh access_token nếu hết hạn giữa
                       chừng (video dài có thể mất vài phút để upload).
  - bulk_upload()    : nhiều video upload tuần tự, DỪNG NGAY toàn bộ hàng
                       đợi nếu gặp quota cạn -- các job còn lại chắc chắn
                       cũng sẽ fail cùng lý do, cố thử tiếp chỉ phí thời
                       gian/bandwidth vô ích.
  - Lên lịch (schedule): truyền publish_at (ISO8601 UTC) vào VideoMetadata
                       -- YouTube tự publish đúng giờ (video ở trạng thái
                       private cho tới lúc đó, đây là ràng buộc bắt buộc
                       của chính API, không phải lựa chọn thiết kế ở đây).
  - update_video()   : sửa lại metadata/lịch đăng của video ĐÃ upload (vd
                       đổi giờ, thêm hashtag vào mô tả) -- YouTube coi
                       videos.update là THAY THẾ NGUYÊN part chứ không
                       phải patch từng field, nên hàm này tự fetch bản hiện
                       tại rồi merge trước khi gửi lại, tránh vô tình xoá
                       field không định đổi.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from youtube_auth import YouTubeAuthError, get_valid_access_token

UPLOAD_INIT_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
THUMBNAIL_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"

CHUNK_SIZE = 8 * 1024 * 1024  # 8MB -- khớp chunk size app YTM đã dùng ổn định
MAX_RETRIES_PER_CHUNK = 5
RETRY_BACKOFF_BASE_S = 2.0
SCHEDULE_MIN_LEAD = timedelta(minutes=15)  # ràng buộc cứng của YouTube
SCHEDULE_MAX_LEAD = timedelta(days=180)


class YouTubeUploadError(RuntimeError):
    pass


class QuotaExceededError(YouTubeUploadError):
    pass


class UploadPacingHold(QuotaExceededError):
    """Kênh đã đủ trần upload 24 giờ: caller dừng hàng đợi như hết quota, chạy lại sau."""


class UploadInDoubt(YouTubeUploadError):
    """Phiên upload cũ hết hạn mà không biết video đã tạo chưa: người kiểm kênh rồi `--forget`."""


# Sổ upload + trần 24 giờ (05/10/2026, ý từ Channel module của Youtube_Creator_V2). CHỈ kênh Phật giáo/Phong Thuỷ;
# credential khác (CL) đi đường cũ, không đổi hành vi.
#  - giữ chỗ bằng dòng "started" kèm session URI TRƯỚC byte đầu tiên; đứt giữa chừng thì lần sau HỎI LẠI phiên
#    (200/201 = video đã tạo xong, nhận id; 308 = upload tiếp từ offset) thay vì upload lại thành video thứ hai.
#  - đếm theo GIỜ UPLOAD (không phải giờ lên sóng): đăng dồn video riêng tư hẹn giờ cũng bị coi là dồn.
UPLOAD_LOG = Path(__file__).resolve().parent / "output" / "upload_log.json"
GUARDED = {"phat_giao.json": 24, "phong_thuy.json": 24}


def _guard_key(credentials_path) -> str | None:
    name = Path(str(credentials_path)).name
    return name if name in GUARDED else None


def _log_load() -> dict:
    return json.loads(UPLOAD_LOG.read_text(encoding="utf-8")) if UPLOAD_LOG.exists() else {}


def _log_save(log: dict) -> None:
    UPLOAD_LOG.parent.mkdir(parents=True, exist_ok=True)
    tmp = UPLOAD_LOG.with_suffix(".tmp")
    tmp.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(UPLOAD_LOG)


def _entry_id(key: str, video_path: Path, size: int) -> str:
    return f"{key}|{video_path.resolve()}|{size}"


def pacing_hold_until(key: str, log: dict, now: datetime | None = None) -> datetime | None:
    """Mốc được upload tiếp nếu kênh đã đủ trần trong 24 giờ qua, không thì None."""
    now = now or datetime.now(timezone.utc)
    ts = sorted(datetime.fromisoformat(e["ts"]) for e in log.values()
                if e["key"] == key and now - datetime.fromisoformat(e["ts"]) < timedelta(hours=24))
    return ts[-GUARDED[key]] + timedelta(hours=24) if len(ts) >= GUARDED[key] else None


def _query_session(upload_url: str, total_size: int) -> tuple[str, object]:
    """Hỏi phiên resumable cũ: ("done", resource) | ("resume", offset) | ("dead", code)."""
    req = urllib.request.Request(upload_url, data=b"", method="PUT",
                                 headers={"Content-Length": "0", "Content-Range": f"bytes */{total_size}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return "done", json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 308:
            rng = exc.headers.get("Range")
            return "resume", int(rng.split("-")[1]) + 1 if rng else 0
        if exc.code in (404, 410):
            return "dead", exc.code
        raise YouTubeUploadError(f"Hỏi lại phiên upload lỗi ({exc.code}): {_parse_error_body(exc)} -- chạy lại sau")


@dataclass
class VideoMetadata:
    title: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    category_id: str = "22"  # People & Blogs -- mặc định hợp lý cho nội dung giáo lý/nói chuyện
    privacy_status: str = "private"
    publish_at: str | None = None  # ISO8601 UTC, vd "2026-07-25T09:00:00Z"

    def validate_schedule(self) -> None:
        if not self.publish_at:
            return
        publish_dt = datetime.fromisoformat(self.publish_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if publish_dt - now < SCHEDULE_MIN_LEAD:
            raise YouTubeUploadError(f"publish_at phải cách hiện tại ít nhất {SCHEDULE_MIN_LEAD} (ràng buộc của YouTube).")
        if publish_dt - now > SCHEDULE_MAX_LEAD:
            raise YouTubeUploadError(f"publish_at không được quá {SCHEDULE_MAX_LEAD.days} ngày trong tương lai (ràng buộc của YouTube).")

    def to_api_body(self) -> dict:
        self.validate_schedule()
        status = {"privacyStatus": self.privacy_status, "selfDeclaredMadeForKids": False}
        if self.publish_at:
            # Bắt buộc theo API: có publishAt thì privacyStatus phải là private,
            # YouTube tự chuyển sang public đúng giờ -- không phải mình tự canh gọi lại.
            status["privacyStatus"] = "private"
            status["publishAt"] = self.publish_at
        return {
            "snippet": {"title": self.title, "description": self.description, "tags": self.tags, "categoryId": self.category_id},
            "status": status,
        }


@dataclass
class UploadJob:
    video_path: str
    metadata: VideoMetadata
    thumbnail_path: str | None = None
    label: str = ""  # để log/nhận diện trong kết quả bulk, mặc định dùng tên file


def _refresh_or_raise(credentials_path) -> str:
    try:
        return get_valid_access_token(credentials_path)
    except YouTubeAuthError as exc:
        raise YouTubeUploadError(str(exc))


def _parse_error_body(exc: urllib.error.HTTPError) -> dict:
    try:
        return json.loads(exc.read())
    except Exception:
        return {}


def _is_quota_exceeded(error_body: dict) -> bool:
    for err in error_body.get("error", {}).get("errors", []):
        if err.get("reason") in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"):
            return True
    return False


def upload_video(
    video_path: str | Path,
    metadata: VideoMetadata,
    credentials_path: str | Path,
    thumbnail_path: str | Path | None = None,
    chunk_size: int = CHUNK_SIZE,
) -> dict:
    """Upload 1 video, trả về video resource JSON của YouTube (có "id" --
    xem tại youtube.com/watch?v=<id>). Raise QuotaExceededError RIÊNG
    (khác YouTubeUploadError chung) để bulk_upload() biết dừng hẳn hàng
    đợi thay vì thử tiếp các job chắc chắn cũng fail."""
    video_path = Path(video_path)
    if not video_path.exists():
        raise YouTubeUploadError(f"Không tìm thấy video: {video_path}")
    total_size = video_path.stat().st_size

    access_token = _refresh_or_raise(credentials_path)
    key = _guard_key(credentials_path)
    if key is None:
        upload_url = _init_resumable_session(video_path, metadata, access_token, total_size, credentials_path)
        result = _upload_chunks(video_path, upload_url, total_size, access_token, credentials_path, chunk_size)
    else:
        result = _guarded_upload(key, video_path, metadata, access_token, total_size, credentials_path, chunk_size)

    if thumbnail_path:
        upload_thumbnail(result["id"], thumbnail_path, credentials_path)
    return result


def _guarded_upload(key: str, video_path: Path, metadata: VideoMetadata, access_token: str, total_size: int,
                    credentials_path, chunk_size: int) -> dict:
    log = _log_load()
    eid = _entry_id(key, video_path, total_size)
    ent = log.get(eid)
    if ent and ent["state"] == "done":
        raise YouTubeUploadError(f"File này đã upload thành video {ent['video_id']} ({ent['ts'][:16]}) -- không upload lần hai. "
                                 f"Cố ý upload lại: python youtube_upload.py --forget \"{video_path}\"")
    offset = 0
    if ent and ent.get("session"):
        state, val = _query_session(ent["session"], total_size)
        if state == "done":
            ent.update(state="done", video_id=val["id"])
            _log_save(log)
            return val
        if state == "dead":
            raise UploadInDoubt(f"Phiên upload cũ của {video_path.name} đã hết hạn ({val}); có thể video đã lên kênh. "
                                f"Kiểm tra kênh, nếu chưa có: python youtube_upload.py --forget \"{video_path}\"")
        upload_url, offset = ent["session"], val
    else:
        until = pacing_hold_until(key, log)
        if until:
            raise UploadPacingHold(f"{key}: đã {GUARDED[key]} upload trong 24 giờ -- upload tiếp sau {until:%Y-%m-%d %H:%M}Z")
        upload_url = _init_resumable_session(video_path, metadata, access_token, total_size, credentials_path)
        log[eid] = ent = {"key": key, "ts": datetime.now(timezone.utc).isoformat(), "title": metadata.title,
                          "state": "started", "session": upload_url}
        _log_save(log)   # giữ chỗ + session TRƯỚC byte đầu tiên
    result = _upload_chunks(video_path, upload_url, total_size, access_token, credentials_path, chunk_size, offset)
    log = _log_load()
    log[eid] = {**ent, "state": "done", "video_id": result["id"]}
    _log_save(log)
    return result


def forget(video_path: str | Path) -> int:
    log = _log_load()
    p = str(Path(video_path).resolve())
    drop = [k for k in log if k.split("|")[1] == p]
    for k in drop:
        del log[k]
    _log_save(log)
    return len(drop)


def _init_resumable_session(video_path: Path, metadata: VideoMetadata, access_token: str, total_size: int, credentials_path) -> str:
    body = json.dumps(metadata.to_api_body()).encode("utf-8")
    req = urllib.request.Request(
        f"{UPLOAD_INIT_URL}?part=snippet,status&uploadType=resumable", data=body, method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/*",
            "X-Upload-Content-Length": str(total_size),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            location = resp.headers.get("Location")
    except urllib.error.HTTPError as exc:
        error_body = _parse_error_body(exc)
        if _is_quota_exceeded(error_body):
            raise QuotaExceededError(f"Hết quota YouTube API: {error_body}")
        if exc.code == 401:
            fresh_token = _refresh_or_raise(credentials_path)
            return _init_resumable_session(video_path, metadata, fresh_token, total_size, credentials_path)
        raise YouTubeUploadError(f"Khởi tạo upload session lỗi ({exc.code}): {error_body}")
    if not location:
        raise YouTubeUploadError("Google không trả Location header cho upload session.")
    return location


def _upload_chunks(video_path: Path, upload_url: str, total_size: int, access_token: str, credentials_path, chunk_size: int,
                   offset: int = 0) -> dict:
    with open(video_path, "rb") as f:
        while offset < total_size:
            end = min(offset + chunk_size, total_size) - 1
            f.seek(offset)
            chunk = f.read(end - offset + 1)

            for attempt in range(MAX_RETRIES_PER_CHUNK):
                req = urllib.request.Request(
                    upload_url, data=chunk, method="PUT",
                    headers={
                        "Content-Length": str(len(chunk)),
                        "Content-Range": f"bytes {offset}-{end}/{total_size}",
                        "Content-Type": "video/*",
                    },
                )
                try:
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        if resp.status in (200, 201):
                            return json.loads(resp.read())
                        offset = end + 1  # phòng hờ, thực tế nhánh 308 luôn rơi vào except bên dưới
                        break
                except urllib.error.HTTPError as exc:
                    if exc.code == 308:  # chunk được nhận, còn tiếp -- server báo lại offset đã có
                        range_header = exc.headers.get("Range")
                        offset = int(range_header.split("-")[1]) + 1 if range_header else end + 1
                        break
                    error_body = _parse_error_body(exc)
                    if _is_quota_exceeded(error_body):
                        raise QuotaExceededError(f"Hết quota YouTube API giữa chừng upload: {error_body}")
                    if exc.code == 401:
                        access_token = _refresh_or_raise(credentials_path)
                        continue  # thử lại đúng chunk này với token mới, không đổi offset
                    if exc.code >= 500 and attempt < MAX_RETRIES_PER_CHUNK - 1:
                        time.sleep(RETRY_BACKOFF_BASE_S * (attempt + 1))
                        continue
                    raise YouTubeUploadError(f"Upload chunk lỗi ({exc.code}) tại offset {offset}: {error_body}")
                except (urllib.error.URLError, OSError) as exc:
                    if attempt < MAX_RETRIES_PER_CHUNK - 1:
                        time.sleep(RETRY_BACKOFF_BASE_S * (attempt + 1))
                        continue
                    raise YouTubeUploadError(f"Lỗi mạng khi upload chunk tại offset {offset}: {exc}")
            else:
                raise YouTubeUploadError(f"Upload chunk tại offset {offset} thất bại sau {MAX_RETRIES_PER_CHUNK} lần thử.")

    raise YouTubeUploadError("Upload hết byte nhưng không nhận được video resource cuối cùng (bất thường).")


def upload_thumbnail(video_id: str, thumbnail_path: str | Path, credentials_path) -> None:
    thumbnail_path = Path(thumbnail_path)
    if not thumbnail_path.exists():
        raise YouTubeUploadError(f"Không tìm thấy thumbnail: {thumbnail_path}")
    data = thumbnail_path.read_bytes()
    if len(data) > 2 * 1024 * 1024:
        raise YouTubeUploadError(f"Thumbnail vượt giới hạn 2MB của YouTube ({len(data)} bytes).")
    access_token = _refresh_or_raise(credentials_path)
    content_type = "image/png" if thumbnail_path.suffix.lower() == ".png" else "image/jpeg"
    req = urllib.request.Request(
        f"{THUMBNAIL_URL}?videoId={video_id}", data=data, method="POST",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": content_type},
    )
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as exc:
        raise YouTubeUploadError(f"Set thumbnail lỗi ({exc.code}): {_parse_error_body(exc)}")


def _fetch_video_snippet_status(video_id: str, access_token: str) -> dict:
    req = urllib.request.Request(
        f"{VIDEOS_URL}?part=snippet,status&id={video_id}", headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise YouTubeUploadError(f"Không đọc được video {video_id} ({exc.code}): {_parse_error_body(exc)}")
    items = data.get("items", [])
    if not items:
        raise YouTubeUploadError(f"Không tìm thấy video {video_id}.")
    return items[0]


def update_video(
    video_id: str,
    credentials_path: str | Path,
    *,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    category_id: str | None = None,
    privacy_status: str | None = None,
    publish_at: str | None = None,
) -> dict:
    """Sửa metadata/lịch đăng của video ĐÃ upload. Chỉ field nào truyền vào
    (khác None) mới bị đổi -- các field còn lại giữ nguyên giá trị hiện có
    trên YouTube (tự fetch trước rồi merge, vì API yêu cầu gửi nguyên cả
    snippet/status khi update, không phải patch từng field)."""
    access_token = _refresh_or_raise(credentials_path)
    current = _fetch_video_snippet_status(video_id, access_token)
    snippet = current.get("snippet", {})
    status = current.get("status", {})

    if title is not None:
        snippet["title"] = title
    if description is not None:
        snippet["description"] = description
    if tags is not None:
        snippet["tags"] = tags
    if category_id is not None:
        snippet["categoryId"] = category_id
    if privacy_status is not None:
        status["privacyStatus"] = privacy_status
    if publish_at is not None:
        status["privacyStatus"] = "private"  # ràng buộc bắt buộc của API, giống lúc tạo mới
        status["publishAt"] = publish_at

    body = json.dumps({"id": video_id, "snippet": snippet, "status": status}).encode("utf-8")
    req = urllib.request.Request(
        f"{VIDEOS_URL}?part=snippet,status", data=body, method="PUT",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        error_body = _parse_error_body(exc)
        if _is_quota_exceeded(error_body):
            raise QuotaExceededError(f"Hết quota YouTube API: {error_body}")
        raise YouTubeUploadError(f"Cập nhật video lỗi ({exc.code}): {error_body}")


def delete_video(video_id: str, credentials_path: str | Path) -> None:
    """Xoá VĨNH VIỄN 1 video -- không có API undo. Chỉ dùng khi người dùng
    đã xác nhận rõ ràng (vd thay video đã upload sai file bằng bản đúng,
    YouTube không hỗ trợ thay file của 1 video đã tồn tại)."""
    access_token = _refresh_or_raise(credentials_path)
    req = urllib.request.Request(
        f"{VIDEOS_URL}?id={video_id}", method="DELETE", headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as exc:
        raise YouTubeUploadError(f"Xoá video lỗi ({exc.code}): {_parse_error_body(exc)}")


def bulk_upload(jobs: list[UploadJob], credentials_path: str | Path) -> list[dict]:
    """Upload TUẦN TỰ (YouTube không khuyến khích nhiều resumable session
    song song trên cùng 1 kênh -- dễ vướng rate limit). Dừng ngay hàng đợi
    khi gặp QuotaExceededError."""
    results = []
    for job in jobs:
        label = job.label or Path(job.video_path).name
        try:
            video = upload_video(job.video_path, job.metadata, credentials_path, thumbnail_path=job.thumbnail_path)
            results.append({"label": label, "ok": True, "video_id": video.get("id"), "url": f"https://youtu.be/{video.get('id')}"})
            print(f"OK: {label} -> https://youtu.be/{video.get('id')}", flush=True)
        except QuotaExceededError as exc:
            results.append({"label": label, "ok": False, "error": str(exc), "quota_exceeded": True})
            print(f"HẾT QUOTA -- dừng hàng đợi, còn {len(jobs) - len(results)} job chưa chạy: {exc}", file=sys.stderr)
            break
        except YouTubeUploadError as exc:
            results.append({"label": label, "ok": False, "error": str(exc)})
            print(f"LỖI ({label}): {exc}", file=sys.stderr)
    return results


def main() -> int:
    if sys.argv[1:2] == ["--forget"]:   # bỏ dòng sổ upload của một file (sau khi tự kiểm kênh)
        print(f"đã bỏ {forget(sys.argv[2])} dòng sổ upload của {sys.argv[2]}")
        return 0
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--credentials", required=True)
    ap.add_argument("--video")
    ap.add_argument("--title")
    ap.add_argument("--description", default="")
    ap.add_argument("--tags", default="", help="phân cách bằng dấu phẩy")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--publish-at", default=None, help="ISO8601 UTC, vd 2026-07-25T09:00:00Z")
    ap.add_argument("--thumbnail", default=None)
    ap.add_argument("--category-id", default="22")
    ap.add_argument("--jobs-json", default=None, help="Bulk mode: file JSON list các job (video_path/title/description/tags/...)")
    args = ap.parse_args()

    if args.jobs_json:
        raw_jobs = json.loads(Path(args.jobs_json).read_text(encoding="utf-8"))
        jobs = [
            UploadJob(
                video_path=j["video_path"],
                metadata=VideoMetadata(
                    title=j["title"], description=j.get("description", ""), tags=j.get("tags", []),
                    category_id=j.get("category_id", "22"), privacy_status=j.get("privacy_status", "private"),
                    publish_at=j.get("publish_at"),
                ),
                thumbnail_path=j.get("thumbnail_path"), label=j.get("label", ""),
            )
            for j in raw_jobs
        ]
        results = bulk_upload(jobs, args.credentials)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0 if all(r["ok"] for r in results) else 1

    if not args.video or not args.title:
        print("LỖI: cần --video + --title (hoặc dùng --jobs-json cho bulk mode).", file=sys.stderr)
        return 1

    metadata = VideoMetadata(
        title=args.title, description=args.description,
        tags=[t.strip() for t in args.tags.split(",") if t.strip()],
        category_id=args.category_id, privacy_status=args.privacy, publish_at=args.publish_at,
    )
    try:
        video = upload_video(args.video, metadata, args.credentials, thumbnail_path=args.thumbnail)
    except YouTubeUploadError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1
    print(f"OK: https://youtu.be/{video.get('id')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
