# Video DÀI 16:9: hồ sơ graphic motion (kênh Hình Sự)

## Mặc định Long mới (GH-274/275/280)

Builder nhận diện topic cũ bằng `data/long/_legacy_topics.json`. Các topic ngoài danh sách nhận các mặc định sau trong bộ nhớ khi đọc spec; không tự ghi lại spec. Khóa đã khai luôn được giữ nguyên.

| Kênh | opening_gate | cine_auto | idcards | voice2 | ambience |
| --- | --- | --- | --- | --- | --- |
| CL | bật | bật | bật (dành cho #276) | Ngọc Huyền, radio | mưa, gió hoặc côn trùng khi lời chương có ngữ cảnh tương ứng |
| MIM | bật | bật | bật (dành cho #276) | giọng trích của kênh, radio | tắt |
| CK | bật | bật | bật (dành cho #276) | giọng trích của kênh, radio | tắt |

Long mới chủ ý tắt `opening_gate` phải dùng `--allow-opening` khi chạy `html` hoặc `render`. Bật gate vẫn cần nội dung mở bài qua kiểm tra. Topic cũ không tự nhận mặc định; muốn dùng `cine_auto` phải khai `"cine_auto": true`.

`cine_auto` chọn máy quay, hiệu ứng và chuyển cảnh theo seed; không ghi đè `cam`, `fx`, `frame`, `layout`, `transition_in` đã khai. Ảnh `photo`, `print`, `split` nhận chuyển động; nền ảnh của `kinetic`, `slam`, `question` có chuyển động chậm. B-roll chỉ nhận `cam: "push_in"` hoặc `"pull_out"` khi khai tay (scale tối đa 1.06). Ảnh `photo` rộng ít nhất 2:1 với `stops` đã neo hợp lệ có thể chuyển thành `pano`, trong giới hạn sáu cảnh và 25% thời lượng. Builder in tỷ lệ và cảnh báo nếu tỷ lệ ảnh có `cam` dưới 50%; cần xem nhịp thật, nhất là đoạn có ít ảnh.

Âm thanh Long mới dùng gain nhạc cơ sở 0.17, sidechain threshold 0.05, ratio 4 và ambience tăng 15 dB. Gain nhạc khai ở từng đoạn được nhân theo tỷ lệ 0.17/0.12; có thể đặt `mix_levels` theo kênh trong spec, ví dụ `"mix_levels": {"CL": {"gain": 0.2, "threshold": 0.06, "ratio": 3.5, "ambience_db": 15}}`. Thẻ chương nhả sidechain; khoảng lặng cho compressor hồi lại; `question` vẫn hạ nhạc. Sau `mix`, bộ đo lưu mức RMS các đoạn có cả giọng lẫn nhạc, gắn hash của `mix.wav`. `final` của topic mới chặn khi số đo thiếu, cũ, hoặc nhạc nhỏ hơn giọng trên 18 dB. Không có nhạc thì bỏ qua cổng này. Topic legacy giữ mức trộn cũ.

Anh em ngang của `motion/stier/` (Short dọc). Cùng ngôn ngữ hình: hồ sơ lưu trữ, tư liệu thật, một màu nhấn. Khác ở ba điểm:

- bố cục ngang 1920x1080;
- chia theo chương;
- có video B-roll Pexels và nhạc nền thật.

Bộ kỹ năng giữ chân người nghe: **[RETENTION.md](RETENTION.md)**. Nguồn tư liệu dùng tự do lâu dài: **[SOURCES.md](SOURCES.md)**. Đọc file này TRƯỚC khi viết kịch bản.

## Quy trình

Dùng python của `vietneu-tts/.venv`, vì bước TTS cần gói `vieneu`.

```
python motion/long/research_long.py yakuza "Yakuza" "Yamaguchi-gumi" "?Sugamo Prison"   # bài Wikipedia + ảnh Commons tự do ("?"= tìm ảnh)
python motion/long/media_search.py search yakuza "tattoo" --src wellcome,openverse,artic,europeana   # kho mở ngoài Commons (xem SOURCES.md)
python motion/long/media_search.py get yakuza tattoo1 X3        # tải ứng viên X3 thành ảnh "tattoo1" (tự ghi vào spec + credit)
python motion/long/media_search.py sat yakuza kobe_sat 135.15 34.66 135.25 34.72   # ảnh vệ tinh Sentinel-2 (Copernicus, ghi nguồn tự động)
python motion/long/pexels.py search yakuza "tokyo night rain" ...                      # B-roll ngang
python motion/long/pexels.py get yakuza <id> <id> ...
# viết data/long/yakuza/spec.json + ch00.json … chNN.json
python motion/long/build_long.py yakuza takes 3        # (tuỳ chọn) đọc mỗi câu 3 lần -> tts/takes.json
<.venv-video python> motion/long/stt_takes.py yakuza   # Whisper nghe lại mọi bản -> tts/transcripts.json
python motion/long/build_long.py yakuza pick           # chọn bản khớp chữ nhất -> tts/picks.json, in câu đáng nghe lại
python motion/long/build_long.py yakuza tts            # đọc giọng, cache theo từng câu (dùng picks nếu có), in thời lượng từng chương
python motion/long/build_long.py yakuza html           # ảnh, bản đồ, data.js, composition, sfx, mix từng chương
python motion/long/build_long.py yakuza render ch03 --draft   # nháp có tiếng: chNN/draft_av.mp4
python motion/long/build_long.py yakuza render         # bản thật, từng chương
python motion/long/build_long.py yakuza final          # nối chương + loudnorm -14 LUFS -> final.mp4
python motion/long/describe.py yakuza                  # mô tả: mốc chương + nguồn + ghi công ảnh/nhạc/video
```

`html` và `render` dừng lại, trước khi render, nếu một thẻ giấy có con dấu mà không bật mực, con dấu tràn khỏi thẻ, tiêu đề thẻ rộng hơn lòng thẻ, hoặc clip B-roll là HDR (`color_transfer` PQ/HLG hoặc bt.2020).

`render` kiểm tra từng composition bằng Chrome headless trước khi chạy HyperFrames: lỗi JavaScript `pageerror` chặn render, lỗi console được in để soát. Cần Node, `puppeteer-core` trong cache npx và Chrome trong `~/.cache/puppeteer`; thiếu công cụ hoặc không chạy được thì cảnh báo và bỏ qua kiểm tra trang. Sau render, ffmpeg trích ba khung ở 10%, 50%, 90%; nếu cả ba gần như giống nhau, lệnh báo video đứng hình và hủy key của chương. Hãy xem lại cảnh và render lại bằng `--force`. Cổng này cũng kiểm tra video được giữ từ cache; các cảnh cố ý gần như tĩnh có thể bị báo nhầm.

## Font và giấy phép

Các font Be Vietnam Pro, Inter, Montserrat và Playfair Display nằm trong `motion/long/fonts/`, dùng cho kiểm tra bố cục Long. Chúng được phân phối theo SIL Open Font License 1.1; thông báo bản quyền từng họ và toàn văn giấy phép nằm trong [LICENSE-OFL.txt](fonts/LICENSE-OFL.txt). Khi đưa thay đổi sang worktree hoặc clone mới, cần đưa cả các tệp `.ttf` và giấy phép vào git.

Giọng: vieneu 3.8.3, `VOICE = "Anh Khôi"` (3.8.3 đổi tên thành "Thiện Minh", tên cũ là alias, embedding y hệt).
Bước trộn áp `VOICE_FX` (highpass 70, -2dB@200, +2.5dB@3.2k, de-esser, nén 3:1) lên giọng; spec `"master": false` để tắt
(Yakuza đặt false vì bản đã đăng dùng giọng thô). Mốc chữ luôn lấy từ voice.wav thô.

## Spec

`spec.json` gồm:

- `imgs {key: "File:..."}`: nhận PD, CC0, CC BY và CC BY-SA. Không nhận NC, ND.
- `geo {tên: {countries, bbox, pins, box}}`
- `say {chữ hiển thị: cách đọc}`: ví dụ `"inagawa-kai": "Inagawa cai"`. Phụ đề vẫn giữ chữ gốc.
- `youtube {titles, summary, sources, tags}`

Mỗi chương `chNN.json` gồm:

- `hud {k, t}`
- `bgm {file, at, gain}`
- `lines[]`: mỗi phần tử là một chuỗi, hoặc `{"t": ..., "p": giây_nghỉ}`.
- `scenes[]`

Mốc thời gian dùng giống Short:

| Cú pháp | Nghĩa |
|---|---|
| `i` | đầu câu thứ i |
| `[i, "từ", n, lệch]` | lúc đọc chữ đó (lần thứ n, cộng thêm độ lệch) |
| `[i, null, 0, lệch]` | đầu câu i cộng độ lệch |

Sai chữ neo là lỗi cứng: build dừng ngay, không để lỗi lọt vào render.

## Kịch bản → dữ liệu dựng, theme noir

- `python motion/long/script_lines.py <topic>`: chuyển `data/long/<topic>/script.md` (đã duyệt) thành `lines` của từng `chNN.json`.
  `‖` = nghỉ dài, `**[DIỄN Ý]**` = trích diễn ý, `»` = lời trích, đọc bằng `QUOTE_VOICE` (Minh Đức) qua bộ lọc radio, cảnh quote có `qline` sẽ hiện sóng âm và nhãn "GIỌNG ĐỌC MINH HỌA".
  Cuối câu được phép có một dấu `{...}`. Dấu bị gỡ khỏi lời đọc. `scenes_from(lines, marks)` dựng cảnh: không dấu ra `kinetic` và được đếm để khỏi ra một video toàn một kiểu; `slam`, `quote`, `date`, `counter`, `question`, `chapter` ra đúng loại đó. `anchors.check` soi chữ neo trước khi ghi.
  Spec `"craft": true` (chỉ video mới) thì `html` / `render` / `final` từ chối câu dài hơn 35 âm tiết, cách gọi "quý vị", liệt kê quá 3 mục, chương mở không có câu hỏi, cả bài không nghỉ dài, sáu cảnh cùng loại liên tiếp, hoặc một chương không có cảnh ngắt nhịp. Video cũ không ghi cờ này.
- `spec.theme = "noir"`: khung điện ảnh 96px, phụ đề nằm trong dải đen dưới, cảnh `film: true` có nhấp nháy và tiếng máy chiếu.
- Cảnh riêng của noir: `seismo` (băng địa chấn, `hitAt`), `saint` (thẻ thánh cháy, `burnAt/burnDur/burnTo`), `paper` (trang báo mô phỏng),
  `pizzini` (giấy đánh máy + `cipher` chữ→số kiểu Provenzano), `dots` (mỗi chấm một người, `groups`), `board` (bảng ghim + dây đỏ),
  `memorial` (tên khắc đá), `calendar` (lịch xé `from/days/endAt`), `sticker` (tờ dán Addiopizzo).
- Mọi cảnh nhận `sfx: [{k: "gavel"|"bell"|"heart"|"match"|"slap"|…, at}]` để đặt tiếng tay.
- `bgm` có thể là danh sách đoạn `{file, at, gain, start, end, fin, fout}` (start/end là mốc lời) để đổi nhạc giữa chương.

## Loại cảnh (casewide.js)

| Loại | Dùng cho |
|---|---|
| `chapter` | Thẻ chương |
| `broll` | Video Pexels, có thể kèm `kin` (chữ phủ) |
| `photo` | Ảnh tràn khung, Ken Burns |
| `print` | Ảnh in cạnh khối chữ; dành cho ảnh dọc hoặc chân dung |
| `file` | Thẻ hồ sơ; dòng thông tin hiện dần theo lời đọc |
| `kinetic` | Chữ động |
| `slam` | Một dòng chữ đập mạnh |
| `question` | Câu hỏi; nhạc tắt, ẩn phụ đề |
| `counter` | Số đếm |
| `bars` | Biểu đồ cột |
| `timeline` | Dòng thời gian ngang |
| `map` | Bản đồ |
| `quote` | Trích dẫn; `dy:true` gắn nhãn DIỄN Ý |
| `org` | Sơ đồ gia đình hoặc tổ chức |
| `ledger` | Bảng kê |
| `split` | Hai ảnh đặt cạnh nhau |
| `date` | Ngày tháng |
| `cards` | Ván bài lật |
| `evidence` | Tang vật |

Nhiều cảnh nhận thêm các trường sau:

- Nền: `vid` (id Pexels, `ms` = giây bắt đầu trong clip) hoặc `bg` (ảnh).
- Lớp phủ: `label`, `tag`, `illus`, `stamp`.

Credit ảnh tự hiện theo giấy phép.

### Cảnh điện ảnh (tuỳ chọn, port từ engine gốc PR #250)

Tất cả đều tuỳ chọn: spec không khai khoá nào thì cảnh dựng y như trước. Mọi chuyển động chạy trên timeline GSAP tạm dừng (tua được); hạt dùng PRNG có hạt riêng. Không port `depth` (2.5D, cần macOS Vision).

**`pano`**: ảnh rộng (từ 16:9, vd 3240×1080) không bị cắt 16:9; máy lia ngang và TỚI mỗi điểm dừng đúng lúc lời đọc nhắc tới, ease `sine.inOut`. Cảnh dài 8–20 s (cảnh khác 2,5–9 s). Tốc độ trung bình tối đa 180 px/s ở 1080p: `build_long.py html` chặn điểm dừng quá gần nhau trong lời đọc. Mỗi điểm dừng tính một lần đổi hình ở `cadence.py`. Sàn: tối đa 6 `pano` mỗi Long và 25% thời lượng (`floor.py`). Khoá: `img`, `stops` (≥ 2, `at` tăng dần), `cam` (chỉ `push_in`/`pull_out`), `fx`, `transition_in`.

```json
{"type": "pano", "at": [12, "Khi"], "img": "wide_harbor",
 "stops": [{"x": 0.0, "at": [12, "Khi"]}, {"x": 0.55, "at": [13, "cảng"]}, {"x": 1.0, "at": [14, "tàu"]}],
 "fx": ["mist_drift"], "transition_in": "dip_black"}
```

**`photo` (và `pano`) thêm:**
- `cam` ∈ `dolly`, `push_in`, `pull_out`, `pan`, `tilt_up`: chậm, ease; thay `move`/pan ±60 px cố định khi có. Không dùng cho ảnh dọc vào khung (`frame`).
- `fx` ∈ `fog`, `dust`, `rain`, `god_rays`, `candle_flicker`, `embers`, `mist_drift`, `snow_ash` (một tên hoặc tối đa 3 trong danh sách): lớp phủ nhẹ chạy theo nhịp riêng suốt cảnh.
- `transition_in` ∈ `dip_black`, `flash_white`, `whip` (≤ 0,25 s): thay `tr`/chuyển cảnh tự xoay của cảnh đó.

```json
{"type": "photo", "at": [20, "đêm"], "img": "alley", "cam": "push_in", "fx": ["rain", "fog"], "transition_in": "flash_white"}
```

**`map` thêm `route`**: danh sách tên ghim; một đường vẽ dần qua các ghim, đoạn tới ghim k kết thúc đúng `at` của ghim k (ghim phải có trong `pins`, `at` không giảm dọc route). Khác `routes` (từng cặp from/to có mốc riêng).

```json
{"type": "map", "at": [30, "Từ"], "geo": "main",
 "pins": [{"name": "Hanoi", "at": [30, "Từ"]}, {"name": "Haiphong", "at": [31, "đến"]}, {"name": "Saigon", "at": [32, "cuối"]}],
 "route": ["Hanoi", "Haiphong", "Saigon"]}
```

## Bẫy đã gặp

- `<video>` phải được **nướng tĩnh** vào HTML. HyperFrames bỏ qua thẻ video do script tạo ra. Build tự kiểm tra clip có đủ dài cho cảnh không.
- Anh Khôi đọc "8-9-3" thành "8 đến 9 ba", nên phải viết bằng chữ. Đuôi "-kai" bị đọc thành "ki", nên cần map `say`.
- Tốc độ render khoảng 2,7 lần thời lượng thực (video 34 phút mất khoảng 90 phút).
- `motion/hf/assets/long` là junction trỏ tới `output/long`, nên ảnh và video không phải copy.
- **Bề rộng chữ phụ thuộc look.** Font của look khác `classic` rộng hoặc hẹp hơn Be Vietnam Pro / Playfair, nên `variety.LOOKS` có hệ số `kw` (chữ kinetic) và `kws` (tiêu đề `print`, câu hỏi) để `casewide.js` co giãn cỡ chữ. Thêm look mới thì bỏ file TTF vào `motion/long/fonts/`, khai trong `lint_html.KIN_FONTS`, rồi chạy `html`: lint sẽ báo dòng kinetic nào tràn khung.
- **Bản đồ có `zoom`**: nhãn ghim phóng to cùng bản đồ và bị cắt ở mép phải. Lint tính theo toạ độ ghim và báo số ký tự còn chỗ. Hai ghim sát nhau thì gộp vào một nhãn.
- Nhãn `day` của cảnh `date` dài quá 45 ký tự thì engine tự co chữ; vẫn nên viết ngắn.
- Đừng lấy bản scan giấy trắng (sơ đồ tổ chức, thông báo truy nã) làm nền cho kinetic, bars hay câu hỏi: chữ đè lên chữ. Muốn cho xem thì dùng `photo` với `frame=True`.
- Ảnh dọc trong `photo` tự vào khung (w/h < 1,25); chữ `kin` đi kèm nằm bên trái và được thu hẹp để khung không che.

## Bộ đồ nghề viết cảnh tay

- `scenekit.py`: `sc`, `kin`, `chapter`, `write` cho `data/long/<topic>/gen_scenes.py` (mẫu: `capone`, `bulger`). Ảnh khai bằng một đoạn tên `File:…` qua `find()`, không dùng số thứ tự trong `research.json`.
- `commons_find.py <topic> "từ khóa" …`: tìm thêm ảnh tự do trên Commons, ghi `commons.json` và contact sheet `csheet_N.jpg`.
- `dryplan.py <topic>`: soát mọi chữ neo trước khi thu giọng, in luôn báo cáo sàn sản xuất.
- Máy hiện tại chạy được 2–3 lệnh `render` song song (mỗi lệnh chậm đi khoảng 25%). `--draft` không nhanh hơn bao nhiêu, chỉ dùng cho chương có sketch hoặc bản đồ mới.

## Đăng: thumbnail, SEO, phụ đề, playlist

- Thumbnail: mẫu ở `thumbs/`, copy vào `motion/hf/compositions/long/` rồi render 1 khung.
  - Công thức rút từ nghiên cứu CTR: độ tương phản cao là biến mạnh nhất, tiếp theo là gương mặt hoặc hình người.
  - Chữ chỉ 0–3 từ, bổ sung cho tiêu đề chứ không lặp lại.
  - Tối đa 2–3 thành phần, không khí poster phim.
  - Luôn soi ở cỡ mobile (~200px).
  - Làm 3 bản để A/B test bằng Test & Compare trong Studio.
- `python motion/long/describe.py <topic>`: mô tả ≤5000 **byte**, gồm hook 2 dòng đầu chứa từ khóa, link xem tiếp, mốc chương, nguồn, ghi công.
- `python motion/long/srt.py <topic>`: phụ đề tiếng Việt từ mốc từng từ.
- `python motion/long/publish_long.py <topic> CL <publishAt UTC> --playlist "Tên" "Mô tả" <id…>`: chạy lần lượt các bước sau.
  1. upload private + publishAt
  2. category
  3. thumbnail
  4. phụ đề
  5. playlist mới
  - Chạy lại thì các bước đã xong được bỏ qua.

## Beat text (hiệu ứng chữ) — dùng chung Long và Short

- Engine: `motion/hf/assets/engine/beat.js` + `beat.css` (nạp trước `casewide.js` / `casefile.js`). Bộ chọn và tiếng tay nằm ở `motion/beatfx.py`.
- Mỗi dòng chữ (`kinetic.items`, `kin` phủ trên ảnh/clip) và mỗi `slam` được gán `fx` tự động khi dựng. Việc gán là tất định theo tên chương, không lặp kiểu vừa dùng:

| Loại dòng | Các kiểu |
|---|---|
| Dòng thường (cả cảnh dùng chung một kiểu) | `rise` (trồi từ mép che), `blur` (nhòe→nét), `slice` (2 nửa ghép), `drop` (rơi nảy), `pop` |
| Dòng nhấn `acc` | `marker` (bút dạ quang quét), `redact` (bôi đen rồi lộ), `stamp` (con dấu), `tape` (băng phong tỏa), `outline` (viền→đổ màu), `flicker` (neon chập chờn) |
| Dòng nhỏ `sm` | `type` (máy đánh chữ), `rise`, `blur` |
| Dòng ngắn có số | `scramble` (giải mã ký tự), `type` |
| Slam | `punch` (cũ), `glitch` (tách kênh màu), `zoom` (lao tới), `slice` (3 dải so le), `outline` |

- Muốn ép một kiểu thì ghi `"fx": "redact"` vào item hoặc slam. Riêng `"fx": "strike", "strikeAt": [i, "từ"]` gạch ngang câu "không phải X".
- `stamp` và `tape` có khung, nên chỉ được gán cho dòng ≤18 ký tự (Short: ≤12).

### Chữ động Long mới (GH-277)

Long mới bật mặc định `kinetic_auto`; Long legacy giữ bộ chọn cũ. Đặt `"kinetic_auto": false` để tắt, hoặc `true` để bật chủ ý cho topic cũ. Bộ chọn chạy sau bộ trộn cảnh; nó không tạo cảnh hoặc đổi loại cảnh. Chọn tất định theo topic, chương và thứ tự cảnh. Chạy riêng một chương cho cùng kết quả như chương đó trong lượt dựng toàn bài. Cảnh/dòng có `fx` hoặc `style` viết tay giữ lựa chọn đó.

| Khóa | Nghĩa |
|---|---|
| `fx` | Hiệu ứng chữ. Ngoài các ID cũ: `depth-parallax-words`, `kinetic-center-build`, `mask-reveal-up`, `shimmer-sweep`, `focus-blur-resolve`, `per-word-crossfade`, `stagger-from-center`, `flip`, `sync`. |
| `typestyle` | `solid`, `duo`, `editorial`, `poster`, `outline`, `gold` (`marker` chỉ ghi tay: bộ chọn không tự dùng vì vệt nền trải cả khối, nhìn như gạch ngang chữ). Gạch tự động chỉ bật với dòng có vế đối lập `X · Y` mà vế đầu có KHÔNG PHẢI, CHẲNG PHẢI, ĐỪNG hoặc SAI. Bộ chọn ưu tiên kiểu ít dùng, tránh lặp liên tiếp; gold chỉ tự chọn trên cảnh kinetic/slam có nền đã làm tối. |
| `wt`, `emw` | Mốc từng từ theo giây và chỉ số các từ nhấn (đánh số từ 0) cho `sync`. Bộ chọn tự căn nếu toàn bộ chữ khớp lời đọc trong cùng cảnh; thiếu mốc thì chọn hiệu ứng khác. Các mốc do bước căn giọng hiện có ước lượng, cần Lead so với âm thanh. |
| `autoStrike`, `strikeAt` | Tự gạch khi gặp KHÔNG PHẢI, CHẲNG PHẢI, ĐỪNG hoặc SAI. Có dấu chấm giữa thì gạch vế trước; có thể đặt mốc `strikeAt`. |

Ví dụ một item: `{"text": "KHÔNG PHẢI X · Y", "at": [1, "KHÔNG"], "fx": "flip", "typestyle": "editorial"}`. Các trường tạo tự động không ghi lại vào spec. Dòng nhỏ hoặc chữ không khớp giọng không tự chọn sync. Tên kiểu là độc lập với tên hiệu ứng: `marker` hay `outline` có thể là kiểu chữ hoặc hiệu ứng.

Lệnh `html` in phân bố theo chương và tổng lượt dựng, kèm cảnh báo nếu chương có ít hơn bốn hiệu ứng hoặc một hiệu ứng vượt 20%. Dòng viết tay luôn được giữ nên có thể làm các giới hạn không khả thi; chương có dưới bốn dòng cũng không thể có bốn hiệu ứng. Khi chỉ dựng một số chương, bảng tổng chỉ phản ánh các chương đó. Cần kiểm tra lại bảng toàn bài và hình render. Quote vẫn dùng cách gõ chữ cố định của `casewide.js`, chưa nhận hiệu ứng hoặc kiểu mới; slam viết tay dùng hiệu ứng cũ cũng không nhận kiểu mới. Các giới hạn này cần Lead xử lý trước khi coi ticket hoàn tất.

## Đa dạng giữa các video (chống "repetitive content")

Chính sách Spam của YouTube lấy đúng ví dụ "the exact same background music and repetitive AI generated imagery across many videos". Sáu Long đầu tiên (Yakuza → Tam Giác Vàng) dùng chung 13 bài nhạc và cùng một diện mạo, nên mỗi video mới phải khác các video gần đây. Nghiên cứu nằm ở `RESEARCH-million-views.md`.

- `motion/variety.py` quản lý việc này.
  - Sổ `data/variety/ledger.json` (có commit) ghi mỗi video: nhạc nền, theme, look. `publish_long.py` tự ghi sau khi upload.
  - `python motion/variety.py audit <topic>` so video với 3 video gần nhất cùng kênh. Báo lỗi khi nhạc nền trùng trên 35% (Jaccard), hoặc look giống video ngay trước.
  - `build_long.py html` in cảnh báo. `build_long.py final` **từ chối** dựng nếu chưa sửa (có thể bỏ qua bằng `--allow-repeat`).
- **Look**: ghi `"look"` trong spec. Có các look `classic | amber | steel | jade | rose | sulfur`, mỗi look là một bảng màu, một cặp font có tiếng Việt và một màu nền. `python motion/variety.py next-look` gợi ý look ít dùng nhất. Spec không ghi look thì render y như cũ (`classic`).
- **Nhạc theo mood**: trong chNN.json (hoặc gen_scenes) ghi `bgm={"mood": "tense", "gain": .12}` thay vì `"file"`.
  - Các mood: tense | dark | sad | epic | mystery | quiet.
  - Picker loại bài đã xuất hiện trong 5 Long trước cùng kênh và bài vượt 15% tổng Long sau khi thêm video này (làm tròn lên, tối thiểu 1). Sau đó tối ưu Jaccard với 3 video trước; audit kiểm cả hai luật. Ô đã chọn tay hoặc cache vẫn giữ nguyên và audit vẫn cảnh báo nếu vi phạm. Nếu hết ứng viên, picker cảnh báo và để ô chưa chọn.
  - Kết quả được cache ở `output/long/<topic>/bgm_picks.json`, nên render lại vẫn ra bài cũ.
  - Danh mục nhạc: `motion/long/music_catalog.json`. File nhạc: `output/music/`. `python motion/variety.py library` cho biết mỗi bài đã dùng bao nhiêu lần.
  - Danh mục gồm Kevin MacLeod (incompetech), Scott Buckley, Chris Zabriskie và Kai Engel; mỗi bài ghi giấy phép CC BY 3.0 hoặc 4.0 và nguồn. Mô tả ghi công theo tác giả, giấy phép và nguồn từng bài; kiểm tra giấy phép trong danh mục trước khi dùng. Lệnh library thống kê bài có file theo kênh, tác giả và liệt kê file thiếu.

## Sàn sản xuất (`floor.py`)

Một Long mới không được kém sáu Long đã đăng. `floor.py` đo kịch bản và cảnh, rồi từ chối `render` (bản thật), `final` và `publish_long.py` khi dưới sàn. `html` chỉ in cảnh báo, `render --draft` vẫn chạy để soi từng chương lúc đang viết.

| Chỉ số | Thấp nhất trong 6 Long | Sàn |
|---|---:|---:|
| Âm tiết kịch bản | 5.610 | 5.000 |
| Số chương | 12 | 10 |
| Số loại cảnh | 19 | 14 |
| Ảnh khác nhau | 49 | 40 |
| Cảnh có b-roll | 35 | 30 |
| Tỷ lệ kinetic | cao nhất 34% | tối đa 38% |
| Chữ trên nền trống | cao nhất 10% | tối đa 12% |

- `scenes_from.py` gắn `"auto": true` cho mọi câu không có dấu. Đó là bộ khung nháp; còn một cảnh `auto` là sàn chặn.
- `publish_long.py` còn đòi spec có `"approved"` (ngày và lời duyệt của chủ kênh) trước lần upload đầu.
- `python motion/long/unschedule.py <CH> <topic…> [--dry]` gỡ lịch public, giữ video private, không xóa.
- Bị chặn thì bổ sung tư liệu và kịch bản. Đừng hạ ngưỡng. Quy trình đầy đủ nằm ở `CLAUDE.md` gốc repo.

## Review mạch kể Long

Sau factcheck và trước khi Lead duyệt, chạy `python scripts/long_story_review.py <topic> [chNN ...]`; kết quả nằm trong `story_review/chNN.md`. Dùng `--dry-run` để xem prompt; người viết hoặc Lead đối chiếu các chi tiết cần xác minh trước khi áp dụng. Bước TTS cảnh báo nếu Long mới thiếu review. `script_lines.py` cảnh báo, không chặn: `RAO_NGUON` (bình nguồn dồn dập), `NHIP_DEU` (nhiều câu ngắn liên tiếp), `NHAY_MOC` (mốc xa xuất hiện sớm), `META_NGUOI_KE` (lời bình của người kể). Chỉ số câu bắt đầu từ 0.


## Họ thẻ thông tin GH-276

Long mới mặc định `idcards: true`; topic cũ không khai khóa vẫn giữ `file` cũ. Bộ chọn chạy trên toàn video, tất định theo topic và số thứ tự cảnh. Kiểu cần ảnh có thể mượn ảnh đã khai trong spec từ cảnh gần nhất trước đó trong cùng chương; ảnh mượn ghi `img_borrowed: true`, không mượn ảnh AI hoặc ảnh phim. `style` ghi tay được giữ. `hint` nhận `person`, `document`, `money`, `tech`, `place`; `spec.era` hoặc `date` chứa năm giúp lọc thời kỳ. Nếu thiếu năm, không tự đoán thời kỳ. Cảnh `file` nhận `name`, `desc`, `rows` hoặc `items`, `date`, `img`, `focus`, `cam`; các dòng có `at` như cảnh file. Chỉ đưa lên thẻ nội dung đang được đọc.

```json
{"type":"file","at":3,"name":"NHÂN VẬT","hint":"person","style":"lower_third","rows":[{"k":"BỐI CẢNH","v":"Nội dung đang đọc","at":[3,"Nội dung"]}]}
```

| Style | Kênh phù hợp |
|---|---|
| `clip_file` | CL |
| `lower_third`, `callout` | CL, MIM, CK |
| `news_clip`, `telegram` | CL, đúng thời kỳ |
| `polaroid`, `index_card`, `envelope`, `museum_label` | CL, MIM |
| `fingerprint`, `passport`, `verdict`, `wanted`, `case_divider` | CL |
| `edict_scroll`, `seal_slip` | CL cổ đại |
| `terminal`, `spec_sheet` | MIM |
| `receipt` | CK |
| `app_card` | CK, MIM |

Không dùng tên báo hay cơ quan thật, chữ ký thật hoặc số hồ sơ bịa. Chỉ `news_clip` và `telegram` mang nhãn “ĐỒ HỌA”. `lower_third`, `callout`, `polaroid`, `museum_label` cần `img` ngay trên cảnh; bộ chọn không chọn các kiểu này nếu thiếu ảnh, cổng cũng báo kiểu khai tay thiếu ảnh. `focus: [x, y]` dùng tọa độ tương đối từ 0 đến 1 trên ảnh gốc (hoặc pixel ảnh gốc), vòng khoanh và ảnh cùng chuyển động theo `cam`. `fingerprint`, `wanted`, `verdict` chỉ dùng khi cảnh ghi `"convicted": true` và `"conviction_source": "https://..."` dẫn tới nguồn kết án đã kiểm. Biên tập viên chịu trách nhiệm kiểm nguồn và ngữ cảnh; cổng không thể tự chứng minh nội dung nguồn. Kể cả kiểu khai tay, cổng vẫn chặn khi thiếu khai báo này.

Cổng sàn kiểm họ thẻ tối đa 12% số cảnh, từng kiểu tối đa 4%, không trùng một kiểu trong sáu thẻ trước và có ít nhất bốn cảnh khác giữa hai thẻ. Cổng chỉ báo lỗi, không tự xóa hay thay cảnh để đáp ứng mật độ. Nếu quá ít kiểu phù hợp, cần biên tập lại cảnh hoặc dữ liệu thời kỳ/ngữ cảnh; không ép chọn kiểu không phù hợp. Chạy `python motion/long/idcards_demo.py` tạo composition mẫu; 12 kiểu mới trước, tám kiểu vòng 2 sau, mỗi kiểu 6 giây, xem tại giây 3, 9, 15... Hai ảnh tư liệu có sẵn được nhúng trực tiếp vào demo. Không render tự động.
