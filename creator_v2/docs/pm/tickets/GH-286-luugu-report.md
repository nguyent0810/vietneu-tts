# GH-286 — Báo cáo review Lưu Dung

## Kết quả

- Đã viết đủ `data/long/cl-luu-gu/story_review/ch00.md` đến `ch13.md`; mỗi file có 4–5 đoạn review kèm cách sửa cụ thể, toàn chương viết lại và mục Cần xác minh.
- Đã ghép `data/long/cl-luu-gu/script.v2.md`; đối chiếu bằng Python cho thấy phần đầu và mục Ghi chú kiểm chứng giống nguyên bản. `script.md` không bị ghi đè. Do yêu cầu giữ nguyên, con số độ dài dự kiến trong phần đầu và các ghi chú cuối vẫn mô tả bản 1, không phải kết quả đếm bản v2 dưới đây.
- Đã rút các đoạn giảng nguồn lặp, điều chỉnh nhịp câu, bỏ các suy đoán về động cơ, hành động và các chi tiết không có trong factcheck. Giữ phân biệt lệnh kê biên với việc thẩm vấn và soạn chiếu.

## Độ dài và cổng kiểm

Âm tiết theo cách đếm của `script_lines.py`, tức tách token theo khoảng trắng. Chênh lệch được tính so với bản gốc của từng chương.

| Chương | Bản cũ | Bản v2 | Chênh lệch |
|---|---:|---:|---:|
| CH00 | 148 | 162 | +9,46% |
| CH01 | 421 | 441 | +4,75% |
| CH02 | 460 | 487 | +5,87% |
| CH03 | 470 | 449 | −4,47% |
| CH04 | 459 | 424 | −7,63% |
| CH05 | 430 | 425 | −1,16% |
| CH06 | 435 | 439 | +0,92% |
| CH07 | 440 | 466 | +5,91% |
| CH08 | 414 | 429 | +3,62% |
| CH09 | 442 | 406 | −8,14% |
| CH10 | 423 | 438 | +3,55% |
| CH11 | 428 | 386 | −9,81% |
| CH12 | 428 | 420 | −1,87% |
| CH13 | 417 | 441 | +5,76% |
| **Tổng** | **5.815** | **5.813** | **−0,03%** |

- `python motion/long/script_lines.py cl-luu-gu`: thoát 0; 8 cảnh báo NHIP_DEU, 1 RAO_NGUON, tổng 9; không có lỗi chặn. Số thực chạy khác con số 5 trong brief.
- Chép bản v2 bằng Python UTF-8 vào `data/long/cl-luu-gu/story_review/gh286_tmp/script.md`, rồi chạy `python motion/long/script_lines.py cl-luu-gu/story_review/gh286_tmp`: thoát 0, không có lỗi gate, 0 NHIP_DEU, 0 RAO_NGUON và không có cảnh báo khác. Tổng 5.813 nằm trong khoảng 5.800–6.600; cả 14 chương nằm trong ±10% bản cũ. Thư mục tạm được giữ trong topic để có thể chạy lại.
- Đã kiểm 14 file review, 4–5 mục sửa mỗi chương, phần đầu và ghi chú giữ nguyên. Kiểm ký tự thay thế Unicode và rà dấu hỏi: không thấy ký tự thay thế; dấu `?` xuất hiện ở câu hỏi hoặc trích ghi chú gốc, không phải chữ tiếng Việt bị hỏng.
- Không gọi mạng, không render, không commit, không đăng, không đổi lịch. Không có clip sheet hay thumbnail mới vì ticket chỉ yêu cầu review kịch bản, không dựng video.

## Cần xác minh — gộp từ các chương

- Lệnh kê biên ngày 12/2/1799 có tên Lưu Dung dựa trên ghi chép khuyết danh thứ cấp; chưa đối chiếu được Thanh thực lục. Không có căn cứ từ các nguồn đã dùng để xác nhận ông trực tiếp thực hiện phần nào, thẩm vấn hay soạn chiếu hai mươi tội.
- Đông Hoa lục về vụ thơ Từ Thuật Quỳ mới được tiếp cận qua bản trích lại. Cần đối chiếu bản gốc câu trích, trình tự và kết cục vụ án trước khi duyệt lời đọc.
- Năm sinh Hòa Thân, khoảng cách tuổi, năm và địa danh tri phủ Thái Nguyên, năm bổ nhiệm Tuần phủ Hồ Nam và Tả đô ngự sử, năm giữ chức Thượng thư Bộ Lại đều dựa ít nhất một phần vào nguồn thứ cấp. Thời gian ở quân đài được kể theo nghĩa hơn một năm.
- Năm mất và tuổi Lưu Thống Huân theo nguồn thứ cấp; tháng Mười một âm lịch cuối năm có thể rơi sang đầu năm dương lịch sau. Ngày cụ thể giam và phóng thích năm 1755 chưa rõ.
- Diễn tiến kiểm kho Sơn Đông và hành động cụ thể của từng người cần đối chiếu nguyên văn trước khi duyệt; không suy ra lời hay hành động của Lưu Dung. Câu sử về vụ giáng năm 1789 không xác định riêng ông đã vắng mặt hay thời gian vắng.
- Nguồn gốc biệt danh và chuyện Gia Khánh gọi Lưu Đà Tử chỉ là giai thoại qua nguồn thứ cấp không dẫn sử gốc. Ngày dương lịch và địa điểm mất của Lưu Dung, biệt hiệu Nồng mặc tể tướng và lời Từ Kha khen thư pháp cũng dựa nguồn thứ cấp hoặc bản trích; cần đối chiếu nguồn gốc nếu giữ.
- Câu Gia Khánh lên ngôi năm 1796 đã bỏ vì factcheck chưa có dòng riêng. Giữ nguyên mục Ghi chú kiểm chứng cuối bản 1 theo yêu cầu ticket nên ghi chú đó vẫn nhắc câu đã bỏ; Lead cần biết khi duyệt.

- Hai l??t ki?m ph? ban ??u th?t b?i do c?ch escape xu?ng d?ng trong l?nh Python v? wildcard ???ng d?n c?a `rg` tr?n Windows; ?? ch?y l?i v?i c?ch t?ch d?ng v? `rg -g` ??ng, c? hai ??u th?nh c?ng. B??c ki?m l?i x?c nh?n n?i dung 14 b?n vi?t l?i kh?p t?ng ch??ng trong v2.
