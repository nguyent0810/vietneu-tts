# QA preview · p131_fs_quet_nha_c1v2

- Chủ đề: fs_quet_nha_mung1_tet · phương án **c1 v2**
- content_sha256: `54dd0dd33d148bbca651d4f2d876c8543267ee1a828d05122e747b662999b68f`
- candidates_file_sha256: `756f6253d4da073b9ddc3a9388c383cce39d812f2c1a8ae38fe42249c488bc67`
- Trạng thái duyệt: **PENDING_APPROVAL** — v2 theo yêu cầu PO; chờ PO duyệt.
- Title: Cô hầu biến mất trong đống rác ngày mồng 1 Tết · Thumbnail: Chui vào đống rác
- Render: **RENDERED**  · máy: oracle vieneu-worker (A1 2 OCPU/12 GB)
- Thời lượng: 45.5 s · thời gian render: 645 s · RAM đỉnh: 2217 MB
- Âm thanh: {'integrated_lufs': -20.0, 'true_peak_dbfs': -1.4}

- First frame: **FIRST_FRAME_MISMATCH** — Duyệt: đống rác trước sân nhà xưa, bóng người phụ nữ mờ dần, đèn lồng đỏ. Thực tế: chữ động 'Cô hầu / chui vào đống rác' (không có ảnh).

## Nguồn
- s1 Giáo dục & Thời đại
- s2 vietbao.vn
- s3 Znews
- s4 Pháp luật VN

## Fact đã dùng
- f01, f02, f03, f04, f07, f08, f09, f10

## Lỗi / điểm còn tồn tại
- 'Sưu thần ký' chỉ dựa 1 bài báo (s1); chưa đối chiếu văn bản gốc.
- Không có ảnh tư liệu (Tết/chổi); toàn bộ là thiết bị chữ động — first frame đã duyệt (đống rác + bóng người mờ, đèn lồng) KHÔNG dựng được, thay bằng hook_slam chữ.
- Render 2 lần: lần 1 chữ A/B đè chữ cảnh split, 'Nghèo dần' tràn và dấu son đè chữ -> đã sửa.

## Cảnh cần PO chú ý
- 0–3s: hook chữ thay cho cảnh đã duyệt
- cảnh split hai dị bản (A/B)
- Âm lượng −20,0 LUFS (thấp so với chuẩn short −14)

## File
- final_preview.mp4 · contact_sheet.jpg · first_frame.jpg · timing.json · status.json · render.log · mem_samples.txt
