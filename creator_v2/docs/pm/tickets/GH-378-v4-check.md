# GH-378: soát kịch bản HKV v4 (phạm vi hẹp theo chủ kênh)

Đầu vào `script.v4.md` (Gemini kéo dài từ v3c); đầu ra `script.v4c.md`. Phạm vi: chỉ sửa câu nói tới tư liệu (tên, năm/ngày, con số, chức danh, ai làm gì, lời trích) cho khớp `factcheck.md`. Không khí, cảnh, hình ảnh, kịch tính của Gemini giữ nguyên, không thêm {pd}.

Tổng 27 chỗ sửa (3 câu dài chỉ tách đôi, không đổi nghĩa). Kiểm: `script_lines.gate == []`; `craft.audio_problems == []`; không câu nào quá 32 âm tiết; 5.894 âm tiết (đạt mức 5.600). Đối chiếu ngược với 211 chỗ sửa v3: không câu cũ nào bị đưa lại nguyên văn.

Lời trích: các dòng TRÍCH DỊCH mới trong v4 (sách 1930 mục Hoàng, Trương, Đỗ) đã so với factcheck §16, khớp.

Ghi nhận không sửa (ngoài phạm vi hẹp): các cảnh {pd} cũ từ v3c còn chi tiết hành động của người thật (CH05 gian giam, CH11 ghế mây, CH12 bàn tay run, lom khom). Người này đã mất, nên theo chỉ đạo giữ nguyên.

## Bảng sửa

| Chương | Câu cũ (v4) | Câu mới (v4c) | Loại |
|---|---|---|---|
| CH00 | Nhưng đến cuối đời, thứ còn lại trong tay chỉ là một cây chổi tre. | Nhưng đến cuối đời, thứ còn lại trong tay chỉ là một cây chổi. | FIX |
| CH01 | Có nguồn kể cha ông từng mở một quán trà nhỏ tại thành phố này. | Wikipedia tiếng Anh lại chép rằng cha ông mở một quán trà. | FIX |
| CH01 | Năm 1862, người Pháp rút khỏi Hội đồng chung để tự lập ra sở cảnh sát riêng. | Năm 1862, người Pháp rút khỏi Hội đồng chung của các tô giới để đi con đường riêng. | FIX |
| CH01 | Có nguồn kể sau một lần cãi cọ | Theo Wikipedia tiếng Anh, sau một lần cãi cọ | FIX |
| CH01 | Nhưng rồi người Pháp nhận thấy họ không thể quản lý khu phố Hoa nếu thiếu ông, nên đã gọi ông quay lại. | Rồi ông được gọi trở lại làm việc trong sở bắt. | CUT |
| CH02 | đổi lại việc Pháp trục xuất người làm cách mạng. | đổi lại việc Pháp hứa trục xuất những người làm cách mạng khỏi vùng mình quản. | FIX |
| CH02 | Trong giang hồ từng có giai thoại rằng ông câu kết với trộm cướp, tự dựng các vụ án rồi tự mình ra tay bắt giữ. | Một bài báo phổ thông kể giai thoại rằng ông tự dàn cảnh các vụ cướp rồi tự mình ra tay bắt, nhưng bài ấy không dẫn nguồn. | FIX |
| CH02 | Dù chỉ là giai thoại, điều đó cho thấy người đời nhìn nhận sự khôn ngoan hai mặt của ông như thế nào. | Vì vậy chuyện ấy chỉ nên nghe như một giai thoại. | FIX |
| CH04 | Bà là một ca sĩ sân khấu đang rất được ái mộ bấy giờ. | Bà là một ca sĩ sân khấu. | FIX |
| CH05 | Đối với người Pháp, một thám viên bản địa dù mẫn cán đến đâu cũng có thể bị gạt bỏ khi gây rắc rối lớn. | Wikipedia gắn việc ấy với chuyện ông công khai đánh con trai quân phiệt Lư Vĩnh Tường. | FIX |
| CH05 | Sự đối lập ấy cho thấy người đời sau đã tìm cách làm đẹp hồ sơ cho ông trùm như thế nào. | Hai lời chép khác nhau, và các nguồn trong tay chưa đủ để phân xử bên nào đúng. | FIX |
| CH06 | Khoản tiền khổng lồ ấy đổi lại sự tự do, nhưng cũng đánh dấu sự khởi đầu của một trật tự mới. | Theo Wikipedia, ngoại giao và tiền bạc của Đỗ đã cứu được người thầy, và từ đó vị thế của Đỗ lên nhanh. | FIX |
| CH06 | Sách năm 1930 ghi Trương Khiếu Lâm tên Trương Dần, sinh năm 1877 ở Từ Khê, Chiết Giang. | Sách năm 1930 ghi Trương Khiếu Lâm tên Trương Dần, người Từ Khê, Chiết Giang; Wikipedia ghi ông sinh năm 1877. | FIX |
| CH08 | Ngày 6 tháng 4 năm 1927, một ủy ban loại trừ cộng sản được lập ra, phối hợp chặt chẽ cùng Thanh bang. | Ngày 6 tháng 4 năm 1927, Ủy ban Giám sát Quốc dân đảng ở Thượng Hải lập một ủy ban loại cộng sản khỏi đảng, phối hợp với các thành viên Thanh bang. | FIX |
| CH08 | kiểm soát hoàn toàn Thượng Hải. | kiểm soát Thượng Hải. | FIX |
| CH09 | Mục viết về Đỗ Nguyệt Sanh ca ngợi nhiều chức vụ lớn của Đỗ, như Chủ tịch Tổng hội thương giới hay Hoa đổng Công bộ cục. | Mục viết về Đỗ Nguyệt Sanh kể nhiều chức vụ của Đỗ, như chủ tịch hội liên hiệp giới thương mại tô giới Pháp hay Hoa đổng Công bộ cục tô giới Pháp. | FIX |
| CH10 | nổi tiếng với mười hai tấm gương méo nhập từ Hà Lan. | có mười hai tấm gương méo nhập từ Hà Lan. | FIX |
| CH10 | Có từ bảy trăm đến chín trăm năm mươi người chết ngay tại chỗ. / Khoảng hai nghìn người chết hoặc bị thương theo ghi chép của Đại Thế Giới. | Trang về Trận Thượng Hải ghi cả ngày hôm ấy có từ bảy trăm đến chín trăm năm mươi thường dân chết ngay, tổng cộng khoảng ba nghìn người chết và bị thương. / Riêng trang về Đại Thế Giới ghi khoảng hai nghìn người chết hoặc bị thương. | FIX |
| CH11 | Hành vi phản bội ấy phải trả bằng một cái giá rất đắt. | Ông không sống được đến hết chiến tranh. | FIX |
| CH11 | Không ai rõ ai đã bóp cò trong phát đạn định mệnh ấy. | Các nguồn tôi đọc không nói ai đã bắn. | FIX |
| CH11 | Điều đó đến nay vẫn chưa có câu trả lời rõ ràng trong các tài liệu để lại. | Các nguồn tôi đọc không ghi lý do. | FIX |
| CH13 | Trong các vai chính của bộ phim lừng danh ấy, cái tên Hoàng Kim Vinh không hề xuất hiện. | Trang Wikipedia của bộ phim không nhắc tên Hoàng Kim Vinh trong dàn vai chính. | FIX |
| CH13 | Nhiều năm sau, phim Kiêu Hùng hay phim 1921 mới tái hiện lại hình ảnh của ông. | Phim Kiêu Hùng năm 2015 có một nhân vật dựa trên ông, còn phim 1921 có Nghê Đại Hồng đóng Hoàng Kim Vinh. | FIX |
| CH13 | Tòa tháp Đại Thế Giới ngày nay vẫn sừng sững giữa ngã tư tấp nập, nhưng những ông trùm năm xưa đã vĩnh viễn đi vào dĩ vãng. | Nơi ấy đã đổi tên, đổi chủ và đổi công dụng, còn những ông trùm năm xưa đã đi vào dĩ vãng. | FIX |
| CH08, CH09, CH10 | 3 câu dài 33 âm tiết | tách thành 2 câu | tách câu |
