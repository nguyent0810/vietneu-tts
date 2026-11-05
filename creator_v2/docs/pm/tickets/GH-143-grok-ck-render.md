# GH-143 · Grok: render và tờ QA cho Short `ck-them-10-trieu-gio-bot-mot-mon`

Issue: https://github.com/nguyent0810/vietneu-tts/issues/143. Spec đã qua `script_lint` và `--preflight` (`docs/pm/tickets/GH-143-codex-ck-spec-report.md`).

**Hạn:** 60 phút. Slot lên sóng là 19:00 VN.

## Được ghi
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/**`
- Trong spec, **chỉ** điền `vid` cho cảnh đang `"vid": null` có `"q"`. Không đổi gì khác.
- Báo cáo `docs/pm/tickets/GH-143-render-report.md`.

**Không:**
- sửa `lines`, `title`, số liệu hay code;
- upload, enqueue, đổi lịch;
- commit;
- đọc credentials;
- chạy hai render cùng lúc.

## Việc

### 1. Điền clip
- Với mỗi cảnh `"vid": null`, tìm clip Pexels theo `q` bằng công cụ repo (`motion/stier/clips.py` / `find.py`). Clip phải dọc hoặc crop dọc được.
- Không logo, không chữ đọc được, không biển hiệu, không bao bì có thương hiệu, không người nhìn thẳng camera kiểu quảng cáo.
- Chạy lại `python motion/stier/build.py ck-them-10-trieu-gio-bot-mot-mon --preflight` sau khi điền.
- Lần preflight trước báo "thiếu cảnh ảnh/video cộng đồng; cảnh thuần chữ 41% (> 35%)" vì hai cảnh clip còn `vid: null`. Điền xong mà preflight vẫn báo LỖI phối cảnh thì **dừng**, ghi vào báo cáo, không tự đổi cảnh khác.
- Muốn chạy `script_lint.py` thì dùng `PYTHONPATH=.` (lỗi import đã biết).

### 2. Render
`python motion/stier/build.py ck-them-10-trieu-gio-bot-mot-mon`: bản thật, giọng mặc định của kênh CK.

### 3. Tờ soát
- 20 khung → `output/stier/ck-them-10-trieu-gio-bot-mot-mon/qa_sheet.png`.
- Clip sheet nếu có clip: `motion/long/clip_sheet.py` hoặc `motion/stier/sheet.sh`.
- Đo true peak và LUFS của `final.mp4`. Mục tiêu: −14 LUFS, true peak ≤ −1 dBTP.
- Chép transcript STT nếu build có sinh, để Lead so với `lines`.

## Báo cáo
- Trạng thái.
- Thời lượng.
- Đường dẫn `final.mp4`, `qa_sheet.png`, clip sheet.
- Clip đã điền (id).
- True peak và LUFS.
- Lỗi quan sát được.

Không tự kết luận "đạt"; Lead soát. Câu trả lời cuối: tối đa 3 dòng.
