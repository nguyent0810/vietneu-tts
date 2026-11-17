# Brief giao người viết Long

Lead điền mẫu sau plan đã duyệt; quy trình phê duyệt giữ trong SKILL.md. Chuẩn chung: [audio-script](../../../../docs/script/audio-script.md); hồ sơ [BUD](../../../../docs/script/profiles/bud.md)/[FS](../../../../docs/script/profiles/fs.md), [Long chuẩn](../../../../docs/script/profiles/long-standard.md) và khuôn của tập. Lời kể có tiến triển/cảm xúc, không kéo dài cho đủ giờ; các mẹo show/callback/tương phản là gợi ý nghề.

## NHIỆM VỤ
Long `<id>` · kênh `<...>` · khuôn `<...>` · engine `<...>` · người nghe `<...>`.
Lời hứa một câu `<...>` · câu trả dự kiến `<...>` · motif nếu cần `<...>`.
Giọng/ruleset/tempo/pause `<...>` · đích `<phút>` · ngân sách theo [bảng giọng](../../../../docs/script/voice-rates.md), ghi rõ ước hay đo.
Plan duyệt `<path>` · nghiên cứu `<path>` · beat sheet `<path>` · ngày hiệu lực `<ngày có thật>`.
Dữ kiện quan trọng `<3–5 ý>` · điểm chưa chắc `<...>` · phạm vi phỏng dựng theo hồ sơ `<...>`.

## 120 GIÂY ĐẦU: CÂU TRỌN, NHỊP HÌNH RIÊNG
PO17/11: ảnh/clip động≤8s, tĩnh≤4s, chữ nền trống≤1,5s; mục tiêu3–8s/ảnh, đổi ở ý mới. Bỏ ép mười tiếng/ba giây mỗi câu; viết theo nhịp ý, không tách cụm từ/năm thành mảnh cụt. Hình theo gợi ý ý/cảnh trong notes, workflow hình hiện tại quyết cách gắn; không bắt một ảnh mới vì một câu mới trong luật audio.
Giữ kiểm hình `pace_gate_issues(row,segs)`/`opening_gate(row,segs)` ở phiên sản xuất đúng segments, không chạy renderer để kiểm lời. Ngưỡng/loại visual mở theo long-video, không đổi code cổng.

## BÀN GIAO VÀ TỰ SỬA
`nhap_<id>.txt`: một câu/dòng, heading **đậm trọn**. `source_notes_<id>.md`: nguồn của claim/quote/số, diễn giải/phỏng dựng/nhãn theo hồ sơ, ngân sách/giọng/clock và điểm chưa chắc.
Chạy `.venv/bin/python long_script_lint.py nhap_<id>.txt --strict`; chép kết quả thật, CB sửa hoặc ghi lý do. Làm [vòng viết→tự chấm→sửa và phiếu8 mục](../../../../docs/script/audio-script.md#7-viết--tự-chấm--sửa). Ghi dòng trước→sau và vì sao; không coi phiếu là cổng hay tự gọi kiểm độc lập. Routing người viết/reviewer giữ theo Lead.
