# GH-316 — Báo cáo bước cảnh (CK bài 10, `ck-c7-mo-tai-khoan-phi`)

Người làm: subagent Claude (Sonnet), thay Codex vì Codex làm hỏng dấu tiếng Việt. Mọi file ghi bằng Python UTF-8; đã quét `??` và `U+FFFD` trong `*.json` và `gen_scenes.py`: 0 file lỗi. Không đụng `lines` và `title` (so với `HEAD`: cả 8 chương giữ nguyên). Không render, không TTS, không commit, không đăng.

## File đã ghi
- `data/long/ck-c7-mo-tai-khoan-phi/gen_scenes.py` (chạy lại sinh `spec.json` và `ch00.json`–`ch07.json`).
- `data/long/ck-c7-mo-tai-khoan-phi/spec.json`, `ch00.json`–`ch07.json` (do `gen_scenes.py` sinh).
- Báo cáo này. Không sửa `plan.md` (xem mục "Cần Lead quyết định").

## Số cảnh và loại cảnh

Tổng 140 cảnh, 19 loại, kinetic 10,7% (15 cảnh), `file` 3 cảnh = 2,1% (cảnh số 14 `receipt`, 25 `lower_third`, 76 `callout`, cách nhau xa hơn 5 cảnh, ba kiểu khác nhau). Mọi cảnh chữ (kinetic, slam, question, myth) đều có `bg` hoặc `vid`; chữ trên nền trống 0,5% (chỉ cảnh `brand`).

| Chương | Cảnh | Loại cảnh |
| --- | ---: | --- |
| ch00 | 16 | brand 1, broll 2, counter 3, date 2, file 1, ledger 2, photo 1, question 2, slam 1, timeline 1 |
| ch01 | 17 | broll 1, chapter 1, file 1, kinetic 3, ledger 2, myth 1, photo 4, question 1, source 2, timeline 1 |
| ch02 | 18 | chapter 1, counter 3, date 1, kinetic 1, ledger 2, myth 1, photo 3, question 1, slam 1, source 1, stack 1, timeline 1, units 1 |
| ch03 | 13 | broll 1, chapter 1, counter 1, kinetic 1, ledger 1, myth 2, photo 2, question 1, source 1, timeline 1, units 1 |
| ch04 | 18 | bars 1, chapter 1, counter 1, date 1, file 1, kinetic 1, ledger 4, myth 1, slam 2, source 2, split 1, timeline 1, units 1 |
| ch05 | 15 | bars 1, broll 1, chapter 1, counter 1, date 1, kinetic 3, ledger 2, photo 2, source 1, split 1, units 1 |
| ch06 | 15 | bars 1, chapter 1, counter 3, kinetic 3, ledger 2, photo 1, question 1, slam 1, timeline 1, units 1 |
| ch07 | 28 | bars 2, chapter 1, counter 6, kinetic 3, ledger 5, myth 1, photo 3, question 2, slam 1, stack 1, timeline 1, units 1, waterfall 1 |

Mỗi chương có ít nhất 8 loại (sàn của `long_gate` là 5). Floor CK không đòi số loại; tổng 19 loại.

## Ảnh và clip

- Ảnh AI `ai01`–`ai16`: đủ 16 ảnh, tổng 59 lượt (`ai06` 2 lượt, `ai01/13/15/14/07` 3, `ai16/02/03/10/05/08/11/09` 4, `ai04/12` 5). Không ảnh nào quá 5 lượt (ticket cho tối đa 6).
- Ảnh Commons (18 khóa, 48 lượt, tối đa `hose2` 5 lượt): HOSE (`hose1`–`hose4`, `hnx` là Sở Hà Nội), skyline (`sky1`–`sky4`), hầm két (`vault1`–`vault3`), phố Hà Nội (`hn1`–`hn6`). Chỉ lấy ảnh nằm trong danh sách dùng được của `LOAI.md`; không logo, mã cổ phiếu, mặt người, tiền giấy. Chưa kiểm bằng mắt từng khung (chưa render).
- Cổng `long_gate` chỉ đếm khóa `img` của cảnh photo/file: không ảnh nào quá 3 lượt theo cách đếm ấy (đã tự đếm: tối đa 2–3).
- Clip: `900002` 2 lần (ch00, ch03), `900003` 1 (ch00), `900004` 1 (ch05), `900005` 1 (ch01), `900006` 1 (ch00). Không dùng `900001`. Không clip nào lặp ở hai chương liền kề. Cổng `long_gate` cho tối đa 2 lần mỗi clip với bài khoảng 12 phút: đạt.
- Chỉ 6 cảnh b-roll: floor CK không áp sàn 30 cảnh b-roll (sàn đó chỉ áp cho CL).

## Nhãn "VÍ DỤ GIẢ ĐỊNH" và thuế giả định

- Mọi cảnh có số của chị Hạnh mang nhãn (`tag` thẻ vàng góc trên trái cho cảnh ảnh/chữ; `srcnote` góc dưới phải cho biểu đồ, sổ, đếm số; một số cảnh có cả `unit`/tiêu đề ghi "VÍ DỤ GIẢ ĐỊNH"). Đã quét tự động: không cảnh nào chứa số của chị mà thiếu chữ GIẢ ĐỊNH (các cảnh còn lại chỉ có số của văn bản pháp luật hoặc số liệu thật).
- Thuế 0,1% hiện rõ GIẢ ĐỊNH ở ch04 (6 cảnh: ledger cách tính, counter 0,1%, ledger 50 triệu, bars 50/45 triệu, slam "BÁN LỖ VẪN CÓ THUẾ", units "chiều bán") và ở các dòng "THUẾ GIẢ ĐỊNH" của ch07. Chuỗi dùng: "GIẢ ĐỊNH · THUẾ 0,1% TRÊN GIÁ TRỊ BÁN · CHƯA XÁC NHẬN NGUYÊN VĂN ĐIỀU KHOẢN". Cảnh `myth` "ý kiến Cục Thuế ≠ điều khoản" và slam "CHƯA XÁC NHẬN ĐƯỢC" giữ đúng rào của kịch bản.
- Không có tên công ty chứng khoán, ngân hàng (chỉ danh từ chung "ngân hàng"), ứng dụng, mã cổ phiếu trên màn hình. Nguồn nêu theo văn bản (Thông tư, Quyết định, Luật) và "Cục Thuế", không nêu tên báo hay công ty trên màn hình.
- Số trên màn hình chỉ lấy từ `script.md`/`factcheck.md`: tài khoản (252.000, 14.384.902), 0,15%, 75.000, 150.000, 0,027%, 13.500, 0,1%, 50.000, 45.000, 270, 3.240, 12%, 33 nghìn, 0,066%, 50.075.000, 49.875.000, 200.000, 0,4%, 50.200, 0,401%, 50.300, 0,602%, 0,054%, 48,04 triệu. Các con số tỷ lệ lấy từ ghi chú kiểm chứng; "≈ 33.000" là làm tròn của 32.877 như lời đọc.

## Kiểm cảnh, nhịp và thời lượng (chưa có TTS)

Giả lập giờ đọc theo âm tiết, rồi chạy đúng các hàm của bước `html`: `build_long.plan` + `kinetic_style.apply` + `scene_params.validate_topic` + `late_first` + `floor.problems` (có họ thẻ #276) + `cadence.analyse`. Kết quả:

| Tốc độ đọc giả lập | Cảnh ngắn nhất | Cảnh dài nhất | Lỗi |
| --- | ---: | ---: | --- |
| 4,2 âm tiết/giây (theo ticket) | 3,1 s | 7,5 s | 0; cadence 2,64 s/đổi, không cảnh báo |
| 5,0 (nhanh) | 2,6 s | 6,5 s | 0 |
| 3,5 (chậm, sát nhịp 210 âm tiết/phút của `long_gate`) | 3,7 s | 8,9 s | 0, nhưng `cadence` cảnh báo khoảng trống hơn 8 s ở ch01, ch02, ch03, ch05, ch07 (cảnh `source`, `units`, `question` đứng yên 8,1–8,9 s) |

Phần tử con thứ hai của ledger/timeline/split đều neo vào mốc của chính cảnh (`at` + 0,2/0,8 s hoặc +0,1/+0,8 s), nên hiện trong 1 giây. Không `countAt` trễ. Khi có TTS, chạy `python scripts/check_scene_durations.py ck-c7-mo-tai-khoan-phi --out <thư mục output sản xuất>`; nếu giọng chậm hơn 3,6 âm tiết/giây, tách đôi vài cảnh tĩnh dài (danh sách ở dòng cuối bảng).

## Kết quả 5 bước kiểm của ticket (chạy từ `creator_v2/`)

1. `python data/long/ck-c7-mo-tai-khoan-phi/gen_scenes.py`: đạt ("spec + 8 chương").
2. `motion/variety.py audit`: **OK: đủ khác các video gần đây**. Lưu ý: nhạc `bgm` trong sổ còn rỗng vì nhạc chỉ được chọn ở bước `html` (mood curious/calm/mystery như các CK khác); phải audit lại sau `html`. Theme/look: kênh CK cố định `theme: chart` và look `classic` (audit miễn look cho theme `chart`); cả 3 CK gần nhất cũng như vậy, nên khác biệt chỉ nằm ở nhạc.
3. `python motion/long/cadence.py ck-c7-mo-tai-khoan-phi`: **cả 8 chương CẢNH BÁO nhưng là cảnh báo giả**: chưa có `timing.json` nên công cụ dùng 150 giây mỗi chương làm dự phòng. Với giờ giả lập 4,2 âm tiết/giây (xem bảng trên) không còn cảnh báo.
4. `floor.problems(chapters, "CK", topic, idcards_enabled=True)`: chỉ còn "chưa có timing" (cần TTS). Khi giả lập timing: 0 lỗi (chữ nền trống 0,49%, chuỗi chữ nền trống dài nhất 3,4 s; họ thẻ 3/140 cảnh, không lỗi #276; kinetic 10,7% dưới 38%).
5. `python scripts/plan_lint.py ck-c7-mo-tai-khoan-phi`: **LỖI: CK cần một tiêu đề khoản tiền + mốc thời gian.** Công cụ chỉ đọc mục 5 của `plan.md`, không đọc spec. Đã thử trên bản sao `plan.md` đặt ba tiêu đề của spec vào mục 5 (thư mục tạm, `--root`): **OK**. Cần Lead thay mục 5 của `plan.md` (xem dưới).
6. `python scripts/long_gate.py ck-c7-mo-tai-khoan-phi --min-syl 1900`: **TRƯỢT với đúng 2 lỗi dự kiến**: chưa TTS (8 chương) và `spec.youtube` thiếu `publish_at`, `playlist`. Còn lại đạt: 2.571 âm tiết, 132 cảnh thân bài, mỗi chương ≥5 loại, clip/ảnh trong ngưỡng, 28 URL trong factcheck, 15 URL công khai trong spec, tiêu đề 59 ký tự ≤60, không chuỗi cấm trong mô tả. `video_credits` đã có, nên không còn báo thiếu.

## Spec

- `channel: "CK"`, `opening_gate: true`, `craft: true`, `accent` vàng, `endcard 20`, `beat2`, `master`. Không bật `chart_rules` (ticket không đòi; biểu đồ đếm theo bộ của `long_gate` sẽ dưới 35%).
- Tiêu đề chính đúng chữ: "Mua 50 Triệu Cổ Phiếu: Giá Phải Tăng Bao Nhiêu Mới Hòa Vốn?" (59 ký tự).
- Dự phòng (luật #337): "Giữ 50 Triệu Cổ Phiếu 12 Tháng: Phí Và Thuế Là Bao Nhiêu?" (57; khoản tiền + mốc thời gian + từ phí/thuế) và "Giá Đứng Yên Vẫn Lỗ 200 Nghìn: Bốn Khoản Phí Ở Đâu Ra?" (54; rủi ro).
- Mô tả (`more[0]`) có câu "Nội dung giáo dục, không phải tư vấn đầu tư." và nêu chị Hạnh cùng mọi số là ví dụ giả định; `more[1]` nêu rào thuế 0,1% chưa đối chiếu nguyên văn, phí Sở 0,027% chỉ có nguồn cho Sở Hà Nội.
- `youtube.sources`: 15 URL công khai lấy từ `factcheck.md`. Không đưa các trang môi giới (finhay) hay ghi chú nội bộ.
- `hud {k, t}` đủ 8 chương; `bgm` mood (curious/calm/mystery) như CK trước.

## Chỗ khó minh họa và phán đoán Lead cần soát

1. **Thuế 0,1% chưa xác nhận nguyên văn**: chỉ hiện như giả định, kèm nhãn GIẢ ĐỊNH ở mọi cảnh; ch04 có hai cảnh `myth`/`slam` nhắc rõ "chưa xác nhận được". Không có số thuế nào hiện mà không có chữ GIẢ ĐỊNH.
2. **Phí Sở 0,027%** chỉ có nguồn cho Sở Hà Nội: màn hình ghi "TẠI SỞ HÀ NỘI" và "KHOẢNG"; cảnh `myth` ở ch03 nói rõ chưa biết chị Hạnh có phải trả riêng hay không.
3. **Số nhỏ so với số lớn**: phí 75/50 nghìn đồng trên 50 triệu hầu như không thấy được trên cột biểu đồ. Đã chọn biểu diễn bằng nghìn đồng (stack 75+75+50 = 200 nghìn ở ch07, bars 150.000 so với 3.240 ở ch05) và ledger/counter ghi số rõ thay vì cột sát nhau. Cột "3.240 đ" ở ch05 sẽ rất thấp: đúng với "chừng hai phần trăm", nhưng cần xem khung hình.
4. **Hai dòng đầu của ledger/timeline hiện trước lời** vài giây (neo theo mốc của cảnh để qua luật "phần tử con thứ hai trong 1 giây"), từ dòng thứ ba trở đi neo theo chữ trong câu.
5. **Cảnh `source` trích điều luật**: nội dung chỉ tóm ý như lời đọc (Điều 88 Luật Chứng khoán 2019, Thông tư 121/2020, QĐ 1541, Luật Thuế TNCN 109/2025). Không bịa nguyên văn; nên đối chiếu `snippet` với `factcheck.md` khi duyệt.
6. **Ba thẻ `file`** (receipt giá trị "?" ở ch00 vì số chưa nói tới, lower_third kèm ảnh AI `ai10`, callout kèm ảnh `hose3`): ba kiểu khác nhau để qua luật "kiểu không lặp trong 6 thẻ"; `app_card` không dùng (tránh hiển thị ứng dụng).
7. **Hai cảnh `split`** (ch04, ch05) dùng ảnh AI minh họa trừu tượng với dấu "≠"; chưa xem bằng mắt.
8. Chưa kiểm bằng mắt, cần render nháp chương: cảnh `date` (định dạng "01.07.2026"), cảnh `units` 2 ô, thẻ `file` kiểu `receipt`, vị trí thẻ `tag` so với tiêu đề biểu đồ, và chữ phủ trên ảnh dọc (`vault`).
9. Clip sheet chưa làm (ticket không nêu); thumbnail không thuộc ticket.

## Cần Lead quyết định

- Thay mục 5 của `data/long/ck-c7-mo-tai-khoan-phi/plan.md` để `plan_lint.py` qua (không sửa vì ngoài phạm vi file được ghi). Nội dung đã thử, lint trả OK:

```
## 5. Tiêu đề và Thumbnail

### 3 phương án Tiêu đề (≤ 60 ký tự):
1. `Mua 50 Triệu Cổ Phiếu: Giá Phải Tăng Bao Nhiêu Mới Hòa Vốn?` (59 ký tự) — tiêu đề chính (Lead chọn).
2. `Giữ 50 Triệu Cổ Phiếu 12 Tháng: Phí Và Thuế Là Bao Nhiêu?` (57 ký tự) — khoản tiền + mốc thời gian.
3. `Giá Đứng Yên Vẫn Lỗ 200 Nghìn: Bốn Khoản Phí Ở Đâu Ra?` (54 ký tự) — rủi ro.
```

- Điền `publish_at` và `playlist` vào spec khi chốt lịch.
- Bước tiếp theo theo `CLAUDE.md`: TTS (`build_long.py … tts`), rồi `check_scene_durations.py --out`, `html`, audit nhạc, render nháp chương có `date`/`units`/`file`.
