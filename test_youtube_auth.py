"""Regression test cho BUG THẬT phát hiện qua Codex CLI review trước khi
commit (audit launchd 04/08): OAuth `state` (CSRF token) được sinh ra và
gửi trong auth_url, nhưng trước đây KHÔNG BAO GIỜ được đối chiếu lại lúc
nhận callback -- bất kỳ request nào tới đúng port trong lúc
httpd.handle_request() đang chờ đều được chấp nhận vô điều kiện. Test này
dựng 1 HTTP server callback THẬT (không mock urllib.request phía server,
chỉ mock webbrowser.open để không mở trình duyệt thật) và bắn request giả
lập có state sai/thiếu -- bootstrap() phải từ chối TRƯỚC KHI đổi code lấy
token (không gọi mạng thật ra ngoài)."""
import http.client
import threading
import time

import pytest

import youtube_auth as ya


def _fire_callback_after_delay(port: int, query: str, delay: float = 0.3) -> None:
    """Giả lập trình duyệt redirect về callback SAU KHI server đã bắt đầu
    handle_request() -- chạy trong thread riêng, không chặn test thread.

    Dùng http.client (KHÔNG dùng urllib.request.urlopen) -- 1 test khác
    trong file này monkeypatch thẳng urllib.request.urlopen (module-level,
    dùng CHUNG process với helper này) để giả lập lỗi token exchange; nếu
    helper này cũng đi qua urllib.request.urlopen, nó sẽ VÔ TÌNH bị chính
    mock đó chặn, không bao giờ thật sự gọi tới local callback server,
    khiến httpd.handle_request() treo mãi chờ request không bao giờ tới."""
    def _do():
        time.sleep(delay)
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            conn.request("GET", f"/?{query}")
            conn.getresponse()
        except Exception:
            pass  # server có thể đã đóng response trước khi client đọc xong -- không quan trọng cho test này
    threading.Thread(target=_do, daemon=True).start()


def test_bootstrap_rejects_mismatched_state(monkeypatch):
    monkeypatch.setattr(ya.webbrowser, "open", lambda url: None)
    port = 8901
    _fire_callback_after_delay(port, "code=fake_code_123&state=WRONG_STATE_VALUE")

    with pytest.raises(ya.YouTubeAuthError, match="state không khớp"):
        ya.bootstrap("fake_client_id", "fake_client_secret", "test_channel_mismatch", port=port)


def test_bootstrap_rejects_missing_state(monkeypatch):
    monkeypatch.setattr(ya.webbrowser, "open", lambda url: None)
    port = 8902
    _fire_callback_after_delay(port, "code=fake_code_123")  # KHÔNG có state=... trong query

    with pytest.raises(ya.YouTubeAuthError, match="state không khớp"):
        ya.bootstrap("fake_client_id", "fake_client_secret", "test_channel_missing", port=port)


def test_bootstrap_proceeds_past_state_check_when_state_matches(monkeypatch):
    """Đối chứng: state ĐÚNG phải vượt qua được bước kiểm tra CSRF (không
    raise 'state không khớp'). Mock luôn urllib.request.urlopen cho bước
    đổi code lấy token (Codex CLI review chỉ ra bản đầu vô tình gọi mạng
    THẬT ra oauth2.googleapis.com -- flaky/chậm không cần thiết cho 1 test
    chỉ cần chứng minh "đã đi qua state check", không cần test token
    exchange thật ở đây)."""
    monkeypatch.setattr(ya.secrets, "token_urlsafe", lambda n: "FIXED_TEST_STATE")
    monkeypatch.setattr(ya.webbrowser, "open", lambda url: None)

    def fake_urlopen(req, timeout=15):
        raise ya.urllib.error.HTTPError(req.full_url, 400, "invalid_client (giả lập)", {}, None)
    monkeypatch.setattr(ya.urllib.request, "urlopen", fake_urlopen)

    port = 8903
    _fire_callback_after_delay(port, "code=fake_code_123&state=FIXED_TEST_STATE")

    with pytest.raises(ya.YouTubeAuthError) as exc_info:
        ya.bootstrap("fake_client_id", "fake_client_secret", "test_channel_match", port=port)
    # PHẢI lỗi ở bước đổi code lấy token (mock HTTPError ở trên) -- KHÔNG
    # PHẢI ở bước state check.
    assert "state không khớp" not in str(exc_info.value)
