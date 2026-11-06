# GH-228: thêm ảnh cho 6 Short CL loại S

Sáu bài sau mỗi bài mới có 1 ảnh (`docs/pm/tickets/GH-228-cl-respec-report.md`):
- cl-frank-grigware-van-tay
- cl-black-dahlia-56-phut
- cl-ross-tien-chuoc
- cl-alger-hiss-khai-man
- cl-diane-jackson-van-tay
- cl-james-ricks-ban-tu

**Việc:** mỗi bài thêm cho đủ **≥ 4 ảnh khác nhau**. Một ảnh dùng tối đa 2 cảnh.
- Ảnh minh họa chung lấy từ danh sách `docs/pm/tickets/GH-228-cl-library-images.md`: 50 ảnh noir, không người thật, không chữ. Đường dẫn trong bảng tính từ gốc repo; xem cách các spec CL lô này khai báo ảnh `local:`. Đặt `credit: false`.
- Chọn ảnh hợp lời từng câu: bài về vân tay dùng ảnh bàn điều tra, kính lúp, hồ sơ; bài bắt cóc tiền chuộc dùng ảnh điện thoại, xe, bến cảng…
- Không dùng cùng một ảnh kho cho 2 bài.
- Ảnh tư liệu thật của vụ án (nếu đã có) giữ nguyên.

Lời giữ nguyên. Sửa bằng Python UTF-8. Chạy `python motion/stier/build.py --preflight <slug>` cho cả 6 bài đến khi OK, rồi chạy lệnh kiểm mất dấu. Không render, không commit.

**Báo cáo** `docs/pm/tickets/GH-228-cl-s-images-report.md`: mỗi bài ghi danh sách ảnh đã dùng.
