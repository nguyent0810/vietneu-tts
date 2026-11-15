# GH-416 — Báo cáo

## Thay đổi

- `motion/first_frames.py` trích khung qua ffmpeg, bỏ trên 12%, dưới 22%, mỗi bên 5%; thu nhỏ tối đa 320 px và đo độ lệch chuẩn sáng, tỉ lệ điểm chênh sáng láng giềng trên 20. Chỉ báo lỗi khi mọi khung đều phẳng; lỗi đọc video cũng chặn.
- Long kiểm file tạm sau ghép trước công bố ở 0,5 / 1,5 / 2,5 giây; bỏ qua legacy. Short kiểm sau grade ở 0,3 / 1 / 2 giây khi `rules >= 3`. Thông báo nêu số đo và gợi ý kiểm focus.
- Test bao gồm video tổng hợp, Long legacy và topic mới.

## Ngưỡng và số đo

Khung phẳng khi đồng thời std < 8 và edge < 0,025. Edge là tỉ lệ pixel có chênh lệch sáng với láng giềng ngang hoặc dọc > 20, sau thu nhỏ. Bảng sau là `std / edge` cho video tổng hợp: `kinds0` là xám có hạt nhẹ và chữ HUD; `kinds1` là chân dung vẽ có chi tiết; `kinds2` là một khung phẳng, hai khung có chi tiết.

| Mẫu | 0,3 s | 1 s | 2 s |
|---|---:|---:|---:|
| test_video_frames_kinds0_True_0 | 2.37 / 0.0000 | 2.35 / 0.0000 | 2.36 / 0.0000 |
| test_video_frames_kinds1_False0 | 35.86 / 0.0153 | 35.86 / 0.0153 | 35.88 / 0.0153 |
| test_video_frames_kinds2_False0 | 2.37 / 0.0000 | 35.87 / 0.0156 | 35.90 / 0.0153 |

Đo 20 trong 221 Short ở `D:/Tools/Youtube Creator v2/vietneu-main/creator_v2/output/stier`, lấy cách đều theo danh sách tên. Đây là kiểm tra không bị chặn trên mẫu, chưa xác nhận nội dung từng khung bằng mắt. Không có `output/long/*/final.mp4` tại đường dẫn brief nên chưa hiệu chỉnh trên Long thật.

| Short | 0,3 s | 1,0 s | 2,0 s | Kết quả |
|---|---:|---:|---:|---|
| bud-bd-20-11-thay-tro | 40.27 / 0.0559 | 40.26 / 0.0556 | 40.00 / 0.0562 | QUA |
| bud-bd-5-dieu-nen-nho-v3 | 38.69 / 0.0259 | 39.02 / 0.0259 | 39.49 / 0.0262 | QUA |
| bud-cx-con-khi-va-bay | 25.57 / 0.0333 | 27.12 / 0.0420 | 30.17 / 0.0520 | QUA |
| bud-cx-tho-tren-mat-trang | 39.96 / 0.0563 | 38.19 / 0.0599 | 37.43 / 0.0581 | QUA |
| bud-dv-loi-cuoi | 33.82 / 0.0300 | 40.19 / 0.0465 | 42.19 / 0.0526 | QUA |
| bud-hl-nghiep-khong-phai-dinh-menh-v3 | 22.87 / 0.0717 | 26.51 / 0.0870 | 26.62 / 0.0920 | QUA |
| bud-kg-ke-103-thang-minh | 32.47 / 0.0527 | 41.57 / 0.0400 | 57.34 / 0.0792 | QUA |
| bud-kg-ke-62-cua-toi-v2 | 35.24 / 0.0302 | 37.92 / 0.0434 | 37.12 / 0.0424 | QUA |
| bud-la-ram-ha-nguyen-v3 | 32.49 / 0.0257 | 32.53 / 0.0260 | 35.74 / 0.0401 | QUA |
| bud-ng-neu-ban-kiet-suc | 31.07 / 0.0489 | 31.35 / 0.0454 | 30.24 / 0.0467 | QUA |
| bud-tl-khi-dang-gian-v3 | 32.16 / 0.0345 | 35.65 / 0.0500 | 35.91 / 0.0514 | QUA |
| bud-ts-chiec-be | 33.47 / 0.0704 | 33.83 / 0.0734 | 37.30 / 0.0942 | QUA |
| bud-ts-song-giua-ghet-v3 | 32.92 / 0.0396 | 31.53 / 0.0339 | 32.12 / 0.0453 | QUA |
| bud-vs-nhuc-ke-v3 | 32.09 / 0.0590 | 34.31 / 0.0717 | 34.63 / 0.0693 | QUA |
| ck-b4-tien-nuoi-xe | 24.14 / 0.0516 | 26.39 / 0.0635 | 27.09 / 0.0641 | QUA |
| ck-dien-giam-44-dong-20-nam | 41.03 / 0.0485 | 40.61 / 0.0484 | 40.79 / 0.0482 | QUA |
| cl-bao-can-vua-quy-phi | 98.52 / 0.0787 | 104.32 / 0.0834 | 104.97 / 0.0855 | QUA |
| cl-dong-lang-tu-1947 | 72.54 / 0.1002 | 72.67 / 0.1018 | 72.74 / 0.1018 | QUA |
| cl-hoa-than-thi-ve | 72.82 / 0.0716 | 73.08 / 0.0712 | 73.09 / 0.0706 | QUA |
| mim-ve-tinh-google-4-chip-tpu | 48.28 / 0.0522 | 48.31 / 0.0547 | 48.38 / 0.0528 | QUA |

## Kiểm tra

- `tests/test_first_frames.py`: **5 passed**, qua `pytest.main` với `-q -p no:cacheprovider --basetemp=tmp_gh416_pytest_c` và vá tạm `os.mkdir` mode 0777 trong tiến trình test. Môi trường từ chối truy cập thư mục mode 0700 do pytest tạo.
- Đã chạy `tests/test_console.py`: 4 test đạt, 2 test CLI `qa_blank` lỗi `PermissionError` vì tiến trình con tạo thư mục tạm mode 0700 không truy cập được. Lead cần chạy lại trong môi trường có quyền thư mục tạm; chưa kết luận toàn bộ cổng test đạt.
- Không chạy toàn bộ pytest, không render production. Không chạy `git diff` do luật repo cấm đụng git; đã kiểm tra dấu tiếng Việt trong những dòng mới sau khi sửa lỗi mã hóa pipe PowerShell.
- Không có khẳng định nội dung cần fact-check. Ticket code không tạo clip sheet hay thumbnail.
