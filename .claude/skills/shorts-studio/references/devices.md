# Thiết bị hình (devices) & Khối Registry Đã Cài

Mỗi thiết bị = một nhịp (thường một câu, 2,5-6s): khung riêng, vào cảnh theo từ đầu, phát triển theo mốc lời sau, seam ra cảnh sau.
Metadata (purpose / framing / axis / circle) dùng cho luật đa dạng -- khớp giữa `devices/*.js` (`meta`) và `DEVICES` trong `studio.py`.

---

## 1. Thiết bị hình Studio cốt lõi (engine 1.x)

| Thiết bị | Mục đích | Khung · trục | Trường chính | Ghi chú |
|---|---|---|---|---|
| `hook_poster` | hook | edge-band · static | `num` (số/năm nghiêng đỏ), `kick`, `big` (**nhấn**), `markWord`, `markAt` | Khung 0 đủ nghĩa; gạch chân vẽ ở `markAt` |
| `hook_slam` | hook | edge-band · Z | `kick`, `groups:[{text, big?, at}]`, `markAt`, `allAtStart` | Mỗi nhóm một trục (Z-slam/X-snap/Y-rise); `allAtStart:true` = mọi nhóm hiện ở khung 0, tới mốc thì nhấn lại |
| `split` | compare | stacked-split · mask | `a`/`b`: `{lab, val, num, at}`, `static` | Hai vùng cắt cạnh; `static:true` làm móc |
| `myth_strike` | compare | center-hero · X | `mythLab, myth, truthLab, truth, strikeAt, truthAt` | Gạch chéo ngộ nhận, sự thật đến bằng inverse zoom |
| `window` | statement | center-hero · in-glyph | `word, fill: rain\|solid\|image, img, lab, sub, subAt, size, y` | Chữ khổng lồ làm cửa sổ; `rain` vẽ bằng code |
| `wheel` | process | center-hero · 3D · **tròn** | `labels` (mặc định 12 chi), `target, also, alsoAt, links, linkR, linkAt, linkTone, kick, tag, tagAt` | Đĩa nghiêng quay về ô đích, làm phẳng, vẽ đường tam hợp/lục hợp |
| `cycle_draw` | process | center-hero · draw · **tròn** | `kick, nodes:[{id,label,tone,at}], edges:[{from,to,kind:outer\|inner,at}]` | Ngũ hành sinh/khắc, chu trình nước, vòng kinh tế |
| `calendar` | time | card-on-field · 3D | `pages:[{head,day,wd,lun}], flips:[anchor], stamp, stampAt, stampX, stampY` | Lịch bloc lật trang + dấu son |
| `time_spine` | time | world-camera · draw | `kick, items:[{yr,label,at}]` | Trục thời gian dọc, nhãn luân phiên |
| `stamp` | statement | edge-band · X | `han, kick, big, stamps:[{text,at,x,y,rot}]` | Chữ lớn + chữ Hán mờ + dấu son đóng theo lời |
| `source_card` | evidence | card-on-field · Y | `source, ref, snippet ([[cụm sáng]]), hlAt, seal, sealAt` | Dẫn nguồn trước phán định (kinh, sách, báo cáo) |
| `ledger` | list | grid · Y | `title, head[], rows:[{y, value, from, unit, at, valueAt, cells:[{k,v,at}]}]` | Bảng tra (năm sinh -> tuổi -> sao) |
| `list_build` | list | grid · X | `title, items:[{text, sub, key, at} \| {group, at}]` | Danh sách tích lũy, mục cũ mờ dần |
| `quote` | quote | center-hero · in-glyph | `text` (mặc định = câu `line`), `mode: karaoke\|rise`, `source, sourceAt` | Karaoke theo mốc từng từ thật |
| `count_ring` | number | center-hero · count · **tròn** | `label, value, from, decimals, suffix, at, pct, note, noteAt` | Đếm + vòng; đơn vị vào sau |
| `bars` | number | grid · X | `title, unit, bars:[{label,value,at,hot}], diff, diffAt` | Thanh ngang (9:16) |
| `unit_grid` | number | grid · Z | `title, total, cols, lit:[...], litAt, unitLabel` | "k trên N" |
| `month_sheet` | time | grid · draw | `title, note, wd, weeks, goods:[{day,at}], strip, stripLab` | Tờ lịch tháng; vòng chỉ khoanh số dương |
| `thiep_cuoi` | statement | card-on-field · static | `han, eyebrow, sub, rows:[{day,am,meta,mute}], note` | Thiệp; `mute` cho hàng không có ngày |
| `close` | close | edge-band · mask | `q` (**nhấn**), `markWord, markSpan` | Câu hỏi kết, gạch chân cụm cuối |

---

## 2. Khối Registry HyperFrames đã cài sẵn

Lead đã cài đặt sẵn các khối registry chính vào `hyperframes_short/compositions/` để sử dụng trực tiếp trong dựng video:

### Danh mục khối đã cài:
1. `components/ink-bleed-reveal`: Hiệu ứng loang mực thủy mặc cho tranh hoặc chữ tiêu đề.
2. `components/text-shimmer`: Vệt sáng specular quét ngang qua dòng chữ tạo điểm nhấn cao cấp.
3. `components/grain-overlay`: Phủ hạt analog tạo chất điện ảnh (chú ý: dùng animation tìm hiểu seek-safety).
4. `components/particle-text-dissolve`: Tụ hạt hoặc làm tan chữ thành bụi vàng lấp lánh.
5. `components/constellation-hub`: Đồ thị trung tâm với các nút liên kết quay quỹ đạo (rất hợp ngũ hành, tương sinh).
6. `ui-3d-reveal.html`: Khung hiển thị giao diện / thẻ lật 3D phối cảnh.
7. `lens-flare.html`: Hiệu ứng lóe sáng quang học.

### Cách nối và sử dụng:
- Các components được nhúng trực tiếp vào composition HTML hoặc template thông qua thẻ `<template>` hoặc custom element.
- Kết nối timeline GSAP: Gọi hàm kích hoạt animation qua mốc thời gian của timeline chính:
  ```js
  // Ví dụ nối text-shimmer vào mốc 1.5s
  tl.add(playShimmer("#title-text"), 1.5);
  ```
- Hoặc kết hợp các hạt `particle-text-dissolve` vào giai đoạn hook đầu video để tạo chữ ký riêng.

### Cảnh báo kỹ thuật quan trọng:
> [!WARNING]
> **CẢNH BÁO SHADER**: Khối `lens-flare` mang thuộc tính `data-requires-webgpu data-no-timeline` với canvas shader. Bắt buộc phải render thử độc lập trước khi đưa vào lô để đảm bảo trình duyệt headless không bị crash hay drop frame.

> [!CAUTION]
> **Luật 18 (Quy định bắt buộc)**: Thợ **KHÔNG chạy `hyperframes add`** (hệ thống tự động sẽ chặn lệnh này). Khi cần khối registry mới chưa có trong danh sách trên, thợ ghi rõ tên khối vào báo cáo để Lead xem xét và cài đặt.

---

## 3. Lộ trình thiết bị ưu tiên tiếp theo (Lead phát triển)
- HOOK: `hook_search_query` (ô tìm kiếm gõ sẵn), `hook_macro_reveal` (cận cảnh $\rightarrow$ lùi ra).
- NUMBER: `num_odometer` (năm/giá cuộn từng chữ số).
- COMPARE: `cmp_balance` (cán cân gắn giá trị so sánh).
- LIST: `list_slot_ticker` (máy đánh bạc, chữ tiếng Việt giãn hàng $1,4\times$), `list_year_table` (bảng năm sinh dài tự dò).
- PROCESS: `proc_symbol_assemble` (biểu tượng ráp từng phần: sen, pháp luân, thái cực).
- PLACE: `place_floorplan` (sơ đồ nhà + la bàn xoay cho phong thủy nhà ở).
- EVIDENCE: `ev_photo_annotate` (ảnh thật tượng Phật/phù điêu + vòng chú thích tay).
