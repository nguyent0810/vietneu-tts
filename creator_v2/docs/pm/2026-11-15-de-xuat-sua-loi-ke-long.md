# Đề xuất sửa cách viết lời Long MIM/CK/CL (issue #430)

Ngày 15/11/2026, gửi chủ kênh duyệt. Chủ kênh chê lời kể Long Lưu Gù "rất dở, không có storytelling gì hấp dẫn", và yêu cầu không rào nguồn quá chặt, để agent còn sáng tạo.

## 1. Kết luận ngắn

Không có model nào viết dở hẳn. Lời khô là do **chuỗi luật và vai trò** từ 11/11 dồn người viết vào việc báo cáo nguồn thay vì kể chuyện.

## 2. Bằng chứng

**Mật độ câu rào nguồn** trong lời đọc CL. Rào nguồn là các câu có "theo, ghi, chép, nguồn, bách khoa, Wikipedia, trang tiếng…, có thể, chưa rõ…".

| Long | Rào nguồn | Câu hỏi | Ghi chú |
|---|---:|---:|---|
| Kowloon | 3,6% | 1,3% | 6 Long chuẩn |
| Golden | 6,4% | 0,9% | 6 Long chuẩn |
| Shanghai | 10,1% | 2,6% | 6 Long chuẩn |
| Hòa Thân | 9,4% | 1,2% | |
| Mata Hari | 12,7% | 1,5% | |
| **Lưu Gù** | **16,7%** | 2,0% | bị chê |
| **Địch Nhân Kiệt** | **19,2%** | 5,4% | đăng 24/11 |
| **Hoàng Kim Vinh** | **26,9%** | 3,6% | đăng 19/11 |

**Bake-off CH00–CH02 Lưu Gù:** cùng factcheck, cùng luật mới của chủ kênh (được phỏng dựng có nhãn).

| Bản | Rào nguồn | Cảnh phỏng dựng | Nhận xét Lead |
|---|---:|---:|---|
| Bản đang lên kênh | 13,7% | 0 | Liệt kê dữ kiện, nhiều câu giảng nguồn |
| agy Gemini | 7,9% | 10 | Dựng cảnh tốt, câu hỏi giữ chân rõ. Có 1 câu suy đoán hơi mạnh ("người hiểu rõ Hòa Thân nhất") |
| Sonnet | 11,0% | 8 | Nhịp điện ảnh, câu ngắn cho tai, cold open tốt nhất |
| Codex | — | — | **Mất dấu tiếng Việt toàn bộ ('?')**, không dùng được |

File để so: `docs/pm/bakeoff-430/agy.md` và `sonnet.md` (worktree `wt-430`).

## 3. Nguyên nhân gốc

1. **Trục kể đặt nguồn làm nhân vật chính.** Các trục "bốn cách người ta kể" (Hoàng Kim Vinh), "phim kể / hồ sơ ghi" (Lưu Gù), "ba bản chân dung" (Vidocq) khiến lời đọc phải liên tục nói "trang tiếng Anh ghi…, sách 1930 ghi…". Hoàng Kim Vinh 27% chính là vì trục này.
2. **Một agent vừa nghiên cứu vừa viết.** Brief của Lead dồn việc kiểm nguồn (mở URL, đối chiếu, nêu cả hai phía) vào cùng lượt viết lời. Người viết ở chế độ "kiểm toán" thì viết ra kiểu báo cáo.
3. **Luật cộng dồn.**
   - Brief viết: "mọi số nói rõ của ai".
   - Brief review: "mọi lời rào phải giữ".
   - Cổng `factcheck_lint`: số và ngày phải có trong factcheck.
   - Cảnh báo `RAO_NGUON`.

   §13 luật 2 vốn nói "nói giới hạn nguồn **một lần**", nhưng các lớp trên kéo ngược lại.
4. **Reviewer cắt chất kể.** Bước review câu chuyện giao Codex (vì agy hết hạn mức). Báo cáo review Lưu Gù ghi rõ "bỏ các suy đoán về động cơ, hành động". Codex là model làm code, rất bảo thủ khi viết văn. Lần này nó còn làm mất dấu tiếng Việt khi tự ghi file.
5. **Thiếu một cổng đo chất kể.** Có cổng cho số, cảnh, nhạc, nhưng không có gì đo "câu kể và cảnh / câu giảng nguồn". Cảnh báo `SOURCE_DENSITY` có mà không chặn.

## 4. Đề xuất (chờ chủ kênh duyệt)

**A. Tách 3 vai, mỗi vai một việc**
1. *Người nghiên cứu* làm `factcheck.md` + "hồ sơ truyện" (dòng thời gian, nhân vật, xung đột, chi tiết đắt giá, mâu thuẫn nguồn). Không viết lời.
2. *Người kể* viết lời từ hồ sơ, được tự do:
   - dựng cảnh có nhãn PHỎNG DỰNG;
   - nêu giả thuyết hợp lý;
   - chọn bản kể đáng tin nhất khi các nguồn lệch nhau, ghi lý do chọn vào factcheck, không kể cả hai bản trong lời đọc trừ khi chỗ lệch chính là điểm hấp dẫn.
3. *Người soát* chỉ chặn 3 thứ:
   - sai sự thật / số không có trong factcheck;
   - bịa lời hoặc cảm xúc người còn sống;
   - nội dung nguy hiểm.

   Người soát **không được cắt cảnh, giả thuyết hay nhịp kể**.

**B. Ngân sách rào nguồn**
- Lời đọc tối đa khoảng **8%** câu có rào nguồn (mức của Golden, Shanghai).
- Ghi nguồn chuyển sang **phụ đề nguồn trên hình**: dòng nhỏ "Nguồn: Thanh sử cảo" ở cảnh, đã có sẵn `srcnote` và `sub`. Lời đọc chỉ rào khi người nghe cần biết đó là tranh cãi.
- `script_lines`: đổi `RAO_NGUON`/`SOURCE_DENSITY` thành cảnh báo khi vượt 8%, thêm số đo này vào báo cáo kịch bản.

**C. Trục kể = nhân vật và cái giá, không phải nguồn**
- Mỗi Long có một nhân vật, một mục tiêu hoặc nỗi sợ, một chuỗi lựa chọn và hậu quả.
- Đối chiếu "phim kể / hồ sơ ghi" chỉ dùng làm 1–2 cú twist, không làm trục.

**D. Model**
- Lời Long: **Sonnet hoặc agy Gemini** viết. Chủ kênh chọn sau khi đọc bake-off, hoặc luân phiên hai model rồi đo retention.
- Review câu chuyện: model khác họ với người viết (Sonnet ↔ agy). **Không giao Codex viết hay review lời tiếng Việt.**
- Codex chỉ làm code, cổng và lắp spec.

**E. Sửa tài liệu và prompt**
- `docs/pm/prompts/long-story-review.md` và brief review: đổi mục tiêu từ "giữ mọi lời rào, cắt suy đoán" sang "tăng cảnh, xung đột, câu hỏi giữ chân; chỉ sửa sai sự thật".
- `storytelling-guide.md` §13: thêm luật phỏng dựng có nhãn, ngân sách rào 8%, và luật nguồn hiển thị trên hình.

**F. Áp ngay cho video đang chờ**
- 5 Long đợt mới (MIM Air Canada, Knight; CK margin, 50 triệu; CL Vidocq) chưa TTS. Đề xuất cho người kể viết lại theo A–E trước khi TTS. Thêm khoảng nửa ngày công agent, không tốn render.
- Hoàng Kim Vinh (19/11) và Địch Nhân Kiệt (24/11) đã upload private, chưa public. Hai lựa chọn:
  - (a) giữ nguyên;
  - (b) viết lại lời, TTS và render lại. Tốn khoảng 3–4 giờ máy mỗi bài, kịp lịch.

  Chủ kênh quyết.
- Lưu Gù đã/sắp public: giữ nguyên (luật không sửa video đã đăng). Dùng làm mốc so retention.
