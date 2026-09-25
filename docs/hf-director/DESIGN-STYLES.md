# Bảng phong cách hình cho ba kênh

Tài liệu tra cứu, không phải quy định. Mục đích: khi muốn thêm một style mới
thì biết nó hợp kênh nào, vướng gì, và có sẵn khối nào để lắp — thay vì bàn
lại từ đầu.

## Ba kênh, ba tông

| Mã | Kênh | Tông (theo `domain_creative_profiles.json`) | Neo hình ảnh |
|---|---|---|---|
| `CL` | Hình Sự / pháp lý | khách quan, thận trọng, **không suy đoán/kết tội khi chưa có bản án**; nhịp dựng **nhanh và căng**, 10–15 giây/beat | tài liệu trung tính, tông trầm thật, **không bạo lực đồ hoạ** |
| `FS` | Phong Thuỷ / huyền học phương Đông | gần gũi, dễ hiểu, tôn trọng truyền thống, **không mê tín hoá/thổi phồng** | tranh mực Á Đông, nhấn vàng ấm |
| `BUD` | Phật giáo / tâm linh | trang nghiêm, tôn trọng; nhịp chậm, chiêm nghiệm | sơn dầu số, tông đất trầm ấm |

Lưu ý quan trọng đã ghi trong profile CL: nhịp của CL **không được** mượn kiểu
"chậm rãi chiêm nghiệm" của BUD. Đã từng sai đúng chỗ này một lần.

## Năm style đã dựng (đang chạy cho CL)

| Style | Cái nhìn | Chuyển cảnh | Skin phụ đề |
|---|---|---|---|
| `dossier` | Hồ sơ mật — đen sâu, đỏ máu `#c1121f`, thẻ hồ sơ, bụi trôi | zoom-through + mờ | `karaoke` — từ đang đọc vàng trơn |
| `interrogation` | Phòng thẩm vấn — một vũng đèn, chữ giữa khung, đèn chập chờn `#8fb8d8` | focus pull | `pill` — từ đang đọc trong viên thuốc accent |
| `vhs` | Băng ghi hình — CRT, timecode chạy, tách màu RGB `#45d483` | glitch | `rgb` — tách màu đỏ/xanh |
| `casemap` | Bản đồ điều tra — lưới bản vẽ, dây nối vẽ dần `#38bdf8` | dạt ngang + mờ | `slab` — cả dòng trên nền tối, gờ accent, canh trái |
| `night` | Hiện trường đêm — mưa, đèn vàng `#f59e0b`, chữ có bóng nước | loé sáng | `glow` — từ đang đọc phát sáng ấm |

Lịch đang chạy: **mỗi ngày một style**, 5 short trong ngày dùng chung → cả ngày
trông như một tập phim, phân biệt làn nội dung bằng nhãn kicker chứ không bằng
màu. Tám ngày với năm style thì ba style phải lặp; đủ chín style là hết lặp.

## Hai loại màn

Mỗi câu narration là một màn, và có **hai loại màn khác hẳn nhau**:

| Loại | Khi nào | Style cung cấp |
|---|---|---|
| **Màn thẻ** | mặc định | `buildScene` + `enter` |
| **Màn video** | câu có `media` trong plan | `buildMediaScene` + `enterMedia` |

Màn video **không phải** màn thẻ có dán thêm clip. Clip nằm ở lớp dưới cùng
(phủ kín khung, nướng tĩnh vào HTML), rồi mỗi style tự quyết cắt khung thế
nào, che tối bao nhiêu, nhãn gì, chữ đặt đâu:

| Style | Xử lý màn video |
|---|---|
| `dossier` | Ảnh tư liệu kẹp khung trắng + băng dính hai góc, slug đánh số hồ sơ |
| `interrogation` | Chỉ thấy phần lọt vào **vũng đèn**; ngoài vùng sáng nuốt vào đen |
| `vhs` | Băng chạy **toàn khung** + scanline + vệt nhiễu trôi + `▶ PLAY` |
| `casemap` | Ảnh **ghim trên bảng**, viền polaroid, nghiêng nhẹ, có đinh ghim |
| `night` | Toàn khung sau **mưa và quầng đèn vàng**, tem accent |

Kèm Ken Burns trên chính thẻ `<video>` (scale 1 → 1.12) — clip đứng yên sáu
giây là ảnh tĩnh biết nhúc nhích.

Hai luật cứng: **một câu không được vừa có figure vừa có clip** (cùng chiếm
vùng giữa khung), và **tiêu đề màn video phải nằm trên y≈1390** — dưới mức đó
là vùng phụ đề, đã đè nhau một lần.

## Hai mươi phong cách — xếp theo kênh

### Nên làm cho CL

| Style | Vai trò | Có sẵn gì để lắp |
|---|---|---|
| **Swiss Design** | Lane điều luật — lưới nghiêm, số liệu là nhân vật chính | Ngôn ngữ figure hiện tại (ngưỡng/dải/sơ đồ) vốn đã là Thụy Sĩ |
| **Editorial** | Lane hồ sơ vụ án — bố cục tạp chí điều tra | `lower-third-bild`, `news-ticker` trong registry |
| **Minimalism** | Bài một ý — một câu, một con số, nền trống | Rẻ nhất để render, dễ đọc nhất trên điện thoại |
| **Collage Art** | Lane vụ án — giấy, băng dính, dấu mộc | `freeze-frame-dressing` (giấy + băng dính + flash) |
| **Handwritten** | Lane vụ án — ghi chú điều tra viên | Họ `hw-*`: `hw-frame`, `hw-text-cloud`, `hw-pipeline`, `hw-title` |
| **Glass Morphism** | Lane lừa đảo — giao diện app, thẻ kính mờ | `liquid-glass-widgets`, `liquid-glass-notification` |

### Hợp FS / BUD hơn

- **Aurora** → BUD (dải sáng chậm, thiền) · `aurora-drift` có sẵn
- **Bohemian**, **Victorian** → BUD (hoa văn, giấy cũ, tông đất)
- **Retro** → FS (lịch cũ, giấy ngả vàng, mực in lệch)
- **Vector Art** → FS (hình bát quái, ngũ hành, la bàn vẽ nét)

### Không dùng cho cả ba

**Pop Art · Y2K · Graffiti · Maximalism · Pixel Art · Clay** — đặt cạnh "Điều 134:
cố ý gây thương tích" thì thành cợt nhả; đặt cạnh nội dung Phật giáo thì thiếu
tôn trọng.

**Surreal · Futuristic** — đụng thẳng lằn ranh ADR-0002: kênh pháp luật không
dựng hình siêu thực về vụ việc có thật.

**Cyberpunk** — nằm ở ranh giới. Có thể hợp *riêng* lane lừa đảo qua mạng, nhưng
`Glass Morphism` phục vụ cùng mục đích mà không ồn ào bằng.

## Bốn ràng buộc kỹ thuật

**1. Dấu tiếng Việt — giết nhiều style nhất.** Đã phải **bỏ Oswald** khỏi
`dossier` vì không chắc phủ đủ `ơ ư đ ậ ẫ ợ`. Pixel Art, Graffiti, Victorian,
Y2K sống bằng font hiển thị mà phần lớn **không có bộ dấu tiếng Việt** — chữ sẽ
mất dấu hoặc rơi về font khác giữa câu. **Kiểm font trước khi chọn style.**

**2. Tất định.** Engine cấm `Math.random`, `Date.now`, `repeat: -1`. Graffiti /
Collage / Maximalism sống bằng cảm giác ngẫu nhiên — làm được, nhưng phải qua
PRNG có seed (`HF.rng`), không phải ngẫu nhiên thật.

**3. Thời gian render.** Style thuần CSS/SVG ~85 giây/video. Style có shader
WebGL (Aurora, Futuristic, Cyberpunk) nặng hơn đáng kể — 5 video/ngày thì được,
một đợt 40 video thì phải tính lại.

**4. Khổ dọc.** Phần lớn block trong registry viết cho 1920×1080. Chỉ vài block
gắn nhãn `vertical`/`portrait` là sẵn khổ dọc (vd `flowchart-vertical`).

## Thêm một style thế nào

Một file trong `hyperframes_short/compositions/<tên>.html`:

```js
window.HF_STYLE = {
  buildScene(inner, ln, i, n, { rand, V }) { /* thẻ/khối của style */ },
  enter(tl, inner, ln, i, { rand, V })     { /* entrance, fromTo */ },
  transition(tl, oldScene, newScene, T)    { /* cảnh ra + cảnh vào CÙNG mốc T */ },
  ambient(tl, DUR, { rand, V, root })      { /* nền, hạt, đèn, progress */ },
};
HF.build();
```

Thêm vào `STYLES` trong `hyperframes_bridge.py` (file + accent), đặt class
`skin-*` cho `#capzone`, xong. Engine lo scene, phụ đề karaoke, figure, audio.

Nhớ: phần tử bên trong figure/scene phải đặt **tên class riêng** — `.cap` đã là
class của dòng phụ đề, dùng lại sẽ thừa hưởng nhầm (đã dính một lần: hai nhãn
của figure `range` chồng lên nhau vì trùng tên `.cap`).
