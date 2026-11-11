# GH-276 vòng 3 — báo cáo sản xuất

## Đã thực hiện

- `receipt`: tăng bề rộng từ 700 lên 980 px, tăng cỡ chữ và khoảng đệm dòng, line-height 1,5, màu chữ #222; giữ dòng tổng có viền đôi. Dữ liệu demo có cả “KHOẢN MẪU”, “TỔNG” và chuỗi dấu khó.
- `polaroid` dùng Itim; `telegram`, `receipt`, `index_card`, `terminal` dùng IBM Plex Mono. Đã thêm hai họ vào URL Google Fonts của Long và demo; bỏ Comic Sans MS và Courier New khỏi KIN_FONTS.
- `museum_label` luôn in “HIỆN VẬT” thay vì để khóa kỹ thuật lọt ra đầu nhãn. `news_clip` dùng chiều cao tự theo nội dung thay vì cố định 740 px. Các kiểu `lower_third`, `callout`, `edict_scroll` giữ hướng vòng 2; thêm nhãn ĐỒ HỌA cho `edict_scroll` theo brief.
- `idcards_demo.py` có 20 kiểu × 6 giây, 12 kiểu mới trước, tám kiểu vòng 2 sau; bốn kiểu yêu cầu có chuỗi “Nguyễn Thị Ngọc Ẩn, Huỳnh Hữu Khoảng, Ỷ Lại, ỨNG ĐẪN”. `clip_file` giữ nguyên và không tính vào 20 mẫu này.

## Mười hai kiểu mới

- `index_card`: thẻ kẻ dòng, viền đỏ và lỗ dưới; trượt lên, dòng hiện theo thời điểm.
- `fingerprint`: vùng thông tin và năm ô vân tay SVG; ô lần lượt in, sau đó thông tin hiện.
- `passport`: giấy thông hành có hoa văn SVG, ảnh hoặc ô “ẢNH”, dấu ngày; trang lật và dấu đóng.
- `verdict`: tiêu đề tòa căn giữa, nội dung và dấu chữ nhật “ĐÃ TUYÊN”; giấy hiện, dòng hiện và dấu dập rung.
- `wanted`: poster đóng khung, ô ảnh, tên và khoản thưởng khi có; bốn đinh rơi vào bốn góc.
- `envelope`: phong thư, nắp tam giác và dấu sáp SVG; nắp mở, thư rút lên, dòng hiện.
- `seal_slip`: bốn thanh tre chữ dọc, triện vuông; thanh trải ra rồi triện đóng.
- `case_divider`: bìa có số hoặc mã vụ lớn, tab và tên; bìa lật, tab trượt.
- `terminal`: cửa sổ nền tối, dấu nhắc, từng ký tự hiện theo thời điểm và con trỏ nháy.
- `spec_sheet`: bản vẽ nền xanh có lưới, đường kích thước SVG và bảng; lưới hiện, nét được vẽ, bảng hiện.
- `app_card`: khung điện thoại, thông tin lớn và bong bóng giao dịch; máy trượt lên, các dòng bật vào.
- `slate`: clapperboard sọc, hai cột PHIM và ĐỜI THẬT; thanh kẹp đập xuống, cột hiện.

Chín kiểu tài liệu theo brief có nhãn ĐỒ HỌA. Các nhánh được kiểm tra với trường tùy chọn bị thiếu; test CSS kiểm tra line-height của khai báo font các lớp thẻ.

## Mượn ảnh và Mata Hari

Bộ chọn theo dõi ảnh đã khai trong `spec.imgs` theo từng chương, lấy ảnh gần nhất trước thẻ, hỗ trợ `img`, `bg` và hai ảnh `split`; `print` và `pano` dùng `img`. Chỉ khi chọn kiểu bắt buộc ảnh mới ghi ảnh mượn vào `img` và đánh dấu `img_borrowed: true`. Không mượn khóa ngoài spec, nguồn AI hoặc ảnh phim; ảnh không vượt ranh giới chương. Style khai tay vẫn được giữ. Đã thử trên bản sao trong bộ nhớ của `data/long/mata-hari`; không sửa dữ liệu bài.

31 thẻ, 9 kiểu, 12 thẻ mượn ảnh; kiểu lớn nhất 4/31 = 12,9%, không có kiểu nào lặp trong sáu thẻ trước:

| Kiểu | Số thẻ |
|---|---:|
| case_divider | 4 |
| envelope | 4 |
| index_card | 4 |
| museum_label | 4 |
| callout | 3 |
| lower_third | 3 |
| slate | 3 |
| polaroid | 3 |
| clip_file | 3 |

Cổng sàn vẫn báo 9 cặp thẻ không cách đủ bốn cảnh: 4–8, 62–63, 110–113, 150–153, 175–179, 179–180, 180–184, 194–196 và 263–267. Đây là vị trí có sẵn trong dữ liệu, bộ chọn không tự chuyển hoặc xóa cảnh.

## Kiểm tra và giới hạn

- `node --check motion/hf/assets/engine/casewide.js`: đạt.
- Python môi trường ticket, `-m pytest tests/test_idcards.py tests/test_long_floor.py tests/test_long_defaults.py tests/test_cine_auto.py --basetemp=tmp_pytest -p no:cacheprovider`: 32 đạt, 1 lỗi setup do Windows từ chối quyền dọn `tmp_pytest`.
- Chạy lại đủ bốn tệp bằng cùng Python và `-p no:cacheprovider`, `--basetemp=tmp_pytest_gh276r5`, trong tiến trình đổi mode tạo thư mục từ 0700 sang 0777 để tránh lỗi ACL Windows: **33/33 đạt**. Lần thử `tmp_pytest_gh276r3` không điều chỉnh mode cũng gặp lỗi quyền.
- Không render theo brief, do đó chưa có clip sheet hoặc thumbnail và chưa kiểm được hình thật, dấu tiếng Việt trên khung hay nhịp chuyển động bằng mắt. Lead chạy `python motion/long/idcards_demo.py` bằng Python môi trường ticket để tạo composition rồi render và xem 20 mẫu.
- Không có khẳng định tư liệu mới cần factcheck; chữ và khoản thưởng trong demo là dữ liệu mẫu.
- Không đăng, commit hay thay đổi lịch.
