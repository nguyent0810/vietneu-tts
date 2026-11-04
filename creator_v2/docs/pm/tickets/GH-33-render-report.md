# GH-33 — Báo cáo render 12 Short pilot tin nóng tuần 45

- **Issue:** https://github.com/nguyent0810/Youtube_Creator_V2/issues/33
- **Brief thực thi:** `docs/pm/tickets/GH-33-agy-render.md`
- **Báo cáo spec đầu vào:** `docs/pm/tickets/GH-33-specs-report.md`

---

## 1. Tóm tắt kết quả chạy `build.py` và nguyên nhân chặn cứng

Đã chạy lần lượt từng lệnh `python motion/stier/build.py <slug>` (bản thật, không `--draft`, đúng thứ tự 6 slug CK trước rồi 6 slug MIM sau, không chạy song song).

**Kết quả:** Cả **12/12 slug đều dừng ngay ở dòng 640–641 của `motion/stier/build.py` (`SystemExit`, mã thoát `1`) trước khi gọi TTS hay render:**

```text
ck-thue-xang-0-giam-1804: 223 từ — ngoài 55-135
ck-dien-giam-44-dong-20-nam: 230 từ — ngoài 55-135
ck-vang-sjc-140-trieu-chenh-14-trieu: 227 từ — ngoài 55-135
ck-ho-kinh-doanh-giam-30-thue: 235 từ — ngoài 55-135
ck-lai-giam-05-tien-gui-80-ngan-han: 233 từ — ngoài 55-135
ck-binance-63-ty-rut-36-ty: 237 từ — ngoài 55-135
mim-binance-20-phut-6-3-ty: 202 từ — ngoài 55-135
mim-cam-nhap-dien-thoai-cu-2027: 189 từ — ngoài 55-135
mim-sam-altman-ram-5-phan-tram: 213 từ — ngoài 55-135
mim-android-20-tin-nhan-tu-than: 205 từ — ngoài 55-135
mim-9-tren-10-ai-tu-lay-otp: 220 từ — ngoài 55-135
mim-ve-tinh-google-4-chip-tpu: 195 từ — ngoài 55-135
```

### Vì sao `script_lint.py` báo 0 lỗi nhưng `build.py` chặn cứng cả 12 bài?
1. **Cổng số từ (`build.py:637-641`):** `build.py` bắt buộc tổng số từ `nw = sum(len(l.split()) for l in spec["lines"])` nằm trong khoảng **`55–135 từ`** (tương đương thời lượng **25–40 giây** ở tốc độ đọc tiếng Việt ~3,3–3,5 từ/giây). Ở bước viết spec trước đó (`GH-33-specs-report.md`), agent chỉ chạy `script_lint.py` (linter của kênh BUD, không kiểm trần 135 từ khi không bật `"v2": true`) và không chạy `build.py`. Toàn bộ 12 spec hiện có **`189–237 từ`** (nếu đọc hết sẽ dài **~55–70 giây**, vượt xa khung 25–40 giây của Short).
2. **Tuân thủ phạm vi ticket (`GH-33-agy-render.md`):**
   - Ticket quy định rõ: *"Không: sửa `motion/**`, `hf_batch_render` hay code engine... Thấy lỗi spec thì ghi vào báo cáo, không tự sửa nội dung lời đọc hay số liệu."*
   - Vì không được sửa `motion/stier/build.py` và không được tự ý cắt gọt nội dung lời đọc (`lines`) từ ~220 từ xuống ≤ 135 từ, agent giữ nguyên 12 file `data/stier/specs/<slug>.json` và kiểm toán toàn bộ các cổng kiểm phía sau trong `build.py` để Lead/Codex xử lý dứt điểm trong một lần sửa spec.

---

## 2. Bảng tổng hợp 12 slug (Trạng thái · Thời lượng · Đường dẫn · Lỗi phát hiện)

| # | Slug | Trạng thái | Thời lượng | Đường dẫn `final.mp4` | Đường dẫn `qa_sheet.png` | Lỗi chặn trong `build.py` & lỗi spec phát hiện |
|---|---|---|---|---|---|---|
| 1 | `ck-thue-xang-0-giam-1804` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(223 từ ≈ 65s, vượt 25–40s)* | `output/stier/ck-thue-xang-0-giam-1804/final.mp4` *(chưa sinh)* | `output/stier/ck-thue-xang-0-giam-1804/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `223 từ — ngoài 55-135` (`build.py:641`).<br>• **`say` / TTS (`build.py:143`):** `"say": {}` rỗng trong khi câu 2, 3 có chữ số/ký hiệu `E5`, `92`, `E10`, `95` chưa phiên âm.<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T D D D D G T]` thiếu cảnh `M` (ảnh/video cộng đồng); vi phạm `3 cảnh liền cùng kiểu D` (4 cảnh `D` liên tiếp ở cảnh 1–4: `date`, `chart`, `chart`, `counter`); kiểu `D` chiếm > 60% thời lượng. |
| 2 | `ck-dien-giam-44-dong-20-nam` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(230 từ ≈ 67s, vượt 25–40s)* | `output/stier/ck-dien-giam-44-dong-20-nam/final.mp4` *(chưa sinh)* | `output/stier/ck-dien-giam-44-dong-20-nam/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `230 từ — ngoài 55-135` (`build.py:641`).<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T D D D T G T]` thiếu cảnh `M` (ảnh/video cộng đồng); vi phạm `3 cảnh liền cùng kiểu D` (cảnh 1–3: `chart`, `counter`, `ledger`); cảnh 5 (`board`, từ câu 5 đến câu 7, dài 61 từ) sẽ vượt trần `> 11s/cảnh`. |
| 3 | `ck-vang-sjc-140-trieu-chenh-14-trieu` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(227 từ ≈ 66s, vượt 25–40s)* | `output/stier/ck-vang-sjc-140-trieu-chenh-14-trieu/final.mp4` *(chưa sinh)* | `output/stier/ck-vang-sjc-140-trieu-chenh-14-trieu/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `227 từ — ngoài 55-135` (`build.py:641`).<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T T D D D D T]` thiếu cảnh `M` (ảnh/video cộng đồng); **thiếu cả cảnh `G`** (`board`/`cards3d`/`map`); vi phạm `3 cảnh liền cùng kiểu D` (4 cảnh `D` liên tiếp ở cảnh 2–5: `chart`, `chart`, `counter`, `ledger`); cảnh 4 (`counter`, câu 4–5) dài > 11s.<br>• **Lỗi neo chữ (`at`):** cảnh 3 (`chart`, bắt đầu ở câu 3) có cột `"BÁN RA"` neo `"at": [2, "bốn"]` (lùi về câu 2, trước khi cảnh 3 mở). |
| 4 | `ck-ho-kinh-doanh-giam-30-thue` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(235 từ ≈ 68s, vượt 25–40s)* | `output/stier/ck-ho-kinh-doanh-giam-30-thue/final.mp4` *(chưa sinh)* | `output/stier/ck-ho-kinh-doanh-giam-30-thue/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `235 từ — ngoài 55-135` (`build.py:641`).<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T G D D D T G]` thiếu cảnh `M` (ảnh/video cộng đồng); vi phạm `3 cảnh liền cùng kiểu D` (cảnh 2–4: `timeline`, `ledger`, `chart`); cảnh 6 (`board`, phủ câu 6–7, dài 68 từ) vượt trần `> 11s/cảnh`. |
| 5 | `ck-lai-giam-05-tien-gui-80-ngan-han` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(233 từ ≈ 68s, vượt 25–40s)* | `output/stier/ck-lai-giam-05-tien-gui-80-ngan-han/final.mp4` *(chưa sinh)* | `output/stier/ck-lai-giam-05-tien-gui-80-ngan-han/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `233 từ — ngoài 55-135` (`build.py:641`).<br>• **`mix_lint` & thời lượng cảnh:** chuỗi cảnh `[T D D M D G T]` lách qua `M` nhờ thẻ `file` ở câu 4 (không có footage/ảnh thật); cảnh 2 (`ledger`, phủ câu 2–3, 52 từ) vượt trần `> 11s/cảnh` trong `mix_lint`. |
| 6 | `ck-binance-63-ty-rut-36-ty` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(237 từ ≈ 69s, vượt 25–40s)* | `output/stier/ck-binance-63-ty-rut-36-ty/final.mp4` *(chưa sinh)* | `output/stier/ck-binance-63-ty-rut-36-ty/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `237 từ — ngoài 55-135` (`build.py:641`).<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T D D D D D T]` thiếu cảnh `M` (ảnh/video cộng đồng); **thiếu cả cảnh `G`** (`board`/`cards3d`/`map`); vi phạm `3 cảnh liền cùng kiểu D` (5 cảnh `D` liên tiếp ở cảnh 1–5: `timeline`, `counter`, `counter`, `chart`, `ledger`); kiểu `D` chiếm > 60% thời lượng; cảnh 5 (`ledger`, phủ câu 5–6, 63 từ) vượt trần `> 11s/cảnh`.<br>• **Lỗi neo chữ (`at`):** cảnh 1 (`timeline`, `at: 1`) có mục `"20 PHÚT"` neo `"at": [0, "Hai"]` (thuộc câu 0, trước khi cảnh 1 bắt đầu). |
| 7 | `mim-binance-20-phut-6-3-ty` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(202 từ ≈ 58s, vượt 25–40s)* | `output/stier/mim-binance-20-phut-6-3-ty/final.mp4` *(chưa sinh)* | `output/stier/mim-binance-20-phut-6-3-ty/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `202 từ — ngoài 55-135` (`build.py:641`).<br>• **Lỗi bảng `say` (`build.py:99`):** khóa `"=TRM Labs"` chứa khoảng trắng nhưng `spoken()` tách câu theo `text.split()` từng từ đơn nên không khớp.<br>• **Lỗi neo chữ (`at`) & thời lượng cảnh:** cảnh 1 (`timeline`, bắt đầu ở câu 1, kết thúc ở câu 3) có mục `"-36 GIỜ"` neo `"at": [3, "ba"]` (nằm ở câu 3, tức **sau khi cảnh 1 đã kết thúc và chuyển sang cảnh 2**); cảnh 1 phủ câu 1–2 (44 từ) dễ vượt trần `> 11s/cảnh`. Không có footage/ảnh thật (cảnh `M` duy nhất là thẻ `file`). |
| 8 | `mim-cam-nhap-dien-thoai-cu-2027` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(189 từ ≈ 55s, vượt 25–40s)* | `output/stier/mim-cam-nhap-dien-thoai-cu-2027/final.mp4` *(chưa sinh)* | `output/stier/mim-cam-nhap-dien-thoai-cu-2027/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `189 từ — ngoài 55-135` (`build.py:641`).<br>• **Lỗi trùng mốc cảnh gây crash (`build.py:479`):** cảnh 1 (`date`) có `"at": 1` và cảnh 2 (`cards3d`) cũng có `"at": 1` → thời lượng cảnh 1 bằng `0.00s` (`ValueError: cảnh 1 (date) quá ngắn`).<br>• **Lỗi neo chữ (`at`) lệch ngoài cảnh:** cảnh 3 (`board`, `at: 3`) có node `"máy cũ"` neo `[2, "máy"]` (câu 2) và node `"linh kiện cũ"` neo `[4, "linh"]` (câu 4, sau khi đã sang cảnh 4); cảnh 4 (`ledger`, `at: 4`) có 2 dòng neo ở câu 2 (`[2, "nguyên"]`) và câu 3 (`[3, "tân"]`).<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T D G G D D T]` thiếu cảnh `M` (ảnh/video cộng đồng). |
| 9 | `mim-sam-altman-ram-5-phan-tram` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(213 từ ≈ 61s, vượt 25–40s)* | `output/stier/mim-sam-altman-ram-5-phan-tram/final.mp4` *(chưa sinh)* | `output/stier/mim-sam-altman-ram-5-phan-tram/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `213 từ — ngoài 55-135` (`build.py:641`).<br>• **Lỗi bảng `say` & chữ số thô:** câu 1 có số `"10"` (`"cuối tháng 10 năm 2026"`) chưa có trong `say`; các khóa `"Sam Altman"`, `"Cheeky Pint"`, `"Elon Musk"` có khoảng trắng nên `spoken()` (`text.split()`) không thay thế được.<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T D G T G D T]` thiếu cảnh `M` (ảnh/video cộng đồng).<br>• **Lỗi neo chữ (`at`):** cảnh 2 (`board`, `at: 2`) có node `"máy tính cá nhân"` neo `"at": [1, "cá"]` (thuộc câu 1, trước khi cảnh 2 bắt đầu). |
| 10 | `mim-android-20-tin-nhan-tu-than` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(205 từ ≈ 59s, vượt 25–40s)* | `output/stier/mim-android-20-tin-nhan-tu-than/final.mp4` *(chưa sinh)* | `output/stier/mim-android-20-tin-nhan-tu-than/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `205 từ — ngoài 55-135` (`build.py:641`).<br>• **Lỗi bảng `say`:** khóa `"Mark Blaszczyk"` có khoảng trắng nên `spoken()` không khớp từng từ.<br>• **Lỗi thời lượng cảnh (`mix_lint`):** cảnh 4 (`board`, phủ câu 4–5, 55 từ) vượt trần `> 11s/cảnh`. Không có footage/ảnh thật (cảnh `M` duy nhất là thẻ `file`). |
| 11 | `mim-9-tren-10-ai-tu-lay-otp` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(220 từ ≈ 63s, vượt 25–40s)* | `output/stier/mim-9-tren-10-ai-tu-lay-otp/final.mp4` *(chưa sinh)* | `output/stier/mim-9-tren-10-ai-tu-lay-otp/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `220 từ — ngoài 55-135` (`build.py:641`).<br>• **Lỗi bảng `say` & chữ số thô:** câu 1 có số `"10"` (`"cuối tháng 10"`) và câu 6 có `"5.5"` (`"Claude Opus 5.5"`) chưa khớp vì khóa `"Claude Opus 5.5"` và `"Cornell Tech"` chứa khoảng trắng.<br>• **Lỗi thời lượng cảnh (`mix_lint`):** cảnh 5 (`counter`, phủ câu 5–6, 52 từ) vượt trần `> 11s/cảnh`. Không có footage/ảnh thật (cảnh `M` duy nhất là thẻ `file`). |
| 12 | `mim-ve-tinh-google-4-chip-tpu` | **BỊ CHẶN (`exit 1`)** | Chưa tạo *(195 từ ≈ 56s, vượt 25–40s)* | `output/stier/mim-ve-tinh-google-4-chip-tpu/final.mp4` *(chưa sinh)* | `output/stier/mim-ve-tinh-google-4-chip-tpu/qa_sheet.png` *(chưa sinh)* | • **Độ dài lời đọc:** `195 từ — ngoài 55-135` (`build.py:641`).<br>• **Lỗi bảng `say` & chữ số thô:** câu 1 có số `"10"` (`"Cuối tháng 10"`) chưa có trong `say`; câu 2 có `"Gemma 4"` nhưng khóa `"Gemma 4"` trong `say` chứa khoảng trắng nên số `"4"` bị lọt.<br>• **`mix_lint` (`build.py:561`):** chuỗi cảnh `[T D T G G D T]` thiếu cảnh `M` (ảnh/video cộng đồng). |

---

## 3. Tự soát tĩnh 6 hạng mục theo yêu cầu ticket cho 12 slug

Do `build.py` dừng ở dòng 641 trước khi tạo `final.mp4`, dưới đây là kết quả soát tĩnh trực tiếp trên 12 spec đối chiếu với các cổng của `motion/stier/build.py`:

1. **Thời lượng (chuẩn 25–40 s):**
   - **Không đạt ở cả 12/12 slug.** Tổng số từ hiện tại là **189–237 từ** (CK: 223–237 từ; MIM: 189–220 từ), bị cổng `55 <= nw <= 135` của `build.py` chặn cứng và nếu đọc hết sẽ dài ~55–70 giây. Cần rút gọn `lines` về khoảng **95–125 từ** để vừa qua cổng `build.py` vừa đạt thời lượng 25–40 giây.
2. **Khung 0 có đúng chữ hook không:**
   - **Đạt ở cả 12/12 slug.** Mọi `scenes[0]` đều là `kinetic` với `items[0].at = 0` và `acc = true`, khớp chính xác chữ khung đầu trong pack (`THUẾ 0% ↔ GIẢM 1.804Đ/LÍT`, `20 NĂM ↔ GIẢM 44Đ/KWH`, `SJC 140TR ↔ THẾ GIỚI 123,8TR`, `DOANH THU ≤10 TỶ · -30% THUẾ`, `LÃI -0,5% ↔ 80% GỬI NGẮN`, `MẤT 6,3 TỶ ↔ RÚT 3,64 TỶ`, `20 PHÚT MẤT 6,3 TỶ`, `01/01/2027 CẤM NHẬP MÁY CŨ`, `CHỈ DÙNG 5% THANH RAM`, `20 TIN NHẮN SẬP ANDROID`, `9/10 AI TỰ LẤY OTP`, `4 CHIP TPU QUỸ ĐẠO`). Cơ chế `hold_open` mặc định của `build.py` (`build.py:570`) sẽ giữ chữ ngay từ khung 0.
3. **Chữ có tràn hoặc bị cắt không (kiểm cổng `text_em` và `long_sub` ≤ 52 ký tự):**
   - **Đạt ở cả 12/12 slug.** Không có cảnh `kinetic` nào ép `size` thủ công vượt 980px; mọi dòng phụ `counter.sub.text`, `slam.sub` và `chart.unit` đều ≤ 45 ký tự (dưới ngưỡng 52 ký tự của `build.py:547`). Không có `counter.prefix` nào chứa chữ số hoặc dấu `~`/`≈`/`<`/`>`.
4. **Mix có đủ chữ (`T`), footage/ảnh (`M`), data viz (`D`), `board`/`cards3d` (`G`) không:**
   - **Không đạt ở cả 12/12 slug:**
     - **0/12 slug** có footage (`clip`/`vid`) hoặc ảnh (`photo`).
     - **8/12 slug** (`ck-thue-xang-0-giam-1804`, `ck-dien-giam-44-dong-20-nam`, `ck-vang-sjc-140-trieu-chenh-14-trieu`, `ck-ho-kinh-doanh-giam-30-thue`, `ck-binance-63-ty-rut-36-ty`, `mim-cam-nhap-dien-thoai-cu-2027`, `mim-sam-altman-ram-5-phan-tram`, `mim-ve-tinh-google-4-chip-tpu`) bị `mix_lint` chặn cứng vì `share["M"] == 0` (`thiếu cảnh ảnh/video cộng đồng`). 4 slug còn lại chỉ có thẻ đồ họa `file` (được `MODE` tính là `M`), không có ảnh hay clip thực tế.
     - **2/12 slug** (`ck-vang-sjc-140-trieu-chenh-14-trieu`, `ck-binance-63-ty-rut-36-ty`) thiếu hoàn toàn cảnh `G` (`board`/`cards3d`/`map`).
     - **5/6 slug CK** có 3–5 cảnh `D` liên tiếp (`chart`/`counter`/`ledger`/`timeline`/`date`), bị `mix_lint` chặn cứng (`3 cảnh liền cùng kiểu D`).
5. **Âm lượng nhạc nền (`music_gain`, `music_duck`, `sfx_gain` và true peak):**
   - Trong spec, cả 12/12 slug đều đặt đúng thông số chuẩn (`"music_gain": 0.18, "music_duck": 3, "sfx_gain": 0.36`), và `build.py` có bộ giới hạn đỉnh thật `alimiter=limit=0.78` (giữ true peak ≤ −1,5 dBTP). Chưa đo được LUFS/dBTP thực tế trên `final.mp4` vì `build.py` dừng trước bước trộn âm.
6. **Media đã tải kèm giấy phép:**
   - **Không có (0 file).** Cả 12 spec đều khai báo `"imgs": {}` và không có trường `"clip"` / `"vid"` nào trong `scenes`. Không có file nào trong `data/stier/specs/*.json` hay `motion/**` bị sửa đổi.
