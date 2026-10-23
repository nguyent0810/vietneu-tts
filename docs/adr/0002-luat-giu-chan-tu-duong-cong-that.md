# Luật viết kịch bản Long lấy từ đường giữ chân thật của kênh, mã hoá thành lint và một điểm duyệt kịch bản

Trạng thái: đã chấp nhận (14–21/10/2026).

Trước đây kịch bản Long theo một checklist chữ chung (mượn từ kênh khác), và checklist này hay bị bỏ qua. Ngày 14/10 ta ghép `audienceWatchRatio` của 6 Long (B3, B5, F1, F3, F4, F6) với câu đang đọc ở từng giây. Những chỗ rơi dốc nhất trùng với các kiểu câu lặp lại được:

- câu nói về chính video ("Video này sẽ…"): B5 mất 25 điểm ở giây 18–37;
- chương định nghĩa đặt trước phần trả lời: F6 mất 52 điểm ở giây 21–42, đúng lúc vào "lục thập hoa giáp";
- câu dồn 5 năm sinh liền nhau, dài 40–44 tiếng đọc: F6 rơi 7 điểm;
- câu kết "Tóm lại", hoặc đọc to bảng tổng hợp: F4 mất 31% trong 50 giây.

Ta biến các chỗ rơi này thành 10 luật đầu skill `long-script`, rồi mã hoá vào `long_script_lint.py`. Lint đếm **tiếng đọc**, không đếm token ("1983" là 7 tiếng). Chỉ một lỗi chặn cứng: câu dài hơn 35 tiếng đọc. Mọi cảnh báo khác phải sửa, hoặc ghi lý do trong docstring của file dựng.

Long còn có một **điểm duyệt**: chủ kênh duyệt `plan.md` (đề, cung A→B, cảnh mở, bảng vòng mở–đóng, danh sách chương) trước khi viết dòng lời đầu tiên.

## Các phương án đã cân nhắc

- **Giữ checklist chữ.** Bị bỏ qua, và không đo được mức tuân thủ.
- **Chặn cứng mọi luật.** Quá chặt: mẫu nhỏ (ở B5, một người xem bằng khoảng 1 điểm %), nên nhiều luật mới chỉ là giả thuyết.
- **Không duyệt plan, chỉ duyệt video xong.** Mỗi vòng sửa tốn thêm một lần render (khoảng 1,7 lần thời lượng video).

## Hệ quả

- Chỉ tin một lần rơi khi mất ≥ 4 điểm, hoặc khi nó lặp lại ở nhiều video.
- Khi các tài liệu lệch nhau, thứ tự ưu tiên là: số liệu của kênh, rồi quyết định 21/10 (khung 12–14 chương khoảng 2 phút), rồi quyết định 22/10 (ADR 0001).
- Runner của bước render vẫn đếm token nên bỏ sót câu nhiều số. Lint là chỗ bắt câu dài.
- Giới hạn đã biết: lint ước 185 tiếng/phút, nhưng giọng thật có thể chậm hơn (giọng Bình đọc khoảng 178). Khi đã có `out/<id>.json`, lint dùng số giây thật.

## Bằng chứng

`.claude/skills/long-script/references/evidence.md`, `sources.md`, `long_script_lint.py`, `tests/test_long_script_lint.py`, ticket 42–44 và 60 trong `output/cl_staging/grok/queue/`.
