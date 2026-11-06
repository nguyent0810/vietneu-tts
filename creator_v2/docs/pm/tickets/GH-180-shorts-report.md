# GH-180 · Báo cáo lời Short CK 13–15/11

Brief: `docs/pm/tickets/GH-180-shorts-grok.md`. Lời nằm ở `docs/pm/tickets/GH-180-shorts-lines.md`.

Đã viết 9 lời: 6 loại L (2 cho mỗi Long E5, E6, A2) và 3 loại S. Không tạo spec, không render, không commit, không sửa slot. File `docs/pm/tickets/GH-180-report.md` là báo cáo luật dừng của một GH-180 khác, để nguyên.

## Tiền đề lịch trong brief đã cũ

Brief nói lịch Short CK chỉ kéo tới 12/11. Trong `data/stier/specs/` đã có slot các ngày 13–16/11. Lô này không đụng các slot ấy. Nhóm A/B/C trong file lời chỉ là thứ tự đọc.

Đã có trên lịch:

| Ngày | Slug | Giờ |
|---|---|---|
| 13/11 | ck-e4-so-300-trieu-vuot-han-muc | 17:30 |
| 13/11 | ck-d3-lo-40-can-lai-67 | 19:00 |
| 13/11 | ck-e5-luong-25-trieu-thue-giam-13-lan | 22:00 |
| 14/11 | ck-e4-850-trieu-ngoai-han-muc | 17:30 |
| 14/11 | ck-e5-moc-nop-thue-17-trieu | 19:00 |
| 14/11 | ck-d3-odean-lai-ban-som-lo-giu-lau | 22:00 |
| 15/11 | ck-e5-luong-40-trieu-thue-duoi-4-phan-tram | 17:30 |
| 15/11 | ck-e4-40-ty-do-mot-ngay | 19:00 |
| 15/11 | ck-e6-rut-mot-lan-200-trieu | 22:00 |
| 16/11 | ck-e6-them-5-nam-luong-huu-4-5-trieu | 17:30 |
| 16/11 | ck-a2-10-trieu-muoi-nam-truoc | 19:00 |
| 16/11 | ck-a2-luong-toi-thieu-52-so-voi-10 | 22:00 |

Sáu Short đi kèm ba Long đã lấy các lát dễ thấy nhất: thuế lương 25 triệu giảm khoảng 13 lần, ngưỡng 17,3 triệu, lương 40 triệu còn dưới 4%, rút một lần 200 triệu, thêm 5 năm thì lương hưu khoảng 4,5 triệu, 10 triệu năm 2016, lương tối thiểu tăng khoảng 52% danh nghĩa và khoảng 10% thực. Chín lời mới đi góc khác.

## Cách viết

Đã đọc `docs/pm/2026-10-12-shorts-analysis.md` mục 7, skill `../.claude/skills/shorts-studio/SKILL.md`, và spec đang thắng `ck-lai-kep-lam-phat`, `ck-bao-hiem-350`, `ck-tiet-kiem-so-xanh`. Công thức giữ lại: một con số tiền thật, một quyết định đời thường, câu chốt, không câu hỏi, không kêu gọi xem video dài.

Memory 28/10 trong `docs/codex/long-rules.md` cho phép Short L để lại câu hỏi mà Long trả lời. Brief của ticket này cấm câu hỏi trong lời. Lời theo brief. Cầu sang Long để Codex gắn video liên quan.

Nhãn `"hypo": true` theo ghi chú #173 trong `docs/pm/tickets/GH-173-codex-report.md`. Số luật và số thống kê đã công bố không gắn hypo. Số của người, phiếu lương, mức thưởng do kênh đặt ra thì gắn hypo. Phép chiếu “nếu mức lạm phát giữ nguyên” gắn hypo riêng, và lời nói đó không phải dự báo.

Slug đã soát trong `data/stier/specs/`: chưa có file trùng chín slug mới.

## Đếm

Âm tiết = số token cách khoảng trắng, đã bỏ dấu câu. Tiêu đề = số ký tự Unicode. Hook đều ≤ 9. Lời từ 103 đến 136, trong khoảng 90–140. Tiêu đề từ 48 đến 58 ký tự.

| # | Slug | Loại | Hook | Âm tiết | Tiêu đề |
|---|---|---|---|---|---|
| 1 | ck-e5-thuong-tet-khau-tru | L | 9 | 132 | 55 |
| 2 | ck-e5-mot-dua-tre-mot-to-dang-ky | L | 9 | 136 | 55 |
| 3 | ck-dien-sinh-hoat-bac-mot-1901 | S | 9 | 106 | 53 |
| 4 | ck-e6-bon-trieu-tam-rut-mot-lan | L | 9 | 103 | 51 |
| 5 | ck-e6-tro-cap-540-nghin | L | 9 | 134 | 56 |
| 6 | ck-ho-kinh-doanh-duoi-mot-ty | S | 9 | 123 | 57 |
| 7 | ck-a2-mot-nua-sau-muoi-sau-nam | L | 9 | 114 | 54 |
| 8 | ck-a2-thang-chin-nam-phay | L | 8 | 105 | 48 |
| 9 | ck-tran-tro-cap-that-nghiep-26-trieu | S | 9 | 117 | 58 |

## Phép tính đã kiểm lại

Thưởng Tết, ví dụ giả định, cùng số trong `data/long/ck-e5-thue-tncn-2026/script.md`:

- Bảo hiểm tháng: 25.000.000 × 10,5% = 2.625.000.
- Tháng có thưởng: 75.000.000 − 2.625.000 − 21.700.000 = 50.675.000. Thuế 6.635.000.
- Cả năm: thu nhập tính thuế 58.100.000 × 5% = 2.905.000.
- Đã khấu trừ: 33.750 × 11 + 6.635.000 = 7.006.250. Chênh 4.101.250. Lời nói “khoảng bảy triệu” và “khoảng bốn triệu một”.

Một người phụ thuộc, cùng ví dụ: chồng không được giảm trừ cho con thì thuế tháng 343.750. Chênh cả năm 3.720.000. Vợ lương 15 triệu sau bảo hiểm còn 13.425.000, dưới 15,5 triệu.

Một nửa sức mua: ln(2) / ln(1,0452) ≈ 15,68 năm. Cách nhẩm 70 / 4,52 ≈ 15,49 năm. Lời tách hai cách này, và nói phần mười sáu năm chỉ đúng nếu 4,52% lặp lại.

Trần trợ cấp vùng một: 5 × 5.310.000 = 26.550.000.

Điện: 3.844 / 1.901 ≈ 2,02, nên lời nói “khoảng gấp đôi”.

Rút bảo hiểm một lần: 1,24 / 4,84 ≈ 25,6%. Bài Thanh Niên ghi thêm 27,7%. 4,84 × 0,277 ≈ 1,34 triệu, không khớp 1,24 triệu. Lời chỉ đọc hai số người và “khoảng một phần tư”.

## Nguồn đã mở trong phiên này

- Nghị định 141/2026, ngưỡng 1 tỷ, hóa đơn, khoảng 2.556.042 hộ: trang Chính phủ in ngày 06/05/2026.
- Giá điện sinh hoạt, SGGP, Quyết định 2892, 1.901 và 3.844 đồng/kWh.
- Bản tin CPI tháng 9/2026 của NSO, tiếng Anh: tháng 9 +5,08% cùng kỳ, 9 tháng +4,52%, lõi +4,26%.
- Dân trí, cách tính trợ cấp thất nghiệp 2026: 60% và trần 5 lần lương tối thiểu vùng.
- Nghị định 293/2025, toàn văn trên trang Chính phủ: vùng I 5.310.000 từ 01/01/2026. Lương giờ vùng III trên trang này là 20.000, không dùng 19.900 từ một đoạn tóm tắt tìm kiếm.
- Thanh Niên 04/06/2023: khoảng 4,84 triệu người và 1,24 triệu người quay lại.
- Báo Chính phủ, chính sách từ tháng 10/2026: trợ cấp hưu trí xã hội 500.000 lên 540.000 từ 05/10/2026.
- Nghị định 176/2025 trên trang Chính phủ: đủ 75 tuổi, điều kiện lương hưu, hộ nghèo từ đủ 70 đến dưới 75, mức khi ấy 500.000.
- Luật 109, Điều 10, trang Chính phủ: giảm trừ 15,5 và 6,2; mỗi người phụ thuộc chỉ tính một lần vào một người nộp thuế.
- Tạp chí Công Thương 15/10/2026: biểu 5 bậc đúng các mốc 10 / 30 / 60 / 100 triệu.
- Luật Việt Nam, tỷ lệ đóng 2026: người lao động 8% + 1,5% + tối đa 1%, bảng cộng 10,5%.

URL đầy đủ nằm cạnh từng bài trong file lời.

## Phần cố ý không đưa vào lời

- Nhóm hàng CPI tháng 9 (xăng, đi lại, thuê nhà, giỏ của anh Tuấn và chị Mai). Trang NSO đã mở không có bảng nhóm. File PDF tiếng Việt của Cục không mở.
- Lạm phát 2008. API World Bank lỗi DNS trong phiên nghiên cứu, không lấy số ấy.
- Bậc điện ở giữa. Ảnh SGGP không đọc được thành chữ. Bài Đời sống pháp luật chỉ trả về tiêu đề. Bảng Znews lệch với chính văn bài đó, bỏ.
- Tỷ lệ 27,7% trên Thanh Niên, vì không khớp hai số người của cùng bài.
- Việc năm đóng bảo hiểm về số không sau khi rút một lần. Điều 5 khoản 3 Luật 41 không mở trong phiên này. Long có câu ấy. Short không đọc.
- Mốc thu nhập người phụ thuộc 1 triệu lên 3 triệu. Trang Luật 109 đã mở để mức ấy cho Bộ Tài chính. Bài Tạp chí Công Thương ghi 3 triệu. Hai chỗ không cùng kiểu căn cứ, nên không đọc.
- Phần miễn thuế thu nhập doanh nghiệp trong Nghị định 141. Đó là việc của doanh nghiệp, không phải hộ.
- Mức chuẩn trợ giúp xã hội 360.000 lên 540.000. Cùng nghị định với trợ cấp hưu trí xã hội, nhưng là khoản khác.
- Số tháng được hưởng trợ cấp thất nghiệp. Để trên màn hình nếu Codex cần, không thành ý thứ hai.
- VnEconomy lỗi DNS. Lao Động không lấy được nội dung. Không dùng “hơn 4,8 triệu” và “gần 1,3 triệu” của các trang ấy cho lời Short, dù Long đang dùng cách làm tròn đó.

## Bài kề, để Codex khỏi làm trùng

- `ck-quy-tac-72`: cùng kiểu nhẩm số năm, khác câu hỏi. Bài mới chỉ nói sức mua còn một nửa nếu 4,52% lặp lại.
- `ck-lam-phat-100-trieu`: cùng mức 4,52% trên 100 triệu. Bài mới không tính một số tiền gửi.
- `ck-lai-kep-lam-phat`: 3% và khoảng 23 năm. Không kể lại.
- `ck-dien-giam-44-dong`: đợt giảm giá bình quân. Bài mới nói bậc lũy tiến.
- Long `ck-f1-tro-cap-that-nghiep` hẹn 20:00 ngày 18/11 và đã có trần 26,55 triệu trong chương trần bốn vùng. Short trần vùng một vẫn là loại S. Gắn video liên quan ở Studio, không viết lời mời.

## Chưa làm

Codex lắp spec, dựng hình, render, commit, và xếp giờ. Chín slug chưa có trong `data/stier/specs/`. Không trường `slot` nào được ghi.
