# Kết quả YCV-ju9q · M1 W2 — mim-jobs-1985

## Vòng 2

Đã giảm tỷ lệ cảnh chỉ chữ, dựng lại HTML, soi clip sheet và chạy cổng cuối. Không sửa `script.md`, không chạy TTS, render, thumbnail hay bot ảnh.

### Danh sách cảnh chỉ chữ trước khi đổi (giảm dần)

CH06 câu 7 `slam` 8,16 giây; CH05 câu 1 `org` 8,08; CH04 câu 2 `slam` 7,76; CH04 câu 10 `kinetic` 6,88; CH07 câu 2 `slam` 6,72; CH06 câu 1 `org` 6,64; CH07 câu 5 `kinetic` 6,40; CH06 câu 3 `org` và CH03 câu 6 `org` cùng 6,32; CH06 câu 8 `org` 6,08; CH04 câu 1 `org` 6,00; CH08 câu 2 `slam` 5,84; CH06 câu 12 `slam` và CH04 câu 8 `org` cùng 5,76; CH01 câu 2 `slam` 5,68; CH05 câu 15 `kinetic` 5,60; CH03 câu 2 `slam` 5,52; CH00 câu 1/CH02 câu 8 `org` 5,36; CH07 câu 6 `org` 5,28; CH04 câu 7/3 `slam`/`org` 5,04; CH06 câu 5 `kinetic` 4,96; CH01 câu 3/CH05 câu 10/CH05 câu 8 4,88; CH08 câu 6/CH00 câu 3 4,72; CH02 câu 2 4,64; CH05 câu 12/CH00 câu 2/CH06 câu 6 4,48; CH03 câu 3/CH08 câu 7 4,40; CH01 câu 5 4,32; CH03 câu 1/CH02 câu 5 4,24; CH02 câu 1 4,16; CH00 câu 6/CH01 câu 8 4,08; CH04 câu 6/CH03 câu 5 4,00; các cảnh còn lại dưới 4 giây.

### Cảnh đã đổi

| Chương, câu | Cách đổi | Clip / ảnh |
|---|---|---|
| CH00, 1 | ảnh tư liệu cho bối cảnh mất quyền điều hành | `jobs84` |
| CH01, 2 và 5; CH02, 1 | ảnh Macintosh, Sculley cho sản phẩm và cuộc chọn lựa | `mac84`, `sculley06` |
| CH03, 6 | ảnh minh họa cho hồi tưởng năm 2005 | `ai01` (stand-in) |
| CH04, 1, 2, 3, 5, 7, 8, 10 | timeline vụ kiện; counter giá NeXT/đầu tư Pixar; bars vốn; ảnh NeXTcube; timeline mốc tháng 11; b-roll máy tính cổ | `nextcube`, Pexels `8888818` |
| CH05, 1, 10, 13 | bars nhân sự; ảnh NeXTcube2; b-roll máy tính cổ | `nextcube2`, Pexels `8888818` |
| CH06, 1, 3, 7, 8, 10, 11 | timeline; counter thương vụ/lỗ ròng; bars doanh thu; ảnh NeXTstation; b-roll bàn phím | `nextstation`, Pexels `854027` |
| CH07, 2, 5 | timeline CEO tạm quyền và đường trở lại | không dùng clip |

Đã xử lý hai cảnh báo `scene_rules` loại cảnh liền kề bằng cách đổi loại/neo đúng thứ tự. Kết quả cuối: 0 cảnh báo, 0 đề xuất.

### Lệnh đã chạy và kết quả

1. `gen_scenes.py`, `script_lines.py` — thành công; 120 câu, 1.932 âm tiết.
2. `coverage_lint.py` — trước: 29,66% (158,48/534,38 giây); sau: 21,77% (116,32/534,38 giây), đạt ≤22%.
3. `scene_rules.py mim-jobs-1985` — 0 cảnh báo, 0 đề xuất.
4. `build_long.py mim-jobs-1985 html` — thành công đủ CH00–CH08, không có `Error`.
5. `clip_sheet.py` — thành công. Đã thay clip `854167` vì lộ chữ “MacBook Pro”; sheet cuối dùng `8888818` và `854027`, không lộ logo/chữ đọc được.
6. `long_gate.py mim-jobs-1985 --min-syl 1900` — **ĐẠT**: 1.932 âm tiết, 8,9 phút, 111 cảnh, 4,8 giây/cảnh, 2 clip khác, 5 ảnh khác, 32 URL nguồn.

### Cảnh báo còn lại

- HTML còn cảnh báo một số dòng chữ lớn chép nguyên lời đọc, và các cảnh báo floor không chặn build (3 b-roll/6 ảnh thấp hơn sàn khuyến nghị).
- `long_gate` cảnh báo ảnh dọc `jobs84`, `mac84`, `sculley06` chưa có `focus`; cổng vẫn ĐẠT.
- `ai01` chưa có file ảnh AI; cảnh dùng stand-in, là ngoại lệ ảnh AI theo luật Long.
- Không có khẳng định mới nào không kiểm được.

### Bàn giao

- Cảnh/spec: `data/long/mim-jobs-1985/gen_scenes.py`
- HTML: `output/long/mim-jobs-1985/mim-jobs-1985_ch00.html` đến `mim-jobs-1985_ch08.html`
- Clip sheet đã soi: `output/long/mim-jobs-1985/qa_clips.jpg`
- Thumbnail: không tạo/không sửa theo ticket.
