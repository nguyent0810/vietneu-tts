# YCV-ju9q · M1 W1 vòng 2: viết lại `mim-jobs-1985/script.md` cho người nghe

## Đánh giá vòng 1

Vòng 1 đúng dữ kiện, nhưng chưa thể gửi chủ kênh duyệt.

Bài đọc giống biên bản kiểm chứng, không phải một câu chuyện. Khoảng 40% số câu là lời bình về cách kể chuyện hoặc câu rào đón, để độn cho đủ âm tiết. Luật "không câu đệm" trong `docs/codex/long-rules.md` cấm việc này.

## Phải bỏ

1. **Ghi chú sản xuất bị đọc thành tiếng.** Ví dụ:
   - "Trên màn hình, mốc ấy là ngày 17 tháng 9 năm 1985." (CH00)
   - "Ở lời đọc này, mốc quan trọng là…" (CH02)
   - "Ở đây ta chỉ nói cuối tháng 5 vì nguồn có chênh lệch…" (CH03)

   Ngày ghi trên màn hình và lý do chọn mốc thuộc `factcheck.md`, không thuộc lời đọc.
2. **Câu bình về cách kể.** Ví dụ:
   - "Điều này cũng tránh cách kể rằng…"
   - "Đó không phải bằng chứng về động cơ…"
   - "Điểm xuất phát này quan trọng vì nó không biến Jobs thành nhân vật…"
   - "Sự chính xác này quan trọng vì…"
   - "Đó là lời nhìn lại được quy cho Sculley, không phải chìa khóa…"
   - "Hai phần của câu chuyện cùng đúng…"

   Nguyên tắc không suy diễn động cơ được giữ bằng cách **không viết câu suy diễn**. Không cần nói ra rằng mình không suy diễn.
3. **Câu lặp ý.** Ví dụ:
   - CH01 nói 6 lần "sản phẩm khác quyền điều hành";
   - CH06 giải thích 400 và 427 triệu 5 lần;
   - CH07 nói 3 lần "hai bước 1997".

   Mỗi ý chỉ nói **một lần**, rõ ràng.

## Phải có (story-first)

- **Mỗi chương là một cảnh có người, thời điểm và hành động**, kể bằng dữ kiện trong kho:
  - một tờ báo ra ngày 1/6/1985 với cái tít (#6);
  - câu Sculley nói ngày 25/7/1985 (#7) đặt ngay sau câu Apple hứa trao cho Jobs "vai trò rộng hơn";
  - năm người đi theo Jobs (#11);
  - lá đơn kiện chỉ vài ngày sau khi Jobs rời đi (#12);
  - tờ séc 10 triệu, một nửa trả Lucasfilm (#17);
  - năm 1993 NeXT cắt 230 trên 530 người (#16);
  - Apple lỗ 1,045 tỷ (#21), rồi thông cáo 16/9/1997 (#23).
- **Câu mở giữ như cũ:** sự kiện tháng 9/1985. Ngay sau đó là nghịch lý: 12 năm sau, Apple phải mua lại chính công ty của người đã rời đi.
- **Vòng lặp mở:**
  - cuối CH00 đặt câu hỏi trung tâm;
  - cuối mỗi chương để lại một câu hỏi nhỏ dẫn sang chương sau;
  - CH08 trả lời câu hỏi trung tâm trong **tối đa 3 câu**, không giảng bài học dài.
- **Trích dẫn để ở chỗ có sức nặng:**
  - "at 30 I was out" (#24) đặt ở CH03, đúng lúc Jobs rời đi;
  - lời Sculley nhìn lại (#25, #26) đặt ở CH07, đối với câu năm 1985 (#7).
  - Cả hai gắn [TRÍCH DỊCH] và quy dẫn như vòng 1.
- **Phần 400 và 427 triệu:** nói đúng **hai câu**:
  - câu 1: lúc công bố, Apple nói 400 triệu USD;
  - câu 2: báo cáo năm (10-K) ghi tổng giá mua 427 triệu, tính cả các khoản nợ Apple gánh thay.

## Độ dài

**2.000–2.500 âm tiết**, khoảng 10–12 phút.
- Ngắn hơn vòng 1 là đúng hướng. Không độn để đủ số.
- Chạy `codex_ticket` với `--min-syl 2000`.
- Giữ 9 chương nếu đủ chất. Được gộp còn 8 chương.

## Giữ nguyên từ vòng 1

- Phạm vi file, nguồn dữ kiện và các quyết định ở §"Quyết định" của `docs/pm/tickets/YCV-ju9q-M1-W1-codex.md`.
- Tách "bị tước quyền điều hành" và "tự nộp đơn từ chức".
- Mục HÌNH trong `factcheck.md`: cập nhật lại chỉ số câu sau khi viết lại, tối đa 6 ảnh AI.
- Cổng `script_lines.py` và `studio_lint.py --strict` đạt 0 lỗi.
- `long_gate` sẽ trượt vì chưa có cảnh. Không cần ghi lại 23 lỗi đó.

## Báo cáo

Ghi đè `docs/pm/tickets/YCV-ju9q-M1-W1-ket-qua.md`. Thêm mục **"Vòng 2"**, gồm:
- số âm tiết trước và sau;
- số câu đã bỏ;
- danh sách cảnh (người, thời điểm, hành động) của từng chương.
