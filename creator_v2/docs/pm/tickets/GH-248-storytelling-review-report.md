# GH-248 — Phản biện hướng dẫn storytelling

## Kết luận

**Chưa tối ưu**, vì ba lý do: (1) hướng dẫn khuyến khích cảnh và chi tiết giác quan mà chưa đặt hàng rào chứng cứ, dễ dẫn đến bịa; (2) khuôn cứng cho mở, cú lật và kết dễ làm bài giống nhau, đồng thời xung đột với luật riêng và cổng hiện hành; (3) nhiều luật khó kiểm, thiếu chỉ dẫn cụ thể cho TTS, lời hứa–đáp án và cách đo tác động.

Chẩn đoán CL ghi Short có trung vị quanh 1.000 view, AVP 67–70%; Long có 6.721/8.282 view từ thông báo trong 28 ngày. AVP không có nghĩa mọi người đã xem đều xem hết. Số liệu chưa chứng minh tỷ lệ vuốt hay văn phong là nguyên nhân, cũng chưa chứng minh có ngưỡng phân phối cố định. Cần xem tỷ lệ chọn xem, thời lượng xem, nguồn traffic và cỡ mẫu; văn phong không tự sửa được bao bì Long.

## 1. Thiếu gì?

- **Stakes và góc nhìn:** trong vài câu đầu nêu nhân vật đứng trước trở ngại hoặc lựa chọn gì và điều có thể mất hay được, khi nguồn cho phép. Chọn góc nhìn chính; khi chuyển sang nhân chứng hoặc hồ sơ phải nói rõ. Không tự dựng suy nghĩ, động cơ hay rủi ro không có căn cứ.
- **Show, don't tell:** thay tính từ bằng hành động, quyết định, vật chứng hoặc hệ quả có nguồn. Không bắt buộc tái dựng một cảnh vật lý; hồ sơ không nêu tiếng động, mùi, ánh sáng thì không thêm.
- **Thang cụ thể:** đi từ ý khái quát đến ai làm gì, rồi vật chứng hoặc con số liên quan và hệ quả; chọn mức cụ thể nhất mà nguồn hỗ trợ. Con số cần đơn vị, ngữ cảnh và so sánh thích hợp; làm tròn trong lời nếu không làm sai ý.
- **Payoff/callback:** lập bảng nội bộ lời hứa → bằng chứng → vị trí trả. Trả mọi lời hứa chính trước khi kết hoặc nói rõ chưa biết. Callback có thể là câu hỏi, lựa chọn hoặc hình ảnh cũ, không cần lặp nguyên từ. Short phải tự cung cấp một đáp án hữu ích, không giấu toàn bộ để kéo sang Long.
- **Viết cho TTS:** mỗi câu một ý, tách mệnh đề khó, dùng dấu câu để ngắt tự nhiên; không dùng quá nhiều dấu để ép cảm xúc. Số dài làm tròn, mã và giờ chính xác ưu tiên hiện hình khi không thiết yếu cho lời. Nghe thử bằng đúng giọng/tốc độ dự kiến; nghe riêng số, đơn vị, viết tắt và tên nước ngoài. Ghi cách đọc phù hợp, giữ tên gốc trên màn hình khi cần và không phiên âm sai nhận dạng.
- **Theo kênh:** CL phân biệt dữ kiện, lời khai và điều chưa rõ; MIM giải thích cơ chế qua hệ quả cụ thể trước thuật ngữ khi phù hợp; CK nêu điều kiện, giả định và giới hạn phép so sánh. Nhân vật giả định phải được nhận diện ngay, không trình bày như người thật.

## 2. Sai, rủi ro và mâu thuẫn

1. Ví dụ cảnh đêm, cửa đá, rạng sáng và lời khuyên dùng giác quan có thể khiến agent bịa thời điểm, âm thanh hay tâm trạng. “Phiên tòa lặng lẽ dừng lại” thêm sắc thái không tự suy ra từ việc đình chỉ. Mỗi khẳng định số, ngày, tên cần dòng factcheck và URL đã mở; chi tiết giác quan, động cơ, lời thoại cũng phải có nguồn hỗ trợ. Không có nguồn thì bỏ hoặc trình bày rõ là lời kể/chưa chắc. Ví dụ trong guide cần nguồn hoặc nhãn giả định.
2. “Dẫn người nghe tin một điều, rồi lật” có thể biến thành đánh lừa. Nên nêu nhận định có căn cứ, phân biệt nhận định với sự kiện, rồi đưa chứng cứ sửa hoặc làm rõ. Không dựng đếm ngược, nghịch lý hay câu hỏi chưa có đáp án khi hồ sơ không có.
3. Guide chỉ yêu cầu câu 1 Short là nghịch lý **hoặc** con số; brief series GH-248 yêu cầu ≤9 từ, có số hoặc tên riêng của tiêu đề **và** là mâu thuẫn/nghịch lý; câu 2 cụ thể. Series A/B bắt buộc câu cuối mời xem Long, trong khi guide cho phép bỏ lửng. Đây là luật ticket riêng, không mặc định áp cho mọi kênh.
4. BUD trong `script_lint.py`: R1 cảnh báo/lỗi hook trên 12 từ; R2 tìm từ móc; R4 tìm từ hook ở câu cuối; R5 đòi dấu hỏi cuối; R6 kiểm nhịp và độ dài. `v2` nâng phần lớn vi phạm thành lỗi; thiếu sources R10 là lỗi. Không áp profile BUD máy móc sang CL/CK/MIM; R4/R5 có thể xung đột CTA Long. Trong file này không có hàm hay chuỗi tên `short_retention`; R2 chỉ là phép tìm từ khóa, không chứng minh đã đo retention thực.
5. `opening_gate.py` đã đòi dấu hỏi trong 45 giây, hạn chế ba câu hỏi trong cửa sổ 20 giây thuộc đoạn 36–90 giây, kiểm từ khóa tiêu đề ở 15/20 giây, hình trong 5 giây và tỷ lệ cảnh chữ trống. “Câu hỏi lớn” viết dưới dạng trần thuật không chắc qua cổng. Guide ép cold open 30–40 giây, trong khi chuẩn golden tự mô tả khoảng 60 giây. Mốc lật ở 2/3 và kết về hình đầu chỉ nên là lựa chọn, không phải luật chung.
6. Short 30–40 giây và Long 10–30 phút của guide không thay quy trình Long trong `CLAUDE.md`: 5.500–7.000 âm tiết, 12–14 chương và floor tối thiểu 5.000. “Một tỷ hai” hữu ích trong ngữ cảnh phù hợp nhưng không thể thay mọi số thập phân nếu làm mất nghĩa hoặc độ chính xác.

## 3. Viết lại để kiểm được

Các ngưỡng dưới đây là đề xuất biên tập, chưa chứng minh tối ưu và không thay luật cứng.

| Luật mơ hồ | Cách viết lại, cách kiểm |
|---|---|
| Câu ngắn, một ý | Cảnh báo câu trên 22 từ hoặc đoạn giữa dấu câu trên 14 từ, kế thừa R6 BUD nếu phù hợp; người nghe thử quyết định có tách. Số từ không đo chính xác số mệnh đề. |
| Động từ mạnh | Trong ba câu đầu, người duyệt xác định ít nhất một hành động hoặc lựa chọn có chủ thể; không ép dùng “nổ”, “lật”. |
| Chi tiết giác quan | Chỉ dùng khi nguồn hỗ trợ, đối chiếu factcheck; không có thì dùng hành động hoặc vật chứng đã kiểm. |
| Mỗi chương đóng vòng cũ, mở vòng mới | Lập bảng lời hứa, vị trí mở, vị trí trả và nguồn; mọi lời hứa chính được trả hoặc nói rõ chưa biết. Không ép chương nào cũng mở vòng mới. |
| Câu hai là hành động | Áp đúng ticket series; ở bài khác người duyệt xác định câu hai có thêm sự kiện, lựa chọn hoặc hệ quả cụ thể. Máy không thể xác định đầy đủ bằng danh sách động từ. |
| Cú xoay ở 2/3 | Chỉ dùng khi có chứng cứ làm thay đổi cách hiểu; ghi câu trước/sau và nguồn. Không bắt lỗi khi không nằm ở 2/3. |
| Kết bỏ lửng | Short trả ít nhất một thông tin đã hứa; nếu còn bất định thì nói rõ. Series A/B phải có lời mời Long; bài độc lập có thể kết luận. |
| Cold open 30–40 giây | Chọn độ dài theo chất liệu, đo bằng giọng TTS thực; vẫn tuân thủ opening gate hiện hành. Ước tính chữ không thay timing thật. |

## 4. Chấm mẫu thật và viết lại

Thang 4 điểm: mỗi điểm cho (1) câu đầu cụ thể/mâu thuẫn; (2) diễn tiến có chủ thể và dữ kiện; (3) có thông tin trả lời hoặc chuyển hướng; (4) kết phù hợp guide và luật series nếu áp dụng. Đây là chấm biên tập, không xác nhận nguồn hay hiệu quả. Hai Long chỉ xét khoảng 40 giây đầu, ước tính khoảng 3,5 âm tiết/giây cộng nghỉ, chưa có timing TTS; ranh giới chỉ gần đúng. Không trừ điểm vì đáp án xuất hiện sau đoạn đang xét.

### Short Bao Chửng — 2/4
Hook 9 từ, câu hai cụ thể; phần giữa chuyển từ lệnh cấm sang áo cơm, thư và chuyện con mà thiếu cầu nối với lời hứa; cuối mời Long đúng series nhưng chưa đóng chuyện lời cấm. Viết lại hai câu đầu, giữ thông tin đã có:

> Bao Chửng cấm con cháu nhận hối lộ.
> Ông nói người phạm điều ấy không được chôn vào mộ tổ.

Cần biên tập phần sau để đáp lời hứa; kiểm lại nguồn và không tự coi hai câu là nguyên văn.

### Short Đông Lăng — 4/4
Hook 9 từ, có tên và nghịch lý; diễn tiến theo thời gian, trả lời bằng phiên đình chỉ và kết luận về sư đoàn 12, cuối có CTA Long. Tuy nhiên “không ai bị án” ở hook rộng hơn kết luận về sư đoàn. Đề xuất:

> Nổ mìn lăng, quân Tôn không ai bị án.
> Tháng tư năm sau, phiên tòa tạm đình chỉ.

Câu đầu 9 từ, nhưng “quân Tôn” là cách rút gọn sư đoàn 12 và có thể bị hiểu rộng; phải kiểm tên trong tiêu đề và phạm vi với nguồn trước khi dùng. Không khẳng định cách rút gọn này đã qua cổng.

### Short Mayréna — 3/4
Hook 8 từ, có nghịch lý; có hành động và kết quả. Câu bầu vua hiện đứng trước lời giải thích nhiệm vụ đi thương thuyết, gây khó theo dõi; kết về nguyên nhân chết chưa thống nhất tạo khoảng trống nhưng chưa nối rõ với câu chuyện. Đề xuất đổi thứ tự, giữ dữ kiện:

> Toàn quyền Đông Dương đồng ý để ông thương thuyết với các bộ trong nội địa.
> Ngày ba tháng sáu năm một tám tám tám, các tù trưởng bầu ông ở Con-gung.

Ngày dài cần thử TTS; cân nhắc cho năm hiện hình nếu không cần đọc đủ, và đối chiếu nguồn trước khi dùng.

### Long CK lương hưu — 3/4
Khoảng 40 giây đầu từ “Tháng sáu…” tới gần câu hỏi lựa chọn hai trăm triệu hay lương hưu, tùy nhịp nghỉ. Có nhân vật ví dụ, tình huống và lựa chọn cụ thể; câu hỏi đến sớm. Cần làm rõ số cũng giả định, và lời người bạn là tình huống dựng. Đề xuất:

> Chị Hạnh là nhân vật giả định: chị nghỉ việc sau mười năm ở xưởng may.
> Với mức lương đóng giả định mười triệu, chị tính khoản nhận một lần khoảng hai trăm triệu.

Phải có nhãn “VÍ DỤ GIẢ ĐỊNH” theo luật CK; kiểm điều kiện và phép tính với factcheck trước sử dụng.

### Long MIM Oppenheimer–Feynman — 3/4
Khoảng 40 giây đầu từ “Sa mạc New Mexico…” đến gần câu kính chắn gió. Có người thật, bối cảnh và câu hỏi lớn; tên phim/IP vào sớm. Hai câu đầu thiên về bối cảnh, ngày chính xác làm lời dài, chi tiết giông/kính cần nguồn. Đề xuất:

> Năm 1945, Feynman ngồi sau kính chắn gió một chiếc xe tải ở New Mexico.
> Ông chờ vụ thử Trinity, ở cách tháp thử hơn ba mươi cây số.

Kiểm lại thời điểm ngồi, địa điểm và khoảng cách với nguồn; nếu dùng cách mở này, chạy opening gate để kiểm từ khóa tiêu đề và câu hỏi.

**Golden đối chiếu:** CH00 đưa đoàn la, thuốc phiện, quân truy đuổi rồi máy bay vào chuỗi hành động rõ. Bản này tự mô tả cold open khoảng 60 giây, là lý do không biến mốc 30–40 giây thành bắt buộc. Golden là chuẩn tham chiếu, không tính vào hai Long được chấm.

## 5. Đề xuất tự động hóa

Đây là đề xuất, không sửa hoặc chạy code. Bật theo profile, không thay ngầm cổng đã dùng; kiểm bằng người cho ý nghĩa và chứng cứ.

| Tên / nơi dự kiến | Điều kiện | Mức | Báo nhầm và giới hạn |
|---|---|---|---|
| `SERIES_HOOK_LENGTH` / `script_lint.py` | Chỉ profile series GH-248: câu đầu >9 từ theo tokenizer thống nhất | Lỗi khi bật profile | Tên có gạch nối và số đọc thành chữ làm cách đếm khác nhau; cần test Unicode. R1 BUD >12 không thay thế luật này. |
| `SERIES_HOOK_ANCHOR` / `script_lint.py` | Hook thiếu số hoặc tên riêng được khai báo từ tiêu đề | Cảnh báo | Phiên âm, viết tắt, số bằng chữ, nhiều phương án tiêu đề; máy không hiểu nghịch lý. |
| `SERIES_LONG_CTA` / `script_lint.py` | Series A/B, câu cuối thiếu cụm chỉ bản dài theo cấu hình | Cảnh báo | Có nhiều cách mời tự nhiên; người duyệt xác nhận. Không ép mẫu câu hỏi BUD. |
| `TTS_LONG_CLAUSE` / `script_lint.py` | Câu >22 từ hoặc đoạn giữa dấu câu >14 từ khi profile chưa được áp R6 | Cảnh báo | Tên riêng, số, dấu viết tắt; đếm từ không đo hơi hay mệnh đề. Không nhân đôi R6. |
| `TTS_UNREADABLE` / `script_lint.py` | Có chữ số, viết tắt, ngoặc hoặc gạch chéo trong lời | Cảnh báo | TTS có thể đọc đúng; nghe thử thay vì cấm. R7 BUD đã kiểm tương tự. |
| `OPENING_PROMISE` / `opening_gate.py` | Giữ kiểm tra dấu hỏi trước 45 giây; báo rõ timing thực hay ước tính | Giữ lỗi hiện tại | Câu hỏi tu từ cũng qua, câu hỏi ngầm không có dấu bị báo thiếu; máy không hiểu đây có phải câu hỏi lớn. |
| `CLAIM_TRACE` / công cụ riêng | Cảnh báo số/tên chưa ánh xạ tới dòng factcheck và URL | Cảnh báo | Nhận diện tên khó; URL tồn tại không chứng minh nội dung hay mở được. Người kiểm từng khẳng định. |
| `LOOP_LEDGER` / kiểm dữ liệu kịch bản | Trong bảng lời hứa, mục thiếu vị trí trả hoặc trạng thái chưa rõ | Cảnh báo | Khai sai vẫn qua, vòng ngầm không được phát hiện; lặp chữ không chứng minh đã trả. |

Không tự động kết luận “giật gân”, stakes, cú lật hay sự hài lòng bằng danh sách từ. Thử trên mẫu đã duyệt, thống kê báo nhầm trước khi nâng lên lỗi.

## Ưu tiên P1–P3

| Ưu tiên | Việc | File dự kiến sửa ở ticket sau | Tiêu chí đạt |
|---|---|---|---|
| P1 | Hàng rào nguồn cho giác quan, động cơ, lời kể và ví dụ; ghi nhãn giả định CK | `docs/pm/storytelling-guide.md` | Mẫu sự kiện có nguồn kiểm được hoặc nhãn giả định; hướng dẫn yêu cầu bỏ/nêu bất định khi thiếu chứng cứ. |
| P1 | Phân biệt luật chung, series CL, BUD và cổng Long; bỏ mốc cứng về độ dài mở, cú lật, kết bỏ lửng | `docs/pm/storytelling-guide.md` | Nêu đúng hook/CTA series và cổng Long, không ghi đè quy trình hiện hành. |
| P1 | Thêm stakes có nguồn, bảng lời hứa–trả và TTS; Short tự đứng | `docs/pm/storytelling-guide.md` | Có checklist duyệt, lời hứa chính được trả hoặc nói chưa biết; thử giọng thực trước xuất bản. |
| P2 | Thử lint theo profile, tái sử dụng kiểm TTS hiện có | `motion/stier/script_lint.py`, test tương ứng; `motion/long/opening_gate.py` nếu cần | Không đổi mặc định profile cũ; kiểm Unicode, CTA, ba mẫu CL; đo báo nhầm và Lead duyệt trước khi bật lỗi. |
| P2 | Thử nhiều kiểu mở có kiểm soát | `docs/pm/storytelling-guide.md` và kế hoạch do Lead chỉ định | Ghi mẫu, đo sau 72 giờ, tỷ lệ chọn xem, thời lượng xem, sub/1.000 view và bất định; không kết luận nhân quả từ mẫu nhỏ hoặc thay nhiều biến. |
| P3 | Thử bảng lời hứa và ánh xạ factcheck | `docs/pm/storytelling-guide.md`, công cụ và test chỉ định trong ticket code riêng | Mỗi lời hứa có vị trí mở/trả; thiếu nguồn chỉ báo cảnh báo, người kiểm nội dung URL. |

## Phạm vi và kiểm tra

Đã đọc các tệp theo brief, dùng Python đọc UTF-8 và `rg` tìm `short_retention` trong `script_lint.py`; không thấy hàm hoặc chuỗi tên đó. Không chạy lint hoặc render vì ticket chỉ phân tích; không sửa code, data hay spec. Không mở URL thực tế trong lượt review; các câu viết lại chỉ dựa trên dữ kiện trong mẫu, cần factcheck trước sản xuất. Không đăng, không đổi lịch, không commit.
