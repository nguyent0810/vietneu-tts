# Độ to đầu ra đo hai lượt và qua limiter đỉnh thật; giọng đọc theo preset C; không tăng vang hay nhạc khi chưa hỏi

Trạng thái: đã chấp nhận (01/10 cho giọng, 24/10 cho độ to; PR #29).

**Giọng.** Ngày 01/10 chủ kênh nghe ba mẫu. Mẫu A bị chê "rẹt rẹt như robot", đọc nhanh. Mẫu B vang và nhạc quá to. Preset C được chọn:

- BUD: giọng Bình, tempo .91, câu đỉnh .85–.88, vang .045; lời trích kinh dùng giọng thứ hai (Quang Sơn);
- FS: giọng Thái Sơn v3, tempo .96, không vang.

**Độ to.** Ngày 23/10 đo đầu ra Short: FS −20,8 LUFS, BUD −17,9 LUFS, đỉnh có bài tới −0,4 dBTP. Nguyên nhân là `loudnorm` một lượt, đích −14. Giọng TTS có hệ số đỉnh khoảng 18 dB (tích hợp −24,6 LUFS nhưng đỉnh đã ở −6 dBTP). Kéo lên tới đích thì đỉnh vượt 0 dB, nên loudnorm tự rơi về chế độ động và dừng sớm.

Quy trình mới trong `mux_audio`:

1. Trộn các lớp tiếng.
2. Đo độ to.
3. Tăng gain tới đích.
4. Qua `alimiter`, lấy mẫu dư 192 kHz, chặn đỉnh thật ở −1 dBTP.
5. Đo lại và bù theo cát tuyến, cho tới khi sai số ≤ 0,3 LU.

Đích: **Short −14 LUFS, Long −16 LUFS**. Đo bằng giọng thật sau khi sửa: Short −14,2, Long −16,2, đỉnh −1,3 dBTP.

## Các phương án đã cân nhắc

- **Loudnorm một lượt.** Hụt đích, như số đo trên.
- **Nén mạnh cho chạm đích.** Mất cái tự nhiên của giọng kể dài.
- **Cùng −14 cho Long.** Giọng kể 30 phút cần giữ dao động. Mức "YouTube chuẩn hoá về −14" chưa có nguồn chính thức xác nhận.

## Hệ quả

- **Nhạc nền** nén theo giọng: `duck_db`, mặc định 6 dB. Cộng với khoảng cách sẵn 15–18 dB, nhạc nằm dưới giọng khoảng 21–24 dB khi có lời.
- **Tiếng động** mặc định thấp hơn giọng 12 dB; tiếng va chạm tối đa thấp hơn 6 dB.
- **Chuông/bát ở cú lật**: chỉ đặt ở câu nghỉ ≥ 1,2 giây, cách nhau ít nhất 10 câu. Bản nháp đầu có 84 tiếng chuông trong 30 phút, quá dày.
- **Bài nhạc dễ lấn giọng** (dao động RMS > 14 dB hoặc dồn năng lượng ở dải giữa) bị loại khỏi Long (`hf_music.MASKS_VOICE`).
- Muốn đổi tiếng của video đã render thì dùng `--remix-audio`, không cần render lại hình.

## Bằng chứng

`hyperframes_bridge.py` (`LOUD_TARGET`, `normalize_loudness`), `hf_foley.py`, `hf_music.py`, `tests/test_loudness_ticket68.py`, `output/cl_staging/grok/reports/68_audio_mix_bgm_sfx.md`, commit `8efd3e1`.
