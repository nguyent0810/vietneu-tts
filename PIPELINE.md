# Pipeline tự động hoá TTS theo chủ đề

Tài liệu này mô tả bộ script tự build thêm trên VieNeu-TTS gốc để tự động
hoá quy trình: quét nội dung trên Google Drive theo chủ đề → render audio
(cắt tự nhiên, QA, retry) → xuất kèm phụ đề (.srt) + manifest (.json) →
upload lại Drive.

## Cấu trúc Drive

```
TTS-Input/{Chủ đề}/Long/*.txt         # mỗi file = 1 audio dài
TTS-Input/{Chủ đề}/Long/processed/    # input đã xử lý xong (tự chuyển vào)
TTS-Input/{Chủ đề}/Short/*.txt        # mỗi file chứa nhiều đoạn "*** N"
TTS-Input/{Chủ đề}/Short/processed/

TTS-Output/{Chủ đề}/Long/{tên}.wav (+.srt +.json)
TTS-Output/{Chủ đề}/Short/processed/{tên}/{N}_{tên}.wav (+.srt +.json)
```

Chủ đề mới tự được phát hiện khi tạo folder con trong `TTS-Input/` — không
cần sửa code.

## Chạy

```bash
./run.sh                          # mọi chủ đề, cả Long + Short
./run.sh --long                   # chỉ Long/
./run.sh --short                  # chỉ Short/
./run.sh --topic "Phật giáo"      # chỉ 1 chủ đề
./run.sh --voice Tuyen            # ép 1 giọng cho MỌI chủ đề
```

Giọng theo chủ đề cấu hình trong `topic_voices.json` — sửa file này khi cần
đổi giọng hoặc thêm chủ đề, không cần sửa code Python.

## Kiểm tra & bảo trì

```bash
./smoke_test.sh                   # test nhanh toàn bộ pipeline còn hoạt động đúng
./cleanup_local.sh --dry-run      # xem local cache/output cũ sẽ bị dọn (mặc định 14 ngày)
./cleanup_local.sh                # dọn thật
```

## Thiết lập cần làm 1 lần

### 1. rclone + Google Drive

```bash
brew install rclone
rclone config   # tạo remote tên "gdrive", chọn Google Drive
```

### 2. (Khuyến nghị) Tạo client_id riêng cho rclone

rclone mặc định dùng client_id dùng chung — sẽ ngừng hoạt động trong 2026.
Nên tạo client_id riêng để không bị gián đoạn:

1. Vào [Google Cloud Console](https://console.cloud.google.com/) → tạo project mới (hoặc dùng project có sẵn).
2. Vào **APIs & Services → Library**, bật **Google Drive API**.
3. Vào **APIs & Services → OAuth consent screen** → chọn **External**, điền thông tin tối thiểu (tên app, email), thêm chính email của bạn vào phần **Test users**.
4. Vào **APIs & Services → Credentials → Create Credentials → OAuth client ID** → chọn loại **Desktop app**.
5. Copy `Client ID` và `Client secret` vừa tạo.
6. Cập nhật vào rclone:
   ```bash
   rclone config update gdrive client_id="CLIENT_ID_CỦA_BẠN" client_secret="CLIENT_SECRET_CỦA_BẠN"
   ```
7. Chạy `rclone lsd gdrive:` để xác nhận vẫn kết nối được (có thể cần đăng nhập lại 1 lần).

### 3. HF_TOKEN (khuyến nghị)

Tạo token tại https://huggingface.co/settings/tokens (loại "Read" là đủ),
rồi tạo file `.env` ở thư mục gốc:

```
HF_TOKEN=hf_xxxxxxxxxxxx
```

`run.sh` tự đọc file này. Không có token vẫn chạy được (chế độ ẩn danh) —
chỉ dễ dính rate limit khi chạy nhiều/tần suất cao.

### 4. GitHub token cho tích hợp tool khác

Copy `.github_integration.env.example` thành `.github_integration.env`
(đã có sẵn ở thư mục gốc), điền:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
CONTENT_TOOL_REPO=https://github.com/<user>/<content-tool-repo>
VIDEO_TOOL_REPO=https://github.com/<user>/<video-tool-repo>
```

File này đã nằm trong `.gitignore`, không bị commit. Nên tạo
**fine-grained personal access token** (không phải classic token) tại
https://github.com/settings/personal-access-tokens/new, chỉ cấp quyền
"Contents: Read-only" cho đúng các repo cần tích hợp, có ngày hết hạn.

## Kiến trúc code

| File | Vai trò |
|---|---|
| `render_engine.py` | Lõi render — chunk tự nhiên, QA, retry, xuất srt/json. `RenderSession` giữ model đã load, tái dùng cho nhiều lần render (tránh load lại ~6-9s/lần). |
| `render_natural.py` | CLI đứng riêng, render 1 file — dùng khi test tay hoặc chạy 1 file độc lập. |
| `drive_utils.py` | Helper rclone dùng chung, có retry/backoff cho lỗi mạng thoáng qua. |
| `process_drive_queue.py` | Xử lý 1 folder kiểu "Long". |
| `process_short_queue.py` | Xử lý 1 folder kiểu "Short" (tách theo `*** N`). |
| `process_topics.py` | Entry point chính — quét chủ đề, share `RenderSession` theo giọng, khoá chống chạy chồng (`.process_topics.lock`). |
| `topic_voices.json` | Mapping chủ đề → giọng. |
| `run.sh` | Wrapper: kiểm tra điều kiện, log, gọi `process_topics.py`. |
| `smoke_test.sh` | Test nhanh end-to-end (tạo chủ đề tạm, render, verify, dọn dẹp). |
| `cleanup_local.sh` | Dọn local cache/output cũ theo thời gian. |

## Ghi chú cho tích hợp tương lai

- Mỗi file `.wav` đi kèm `.srt` (phụ đề chính xác 100% vì audio sinh ra từ
  chính text đó, không cần ASR) và `.json` (manifest: giọng, thời lượng,
  timing từng câu, chủ đề, nguồn) — tool video/YouTube uploader sau này đọc
  trực tiếp các file này, không cần tự suy luận metadata từ tên file.
- Ngưỡng QA (`SEC_PER_CHAR`, `DURATION_RATIO_THRESHOLD`,
  `INTERNAL_SILENCE_THRESHOLD` trong `render_engine.py`) được tinh chỉnh cho
  giọng/nội dung tiếng Việt đã test — nếu tỷ lệ retry tăng bất thường khi có
  nội dung/giọng mới, nên xem lại các ngưỡng này.
