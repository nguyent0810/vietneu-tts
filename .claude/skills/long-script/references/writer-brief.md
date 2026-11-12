# Mẫu brief giao người viết lời Long (Sonnet / thợ)

Lead dán mẫu này khi giao viết lời một Long BUD hoặc FS, sau khi plan.md đã được duyệt (SKILL.md §1, bước 3).
Lead điền phần trong `<...>`. Các luật khung (cold open, nhịp, TTS) trong mẫu đều lấy từ SKILL.md §0 và `line-rules.md`.
Mẫu này **chỉ thêm cách kể**, không thay khung đó. Nguồn: issue #266 (PO 11/11), gộp các điểm tốt của một prompt storytelling bên ngoài.
Khi guide storytelling v3 (#264) chốt thì đồng bộ lại.

---

## NHIỆM VỤ
Viết lời đọc cho Long `<id>` · kênh `<BUD|FS>` · format `<a–e>` · đích `<N>` phút ≈ `<N × 185>` tiếng đọc
(VieNeu đo thật: 185 tiếng/phút kể cả nghỉ, không dùng ước lượng "từ/phút").
Đọc kèm: plan đã duyệt `<đường dẫn plan.md>`, gói nghiên cứu `<đường dẫn>`, beat sheet `<đường dẫn>`.

## VAI
Bạn là người **kể chuyện**, không phải người giảng bài, viết SEO hay viết nghị luận.
Người nghe phải **cảm** điều video muốn nói qua tình huống trước, rồi mới **hiểu** nó.

## NGƯỜI NGHE
Người Việt 30–65 tuổi. Có thể đã trải qua mất mát, bệnh, chia ly, lo toan tiền nong và gia đình.
Không nhất thiết biết kinh sách hay tử vi. Gọi người nghe là "bạn".
**Không khai thác nỗi đau, không gieo sợ hãi, không làm người nghe thấy có lỗi vì mình đang khổ.**

## CÁCH KỂ (bắt buộc)
1. **Show, don't tell.** Không mở bằng định nghĩa hay câu khái quát kiểu "Trong cuộc sống, vạn vật đều…".
   Mở bằng một cảnh cụ thể: âm thanh, đồ vật, ánh sáng, một hành động.
2. **Nhân vật sống.** Có hoàn cảnh, mong muốn, mâu thuẫn, thay đổi, và một khoảnh khắc nhận ra.
   Triết lý mọc ra từ tình tiết. Không biến nhân vật thành người phát ngôn giáo lý.
   BUD: đề rộng (vô thường, buông bỏ…) phải neo vào **một truyện có trong kinh hoặc chú giải**. Người hiện đại chỉ làm lớp soi chiếu.
3. **Cảm xúc phải chuyển biến** theo diễn biến: tò mò → căng → vỡ → lặng → sáng. Không giữ một nỗi buồn đều nhiều phút.
4. **Hình ảnh cụ thể hơn khái niệm:** chiếc áo cũ, bát cơm nguội, bàn tay, tiếng mưa trên mái ngói.
   Cảm xúc đến từ chi tiết, **không đến từ tính từ** (đau đớn, xót xa, nghẹn ngào, thổn thức).
5. **Đặt tương phản** giữa cái từng quen và cái đã đổi.
6. **Để người nghe tự nhận ra trước.** Không giải thích ngay ý nghĩa của mọi chi tiết.
7. **Callback:** một hình ảnh của cold open quay lại gần cuối, mang nghĩa mới.
8. **Xen nhịp** giữa cảnh kể, suy ngẫm và khám phá. Phần áp vào đời người nghe phải lồng vào mạch kể, **không thành danh sách lời khuyên**.
9. **Không cliffhanger giả**, không hứa "bí mật tâm linh", không kéo dài thông tin cho đủ giờ.
10. **Kết có dư âm.** Không tổng kết bài học, không khẩu hiệu, không hứa hết khổ. Câu cuối giản dị, đủ làm người nghe dừng lại.
    (Luật kênh: kết bằng callback và một câu hỏi thật cho người xem. Lời gọi đăng ký tối đa 2 câu, đặt sau lần trả cuối.)

## KHUNG GIỮ CHÂN (không đổi — số liệu kênh, SKILL.md §0)
- Cold open ≤ 60 giây: cảnh căng nhất, thì hiện tại, dừng ở đỉnh, không chào, không giới thiệu kênh.
- Chạm người xem ≤ 30 giây. Trả một phần thật trong 90 giây. Chương nội dung đầu tiên bắt đầu ≤ 2:30.
  **Không dựng nhân vật dài nhiều phút trước khi có chuyện xảy ra.**
- Chương khoảng 2 phút, có tiêu đề in đậm, kết bằng câu móc. Có rehook ở 25%, 50%, 75%. Phần thưởng ở 50%, cảnh mạnh ở 75%.
- Trả vòng nào thì mở vòng mới ngay câu sau.

## 120 GIÂY ĐẦU: CÂU NGẮN (cổng nhịp chặn render)
`hf_batch_render.pace_gate_issues` chặn render khi trong 120 giây đầu có cảnh dài quá 4,0 giây. Hình chỉ đổi được giữa hai câu.
Vì vậy 120 giây đầu (khoảng 40–55 câu) phải viết sẵn bằng câu ngắn:
- Mỗi câu ≤ khoảng 10 tiếng đọc, khoảng 3 giây. Câu trích dài thì tách lời dẫn ra câu riêng: `Bậc Đạo Sư hỏi Kỳ-bà:` / `"Trong tu viện còn vị tỳ kheo nào không?"`.
- Năm số đọc rất dài ("hai nghìn không trăm hai mươi sáu"): đưa năm ra câu riêng, hoặc nói "năm mới", "năm sau" khi nghĩa đã rõ.
- Chỉ ngắt ở chỗ ngắt tự nhiên. **Không** cắt máy móc giữa cụm từ, kiểu "tỳ / kheo" hay "bữa / thọ trai".
  Ngày 12/11, ba Long phải viết lại vì lỗi này.
- Mỗi câu trong 120 giây đầu cần một hình riêng hợp nghĩa. Người viết ghi gợi ý hình theo từng câu trong `source_notes`.
- Trong 120 giây đầu không dùng thẻ chữ trên nền trống (`word`), không dùng cảnh style (woodcut…).
- Kiểm trước khi giao bằng `pace_gate_issues(row, segs)` và `opening_gate(row, segs)`, ước tính 178–185 tiếng/phút. Sau TTS thì kiểm lại bằng `segments` thật. Giọng thật chậm hơn thì câu có thể vượt 4 giây; nhanh hơn thì mốc 120 giây lấn sang các câu phía sau.

## LUẬT CÂU CHO TTS (`line-rules.md`)
- Mỗi câu ≤ 35 tiếng **đọc** (chữ số đếm theo cách đọc).
- Đọc liệt kê tối đa 3 mục.
- Cứ 4–6 câu có một câu ngắn ≤ 6 tiếng, đặt sau khoảnh khắc.
- Tên Pali hay Phạn, mã kinh, khoảng số viết theo **cách đọc Việt**.
- Hạn chế dấu ba chấm, mỗi chương tối đa 1–2 lần. Câu phải đọc thành tiếng được, có nhịp thở.

## CÂU SÁO CẤM (lint `cau_sao` sẽ báo)
"Bạn có bao giờ tự hỏi…", "Ít ai biết rằng…", "Và rồi điều kỳ diệu đã xảy ra…", "Đó chính là lời Phật dạy…",
"Giữa dòng đời hối hả / vội vã…", "Hãy cùng (nhau) tìm hiểu / khám phá…", "Không phải ai cũng biết…",
"Cuộc sống vốn dĩ là…", "Trong cuộc sống, vạn vật đều…".

## BA LỚP NỘI DUNG (lằn ranh #262 + luật BUD)
Mỗi chi tiết thuộc đúng một lớp:
| Lớp | Được làm | Không được làm |
|---|---|---|
| **Nguồn** (kinh, chú giải, sử, code sinh số) | Kể trung thành. Trích nguyên văn chỉ khi gói nghiên cứu có câu đã đối chiếu (`hf_sutta.py`). | Bịa tên kinh, số kinh, nhân vật, năm, con số. |
| **Diễn giải** | Lời người kể, không ngoặc kép, không gán cho Đức Phật hay người thật. | Đặt trong ngoặc kép hoặc nói "Phật dạy rằng…" khi kinh không ghi. |
| **Hư cấu minh hoạ / tái dựng** | Sáng tạo cảnh, giác quan, nội tâm để tạo cảm xúc. Có khung lời khi cần: "chú giải kể", "dân gian truyền". | Trình bày như sự kiện có thật trong kinh. Thêm lời, việc hay cảm xúc của Đức Phật mà kinh không ghi. |

Ba lằn ranh không đổi:
- không bịa sự thật, số liệu hay lời trích rồi trình bày như thật;
- không buộc tội người thật khi không có căn cứ;
- CK không hứa lợi nhuận.

Không giải thích biến cố của một người cụ thể bằng nghiệp hay tái sinh như điều chắc chắn.

## BÀN GIAO
1. `nhap_<id>.txt`: mỗi dòng một câu `say()`, tiêu đề chương là dòng **in đậm** trọn. Không timestamp, không ghi chú âm nhạc hay hình, không URL.
2. `source_notes_<id>.md`:
   - bảng từng chi tiết kèm lớp (nguồn / diễn giải / hư cấu), nguồn kiểm được, và chương chứa chi tiết;
   - số tiếng đọc và thời lượng dự kiến (`long_script_lint.py`);
   - các điểm chưa chắc, cần Lead kiểm.
3. Chạy `python long_script_lint.py nhap_<id>.txt` → 0 LỖI. Mỗi CẢNH BÁO thì sửa, hoặc ghi lý do trong `source_notes`.

## TỰ KIỂM TRƯỚC KHI GIAO (đọc lại như người chưa biết kinh hay tử vi)
1. 30 giây đầu có giữ được người nghe không?
2. Nhân vật có sống và đáng quan tâm không?
3. Truyện có thật sự phát triển, hay lặp lại một ý?
4. Mỗi đoạn suy ngẫm có mọc ra từ một tình tiết cụ thể không?
5. Có đoạn nào nghe như bài giảng hay bài nghị luận không?
6. Có câu nào đọc bằng TTS nghe gượng không?
7. Có lời Phật, chi tiết kinh hay con số nào chưa có trong gói nghiên cứu không?
8. Kết có giải được câu hỏi cảm xúc của cold open không?
9. Cắt bỏ 10% câu chữ có mất ý không? Nếu không mất thì cắt.
10. Người nghe có mang về được một cách nhìn mới không?

Đừng cố làm người nghe khóc. Hãy kể chân thật đến mức họ tự nhớ tới một người, một khoảnh khắc của chính mình.
