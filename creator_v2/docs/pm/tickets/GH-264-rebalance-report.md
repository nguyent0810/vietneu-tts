# GH-264 — Báo cáo cân nhịp

Thời lượng tính theo điểm đầu câu trong `timing.json`; neo giữa câu được nội suy theo số từ trong câu vì timing chỉ có mốc câu. Riêng loi-cam ước tính 3,3 từ/giây cho lời mới. Các số sau sửa là dự kiến, không phải đo bản render mới.

| Slug | Trước (giây) | Sau (giây) | Cảnh photo thêm (đầu câu; ảnh) |
|---|---|---|---|
| cl-bao-s2-loi-cam | 6.67 · 16.06 · 3.64 · 7.27 · 4.55 | 2.73 · 3.94 · 3.64 · 4.55 · 4.85 · 3.03 · 3.64 · 7.27 · 4.55 | câu 2: i0, câu 4: i0, câu 5: i1, câu 6: i3 |
| cl-bao-s2-song-hue-dan | 5.84 · 11.28 · 3.36 · 7.2 · 3.36 | 2.24 · 3.60 · 4.80 · 3.36 · 3.12 · 3.36 · 7.20 · 3.36 | câu 2: i3, câu 5: i0, câu 6: i3 |
| cl-bao-s2-au-duong-tu | 2.08 · 11.12 · 3.12 · 12.56 · 2.48 | 2.08 · 2.88 · 5.04 · 3.20 · 3.12 · 7.12 · 5.44 · 2.48 | câu 3: i1, câu 6: i0 |
| cl-a-nezumi-1831 | 4.32 · 10.0 · 4.8 · 11.84 | 4.32 · 6.64 · 3.36 · 4.80 · 9.04 · 2.80 | câu 5: i3, câu 12: i3 |
| cl-a-oppert-1868 | 2.56 · 19.28 · 3.84 · 6.0 | 2.56 · 5.44 · 5.28 · 4.64 · 3.92 · 3.84 · 6.00 | câu 3: i3, câu 5: i3, câu 6: i1 |
| cl-a-vien-minh-vien-1860 | 11.6 · 2.88 · 5.6 · 9.76 | 2.08 · 5.76 · 3.76 · 2.88 · 5.60 · 9.76 | câu 2: i3, câu 4: i0 |
| cl-a-phaulkon-1688 | 2.48 · 4.48 · 15.84 · 9.28 | 2.48 · 4.48 · 6.24 · 6.88 · 2.72 · 5.20 · 4.08 | câu 5: i3, câu 10: i0 |
| cl-a-manila-1762 | 16.24 · 2.88 · 2.24 · 9.28 | 2.56 · 3.20 · 3.52 · 6.96 · 2.88 · 2.24 · 9.28 | câu 2: i3, câu 3: i2, câu 4: i0 |
| cl-a-mayrena-1888 | 6.4 · 12.48 · 7.04 · 4.96 | 2.48 · 3.92 · 5.64 · 6.84 · 7.04 · 4.96 | câu 2: i0, câu 4 + 1 giây: i3 |
| cl-dong-lang-min-1928 | 8.32 · 2.64 · 6.0 · 8.72 · 2.88 | 2.08 · 6.24 · 2.64 · 6.00 · 8.72 · 2.88 | câu 2: i3 |
| cl-dong-lang-da-min-chau | 2.24 · 6.0 · 9.36 · 5.92 · 6.4 | 2.24 · 6.00 · 9.36 · 5.92 · 6.40 | Không |
| cl-dong-lang-tu-1947 | 2.0 · 2.88 · 9.04 · 6.32 · 8.4 | 2.00 · 2.88 · 9.04 · 6.32 · 5.44 · 2.96 | câu 10: i0 |

Các cảnh photo thêm dùng `kb: out`, tiêu điểm `[0.5, 0.55]`; mã ảnh đối chiếu với `imgs` của từng spec. Phaulkon tách timeline tại binh biến; Âu Dương Tu tách timeline tại câu về hối lộ, giữ nguyên nội dung các mốc.

Kiểm tra:

- `PYTHONPATH=. python motion/stier/build.py <12 slug> --preflight`: OK cả 12 sau chỉnh sửa cuối.
- `PYTHONPATH=. python motion/stier/script_lint.py <slug>` cho từng bài: 0 lỗi; cảnh báo lần lượt theo thứ tự bảng: 5, 9, 1, 3, 5, 5, 6, 5, 6, 1, 1, 1. Cảnh báo liên quan hook, câu cuối, câu dài, dẫn nguồn và R10; không sửa `lines` theo phạm vi ticket.
- Kiểm tra tự động thời lượng dự kiến, khoảng cách mốc timeline và dùng đủ `imgs`: đạt.
- Không thêm khẳng định mới; chưa kiểm chứng lại các khẳng định có sẵn trong lời và nhãn vì ticket chỉ cho sửa cảnh.
- Không render theo ticket: chưa có clip sheet mới để kiểm tra hình thực tế; sheet cũ nằm tại `output/stier/<slug>/final_sheet.jpg`, không phản ánh sửa đổi. Không có thumbnail mới trong phạm vi.
- Do mốc chỉ ở cấp câu và chưa render, thời lượng thực tế, tính khớp giọng/nhãn và chuyển động phải được Lead kiểm khi dựng lại. Mốc `loi-cam` hoàn toàn là ước lượng và cần đo lại sau TTS.

- Kiểm tra rg dấu hỏi trên 12 spec và báo cáo: không có kết quả.
