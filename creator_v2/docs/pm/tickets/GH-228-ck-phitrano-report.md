# GH-228 — Báo cáo

## Đã thực hiện

- Sửa `data/stier/specs/ck-phi-tra-no-ngan-hang-truoc-han.json`: bỏ khoảng phí không có nguồn trong lời và hình, bỏ giải thích về chi phí vốn; đổi câu mở tình huống sang “bạn”.
- Thay nội dung bằng thỏa thuận giữa khách hàng và bên cho vay, cùng việc kiểm tra điều khoản phí. Không dùng ví dụ số giả định.
- Giữ nguyên `publish_at`, tiêu đề, mô tả và các trường YouTube khác. Sáu loại cảnh: photo, timeline, cards3d, file, board, slam.
- Bổ sung nguồn văn bản Thông tư trong `sources`: https://thuvienphapluat.vn/van-ban/Tien-te-Ngan-hang/Thong-tu-39-2016-TT-NHNN-hoat-dong-cho-vay-cua-to-chuc-tin-dung-chi-nhanh-ngan-hang-nuoc-ngoai-338877.aspx . Đã mở: Điều 14 nói về thỏa thuận phí trả nợ trước hạn; Điều 23 yêu cầu thỏa thuận cho vay bằng văn bản nêu loại và mức phí.
- URL Báo Chính phủ cũ trong mô tả không mở được bằng công cụ duyệt trong lượt này. Không xác minh lại nội dung URL đó; giữ mô tả theo brief. Không còn khẳng định mức phí phổ biến hay lý do bù đắp chi phí vốn.

## Lời mới từng câu

1. Trả nợ trước hạn có thể phát sinh phí, tùy theo thỏa thuận.
2. Bạn gom đủ tiền và muốn trả khoản vay sớm hơn thời hạn đã ký.
3. Phí trả nợ trước hạn do bạn và tổ chức cho vay thỏa thuận với nhau.
4. Nội dung về phí cần được ghi rõ trong thỏa thuận cho vay.
5. Trước khi trả sớm, bạn hãy xem điều khoản phí trong hợp đồng.
6. Nếu chưa rõ cách tính, hãy hỏi bên cho vay trước khi quyết định trả nợ.

## Kiểm tra

- `PYTHONIOENCODING=utf-8 python motion/stier/build.py --preflight ck-phi-tra-no-ngan-hang-truoc-han`: **OK**, 86 từ, ước lượng 26,1 giây.
- `PYTHONPATH=. PYTHONIOENCODING=utf-8 python motion/stier/script_lint.py ck-phi-tra-no-ngan-hang-truoc-han`: **0 lỗi, 7 cảnh báo**: R1 hook 13 từ; R2 thiếu câu móc lại; R5 câu cuối không phải câu hỏi; R6 mệnh đề dài tại câu 1, 2, 5 theo chỉ số lint; R9 không có con số/chi tiết đếm được. Không thêm số để tránh đưa mức phí không có căn cứ.
- `rg -n '\?' data/stier/specs/ck-phi-tra-no-ngan-hang-truoc-han.json`: chỉ khớp dấu hỏi câu trong tiêu đề và mô tả. Đã phát hiện lỗi mất dấu ở lần ghi đầu và sửa lại bằng Python UTF-8 trước khi chạy lại kiểm tra.
- `rg -n '1% - 2%|một đến hai phần trăm' data/stier/specs/ck-phi-tra-no-ngan-hang-truoc-han.json`: không có kết quả.
- Không render theo brief; không có clip sheet hoặc thumbnail mới để cung cấp. Chưa kiểm tra khung hình thực tế hay nghe TTS.
- Không đăng, enqueue, commit, đổi nhánh hoặc đổi lịch.
