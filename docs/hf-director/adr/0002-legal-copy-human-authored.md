# Mọi câu chữ mang khẳng định pháp lý phải do người viết đặt tay

Renderer chỉ được sinh chữ **thuần định dạng** từ dữ liệu có cấu trúc:
`2000000 → "2 TRIỆU"`, `1963 → "1963"`. Mọi nhãn mang nội dung khẳng định — ví
dụ "Dưới 2 triệu — xử phạt hành chính" — phải là editorial override do người
viết đặt trong plan. Director không được sinh loại chữ này, kể cả khi model đủ
tự tin.

Lý do: đây là kênh phổ biến kiến thức pháp luật đăng công khai. Một nhãn như
trên không phải là nhãn, nó là một khẳng định về hậu quả pháp lý. Sai một chữ
trong đó không phải lỗi hiển thị, mà là thông tin sai đưa tới hàng nghìn người
kèm hình ảnh làm nó trông như đã được kiểm chứng.

## Consequences

Figure `threshold` render được ngay mà không cần người viết gì — chỉ là nó sẽ
hiện "Dưới 2 triệu / Từ 2 triệu" trung tính cho tới khi có override. Đó là
trạng thái chấp nhận được, không phải lỗi.
