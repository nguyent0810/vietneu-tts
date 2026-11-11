# GH-264 — Chốt storytelling-guide v3 (Codex, chỉ tài liệu)

## Đọc
- Issue #264 (bản sao nằm ở mục "Quyết định PO" bên dưới).
- Bản nháp v3: `docs/pm/storytelling-guide.v3-draft.md`.
- Review: `docs/pm/tickets/GH-262-storytelling-v3-review.md`.
- v2 thật: `docs/pm/storytelling-guide.md`, gồm cả bảng "Năm dạng mở" do Lead thêm.
- Phản biện cũ: `docs/pm/tickets/GH-248-storytelling-review-report.md`.
- 9 Short thật, trường `lines`: `data/stier/specs/cl-bao-s2-loi-cam.json`, `cl-bao-s2-song-hue-dan`, `cl-bao-s2-au-duong-tu`, `cl-a-nezumi-1831`, `cl-a-oppert-1868`, `cl-a-vien-minh-vien-1860`, `cl-a-phaulkon-1688`, `cl-a-manila-1762`, `cl-a-mayrena-1888`.

## Quyết định PO (10/11)
1. **Nội tâm nhân vật:** người viết tự cân nhắc, không chốt mốc thời gian hay danh sách nhân vật. Bắt buộc văn phong là **lời kể hấp dẫn cho người nghe**, không liệt kê, cứng, khô.
2. **Đo:** thiết kế ghép cặp. Giữ vài bài văn phong v2 làm đối chứng, đăng xen kẽ, đo giữ chân (AVP, tỉ lệ xem tiếp), quyết định ở mốc 7 ngày.
3. **Vùng tái dựng:** chi tiết văn hóa và bối cảnh được sáng tạo để tạo cảm xúc, không bắt nguồn thứ hai. Lằn ranh đỏ chỉ 3 điều của #262. BUD thêm: không gán cho Đức Phật lời hay việc không có trong kinh.
4. **Hướng linh hoạt:** phép thử chỉ là câu tự hỏi, lint chỉ cảnh báo. Chỉ các cổng preflight đã có mới chặn.

PO nhấn mạnh: *"không bịa khác với sáng tạo, phái sinh"*; luật cũ làm văn "rất robot".

## Việc: viết `docs/pm/storytelling-guide.md` = v3 (ghi đè v2)
1. Lấy bản nháp v3 làm khung. Sửa các chỗ ghi "chưa kiểm chứng" bằng cách đối chiếu với v2 thật và 9 bài thật.
2. **Nới theo quyết định PO 1 và 3:**
   - Bỏ mốc "khoảng một thế kỷ" và bỏ khuyến nghị cứng về tầng A/B/C. Giữ một câu nhắc người viết tự cân nhắc với nạn nhân và thân nhân còn sống.
   - Vùng 2a không cần nguồn thứ hai, không cần hedge cho bối cảnh văn hóa chung.
   - Mục "Ba cái bẫy" của vùng 3: viết lại, chỉ cảnh báo khi câu đó **khẳng định một sự kiện cụ thể mới** về người thật. Ví dụ "nỗi sợ lớn nhất của một gia đình thời ấy" là giọng kể, được phép.
3. Giữ từ v2: bảng "Năm dạng mở" và quy tắc đổi dạng giữa các bài liền nhau.
4. Mục 9 "mẫu hoàn chỉnh": thêm bản v3 của `cl-bao-s2-loi-cam`. Dùng đúng dữ kiện trong spec, giọng kể có cảm xúc như ví dụ trong #262. Đếm từ: 55–135 từ, câu 1 ≤ 9 từ, có số hoặc tên của tiêu đề.
5. Giữ ngắn và dễ dùng: tối đa khoảng 200 dòng, bảng nhiều hơn chữ.

## Thêm: đề xuất đoạn nối (chỉ viết vào báo cáo, KHÔNG sửa các file này)
- `creator_v2/AGENTS.md`: đoạn "Giọng kể" tối đa 8 dòng.
- `creator_v2/docs/codex/long-rules.md`: mục "Giọng kể" tối đa 1 trang.
- Hai dòng chuẩn cho mẫu brief viết lời.

## Ràng buộc
- **Chỉ ghi** `docs/pm/storytelling-guide.md` và file báo cáo.
- Không sửa code, spec, AGENTS.md hay long-rules.md. Không commit.
- Ghi bằng Python utf-8. Grep không có `?` thay chữ có dấu.

## Báo cáo
`docs/pm/tickets/GH-264-guide-v3-report.md` gồm:
- thay đổi so với nháp;
- các chỗ "chưa kiểm chứng" đã giải quyết thế nào;
- 3 đoạn nối đề xuất (nguyên văn).
