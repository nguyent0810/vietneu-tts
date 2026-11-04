# GH-10 · Codex sửa vòng 3 cho `mim-jobs-1985`

Danh sách lỗi: `docs/pm/tickets/GH-10-preview2-report.md`.

Phạm vi file và các điều cấm giữ nguyên như `docs/pm/tickets/GH-10-fix-codex.md`: không sửa `script.md`, không TTS, không render, không commit.

## Việc

1. **`sculley06` ở `ch03#6` và `ch07#6`.**
   - Bỏ `maxH`, `maxW` và `pos`, vì engine hiểu `maxH`/`maxW` là pixel và `pos` là chuỗi CSS.
   - Kiểm mọi cảnh trong bài: nếu có `maxH`/`maxW` nhỏ hơn 50 hoặc `pos` dạng mảng thì sửa như trên.
2. **Hai cảnh `org` trống quá 2 giây:** "BƯỚC 1 · BỊ TƯỚC QUYỀN" (ch03) và "TRUNG TÂM CỦA NEXT" (ch04). Neo nút con sớm hơn: trong vòng 1 giây sau khi cảnh mở.
3. **`ch04#4` (nhỏ):** nếu `nextstation` còn lượt dùng (tối đa 3 lần) thì thay ảnh; không còn thì để nguyên.

## Gate

Chạy đủ 8 cổng như vòng trước. `long_gate` phải ra ĐẠT, `floor` phải ra `[]`.

## Báo cáo

Ghi `docs/pm/tickets/GH-10-fix3-report.md`.
