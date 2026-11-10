# GH-264 — Báo cáo chốt storytelling-guide v3

## Đã làm

- Ghi đè `docs/pm/storytelling-guide.md` bằng v3, lấy ba vùng, ba lằn ranh, sáu kỹ thuật, ví dụ và checklist của nháp làm khung.
- Bỏ mốc thời gian và phân tầng A/B/C; để người viết tự cân nhắc nội tâm, nhất là với nạn nhân và thân nhân còn sống. Bỏ cấm nội tâm nạn nhân trong bảng CL.
- Vùng 2a không đòi nguồn thứ hai hay lời dè dặt cho bối cảnh chung; vùng 3 chỉ cảnh báo ba kiểu câu khi khẳng định sự kiện cụ thể mới về người thật. Phép thử, bảng vùng và lint là hỗ trợ, không tạo cổng chặn.
- Giữ bảng năm dạng mở và quy tắc đổi dạng giữa các bài liền nhau của v2; giữ phạm vi series GH-248, Short tự trả lời hứa, các luật kênh và cổng hiện hành.
- Thêm mẫu Bao Chửng dùng dữ kiện trong spec và giọng kể 2a/3; không dựng cảnh hấp hối. Thêm kế hoạch ghép cặp v2/v3, đăng xen kẽ và đánh giá AVP, tỉ lệ xem tiếp tại 7 ngày. Đây là đề xuất đo, không thực hiện đăng hoặc đổi lịch.

## Đối chiếu các chỗ chưa kiểm chứng

| Chỗ trong review/nháp | Kết quả |
|---|---|
| V2 và phản biện GH-248 từng không có trong checkout của review | Đã đọc cả hai: v2 có bảng năm dạng mở, quy tắc đổi dạng, phạm vi series và lời hứa–đáp án; giữ các điểm tương thích trong v3. V2 có hàng rào nguồn rộng hơn cho giác quan và suy nghĩ; thay theo quyết định PO về tái dựng. |
| Chín spec chưa có lúc review | Đã đọc trường `lines` của đủ chín bài; các bài có diễn tiến và chi tiết cụ thể, nhưng nhiều bài nối dữ kiện theo dạng liệt kê, vì vậy v3 nhấn giọng kể và nhịp. Đây là nhận xét biên tập, không phải đo hiệu quả. |
| Bao Chửng chỉ có một phần dữ kiện | Đã đối chiếu spec: lời cấm, mộ tổ, Tống sử, không phải lời lúc hấp hối, áo cơm và thư riêng đều có trong spec; các câu về ý nghĩa mộ tổ là bối cảnh/giọng kể sáng tạo. |
| Mốc “khoảng một thế kỷ” và tầng A/B/C | Không dùng: PO giao người viết tự cân nhắc, không chốt mốc hay danh sách. |
| Nguồn lịch sử, số liệu analytics và quy định ngoài repo trong review | Không mở lại URL trong lượt tài liệu này; không xem review hay spec là factcheck mới. Trước khi dùng mẫu để sản xuất, kiểm từng khẳng định và URL theo quy trình hiện hành. Không dùng số analytics chưa kiểm trong guide. |
| Ngưỡng preflight được review đo thủ công | Giữ yêu cầu chạy cổng hiện hành, không khẳng định đã chạy hay áp chung mọi ngưỡng Short cho tất cả profile. Đếm riêng mẫu theo yêu cầu ticket ở phần kiểm bên dưới. |

## Đề xuất đoạn nối nguyên văn

### AGENTS.md — Giọng kể

> **Giọng kể:** Viết lời hấp dẫn, có diễn tiến và nhịp, tránh liệt kê khô cứng.  
> Áp dụng ba vùng trong `docs/pm/storytelling-guide.md`: sự thật có nguồn, bối cảnh tái dựng, giọng người kể.  
> Được sáng tạo bối cảnh chung và giọng kể; không bịa sự kiện, số hay lời trích như sự thật.  
> Không gán tội hoặc tính cách xấu cho người thật thiếu căn cứ; CK không hứa lợi nhuận, giả định phải có nhãn.  
> BUD không gán cho Đức Phật lời hay việc không có trong kinh.  
> Người viết tự cân nhắc nội tâm, đặc biệt với nạn nhân và thân nhân còn sống.  
> Câu tự hỏi và lint văn phong chỉ hỗ trợ; luật nguồn và các cổng hiện hành vẫn áp dụng.

### long-rules.md — Giọng kể

> ## Giọng kể
>
> Viết cho người nghe: có nhân vật, diễn tiến, chi tiết và nhịp; tránh liệt kê cứng, khô. Giữ sự thật đúng nguồn và cho phép sáng tạo cách kể.
>
> | Vùng | Cách dùng |
> |---|---|
> | 1. Sự thật | Kiểm số, ngày, tên, hành động, kết cục và trích dẫn; mỗi khẳng định có số, ngày hoặc tên có dòng factcheck và URL đã mở. |
> | 2. Tái dựng | Được sáng tạo bối cảnh văn hóa chung không cần nguồn thứ hai hay lời dè dặt; cảm giác phỏng đoán cần thể hiện là phỏng đoán. Không dựng sự kiện cụ thể thành sự thật. |
> | 3. Giọng kể | Tự do nhận xét, so sánh, ẩn dụ và nói với bạn; kiểm nguồn nếu câu khẳng định sự kiện cụ thể mới về người thật. |
>
> Không bịa sự kiện, số hay lời trích như sự thật; không gán tội hoặc tính cách xấu cho người thật thiếu căn cứ; CK không hứa lợi nhuận, nhân vật và số giả định phải có nhãn VÍ DỤ GIẢ ĐỊNH. BUD không gán cho Đức Phật lời hay việc không có trong kinh. Tự cân nhắc nội tâm, đặc biệt với nạn nhân và thân nhân còn sống.
>
> Chọn kỹ thuật phù hợp: cái giá với con người; nhịp và khoảng lặng; đối lập nhỏ và lớn; kết bằng ý nghĩa hoặc câu hỏi; đặt bạn vào cảnh; liên hệ đời thường. Đổi dạng mở giữa các bài liền nhau, trả lời lời hứa hoặc nói rõ chưa biết. Làm tròn số cho tai, đọc to và nghe thử TTS.
>
> Tự hỏi câu có thêm sự kiện cụ thể hay gán hành động mới không; đó là trợ giúp biên tập, không phải cổng mới. Theo `docs/pm/storytelling-guide.md` khi brief chỉ định; giữ nguyên luật kênh, nguồn và cổng Long hiện hành.

### Hai dòng cho mẫu brief

> Viết lời kể hấp dẫn theo `docs/pm/storytelling-guide.md` v3; chọn và đổi dạng mở phù hợp, trả lời lời hứa của bài.  
> Tự kiểm sự kiện, nguồn, luật kênh và các cổng hiện hành; bảng vùng là công cụ biên tập tùy chọn, lint văn phong chỉ cảnh báo.

## Kiểm tra

Đã đọc brief, nháp, review GH-262, v2, phản biện GH-248 và chín spec được chỉ định bằng công cụ đọc UTF-8. Python đếm guide 129 dòng; mẫu có 115 từ, câu đầu 9 từ và có tên Bao Chửng trong tiêu đề. Kiểm ký tự thay thế Unicode và các dấu `?`: không có ký tự thay thế, các dấu hỏi là dấu câu. Mẫu chưa chạy `build.py --preflight`, chưa kiểm URL trong lượt này.

Chỉ ghi guide và báo cáo bằng Python UTF-8; không sửa code, spec hay các file nối. Không render hoặc lint vì đây là ticket chỉ tài liệu; không đăng, commit hay đổi lịch.
