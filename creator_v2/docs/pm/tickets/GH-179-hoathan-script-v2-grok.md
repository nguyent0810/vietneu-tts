# GH-179: Hòa Thân, kịch bản vòng 2 (viết lại giọng kể)

Lead đã review `data/long/hoa-than/script.md` vòng 1. **Phần dữ kiện tốt và giữ nguyên:** số, ngày, nguồn, cách đặt các con số tài sản cạnh nhau, không dựng cảnh hành hình. **Phần giọng kể hỏng:** lời đọc nghe như biên bản kiểm dữ kiện, không phải phim tài liệu. Viết lại toàn bộ lời đọc. Giữ dàn 14 chương, các mốc của plan và `visual_plan.md`.

## Lỗi phải hết (Lead đếm trên bản 1)
1. **Ghi chú sản xuất lọt vào lời đọc.** Ví dụ thật từ bản 1:
   - "Kịch bản này không kể danh sách thiếp… Plan đã cấm đưa vào lời."
   - "Không có pháp trường trong lời đọc này. Không có dải lụa trên hình."
   - "Mô-típ một dòng bản kê chạy suốt mười hai lần."
   - "Cảnh ấy ta không dựng. Không dây. Không máu trên lời đọc."

   Luật cấm cái gì thì **chỉ đơn giản là không viết cái đó ra**, không được nói ra rằng mình đang không viết.
2. **"Wikipedia" xuất hiện 26 lần trong lời đọc**, chưa kể "bài tiếng Việt", "bài tiếng Anh", "trang bách khoa", "cùng trang ấy", "infobox". Người xem không cần biết bạn đọc trang nào.
   - Nguồn đặt ở `factcheck.md` và bảng nguồn, không đặt trong lời.
   - Lời đọc chỉ nêu tên nguồn khi tên đó **có giá trị kể chuyện**: Thanh sử cảo, chỉ dụ, tấu của quan điều tra, sứ đoàn Macartney, Harris (2018). Tối đa khoảng 1 lần mỗi chương.
   - Khi các nguồn lệch nhau, kể bằng giọng phim tài liệu, ví dụ: "Các con số được chép lại chênh nhau đến kinh ngạc. Có nơi ghi 1,1 tỷ lạng bạc. Có nơi chỉ ghi chừng 60 triệu." Vẫn không chọn một tổng.
3. **Lời đọc không tự nói về cấu trúc của nó.** Bỏ hết các câu kiểu: "Vòng thứ nhất đóng ở chương chín", "Sợi chỉ này sẽ quay lại ở chương tám", "Lời đọc theo mốc tiếng Anh", "Đó là chỗ gãy thứ tư, sẽ mở ở chương bốn", "Video này không chọn…". Vòng mở phải tạo bằng câu hỏi và tình huống, ví dụ "Nhưng vì sao Gia Khánh phải đợi ba năm?", không bằng lời báo trước số chương.
4. **Không đọc "Chương một. Nghịch lý."** Thẻ chương do hình đảm nhận. Xem cách mở chương trong `data/long/bao-thanh-thien/script.md`.

## Giọng mẫu
Đọc kỹ `data/long/bao-thanh-thien/script.md`: nhịp câu, cách dẫn trích, cách mở và đóng chương, cách nói "theo …" chỉ khi cần. Đọc lại skill `../.claude/skills/long-script/SKILL.md` và `references/story.md`, `line-rules.md`.

## Giữ nguyên
- 5.500–7.000 âm tiết, 14 chương.
- `factcheck_lint` 0 lỗi. Mọi số, ngày và trích dẫn trong lời mới vẫn phải có trong `factcheck.md`; cập nhật `factcheck.md` nếu câu đổi.
- `script_lines.gate` OK.
- Mở bài kiểu Nghịch lý, cold open 22/2/1799.
- Các cấm của plan: danh sách thiếp, chi tiết hành hình, chính trị hôm nay.

## Tự kiểm trước khi xong
Chạy và dán kết quả vào báo cáo:
```
python -c "import re,io;t=io.open('data/long/hoa-than/script.md',encoding='utf-8').read();L=[l for l in t.splitlines() if l.strip() and not l.startswith(('|','#','-','>','*'))];bad=[l for l in L if re.search(r'(?i)wikipedia|bách khoa|bài tiếng (việt|anh)|kịch bản|plan|lời đọc|trên hình|mô-típ|infobox|cùng trang|video này|chương (một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)',l)];print(len(bad));print('\n'.join(bad[:40]))"
```
Kết quả phải là 0, hoặc chỉ còn vài dòng mà bạn giải thích được vì sao cần giữ.

**Được ghi:** `data/long/hoa-than/script.md`, `data/long/hoa-than/factcheck.md`, báo cáo `docs/pm/tickets/GH-179-hoathan-script-v2-report.md` (UTF-8). Không commit, không TTS.

**Báo cáo:**
- số âm tiết;
- `factcheck_lint`;
- kết quả lệnh tự kiểm;
- 10 câu trước và sau tiêu biểu;
- tiêu đề đề xuất, mỗi dữ kiện kèm câu dẫn.
