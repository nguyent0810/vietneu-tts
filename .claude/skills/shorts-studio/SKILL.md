---
name: shorts-studio
description: Dựng short dọc 9:16 có lời đọc tiếng Việt (25-40 giây) cho BẤT KỲ kênh/chủ đề nào bằng HyperFrames -- bộ thiết bị hình (device) dùng lại được, nhiều theme, luật đa dạng chống rập khuôn, cổng QA. Dùng khi làm short mới cho kênh có sẵn (FS, BUD...) hoặc kênh mới, khi cần đổi phong cách, thêm thiết bị hình, hay port khối registry HyperFrames.
---

# Shorts Studio (HFS)

Một short = **một file spec JSON** -> `studio.py` dựng job HyperFrames (một composition, một timeline), render, trộn âm thanh, chạy QA.
Engine: `hyperframes_short/studio/` (core.js, base.css, devices/*.js, themes/*.json). Builder: `studio.py` (gốc repo).
Nền tảng nghiên cứu (đọc khi cần sâu): `references/research/` -- A quy trình, B kỹ thuật, C kho chuyển động (48 rule, 22 blueprint, 45 thiết bị),
D theme/âm thanh/phụ đề (14 theme), E registry 447 khối, F chữ động, G bố cục/ảnh, H 3D/whiteboard/biểu đồ.

## Quy trình (đạo diễn) -- làm theo thứ tự
1. **Brief**: kênh, khán giả, chủ đề, mục tiêu (search/feed), luật kênh (FS: tên chi, "tham khảo"; BUD: dẫn kinh có số hiệu, không vẽ mặt Phật).
   Số liệu năm sinh/can chi/ngày âm **tính bằng code** (canchi.py, vnlunar, build_F3), lời kinh **đối chiếu** `hf_sutta.py`.
2. **Kịch bản** 6-8 câu (`references/pipeline.md`): câu 1 <= 10 chữ và TRẢ LỜI ngay; câu 2 là thông tin cụ thể thứ hai (có số/tên),
   KHÔNG ẩn dụ (câu 2 là chỗ rơi người xem mạnh nhất: 6,7-8,1%/giây); kết bằng danh sách/câu hỏi để xem lại.
3. **Beat sheet -> chọn thiết bị** cho từng câu theo mục đích (hook/number/compare/list/process/time/quote/evidence/close) --
   `references/devices.md`. Luật: khung 0 đủ nghĩa; >= 3 khung khác nhau; không lặp khung/trục liền kề; <= 1 cơ chế tròn; ảnh stock không bao giờ
   là nội dung duy nhất của câu (chữ làm cửa sổ, chú thích, nền mờ). `references/motion-grammar.md`.
4. **Chọn theme** theo kênh (`python studio.py themes`, `references/themes.md`). Kênh mới: tạo theme JSON mới (font PHẢI có dấu tiếng Việt).
5. **Viết spec** (`references/spec.md`) -> `python studio.py build spec.json` (dry) -> sửa cảnh báo đa dạng -> `--render --qa`.
6. **QA** (`references/qa.md`): lint 0 lỗi, check ok (runtime/layout/contrast), xem `qa_sheet.jpg` từng cảnh (khung 0, giữa, seam),
   soát dấu tiếng Việt bị cắt, chữ tràn vào dải phụ đề (y >= 1490) hay vùng nút Shorts bên phải (x > 940).
7. **Giao**: mp4 + render.json ở `output/cl_staging/studio_out/` (hoặc `out` trong spec); sổ kênh `output/cl_staging/<channel>/studio_ledger.json`
   chặn lặp móc trong 3 video gần nhất. Đăng theo pipeline của kênh (riêng tư + hẹn giờ).

## Lệnh
```bash
.venv/bin/python studio.py devices      # thiết bị + metadata (purpose/framing/axis/circle)
.venv/bin/python studio.py themes       # theme
.venv/bin/python studio.py build output/cl_staging/studio_specs/<id>.json --render --qa [--strict] [--no-ledger]
```
Mẫu spec chạy được (TTS tự sinh): `.claude/skills/shorts-studio/examples/demo_fs_sinhcon.json` (tet-poster),
`demo_bud_batchanhdao.json` (saffron), `demo_sci_thangnhuan.json` (blueprint). Theme mới -> `python studio.py fonts` để tải font của nó.

## Khi nào gọi skill HyperFrames gốc (`references/hf-skill-map.md`)
- Thêm/đổi thiết bị: `/hyperframes-animation` (rule + blueprint), `/hyperframes-keyframes` (path/mask/3D), `/hyperframes-core` (hợp đồng clip, determinism).
- Tìm khối có sẵn TRƯỚC khi tự viết: `npx hyperframes@0.8.75 catalog --query "<english>" --json` (Node 22) -> port theo `references/adding-a-device.md`.
- Ảnh/video thật: `/media-use` (media-treatment CLI, không dùng CSS filter overlay); âm thanh: `/hyperframes-audio`; kiểm: `/hyperframes-cli`.
- Thiết kế theme mới: `/hyperframes-creative` (frame-presets, palettes, typography) -- nhớ đổi font không có tiếng Việt.

## Bẫy đã gặp (đừng lặp lại)
- Không tween visibility trên `.clip`/con của cảnh bằng `visibility` thô -> tua ngược làm hiện đè (lỗi lịch v3). Dùng `autoAlpha`; cảnh là clip do builder viết.
- Biến dựng trong `build()` phải trả về cho `enter()` (lỗi `aw` làm trắng cả video). Soát lỗi JS: `check` (runtime) hoặc mở job trong Browser pane + đọc console.
- Mốc thời gian âm -> GSAP dịch cả timeline. Builder đã chặn; device dùng `Math.max(0, t)`.
- `font_family_without_font_face` (font hệ thống CJK...) làm `check` bỏ qua toàn bộ soát trình duyệt -> báo "0 sample" KHÔNG phải pass.
- Font gói sẵn của HyperFrames KHÔNG có tiếng Việt. Studio dùng woff2 cục bộ (`studio/fonts/`, subset vietnamese + latin, `faces.json`); builder chép
  font của theme vào job + @font-face -> render không cần mạng. Font hệ thống (CJK) khai `local()` để lint không chặn check.
- Không bounce bừa: mọi ease qua bảng `ctx.E`; `E.pop()` chỉ nảy khi theme còn ngân sách overshoot (BUD = 0).
