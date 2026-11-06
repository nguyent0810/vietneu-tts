# GH-228 — báo cáo lắp lại hình CL

**Chưa hoàn tất:** đã sửa sáu bài nối Long; sáu bài S chưa đạt bốn ảnh. Thư mục `output/asset_library/` được brief chỉ định không tồn tại, và chưa xác minh đủ ảnh Commons riêng cho từng vụ. Không thay bằng ảnh người trùng tên hoặc tư liệu không rõ liên quan.

| Bài | Ảnh khác nhau trong cảnh | Loại cảnh | Preflight |
|---|---:|---|---|
| cl-bao-luoi-bo | 4 | hero, file, photo, timeline, slam, ledger | OK |
| cl-bao-nghien-muc | 4 | hero, file, photo, timeline, slam, ledger | OK |
| cl-bao-cong-phu | 4 | hero, file, photo, timeline, slam, ledger | OK |
| cl-hoa-than-hai-muoi-toi | 4 | hero, file, photo, timeline, slam, ledger | OK |
| cl-hoa-than-doi-ten-phu | 4 | hero, file, photo, timeline, slam, ledger | OK |
| cl-hoa-than-thi-ve | 4 | hero, file, photo, timeline, slam, ledger | OK |
| cl-frank-grigware-van-tay | 1 | hero, file, kinetic, doc, slam, photo | OK, chưa đạt brief |
| cl-black-dahlia-56-phut | 1 | hero, file, kinetic, doc, slam, photo | OK, chưa đạt brief |
| cl-ross-tien-chuoc | 1 | hero, file, kinetic, doc, slam, photo | OK, chưa đạt brief |
| cl-alger-hiss-khai-man | 1 | hero, file, kinetic, doc, slam, photo | OK, chưa đạt brief |
| cl-diane-jackson-van-tay | 1 | hero, file, kinetic, doc, slam, photo | OK, chưa đạt brief |
| cl-james-ricks-ban-tu | 1 | hero, file, kinetic, doc, slam, photo | OK, chưa đạt brief |

Sáu bài Long dùng bốn ảnh local mỗi bài, mỗi ảnh một cảnh; ảnh chọn từ các file có sidecar PD/CC0 trong kho Long. Cần kiểm tra hình thật, vị trí cắt, cách ghi nguồn và cách builder xử lý đường dẫn local trước khi duyệt; preflight không xác nhận hình hiển thị. Các cảnh của sáu bài Long hiện còn cùng thứ tự, cần Lead xem nhịp và mức đa dạng giữa các bài. Không xác minh thêm các khẳng định cũ; lời và dữ kiện giữ nguyên, kể cả các điểm cần Lead kiểm trong báo cáo sản xuất trước.

Chạy `python motion/stier/build.py --preflight <slug>` sau sửa: 12/12 exit 0. Chạy `PYTHONPATH=. python motion/stier/script_lint.py <slug>`: 12/12 exit 0, không lỗi cứng; còn 56 cảnh báo R2, R4, R5, R6, R7, R10 như báo cáo trước. Giữ lời theo phạm vi ticket.

Kiểm UTF-8/JSON và tìm ký tự thay thế, hai dấu hỏi liền nhau, dấu hiệu mã hóa sai: 12/12 không thấy; kiểm tra giới hạn, không chứng minh mọi chữ đúng. Lần đầu lệnh dò lỗi mã hóa bị lỗi regex; đã chạy lại thành công. Khi sửa đã phát hiện chữ mới bị mất dấu do đường ống PowerShell, đã ghi lại bằng Python với escape Unicode rồi chạy lại kiểm tra và preflight.

Không render theo brief, nên không có clip sheet hay thumbnail mới; chưa kiểm chuyển động và độ đọc số trên khung thật. Không đăng, commit hoặc đổi lịch. Cần cung cấp vị trí kho ảnh chung hoặc đủ ảnh Commons đã xác minh cho sáu bài S để hoàn tất.
