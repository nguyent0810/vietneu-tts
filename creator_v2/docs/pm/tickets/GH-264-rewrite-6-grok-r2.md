# GH-264 — Viết lại lần 2: 6 Short CL (Grok)

## Vì sao làm lại
Lần 1 (`GH-264-rewrite-9-lines.json`) giữ nguyên danh sách dữ kiện cũ, rồi chỉ chèn 1–2 câu như "Bạn nhớ lời bầu hay con tem." Kết quả vẫn khô, câu chèn thì khó hiểu. Lead đã viết 3 bài mẫu đạt giọng. **Đọc kỹ trước khi viết:** `docs/pm/tickets/GH-264-samples-lead.json`, gồm Bao lời cấm, Nezumi và Oppert.

Bài mẫu làm được ba việc:
- **Bỏ dữ kiện phụ** để lấy chỗ kể, ví dụ ngày sinh, số người trên tàu, linh mục Féron. Vùng 1 nghĩa là không sửa sai, không phải giữ đủ.
- Có **một mạch**: tình thế, cú chặn, cái giá với con người, câu kết đọng lại.
- Câu vùng 2 và 3 **rõ nghĩa khi nghe một lần**. Không dùng câu cụt kiểu "Vai tuồng. Túi rỗng."

## 6 bài
`cl-bao-s2-song-hue-dan`, `cl-bao-s2-au-duong-tu`, `cl-a-vien-minh-vien-1860`, `cl-a-phaulkon-1688`, `cl-a-manila-1762`, `cl-a-mayrena-1888`.

Dữ kiện lấy từ `lines` và `sources` của `data/stier/specs/<slug>.json`. Đọc thêm `docs/pm/storytelling-guide.md` (v3).

## Luật
- Không thêm dữ kiện cụ thể mới về người thật. Không tự tính ra số mới.
- Câu 1: tối đa 9 từ, có tên hoặc số của tiêu đề, là nghịch lý.
- Đổi dạng mở giữa các bài liền nhau. Ba bài mẫu đã dùng: nghịch lý, nhận định phổ biến → hồ sơ, "Thử nghĩ xem" / "Thử đặt mình".
- Bao: câu cuối mời xem bản dài Bao Thanh Thiên một cách tự nhiên, mỗi bài một kiểu. Châu Á: kết bằng ý nghĩa hoặc câu hỏi rõ nghĩa.
- 100–135 từ. Số viết bằng chữ. Không `?`, "...", ngoặc, gạch ngang.
- Tránh từ gọi tên cảm xúc dựng sẵn và giọng giảng đạo lý.
- Phaulkon: không gộp "bị xử" với "lúc vua hấp hối". Spec nói binh biến khi vua sắp mất, ông bị xử ngày năm tháng sáu.

## Ghi
Ghi vào `docs/pm/tickets/GH-264-rewrite-6-r2.json` theo dạng giống file mẫu (`lines_v3`, `zones`, `so_tu`, `giay`, `ghi_chu`). Dùng Python utf-8, `ensure_ascii=False`.

Không sửa spec, không render, không commit.

## Báo cáo
`docs/pm/tickets/GH-264-rewrite-6-r2-report.md`: mỗi bài ghi dạng mở, dữ kiện đã bỏ, và câu nào là vùng 2 hoặc 3.
