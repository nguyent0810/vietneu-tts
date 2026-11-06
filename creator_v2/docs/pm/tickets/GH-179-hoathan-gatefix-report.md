# GH-179 — Báo cáo sửa Hòa Thân

**Trạng thái: chưa hoàn tất.** Cổng cuối còn một lỗi vì cả 14 chương chưa có TTS. Ticket giao TTS cho agy làm sau, trong khi yêu cầu chung đòi cổng in ĐẠT; không tạo timing giả hoặc chạy TTS ngoài phạm vi ticket.

## Việc đã làm

- Đồng bộ hai câu CH05 và CH09 với script.md; không sửa script.md. Bộ sinh được bổ sung bước chạy script_lines sau khi sinh để lấy lời đọc mới từ script.md, và giữ bảng say cùng metadata YouTube.
- Thêm cảnh file ở CH12 về Khánh Thân vương. Thay 17 lượt ảnh lặp bằng hiện vật và tranh có sẵn, ghi nhãn minh họa phù hợp; thêm focus cho ảnh dọc.
- Bổ sung giờ dự kiến 15/11/2026 14:00 UTC, playlist, tiêu đề 14 chương, nguồn, ghi công ảnh CC BY đã thay, và 11 mục phiên âm Latin/Anh. 51 từ cổng đếm gồm nhiều từ tiếng Việt không dấu hoặc từ đầu câu, không phải 51 tên nước ngoài.
- Tiêu đề ticket đề xuất dài hơn giới hạn 60 ký tự trong AGENTS.md; dùng tạm “TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Hồ Sơ Hòa Thân” để tuân thủ giới hạn. Lead cần chốt.
- Chỉ có bốn câu trích dịch lịch sử khác nhau; câu “Ban cho tự vẫn” được dùng lại ở CH00 và CH08. Con số sáu của factcheck_lint gồm dòng quy ước và nhãn cảnh riêng, không phải sáu câu lịch sử khác nhau. Đã bổ sung một dòng chứng từ cho lần lặp CH08, nguyên văn 賜自盡, nguồn https://zh.wikisource.org/wiki/清史稿/卷319 đã mở. Không bịa câu thứ sáu.

## Những ảnh đã thay

- CH07: giakhanh → emperor_jifu_robe, qianlong_dragon_dish, court_jifu_robe; canlong → emperor_jifu_robe, qianlong_essay_old_age; hoa → wenguan_portrait_1, wenguan_portrait_2.
- CH08: canlong → qianlong_poem_flowers; giakhanh → qianlong_lacquer_teabowl, qianlong_poem_victory; hieu → bridal_dragon_robe, qianlong_dragon_dish, court_jifu_robe.
- CH09: giakhanh → qianlong_temple_name; hoa → court_jifu_robe.
- CH11: hoa → qianlong_lacquer_teabowl; luudung → wenguan_portrait_1.

Ảnh thay là hiện vật hoặc tranh minh họa, không gắn nhãn chân dung người thật cho hình quan văn. Các ảnh Commons cũ theo khóa đang khai trong spec không có file tương ứng trong output/long/hoa-than/img ở thời điểm kiểm tra. Chưa có điều kiện soi khung sau dựng, Lead cần kiểm tra sự phù hợp hình ảnh và việc tải lại các ảnh tư liệu trước render. Chưa thể xác định đầy đủ giấy phép và ghi công các ảnh Commons cũ khi metadata của chúng chưa có trên đĩa.

## Kiểm tra

- python motion/long/scene_params.py hoa-than: thoát 0, 0 lỗi, 0 cảnh báo.
- python motion/long/floor.py hoa-than: thoát 0, không in nội dung.
- python motion/variety.py audit hoa-than: thoát 0, OK.
- python motion/long/cadence.py hoa-than: thoát 0 nhưng cảnh báo CH00–CH03 và CH10–CH13; tối đa ước tính 39,49 giây tại CH01. Đây là ước tính 150 giây/chương khi chưa có timing; cần chạy lại sau TTS.
- python motion/long/factcheck_lint.py hoa-than: thoát 0, 0 lỗi.
- python scripts/long_gate.py hoa-than --min-syl 5000: 5.722 âm tiết, 305 cảnh, 48 ảnh, 22 URL; TRƯỢT 1 lỗi duy nhất: thiếu TTS CH00–CH13.
- Chưa chạy render, clip sheet hay thumbnail; không có đường dẫn sheet/thumbnail đã kiểm cho lượt sửa này.

## Việc Lead cần xử lý

Chạy TTS theo phân công ticket, chạy lại toàn bộ cổng và kiểm tra thực tế nhịp/các asset trước render. Các điểm chưa kiểm được từ factcheck cũ vẫn giữ nguyên, gồm toàn văn McMahon, trang bảo tàng và nhật ký Macartney nguyên văn. File hỗ trợ gh179_work.py đã bị tạo ở thư mục gốc trong quá trình sửa; để nguyên vì AGENTS.md cấm xóa file ngoài thư mục topic.
