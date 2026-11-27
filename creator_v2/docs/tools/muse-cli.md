# Tạo ảnh AI cho Long bằng Muse (`muse-cli`)

Muse (muse.ai) là agent AI cá nhân của chủ kênh. `muse-cli` cho phép gửi yêu cầu và tải file agent tạo ra ngay từ dòng lệnh, không cần mở trình duyệt hay qua webhook. Từ 27/11/2026 đây là đường chính để tạo ảnh AI cho Long (#539). Đường webhook cũ (`scripts/ai_img_request.py`, `docs/tools/grokbot-webhook.md`) vẫn giữ làm dự phòng.

## Chuẩn bị (một lần mỗi máy)

- Cài: `uv tool install muse-cli` (máy Lead đã có ở `~/.local/bin/muse-cli`).
- Đăng nhập: chủ kênh chạy `muse-cli auth` một lần. Kiểm tra bằng `muse-cli status` (in VM, số phiên, tin chưa đọc). Không dán kết quả `status` hay thông tin tài khoản vào issue (repo public).
- Không cài, không đăng nhập Muse trên máy C (máy render). Phiên đăng nhập chỉ ở máy Lead.
- Windows: đặt `PYTHONIOENCODING=utf-8` trước các lệnh in tiếng Việt (`history`), nếu không sẽ lỗi `cp1252`.

## Dùng cho Long (cách thường dùng)

1. Người viết cảnh soạn `data/long/<topic>/ai_prompts.md`. Mỗi ảnh một mục:
   ```
   ## ai_03.png — chị Hạnh cầm điện thoại buổi sáng
   - Prompt: Painterly illustration, close medium shot of … no text, no numbers, no logos.
   ```
   Có thể thêm một mục `## Phong cách chung` (áp cho mọi ảnh). Prompt viết tiếng Anh, tự đủ nghĩa (agent không đọc được file khác trong repo).
2. Chạy tách (không dùng shell nền của phiên, vì reaper):
   ```
   python scripts/muse_img_request.py <topic>                  # mọi ảnh còn thiếu
   python scripts/muse_img_request.py <topic> --only ai_01,ai_02 --no-import   # vài ảnh, chưa nhập
   ```
   - Mỗi topic dùng một side chat riêng (tạo tự động, id lưu ở `output/long/<topic>/muse_thread.txt`), không lẫn với chat chính của chủ kênh.
   - Ảnh về `motion/hf/assets/long/<topic>/img/ai/ai_NN.png`, rồi script chạy `scripts/ai_img_import.py` để nhập như đường cũ (`img/aiNN.jpg`).
   - Mỗi ảnh khoảng 1 phút (đo 27/11/2026: Muse trả ảnh sau ~30–45 s); bộ 25 ảnh khoảng 30 phút. Script gửi với `send --wait 60` rồi dò `muse-cli files` tới khi có ảnh mới (mặc định tối đa 600 s mỗi ảnh, `--wait`).
   - Hết giờ mà chưa có ảnh: message id được ghi vào `output/long/<topic>/muse_pending.json`; chạy lại lệnh sẽ TẢI LẠI theo id, không gửi lại prompt (không tốn thêm lượt).
3. Lead soát bằng mắt (contact sheet) trước khi dùng: không chữ/số/logo, đúng nhân vật, đúng 16:9. Ảnh hỏng thì xoá file `ai_NN.png` rồi chạy lại `--only ai_NN`.
4. Ảnh khởi đầu clip Flow (thường `ai_01`, `ai_02`) nên tạo trước bằng `--only` để Flow chạy song song với phần còn lại.

## Lệnh thủ công hay dùng

| Việc | Lệnh |
|---|---|
| Gửi một yêu cầu, chờ và tải file | `muse-cli send --thread <id> --wait 900 --download <thư mục> "<prompt>"` |
| Xem tin gần nhất | `PYTHONIOENCODING=utf-8 muse-cli history --thread <id> --limit 5` |
| Liệt kê file agent đã tạo | `muse-cli files` |
| Tải file theo message id | `muse-cli download <message_id> --thread <id> -o <thư mục>` |
| Tạo / lưu trữ side chat | `muse-cli session-start --title "…"`, `muse-cli session-archive <id>` |

## Luật nội dung (giữ như ảnh AI khác)

- Người còn sống: không ảnh AI rõ mặt. Nhân vật lịch sử đã mất: được phỏng dựng rõ mặt theo tư liệu, có nhãn PHỎNG DỰNG (storytelling-guide §15).
- Nhân vật giả định (vd chị Hạnh của CK): giữ đúng một "hồ sơ nhân vật" trong mọi prompt để mặt nhất quán.
- Không chữ, số, logo, mã cổ phiếu trong ảnh. Mô tả video khai nội dung tổng hợp như mọi ảnh AI.

## Sự cố đã gặp

- `history` lỗi `UnicodeEncodeError` → thiếu `PYTHONIOENCODING=utf-8`.
- `send --wait N` báo "no assistant reply" dù ảnh đã có sau ~30 s: muse-cli không nhận ra câu trả lời dạng ảnh. Đừng chờ bằng `--wait`; dò `muse-cli files --thread <id>` (script tự làm).
- `send --wait 0` (fire-and-forget) làm tin bị rơi, agent không nhận được. Luôn gửi với `--wait` ≥ 30.
- Webhook bot nhận 26 prompt mà 75 phút không trả ảnh (CK FTSE, 25/11) → lý do chuyển sang `muse-cli`.
