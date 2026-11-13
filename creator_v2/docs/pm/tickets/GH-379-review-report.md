# Báo cáo GH-379: review câu chuyện Binance

## Phạm vi và kết quả

- Đã viết tám bản review CH00–CH07 tại `data/long/mim-binance-6-3-ty-20-phut/story_review/chNN.md`, mỗi bản có năm điểm review, bản viết lại và mục cần xác minh.
- Đã ghép `data/long/mim-binance-6-3-ty-20-phut/script.v2.md`; không ghi đè `script.md`. Đầu file và mục Ghi chú kiểm chứng giữ nguyên. Tám bản viết lại đã đối chiếu khớp phần tương ứng trong bản ghép.
- Ticket chỉ cung cấp prompt CH00–CH07, trong khi kịch bản có CH08. Đã giữ chương kết trong bản ghép và chỉnh để phân biệt phần lớn tiền rời đi trong hai mươi phút, nhận định của TRM/Halborn và hai loại quyền kiểm soát. Không tạo review CH08 ngoài phạm vi ticket.
- Đã xét sáu luật §13: gộp dữ kiện thành diễn biến, đặt giới hạn cạnh nhận định, tiến mạch, dành khoảng lặng cho mất mát bằng dữ kiện thay vì cảm xúc bịa, giữ niên đại, không kể hộ động cơ. Luật về mất mát nhân mạng không áp trực tiếp vào vụ thiệt hại tài sản này.
- Không gọi mạng, không render, không đăng và không dùng git. Vì ticket không yêu cầu dựng, không có clip sheet hoặc thumbnail mới.

## Âm tiết

Đếm theo lời đọc do `motion.long.script_lines.parse` phân tích, mỗi từ là một âm tiết; chênh lệch từng chương đều trong ±10%.

| Chương | Cũ | Mới | Thay đổi |
|---|---:|---:|---:|
| CH00 | 196 | 183 | -6.6% |
| CH01 | 200 | 188 | -6.0% |
| CH02 | 224 | 206 | -8.0% |
| CH03 | 284 | 304 | +7.0% |
| CH04 | 267 | 268 | +0.4% |
| CH05 | 305 | 296 | -3.0% |
| CH06 | 427 | 417 | -2.3% |
| CH07 | 288 | 278 | -3.5% |
| CH08 | 233 | 221 | -5.2% |
| **Tổng** | **2424** | **2361** | **-2.6%** |

## Lệnh và cổng kiểm

- `python motion/long/script_lines.py mim-binance-6-3-ty-20-phut`: mã thoát 0; bản gốc 2.424 âm tiết.
- Với nội dung v2, gọi trực tiếp `script_lines.parse`, `script_lines.gate`, `script_lines.flow_warnings`, `script_lines.beat_warnings` và `craft.audio_problems` từ Python như phương án dự phòng được ticket cho phép: gate `[]`; craft `[]`; không có cảnh báo luồng, gồm NHIP_DEU và RAO_NGUON, ở cả bản cũ lẫn mới. Cảnh báo NHIP_30S ước lượng: cũ 8, mới 7; các cửa sổ có thể thay đổi do nhịp mới, Lead cần kiểm lại sau TTS. Không có cảnh báo Python từ `parse`/`gate` ở cả hai bản.
- V2 có câu hỏi trong tám câu đầu, có “bạn”, có dấu ngừng dài; dòng lời đọc dài nhất 29 âm tiết. Cả ba câu `[TRÍCH DỊCH]` giống nguyên văn bản gốc.
- Kiểm tra bằng Python: tám bản viết lại khớp bản ghép; không có hai dấu hỏi liên tiếp trong các file đã ghi. Dấu `?` xuất hiện trong lời kể là dấu câu hỏi, không phải ký tự thay chữ có dấu.
- `python scripts/long_gate.py mim-binance-6-3-ty-20-phut --min-syl 1900`: **TRƯỢT, 23 lỗi**, mã thoát 1. Lệnh đọc kịch bản gốc `script.md` (2.424 âm tiết), không phải `script.v2.md`. Kết quả báo cả chín chương thiếu HUD và loại cảnh, chưa có TTS, chưa có cảnh, thiếu trường/nguồn `spec.youtube` và bảng `say` cho 43 thuật ngữ. Các phần dựng/spec không thuộc ticket review nên chưa sửa. Cổng bắt buộc **chưa đạt**, không thể báo hoàn tất Long.

## Cần xác minh gộp

- Nguồn TRM gốc về khung phần lớn tiền rời đi trong khoảng hai mươi phút, thời gian dàn dựng, danh hiệu lớn nhất và dấu hiệu xâm phạm hệ thống ký; factcheck cho biết một số bản gốc chưa mở được. Kiểm độc lập danh hiệu Bybit lớn nhất trước đó và nguyên nhân khác biệt giữa các phép đếm.
- Đối chiếu Elliptic gốc về dòng thời gian, lần quét, kết thúc gần nửa đêm, tổng đóng băng, tỷ lệ 44% và lượng tiền còn giữ; mốc Avalanche/Polygon theo Halborn là khoảng 23:05 UTC. Giờ khóa chi tiết hiện dựa vào Halborn.
- Xác minh phạm vi các giao dịch thử và cách dịch `service container`; báo cáo cuối của Binance về đường xâm nhập chưa công bố.
- Đối chiếu thông báo FBI gốc, phát biểu của Kim Yo Jong và Jonathan Levin, nguyên văn cũng như ngữ cảnh. Vụ việc còn điều tra; phải giữ cả kết luận của FBI lẫn lời phủ nhận của Triều Tiên.
- Đối chiếu thời điểm và phạm vi mở rút, số tiền rút/nạp, cùng phạm vi và thời điểm chụp bằng chứng dự trữ của Binance.

Các mục trên là việc cần Lead kiểm nguồn; lượt review này tuân thủ lệnh không gọi mạng và không tự nhận đã mở lại nguồn.
