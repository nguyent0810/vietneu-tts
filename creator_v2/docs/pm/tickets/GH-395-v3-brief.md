# GH-395 viết lại lời Long CL `cl-dich-nhan-kiet` theo cách mới (§14) — người kể: Sonnet

Chủ kênh 15/11/2026 (#430): bản đang có "rất dở", "tôi không muốn nguồn là trục kể". Viết lại TOÀN BỘ lời đọc.

Đọc trước: `docs/pm/storytelling-guide.md` **§14** (đè lên mọi luật khác), "Tiêu đề và mở đầu kiểu survival", "Cửa sổ sốc"; `data/long/cl-dich-nhan-kiet/factcheck.md` (nguồn sự thật); bản đang có `script.md` chỉ để tham khảo dữ kiện — KHÔNG giữ cấu trúc, trục ("hai cuốn sổ đặt cạnh nhau: thám tử trong phim / người trong hồ sơ") hay câu chữ của nó. Mẫu giọng tốt: `docs/pm/bakeoff-430/sonnet.md` và `agy.md` (nhánh analysis/430-luugu, có thể không có trong worktree — không bắt buộc).

Yêu cầu:
- Trục: Địch Nhân Kiệt — vị quan sống sót dưới chế độ mật vụ Võ Chu bằng lời nhận tội giả, mảnh lụa trong áo bông, và cái giá của việc cứu người giữa thời khủng bố. Mỗi chương là một chặng của nhân vật: tình thế → lựa chọn → hệ quả → câu hỏi kéo sang chương sau. Đối chiếu nguồn chỉ 1–2 lần làm twist.
- Phỏng dựng cảnh (không gian, thời tiết, đồ vật, người vô danh) và giả thuyết hợp lý được phép: báo bằng lời ("hãy hình dung", "có lẽ"), đánh `{pd}` cuối câu. Không bịa bằng chứng, lời trích, con số, phán quyết. Dữ kiện phải khớp factcheck.md.
- Rào nguồn ≤ ~8% số câu; nguồn sẽ hiện trên hình. Không mở câu bằng "theo…" liên tục.
- Cold open 40 s: câu sốc/bi kịch/nghịch lý trong 3 câu đầu, câu hỏi trước câu 5, không chào/lộ trình trước 30 s. Kết mỗi chương bằng câu hỏi/hệ quả.
- Giọng phim tài liệu cho tai (TTS): câu ngắn–vừa xen kẽ, ≤ 32 âm tiết, có "bạn", hình ảnh cụ thể. 5.600–6.800 âm tiết, 13–14 chương CH00…, định dạng như script.md hiện tại (mỗi dòng một câu, ‖, `»` lời trích, `[TRÍCH DỊCH]` chỉ với câu có nguyên văn + URL trong factcheck, `{beat: …}`).
- Đầu file: 3 phương án tiêu đề ≤ 60 ký tự theo mẫu survival (bi kịch/nghịch lý), không nêu nguồn trong tiêu đề.
- Cuối file: giữ "Ghi chú kiểm chứng" (cập nhật theo bản mới) và bảng phiên âm nếu có.

Kiểm (Python, trên nội dung mới): `motion/long/script_lines.py` parse + gate == []; `motion/long/craft.py` audio_problems == []; đếm tỉ lệ câu có "theo|ghi|chép|nguồn|bách khoa|wikipedia|trang tiếng|sử cảo|tài liệu|bản ghi" ≤ 8%.

Đầu ra: ghi `data/long/cl-dich-nhan-kiet/script.v3.md` (KHÔNG ghi đè script.md) và báo cáo `docs/pm/tickets/GH-395-v3-report.md` (âm tiết, % rào, số cảnh {pd}, tiêu đề, kết quả kiểm). Ghi bằng Python `open(..., 'w', encoding='utf-8')`, không PowerShell. Không sửa file khác, không commit, không gọi mạng, không render/TTS.
