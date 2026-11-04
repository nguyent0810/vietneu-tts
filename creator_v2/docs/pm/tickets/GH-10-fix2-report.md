# GH-10 · Báo cáo Codex vòng sửa 2

## Đã sửa

| Scene ID | Kết quả |
|---|---|
| `ch01#6` | Nhãn câu trích dẫn đổi thành `TRÍCH DỊCH`. |
| `ch03#0`, `ch08#0` | Không đổi khoảng cách chữ: cheatsheet không nêu tham số khoảng cách thẻ chương; không đọc/sửa engine theo phạm vi ticket. |
| `ch03#6`, `ch04#4`, `ch05#11`, `ch07#6` | Sửa `print_scene`: tiêu đề chính luôn nằm ở `side.h`, không còn phụ thuộc `head`. Riêng `ch05#11` đã đổi sang đồ họa `org`, nên không còn cảnh `print` có tiêu đề mất. |
| `ch03#6`, `ch07#6` | `sculley06` dùng `pos=[0.5, 0.14]`, `maxH=0.52`, `maxW=0.56` để chỉ lấy đầu/vai, không lộ thẻ tên. |
| `ch04#6` | Bỏ ảnh `nextcube`; thay bằng sơ đồ phần cứng NeXT → môi trường lập trình. Không còn callout mô tả sai màn hình tắt. |
| `ch05#11` | Bỏ ảnh `nextcube`; thay bằng sơ đồ CERN → máy NeXT, giữ đúng ý website đầu tiên. |
| `ch07#0` | Bỏ nền `nextcube`; dùng `nextstation`. |
| Cấu hình ảnh | Xóa hẳn key/nguồn `nextcube` khỏi `IMGS`, `STAND`, `FOCUS` và toàn bộ cảnh; phần ghi công không còn tham chiếu ảnh này. Để giữ mức dùng ảnh tối đa ba lần, `ch06#11` đổi từ ảnh `nextstation` sang timeline có nghĩa. |

Không thêm khẳng định mới cần fact-check; lời đọc `script.md` không bị sửa.

## Gate đã chạy

| Cổng / lệnh | Kết quả |
|---|---|
| `python data/long/mim-jobs-1985/gen_scenes.py` | Qua, tạo lại `spec.json` và 9 chương. |
| `python motion/long/script_lines.py mim-jobs-1985` | Qua: 120 câu, 1.932 âm tiết. |
| `python motion/long/build_long.py mim-jobs-1985 html` | Qua đủ 9/9 HTML, không có `Error`. Còn 2 warning beat2 cũ: `ch00#10` “BƯỚC MỘT” và `ch07#4` “TẠM QUYỀN” sẽ co còn khoảng 95%. |
| `python motion/long/coverage_lint.py mim-jobs-1985` | Qua: text-only 18,31% (97,84/534,38 giây), chuỗi dài nhất 9,40 giây. |
| `python motion/long/scene_rules.py mim-jobs-1985` | 0 warnings, 0 proposals. |
| `python motion/long/clip_sheet.py mim-jobs-1985` | Đã tạo và soi sheet gồm 19 clip; không thấy logo/chữ thương hiệu đọc được ở các khung xem trước. |
| `python scripts/long_gate.py mim-jobs-1985 --min-syl 1900` | **ĐẠT** — 1.932 âm tiết, 127 cảnh, 4,2 giây/cảnh, 19 clip khác nhau, 11 ảnh khác nhau, 32 URL nguồn. |
| Kiểm floor MIM theo ticket | `[]`. |

Lần chạy HTML đầu tiên dừng ở `OSError: cannot open resource` vì đồ họa `file_card` mới chạm linter font dùng chung. Không sửa engine; thay hai đồ họa đó bằng `org`/`timeline`, sau đó HTML qua 9/9.

## Số lần dùng ảnh sau sửa

| Ảnh | Lần dùng |
|---|---:|
| `ai01` | 2 |
| `ai02` | 2 |
| `ai03` | 2 |
| `ai04` | 2 |
| `ai05` | 2 |
| `ai06` | 2 |
| `jobs84` | 3 |
| `mac84` | 3 |
| `nextcube2` | 3 |
| `nextstation` | 3 |
| `sculley06` | 3 |

## Đầu ra

- Clip sheet đã kiểm: `output/long/mim-jobs-1985/qa_clips.jpg`.
- Thumbnail không thuộc phạm vi ticket, không tạo hay chỉnh sửa (ticket cấm render).
- Không chạy TTS, render, publish, hoặc thao tác lịch/Git.
