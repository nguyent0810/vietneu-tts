# Đề xuất giọng mẫu cho 5 kênh (GH-531, H1)

25/11/2026. File này là báo cáo. Không sửa `docs/pm/giong-mau/*`, không commit, không đăng, không đổi lịch.

Cách đếm chữ: tách bằng khoảng trắng trên lời đọc. Dấu nghỉ `‖` không tính. Đoạn CL, MIM, CK chép nguyên câu trong `data/long/<topic>/ch*.json`. Được cắt câu ở hai đầu. Không sửa chữ bên trong câu. Cửa sổ giữ chân dài khoảng 2% thời lượng, nên vài đoạn thêm câu liền ngay trước hoặc ngay sau lát cắt; chỗ nào thêm đều ghi rõ.

Nguồn số: `data/analytics/long_passages.json`, 56 Long đã đăng của CL, MIM, CK. Sáu video không có views thì bỏ. Views từ vài chục đến vài trăm, số liệu nhiễu. Ưu tiên views từ 50 trở lên, và video có nhiều cửa sổ cùng hướng (hold > 0 là người xem tua lại hoặc ở lại). Hold = 0 vẫn là cửa sổ giảm ít nhất; những cửa sổ ấy không được đưa lên cặp chính.

Lọc thêm, đúng brief: đoạn giữa chương, không lấy mở đầu video, không có lời trích dấu `»` (và không lấy dòng kịch bản đánh dấu trích `q`), không lấy dữ kiện dễ sai theo thời gian (năm nay, biểu phí, bậc thuế, giá vàng, chuỗi ngày của một lần backtest). Mỗi đoạn 80–200 chữ.

## Đề xuất cuối

Đưa vào prompt đúng hai đoạn ưu tiên. Dự phòng chỉ thay khi đoạn ưu tiên trùng đề tài bài đang viết, hoặc khi nghe mù thấy đoạn ưu tiên không đứng được. Không dán cả ba một lúc: nghiên cứu prompt đã ghi mẫu quá nhiều thì model overfit.

| Kênh | Ưu tiên 1 | Ưu tiên 2 | Dự phòng |
| --- | --- | --- | --- |
| CL | Hòa Thân, tòa sách, ch11, 85 chữ | Bao Công, lưỡi bò, ch03, 106 chữ | Đông Lăng, cửa đá, ch05, 106 chữ |
| MIM | Oppenheimer, máy Marchant, ch01, 102 chữ | AlphaGo, nước trông như sai, ch05, 115 chữ | GPU, Mona Lisa bằng bi sơn, ch02, 93 chữ |
| CK | Mua hay thuê, sức chịu đựng, ch06, 99 chữ | Không dám bán, chiếc cân, ch02, 91 chữ | Phiên giao dịch, tám nghìn đồng, ch05, 80 chữ |
| FS | Mẫu mới: bếp và cửa, tuổi Tý | Mẫu mới: ngày dọn, tuổi Sửu | Mẫu mới: cây trước hiên, tuổi Mão |
| BUD | Mẫu mới: chén nước nguội | Mẫu mới: một cái bát | Mẫu mới: tin nhắn chưa gửi |

Sáu đoạn đang nằm trong `docs/pm/giong-mau/{CL,MIM,CK}.md` đều đề nghị thay. Lý do từng đoạn ở cuối mỗi kênh. Vidocq vẫn là tai chủ kênh đã chọn ngày 17/11 cho phần mở; luật mở đã nằm trong prompt. Slot H1 là đoạn giữa chương, lấy từ Long đã đo.

FS và BUD: mẫu soạn mới, cần bên FS/BUD xác nhận bằng số liệu giữ chân. Máy này không có kịch bản hay analytics của hai kênh ấy.

## CL

Bốn video có số, views 235–495, avp quanh 30–37, mỗi video ba cửa sổ hold > 0. Hai video khác (`cl-dich-nhan-kiet`, `cl-hoang-kim-vinh`) không có views, bỏ. Giọng các cửa sổ đo được là giọng đối chiếu hồ sơ với phim: một vật cụ thể, rồi một câu ngắn bẻ cách phim kể. Khô hơn Vidocq và Biggs. Đó là giọng đang giữ người xem trên các Long đã đăng.

### 1. Hòa Thân, hai người trong một tòa sách — ưu tiên 1

- Video: `hoa-than`, id `AxYgjI8rFgg`. Views 495, avp 31,76. Cao views nhất CL.
- Chương 11, giữa chương (câu 21–28 / 38). Cửa sổ 1417–1452s, hold 0,0245, watch 0,237. Cả đoạn nằm trong cửa sổ. Cắt hai đầu để bỏ năm sinh, năm mất và năm 1773.
- 85 chữ.

> Ông không phải một thanh tra đi bắt gian thần mỗi tập. Thanh sử cảo còn ghi Hòa Thân cũng từng làm tổng tài Tứ Khố. Hai người cùng đứng trong một tòa sách. Phim biến họ thành hai chiến tuyến. Lưu Dung, trong hồ sơ, là đồng liêu Bộ Lại. Hai năm cùng một chức không thành một mối thù có biên bản. Nhà Thanh không có chức tể tướng theo nghĩa phim cần. Có Quân cơ. Có Đại học sĩ. Có Thượng thư.

Vì sao cuốn: một cảnh (hai người đứng trong một tòa sách) kề một ý trừu tượng (phim cần hai chiến tuyến). Nhịp cụt ở câu cuối, ba chức danh rơi như ba nhịp. Cái giá của cách kể phim nằm ngay trong câu: hồ sơ có hai người cùng ký, phim cần một cặp dễ nhớ.

Điểm yếu: ít gọi "bạn", ít câu hỏi. Câu "Thanh sử cảo còn ghi" dễ dạy model dẫn tên sách. Hold nhỏ. Trong file có dấu `‖` sau "hai chiến tuyến"; mẫu bỏ dấu ấy, không bỏ chữ.

### 2. Bao Công, lưỡi bò — ưu tiên 2

- Video: `bao-thanh-thien`, id `IVOqSZWHIYY`. Views 424, avp 37,25. Avp cao nhất CL.
- Chương 3, đầu chương (bỏ dòng tên chương). Cửa sổ 235–266s, hold 0,0188, watch 0,447, cửa sổ này cũng ăn sang cuối chương 2. Sáu câu đầu của đoạn dưới đây nằm trong lát cắt. Sáu câu sau là cùng một cảnh, ngay sau lát cắt, để đoạn có ngã rẽ.
- 106 chữ. Không có dấu `»`.

> Một buổi sáng ở huyện Thiên Trường, có người đến báo quan. Con bò của ông bị kẻ lạ cắt mất lưỡi. Nếu bạn là quan huyện, bạn sẽ làm gì? Tìm dấu chân? Tra hỏi hàng xóm? Hay bắt người đi ngang qua? Bao Chửng không làm gì trong số đó. Ông chỉ bảo người chủ bò một câu. Cứ về đi, giết con bò ấy mà bán. Người chủ bò làm theo. Con bò mất lưỡi cũng không sống được bao lâu, nên ông chủ không thiệt thêm nhiều. Ít lâu sau, lại có người đến cửa quan. Lần này là để tố giác.

Vì sao cuốn: vật (con bò, cái lưỡi), câu hỏi, ba nhịp ngắn, gọi "bạn", rồi một lệnh ngược với phản xạ. Cái giá của người chủ bò được nói bằng tiền thiệt, rất cụ thể.

Điểm yếu: nằm ở đầu chương 3, sát mạch chuyển chương, chưa phải giữa chương. Nửa sau chưa được cửa sổ 2% đo trực tiếp. Câu "Cứ về đi, giết con bò ấy mà bán" là lời kể hành động, không có dấu trích; nếu Lead muốn sạch hơn nữa thì cắt từ câu ấy trở đi, đoạn còn lại dưới 80 chữ nên không đủ một mẫu.

### 3. Đông Lăng, cửa đá — dự phòng

- Video: `dong-lang`, id `YZJ5ex6dzA0`. Views 275, avp 29,77.
- Chương 5, cuối chương (câu 30–39 / 39). Cửa sổ 638–672s, hold 0,0667, cao nhất CL, watch 0,300. Cắt câu cuối của cửa sổ vì câu ấy thuộc chương 6 và là một mốc ngày (5/7/1928).
- 106 chữ.

> Đây là một chi tiết đến từ lời kể về sau. Ta giữ nó như một lời kể, không phải một tang vật có số hiệu. Sau đêm ấy, Dụ Lăng đã không còn như cũ. Cánh cửa đá bị phá còn nằm đó. Địa cung ngập nước còn nằm đó. Và sư đoàn đã chuyển sang lăng thứ hai. Với người xem phim, cảnh mở cửa đá là cảnh hồi hộp. Với hồ sơ, đó là một công việc kỹ thuật. Một lăng được xây để không ai vào được. Nó chỉ mở ra bằng thuốc nổ khi người trông giữ không còn quyền ngăn.

Vì sao cuốn: lặp cảnh (cửa đá còn nằm đó, địa cung ngập nước còn nằm đó), rồi đổi nhịp từ phim sang hồ sơ. Cái giá là một công việc kỹ thuật, không phải một cảnh hồi hộp.

Điểm yếu: cuối chương. Xưng "ta". Hai câu đầu dạy giọng "lời kể về sau", dễ thành câu rào. Giữ làm dự phòng vì hold cao và có vật để bám, chưa đủ sạch để đứng ưu tiên 1.

### 4. Đông Lăng, gửi quà

- Cùng video. Chương 8, cuối chương (câu 35–45 / 45). Cửa sổ 991–1024s, hold 0,0625, watch 0,240. Trọn trong lát cắt của chương 8; cắt phần chương 9 (danh sách lời đồn).
- 81 chữ.

> Vì người nhận không cần ngọc. Họ cần cái tiếng của nó. Tôn Điện Anh hiểu điều đó. Hai món được nhắc nhiều nhất là Cửu Long Bảo Kiếm và Dạ Minh Châu. Lệnh gọi ông về Nam Kinh đang treo trên đầu. Giữ báu vật bên mình là giữ bằng chứng. Đem chúng đi cho người khác thì khác. Theo các bản kể, ông chọn cách thứ hai. Ông không chạy. Ông không đối chất. Ông chọn cách gửi quà.

Vì sao cuốn: đổi nhịp rất rõ. Ba câu cụt đóng đoạn. Cái giá của việc giữ báu vật được nói trước, bằng một lệnh đang treo.

Điểm yếu: cuối chương. "Theo các bản kể" là câu rào. Không gọi "bạn". Nhịp hay, căn cứ giữ chân tốt, kém một bậc so với cửa đá vì ít cảnh giác quan hơn.

### 5. Bao Công, ô bồn

- Cùng video Bao Công. Chương 11, giữa chương. Cửa sổ 1191–1222s, hold 0,0182, watch 0,303. Bốn câu đầu nằm trong cửa sổ. Ba câu sau liền ngay đó.
- 87 chữ.

> Mỗi thế kỷ, truyện về ông lại dày thêm một lớp. Ví dụ thứ hai là vụ "Ô bồn". Một thương nhân bị giết, hài cốt bị nung thành một chiếc bồn đen. Chiếc bồn mang hồn người chết đến kể với quan. Đó cũng là một vở tuồng đời Nguyên, chứ không phải biên bản của tòa án thời Tống. Vụ "mèo đổi thái tử" thì xoay quanh một người có thật. Đó là Lưu Thái hậu, mẹ nuôi và người nhiếp chính của Nhân Tông.

Vì sao cuốn: một vật (chiếc bồn) rồi một câu bẻ (tuồng, không phải biên bản).

Điểm yếu: có hình hài cốt. Luật kênh cấm tả máu me. Không đưa đoạn này vào prompt. Ghi ở đây để thấy cửa sổ ấy giữ chân bằng vật và bằng cú bẻ, cùng họ với tòa sách và cửa đá.

Đã bỏ các cửa sổ dày năm và dày số: gia tài Hòa Thân (1,1 tỷ lạng, 60 triệu lạng), tiểu sử Kỷ Vân 1724–1805, án văn tự Lưu Dung năm 1778. Những đoạn ấy có hold, và chúng là đúng loại dữ kiện dễ sai thời gian, dễ bị model chép sang bài khác.

### Mẫu CL hiện tại

Ví dụ 1, Vidocq, đoạn mở, chủ kênh chọn 17/11. **Thay.** Đoạn ấy có xương đúng hồ sơ kênh: từ định chế, rồi một cảnh, rồi câu hỏi về cái giá. Nó đứng sai slot H1. Nó là mở đầu video. Nó đặc các mốc 1796, 1811, 1812. Prompt đã cấm chép cấu trúc mở; để chính cấu trúc ấy trong few-shot thì lệnh cấm yếu đi. Video không có trong tệp 56 Long.

Ví dụ 2, Biggs, chương 3, khoảng 92 chữ, cảnh phòng xử, gọi "bạn", cái giá là phần đời còn lại. **Thay** khỏi cặp chính. Tai của đoạn này điện ảnh hơn các cửa sổ đã đo, và nó là cảnh `[PD]` của người đã mất, hợp luật phóng tác. Nó không có dòng views, avp, hold trong `long_passages.json`. H1 của lượt này lấy mẫu từ Long đã đo. Nếu nghe mù mà chủ kênh vẫn chọn Biggs, tai chủ kênh thắng; file này không tranh việc ấy.

## MIM

Nhóm views từ 50 trở lên có nhiều video giữ chân dương cả ba cửa sổ. Avp cao không đi cùng views cao. `mim-may-choi-game` có views 354 nhưng avp 13,51 và watch của cửa sổ chỉ khoảng 0,10–0,14: hold dương trên một nhóm còn lại rất mỏng, không lấy. `mim-ai-voice` views 461, cửa sổ là lời khuyên "gấp, giấu, tiền" và thiệt hại "mười một tháng đầu năm 2025": đúng dữ kiện dễ cũ, và có câu "cuối video". Không lấy.

### 1. Oppenheimer, máy Marchant — ưu tiên 1

- Video: `mim-oppenheimer-feynman`, id `UOpyEIWnm6A`. Views 97, avp 60,09. Avp cao trong nhóm views từ 50. Watch của cửa sổ này 0,66.
- Chương 1, giữa chương (câu 24–33 / 38). Cửa sổ 172–200s, hold 0,1613. Trọn trong cửa sổ. Không phải mở đầu video (mốc 172s trên video 1431s).
- 102 chữ.

> Và cậu trẻ này cãi, chẳng cần biết mình đang nói với ai. Ngày đầu tiên, họ cần bình phương của bốn mươi tám. Feynman với tay sang chiếc máy cộng quay tay hiệu Marchant. Bethe nhanh hơn. Ông nói: khoảng hai nghìn ba trăm. Muốn chính xác thì là hai nghìn ba trăm linh bốn. Máy ra đúng con số ấy. Bethe có mẹo riêng cho những số gần năm mươi. Từ đó, hễ phải tính gì, hai người lại đua nhau tính nhẩm. Feynman kể ông thường thua, mãi vài năm sau mới thắng được chừng một lần trong bốn.

Vì sao cuốn: một vật trên bàn (máy cộng quay tay), hai người, nhịp cụt "Bethe nhanh hơn", rồi một con số có nghĩa. Cái giá của việc thua cuộc đua nhẩm được nói ở câu cuối, rất nhỏ và rất người.

Điểm yếu: views 97, nhiễu còn lớn. "Ông nói:" là lời kể lại của người đã mất, không có dấu `»`. Nếu Lead muốn sạch trích, đoạn này yếu hơn các đoạn không có lời nói. Giữ ưu tiên 1 vì avp, hold và cảnh đứng cùng nhau.

### 2. AlphaGo, nước trông như sai — ưu tiên 2

- Video: `mim-alphago-lee-sedol`, id `nbNu6xYtoYg`. Views 100, avp 43,69.
- Chương 5, giữa chương (câu 22–28 / 37). Cửa sổ 463–486s, hold 0,138, watch 0,475. Trọn trong cửa sổ. Cắt trước câu họp báo của Lee Sedol, vì đó là lời nói lại.
- 115 chữ.

> Nó nối những đám quân đen lại với nhau, như thể đã được đặt sẵn từ trước. Về cuối ván còn một chuyện lạ nữa. AlphaGo đi vài nước trông rất lỏng tay, tới mức bình luận viên tưởng nó đánh sai. Bạn còn nhớ chi tiết mình dặn chứ? Nó không cố thắng đậm. Một người trong nhóm làm ra nó giải thích bằng một ví dụ. Giữa chín mươi chín phần trăm thắng với cách biệt một điểm rưỡi, và tám mươi phần trăm thắng với cách biệt hai mươi điểm, nó sẽ chọn cái đầu. Những nước trông như sai ấy, thật ra là lời tuyên bố rằng ván cờ đã xong.

Vì sao cuốn: gọi "bạn", rồi một cú đổi nghĩa. Nước trông sai trở thành câu tuyên bố. Có ví dụ số, và câu ngay sau nói số ấy nghĩa là gì. Khác đề tài với Oppenheimer, nên hai mẫu không khóa model vào một câu chuyện.

Điểm yếu: "Bạn còn nhớ chi tiết mình dặn chứ?" dễ dạy callback rỗng. Câu phần trăm dài. Views 100. Vẫn hơn Mona Lisa ở chỗ giữa chương và hold cao hơn.

### 3. GPU, Mona Lisa bằng bi sơn — dự phòng

- Video: `mim-ai-gpu`, id `Es4bogrdk-c`. Views 300, avp 32,38. Views cao hơn hai đoạn trên, ít nhiễu hơn.
- Chương 2, cuối chương (câu 20–25 / 25). Cửa sổ 224–239s, hold 0,0792, watch 0,369. Bốn câu sau nằm trong cửa sổ. Hai câu đầu (sự kiện năm 2008) liền ngay trước, để đủ 80 chữ.
- 93 chữ.

> Năm 2008, ở một sự kiện của chính Nvidia, hai người dẫn chương trình MythBusters đã dựng cảnh này bằng súng bắn bi sơn. Cỗ máy thứ nhất bắn từng viên một, chậm rãi vẽ một hình đơn giản. Cỗ máy thứ hai có một nghìn một trăm nòng, bắn cùng một lúc. Chưa tới một phần mười giây, bức Mona Lisa hiện ra trên tấm toan. Từng viên bi là một điểm ảnh. Và chẳng bao lâu, có người tự hỏi: nếu thay điểm ảnh bằng những con số khác thì sao?

Vì sao cuốn: một hình thay cho một ý kỹ thuật. Câu hỏi cuối mở sang GPU mà không giảng thuật ngữ. Đúng kiểu "câu đặc rồi một vật" mà nghiên cứu prompt đã ghi ở H4.

Điểm yếu: cuối chương. Có mốc năm 2008. Hold thấp hơn AlphaGo. Để dự phòng khi bài đang viết đụng Oppenheimer hoặc cờ vây, và khi cần một mẫu có views đỡ nhiễu hơn.

### 4. Oppenheimer, thẻ đục

- Cùng video Oppenheimer. Chương 6, giữa chương (câu 19–28 / 31). Cửa sổ 715–744s, hold 0,0715, watch 0,596. Cắt câu "Bạn còn nhớ chớp sáng ở đầu video chứ?" ở đầu cửa sổ.
- 112 chữ.

> Người vận hành máy là lính của Đội Kỹ sư Đặc biệt. Quân đội chọn họ khắp nước vì có năng khiếu kỹ thuật, rồi đưa lên núi. Họ đục lỗ lên thẻ những con số mà không ai giải thích là số gì. Họ chỉ biết đục. Feynman cho rằng chỗ tắc thật nằm ở đó. Không phải ở máy. Ông xin Oppenheimer, và được phép giảng cho họ biết họ đang làm gì. Theo lời Feynman, cả nhóm như bừng tỉnh: giờ họ biết mình đang góp sức vào cuộc chiến. Áp suất ra cao hơn nghĩa là năng lượng thoát ra nhiều hơn. Những con số bỗng có nghĩa.

Vì sao cuốn: nhịp cụt "Họ chỉ biết đục", rồi cái giá của việc không được biết mình đang tính gì. Cảnh phòng máy, không phải bài giảng.

Điểm yếu: cùng một video với ưu tiên 1. Cặp mẫu cần hai đề tài. "Theo lời Feynman" là câu dẫn. Giữ trong danh sách ứng viên, không đưa vào cặp.

### 5. Ảo giác, máy sai rồi đổ cho người hỏi

- Video: `mim-ai-hallucinate`, id `H9nlRjxfmPw`. Views 135, avp 42,79.
- Chương 6, giữa chương. Cửa sổ 558–574s, hold 0,0269, watch 0,346. Bốn câu sau nằm trong cửa sổ. Câu hỏi mở liền ngay trước. Cắt phần Giáo hoàng và ngày 21/4/2025, vì đó là dữ kiện dễ sai thời gian.
- 85 chữ.

> Một câu hỏi khác: vì sao các phi hành gia NASA bị kẹt ngoài không gian? Hai phi hành gia lẽ ra chỉ ở trạm vũ trụ quốc tế tám ngày, đã phải ở lại hơn chín tháng, vì tàu của họ trục trặc. Một trợ lý trả lời rằng các phi hành gia NASA không hề bị kẹt, rồi nhắc người hỏi: Có lẽ bạn đang nhầm với một bộ phim khoa học viễn tưởng. Máy sai. Rồi bảo người đúng là đang nhầm.

Vì sao cuốn: đổi nhịp ở hai câu cụt cuối. Cái giá là máy sai mà vẫn chắc.

Điểm yếu: hold là cửa sổ yếu nhất của video này. Chi tiết tám ngày và chín tháng dễ bị chép nhầm sang bài khác. Thua AlphaGo và Mona Lisa nên không vào cặp.

Đã xem thêm, không đưa vào năm ứng viên: Jobs "trong nhà máy" (cuối chương, câu dẫn một bài nghiên cứu), captcha "một dấu tick" (đầu chương, "Theo Google"), Doraemon trong `mim-ai-70` (có "tới hôm nay" và mốc Nobel tháng 10/2024).

### Mẫu MIM hiện tại

Ví dụ 1, Air Canada, chương 2, khung chat như chiếc quầy. **Thay.** Ví von đúng giọng kênh, có "bạn", không dính "năm nay". Video không có trong tệp 56. Không có views, avp, hold để đặt nó trên các cửa sổ đã đo.

Ví dụ 2, Knight Capital, chương 2. **Thay.** Có "bạn" và một cuộc chạy đua trước tiếng chuông mở cửa. Trong đoạn có mốc "mùng một tháng tám năm hai nghìn mười hai". Cùng lý do: không có dòng giữ chân trong tệp này.

## CK

CK là kênh khó nhất trong tệp. Video ngắn, cửa sổ 2% thường dưới 80 chữ. Nhiều cửa sổ hold cao lại là giá, thuế, "năm nay", hoặc chữ "phẩy" trong lời đọc. Những đoạn ấy bị loại dù hold đẹp, vì few-shot sẽ chép số cũ và dạy máy đọc "phẩy". Video `ck-e5-thue-tncn-2026` có avp 73,18 và hình bậc thang nước rất đúng giọng, nhưng các bậc triệu đồng và phần trăm là luật dễ đổi. Không đưa vào mẫu. Video `ck-c6-gia-tran-san-t2` avp 71,16, lời chỉ vào ô trên hình ("ô T cộng không"). Prompt cấm kiểu "như bạn thấy trên màn hình". Không lấy.

### 1. Mua hay thuê, sức chịu đựng — ưu tiên 1

- Video: `ck-b1-mua-hay-thue`, id `pXKfIo_nyVM`. Views 133, avp 38,06.
- Chương 6, cuối chương (câu 16–21 / 21). Cửa sổ 679–695s, hold 0,1109, watch 0,281. Bốn câu đầu nằm trong cửa sổ (82 chữ). Hai câu cuối liền ngay sau, là chỗ đoạn gọi "bạn". Cắt phía trước vì có "năm học này" và một dòng trích bài báo (`q`).
- 99 chữ. Không có chữ "phẩy".

> Nên trước khi tin rằng phải mua nhà thì con mới có chỗ học, hãy đọc kế hoạch tuyển sinh của phường mình. Thứ tư là sức chịu đựng. Khi bảy phần mười thu nhập đã dành để trả nợ, một lần mất việc hay một trận ốm dài sẽ nặng hơn nhiều so với lúc đi thuê. Ngược lại, người thuê dễ chuyển theo việc làm, theo trường của con, nhưng sống với cảm giác chưa có chỗ của riêng mình. Không cột nào trong bảng tính đo được cảm giác ấy. Chỉ bạn tự cân được thôi.

Vì sao cuốn: tiền của người nghe, rồi cái giá nằm ngoài bảng (mất việc, ốm, cảm giác chưa có chỗ của mình). Gọi "bạn" ở câu chốt. Đúng hồ sơ CK: gần, không hô mua bán, không hứa lãi.

Điểm yếu: "Thứ tư" là mắt xích của một danh sách. Cuối chương. "Bảy phần mười" là ngưỡng trong bài tính của video, model có thể chép như một quy tắc. Vẫn là đoạn CK sạch nhất trong các cửa sổ hold dương.

### 2. Không dám bán, chiếc cân lệch — ưu tiên 2

- Video: `ck-d3-lo-khong-dam-ban`, id `7K1zP3ZdabQ`. Views 180, cao nhất CK, avp 29,86.
- Chương 2, nửa sau của chương ngắn (15 câu). Cửa sổ 186–195s, hold 0,0385, watch 0,325. Ba câu cuối nằm trong cửa sổ. Hai câu hỏi và câu "Odean cũng đã kiểm tra" liền ngay trước. Cắt các câu có "phẩy" (14,8 và 9,8) và câu "ở đầu video".
- 91 chữ.

> Nhưng biết đâu họ có lý do chính đáng thì sao? Odean cũng đã kiểm tra điều ấy. Theo nghiên cứu, hành vi này không giải thích được bằng việc cân bằng lại danh mục, cũng không phải để tránh phí giao dịch. Và trong dữ liệu của ông, những cổ phiếu lãi đã bị bán đi, về sau lại không hề kém hơn những cổ phiếu lỗ được giữ lại. Chiếc cân lệch không chỉ nằm trong phòng thí nghiệm. Nó nằm trong tài khoản thật của hàng nghìn người.

Vì sao cuốn: một câu hỏi, rồi một hình (chiếc cân) đặt vào tài khoản thật. Cái giá của việc chốt lãi sớm được nói bằng kết quả về sau, không bằng lời khuyên mua bán.

Điểm yếu: avp 29,86, thấp hơn nhiều video CK khác. "Theo nghiên cứu" dễ dạy giọng bài báo. Hold của cửa sổ này nhỏ hơn cửa sổ đầu chương (0,0714), nhưng cửa sổ đầu là câu đặt tên hiện tượng năm 1985, đặc năm và đặc chức danh. Khác đề tài với chuyện mua nhà, nên đứng được cạnh ưu tiên 1.

### 3. Phiên giao dịch, tám nghìn đồng — dự phòng

- Video: `ck-c2-phien-giao-dich`, id `S_oMZt36W60`. Views 81, avp 53,85.
- Chương 5, cuối chương. Cửa sổ 563–577s, hold 0,0435, watch 0,469. Ba câu đầu của đoạn nằm trong cửa sổ. Câu cuối liền ngay sau để đủ 80 chữ. Cắt câu "giả sử phí không phẩy mười lăm phần trăm" và cắt dòng trích luật (`q`) có "một tháng bảy năm nay".
- 80 chữ.

> Mua một trăm cổ phiếu giá hai mươi nghìn, rồi bán lại đúng hai mươi nghìn: bạn mất tám nghìn đồng phí và thuế. Bán cao hơn một bước giá, ở hai mươi nghìn không trăm năm mươi, vẫn lỗ khoảng ba nghìn. Phải lên hai bước, tới hai mươi nghìn một trăm, mới bắt đầu có lãi, chừng hai nghìn đồng. Số tiền nhỏ, nhưng như bài một đã tính, nó lớn dần theo số lần bạn mua bán.

Vì sao cuốn: tiền trong ví người nghe, từng bước giá, "bạn" ở câu đầu. Số đã là câu nói, không có chữ "phẩy".

Điểm yếu: cuối chương. Câu "giả sử" bị cắt cùng với chữ "phẩy", nên đoạn dễ nghe như biểu phí thật. "Như bài một đã tính" là callback sang video khác. Mức tám nghìn đồng sẽ cũ. Chỉ dùng khi hai đoạn ưu tiên trùng đề tài, và Lead nên thêm bằng miệng rằng đây là ví dụ giả định, không ghi thêm chữ vào giữa câu.

### 4. Đường trung bình, quả cầu pha lê — không đưa vào cặp

- Video: `ck-c4-duong-trung-binh`, id `Ss_unzSu7DY`. Views 137, avp 61,62, cao trong nhóm views từ 100.
- Chương 5, đầu chương. Cửa sổ 463–474s, hold 0, watch 0,575. Hold bằng 0: giảm ít nhất, không phải tua lại. Cắt câu sau vì có "phiên ba tháng tư năm hai nghìn không trăm hai mươi lăm".
- 98 chữ nếu lấy từ câu đầu.

> MA không phải quả cầu pha lê. Nhưng nó cũng không vô dụng. Nó là một cách tóm tắt, giống điểm trung bình học kỳ. Thứ nhất, nó lọc bớt nhiễu. Nhìn biểu đồ ngày, mắt dễ bị cuốn theo từng phiên tăng giảm. Một đường trung bình giúp bạn thấy hướng đi chung của vài tháng. Thứ hai, nó cho bạn một mốc để tự hỏi. Giá đang cách đường trung bình xa hay gần, đi lên hay đi xuống đã bao lâu? Còn khi nào nó dễ sai? Khi thị trường đi ngang, vì cắt giả.

Vì sao đáng đọc: ví "điểm trung bình học kỳ" là đúng giọng CK, có "bạn", có câu hỏi.

Vì sao không chọn: hold = 0, đầu chương, và chữ "MA" sẽ bị TTS đọc sai, đồng thời dạy model viết tắt. Cắt câu đầu thì "Nó" không còn chỉ vào đâu. Để trong hồ sơ này như phương án đã cân, không phải mẫu.

### 5. Cô Đều, tám tháng vẫn lỗ — không đưa vào cặp

- Video: `ck-e1-mua-deu-moi-thang`, id `a45PR7ejNgk`. Views 81, avp 25,73. Hold cửa sổ 0,1665, cao nhất CK, watch chỉ 0,20.
- Chương 4. Cửa sổ 316–327s. Phần hold dương, nếu cắt hết mốc ngày, chỉ còn khoảng 60 chữ. Nối thêm cho đủ chữ thì dính "sáu tháng một năm hai nghìn không trăm hai mươi hai" và các mức triệu đồng của lần chạy số ấy.

Nhịp "Tám tháng, tháng nào cũng nộp thêm ba triệu, và tháng nào mở ra cũng thấy lỗ" rất đúng giọng. Dữ kiện thời gian quá dày để làm few-shot. Không chép đoạn vào file mẫu.

### Mẫu CK hiện tại

Ví dụ 1, vay ký quỹ 10 triệu, chương 2, ngưỡng gọi nộp tiền đứng sát sau lưng. **Thay.** Giọng đúng: chỉ số đầm hơn cổ phiếu riêng, cái giá áp vào người vay. Không có "năm nay", không có "phẩy". Video `ck-c9-vay-10-trieu-margin` không có trong tệp 56. Không có căn cứ giữ chân để giữ nó trên đoạn sức chịu đựng.

Ví dụ 2, nâng hạng FTSE, chương 6, tiền chủ động như người đi chợ. **Thay.** Đây là ví đời thường sạch nhất trong sáu mẫu mắt Lead đã chọn. Video `ck-c11-ftse-nang-hang` cũng không có trong tệp 56. Cặp mới lấy hai đoạn đã đo, cùng việc: một hình đời thường kề một cái giá tính được. Nếu nghe mù mà "người đi chợ" vẫn hơn chiếc cân, đó là kết quả lượt nghe, chưa có trong tệp analytics này.

## FS

Không có kịch bản và không có analytics trên máy này. Phần dưới là nghiên cứu công khai, rồi mẫu soạn mới. Mẫu soạn mới, cần bên FS/BUD xác nhận bằng số liệu giữ chân.

Hồ sơ kênh trong `docs/pm/prompt-viet-loi.md`: giọng truyền thống, ấm; nói "theo cách tính dân gian / theo truyền thống"; gọi con giáp bằng tên chi; không phán chắc điều xấu. Prompt chung vẫn gọi người nghe là "bạn". Các kênh lớn thường xưng "quý vị" và hay khóa cát hung trên tiêu đề. Mẫu dưới đây giữ "bạn" và tên chi, không học lời phán.

### Kênh đã mở, 25/11/2026

Không gọi YouTube API. Trang xem trực tiếp chỉ trả tên kênh. Quy mô và mô tả lấy từ bản trang kênh truy được trong lượt tìm cùng ngày. Không có transcript, nên chưa khẳng định nhịp câu bên trong video.

1. Thầy Phong Thủy Tam Nguyên, https://www.youtube.com/@ThầyPhongThủyTamNguyên/playlists . Khoảng 502.000 người đăng ký. Playlist tách theo việc: phong thủy dương trạch, tứ trụ và vận hạn từng tuổi, vật phẩm, động thổ, trấn trạch. Kênh có hotline và trang bán khóa học, vật phẩm. Kỹ thuật nhìn thấy: một việc nhà hoặc một tuổi mỗi lần. Có nhánh chào hàng. Mẫu của mình không học nhánh ấy. Tin cậy: vừa cho quy mô và cách chia mục, thấp cho câu chữ.

2. Kênh Tử Vi, https://www.youtube.com/@kenhtuvi . Khoảng 494.000 người đăng ký. Phần giới thiệu hướng tới người trẻ và phong tục ông cha. Tiêu đề dạng một tuổi, một năm, gọi bằng can chi (Giáp Tuất 1994, Quý Dậu 1993). Playlist tâm linh mở bằng một chuyện nhà rồi mới tới bài học. Kỹ thuật: đơn vị kể là một tuổi và một việc. Tiêu đề thường hứa cát hoặc hung. Mình lấy đơn vị và tên chi. Tin cậy: vừa.

3. TỬ VI TƯỚNG SỐ, https://www.youtube.com/channel/UCWhAGiisZ8l-jlANPY8SP5Q . Khoảng 362.000 người đăng ký. Giới thiệu: mười hai con giáp, âm dương ngũ hành, lá số theo giờ ngày tháng năm sinh, xem để chuẩn bị cho công việc, tiền, tình, sức. Kỹ thuật: chuỗi theo chi và theo kỳ. Tin cậy: vừa cho lời giới thiệu, thấp cho nhịp nói.

4. Phong Thủy 100 Năm, khoảng 48.500 người đăng ký, không thuộc nhóm lớn. Tiêu đề dạng xung khắc, tang thương, ly hôn. Ghi để tránh: phán chắc một điều dữ cho một cặp tuổi. Tin cậy: vừa cho kiểu tiêu đề.

Gộp lại, cách kể đang chiếm chỗ trên YouTube tiếng Việt ở ngách này là: mở bằng một tuổi hoặc một việc trong nhà, gọi tên chi, nói như người chỉ cho xem, và rất hay khóa kết luận tốt xấu ngay từ tiêu đề. Giọng FS của xưởng lấy nửa đầu. Nửa sau thì ngược lại: nói theo truyền thống, để người nghe tự xem, không chốt điều xấu.

### Mẫu mới

Ưu tiên 1, bếp và cửa, tuổi Tý. 166 chữ.

> Bạn để ấm nước trên bếp, rồi đi ra cửa trước một lúc. Theo cách tính dân gian, bếp là chỗ lửa ở, cửa là chỗ gió vào. Tuổi Tý, người ta thường kể là hợp với chỗ kín và gần nước hơn là hợp với cửa đón gió thẳng. Bạn đừng vội dời cả căn bếp vì một câu ấy. Truyền thống chỉ bảo bạn dừng lại, nhìn hai thứ đang có: lửa có bị gió thổi lệch không, và người nấu có phải đứng xoay lưng ra cửa không. Nếu có, cái giá không phải là một tai họa đã chốt. Cái giá là mỗi bữa cơm bạn nấu trong một tư thế khó chịu, lâu rồi cũng thành mệt. Hãy thử một việc nhỏ trước. Xoay người. Hoặc che một khoảng gió. Rồi để vài ngày, xem nhà có dễ thở hơn không. Bạn vẫn là người quyết. Con giáp chỉ là một cách gọi để bạn nhớ mình đang đứng ở đâu.

Ưu tiên 2, ngày dọn, tuổi Sửu. 159 chữ. Khác việc với mẫu bếp, để hai mẫu không cùng một căn phòng.

> Tuổi Sửu, theo truyền thống, người ta hay ví với việc chậm mà chắc, như người kéo một xe nặng qua sân. Khi bạn tính chuyện dời bàn thờ, hoặc dọn một phòng đã ở lâu, dân gian thường khuyên chọn ngày mà người trong nhà đều rảnh, không phải ngày làm cho xong. Cách tính ấy không bắt bạn phải sợ một ngày trên lịch. Nó chỉ nói: việc nặng mà làm lúc người mệt thì dễ sơ suất. Bạn nhìn lại cái giá rất cụ thể. Một bát hương đặt lệch. Một thùng đồ để chắn lối đi cả tuần. Một người già trong nhà phải đứng chờ vì bạn muốn tranh thủ buổi trưa. Hãy hỏi một câu trước khi chọn ngày. Ai sẽ khuân, và ai cần được ngồi? Nếu câu trả lời còn trống, ngày đẹp trên lịch cũng chưa phải ngày của nhà bạn. Truyền thống để nhắc việc, không để dọa bạn.

Dự phòng, cây trước hiên, tuổi Mão. 165 chữ.

> Tuổi Mão, cách gọi dân gian thường đi với cửa và với những thứ mọc lên phía trước nhà. Bạn ra hiên, nhìn cây đang đứng đó. Theo truyền thống, một cây quá sát cửa không bị kết tội. Người ta chỉ hỏi nó có che mất ánh sáng buổi sáng không, và người ra vào có phải né không. Nếu lá rụng đầy bậc, cái giá là mỗi sáng bạn bước qua một bậc trơn. Không phải một lời đã phán. Bạn có thể cắt một nhánh, hoặc chuyển chậu ra xa cửa một bước. Rồi để ý vài hôm. Nhà có sáng hơn không. Chỗ đứng có rộng hơn không. Con giáp ở đây là cái tên để bạn nhớ hướng mình đang nhìn. Nó không thay cho mắt bạn. Nếu ai nói chắc một điều dữ cho tuổi Mão chỉ vì một cái cây, bạn cứ để câu ấy ở ngoài cửa. Truyền thống ở đây chỉ nói điều bạn xem được.

Mẫu thứ tư, chỗ ngồi, tuổi Thìn. 142 chữ. Cùng họ với mẫu bếp (một chỗ trong nhà, thử một việc nhỏ), nên không đưa vào cặp khi đã có Tý và Sửu.

> Tuổi Thìn, dân gian hay kể là thích chỗ có thể nhìn ra, không thích ngồi với lưng kê vào lối người đi qua. Bạn thử ngồi vào bàn của mình một lúc, không sửa gì. Theo cách tính truyền thống, chỗ ngồi là một phần của nhà, nhỏ thôi, nhưng ngày nào bạn cũng ở đó. Nếu mỗi lần có người bước vào là bạn giật mình xoay lại, cái giá là sự chú ý bị cắt. Không phải một vận đã điểm tên bạn. Hãy thử xoay ghế sao cho cửa nằm trong khóe mắt, rồi làm một buổi. Bạn có đỡ ngẩng đầu hơn không. Nếu không khác, trả ghế về chỗ cũ. Một con giáp không đủ lý do để mua bàn mới. Nó chỉ đủ lý do để bạn thử một thế ngồi, rồi tự kết luận.

## BUD

Cùng điều kiện với FS: mẫu soạn mới, cần bên FS/BUD xác nhận bằng số liệu giữ chân. Hồ sơ kênh: giọng tĩnh, chữa lành. Lời Phật chỉ gán khi có kinh trong bảng dữ kiện. Trong mẫu thì tránh trích kinh. Bốn đoạn dưới không có câu nào gán cho Đức Phật, không nêu tên kinh.

### Nguồn đã mở

1. Báo Pháp Luật Việt Nam, 27/06/2024, đã mở toàn bài: https://baophapluat.vn/chia-se-tu-trai-tim-50-bai-giang-nhan-qua-hay-nhat-cua-thay-thich-phap-hoa-post516901.html . Bài giới thiệu sách *Chia sẻ từ trái tim*, 50 bài giảng của thầy Thích Pháp Hòa. Cách kể được mô tả trong bài: chuyện trong đời tu hoặc chuyện một người đến hỏi, ví dụ việc hằng ngày, giọng giản dị, rồi người nghe tự đối chiếu. Bài có trích lời thầy. Mình không chép các câu ấy vào mẫu. Tin cậy: vừa cho cách kể, không có số giữ chân. Bài là giới thiệu sách.

2. Kênh Pháp thoại Thầy Pháp Hòa, số liệu vidIQ ngày 24/11/2026: khoảng 1,68 triệu người đăng ký, khoảng 168 triệu lượt xem, video dài một đến hai giờ. Kênh tổng hợp "Nghe Pháp Thầy Thích Pháp Hòa" khoảng 1,3 triệu người đăng ký. Một video tổng hợp dạng nghe khi ngủ, trên kênh bài giảng, khoảng 1,4 triệu lượt xem. Tiêu đề công khai xoay một nỗi đời: khó ngủ, nóng giận, biết đủ, cái tôi. Kỹ thuật nhìn từ tiêu đề và từ bài báo ở trên: mở bằng việc đang xảy ra, nói chậm, người nghe dùng lúc đêm. Phần dí dỏm của thầy không đưa vào mẫu, vì hồ sơ kênh là tĩnh. Tin cậy: vừa cho quy mô, thấp cho nhịp câu vì không có transcript đầy đủ.

3. Làng Mai Official, video pháp thoại Kinh Pháp Hoa đăng 21/11/2026, kênh khoảng 127.000 người đăng ký. https://www.youtube.com/watch?v=rA_pUMR_Ric . Cực kia của ngách: một kinh, nói chậm, lời dẫn trang trọng. Quy mô nhỏ hơn các kênh triệu người. Mẫu không học cách xưng "đại chúng" và không trích kinh. Tin cậy: vừa cho vị trí của kiểu kể này.

Trang phật giáo địa phương từng thấy trong kết quả tìm không mở được (lỗi tên miền). Không dùng trang ấy.

Gộp lại, phần đông người nghe pháp tiếng Việt trên YouTube đang ở với giọng một việc đời, một ví dụ cầm được, video dài, nhiều khi để nghe lúc khó ngủ. Kiểu giảng một bộ kinh, xưng trang trọng, vẫn còn, và ít người đăng ký hơn ở các kênh đã thấy. Mẫu BUD lấy nhịp đêm: một vật, một việc tay làm được, một câu hỏi, không ra lệnh hết khổ.

### Mẫu mới

Ưu tiên 1, chén nước nguội. 164 chữ.

> Bạn rót một chén nước, rồi để nó trên bàn trong lúc đi làm việc khác. Khi quay lại, nước vẫn nằm đó. Nó không trách bạn. Nó chỉ nguội. Hãy nhìn cái nguội ấy như một việc nhỏ, không phải một lỗi. Hơi nóng đi đâu, bạn không cần giải thích cho xong. Bạn chỉ cần nhận ra tay mình đang cầm một thứ đã đổi. Có những buổi, nỗi buồn cũng vậy. Nó không cần bạn đánh thắng nó trước khi trời tối. Nó cần một chỗ để được thấy. Bạn ngồi xuống. Uống một ngụm, hoặc không uống. Cái giá của việc bỏ qua chén nước không phải là một hình phạt. Cái giá là tối nay bạn khó nhớ mình đã khát từ lúc nào. Hãy hỏi một câu rất gần. Bây giờ, trong người bạn, thứ nào đang nguội? Bạn không phải trả lời thành tiếng. Chỉ đừng bỏ đi trước khi câu hỏi kịp ngồi xuống cạnh bạn.

Ưu tiên 2, một cái bát. 147 chữ. Khác vật với chén nước, cùng nhịp tay.

> Bát ăn tối còn nằm trong chậu. Nước đục. Một cái đũa nổi. Bạn có thể để đến sáng. Nhiều người làm vậy, và trời vẫn sáng. Nhưng bạn thử rửa một cái thôi, không phải cả chậu. Nước ấm chạy qua lòng bàn tay. Cái bát nặng hơn lúc nó còn đầy cơm, vì bây giờ nó là đồ vật, không còn là bữa ăn. Không có lời hứa rằng ngày mai hết đau. Chỉ có việc bạn làm được trong lúc đau vẫn còn. Một cái bát. Rồi một cái nữa, nếu tay còn muốn. Nếu không, dừng. Cái giá của việc ép mình rửa sạch cả nhà trong một đêm là bạn lại biến sự dịu dàng thành một bài kiểm. Hãy để chậu được dở dang. Sáng mai nó vẫn ở đó. Bạn cũng vậy. Và như thế là đủ cho đêm nay.

Dự phòng, tin nhắn chưa gửi. 162 chữ.

> Bạn mở một tin nhắn đã đọc từ trưa, rồi không trả lời. Màn hình tối đi. Trong phòng chỉ còn tiếng quạt. Bạn không xấu vì đã im. Có những lời cần một đêm mới nói được cho phải. Cũng có những lời không cần gửi, vì gửi xong bạn chỉ thêm một việc phải canh. Hãy đặt điện thoại úp xuống. Cảm giác trong ngực vẫn ở đó. Nó không biến mất vì bạn đã làm một cử chỉ đẹp. Không ai bảo bạn phải tha thứ, và không ai bảo bạn phải nói cho xong. Cái giá của việc nằm mà soạn đi soạn lại một câu là giấc ngủ bị cắt thành những mảnh nhỏ. Bạn thử một câu hỏi, rồi thôi. Câu ấy có cần đi khỏi phòng này đêm nay không? Nếu chưa, hãy để nó ở lại với bạn. Sáng mai câu chữ còn đó. Người nhận cũng còn đó. Bạn được phép chưa gửi.

Mẫu thứ tư, mưa trên mái. 144 chữ. Gần mẫu chén ở nhịp "nghe một thứ lặp lại", nên không vào cặp khi đã có chén nước.

> Mưa xuống mái, đều, không hỏi bạn có rảnh không. Bạn nằm, nghe một lúc. Tiếng ấy không khuyên bạn điều gì. Nó chỉ lặp. Trong những ngày đầu óc đông người, một tiếng lặp có ích hơn một lời giải. Bạn đừng biến mưa thành điềm. Đừng biến một buổi nặng lòng thành bằng chứng rằng mình hỏng. Hãy chỉ đếm năm nhịp, rồi bỏ đếm. Cái giá của việc tìm cho kỳ được ý nghĩa của cơn mưa là bạn không còn nghe mưa. Bạn đang nghe chính nỗi sốt ruột của mình. Nếu mắt còn mở, hãy nhìn một điểm trên trần, chỗ tối hơn những chỗ khác. Nó không đi đâu. Bạn cũng chưa cần đi đâu. Khi mưa thưa, phòng sẽ rộng ra một chút. Bạn sẽ biết, vì tiếng đã đổi. Không cần ai chấm điểm đêm nay.

## Việc còn lại, không làm trong lượt này

Lead thay file trong `docs/pm/giong-mau/` sau khi chủ kênh chọn. Prompt đã trỏ "hai đoạn ví dụ của chính kênh này". Lượt này không sửa prompt.

FS và BUD cần người giữ hai kênh ấy nghe, và khi có cửa sổ giữ chân thì thay mẫu soạn mới bằng câu thật của kênh, cùng luật: giữa chương, 80–200 chữ, không trích, không dữ kiện dễ sai thời gian.

Views trong tệp này thấp. Cặp CL, MIM, CK là cặp có căn cứ nhất trong dữ liệu đang có, chưa phải cặp đã thắng nghe mù.
