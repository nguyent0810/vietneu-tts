# GH-33 · Codex: ráp lời đọc mới vào 12 spec Short, cảnh theo beats

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33.

Đầu vào: `docs/pm/tickets/GH-33-lines.json`. Grok đã viết lại, Lead đã duyệt. Mỗi slug gồm `title`, `frame0`, `lines` (119–122 từ, câu trọn nghĩa), `say`, `beats` (gợi ý hình cho từng câu: M/D/G/T kèm mô tả và từ khóa Pexels).

## Lỗi vòng trước, không được lặp lại
- Cắt câu giữa chừng để đủ số từ.
- 12 spec dùng chung một chuỗi cảnh y hệt (`kinetic counter board counter board slam`).

## Được ghi
- 12 spec `data/stier/specs/<slug>.json`
- báo cáo `docs/pm/tickets/GH-33-assemble-report.md`

**Không:** sửa chữ trong `lines` (copy nguyên văn), sửa code, render, TTS, upload, commit.

## Việc
1. Mỗi spec:
   - `title`, `lines`, `say` lấy **nguyên văn** từ `GH-33-lines.json`; gộp với `say` cũ nếu còn mục cần;
   - chữ cảnh 0 = `frame0`, hiện ngay giây 0.
2. **`scenes` dựng theo `beats`, mỗi câu ≥ 1 cảnh:**
   - đúng loại M/D/G/T;
   - dùng đúng kiểu cảnh engine có (`counter`, `chart`, `ledger`, `table`, `timeline`, `board`, `cards3d`, `map`, `kinetic`, `quote`, `slam`, cảnh clip/ảnh…);
   - mốc thời gian neo vào câu hoặc chữ (xem docstring `build.py`).

   Chuỗi kiểu cảnh của 12 bài phải khác nhau và không trùng chuỗi cảnh của Short liền kề trong cùng kênh.
3. **Clip M.**
   - Tìm id Pexels thật bằng công cụ sẵn có trong repo (`motion/stier/clips.py`, `find.py`, `pexels` CLI), theo từ khóa trong `beats`.
   - Công cụ cần khóa API mà sandbox không có thì để `"vid": null`, thêm `"q": "<từ khóa>"`, rồi ghi vào báo cáo để agy điền lúc render.
   - Ảnh Wikimedia Commons chỉ dùng file có giấy phép tự do; ghi `File:` trong `imgs`.
4. **CK:**
   - `description` giữ câu "Nội dung giáo dục, không phải tư vấn đầu tư.";
   - cảnh chốt có dòng nhỏ này nếu `beats` yêu cầu;
   - không logo, không tên ngân hàng hay công ty trên clip.
5. **Mô tả, tag.** Áp `description_head`, `hashtags`, `tags` từ `docs/pm/tickets/GH-33-titles.json` vào đầu `description`/`tags`, giữ phần nguồn và ghi công.
6. **Kiểm cho cả 12 slug:**
   - `python motion/stier/build.py <12 slug> --preflight` → 0 lỗi;
   - `python motion/stier/script_lint.py <slug>` → 0 LỖI;
   - tự kiểm `lines` khớp 100% với `GH-33-lines.json` (so chuỗi).

## Báo cáo
Mỗi slug:
- chuỗi kiểu cảnh;
- clip/ảnh đã chọn, hoặc `q` chờ điền;
- kết quả `preflight`/`lint`;
- xác nhận `lines` khớp nguyên văn.
