# GH-143 · Báo cáo render CK Short `ck-them-10-trieu-gio-bot-mot-mon`

## Trạng thái

Preflight sau khi điền `vid` hết lỗi phối cảnh. Lệnh render bản thật thoát mã 0, nhưng hình đứng yên ở cảnh mở suốt 34,63 giây. Hai clip đã chọn không vào bản dựng. Không upload, không enqueue, không đổi lịch, không commit. Không sửa `lines`, `title`, số liệu hay code. Không đổi loại cảnh.

## Preflight

```text
python motion/stier/build.py ck-them-10-trieu-gio-bot-mot-mon --preflight
ck-them-10-trieu-gio-bot-mot-mon: OK — 108 từ, ước lượng 32.7s
```

## Render

```text
python motion/stier/build.py ck-them-10-trieu-gio-bot-mot-mon
```

Thoát mã 0 sau 181 giây. Look `blueprint`. Giọng trong `timing.json`: Ngọc Huyền. Nhạc `no_frills_salsa.mp3`, offset 120 (`output/stier/ck-them-10-trieu-gio-bot-mot-mon/music.json`). `build.py` có ghi thêm slug này vào `data/variety/ck_music.json`; sổ đó nằm ngoài danh sách được ghi nên đã trả về đúng nội dung trước lệnh render.

## Thời lượng

`final.mp4`: 34,63 giây (`ffprobe` `duration=34.633333`). Giọng 34,02 giây. Composition `dur` 34,62 giây.

## Đường dẫn

- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/final.mp4`
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/qa_sheet.png` (20 khung, `select=not(mod(n,52)),scale=300:533,tile=10x2`)
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/qa_clips.png`
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/final_sheet.jpg` (tờ build tự sinh, mỗi 2 giây)

`motion/long/clip_sheet.py` chỉ đọc `data/long/<topic>/chXX.json`, không áp vào Short này. `motion/stier/sheet.sh` trỏ ffmpeg vendor không có trên máy. Tờ clip ghép 3 khung đã cắt dọc của mỗi clip bằng ffmpeg trên PATH.

## Clip đã điền

| Cảnh | `at` | `vid` | Đã xem |
|---:|---:|---|---|
| 1 | 1 | `pexels:6288844` | Tay và giỏ đan trứng, rau mùi; 12,5 giây; không logo, không chữ, không mặt nhìn camera. Khung 0,5 / 2,5 / 5 / 8 / 11 giây. |
| 7 | 7 | `pexels:7889399` | Một nhánh súp lơ trên bàn gỗ; 14 giây; không bao bì, không logo, không chữ, không người. Khung 0,5 / 2,5 / 5 / 8 / 12 giây. |

File đã cắt: `motion/hf/assets/clips/pexels-6288844.mp4`, `motion/hf/assets/clips/pexels-7889399.mp4`. Composition không có thẻ `<video>`. `credits.json` là `[]`.

Đã loại `pexels:7246481`: giỏ ớt có túi lưới mang một nhãn tối nhỏ.

## Âm thanh

`audio_lint` của build: `TP -2.1 dBTP`.

`ffmpeg ebur128=peak=true` trên `final.mp4`:

```text
Integrated loudness:
  I:         -13.9 LUFS
True peak:
  Peak:       -2.1 dBFS
```

Mục tiêu trong brief: −14 LUFS, true peak ≤ −1 dBTP.

## Transcript STT

Build không sinh file transcript STT. Không chép thêm.

## Lỗi quan sát được

20 khung trong `qa_sheet.png` và các khung lấy tại 0,2 / 3,2 / 4,5 / 7,5 / 12,5 / 16,5 / 21 / 25,5 / 29,2 / 32,5 giây đều là cảnh mở `10 TRIỆU ↑` / `GIỎ −1 MÓN` / `VÍ DỤ GIẢ ĐỊNH`. Không thấy footage, không thấy bộ đếm CPI, không thấy thẻ, không thấy phụ đề. Chênh pixel giữa các khung chỉ ở mức hạt nền.

`casefile.js` ném `loại cảnh lạ` khi `s.type` không có trong bảng cảnh. Spec đang để `"type": "clip"`. `build.py` chỉ gắn video khi cảnh có trường `clip` dạng `pexels:<id>`, rồi ghi đè `vid` thành id thẻ HTML. Điền `vid` đủ để `mix_lint` tính hai cảnh này là M, không đủ để footage xuất hiện. Không đổi loại cảnh và không render lần hai.
