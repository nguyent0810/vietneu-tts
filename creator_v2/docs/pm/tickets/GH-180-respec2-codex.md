# GH-180 vòng 3: 9 Short CK phải qua luật phối cảnh

Lead trả lời các vướng mắc trong `docs/pm/tickets/GH-180-respec-report.md`:
- **`cards3d`, `chart`, `board` là loại cảnh hợp lệ.** Bảng 19 loại trong README đã cũ. Bằng chứng: spec mẫu `ck-e5-luong-25-trieu-thue-giam-13-lan.json` dùng chúng và đã đăng. Engine có `chart.js`, cards3d trong `casefile.js`.
- **Luật mix của preflight** là luật thật, phải đạt:
  - ≥ 1 cảnh ảnh hoặc video cộng đồng;
  - ≥ 1 cảnh sơ đồ (`board`, `cards3d` hoặc `map`);
  - không loại cảnh nào chiếm quá 60% thời lượng.
- **Ảnh/video:** mỗi bài **đúng 1–2 cảnh ảnh hoặc clip**, và không dùng cùng một file cho 2 bài. Nguồn:
  - ảnh AI chủ đề tiền bạc trong kho chung: `output/asset_library/lib198/` và `lib198b/`, tag `ck` (`python ../library/tools/assets.py find`), dùng như ảnh AI, `credit: false`;
  - clip CK đã dùng cho Short khác (xem cách spec mẫu khai báo clip và ảnh cộng đồng).

  Chọn 9 file khác nhau, hợp nội dung từng bài: hóa đơn điện, tiền lương, bảo hiểm, cửa hàng…
- **Số chính cỡ lớn:** card trong `cards3d`, `chart` (bars) để so sánh, `counter` hoặc `slam` cho số chốt. Xem hình mẫu `output/stier/ck-e5-luong-25-trieu-thue-giam-13-lan/final_sheet.jpg`.

Lời đọc giữ nguyên. Giữ `hypo`. Chạy `python motion/stier/build.py --preflight <slug>` cho cả 9 **đến khi OK**. Sửa bằng Python UTF-8 và chạy lệnh kiểm mất dấu. Không render, không commit.

**Báo cáo** `docs/pm/tickets/GH-180-respec2-report.md`: mỗi bài ghi loại cảnh, file ảnh hoặc clip, kết quả preflight.
