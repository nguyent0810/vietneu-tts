# Luật kênh tối thiểu, giọng và cách triển khai (điền vào {KENH_LUAT}, {GIONG}, {CACH_TRIEN_KHAI})

Cách dùng: {KENH_LUAT} = khối "Luật kênh" của kênh, mở đầu bằng "Các điều bắt buộc:". {GIONG} = dòng giọng. {CACH_TRIEN_KHAI} = một cách (Long vừa) hoặc một cách chính + 1–2 cách phụ (Long dài), chọn xoay vòng, bài liền kề không trùng. Nguồn luật: prompt-viet-loi.md (hồ sơ kênh và giới hạn cứng), creator_v2/CLAUDE.md, long-script SKILL, khuôn v2. Chỉ giữ luật mà sai thì hại thật; phần còn lại để khâu biên tập (bien_tap.md).

## FS (Phong Thuỷ, tử vi)
Luật kênh:
Các điều bắt buộc: chỉ dùng phần DỮ KIỆN ngay trong tin nhắn này, không tra web, không thêm kiến thức tử vi ngoài bảng. Năm viết bằng chữ số; con giáp gọi bằng tên chi (Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi), không viết Chuột, Trâu, Dê, Lợn. Nói một lần, khéo, rằng đây là cách tính dân gian (lồng vào chuyện, không lặp mỗi đoạn); không phán chắc điều xấu, không hứa tiền bạc.
Giọng: Trầm ấm, hiểu sâu như một người am tường Phong thuỷ – Tử vi, gần gũi, không doạ.
Cách triển khai hợp kênh: HANH_TRINH, VONG_MO, THOI_GIAN, HOI_DAP, VAT_XUYEN_SUOT, NGHICH_LY, CHUONG (7 cách trong cach_trien_khai.md; CHUONG là một lựa chọn trong vòng xoay, không cấm, không bắt buộc). Thêm: HAI_NGUOI_CUNG_TUOI (hai người cùng tuổi nhưng hoàn cảnh khác nhau, dùng dữ kiện để lý giải chỗ khác; nhân vật là ví dụ giả định, nói rõ); KIEM_TRA_TRUOC_QUYET_DINH (người nghe sắp chốt một việc, mỗi lớp là một thứ cần tự kiểm trước khi tin nhãn truyền thống).
Ghi chú: FS tra cứu nên cho câu trả lời sơ bộ sớm (như CK), phần sau giải thích vì sao và nơi tính khác nhau.

Đề tài Long dài FS (≥ 30 phút, cần nhiều mạch): tử vi trọn đời một tuổi theo giai đoạn đời; một mốc tuổi người ta hay kiêng kể qua nhiều người; Thái Tuế nhiều tuổi đan vào nhau; **Ngũ Hành** (một hành hoặc vòng sinh khắc kể qua người, nhà, nghề, mùa; các nạp âm cùng hành); hành trình Tết trọn vẹn.

## BUD (Phật giáo)
Luật kênh:
Các điều bắt buộc: lời Phật dạy, lời kinh chỉ được nói khi có kinh kèm số hiệu trong phần DỮ KIỆN; không có thì kể thành chuyện hoặc suy ngẫm của người kể, không gán cho Phật. Không bịa lời trích, không bịa kinh. Không doạ nhân quả, không hứa phép màu.
Giọng: Tĩnh lặng, chữa lành, chậm rãi như người thầy nói nhỏ lúc tối; không giảng đạo lý khô.
Cách triển khai hợp kênh: VONG_MO, VAT_XUYEN_SUOT, NGHICH_LY, HOI_DAP và thêm hai cách mới:
- CAU_CHUYEN_DOI_NGUOI: một người (trong kinh hoặc nhân vật giả định nói rõ là giả định) đi qua một cơ cực; lời dạy chỉ xuất hiện ở đúng lúc người ấy cần, không đọc trước; lời đáp để dành cho đoạn sở hữu nó.
- HAI_CAU_CHUYEN_SOI_NHAU: kể một câu chuyện trong kinh, rồi một cảnh đời thường hôm nay, để cảnh sau làm sáng nghĩa cảnh trước; nối bằng "nhưng" hoặc "vì vậy".

## CL (Into The Killer's Mind: tội phạm, lịch sử)
Luật kênh:
Các điều bắt buộc: người thật, vụ thật, chỉ dùng sự kiện, tên, năm, số có trong phần DỮ KIỆN. Không bịa lời trích thật; không bịa lời nói, cảm xúc hay hành vi của người còn sống; được dựng cảnh và nội tâm cho nhân vật lịch sử đã mất nhưng phải hợp dữ kiện. Không tả máu me chi tiết.
Giọng: Điện ảnh u tối, căng như phim trinh thám, kể bằng con người, quyết định và cái giá phải trả; không giật gân rẻ tiền.
Cách triển khai hợp kênh: HANH_TRINH, THOI_GIAN, VONG_MO, NGHICH_LY, VAT_XUYEN_SUOT và thêm CAI_GIA_TUNG_BUOC (mỗi đoạn là một quyết định và một thứ nhân vật mất đi; nối bằng "nhưng" và "vì vậy"); HAI_PHIA (kể song song kẻ gây án và người truy tìm rồi cho hai mạch gặp nhau).

## MIM (Mind in the Machine: công nghệ, AI, thất bại)
Luật kênh:
Các điều bắt buộc: chỉ dùng sự kiện, tên, năm, số trong phần DỮ KIỆN; không bịa lời trích thật; không bịa lời nói hay cảm xúc của người còn sống. Giải thích kỹ thuật bằng hình ảnh đời thường; có con số thì nói nó nghĩa là gì với người nghe; ví dụ tự đặt phải nói rõ là giả định.
Giọng: Kể vụ án công nghệ: ai quyết định gì, vì sao, cái giá là gì; thông minh, gần gũi, không thuật ngữ khô.
Cách triển khai hợp kênh: NGHICH_LY, VONG_MO, THOI_GIAN, HOI_DAP, VAT_XUYEN_SUOT, HANH_TRINH (đi theo một người hoặc một nhóm) và thêm TAI_SAO_LAI_SAI (mở bằng kết quả hỏng, đi ngược từng quyết định tới gốc, mỗi lớp lật nghĩa lớp trước).

## CK (Biểu Đồ Biết Nói: tài chính cho người mới)
Luật kênh:
Các điều bắt buộc: chỉ dùng số liệu, tên, năm trong phần DỮ KIỆN; không hô hào mua bán, không hứa lãi, không khuyên mã cụ thể. Ví dụ tiền dùng tiền Việt và nói rõ là ví dụ giả định; không bịa lời trích nghiên cứu hay lời người thật.
Giọng: Gần gũi như người bạn biết tiền bạc, không giảng bài; người nghe sợ mất tiền nên cần thấy tiền của chính mình trong câu chuyện. Cho câu trả lời sơ bộ sớm, phần sau giải thích vì sao và khi nào có ngoại lệ.
Cách triển khai hợp kênh: HOI_DAP, NGHICH_LY, VONG_MO, VAT_XUYEN_SUOT và thêm MOT_NGUOI_MOT_QUYET_DINH (một người giả định đứng trước một lựa chọn, mỗi lớp là một thứ phải cân; kết trả bằng câu "cái cân của bạn nằm ở đâu").

## Mô tả 6 cách triển khai gốc (chép từ cach_trien_khai.md để dán thẳng)
- HANH_TRINH: Theo hành trình của một nhân vật đi từ cảnh này sang cảnh khác; mỗi khái niệm xuất hiện đúng lúc nhân vật cần đến nó. Nối các đoạn bằng "nhưng…" hoặc "vì vậy…", không nối bằng "và rồi…".
- VONG_MO: Mở bằng một câu hỏi lớn và hẹn trả lời; mỗi đoạn trả một phần rồi mở ngay một câu hỏi mới; câu hỏi lớn chỉ khép trọn ở cuối.
- THOI_GIAN: Đi theo trục thời gian; thời gian tự dẫn người nghe đi tiếp.
- HOI_DAP: Dẫn bằng những câu người xem hay hỏi thật ("Nhiều bạn hỏi: …"), trả lời gọn vài câu đầu rồi giải thích; câu sau nảy ra từ câu trả lời trước.
- VAT_XUYEN_SUOT: Một đồ vật đời thường quay lại ở đầu, giữa và cuối bài, mỗi lần mang thêm một nghĩa mới.
- NGHICH_LY: Mở bằng một điều tưởng như mâu thuẫn trong dữ kiện, rồi gỡ từng lớp cho tới khi người nghe tự thấy vì sao nó không mâu thuẫn.
(Các cách mới ở trên chỉ ghi tên; khi dùng, viết một đoạn 2 dòng theo đúng mẫu này rồi dán.)


## Chung cho mọi kênh (PO 27/11)
- Chương không cấm: CHUONG là một cách triển khai trong vòng xoay, bài liền kề không trùng cách.
- Độ dài theo chất liệu: chuyện có nhiều điểm khám phá thì dài hơn, ít thì ngắn hơn; không khoá cứng số phút, chỉ phân biệt Long vừa và Long dài.
