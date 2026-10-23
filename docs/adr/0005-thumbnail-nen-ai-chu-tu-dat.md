# Thumbnail Long: nền AI không có chữ, chữ do ta tự đặt, có tên mỏ neo, duyệt ở cỡ 168 px

Trạng thái: đã chấp nhận (23/10/2026).

Ngày 21/10 ta chốt thumbnail V2, mỗi bản 0–3 chữ, làm ba bản A/B/C. Ngày 23/10, bản đầu của Long Trạng Trình ("SẤM CỦA AI?") không cho người xem biết video nói về ai. Khi xem 12 video Trạng Trình top (0,86–2 triệu view) thì 11 video có tên nhân vật trên ảnh. CTR Long hiện là FS 6,8%, BUD 3,5%. BUD là điểm nghẽn.

Ta thử ba cách cho Long Cao Biền: tự dựng thuần, nhờ ChatGPT vẽ cả ảnh lẫn chữ, và nhờ Flow vẽ. Cách được chọn là **ghép**:

1. ChatGPT vẽ nền không có chữ: mặt cận, kịch tính, chừa một mảng tối cho chữ.
2. Đặt chữ bằng `thumb_cb.py <nền> <ra> full q=175 "t=DÒNG1|DÒNG2|CÂU HỎI" pal=BUD|FS`: tên riêng viết hoa trên hai dòng, cộng một câu hỏi ≤ 3 chữ.
3. Soát bản 168×94 (cỡ thumbnail trên điện thoại), và so trên một tờ chung với khoảng 36 thumbnail đối thủ.

## Các phương án đã cân nhắc

- **Tự dựng thuần từ ảnh có sẵn.** Ảnh tĩnh, thiếu kịch tính.
- **Để AI vẽ cả chữ.** Đẹp ở cỡ 168 px, nhưng không sửa được dấu tiếng Việt, lệch font của chuỗi, và Flow còn để lại watermark ✦.
- **Thumbnail 2 chữ lớn kèm một câu hứa và nhãn chuỗi** (kiểu cũ). Chữ quá nhiều; không có tên thì không có mỏ neo.

## Hệ quả

- Không dùng chữ doạ, chữ hứa hẹn kiểu "tiên tri" hay "999".
- Đổi font phải hỏi chủ kênh.
- Phản biện ngoài (Codex xem ảnh) chỉ để tham khảo. Ví dụ đã phủ quyết: Codex đòi "tối đa 3 chữ" cho cả tên, trong khi luật là tên + ≤ 3 chữ.
- Bẫy dấu: dấu huyền của chữ hoa ở dòng dưới có thể đọc thành dấu nặng của dòng trên. Vì vậy `thumb_v2.py` xếp dòng theo khung mực, không theo cỡ font.

## Bằng chứng

`output/cl_staging/long/research/long_test/thumbs/so_sanh_thumb_cb.jpg`, `so_sanh_thumb_ghep.jpg`, `output/cl_staging/long/research/flow_playbook.md` §9, `output/cl_staging/retro/2026-10-23_long_pilot.md`.
