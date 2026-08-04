"""
Xác thực YouTube Data API v3 qua OAuth2 -- CHỈ cần tương tác 1 LẦN DUY NHẤT
để lấy refresh_token (Google bắt buộc, không có cách nào tránh hoàn toàn --
kể cả Service Account cũng không upload video lên kênh cá nhân được). Sau
bước bootstrap 1 lần này, mọi lần gọi sau (bulk upload, lên lịch, phân tích
kênh...) đều headless 100% -- không mở trình duyệt, không cần người ngồi
chờ, refresh_token dùng lại được vô hạn lần cho tới khi bị thu hồi thủ công.

Viết mới hoàn toàn (KHÔNG tái sử dụng code app YTM -- app đó là Electron,
logic OAuth/upload gắn chặt vào ipcMain/BrowserWindow/safeStorage, không
tách ra dùng ngoài Electron được, xem báo cáo research). Có tham khảo đúng
thuật toán đã chạy ổn của app đó (chunk 8MB, retry+backoff, refresh khi
401, dừng khi quota cạn -- xem youtube_upload.py) khi viết lại, nhưng code
hoàn toàn mới, gọi thẳng REST API của Google bằng urllib (không phụ thuộc
SDK google-api-python-client, không phụ thuộc Electron).

Thiết lập lần đầu (1 lần/kênh, cần trình duyệt):
    1. Tạo OAuth Client (loại "Desktop app") tại
       https://console.cloud.google.com/apis/credentials -- bật "YouTube
       Data API v3" + "YouTube Analytics API" cho project đó.
    2. Chạy:
       uv run python youtube_auth.py bootstrap \\
         --client-id <...> --client-secret <...> --channel-label kinh_dia_tang
       Trình duyệt sẽ mở, đăng nhập + đồng ý quyền, xong tự lưu
       .youtube_channels/kinh_dia_tang.json (gitignored, chứa refresh_token
       -- KHÔNG commit file này).
    3. Từ đó về sau, mọi script (youtube_upload.py, youtube_analytics.py)
       chỉ cần --credentials .youtube_channels/kinh_dia_tang.json, không
       tương tác gì thêm -- chạy nền/cron được.
"""
import json
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
CHANNELS_LIST_URL = "https://www.googleapis.com/youtube/v3/channels"

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

CREDENTIALS_DIR = Path(__file__).parent / ".youtube_channels"


class YouTubeAuthError(RuntimeError):
    pass


class _CallbackHandler(BaseHTTPRequestHandler):
    """Nhận đúng 1 request callback từ Google (chứa ?code=...) rồi thôi --
    server tắt ngay sau request đầu tiên (xem handle_request() ở bootstrap)."""

    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]
        self.server.auth_state = params.get("state", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = "Đã xác thực xong, có thể đóng tab này." if self.server.auth_code else f"Lỗi: {self.server.auth_error}"
        self.wfile.write(f"<html><body><p>{msg}</p></body></html>".encode("utf-8"))

    def log_message(self, format, *args):
        pass


def _credentials_path(channel_label: str) -> Path:
    return CREDENTIALS_DIR / f"{channel_label}.json"


def bootstrap(
    client_id: str, client_secret: str, channel_label: str,
    scopes: list[str] | None = None, port: int = 8734,
) -> Path:
    """Chạy 1 LẦN/kênh: mở trình duyệt xin quyền, đổi code lấy refresh_token,
    lưu lại. Dùng "loopback IP address flow" -- khuyến nghị chính thức của
    Google cho desktop app, không cần redirect URI public, chỉ 1 server tạm
    trên localhost nhận đúng 1 request rồi tắt ngay."""
    scopes = scopes or DEFAULT_SCOPES
    redirect_uri = f"http://127.0.0.1:{port}"
    state = secrets.token_urlsafe(16)

    auth_params = {
        "client_id": client_id, "redirect_uri": redirect_uri, "response_type": "code",
        "scope": " ".join(scopes), "access_type": "offline", "prompt": "consent", "state": state,
    }
    auth_url = f"{OAUTH_AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

    httpd = HTTPServer(("127.0.0.1", port), _CallbackHandler)
    httpd.auth_code = None
    httpd.auth_error = None
    httpd.auth_state = None

    print(f"Mở trình duyệt để đăng nhập + đồng ý quyền...\nNếu không tự mở, truy cập:\n{auth_url}\n", flush=True)
    webbrowser.open(auth_url)
    httpd.handle_request()  # block tới khi nhận đúng 1 request callback

    if httpd.auth_error or not httpd.auth_code:
        raise YouTubeAuthError(f"OAuth thất bại: {httpd.auth_error or 'không nhận được code'}")

    # BUG THẬT phát hiện qua Codex CLI review trước khi commit: `state`
    # được sinh ra (secrets.token_urlsafe) và gửi đi trong auth_url, nhưng
    # KHÔNG BAO GIỜ được đối chiếu lại lúc nhận callback -- mất hoàn toàn
    # tác dụng chống CSRF/account-binding của tham số state (bất kỳ request
    # nào tới đúng port trong lúc httpd.handle_request() đang chờ đều được
    # chấp nhận, bất kể state khớp hay không). So khớp NGAY trước khi đổi
    # code lấy token -- fail-closed nếu thiếu hoặc không khớp.
    if httpd.auth_state != state:
        raise YouTubeAuthError(
            "OAuth state không khớp (hoặc thiếu) trong callback -- có thể là tấn công CSRF hoặc "
            "callback từ 1 phiên OAuth khác, từ chối đổi code lấy token."
        )

    token_data = urllib.parse.urlencode({
        "code": httpd.auth_code, "client_id": client_id, "client_secret": client_secret,
        "redirect_uri": redirect_uri, "grant_type": "authorization_code",
    }).encode("utf-8")
    req = urllib.request.Request(OAUTH_TOKEN_URL, data=token_data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tokens = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise YouTubeAuthError(f"Đổi code lấy token thất bại: {exc.read().decode('utf-8', 'replace')}")

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise YouTubeAuthError(
            "Google không trả refresh_token -- nếu kênh này đã bootstrap trước đó, vào "
            "https://myaccount.google.com/permissions thu hồi quyền cũ của app rồi chạy lại "
            "(Google chỉ đảm bảo trả refresh_token ở lần consent thật sự MỚI)."
        )

    channel_info = _fetch_own_channel(tokens["access_token"])

    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    creds_path = _credentials_path(channel_label)
    creds_path.write_text(json.dumps({
        "channel_label": channel_label,
        "channel_id": channel_info.get("id"),
        "channel_title": channel_info.get("snippet", {}).get("title"),
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "scopes": scopes,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    creds_path.chmod(0o600)

    print(f"OK -- đã lưu {creds_path} cho kênh '{channel_info.get('snippet', {}).get('title')}'.")
    return creds_path


def _fetch_own_channel(access_token: str) -> dict:
    params = urllib.parse.urlencode({"part": "snippet", "mine": "true"})
    req = urllib.request.Request(f"{CHANNELS_LIST_URL}?{params}", headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise YouTubeAuthError(f"Không lấy được thông tin kênh: {exc.read().decode('utf-8', 'replace')}")
    items = data.get("items", [])
    return items[0] if items else {}


def load_credentials(credentials_path: str | Path) -> dict:
    path = Path(credentials_path)
    if not path.exists():
        raise YouTubeAuthError(
            f"Chưa có credentials tại {path} -- chạy bootstrap 1 lần trước "
            f"(xem docstring đầu file youtube_auth.py)."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def get_valid_access_token(credentials_path: str | Path) -> str:
    """Luôn refresh lấy access_token mới thay vì cache/tự theo dõi hạn dùng
    -- refresh_token dùng lại được vô hạn lần, đơn giản hơn hẳn so với tự
    canh thời điểm hết hạn + lệch giờ hệ thống, và phí thêm 1 round-trip
    mạng là không đáng kể cho tần suất dùng của pipeline này (upload/phân
    tích theo tập, không phải real-time)."""
    creds = load_credentials(credentials_path)
    token_data = urllib.parse.urlencode({
        "client_id": creds["client_id"], "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"], "grant_type": "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request(OAUTH_TOKEN_URL, data=token_data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tokens = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise YouTubeAuthError(
            f"Refresh access_token thất bại (refresh_token có thể đã bị thu hồi -- "
            f"cần bootstrap lại): {exc.read().decode('utf-8', 'replace')}"
        )
    return tokens["access_token"]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    boot = sub.add_parser("bootstrap", help="Chạy 1 lần/kênh để lấy refresh_token")
    boot.add_argument("--client-id", required=True)
    boot.add_argument("--client-secret", required=True)
    boot.add_argument("--channel-label", required=True, help='vd "kinh_dia_tang"')
    boot.add_argument("--port", type=int, default=8734)

    args = ap.parse_args()
    if args.cmd == "bootstrap":
        try:
            bootstrap(args.client_id, args.client_secret, args.channel_label, port=args.port)
        except YouTubeAuthError as e:
            print(f"LỖI: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
