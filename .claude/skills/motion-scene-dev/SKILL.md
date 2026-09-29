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

## Thử
1. `node --check longform.js`; test tĩnh trong `test_hf_longform.py` cho luật mới.
2. Thêm cảnh vào `hf_showreel.py`, render `HF_QA=1 HF_KEEP_HTML=1 python hf_showreel.py looks [c]`.
3. `hf_qa` phải ĐẠT (WCAG AA ≥ 4.5:1, không lỗi bố cục/runtime); phát hiện cố ý thêm vào
   `hf_qa.ALLOW`.
4. Rút khung ở đầu, giữa, cuối mỗi cảnh; NHÌN trước khi dùng cho video thật.
