# GH-430 bake-off (codex)

Đề: viết lại lời kể **CH00–CH02** của Long CL Lưu Gù (`data/long/cl-luu-gu/`). Đọc: `script.md` (bản đang lên kênh, bị chủ kênh chê "không có storytelling gì hấp dẫn"), `script.v1.md`, `factcheck.md`, `docs/pm/storytelling-guide.md` (đặc biệt "Tiêu đề và mở đầu kiểu survival", "Cửa sổ sốc").

Luật mới của chủ kênh (15/11/2026): "cho phép phỏng đoán, phỏng tác dựa trên tư liệu lịch sử, quan trọng là hấp dẫn người nghe, cách kể chuyện sâu sắc hấp dẫn storytelling/document, văn phong hay cho người nghe". Cảnh phỏng dựng báo bằng lời ("hãy hình dung…", "có lẽ…") và đánh `{pd}` cuối câu. KHÔNG bịa bằng chứng, lời trích, con số; dữ kiện lịch sử phải khớp factcheck.md.

Yêu cầu: giọng phim tài liệu kể chuyện cuốn hút cho TAI (TTS tiếng Việt): câu ngắn–vừa xen kẽ, ≤ 32 âm tiết, hình ảnh cụ thể, xung đột và câu hỏi giữ chân cuối mỗi chương; câu sốc/nghịch lý trong 3 câu đầu; không chào/lộ trình trước 30 giây; rào nguồn gọn, tự nhiên (không mở mỗi câu bằng "theo…"). Giữ định dạng script (mỗi dòng một câu, ‖ ngừng dài, `»` lời trích, {beat: …}). Độ dài mỗi chương ±15% bản đang có.

Đầu ra: CHỈ một file `docs/pm/bakeoff-430/codex.md` (Markdown, ghi bằng Python utf-8 — không PowerShell), gồm 3 chương viết lại + cuối file 5 dòng "Tôi đã đổi gì so với bản cũ". Không sửa file khác, không commit, không gọi mạng.
