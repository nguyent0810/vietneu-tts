# QA — p131_fs_quet_nha_c1v2_img (Quét nhà c1 v2, làm lại hình bằng ảnh AI) · 04/11/2026

- Packaging c1 v2 đã APPROVE (hash 54dd0dd3…): title, thumbnail, hook và lời đọc giữ nguyên. `lines` và `voice` giống hệt spec đã duyệt, dùng lại voice.wav cũ.
- Ảnh: 5 ảnh Grok Bot, 1080×1920. Đã soát bằng mắt: không có chữ hay số, không thấy rõ mặt, không có bạo lực. Hash khớp giữa Mac và Oracle.
- Render trên Oracle (2 OCPU / 12 GB), qua studio_runner:
  - Lần 1: 883 s, RAM đỉnh 474 MB. Lỗi: nhãn đè kicker; ảnh không phủ kín khung.
  - Lần 2: 875 s, đạt.
- Probe: h264 1080×1920 + AAC, dài 45,5 s.
- Loudness: −20,0 LUFS, đỉnh −1,6 dBFS. Lỗi chung của production, sửa ở PR #133.
- check: runtime 0 lỗi, contrast 0 lỗi, layout 1 lỗi (bằng bản đã APPROVE).
- First frame: ảnh ai_01 (đống rác, bóng cô hầu mờ dần, đèn lồng đỏ), khớp mô tả first frame đã duyệt.
- Còn mở:
  - ai_05: đầu cảnh còn thấy dải tối hai bên khi máy đang phóng vào.
  - 4 cảnh pan_tour liên tiếp, studio báo cảnh báo đa dạng.
  - Cảnh 0 không phải hook_*. Đây chỉ là cảnh báo, không chặn render.
- Trạng thái: CHƯA DUYỆT. Chờ PO xem.
