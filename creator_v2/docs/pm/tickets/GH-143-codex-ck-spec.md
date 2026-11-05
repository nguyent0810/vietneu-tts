# GH-143 · Codex: lắp spec Short `ck-them-10-trieu-gio-bot-mot-mon`

Issue: https://github.com/nguyent0810/vietneu-tts/issues/143. Chủ kênh duyệt sản xuất 04/11, nhắm slot 04/11 19:00.

**Hạn:** 30 phút.

## Đầu vào (Lead đã review)
- `docs/pm/tickets/GH-143-ck-short-lines.json`
  - `lines`, `say`, `frame0`, `beats`, `description`, `sources`, `title_chosen`;
  - Lead đã sửa lời. **Giữ đúng nguyên văn từng câu trong `lines`.**
- `docs/pm/tickets/GH-143-ck-short-report.md`: phép tính và nguồn.
- Mẫu spec CK mới nhất:
  - `data/stier/specs/ck-dien-giam-44-dong-20-nam-v2.json` (cấu trúc cảnh, `acc`, `kicker`, `sub`);
  - `data/stier/specs/ck-p1-thue-5-nam-cong-lai.json`.
- Định dạng spec: docstring `motion/stier/build.py`. Chuẩn: `motion/stier/README.md`.

## Được ghi
- `data/stier/specs/ck-them-10-trieu-gio-bot-mot-mon.json`
- báo cáo `docs/pm/tickets/GH-143-codex-ck-spec-report.md`

**Không:**
- render, TTS;
- upload, enqueue, đổi lịch;
- sửa code hay spec khác;
- commit;
- đọc credentials.

## Việc

### 1. Các trường lấy từ file lines
- `title` = `title_chosen`.
- `short_type` = `"S"`.
- `theme` = `"ck"`.
- `lines`, `say`, `description`, `sources`: lấy nguyên.
- `tags`: 10–14 tag tiếng Việt về lạm phát, CPI, sức mua, tiền gửi, lãi suất thực. Không có tên ngân hàng hay tổ chức tài chính.

### 2. Cảnh theo `beats`
- **Cảnh 0:** chữ đối nghịch "10 TRIỆU ↑" và "GIỎ −1 MÓN", hiện ngay giây 0.
- **D/G:** dùng counter, chart, cards3d, ledger như mẫu.
  - Mọi số tự dựng trên màn hình gắn nhãn **"VÍ DỤ GIẢ ĐỊNH"**.
  - Số CPI thì không gắn nhãn đó; ghi nguồn "CỤC THỐNG KÊ · T10/2026".
  - Số chính xác hiện trên màn hình: 262.725.000đ và 2.725.000đ. Lời đọc vẫn nói số tròn.
- **M:** cảnh clip có `"q"` theo keywords, để `"vid": null`; agent render sẽ điền.
  - Clip không có logo, không có chữ thương hiệu, không biển hiệu cửa hàng.
- **Mix:** `"mix": true`, `music_gain` 0.18, `music_duck` 3, `sfx_gain` 0.36.
- **Look:** chọn qua `motion/stier/looks.py`, khác look của `ck-b1-lai-uu-dai-nam-ngoai` và `ck-e2-bang-tra-quy-khan-cap`.

### 3. Kiểm
Chạy hai lệnh sau và sửa spec đến hết LỖI. **Không được sửa `lines`.** Nếu lỗi chỉ sửa được bằng cách đổi lời thì ghi vào báo cáo rồi dừng.
- `python motion/stier/script_lint.py ck-them-10-trieu-gio-bot-mot-mon`
- `python motion/stier/build.py ck-them-10-trieu-gio-bot-mot-mon --preflight`

## Báo cáo
- Kết quả lint và preflight, dán nguyên dòng kết quả.
- Thời lượng ước tính.
- Look đã chọn.
- Danh sách cảnh, kèm cảnh nào cần clip.

Câu trả lời cuối: tối đa 3 dòng.
