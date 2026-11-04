# GH-33 · agy: render lại 12 Short pilot (spec đã qua `--preflight`)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33.

Spec mới: `docs/pm/tickets/GH-33-assemble-report.md`. Cả 12 spec đã qua `python motion/stier/build.py <slug> --preflight` (36–37 s) và `script_lint`. Lần render trước (`GH-33-render-report.md`) bị chặn vì spec cũ quá dài; lỗi đó đã sửa.

**Slug, CK trước:**
- `ck-thue-xang-0-giam-1804`, `ck-dien-giam-44-dong-20-nam`, `ck-vang-sjc-140-trieu-chenh-14-trieu`
- `ck-ho-kinh-doanh-giam-30-thue`, `ck-lai-giam-05-tien-gui-80-ngan-han`, `ck-binance-63-ty-rut-36-ty`
- `mim-binance-20-phut-6-3-ty`, `mim-cam-nhap-dien-thoai-cu-2027`, `mim-sam-altman-ram-5-phan-tram`
- `mim-android-20-tin-nhan-tu-than`, `mim-9-tren-10-ai-tu-lay-otp`, `mim-ve-tinh-google-4-chip-tpu`

## Được ghi
- `output/stier/<slug>/**`
- trong spec, **chỉ** điền `vid` cho cảnh đang `"vid": null` có `"q"`; không đổi gì khác
- báo cáo `docs/pm/tickets/GH-33-render2-report.md`

**Không:** sửa `lines`, `title`, số liệu hay code; upload, enqueue, đổi lịch, commit; đọc credentials.

## Việc
1. **Điền clip.** Cảnh `"vid": null` thì tìm clip Pexels theo `q` bằng công cụ repo (`motion/stier/clips.py` / `find.py` / `pexels`), dọc hoặc dễ crop dọc. Không logo, không chữ đọc được, không người nhìn thẳng camera kiểu quảng cáo. CK tuyệt đối không có thương hiệu ngân hàng hay công ty. Chạy lại `--preflight` sau khi điền.
2. **Render:** `python motion/stier/build.py <slug>`, bản thật.
3. **Tờ soát mỗi bài:**
   - 20 khung → `output/stier/<slug>/qa_sheet.png`;
   - clip sheet nếu có clip;
   - đo true peak và LUFS của `final.mp4` (true peak ≤ −1 dBTP).
4. **Báo cáo tạm** ngay sau 6 bài CK, rồi làm MIM.

## Báo cáo
Bảng 12 slug: trạng thái, thời lượng, đường dẫn `final.mp4` và `qa_sheet.png`, clip đã điền, true peak/LUFS, lỗi quan sát được. Không tự kết luận "đạt"; Lead sẽ soát.
