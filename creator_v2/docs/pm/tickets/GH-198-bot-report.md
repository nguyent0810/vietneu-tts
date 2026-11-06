# Grok Bot đọc file qua thư mục chung: báo cáo

Codex làm, Lead viết lại báo cáo (bản gốc bị lỗi mã hoá do ghi qua PowerShell).

- `scripts/ai_img_request.py`:
  - chép `ai_prompts.md` sang `%USERPROFILE%\Downloads\grokbot\<topic>\`, ghi đè được bằng `GROKBOT_SHARE_DIR`;
  - gửi bot đường dẫn tuyệt đối của file prompt và thư mục `out\`;
  - chờ đủ ảnh, chép đúng các tên khai trong prompt về `motion/hf/assets/long/<topic>/img/ai/` (ảnh đã có thì giữ), rồi chạy `ai_img_import.py`.
- Thêm cờ `--no-send`: chỉ chờ và chép, không gọi webhook.
- `docs/tools/grokbot-webhook.md`: ghi rõ bot không đọc được ổ D.
- Test `tests/test_ai_img_request_stage.py`: 2 passed. Webhook và import được giả lập.
