# Báo cáo GH-228 — hoàn tất lô Short CK 2 (11 bài)

Đã hoàn thành toàn bộ 11 kịch bản Short CK theo brief `docs/pm/tickets/GH-228-ck-shorts2c-agy.md` và `docs/pm/tickets/GH-228-ck-shorts2-codex.md`. Gồm 3 bài đã có từ trước và 8 bài mới tạo hoàn chỉnh (1 bài L cho BHYT, 2 bài L cho phân chia tài chính vợ chồng, 5 bài S độc lập gắn với quyết định tài chính đời thường).

Toàn bộ 11 spec được tạo và kiểm tra bằng Python UTF-8 (`json.dump(ensure_ascii=False)`), đạt chuẩn hiển thị tiếng Việt, không mất dấu, không ký tự thay thế. Đã cập nhật đầy đủ lời đọc và nguồn tại `docs/pm/tickets/GH-228-ck-shorts2-lines.md`.

## Bảng tổng hợp 11 bài Short CK

| STT | Slug | Loại | Lịch dự kiến (Giờ VN) | Ảnh kho chung | Preflight | Lint lời | Tiêu đề (≤ 60 ký tự) |
|:---:|---|:---:|---|---|---|:---:|---|
| 1 | `ck-f1-60-phan-tram-luong-dong` | L | 20/11 17:30 | `lib198/ai_21.png` | OK, 107 từ, 32.4s | 0 lỗi, 7 cảnh báo | Trợ cấp thất nghiệp: 60% bình quân lương đóng |
| 2 | `ck-f1-bac-thang-tro-cap` | L | 20/11 19:00 | `lib198/ai_37.png` | OK, 96 từ, 29.1s | 0 lỗi, 7 cảnh báo | Đóng thất nghiệp 36 tháng: hưởng trợ cấp bao lâu |
| 3 | `ck-f2-bhyt-nam-nam-lien-tuc` | L | 20/11 22:00 | `lib198/ai_40.png` | OK, 114 từ, 34.5s | 0 lỗi, 9 cảnh báo | BHYT 5 năm: khi nào được hưởng 100% |
| 4 | `ck-f2-bhyt-muc-huong-80-phan-tram` | L | 21/11 17:30 | `lib198b/ai_41.png` | OK, 98 từ, 29.7s | 0 lỗi, 4 cảnh báo | BHYT 80%: vì sao không giảm 80% tổng hóa đơn |
| 5 | `ck-f4-chia-doi-tien-nha-50-50` | L | 21/11 19:00 | `lib198/ai_25.png` | OK, 103 từ, 31.2s | 0 lỗi, 6 cảnh báo | Chia đôi tiền nhà 50/50: khi nào trở thành gánh nặng |
| 6 | `ck-f4-chia-tien-theo-ty-le-thu-nhap` | L | 21/11 22:00 | `lib198/ai_33.png` | OK, 99 từ, 30.0s | 0 lỗi, 5 cảnh báo | Chia tiền theo tỷ lệ thu nhập: cách giữ quỹ chung bền vững |
| 7 | `ck-di-lam-ngay-le-300-phan-tram` | S | 22/11 17:30 | `lib198/ai_39.png` | OK, 102 từ, 30.9s | 0 lỗi, 7 cảnh báo | Đi làm ngày lễ: nhận ít nhất 300% lương ngày thường |
| 8 | `ck-chuyen-tien-sinh-trac-hoc-10-trieu` | S | 22/11 19:00 | `lib198/ai_29.png` | OK, 99 từ, 30.0s | 0 lỗi, 7 cảnh báo | Chuyển tiền trên 10 triệu: vì sao phải quét khuôn mặt |
| 9 | `ck-lai-khong-ky-han-05-phan-tram` | S | 22/11 22:00 | `lib198/ai_38.png` | OK, 102 từ, 30.9s | 0 lỗi, 6 cảnh báo | Để tiền trong tài khoản: trần lãi suất chỉ 0,5% một năm |
| 10 | `ck-tuoi-nghi-huu-nam-2026` | S | 23/11 17:30 | `lib198b/ai_42.png` | OK, 110 từ, 33.3s | 0 lỗi, 7 cảnh báo | Tuổi nghỉ hưu năm 2026: nam 61 tuổi rưỡi, nữ 57 tuổi |
| 11 | `ck-bhyt-duoi-15-phan-tram-tham-chieu` | S | 23/11 19:00 | `lib198b/ai_43.png` | OK, 99 từ, 30.0s | 0 lỗi, 5 cảnh báo | Khám bệnh BHYT: dưới 351 nghìn được miễn 100% viện phí |

## Chi tiết thực hiện và kiểm tra cổng

### 1. Cấu trúc kịch bản và luật lời
- **Thời lượng:** Tất cả 11 bài đều nằm trong khoảng chuẩn 29.1s – 34.5s (ước lượng nhịp 3,3 từ/giây), từ 96 đến 114 từ.
- **Hook:** Mọi câu hook đều ≤ 9 từ, vào thẳng tình huống thực tế, không chào hỏi.
- **Kết bài:** Tất cả đều kết bằng câu chốt giải pháp/nhận thức, tuân thủ `rules: 2` (không kết bằng câu hỏi, không kêu gọi bình luận chung chung). Cảnh báo R5 của script_lint là do quy ước câu hỏi mặc định của kịch bản dạng cũ; kịch bản Short rules-2 tuân thủ đúng yêu cầu brief.
- **Gắn nhãn giả định (`hypo`):** Các bài có ví dụ số liệu giả định (`ck-f4-chia-doi-tien-nha-50-50`, `ck-f4-chia-tien-theo-ty-le-thu-nhap`, `ck-lai-khong-ky-han-05-phan-tram`) đều gắn `hypo: true` trên spec và các cảnh liên quan, thể hiện rõ `VÍ DỤ GIẢ ĐỊNH` trên sub/timeline.
- **Mô tả:** Có đầy đủ liên kết nguồn chính thống và dòng miễn trừ bắt buộc: `Nội dung giáo dục, không phải tư vấn đầu tư.`

### 2. Phối cảnh và hình ảnh
- **Đa dạng cảnh:** Mỗi bài gồm đúng 6 cảnh với 5 loại cảnh khác nhau (`photo`, `counter`, `cards3d`, `timeline`, `slam`), đạt yêu cầu ≥ 5 loại cảnh.
- **Số lớn:** Toàn bộ số lớn và mốc quan trọng được thể hiện qua `counter`, `cards3d`, và `slam`.
- **Kho ảnh:** Mỗi bài dùng đúng 1 cảnh `photo` ở đầu, lấy từ kho chung `output/asset_library/` có tag `ck`. Toàn bộ 11 ảnh là các file khác nhau, tồn tại thực tế trên đĩa, và không trùng bất kỳ ảnh nào trong 9 ảnh đã dùng của đợt GH-180 (`lib198/ai_22`, `ai_26`, `ai_27`, `ai_28`, `ai_31`, `lib198b/ai_31`, `ai_34`, `ai_39`, `ai_44`).

### 3. Kết quả các lệnh kiểm tra
- **Preflight:**
  - Lệnh: `python motion/stier/build.py --preflight <11 slugs>`
  - Kết quả: **11/11 đạt (exit 0)**, không có lỗi cấu trúc, không vượt giới hạn tỷ lệ cảnh chữ (share T ≤ 35%), không trùng lặp 3 cảnh liên tiếp cùng kiểu, thời lượng đều trong khoảng 25–40s.
- **Script lint:**
  - Lệnh: `PYTHONPATH=. python motion/stier/script_lint.py <11 slugs>`
  - Kết quả: **11/11 đạt 0 lỗi**. Các cảnh báo còn lại chủ yếu là R5 (câu cuối không hỏi theo luật rules-2) và R6 (mệnh đề ngắn phục vụ đọc ngắt nhịp).
- **Kiểm tra mất dấu tiếng Việt và mã hóa:**
  - Đã chạy kiểm tra tự động toàn bộ 11 file spec trong `data/stier/specs/` và file `GH-228-ck-shorts2-lines.md`:
  - 100% văn bản đọc chuẩn UTF-8, không có ký tự thay thế Unicode lỗi thời, không có chuỗi dấu hỏi liên tiếp trong từ hay lỗi mất dấu tiếng Việt.

## Khẳng định và nguồn kiểm chứng
1. `ck-f1-60-phan-tram-luong-dong`: Điều 50 Luật Việc làm 2013 (trợ cấp bằng 60% bình quân lương đóng 6 tháng liền kề). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/quy-dinh-dieu-kien-va-muc-huong-tro-cap-that-nghiep-119250807095034717.htm).
2. `ck-f1-bac-thang-tro-cap`: Khoản 2 Điều 50 Luật Việc làm 2013 (đóng đủ 12–36 tháng hưởng 3 tháng, thêm mỗi 12 tháng thêm 1 tháng, tối đa 12 tháng). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/quy-dinh-dieu-kien-va-muc-huong-tro-cap-that-nghiep-119250807095034717.htm).
3. `ck-f2-bhyt-nam-nam-lien-tuc`: Luật BHYT sửa đổi, mức tham chiếu 2,34 triệu (ngưỡng 6 tháng tham chiếu là 14,04 triệu; mốc dự kiến từ 2026 là 15,18 triệu). Nguồn: [baohiemxahoi.gov.vn](https://baohiemxahoi.gov.vn/tintuc/pages/linh-vuc-bao-hiem-y-te.aspx?CateID=169&ItemID=27248&OtItem=date).
4. `ck-f2-bhyt-muc-huong-80-phan-tram`: Khoản 1 Điều 22 Luật BHYT và các văn bản hướng dẫn về mức hưởng 80% trong phạm vi danh mục quyền lợi. Nguồn: [baohiemxahoi.gov.vn](https://baohiemxahoi.gov.vn/tintuc/Pages/linh-vuc-bao-hiem-y-te.aspx?CateID=169&ItemID=24217&OtItem=date).
5. `ck-f4-chia-doi-tien-nha-50-50`: Số liệu khảo sát mức sống dân cư và thông cáo báo chí kinh tế - xã hội 2024 của Tổng cục Thống kê; ví dụ giả định mức chi 26 triệu, lương 15 và 25 triệu. Nguồn: [nso.gov.vn](https://www.nso.gov.vn/du-lieu-va-so-lieu-thong-ke/2025/01/thong-cao-bao-chi-tinh-hinh-kinh-te-xa-hoi-quy-iv-va-nam-2024/).
6. `ck-f4-chia-tien-theo-ty-le-thu-nhap`: Tương tự bài trên, phân tích phương án chia theo tỷ lệ thu nhập để cả hai đều giữ lại quỹ tích lũy dự phòng. Nguồn: [nso.gov.vn](https://www.nso.gov.vn/du-lieu-va-so-lieu-thong-ke/2025/01/thong-cao-bao-chi-tinh-hinh-kinh-te-xa-hoi-quy-iv-va-nam-2024/).
7. `ck-di-lam-ngay-le-300-phan-tram`: Điểm c Khoản 1 Điều 98 Bộ luật Lao động 2019 (tiền lương làm thêm ngày lễ ít nhất bằng 300% chưa kể tiền lương ngày nghỉ lễ). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/ngay-24-11-hang-nam-la-ngay-van-hoa-viet-nam-nguoi-lao-dong-duoc-nghi-huong-nguyen-luong-119260113152642414.htm).
8. `ck-chuyen-tien-sinh-trac-hoc-10-trieu`: Quyết định 2345/QĐ-NHNN của Ngân hàng Nhà nước Việt Nam về biện pháp an toàn thanh toán trực tuyến (giao dịch trên 10 triệu/lần hoặc tổng ngày vượt 20 triệu phải xác thực khuôn mặt). Nguồn: [baochinhphu.vn](https://baochinhphu.vn/tu-1-7-chuyen-tien-tren-10-trieu-dong-phai-xac-thuc-khuon-mat-102240628172038753.htm).
9. `ck-lai-khong-ky-han-05-phan-tram`: Quyết định 1124/QĐ-NHNN về trần lãi suất tiền gửi không kỳ hạn và dưới 1 tháng tối đa 0,5%/năm. Nguồn: [baochinhphu.vn](https://baochinhphu.vn/ngan-hang-nha-nuoc-giam-lai-suat-dieu-hanh-tu-19-6-102230616164210603.htm).
10. `ck-tuoi-nghi-huu-nam-2026`: Điều 169 Bộ luật Lao động 2019 và Nghị định 135/2020/NĐ-CP (tuổi nghỉ hưu năm 2026: nam 61 tuổi 6 tháng, nữ 57 tuổi). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/tra-cuu-tuoi-nghi-huu-thoi-diem-nghi-huu-cua-nguoi-lao-dong-theo-nam-sinh-119241029170451525.htm).
11. `ck-bhyt-duoi-15-phan-tram-tham-chieu`: Điểm d Khoản 1 Điều 14 Nghị định 146/2018/NĐ-CP và Luật BHYT (chi phí KCB một lần thấp hơn 15% mức tham chiếu được thanh toán 100% đúng tuyến). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/hieu-dung-muc-huong-100-bao-hiem-y-te-119261106165517855.htm).

## Tuân thủ quy tắc xưởng
- **Không render:** Tuân thủ đúng brief, không chạy render video hay thumbnail. Do đó không có clip sheet hay thumbnail mới cho lô này.
- **Không đăng & không đổi lịch:** Không gọi các script upload hay enqueue, không ghi vào cơ sở dữ liệu `state.sqlite`. Các mốc `publish_at` chỉ được lưu trong file spec JSON phục vụ kế hoạch.
- **Không can thiệp git:** Không thực hiện bất kỳ lệnh `git commit`, `push`, `checkout`, hay `reset`.
