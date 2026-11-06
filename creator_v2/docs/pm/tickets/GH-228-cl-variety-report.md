# GH-228 — báo cáo đổi nhịp hình CL

Đã sửa 12 spec được liệt kê trong báo cáo shorts1, giữ nguyên `lines` và thông tin lịch. 12 chuỗi loại cảnh và 12 cụm slam khác nhau; không còn slam “DẤU VẾT”. Mở bài phân bố: photo 3, quote 3, date 2, file 2, ledger 2. Quote ở đây là nguyên câu lời dẫn của chính bài, có ghi “LỜI DẪN”, không gán là phát ngôn lịch sử. Mốc đơn trên nền trống đã được thay; có timeline hai mốc và split hai ảnh. Không đưa map vào vì không có cấu hình địa lý được kiểm trong các spec ban đầu.

| Slug | Chuỗi loại cảnh | Slam | Preflight |
|---|---|---|---|
| cl-bao-luoi-bo | photo → file → split → slam → photo → ledger | LƯỠI BÒ BỊ CẮT | OK |
| cl-frank-grigware-van-tay | file → date → photo → doc → slam → split → photo | DẤU TAY TRÙNG | OK |
| cl-bao-nghien-muc | ledger → photo → file → split → slam → photo | NGHIÊN MỰC | OK |
| cl-black-dahlia-56-phut | date → photo → doc → file → slam → split → photo | MỘT CÁI TÊN | OK |
| cl-bao-cong-phu | quote → photo → split → slam → file → photo | MỞ CỔNG CHÍNH | OK |
| cl-ross-tien-chuoc | photo → date → file → doc → slam → split → photo | TIỀN CHUỘC | OK |
| cl-hoa-than-hai-muoi-toi | ledger → date → photo → split → slam → file | HAI MƯƠI TỘI | OK |
| cl-alger-hiss-khai-man | file → photo → date → doc → split → slam → photo | HAI LẦN KHAI MAN | OK |
| cl-hoa-than-doi-ten-phu | date → photo → timeline → split → slam → file | ĐỔI TÊN | OK |
| cl-diane-jackson-van-tay | quote → date → photo → doc → split → slam → photo | DẤU TAY CŨ | OK |
| cl-hoa-than-thi-ve | photo → date → split → file → slam → photo | MỘT THỊ VỆ | OK |
| cl-james-ricks-ban-tu | quote → file → photo → date → split → slam → doc | MỘT BẠN TÙ | OK |

## Kiểm tra

- `python motion/stier/build.py --preflight <slug>` chạy lần cuối cho từng slug: 12/12 OK, ước tính 26,1–32,4 giây. Vòng đầu phát hiện `split.a/b` phải là đối tượng, đã sửa và chạy lại.
- `PYTHONPATH=. python motion/stier/script_lint.py <slug>`: 12/12 không lỗi cứng, còn 56 cảnh báo R2, R4, R5, R6, R7, R10 như báo cáo shorts1; giữ lời đọc theo brief. R10 ở bài lưỡi bò là cảnh báo nhận nhầm đã ghi trong báo cáo trước.
- Kiểm Python UTF-8 với từng JSON: 12 chuỗi cảnh và 12 slam duy nhất; mỗi spec tham chiếu bốn khóa ảnh khác nhau trong cảnh. Kiểm dấu hỏng `?` và ký tự thay thế U+FFFD trong các trường cảnh: không thấy sau khi sửa. Lần ghi ban đầu qua pipe PowerShell đã làm hỏng dấu ở các trường cảnh mới; đã khôi phục và kiểm lại. Dấu hỏi đúng nghĩa trong tiêu đề/mô tả được giữ nguyên.
- Chưa render theo brief, nên không có clip sheet hoặc thumbnail mới. Không thể xác nhận hình, độ đọc được của nhãn, split, nền date, hoặc nhịp chuyển động thực tế bằng preflight; cần dựng và soi sheet ở bước sản xuất tiếp theo.

## Ảnh và giới hạn kiểm chứng

Sáu spec S ban đầu chỉ có một ảnh, vì vậy bổ sung ba ảnh tư liệu công cộng vào từng spec: [phòng thí nghiệm FBI khoảng 1940](https://commons.wikimedia.org/wiki/File:Fbi-lab-1940.jpg), [tòa phòng thí nghiệm FBI năm 2003](https://commons.wikimedia.org/wiki/File:FBI_Laboratory_(2003).jpg), [nhân viên đơn vị nhận dạng cảnh sát công viên Mỹ](https://commons.wikimedia.org/wiki/File:USPP-Identification_Unit-officer.jpg). Trang Commons ghi là tác phẩm cơ quan liên bang thuộc phạm vi công cộng tại Mỹ. Đây là tư liệu bối cảnh, không phải ảnh vụ án; các cảnh có nhãn mô tả nguồn, thời điểm hoặc đơn vị. Chúng được dùng lại giữa các bài và cần Lead duyệt tính phù hợp, đặc biệt khi ảnh 2003 hoặc ảnh cảnh sát công viên xuất hiện cạnh vụ cũ. Preflight không tải ảnh, chưa kiểm ảnh thực tế hoặc xác nhận khả năng tải bằng builder. Hai ảnh trong split và ảnh nền date cần soi nhãn trên khung sau dựng; không coi preflight là bằng chứng chúng hiển thị đúng.

Không thêm dữ kiện lời đọc; chưa kiểm lại độc lập các dữ kiện cũ. Những điểm chưa kiểm và cần duyệt trong `GH-228-cl-shorts1-report.md` vẫn tồn tại, gồm mâu thuẫn nguồn FBI vụ Ross, ảnh tư liệu phương pháp, đọc thử TTS và nguồn hai Long còn thiếu. Không render, đăng, commit hoặc đổi lịch.
