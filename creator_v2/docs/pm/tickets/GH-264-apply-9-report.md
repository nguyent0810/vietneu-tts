# GH-264 — Báo cáo áp lời v3

Chỉ số câu bắt đầu từ 0; bảng ghi neo cảnh và từng hàng timeline. Nhãn ảnh cùng neo với cảnh; headAt hero giữ 0. Các ảnh không dùng đã bỏ cảnh tương ứng, giữ nguyên trường imgs.

Preflight chạy bằng `.venv\Scripts\python.exe motion/stier/build.py --preflight` với 9 slug, không dùng `--allow-hook`: tất cả OK. Cảnh báo: ảnh chưa có cục bộ để đo độ sáng ở cả 9 bài.

Lint chạy bằng `PYTHONPATH=. .venv\Scripts\python.exe motion/stier/script_lint.py` với 9 slug: 0 lỗi. Các cảnh báo còn lại được liệt kê dưới mỗi bài; R10 của sông Huệ Dân cần Lead kiểm tra.

Không kiểm chứng lại nguồn trong phạm vi áp lời; không có khẳng định mới được thêm. Không render theo brief nên không có clip sheet hoặc thumbnail mới. Không enqueue, đăng, commit hay đổi lịch.

## cl-bao-s2-loi-cam

Preflight: OK — 126 từ, 38.2 giây. Lint: 0 lỗi, 5 cảnh báo (R2, R5, R6).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [2, 'Câu'] · i1 | [4, 'Tống'] · i1 |
| [4, 'Dù'] · i2 | [6, 'Làm'] · i2 |
| [6, 'Các'] · timeline; hàng: [6, 'Các'] 15 QUYỂN, [7, 'Con'] CON RUỘT, [8, 'Người'] CON THIẾP | [7, 'Trong'] · timeline; hàng: [7, 'Trong'] THƯ RIÊNG, [8, 'Quyền'] QUYỀN CAO |
| [10, 'Bản'] · i3 | [9, 'Một'] · i3 |

Lời sửa để qua preflight: không.

## cl-a-nezumi-1831

Preflight: OK — 132 từ, 40.0 giây. Lint: 0 lỗi, 3 cảnh báo (R5, R6).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [2, 'Năm'] · i1 | [2, 'Năm'] · i1 |
| [3, 'Lời'] · i2 | [5, 'Lời'] · i2 |
| [6, 'Lúc'] · timeline; hàng: [6, 'Lúc'] LÚC BẮT, [7, 'Chuyện'] LỜI KỂ, [8, 'Tòa'] ÁN TỬ | [7, 'Nhưng'] · timeline; hàng: [7, 'Nhưng'] LÚC BẮT, [9, 'Chuyện'] LỜI KỂ, [10, 'Tòa'] ÁN TỬ |
| [9, 'Bức'] · i3 | — bỏ cảnh |

Lời sửa để qua preflight: câu 11: “Có lẽ người nghèo cần một người hùng, hơn là cần một cuốn sổ.” → “Có lẽ người nghèo cần một người hùng, hơn cần một cuốn sổ.”

## cl-a-oppert-1868

Preflight: OK — 132 từ, 40.0 giây. Lint: 0 lỗi, 5 cảnh báo (R4, R5, R6).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [3, 'Ông'] · i1 | [1, 'Một'] · i1 |
| [4, 'Tấm'] · i2 | [6, 'Nhưng'] · i2 |
| [5, 'Có'] · timeline; hàng: [5, 'Có'] LỜI NGHI, [6, 'Về'] HAMBURG, [7, 'Trang'] KHÔNG CÓ | [8, 'Về'] · timeline; hàng: [8, 'Về'] HAMBURG |
| [9, 'Nhiếp'] · i3 | — bỏ cảnh |

Lời sửa để qua preflight: câu 9: “Một lớp đá vôi bình thường đã giữ yên giấc ngủ của một người cha.” → “Một lớp đá vôi thường đã giữ yên giấc ngủ của người cha.”

## cl-bao-s2-song-hue-dan

Preflight: OK — 132 từ, 40.0 giây. Lint: 0 lỗi, 9 cảnh báo (R2, R3, R5, R6, R10).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [2, 'Hoạn'] · i1 | [2, 'Hoạn'] · i1 |
| [5, 'Bao'] · i2 | [6, 'Gặp'] · i2 |
| [6, 'Có'] · timeline; hàng: [6, 'Có'] ĐỊA BẠ, [7, 'Ông'] HẶC, [8, 'Tống'] KHÔNG NGÀY | [7, 'Có'] · timeline; hàng: [7, 'Có'] ĐỊA BẠ, [7, 'ông'] HẶC |
| [10, 'Bản'] · i3 | [9, 'Chuyện'] · i3 |

Lời sửa để qua preflight: câu 4: “Thử nghĩ xem, mấy khu vườn riêng lại chặn mất dòng sông của kinh thành.” → “Thử nghĩ xem, mấy khu vườn riêng chặn mất dòng sông của kinh thành.”

## cl-bao-s2-au-duong-tu

Preflight: OK — 132 từ, 40.0 giây. Lint: 0 lỗi, 1 cảnh báo (R5).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [1, 'Ông'] · i1 | [1, 'Ông'] · i1 |
| [6, 'Âu'] · i2 | [6, 'Âu'] · i2 |
| [7, 'Ông'] · timeline; hàng: [7, 'Ông'] VÍ DỤ, [8, 'Bao'] TRÁNH LỆNH, [9, 'Không'] KHÔNG HỐI LỘ | [7, 'Ông'] · timeline; hàng: [7, 'Ông'] VÍ DỤ, [8, 'Bao'] TRÁNH LỆNH, [10, 'Nhưng'] KHÔNG HỐI LỘ |
| [10, 'Bản'] · i3 | [12, 'Nghe'] · i3 |

Lời sửa để qua preflight: câu 9: “Có lẽ chiếc ghế ấy không dễ nhận.” → “Có lẽ ghế ấy không dễ nhận.”

## cl-a-vien-minh-vien-1860

Preflight: OK — 132 từ, 40.0 giây. Lint: 0 lỗi, 5 cảnh báo (R2, R5, R6).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [2, 'Những'] · i1 | [4, 'Những'] · i1 |
| [4, 'Mười'] · i2 | [5, 'Mười'] · i2 |
| [5, 'Một'] · timeline; hàng: [5, 'Một'] 47 VIỆN, [6, 'Viên'] 1707 | [7, 'Ngày'] · timeline; hàng: [7, 'Ngày'] 18 THÁNG 10, [8, 'Một'] 47 VIỆN |
| [7, 'Bức'] · i3 | — bỏ cảnh |

Lời sửa để qua preflight: câu 6: “Đồ quý vốn ở chung một chỗ bỗng bị xé lẻ đi khắp nơi.” → “Đồ quý ở chung một chỗ bị xé lẻ đi khắp nơi.”

## cl-a-phaulkon-1688

Preflight: OK — 130 từ, 39.4 giây. Lint: 0 lỗi, 6 cảnh báo (R2, R4, R5, R6).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [2, 'Ông'] · i1 | [1, 'Vốn'] · i1 |
| [4, 'Từ'] · timeline; hàng: [4, 'Từ'] 1685, [5, 'Ông'] NƯỚC PHÁP, [6, 'Phetracha'] BINH BIẾN | [2, 'Đến'] · timeline; hàng: [2, 'Đến'] 1685, [3, 'Từ'] NƯỚC PHÁP, [6, 'Khi'] BINH BIẾN |
| [7, 'Ông'] · i2 | [7, 'Phaulkon'] · i2 |
| [8, 'Bức'] · i3 | — bỏ cảnh |

Lời sửa để qua preflight: không.

## cl-a-manila-1762

Preflight: OK — 128 từ, 38.8 giây. Lint: 0 lỗi, 5 cảnh báo (R5, R6).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [2, 'Tướng'] · i1 | [5, 'Tướng'] · i1 |
| [3, 'Tổng'] · i2 | [6, 'Rojo'] · i2 |
| [4, 'Khi'] · timeline; hàng: [4, 'Khi'] PHẦN TƯ, [5, 'Phần'] BỎ, [6, 'Rojo'] 30 GIỜ | [7, 'Nhưng'] · timeline; hàng: [7, 'Nhưng'] PHẦN TƯ, [8, 'Phần'] BỎ |
| [8, 'Si-mông'] · i3 | — bỏ cảnh |

Lời sửa để qua preflight: không.

## cl-a-mayrena-1888

Preflight: OK — 127 từ, 38.5 giây. Lint: 0 lỗi, 6 cảnh báo (R2, R4, R5, R6).

| Neo cũ · ảnh / hàng | Neo mới · ảnh / hàng |
|---|---|
| 0 · i0 | 0 · i0 |
| [2, 'Toàn'] · i1 | [2, 'Toàn'] · i1 |
| [5, 'Ông'] · i2 | [8, 'Di'] · i2 (đổi thứ tự sau timeline; ảnh tem) |
| [7, 'Năm'] · timeline; hàng: [7, 'Năm'] 1889, [8, 'Di'] TEM | [6, 'Năm'] · timeline; hàng: [6, 'Năm'] 1889, [7, 'Ông'] 1890; hàng TEM chuyển sang ảnh i2 |
| [9, 'Ông'] · i3 | — bỏ cảnh |

Lời sửa để qua preflight: không.
