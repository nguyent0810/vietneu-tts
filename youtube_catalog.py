"""
Đọc + ghi danh mục kênh (playlist/video đã đăng, kèm thống kê view/like/
comment) qua YouTube Data API v3 -- dùng chung credentials với
youtube_upload.py / youtube_analytics.py (xem youtube_auth.py). Dùng để
phân tích hiệu suất video cũ trước khi quyết định SEO/giờ đăng cho video
mới, và để thêm video mới upload vào đúng playlist tương ứng.
"""
import json
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from youtube_auth import YouTubeAuthError, get_valid_access_token

PLAYLISTS_URL = "https://www.googleapis.com/youtube/v3/playlists"
PLAYLIST_ITEMS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"

# Lỗi coi là tạm thời -- đáng retry (rate-limit/backend transient); các mã
# 4xx khác (400/401/403 permission, 404 not found...) KHÔNG retry vì gọi
# lại cũng sẽ lỗi y hệt, retry chỉ tổ tốn quota.
RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}
MAX_RETRIES = 5


class YouTubeCatalogError(RuntimeError):
    pass


class AmbiguousPlaylistError(YouTubeCatalogError):
    """>1 playlist khớp CHÍNH XÁC cùng tên -- không được tự ý chọn 1 cái
    khi đang GHI dữ liệu (phụ thuộc thứ tự trả về của API là không an
    toàn); caller phải tự giải quyết (đổi tên 1 trong 2, hoặc chỉ định
    playlist_id_hint trực tiếp)."""
    pass


def _sleep_backoff(attempt: int) -> None:
    time.sleep(min(30.0, (2 ** attempt) + random.uniform(0, 1)))


def _request_with_retry(build_request, description: str):
    """Gửi 1 urllib.request.Request (do build_request() dựng lại MỖI lần,
    vì access_token có thể cần refresh) với retry+backoff cho lỗi mạng
    tạm thời (URLError/timeout) và HTTP status trong RETRYABLE_HTTP_STATUS.
    KHÔNG retry lỗi 4xx khác (permission/not-found) -- trả lỗi ngay."""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            req = build_request()
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < MAX_RETRIES - 1:
                last_exc = YouTubeCatalogError(f"{description} lỗi tạm thời ({exc.code}), sẽ thử lại: {body}")
                _sleep_backoff(attempt)
                continue
            raise YouTubeCatalogError(f"{description} lỗi ({exc.code}): {body}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_exc = YouTubeCatalogError(f"{description} lỗi mạng tạm thời: {exc}")
            if attempt < MAX_RETRIES - 1:
                _sleep_backoff(attempt)
                continue
            raise last_exc
    raise last_exc


def _get(credentials_path, url: str, params: dict) -> dict:
    try:
        access_token = get_valid_access_token(credentials_path)
    except YouTubeAuthError as exc:
        raise YouTubeCatalogError(str(exc))

    def build():
        return urllib.request.Request(
            f"{url}?{urllib.parse.urlencode(params)}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return _request_with_retry(build, "YouTube Data API")


def _post(credentials_path, url: str, body: dict) -> dict:
    """1 lần gọi DUY NHẤT, KHÔNG tự động retry -- khác _get(). Lý do (Codex
    review #5 vòng 2): POST vào các endpoint GHI (playlists.insert,
    playlistItems.insert) không phải lúc nào cũng an toàn để blind-retry --
    nếu request đã xử lý XONG ở server nhưng client mất response vì
    timeout/URLError, retry mù sẽ tạo ra BẢN GHI TRÙNG (playlist trùng tên
    hoặc video bị thêm 2 lần vào playlist). Caller phải tự RECONCILE (tra
    lại trạng thái thật qua GET) trước khi quyết định retry -- xem
    _create_playlist_with_reconcile()/_add_video_with_reconcile() bên
    dưới, đây là các hàm DUY NHẤT được phép retry cho 2 thao tác ghi này."""
    try:
        access_token = get_valid_access_token(credentials_path)
    except YouTubeAuthError as exc:
        raise YouTubeCatalogError(str(exc))
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, method="POST",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise YouTubeCatalogError(f"YouTube Data API (ghi) lỗi ({exc.code}): {exc.read().decode('utf-8', 'replace')}")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise YouTubeCatalogError(f"YouTube Data API (ghi) lỗi mạng (không rõ server đã xử lý request hay chưa): {exc}")


def _put(credentials_path, url: str, body: dict) -> dict:
    """Giống _post() (1 lần gọi, không tự retry) nhưng dùng HTTP PUT --
    BUG THẬT phát hiện khi chạy publish-new (xem phiên làm việc):
    playlists.update PHẢI dùng PUT, YouTube API phân biệt insert/update
    theo METHOD HTTP chứ không phải theo nội dung body -- gọi bằng POST bị
    hiểu nhầm thành playlists.insert, trả lỗi 400 unexpectedPart khó hiểu
    (vì body thiếu snippet mà insert yêu cầu) thay vì lỗi rõ ràng."""
    try:
        access_token = get_valid_access_token(credentials_path)
    except YouTubeAuthError as exc:
        raise YouTubeCatalogError(str(exc))
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, method="PUT",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise YouTubeCatalogError(f"YouTube Data API (ghi) lỗi ({exc.code}): {exc.read().decode('utf-8', 'replace')}")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise YouTubeCatalogError(f"YouTube Data API (ghi) lỗi mạng (không rõ server đã xử lý request hay chưa): {exc}")


def get_own_channel_id(credentials_path) -> str:
    """Trả về channel_id THẬT của credentials đang dùng (gọi channels.list
    mine=true) -- dùng để xác nhận credentials khớp đúng kênh mong đợi
    TRƯỚC khi ghi (Codex flag: title playlist không đủ để tránh ghi nhầm
    kênh nếu truyền sai --credentials)."""
    data = _get(credentials_path, CHANNELS_URL, {"part": "id", "mine": "true"})
    items = data.get("items", [])
    if not items:
        raise YouTubeCatalogError("channels.list mine=true không trả về kênh nào -- credentials có thể sai/hết quyền.")
    return items[0]["id"]


def list_playlists(credentials_path) -> list[dict]:
    """Trả về [{id, title, item_count}] cho toàn bộ playlist của kênh đang xác thực."""
    playlists = []
    page_token = None
    while True:
        params = {"part": "snippet,contentDetails", "mine": "true", "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        data = _get(credentials_path, PLAYLISTS_URL, params)
        for item in data.get("items", []):
            playlists.append({
                "id": item["id"], "title": item["snippet"]["title"],
                "item_count": item.get("contentDetails", {}).get("itemCount", 0),
            })
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return playlists


def find_playlist_by_title(credentials_path, title_substring: str) -> dict | None:
    normalized = title_substring.strip().lower()
    for playlist in list_playlists(credentials_path):
        if normalized in playlist["title"].strip().lower():
            return playlist
    return None


def list_playlist_video_ids(credentials_path, playlist_id: str) -> list[str]:
    """Trả về videoId theo đúng thứ tự trong playlist (position tăng dần)."""
    video_ids = []
    page_token = None
    while True:
        params = {"part": "contentDetails", "playlistId": playlist_id, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        data = _get(credentials_path, PLAYLIST_ITEMS_URL, params)
        for item in data.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return video_ids


def _list_playlist_items(credentials_path, playlist_id: str) -> list[dict]:
    """Trả về [{playlist_item_id, video_id}] -- playlistItems.delete cần
    ID CỦA MỤC TRONG PLAYLIST (khác videoId), list_playlist_video_ids()
    không giữ lại giá trị này nên tách hàm riêng thay vì sửa hàm đó (tránh
    đổi kiểu trả về, có chỗ khác đang dùng list[str] thẳng)."""
    out = []
    page_token = None
    while True:
        params = {"part": "id,contentDetails", "playlistId": playlist_id, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        data = _get(credentials_path, PLAYLIST_ITEMS_URL, params)
        for item in data.get("items", []):
            out.append({"playlist_item_id": item["id"], "video_id": item["contentDetails"]["videoId"]})
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return out


def remove_video_from_playlist(credentials_path, playlist_id: str, video_id: str) -> bool:
    """Gỡ 1 video khỏi playlist (playlistItems.delete) -- KHÔNG xoá video,
    chỉ gỡ liên kết. Trả về False nếu video không có trong playlist (no-op,
    không phải lỗi -- gọi lại an toàn). Không tự động retry lỗi 404 (item
    đã bị gỡ từ trước, retry vô ích) nhưng CÓ retry lỗi tạm thời khác qua
    _request_with_retry."""
    items = _list_playlist_items(credentials_path, playlist_id)
    match = next((it for it in items if it["video_id"] == video_id), None)
    if match is None:
        return False
    # KHÔNG dùng _request_with_retry() ở đây -- nó luôn json.loads(resp.read()),
    # nhưng playlistItems.delete trả về 204 No Content (body rỗng), sẽ crash
    # JSONDecodeError nếu tái dùng thẳng. DELETE cũng không cần retry phức tạp
    # (idempotent theo bản chất -- gọi lại khi item đã bị gỡ chỉ trả 404, đã
    # được coi là "không phải lỗi" ở check match is None phía trên).
    for attempt in range(MAX_RETRIES):
        access_token = get_valid_access_token(credentials_path)
        req = urllib.request.Request(
            f"{PLAYLIST_ITEMS_URL}?id={match['playlist_item_id']}",
            method="DELETE", headers={"Authorization": f"Bearer {access_token}"},
        )
        try:
            urllib.request.urlopen(req, timeout=30)
            return True
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return False  # đã bị gỡ từ trước (race với tiến trình khác) -- không phải lỗi
            body = exc.read().decode("utf-8", "replace")
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < MAX_RETRIES - 1:
                _sleep_backoff(attempt)
                continue
            raise YouTubeCatalogError(f"playlistItems.delete lỗi ({exc.code}): {body}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt < MAX_RETRIES - 1:
                _sleep_backoff(attempt)
                continue
            raise YouTubeCatalogError(f"playlistItems.delete lỗi mạng tạm thời: {exc}")
    return False


def get_videos_details(credentials_path, video_ids: list[str]) -> list[dict]:
    """Trả về [{id, title, description, tags, published_at, view_count,
    like_count, comment_count, duration}] -- videos.list giới hạn 50
    id/lần gọi, tự chia batch nếu nhiều hơn."""
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        params = {"part": "snippet,statistics,contentDetails", "id": ",".join(batch)}
        data = _get(credentials_path, VIDEOS_URL, params)
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            results.append({
                "id": item["id"],
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "tags": snippet.get("tags", []),
                "published_at": snippet.get("publishedAt"),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "duration": item.get("contentDetails", {}).get("duration"),
            })
    return results


def create_playlist(credentials_path, title: str, description: str = "", privacy_status: str = "private") -> dict:
    """Tạo playlist mới (playlists.insert). Trả về {id, title, item_count=0}.
    KHÔNG tự kiểm tra trùng tên trước khi gọi -- caller (vd
    ensure_playlist_and_add) chịu trách nhiệm tra cứu trước để tránh tạo
    playlist trùng khi gọi lặp lại (API không tự chặn trùng tên).
    Mặc định "private" (Codex review #5: không tạo thẳng public -- staging
    trước, publish bằng update_playlist_privacy() riêng sau khi đã verify
    đủ thành viên)."""
    data = _post(credentials_path, f"{PLAYLISTS_URL}?part=snippet,status", {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": privacy_status},
    })
    return {"id": data["id"], "title": data["snippet"]["title"], "item_count": 0}


def update_playlist_privacy(credentials_path, playlist_id: str, privacy_status: str, title: str) -> dict:
    """Đổi privacyStatus của playlist đã có (playlists.update) -- dùng để
    publish (private -> public) SAU KHI đã verify đủ thành viên, tách biệt
    khỏi bước tạo/ghi (Codex review #5, mục Privacy).

    title: BẮT BUỘC truyền -- playlists.update yêu cầu part=snippet,status
    VÀ body phải có snippet.title (xác nhận qua tài liệu chính thức +
    test thật: part=status một mình hoặc thiếu snippet.title đều trả lỗi
    400 "unexpectedPart" dù message API không giải thích rõ lý do). Vẫn
    CHỈ đổi privacyStatus -- gửi lại title hiện tại không làm thay đổi
    tên playlist."""
    data = _put(credentials_path, f"{PLAYLISTS_URL}?part=snippet,status", {
        "id": playlist_id,
        "snippet": {"title": title},
        "status": {"privacyStatus": privacy_status},
    })
    return {"id": data["id"], "privacy_status": data.get("status", {}).get("privacyStatus")}


def _create_playlist_with_reconcile(credentials_path, title: str, description: str, privacy_status: str) -> dict:
    """Retry AN TOÀN cho playlists.insert: sau lỗi từ _post() (HTTP
    retryable hoặc lỗi mạng không rõ kết quả), KHÔNG gọi lại POST ngay --
    tra lại find_playlist_by_exact_title(title) trước:
    - 0 kết quả -> lần gọi trước THẬT SỰ chưa tạo được, an toàn để thử lại.
    - 1 kết quả -> lần gọi trước ĐÃ tạo thành công, chỉ mất response -- dùng
      thẳng playlist đó, không tạo thêm bản trùng.
    - >1 kết quả -> không rõ playlist nào do lần gọi trước tạo ra, abort
      (AmbiguousPlaylistError) thay vì đoán."""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            return create_playlist(credentials_path, title, description, privacy_status)
        except YouTubeCatalogError as exc:
            last_exc = exc
            if attempt == MAX_RETRIES - 1:
                raise
            _sleep_backoff(attempt)
            matches = find_playlist_by_exact_title(credentials_path, title)
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise AmbiguousPlaylistError(
                    f"Sau lỗi tạo playlist '{title}' ({exc}), tra lại thấy {len(matches)} playlist "
                    f"trùng tên -- không rõ playlist nào do lần gọi trước tạo ra, cần giải quyết thủ công."
                ) from exc
            continue
    raise last_exc


def _add_video_with_reconcile(credentials_path, playlist_id: str, video_id: str) -> None:
    """Retry AN TOÀN cho playlistItems.insert: sau lỗi từ _post(), tra lại
    list_playlist_video_ids(playlist_id) trước khi thử lại -- nếu video ĐÃ
    là thành viên (lần gọi trước thành công, chỉ mất response) thì coi là
    xong, không insert lần 2; nếu chưa, an toàn để thử lại."""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            add_video_to_playlist(credentials_path, playlist_id, video_id)
            return
        except YouTubeCatalogError as exc:
            last_exc = exc
            if attempt == MAX_RETRIES - 1:
                raise
            _sleep_backoff(attempt)
            member_ids = list_playlist_video_ids(credentials_path, playlist_id)
            if video_id in member_ids:
                return
            continue
    raise last_exc


def _list_playlist_video_ids_tolerant(credentials_path, playlist_id: str, expect_video_id: str | None = None,
                                       retries: int = 4, base_delay: float = 1.5) -> list[str]:
    """list_playlist_video_ids() chịu được READ-AFTER-WRITE LAG phía
    YouTube -- phát hiện THẬT khi chạy live batch 35 Short (xem phiên làm
    việc): playlist VỪA TẠO đôi khi trả 404 "playlistNotFound" nếu đọc lại
    NGAY LẬP TỨC (chưa lan truyền xong phía server, không phải lỗi
    playlistId sai), hoặc video VỪA insert chưa xuất hiện ngay trong danh
    sách dù bản thân playlist đã đọc được. Xác nhận qua fresh API call sau
    khi lỗi: cả 2 trường hợp video/playlist đều THẬT SỰ tồn tại đúng, chỉ
    là đọc quá sớm.

    CHỈ dùng ở 2 điểm đọc NGAY SAU khi CHÍNH TA vừa ghi trong
    ensure_playlist_and_add() -- KHÔNG dùng ở call site khác (vd
    pin_existing_playlist_ids) để không che giấu lỗi playlistId sai thật
    sự ở nơi khác (playlist không do batch này tạo ra).

    expect_video_id: nếu truyền, còn retry thêm nếu playlist đọc được
    nhưng video CHƯA xuất hiện trong danh sách (lag ở tầng
    playlistItems, khác lag ở tầng playlist)."""
    video_ids: list[str] = []
    for attempt in range(retries):
        try:
            video_ids = list_playlist_video_ids(credentials_path, playlist_id)
        except YouTubeCatalogError as exc:
            if "(404)" not in str(exc) or attempt == retries - 1:
                raise
            time.sleep(base_delay * (attempt + 1))
            continue
        if expect_video_id is None or expect_video_id in video_ids or attempt == retries - 1:
            return video_ids
        time.sleep(base_delay * (attempt + 1))
    return video_ids


def find_playlist_by_exact_title(credentials_path, title: str) -> list[dict]:
    """Khớp CHÍNH XÁC (đã strip, so sánh nguyên văn không phân biệt hoa/
    thường) -- khác find_playlist_by_title() (substring, có thể khớp NHẦM
    khi nhiều playlist tên chứa cùng 1 cụm con, vd kênh Phong Thuỷ có cả
    "Mệnh Thủy" (1 video) và "Khám Phá Tử Vi & Phong Thủy Mệnh Thủy" (14
    video) -- substring "mệnh thủy" khớp cả hai, không an toàn để tự động
    ghi). Trả về DANH SÁCH (có thể rỗng/1/nhiều) -- caller (vd
    ensure_playlist_and_add) chịu trách nhiệm abort nếu >1 kết quả (Codex
    review #5: không được tự chọn playlist đầu tiên khi tên trùng, phụ
    thuộc thứ tự trả về của API là không an toàn cho thao tác GHI)."""
    normalized = title.strip().lower()
    return [p for p in list_playlists(credentials_path) if p["title"].strip().lower() == normalized]


def ensure_playlist_and_add(credentials_path, playlist_title: str, video_id: str,
                             description: str = "", privacy_status: str = "private",
                             dry_run: bool = False, playlist_id_hint: str | None = None) -> dict:
    """Tìm playlist theo tên CHÍNH XÁC -- có thì dùng, không có thì tạo mới
    -- rồi thêm video vào (idempotent: kiểm tra video đã có trong playlist
    chưa trước khi insert, tránh thêm trùng khi gọi lại sau lỗi/resume).

    playlist_id_hint: nếu truyền (vd ID đã "pin" từ dry-run manifest cho
    playlist ĐÃ CÓ SẴN), bỏ qua tra cứu theo tên -- dùng thẳng ID này, vừa
    giảm số lệnh gọi list_playlists() (quota), vừa tránh drift nếu tên
    playlist bị đổi giữa lúc dry-run và lúc ghi thật. Chỉ nên dùng cho
    playlist đã xác nhận tồn tại; để None nếu playlist có thể cần tạo mới.

    Abort (AmbiguousPlaylistError) nếu tên khớp CHÍNH XÁC >1 playlist --
    không tự chọn playlist đầu tiên khi đang ghi dữ liệu thật.

    dry_run=True: KHÔNG gọi bất kỳ API ghi nào (create/insert), chỉ trả về
    kế hoạch sẽ làm -- dùng để duyệt trước khi ghi thật (Codex yêu cầu dry-
    run manifest trước khi backfill).

    Trả về plan với field `action` mô tả KẾT QUẢ THẬT (không phải dự định):
    "would_create"/"would_add"/"would_skip_existing_member" khi dry_run, hoặc
    "created_playlist_and_added"/"added_video"/"skipped_already_member" khi
    ghi thật (Codex review #5: field will_add_video cũ mô tả sai là "sẽ
    làm" thay vì "đã làm")."""
    if playlist_id_hint:
        existing_matches = [{"id": playlist_id_hint, "title": playlist_title}]
    else:
        existing_matches = find_playlist_by_exact_title(credentials_path, playlist_title)
        if len(existing_matches) > 1:
            raise AmbiguousPlaylistError(
                f"'{playlist_title}' khớp CHÍNH XÁC {len(existing_matches)} playlist "
                f"(ids={[p['id'] for p in existing_matches]}) -- không tự chọn, cần giải quyết thủ công "
                f"(đổi tên 1 playlist trùng, hoặc truyền playlist_id_hint)."
            )
    existing = existing_matches[0] if existing_matches else None

    plan = {
        "playlist_title": playlist_title,
        "playlist_id": existing["id"] if existing else None,
        "will_create_playlist": existing is None,
        "video_id": video_id,
        "already_in_playlist": False,
        "action": None,
    }
    if dry_run:
        if existing:
            member_ids = list_playlist_video_ids(credentials_path, existing["id"])
            plan["already_in_playlist"] = video_id in member_ids
            plan["action"] = "would_skip_existing_member" if plan["already_in_playlist"] else "would_add"
        else:
            plan["action"] = "would_create_and_add"
        return plan

    playlist = existing or _create_playlist_with_reconcile(credentials_path, playlist_title, description, privacy_status)
    plan["playlist_id"] = playlist["id"]
    plan["will_create_playlist"] = existing is None
    # Thực tế phát hiện khi chạy live thật (ledger 35 Short, xem phiên làm
    # việc): playlist VỪA TẠO đôi khi 404 "playlistNotFound" nếu đọc lại
    # NGAY LẬP TỨC (read-after-write lag phía YouTube, không phải lỗi
    # logic) -- dùng list retry chịu lag CHỈ ở 2 điểm đọc-ngay-sau-ghi này
    # (không áp cho list_playlist_video_ids() dùng nơi khác, để không che
    # giấu lỗi playlistId sai thật sự ở các call site khác).
    member_ids = _list_playlist_video_ids_tolerant(credentials_path, playlist["id"])
    if video_id in member_ids:
        plan["already_in_playlist"] = True
        plan["action"] = "skipped_already_member"
        return plan
    _add_video_with_reconcile(credentials_path, playlist["id"], video_id)
    # Verify sau ghi (Codex review #5: không tin kết quả HTTP 200 một
    # mình -- đọc lại thành viên thật để xác nhận, đặc biệt vì insert có
    # thể "thành công phía server nhưng client timeout trước khi nhận
    # response" ở lần gọi TRƯỚC, khiến resume hiểu nhầm trạng thái).
    verified_ids = _list_playlist_video_ids_tolerant(credentials_path, playlist["id"], expect_video_id=video_id)
    if video_id not in verified_ids:
        raise YouTubeCatalogError(
            f"Đã gọi playlistItems.insert cho video={video_id} playlist={playlist['id']} "
            f"nhưng verify lại KHÔNG thấy video trong playlist -- không xác nhận được ghi thành công."
        )
    plan["already_in_playlist"] = False
    plan["action"] = "created_playlist_and_added" if existing is None else "added_video"
    return plan


def add_video_to_playlist(credentials_path, playlist_id: str, video_id: str, position: int | None = None) -> dict:
    """Thêm 1 video vào playlist (playlistItems.insert). position=None ->
    YouTube tự thêm vào cuối playlist."""
    snippet = {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}
    if position is not None:
        snippet["position"] = position
    return _post(credentials_path, f"{PLAYLIST_ITEMS_URL}?part=snippet", {"snippet": snippet})


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--credentials", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)

    lp = sub.add_parser("list-playlists")
    fp = sub.add_parser("playlist-videos")
    fp.add_argument("--title", required=True, help="Khớp gần đúng theo tên playlist (không phân biệt hoa/thường)")

    args = ap.parse_args()
    try:
        if args.cmd == "list-playlists":
            print(json.dumps(list_playlists(args.credentials), ensure_ascii=False, indent=2))
        elif args.cmd == "playlist-videos":
            playlist = find_playlist_by_title(args.credentials, args.title)
            if not playlist:
                print(f"LỖI: không tìm thấy playlist khớp '{args.title}'.", file=sys.stderr)
                return 1
            video_ids = list_playlist_video_ids(args.credentials, playlist["id"])
            details = get_videos_details(args.credentials, video_ids)
            print(json.dumps({"playlist": playlist, "videos": details}, ensure_ascii=False, indent=2))
    except YouTubeCatalogError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
