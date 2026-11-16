# Báo cáo soát kịch bản v3 Địch Nhân Kiệt (GH-395-check)

**Ngày thực hiện:** 15/11/2026  
**Vai trò:** Người soát theo `docs/pm/storytelling-guide.md` §14 mục 2 (chỉ chặn 4 loại lỗi dữ kiện/an toàn, không can thiệp giọng văn, không cắt cảnh phỏng dựng `{pd}` hay giả thuyết).  
**Tài liệu đối chiếu:** `data/long/cl-dich-nhan-kiet/script.v3.md` so với `data/long/cl-dich-nhan-kiet/factcheck.md`.

---

## 1. Tổng kết 4 loại lỗi theo brief

| Loại lỗi | Số lượng tìm được | Ghi chú |
|---|:---:|---|
| **Loại 1:** Câu nói sai dữ kiện so với `factcheck.md` (tên, năm, nơi, quan hệ, ai làm gì) | **1** *(+ 1 lưu ý ở tiêu đề)* | CH03 câu 107 nhầm lăng Hán Cao Tổ (Trường Lăng) thành "lăng cha nhà vua" Đường Cao Tông. Tiêu đề 3 dùng sai đơn vị "án" thay vì "người". |
| **Loại 2:** Con số / ngày không có trong `factcheck.md` | **0** | Toàn bộ mốc năm, ngày, số lượng trong kịch bản đều có nguồn đối chiếu trong factcheck.md. |
| **Loại 3:** Lời trích `»` / `[TRÍCH DỊCH]` không khớp nguyên văn trong `factcheck.md` | **0** | Đã đối chiếu tự động và thủ công toàn bộ 37 câu `[TRÍCH DỊCH]`: khớp 100% từng chữ với bản dịch của factcheck.md. |
| **Loại 4:** Bịa lời nói hay cảm xúc cho người còn sống; nội dung nguy hiểm | **0** | Người còn sống được nhắc đến (Lương Quán Hoa, Lưu Đức Hoa, Từ Khắc ở CH13) chỉ được nêu vai trò làm phim/đóng phim lịch sử năm 2004, 2010; không bịa lời nói, nội tâm hay cảm xúc; không có nội dung nguy hiểm. |

---

## 2. Bảng chi tiết các lỗi tìm được

| Chương | Câu (trích nguyên câu) | Loại lỗi (1–4) | Dòng factcheck liên quan | Cách sửa tối thiểu (một câu thay thế giữ giọng kể) |
|---|---|:---:|---|---|
| **CH03** (câu 107) | `Một nắm đất ở lăng cha nhà vua: ví dụ nhỏ, nhưng đặt đúng vào chỗ nhà vua đang tự hào là người con hiếu.` | **1** | Dòng 248 (`Trường Lăng (lăng Hán Cao Tổ)`) & Dòng 86 (`Chiêu Lăng là lăng Thái Tông`) | `Một nắm đất ở lăng Hán Cao Tổ: ví dụ nhỏ, nhưng đặt đúng vào chỗ nhà vua đang tự hào là người con hiếu.` |
| **Mở đầu** (dòng 10, Tiêu đề 3 - lưu ý cho Lead) | `3. Xử 17.000 Án Không Ai Kêu Oan, Rồi Tự Nhận Mình Phản? (53 ký tự)` | **1** | Dòng 79, 80, 215 (`Đơn vị: người (S1, S2, W2); quy đổi cho tai: "17.000 người", không phải án/vụ`) | `3. Xử Xong Cho 17.000 Người Không Ai Oan, Rồi Nhận Mình Phản? (57 ký tự)` *(hoặc dùng Phương án 1 hoặc 2)* |

---

## 3. Phân tích chi tiết từng điểm kiểm tra

### 3.1. Lỗi Loại 1 tại CH03 (câu 107)
- **Hiện trạng trong kịch bản:**
  - Câu 106: `Ông còn hỏi thêm một điều: nếu có kẻ trộm một nắm đất ở Trường Lăng, bệ hạ sẽ xử ra sao?`
  - Câu 107: `Một nắm đất ở lăng cha nhà vua: ví dụ nhỏ, nhưng đặt đúng vào chỗ nhà vua đang tự hào là người con hiếu.`
- **Đối chiếu factcheck.md:**
  - Dòng 86: Cây bách bị chặt trộm nằm ở Chiêu Lăng (lăng của Đường Thái Tông - cha của hoàng đế Đường Cao Tông Lý Trị).
  - Dòng 247-248: Điển tích thời Hán kể lại việc Trương Thích Chi can Hán Văn Đế khi có kẻ trộm ngọc ở miếu Hán Cao Tổ. Trương Thích Chi hỏi: *"Giả như có kẻ lấy trộm một nắm đất ở Trường Lăng [lăng Hán Cao Tổ - cha Hán Văn Đế], thì bệ hạ dùng thêm hình phạt gì?"*. Địch Nhân Kiệt dẫn lại câu hỏi này trước Đường Cao Tông.
  - Trường Lăng là lăng Hán Cao Tổ (thời Hán), không phải lăng cha Đường Cao Tông (lăng cha Cao Tông là Chiêu Lăng). Câu 107 viết `"lăng cha nhà vua"` trong bối cảnh đang nói chuyện với Đường Cao Tông khiến người nghe hiểu sai rằng Trường Lăng là lăng mộ cha của Đường Cao Tông.
- **Sửa tối thiểu:** Thay cụm từ `"lăng cha nhà vua"` bằng `"lăng Hán Cao Tổ"` (hoặc `"lăng tiên đế thời Hán"`), giữ nguyên toàn bộ nhịp điệu và giọng kể.

### 3.2. Lưu ý Tiêu đề 3 (dòng 10)
- Tiêu đề 3 ghi `"Xử 17.000 Án"`. Trong khi đó, dòng 79, 80 và dòng 215 của `factcheck.md` ghi chú rất rõ: đơn vị chính sử ghi nhận là 17.000 người (`萬七千人`), không dùng đơn vị `"án"` (án dồn đọng của 17.000 người). Trong thân bài (câu 26, câu 75), người viết đã tuân thủ rất tốt (`"án tồn của 17.000 người"`). Để đồng nhất, Lead nên chọn Phương án 1 hoặc 2, hoặc chỉnh Tiêu đề 3 theo đơn vị người.

### 3.3. Kiểm tra Loại 2 (Con số và ngày tháng) — 0 lỗi
- Đã kiểm tra toàn bộ các mốc thời gian: 630 (sinh), 659 (minh kinh), 674 (Thiên Hoàng/Thiên Hậu), 675 (đại lý thừa), 676 (chặt bách Chiêu Lăng), 679 (hặc Vi Hoằng Cơ), 688 (đốt 1.700 miếu Giang Nam & sự biến Dự Châu), 690 (lập triều Võ Chu), 691 (làm tể tướng), 692 (vụ án Lai Tuấn Thần & Nghiêm Thiện Tư), 696 (Khiết Đan hạ Ký Châu, ra Ngụy Châu), 697 (Lai Tuấn Thần bị xử tử, sớ bỏ 4 trấn), 698 (Mặc Chuyết hạ Triệu/Định Châu, rước Lư Lăng vương), 700 (can dựng đại tượng Phật, quốc lão qua đời), 704 (dị bản năm mất), 705 (biến Thần Long), 1949 (van Gulik dịch truyện), 2004 (phim Lương Quán Hoa), 2010 (phim Từ Khắc).
- Toàn bộ các con số định lượng (17.000 người, 2 tướng, 3 câu can, 3 cung, hàng vạn người đào đường, mấy trăm lính Kỳ Châu, 1.700 ngôi miếu, 4 ngôi miếu giữ lại, 600-700 gia đình / 5.000 người tịch thu / 2.000 người án tử ở Dự Châu, 3 ngày ăn chay, hơn 850 người nhận tội oan, 7 người trong danh sách / 3 tể tướng, cậu bé chưa mười tuổi, hơn bốn mươi năm của Lâu Sư Đức, 1 vạn người bị Mặc Chuyết giết, 10 vạn quân đuổi theo, 5 vạn quân mộ trong 10 ngày, tượng Phật hàng triệu, 12 chữ vàng...) đều có căn cứ khớp từng dòng trong `factcheck.md`.

### 3.4. Kiểm tra Loại 3 (Lời trích » / [TRÍCH DỊCH]) — 0 lỗi
- Script có 37 câu trích thoại gắn nhãn `[TRÍCH DỊCH]`. Script kiểm tra đối chiếu tự động cho thấy 37/37 câu đều khớp chính xác từng ký tự với cột `TRÍCH DỊCH` trong `factcheck.md`. Không có hiện tượng sửa lời trích hay bịa đặt trích dẫn.

### 3.5. Kiểm tra Loại 4 (Người còn sống & nội dung an toàn) — 0 lỗi
- Không có nhân vật còn sống nào bị gán lời thoại, suy nghĩ hay cảm xúc. Các nhân vật đương đại xuất hiện ở CH13 chỉ gồm diễn viên Lương Quán Hoa, Lưu Đức Hoa và đạo diễn Từ Khắc với tư cách là người tham gia các tác phẩm phim ảnh đã phát sóng năm 2004 và 2010.
- Không có nội dung nguy hiểm, độc hại hoặc vi phạm quy tắc an toàn.

---

## 4. Kết luận
Kịch bản `script.v3.md` có chất lượng bám sát tư liệu rất cao, tuân thủ chặt chẽ các cổng kiểm chứng và quy tắc kể chuyện v3 (§14).  
Chỉ có **duy nhất 01 lỗi sai dữ kiện (Loại 1) tại CH03 (câu 107)** cần chỉnh sửa thay thế bằng câu tối thiểu giữ giọng kể trước khi Lead duyệt thu âm.
