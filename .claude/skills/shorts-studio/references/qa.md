# Cổng QA (Bộ Kiểm Bắt Buộc Trước Khi Báo Xong)

Mọi video short trước khi báo hoàn thành và gửi Lead review phải vượt qua đầy đủ các bước kiểm tra tự động và thẩm định hình ảnh trực quan:

```bash
# Thiết lập môi trường Node 22
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm use 22
cd hyperframes_short/jobs/<id>
```

---

## 1. Bộ kiểm 6 bước bắt buộc cho Thợ

1. **Kiểm tràn chữ (Overflow Check)**:
   - Chạy script kiểm tra bounding box trên headless Chrome: `overflow n = 0`.
   - Bắt buộc kiểm tra `font900 = có` đối với tiêu đề và chữ số chính; không có ký tự bị cắt dấu tiếng Việt (Ấ, Ầ, Ỗ, Ữ, Ự...).
2. **Safe-Zone & Top $\ge 40$**:
   - Đo tại 4 mốc thời gian: 10%, 35%, 65% và khung cuối (100%).
   - Mép trên của thành phần hiển thị phải cách đỉnh ít nhất $40\text{px}$ (`top >= 40`), không đè lên chip danh mục ($y < 110$).
   - Giới hạn trên: Tiêu đề nằm trong $y = 110 - 400$.
   - Giới hạn dưới: Toàn bộ nội dung/CTA không vượt quá $y = 1473\text{px}$; phụ đề nằm dưới $y = 1490$.
3. **Đo khoảng trống dọc & Độ phủ an toàn**:
   - Độ phủ bề ngang: Phủ $\ge 85\%$ bề ngang an toàn ($x$ từ $60 - 940$, $cover \ge 880\text{px}$).
   - Khoảng trống dọc: Đo khoảng cách giữa mép dưới tiêu đề và mép trên nội dung, cũng như giữa nội dung và chân trang. **Không có khoảng trống dọc trống trơn nào $> 250\text{px}$**.
4. **Soát 2 kích thước hiển thị (1080px & 168px)**:
   - Khung gốc $1080\times 1920$: Đầy đủ chi tiết, sắc nét, chuyển động mượt mà.
   - Khung thu nhỏ $168\text{px}$ (mô phỏng thumbnail YouTube Shorts mobile): Tiêu đề và tên hàng/năm sinh chính phải đọc được rõ ràng.
5. **Dựng tờ ảnh kiểm tra (Media Sheet)**:
   - Dựng tờ ảnh chụp khung hình tại 4 mốc thời gian: **25%, 50%, 75% và khung cuối**.
   - Khung cuối phải đứng yên tuyệt đối $\ge 3$ giây (`mean abs difference` giữa khung $-3\text{s}$ và cuối $\le 0.05$).
6. **Mở xem và mô tả thật từng ảnh (Luật 15 & 17)**:
   - **MỞ FILE TỜ ẢNH RA XEM TẬN MẮT**, không dựa vào câu truy vấn prompt.
   - Ghi mô tả chân thực những gì thấy vào báo cáo.
   - FS: Nhân vật phải là người Á Đông / Việt Nam.
   - BUD: Không vẽ mặt Đức Phật bằng code, tranh hoạt hình; ảnh AI có mặt được dùng từ 23/10 nếu không méo (docs/adr/0004); dùng ảnh thật tượng Phật/phù điêu cổ từ bảo tàng CC0 (CMA, Met, AIC) hoặc Commons. Mặt tượng không bị đè chữ, không cắt đầu. Không có đồ đời nay, không biểu tượng tôn giáo khác.

---

## 2. Các lệnh kiểm tra Studio HyperFrames

1. `npx hyperframes@0.8.75 lint --json`: Phải 0 lỗi. Lỗi bất kỳ (vd: `font_family_without_font_face`) làm `check` bỏ qua soát trình duyệt ("0 sample" $\ne$ đạt).
2. `npx hyperframes@0.8.75 check --json --at <giữa mỗi cảnh>`: `ok:true` (runtime 0 lỗi JS, layout 0 lỗi, contrast 0 lỗi).
3. `qa_sheet.jpg` (16 khung): Nhìn tổng quan khung 0 đủ nghĩa, chữ không tràn dải phụ đề, cảnh không bị trống trơ trọi.
4. Kiểm tra tua ngược (với thiết bị mới): `snapshot --at T_muộn,T_sớm` so với `snapshot --at T_sớm`.
5. Âm thanh (`ffprobe` + LUFS):
   - Thời lượng khớp `data-duration`.
   - BUD: Đo âm lượng giọng đọc và BGM, xác nhận chênh lệch đạt đúng $-20.0\text{ dB}$ LUFS; chuông CC0 vang ở giây 0; nhạc giảm nhẹ ở 3s cuối (giữ 40%).
   - FS: Nhạc phương Đông chậm; không có Asian Drums cho bảng tĩnh.
