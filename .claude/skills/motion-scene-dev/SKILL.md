---
name: motion-scene-dev
description: "Thêm hoặc sửa cảnh / hiệu ứng trong kho video dài (longform.js, engine.js, hyperframes_bridge.py) mà không làm vỡ render: luật tất định của HyperFrames, các bẫy đã dính (đo toạ độ khi font chưa nạp, class trùng phụ đề, svg không giãn, fromTo hiện sớm, transform bị ghi đè), cách thử bằng showreel và hf_qa. Dùng khi cần một loại sơ đồ/bố cục/chuyển cảnh mới cho video dài."
---

# Viết cảnh mới cho kho video dài

## Nơi đặt
- Sơ đồ: `visuals.<type> = { build(inner, ln, i, ctx), enter(tl, inner, ln, ctx) }` trong
  `longform.js`; đăng ký `VISUAL_TYPES` trong `hyperframes_bridge.py`. `ctx.until` = giây
  kết thúc khoảng sơ đồ; `when(ctx, step, fallback)` ra thời điểm của `at`/`word`.
- Bố cục ảnh: `layouts.<name> = { build, enter?, enterCont?, motion?(tl, clip, ln, mEnd) }`
  (motion trả true = tự lo chuyển động clip); thêm vào `MEDIA_LAYOUTS` (+ `LAYOUT_POOL`).
- Biến thể: `variantOf("<họ>", spec, [...])` — bộ chọn lo luân phiên.
- CSS: `longform.css`; màu theo biến `--lf-*` (nền giấy ghi đè trong `inkwash_long.html`).
- Bộ style bổ sung (#258: woodcut, papercut, oneline, film16, blueprint, pencil): `longform_styles.js` + `.css`,
  nạp SAU longform.js ở 7 style Long, `register(name, def)` chỉ THÊM khoá mới vào `HF_LONG.visuals`. Opt-in, trần
  3 cảnh/video, không liền nhau (`hyperframes_bridge.style_scene_issues`). Font của style phải là họ KHÁC font kho
  đã nạp (khai báo @font-face kép làm lệch raster chữ cảnh cũ). Kiểm: `python hf_style_demo.py stills|determinism|regress <compositions của main>`.

## Luật tất định (HyperFrames tua tới từng khung rồi chụp)
- Mọi chuyển động nằm trên `tl` đã pause. Không `Math.random` (dùng `HF.rng(HF.hashSeed(..))`),
  không `Date`, không mạng lúc render (địa lý nướng sẵn bằng `hf_geo`).
- Trạng thái thay đổi liên tục (hạt, số đếm, shader): MỘT tween tiến trình + `onUpdate`
  tính từ `t` — không đặt tween ở thời điểm âm, không `tl.call`.

## Bẫy đã dính (đừng lặp)
| Triệu chứng | Nguyên nhân | Cách đúng |
|---|---|---|
| Phần tử hiện lơ lửng từ giây 0 | `fromTo` vẽ trạng thái đầu ngay lúc dựng | CSS mặc định ẩn + `tl.set` + `tl.to` |
| Dạ quang/nét vẽ lệch chữ | đo `getBoundingClientRect` khi font chưa nạp | phần tử CON của thứ được đánh dấu, đặt bằng `inset`, SVG viewBox 0..100 |
| Chữ trích dẫn trắng trên giấy | class `.w` trùng chữ phụ đề trong base.css | đặt tiền tố riêng (`qw`, `lf-*`) |
| Nét vẽ tay chỉ còn vệt ngắn | `<svg>` tuyệt đối với left+right không giãn | ghi rõ `width/height` |
| Nét thành chấm 1px | `non-scaling-stroke` làm dash theo pixel | lộ dần bằng `clipPath` / mặt nạ `conic-gradient` |
| Thẻ tên nhảy khỏi ghim | tween `x` ghi đè `translate(-50%)` | chỉ tween opacity, hoặc tween phần tử con |
| Chữ dựng đứng từng ký tự | `display:grid` cho chuỗi span | grid chỉ khi cần chồng lớp |
| Ảnh full-frame loé qua lớp giấy | crossfade hai khung giống hệt | tráo cảnh tức thì trong cùng nhóm |
| Phụ đề chìm trên ảnh (nền giấy) | bóng tối dưới ảnh + chữ mực tối | `--lf-shade` màu giấy |
| Chữ dính liền ("SƠĐỒ") | khoảng trắng cuối inline-block bị bỏ | `margin-right` thay khoảng trắng |
| Xoay/phóng SVG sai tâm | `transformOrigin` tính theo bbox phần tử | `svgOrigin: "x y"` |
| Chữ lớn gãy giữa từ ("KHU/ẤY") | ký tự tách span rời, trình duyệt ngắt ở bất kỳ đâu | gom ký tự vào `.wd` (`inline-block; nowrap`) theo từ |
| QA báo chữ nhỏ thiếu tương phản dù màu khai báo đủ | `check` đo điểm ảnh; nét mảnh 18px bị khử răng cưa nhạt đi | chọn màu dư ~7:1 cho chữ nhỏ (footer giấy `#2b2620`) |
| Cùng mốc t ra hai khung khác nhau tuỳ thứ tự seek (10/11, clip gạch chéo `pencil`) | `fromTo` có thuộc tính CHỈ trong `from` (`attr.x`) -> GSAP lấy giá trị hiện tại lúc khởi tạo làm đích | mọi thuộc tính có mặt ở cả `from` lẫn `to`, hoặc đặt tĩnh lúc dựng và chỉ tween thứ thay đổi; kiểm bằng `hf_style_demo.py seekorder` |

## Thử
1. `node --check longform.js`; test tĩnh trong `test_hf_longform.py` cho luật mới.
2. Thêm cảnh vào `hf_showreel.py`, render `HF_QA=1 HF_KEEP_HTML=1 python hf_showreel.py looks [c]`.
3. `hf_qa` phải ĐẠT (WCAG AA ≥ 4.5:1, không lỗi bố cục/runtime); phát hiện cố ý thêm vào
   `hf_qa.ALLOW`.
4. Rút khung ở đầu, giữa, cuối mỗi cảnh; NHÌN trước khi dùng cho video thật.
