# GH-228 — Báo cáo sản xuất lô Short CL 2

**Hoàn tất.** Đã viết đủ 14/14 spec (`data/stier/specs/cl-*.json`): 6 bài L (4 Hòa Thân, 2 Bao Thanh Thiên) và 8 bài S trải rộng nhiều quốc gia (Anh, Pháp, Mỹ, Ireland, Scotland, Ý, Áo) qua các thế kỷ 18, 19, 20.

Toàn bộ 14 spec tuân thủ đầy đủ các luật kế thừa và bài học rút ra từ lô 1:
- **Ảnh:** Mỗi bài có 4 ảnh khác biệt; không ảnh nào xuất hiện quá 2 cảnh trong cùng một bài; **không dùng lại bất kỳ ảnh nào trong 40 ảnh đã dùng ở lô 1**; và **không có ảnh nào trùng nhau giữa 14 bài trong lô 2** (tổng cộng 56/56 ảnh duy nhất);
- **Cảnh mở:** Phân bổ đều giữa các dạng `photo` (4 bài), `ledger` (2 bài), `quote` (2 bài), `date` (2 bài), `split` (2 bài), `counter` (1 bài), `file` (1 bài); không dùng ảnh hồ sơ/FBI mở đầu ở quá 1 bài;
- **Đa dạng hình ảnh:** 14/14 bài có chuỗi loại cảnh hoàn toàn khác biệt; không có khung mốc năm nhỏ trên nền trống;
- **Cụm slam:** Loại bỏ hoàn toàn chữ slam chung kiểu "DẤU VẾT"; 14/14 cụm slam là cụm 2–4 chữ in hoa lấy từ chính lời đọc của bài đó, không trùng lặp;
- **Lời thoại:** Hook ≤ 9 từ (8–9 từ); độ dài ước tính 27,9s – 36,7s (92 – 121 từ, ngưỡng 25–40s); tiêu đề ≤ 60 ký tự; số làm tròn dễ nghe; truyền thuyết gắn nhãn "theo giai thoại" / "chính sử"; không mô tả bạo lực hay xác chết.

## Bảng thông số 14 Short lô 2

| Slug | Loại | Giờ VN | publish_at UTC | Số ảnh | Chuỗi loại cảnh | Số từ | Preflight | Cụm slam |
|---|---|---|---|:---:|---|:---:|---|---|
| cl-irish-crown-jewels-1907 | S | 16/11 12:00 | 2026-11-16T05:00:00Z | 4 | photo → date → ledger → slam → split → quote | 103 | OK, 31,2s | KÉT SẮT NGUYÊN VẸN |
| cl-hoa-than-ham-chua-bac | L | 16/11 19:00 | 2026-11-16T12:00:00Z | 4 | ledger → file → counter → slam → photo → quote | 92 | OK, 27,9s | HẦM CHÔN BẠC |
| cl-george-smith-bon-tam | S | 17/11 12:00 | 2026-11-17T05:00:00Z | 4 | quote → file → split → slam → photo → ledger | 97 | OK, 29,4s | KÉO CHÂN NẠN NHÂN |
| cl-bao-ba-chiec-dao | L | 17/11 19:00 | 2026-11-17T12:00:00Z | 4 | date → split → photo → slam → file → quote | 101 | OK, 30,6s | BA CHIẾC ĐAO |
| cl-tranh-mona-lisa-1911 | S | 18/11 12:00 | 2026-11-18T05:00:00Z | 4 | photo → split → date → slam → ledger → quote | 104 | OK, 31,5s | TRANH TRONG PHÒNG TRỌ |
| cl-hoa-than-su-doan-anh | L | 18/11 19:00 | 2026-11-18T12:00:00Z | 4 | split → photo → file → slam → ledger → quote | 108 | OK, 32,7s | TỪ CHỐI SỨ ĐOÀN |
| cl-clifford-irving-hoi-ky | S | 19/11 12:00 | 2026-11-19T05:00:00Z | 4 | counter → photo → file → slam → split → ledger | 115 | OK, 34,8s | CUỘC GỌI VẠCH MẶT |
| cl-bao-can-vua-quy-phi | L | 19/11 19:00 | 2026-11-19T12:00:00Z | 4 | file → quote → split → slam → photo → ledger | 105 | OK, 31,8s | BÃI HAI CHỨC QUAN |
| cl-great-train-robbery-1963 | S | 20/11 12:00 | 2026-11-20T05:00:00Z | 4 | photo → date → split → slam → file → ledger | 109 | OK, 33,0s | VÂN TAY TRÊN BÀN CỜ |
| cl-hoa-than-hon-uoc-cong-chua | L | 20/11 19:00 | 2026-11-20T12:00:00Z | 4 | ledger → photo → split → slam → file → quote | 121 | OK, 36,7s | THA TỘI CHẾT |
| cl-kim-cuong-hope-1792 | S | 21/11 12:00 | 2026-11-21T05:00:00Z | 4 | quote → date → photo → slam → split → ledger | 112 | OK, 33,9s | NĂM ĐÊM ĐỘT NHẬP |
| cl-hoa-than-dac-an-cuoi-ngua | L | 21/11 19:00 | 2026-11-21T12:00:00Z | 4 | date → photo → file → slam → ledger → quote | 104 | OK, 31,5s | CƯỠI NGỰA VÀO CUNG |
| cl-victor-lustig-ban-thap-eiffel | S | 22/11 12:00 | 2026-11-22T05:00:00Z | 4 | split → date → file → slam → photo → ledger | 100 | OK, 30,3s | BÁN THÁP PHẾ LIỆU |
| cl-khoi-da-dinh-menh-1950 | S | 22/11 19:00 | 2026-11-22T12:00:00Z | 4 | photo → file → counter → slam → split → quote | 111 | OK, 33,6s | KHỐI ĐÁ ĐỊNH MỆNH |

## Lệnh và cổng kiểm tra

1. **Khảo sát và tìm đề tài:**
   - Đối chiếu script và factcheck video dài `data/long/hoa-than/` và `data/long/bao-thanh-thien/`. 6 bài L khai thác các sự thật lịch sử đã được kiểm chứng (hầm chôn 3 triệu lạng bạc, từ chối sứ đoàn Macartney, hôn ước công chúa cứu phò mã, đặc ân cưỡi ngựa biến thành tội; 3 chiếc đao trảm không có trong Tống sử, dâng tấu can ngăn thăng quan cho bác Quý phi). Không trùng 6 bài L của lô 1.
   - Tìm kiếm và đối chiếu 8 đề tài vụ án mới (S) chưa từng làm trên kênh, có nguồn tư liệu mở được trên Wikipedia / Commons / lưu trữ lịch sử.
2. **Kiểm tra trùng lặp tài sản ảnh:**
   - Kiểm tra chéo toàn bộ danh sách `imgs` của 12 spec lô 1: phát hiện 40 ảnh đã dùng ở lô 1.
   - Chọn lọc 56 ảnh hoàn toàn mới (24 ảnh tư liệu từ kho của Long và 32 ảnh Commons/kho tài sản `output/asset_library/`), đảm bảo:
     - 0 ảnh trùng lô 1;
     - 0 ảnh trùng lặp giữa 14 bài lô 2;
     - Mỗi bài có đúng 4 ảnh riêng biệt, mỗi ảnh dùng tối đa 2 cảnh.
3. **Preflight:**
   - Chạy lệnh: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe motion/stier/build.py --preflight <slug>` cho toàn bộ 14 spec.
   - Kết quả: **14/14 đạt OK**. Thời lượng ước tính từ 27,9 giây đến 36,7 giây (nằm hoàn toàn trong khung 25–40s).
4. **Script Lint:**
   - Chạy lệnh: `PYTHONPATH=. .venv/Scripts/python.exe motion/stier/script_lint.py <slug>` cho toàn bộ 14 spec.
   - Kết quả: **0 lỗi cứng** trên cả 14 bài. Các cảnh báo còn lại là cảnh báo phong cách thường thấy ở Short CL (câu cuối khẳng định thay vì hỏi theo quy định §7; nhịp ngắt mệnh đề cho giọng đọc tự nhiên; bổ sung đầy đủ phát âm `say` cho tên riêng nước ngoài).
5. **Kiểm tra lỗi mã hóa và mất dấu:**
   - Quét regex `\w\?\w` trên toàn bộ 14 file spec: **0 ký tự lỗi / mất dấu**. Toàn bộ file spec được ghi bằng Python `encoding="utf-8"`, `ensure_ascii=False`.
6. **Lập danh sách lời và nguồn:**
   - Đã ghi đầy đủ lời đọc, nguồn đối chiếu, loại S/L, chuỗi loại cảnh, cụm slam vào `docs/pm/tickets/GH-228-cl-shorts2-lines.md`.

## Giới hạn và tuân thủ

- Theo đúng quy định của ticket và AGENTS.md: **Không chạy lệnh render**, không tạo clip sheet hay thumbnail, không enqueue, không upload lên YouTube, không thay đổi lịch phát sóng trong cơ sở dữ liệu thật (`state.sqlite`), không thực hiện lệnh git (`git commit`, `git push`, `git checkout`).
