---
status: accepted — supersedes ADR-0003
---

# Bỏ Gemini và bỏ cổng duyệt của người; thay bằng ràng buộc máy kiểm được

Ưu tiên đổi sang **tốc độ và tự động hoàn toàn**. Director giờ là rule thuần:
không gọi LLM, không có bước người duyệt, không có `needs_human_figure`, không
có gì chặn đăng ngoài chính hợp đồng schema.

ADR-0003 dựa trên lập luận "AI đề xuất, người chốt". Lập luận đó vẫn đúng với
thứ nó thực sự bảo vệ — nhưng nó bảo vệ **sai chỗ**: cổng chỉ chặn khi director
*tự biết mình không chắc*. Lỗi nguy hiểm thật lại là lúc director **chắc chắn
mà sai**: câu "phạt tiền từ mười đến năm mươi triệu đồng" bị đọc thành ngưỡng
`50 triệu trở lên` với confidence 0.92 — không bao giờ lọt vào diện cần duyệt.

## Cái gì thay thế người

Ba ràng buộc máy, kiểm được bằng test, không phụ thuộc ai nhớ:

1. **Không còn văn xuôi do máy sinh.** Bỏ LLM nghĩa là director chỉ còn xuất
   số và trích đoạn nguyên văn. `_steps_are_verbatim()` vẫn ép phần trích đoạn.
   ADR-0002 nhờ vậy được giữ *về mặt cơ chế* chứ không phải nhờ kỷ luật: không
   có thành phần nào trong đường ống còn khả năng viết một mệnh đề pháp lý.
2. **Dải giá trị không được đọc thành ngưỡng.** Thêm figure type `range`
   (`from`/`to`); mọi câu có cấu trúc "từ A đến B" bắt buộc đi vào `range` hoặc
   `none`, tuyệt đối không được thành `threshold`/`stat`.
3. **Nhãn pháp lý vẫn chỉ đến từ người.** `figure_labels` không đổi. Không ai
   viết thì renderer hiện chữ trung tính thuần định dạng — chấp nhận được, và
   đó là trạng thái mặc định mới.

## Hệ quả

`needs_human_figure` biến mất khỏi hợp đồng: một trường không còn ai đọc là
trường sẽ lệch. `publish_gate()` giữ lại nhưng chỉ còn kiểm hợp đồng schema —
đó là kiểm tra máy, không phải duyệt người.

Rủi ro chấp nhận có ý thức: một rule sai kiểu mới sẽ ra thẳng kênh, không có
lưới đỡ. Đổi lại là đường ống chạy không cần người. Khi phát hiện một lớp sai
mới, cách xử lý đúng là **thêm ràng buộc + test**, không phải dựng lại cổng
duyệt.
