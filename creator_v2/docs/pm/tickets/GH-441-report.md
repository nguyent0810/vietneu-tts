# GH-441 — báo cáo

Đã sửa cổng chung preflight/build: chặn dòng kết thúc bằng dấu phẩy; đếm theo câu các cụm rào nguồn dùng FLOW_SOURCE_TERMS, SOURCE_PATTERN và mẫu bổ sung, chặn Short truyện/test_cell và cảnh báo dạng khác. Chỉ áp dụng từ ngày 29/11/2026 hoặc khi không khai publish_at. Dấu {pd} cuối câu được bỏ trước TTS; chip PHỎNG DỰNG hiển thị trong khoảng thời gian câu đó trên mọi cảnh giao với câu. Đã thêm test tests/test_stier_ear.py và sửa casefile.js/css để hiện chip.

Kiểm tra:
- pytest tests/test_stier_ear.py: 9 passed. Dùng wrapper đổi mode mkdir của pathlib thành 0777 và --basetemp riêng vì ACL thư mục tạm mặc định bị từ chối.
- pytest tests/test_stier_ear.py tests/test_console.py: lần đầu 12 passed, 3 lỗi fixture tmp_path do Windows từ chối truy cập. Khi dùng wrapper trên: 12 passed, 3 failed; một lỗi test mới do lỗi mã hóa khi ghi lần đầu, đã sửa và chạy lại thành công; hai lỗi test_console do tiến trình qa_blank.py không ghi được thư mục tempfile của Windows (WinError 5). Chưa xác nhận test_console xanh, cần Lead chạy lại trong môi trường có quyền thư mục tạm.
- node --check motion/hf/assets/engine/casefile.js: đạt.
- python motion/stier/build.py cl-a-mayrena-1888 cl-a-manila-1762 cl-a-phaulkon-1688 cl-hkv-survival-pilot --preflight: exit 0, tất cả OK. Ba spec mới nhất chọn theo publish_at: Mayrena 127 từ/38,5s, Manila 128/38,8s, Phaulkon 130/39,4s; pilot 132/40,0s.
- Ba spec mới có cảnh báo evidence bỏ qua trường code/title/desc (Phaulkon: title/desc), rules dưới 3 chưa áp luật hook #337; tất cả bốn spec có ảnh chưa có sẵn để đo sáng. Pilot còn cần người duyệt hook và khung 0.
- Không render theo brief, nên chưa kiểm hình thật, vị trí/độ đọc chip, clip sheet hoặc thumbnail; không có đường dẫn sheet/thumbnail. Không kiểm chứng dữ kiện nội dung vì đây là ticket code. Chưa chạy script_lint riêng; preflight đã chạy short_retention.

Không đăng, commit, push hay đổi lịch. Không ghi state.sqlite. Không có chuỗi hai dấu hỏi mới trong build.py hoặc test mới. Các thư mục tạm do pytest tạo được giữ nguyên theo luật không xoá ngoài topic.
