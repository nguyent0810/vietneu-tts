# Cổng kịch bản Long: chặn ghi chú sản xuất và trích nguồn lọt vào lời đọc

**Sự cố 06/11 (kịch bản Hòa Thân, bản 1):** lời đọc chứa
- ghi chú sản xuất: "Plan đã cấm đưa vào lời.", "Không có dải lụa trên hình.", "Mô-típ một dòng bản kê…", "Cảnh ấy ta không dựng.";
- tự nói về cấu trúc: "Vòng thứ nhất đóng ở chương chín.", "Sợi chỉ này sẽ quay lại ở chương tám.";
- "Wikipedia" 26 lần, "bài tiếng Việt/Anh", "infobox", "cùng trang ấy".

`script_lines.gate` vẫn báo OK. Cần cổng bắt các lỗi này **trước TTS**.

**Áp dụng ngoại lệ AGENTS.md.** Được sửa:
- `motion/long/script_lines.py`, phần gate;
- test mới `tests/test_script_meta_leak.py`;
- báo cáo `docs/pm/tickets/GH-179-metaleak-report.md`.

Ghi file bằng Python, `encoding="utf-8"`. Trước khi kết thúc, chạy:
`python -c "import subprocess,sys;d=subprocess.run(['git','diff'],capture_output=True,text=True,encoding='utf-8').stdout;sys.exit('MẤT DẤU' if '???' in d or 'Kh?ng' in d else 0)"`

**Việc:** trong gate, chỉ xét **câu sẽ đọc** (dùng đúng hàm parse mà gate đang dùng; bỏ bảng nguồn, tiêu đề, ghi chú). Thêm:
1. `META_LEAK` (**chặn**): câu chứa thuật ngữ sản xuất. Danh sách khai báo thành hằng số dễ sửa, không phân biệt hoa thường, so theo từ:
   - kịch bản, plan, brief, lời đọc, trên hình, trên màn hình (trừ khi đi với "phim"), mô-típ, motif, infobox, prompt, render, agent, Lead, factcheck, TTS;
   - mẫu "chương + số đếm" kèm động từ cấu trúc: "(sẽ )?(quay lại|đóng|mở) ở chương …", "vòng thứ … đóng".
2. `SOURCE_DENSITY` (**cảnh báo**, không chặn): đếm "wikipedia", "bách khoa", "bài tiếng việt", "bài tiếng anh", "cùng trang". Quá 1 lần mỗi chương thì cảnh báo, nêu chương và số lần.
3. Không được bắt nhầm trên các Long đã đăng. Chạy gate trên mọi `data/long/*/script.md` đang có (golden, bao-thanh-thien, yakuza, mafia…) và ghi kết quả vào báo cáo. Kịch bản đã đăng nào bị `META_LEAK` thì xem lại từ khóa cho chặt hơn; ví dụ "trên màn hình" dùng trong một câu kể về phim là hợp lệ.
4. Test:
   - các câu mẫu của sự cố bị chặn;
   - câu hợp lệ không bị chặn, ví dụ "Trên màn hình, Vương Cương đóng một gã hề.", "Bộ phim kể…";
   - cảnh báo mật độ nguồn.

   Chạy `python -m pytest tests -q`.

**Không:** commit, sửa kịch bản.
