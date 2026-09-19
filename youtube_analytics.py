"""
Kéo dữ liệu phân tích kênh/video qua YouTube Analytics API v2 -- headless
100%, dùng chung credentials với youtube_upload.py (xem youtube_auth.py).
Viết mới hoàn toàn bằng urllib, có tham khảo đúng tập metric app YTM đã
dùng ổn định (views/watch time/subscribers/retention/traffic source), xem
báo cáo research trong lịch sử hội thoại vì sao không tái dùng trực tiếp
code Electron của app đó được.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

from youtube_auth import YouTubeAuthError, get_valid_access_token

ANALYTICS_URL = "https://youtubeanalytics.googleapis.com/v2/reports"

DEFAULT_CHANNEL_METRICS = "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments,shares"
DEFAULT_VIDEO_METRICS = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares"


class YouTubeAnalyticsError(RuntimeError):
    pass


def _query(credentials_path, params: dict) -> dict:
    try:
        access_token = get_valid_access_token(credentials_path)
    except YouTubeAuthError as exc:
        raise YouTubeAnalyticsError(str(exc))
    url = f"{ANALYTICS_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise YouTubeAnalyticsError(f"YouTube Analytics API lỗi ({exc.code}): {exc.read().decode('utf-8', 'replace')}")


def get_channel_analytics(
    credentials_path, start_date: str, end_date: str,
    metrics: str = DEFAULT_CHANNEL_METRICS, dimensions: str = "day",
) -> dict:
    """start_date/end_date dạng YYYY-MM-DD. Trả về báo cáo thô của Google
    (columnHeaders + rows) -- caller tự map theo nhu cầu (dashboard, export
    CSV...), không áp khuôn dạng cứng ở đây."""
    return _query(credentials_path, {
        "ids": "channel==MINE", "startDate": start_date, "endDate": end_date,
        "metrics": metrics, "dimensions": dimensions, "sort": dimensions,
    })


def get_video_analytics(
    credentials_path, video_id: str, start_date: str, end_date: str, metrics: str = DEFAULT_VIDEO_METRICS,
) -> dict:
    return _query(credentials_path, {
        "ids": "channel==MINE", "startDate": start_date, "endDate": end_date,
        "metrics": metrics, "filters": f"video=={video_id}",
    })


def get_traffic_sources(credentials_path, start_date: str, end_date: str, video_id: str | None = None) -> dict:
    params = {
        "ids": "channel==MINE", "startDate": start_date, "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched", "dimensions": "insightTrafficSourceType", "sort": "-views",
    }
    if video_id:
        params["filters"] = f"video=={video_id}"
    return _query(credentials_path, params)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--credentials", required=True)
    ap.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--video-id", default=None, help="Bỏ trống = phân tích toàn kênh")
    args = ap.parse_args()
    try:
        if args.video_id:
            report = get_video_analytics(args.credentials, args.video_id, args.start_date, args.end_date)
        else:
            report = get_channel_analytics(args.credentials, args.start_date, args.end_date)
    except YouTubeAnalyticsError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
