# Hướng dẫn storytelling cho kịch bản audio — v2

Viết cho tai: mỗi câu dễ hiểu ngay lần đầu, có chủ thể và một ý chính. Chọn hình thức theo chất liệu; không hy sinh sự thật để tạo hồi hộp.

## Phạm vi và thứ tự áp dụng
| Lớp | Áp dụng | Nguồn gốc |
|---|---|---|
| Nguyên tắc chung | Khuyến nghị biên tập cho mọi kênh; không thay luật hay cổng bắt buộc. | Hướng dẫn này và `AGENTS.md`. |
| Series CL GH-248 | Các Short thuộc lô series được giao: hook tối đa 9 từ, có số hoặc tên riêng của tiêu đề **và** là mâu thuẫn/nghịch lý; câu 2 là hành động hoặc chi tiết cụ thể. Series A/B có câu cuối mời xem Long tự nhiên. | `docs/pm/tickets/GH-248-cl-series-shorts.md`; xem đủ luật cảnh và tiêu đề tại đó. |
| Long hiện hành | Mọi Long: theo quy trình và vượt các cổng hiện hành, kể cả mở bài, nội dung và sàn sản xuất. | `CLAUDE.md`, `motion/long/opening_gate.py`, `motion/long/floor.py`. |
| BUD | Quy tắc và profile BUD chỉ áp cho BUD; không mặc định áp sang MIM, CK hay CL. | `motion/stier/script_lint.py`. |

Khi có luật riêng của ticket hoặc kênh, đọc file gốc và áp đúng phạm vi. Không lấy ví dụ trong guide làm giấy miễn cổng.

## Hàng rào nguồn
- Mỗi khẳng định có số, ngày hoặc tên phải có dòng factcheck và URL đã mở được. Kiểm nội dung nguồn, không chỉ kiểm URL; phân biệt sự kiện, lời khai và điều chưa rõ.
- Giác quan, thời điểm, động cơ, suy nghĩ và lời thoại chỉ dùng khi có nguồn hỗ trợ. Thiếu nguồn thì bỏ; nếu có lời kể chưa được xác nhận, nêu rõ đó là lời kể và mức chưa chắc, không biến thành sự thật. Không bịa trích dẫn; bản dịch ghi `[TRÍCH DỊCH]`.
- CK: nhận diện nhân vật **và** số giả định ngay khi giới thiệu, trên hình có nhãn **VÍ DỤ GIẢ ĐỊNH** đọc được; nêu điều kiện và giới hạn phép so sánh. Không trình bày lời thoại dựng như lời người thật.
- Đảo ngược kỳ vọng: nêu nhận định phổ biến có căn cứ, phân biệt nhận định với sự kiện, rồi đưa chứng cứ sửa hoặc làm rõ. Không dựng bẫy, nghịch lý hay đếm ngược thiếu căn cứ.

## Chọn cách kể
| Công cụ | Khi dùng |
|---|---|
| Stakes và góc nhìn | Nêu trở ngại hoặc lựa chọn và điều có thể được/mất nếu nguồn hỗ trợ; theo một góc nhìn chính, báo rõ khi chuyển sang nhân chứng hay hồ sơ. Không tự gán ý nghĩ, động cơ hoặc rủi ro. |
| Show, đừng chỉ kể | Thay tính từ bằng hành động, quyết định, vật chứng hoặc hệ quả có nguồn. Không tự thêm tiếng động, mùi hay ánh sáng để dựng cảnh. |
| Thang cụ thể | Từ nhận định khái quát → ai làm gì → vật chứng hoặc số có đơn vị, ngữ cảnh → hệ quả. Chọn mức cụ thể nhất nguồn cho phép, không bắt buộc đủ mọi nấc. |
| Mở giữa cảnh, nghịch lý, con số, nhân vật hoặc mốc thời gian | Dùng khi chi tiết có nguồn và giúp hiểu vấn đề; nhân vật CK giả định phải được nhận diện ngay. |
| Cold open ngắn, cú lật muộn, kết mở hoặc callback | Chọn độ dài mở theo nội dung và nghe timing thật; đặt cú lật ở nơi chứng cứ đổi cách hiểu. Kết mở chỉ khi còn bất định và phải nói rõ; callback có thể trở lại câu hỏi, lựa chọn hoặc hình ảnh. Không bắt buộc mốc hay kết cấu cố định; Long vẫn qua cổng mở bài. |

## Năm dạng mở (chọn một, đổi dạng giữa các bài liền nhau)
Mọi ví dụ dưới đây đã có trong video đã kiểm nguồn. Cùng một dạng mở lặp lại nhiều lần liên tiếp sẽ thành khuôn.

| Dạng | Ví dụ đã dùng | Vì sao giữ người nghe |
|---|---|---|
| Nghịch lý | "Bao Chửng cấm con cháu tham ô về nhà." (Tống sử q.316) | Hai điều trái nhau đòi lời giải |
| Con số đặt cạnh cái giá | "Gửi một tỷ hai, ngân hàng phá sản: khoản chắc chắn được trả là ba trăm năm mươi triệu. Phần còn lại thì sao?" | Số cụ thể + khoảng trống người nghe muốn lấp |
| Giữa cảnh có mốc thật | "Sa mạc New Mexico, ngày 16 tháng 7 năm 1945." (giờ nổ theo Bảo tàng Nguyên tử Quốc gia Mỹ) | Thả vào khoảnh khắc trước khi giải thích |
| Nhân vật đại diện (CK, giả định) | "Đóng bảo hiểm mười năm, nghỉ việc, rút một lần được khoảng hai trăm triệu. Hay chờ lương hưu?" + nhãn VÍ DỤ GIẢ ĐỊNH | Người nghe tự đặt mình vào lựa chọn |
| Nhận định phổ biến → hồ sơ | "Phim kể X. Hồ sơ ghi Y." (chỉ khi có nguồn cho cả hai vế) | Sửa một điều người nghe tưởng đã biết |

Nhịp câu: xen câu ngắn (≤ 8 từ) sau một chuỗi câu dài để đánh dấu chi tiết quan trọng; nhịp ba ("Không giấy tờ. Không nhân chứng. Không bản án.") chỉ dùng khi cả ba vế có nguồn.

## Lời hứa và đáp án
Trước khi nộp, lập bảng nội bộ cho từng lời hứa chính; ghi vị trí mở, bằng chứng/nguồn và vị trí trả. Nếu chưa biết, nói rõ giới hạn thay vì giả vờ đã trả. Short phải tự trả ít nhất một thông tin đã hứa, kể cả khi mời xem Long.

| Lời hứa (vị trí mở) | Bằng chứng / nguồn | Vị trí trả |
|---|---|---|
| Tình huống hoặc câu hỏi cụ thể (câu mở) | Dữ kiện đã kiểm và URL trong factcheck | Câu hoặc cảnh trả lời; nếu chưa rõ, nêu điều chưa biết |

## Ví dụ trước / sau
| Mẫu trong phản biện | Trước | Sau và giới hạn |
|---|---|---|
| Short Đông Lăng | “Tôn Điện Anh nổ mìn lăng vua, và không ai bị án.” | “Năm 1928, Tôn Điện Anh lên kế hoạch cướp Đông Lăng.” Nguồn [Sun Dianying](https://en.wikipedia.org/wiki/Sun_Dianying) xác nhận ý này; đối chiếu `data/long/dong-lang/factcheck.md` CH00–CH01. Đây là ví dụ về thu hẹp khẳng định, không mặc định đạt hook series. Nguồn đó hiện không xác nhận chi tiết phiên tòa; kiểm nguồn khác trước khi dùng. |
| Long CK lương hưu | “Chị Hạnh nghỉ việc sau mười năm ở xưởng may.” | “Đây là ví dụ giả định: chị Hạnh nghỉ việc sau mười năm ở xưởng may.” Hiện nhãn **VÍ DỤ GIẢ ĐỊNH**; mọi số tiếp theo cũng phải nói là giả định và kiểm điều kiện, phép tính trước khi dùng. |

## Viết và nghe cho TTS
- Mỗi câu một ý, tách mệnh đề khó, dùng dấu câu cho nhịp tự nhiên; chọn động từ và chủ thể rõ, không ép cảm xúc bằng dấu câu.
- Làm tròn số dài khi không mất nghĩa; giữ đơn vị và ngữ cảnh. Mã tài liệu, giờ chính xác ưu tiên trên màn hình khi lời đọc không cần chính xác đến mức đó.
- Ghi cách đọc tên nước ngoài để TTS đọc đúng; giữ tên gốc trên hình, không phiên âm làm sai nhận dạng. Nghe riêng tên, số, đơn vị và chữ viết tắt.
- Nghe thử toàn bài bằng đúng giọng và tốc độ dự kiến; sửa câu khó nghe, đo timing thực và chạy các cổng áp dụng.

## Checklist duyệt kịch bản — Có / Không
- Mỗi số, ngày, tên có dòng factcheck và URL đã mở, nội dung nguồn hỗ trợ đúng phạm vi?
- Giác quan, thời điểm, suy nghĩ, động cơ và lời thoại có nguồn; lời kể chưa chắc được nêu rõ?
- CK nhận diện ngay nhân vật và số giả định, có nhãn đọc được và điều kiện phép tính?
- Stakes, góc nhìn và hành động hoặc vật chứng đều có căn cứ?
- Nhận định phổ biến và chứng cứ sửa có căn cứ, không dựng bẫy?
- Lời hứa chính có bằng chứng, vị trí trả hoặc nói rõ chưa biết; Short tự trả ít nhất một thông tin?
- Các luật riêng của ticket, kênh và series đã được kiểm đúng phạm vi?
- Long đã theo quy trình và qua các cổng hiện hành; BUD chỉ áp đúng profile?
- Số, đơn vị, mã và tên nước ngoài được viết phù hợp cho lời đọc và màn hình?
- Đã nghe toàn bài bằng đúng giọng, tốc độ dự kiến và sửa chỗ khó nghe?
