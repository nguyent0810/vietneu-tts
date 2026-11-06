# GH-173 — Báo cáo QA khung hình nhãn VÍ DỤ GIẢ ĐỊNH

QA trên code nhãn đã có trong worktree (`casefile.js`, `casefile.css`, preflight trong `build.py`). Không sửa engine, không sửa spec gốc, không commit, không upload, không đổi lịch.

## Spec đã chọn

Ba bản sao, mỗi bản chỉ thêm `hypo`. Spec gốc không đổi.

| Kênh | Gốc | Bản thử | Cảnh bật nhãn |
| --- | --- | --- | --- |
| CK | `ck-b4-khoan-khong-hoa-don` | `data/stier/specs/_qa173_ck.json` | cảnh 1 chart, cảnh 2 counter, cảnh 3 cards3d (`hypo_sub`: "Phép tính minh họa") |
| MIM | `mim-captcha-500-nam-moi-ngay` | `data/stier/specs/_qa173_mim.json` | cảnh 2 cards3d (`hypo_sub` như trên), cảnh 3 counter |
| CL | `unabomber` | `data/stier/specs/_qa173_cl.json` | cảnh 1 ledger (`hypo_sub` như trên), cảnh 3 counter |

Số cảnh trong bảng là chỉ số preflight (cảnh 0 là cảnh đầu).

CK được chọn vì cùng một spec đã có "giả định" ở `unit` của chart, `sub` của counter và `note` của cards3d, đúng ba loại cảnh preflight đang canh. MIM được chọn vì đây là spec MIM duy nhất có "giả định" trong trường preflight theo dõi (`note` của cards3d). Cảnh counter của MIM có dòng "ƯỚC TÍNH · KHÔNG PHẢI SỐ ĐO", không chứa chữ "giả định", nên gốc không cảnh báo cảnh đó; nhãn vẫn được bật vì cảnh này là kết quả của phép ước tính.

CL không có spec theme `case` nào chứa chữ "giả định" (đã rà `data/stier/specs/`). Gốc `unabomber` vì vậy không thể cảnh báo, và các số trên ledger / counter là sự kiện lịch sử, không phải ví dụ giả định. Cờ `hypo` trên bản CL chỉ để đo băng giấy. Theme `case` cũng không có cảnh chart hay cards3d, nên ledger và counter là hai loại cảnh CL dùng được.

## Preflight

Lệnh: `python motion/stier/build.py --preflight <slug> ...` (cờ nằm trong `build.py`; README chưa ghi). Cảnh báo hypo in ra stdout và không đổi mã thoát. Mã thoát 1 đến từ lỗi cứng đã có sẵn trên spec gốc.

Trước, stdout lưu ở `output/stier/_qa173/preflight-before.txt`:

```
CẢNH BÁO ck-b4-khoan-khong-hoa-don: cảnh 1 (chart): unit chứa GIẢ ĐỊNH cỡ nhỏ; thêm hypo
CẢNH BÁO ck-b4-khoan-khong-hoa-don: cảnh 2 (counter): sub chứa GIẢ ĐỊNH cỡ nhỏ; thêm hypo
CẢNH BÁO ck-b4-khoan-khong-hoa-don: cảnh 3 (cards3d): note chứa GIẢ ĐỊNH cỡ nhỏ; thêm hypo
ck-b4-khoan-khong-hoa-don: OK — 94 từ, ước lượng 28.5s
CẢNH BÁO mim-captcha-500-nam-moi-ngay: cảnh 2 (cards3d): note chứa GIẢ ĐỊNH cỡ nhỏ; thêm hypo
LỖI mim-captcha-500-nam-moi-ngay: dấu ~ trước số dễ đọc thành dấu trừ: ['~32', '~4,6'] -- dùng ≈
LỖI unabomber: câu 0: ký hiệu/viết tắt 'FBI' chưa có say
LỖI unabomber: câu 7: ký hiệu/viết tắt 'FBI' chưa có say
```

Sau, `output/stier/_qa173/preflight-after.txt`:

```
_qa173_ck: OK — 94 từ, ước lượng 28.5s
LỖI _qa173_mim: dấu ~ trước số dễ đọc thành dấu trừ: ['~32', '~4,6'] -- dùng ≈
LỖI _qa173_cl: câu 0: ký hiệu/viết tắt 'FBI' chưa có say
LỖI _qa173_cl: câu 7: ký hiệu/viết tắt 'FBI' chưa có say
```

Ba cảnh báo CK và một cảnh báo MIM hết trên bản thử. Bản CL không có cảnh báo hypo trước hay sau. Lỗi `~` và `FBI` giữ nguyên, ngoài phạm vi ticket.

## Cách chụp

Không render mp4. Mỗi cảnh có hypo được chụp bằng `hyperframes snapshot --at <giây> --no-end` (hyperframes 0.8.75) trên project `output/stier/_qa173/<kenh>/`. Thời điểm nằm sau lúc nhãn vào (0,45–0,5s) và trước lúc cảnh mờ (`t1 − 0,1`).

StaticGuard của snapshot chỉ thấy timeline khi chuỗi `window.__timelines` nằm trong HTML. Project QA vì vậy inline `beat.js` và `casefile.js`, trỏ GSAP sang `assets/vendor/gsap.min.js`, và thêm stub trong `<head>`. File engine trong `motion/hf/` không bị sửa. Ảnh và font nạp đủ (CK 11, MIM 14, CL 15 mặt chữ).

Hộp đo bằng Chrome headless, viewport 1080×1920, `seek` trên `window.__timelines.main`, `getBoundingClientRect` so với `#root`. Mép sơn lấy từ pixel PNG. Tab băng CL tính cả `::before` / `::after` sau khi xoay.

Giới hạn của khung: thời lượng là ước lượng 3,3 từ/giây cộng `tts.pauses` của spec, không có TTS. `looks.resolve` không được gọi (hàm đó ghi sổ look dùng chung), nên khung dùng look mặc định. `plan()` của CK với `mix: true` dừng vì luật mix: cảnh chart ước lượng dài 11,1s. Project CK được dựng lại sau khi bỏ `mix` trên bản trong bộ nhớ; file `_qa173_ck.json` vẫn giữ `mix: true`. Nhãn không phụ thuộc mix hay look.

## Bảng cảnh × kết quả

Toạ độ là pixel trên khung 1080×1920. "Mép phải" là mép phải của hộp nhãn, gồm tab băng CL. Ngưỡng cột nút là x > 900.

| Kênh | Cảnh | Loại | Ảnh | Cỡ chữ nhãn / phụ đề | Mép phải | Kết quả |
| --- | --- | --- | --- | --- | --- | --- |
| CK | 1 | chart | `output/stier/_qa173/ck/frames/frame-00-at-20s.png` | 62px / 62px | 638 | Đạt |
| CK | 2 | counter | `output/stier/_qa173/ck/frames/frame-01-at-25.24s.png` | 62px / 62px | 636 | Đạt |
| CK | 3 | cards3d | `output/stier/_qa173/ck/frames/frame-02-at-30.69s.png` | 62px / 62px | 636 | Lỗi: nhãn đè tiêu đề cảnh |
| MIM | 2 | cards3d | `output/stier/_qa173/mim/frames/frame-00-at-16.71s.png` | 62px / 62px | 766 | Lỗi: nhãn che hết tiêu đề cảnh |
| MIM | 3 | counter | `output/stier/_qa173/mim/frames/frame-01-at-23.17s.png` | 62px / 62px | 766 | Đạt |
| CL | 1 | ledger | `output/stier/_qa173/cl/frames/frame-00-at-6.08s.png` | 62px / 62px | 722 | Đạt (đo bố cục; số liệu là sự kiện, không phải ví dụ giả định) |
| CL | 3 | counter | `output/stier/_qa173/cl/frames/frame-01-at-16.08s.png` | 62px / 62px | 722 | Đạt (cùng ghi chú như ledger) |

Mỗi thư mục `frames/` còn `contact-sheet.jpg`.

### Từng khung

- CK chart, t = 20s. Ruy-băng vàng "VÍ DỤ GIẢ ĐỊNH", nét vàng sơn từ (52, 206) đến (594, 306). Cảnh chart phóng từ 1,00 lên 1,03 nên hộp lệch khỏi `left: 64px; top: 220px`, vẫn cách xa x = 900. Kicker đáy y = 165. Tiêu đề biểu đồ bắt đầu dưới nhãn (hộp `.chtitle` tại y = 337, nét chữ quanh y = 350). Cột, đơn vị, phụ đề "ba trăm mười lăm" không bị đè.
- CK counter, t = 25,24s. Ruy-băng một dòng, nét vàng tới y = 320, mép hộp y = 323. Nét trắng của "5,25 TRIỆU" bắt đầu y = 347, còn 27px. Nhãn "MẤT GIÁ MỖI THÁNG", dòng phụ và phụ đề "mỗi tháng." nằm dưới. Kicker không chạm.
- CK cards3d, t = 30,69s. Ruy-băng có dòng phụ "PHÉP TÍNH MINH HỌA", hộp (64, 220)–(636, 358), nét vàng tới (592, 355). Tiêu đề cảnh "MỖI THÁNG · NĂM ĐẦU" có hộp y = 304–380. Phần trái của tiêu đề không còn nét trắng trong vùng x < 636. "NĂM ĐẦU" vẫn đọc được bên phải, nét trắng từ khoảng x = 653, y = 298–363. Ba thẻ bắt đầu y = 427, dòng note và phụ đề không chạm nhãn.
- MIM cards3d, t = 16,71s. Khung lệnh cyan, tag "MÔ PHỎNG", dòng "PHÉP TÍNH MINH HỌA", prompt ">" và "VÍ DỤ GIẢ ĐỊNH". Hộp (64, 220)–(766, 366). Tiêu đề cảnh "PHÉP TÍNH" (hộp y = 304–380) không còn nét trong cả dải y = 290–380, kể cả bên phải khung; pixel giữa tiêu đề là nền tối của khung. Ba thẻ bắt đầu y = 432. Note "GIẢ ĐỊNH CỦA CLOUDFLARE, 05/2021" và phụ đề "Giả sử mười ngày," không chạm nhãn.
- MIM counter, t = 23,17s. Cùng khung lệnh, không có `hypo_sub` mà vẫn cao 146px vì có hàng "MÔ PHỎNG". Hộp DOM của "500 NĂM" bắt đầu y = 360 nên chồng nhãn 6px, nhưng khoảng đó là khoảng trống phía trên nét chữ. Nét cyan của nhãn hết ở y = 364, nét trắng của số bắt đầu y = 386, còn 22px. Con trỏ cyan có đáy y = 340, nằm trên số. Dòng "THỜI GIAN CỦA LOÀI NGƯỜI · MỖI NGÀY", dòng "ƯỚC TÍNH · KHÔNG PHẢI SỐ ĐO" và phụ đề không chạm nhãn.
- CL ledger, t = 6,08s. Băng giấy (80, 227)–(697, 360), tab sau khi xoay kéo hộp ra x = 55–722, y trên khoảng 205. Thẻ sổ bắt đầu y = 421, còn 61px. Kicker "HỒ SƠ 1996 / UNABOMBER" và phụ đề "23 người bị thương." không chạm. Dòng tổng "BỊ THƯƠNG / 23" lúc chụp còn opacity dưới 0,15 vì mốc từ của dòng đó; nhãn không phủ thẻ sổ.
- CL counter, t = 16,08s. Băng một dòng, giấy tới y = 321, tab tới x = 721. Nét trắng của "35.000" bắt đầu y = 453. "CHỮ", "BẢN TUYÊN NGÔN · 1995" và phụ đề "nghìn chữ của hắn." nằm dưới.

## Lỗi bố cục theo loại cảnh

**cards3d.** Tiêu đề `.c3t` được đặt tại `top − 130`. Với ba thẻ, `top` khoảng 430 nên tiêu đề nằm ở y = 304, trong khi nhãn chiếm y = 220 trở xuống. Trên CK có `hypo_sub`, đáy nhãn là 358 và nuốt phần trái tiêu đề. Trên MIM, hàng "MÔ PHỎNG" làm khung cao 146px dù `hypo_sub` chỉ ngồi cùng hàng meta, đáy 366, và tiêu đề ngắn "PHÉP TÍNH" bị che hết. Các thẻ kính thì bắt đầu quanh y = 427–432, không dính nhãn. Ruy-băng CK một dòng đo trên cảnh counter có đáy 323, vẫn cắt một tiêu đề đặt ở y = 304 khoảng 19px; chưa có khung cards3d một dòng để chụp riêng.

**counter.** Ruy-băng CK một dòng và băng CL một dòng để trống 27px và hơn 100px phía trên nét số. Khung MIM cao hơn, sát số hơn (22px từ mép cyan tới nét trắng) nhưng không đè nét. Hộp dòng của số MIM chồng 6px vào nhãn chỉ vì leading trống của cỡ 198px.

**chart.** Đạt. Nhãn đi theo phép phóng chậm của cả cảnh, mép vàng tới y = 306, tiêu đề biểu đồ nằm dưới.

**ledger.** Đạt, kể cả khi có `hypo_sub` và hai tab băng. Khe tới thẻ sổ khoảng 61px.

Thẻ cards3d và thẻ ledger có mép phải vượt 900 (thẻ CK tới khoảng x = 963, thẻ MIM tới khoảng 969, sổ CL tới x = 993). Đó là khối nội dung sẵn có. Nhãn thì không: mép phải lớn nhất là 766 (MIM), 722 (CL kể cả tab), 638 (CK).

## Cỡ chữ, kiểu kênh, dấu tiếng Việt

`.hypo-title` và `.cap` đều computed `font-size: 62px` (`var(--caption-size)`) trên cả bảy khung. Dòng phụ là 24px (CK, CL) hoặc 22px (MIM, nằm trong hàng meta).

Kiểu đúng kênh trên cả các khung của kênh đó: CK ruy-băng vàng, chữ Be Vietnam Pro 900, màu `#fbbf24`; MIM khung lệnh cyan, JetBrains Mono, tag "MÔ PHỎNG", dấu `>`, con trỏ; CL băng giấy kem, chữ Playfair Display nghiêng, hai tab băng.

Dấu trên nhãn đủ ở mọi khung: "VÍ DỤ GIẢ ĐỊNH" và "PHÉP TÍNH MINH HỌA" (dòng phụ bị `text-transform: uppercase`). Phụ đề giữ dấu (trăm, mỗi, Giả sử, ngày, thương, chữ, hắn).

Link font trong HTML xin Playfair italic 700, còn CSS đặt italic 900. `document.fonts` có Playfair 700 italic và 900 normal, không có mặt 900 italic. Khung CL vẫn ra chữ nghiêng, nét rõ, dấu đủ. Đây là ghi chú mặt chữ, không phải lỗi đè.

## Ngoài phạm vi

Không sửa `motion/hf/assets/engine/casefile.js`, `casefile.css`, `build.py`, test, hay spec gốc. Không commit, không upload, không đổi lịch, không gọi `looks.resolve` hay `pick_track`.
