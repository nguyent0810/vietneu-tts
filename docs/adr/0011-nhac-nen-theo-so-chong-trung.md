# Nhạc nền chọn theo sổ chống trùng, cho cả Long lẫn Short

Trạng thái: đã chấp nhận (04/10/2026).

Trước 04/10, nhạc nền gần như không đổi giữa các video:

- mọi Long BUD dùng đúng 3 bản *Meditation Impromptu*;
- 240 short BUD dùng chung một bài;
- 113 short FS đều dùng *Asian Drums*.

Chính sách Spam của YouTube nêu đích danh việc dùng "cùng nhạc nền" trên nhiều video. Với một kênh đăng 5 short mỗi ngày, đây là rủi ro bị xếp vào nội dung lặp.

**Long.** `hf_music.pool_for` chọn một lần 4 bài, là những bài ít dùng nhất trong 3 video cùng kênh gần ngày đăng nhất (tính cả hai chiều thời gian). Kết quả ghi vào `bgm_ledger.json`. Nhạc chỉ đổi bài ở thẻ chương, chồng mờ 3 giây, san đều độ to. Bài thật sự đã phát được ghi vào `render.json` (`bgm_used`), để uploader ghi nguồn đủ mọi bài.

**Short.** Chọn bài ít dùng nhất trong 8 short gần nhất, không bài nào chiếm quá 35% trong 7 ngày; ghi vào `bgm_shorts.json`.

## Các phương án đã cân nhắc

- **Ghim một bài trong file dựng.** Sẽ lặp lại.
- **Chọn ngẫu nhiên lúc render.** Render lại sẽ ra bài khác, nên ghi nguồn bị lệch với bài thật sự đã phát.

## Hệ quả

- Cần duy trì một kho bài kèm `bgm/LICENSE.txt`. Bài mới tải từ incompetech (CC BY, ghi nguồn Kevin MacLeod), phải có dao động RMS 5 giây ≤ khoảng 14 dB.
- `hf_music.py audit <id>` cảnh báo khi trùng hơn 35% (Jaccard) với video gần đó.
- Bài dễ lấn giọng bị loại khỏi vòng xoay Long (ADR 0010).
- Mỗi kênh một màu nhạc: FS bỏ trống trận khi dùng cho bảng tĩnh. BUD dùng nhạc thiền không trống, thấp hơn giọng khoảng 20 dB, chuông CC0.

## Bằng chứng

`hf_music.py` (docstring, `CATALOG`, `LEGACY`, `MASKS_VOICE`), commit `092d397`, `output/cl_staging/long/bgm_ledger.json`.
