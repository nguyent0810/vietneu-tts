# Brief giao người viết Long

Lead điền mẫu sau plan đã duyệt; quy trình phê duyệt giữ trong SKILL.md. Chuẩn chung: [audio-script](../../../../docs/script/audio-script.md); hồ sơ [BUD](../../../../docs/script/profiles/bud.md)/[FS](../../../../docs/script/profiles/fs.md), [Long chuẩn](../../../../docs/script/profiles/long-standard.md) và khuôn của tập. Lời kể có tiến triển/cảm xúc, không kéo dài cho đủ giờ; các mẹo show/callback/tương phản là gợi ý nghề.

## NHIỆM VỤ
Long `<id>` · kênh `<...>` · khuôn `<...>` · engine `<...>` · người nghe `<...>`.
Lời hứa một câu `<...>` · câu trả dự kiến `<...>` · motif nếu cần `<...>`.
Giọng/ruleset/tempo/pause `<...>` · đích `<phút>` · ngân sách theo [bảng giọng](../../../../docs/script/voice-rates.md), ghi rõ ước hay đo.
Plan duyệt `<path>` · nghiên cứu `<path>` · beat sheet `<path>` · ngày hiệu lực `<ngày có thật>`.
Dữ kiện quan trọng `<3–5 ý>` · điểm chưa chắc `<...>` · phạm vi phỏng dựng theo hồ sơ `<...>`.

## VĂN XUÔI VÀ ĐỌC THỬ (078)
Viết văn xuôi tự do, trước hết CH00–01: `prose.md`, chương `## …`. Chạy `.venv/bin/python tools/prose_to_script.py prose.md script.txt` rồi dựng plan bằng `tools/long_plan_build.py --script`. Lead đọc thử `.venv/bin/python tools/tts_sample.py <plan.json> --only <id> --chapters 0 1` trước khi viết tiếp. Đọc nguyên câu, không tách vế; không giới hạn độ dài câu, máy không cảnh báo hay chặn (PO 17/11). Không có quota câu ngắn trong finding; nhịp 12–18 tiếng/câu ngắn chỉ gợi ý. Không đổi luật nội dung/nguồn/cold open của hồ sơ.

## 120 GIÂY ĐẦU: CÂU TRỌN, NHỊP HÌNH RIÊNG
PO17/11: ảnh/clip động≤8s, tĩnh≤4s, chữ nền trống≤1,5s; mục tiêu3–8s/ảnh, đổi ở ý mới. Bỏ ép mười tiếng/ba giây mỗi câu; viết theo nhịp ý, không tách cụm từ/năm thành mảnh cụt. Hình theo gợi ý ý/cảnh trong notes, workflow hình hiện tại quyết cách gắn; không bắt một ảnh mới vì một câu mới trong luật audio.
Giữ kiểm hình `pace_gate_issues(row,segs)`/`opening_gate(row,segs)` ở phiên sản xuất đúng segments, không chạy renderer để kiểm lời. Ngưỡng/loại visual mở theo long-video, không đổi code cổng. Bridge hiện chỉ pan theo `line` đầu/cuối câu, chưa đổi ảnh theo mốc từ; câu 40 tiếng/13s vẫn vướng cổng 4s/8s, cần Lead quyết phương án hình, không cắt vế lời.

## BÀN GIAO VÀ TỰ SỬA
`prose_<id>.md` + `nhap_<id>.txt` do adapter sinh: một câu/dòng, heading **đậm trọn**; kèm MP3 mẫu CH00–01 trong `output/cl_staging/long/tts_test/<id>/` để Lead nghe. `source_notes_<id>.md`: nguồn của claim/quote/số, diễn giải/phỏng dựng/nhãn theo hồ sơ, ngân sách/giọng/clock và điểm chưa chắc.
Chạy `.venv/bin/python long_script_lint.py nhap_<id>.txt --strict`; chép kết quả thật, CB sửa hoặc ghi lý do. Làm [vòng viết→tự chấm→sửa và phiếu8 mục](../../../../docs/script/audio-script.md#7-viết--tự-chấm--sửa). Ghi dòng trước→sau và vì sao; không coi phiếu là cổng hay tự gọi kiểm độc lập. Routing người viết/reviewer giữ theo Lead.
