# HF Director

Lớp quyết định **câu nào trong một Short nên được biểu diễn bằng hình gì**, đặt
giữa kịch bản và bộ dựng HyperFrames. Tồn tại vì quyết định đó phụ thuộc nội
dung từng câu, nhưng phải tái lập được và phải có chỗ cho người chốt trước khi
video lên kênh.

## Language

### Quyết định

**Figure**:
Một quyết định *ngữ nghĩa* rằng một câu nên được biểu diễn bằng hình, gồm
`type` + `data` + `confidence` + `source` (+ `relation` nếu có). Không chứa
thông tin hình học hay chữ hiển thị.
_Avoid_: chart, graphic, visual, biểu đồ

**Figure type**:
Loại biểu diễn: `none` · `threshold` · `range` · `flow` · `timeline` · `stat`.
_Avoid_: kind, figure kind

**Threshold vs Range**:
`threshold` là MỘT mốc có phía ("từ 2 triệu trở lên"); `range` là HAI đầu của
một dải ("từ 10 đến 50 triệu"). Đọc dải thành ngưỡng là lớp lỗi khiến ADR-0005
phải thay ADR-0003 — có test hồi quy riêng.

**Presentation props**:
Toạ độ, tỉ lệ, cỡ chữ, nhãn định dạng — do `engine.js` tính từ Figure tại lúc
render. Không bao giờ được lưu vào plan.
_Avoid_: style, layout data

**Relation**:
Quan hệ giữa hai Figure trong cùng một Short, khai báo ngay trên Figure:
`{"pairs_with": <sentence_id>, "role": "contrast"}`.
_Avoid_: link, pair, group

### Nguồn và thẩm quyền

**Source**:
Ai ra quyết định cho một Figure: `rule` · `human`. (`gemini` đã bị loại khỏi
đường ống ở ADR-0005; giá trị này chỉ còn gặp ở plan cũ.) Quyết định của
`human` không bị lượt chạy sau ghi đè.
_Avoid_: author, origin, decided_by

**Editorial override**:
Chữ do người viết đặt tay trong plan, dùng cho mọi câu chữ mang **khẳng định
pháp lý**. Renderer chỉ được sinh chữ thuần định dạng (số, đơn vị, ngày).
_Avoid_: label, caption, copy

**sentence_id**:
Số nguyên **1-based**, chỉ mục vào `script[]` của plan.
_Avoid_: Q3, line number, index (0-based)

**Sửa tay**:
Đổi một figure sang `source: "human"`. Không còn bước duyệt bắt buộc (ADR-0005),
nhưng figure đã sửa tay vẫn không bị lượt chạy sau ghi đè, trừ khi `--force`.
_Avoid_: approval, confirm, sign-off

### Đơn vị

**Sentence**:
Một dòng trong `script[]` của plan — đơn vị ra quyết định duy nhất của
Director. Một Short có đúng 5 Sentence.
_Avoid_: line, beat, segment, câu thoại

**Beat**:
Đơn vị 18–25 giây của `creative_director.py` cho video dài. **Không** dùng cho
Short — hai hệ thống này cố ý không chia sẻ đơn vị thời lượng.
