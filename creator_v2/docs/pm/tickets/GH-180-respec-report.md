# GH-180 vòng 2 — báo cáo lắp lại cảnh

## Trạng thái: chưa hoàn tất

Đã sửa phần cảnh của chín spec, giữ nguyên các trường khác, bao gồm lời đọc và lịch trong spec. Mỗi bài hiện có năm loại cảnh trong bảng README và có bảng so sánh `ledger`; đã bỏ footage lặp, không dùng ảnh hay clip ở cả chín bài. Các cảnh giả định tiếp tục giữ `hypo` và nhãn bổ sung vốn có. Các số chính được đưa vào counter hoặc slam tại nhiều cảnh, nhưng một số giá trị so sánh chỉ nằm trong ledger và chưa kiểm tra được độ lớn thực tế trên màn hình.

Không thể cho cả chín qua preflight trong phạm vi quy định: preflight đòi ảnh/video cộng đồng và cảnh sơ đồ (`board`, `cards3d` hoặc `map`). Luật repo chỉ cho dùng loại trong bảng 19 loại ở README và yêu cầu dừng khi cần loại ngoài bảng. `board` và `cards3d` không có trong bảng, còn `map` không thích hợp cho các phép tính này. Mẫu ticket dùng `cards3d` và `chart`, cả hai cũng không có trong bảng. Cần Lead làm rõ bảng loại cảnh hợp lệ và cách đáp ứng yêu cầu phối cảnh; sau đó cần chọn chín hình/clip khác nhau, kiểm thực tế và chạy lại preflight. Không sửa engine hay vô hiệu hóa cổng.

## Loại cảnh và ảnh

Mỗi dòng ghi tập loại cảnh trước → sau; thứ tự theo lần xuất hiện đầu. Tất cả đều không dùng ảnh hay clip sau sửa; trước đó cùng dùng `pexels:7710775` ở nhiều cảnh.

- `ck-e5-thuong-tet-khau-tru`: kinetic, cards3d, counter, board → kinetic, ledger, counter, slam, timeline.
- `ck-e6-bon-trieu-tam-rut-mot-lan`: kinetic, cards3d, board, counter → kinetic, counter, slam, timeline, ledger.
- `ck-a2-mot-nua-sau-muoi-sau-nam`: kinetic, cards3d, counter, board → kinetic, counter, ledger, slam, timeline.
- `ck-e5-mot-dua-tre-mot-to-dang-ky`: kinetic, cards3d, counter, board → kinetic, slam, ledger, counter, timeline.
- `ck-e6-tro-cap-540-nghin`: kinetic, cards3d, counter, board → kinetic, counter, ledger, slam, timeline.
- `ck-a2-thang-chin-nam-phay`: kinetic, cards3d, counter, board → kinetic, counter, slam, timeline, ledger.
- `ck-dien-sinh-hoat-bac-mot-1901`: kinetic, cards3d, counter, board → kinetic, ledger, counter, slam, timeline.
- `ck-ho-kinh-doanh-duoi-mot-ty`: kinetic, cards3d, counter → kinetic, slam, counter, timeline, ledger.
- `ck-tran-tro-cap-that-nghiep-26-trieu`: kinetic, cards3d, counter, board → kinetic, slam, counter, ledger, timeline.

## Kiểm tra

- `python motion/stier/build.py --preflight <slug>` chạy cho cả chín: cả chín exit 1, chưa đạt phối cảnh. Ngoài hai lỗi chung nêu trên, một số bài còn vượt tỷ lệ cảnh cùng nhóm hoặc cảnh chữ, hoặc có ba cảnh cùng nhóm liên tiếp. Preflight dừng ở phối cảnh nên chưa xác nhận các cổng tiếp theo. Báo cáo vòng trước đã ghi hai bài con đăng ký và trợ cấp 540 nghìn vượt giới hạn lời/thời lượng; giữ nguyên lời nên vấn đề đó vẫn cần Lead quyết định.
- `PYTHONPATH=. python motion/stier/script_lint.py <slug>` chạy cả chín: 0 lỗi mỗi bài; số cảnh báo theo thứ tự danh sách trên: 5, 6, 5, 7, 9, 4, 4, 12, 8. Cảnh báo chủ yếu thiếu móc, câu cuối không hỏi và câu dài; bài hộ kinh doanh có cảnh báo nhận nhầm trích kinh. Không sửa lời theo brief.
- Chạy đúng lệnh kiểm mất dấu của ticket trước: exit 1 do bốn file cũ ngoài phạm vi `bud-bd-3-chu-khi-nghi-nhieu-v3.json` (tên chính xác bên dưới), `bud-bd-4-kieu-ban-that-v3.json`, `bud-kg-ke-5-han-thu-v3.json`, `mim-watson-toronto.json`. Không có spec GH-180 trong kết quả.
- Đối chiếu lời với file lời nguồn: bảy bài khớp, hai bài đã khác file lời trước lượt sửa này: bài con đăng ký khác câu 1 và 4, bài trợ cấp 540 nghìn khác câu 5. Lượt này chỉ thay `scenes`, không đổi `lines`; cần Lead xác nhận phiên bản lời hiện tại.
- Không mở lại URL nguồn trong vòng sửa hình; chưa xác minh độc lập các khẳng định, tiếp tục kế thừa nguồn và các điểm cần kiểm từ báo cáo trước.
- Không render theo ticket; không có clip sheet mới, ảnh QA hay thumbnail mới. Chưa thể xác nhận nhãn giả định đọc rõ ở 360 px hoặc cảnh chuyển động. Không đăng, commit, sửa lịch hay ghi state.

Cần Lead xác nhận loại cảnh được phép và hướng xử lý cổng, rồi tiếp tục chọn media, làm lại phối cảnh và kiểm lại.
