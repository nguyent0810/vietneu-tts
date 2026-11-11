# GH-276 vòng 3: sửa 8 kiểu vòng 2, làm 12 kiểu còn lại, cho mượn ảnh trong chương (Codex)

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-idcards`, nhánh `feat/276-idcards`. Lead đã rebase lên main (ef2bb39) và commit bản vòng 2 thành `525de89`. Đường dẫn tính từ `creator_v2/`.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- Pytest: `--basetemp=tmp_pytest -p no:cacheprovider`. Bộ gốc có 7 test đỏ do thiếu `vnlunar`, bỏ qua. Gặp lỗi quyền khi dọn thư mục tạm thì ghi lại và **làm tiếp, không dừng**.
- File được sửa: như vòng 2 (`casewide.js`, `casewide.css`, `idcards.py`, `idcards_demo.py`, `scene_params.py`, `lint_html.py`, `tests/test_idcards.py`, `motion/long/README.md`), thêm `motion/variety.py` (chỉ hàm `fonts_url`, để thêm họ font) và `motion/long/build_long.py` (chỉ chỗ ghép URL font, nếu cần).

## Lead đã render và xem vòng 2
Đạt: 8 bố cục khác nhau thật, chuyển động vào đúng ý. Giữ nguyên hướng. Cần sửa:
1. **`receipt` mất dấu:** dòng khoản mục "KHOẢN MẪU" hiện thành "KHOAN MAU". Dòng `TỔNG` thì đúng. Sửa line-height và padding của `.id2-receipt-row` và mọi chữ HOA cỡ nhỏ. Hóa đơn quá nhỏ và chữ xám quá nhạt: phóng to khoảng 1,4 lần, chữ khoản mục màu đậm (#333 trở lên).
2. **Font hệ thống:** bỏ `Comic Sans MS` và `Courier New`. Hai font này chỉ có trên Windows và Comic Sans trông rẻ.
   - Chú thích viết tay (`polaroid`): **Itim** từ Google Fonts (có subset vietnamese).
   - Máy đánh chữ (`telegram`, `receipt`, `index_card`, `terminal`): **IBM Plex Mono** từ Google Fonts (có subset vietnamese).
   - Thêm hai họ này vào URL Google Fonts mà composition Long nạp (`variety.fonts_url` hoặc chỗ ghép trong `build_long.py`), và vào `idcards_demo.py`.
   - Xóa hai dòng `Comic Sans MS` và `Courier New` khỏi `KIN_FONTS` (`KIN_FONTS` chỉ dùng để đo chữ kinetic).
3. **`museum_label` lộ chữ kỹ thuật "museum_label"** ở đầu nhãn. Thay bằng "HIỆN VẬT", hoặc bỏ dòng đó.
4. **`news_clip`:** nửa dưới mẩu báo trống. Thu chiều cao mẩu báo theo nội dung, hoặc cho cột chữ lấp đủ.

## Mượn ảnh trong chương (đổi luật bộ chọn)
Mata Hari chỉ có 1/31 cảnh thẻ có `img`, nên 4 kiểu cần ảnh gần như không bao giờ được chọn.
- Luật mới: kiểu cần ảnh được chọn khi cảnh có `img`, **hoặc** khi trong cùng chương có cảnh trước đó dùng ảnh (`img`, `bg`, cảnh `print`/`split`/`pano`, tùy khóa thật trong spec của chương). Lấy ảnh **gần nhất trước** cảnh thẻ.
- `assign()` ghi ảnh mượn vào cảnh dưới khóa `img`, kèm `img_borrowed: true`, để Lead thấy.
- Không có ảnh để mượn thì không chọn kiểu đó.
- Chỉ dùng ảnh mà spec đã khai báo. Không tải ảnh, không dùng ảnh AI.
- Chạy lại trên bản sao Mata Hari (chỉ đọc). Báo cáo phân bố và số cảnh mượn ảnh. Mục tiêu ≥ 8 kiểu, không kiểu nào > 25% số thẻ, không lặp trong 6 thẻ liên tiếp. Nếu vẫn không đạt thì ghi rõ do đâu.

## 12 kiểu còn lại
Cùng chuẩn vòng 2: **bố cục DOM riêng + chuyển động vào riêng**, không chỉ đổi màu.

| style | Bố cục | Chuyển động vào |
|---|---|---|
| `index_card` | Thẻ thư mục kẻ dòng xanh, đường đỏ trên cùng, lỗ đục ở mép dưới, chữ máy đánh chữ | Thẻ trượt lên từ ngăn kéo, chữ hiện từng dòng |
| `fingerprint` | Thẻ chỉ bản cảnh sát: lưới 5 ô vân tay vẽ bằng SVG (đường cong đồng tâm, không phải ảnh), ô thông tin bên trên | Ô vân tay in dần từng ô, rồi thông tin hiện |
| `passport` | Trang giấy thông hành cũ, hoa văn guilloche SVG, ô ảnh (dùng `img` nếu có, không có thì ô trống ghi "ẢNH"), dấu xuất nhập cảnh tròn hoặc chữ nhật có chữ và ngày | Trang lật mở, dấu đóng xuống lệch góc |
| `verdict` | Bản án: tiêu đề tòa căn giữa, đường kẻ, các dòng tội danh, dấu đỏ hình chữ nhật chữ "ĐÃ TUYÊN" | Giấy hiện, dòng chạy, dấu dập xuống có rung |
| `wanted` | Poster truy nã: khung gỗ hoặc giấy dán tường, chữ "TRUY NÃ" to kiểu slab, ô ảnh, tên, tiền thưởng | Poster đóng đinh vào (đinh rơi xuống 4 góc) |
| `envelope` | Phong thư nhìn chính diện, nắp tam giác, con dấu sáp đỏ SVG (khác hẳn vòng tròn đỏ của `verdict`) | Nắp mở, thư rút lên, các dòng hiện |
| `seal_slip` | Thẻ tre dọc 3–5 thanh ghép, chữ dọc (`writing-mode: vertical-rl`), triện son vuông | Các thanh tre trải ra, triện đóng xuống |
| `case_divider` | Bìa phân trang: số vụ stencil rất to, tab màu nhô ở cạnh, tên vụ | Bìa lật sang, tab trượt ra |
| `terminal` | Cửa sổ dòng lệnh nền tối, chữ xanh hoặc hổ phách, con trỏ nháy, dấu nhắc `>` | Từng ký tự gõ theo `at`, con trỏ nháy |
| `spec_sheet` | Bản vẽ blueprint nền xanh, lưới mảnh, đường kích thước có mũi tên, bảng thông số góc phải dưới | Lưới hiện, đường kích thước vẽ dần (SVG stroke), bảng hiện |
| `app_card` | Thẻ app điện thoại: khung máy bo góc, số dư lớn, dòng giao dịch, hoặc bong bóng chat trái phải | Khung trượt lên, từng dòng hoặc bong bóng bật vào |
| `slate` | Clapperboard đen trắng sọc, hai cột "PHIM" và "ĐỜI THẬT" | Thanh kẹp đập xuống, hai cột hiện |

Riêng `clip_file` (thẻ kẹp ghim cũ) giữ nguyên.

## Luật chung (như vòng 2)
- Dấu tiếng Việt không bị cắt ở mọi cỡ chữ, cả chữ HOA. Thêm test đọc CSS: mọi lớp chữ của các kiểu idcard có `line-height ≥ 1.2`. Tránh `overflow:hidden` sát chữ.
- Nhãn "ĐỒ HỌA" kín đáo ở góc chỉ cho kiểu dạng tài liệu (`news_clip`, `telegram`, `verdict`, `wanted`, `passport`, `fingerprint`, `envelope`, `edict_scroll`, `seal_slip`).
- Không ném lỗi khi thiếu trường tùy chọn. Lỗi trang làm video đứng hình (#284).
- `idcards_demo.py`: đủ 20 kiểu, mỗi kiểu 6 giây. Thứ tự: 12 kiểu mới, rồi 8 kiểu vòng 2 (đã sửa). Thêm một trang chữ nhỏ có dấu khó ("Nguyễn Thị Ngọc Ẩn, Huỳnh Hữu Khoảng, Ỷ Lại, ỨNG ĐẪN") vào ít nhất `receipt`, `telegram`, `index_card` và `terminal`.

## Kiểm
- `node --check motion/hf/assets/engine/casewide.js`.
- `pytest tests/test_idcards.py tests/test_long_floor.py tests/test_long_defaults.py tests/test_cine_auto.py`.
- Không render. Lead render và xem hình.

## Báo cáo
Ghi `docs/pm/tickets/GH-276-r3-report.md` bằng Python utf-8, tiếng Việt có dấu. Gồm: sửa gì ở 8 kiểu cũ, bố cục và chuyển động 12 kiểu mới, phân bố Mata Hari sau luật mượn ảnh, kết quả test.

Không commit, không render, không đăng. **Phải làm đủ 4 mục sửa, luật mượn ảnh và 12 kiểu. Dừng giữa chừng tính là hỏng.**
