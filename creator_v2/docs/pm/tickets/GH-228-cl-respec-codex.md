# GH-228: lắp lại hình 12 Short CL (lô 1)

Lead soát contact sheet bài `cl-bao-luoi-bo` (`output/stier/cl-bao-luoi-bo/final_sheet.jpg`): **1 chân dung Bao Chửng chiếm 6/10 khung**. Hình đơn điệu, cùng loại lỗi với lô CK vòng 1. Lời và dữ kiện giữ nguyên, chỉ sửa phần hình.

**Danh sách 12 spec:** xem `docs/pm/tickets/GH-228-cl-shorts1-report.md`.

**Yêu cầu cho mỗi bài:**
- ≥ 4 ảnh khác nhau. Một ảnh dùng tối đa 2 cảnh;
- ≥ 5 loại cảnh của theme `case`: photo hoặc split, file, ledger, timeline, date, quote, counter, slam, map, board;
- số hoặc ngày chính hiện cỡ lớn;
- luật phối cảnh của preflight phải đạt.

**Nguồn ảnh:**
- bài nối Bao Thanh Thiên: `output/long/bao-thanh-thien/img/` (88 ảnh tự do, mô tả ở `research.json` và sidecar `*.json`);
- bài nối Hòa Thân: `output/long/hoa-than/img/` (142 ảnh tư liệu, ảnh AI `ai01–ai20` chỉ dùng cho bối cảnh);
- bài S: ảnh Commons tự do của vụ án đó (`motion/long/SOURCES.md`), cộng ảnh minh họa chung trong kho `output/asset_library/` tag `cl` / `minh_hoa_chung`, đặt `credit: false`;
- không vẽ người thật bằng AI.

Xem cách các spec CL cũ khai báo ảnh `local:` và ảnh Commons, ví dụ `unabomber.json`.

**Làm:** sửa bằng script Python UTF-8, chạy `python motion/stier/build.py --preflight <slug>` cho cả 12 đến khi OK, rồi chạy lệnh kiểm mất dấu. Không render, không commit.

**Báo cáo** `docs/pm/tickets/GH-228-cl-respec-report.md`: mỗi bài ghi số ảnh khác nhau, các loại cảnh, kết quả preflight.
