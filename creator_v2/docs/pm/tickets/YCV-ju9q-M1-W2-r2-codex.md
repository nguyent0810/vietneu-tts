# YCV-ju9q · M1 W2 vòng 2: đưa tỉ lệ chỉ chữ về ≤ 22%, rồi html cho `mim-jobs-1985`

Claude đã chạy xong TTS cho cả 9 chương. Mọi file `output/long/mim-jobs-1985/chNN/timing.json` đã có, tổng 8,91 phút.

## Số đo hiện tại

`python motion/long/coverage_lint.py mim-jobs-1985`:

| Chỉ số | Hiện tại | Ngưỡng |
|---|---|---|
| Thời lượng chỉ chữ | 29,66% (158 s / 534 s) | ≤ 22% |
| Chuỗi chỉ chữ dài nhất | 8,16 s | ≤ 17 s, đã đạt |

Cột đầu **TRƯỢT**. Muốn qua cần đổi khoảng 40 giây cảnh chỉ chữ thành cảnh có hình.

`python motion/long/scene_rules.py mim-jobs-1985` ra 2 cảnh báo lặp, 0 đề xuất. Xem `output/long/mim-jobs-1985/scene_rules.json` và áp nếu hợp lý.

## Việc cần làm

1. Liệt kê các cảnh chỉ chữ (`kinetic`, `slam`, `question`, `quote`, `myth`, `brand` không có `vid`/`bg`/`img`), xếp theo thời lượng giảm dần. Ghi danh sách này vào báo cáo.
2. Đổi từ cảnh dài nhất trở xuống, mỗi cảnh chọn **một** trong ba cách:
   - **Thêm clip nền:** gắn `vid` b-roll Pexels đúng nghĩa câu. Ví dụ: văn phòng hoặc phòng họp thập niên 80, bàn phím, máy tính cũ, hành lang công ty, tòa nhà, rạp chiếu phim. Giữ chữ phía trên, thêm `veil` để chữ còn đọc được.
   - **Chuyển thành `photo`/`print`:** dùng ảnh tư liệu sẵn có trong `IMGS` hoặc ảnh AI `ai01`–`ai06`, kèm `kin` cho chữ.
   - **Chuyển thành đồ họa có nghĩa:** `timeline`, `counter`, `bars`, `ledger`.
   - Không được chèn cảnh đệm vô nghĩa.
3. Tải clip: `python motion/long/pexels.py search|get mim-jobs-1985 …`.
   - Clip không được lộ logo, chữ đọc được hay mặt người nổi tiếng.
   - Không dùng clip giả làm Apple hay Jobs.
4. Chạy lần lượt:
   - `gen_scenes.py`
   - `script_lines.py`
   - `coverage_lint.py`: lặp lại bước 2 tới khi chỉ chữ ≤ 22%.
   - `scene_rules.py`
5. Chạy `python motion/long/build_long.py mim-jobs-1985 html`.
   - Phải in đủ 9 dòng `chNN: … -> …html`, không có `Error`.
   - Nếu hỏng vì sandbox (`EPERM`/`spawn`), ghi lại lỗi rồi dừng bước này.
6. Chạy `python motion/long/clip_sheet.py mim-jobs-1985`. Mở `qa_clips.jpg`, xem từng clip, thay clip lỗi.
7. Chạy `python scripts/long_gate.py mim-jobs-1985 --min-syl 1900`. Phải ra **ĐẠT**; nếu lỗi duy nhất là thiếu ảnh AI thì chấp nhận.

**Không** sửa `script.md`, không chạy lại TTS, không render, không gọi bot ảnh, không sửa `ai_prompts.md`.

Có một sửa nhỏ của Claude trong `gen_scenes.py`: đã bỏ 2 dòng trong `youtube.more` / `video_credits`. Giữ nguyên hai chỗ đó.

## Báo cáo

Ghi đè `docs/pm/tickets/YCV-ju9q-M1-W2-ket-qua.md`, thêm mục **"Vòng 2"**, gồm:

- danh sách cảnh đã đổi: chương, câu, cách đổi, id clip;
- `coverage_lint` trước và sau;
- `scene_rules` đã áp gì;
- kết quả `html`, `clip_sheet` và `long_gate`.
