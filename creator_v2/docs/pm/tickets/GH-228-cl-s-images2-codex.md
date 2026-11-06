# GH-228: 6 Short CL loại S dùng chung một bộ ảnh

Lead soát contact sheet. 6 bài sau đều lặp cùng các ảnh: ảnh phòng thí nghiệm "FORENSIC SCIENCE WORKSTATION" (FBI 2003), ảnh tòa nhà FBI, cùng một ảnh bàn hồ sơ.
- cl-frank-grigware-van-tay
- cl-black-dahlia-56-phut
- cl-ross-tien-chuoc
- cl-alger-hiss-khai-man
- cl-diane-jackson-van-tay
- cl-james-ricks-ban-tu

Vụ án xảy ra từ 1910 tới 1960 nên ảnh năm 2003 lệch thời đại, và 6 bài trông như một khuôn.

**Việc:**
- **Bỏ** ảnh FBI workstation và ảnh tòa nhà FBI ở cả 6 bài.
- **Mỗi bài dùng ≥ 4 ảnh, và không ảnh nào xuất hiện ở 2 bài.**
  - Giữ ảnh tư liệu đúng của vụ án nếu có (ví dụ chân dung Elizabeth Short cho Black Dahlia).
  - Phần còn lại lấy ảnh noir từ `docs/pm/tickets/GH-228-cl-library-images.md`: 50 ảnh, chia cho 6 bài, mỗi bài 3–4 ảnh khác nhau, hợp lời. Ví dụ: tù hoặc nhà giam → `prison corridor`; bắt cóc tiền chuộc → `phone booth`, `car under bridge`; khai man → `courtroom`; vân tay → `magnifying glass`, `case files`, `evidence bag`.
- Giữ trình tự cảnh khác nhau giữa các bài như vòng trước, lời không đổi.

Sửa bằng Python UTF-8. Chạy preflight cho cả 6 bài đến khi OK. Không render, không commit.

**Báo cáo** `docs/pm/tickets/GH-228-cl-s-images2-report.md`: mỗi bài ghi danh sách ảnh đã dùng.
