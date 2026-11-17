# Giọng VieNeu, BGM và SFX theo kênh (5 kênh)

Ngày: 17/11/2026. Phạm vi: chỉ nghiên cứu và kiểm kê, không sửa mã, không tải âm thanh.
Quyết định chủ kênh (17/11): VieNeu-TTS là engine TTS duy nhất. Tài liệu này không đề xuất công cụ TTS khác.

## 0. Đọc trước: giới hạn của bằng chứng

- **Không nghe được audio của bất kỳ kênh tham chiếu nào.** WebFetch chỉ trả về khung điều hướng của trang YouTube (đã thử `@NhanQuaRadio`, `watch?v=g7BR-6hP8OM`, kênh Phong Thủy Cát Tường: không có mô tả, không có số liệu). Vì vậy mọi câu "kênh X dùng giọng/nhạc Y" dưới đây hoặc (a) đến từ trang tác giả/nhà cung cấp tôi đã mở, hoặc (b) chỉ là tiêu đề/mô tả trong kết quả tìm kiếm (ghi rõ "chỉ thấy trong kết quả tìm kiếm"), hoặc (c) là suy luận của tôi (ghi "suy luận").
- **Quan sát của chủ kênh (BUD hay dùng nhạc "thiền", FS hay dùng sáo/nhạc Hoa) chưa kiểm chứng được bằng âm thanh thật.** Bằng chứng gián tiếp duy nhất: trong kết quả tìm kiếm có các danh sách phát "Tuyệt Phẩm Đàn Tranh Sáo Trúc", "Nhạc Hoa" (tức thể loại tồn tại và có nhu cầu), và mô tả kênh "Pháp Tâm Audio" có "tụng kinh, niệm Phật, thiền âm". Chưa có trang nào cho thấy một kênh Phong Thủy cụ thể dùng sáo/đàn tranh. Cần chủ kênh hoặc agy mở 5 kênh BUD và 5 kênh FS lớn rồi ghi tay (xem mục 7, bước 0).
- Các con số về mức giọng/nhạc (18–24 dB, -14 LUFS) đến từ blog kỹ thuật, không phải chuẩn của YouTube. Dùng làm điểm xuất phát, quyết định bằng nghe mù và đo trên bản final.
- Chọn giọng VieNeu dưới đây dựa trên (1) nhãn giới tính/vùng/phong cách trong bảng preset, (2) số đo kurtosis dải trên 5 kHz trong `docs/pm/2026-10-22-cl-am-thanh-set-set.md` (mục 1b), (3) lịch sử dùng giọng trong repo. **Tôi chưa nghe lại từng giọng**; đây là giả thuyết để bài nghe mù ở mục 7 xác nhận.

## 1. Kết quả nghiên cứu Internet (rút gọn)

### 1.1 Hồ sơ giọng theo thể loại
Không tìm được nguồn có số liệu giữ chân người xem theo giọng đọc cho tiếng Việt. Những gì có căn cứ:
- True crime: các hồ sơ lồng tiếng chào bán trên voices.com lặp đi lặp lại các nhãn "deep, calm, controlled, authoritative, measured" (chỉ thấy trong kết quả tìm kiếm; đây là quảng cáo của người bán giọng, không phải dữ liệu khán giả).
- Casefile (tham chiếu quốc tế): người dẫn ẩn danh, tự làm âm thanh, nhạc và hiệu ứng cho mọi tập (trang giới thiệu của chương trình, chỉ thấy trong kết quả tìm kiếm). Nhận xét thính giả chia đôi: "bình thản, như đài phát thanh" và "đều đều, cuối câu lên giọng".
- Fall of Civilizations (tham chiếu quốc tế cho tài liệu lịch sử): các tập đầu dùng nhạc incompetech (Kevin MacLeod, CC BY); về sau có nhạc gốc của Pavlos Kapralos; có nhạc chủ đề của John Bartmann; nhận xét: nhạc ambient + tiếng môi trường + người bản xứ đọc ngôn ngữ gốc (chỉ thấy trong kết quả tìm kiếm). Đáng chú ý: một kênh tài liệu thành công từng bắt đầu bằng đúng kho nhạc MacLeod mà repo đang dùng, rồi chuyển sang nhạc gốc khi có điều kiện.
- Kurzgesagt: mỗi video có bản nhạc được soạn riêng bởi Epic Mountain (trang kurzgesagt.org, chỉ thấy trong kết quả tìm kiếm). Không xác nhận được thể loại.
- Kênh Việt: **không tìm được** nguồn nào mô tả giọng/nhạc của kênh tài chính cá nhân, phong thủy hay Phật giáo cụ thể. Chỉ có danh sách tên kênh (Nhân Quả Radio, Pháp Tâm Audio, Truyện Nhân Quả Phật Giáo, Phong Thủy Cát Tường, Phong thủy Song Hà, Tài Chính - Tâm An, Intelligent Money Podcast) mà tôi không mở được nội dung.

Hệ quả: các khuyến nghị giọng dưới đây là **suy luận có đo đạc nội bộ**, không phải "giọng đã được chứng minh thắng".

### 1.2 BGM theo thể loại và theo đoạn
Có căn cứ (đã mở):
- Routenote (true crime/mystery): lọc theo "cinematic, ambient, minimalist, electronic" và tâm trạng "tense, dark, ominous"; nhạc cụ "strings, piano, drones, percussive pulses"; điều tra sâu cần "minimal, haunting textures"; tiết lộ lớn cần "swelling, more intense arrangements"; **khi có lời chỉ dùng chất liệu khí quyển/drone, để đoạn có giai điệu cho phần mở, tóm tắt, kết**; dùng chủ đề âm nhạc lặp lại giữa các tập để tạo thương hiệu; SFX phải "không át lời".
- Quy ước theo đoạn suy ra từ nguồn trên (suy luận): cold open = một lớp drone/pulse mỏng hoặc im lặng rồi một cú nhấn; thân bài = bed tối giản, không giai điệu nổi; cao trào = thêm lớp (pulse, strings) nhưng vẫn dưới giọng, hoặc cắt hẳn nhạc 0,5–2 s rồi nhấn; kết = giai điệu rõ hơn, giải quyết, fade dài. Đây cũng là cách repo đang làm (`hf_ambience` beat `silence/hit`, `hf_sound` mood_mapping).
- Thiền/Phật giáo (chỉ thấy trong kết quả tìm kiếm): bài nghiên cứu trên Tạp chí Nghiên cứu Phật học nói tiếng chuông, mõ, tụng niệm tạo nhịp ổn định tâm; RFA liệt kê nhạc khí Phật giáo Việt Nam: chuông, mõ, khánh, trống, ốc, tang, bản mộc, thủ xích, đại hồng chung. Suy luận: chuông xoay kiểu Tây Tạng (singing bowl) không đặc trưng cho Phật giáo Bắc tông Việt Nam; chuông/mõ/khánh gần với trải nghiệm chùa Việt hơn, còn sáo trúc/đàn tranh là nhạc nền Á Đông chung.
- Phong thủy: không có nguồn nào xác nhận. Suy luận: nguồn gốc Trung Hoa, người xem Việt quen với đàn tranh/sáo trúc/nhị hồ ở vai trò "huyền bí, cổ truyền".
- Tài chính, lịch sử công nghệ: không có nguồn thể loại; blog OverseerOS (đã mở) đưa độ sâu khác nhau (mục 1.3), không nêu thể loại nhạc. Suy luận: nhạc nền nhẹ, nhịp ổn, ít giai điệu (lounge/lofi/ambient điện tử) để không tranh chú ý khi có con số.

### 1.3 Mức nhạc so với giọng, SFX, loudness
- OverseerOS (blog kỹ thuật, đã mở): nhạc thấp hơn giọng khoảng **18–24 dB** khi có lời; tài chính/kinh doanh **20–26 dB**; tài liệu/lịch sử **18–24 dB**; nhạc thưa cảm xúc 15–20 dB; thêm duck 3–6 dB khi có giọng; công thức: LUFS nhạc = LUFS giọng trừ khoảng cách. Chính blog này nói -14 LUFS không phải yêu cầu bắt buộc khi tải lên; ưu tiên là rõ lời, không clip. Tóm lược kết quả tìm kiếm khác (chưa mở): YouTube chỉ hạ âm lượng khi quá to, không nâng khi nhỏ.
- Netflix (kết quả tìm kiếm, chưa mở được trang gốc): chuẩn -27 LKFS (±2) đo theo lời thoại, true peak -2 dBFS. Chỉ dùng làm tham chiếu "anchor theo lời", không áp cho YouTube.
- Routenote: lớp SFX xây hồi hộp mà không át lời.
- Repo đã chọn: loudnorm I=-14, TP=-1.5 + limiter 0,78 (Long creator_v2), nhạc cách giọng 16–18 LU (BUD/FS), nền không khí cách giọng 26 LU. Khớp khoảng khuyến nghị, hơi gần hơn mức 20–26 của tài chính (CK).

### 1.4 Nguồn nhạc an toàn cho kênh kiếm tiền
Đã mở và xác nhận:
- **YouTube Audio Library** (support.google.com/youtube/answer/3376882): thành viên YPP được kiếm tiền; nhạc tải từ Audio Library không bị Content ID; bài giấy phép Creative Commons vẫn phải ghi công trong mô tả; có bộ lọc "Attribution not required". Chỉ nhạc trong Audio Library được YouTube coi là an toàn bản quyền.
- **Kevin MacLeod / Incompetech** (faq + youtube-contentid): CC BY 4.0, được kiếm tiền, ghi công trong **mô tả video** theo mẫu `"Tên bài" Kevin MacLeod (incompetech.com)` + giấy phép CC BY 4.0. Content ID **vẫn có thể bắn claim nhầm**: thêm ghi công vào mô tả TRƯỚC khi tranh chấp, claim thường được gỡ trong 72 giờ; có form gỡ hàng loạt và email help@incompetech.com.
- **Scott Buckley** (using-this-music): CC BY 4.0, miễn phí cả thương mại nếu ghi công; **bắt buộc ghi trong mô tả** (từ 17/04/2023, tên "Scott Buckley" viết đúng); nhạc không được đưa vào Content ID; claim còn xảy ra do nhà phát hành (Sentric) hoặc sai chính tả, có trang "Copyright Claims Release". Không ghi công = giấy phép CC không áp dụng.
- **Freesound** (faq): CC0 không cần ghi công; CC BY phải ghi công; **CC BY-NC không dùng cho video kiếm tiền**. Luôn mở trang từng âm để xem trường License.
Chỉ thấy trong kết quả tìm kiếm (chưa mở được trang): Chris Zabriskie chuyển sang CC BY (bài CC 2012), ưu tiên ghi công trên màn hình; Kai Engel có catalog CC cũ trên FMA/Bandcamp, tình trạng mới chưa xác nhận; Silverman Sound có bộ nhạc Trung Hoa (erhu, guzheng, sáo trúc) CC BY 4.0; BudgetPixel có bản guzheng CC BY 4.0 nhưng do AI tạo (cân nhắc chính sách "nội dung không xác thực" của YouTube); BigSoundBank có tiếng bát hát Tây Tạng CC0; Freesound 80578 (Benboncan, Nepalese Singing Bowl) là CC BY 4.0; TunePocket (trả phí) có bài Trung Hoa nhưng có cờ Content ID; nhiều bài thiền miễn phí đã đăng ký Content ID hoặc cấm phát 24/7.
- Chính sách YouTube 15/07/2025: "repetitious content" đổi tên thành "inauthentic content", chủ yếu là đổi tên và làm rõ; ví dụ có cả kênh dùng cùng một giọng lồng tiếng cho mọi video; mất kiếm tiền có thể áp lên cả kênh (kết quả tìm kiếm, chưa mở trang gốc). Liên quan trực tiếp đến việc luân phiên nhạc/giọng (mục 5).

## 2. Kiểm kê repo (đọc, không sửa)

Đường dẫn gốc: `D:\Tools\Youtube Creator v2\vietneu-main`. Hai pipeline âm thanh song song:
- `creator_v2/` (MIM, CK, CL; Short qua `motion/stier/`, Long qua `motion/long/`).
- Gốc repo (FS, BUD, VSD): `hf_music.py`, `hf_foley.py`, `hf_ambience.py`, `hf_sound.py`, `hf_sfx.py`, `bgm_tracks.py`, `mix_bgm.py`, cấu hình `library/channels/*.yaml`.

| Kênh | Giọng hiện tại | Nhạc (kho, nguồn) | SFX / nền | Mức trộn |
|---|---|---|---|---|
| MIM Short | Thanh Bình (chọn 12/10) | 24 bài Kevin MacLeod trong `MIM_TRACKS` (Bit Shift, Digital Lemonade, Hyperfun, Hackbeat, Funkorama, Ouroboros, Chill Wave...), sổ `data/variety/mim_music.json` 227 lượt, mỗi bài 8–12 lần | `stier/sfx.py` tổng hợp numpy (boom, thud, whoosh, tick, key, blip, pad...), 4 file CC0 trong `stier/ambience` (rain, water, bell, gong) | `music_gain` 0,16; `music_filter`: sidechain ratio 6, loudnorm -14/TP -1,5, limiter 0,78; cảnh `question` hạ nhạc về 0,12 |
| MIM Long | Thanh Bình | `motion/long/music_catalog.json`: 51 bài gắn MIM (MacLeod, Scott Buckley, Kai Engel, Chris Zabriskie; toàn catalog 155 bài) | `sfx_long` (shutter, thud, tick, boom chương, logo_lab, brand sting `brand_sting.py`), `long_ambience` (nối `hf_ambience`) | `gain` .17, threshold .05, ratio 4; ambience +15 dB trong plan; loudnorm -14 |
| CK Short | Ngọc Huyền (12/10); Xuân Vĩnh (trích), Phạm Tuyên (câu hỏi) | 26 bài MacLeod (Local Forecast Elevator, Lobby Time, Backbay Lounge, Bossa Antigua, Hep Cats, No Frills Salsa...), sổ `ck_music.json` 161 lượt, 5–7 lần/bài | như MIM Short; `logo_chart` (mallet) cho nhận diện | `music_gain` 0,14, `gap` 0,5 s giữa câu |
| CK Long | Ngọc Huyền | 47 bài trong catalog gắn CK | như MIM Long | như MIM Long |
| CL Short | Anh Khôi (alias Thiện Minh) + `VOICE_FX_CL` | pool theme `case`: nền `drone` tự tổng hợp, không bài ngoài | `sfx.py` noir | VOICE_FX: highpass 70, shelf -5 dB từ 5 kHz, lowpass 9 kHz, deesser, nén attack 15 ms |
| CL Long | Anh Khôi, trích: Minh Đức | 59 bài catalog gắn CL (Dark Times, Deep Haze, Long Note Four, Night Cave, Gathering Darkness, SCP-x..., Symmetry...) | `NoirMix`: diêm, lửa, chuông nhà thờ, búa toà, nhịp tim, tĩnh điện radio, máy chiếu phim, rumble; ambience qua `hf_ambience` | như MIM Long; doc 22/10: nhạc CL không có trên máy này |
| FS Short | Thục Đoan (Long); Short theo `hf_voice`/plan | `hf_music.SHORT_POOL['fs']`: 10 bài MacLeod + Asian Drums (11), hệ số .2; bản cắt riêng `chunks_cache/bgm_short` | `hf_sfx.Palette`: bell, bowl, chime, gong, woodblock, tick, whoosh | nhạc .2 (bud .33 cho BUD) |
| FS Long | Thục Đoan | `CATALOG['fs']` 10 bài: Eastern Thought, Ishikari Lore, Senbazuru, Eastminster, Frozen Star, Clean Soul, Shores of Avalon, Deliberate Thought, Thinking Music, Comfortable Mystery 4. **3 bài bị loại khỏi Long** (`MASKS_VOICE`: Eastern Thought, Comfortable Mystery 4, Asian Drums) -> còn 8 trong vòng xoay; mỗi video chọn 4 (`N_PICK`), tránh trùng >35% (Jaccard) với 3 video lân cận | `hf_foley` FS: bàn tính gỗ, đồng xu gieo quẻ, la bàn tách tách, cồng, **đàn tranh/ngũ âm bằng Karplus-Strong (`pluck`)**, drone; `hf_ambience` 10 loại tổng hợp | `music_gap_db` 16, duck 6 dB, `pre_payoff_duck` -10, SFX cooldown 3 s, 3 SFX/phút, target -16 LUFS Long / -14 Short, TP -1,0 |
| BUD Short | Ngọc Huyền (theme `bud`) | `BUD_TRACKS` 9 bài (Healing, At Rest, Clean Soul, Floating Cities, Fluidscape, Perspectives, Frost Waltz, Ether Vox, Arcadia); đường gốc `hf_music.SHORT_POOL['bud']` 11 bài, hệ số .33; `bud_music.json` mới có 1 lượt | chuông, mõ, gió từ `hf_sfx` | `music_gain` 0,2 (stier) / .33 (hf_music) |
| BUD Long | Thục Đoan, nhịp chậm (atempo ~0,86 ở ví dụ `hf_voice`), vang phòng nhẹ | `CATALOG['bud']` 11 bài MacLeod: White Lotus, Peace of Mind, Garden Music, Wood and Metal and Water, That Zen Moment, Ripples, Starry, Parting of the Ways 1, Meditation Impromptu 01–03; 2 bài bị loại (Parting, Wood and Metal) -> 9 trong vòng xoay | `hf_foley` BUD: đại hồng chung, bút sắt khắc lá bối, tràng hạt, bước chân, tích trượng, bấc đèn, vó ngựa, cổng; ambience dế đêm/gió/chim sớm/sông | `music_gap_db` 18, duck 6, 2 SFX/phút, mood_mapping có `drone_bud` cho "tension"; cấm trống, giọng hát, SFX điện tử |

Ghi chú kỹ thuật:
- `assets/ambience/` ở gốc repo **không tồn tại**: toàn bộ nền không khí của FS/BUD là tổng hợp numpy (CC0 theo thiết kế). `hf_ambience` cho phép thay bằng bản thu CC0/PD qua `sources.json` (chặn giấy phép khác). Trong `creator_v2/data/long/` chỉ 1/92 spec có khoá `ambience` (kind: wind, night_insects).
- Mức nhạc nền Short (`bgm_tracks.py`): mục tiêu -33 LUFS integrated sau gain, trần TP -1 dBTP; Long cũ `mix_bgm.py` -10 dB so với bài chuẩn (khoảng cách giọng/nhạc ~20 dB theo đo của tác giả).
- Hai chuẩn loudness cùng tồn tại: -14 LUFS (creator_v2) và -16 LUFS Long (`hf_sound` Preset C cho FS/BUD). Chưa rõ có cố ý không.

## 3. Khuyến nghị theo kênh

Quy ước chung: chỉ xét preset VieNeu v3 Turbo trong bảng chủ kênh cung cấp; clone giọng là chức năng của VieNeu nhưng chỉ cân nhắc với mẫu có quyền sử dụng rõ ràng, không đưa vào bài nghe mù đầu.

### 3.1 MIM (Mind in the Machine)

**(1) Giọng (top 3)**
1. **Thanh Bình** (Nam·Bắc·kể chuyện): giữ. Kể chuyện hợp phim tài liệu; kurtosis HF 3,6, hơi cao hơn Ngọc Huyền 2,2 nhưng chấp nhận được; đã có 1 Long Apollo hoàn chỉnh.
2. **Minh Đức** (Nam·Bắc·tin tức): giọng "đọc có thẩm quyền" cho đoạn số liệu, đã dùng làm giọng trích bên CL. Rủi ro: phẳng nếu đọc 25–30 phút.
3. **Hải Đăng** (Nam·Bắc·tự nhiên, mặc định): thân thiện hơn, hợp Short hơn Long.
Dự phòng: Quang Sơn (Nam·Trung, kurtosis 1,5, sạch nhất trong nhóm nam), nhưng giọng Trung có thể không hợp khán giả mục tiêu.
**Đánh giá hiện tại:** hợp lý. Chỉ cần kiểm tra mệt tai ở Long 25–30 phút (xem nghe mù).

**(2) BGM theo đoạn**
- Cold open: drone/pad điện tử tối giản hoặc im lặng rồi một nốt/hit; tránh bài nhí nhảnh (Hyperfun, Digital Lemonade, Funkorama trong pool Short).
- Thân bài: ambient điện tử chậm, ít giai điệu (nhóm "calm, curious": Chill Wave, Ice Flow; Scott Buckley/Kai Engel đã có trong catalog Long); nhạc dưới giọng 18–24 dB.
- Cao trào: thêm lớp pulse hoặc strings, vẫn dưới giọng; hoặc cắt nhạc 0,5–2 s (beat `silence` có sẵn).
- Kết: giai điệu rõ, ấm hơn (Inspired), fade dài.
- Nguồn an toàn: kho hiện có (MacLeod CC BY); YouTube Audio Library lọc "Ambient", "Cinematic", chọn "Attribution not required" để bớt nghĩa vụ ghi công; Scott Buckley (CC BY, ghi công trong mô tả). Từ khoá thử: "ambient electronic", "slow synth pad", "dark ambient", "technology documentary".

**(3) SFX/ambience:** blip/tick UI rất ngắn khi chữ lệnh terminal hiện, whoosh nhẹ khi đổi chương, hum điện từ rất nhỏ làm nền phòng thí nghiệm (`room`/`wind` của hf_ambience), im lặng có chủ đích trước câu then chốt. Tránh sci-fi quá tay (cooldown 3 s, tối đa 2–3 SFX/phút như BUD/FS).

**(4) Khoảng trống so với repo:** Short MIM dùng 24 bài, mỗi bài đã lặp 8–12 lần, nhiều bài thể loại funk/upbeat không khớp giọng kể chuyện nghiêm túc. Long có 51 bài gắn MIM nên đa dạng hơn. Khuyến nghị: tách pool Short thành "calm/curious" và "upbeat" theo format; dùng upbeat chỉ cho Short hook nhanh.

**(5) Nghe mù (xem mục 7)**: 3 giọng (Thanh Bình, Minh Đức, Hải Đăng) × 2 BGM (A: ambient điện tử tối giản; B: bài MacLeod hiện dùng).

### 3.2 CK (Biểu Đồ Biết Nói)

**(1) Giọng (top 3)**
1. **Ngọc Huyền** (Nữ·Bắc·tự nhiên): giữ. Kurtosis HF 2,2 (êm), đã là giọng chủ kênh chọn 12/10; số liệu và luật đọc nhẹ nhàng, ít gây căng.
2. **Mai Anh** (Nữ·Bắc·tin tức): hợp phần điều khoản pháp luật, số liệu, giọng "bản tin" tạo cảm giác đáng tin. Rủi ro: cứng nếu cả video.
3. **Minh Đức** hoặc **Phạm Tuyên** (Nam·Bắc): giọng nam cho bản thử khác biệt (Phạm Tuyên đang là giọng câu hỏi của CK, Minh Đức dạng tin tức).
**Đánh giá hiện tại:** hợp lý. Ghi chú: Xuân Vĩnh (giọng trích) đọc nhanh 4,1–4,6 từ/giây, đã phải thêm khoảng nghỉ 0,5 s.

**(2) BGM theo đoạn**
- Cold open: nhịp tim số liệu (một nốt, tick) hoặc lặng, để con số đầu tiên nổi.
- Thân bài: lounge/lofi nhẹ, nhịp ổn, rất ít giai điệu, nhạc **thấp hơn giọng 20–26 dB** (nguồn OverseerOS cho tài chính); repo `music_gain` 0,14 đã thấp hơn MIM.
- Cao trào (con số chốt, kết luận pháp lý): rút nhạc xuống hoặc dừng 1 s, rồi một nốt chuông/mallet (`logo_chart`).
- Kết: nhạc ấm, giải quyết; kèm câu "không phải lời khuyên đầu tư".
- Nguồn: kho CK hiện có (MacLeod); YouTube Audio Library lọc "Calm/Corporate" (kiểm tra tên bộ lọc thực tế khi mở); Chris Zabriskie (cần mở trang xác nhận giấy phép từng bài). Từ khoá thử: "lofi", "light corporate", "minimal piano", "soft electronic".

**(3) SFX:** tick/mallet khi số chạm đích, whoosh rất nhẹ khi biểu đồ vẽ, tiếng "chạm" khi mốc pháp lý hiện. Tiết chế: tài chính không giật gân.

**(4) Khoảng trống:** pool Short có bài jazz/bossa/salsa (Hep Cats, No Frills Salsa, Bass Walker) vui và dễ gây tranh chú ý khi có con số; Long có 47 bài. Khuyến nghị: lọc pool Short xuống các bài "calm/warm", để nhóm upbeat cho thumbnail/preview.

**(5) Nghe mù**: 3 giọng (Ngọc Huyền, Mai Anh, Phạm Tuyên) × 2 BGM (A: lofi/piano mỏng; B: bossa/lounge hiện dùng).

### 3.3 CL (Into The Killer's Mind / Ngoài Đời Thật)

**(1) Giọng (top 3)**
1. **Thiền Tâm Đức** (Nam·Bắc·kể chuyện): kurtosis HF 3,6 (thấp hơn Anh Khôi 5,9–6,0); kể chuyện, nên thử trước.
2. **Thái Sơn** (Nam·Nam·kể chuyện): giọng Nam bộ trầm, khác biệt rõ với MIM; chưa có số đo buzz trong repo, cần đo trước (script `set/voicem.py` trong doc 22/10).
3. **Quang Sơn** (Nam·Trung·tự nhiên): sạch nhất (kurtosis 1,5, chỉ 2,4% khung nhọn), nhưng "tự nhiên" chứ không "kể chuyện" và giọng Trung.
**Đánh giá hiện tại:** Anh Khôi = Thiện Minh có xung buzz mạnh nhất trong các giọng đo (6,0 so với 3,6 của Thanh Bình), khán giả đã phản hồi "sẹt sẹt"; chủ kênh chọn giữ giọng + bộ lọc mới ngày 23/10 (phương án B). Chưa có số liệu phản hồi sau khi sửa. Giữ Anh Khôi làm đối chứng trong bài nghe mù; nếu một giọng thay thế thắng rõ thì thay (không cần chờ).

**(2) BGM theo đoạn**
- Cold open: drone thấp + pulse chậm, hoặc lặng rồi một tiếng động hiện trường; không giai điệu.
- Thân bài: drone/texture, piano thưa hoặc dây rất khẽ (kiểu "minimal, haunting textures" theo Routenote); catalog CL đã có Deep Haze, Long Note Four, Night Cave, Lightless Dawn, Ossuary 6, Disquiet.
- Cao trào/tiết lộ: thêm lớp dây dâng hoặc pulse (Gathering Darkness, Stormfront) nhưng dưới giọng; hoặc cắt hẳn nhạc 1–2 s rồi một cú nhấn trầm.
- Kết: giải quyết buồn (Echoes of Time, Lost Time), fade dài.
- Nguồn: kho 59 bài hiện có (MacLeod); Scott Buckley, Kai Engel, Zabriskie (đã có trong catalog); Audio Library lọc "Dark", "Dramatic". Từ khoá thử: "dark ambient", "noir piano", "tension drone", "cinematic suspense".

**(3) SFX/ambience:** `NoirMix` đã đủ (diêm, lửa, chuông nhà thờ, búa toà, nhịp tim, radio, máy chiếu). Bổ sung ý: tiếng mưa/đêm rất khẽ (`rain`, `night_insects` của `hf_ambience`) dưới giọng 26 LU; tiếng bước chân và cửa dùng thưa; không lặp "boom" mỗi cảnh (doc 22/10 chẩn đoán SFX noir tạo xung dải cao).

**(4) Khoảng trống:** nhạc CL không có trên máy này (doc 22/10), chưa đo được final Long đã đăng; SFX synth có clip lác đác (đã nêu S2 trong doc, trạng thái sửa: đọc phần "Đã sửa 23/10"). Giọng vẫn là điểm yếu số 1.

**(5) Nghe mù**: 4 giọng (Anh Khôi + bộ lọc, Thiền Tâm Đức, Thái Sơn, Quang Sơn) × 2 BGM (A: drone/texture tối; B: piano thưa).

### 3.4 FS (Phong Thủy)

**(1) Giọng (top 3)**
1. **Thục Đoan** (Nữ·Nam·kể chuyện): giữ. Kurtosis HF thấp (nằm trong nhóm 0,6–1,8 của doc 22/10), êm, đã là giọng chuẩn VSD/FS Long.
2. **Ngọc Linh** (Nữ·Bắc·kể chuyện): thử giọng Bắc cho cùng nội dung; kể chuyện.
3. **Phạm Tuyên** (Nam·Bắc·tự nhiên): giọng nam "thầy" cho phần giải thích, đối chiếu giới tính.
Chưa có nguồn xác nhận khán giả FS ưa giới tính/vùng nào (không có số liệu), nên đây là điểm để A/B trên kênh (Test & Compare) sau bài nghe mù.
**Đánh giá hiện tại:** hợp lý về mặt kỹ thuật. Chưa kiểm chứng "giọng nữ Nam bộ" có hợp chủ đề phong thủy so với giọng Bắc hay nam.

**(2) BGM theo đoạn**
- Cold open: một nốt đàn tranh hoặc chuông cồng, rồi lặng; hợp ngữ cảnh "huyền bí cổ truyền".
- Thân bài: đàn tranh/sáo trúc/nhị hồ **thưa**, một lớp, tiết tấu chậm; vì lời nữ ở dải 200–3000 Hz, nên dùng EQ chừa dải giọng (cắt nhẹ 1–3 kHz của nhạc) thay vì loại hẳn bài có nhạc cụ Á.
- Cao trào (công thức, bảng tra): nhạc lùi, chỉ còn chuông hoặc cồng, rồi đọc; giữ `pre_payoff_duck` -10 dB.
- Kết: sáo hoặc đàn tranh phát triển giai điệu, fade dài.
- Nguồn: Audio Library lọc "Ambient/World/Folk" (kiểm tra tên bộ lọc khi mở); Silverman Sound bộ nhạc Trung Hoa CC BY 4.0 (erhu, guzheng, sáo trúc; chưa mở được trang, cần xác minh giấy phép từng bài); Freesound lọc CC0 với từ khoá "guzheng", "dizi", "bamboo flute", "gong"; Incompetech thử từ khoá "Asian", "Oriental" (chưa mở danh mục, chưa kiểm chứng). Tránh bài AI tạo sẵn (BudgetPixel) cho tới khi làm rõ chính sách nội dung không xác thực.

**(3) SFX:** repo đã có bàn tính gỗ, đồng xu gieo quẻ, la bàn tách tách, cồng, đàn tranh Karplus-Strong. Thêm gợi ý: tiếng mực/giấy khi hiện bảng; chuông gió rất khẽ cho "vận khí tốt"; im lặng trước "năm xấu".

**(4) Khoảng trống (quan trọng nhất):**
- Kho FS Long chỉ 8 bài trong vòng xoay, không bài nào là nhạc cụ Trung/Việt thật (Eastern Thought, Senbazuru, Asian Drums có tên Á nhưng là sáng tác của MacLeod/phương Tây, và 3 bài trong số này đã bị loại vì "lấn giọng" ở dải giữa). Nhạc FS hiện nghiêng về pad/piano phương Tây. Đây là đúng điểm chủ kênh nhận xét.
- Đàn tranh chỉ có ở dạng SFX tổng hợp (Karplus-Strong) cho điểm nhấn, không có nhạc nền Á Đông thật.
- Short FS: 11 bài, Asian Drums từng dùng cho 113 short trước 15/11 (đã sửa bằng sổ xoay).

**(5) Nghe mù**: 3 giọng (Thục Đoan, Ngọc Linh, Phạm Tuyên) × 2 BGM (A: đàn tranh/sáo trúc thưa CC BY hoặc CC0; B: pad/piano hiện dùng như Thinking Music).

### 3.5 BUD (Phật Giáo)

**(1) Giọng (top 3)**
1. **Thục Đoan** (Nữ·Nam·kể chuyện): giữ cho Long; kể chuyện, êm, đã chạy atempo chậm và vang phòng nhẹ.
2. **Thiền Tâm Đức** (Nam·Bắc·kể chuyện): tên preset trùng sắc thái, giọng nam trầm hợp lời kinh/nhân quả; kurtosis 3,6 (cao hơn Thục Đoan, cần nghe kiểm).
3. **Quỳnh Anh** (Nữ·Bắc·đọc truyện): giọng đọc truyện cho truyện ngắn; Short hiện dùng Ngọc Huyền (theme `bud`), nên Quỳnh Anh hoặc Thục Đoan cũng đáng thử cho Short để thống nhất với Long.
Dự phòng cho trích kinh: giọng thứ hai (Minh Đức hoặc Quang Sơn) giữ cơ chế `alt` của `hf_voice` để người nghe nhận ra "đây là lời kinh".
**Đánh giá hiện tại:** Short (Ngọc Huyền) và Long (Thục Đoan) khác giọng nhau: đây là điểm cần chủ kênh quyết (thống nhất hay giữ khác).

**(2) BGM theo đoạn**
- Cold open: một tiếng chuông (đại hồng chung xa, `temple_bell_far`) rồi lặng; hoặc mõ rất khẽ.
- Thân bài: pad/piano rất chậm kèm lớp sáo trúc hoặc đàn tranh thưa; không trống, không giọng hát, không SFX điện tử (đúng danh sách cấm trong `bud.yaml`).
- Cao trào (giác ngộ/đoạn then chốt): im lặng 1–2 s hoặc chuông khánh, rồi đọc.
- Kết: nhạc ấm hơn (nhóm Meditation Impromptu), fade dài, một tiếng chuông.
- Nguồn: kho BUD hiện có (MacLeod) là bước đệm; thêm nhạc cụ thật từ Audio Library "Ambient/Classical", Freesound CC0 cho chuông/mõ (kiểm trường License), BigSoundBank CC0 cho bát/chuông (chưa mở được trang). Từ khoá thử: "meditation", "zen", "ambient pad", "dizi", "guzheng", "temple bell", "mõ". Chuông xoay Tây Tạng chỉ như điểm nhấn nhẹ, không làm nhạc nền chính (suy luận về tính phù hợp với Phật giáo Việt).

**(3) SFX/ambience:** đại hồng chung, mõ, khánh, tràng hạt, bước chân, bấc đèn (repo đã có đủ, trừ mõ/khánh thật). Ambience: dế đêm, chim sớm, gió, sông; mưa nhỏ cho cảnh buồn. `drone_bud` cho "tension" có sẵn.

**(4) Khoảng trống:** 100% nhạc là MacLeod (piano/pad phương Tây); không có chuông mõ thật hay nhạc cụ Á Đông; Short dùng pool riêng (9 bài trong `stier`, 11 bài trong `hf_music`) và sổ `bud_music.json` mới có 1 mục (chưa chạy sổ xoay qua đường stier); hệ số Short khác nhau (0,2 và 0,33) giữa hai đường. Điều này khớp quan sát "BUD hay dùng nhạc thiền" ở chỗ: kênh khác nghe "thiền" nhờ tiếng chuông/sáo, còn repo hiện chỉ có piano/pad. Chưa có bằng chứng đo được là khán giả BUD ưa chuông/sáo hơn piano.

**(5) Nghe mù**: 3 giọng (Thục Đoan, Thiền Tâm Đức, Quỳnh Anh) × 2 BGM (A: pad/piano + chuông xa + sáo trúc thưa; B: White Lotus/Peace of Mind hiện dùng).

## 4. Voice cloning (ghi chú)
VieNeu hỗ trợ clone từ mẫu ngắn. Không có nguồn nào trong lần nghiên cứu này đánh giá chất lượng clone tiếng Việt, nên chưa khuyến nghị. Nếu thử: chỉ dùng mẫu của chính chủ kênh hoặc người ký thoả thuận, ghi vào ledger giọng, không dùng giọng người thật có thể gây nhầm lẫn (đúng luật Dramatize/real-person của repo).

## 5. Rủi ro Content ID và "nội dung không xác thực"
- Ghi công MacLeod/Scott Buckley trong **mô tả** (không chỉ trên màn hình); repo đã làm qua `hf_music.credit()` và `describe.py` (cần quét trước khi up, theo luật mô tả công khai).
- Claim nhầm vẫn xảy ra với cả nhạc CC (MacLeod, Buckley): quy trình = thêm ghi công vào mô tả trước, rồi dispute; Buckley còn có form gỡ claim của nhà phát hành.
- Luân phiên nhạc và giọng (chính sách YouTube nêu ví dụ "cùng giọng/cùng nhạc cho mọi video") đã được repo xử lý ở nhạc (sổ xoay, Jaccard 35%); **giọng** thì một kênh dùng một giọng cho mọi video là chuẩn, nên cần khác biệt ở kịch bản, hình và cấu trúc, không phải đổi giọng liên tục.
- Chưa mở được trang chính sách gốc của YouTube; kiểm tra lại trang Partner Program trước khi quyết định lớn.

## 6. Việc nên làm (xếp ưu tiên)
1. Bước 0 (không tốn hạn mức TTS): ghi tay 5 kênh BUD + 5 kênh FS (giọng, nhạc, chuông/sáo, mức nhạc), điền bảng vào issue; đóng câu hỏi quan sát của chủ kênh.
2. FS và BUD: thêm 4–6 bài nhạc nền Á Đông thật từ nguồn CC BY/CC0/Audio Library, chạy `hf_music` audit và đo MASKS_VOICE trước khi cho vào vòng xoay Long (đừng bỏ qua tiêu chí đã có: RMS 5 giây ≤ ~14 dB, không dồn năng lượng dải giữa).
3. BUD: thêm chuông/mõ/khánh thật CC0 vào `hf_ambience` qua `sources.json` (khoá `temple_bell_far` đã có), hiện còn tổng hợp.
4. CL: chạy lại bài nghe mù giọng; đo kurtosis các ứng viên, ưu tiên thay Anh Khôi nếu có giọng sạch hơn rõ.
5. MIM/CK Short: lọc pool theo tâm trạng, bớt bài upbeat/jazz cho các Short có số liệu.
6. Thống nhất chuẩn loudness (-14 vs -16) giữa hai pipeline hoặc ghi lý do.

## 7. Kế hoạch nghe mù (chung)

Chuẩn bị (agy hoặc Codex chạy, không tải audio ngoài, chỉ dùng kho nhạc hiện có và nhạc CC được chủ kênh duyệt):
- Bước 0: ghi tay tham chiếu như mục 6.1 (nếu chưa có).
- Chọn **một đoạn kịch bản thật, cùng nội dung** 60–90 giây mỗi kênh, đã qua lint (đoạn thân bài + một câu cao trào, không nhạy cảm).
- Render **mỗi giọng một lần** bằng VieNeu (cache theo câu), áp đúng chuỗi xử lý của kênh (CL: `VOICE_FX_CL`; các kênh khác: chuỗi chuẩn). Đặt tên file ngẫu nhiên (X1…X8), file khoá đáp án riêng.
- Trộn **2 biến thể BGM** cho từng giọng: A = đề xuất mới, B = hiện tại. Cùng mức loudnorm -14 LUFS, TP -1,5, cùng khoảng cách giọng/nhạc ban đầu 20 dB (CK 22–24 dB), để chỉ khác loại nhạc.
- Số mẫu: CL 4 giọng × 2 = 8; MIM, CK, FS, BUD 3 giọng × 2 = 6.

Người nghe và chấm:
- Chủ kênh + ít nhất 2 người ngoài (không biết đáp án), nghe tai nghe và loa điện thoại.
- Thang 1–5 cho: dễ nghe lâu (mệt tai), độ tin cậy/hợp chủ đề, rõ lời, nhạc có lấn giọng không, muốn nghe tiếp không. Chọn cặp thắng bằng điểm trung bình, hoà thì chọn giọng ít buzz hơn (đo kurtosis HF).
- Kiểm tra kỹ thuật song song: kurtosis HF (`set/voicem.py` của doc 22/10), LUFS, TP, LRA bằng ffmpeg ebur128, mức nhạc trừ giọng bằng `measure_mix_level`.

Sau chọn:
- Chạy thử 1 Long hoặc 3 Short với cấu hình thắng; theo dõi 24h/72h/7 ngày (AVP, CTR, bình luận về âm thanh), không đổi giọng/nhạc hàng loạt khi chưa có số liệu.
- Không sửa video đã đăng (luật retro).

## 8. Nguồn

Đã mở và đọc:
- YouTube Audio Library (YouTube Help): https://support.google.com/youtube/answer/3376882
- Incompetech, Music FAQ: https://incompetech.com/music/royalty-free/faq.html
- Incompetech, YouTube Content ID: https://incompetech.com/music/royalty-free/youtube-contentid.html
- Scott Buckley, Using This Music: https://www.scottbuckley.com.au/library/using-this-music/
- Freesound FAQ: https://freesound.org/help/faq/
- Routenote, music for mystery and true crime: https://licensing.routenote.com/blog/how-to-find-music-for-mystery-and-true-crime-content/
- OverseerOS, music volume under voiceover: https://www.overseeros.com/blog/background-music-volume-under-voiceover
- Tài liệu nội bộ: `creator_v2/docs/pm/2026-10-22-cl-am-thanh-set-set.md`

Chỉ thấy trong kết quả tìm kiếm (trang không mở được hoặc không đọc được nội dung; coi là chưa xác minh):
- YouTube, Pháp Tâm Audio: https://www.youtube.com/@Phaptamaudiophatgiao
- YouTube, Nhân Quả Radio: https://www.youtube.com/@NhanQuaRadio
- YouTube, Truyện Nhân Quả Phật Giáo: https://www.youtube.com/channel/UCriwpRk8FlICvXl_2PMSutQ
- YouTube, Phong Thủy Cát Tường: https://www.youtube.com/channel/UCbi-qtWvz-AW3YuchrCeVXQ
- YouTube, playlist Tuyệt Phẩm Đàn Tranh Sáo Trúc: https://www.youtube.com/playlist?list=PLzrR18Xs9hBimq04b2ISLAI732susXS-r
- Casefile, About: https://casefilepodcast.com/?p=696
- Fall of Civilizations (bản sao Wikipedia): https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/Fall_of_Civilizations_(podcast)
- Kurzgesagt, quy trình video: https://kurzgesagt.org/youtube/
- Netflix Sound Mix Specifications v1.5: https://backlothelp.netflix.com/hc/en-us/articles/360001794307-Netflix-Sound-Mix-Specifications-Best-Practices-v1-5
- Silverman Sound, nhạc Trung Hoa: https://www.silvermansound.com/royalty-free-chinese-music
- Creative Commons, Chris Zabriskie: https://creativecommons.org/2012/12/11/cc10-featured-content-jason-sigal-on-chris-zabriskie/
- BigSoundBank, tibetan bowl: https://bigsoundbank.com/tibetan-bowl-singing-s1109.html
- Freesound 80578: https://freesound.org/people/Benboncan/sounds/80578/
- YouTube inauthentic content (Plagiarism Today): https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/
- Tạp chí Nghiên cứu Phật học, thiền và chữa lành bằng âm thanh: https://tapchinghiencuuphathoc.vn/2pdf/thien-va-chua-lanh-bang-am-thanh-hieu-ve-phuong-tien-va-cuu-canh
- RFA, Âm nhạc Phật giáo: https://www.rfa.org/vietnamese/news/programs/MusicForWeekend/music-in-buddism-vhoang-04152012132656.html
