# GH-228 — báo cáo sản xuất

**Chưa hoàn tất.** Đã viết 12/14 spec: 6 L (3 Bao Chửng, 3 Hòa Thân) và 6 S. Hai bài L nối Khun Sa và Đỗ Nguyệt Sanh chưa viết vì brief yêu cầu chi tiết đã có trong cả script lẫn `factcheck.md` của Long, nhưng `data/long/golden/factcheck.md` và `data/long/shanghai/factcheck.md` không tồn tại. Hai slot 15/11 còn trống. Đề nghị Lead cung cấp hoặc xác định file kiểm chứng tương ứng; chưa thể coi lô đủ điều kiện bàn giao.

| Slug | Loại | Giờ VN | publish_at UTC | Số từ | Preflight |
|---|---|---|---|---:|---|
| cl-bao-luoi-bo | L | 09/11 12:00 | 2026-11-09T05:00:00Z | 86 | OK, 26,1s |
| cl-frank-grigware-van-tay | S | 09/11 19:00 | 2026-11-09T12:00:00Z | 92 | OK, 27,9s |
| cl-bao-nghien-muc | L | 10/11 12:00 | 2026-11-10T05:00:00Z | 99 | OK, 30,0s |
| cl-black-dahlia-56-phut | S | 10/11 19:00 | 2026-11-10T12:00:00Z | 96 | OK, 29,1s |
| cl-bao-cong-phu | L | 11/11 12:00 | 2026-11-11T05:00:00Z | 91 | OK, 27,6s |
| cl-ross-tien-chuoc | S | 11/11 19:00 | 2026-11-11T12:00:00Z | 95 | OK, 28,8s |
| cl-hoa-than-hai-muoi-toi | L | 12/11 12:00 | 2026-11-12T05:00:00Z | 97 | OK, 29,4s |
| cl-alger-hiss-khai-man | S | 12/11 19:00 | 2026-11-12T12:00:00Z | 89 | OK, 27,0s |
| cl-hoa-than-doi-ten-phu | L | 13/11 12:00 | 2026-11-13T05:00:00Z | 89 | OK, 27,0s |
| cl-diane-jackson-van-tay | S | 13/11 19:00 | 2026-11-13T12:00:00Z | 103 | OK, 31,2s |
| cl-hoa-than-thi-ve | L | 14/11 12:00 | 2026-11-14T05:00:00Z | 89 | OK, 27,0s |
| cl-james-ricks-ban-tu | S | 14/11 19:00 | 2026-11-14T12:00:00Z | 107 | OK, 32,4s |

Thời lượng trên là ước tính của preflight, chưa đo bằng giọng dựng. Các mốc `publish_at` chỉ nằm trong spec; chưa đổi lịch thật. Truy vấn `state.sqlite` mở `mode=ro`: không thấy item CL khác `failed` trong khoảng 09–15/11. Ba Short Hòa Thân đặt trước ngày Long dự kiến 15/11 theo ô xen kẽ, do đó liên kết video liên quan cần gắn sau khi video dài tồn tại; `long_target` cho Hòa Thân mới là định danh dự kiến, chưa xác nhận có item trong sổ.

## Lệnh và cổng kiểm

- Đọc brief, README S-tier, skill shorts-studio, §7 tài liệu phân tích, nguồn hình, script và factcheck Long Bao Chửng / Hòa Thân; đọc spec Unabomber và 4 spec mới nhất có sheet. Bốn sheet mới nhất tìm được thuộc CK, không phải CL; đã mở xem, chưa có 3–4 sheet CL mới nhất được xác nhận theo brief.
- Tìm trùng bằng `rg` trong `data/stier/specs`: đã loại Gardner và các chủ đề trùng tìm thấy; sáu chủ đề S chọn không thấy chuỗi tên tương ứng. `data/channel_titles/CL.json` không tồn tại, nên chưa đối chiếu danh mục tiêu đề ngoài kho spec.
- Ghi spec bằng Python UTF-8, `json.dumps(..., ensure_ascii=False)`; ghi lời và nguồn trong `GH-228-cl-shorts1-lines.md`; dữ kiện trong `GH-228/factcheck.md`.
- `python motion/stier/build.py --preflight <12 slug>`: 12/12 OK; sau sửa hook Black Dahlia chạy lại riêng, OK 96 từ. Mỗi spec có 6 loại cảnh hợp lệ. Preflight không chứng minh hình hiển thị hoặc tư liệu tải được.
- `PYTHONPATH=. python motion/stier/script_lint.py <slug>`: 0 lỗi cứng trên 12; còn 56 cảnh báo: R2 thiếu nhịp móc giữa, R4 callback, R5 câu cuối không hỏi, R6 câu dài, R7 viết tắt FBI, R10 nhận nhầm trích kinh ở bài lưỡi bò. R5 giữ câu chốt theo §7 (không kết bằng câu hỏi); bốn spec có `say` cho FBI nhưng chưa nghe TTS. Cần sửa/duyệt nhịp và đọc thử trước khi dựng.
- `npx hyperframes usage --json`: thất bại EPERM khi ghi npm cache ngoài vùng ghi; usage không xác định. Không chạy render, không tạo sheet mới, không enqueue, không upload, không commit, không đổi lịch.

## Nguồn, hình và việc cần Lead duyệt

- `golden` và `shanghai` có script nhưng thiếu `factcheck.md` theo đúng yêu cầu brief; chưa kết luận chi tiết nào của hai Long đó đã kiểm được theo cổng brief.
- Nguồn FBI vụ Ross có chỗ tự mâu thuẫn: đoạn đầu ghi nhầm tên người bị bắt là Ross, đoạn thân xác định Seadlund; lời không nêu ngày bắt vì trong cùng trang có hai ngày khác nhau. Cần Lead xem lại đối chiếu độc lập trước khi duyệt.
- Bốn spec S Grigware, Ross, Diane Jackson, James Ricks dùng chung ảnh bộ lấy dấu FBI năm 2016 làm tư liệu phương pháp, không phải tang vật vụ án; đã ghi nhãn trong spec. Cần duyệt tính phù hợp và thay ảnh riêng nếu cần. Toàn bộ 12 spec đang cùng chuỗi kiểu cảnh; cần thay đổi nhịp hình để tránh rập khuôn. Ảnh Bao / Hòa Thân là tranh lịch sử PD lấy tên từ research Long; ảnh Elizabeth Short và Hiss từ Commons PD. Chưa tải, kiểm bản cụ thể bằng mắt hay xác nhận tải/giấy phép qua builder; cần làm trước sản xuất.
- Chưa đọc to, nghe giọng, render, kiểm chuyển động hay soi ảnh thật. Không có clip sheet hoặc thumbnail mới để giao; ticket cấm render. Bốn sheet CK tham khảo ở `output/stier/ck-tran-tro-cap-that-nghiep-26-trieu/final_sheet.jpg`, `output/stier/ck-ho-kinh-doanh-duoi-mot-ty/final_sheet.jpg`, `output/stier/ck-dien-sinh-hoat-bac-mot-1901/final_sheet.jpg`, `output/stier/ck-a2-thang-chin-nam-phay/final_sheet.jpg`.
