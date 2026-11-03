# QA preview · L_p131_fs_mauthan_c2v2

- Chủ đề: fs_mau_than_1968_2027 · phương án **c2 v2**
- content_sha256: `8feffab11291212eb942eaf8e9ec5007ef61e78dddfcdab1a236ec002e8fd4db`
- candidates_file_sha256: `a96f3e577dac89e6328983b74bd1e52e91146c415d2bdc3022c8c08fc5819dc5`
- Trạng thái duyệt: **APPROVED** — PO 04/11 APPROVE c2 v2 (decisions/fs_mau_than_1968_2027/v2.json)
- Title: Sinh năm 1968 Mậu Thân: 2027 không phạm tam tai, lưu ý gì? · Thumbnail: 1968 không phạm tam tai
- Render: **RENDERED**  · máy: oracle vieneu-worker (A1 2 OCPU/12 GB)
- Thời lượng: 191.1 s · thời gian render: 611 s · RAM đỉnh: 2236 MB
- Âm thanh: {'integrated_lufs': -16.0, 'true_peak_dbfs': -1.2}

- First frame: **FIRST_FRAME_MISMATCH** — Duyệt: vòng 12 con giáp xoay, chữ '1968 · Mậu Thân' ở tâm. Thực tế: thẻ chữ '1968 · Không phạm tam tai'; vòng con giáp xuất hiện ở câu 3 (~10 s).

## Nguồn
- s1 thayungkhiem.vn (thương mại)
- s3 lasotuvi.io
- s4 thayungkhiem Thư viện Bát Tự
- s6 VietNamNet (bài 2026, quy tắc tam tai chung)

## Fact đã dùng
- f01, f02, f07, f09, f10, f11, f12, f13, f14, f17

## Lỗi / điểm còn tồn tại
- PREVIEW = mở đầu + 3 lớp + tóm lại (~4 phút).
- KHÔNG có sao hạn, Kim Lâu, Thái Tuế (f15/f18/f08 chưa xác minh) — có thể kém hấp dẫn hơn baseline.
- Trạng thái duyệt: **APPROVED** — PO 04/11 APPROVE c2 v2 (decisions/fs_mau_than_1968_2027/v2.json)
- Ý 'Cẩn trọng không có nghĩa là lo sợ…' là lời kênh.
- Render 2 lần: lần 1 thiếu media (chữ trên nền trống 21%) và thiết bị 'card' không vẽ (khung trống ~156s) -> thêm 7 media + đổi sang list_build.
- 6 câu viết lại để mỗi câu ≤3 tên chi (luật engine: TTS đọc lồng) — ý giữ nguyên.
- Cảnh báo nhịp hình (không chặn): chỉ 4 loại cảnh, 6–7 giây/cảnh (mục tiêu 2–4s).

## Cảnh cần PO chú ý
- hook 0–8s
- chiwheel tam tai
- wheel Thân xung Dần

## File
- final_preview.mp4 · contact_sheet.jpg · first_frame.jpg · timing.json · status.json · render.log · mem_samples.txt
