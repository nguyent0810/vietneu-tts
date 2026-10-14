"""
Xác thực TikTok Content Posting API qua OAuth2 (Login Kit for Desktop) --
CHỈ cần tương tác 1 LẦN DUY NHẤT để lấy refresh_token. Sau bước bootstrap 1
lần này, mọi lần gọi sau (tiktok_upload.py) đều headless -- không mở trình
duyệt, không cần người ngồi chờ. Cùng kiến trúc/quy ước với youtube_auth.py
(cùng thư mục credentials-per-kênh, cùng cách refresh access_token mỗi lần
gọi thay vì tự canh hạn dùng) -- KHÔNG dùng chung code vì API khác hẳn:
TikTok bắt buộc PKCE (code_verifier/code_challenge) và redirect_uri chỉ
được phép là localhost/127.0.0.1 (không như Google chấp nhận cả 2 dạng).

Khác biệt quan trọng so với YouTube cần biết trước khi dùng:
- refresh_token CHỈ sống 365 ngày (không phải vô hạn như Google) -- cần
  bootstrap lại sau khoảng đó.
- App CHƯA qua audit của TikTok (unaudited/sandbox) chỉ được đăng ở chế độ
  private (SELF_ONLY) -- không thể public ngay cả khi code yêu cầu, TikTok
  tự giới hạn phía server. Đây là rào chắn an toàn tự nhiên cho việc test.
- redirect_uri PHẢI được đăng ký TRƯỚC trong TikTok Developer Portal (app
  settings -> Login Kit -> Redirect URI), khớp CHÍNH XÁC với giá trị dùng ở
  đây (khuyến nghị đăng ký dạng wildcard port "http://127.0.0.1:*/callback/"
  để không phải sửa lại mỗi lần đổi --port).

Thiết lập lần đầu (1 lần/kênh, cần trình duyệt):
    1. Trong TikTok Developer Portal (developers.tiktok.com/apps), thêm
       product "Content Posting API" cho app, đăng ký redirect URI dạng
       "http://127.0.0.1:*/callback/" (wildcard port) hoặc 1 cổng cố định
       khớp --port dưới đây.
    2. Chạy:
       uv run python tiktok_auth.py bootstrap \\
         --client-key <...> --client-secret <...> --channel-label phat_giao
       Trình duyệt sẽ mở, đăng nhập + đồng ý quyền, xong tự lưu
       .tiktok_channels/phat_giao.json (gitignored, chứa refresh_token --
       KHÔNG commit file này).
    3. Từ đó về sau, tiktok_upload.py chỉ cần --credentials
       .tiktok_channels/phat_giao.json, không tương tác gì thêm.
"""
import base64
import hashlib
import json
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OAUTH_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
OAUTH_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# video.publish: bắt buộc cho Content Posting API (direct post + status).
# video.upload: TikTok liệt kê cùng video.publish cho luồng đăng nội dung.
# KHÔNG thêm user.info.basic nếu không thực sự dùng dữ liệu hồ sơ -- xin dư
# quyền dễ bị TikTok flag khi audit app (đã kiểm tra tài liệu chính thức).
DEFAULT_SCOPES = ["video.publish", "video.upload"]

CREDENTIALS_DIR = Path(__file__).parent / ".tiktok_channels"


class TikTokAuthError(RuntimeError):
    pass


class _CallbackHandler(BaseHTTPRequestHandler):
    """Nhận đúng 1 request callback từ TikTok (chứa ?code=...&state=...)
    rồi thôi -- server tắt ngay sau request đầu tiên (xem handle_request()
    ở bootstrap)."""

    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_state = params.get("state", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]
        self.server.auth_error_desc = params.get("error_description", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = "Đã xác thực xong, có thể đóng tab này." if self.server.auth_code else f"Lỗi: {self.server.auth_error}"
        self.wfile.write(f"<html><body><p>{msg}</p></body></html>".encode("utf-8"))

    def log_message(self, format, *args):
        pass


def _credentials_path(channel_label: str) -> Path:
    return CREDENTIALS_DIR / f"{channel_label}.json"


def _make_pkce_pair() -> tuple[str, str]:
    """PKCE bắt buộc cho desktop app (TikTok Login Kit for Desktop) --
    code_verifier: chuỗi ngẫu nhiên 43-128 ký tự [A-Za-z0-9-._~]. Tài liệu
    TikTok mô tả code_challenge = hex(SHA256(code_verifier)) -- KHÁC chuẩn
    PKCE thường thấy ở nơi khác (base64url thay vì hex), làm đúng theo tài
    liệu TikTok, không suy đoán từ chuẩn RFC chung."""
    code_verifier = secrets.token_urlsafe(96)[:128]
    code_challenge = hashlib.sha256(code_verifier.encode("ascii")).hexdigest()
    return code_verifier, code_challenge


def bootstrap(
    client_key: str, client_secret: str, channel_label: str,
    scopes: list[str] | None = None, port: int = 8735,
) -> Path:
    """Chạy 1 LẦN/kênh: mở trình duyệt xin quyền, đổi code lấy refresh_token,
    lưu lại. redirect_uri PHẢI khớp CHÍNH XÁC 1 giá trị đã đăng ký trước
    trong TikTok Developer Portal (xem docstring đầu file)."""
    scopes = scopes or DEFAULT_SCOPES
    redirect_uri = f"http://127.0.0.1:{port}/callback/"
    state = secrets.token_urlsafe(16)
    code_verifier, code_challenge = _make_pkce_pair()

    auth_params = {
        "client_key": client_key, "response_type": "code", "scope": ",".join(scopes),
        "redirect_uri": redirect_uri, "state": state,
        "code_challenge": code_challenge, "code_challenge_method": "S256",
    }
    auth_url = f"{OAUTH_AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

    httpd = HTTPServer(("127.0.0.1", port), _CallbackHandler)
    httpd.auth_code = None
    httpd.auth_state = None
    httpd.auth_error = None
    httpd.auth_error_desc = None

    print(f"Mở trình duyệt để đăng nhập + đồng ý quyền...\nNếu không tự mở, truy cập:\n{auth_url}\n", flush=True)
    webbrowser.open(auth_url)
    httpd.handle_request()  # block tới khi nhận đúng 1 request callback

    if httpd.auth_error or not httpd.auth_code:
        raise TikTokAuthError(f"OAuth thất bại: {httpd.auth_error or 'không nhận được code'} ({httpd.auth_error_desc or ''})")
    if httpd.auth_state != state:
        raise TikTokAuthError("state trả về không khớp -- có thể bị CSRF/callback giả, DỪNG, không tin code này.")

    token_data = urllib.parse.urlencode({
        "client_key": client_key, "client_secret": client_secret, "code": httpd.auth_code,
        "grant_type": "authorization_code", "redirect_uri": redirect_uri, "code_verifier": code_verifier,
    }).encode("utf-8")
    req = urllib.request.Request(
        OAUTH_TOKEN_URL, data=token_data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tokens = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise TikTokAuthError(f"Đổi code lấy token thất bại: {exc.read().decode('utf-8', 'replace')}")

    if "error" in tokens or not tokens.get("refresh_token"):
        raise TikTokAuthError(f"TikTok không trả token hợp lệ: {tokens!r}")

    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    creds_path = _credentials_path(channel_label)
    creds_path.write_text(json.dumps({
        "channel_label": channel_label,
        "open_id": tokens.get("open_id"),
        "client_key": client_key, "client_secret": client_secret,
        "refresh_token": tokens["refresh_token"], "scopes": scopes,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    creds_path.chmod(0o600)

    print(f"OK -- đã lưu {creds_path} (open_id={tokens.get('open_id')}).")
    print("LƯU Ý: nếu app này CHƯA qua audit TikTok, mọi bài đăng sẽ bị giới hạn "
          "chế độ private (SELF_ONLY) phía server TikTok, bất kể tham số truyền vào.")
    return creds_path


def load_credentials(credentials_path: str | Path) -> dict:
    path = Path(credentials_path)
    if not path.exists():
        raise TikTokAuthError(
            f"Chưa có credentials tại {path} -- chạy bootstrap 1 lần trước "
            f"(xem docstring đầu file tiktok_auth.py)."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def get_valid_access_token(credentials_path: str | Path) -> str:
    """Luôn refresh lấy access_token mới thay vì cache/tự theo dõi hạn dùng
    -- cùng lý do đã áp dụng ở youtube_auth.py (đơn giản hơn tự canh hết
    hạn, phí round-trip mạng không đáng kể cho tần suất dùng thực tế)."""
    creds = load_credentials(credentials_path)
    token_data = urllib.parse.urlencode({
        "client_key": creds["client_key"], "client_secret": creds["client_secret"],
        "grant_type": "refresh_token", "refresh_token": creds["refresh_token"],
    }).encode("utf-8")
    req = urllib.request.Request(
        OAUTH_TOKEN_URL, data=token_data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tokens = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise TikTokAuthError(
            f"Refresh access_token thất bại (refresh_token có thể đã hết hạn 365 ngày hoặc bị "
            f"thu hồi -- cần bootstrap lại): {exc.read().decode('utf-8', 'replace')}"
        )
    if "error" in tokens or not tokens.get("access_token"):
        raise TikTokAuthError(f"TikTok không trả access_token hợp lệ khi refresh: {tokens!r}")

    # TikTok có thể trả refresh_token MỚI mỗi lần refresh -- PHẢI ghi đè lại
    # file, nếu không lần refresh sau sẽ dùng refresh_token cũ đã bị thay thế.
    new_refresh_token = tokens.get("refresh_token")
    if new_refresh_token and new_refresh_token != creds["refresh_token"]:
        creds["refresh_token"] = new_refresh_token
        Path(credentials_path).write_text(json.dumps(creds, ensure_ascii=False, indent=2), encoding="utf-8")

    return tokens["access_token"]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    boot = sub.add_parser("bootstrap", help="Chạy 1 lần/kênh để lấy refresh_token")
    boot.add_argument("--client-key", required=True)
    boot.add_argument("--client-secret", required=True)
    boot.add_argument("--channel-label", required=True, help='vd "phat_giao"')
    boot.add_argument("--port", type=int, default=8735)

    args = ap.parse_args()
    if args.cmd == "bootstrap":
        try:
            bootstrap(args.client_key, args.client_secret, args.channel_label, port=args.port)
        except TikTokAuthError as e:
            print(f"LỖI: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
