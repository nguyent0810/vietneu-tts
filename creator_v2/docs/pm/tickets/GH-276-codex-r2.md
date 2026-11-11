# GH-276 vòng 2: làm lại thẻ thông tin, mỗi kiểu một thiết kế riêng (Codex)

## Kết quả vòng 1 (Lead render trang demo, xem bằng mắt)
Bộ chọn, cổng mật độ và test đều ổn, **giữ nguyên**. Phần hình **không đạt**. Cả 20 kiểu là cùng một tấm thẻ, cùng bố cục (tên to, mô tả, 2 dòng), chỉ đổi màu nền và viền. Lỗi cụ thể:
- **Mất dấu ngã:** "CÂU CHUYỆN MẪU" hiện thành "MÂU" ở 18/20 kiểu. Dấu trên chữ hoa bị cắt vì `line-height:1.05` cộng `overflow:hidden`. Cần `line-height ≥ 1.25` cho tiêu đề serif, và padding trên đủ chỗ cho dấu.
- `polaroid` không có ảnh. `wanted` không ra poster truy nã. `seal_slip` có vạch đè lên chữ, chữ tràn khung. `telegram` chữ quá mờ. `callout` có đường dẫn nằm lơ lửng, không trỏ vào gì. `envelope`, `passport` và `verdict` dùng chung một vòng tròn đỏ.
- Ngoài kiểu kẹp ghim cũ, không kiểu nào có chuyển động vào riêng.

## Việc vòng 2
**Làm 8 kiểu thật kỹ trước.** 12 kiểu còn lại để vòng 3. Mỗi kiểu phải có **bố cục DOM riêng** (không chỉ đổi màu) và **chuyển động vào riêng**:

| style | Bố cục bắt buộc | Chuyển động vào |
|---|---|---|
| `lower_third` | Dải tên góc dưới trái, đè lên **ảnh nền tràn màn hình có cam** (dùng `img`, không có thì lấy ảnh gần nhất trong chương). Một dòng tên to, một dòng vai trò, đường kẻ màu nhấn | Vạch kẻ quét ngang, rồi chữ trượt lên từ sau mặt nạ |
| `callout` | Ảnh tràn màn hình. Vòng tròn khoanh đúng điểm `focus` của ảnh, đường dẫn gấp khúc từ vòng tròn tới nhãn chữ | Vòng tròn vẽ dần (SVG stroke), đường dẫn chạy ra, nhãn hiện sau |
| `news_clip` | Mẩu báo xé mép (clip-path răng cưa). Măng-sét chung chung "TIN TỨC · <năm>", **không** tên báo thật. Tít báo to, 2 cột chữ (các dòng `rows`), có ảnh nhỏ đen trắng nếu có `img` | Mẩu báo rơi xuống, xoay nhẹ, máy quay đẩy chậm vào tít |
| `telegram` | Băng giấy điện tín dán chéo trên nền giấy. Font máy đánh chữ, chữ HOA, kết mỗi dòng bằng "STOP". Tem "ĐIỆN TÍN" ở góc | Từng ký tự gõ ra (đúng mốc `at`), băng giấy trượt vào |
| `polaroid` | Ảnh (`img`) chiếm 75% khung polaroid, viền dưới dày, chú thích font viết tay có tiếng Việt (ví dụ Itim hoặc Charm). Không có ảnh thì **không chọn** kiểu này | Ảnh thả xuống, xoay, rồi "hiện màu" từ xám sang màu |
| `edict_scroll` | Cuộn giấy mở ngang có hai trục gỗ ở hai đầu. Chữ dọc hoặc ngang, ấn son vuông đóng ở cuối | Hai trục kéo ra hai bên, cuộn mở dần, ấn son dập xuống có rung nhẹ |
| `receipt` | Hóa đơn in nhiệt hẹp, mép dưới răng cưa. Từng dòng tiền căn phải, dòng tổng gạch đôi, font mono | Hóa đơn "in" từ trên xuống từng dòng theo `at` |
| `museum_label` | Nhãn bảo tàng nhỏ, đặt **cạnh** ảnh hiện vật (ảnh chiếm 2/3 màn hình bên trái). Tên, niên đại, chất liệu; chữ sans, nền trắng ngà | Ảnh hiện trước, nhãn trượt vào từ phải |

## Luật chung
- **Tiếng Việt:** dấu không bị cắt ở mọi cỡ chữ. Kiểm bằng test đọc CSS: tiêu đề có `line-height ≥ 1.2`. Mọi font mới phải có bộ glyph tiếng Việt và được khai báo trong `lint_html.KIN_FONTS`.
- Nhãn "ĐỒ HỌA" chỉ dành cho kiểu dạng tài liệu (`news_clip`, `telegram`), đặt kín đáo ở góc.
- Không ảnh AI, không tải ảnh mới. Chỉ dùng `img` mà cảnh đã khai báo.
- Bộ chọn: kiểu cần ảnh (`lower_third`, `callout`, `polaroid`, `museum_label`) chỉ được chọn khi cảnh có `img`.
- `idcards_demo.py`: ghi composition demo, dùng 2 ảnh có sẵn trong `motion/hf/assets/long/mata-hari/img/` (đọc tên file thật) để các kiểu cần ảnh có ảnh. Thứ tự: 8 kiểu mới trước, mỗi kiểu 6 giây.

## File được sửa
Như brief vòng 1: `casewide.js`, `casewide.css`, `idcards.py`, `idcards_demo.py`, `scene_params.py`, `lint_html.py` (phần `KIN_FONTS`), `tests/test_idcards.py`, `README.md`.

## Kiểm
- `node --check casewide.js`.
- Chạy pytest **chỉ** cho `tests/test_idcards.py tests/test_long_floor.py` (`--basetemp=tmp_pytest -p no:cacheprovider`).
- Không render. Lead render demo và xem hình.

## Báo cáo
Ghi `docs/pm/tickets/GH-276-r2-report.md` bằng Python utf-8, tiếng Việt có dấu. Với mỗi kiểu: mô tả bố cục DOM và chuyển động.

**Phải làm đủ 8 kiểu.** Dừng giữa chừng tính là hỏng.
