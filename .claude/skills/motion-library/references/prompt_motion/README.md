# Thư viện tham khảo prompt-motion.com

Toàn bộ 234 mẫu motion graphic do Claude tạo trên https://prompt-motion.com/ (có prompt gốc), phân loại ngày 25/10/2026
cho hai kênh FS (Phong Thủy) và BUD (Phật giáo), đối chiếu với kho cảnh của `longform.js` và Short Studio.

| File | Dùng khi |
|---|---|
| `quy_uoc.md` | **Đọc trước.** 12 luật chung, 12 dạng cảnh (khi nào dùng, spec, mẫu, cấm), hàng đợi cảnh MỚI, đối chiếu engine với danh sách cấm |
| `catalog.md` | Tra mẫu theo nhóm A–N, kèm độ hợp FS/BUD, kỹ thuật, engine tương đương, rủi ro |
| `catalog.json` | Cùng dữ liệu, cho script lọc (ví dụ mọi mẫu `fit_bud >= 2`) |
| `prompt_mau.md` | Khuôn prompt 6 khối giao thợ viết cảnh mới; khuôn ngắn xin ảnh nền AI không chữ |
| `build_catalog.py` | Sinh lại `catalog.md` sau khi sửa `catalog.json` |
| `cap_nhat.py` | Lấy lại dữ liệu thô khi trang có mẫu mới |

## Số liệu chính

- 165/234 mẫu (70 %) là prompt một câu ("go all out", "showreel") hoặc quảng cáo SaaS: đẹp chung chung, ít giá trị cho kênh.
- 23 mẫu hợp kênh ở mức 2–3; chỉ một mẫu dùng ngay được: rối bóng giấy cắt (x4b47x-9cc84f, BUD 3, FS 2).
- 16 prompt có cấu trúc thật (prompt_value 3), là nguồn của 12 luật chung và khuôn `prompt_mau.md`.
- Nhóm theo số mẫu: J showreel 98 · K sản phẩm/UI 62 · B explainer 15 · N nhân vật 13 · G tái hiện 10 · F chữ 9 · H chuyển cảnh 5 ·
  M nhạc 5 · A dòng thời gian 4 · E ảnh tư liệu 4 · I hook dọc 3 · L 3D 3 · D số liệu 2 · C bảng 1.

## Giới hạn

Chấm theo tiêu đề, thẻ, prompt, mô tả; chưa xem video. Trước khi viết cảnh mới, mở video mẫu. Video và prompt thuộc người tạo:
chỉ mượn kỹ thuật, không chép thiết kế, không tải video về kho kênh, không cài skill `npx skills add` khi chưa đọc mã.

Nguồn ban đầu: phiên kênh Hình Sự lọc 52 mẫu (25/10/2026); bản này mở rộng ra đủ 234 mẫu và quy về engine của FS/BUD.
