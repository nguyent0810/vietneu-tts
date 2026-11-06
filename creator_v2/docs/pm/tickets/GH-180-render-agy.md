# GH-180: render 9 Short CK (17–19/11)

**Spec đã qua preflight** (`data/stier/specs/`):
- ck-e5-thuong-tet-khau-tru
- ck-e6-bon-trieu-tam-rut-mot-lan
- ck-a2-mot-nua-sau-muoi-sau-nam
- ck-e5-mot-dua-tre-mot-to-dang-ky
- ck-e6-tro-cap-540-nghin
- ck-a2-thang-chin-nam-phay
- ck-dien-sinh-hoat-bac-mot-1901
- ck-ho-kinh-doanh-duoi-mot-ty
- ck-tran-tro-cap-that-nghiep-26-trieu

**Đọc:** `motion/stier/README.md`, skill `../.claude/skills/shorts-studio/SKILL.md`, `AGENTS.md`.

**Việc:**
1. Dựng và render từng Short bằng đúng lệnh trong README (`python motion/stier/build.py <slug>` hoặc lệnh render tương ứng). Có TTS giọng theo chuẩn CK, nhạc nền nhỏ theo chuẩn mix. Mỗi lần chỉ chạy một render; render lock tự xếp hàng.
2. Mỗi Short tạo ảnh QA (`qa_t*.png` hoặc contact sheet, cách các Short CK đã làm). Soát:
   - chữ đúng dấu;
   - nhãn VÍ DỤ GIẢ ĐỊNH (cảnh có `hypo`) rõ và không đè tiêu đề;
   - phụ đề khớp lời;
   - không có chữ "giả định" cỡ nhỏ còn sót;
   - số trên hình khớp lời;
   - thời lượng 25–40 giây.
3. Nghe lại phần đọc số và tên: số đọc đúng, không nuốt chữ.

**Không:** enqueue, upload, đổi lịch, sửa spec. Spec lỗi thì ghi vào báo cáo.

**Báo cáo** `docs/pm/tickets/GH-180-render-report.md` (UTF-8): bảng 9 Short gồm file mp4, thời lượng, đường dẫn ảnh QA, kết quả soát và lỗi nếu có.
