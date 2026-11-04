# Retro CK Shorts pilot (GH-33), 03/11/2026

Phạm vi: 5 Short đã upload private + hẹn lịch. Nguồn đối chiếu: `bundles/CK/<slug>.json` (title, description, script), `docs/pm/tickets/GH-33-CK-facts.json` (nguồn + trích dẫn), và fetch lại các URL nguồn ngày 03/11. Không chỉnh sửa gì.

## Kết luận nhanh
- Không có "nên mua/bán", không ticker, cả 5 mô tả đều có câu "Nội dung giáo dục, không phải tư vấn đầu tư.", không có CẦN KIỂM, `<>` hay đường dẫn data/long. Tên Binance, SJC, EVN theo quyền chủ kênh nên không tính lỗi.
- Số liệu chính (giá xăng, giá điện, 137/140 triệu, 123,8 triệu, 3,64 tỷ, 2,1%, 643 triệu, 95%, 30%/10 tỷ) đều truy được về `GH-33-CK-facts.json` và nguồn.
- Có 3 câu kể sự thật mà nguồn không đỡ, và 2 chỗ chọn số hẹp. Không câu nào đổi hướng kết luận của video, nhưng 2 chỗ (A1, A2) đáng để chủ kênh cân nhắc.

## A. Có thể đổi nghĩa (chủ kênh quyết định có thay video private không)

**A1. Điện: "nhà máy thép hay dệt may bớt hàng trăm triệu đồng" (`ck-dien-giam-44-dong-20-nam`, script).**
Không có con số nào trong nguồn. Thanh Niên (nguồn đã liệt kê) chỉ nêu giá thành thép giảm khoảng 0,12%, xi măng 0,3%, dệt may 0,2%, không có số tiền. Mô tả còn viết "giảm mạnh chi phí đầu vào" trong khi mức giảm chỉ 2%. Đề xuất: nếu thay, đổi thành "giảm chi phí đầu vào vài phần nghìn đến vài phần trăm giá thành" hoặc bỏ câu số tiền.

**A2. Xăng: "Đơn vị vận tải ký cước theo quý và còn gánh phí bến bãi, nhân công" (`ck-thue-xang-0-giam-1804`, script, đồng thời mô tả "hợp đồng cước ký theo quý").**
Dân Trí (nguồn dẫn cho claim này) không nhắc hợp đồng theo quý hay bến bãi, nhân công. Lý do trong bài là: cước thường trễ 20-30 ngày so với giá xăng, doanh nghiệp muốn thấy xu hướng, xe tải phần lớn chạy dầu diesel chưa giảm, giữ giá khi xăng tăng. Ý "cước chưa giảm ngay" đúng, nhưng lý do nêu ra là bịa. Đề xuất: nếu thay, dùng "cước thường trễ 20-30 ngày" và "phần lớn xe chạy dầu diesel chưa giảm".

## B. Cosmetic (giữ nguyên, ghi nhận)

- **B1. Vàng: chọn khoảng chênh.** Title chỉ nêu "Vênh thế giới 14,3 triệu" (mức thấp nhất); script nói đúng "từ 14,3 đến hơn 16 triệu tùy cách tính". VnExpress ghi hơn 17 triệu (17,5 triệu), facts.json cũng ghi "hơn 17" nhưng script viết "hơn 16", lệch với chính file facts. Hướng sai không làm người xem hiểu sai chiều, nhưng title nên ghi "từ 14,3 triệu".
- **B2. Vàng: "lỗ hơn 11 triệu sau 2 tuần".** Số này đến từ tiêu đề Thanh Niên (không fetch được nội dung mới trong VnExpress, bài đó không nhắc). Chấp nhận theo tiêu đề Thanh Niên; nên lưu thêm trích dẫn thân bài.
- **B3. SME giảm 30% thuế: "tự trừ ngay trong từng kỳ kê khai quý".** VnEconomy: doanh nghiệp tự xác định khi tạm nộp quý; hộ kinh doanh gắn với kỳ kê khai tương ứng. Script nói chung chung "hộ kinh doanh", chưa sai hẳn. Điều khoản "vượt 10 tỷ thì kê khai điều chỉnh và nộp lại toàn bộ" được VnEconomy xác nhận (facts.json trích dẫn câu khác nên chưa chứng minh được, nhưng thân bài có).
- **B4. Binance: "ETF bị rút ròng trong phiên cuối tuần".** CoinDesk ghi phiên thứ Sáu. Dùng "phiên thứ Sáu". Từ "cũng" và "châm ngòi" (mô tả) ngầm gán quan hệ nhân quả hack - ETF chưa có nguồn.
- **B5. Mốc thời gian "hôm nay".** Title xăng ("Giá xăng hôm nay") và vàng/điện gắn ngày; xăng đăng 04/11 (giá xăng VN điều chỉnh định kỳ hàng tuần có thể đã đổi). Nên dùng ngày cụ thể thay "hôm nay".
- **B6. Mô tả lặp câu disclaimer hai lần** (cả 5 bài). Không sai, thừa.
- **B7. Ví dụ giả định có nhãn "ví dụ giả định" trong lời đọc:** đạt (50 lít x 1.804 ≈ 90.000 đồng, 1 triệu x 2% = 20.000, 40 triệu x 30% = 12 triệu).

## C. Lỗi quy trình cần sửa tận gốc

**C1. Cổng trùng chủ đề chỉ chạy lúc upload.** `novelty.duplicate_on_channel` được gọi ở `motion/stier/upload_one.py:106` (và `enqueue.py:74` cho CL), không gọi ở bước tạo spec/titles/render CK. Kết quả: `ck-lai-giam-05-tien-gui-80-ngan-han` đã được viết kịch bản, dựng và render rồi mới bị chặn khi upload (lãng phí 1 lượt render). Sửa: gọi `duplicate_on_channel` cho từng title ứng viên ngay khi chốt `GH-33-titles.json` và trước `assemble`/render trong `motion/stier`, thất bại thì dừng sớm.

**C2. Claim trong `verified_facts` không khớp trích dẫn.** Ví dụ `GH-33-CK-facts.json`: claim "doanh nghiệp vượt 10 tỷ phải nộp bổ sung" gắn với trích dẫn không nói điều đó; lý do vận tải (A2) và số tiền nhà máy (A1) thậm chí không có trong `verified_facts`, chỉ nằm trong `outline_lines`. Sửa: lint script-vs-facts, mỗi câu có số hoặc nhân quả trong script phải trỏ tới một fact có trích dẫn; câu "lý do" không có nguồn thì chặn.

**C3. Lệch số giữa facts và script (hơn 17 vs hơn 16, B1).** Sửa: sinh phạm vi số từ cùng một nguồn trong facts rồi để script đọc lại, không gõ tay lại.

## Việc cần chủ kênh quyết định
Thay video A1 (điện) và A2 (xăng) hay giữ. Theo ngưỡng "chỉ thay khi đổi nghĩa": cả hai đều là câu nêu dữ kiện sai nguồn, không đổi kết luận video. Đề xuất giữ nếu chưa đăng public vẫn được; nếu muốn sạch thì thay chỉ A1 và A2 (cả hai còn private và chưa tới giờ hẹn).
