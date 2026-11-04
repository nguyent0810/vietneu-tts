# YCV-ju9q · M1: render, final, khung soát và thumbnail cho `mim-jobs-1985` (agy hoặc Grok)

Claude đã duyệt cảnh. `long_gate` ra **ĐẠT** và `coverage_lint` đo được 21,77% chỉ chữ. HTML của 9 chương đã có. Theo luật kênh, Long **không render bản nháp**: render thẳng bản thật.

## Được ghi

- `output/long/mim-jobs-1985/**`
- `motion/long/thumbs/mim-jobs-1985_t1.html` và `mim-jobs-1985_t2.html`
- báo cáo `docs/pm/tickets/YCV-ju9q-M1-render-report.md`

Không sửa `data/long/**`, engine hay code. Không đăng, không commit, không gọi bot sinh ảnh.

## Việc

1. **Render.**
   - Chạy `python motion/long/build_long.py mim-jobs-1985 render` cho đủ 9 chương. Lệnh chạy lâu: để chạy hết, không ngắt.
   - Khi xong, chạy `python motion/long/build_long.py mim-jobs-1985 final` để ra `final.mp4`.
2. **Khung soát.**
   - Dùng ffmpeg trích từ `final.mp4` mỗi 5 giây một khung.
   - Ghép thành `output/long/mim-jobs-1985/qa_final_sheet.jpg`: lưới 8 cột, mỗi khung 320 px, ghi mốc thời gian dưới khung.
   - Tự xem sheet và ghi vào báo cáo mọi lỗi thấy được:
     - chữ tràn khung hoặc bị cắt;
     - màn trống hoặc đen quá 1 giây;
     - mặt người bị cắt trong ảnh dọc (`jobs84`, `mac84`, `sculley06` chưa có `focus`);
     - logo hoặc chữ đọc được trong clip;
     - ảnh AI bị cắt mất chủ thể.
   - Lỗi nào cũng ghi kèm mốc thời gian.
3. **Thumbnail.**
   - Chép mẫu `motion/long/thumbs/mim-macintosh-1984_t1.html` thành hai bản:
     - **t1:** chữ lớn "1985 → 1997", nối bằng một mũi tên vòng; dòng nhỏ "BỊ GẠT KHỎI APPLE".
     - **t2:** chữ lớn "BỊ GẠT RA", dòng nhỏ "RỒI QUAY LẠI".
   - Mỗi thumbnail chỉ 3–6 chữ, không ghi "VÍ DỤ GIẢ ĐỊNH".
   - Nền dùng ảnh `output/long/mim-jobs-1985/img/ai01.jpg` hoặc `ai06.jpg` (người quay lưng). Không dùng mặt Jobs. Không dùng logo Apple.
   - Chạy `python motion/long/thumb.py mim-jobs-1985 t1 t2`. Kiểm `t1_small.jpg` và `t2_small.jpg`: ở cỡ 320 px chữ vẫn phải đọc được.
4. **Báo cáo** gồm:
   - thời lượng `final.mp4`;
   - danh sách lỗi theo mốc thời gian;
   - đường dẫn tới sheet và hai thumbnail.
