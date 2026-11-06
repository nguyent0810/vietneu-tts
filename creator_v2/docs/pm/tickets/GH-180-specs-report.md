# GH-180 · Báo cáo lắp spec Short CK

## Kết quả

Đã tạo 9 spec tại `data/stier/specs/` và script UTF-8 `docs/pm/tickets/GH-180-gen_specs.py`. Lời trong `lines` lấy nguyên từng dòng đánh số từ file lời; các cảnh giả định đã gắn `hypo: true`, cảnh phép chiếu CPI có thêm nhãn phép tính. Có URL nguồn trong mô tả và `sources`, câu miễn trừ CK, và đích Long cho 6 bài loại L. `publish_at` là UTC; không ghi lịch thật.

| Ngày VN | 17:30 | 19:00 | 22:00 |
|---|---|---|---|
| 17/11 | `ck-e5-thuong-tet-khau-tru` | `ck-e6-bon-trieu-tam-rut-mot-lan` | `ck-a2-mot-nua-sau-muoi-sau-nam` |
| 18/11 | `ck-e5-mot-dua-tre-mot-to-dang-ky` | `ck-e6-tro-cap-540-nghin` | `ck-a2-thang-chin-nam-phay` |
| 19/11 | `ck-dien-sinh-hoat-bac-mot-1901` | `ck-ho-kinh-doanh-duoi-mot-ty` | `ck-tran-tro-cap-that-nghiep-26-trieu` |

## Kiểm tra và việc cần Lead quyết định

- Đã chạy `python docs/pm/tickets/GH-180-gen_specs.py`.
- Đã chạy `python motion/stier/build.py --preflight <slug>` cho cả 9, sau khi chỉnh phối cảnh. Bảy bài đạt exit 0, không có cảnh báo hypo. Hai bài chưa đạt exit 1: `ck-e5-mot-dua-tre-mot-to-dang-ky` có 136 từ, vượt giới hạn 135 và ước lượng 41,2 giây, vượt 40 giây; `ck-e6-tro-cap-540-nghin` ước lượng 40,6 giây, vượt 40 giây. Brief yêu cầu giữ nguyên văn nên chưa cắt lời hoặc sửa bộ kiểm. Cần Lead quyết định sửa lời hay điều chỉnh cổng; không coi hai spec này là hoàn tất.
- Đã chạy `PYTHONPATH=. python motion/stier/script_lint.py <slug>` cho cả 9: mỗi bài 0 lỗi, exit 0; số cảnh báo theo thứ tự bảng lời 1–9 là 5, 8, 4, 6, 9, 12, 5, 4, 8. Cảnh báo gồm thiếu móc giữa bài, câu cuối không phải câu hỏi, câu/mệnh đề dài; một số cảnh báo nhận nhầm nội dung kinh ở bài hộ kinh doanh. File lời yêu cầu câu cuối không là câu hỏi và brief cấm cắt lời, nên giữ nguyên và chuyển Lead xem.
- Đã chạy chính xác lệnh kiểm mã hóa toàn bộ spec theo ticket: exit 1, tìm thấy chuỗi `???` hoặc `Kh?ng` trong 4 file cũ: `bud-bd-3-chu-khi-nghi-nhieu-v3.json`, `bud-bd-4-kieu-ban-that-v3.json`, `bud-kg-ke-5-han-thu-v3.json`, `mim-watson-toronto.json`. Không có spec GH-180 trong danh sách; không sửa file cũ ngoài phạm vi.
- Không mở lại các URL trong phiên lắp spec này; nguồn và kết quả kiểm chứng được kế thừa từ `GH-180-shorts-lines.md` và `GH-180-shorts-report.md`. Vì vậy chưa xác minh độc lập các khẳng định trong phiên này. Báo cáo lời đã nêu chênh lệch tỷ lệ của nguồn Thanh Niên; lời dùng phép chia hai số, không dùng tỷ lệ 27,7% của bài báo.
- Footage `pexels:7710775` lấy theo spec CK mẫu, chưa xem clip thực tế để kiểm logo/chữ; phối cảnh, nhãn hypo và chuyển động chưa được kiểm bằng hình. Cần kiểm khi render và QA sau này.
- Không render theo phạm vi ticket; do đó chưa có clip sheet, ảnh QA hoặc thumbnail để cung cấp. Không enqueue, upload, commit hoặc đổi lịch.
