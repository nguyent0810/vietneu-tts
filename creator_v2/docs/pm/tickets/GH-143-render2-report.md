# GH-143 · Báo cáo render lần 2 · `ck-them-10-trieu-gio-bot-mot-mon`

## Trạng thái

Lệnh render thoát mã 0 sau 128 giây (đồng hồ tường 129 giây). Hình đổi cảnh trong 34,63 giây. Giây 1 vẫn là cảnh mở, vì cảnh đó chạy từ 0 đến 2,8 giây. Không upload, không enqueue, không đổi lịch, không commit. Không sửa spec, `lines`, hay code.

`build.py` ghi slug này vào `data/variety/ck_music.json` (bài `no_frills_salsa.mp3`). Sổ đó nằm ngoài danh sách được ghi, nên đã trả về đúng byte trước lệnh. Hash `data/variety/short_looks.json` trước và sau lệnh giống nhau.

Look `blueprint`. Giọng trong `timing.json`: Ngọc Huyền. `voice.wav` và `timing.json` giữ mtime 14:09, trước lệnh này. Nhạc `no_frills_salsa.mp3`, offset 120 (`music.json`).

Log mediafit:

```text
pexels:6288844 720x1280 (dọc) -> ô win-band 1080x600: đặt trọn hình trên nền nhoè (cắt mất nếu phủ: 69%)
pexels:7889399 720x1366 (dọc) -> ô win-band 1080x600: đặt trọn hình trên nền nhoè (cắt mất nếu phủ: 71%)
```

Composition (gitignored) có hai thẻ video: `pexels-6288844.win-band.mp4` từ 2,600 giây trong 3,740 giây, và `pexels-7889399.win-band.mp4` từ 27,580 giây trong 3,860 giây. `audio_lint`: `TP -2.1 dBTP`. `qa_blank`: 0 đoạn trống ≥ 1,0 giây.

## Thời lượng

`final.mp4`: 34,63 giây (`ffprobe` `duration=34.633333`, 1039 khung, 30 fps, 1080×1920). Giọng 34,02 giây. Composition `dur` 34,62 giây.

## Đường dẫn

- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/final.mp4`
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/qa_sheet.png` (20 khung, 3000×1066, `scale=300:533,tile=10x2`)
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/qa_t01.png` đến `qa_t32.png` (9 khung kiểm, rộng 720)
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/final_sheet.jpg` (tờ build tự sinh, mỗi 2 giây)

`qa_clips.png` có mtime 14:14, trước lệnh này. Lượt này không dựng lại tờ đó.

Tờ `qa_sheet.png` lấy khung 0, 55, 109, 164, 219, 273, 328, 382, 437, 492, 546, 601, 656, 710, 765, 819, 874, 929, 983, 1038. Thời điểm tương ứng: 0 / 1,83 / 3,63 / 5,47 / 7,30 / 9,10 / 10,93 / 12,73 / 14,57 / 16,40 / 18,20 / 20,03 / 21,87 / 23,67 / 25,50 / 27,30 / 29,13 / 30,97 / 32,77 / 34,60 giây.

## Khung đã lấy

Mốc là số khung `giây × 30`.

| Giây | File | Nhìn thấy |
|---:|---|---|
| 1 | `qa_t01.png` | Cảnh mở: `10 TRIỆU ↑`, `GIỎ −1 MÓN`, `VÍ DỤ GIẢ ĐỊNH`. Phụ đề `triệu,`. |
| 4 | `qa_t04.png` | Dải clip giỏ đan, tay và trứng, rau. Nhãn `VIDEO MINH HOẠ` ở mép trái vùng nhoè. `SỐ DƯ TĂNG` rõ. `GIỎ KHÔNG TỰ LỚN` còn mờ, phía dưới. Phụ đề `nhưng giỏ hàng không`. |
| 8 | `qa_t08.png` | Bộ đếm `5,09%`. Nhãn `CPI CÙNG KỲ · THÁNG 10/2026`. Dòng `CỤC THỐNG KÊ · T10/2026`. Phụ đề `CPI tháng mười tăng`. |
| 12 | `qa_t12.png` | Tiêu đề `VÍ DỤ GIẢ ĐỊNH`. Thẻ chưa vào. Phụ đề `bạn có 250 triệu,`. |
| 16 | `qa_t16.png` | Bộ đếm đang chạy `258 TRIỆU`, nhãn `SỐ DƯ MỚI`, dòng `VÍ DỤ GIẢ ĐỊNH · LÃI 10 TRIỆU`. Phụ đề `triệu,`. |
| 20 | `qa_t20.png` | Tiêu đề `VÍ DỤ GIẢ ĐỊNH · GIỎ CŨ/MỚI` và một thẻ `GIỎ NĂM NGOÁI` `250.000.000Đ`. Phụ đề `ngoái giá 250 triệu,`. |
| 24 | `qa_t24.png` | Đủ hai thẻ: `GIỎ NĂM NGOÁI` `250.000.000Đ` và `GIỎ NĂM NAY` `262.725.000Đ`. Tiêu đề ở trên thẻ. Phụ đề `263 triệu.` |
| 28 | `qa_t28.png` | Dải clip một nhánh súp lơ trên mặt gỗ, hai bên nền nhoè. Khoảng chữ dưới dải còn trống. Phụ đề `Muốn vừa tiền,`. |
| 32 | `qa_t32.png` | Câu kết đang gõ, mới thấy `SỐ DƯ`. Phụ đề `Số dư lớn hơn`. |

Trên tờ soát, ngoài 9 mốc trên:

- 5,47 giây: giỏ hàng, `SỐ DƯ TĂNG` và `GIỎ KHÔNG TỰ LỚN` tách dòng, nét rõ.
- 7,30 giây: bộ đếm đang ở `4,98%`; 9,10 giây: `5,09%`.
- 12,73 giây: một thẻ `SỐ DƯ BAN ĐẦU` `250 TRIỆU`. 14,57 giây: thêm thẻ `LÃI MỘT NĂM` `4%`. Tiêu đề `VÍ DỤ GIẢ ĐỊNH` ở trên hai thẻ.
- 16,40 và 18,20 giây: `260 TRIỆU`.
- 25,50 giây: `2.712.619 ĐỒNG`; 27,30 giây: `2.725.000 ĐỒNG`, nhãn `KHOẢN THIẾU`, dòng `VÍ DỤ GIẢ ĐỊNH · 2.725.000Đ`.
- 30,97 giây: súp lơ, `NHẤC MỘT MÓN` / `ĐỂ VỪA SỐ DƯ`, nhãn `VIDEO MINH HOẠ` mép trái vùng nhoè.
- 32,77 giây: `SỐ DƯ` và `SỨC MUA CHƯA TĂNG`. 34,60 giây: `SỐ DƯ TĂNG` / `SỨC MUA CHƯA TĂNG`.

## Âm thanh

`ffmpeg ebur128=peak=true` trên `final.mp4`:

```text
Integrated loudness:
  I:         -13.9 LUFS
True peak:
  Peak:       -2.1 dBFS
```

`audio_lint` của build: `TP -2.1 dBTP`.

## Lỗi quan sát được

`freezedetect` (`n=0.003`, `d=0.8`) thấy các đoạn giữ khung: 1,43–2,6 giây (1,17 giây), 8,1–9,57 giây (1,47 giây), 9,8–10,7 giây (0,9 giây), 17,23–18,8 giây (1,57 giây), và từ 33,43 giây tới hết file (log không in `freeze_end`).

Clip hiện trong dải ngang giữa khung (`win-band`), hình dọc đặt trọn, hai bên là nền nhoè. Spec ghi `"win": "top"`.

Ở giây 4, dòng `GIỎ KHÔNG TỰ LỚN` còn mờ. Ở giây 12 mới có tiêu đề, thẻ chưa vào. Ở giây 20 mới có một thẻ giỏ. Ở giây 28 clip súp lơ đã có, chữ dưới dải chưa vào. Ở giây 32 câu kết mới gõ `SỐ DƯ`.

Nhãn `VÍ DỤ GIẢ ĐỊNH` đọc được trên các khung có dòng đó, nằm trên thẻ khi thẻ đã vào. `VIDEO MINH HOẠ` nằm ở mép trái vùng nhoè của dải clip. Phụ đề là cửa sổ vài chữ ở đáy khung.

Chưa thấy chữ tràn khỏi mép khung trên các khung đã mở.
