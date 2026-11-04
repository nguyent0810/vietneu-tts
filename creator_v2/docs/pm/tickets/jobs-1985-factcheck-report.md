# Báo cáo bổ sung factcheck mim-jobs-1985

Chỉ sửa `data/long/mim-jobs-1985/factcheck.md`. Không đụng video, script, ch*.json, spec, lint.

## Lint
- Trước: 3 lỗi (số 816 thiếu; TRÍCH DỊCH 0/3; mục CH08 lệch bản final).
- Sau: `mim-jobs-1985: 0 lỗi (factcheck)`.

## Lời trích (đã mở trang và xác nhận câu có trên trang)
1. CH01 (nhãn cảnh) - Bản dịch: "Hội đồng đã chọn chính người tôi mời về." Nguyên văn: "When we did, our Board of Directors sided with him." URL: https://jamesclear.com/great-speeches/2005-stanford-commencement-address-by-steve-jobs . Xác minh: tải trang bằng curl, thấy câu "...our Board of Directors sided with him. So at 30 I was out. And very publicly out." Lưu ý: bản dịch là cô đọng (him = người Jobs thuê về), không sát từng chữ.
2. CH03 - Bản dịch: "Năm 30 tuổi, tôi bị loại ra, rất công khai." Nguyên văn: "So at 30 I was out. And very publicly out." Cùng URL và cùng cách xác minh.
3. CH07 - Bản dịch: "Việc người sáng lập rời đi là một sai lầm, và tôi có phần trong đó." Nguyên văn: "I think, in hindsight, for the founder to leave was a mistake and I was a part of that" (John Sculley, Times of India qua The Register). URL: https://www.theregister.com/2014/04/18/exapple_ceo_john_sculley_ousting_steve_jobs_was_a_mistake/ . Xác minh: WebFetch trang, câu trích khớp.

Không có câu nào chưa xác minh được. Bản dịch CH01 hơi diễn đạt lại (xem lưu ý), cần chủ kênh biết.

## CH08
Bản final CH08 không nhắc Apple–Microsoft hay 150 triệu USD. Dòng CH08 viết lại theo nội dung đã đăng (1985, NeXT, 1997 CEO tạm quyền, 2001 Mac OS X, ledger 1988/1993/12.1996) với nguồn từ CH04-CH07. Khẳng định Apple–Microsoft (#35) chuyển sang ghi chú "đã bỏ khỏi bản final".

## 816
Nhãn CH06 "LỖ RÒNG... KỲ TRƯỚC LỖ 816" = 816 triệu USD (research.md #21, FY1996, 10-K SEC). Thêm dòng ghi chú nêu đơn vị trong factcheck.md; lint hết báo.
