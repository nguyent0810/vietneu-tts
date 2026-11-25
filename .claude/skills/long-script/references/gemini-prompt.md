# Khuôn prompt gửi Gemini viết lời Long (FS / BUD / VSD)

Dùng với `creator_v2/scripts/gemini_chat.py ask <prompt.md> --out prose.md` (mặc định Neon · thinking High).
Lead điền các chỗ `<...>`, lưu thành `prompt.md`. Lượt đầu chỉ CH00–CH01; nghe thử xong mới gửi lượt hai bằng `--chat <url>`.

Bài học lượt so 19/11 (L01 Kim Lâu 1991, 7 tổ hợp model):
- Mọi model chép nguyên chữ ghi chú của brief vào lời ("nghịch lý này là lộ trình"). Vì vậy brief chia hai khối: **CHỈ DẪN** (không bao giờ đọc thành lời) và **CHI TIẾT ĐƯỢC DÙNG** (được kể lại bằng lời của người viết).
- Câu bắt buộc phải có (câu chạm người xem, câu khung dân gian) ghi ở mục riêng, nói rõ "được diễn đạt lại".
- Chỉ cho ra đúng số chương được hỏi; mỗi chương chỉ viết ý của dòng dàn chương của nó.
- #531/#534 (25/11, nghiên cứu prompt cho CL/MIM/CK): lời phải "kể cho tai" theo các mục trong khối KỂ CHO TAI dưới đây; giọng mẫu riêng từng kênh ở `creator_v2/docs/pm/giong-mau/FS.md`, `BUD.md` (hai đoạn giữa chương của Long giữ chân tốt nhất); khung từng chương do Gemini tự lên trong đầu trong cùng prompt (thử lượt tờ nhịp riêng 25/11: lỗi treo). FS Long tra cứu trả lời sớm (như CK); BUD truyện giữ lời đáp cho chương sở hữu nó (như CL).
- 25/11 PO: không ghi đích số chữ / số phút cho từng bài, chỉ ghi loại Long ngắn hay Long dài; Lead không cắt bản nháp cho vừa độ dài. Viết trọn bài trong MỘT prompt (lượt tờ nhịp riêng làm Gemini nghĩ quá lâu rồi lỗi, 25/11) — tự lên khung trong đầu, không in ra.
- 25/11: `gemini_chat.py` chỉ dán CHỮ của file prompt vào Gemini, không đính kèm file. Prompt không được nhắc tên file (`facts.json`, `brief.md`…) — Gemini không thấy chúng; mọi dữ kiện và chỉ dẫn phải dán thẳng vào các khối BẢNG DỮ KIỆN / CHỈ DẪN.
- Lượt L02 (20/11): khuôn cũ mượn thẻ [PD] và dấu nghỉ ‖ của luồng CL (creator_v2). Luồng BUD/FS (`hf_voice`, `tools/prose_to_script.py`) không hiểu hai ký hiệu ấy: giọng đọc đọc ra chữ, và `[/PD] [PD]` làm nhiều câu dính thành một dòng. Tiêu đề "CH00 · …" cũng bị đọc. Định dạng dưới đây theo đúng L01: phần mở không tiêu đề, chương là câu hỏi `## …`.

---

```
Bạn là nhà văn viết lời kể cho phim tài liệu YouTube dài của kênh <FS: Phong Thuỷ, giọng truyền thống, ấm áp | BUD: Phật giáo, giọng tĩnh lặng, chữa lành | VSD: Văn Sử Địa, giọng kể sử gần gũi>.
Lời được giọng AI đọc nguyên văn, nên viết cho tai nghe: dựng cảnh bằng chi tiết cụ thể (vật, âm thanh, cử chỉ) thay cho tính từ cảm xúc; ưu tiên câu ngầm (điều nhân vật chưa nói) hơn câu giải thích; mỗi câu chỉ đưa một con số; không sáo ngữ ("trớ trêu thay", "ngã ba đường"). Gọi người nghe là "bạn". Không bịa lời trích thật. Đoạn giọng mẫu chỉ để học giọng, không chép câu.

KỂ CHO TAI:
- Sau một câu trừu tượng hoặc dày từ Hán Việt (Thái Tuế, Hình, Phá, nạp âm, Tam Tai, Niết Bàn…), cho ngay một câu cảnh (nơi chốn, âm thanh, đồ vật, cơ thể) rồi mới sang ý mới. Không cấm từ Hán Việt.
- Nghe một lần là hiểu: chuyển nhân vật, thời điểm hay khái niệm thì gọi tên rõ, không để đại từ lửng; không viết "như bạn thấy trên màn hình".
- Có con số thì nói luôn nó nghĩa là gì với người nghe; ví dụ do bạn đặt ra phải nói rõ là ví dụ giả định.
- Giữa chương có thể có MỘT câu phản tư buộc vào cảnh vừa kể, rồi câu sau quay lại việc; không thành đoạn, không đặt cuối chương, không răn dạy.
- <FS: người nghe cần câu trả lời sơ bộ sớm (trong hai câu đầu mỗi chương), phần sau giải thích vì sao, có nơi tính khác ra sao, áp dụng thế nào | BUD: phần mở chỉ cho thấy ai đang gặp chuyện và mất gì; lời đáp để dành cho chương sở hữu nó>.
- Kết video bằng câu trả lời cho câu hỏi đã mở ở đầu, có thể quay lại hình ảnh mở đầu; không tóm tắt cả video, không kêu gọi đăng ký chung chung.
- Trước khi trả bài, tự rà từng đoạn như chỉ được nghe một lần: sửa câu phải nghe lại mới hiểu, cắt câu dẫn sáo rỗng, câu nhắc lại tiêu đề, câu kiểu "điều này cho thấy".

QUAN TRỌNG: khối CHỈ DẪN dưới đây là ghi chú cho bạn, KHÔNG được chép chữ nào của nó vào lời đọc (ví dụ không viết "nghịch lý này là lộ trình", "cung chuyển", "mô-típ"). Chỉ dùng ý.

Định dạng trả về (chỉ trả văn bản, không lời dẫn):
Đoạn văn xuôi của phần mở đầu, KHÔNG có tiêu đề…

## <Câu khán giả gõ tìm của CH01>

Đoạn văn xuôi…
- Tiêu đề chương chỉ là câu hỏi người xem gõ tìm, không ghi "CH01", không dấu "·": tiêu đề được đọc thành tiếng.
- Không thẻ, không ký hiệu ([PD], ‖, *, #, ngoặc vuông): giọng đọc đọc mọi ký tự.
- Không in đậm, in nghiêng, gạch đầu dòng hay ghi chú.

NHIỆM VỤ: viết <trọn bài, CH00 đến chương cuối, trong một lần trả lời> cho một <Long ngắn: một chủ đề hẹp, gọn | Long dài: viết đủ ý, không giới hạn số chữ>. Mỗi chương chỉ viết đúng ý dòng dàn chương của nó, kết bằng một câu móc sang chương sau (không răn dạy, không tóm tắt).

=== CHỈ DẪN (không đọc thành lời) ===
Người nghe: <ai, tuổi, đang lo gì>
Thông điệp cả video: <một câu>
Người nghe đi từ: <trạng thái A> → tới: <trạng thái B>
Cảnh mở: <cảnh căng nhất, thì hiện tại, dừng ở câu hỏi chưa trả lời>
Trả một phần trong 90 giây đầu: <ý>
Hình ảnh lặp lại (đầu, giữa, kết): <vật/cử chỉ>
Kết video: <cảnh gọi lại + câu hỏi thật cho người xem>
Khung lời: <FS: "theo cách tính dân gian", "có nơi…" chỗ nhiều cách tính; không số tiền, không hứa tài lộc; gọi con giáp bằng tên chi | BUD: lời Phật chỉ khi có kinh trong bảng dữ kiện>

=== CÂU BẮT BUỘC (được diễn đạt lại, giữ ý) ===
- Trong 30 giây đầu: <vd "nếu bạn sinh năm 1991, tức tuổi Tân Mùi, phép chia ấy là của bạn">
- <câu khung, vd "theo cách tính dân gian… kiến thức truyền thống để tham khảo">

=== NHÂN VẬT (phỏng dựng, không phải người thật) ===
<ai, quan hệ, mỗi người có mặt ở cảnh nào>

=== BẢNG DỮ KIỆN (chỉ dùng số và ý trong đây) ===
<số sinh bằng code, mỗi dòng một dữ kiện, kèm nhãn [dân gian]/[code]/[kinh …]>

=== GIỌNG MẪU ===
<dán nguyên hai đoạn trong creator_v2/docs/pm/giong-mau/FS.md hoặc BUD.md; học giọng, không chép câu, không chép cấu trúc mở, không chép đề tài>

=== DÀN CHƯƠNG ===
CH00 · <tên> · <phút>
CH01 · <tên> · <phút>
…
```

Lượt hai (chỉ khi lượt một bị cắt giữa chừng; cùng chat, `--chat <url>`):
```
Viết tiếp CH02 đến CH<nn> theo đúng dàn chương, cùng giọng và định dạng như CH00–CH01 đã viết. Không viết lại CH00–CH01.
<sửa đổi Lead muốn sau khi nghe thử, nếu có>
```

Sau khi nhận: Lead biên tập (câu ngầm, cắt tính từ dồn và sáo ngữ, nối hình ảnh lặp lại, soát từng con số với bảng dữ kiện), rồi `tools/prose_to_script.py` và lint như SKILL §1.
