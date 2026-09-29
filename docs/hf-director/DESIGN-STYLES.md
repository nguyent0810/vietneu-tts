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

## Năm style đã dựng cho BUD

Năm trường phái điện ảnh khác nhau, dựng để thử chứ chưa chốt cái nào. Cả năm
đều bỏ karaoke từng từ — chữ nhảy theo từng tiếng đọc là nhịp của kênh hình sự,
đặt vào nội dung Phật giáo thì thành sốt ruột.

| Style | Trường phái | Accent | Skin phụ đề |
|---|---|---|---|
| `inkwash` | Thuỷ mặc — giấy dó, vệt mực, khoảng trống là một phần bố cục | `#8c2f22` | `skin-ink` |
| `oilpaint` | Sơn dầu — nét cọ dày, tông đất, ánh vàng | `#c9a227` | `skin-paper` |
| `silence` | Tĩnh vật — gần như không chuyển động, để chữ tự thở | `#6b7f72` | `skin-still` |
| `lightfield` | Trường sáng — sáng đổ chậm qua khung, không có vật thể rõ | `#d8a657` | `skin-still` |
| `dustbeam` | Chùm bụi — cột sáng và hạt bụi trôi, như trong chánh điện | `#e0b872` | `skin-still` |

## Lớp ảnh và video

Nguồn: **Pexels** (Pixabay dự phòng) — ảnh/clip free-to-use, qua `stock_image.py`
và `resolve_media()`. Mọi truy vấn phải đi qua `broll_query_sanitizer` của
domain; **đọc không được sanitizer thì không gửi truy vấn**.

Ba luật riêng của BUD, nằm trong `hyperframes_bridge.py`:

- **Một house grade chung** (`HOUSE_GRADE["BUD"]`): `saturate(.84) contrast(1.05)
  sepia(.14) brightness(1.03)`. Khi số ảnh tăng lên, thứ quyết định "đẹp" không
  phải hiệu ứng trên từng ảnh mà là **cả loạt cùng một tông**. Ảnh tượng Phật
  từ mười nguồn khác nhau, cùng một grade, mới ra một cuốn phim.
- **`FORBIDDEN_TREATMENT["BUD"]`**: cấm glitch, pixelate, halftone, dither,
  chromableed, tapedamage, crtcurvature, scanlines, invert, hue-rotate.
- Không đặt chữ đè lên mặt tượng, không cắt ngang mặt tượng.

### Bốn kiểu hiện ảnh (`reveal`)

Khai trong plan: `{"kind": "image", "query": "...", "reveal": "ink"}`.

| `reveal` | Hình | Nhịp |
|---|---|---|
| `ink` | Vệt mực loang từ một điểm (mask `feTurbulence` có seed) | chậm, 2,6 s — đây là *hiệu ứng*, phải thấm chậm mới ra chất mực |
| `wipe` | Dải mềm quét xuống, như kéo tấm lụa | 1,9 s |
| `iris` | Vòng tròn mềm mở ra từ giữa | 2,0 s |
| `rise` | Dải mềm dâng từ dưới lên — đối cực của `wipe` | 1,9 s |

`ink` **chỉ dùng cho style nền giấy** (`PAPER_STYLES` = `inkwash`, `oilpaint`).
Đặt lên style nền tối thì mask để lại một mảng sáng lem nhem trên nền đen —
đọc ra là lỗi render, không phải thư pháp. Bridge chặn thẳng.

Ba kiểu sau là **chuyển cảnh**, không phải hiệu ứng: mở từ `0%` với
`power1.inOut` thì mỗi màn có gần một giây giấy trống, đọc ra đúng là "đơ".
Nên chúng bắt đầu ở 14–16% với `power2.out` — hiện ngay rồi lắng lại.

**Không** làm reveal bằng `filter` hay `scale`: `filter` đang chở house grade,
`scale` đang chở Ken Burns. Animate chồng lên chúng là xoá bảng màu, hoặc tranh
thuộc tính với tween khác.

### Chữ trên khung hình: theo dòng nội dung, không theo style

Dòng chữ trên cùng (`kicker`) cho người xem biết **đây là loại bài gì**, giống
`HIỂU ĐÚNG LUẬT` / `CẢNH BÁO LỪA ĐẢO` bên CL. Kênh Phật giáo chia theo lane
(`SERIES_LANES` trong `hyperframes_bridge.py`, khai `"lane"` trong plan):

| lane | chữ | dạng bài |
|---|---|---|
| `niem` | CHÁNH NIỆM | cảm xúc, thói quen hằng ngày |
| `phap` | HIỂU ĐÚNG PHẬT PHÁP | giải một khái niệm / một hiểu lầm |
| `doi` | TU GIỮA ĐỜI THƯỜNG | gia đình, quan hệ, công việc |
| `tuong` | BIỂU TƯỢNG PHẬT GIÁO | tượng, thủ ấn, Bồ Tát |
| `diatang` | KINH ĐỊA TẠNG | series kinh |

**Tên style không bao giờ lên hình.** THUỶ MẶC, ÁNH SÁNG, TĨNH LẶNG là quyết
định dựng của mình, không phải thông tin cho người xem. Badge của BUD để
trống; badge của CL vẫn giữ vì ở đó nó mang số điều luật hay kiểu lừa đảo.

### Ngôn ngữ phim, không phải ngôn ngữ phóng sự

Năm style BUD **không có nhãn tư liệu**. "HÌNH MINH HOẠ" đặt dưới mỗi khuôn
hình biến cả video thành phóng sự minh hoạ, trong khi thứ cần đạt là một đoạn
phim. Đã bỏ hẳn `mv-slug` khỏi cả năm.

Kênh **CL thì giữ** (`ẢNH TƯ LIỆU`, `TANG VẬT 01`, `GHI HÌNH 01/05`): ở đó nhãn
không phải trang trí mà là lời nói rõ rằng ảnh stock chỉ mang tính minh hoạ cho
một vụ án có thật — không phải ảnh hiện trường. Cùng tinh thần với ADR-0002.

Kèm một lớp điện ảnh phủ **cả video** (chỉ BUD, `#cine` trong `base.css`):

- **Hạt phim** — nhiễu `feTurbulence` seed cố định, nhảy từng nấc bằng
  `steps()` chứ không `Math.random`. Đặt `overlay` vì nó nhân với độ sáng nền
  (`2·b·s`), nên phải để opacity `.26`: ở `.075` chênh lệch chỉ cỡ 1/60 mức
  xám, đo ra có mà mắt không thấy.
- **Quầng sáng** — radial `screen` rất nhạt ở vùng tâm.
- **Máy chạy chậm hơn**: Ken Burns `1.12` → `1.075` và biên ngang còn 0,6 lần.
  `1.12` trong sáu giây là cú đẩy thấy rõ, hợp nhịp căng của CL; ở nhịp chiêm
  nghiệm nó làm khuôn hình bồn chồn.

Một lớp cho cả video chứ không vá từng màn — vá từng chỗ thì mỗi màn một chất,
mất luôn cảm giác cùng một cuộn phim.

### Style tối cần xử lý màn ảnh riêng

`dustbeam` là một cột sáng trong bóng tối. Ảnh stock tràn kín khung, sáng đều,
phá đúng cái làm nên style. `.mv-veil` khoét một vùng sáng hình bầu dục ở giữa
và nuốt mép vào đen — ảnh trông như được chùm sáng rọi tới, thay vì như một
tấm hình dán đè lên.

Cùng một luật với `.mv-mat` của inkwash: **màn che phải có sẵn, không fade từ
0**. Fade từ 0 nghĩa là ảnh loé ra sáng kín khung một nhịp rồi mới bị nuốt mép.

### Nối màn

Khung tự bật/tắt thẻ media theo `data-start` — tức là **cắt cứng**, trong khi
mọi thứ còn lại đều chuyển mềm. Đó là cú khựng. Engine fade `opacity` bằng GSAP
(hợp lệ trên `.clip`; chỉ `display`/`visibility` là cấm), và `dur_media =
dur + 0.6` để thẻ chưa bị gỡ khi cú fade chưa chạy xong.

Cú fade-out phải **xong trước** điểm kết câu (`ln.end - .45`, dài `.45`), không
muộn hơn. Clip nằm **dưới** `#stage`, nên khung giấy của cảnh mới là thứ giữ nó
trong khuôn; cảnh tan mà ảnh còn thì ảnh tràn ra kín khung, mất hẳn bố cục. Đã
dính đúng lỗi này một lần, và chỉ nhìn ra khi soi frame ở cỡ thật.

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

## Kênh Phong Thuỷ (`fs`)

| lane | chữ trên cùng | style | khung giờ UTC |
|---|---|---|---|
| `tuoi` | TUỔI & CON GIÁP | `hongchi` | 04:30 |
| `nguhanh` | NGŨ HÀNH · CAN CHI | `laban` | 08:00 |
| `kinhdich` | KINH DỊCH | `inkwash` | 12:00 |
| `nhao` | PHONG THỦY NHÀ Ở | `oilpaint` | 15:00 |
| `lich` | LỊCH HOÀNG ĐẠO | `laban` | 23:00 (= 6h sáng VN, nói về chính ngày đó) |

- **`laban`**: nền chàm đêm, vòng khắc la bàn vẽ bằng SVG quay rất chậm; màn ảnh
  nhìn qua mặt kính tròn viền vàng. **`hongchi`**: sơn mài đỏ, khung cắt giấy vàng
  hình học; màn ảnh trong ô vòm. Không vẽ quẻ hay chữ Hán trong nền -- ký hiệu
  thật chỉ đến từ thư viện biểu tượng.
- **Sơ đồ** (`kind: "asset"`): ngũ hành, bát quái lấy từ `assets/symbol_library`,
  hiện nguyên hình giữa ô cửa (tâm 540, 720), không grade.
- **Phụ đề `skin-gold`** giữ bám theo giọng đọc -- bài phong thuỷ là tra cứu.
- **Viết kịch bản**: mọi lời dặn phong thuỷ đi kèm framing "theo quan niệm" *và*
  lý do thực tế; không khẳng định tuyệt đối (hồ sơ FS: "không mê tín hoá").

### Lịch ngày: KHÔNG tin `vnlunar` cho thần trực và trực

Đối chiếu 7 ngày (29/09–05/10/2026) với ngaydep.com và quy tắc truyền thống:
`vnlunar` **đúng** ngày âm, Can Chi, giờ hoàng đạo, tuổi xung; **sai 7/7** ở thần
trực (`12_gods` lệch hai bậc), sai trực (cả `12_constructions` lẫn `12_stars`),
sai nạp âm, và `day_type` tính hoàng/hắc đạo theo *tên trực* chứ không theo thần.
Quy tắc đúng: Thanh Long khởi theo tháng (Dần/Thân→Tý, Mão/Dậu→Dần, Thìn/Tuất→
Thìn, Tỵ/Hợi→Ngọ, Tý/Ngọ→Thân, Sửu/Mùi→Tuất); Trực Kiến rơi vào ngày trùng chi
tháng. Số liệu đã kiểm chứng: `output/cl_staging/fs/calendar_facts_verified.json`.
