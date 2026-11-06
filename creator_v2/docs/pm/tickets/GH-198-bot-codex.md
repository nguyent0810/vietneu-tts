# Grok Bot không đọc được ổ D: chép file qua thư mục chung

Chủ kênh báo ngày 06/11: Grok Bot (webhook routine "CLI Trigger") **không đọc hay ghi được ổ D**. `scripts/ai_img_request.py` đang gửi cho bot `prompt_file` và `output_dir` nằm trong repo trên ổ D, nên bot không làm được.

**File được sửa:** `scripts/ai_img_request.py`, `docs/tools/grokbot-webhook.md`, test mới `scripts/test_ai_img_request_stage.py`. Test để trong `scripts/`, vì `tests/` bị AGENTS.md cấm; Lead sẽ chuyển vào sau. Báo cáo ghi vào `docs/pm/tickets/GH-198-bot-report.md`.

**Việc:**
1. Thêm thư mục chung cho bot. Mặc định là `%USERPROFILE%\Downloads\grokbot\<topic>\`; biến môi trường `GROKBOT_SHARE_DIR` ghi đè thư mục gốc này.
2. Trước khi gửi bot:
   - chép `ai_prompts.md` vào `<share>/<topic>/ai_prompts.md`;
   - tạo `<share>/<topic>/out/`;
   - gửi bot hai đường dẫn đó, dạng Windows tuyệt đối.
3. Trong lúc chờ, đếm file trong `<share>/<topic>/out/`. Đủ thì **chép** (không di chuyển) từng ảnh về `motion/hf/assets/long/<topic>/img/ai/`, rồi chạy `ai_img_import.py` như cũ.
   - Ảnh đã có ở đích thì bỏ qua.
   - Chỉ chép file có tên khai trong prompt (`ai_NN.png`).
4. Thêm cờ `--no-send`: không gọi webhook, chỉ chờ và chép về. Dùng khi đã gửi tay rồi.
5. Không in giá trị `GROKBOT_WEBHOOK_URL` hay `GROKBOT_WEBHOOK_KEY`.
6. Cập nhật `docs/tools/grokbot-webhook.md`: bot chỉ đọc và ghi được trong thư mục chung (Downloads), không đọc được ổ D.
7. Test (giả lập `urllib.request.urlopen`, dùng thư mục tạm):
   - file prompt được chép sang thư mục chung;
   - payload chứa đường dẫn thư mục chung;
   - ảnh trong `out/` được chép về đúng chỗ;
   - `--no-send` không gọi webhook.

**Không:** gọi webhook thật, commit, upload. Chạy `python -m pytest scripts/test_ai_img_request_stage.py -q`, ghi kết quả vào báo cáo.
