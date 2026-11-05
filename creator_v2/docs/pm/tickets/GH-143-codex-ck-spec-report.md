# GH-143 · Báo cáo lắp spec CK Short

## Đã làm

- Đã tạo `data/stier/specs/ck-them-10-trieu-gio-bot-mot-mon.json`.
- Giữ nguyên từng câu trong `lines`, cùng `title_chosen`, `say`, `description` và `sources` từ đầu vào Lead đã review.
- Đặt `short_type: "S"`, `theme: "ck"`, mix `true`, `music_gain: 0.18`, `music_duck: 3`, `sfx_gain: 0.36`; thêm 12 tag CK không nêu ngân hàng, công ty tài chính hay mã cổ phiếu.
- Chọn look `blueprint`. Sổ look ghi `ck-b1-lai-uu-dai-nam-ngoai` là `archive`, còn `ck-e2-bang-tra-quy-khan-cap` là `neon`, nên look này khác cả hai.
- Không render, không TTS, không upload/enqueue/đổi lịch, không sửa code hay spec khác.

## Cổng kiểm

Đã chạy:

```text
python motion/stier/script_lint.py ck-them-10-trieu-gio-bot-mot-mon
```

Kết quả nguyên văn:

```text
Traceback (most recent call last):
  File "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\motion\stier\script_lint.py", line 183, in <module>
    from factory.console import utf8_console
ModuleNotFoundError: No module named 'factory.console'
```

Đây là lỗi import của linter dùng chung; không sửa code theo phạm vi ticket.

Đã chạy:

```text
python motion/stier/build.py ck-them-10-trieu-gio-bot-mot-mon --preflight
```

Kết quả nguyên văn cuối cùng:

```text
LỖI ck-them-10-trieu-gio-bot-mot-mon: phối cảnh chưa đạt (luật mix 12/10/2026): thiếu cảnh ảnh/video cộng đồng; cảnh thuần chữ chiếm 41% thời lượng (> 35%)
```

Đã sửa lỗi neo ban đầu ở cảnh giỏ (neo `gapAt` vào chuỗi không có trong lời) và thay cảnh giỏ từ `chart` sang `cards3d`, nên không còn chuỗi ba cảnh D liên tiếp. Cổng preflight vẫn chưa đạt vì `build.py` hiện chỉ phân loại cảnh chữ là M khi có `clip` hoặc `vid` không rỗng. Hai cảnh M của ticket bắt buộc có `q` và `vid: null` để agent render điền về sau; trường `q`/kiểu `clip` không được bộ mix hiện tại tính là M. Đổi `vid` sang một clip đã chọn sẽ trái yêu cầu ticket; do đó không tự ý thay.

## Thời lượng và cảnh

Thời lượng ước tính: khoảng 35 giây (108 từ ở 3,3 từ/giây, cộng 2,02 giây nhịp nghỉ TTS).

| # | Loại | Nội dung | Cần clip |
|---:|---|---|---|
| 0 | T / kinetic | `10 TRIỆU ↑` đối `GIỎ −1 MÓN`, có nhãn VÍ DỤ GIẢ ĐỊNH từ giây 0 | Không |
| 1 | M / clip | Tay cầm giỏ mua sắm trơn, không logo/chữ/biển hiệu | Có — `vid: null`, q đã ghi |
| 2 | D / counter | CPI cùng kỳ +5,09%, nguồn CỤC THỐNG KÊ · T10/2026 | Không |
| 3 | G / cards3d | Ví dụ giả định: 250 triệu, lãi 4% | Không |
| 4 | D / counter | Số dư mới 260 triệu, có nhãn VÍ DỤ GIẢ ĐỊNH | Không |
| 5 | G / cards3d | Giỏ cũ 250.000.000Đ và giỏ mới 262.725.000Đ, có nhãn VÍ DỤ GIẢ ĐỊNH | Không |
| 6 | D / counter | Khoản thiếu 2.725.000Đ, có nhãn VÍ DỤ GIẢ ĐỊNH | Không |
| 7 | M / clip | Nhấc một món rau trơn khỏi giỏ, không bao bì/logo/chữ | Có — `vid: null`, q đã ghi |
| 8 | T / kinetic | `SỐ DƯ TĂNG` / `SỨC MUA CHƯA TĂNG` | Không |

## Khẳng định không kiểm được

Không có khẳng định mới ngoài bộ nguồn/kiểm chứng Lead đã bàn giao. Chưa thể đạt preflight cho đến khi quy ước clip `q` + `vid: null` được bộ mix hỗ trợ, hoặc người có thẩm quyền điền clip hợp lệ.
