# GH-333 lượt 2: ghép Short→Long theo nghĩa (Codex)

## Input (chỉ đọc)
Lead đã lấy từ YouTube các file sau, nằm ở `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\channels\<CH>\`, với CH là CL, CK, MIM:
- `shorts_public.json`: Short công khai, gồm video_id, title, description.
- `longs_public.json`: Long công khai, gồm video_id, title, description, tags, published.

## Việc
Với mỗi Short, chọn **một** Long cùng kênh mà người vừa xem Short đó nhiều khả năng muốn xem tiếp nhất. Thứ tự ưu tiên:
1. **Cùng nhân vật hoặc cùng vụ việc.** Ví dụ Short về Hòa Thân → Long Hòa Thân. Short về Deep Blue → Long Deep Blue đấu Kasparov.
2. **Cùng bối cảnh hoặc cùng dòng.**
   - CL: hải tặc nhà Thanh → Trịnh Nhất Tẩu; giang hồ Hong Kong → các Long hội nhóm Hong Kong; băng cướp Mỹ → Capone, Bulger; lừa đảo, đồ giả → Long lừa đảo nếu có.
   - CK: lãi kép → Long lãi kép; vàng → Long vàng; VN-Index, mua đều → Long chứng khoán từ số 0; thẻ tín dụng → Long nợ thẻ.
   - MIM: cờ, game → Long AI đấu trí; QR → Long QR.
3. **Cùng chủ đề rộng.** Lúc này đặt `confidence: "low"`.

Không ghép chỉ vì trùng một từ chung như "năm", "người", "triệu", "bí ẩn". Short không có Long nào hợp thì để `long_video_id: null`.

## Output
Ghi `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\channels\<CH>\related_map.json`, mỗi kênh một file:
```
{"channel":"CL","generated":"<ISO>","matches":[{"short_video_id":"...","short_title":"...","long_video_id":"...|null","long_title":"...","confidence":"high|medium|low","reason":"<≤15 từ tiếng Việt>"}]}
```

Có thể viết script Python tạm để đọc và ghi file. Phần chọn Long là việc của bạn: đọc tiêu đề và mô tả rồi quyết định, không dùng chấm điểm từ khóa máy móc.

Ghi bằng Python `encoding="utf-8"`, `ensure_ascii=False`. **Không ghi bằng PowerShell.** Sau khi ghi, kiểm bằng Python rằng không có chuỗi `??` trong file.

## Báo cáo
`docs/pm/tickets/GH-333-map-report.md`: với từng kênh, ghi số Short theo mức high, medium, low, null; 10 ví dụ ngẫu nhiên; và các Long được ghép nhiều nhất. Ghi bằng Python utf-8.

Chỉ ghi 3 file JSON trên và báo cáo. Không sửa code, không gọi mạng, không gọi `gh` để ghi.
