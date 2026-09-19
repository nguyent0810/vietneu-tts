# Chuyển secret sang máy khác

`secrets.tar.gz.age` ở thư mục gốc repo là bản mã hoá của 4 mục credential.
File này commit được vì nội dung đã mã hoá bằng passphrase (age + scrypt);
chỉ passphrase mới mở được, và passphrase KHÔNG nằm trong repo.

## Bên trong có gì

| Đường dẫn | Nội dung |
|---|---|
| `.youtube_channels/` | refresh_token OAuth YouTube theo từng kênh (`hinh_su`, `phat_giao`, `phong_thuy`) |
| `.tiktok_channels/` | refresh_token OAuth TikTok theo từng kênh |
| `.youtube_oauth_clients.env` | `client_id` / `client_secret` app YouTube |
| `.tiktok_oauth_clients.env` | `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET` |

Cả 4 đều nằm trong `.gitignore` và bị `scripts/secret_scan.py` chặn cứng —
đó là chủ ý: bản plaintext không bao giờ được commit, chỉ bản `.age` mới được.

## Giải mã ở máy mới

```bash
brew install age
```

```bash
age -d secrets.tar.gz.age | tar xzvf -
```

Nhập passphrase khi được hỏi. Lệnh này bung thẳng 4 mục về đúng vị trí cũ
trong thư mục gốc repo. Kiểm tra lại:

```bash
python3 scripts/secret_scan.py
```

Scanner phải báo các file này bị chặn (đúng), và không được thấy chúng xuất
hiện trong `git status` — nếu thấy, `.gitignore` đã bị sửa sai.

## Cập nhật lại archive khi token đổi

Sau khi bootstrap thêm kênh hoặc rotate credential:

```bash
tar czf - .youtube_channels .tiktok_channels .youtube_oauth_clients.env .tiktok_oauth_clients.env | age -p > secrets.tar.gz.age
```

Rồi commit lại `secrets.tar.gz.age` như file thường.

## Passphrase đi đường nào

Không bao giờ qua repo, issue, PR hay commit message. Dùng password manager,
hoặc nhắn trực tiếp qua kênh riêng. Mất passphrase thì không khôi phục được
archive — lúc đó bootstrap lại từ đầu:

```bash
uv run python youtube_auth.py bootstrap --client-id <CLIENT_ID> --client-secret <CLIENT_SECRET> --channel-label phat_giao
```

```bash
uv run python tiktok_auth.py bootstrap --client-key <CLIENT_KEY> --client-secret <CLIENT_SECRET> --channel-label phat_giao
```

## Nếu passphrase bị lộ

Đổi passphrase là chưa đủ — bản `.age` cũ vẫn nằm trong git history và vẫn mở
được bằng passphrase cũ. Phải **rotate token thật**: thu hồi quyền app tại
Google Account → Third-party access và TikTok → Manage app permissions, rồi
bootstrap lại toàn bộ kênh và tạo archive mới.
