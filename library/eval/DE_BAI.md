# Đề thử điều phối thư viện (epic #37), giống hệt cho mọi agent

Bạn là THỢ cho kênh YouTube BUD (Phật giáo, short dọc tiếng Việt). Lead là Claude, sẽ chấm bài.
- Thư mục làm việc: repo này (nhánh feat/library-inventory).
- Python: dùng "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/.venv/bin/python".
- Checkout chính (CHỈ ĐỌC): "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS".

ĐỌC TRƯỚC: `library/README.md` và `docs/adr/0018-thu-vien-tri-thuc-chung.md`. Mục 7 của ADR: chỉ áp thư viện vào khuôn ngang/thua và ô thử nghiệm; không đụng dạng đang thắng và chuỗi được bảo vệ.

VIỆC:
1. **Chọn nơi áp và kỹ thuật.**
   - Chạy `<python> library/tools/lib.py pick --channel bud --usage-root "<checkout chính>"`.
   - Chọn MỘT nơi được áp: khuôn ngang/thua hoặc ô thử nghiệm. KHÔNG chọn chuỗi bảo vệ Chú Đại Bi.
   - Chọn MỘT kỹ thuật: từ gợi ý của `pick`, hoặc dùng `lib.py rank --channel bud` / `lib.py find`.
   - Đọc thẻ của kỹ thuật đó trong `library/cards/`, nêu lý do chọn.
2. **Đề xuất MỘT short thử nghiệm 27–32 giây cho nơi đó.**
   - Đề tài, kèm kiểm trùng: `<python> hf_novelty.py check bud "<tiêu đề>"` (dán kết quả).
   - Kịch bản 6 câu theo công thức BUD:
     - câu 1 là câu hỏi;
     - câu 2 là chi tiết bất ngờ;
     - câu cuối là câu hỏi mở.
   - Mọi lời Phật hoặc lời kinh phải đối chiếu bằng `<python> hf_sutta.py <uid> "<cụm>"`, dán đoạn nguyên văn tiếng Anh kèm uid. Không bịa.
   - Spec dựng:
     - id thẻ kỹ thuật dùng;
     - dẫn `path:line` thật của code sẽ dùng hoặc mở rộng (lấy bằng `grep -n`);
     - cách dựng tất định, seek-safe;
     - ước công: thấp / vừa / cao.
   - Một khối JSON plan nháp kiểu plan BUD: `{id, title, script[], source, insight, tags_vi, lane, test_cell, technique}`.
3. **Tự kiểm.** Liệt kê các ràng buộc đã tuân và chỗ chưa chắc:
   - ADR 0018 mục 7;
   - luật BUD: không máu hay vũ khí, không người phương Tây, không tôn giáo khác, lời Phật có nguồn;
   - không mùi AI.

ĐẦU RA: chỉ ghi vào thư mục của bạn `library/eval/<tên_agent>/`, gồm `de_xuat.md` và `plan.json`.

CẤM: render, đăng, commit/push, cài gói, sửa bất kỳ file nào ngoài thư mục của bạn, đọc .env / .youtube_channels / token.
