# Khuôn prompt gửi Gemini viết lời Long (FS / BUD / VSD)

Dùng với `creator_v2/scripts/gemini_chat.py ask <prompt.md> --out prose.md` (mặc định Neon · thinking High).
Lead điền các chỗ `<...>`, lưu thành `prompt.md`. Lượt đầu chỉ CH00–CH01; nghe thử xong mới gửi lượt hai bằng `--chat <url>`.

Bài học lượt so 19/11 (L01 Kim Lâu 1991, 7 tổ hợp model):
- Mọi model chép nguyên chữ ghi chú của brief vào lời ("nghịch lý này là lộ trình"). Vì vậy brief chia hai khối: **CHỈ DẪN** (không bao giờ đọc thành lời) và **CHI TIẾT ĐƯỢC DÙNG** (được kể lại bằng lời của người viết).
- Câu bắt buộc phải có (câu chạm người xem, câu khung dân gian) ghi ở mục riêng, nói rõ "được diễn đạt lại".
- Chỉ cho ra đúng số chương được hỏi; mỗi chương chỉ viết ý của dòng dàn chương của nó.
- Lượt L02 (20/11): khuôn cũ mượn thẻ [PD] và dấu nghỉ ‖ của luồng CL (creator_v2). Luồng BUD/FS (`hf_voice`, `tools/prose_to_script.py`) không hiểu hai ký hiệu ấy: giọng đọc đọc ra chữ, và `[/PD] [PD]` làm nhiều câu dính thành một dòng. Tiêu đề "CH00 · …" cũng bị đọc. Định dạng dưới đây theo đúng L01: phần mở không tiêu đề, chương là câu hỏi `## …`.

---

```
Bạn là nhà văn viết lời kể cho phim tài liệu YouTube dài của kênh <FS: Phong Thuỷ, giọng truyền thống, ấm áp | BUD: Phật giáo, giọng tĩnh lặng, chữa lành | VSD: Văn Sử Địa, giọng kể sử gần gũi>.
Lời được giọng AI đọc nguyên văn, nên viết cho tai nghe: dựng cảnh bằng chi tiết cụ thể (vật, âm thanh, cử chỉ) thay cho tính từ cảm xúc; ưu tiên câu ngầm (điều nhân vật chưa nói) hơn câu giải thích; mỗi câu chỉ đưa một con số; không sáo ngữ ("trớ trêu thay", "ngã ba đường"). Gọi người nghe là "bạn". Không bịa lời trích thật. Đoạn giọng mẫu chỉ để học giọng, không chép câu.

QUAN TRỌNG: khối CHỈ DẪN dưới đây là ghi chú cho bạn, KHÔNG được chép chữ nào của nó vào lời đọc (ví dụ không viết "nghịch lý này là lộ trình", "cung chuyển", "mô-típ"). Chỉ dùng ý.

Định dạng trả về (chỉ trả văn bản, không lời dẫn):
Đoạn văn xuôi của phần mở đầu, KHÔNG có tiêu đề…

## <Câu khán giả gõ tìm của CH01>

Đoạn văn xuôi…
- Tiêu đề chương chỉ là câu hỏi người xem gõ tìm, không ghi "CH01", không dấu "·": tiêu đề được đọc thành tiếng.
- Không thẻ, không ký hiệu ([PD], ‖, *, #, ngoặc vuông): giọng đọc đọc mọi ký tự.
- Không in đậm, in nghiêng, gạch đầu dòng hay ghi chú.

NHIỆM VỤ: chỉ viết <CH00 và CH01> (dài khoảng <1> và <2> phút đọc, ~185 tiếng/phút). Mỗi chương chỉ viết đúng ý dòng dàn chương của nó, kết bằng một câu móc sang chương sau (không răn dạy, không tóm tắt).

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
<đoạn 80–150 chữ đã duyệt, KHÁC đề tài>

=== DÀN CHƯƠNG ===
CH00 · <tên> · <phút>
CH01 · <tên> · <phút>
…
```

Lượt hai (cùng chat, `--chat <url>`):
```
Viết tiếp CH02 đến CH<nn> theo đúng dàn chương, cùng giọng và định dạng như CH00–CH01 đã viết. Không viết lại CH00–CH01.
<sửa đổi Lead muốn sau khi nghe thử, nếu có>
```

Sau khi nhận: Lead biên tập (câu ngầm, cắt tính từ dồn và sáo ngữ, nối hình ảnh lặp lại, soát từng con số với bảng dữ kiện), rồi `tools/prose_to_script.py` và lint như SKILL §1.
