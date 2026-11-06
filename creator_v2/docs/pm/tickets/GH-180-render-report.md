# Báo cáo Render 9 Short CK (Ticket GH-180)

- **Ngày thực hiện:** 06/11/2026
- **Ticket brief:** docs/pm/tickets/GH-180-render-agy.md
- **Kênh:** CK (Biểu Đồ Biết Nói)
- **Agent:** agy (Gemini 3.8 Flash High)
- **Quy tắc tuân thủ:** Không upload, không đặt/đổi lịch, không commit git, không can thiệp code dùng chung. Render tuần tự từng video (render lock).

---

## 1. Bảng tổng hợp 9 Short CK

| STT | Slug | File MP4 | Thời lượng | Ảnh QA (Contact Sheet & Frames) | Kết quả soát | Trạng thái |
|:---:|:---|:---|:---:|:---|:---|:---:|
| 1 | `ck-e5-thuong-tet-khau-tru` | `output/stier/ck-e5-thuong-tet-khau-tru/final.mp4` | 34.1s | `final_sheet.jpg`, `qa_t01.png` - `qa_t32.png` | Nhãn 'VÍ DỤ GIẢ ĐỊNH' rõ, chữ đúng dấu, số khớp lời | ĐẠT |
| 2 | `ck-e6-bon-trieu-tam-rut-mot-lan` | `output/stier/ck-e6-bon-trieu-tam-rut-mot-lan/final.mp4` | 25.8s | `final_sheet.jpg`, `qa_t01.png` - `qa_t24.png` | Số liệu BHXH thực tế, không có hypo, chữ đúng dấu | ĐẠT |
| 3 | `ck-a2-mot-nua-sau-muoi-sau-nam` | `output/stier/ck-a2-mot-nua-sau-muoi-sau-nam/final.mp4` | 29.7s | `final_sheet.jpg`, `qa_t01.png` - `qa_t28.png` | Nhãn 'VÍ DỤ GIẢ ĐỊNH' + dòng phụ 'PHÉP TÍNH, KHÔNG PHẢI DỰ BÁO' rõ | ĐẠT |
| 4 | `ck-e5-mot-dua-tre-mot-to-dang-ky` | `output/stier/ck-e5-mot-dua-tre-mot-to-dang-ky/final.mp4` | 33.2s | `final_sheet.jpg`, `qa_t01.png` - `qa_t32.png` | Nhãn 'VÍ DỤ GIẢ ĐỊNH' rõ, số 25 tr/15 tr khớp lời | ĐẠT |
| 5 | `ck-e6-tro-cap-540-nghin` | `output/stier/ck-e6-tro-cap-540-nghin/final.mp4` | 31.8s | `final_sheet.jpg`, `qa_t01.png` - `qa_t28.png` | Số liệu Nghị định 176/2025/NĐ-CP thực tế, không có hypo | ĐẠT |
| 6 | `ck-a2-thang-chin-nam-phay` | `output/stier/ck-a2-thang-chin-nam-phay/final.mp4` | 27.5s | `final_sheet.jpg`, `qa_t01.png` - `qa_t24.png` | Số liệu CPI Cục Thống kê thực tế, chữ đúng dấu | ĐẠT |
| 7 | `ck-dien-sinh-hoat-bac-mot-1901` | `output/stier/ck-dien-sinh-hoat-bac-mot-1901/final.mp4` | 27.7s | `final_sheet.jpg`, `qa_t01.png` - `qa_t24.png` | Số liệu giá điện 5 bậc từ 1/11 thực tế, chữ đúng dấu | ĐẠT |
| 8 | `ck-ho-kinh-doanh-duoi-mot-ty` | `output/stier/ck-ho-kinh-doanh-duoi-mot-ty/final.mp4` | 29.5s | `final_sheet.jpg`, `qa_t01.png` - `qa_t28.png` | Số liệu thuế hộ kinh doanh Nghị định 141/2026/NĐ-CP | ĐẠT |
| 9 | `ck-tran-tro-cap-that-nghiep-26-trieu` | `output/stier/ck-tran-tro-cap-that-nghiep-26-trieu/final.mp4` | 29.9s | `final_sheet.jpg`, `qa_t01.png` - `qa_t28.png` | Công thức trần 5 lần lương tối thiểu vùng 1 khớp chuẩn | ĐẠT |

---

## 2. Chi tiết kết quả kiểm tra chất lượng (QA)

### 2.1. Cổng tự động (Automation Gates)
- **Preflight:** Cả 9 spec đều đạt `OK` (số từ 103–132 từ, ước tính 31.2s–40.0s).
- **Script Lint (`PYTHONPATH=. python motion/stier/script_lint.py <slug>`):** Cả 9 spec đều đạt `0 lỗi` (chỉ có cảnh báo về cấu trúc hook/mệnh đề theo luật script, không có lỗi chặn).
- **Check Gate (`hyperframes check`):** 0 lỗi runtime, 0 lỗi layout, 0 lỗi lint asset cục bộ trên cả 9 bản dựng.
- **Audio Lint & Mix:**
  - Giọng đọc: Ngọc Huyền (chuẩn CK).
  - True Peak: Dao động từ -2.4 dBTP đến -2.1 dBTP (đều an toàn dưới ngưỡng chuẩn -1.5 dBTP).
  - Voice prominence: Âm lượng giọng nổi từ -24.2 dB đến -21.4 dB, nền nhạc ducking êm, không lấn át lời.
- **Freeze Gate & Blank Detection (`qa_blank.py`):**
  - Tất cả 9 video đạt `0 đoạn trống ≥ 1.0s`.
  - Không có hiện tượng đứng hình (freeze_gate kiểm tra và thông qua toàn bộ).
  - Contact sheet (`final_sheet.jpg`) và các khung ảnh QA (`qa_t*.png`) thay đổi liên tục và mượt mà giữa các cảnh.

### 2.2. Kiểm tra thị giác & nội dung (Visual & Content QA)
1. **Chữ và dấu tiếng Việt:** Toàn bộ chữ hiển thị trên thẻ 3D, chữ kinetic và phụ đề đều đúng dấu Unicode NFC, không có hiện tượng mất dấu hay biến thành dấu hỏi `?`.
2. **Nhãn 'VÍ DỤ GIẢ ĐỊNH':**
   - Các video có cảnh giả định (`ck-e5-thuong-tet-khau-tru`, `ck-a2-mot-nua-sau-muoi-sau-nam`, `ck-e5-mot-dua-tre-mot-to-dang-ky`) đều hiển thị nhãn `VÍ DỤ GIẢ ĐỊNH` chữ vàng, viền rõ nét, kích thước nổi bật (đọc rõ ở độ rộng 360px), nằm ngay ngắn dưới kicker/sub và tuyệt đối không đè tiêu đề.
   - Video `ck-a2-mot-nua-sau-muoi-sau-nam` có thêm dòng phụ `PHÉP TÍNH, KHÔNG PHẢI DỰ BÁO` rất rõ ràng.
   - Các video còn lại dẫn số liệu thực tế từ cơ quan quản lý (BHXH Việt Nam, Cục Thống kê, biểu giá điện Bộ Công Thương, Nghị định thuế, lương tối thiểu vùng) nên không gắn nhãn giả định và không bị sót chữ 'giả định' nhỏ nào.
3. **Phụ đề khớp giọng đọc:** Căn chỉnh từ (`hf_align`) bám sát từng từ đọc, từ nhấn được highlight vàng đúng thời điểm.
4. **Số trên hình khớp lời:**
   - Các con số lớn trên hình (50 triệu, 6,6 triệu, 4,84 triệu người, 4,52%, 540 nghìn, 5,08%, 1.901 đ, 1 tỷ, 26,55 triệu) đều khớp tuyệt đối với lời đọc và phụ đề.
5. **Thời lượng:** Tất cả 9 video đều nằm trong giới hạn chuẩn 25–40 giây (từ 25.8s đến 34.1s).
6. **Kiểm tra phát âm số và tên:**
   - Số được viết thành chữ tiếng Việt hoàn chỉnh trong kịch bản và đọc đầy đủ bằng giọng Ngọc Huyền ("bốn triệu tám trăm bốn mươi nghìn", "năm phẩy không tám phần trăm", "hai mươi sáu triệu năm trăm năm mươi nghìn đồng", v.v.), không nuốt chữ, ngắt nghỉ tự nhiên sau mỗi câu.

---

## 3. Kết luận

Toàn bộ 9 Short CK thuộc ticket GH-180 đã được dựng, render và kiểm duyệt hoàn tất đạt tiêu chuẩn chất lượng. File video và ảnh QA đã sẵn sàng tại `output/stier/` để Lead review.
