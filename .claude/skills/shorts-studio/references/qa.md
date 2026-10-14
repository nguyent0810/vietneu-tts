# Cổng QA (studio.py --qa chạy 1-3; 4-6 làm khi có thiết bị/theme mới)

Node 22: `export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm use 22; cd hyperframes_short/jobs/<id>; npx --yes hyperframes@0.8.75 ...`

1. `lint --json` -- phải 0 lỗi. Lỗi bất kỳ (vd `font_family_without_font_face`) làm `check` bỏ qua soát trình duyệt ("0 sample" ≠ đạt).
   Cảnh báo chấp nhận: composition_file_too_large, timeline_track_too_dense, nested_structure_needs_subcomposition, audio_file_without_element.
2. `check --json --at <giữa mỗi cảnh>` -- `ok:true`: runtime 0 lỗi JS, layout 0 lỗi, contrast 0 lỗi. Chồng lớp có chủ ý: gắn `data-layout-allow-overlap`
   ngay khi dựng (đã làm ở hook_poster, split, calendar); nền trang trí `data-layout-ignore`.
3. `qa_sheet.jpg` (16 khung) -- NHÌN: khung 0 đủ nghĩa, chữ không tràn dải phụ đề / cột nút phải, dấu tiếng Việt không bị cắt, cảnh không trống.
4. Thử tua ngược (thiết bị mới): `snapshot --at T_muộn,T_sớm` so với `snapshot --at T_sớm` -> khác nhau = trạng thái không an toàn khi seek.
5. Lỗi JS chi tiết: mở `jobs/<id>/index.html` trong Browser pane, `read_console_messages` (onlyErrors).
6. `ffprobe` thời lượng = `data-duration`; nghe thử: giọng rõ, nhạc thấp, tiếng động không dồn (<= 7 / 30s).
