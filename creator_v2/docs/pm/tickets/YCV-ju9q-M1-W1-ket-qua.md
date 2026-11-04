# Kết quả YCV-ju9q · M1 W1

## Vòng 3

- Đã bổ sung §9 trong `data/long/mim-jobs-1985/research.md`, từ #29 đến #36.
- Đã viết lại toàn bộ `script.md`: 9 chương, tiêu đề `Steve Jobs 1985: Bị Gạt Khỏi Apple, Thành Đường Quay Lại` (56 ký tự, một dấu `:`), câu hỏi trung tâm giữ nhất quán và phần kết trả lời trực tiếp.
- Đã bỏ các đoạn lặp 400/427 triệu, 50 nghìn máy, 230/530 người, chia khoản Pixar, các mốc quay lại Apple và phần kể lại toàn bài ở CH08. Đã bỏ câu meta về cách đọc số.
- [TRÍCH DỊCH] của Jobs được chuyển sang CH03. Lời nhìn lại của Sculley giữ quy dẫn trong câu.
- Đã cập nhật `factcheck.md`, gồm nguồn cho mọi năm nêu trong lời đọc, mục HÌNH và nguồn Commons hợp lệ cho máy NeXT. Không dùng ảnh phim.

### Dữ kiện mới

| # | Dữ kiện | Dùng trong |
|---:|---|---|
| 29 | NeXT Computer ra mắt năm 1988, giá cơ bản 6.500 USD | CH04 |
| 30 | Website đầu tiên đặt trên máy NeXT tại CERN; trình duyệt đầu tiên viết năm 1990 | CH05 |
| 31 | Toy Story ra rạp 22/11/1995, Pixar IPO 28/11/1995 | CH04 |
| 32 | Giá trị Pixar sau IPO | Không dùng số, để tránh thêm số liệu không cần thiết |
| 33 | Apple đàm phán với Be trước khi chọn NeXT | CH06 |
| 34 | NEXTSTEP trở thành nền của Mac OS X, phát hành tháng 3/2001 | CH07 |
| 35 | Thỏa thuận Apple–Microsoft tại Macworld Boston; Microsoft đầu tư 150 triệu USD | CH08 |
| 36 | Jobs góp phần tuyển Sculley từ Pepsi | CH01; câu “bán nước đường” **CHƯA KIỂM ĐƯỢC**, không dùng |

### Âm tiết và kiểm lệnh

```text
PYTHONIOENCODING=utf-8 python motion/long/script_lines.py mim-jobs-1985
→ 130 câu, 2.055 âm tiết, khoảng 9,8 phút; integrity qua.

PYTHONIOENCODING=utf-8 python motion/long/studio_lint.py mim-jobs-1985 --strict
→ 0 lỗi, 9 cảnh báo về mật độ câu ngắn.

PYTHONIOENCODING=utf-8 python scripts/long_gate.py mim-jobs-1985 --min-syl 2000
→ TRƯỢT, 23 lỗi.
```

### Bảng đếm số và ngày trong lời đọc

Đếm theo từng giá trị/mốc đầy đủ trong phần lời đọc, không tính số chương, tên file và phần chuẩn bị ở đầu tài liệu.

| Giá trị hoặc mốc | Số lần |
|---|---:|
| Tháng 9/1985 | 1 |
| 1983; 1984; 2005; 30 tuổi | 1 mỗi giá trị |
| 1988; 6.500 USD; 10 triệu USD | 1 mỗi giá trị |
| 1995; 22/11; 28/11 | 1 mỗi giá trị |
| 50 nghìn; 1993; 230; 530; 1990 | 1 mỗi giá trị |
| 400; 427; 7.081; 9.833; 1.045; 816 triệu USD | 1 mỗi giá trị |
| 7/2; 16/9; 2001; 150 triệu USD | 1 mỗi giá trị |

### Cổng tổng hợp chưa đạt

Ticket W1 chỉ cho phép ghi `script.md`, `factcheck.md`, báo cáo; vòng 3 chỉ bổ sung quyền ghi `research.md`. Trong topic hiện không có `gen_scenes.py`, `spec.json`, cảnh/hud, TTS hoặc HTML. Vì thế `long_gate` báo thiếu đủ 9 HUD/cảnh, thiếu TTS, thiếu `spec.youtube`/`say` và cảnh trung bình quá dài; đây là hạng mục dựng W2 ngoài phạm vi ghi của ticket.

Không tạo clip sheet hay thumbnail ở W1 vì chưa có cảnh dựng và ticket không cho phép render. Không có khẳng định dùng trong kịch bản nào chưa kiểm được; riêng câu trích tuyển Sculley nêu trên bị loại.
