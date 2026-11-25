# Nghiên cứu prompt Gemini cho lời Long — bước 0, issue 531

Ngày ghi: 25/11/2026. Repo `nguyent0810/vietneu-tts`, issue 531, phần bổ sung 25/11 (bước 0).

Đây là nghiên cứu để Lead chọn biến thử. Chưa chạy A/B. Chưa sửa `docs/pm/prompt-viet-loi.md`. Chưa tạo giọng mẫu mới. Chưa đọc TTS. Chưa commit, chưa comment issue, chưa đổi lịch.

Bối cảnh để đọc các giả thuyết: lời Long tiếng Việt do Gemini web (Neon, thinking High) viết từ `docs/pm/prompt-viet-loi.md`, rồi hồ sơ kênh và bốn khối input. Ba kênh trong bộ thử sau này: CL "Into The Killer's Mind" (án oan, lịch sử), MIM "Mind in the Machine" (thảm hoạ công nghệ), CK "Biểu Đồ Biết Nói" (chứng khoán cho người mới). Bộ thử cố định, khi Lead duyệt, là CH00–CH01 của `mim-ariane-5-37-giay`, `ck-c11-ftse-nang-hang` và `cl-dreyfus-dao-ma`, cùng bảng dữ kiện đã soát. Bản đối chứng là prompt hiện tại cộng một giọng mẫu Vidocq, Neon High. Mỗi lượt chỉ một biến.

## Cách đọc mức tin cậy

- **Cao:** trang đã mở và đọc được thân bài trong phiên này.
- **Vừa:** mở được một phần, hoặc chỉ có transcript trong kết quả tìm, hoặc bài giảng phổ thông.
- **Thấp:** không dùng làm bằng chứng. URL thử mà không đọc được nằm ở khoảng trống cuối mảng 1 và ở mục mâu thuẫn (Casefile, PDF Transom, CONCOCT).

Số liệu giữ chân YouTube (30 giây, 2 phút, AVP) không có trong các bài đã mở. Chỗ nào ghi lượt tải hoặc lượt đăng ký là tầm với của kênh, không phải đường giữ chân.

## Luật giả thuyết không được phá

Chủ kênh và prompt hiện tại:

- Không đặt trần số chữ hay số câu. Câu dài ngắn theo cảm xúc (chủ kênh 18/11: chỉ giới hạn cứng, được phóng tác).
- Số trong lời đọc nói tròn như người nói. `18,08` là "hơn mười tám", không phải "mười tám phẩy tám". Số chính xác để trên hình.
- Không mở bằng khung "trả lời ba câu hỏi". Phần mở vẫn là khoảnh khắc căng nhất và kết bằng một câu hỏi, như prompt đang có.
- Không bịa lời trích. Không bịa lời nói, cảm xúc hay hành vi của người còn sống. Người lịch sử đã mất được phóng tác bầu không khí, nội tâm và nhận định, bọc `[PD]` khi dựng cảnh không có tư liệu.
- Không tả máu me chi tiết. Đúng định dạng máy (`## CHnn`, `[PD]`, `»`, `‖`).
- Giọng mẫu để học giọng, không chép câu.
- `storytelling-guide.md` §14 chuyển quyền kể sang hồ sơ V2. Không biến gợi ý §13 thành cổng mới. GH-337 và cold open survival (15/11) là lớp phút đầu đã có; ticket này không sửa chúng.

## Prompt và giọng mẫu đang chạy

Prompt dán vào Gemini đã yêu cầu: viết cho tai, giàu hình ảnh và âm thanh, trục là nhân vật và cái giá, biến cố thành cảnh, nhịp bằng dấu câu, mở bằng khoảnh khắc căng nhất rồi một câu hỏi, số nói tròn, kể thẳng không "theo nguồn", gọi người nghe là "bạn", mỗi chương chỉ đúng ý dàn chương và móc sang chương sau.

Giọng mẫu chủ kênh chọn 17/11/2026 (`data/long/cl-dreyfus-dao-ma/viet_loi_in/3_giong_mau.md`, bản Gemini web) làm những việc sau, và giả thuyết không được đánh nhau với khẩu vị này:

- Mở bằng cảnh (búa toà, Douai, 1796, tám năm khổ sai), nhảy thời gian, nêu tên, rồi hỏi cái giá của một bản giao kèo.
- Từ Hán Việt của thế giới án (`bản án`, `khổ sai`, `mật vụ`, `hành lang quyền lực`) đứng cạnh vật và cơ thể (mái ngói, áo sơ mi, bình minh, ống khói).
- Người kể nhận định người đã mất ("bản giao kèo với quỷ dữ").
- Số đọc bằng lời ("tám năm", "mười lăm năm sau", "ba giờ sáng").
- Tên nước ngoài giữ chính tả gốc và được lặp đủ: Eugène-François Vidocq.

Một prompt và một mẫu án Pháp này đang dùng chung cho cả CK và MIM. Đó là lý do biến giọng mẫu vẫn còn trên danh sách, dù không xếp đầu.

## Năm biến trên issue, và danh sách này thay chỗ nào

| Biến cũ trên issue 531 | Việc của danh sách mới |
| --- | --- |
| 1. Một mẫu chung ↔ 2–3 mẫu riêng kênh | Giữ, mài thành giả thuyết 3 (H1). Hai đoạn, không năm. Thêm một câu cấm chép cấu trúc mở. |
| 2. Một lượt dữ kiện+văn ↔ hai lượt beat rồi văn | Giữ, mài thành giả thuyết 1 (H2). Beat có hình một câu của Rosenthal, không phải dàn ý tự do. |
| 3. Chân dung người nghe + "viết để nghe" | Hạ xuống giả thuyết 7 (H7). Prompt đã nói viết cho tai; few-shot thường thắng một câu chân dung. |
| 4. Móc 30–45 giây, câu ngắn sau mất mát, giác quan, thoại phỏng dựng | Tách. Đồng hồ móc trùng checklist 30 giây của GH-337 và dễ thành công thức model đọc ra. Câu ngắn sau mất mát đụng lệnh cấm trần độ dài câu: bỏ. Thoại phỏng dựng người còn sống đụng luật cứng: bỏ. Phần giác quan thành giả thuyết 4 (H4), không kèm trần câu. Một câu phản tư giữa chương là giả thuyết 6 (H6), không phải biến 4 cũ. |
| 5. Neon High ↔ Medium ↔ Hydrogen | Giữ cuối danh sách, giả thuyết 8 (H8). Thử sau khi chữ prompt đã đóng. |

Hai giả thuyết mới, vì prompt đã nói nguyên tắc mà model vẫn làm khác: H3 (đoạn mở không trả lời bài) và H5 (số và tên trước khi TTS đọc).

## 1. Kênh kể chuyện dài

Công khai, không phải blog SEO "cách viết script". Không thấy bài phân tích kênh tiếng Việt dài kèm số giữ chân và cách viết lời. Khoảng trống đó ghi riêng ở cuối mảng.

### 1. Dan Carlin — Hardcore History

- URL đã mở: https://www.vice.com/en/article/hardcore-history-podcast/ (Vice, 23/02/2016). Đã mở hết bài.
- Tóm tắt: Carlin không viết script vì script sẽ không còn giọng ông. Tập là trộn kể, kịch và chỗ ngoặt. Người nghe đẩy ông viết dài chừng nào còn thú. Ông bị kéo bởi cực đoan và câu "nếu là mình thì xử sao". Chi tiết hạt (áo choàng da chuột; Thế chiến bắt từ mấy thanh niên Serb trong quán) làm sử thành việc người ta tưởng tượng được. Mẹ vợ ông nói không cần bằng tiến sĩ mới nghe được. Ông nói ứng, có khi thu vài lần.
- Kỹ thuật: một vật cụ thể thay cho một đoạn giảng. Câu hỏi đạo đức đặt vào người nghe, không phải bài học đọc sẵn. Độ dài là hệ quả của nhịp, không phải mục tiêu.
- Tin cậy: cao. Bài không có số giữ chân.

### 2. Paul Cooper — Fall of Civilizations

- URL đã mở: https://www.middleeasteye.net/discover/fall-of-civilizations-podcast-book-decline-fall-history (Oscar Rickett, Middle East Eye, 10/05/2024). Lần lấy đầu trả 404; lần mở sau đọc được bài (khoảng 160 dòng).
- Tóm tắt: Podcast hơn 100 triệu lượt tải, YouTube hơn một triệu đăng ký, tập thường trên ba giờ, viết và thu hai đến ba tháng. Mở bằng một người lữ hành thấy đống đổ nát (Xenophon ở Nimrud/Nineveh; Pietro Della Valle ở Ur), rồi hỏi sống trong lúc sụp đổ là cảm giác gì. Câu ông dùng: chưa hiểu được vở kịch nếu chưa xem sân khấu. Một người (Mansa Musa) cộng một khoản tiền cụ thể mang cả một nền kinh tế vào tai.
- Kỹ thuật: cảnh trước, nghĩa sau. "Cảm giác lúc ấy" dành cho người đã mất và cho nơi chốn, không gán nội tâm cho lãnh đạo còn sống. MIM có thể mượn cặp này (sân khấu kỹ thuật trước, rồi một quyết định), như phép tương tự, không phải số giữ chân của ColdFusion hay Asianometry.
- Tin cậy: cao cho bài đã mở. Hai con số trên là tầm với, không phải retention.

### 3. MrBallen — mở bài và chỗ giấu kết

- URL: https://www.youtube.com/watch?v=q9GCalevtSM (Modern Wisdom, "Storytelling Secrets", 28/05/2024). Transcript nằm trong kết quả tìm của chính URL YouTube này. Trang gương podscripts (`https://podscripts.co/podcasts/modern-wisdom/774-mrballen-navy-seal-to-true-crime-insane-stories-of-courage-fear-resilience`) tìm theo payoff / reveal không ra chữ. Không dùng eathealthy365 hay MaxiFollowers.
- Tóm tắt, theo transcript trong kết quả tìm: ông nói người kể cho quá nhiều ở đầu. Mở bằng kết luận thì người nghe hết lý do ở lại; báo chí làm ngược lại và cách đó giết phần thưởng của truyện. Bất kỳ câu nào ở khoảng 90% đầu mà ra dấu đáp án đều làm hỏng cú trả. Cú trả nằm ở cuối.
- Kỹ thuật: đoạn mở cho thấy ai đang mắc và cái giá đã hiện, chưa giảng vì sao và chưa báo kết. Câu hỏi ở cuối phần mở được giữ; câu trả lời chờ đúng chương sở hữu nó.
- Tin cậy: vừa. Chưa render được trang transcript độc lập.

### 4. Patrick Boyle và The Plain Bagel — tài chính không phải bài giảng mua bán

- URL trong kết quả tìm, chưa `open_page` riêng: https://www.youtube.com/watch?v=p7UAqEI8KDE (Money & Macro, Richard Coffin, "The Global Everything Crisis", có The Plain Bagel, 15/09/2022) và https://www.youtube.com/watch?v=itnCadNugN8 (phỏng vấn bên lề sinh nhật The Plain Bagel).
- Tóm tắt, theo các khúc transcript trong kết quả tìm: không bảo người xem phải làm gì; người xem tự nghĩ. Giọng khô vì tài chính kiểu thuyết giáo làm người ta chán. Việc của người kể là ghép mảnh tin vụn thành một câu chuyện có đầu có cuối của một quyết định, giải thích bằng việc đời thường (mua một cửa hàng góc phố).
- Kỹ thuật cho CK: một quyết định, một ví von tiền Việt, không lời khuyên mua bán. Không bịa số giữ chân.
- Tin cậy: vừa.

### Khoảng trống kênh tiếng Việt và kênh thảm hoạ công nghệ

Đã tìm phân tích công khai về lời kể dài tiếng Việt (true crime, sử, tài chính phổ thông) có cả cách viết lẫn số giữ chân. Không thấy bài nào đủ tiêu chuẩn: mô tả playlist không phải bài về nghề viết. Không mở được phỏng vấn script gốc của ColdFusion hay Asianometry. MIM trong các giả thuyết dưới đây là phép ghép Cooper (sân khấu trước, cảm giác của người trong cuộc khi người đó đã là hồ sơ) và Boyle (một quyết định, không khuyên mua). Đó là giả thuyết, không phải case study đo được của hai kênh ấy.

## 2. Viết cho tai

### 5. NPR Training — Alison MacAdam

- URL đã mở: https://www.npr.org/sections/npr-training/2025/05/31/g-s1-66074/would-you-say-it-that-way-tips-on-writing-for-your-voice (bản đang sống; bài gốc 25/02/2015).
- Tóm tắt: Robert Siegel, qua Jonathan Kern trong *Sound Reporting*, nói "viết như miệng nói" là lời khuyên được đưa nhiều nhất và bị bỏ qua nhiều nhất. Lede báo in (kiểu AP) gãy khi đọc thành tiếng. Bản radio của Steve Inskeep là từng ý ngắn, tách nhau. Thời gian của tai chỉ chạy một chiều, người nghe không tua lại. Coi chừng mệnh đề chen giữa câu. Đừng dùng chữ không nói với bạn bè. Lặp một từ đôi khi sạch hơn đổi từ cho văn. Nói thẳng.
- Kỹ thuật lấy được: cấm kết cấu giấy (mệnh đề chen, "điều này cho thấy") và viết như nói với một người. Phần "câu phải ngắn" của NPR xung đột luật xưởng. Giả thuyết không thêm trần số chữ.
- Tin cậy: cao.

### 6. BBC Writersroom — radio drama (bản lưu trữ)

- URL đã mở: https://web.archive.org/web/20120601025754/http://www.bbc.co.uk/writersroom/write-a-script/writing-radio-drama (lưu 01/06/2012). Trang "ten top tips" đang sống trên bbc.co.uk không lấy được.
- Tóm tắt: Radio tắt nhanh nhất trong các cửa kể. Vào việc ngay, cắt lời dẫn. Mỗi câu phải đáng chỗ của nó. Hình trên radio rõ hơn người ta tưởng, nếu âm thanh và im lặng có nghĩa. Đừng giả văn xuôi thành thoại. Đừng giảng hộ. Lời trên radio trần, nên ít mà đủ. Độc thoại nội tâm dễ thành chỗ nhét thông tin.
- Kỹ thuật: một vật, một tiếng, một khoảng lặng (`‖` đã có trong định dạng) thay cho câu giải thích. Thoại chỉ khi bảng dữ kiện có lời trích, hoặc là cảnh `[PD]` của người đã mất. Không thêm thoại cho người còn sống.
- Tin cậy: cao cho bản lưu trữ 2012.

### 7. Ira Glass — Transom

- URL đã mở: https://transom.org/2004/ira-glass/ (phần dựng truyện).
- Tóm tắt: Truyện audio là hai khối. Khối hành động: việc này kéo việc kia. Khối phản tư: một ý về chuyện vừa xảy ra. Khối nào cũng phải đáng nghe. Giai thoại hay mà không có ý thì xẹp. Bài giảng không có việc thì xẹp. Bản hay nhảy giữa hai khối. Phép thử của ông: kể cho bạn mà còn thấy nóng. Ông học một nước đi: từ sự kiện một vụ bước sang một câu "việc đời chạy như thế nào", rồi trở lại vụ.
- Kỹ thuật: một câu phản tư giữa chương, buộc vào cảnh vừa dựng, rồi trở lại việc. Không phải đoạn triết, không phải câu kết chương.
- Tin cậy: cao cho trang Glass. Phản biện của Glynn Washington (phản tư kéo tai ra khỏi nhân vật) chỉ thấy trong kết quả tìm của PDF Transom https://transom.org/wp-content/uploads/2017/06/Howtotellstoriesbymeandeveryoneelse.pdf — PDF chưa mở. Dùng như lời nhắc vừa, nên H6 chỉ một câu.
- Tin cậy Washington: vừa, và không tính là nguồn đã đọc.

### 8. Rob Rosenthal — câu tiêu điểm trước khi viết

- URL đã mở: https://akademie.dw.com/en/rob-rosenthal-on-audio-storytelling-tips-tools-and-the-power-of-sound/a-71478642 (Kyle James, DW Akademie, 31/01/2025).
- Tóm tắt: Trước khi viết lời, một câu tiêu điểm: ai làm một việc, vì điều gì, nhưng điều gì chặn. Rồi dàn ý, dòng thời gian, cảnh, chủ đề. Viết khi đã có khoảng 80% chất liệu. Phỏng vấn theo thứ tự thời gian. Ông gọi nhạc nền là "chế độ độc tài cảm xúc": cảm xúc phải ra từ cấu trúc và câu chữ. Âm thanh không phải băng dán lên truyện yếu. "Có đầu, giữa, cuối" chưa phải truyện, vì bảng chữ cái cũng có thứ tự.
- Kỹ thuật: câu tiêu điểm là đồ nghề của lượt lập dàn nhịp, không phải câu đọc. Không biến nó thành mở bài "trả lời ba câu hỏi". Phần "nhưng" trong câu ấy là móc có xung đột, thay cho một đồng hồ 30–45 giây.
- Tin cậy: cao.

## 3. Prompt LLM cho văn sáng tạo

### 9. Google — Gemini prompting strategies

- URL đã mở: https://ai.google.dev/gemini-api/docs/prompting-strategies (cùng nội dung trang AI Studio `aistudio.google.com/docs/prompting-strategies`).
- Tóm tắt: Trang bảo luôn đưa ví dụ few-shot. Ví dụ giải thích tuyết trên trang cho thấy vài mẫu đủ kéo model từ câu trả lời dài sang câu ngắn: mẫu đè lên chỉ dẫn miệng. Quá nhiều mẫu thì model học thuộc dạng mẫu, hết tổng quát. Định dạng các mẫu phải giống nhau.
- Kỹ thuật: hai đoạn giọng của đúng kênh, cùng khuôn, bọc thành ví dụ chứ không thành lệnh. Không năm đoạn. Một dòng nói rõ học nhịp và cách đặt từ, không chép câu và không chép hình mở.
- Tin cậy: cao.

### 10. Anthropic — prompting best practices (trang hiện hành)

- URL đã mở lúc đầu: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting — chuyển tới https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices . Dưới đây là trang đã render.
- Tóm tắt: Ví dụ là cách chắc nhất để giữ giọng. Mẫu phải đúng việc, đủ khác nhau, và được bọc để model không đọc chúng như chỉ dẫn mới. Nói việc cần làm hơn là liệt kê việc cấm. Giọng của prompt rò sang giọng bài viết. Nêu vì sao một ràng buộc tồn tại thì model khái quát được. Ví dụ nguyên văn trên trang: câu trả lời sẽ bị một máy TTS đọc thành tiếng, nên đừng dùng dấu ba chấm vì máy không biết đọc thế nào.
- Kỹ thuật: một câu "vì giọng AI sẽ đọc nguyên văn" sát luật cần giữ (số, tên, không giảng ở đoạn mở). Không viết prompt bằng giọng công văn nếu muốn lời kể.
- Tin cậy: cao cho trang đã render. Đây là tài liệu Claude, dùng như nguyên tắc few-shot chung, không phải bằng chứng Gemini sẽ làm y hệt.

### 11. OpenAI — developer message

- URL đã mở: https://platform.openai.com/docs/guides/prompt-engineering và https://developers.openai.com/api/docs/guides/prompt-engineering . Phần đầu trang chủ yếu là mẫu SDK. Phần dùng được, tìm thấy trên trang developers.openai.com: tin nhắn developer gồm Identity, Instructions, Examples (đầu vào + bài mong muốn), Context. Trang khuyên ghim bản model và dựng eval; họ model khác nhau cần prompt và bài chấm khác nhau.
- Tóm tắt: không gán cho trang này danh sách "sáu chiến lược / viết chỉ dẫn rõ / tách việc phức tạp" của cookbook cũ. Phần cookbook ấy không nằm trên phần đã đọc.
- Kỹ thuật: khối ví dụ tách khỏi khối luật. Đổi model (H8) là eval riêng, sau khi chữ prompt đứng yên, vì họ model khác không kế thừa kết quả của Neon High.
- Tin cậy: vừa. Trang mở được, nhưng phần creative-writing riêng gần như không có; chỉ lấy được khung Examples và lời khuyên eval.

### 12. Reif, Ippolito, Yuan, Coenen, Callison-Burch, Wei — few-shot đổi giọng

- URL đã mở: https://arxiv.org/html/2109.03910v2 (ACL 2022, "A Recipe for Arbitrary Text Style Transfer with Large Language Models", arXiv 2109.03910).
- Tóm tắt: Zero-shot thuần hay hỏng định dạng. Một bộ ví dụ viết lại giữ cố định, chỉ đổi câu lệnh giọng, chuyển được sentiment và độ trang trọng ngang người viết lại trong đánh giá người đọc. Few-shot đúng giọng đích thì hiệu quả, nhưng phải có sẵn đoạn mẫu của giọng ấy. Bảng 1, trước: "There, in the middle of the street, stood an old man in a raggedy brown coat that was much too big for him." Sau: "There, in the middle of the road, stood a grizzled old man, the light of life faded from his sunken eyes." Ca thực hành: 30 người trong nhóm viết, truyện 100–300 từ, 333 yêu cầu "viết lại cho thành…". Bản xuất nhóm lưu ở https://bit.ly/3fLDuci — liên kết này chưa mở lại.
- Kỹ thuật: muốn CK hết giọng án Pháp thì đưa mẫu CK, không hy vọng một câu "hãy gần gũi" thắng mẫu Vidocq. Mẫu phải khác đề tài với bài đang viết, đúng như đầu file giọng mẫu hiện tại.
- Tin cậy: cao cho bài báo. Điểm người chấm là bài English style-transfer, không phải retention YouTube.

### 13. Yang, Klein, Peng, Tian — dàn ý chi tiết trước khi viết

- URL: arXiv 2212.10077, "DOC: Improving Long Story Coherence With Detailed Outline Control" (ACL 2023). Thân bài HTML chưa mở. Số dưới đây lấy từ abstract trong kết quả tìm, không từ methods.
- Tóm tắt abstract: hai tầng, một bộ lập dàn ý phân cấp, rồi một bộ giữ đoạn văn đi theo dàn. So với baseline Re3, người chấm cho mạch truyện cộng 22,5 điểm tuyệt đối, độ bám dàn cộng 28,2, độ thú cộng 20,7. Việc lập kế hoạch kéo phần sáng tạo ra khỏi lúc viết nháp.
- Kỹ thuật: lượt 1 chỉ xuất nhịp, lượt 2 mới viết văn và không được kéo nhịp chương sau lên trước. Các con số là lý do để thử, không phải hứa cho lời tiếng Việt.
- Tin cậy: vừa. Có tên CONCOCT (arXiv 2311.04459) trong kết quả tìm, về nhịp truyện; thân bài chưa mở, không dùng số của bài ấy.

## 4. Văn kể tiếng Việt cho TTS

### 14. Đặng, Vương, Phan — chuẩn hoá chữ không chuẩn trước TTS

- URL đã mở: https://arxiv.org/html/2209.02971 (FPT và VNU UET, "Non-Standard Vietnamese Word Detection and Normalization for Text-to-Speech", arXiv 2209.02971).
- Tóm tắt: Chữ không chuẩn trong tiếng Việt nhập nhằng. "2/3" có thể là "hai phần ba" hoặc "mùng hai tháng ba". "911" có thể đọc từng số hoặc đọc thành một số đếm. "3-1" có thể là ngày hoặc tỉ số. Bộ 5819 câu báo. Bộ gán nhãn tốt nhất trong bài, BERT-BiGRU-CRF, F1 khoảng 95%, câu còn lỗi khoảng 6,67%. Nhóm nhãn gồm số, phần trăm, số đếm từng chữ số, ngoại tệ, tên riêng nước ngoài (Ronaldo, Messi, NATO), sigl (WHO, VTV), tiền. Bảng I: "92000" thành "chín mươi hai nghìn"; "31/3" thành "ba mươi mốt tháng ba".
- Kỹ thuật: nếu lời còn chữ số hoặc tên thô, máy TTS tự đoán và hay đoán sai. Cách đọc mặc định của bài này là đọc đủ từng chữ số và đọc phần thập phân. Cách đó đụng luật chủ kênh. Không đưa bộ chuẩn hoá này vào prompt. Prompt phải viết sẵn câu nói tròn, để máy không còn gì để đoán.
- Tin cậy: cao cho thí nghiệm trên câu báo. Không phải nghiên cứu người nghe YouTube.

### 15. VietNormalizer — Nguyễn và cộng sự

- URL đã mở: https://arxiv.org/html/2603.04145v1 (arXiv 2603.04145, 04/03/2026).
- Tóm tắt: Bộ luật, không cần model. Mở số nguyên, số thập phân, ngày, giờ, VND, USD, phần trăm, sigl, và phiên tên vay mượn sang âm gần tiếng Việt (ví dụ NASA thành "na-sa") trước khi đưa vào TTS. Sai thanh là sai nghĩa. Số tiếng Việt không đều: "mười" khác "hai mươi", "một" khác "mốt" và "linh một"; cụm nghìn, triệu, tỷ. Nhánh thập phân tách ở dấu phẩy hoặc chấm rồi đọc từng vế — đúng đường ra câu "phẩy". Thứ tự luật quyết định kết quả. Bài thiết kế, không có vòng nghe.
- Kỹ thuật: cùng kết luận với bài 14, và thêm một cấm. Không bảo Gemini phiên tên thành "na-sa" hay "Ơ-gien". Giọng mẫu đã chốt chính tả Eugène-François Vidocq. Lần đầu dùng dạng đọc được ghi trong bảng dữ kiện; lần sau dùng tên ngắn đã có trong bảng. Không bịa dạng phiên âm.
- Tin cậy: cao cho mô tả luật. Thấp nếu ai muốn dùng nó như bằng chứng "nghe hay".

### 16. VOV2 — Hán Việt khi nói

- URL đã mở: https://vov2.vov.vn/giao-duc-dao-tao/khong-nen-tuy-tien-su-dung-nhung-tu-han-viet-chua-ro-nghia-38305.vov2 (30/10/2022).
- Tóm tắt: Bài dẫn TS Trần Tiến Khôi (Hán Nôm, Đại học Thăng Long). "Phụ mẫu" khó vào tai hơn "cha mẹ", "huynh đệ" khó hơn "anh em", "hải phận / không phận" khó hơn "vùng biển / vùng trời". Nói thì ưu tiên thuần Việt khi tiếng Việt đã có từ. Tránh hết Hán Việt cũng làm người nghe không còn hiểu những từ Hán Việt còn lại. Từ đồng âm, không có mặt chữ, dễ hiểu sai. Chỉ dùng từ khi biết nghĩa.
- Kỹ thuật: không xoá Hán Việt của thế giới truyện (`án`, `khổ sai`, `thanh khoản` khi đó là việc đang xảy ra). Từ Hán Việt khó thì câu ngay sau phải là vật, nơi, tiếng, để tai có chỗ bám. Không thay bằng từ thuần Việt nếu từ thuần Việt làm sai nghề.
- Tin cậy: cao cho một bài báo dẫn chuyên gia. Không phải thí nghiệm nghe.

### 17. vanvn.net — Hán Việt và thuần Việt trong câu văn

- URL đã mở: https://vanvn.net/tu-han-viet-la-gi/ (Mavrick Nguyễn, cập nhật 18/03/2026).
- Tóm tắt: Bài giảng. Hán Việt nghiêng về trang trọng và trừu tượng (giấy tờ, khoa học, lễ). Thuần Việt cụ thể và có hình. Cặp ví dụ: giang sơn / sông núi, phụ mẫu / cha mẹ. Lạm dụng thì câu đơ. Hiệu ứng Tú Xương: một từ Hán Việt đứng cạnh một hình thuần Việt thì câu có xương có thịt.
- Kỹ thuật: đúng hình của giọng mẫu Vidocq (từ định chế, rồi mái ngói). Dùng như minh hoạ sư phạm, không như nghiên cứu.
- Tin cậy: vừa.

## Mâu thuẫn cần Lead thấy trước khi chọn biến

1. **Độ dài câu.** NPR và BBC Writersroom khuyên câu ngắn, cắt lời thừa. Luật xưởng cấm trần độ dài. Các giả thuyết chỉ cấm kết cấu giấy (mệnh đề chen, câu "điều này cho thấy") và bắt một câu cảnh đi sau câu trừu tượng. Số chữ vẫn tự do.
2. **Ba câu hỏi.** Rosenthal có một câu tiêu điểm gồm việc, lý do và vật cản. Câu ấy chỉ sống ở lượt lập nhịp, không được đọc, không được thành mở bài. Prompt hiện tại vẫn kết phần mở bằng một câu hỏi.
3. **Người còn sống.** Cooper và Carlin hỏi "cảm giác lúc ấy" và "nếu là mình". Với hồ sơ xưởng, câu ấy chỉ dành cho người đã mất, trong `[PD]`, hoặc là câu hỏi để người nghe tự đặt. Không bịa lời, cảm xúc, hành vi người còn sống. Không thử biến "thêm thoại".
4. **Số và dấu phẩy.** Hai bài TTS tiếng Việt chứng minh máy sẽ đọc 18,08 thành dạng có "phẩy" nếu chữ số còn trong lời. Cách đọc trong bài báo là đọc đủ số. Luật chủ kênh là nói tròn. Giả thuyết 5 theo luật chủ kênh, không theo bài báo.
5. **Casefile và giọng phán.** Đã thử https://www.vice.com/en/article/meet-the-creator-of-casefile-australias-biggest-crime-podcast/ — trang không còn. Trang transcript Musixmatch mở lại thì rỗng. Một lần tìm trước đó có câu host nói chỉ đặt dữ kiện, không bình luận; lần mở sau không xác nhận được câu ấy trên trang. Dù câu ấy có thật, giọng "không phán" cũng ngược mẫu Vidocq mà chủ kênh đã chọn. Không đưa "bỏ nhận định người kể" vào danh sách thử.
6. **Tên nước ngoài.** VietNormalizer phiên âm cho máy. Mẫu đã duyệt giữ chính tả gốc. Giả thuyết 5 không bịa "Ơ-gien", không xếp tên đầy đủ mỗi câu. Mẫu Vidocq có lặp tên đầy đủ; nếu H5 làm CL mất chất sử thi khi nghe thử, Lead bỏ H5 ở CL hoặc chỉ nghe trên CK và MIM.
7. **§13 và GH-337.** "Một dữ kiện mất mát cụ thể trước khi bàn nguyên nhân" và cửa sổ nhịp 30 giây đã có trong guide. Không thử lại chúng dưới dạng trần câu hay đồng hồ móc trong prompt Gemini.

## Giả thuyết, xếp theo tác động dự kiến tới độ cuốn

Mỗi mục là một biến. Bản đối chứng luôn là prompt hiện tại, một mẫu Vidocq, Neon High. Nghe mù trên CH00–CH01 của ba topic đã nêu. Không gộp biến. Chưa viết sẵn các đoạn mẫu: Lead chọn mẫu trước lượt thử của H1.

### 1. H2 — Hai lượt trong cùng chat: nhịp trước, văn sau

Tác động dự kiến cao nhất. Đây là biến 2 cũ, có hình câu cụ thể.

Thay đổi: lượt 1 chỉ trả một tờ nhịp, không văn xuôi. Mỗi chương một câu theo Rosenthal, viết từ bảng dữ kiện, đúng thứ tự thời gian: ai làm gì, vì sao, nhưng điều gì chặn. Câu này không phải lời đọc. Lượt 2 viết văn. Văn không được kéo một nhịp sang chương sớm hơn, không được thêm nhịp tờ nhịp không có. Không thêm lượt 3 "hãy phê bình rồi viết lại".

Hiệu quả kỳ vọng: CH01 không bị tiêu hết ở cuối CH00. Mỗi phút có một "nhưng" mới, nên tai còn lý do ở lại. Abstract DOC (vừa) thấy lập dàn trước khi viết tăng mạch và độ thú so với kế hoạch mỏng; dùng làm lý do thử, không làm chỉ tiêu.

Tai nhận ra: nghe xong CH00–CH01, người nghe kể lại được ngã rẽ. Bản yếu thì hai chương cùng một ý, hoặc chương sau mới là chuyện.

Chỗ chạm luật: câu tiêu điểm không được xuất hiện trong lời. Không mở bằng "ba câu trả lời". Người còn sống chỉ có hành động có trong bảng dữ kiện; "vì sao" của họ không được bịa thành nội tâm. Không đụng trần độ dài câu.

### 2. H3 — Đoạn mở không trả bài

Tác động dự kiến cao, vì nó nằm trong khoảng 40 giây mà cửa sổ sốc đã dồn vào đó.

Thay đổi: giữ nguyên luật hiện tại (khoảnh khắc căng nhất, kết phần mở bằng một câu hỏi). Thêm một cấm cho riêng đoạn mở: không nêu bài học, không nêu kết, không viết câu khẳng định "vì sao X lại Y". Câu hỏi được hỏi cái giá. Câu trả lời chờ chương sở hữu nó. Câu hỏi kiểu mẫu Vidocq ("cái giá đắt đến mức nào") vẫn hợp lệ, vì đó là câu hỏi, không phải lời giải.

Hiệu quả kỳ vọng: người nghe thấy nguy và thấy giá, rồi muốn biết vì sao. MrBallen (vừa) nói mở bằng kết luận thì hết lý do nghe. Cooper (cao) cho cảnh trước nghĩa.

Tai nhận ra: sau khoảng 40 giây, biết ai đang mắc và mất gì. Chưa biết kết, chưa được giảng xong cơ chế.

Chỗ chạm luật: không thêm khung ba câu hỏi. Không bỏ câu hỏi cuối phần mở. Cold open survival (cảnh, câu hỏi hậu quả, một bằng chứng có nguồn) vẫn đúng, vì giá được cho thấy bằng cảnh và bằng chứng, không được giảng hết.

### 3. H1 — Hai mẫu giọng của đúng kênh

Tác động dự kiến cao cho độ khớp kênh, sau H2 và H3 vì hai mục kia quyết định người nghe có ở lại hay không. Biến 1 cũ, mài lại.

Thay đổi, chỉ ở nhánh thử: bỏ mẫu Vidocq chung, thay bằng hai đoạn ngắn của giọng kênh ấy, khác đề tài bài đang viết, do chủ kênh đã duyệt hoặc lấy từ Long giữ chân tốt nhất của kênh. Thêm một dòng: học nhịp, học cách đặt từ Hán Việt cạnh một cảnh, học cách mở và cách hỏi; không chép câu, không chép cấu trúc mở. Bọc hai đoạn thành ví dụ, không thành lệnh. Hai đoạn, không năm, vì trang Gemini nói mẫu đè chỉ dẫn và mẫu quá nhiều thì overfit (cao). Reif (cao) cho thấy few-shot đúng giọng đích làm được việc mà một câu lệnh giọng làm hỏng định dạng.

Hiệu quả kỳ vọng: CK hết giọng tiểu thuyết án Pháp. MIM nghe như một người đang đứng trong một quyết định. CL giữ xương Hán Việt và cảnh, nếu mẫu CL cũng vậy.

Tai nhận ra: ngay phút đầu, nghe mù vẫn chỉ được kênh nào. Nếu ba bản vẫn cùng một giọng, biến này chưa tách.

Chỗ chạm luật: không đụng bốn giới hạn cứng. Rủi ro là model chép hình mở của mẫu; dòng "không chép cấu trúc mở" là chốt. Không tạo mẫu trong bước nghiên cứu này.

### 4. H4 — Sau câu đặc một câu cảnh

Tác động dự kiến cao vừa. Tai đỡ được câu khó, chưa chắc đã tăng mạch truyện bằng H2.

Thay đổi: sau mỗi câu trừu tượng hoặc dày Hán Việt, một câu cảnh (nơi, tiếng, vật, cơ thể) trước khi sang ý mới. Không cấm Hán Việt. Không trần số chữ. Độ dài hai câu vẫn theo cảm xúc.

Hiệu quả kỳ vọng: "lệnh bị từ chối" của CK thành quầy ngân hàng, không thành bài giảng thanh khoản. Đúng cặp trong mẫu Vidocq, trong VOV2, trong bài vanvn, trong "hình trên radio" của BBC và "một vật" của Carlin.

Tai nhận ra: nhắm mắt vẫn thấy căn phòng. Bản yếu thì một đoạn toàn từ định chế.

Chỗ chạm luật: không trần câu, dù NPR khuyên câu ngắn. Cảnh giác quan của người còn sống không được bịa. Người đã mất được `[PD]`. Không thử lại luật §13 "dữ kiện mất mát trước nguyên nhân" như một biến mới.

### 5. H5 — Số đã là câu nói; tên chỉ một dạng

Tác động dự kiến cao vừa, theo hướng hết gãy tai. Rẻ để nghe, vì lỗi hiện ngay ở phút đầu của TTS, trước khi kịp chấm độ cuốn.

Thay đổi: mọi số trong lời đọc đã là cách nói tròn. Không chữ số, không từ "phẩy", không đọc một phần trăm rồi giải thích lại phần trăm ấy. Số đúng để trên hình, không nhét vào miệng. Tên nước ngoài: lần đầu đúng một dạng đọc được ghi trong bảng dữ kiện; lần sau là tên ngắn đã có trong bảng. Không bịa phiên âm. Không xếp tên đầy đủ mỗi câu.

Hiệu quả kỳ vọng: TTS không đọc "mười tám phẩy không tám" và không vấp tên. Đặng 2022 và VietNormalizer cho thấy máy sẽ đoán nếu còn chữ số hoặc token nước ngoài, và nhánh thập phân của họ đi qua chữ "phẩy".

Tai nhận ra: hết cú vấp số và tên trong phút đầu. Nếu bản thử vẫn có chữ số hoặc chữ "phẩy", biến này hỏng cách viết prompt chứ chưa nói đến chất chuyện.

Chỗ chạm luật: không nhập cách đọc đủ số của hai bài báo. Không bịa biệt danh nhằm khắc hoạ người còn sống. Xem mục mâu thuẫn 6 nếu CL cần tên đầy đủ lặp lại cho chất sử thi.

### 6. H6 — Một câu phản tư rồi trở lại việc

Tác động dự kiến vừa. Dễ biến thành bài giảng nếu prompt nói yếu.

Thay đổi: giữa chương, một câu phản tư buộc vào cảnh vừa nghe, về một cơ chế hoặc về một nhân vật lịch sử đã mất, rồi câu sau là việc tiếp. Không thành đoạn. Không đặt ở câu kết chương. Không thành lời răn. CK: cái giá của việc không biết vì sao lệnh bị từ chối, không phải "bạn nên mua".

Hiệu quả kỳ vọng: người nghe nói được cảnh ấy đổi điều gì, mà không thấy mình đang ngồi học. Glass (cao): giai thoại và phản tư phải xen nhau. Washington (vừa, PDF chưa mở): phản tư kéo ra khỏi người trong cảnh, nên chỉ một câu. Prompt hiện đã cấm giáo huấn ở cuối chương và cấm "theo sử gia"; H6 lấp khoảng giữa chương, nơi model đang hoặc giảng dài hoặc không có ý.

Tai nhận ra: có một câu làm người nghe gật, rồi chuyện chạy tiếp. Bản hỏng thì câu ấy là đạo lý, hoặc là động cơ bịa của người còn sống.

Chỗ chạm luật: không phải ba câu hỏi, không phải câu kết răn dạy, không bịa động cơ người còn sống. Nhận định người đã mất vẫn trong quyền phóng tác sẵn có.

### 7. H7 — Một câu chân dung người nghe, chỉ trong prompt

Tác động dự kiến vừa thấp. Biến 3 cũ. Xếp dưới H1 vì Reif và trang Gemini cho thấy mẫu giọng thắng một câu mô tả người đọc.

Thay đổi: thêm một câu chân dung, khác nhau theo kênh, cộng một dòng "viết như đang kể cho một người đang nghe lúc đi đường, không viết như bài báo". Chân dung chỉ nằm trong prompt, không được đọc thành lời. Nhánh này giữ nguyên mẫu Vidocq, nếu không sẽ lẫn với H1. Nêu vì sao, theo ví dụ TTS trên trang Claude: giọng máy sẽ đọc nguyên văn.

Hiệu quả kỳ vọng: bớt kết cấu báo in (mệnh đề chen, lede tin). Boyle và Coffin (vừa): nói với một người, không phải với học viên cần lời khuyên.

Tai nhận ra: câu nghe như nói, hết giọng bài xã luận. Nếu H1 đã tách được ba kênh, có thể không cần lượt này.

Chỗ chạm luật: chân dung không thành ba câu hỏi, không thành lời hứa mua bán, không thành trần độ dài câu.

### 8. H8 — Đổi model sau cùng

Tác động lên độ cuốn: chưa có cơ sở trong nguồn đã đọc. DOC và Reif gắn mức tăng với dàn ý và với mẫu, không với ngân sách suy nghĩ. Trang OpenAI (vừa) nói họ model khác cần prompt và bài chấm khác: đó là lý do thử model cuối, không phải lý do thử đầu. Biến 5 cũ.

Thay đổi, khi chữ prompt của biến thắng đã đóng: một kênh, một cặp CH00–CH01, Neon High đối Neon Medium, rồi mới tới Hydrogen nếu hai bản đầu không tách. Nếu chủ kênh không phân biệt được, bỏ biến này.

Hiệu quả kỳ vọng: không hứa lời hay hơn. Xưởng đã nghi giọng đổi theo mức thinking; biến này để đo nghi đó, không để mở cuộc thử.

Tai nhận ra: cùng chữ prompt, khác độ cụ thể hoặc độ lan. Không có luật nào bị đụng.

## Thứ tự đề xuất khi Lead cho chạy

Xếp theo tác động ở trên là H2, H3, H1, H4, H5, H6, H7, H8.

Thứ tự chạy nên lệch một nhịp vì H5 rẻ và lộ ngay trên TTS: H2, rồi H3, rồi H1, rồi H5, rồi H4, rồi H6, rồi H7 chỉ khi H1 chưa tách giọng ba kênh, H8 sau cùng khi chữ prompt đã đứng yên.

Mỗi lượt: một biến, nhãn mù, chỉ CH00–CH01, bảng dữ kiện đã soát, không sửa `prompt-viet-loi.md` trong lúc so. Người soát vẫn chỉ sửa dữ kiện. Ghi kết quả nghe, khi có, vào file A/B riêng. File này không chứa kết quả nghe.

## Lead duyệt trước khi thử

Danh sách tám giả thuyết thay năm biến trên issue theo bảng ở đầu file. H3 và H5 là biến mới. H4 và H6 là phần còn lại được phép của biến 4 cũ; phần câu ngắn và phần thoại phỏng dựng đã loại vì đụng luật.

Chưa chạy thử. Chưa chọn mẫu kênh cho H1. Chưa đổi lịch.
