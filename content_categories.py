"""Phân loại nội dung Short thành 5 CATEGORY, MỖI category 1 tiêu chuẩn
chất lượng RIÊNG -- theo yêu cầu trực tiếp của người dùng (xem phiên làm
việc: "Đừng dùng cùng một tiêu chuẩn 'grounded data' để đánh giá tất cả
category").

SAI LẦM đã mắc trước khi có module này: mọi generator Short đều dùng cùng
1 khuôn "fact-check nghiêm ngặt đối chiếu dữ liệu gốc" (đúng cho lịch/12 vị
Thần/con giáp -- CATEGORY 1) NHƯNG áp nhầm sang cả ý tưởng thuộc bản chất
khác (Kinh Dịch ứng dụng, cung hoàng đạo phương Tây) -- dẫn tới kết luận
sai "không làm được" cho những ý tưởng thực ra CHỈ cần tiêu chuẩn khác, chứ
không phải bị loại bỏ.

MỖI generator Short khai báo `CONTENT_CATEGORY` (1 trong 5 hằng số dưới
đây) ở đầu module -- short_judge_panel_engine.py không tự áp rubric (vẫn
trung lập, nhận prompt template từ caller như cũ); rubric CATEGORY được
NỐI vào judge prompt của TỪNG generator qua category_rubric_block(), để
mỗi category thực sự được đánh giá đúng chuẩn của nó, không bị lẫn."""

GROUNDED_DATA = "grounded_data"
EDUCATIONAL = "educational"
INTERPRETATION = "interpretation"
CREATIVE_ASTROLOGY = "creative_astrology"
STORYTELLING = "storytelling"
TRENDING = "trending"

CATEGORY_LABELS = {
    GROUNDED_DATA: "Category 1 -- Daily Grounded Data",
    EDUCATIONAL: "Category 2 -- Educational Knowledge",
    INTERPRETATION: "Category 3 -- Traditional Interpretation",
    CREATIVE_ASTROLOGY: "Category 4 -- Creative Astrology",
    STORYTELLING: "Category 5 -- Storytelling",
    TRENDING: "Category 6 -- Trending/Newsjacking",
}

# Rubric CHÈN THẲNG vào judge prompt của từng generator (thay cho phần
# "BƯỚC 1 -- FACT-CHECK..." cũ, viết riêng lẻ trong từng generator) -- viết
# 1 lần dùng chung, để mọi generator CÙNG category có tiêu chuẩn NHẤT QUÁN
# thay vì mỗi file tự diễn giải khác nhau.
CATEGORY_RUBRICS = {
    GROUNDED_DATA: """TIÊU CHUẨN CATEGORY 1 -- DAILY GROUNDED DATA (fact-check NGHIÊM NGẶT NHẤT trong 5 category):
- MỌI con số/tên gọi/sự kiện phải TRUY ĐƯỢC về đúng dữ liệu gốc đã tính toán sẵn (facts) -- không được sáng tạo, suy luận, hay thêm chi tiết ngoài dữ liệu.
- Phương án nào có BẤT KỲ sai lệch/tự thêm dữ liệu không có trong facts → LOẠI ngay, không thương lượng dù hook hay đến đâu.""",
    EDUCATIONAL: """TIÊU CHUẨN CATEGORY 2 -- EDUCATIONAL KNOWLEDGE (đúng tài liệu, được kể chuyện):
- Nội dung phải ĐÚNG theo tài liệu tham khảo (facts/excerpt) -- không phát minh kiến thức mới, không diễn giải sai lệch ý gốc.
- ĐƯỢC PHÉP giải thích, kể chuyện, minh hoạ bằng ví dụ, so sánh -- miễn là không mâu thuẫn với tài liệu gốc. KHÔNG cần tạo "dữ liệu của hôm nay" -- đây là kiến thức nền, không gắn ngày.
- Mục tiêu là GIÁO DỤC dễ hiểu, không phải liệt kê khô khan.
- Nếu nội dung trình bày một hệ thống/khái niệm truyền thống (Ngũ Hành, Âm Dương, Can Chi...) như cơ chế nhân quả, MỖI câu trình bày một quan hệ/cơ chế cụ thể trong hệ thống đó (vd "X khắc Y", "X sinh Y") PHẢI tự mang framing truyền thống trong chính câu đó hoặc trong mệnh đề ngữ pháp trực tiếp bao trùm nó (vd 1 câu dẫn nhập "Theo hệ thống Ngũ Hành truyền thống, chu trình này gồm:" ngay trước một danh sách liệt kê các quan hệ, nếu mối liên hệ ngữ pháp giữa câu dẫn và danh sách là rõ ràng và liên tục -- KHÔNG chấp nhận 1 câu hedge ở đầu kịch bản rồi các câu sau, không liên quan ngữ pháp trực tiếp, trình bày cơ chế như sự thật khách quan). KHÔNG được trình bày cơ chế này như quy luật vật lý đã được chứng minh khách quan.""",
    INTERPRETATION: """TIÊU CHUẨN CATEGORY 3 -- TRADITIONAL INTERPRETATION (được diễn giải, không phải chân lý tuyệt đối):
- ĐƯỢC PHÉP diễn giải/ứng dụng truyền thống (vd giải nghĩa quẻ, biểu tượng văn hoá) -- đây là nội dung diễn giải, KHÔNG phải dữ liệu tính toán được như Category 1.
- BẮT BUỘC phải nói rõ đây là "1 cách hiểu"/"1 cách ứng dụng truyền thống" -- KHÔNG được trình bày như chân lý tuyệt đối duy nhất, KHÔNG được tuyên bố dự đoán chính xác tương lai của người xem cụ thể. Áp dụng yêu cầu framing này cho MỌI câu có nội dung diễn giải/gán ý nghĩa, kể cả câu ngắn chỉ nêu biểu tượng/tên quẻ (vd "Đó là biểu tượng của quẻ X" cũng cần framing truyền thống nếu đứng như 1 khẳng định độc lập, không chỉ các câu diễn giải dài).
- Vẫn phải đúng KHUNG truyền thống thật (tên quẻ, ý nghĩa cổ điển...) -- không bịa khái niệm không tồn tại, chỉ được diễn giải MỞ trong khuôn khổ khái niệm có thật.
- MỖI câu có nội dung diễn giải/gán ý nghĩa (đúng phạm vi ở trên: "MỌI câu có nội dung diễn giải/gán ý nghĩa, kể cả câu ngắn chỉ nêu biểu tượng/tên quẻ") vẫn PHẢI tự mang framing truyền thống của riêng câu đó (không được bỏ hedge) -- NHƯNG nếu từ 2 câu liên tiếp trở lên, SAU KHI bỏ qua các tiền tố/mệnh đề dẫn nhập ngắn không mang nội dung hedge đứng trước (vd "Theo...", "Đây là...", "Đây đại diện cho...", "Điều này..."), đều chứa CÙNG 1 khuôn cụm danh từ dạng "một cách [X] truyền thống"/"một [X] truyền thống" (chỉ đổi từ đầu X, vd hiểu/diễn giải/góc nhìn/nhìn nhận) → VI PHẠM (lặp khuôn bề mặt, dù mỗi câu riêng lẻ đều đúng khung, và dù khuôn không nằm ở vị trí mở đầu tuyệt đối của câu). Cách sửa hợp lệ: đổi CẤU TRÚC câu (không chỉ thêm/đổi tiền tố dẫn nhập trong khi giữ nguyên khuôn cụm danh từ bên trong) để hedge được tích hợp khác nhau qua từng câu (vd 1 câu dùng khuôn "một cách X truyền thống", câu kế tiếp không lặp lại khuôn đó mà hedge bằng cách khác, như gắn "truyền thống" vào tính từ/trạng ngữ thay vì cụm danh từ), HOẶC gộp các ý liên quan vào DUY NHẤT 1 câu dưới 1 mệnh đề dẫn nhập truyền thống chung bao trùm ngữ pháp trực tiếp. KHÔNG chấp nhận 1 câu hedge độc lập rồi các câu sau, không liên quan ngữ pháp trực tiếp, dựa vào hedge đó.
- MỞ RỘNG chống lặp (Prompt Delta Retention v2): nếu có TỪ 3 CÂU LIÊN TIẾP trở lên đều có CÙNG NHỊP NGHE -- mở đầu bằng 1 cụm attribution/hedge quy nguồn, NGAY SAU ĐÓ là 1 động từ gán nghĩa, RỒI MỚI tới nội dung chính -- thì VI PHẠM, dù cụm attribution/động từ có đổi từ vựng hay không (chỉ đổi nguồn quy kết hoặc đổi động từ KHÔNG tính là đổi nhịp câu thật sự). 2 câu liên tiếp cùng nhịp này KHÔNG bị loại nhưng PHẢI ghi cảnh báo vào feedback.
  Ví dụ VI PHẠM (3 câu, đổi từ vựng nhưng cùng nhịp nghe): "Diễn giải cổ xưa xem núi là sự tĩnh lại. Góc nhìn dân gian coi đó là lúc nên dừng. Cổ nhân truyền lại rằng đây là nền tảng vững vàng."
  Ví dụ HỢP LỆ (vẫn đủ framing trên MỖI câu theo đúng yêu cầu ở trên, chỉ đổi VỊ TRÍ đặt framing để tránh nhịp lặp): "Trong diễn giải truyền thống, núi gợi sự tĩnh lại. Biết dừng đúng lúc, theo cách hiểu này, cũng được xem là một dạng vững vàng." -- câu 2 vẫn có framing ("theo cách hiểu này... được xem là") nhưng đặt XEN GIỮA câu thay vì mở đầu bằng cụm quy-kết-nguồn.""",
    CREATIVE_ASTROLOGY: """TIÊU CHUẨN CATEGORY 4 -- CREATIVE ASTROLOGY (đánh giá sáng tạo, KHÔNG fact-check dữ liệu):
- KHÔNG áp dụng fact-check kiểu đối chiếu số liệu -- thể loại này (cung hoàng đạo, tính cách, tình yêu...) vốn không có "đúng-sai" tính toán được.
- Đánh giá theo CHẤT LƯỢNG SÁNG TẠO: có sáo rỗng/chung chung không (áp dụng cho cung nào cũng đúng = sáo rỗng, LOẠI), có tuyệt đối hoá không (nói chắc chắn điều sẽ xảy ra = LOẠI), có giọng văn hấp dẫn/cụ thể cho ĐÚNG cung đang nói không.
- Đây là nội dung GIẢI TRÍ CÓ TRÁCH NHIỆM -- không khẳng định chắc chắn tương lai, nhưng vẫn được vui/hấp dẫn/cụ thể.
- ĐỘC LẬP với việc không "tuyệt đối hoá tương lai": mỗi khẳng định về đặc điểm tính cách/nguyên tố PHẢI dùng framing chủ quan/xu hướng phù hợp cho nội dung chiêm tinh giải trí (vd "thường/hay có xu hướng/dễ...") thay vì khẳng định trực tiếp như sự thật khách quan về cung đó. Phương án nào có câu khẳng định trực tiếp đặc điểm tính cách/nguyên tố mà KHÔNG dùng framing này → LOẠI, độc lập với việc có "tuyệt đối hoá tương lai" hay không.""",
    STORYTELLING: """TIÊU CHUẨN CATEGORY 5 -- STORYTELLING (mạch lạc, giả định phải rõ ràng):
- Câu chuyện phải MẠCH LẠC (có mở-thân-kết trong khuôn khổ ngắn), không phải liệt kê sự kiện rời rạc.
- Nếu có yếu tố giả định/hư cấu (vd "nếu... thì sao") PHẢI thể hiện RÕ RÀNG đây là giả định -- KHÔNG được biến giả định thành khẳng định sự thật lịch sử.
- Nếu kể giai thoại/lịch sử THẬT: cốt truyện chính phải khớp tư liệu được biết đến rộng rãi, không bịa tình tiết lịch sử không có căn cứ.
- Ưu tiên HOOK MẠNH và GIÁ TRỊ XEM CAO (bài học/insight ở cuối) hơn là liệt kê chi tiết.""",
    TRENDING: """TIÊU CHUẨN CATEGORY 6 -- TRENDING/NEWSJACKING (tin tức/sự kiện đang được quan tâm, fact-check theo nguồn thời sự đã cho, KHÔNG phải kiến thức nền vĩnh viễn):
- MỌI chi tiết sự kiện (ai, việc gì, khi nào, ở đâu) PHẢI TRUY ĐƯỢC về đúng đoạn trích nguồn tin đã cung cấp (facts) -- không được suy diễn thêm tình tiết, không được đoán trước kết quả/diễn biến mà nguồn chưa xác nhận.
- BẮT BUỘC có 1 mốc THỜI GIAN rõ ràng trong kịch bản (vd "theo tin ngày...", "mới đây...", gắn với source_date đã cho) -- nội dung thời sự KHÔNG được viết như thể là sự thật vĩnh viễn, không gắn ngày -- phương án nào thiếu mốc thời gian → LOẠI.
- Nếu facts.still_developing=true (sự việc còn ĐANG DIỄN BIẾN/CHƯA CHỐT, vd điều tra chưa kết luận, số liệu sơ bộ): BẮT BUỘC dùng ngôn ngữ dè dặt phù hợp ("theo thông tin ban đầu", "chưa được xác nhận chính thức") -- KHÔNG khẳng định như kết luận cuối cùng.
- Nếu facts.mentions_real_person=true (có người thật cụ thể được nêu tên, không phải nhân vật ẩn danh/nhóm chung chung): phương án nào suy đoán động cơ/phán xét/thêm chi tiết cá nhân ngoài đúng nội dung nguồn tin → LOẠI -- giữ giọng trung lập, tường thuật, không phán xét.
- MỌI khái niệm/thuật ngữ chuyên môn (giáo lý cụ thể, quan niệm phong thuỷ cụ thể, tội danh/điều luật cụ thể...) xuất hiện trong kịch bản PHẢI có trong facts đã cho -- phương án nào TỰ THÊM khái niệm/thuật ngữ KHÔNG có trong facts (dù đúng thật ngoài đời, dù hợp lý với chủ đề kênh) → LOẠI. Đây là rủi ro ĐẶC THÙ của category tin tức: khác Category 2/3 (có research draft đã qua kiểm chứng làm nền), category này CHỈ có đúng đoạn nguồn người dùng dán -- không được lấy "kiến thức nền" ngoài facts làm căn cứ, dù mô hình "biết" điều đó đúng.
- Đây là nội dung TIN TỨC/BÌNH LUẬN, KHÔNG phải giải trí -- vẫn phải giữ giọng điệu phù hợp kênh (VD: kênh Phật giáo bình luận thời sự theo góc nhìn suy ngẫm/đạo đức chứ không thuần tường thuật; kênh Hình Sự tường thuật khách quan, không suy đoán tội danh trước khi có kết luận chính thức; kênh Phong Thuỷ liên hệ đúng khuôn khổ truyền thống, không suy diễn "điềm báo" ngoài những gì nguồn tin nói) -- NHƯNG không được phá vỡ nguyên tắc "chỉ dùng facts" ở trên để đạt được giọng điệu đó.""",
}


def category_rubric_block(category: str) -> str:
    if category not in CATEGORY_RUBRICS:
        raise ValueError(f"Category không hợp lệ: {category} (phải là 1 trong {list(CATEGORY_RUBRICS)})")
    return CATEGORY_RUBRICS[category]
