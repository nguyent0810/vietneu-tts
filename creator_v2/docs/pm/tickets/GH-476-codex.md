# GH-476 — Adapter văn xuôi → lời TTS V2, nới trần câu, đọc thử chương

Bạn đang chạy TRONG worktree riêng `D:\Tools\Youtube Creator v2\wt-476` (nhánh `lead/476-prose-adapter`). Đường dẫn tính từ `creator_v2/`. Không đụng checkout `vietneu-main`. Đọc issue #476 (bối cảnh: chủ kênh chọn đọc NGUYÊN CÂU, không tách vế).

## 1. `scripts/prose_to_script.py` (mới)
`python scripts/prose_to_script.py <in.md> <out.md>`
- Vào: văn xuôi Markdown của người viết: header tự do, các chương `## CHNN · Tên chương`, đoạn văn thường. Người viết có thể đánh dấu cảnh phỏng dựng bằng `[PD]…[/PD]` quanh một hay nhiều câu, lời trích thật bằng dòng bắt đầu `»` (+ `[TRÍCH DỊCH]` cuối).
- Ra: định dạng `script.md` V2 mà `motion/long/script_lines.py parse` đọc được (xem mẫu `data/long/cl-sarin-tokyo-1995/script.md`): mỗi CÂU một dòng, giữ NGUYÊN chữ (không sửa, không thêm, không bớt chữ nào trong câu); tách câu CHỈ ở dấu kết câu `.` `!` `?` `…` (kể cả khi theo sau là ngoặc kép đóng); KHÔNG tách ở dấu phẩy/chấm phẩy/hai chấm/gạch ngang. Không tách ở số thập phân, viết tắt thường gặp ("TP.", "St.", "M."), dấu chấm trong tên. Câu trong `[PD]…[/PD]` → thêm ` {pd}` cuối dòng. Giữ header, `---`, phần cuối (ghi chú, bảng phiên âm) nguyên văn.
- Sau khi ghi: chạy `script_lines.parse` + `gate` trên kết quả và in lỗi/cảnh báo (không tự sửa chữ). In thống kê: số câu, tiếng mỗi chương, câu dài nhất.
- Test: tách câu đúng (gồm `…`, `?`, `!`, ngoặc kép, số "1.800", viết tắt), không đổi chữ (ghép lại các dòng == văn bản gốc bỏ khoảng trắng thừa), `[PD]` → `{pd}`.

## 2. Nới trần độ dài câu Long V2
`motion/long/craft.py` (hiện chặn > 35 tiếng, khoảng dòng 33): đổi thành cảnh báo > 45 tiếng, chặn > 70 tiếng (chủ kênh nghe thử: câu ~45 tiếng đọc nguyên câu vẫn tốt). Cập nhật test liên quan.

## 3. `scripts/tts_sample.py` (mới)
`python scripts/tts_sample.py <topic> <script.md> CH00 CH01 [--voice "Anh Khôi"]`
- Đọc các chương chỉ định bằng engine như `motion/long/build_long.py` (`factory.speak._load_engine`, `infer(text, voice=…)`), mỗi dòng một lần infer (đọc nguyên câu), nghỉ giữa câu theo dấu cuối câu (`.` 0,55 s, `?` 0,6 s, `!` 0,5 s, `…` 0,7 s, `‖` thêm 0,6 s), áp `voice_fx` của kênh như build_long (giọng mặc định theo kênh của spec), loudnorm -16 LUFS, xuất `output/long/<topic>/tts_test/<CHNN>.mp3`.
- Không ghi cache TTS sản xuất, không đụng output chương. Test nhỏ bằng engine giả (mock infer).

## Test và báo cáo
`python -m pytest -q tests` (dòng cuối). Báo cáo `docs/pm/tickets/GH-476-codex.report.md` (UTF-8, ghi bằng Python). File được ghi: hai script mới, `motion/long/craft.py`, test mới/sửa trong `tests/`, báo cáo. Không commit, không render, không gọi mạng. (TTS thật không cần chạy trong ticket — Lead chạy.)
