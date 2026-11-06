# GH-21: cache render chương Long không phụ thuộc mốc thời gian và code không liên quan

Đọc issue #21 (`gh issue view 21 --repo nguyent0810/vietneu-tts`; nếu mạng sandbox chặn thì dùng tóm tắt dưới đây). Issue gốc nói về `hf_batch_render` (luồng BUD/FS). **Ticket này chỉ làm luồng Long của `creator_v2`.**

**Sự cố thật ngày 06/11 (Bao Thanh Thiên):**
- Chỉ sửa lời của 4 chương (ch07, ch08, ch09, ch11), nhưng render key của ch00–ch06, ch10, ch12, ch13 cũng đổi.
- Thay đổi đó đến sau một lần `git merge` code không đụng chương nào. Kết quả: render lại cả video, khoảng 90 phút.
- Vấn đề chung của issue: sửa một câu thì lệch thời gian mọi chương phía sau.

**Áp dụng ngoại lệ AGENTS.md cho ticket code.** Được sửa:
- `motion/long/build_long.py`, chỉ phần tính render key / cache chương và phần timing theo chương nếu cần;
- các module long liên quan mà bạn chỉ ra (ghi rõ trong báo cáo);
- test mới `tests/test_chapter_render_key_21.py`;
- báo cáo `docs/pm/tickets/GH-21-report.md`.

Ghi file bằng Python, `encoding="utf-8"`. Không đụng `hyperframes_short/` hay `hf_batch_render`.

**Việc:**
1. **Phân tích trước, ghi vào báo cáo.** Render key của một chương Long hiện tính từ những gì: spec chương, wav, timing, mốc tuyệt đối từ đầu video, hash engine hay toàn bộ code, look, nhạc nền…? Thành phần nào làm key của chương *không đổi nội dung* vẫn đổi:
   - (a) khi sửa lời ở chương khác;
   - (b) khi merge code không đụng engine hay template mà chương đó dùng.
2. **Sửa để key chỉ phụ thuộc đúng những gì quyết định hình và tiếng của chương đó:**
   - spec chương;
   - wav và timing của riêng chương, mốc 0 ở đầu chương;
   - ảnh và clip chương đó dùng (hash nội dung);
   - hash của đúng các file engine, CSS, JS và template mà chương dùng (không phải hash cả repo hay cả thư mục);
   - phiên bản renderer.

   Nếu `final` đang ghép các chương theo mốc tuyệt đối, phải giữ đúng thứ tự và độ dài khi ghép. Nhạc nền chạy liên tục qua nhiều chương thì nói rõ cách xử lý: nhạc nền nằm trong chương hay được ghép ở bước final.
3. **Không làm sai cache:** thay đổi thật trong chương (lời, ảnh, look, engine file chương dùng) vẫn phải đổi key.
4. **Test:**
   - sửa lời chương 7 thì key chương 3 và chương 10 giữ nguyên, key chương 7 đổi;
   - đổi một file code không liên quan (ví dụ một script trong `scripts/`) thì không key nào đổi;
   - đổi CSS engine mà chương dùng thì key đổi;
   - đổi ảnh của chương thì key đổi.
5. Chạy `python -m pytest tests -q`. Toàn bộ phải xanh.

**Không:** render thật, commit, upload. Nếu thấy cần thay đổi lớn ngoài phạm vi trên, dừng và ghi đề xuất vào báo cáo thay vì sửa.
