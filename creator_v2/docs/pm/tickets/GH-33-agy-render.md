# GH-33 · agy: render 12 Short pilot tin nóng tuần 45 và lập tờ soát

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33. Spec đã qua `script_lint` (0 lỗi) và đã được Lead review: `docs/pm/tickets/GH-33-specs-report.md`.

**Slug, CK trước (lên sóng sớm hơn):**
- `ck-thue-xang-0-giam-1804`
- `ck-dien-giam-44-dong-20-nam`
- `ck-vang-sjc-140-trieu-chenh-14-trieu`
- `ck-ho-kinh-doanh-giam-30-thue`
- `ck-lai-giam-05-tien-gui-80-ngan-han`
- `ck-binance-63-ty-rut-36-ty`
- `mim-binance-20-phut-6-3-ty`
- `mim-cam-nhap-dien-thoai-cu-2027`
- `mim-sam-altman-ram-5-phan-tram`
- `mim-android-20-tin-nhan-tu-than`
- `mim-9-tren-10-ai-tu-lay-otp`
- `mim-ve-tinh-google-4-chip-tpu`

## Được ghi
- `output/stier/<slug>/**`: tải ảnh/clip, giọng, render
- tờ soát trong `output/stier/<slug>/`
- báo cáo `docs/pm/tickets/GH-33-render-report.md`

**Không:** sửa `motion/**`, `hf_batch_render` hay code engine; upload, enqueue, đổi lịch, commit; đọc credentials. Thấy lỗi spec thì ghi vào báo cáo, không tự sửa nội dung lời đọc hay số liệu. Lỗi neo chữ hoặc thiếu media thì được sửa trong spec, rồi ghi rõ đã sửa gì.

## Việc
1. **Render.** Lần lượt từng slug: `python motion/stier/build.py <slug>`, bản thật, không `--draft`. Thiếu ảnh/clip thì tải theo hướng dẫn mà build in ra (`motion/stier/clips.py`, `grab.py` / `pexels`).
2. **Tờ soát mỗi Short:**
   - 20 khung đều nhau: ffmpeg `select=not(mod(n,STEP)),scale=300:533,tile=10x2`, ghi ra `output/stier/<slug>/qa_sheet.png`;
   - clip sheet nếu có clip: `motion/long/clip_sheet.py` hoặc cách tương đương cho Short. CK: clip không được có logo, ticker hay tên công ty đọc được.
3. **Tự soát và ghi vào báo cáo, mỗi slug:**
   - thời lượng (25–40 s);
   - khung 0 có đúng chữ hook không;
   - chữ có tràn hoặc bị cắt không;
   - mix có đủ chữ, footage, data viz, board/cards3d không;
   - âm lượng nhạc nền có lấn giọng không (đo LUFS hoặc true peak của `final.mp4`, true peak ≤ −1 dBTP);
   - lỗi nào thấy được.
4. Render CK xong là ghi báo cáo tạm ngay, để Lead soát CK trước. Sau đó làm tiếp MIM.

## Báo cáo
Bảng 12 slug: trạng thái, thời lượng, đường dẫn `final.mp4` và `qa_sheet.png`, lỗi; media đã tải kèm giấy phép.
