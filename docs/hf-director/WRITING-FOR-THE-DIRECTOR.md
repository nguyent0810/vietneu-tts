# Viết kịch bản để director nhìn thấy được

Director không hiểu nội dung. Nó nhận ra **hình dạng** của câu văn. Hai câu
nói cùng một ý, viết khác nhau, sẽ cho ra một câu có đồ hoạ và một câu không.

Đây không phải mẹo lách hệ thống — nó là cách viết rõ ràng hơn, và tiện thể
làm cho máy nhìn thấy.

## Bốn hình dạng director nhận ra

**Ngưỡng** — một con số kèm dấu hiệu mốc, dấu hiệu phải đứng **ngay trước** số.

- ✅ "Mốc khởi điểm là **hai triệu đồng**." · "Tỷ lệ tổn thương **từ mười một phần trăm trở lên**."
- ❌ "Tài sản phải đáng kể thì mới bị xử lý." (không có số)
- ❌ "Ba tấn vàng — nhiều hơn mọi tính toán." (chữ "hơn" ở xa số, và nói về kỳ vọng)

**Dải** — hai đầu, viết đủ "từ A đến B".

- ✅ "Phạt tù **từ sáu tháng đến ba năm**." · "Phạt tiền **từ mười đến năm mươi triệu đồng**."
- ❌ "Mức phạt cao nhất là ba năm tù." (chỉ một đầu → thành `stat`)

**Chuỗi bước** — các bước ngăn bằng **dấu phẩy**, "rồi", "sau đó".

- ✅ "Trang mở ra hỏi **số thẻ**, rồi **mã bảo mật**, rồi **mã OTP**."
- ❌ "Trang đó lần lượt hỏi các thông tin bảo mật của bạn." (không có ranh giới bước)
- Mỗi bước phải tự đứng được: từ 3 chữ trở lên, không quá 52 ký tự. Director
  chỉ **cắt** chữ của bạn, nó không bao giờ viết lại (ADR-0002).

**Dòng thời gian** — từ hai mốc năm trở lên, **rải đâu trong bài cũng được**.

- ✅ "Năm **1894**…" ở câu 1 và "…năm **1906**" ở câu 3 → một timeline.
- Tránh viết ngày đầy đủ khi không cần: "Rạng sáng **11 tháng 12 năm 1978**"
  bị bỏ qua có chủ đích, vì mảnh ngày tháng từng bị đọc nhầm thành số liệu.

## Ba điều nên biết

1. **Câu cuối luôn không có hình.** Viết câu chốt cho giọng đọc, đừng dồn số liệu vào đó.
2. **Tối đa 3 trên 5 câu có hình.** Nhồi số vào cả 5 câu chỉ khiến director bỏ bớt theo confidence, và bạn mất quyền chọn.
3. **Lane truyện hư cấu không bao giờ có hình.** Cứ viết truyện cho ra truyện.

## Mẹo thật sự hữu ích

Câu có **cả ngưỡng lẫn dải** thì director lấy cái **đứng trước**. Nếu mốc tiền
quan trọng hơn dải hình phạt, hãy viết mốc tiền trước — như `o03_b`, bài có
ba figure vì mỗi câu nói rõ đúng một hình dạng:

```
câu 2: mốc bốn triệu đồng          -> threshold
câu 3: từ sáu tháng đến ba năm     -> range
câu 4: vay mượn, rồi bỏ trốn, ...  -> flow
```

## Nhãn mang nội dung pháp lý

Renderer chỉ tự sinh chữ **thuần định dạng** ("2 TRIỆU", "TỪ 2 TRIỆU"). Mọi
câu chữ mang khẳng định — "dưới 2 triệu là xử phạt hành chính" — phải do người
viết đặt tay vào `figure_labels` của plan (ADR-0002). Không viết thì hình vẫn
hiện, chỉ là nhãn trung tính. Đó là trạng thái chấp nhận được, không phải lỗi.
