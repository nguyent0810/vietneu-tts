"""Đồng bộ YouTube Analytics của 3 kênh vào Content Hub (Neon).

Chạy CỤC BỘ vì credential OAuth nằm ở máy này (.youtube_channels/{label}.json).
Dữ liệu đã chuẩn hoá được đẩy lên backend qua HTTPS; backend mới là nơi ghi vào
Neon. Máy chủ KHÔNG BAO GIỜ nhận access token của YouTube -- nó chỉ nhận số liệu.

    uv run python youtube_sync.py --channel phong_thuy
    uv run python youtube_sync.py --all
    uv run python youtube_sync.py --all --initial-days 180
    uv run python youtube_sync.py --report

Cấu hình (file .youtube_hub.env, đã gitignore, sinh bởi `npm run worker:token`):
    HUB_WORKER_TOKEN=vhw_...
    HUB_API_BASE=http://127.0.0.1:3000

Tái sử dụng youtube_auth.get_valid_access_token() -- không tự làm lại OAuth,
không đọc client_secret/refresh_token ra ngoài module đó.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from youtube_auth import YouTubeAuthError, get_valid_access_token, load_credentials

REPO_ROOT = Path(__file__).parent
CHANNELS_DIR = REPO_ROOT / ".youtube_channels"
HUB_ENV_FILE = REPO_ROOT / ".youtube_hub.env"

ANALYTICS_URL = "https://youtubeanalytics.googleapis.com/v2/reports"
DATA_API_CHANNELS = "https://www.googleapis.com/youtube/v3/channels"
DATA_API_PLAYLIST_ITEMS = "https://www.googleapis.com/youtube/v3/playlistItems"
DATA_API_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"

# Nhóm chỉ số CỐT LÕI -- có ở mọi kênh. Nếu nhóm này lỗi thì coi như thất bại.
CORE_METRICS = [
    "views",
    "estimatedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "likes",
    "dislikes",
    "comments",
    "shares",
    "subscribersGained",
    "subscribersLost",
]

# Nhóm TUỲ CHỌN -- YouTube chỉ trả cho một số kênh/loại báo cáo. Gọi RIÊNG để
# khi nhóm này lỗi thì chỉ mất impressions/CTR chứ không mất luôn chỉ số cốt lõi.
# Gộp chung một request thì một chỉ số không được hỗ trợ sẽ làm hỏng cả lô.
OPTIONAL_METRICS = ["impressions", "impressionClickThroughRate"]

# Ánh xạ tên chỉ số của YouTube sang tên trường của API Content Hub.
METRIC_FIELD = {
    "views": "views",
    "estimatedMinutesWatched": "estimatedMinutesWatched",
    "averageViewDuration": "averageViewDurationSeconds",
    "averageViewPercentage": "averageViewPercentage",
    "impressions": "impressions",
    "impressionClickThroughRate": "impressionCtr",
    "likes": "likes",
    "dislikes": "dislikes",
    "comments": "comments",
    "shares": "shares",
    "subscribersGained": "subscribersGained",
    "subscribersLost": "subscribersLost",
}

INT_FIELDS = {
    "views",
    "impressions",
    "likes",
    "dislikes",
    "comments",
    "shares",
    "subscribersGained",
    "subscribersLost",
}


class SyncError(RuntimeError):
    pass


@dataclass
class HubConfig:
    base_url: str
    token: str
    worker_label: str


@dataclass
class SyncStats:
    videos: int = 0
    video_metric_rows: int = 0
    channel_metric_rows: int = 0
    revised_rows: int = 0
    skipped_unknown_video: int = 0
    # Ghi chú THÔNG TIN: đã biết trước và không có nghĩa là thiếu dữ liệu.
    # Ví dụ: kênh này không được YouTube cấp impressions/CTR.
    notes: list[str] = field(default_factory=list)
    # LỖ HỔNG dữ liệu thật: có ngày/video lẽ ra phải lấy được nhưng không lấy
    # được. Chỉ những mục này mới hạ trạng thái xuống PARTIAL và giữ checkpoint.
    gaps: list[str] = field(default_factory=list)
    api_calls: list[dict] = field(default_factory=list)

    @property
    def warnings(self) -> list[str]:
        return [*self.gaps, *self.notes]


# --------------------------------------------------------------------------
# Cấu hình
# --------------------------------------------------------------------------


def load_hub_config() -> HubConfig:
    if not HUB_ENV_FILE.exists():
        raise SyncError(
            f"Chưa có {HUB_ENV_FILE.name}. Chạy trong apps/hub:\n"
            f"  npm run worker:token -- --label <tên máy>"
        )
    values: dict[str, str] = {}
    for line in HUB_ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()

    token = values.get("HUB_WORKER_TOKEN", "")
    if not token:
        raise SyncError(f"{HUB_ENV_FILE.name} thiếu HUB_WORKER_TOKEN.")

    return HubConfig(
        base_url=values.get("HUB_API_BASE", "http://127.0.0.1:3000").rstrip("/"),
        token=token,
        worker_label=values.get("HUB_WORKER_LABEL", "local"),
    )


def available_channel_labels() -> list[str]:
    if not CHANNELS_DIR.exists():
        return []
    return sorted(p.stem for p in CHANNELS_DIR.glob("*.json"))


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


def _request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict | None = None,
    timeout: int = 60,
) -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    if data is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"raw": raw.decode("utf-8", "replace")[:500]}
        return exc.code, payload
    except urllib.error.URLError as exc:
        raise SyncError(f"Không kết nối được {url.split('?')[0]}: {exc.reason}") from exc


def hub_post(cfg: HubConfig, path: str, body: dict) -> dict:
    status, payload = _request(
        f"{cfg.base_url}{path}",
        method="POST",
        headers={"Authorization": f"Bearer {cfg.token}"},
        body=body,
    )
    if status >= 400:
        err = payload.get("error", {})
        code = err.get("code", "UNKNOWN")
        msg = err.get("message", "")
        # Kèm chi tiết lỗi validate (đường dẫn trường, không có giá trị) --
        # thiếu nó thì "Payload không hợp lệ" là thông báo vô dụng khi debug.
        details = err.get("details")
        detail_text = ""
        if details:
            shown = details[:5] if isinstance(details, list) else [details]
            detail_text = " | " + "; ".join(
                f"{d.get('path')}: {d.get('message')}" if isinstance(d, dict) else str(d)
                for d in shown
            )
        raise SyncError(f"Hub {path} trả {status} [{code}]: {msg}{detail_text}")
    return payload


def hub_get(cfg: HubConfig, path: str) -> dict:
    status, payload = _request(
        f"{cfg.base_url}{path}", headers={"Authorization": f"Bearer {cfg.token}"}
    )
    if status >= 400:
        code = payload.get("error", {}).get("code", "UNKNOWN")
        raise SyncError(f"Hub {path} trả {status} [{code}]")
    return payload


def youtube_get(url: str, params: dict, token: str) -> tuple[int, dict, float]:
    """Gọi API YouTube. Trả (status, payload, thời gian ms)."""
    started = time.monotonic()
    status, payload = _request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return status, payload, (time.monotonic() - started) * 1000


# --------------------------------------------------------------------------
# Danh tính kênh
# --------------------------------------------------------------------------


def verify_channel_identity(label: str, token: str, expected_channel_id: str) -> dict:
    """Xác nhận token đang thao tác ĐÚNG kênh mong đợi.

    Bước này không thừa: nếu ai đó bootstrap nhầm tài khoản Google cho một
    label, mọi số liệu sau đó sẽ được ghi vào sai kênh trong database mà không
    có gì báo lỗi -- một loại hỏng dữ liệu rất khó phát hiện về sau.
    """
    status, payload, _ = youtube_get(
        DATA_API_CHANNELS,
        {"part": "snippet,contentDetails,statistics", "mine": "true"},
        token,
    )
    if status >= 400:
        raise SyncError(f"[{label}] channels.list lỗi {status}: {payload.get('error', {}).get('message', '')}")

    items = payload.get("items", [])
    if not items:
        raise SyncError(f"[{label}] Token không gắn với kênh YouTube nào.")

    actual = items[0]
    actual_id = actual.get("id", "")
    if actual_id != expected_channel_id:
        raise SyncError(
            f"[{label}] SAI KÊNH: credential trỏ tới {actual_id} nhưng cấu hình ghi "
            f"{expected_channel_id}. Không đồng bộ để tránh ghi số liệu vào nhầm kênh."
        )
    return actual


# --------------------------------------------------------------------------
# Lấy danh sách video
# --------------------------------------------------------------------------


def _parse_iso8601_duration(value: str) -> int | None:
    """PT1H2M3S -> giây. Trả None nếu không đọc được."""
    if not value or not value.startswith("PT"):
        return None
    total, number = 0, ""
    for ch in value[2:]:
        if ch.isdigit():
            number += ch
        elif ch in "HMS" and number:
            total += int(number) * {"H": 3600, "M": 60, "S": 1}[ch]
            number = ""
        else:
            number = ""
    return total


def discover_videos_with_data(
    label: str, token: str, channel_id: str, start: str, end: str, limit: int, stats: SyncStats
) -> list[str]:
    """Hỏi YouTube những video nào THỰC SỰ có dữ liệu trong cửa sổ.

    Vì sao không lấy đơn giản N video mới nhất từ playlist uploads: kênh đăng
    dày (nhiều short mỗi ngày) thì N video mới nhất đều vừa đăng và gần như
    chưa có số liệu, trong khi các video ĐANG có lượt xem lại nằm sâu hơn trong
    playlist. Lấy theo độ mới sẽ tốn hàng chục request để nhận về 0 hàng — đúng
    điều đã xảy ra ở lần chạy thật đầu tiên.

    Một request `dimensions=video` cho ra đúng tập video có dữ liệu, xếp theo
    lượt xem giảm dần.
    """
    PAGE = 200  # trần maxResults của YouTube Analytics
    found: list[str] = []
    start_index = 1

    # Điều kiện dừng phải cho phép VƯỢT `limit` một chút, không dừng đúng tại
    # `limit`. Dừng ngay khi len(found) == limit thì một trang đầy vừa khít
    # (vd limit=200, trang trả đúng 200) trông y hệt "đã hết dữ liệu": không có
    # gap nào được ghi, run vẫn SUCCEEDED, checkpoint vẫn tiến, và phần còn lại
    # không bao giờ được lấy nữa. Phải lấy dư ít nhất 1 mục để PHÂN BIỆT được
    # "vừa đủ" với "còn nữa".
    while True:
        params = {
            "ids": f"channel=={channel_id}",
            "startDate": start,
            "endDate": end,
            "metrics": "views",
            "dimensions": "video",
            "sort": "-views",
            "maxResults": PAGE,
            "startIndex": start_index,
        }
        status, payload, elapsed = youtube_get(ANALYTICS_URL, params, token)
        stats.api_calls.append({
            "endpoint": "youtubeAnalytics.reports.query(topVideos)",
            "requestParams": dict(params),
            "httpStatus": status,
            "rowCount": len(payload.get("rows", []) or []) if status < 400 else 0,
            "responseHash": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            if status < 400 else None,
            "columnHeaders": payload.get("columnHeaders") if status < 400 else None,
            "durationMs": int(elapsed),
        })
        if status >= 400:
            if start_index > 1 and status == 400:
                # Báo cáo "top video" của YouTube Analytics chỉ trả TỐI ĐA 200
                # hàng; startIndex=201 trả 400. Đây là trần cứng của API, không
                # phải lỗi. Không coi là lỗ hổng vì phần thiếu được bù bằng danh
                # sách đầy đủ từ playlist uploads (playlist phân trang không giới
                # hạn) -- xem `fetch_recent_video_ids` và cách gộp ở sync_channel.
                stats.notes.append(
                    f"Báo cáo top-video của YouTube dừng ở {len(found)} mục (trần 200 "
                    f"hàng của API); phần còn lại lấy qua playlist uploads."
                )
                return found
            stats.gaps.append(f"Không liệt kê được video có dữ liệu (HTTP {status}).")
            return found

        rows = payload.get("rows") or []
        found.extend(row[0] for row in rows if row and row[0])
        if len(rows) < PAGE:
            break  # trang ngắn = đã hết dữ liệu thật
        if len(found) > limit:
            break  # đã lấy dư đủ để biết chắc là bị cắt
        start_index += PAGE

    # Bị cắt vì chạm trần --max-videos: đây là LỖ HỔNG dữ liệu thật, không phải
    # ghi chú. Nếu chỉ im lặng cắt bớt thì run vẫn SUCCEEDED, checkpoint vẫn
    # tiến, và những video xếp sau sẽ không bao giờ được lấy lại -- lỗ hổng
    # lịch sử vĩnh viễn nằm ngoài cửa sổ lùi 7 ngày.
    if len(found) > limit:
        # Cắt bớt ở đây KHÔNG sinh gap: hợp với danh sách playlist ở
        # `sync_channel` mới là nơi quyết định độ phủ, và chính chỗ đó báo lỗ
        # hổng nếu --max-videos còn thiếu.
        found = found[:limit]

    return found


def fetch_recent_video_ids(label: str, token: str, uploads_playlist: str, limit: int) -> list[str]:
    """ID các video mới nhất từ playlist "uploads".

    Dùng playlistItems chứ không dùng search.list: search tốn 100 đơn vị quota
    mỗi lần gọi và không đảm bảo trả đủ, còn playlistItems tốn 1 đơn vị.

    Video mới đăng thường chưa có số liệu, nhưng vẫn cần đưa vào database để
    Phase 3 phân tích được "hiệu suất giai đoạn đầu" và biết video nào vừa ra
    mà chưa có dữ liệu — khác hẳn với video không tồn tại.
    """
    video_ids: list[str] = []
    page_token = ""

    # Lấy DƯ một mục so với `limit`, cùng lý do như ở discover_videos_with_data:
    # dừng đúng tại `limit` thì kênh có đúng limit+1 video trông y hệt kênh có
    # đúng limit video. Khi đó hợp hai nguồn vẫn bằng limit, không gap nào được
    # ghi, run SUCCEEDED, checkpoint tiến — và video thứ limit+1 mất vĩnh viễn.
    while len(video_ids) <= limit:
        params = {"part": "contentDetails", "playlistId": uploads_playlist, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        status, payload, _ = youtube_get(DATA_API_PLAYLIST_ITEMS, params, token)
        if status >= 400:
            raise SyncError(f"[{label}] playlistItems lỗi {status}")

        for item in payload.get("items", []):
            vid = item.get("contentDetails", {}).get("videoId")
            if vid:
                video_ids.append(vid)

        page_token = payload.get("nextPageToken", "")
        if not page_token:
            break

    # Trả về tối đa limit+1 để phía gọi PHÂN BIỆT được "vừa đủ" với "còn nữa".
    return video_ids[: limit + 1]


def fetch_video_metadata(label: str, token: str, video_ids: list[str], tz: ZoneInfo) -> list[dict]:
    """Lấy metadata cho một tập ID video cụ thể."""
    if not video_ids:
        return []

    videos: list[dict] = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        status, payload, _ = youtube_get(
            DATA_API_VIDEOS,
            {"part": "snippet,contentDetails,status", "id": ",".join(chunk)},
            token,
        )
        if status >= 400:
            raise SyncError(f"[{label}] videos.list lỗi {status}")

        for item in payload.get("items", []):
            snippet = item.get("snippet", {})
            published_at = snippet.get("publishedAt", "")
            duration = _parse_iso8601_duration(item.get("contentDetails", {}).get("duration", ""))

            local_hour = None
            if published_at:
                try:
                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    local_hour = dt.astimezone(tz).hour
                except ValueError:
                    local_hour = None

            videos.append(
                {
                    "youtubeVideoId": item["id"],
                    "title": snippet.get("title", "(không tiêu đề)")[:500],
                    "description": (snippet.get("description") or "")[:10000] or None,
                    "publishedAt": published_at,
                    "durationSeconds": duration,
                    # Ranh giới Shorts từng đổi (60s rồi 180s). Chỉ phân loại khi
                    # chắc chắn; còn lại để UNKNOWN cho Phase 3 tự xử lý, thay vì
                    # đoán bừa và làm lệch mọi so sánh long-form vs shorts.
                    "format": "SHORT" if duration is not None and duration <= 60 else (
                        "LONG_FORM" if duration is not None and duration > 180 else "UNKNOWN"
                    ),
                    "privacyStatus": item.get("status", {}).get("privacyStatus"),
                    "publishedHourLocal": local_hour,
                }
            )

    return videos


# --------------------------------------------------------------------------
# YouTube Analytics
# --------------------------------------------------------------------------


def _rows_to_records(payload: dict, metrics: list[str], extra: dict | None = None) -> list[dict]:
    """Chuyển đáp ứng {columnHeaders, rows} thành list dict theo tên trường Hub."""
    headers = [h.get("name") for h in payload.get("columnHeaders", [])]
    records = []
    for row in payload.get("rows", []) or []:
        item = dict(extra or {})
        for name, value in zip(headers, row):
            if name == "day":
                item["date"] = value
                continue
            field_name = METRIC_FIELD.get(name)
            if field_name is None or value is None:
                continue
            item[field_name] = int(value) if field_name in INT_FIELDS else float(value)
        if "date" in item:
            records.append(item)
    void = metrics  # giữ chữ ký ổn định
    del void
    return records


def fetch_daily_report(
    label: str,
    token: str,
    channel_id: str,
    start: str,
    end: str,
    metrics: list[str],
    video_id: str | None,
    stats: SyncStats,
) -> tuple[list[dict], int]:
    """Một báo cáo theo ngày. Trả (records, http_status).

    KHÔNG ném lỗi khi status >= 400: phía gọi quyết định chỉ số nào là tuỳ chọn.
    """
    params = {
        "ids": f"channel=={channel_id}",
        "startDate": start,
        "endDate": end,
        "metrics": ",".join(metrics),
        "dimensions": "day",
    }
    if video_id:
        params["filters"] = f"video=={video_id}"

    status, payload, elapsed = youtube_get(ANALYTICS_URL, params, token)

    # Nhật ký nguồn gốc: chỉ tham số truy vấn, KHÔNG có Authorization header.
    stats.api_calls.append(
        {
            "endpoint": "youtubeAnalytics.reports.query",
            "requestParams": {k: v for k, v in params.items()},
            "httpStatus": status,
            "rowCount": len(payload.get("rows", []) or []) if status < 400 else 0,
            "responseHash": hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()
            if status < 400
            else None,
            "columnHeaders": payload.get("columnHeaders") if status < 400 else None,
            "durationMs": int(elapsed),
        }
    )

    if status >= 400:
        return [], status

    extra = {"youtubeVideoId": video_id} if video_id else {}
    return _rows_to_records(payload, metrics, extra), status


def is_transient_status(status: int) -> bool:
    """Lỗi TẠM THỜI (lấy lại được) hay giới hạn CỐ ĐỊNH của kênh?

    Phân biệt này quyết định checkpoint có được tiến hay không:

      - 400 / 404: YouTube không hỗ trợ chỉ số đó cho kênh/loại báo cáo này.
        Vĩnh viễn, chạy lại bao nhiêu lần cũng vậy -> ghi chú, không chặn.
      - MỌI mã còn lại (403 quota/quyền, 429 quá tần suất, 401 token hết hạn,
        408 timeout, 5xx lỗi phía YouTube): dữ liệu LẼ RA lấy được nhưng lần
        này không lấy được -> LỖ HỔNG, giữ checkpoint.

    Danh sách CHO PHÉP là nhánh "vĩnh viễn", không phải nhánh "tạm thời". Làm
    ngược lại (liệt kê các mã tạm thời) thì mọi mã chưa nghĩ tới — như 401 khi
    access token hết hạn giữa chừng một lần sync dài — sẽ âm thầm rơi vào nhánh
    "vĩnh viễn", checkpoint vẫn tiến và dữ liệu mất luôn. Đó đúng là hướng sai
    để mặc định.

    Nguyên tắc: không chắc thì coi là tạm thời. Đồng bộ thừa một lần rẻ hơn
    nhiều so với mất dữ liệu vĩnh viễn.
    """
    PERMANENT = {400, 404}
    return status not in PERMANENT


def merge_records(primary: list[dict], secondary: list[dict], key_fields: tuple[str, ...]) -> list[dict]:
    """Gộp hai tập bản ghi theo khoá, ưu tiên giữ giá trị đã có."""
    index: dict[tuple, dict] = {}
    for rec in primary:
        index[tuple(rec.get(k) for k in key_fields)] = dict(rec)
    for rec in secondary:
        key = tuple(rec.get(k) for k in key_fields)
        if key in index:
            index[key].update({k: v for k, v in rec.items() if k not in key_fields})
        else:
            index[key] = dict(rec)
    return list(index.values())


# --------------------------------------------------------------------------
# Đồng bộ một kênh
# --------------------------------------------------------------------------


def sync_channel(cfg: HubConfig, label: str, initial_days: int, max_videos: int, verbose: bool) -> dict:
    creds_path = CHANNELS_DIR / f"{label}.json"
    creds = load_credentials(creds_path)
    expected_channel_id = creds["channel_id"]

    access_token = get_valid_access_token(creds_path)

    channel_info = verify_channel_identity(label, access_token, expected_channel_id)
    uploads_playlist = (
        channel_info.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    )
    if not uploads_playlist:
        raise SyncError(f"[{label}] Kênh không có playlist uploads.")

    started = hub_post(
        cfg,
        "/api/v1/sync/start",
        {
            "channelLabel": label,
            "workerLabel": cfg.worker_label,
            "initialDays": initial_days,
        },
    )
    sync_run_id = started["syncRunId"]
    window = started["window"]
    tz = ZoneInfo(started["channel"]["reportingTimezone"])
    stats = SyncStats()

    # Đối chiếu BA nguồn danh tính, không chỉ hai.
    #
    # `verify_channel_identity` ở trên mới chỉ khẳng định token khớp channel_id
    # ghi TRONG CÙNG file credential -- một file bị hoán nhầm nhưng tự nhất quán
    # (credential của kênh A kèm channel_id của kênh A, nhưng đặt tên file là
    # kênh B) vẫn qua được. Khi đó số liệu của kênh A sẽ được ghi vào bản ghi
    # kênh B trong database, và không có gì báo lỗi.
    hub_channel_id = started["channel"]["youtubeChannelId"]
    if hub_channel_id != expected_channel_id:
        hub_post(cfg, "/api/v1/sync/finish", {
            "syncRunId": sync_run_id,
            "status": "FAILED",
            "errorMessage": "Danh tính kênh không khớp giữa credential và database.",
        })
        raise SyncError(
            f"[{label}] LỆCH DANH TÍNH: hub ghi kênh {hub_channel_id} cho label "
            f"'{label}', nhưng credential trỏ tới {expected_channel_id}. Dừng để "
            f"tránh ghi số liệu của kênh này vào kênh khác."
        )

    print(f"  [{label}] cửa sổ {window['from']} → {window['to']}"
          f" (checkpoint trước: {started.get('previousCheckpoint') or 'chưa có'})")

    try:
        # Thứ tự quan trọng: hỏi trước xem video nào CÓ dữ liệu trong cửa sổ,
        # rồi mới bổ sung một ít video mới nhất (thường chưa có số liệu nhưng
        # cần tồn tại trong DB để phân tích giai đoạn đầu).
        with_data = discover_videos_with_data(
            label, access_token, expected_channel_id, window["from"], window["to"], max_videos, stats
        )
        # Lấy ĐẦY ĐỦ danh sách video từ playlist uploads (phân trang không bị
        # trần 200 như báo cáo top-video), để độ phủ bị giới hạn bởi
        # --max-videos chứ không bởi trần của API.
        recent = fetch_recent_video_ids(label, access_token, uploads_playlist, max_videos)

        ordered_ids: list[str] = []
        for vid in [*with_data, *recent]:
            if vid not in ordered_ids:
                ordered_ids.append(vid)
        if len(ordered_ids) > max_videos:
            stats.gaps.append(
                f"Kênh có {len(ordered_ids)} video nhưng --max-videos={max_videos} "
                f"nên chỉ xử lý {max_videos}. Tăng --max-videos rồi chạy lại."
            )
        ordered_ids = ordered_ids[:max_videos]

        videos = fetch_video_metadata(label, access_token, ordered_ids, tz)
        stats.videos = len(videos)
        print(f"  [{label}] {len(videos)} video ({len(with_data)} có dữ liệu trong cửa sổ)")

        if not videos:
            stats.notes.append("Kênh chưa có video nào.")

        # --- Chỉ số cấp kênh ---
        channel_core, status = fetch_daily_report(
            label, access_token, expected_channel_id, window["from"], window["to"],
            CORE_METRICS, None, stats,
        )
        if status >= 400:
            raise SyncError(f"[{label}] Báo cáo kênh lỗi {status} — chỉ số cốt lõi không lấy được.")

        channel_optional, opt_status = fetch_daily_report(
            label, access_token, expected_channel_id, window["from"], window["to"],
            OPTIONAL_METRICS, None, stats,
        )
        if opt_status >= 400:
            if is_transient_status(opt_status):
                stats.gaps.append(
                    f"impressions/CTR cấp kênh thất bại TẠM THỜI (HTTP {opt_status}) — "
                    f"giữ checkpoint để lần sau lấy lại."
                )
            else:
                stats.notes.append(
                    f"Kênh không được cấp impressions/CTR (HTTP {opt_status}) — các cột đó "
                    f"để trống thay vì ghi 0. Đây là giới hạn cố định của YouTube cho kênh "
                    f"này, KHÔNG phải lỗ hổng dữ liệu."
                )

        channel_metrics = merge_records(channel_core, channel_optional, ("date",))
        if not channel_metrics:
            stats.gaps.append(
                f"Không có dữ liệu cấp kênh cho {window['from']}..{window['to']}."
            )

        # --- Chỉ số cấp video ---
        # YouTube Analytics không hỗ trợ dimensions=video,day trong cùng một báo
        # cáo, nên phải hỏi từng video với filters=video==ID và dimensions=day.
        # CHỈ hỏi chi tiết theo ngày cho video đã biết là có dữ liệu. Hỏi cả
        # những video mới đăng chưa có số liệu chỉ tốn request để nhận về 0 hàng.
        video_metrics: list[dict] = []
        optional_failures = 0            # giới hạn cố định của kênh -> ghi chú
        transient_optional_failures = 0  # lỗi tạm thời -> lỗ hổng
        # Hỏi chi tiết cho HỢP của hai nguồn, ưu tiên video đã biết là có dữ
        # liệu (xếp theo lượt xem) rồi tới phần còn lại từ playlist. Chỉ dựa vào
        # danh sách top-video sẽ bỏ sót mọi video xếp sau hạng 200.
        detail_targets = ordered_ids
        for idx, vid in enumerate(detail_targets, start=1):
            core, st = fetch_daily_report(
                label, access_token, expected_channel_id, window["from"], window["to"],
                CORE_METRICS, vid, stats,
            )
            if st == 403:
                stats.gaps.append(f"Quota/quyền bị từ chối ở video {vid} — dừng phần video.")
                break
            if st >= 400:
                stats.gaps.append(f"Video {vid}: báo cáo lỗi {st}, bỏ qua.")
                continue

            opt, opt_st = fetch_daily_report(
                label, access_token, expected_channel_id, window["from"], window["to"],
                OPTIONAL_METRICS, vid, stats,
            )
            if opt_st >= 400:
                if is_transient_status(opt_st):
                    transient_optional_failures += 1
                else:
                    optional_failures += 1

            video_metrics.extend(merge_records(core, opt, ("youtubeVideoId", "date")))

            if verbose and idx % 10 == 0:
                print(f"    ...{idx}/{len(detail_targets)} video")

        if optional_failures:
            stats.notes.append(
                f"{optional_failures}/{len(detail_targets)} video không có impressions/CTR "
                f"(giới hạn cố định của kênh)."
            )
        if transient_optional_failures:
            stats.gaps.append(
                f"{transient_optional_failures}/{len(detail_targets)} video lỗi TẠM THỜI khi "
                f"lấy impressions/CTR — giữ checkpoint để lần sau lấy lại."
            )

        # --- Đẩy lên hub theo lô ---
        # Lô nhỏ hơn nhiều so với trần 4.5 MB của Vercel: vượt trần sẽ bị hạ tầng
        # chặn bằng 413 trước khi code chạy, tức client nhận lỗi ngoài hợp đồng.
        push_batch(cfg, sync_run_id, videos=videos, video_metrics=[], channel_metrics=[], stats=stats)
        for i in range(0, len(video_metrics), 500):
            push_batch(
                cfg, sync_run_id,
                videos=[], video_metrics=video_metrics[i : i + 500], channel_metrics=[], stats=stats,
            )
        push_batch(
            cfg, sync_run_id,
            videos=[], video_metrics=[], channel_metrics=channel_metrics, stats=stats,
        )

        # Nhật ký lời gọi API gửi riêng để không phình lô dữ liệu.
        for i in range(0, len(stats.api_calls), 50):
            hub_post(cfg, "/api/v1/sync/ingest", {
                "syncRunId": sync_run_id,
                "apiCalls": stats.api_calls[i : i + 50],
            })

        # PARTIAL CHỈ khi có lỗ hổng dữ liệu thật. Nếu để ghi chú thông tin
        # (như "kênh không có impressions") cũng hạ trạng thái thì checkpoint
        # sẽ KHÔNG BAO GIỜ tiến được, và mọi lần sync đều lấy lại từ đầu.
        status_final = "PARTIAL" if stats.gaps else "SUCCEEDED"
        result = hub_post(cfg, "/api/v1/sync/finish", {
            "syncRunId": sync_run_id,
            "status": status_final,
            # Checkpoint CHỈ tiến khi thành công trọn vẹn. PARTIAL nghĩa là còn
            # lỗ hổng; đẩy checkpoint lúc đó sẽ khoá vĩnh viễn phần thiếu.
            **({"lastCompleteDate": window["to"]} if status_final == "SUCCEEDED" else {}),
            "warnings": stats.warnings[:200],
        })
        return {"label": label, "status": status_final, "window": window, **result}

    except Exception as exc:
        hub_post(cfg, "/api/v1/sync/finish", {
            "syncRunId": sync_run_id,
            "status": "FAILED",
            "errorMessage": str(exc)[:1000],
            "warnings": stats.warnings[:200],
        })
        raise


def push_batch(
    cfg: HubConfig,
    sync_run_id: str,
    *,
    videos: list[dict],
    video_metrics: list[dict],
    channel_metrics: list[dict],
    stats: SyncStats,
) -> None:
    if not videos and not video_metrics and not channel_metrics:
        return
    result = hub_post(cfg, "/api/v1/sync/ingest", {
        "syncRunId": sync_run_id,
        "videos": videos,
        "videoMetrics": video_metrics,
        "channelMetrics": channel_metrics,
    })
    stats.video_metric_rows += result.get("videoMetricRowsUpserted", 0)
    stats.channel_metric_rows += result.get("channelMetricRowsUpserted", 0)
    stats.revised_rows += result.get("videoMetricRowsRevised", 0)
    skipped = result.get("videoMetricRowsSkippedUnknownVideo", 0)
    if skipped:
        stats.skipped_unknown_video += skipped
        stats.gaps.append(f"{skipped} hàng chỉ số bị bỏ vì video chưa có trong database.")


# --------------------------------------------------------------------------
# Báo cáo
# --------------------------------------------------------------------------


def print_report(cfg: HubConfig, channel_label: str | None, detail: bool = False) -> None:
    params = {}
    if channel_label:
        params["channelLabel"] = channel_label
    if detail:
        params["detail"] = "true"
    path = "/api/v1/sync/report" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    data = hub_get(cfg, path)

    print("\n" + "=" * 78)
    print("BÁO CÁO NHẬP DỮ LIỆU")
    print("=" * 78)

    for ch in data.get("channels", []):
        print(f"\n{ch['label']}  ({ch['youtubeChannelId']})  tz={ch['reportingTimezone']}")
        print(f"  video           : {ch['videoCount']}")
        print(f"  hàng chỉ số     : {ch['metricRows']}")
        rng = ch["dateRange"]
        print(f"  dải ngày        : {rng['first'] or '—'} → {rng['last'] or '—'}")
        print(f"  checkpoint      : {ch['checkpoint'] or 'chưa có'}")
        print(f"  hàng bị sửa lại : {ch['revisedRows']}")
        cov = ch["metricCoveragePercent"]
        if any(v is not None for v in cov.values()):
            print("  độ phủ chỉ số   :")
            for name, pct in cov.items():
                if pct is None:
                    continue
                bar = "█" * int(pct / 5) if pct else ""
                flag = "" if pct >= 99 else ("  ← thiếu" if pct < 50 else "  ← không đủ")
                print(f"      {name:<28} {pct:5.1f}% {bar}{flag}")

    det = data.get("detail")
    if det:
        print("\n" + "-" * 78)
        print("CHI TIẾT: TỪNG VIDEO ĐÃ NHẬP")
        print("-" * 78)
        print(f"  {'video ID':<13} {'ngày':>5} {'lượt xem':>10} {'thiếu':>6}  {'dải ngày':<23} tiêu đề")
        for v in det.get("videos", [])[:40]:
            rng = v["dateRange"]
            span = f"{rng['first'] or '—'}→{rng['last'] or '—'}"
            gap = v["missingDaysInRange"]
            flag = f"{gap:>6}" if gap else "     ·"
            views = v["totalViews"] if v["totalViews"] is not None else 0
            print(f"  {v['youtubeVideoId']:<13} {v['metricDays']:>5} {views:>10,} {flag}  {span:<23} {v['title'][:34]}")
        if len(det.get("videos", [])) > 40:
            print(f"  ... còn {len(det['videos']) - 40} video nữa")
        if det.get("truncated", {}).get("videos"):
            print("  ⚠ danh sách bị cắt bởi detailLimit — tăng --detail-limit để xem đủ")

        dates = det.get("dates", [])
        if dates:
            print("\n" + "-" * 78)
            print(f"CHI TIẾT: TỪNG NGÀY ĐÃ NHẬP ({len(dates)} ngày)")
            print("-" * 78)
            for d in dates[-30:]:
                views = d["totalViews"] if d["totalViews"] is not None else 0
                print(f"  {d['date']}  {d['channel']:<12} video={d['videosWithData']:>4}  views={views:>10,}")
            if len(dates) > 30:
                print(f"  (hiển thị 30 ngày gần nhất trong {len(dates)})")

    runs = data.get("recentSyncRuns", [])
    if runs:
        print("\nCác lần đồng bộ gần nhất:")
        for r in runs[:8]:
            warns = r.get("warnings") or []
            n = len(warns) if isinstance(warns, list) else 0
            print(
                f"  {r['started_at'][:19]}  {r['label']:<12} {r['status']:<10}"
                f" {r['requested_from']}→{r['requested_to']}"
                f"  video={r['videos_seen']} rows={r['video_metric_rows_upserted']}"
                f" revised={r['metric_rows_revised']}"
                + (f"  cảnh báo={n}" if n else "")
            )
    print()


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ YouTube Analytics vào Content Hub")
    # --report tách khỏi nhóm loại trừ: lọc báo cáo theo một kênh là hợp lệ
    # (`--report --channel hinh_su`), chỉ --channel và --all mới xung khắc.
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--channel", help="Label kênh (vd phong_thuy)")
    group.add_argument("--all", action="store_true", help="Đồng bộ cả 3 kênh")
    ap.add_argument("--report", action="store_true", help="Chỉ in báo cáo, không đồng bộ")
    ap.add_argument("--initial-days", type=int, default=90,
                    help="Lần chạy đầu (chưa có checkpoint) lùi bao nhiêu ngày (mặc định 90)")
    ap.add_argument("--max-videos", type=int, default=200,
                    help="Trần số video mỗi kênh (mặc định 200)")
    ap.add_argument("--detail", action="store_true",
                    help="Báo cáo kèm danh sách TỪNG video và TỪNG ngày đã nhập")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    try:
        cfg = load_hub_config()
    except SyncError as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2

    if args.report:
        try:
            print_report(cfg, args.channel, detail=args.detail)
        except SyncError as exc:
            print(f"LỖI: {exc}", file=sys.stderr)
            return 1
        return 0

    labels = available_channel_labels() if args.all else ([args.channel] if args.channel else [])
    if not labels:
        print("Cần --channel <label>, --all, hoặc --report.", file=sys.stderr)
        print(f"Các kênh sẵn có: {', '.join(available_channel_labels()) or '(chưa có)'}", file=sys.stderr)
        return 2

    print(f"Đồng bộ {len(labels)} kênh → {cfg.base_url}")
    results, failures = [], 0

    for label in labels:
        print(f"\n▶ {label}")
        try:
            result = sync_channel(cfg, label, args.initial_days, args.max_videos, args.verbose)
            results.append(result)
            s = result.get("stats", {})
            print(f"  [{label}] {result['status']}"
                  f" — video={s.get('videosSeen', 0)}"
                  f" rows={s.get('videoMetricRowsUpserted', 0)}"
                  f" revised={s.get('metricRowsRevised', 0)}"
                  f" checkpoint={'đã tiến' if result.get('checkpointAdvanced') else 'giữ nguyên'}")
        except (SyncError, YouTubeAuthError) as exc:
            failures += 1
            # Không in traceback: có thể chứa URL kèm tham số nhạy cảm.
            print(f"  [{label}] THẤT BẠI: {exc}", file=sys.stderr)

    try:
        print_report(cfg, None, detail=args.detail)
    except SyncError as exc:
        print(f"Không in được báo cáo: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
