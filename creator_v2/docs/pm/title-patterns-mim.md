# Bộ khuôn tiêu đề MIM

Kỳ 28 ngày: 07/10–03/11/2026; dữ liệu Analytics kéo 06/11. Chỉ xét video công khai, gộp bản ghi trùng ID.

> **Bằng chứng:** lượt xem, giờ xem, AVD, AVP và nguồn traffic là **đo**; khuôn và lý giải là **suy luận**, không chứng minh quan hệ nhân quả. Không có impressions, CTR hoặc thiết bị. Mẫu nhỏ; thử từng biến và đo lại sau 72 giờ và 7 ngày.

Giờ xem bằng phút ước tính chia 60; AVD và AVP lấy trực tiếp từ API. Nguồn ghi tối đa hai nguồn có giờ xem cao nhất, kèm tỷ lệ lượt xem trên tổng video. SUBSCRIBER = Browse/Home, RELATED_VIDEO = Đề xuất, EXT_URL = bên ngoài, YT_SEARCH = tìm kiếm.

Năm Long MIM đổi tiêu đề ngày 06/11 theo PR #200, sau kỳ đo; chưa có số sau đổi. Snapshot không xác định chắc danh sách năm video và tên trước/sau; không thể đo tác động tên mới. Tên Watson được rút gọn chuỗi dấu hỏi bằng dấu ba chấm, số ký tự tính theo tên gốc.

## Long công khai: top 5 và bottom 5 theo giờ xem

| Tiêu đề snapshot | Ký tự | Lượt xem | Giờ | AVD | AVP | Nguồn: giờ và % lượt xem |
|---|---:|---:|---:|---:|---:|---|
| AI Giả Giọng Người Thân Để Lừa Tiền: Một Từ Bí Mật Có Thể Cứu Cả Nhà | 68 | 440 | 14.22 | 4:34 | 34.9% | RELATED_VIDEO 5.73h, 23.0%; EXT_URL 4.35h, 4.8% |
| AI Có Cướp Việc Của Bạn? 200 Năm Trước Người Ta Cũng Sợ Y Như Vậy | 65 | 169 | 11.00 | 5:26 | 38.7% | RELATED_VIDEO 6.65h, 39.6%; EXT_URL 2.72h, 10.7% |
| Luật Sư Nộp 6 Vụ Án Do ChatGPT Bịa: Vì Sao AI Tự Tin? | 53 | 129 | 10.35 | 5:51 | 43.6% | EXT_URL 5.58h, 19.4%; RELATED_VIDEO 4.07h, 60.5% |
| Thuật Toán Đề Xuất: Vì Sao TikTok Và YouTube Biết Bạn Thích Gì? | 63 | 267 | 6.07 | 2:47 | 20.5% | RELATED_VIDEO 5.10h, 46.8%; SUBSCRIBER 0.65h, 46.8% |
| Năm Ván Cờ Thay Đổi AI: AlphaGo Đấu Lee Sedol, Và Nước Cờ Một Phần Vạn | 70 | 70 | 5.73 | 8:23 | 41.7% | RELATED_VIDEO 3.50h, 41.4%; EXT_URL 1.00h, 4.3% |
| Mã QR: Ô Vuông Sinh Ra Để Đếm Linh Kiện Ô Tô, Giờ Nằm Trên Mọi Quầy Hàng Việt Nam | 81 | 50 | 2.83 | 3:57 | 47.9% | RELATED_VIDEO 2.13h, 72.0%; YT_CHANNEL 0.13h, 4.0% |
| AlexNet 2012: Card Chơi Game Đã Thành Trái Tim Của AI | 53 | 71 | 2.12 | 4:20 | 34.0% | SUBSCRIBER 0.68h, 73.2%; EXT_URL 0.63h, 4.2% |
| Deep Blue Đấu Kasparov 1997: 19 Nước Cờ Khiến Nhà Vô Địch Bỏ Đi | 63 | 24 | 1.33 | 5:20 | 28.2% | RELATED_VIDEO 1.22h, 87.5%; NO_LINK_OTHER 0.12h, 4.2% |
| Flappy Bird: Kiếm 50.000 Đô Mỗi Ngày, Vì Sao Nguyễn Hà Đông Tự Tay Gỡ Game? | 75 | 13 | 0.18 | 1:21 | 20.1% | RELATED_VIDEO 0.12h, 53.8%; EXT_URL 0.05h, 7.7% |
| Watson Thắng Jeopardy! 2011: Cỗ Máy Trả Lời “Toronto…” | 58 | — | — | — | — | Chưa có dữ liệu kỳ |

Thứ tự giảm dần trong từng nhóm. Video cuối đăng 04/11 sau kỳ đo: không có dòng API, không coi là thua. Bốn video bottom còn lại có dữ liệu. Khác biệt tuổi video, chủ đề và nguồn ảnh hưởng so sánh.

## Short: top 10 theo lượt xem

Ở lại = engagedViews/views trong cùng kỳ, không đồng nhất với AVP.

| Tiêu đề | Ký tự | Lượt xem | Ở lại |
|---|---:|---:|---:|
| Nước đi thứ 78: ván duy nhất con người thắng AlphaGo | 52 | 1420 | 57.7% |
| Mã QR bẩn tới 30% vẫn đọc được: vì sao? | 39 | 1361 | 19.6% |
| Năm 1950, Alan Turing hẹn máy “giống người” vào khoảng năm 2000 | 63 | 1339 | 34.4% |
| Mã QR ra đời từ một ván cờ vây giờ nghỉ trưa | 44 | 1331 | 39.0% |
| Mạng nơ-ron: từng bị coi là ngõ cụt, 2024 nhận Nobel Vật lý | 59 | 1327 | 42.0% |
| Năm 1958, một cỗ máy 5 tấn tự học phân biệt trái và phải | 56 | 1312 | 44.3% |
| Flappy Bird ra mắt rồi im lặng 8 tháng trước khi đứng đầu thế giới | 66 | 1277 | 30.0% |
| Trò đoán chữ năm 1951: một người đoán trúng 69% chữ cái tiếp theo | 65 | 1273 | 55.5% |
| Năm 1966, có người tin chatbot này là người thật | 48 | 1265 | 44.5% |
| Mười mã vạch trên một thùng hàng: bài toán đẻ ra mã QR | 54 | 1257 | 27.0% |

## Khuôn Long để thử

### Rủi ro và giải pháp
- Cấu trúc: [Công nghệ gây hại]: [cách ứng phó].
- Video: “AI Giả Giọng Người Thân Để Lừa Tiền: Một Từ Bí Mật Có Thể Cứu Cả Nhà” (68 ký tự; 14.22 giờ, 440 lượt xem).
- Độ dài mẫu: 68–68 ký tự.
- Bằng chứng: **suy luận**, n=1 video; số liệu là **đo**, chưa có đối chứng.

### Câu hỏi và tiền lệ
- Cấu trúc: [Câu hỏi hiện tại]? [Tiền lệ lịch sử].
- Video: “AI Có Cướp Việc Của Bạn? 200 Năm Trước Người Ta Cũng Sợ Y Như Vậy” (65 ký tự; 11.00 giờ, 169 lượt xem).
- Độ dài mẫu: 65–65 ký tự.
- Bằng chứng: **suy luận**, n=1 video; số liệu là **đo**, chưa có đối chứng.

### Sự cố và cơ chế
- Cấu trúc: [Sai lầm cụ thể]: Vì sao [cơ chế]?.
- Video: “Luật Sư Nộp 6 Vụ Án Do ChatGPT Bịa: Vì Sao AI Tự Tin?” (53 ký tự; 10.35 giờ, 129 lượt xem).
- Độ dài mẫu: 53–53 ký tự.
- Bằng chứng: **suy luận**, n=1 video; số liệu là **đo**, chưa có đối chứng.

### Công nghệ và câu hỏi
- Cấu trúc: [Công nghệ]: Vì sao [hành vi]?.
- Video: “Thuật Toán Đề Xuất: Vì Sao TikTok Và YouTube Biết Bạn Thích Gì?” (63 ký tự; 6.07 giờ, 267 lượt xem).
- Độ dài mẫu: 63–63 ký tự.
- Bằng chứng: **suy luận**, n=1 video; số liệu là **đo**, chưa có đối chứng.

### Cuộc đấu và bước ngoặt
- Cấu trúc: [Số trận]: [đối thủ] và [chi tiết].
- Video: “Năm Ván Cờ Thay Đổi AI: AlphaGo Đấu Lee Sedol, Và Nước Cờ Một Phần Vạn” (70 ký tự; 5.73 giờ, 70 lượt xem).
- Độ dài mẫu: 70–70 ký tự.
- Bằng chứng: **suy luận**, n=1 video; số liệu là **đo**, chưa có đối chứng.


## Khuôn Short để thử

### Chi tiết quyết định
- Cấu trúc: [Chi tiết]: [kết quả bất ngờ].
- Video: “Nước đi thứ 78: ván duy nhất con người thắng AlphaGo” (52 ký tự; 1420 lượt xem, 57.7% ở lại); “Mã QR ra đời từ một ván cờ vây giờ nghỉ trưa” (44 ký tự; 1331 lượt xem, 39.0% ở lại).
- Độ dài mẫu: 44–52 ký tự.
- Bằng chứng: **suy luận**, n=2 video; số liệu là **đo**, chưa có đối chứng.

### Nghịch lý công nghệ
- Cấu trúc: [Công nghệ] [đặc tính bất ngờ]: vì sao?.
- Video: “Mã QR bẩn tới 30% vẫn đọc được: vì sao?” (39 ký tự; 1361 lượt xem, 19.6% ở lại).
- Độ dài mẫu: 39–39 ký tự.
- Bằng chứng: **suy luận**, n=1 video; số liệu là **đo**, chưa có đối chứng.

### Mốc năm và phát minh
- Cấu trúc: Năm [năm], [người hoặc máy] [hành động].
- Video: “Năm 1950, Alan Turing hẹn máy “giống người” vào khoảng năm 2000” (63 ký tự; 1339 lượt xem, 34.4% ở lại); “Năm 1958, một cỗ máy 5 tấn tự học phân biệt trái và phải” (56 ký tự; 1312 lượt xem, 44.3% ở lại); “Năm 1966, có người tin chatbot này là người thật” (48 ký tự; 1265 lượt xem, 44.5% ở lại).
- Độ dài mẫu: 48–63 ký tự.
- Bằng chứng: **suy luận**, n=3 video; số liệu là **đo**, chưa có đối chứng.

## Khuôn có mẫu thua

Flappy Bird: thu nhập lớn rồi hỏi lý do gỡ, 75 ký tự, 13 lượt, 0,18 giờ, AVD 1:21, AVP 20,1% (n=1). Deep Blue: cuộc đấu với con số và kết cục, 63 ký tự, 24 lượt, 1,33 giờ, AVD 5:20, AVP 28,2% (n=1); AlphaGo cùng dạng lại ở top 5. Kết quả thấp được đo; lý do thua chưa kiểm được.

## Giới hạn tiêu đề

Trần hiện tại **60 ký tự**. Bốn video top 5 dài 63–70 ký tự, nhưng tên snapshot có thể đã đổi sau kỳ đo. Đề xuất thử dài hơn 60 khi được duyệt và so ở cùng thời gian sau đăng; chưa đủ chứng cứ đổi trần hoặc kết luận độ dài gây thắng. Không sửa cấu hình.

Nguồn nội bộ: data/analytics/MIM/183/ (videos.json, byvideo_d28.json, video_x_source.json, meta.json, analysis.md).
