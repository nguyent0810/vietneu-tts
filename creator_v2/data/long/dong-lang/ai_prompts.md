# Danh sách AI Prompts cho đề tài Tôn Điện Anh — Vụ án Đông Lăng Đạo Mộ 1928 (slug: dong-lang, kênh CL)

Được tạo theo yêu cầu Ticket GH-228, quy chuẩn `docs/codex/long-rules.md` và `docs/pm/tickets/GH-228-donglang-research-agy.md`.
Các prompt phục vụ Nhóm B (Tái dựng bối cảnh) và Nhóm C (Minh họa khái niệm).

Quy tắc bắt buộc:
- Tuyệt đối không vẽ khuôn mặt nhận diện được của nhân vật lịch sử (Tôn Điện Anh, Từ Hi Thái Hậu, Càn Long, Phổ Nghi, Tưởng Giới Thạch, Tống Mỹ Linh, Đới Lạp, Tống Tử Văn, Hà Ứng Khâm, Diêm Tích Sơn...). Con người chỉ là bóng lưng từ xa, bóng đổ, hoặc ở ngoài tiêu cự.
- Tuyệt đối không vẽ chữ Hán, chữ số, ấn triện, dấu mộc, văn bản chỉ dụ giả, giao diện hay logo.
- Tuyệt đối không vẽ cảnh bạo lực đẫm máu, hành quyết, hoặc cận cảnh nổ mìn chi tiết; chỉ dùng khói bụi mờ ảo, bóng đêm, ánh nến, rương hòm, đường hầm tối.
- Khung hình chuẩn: 16:9 (1920x1080), full-bleed.
- Phong cách: Cinematic historical editorial, photoreal lighting with subtle film grain, muted 1920s Republican era aesthetic (palette: lam xám, đen huyền, hoàng kim mờ, huyết dụ ngọc).
- Các prompt video (`vid_NN.mp4`) dùng cho công cụ tạo video Flow (chuyển động cực chậm, camera drift tĩnh, không giật hình).
- Đã tra cứu kho tài nguyên chung (`library/tools/assets.py` tag `cl`/`hinh_su`): Tận dụng các tài nguyên chung sẵn có (`lib198b/ai_18.png`, `lib198/ai_57.png`, `lib198v/vid_11.mp4`), kết hợp với tối đa 16 ảnh mới và 6 clip mới dưới đây.

---

## ai_01.png — CH00: Dãy núi Mã Lan trong đêm tối và sương mù 1928
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A remote, desolate mountain ridge of Malan Mountain in northern China during a dark cloudy midnight in July 1928. Heavy low-hanging atmospheric fog rolling across rugged jagged cliffs and pine silhouettes. Faint distant glow of military camp lanterns muted by mist. Low-key dramatic lighting, deep charcoal blue shadows contrasted with muted slate grey and cold moonlight, mysterious and ominous atmosphere. Avoid readable text, letters, Chinese characters, logos, recognizable faces, modern elements. No human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ Hán, mặt người, công trình hiện đại.

## ai_02.png — CH00: Lối vào hầm mộ ngầm thâm nghiêm trong bóng đêm
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Deep subterranean stone tunnel leading toward an ancient imperial tomb entrance, circa 1928. Massive weathered limestone blocks carved with faint eroded relief patterns. Low-key dramatic lighting from a single flickering handheld kerosene lantern casting long dramatic shadows against wet stone floor. Dust motes floating in cold subterranean air. Grim, tense, atmospheric silence. Avoid readable text, calligraphy, seals, letters, logos, recognizable human faces. Only a distant soldier silhouette from behind holding a lantern.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ Hán, ấn triện, mặt người, cảnh nổ mìn bạo lực.

## ai_03.png — CH00: Ánh sáng đèn bão lướt qua rương báu vật cổ
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual metaphor of looted imperial fortune. An antique heavy wooden chest bound with oxidized iron straps forced slightly open on a damp stone floor. Soft warm lantern light grazing the cracked lid, illuminating the rim of antique jade carving and unpolished natural pearls without revealing modern coins. Mysterious museum-grade chiaroscuro lighting, deep cavernous shadow gradients. Avoid readable text, numbers, legible coin inscriptions, Chinese characters, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ, số trên tiền, mặt người.

## vid_01.mp4 — CH00: Bụi khói mờ ảo trôi qua vòm đá hầm mộ cổ
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera drift. Smooth macro drift inside a dark subterranean vaulted stone chamber. Fine white limestone dust and faint smoke gently swirling through cold moonlight beams penetrating from a breach above. Somber, eerie stillness, atmospheric particles catching subtle rim light. Ultra-smooth slow cinematic motion, shallow depth of field. Avoid readable text, modern structures, explosions, blood, recognizable faces.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ, tiếng nổ, mặt người, cảnh bạo lực.

## ai_04.png — CH01: Cán cân công lý và chiếc hòm sắt phong ấn
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual metaphor of suppressed justice and imperial theft. A vintage heavy iron lock and heavy chains wrapped around an antique lacquered archive casket. In the soft background out of focus, an antique brass balance scale tipped heavily to one side. Moody chiaroscuro lighting, deep mahogany and dark steel tones, cold editorial feel, generous negative space on one side for infographic text. Avoid readable text, numbers, letters, logos, watermarks, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ, số, mặt người.

## vid_02.mp4 — CH01: Ánh sáng nến quét qua trang hồ sơ lưu trữ cũ
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera glide. Slow macro camera glide across an antique weathered wooden desk in a quiet archive room. A flickering candle flame casting warm amber light across yellowed blank parchment paper, vintage magnifying glass, and a pair of vintage brass calipers. Deep moody shadows, cinematic historical true-crime atmosphere. Avoid readable text, letters, Chinese calligraphy, printed words, recognizable faces.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ đọc được, mặt người.

## ai_05.png — CH02: Quán rượu sòng bạc ven đường thời Dân Quốc sơ kỳ
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Interior of a dimly lit, weathered rural gambling den in Henan province, early 1910s. Heavy worn wooden tables, dice cups, clay liquor jugs, hazy tobacco smoke hanging thick under exposed dark wooden roof beams. Low-key amber lantern light cutting through hazy darkness. A few indistinct silhouettes of men viewed from behind in traditional worn Republican cloth tunics. Gritty historical atmosphere. Avoid readable text, Chinese characters, gaming board text, recognizable faces, violence.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ Hán, mặt người, cảnh ẩu đả bạo lực.

## ai_06.png — CH02: Khói thuốc phiện lơ lửng bên bàn gỗ cũ
- Prompt (tiếng Anh): cinematic historical editorial still, painterly-photoreal with subtle film grain, full-bleed 16:9. Conceptual visual of underworld trade and illicit opium paste. An antique dark wooden side table with a vintage bronze oil lamp with tiny burning flame, a slender plain bamboo pipe resting beside a small unglazed ceramic paste pot. Thin translucent ribbon of smoke curling upwards into deep shadow. Muted antique sepia and deep umber palette, contemplative gloomy tone. Negative space for graphics. Avoid readable text, letters, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ, mặt người, cảnh tiêm chích.

## ai_07.png — CH03: Đoàn xe tải quân sự mờ xa trong bụi mù chiến trận
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A convoy of vintage 1920s open-back military supply trucks traversing a dry dirt mountain road in northern China, summer 1928. Heavy dust clouds billowing behind the wheels in the golden late afternoon sun. Distant soldiers with vintage canvas caps standing in the truck beds seen only as small indistinct silhouettes from far away. Desaturated olive drab, khaki and dusty beige palette. Gritty documentary cinematic style. Avoid readable text, license plates, military insignia, banners with writing, recognizable faces.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ số, biển số xe, cờ hiệu có chữ, mặt người.

## vid_03.mp4 — CH03: Bánh xích xe quân sự và bóng lính tuần tra trong sương sớm
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera drift. Slow ground-level camera drift alongside a muddy dirt road at dawn. Indistinct silhouettes of 1920s Chinese warlord infantry soldiers marching steadily in the distance through morning mist, rifles slung over shoulders, seen from behind. Cold muted slate and pale gold dawn sky, heavy historical documentary tone. Smooth cinematic motion, shallow depth of field. Avoid readable text, unit numbers, insignia, recognizable faces.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ, mặt người, súng chĩa vào ống kính.

## ai_08.png — CH04: Cổng rào quân sự dã chiến phong tỏa con đường núi
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A military checkpoint and barbed wire roadblock cutting across a misty mountain pass road leading to imperial tombs, July 1928. Wooden barricades, sandbag revetment, a vintage canvas tent under ancient pine trees. A single sentry viewed from behind in silhouette in 1920s National Revolutionary Army uniform standing in the drizzle. Tense military blockade atmosphere, cold damp grey palette. Avoid readable text, signs with writing, banners, logos, recognizable faces.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ viết trên biển báo, mặt người.

## ai_09.png — CH05: Vòm cổng đá ngầm đóng kín dưới tầng hầm sâu
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Massive subterranean marble imperial gateway deep inside an ancient tomb underground palace. Enormous double stone doors intricately carved with weathered Buddhist reliefs, sealed tightly shut with heavy stone sill. Cold blue-grey ambient lighting with a warm spotlight rake illuminating the textured marble grain and ancient masonry seams. Ominous, grand, fortress-like underground architecture. Avoid readable text, calligraphy, modern elements, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ Hán, mặt người, cảnh phá hoại chi tiết.

## vid_04.mp4 — CH05: Dòng nước ngầm tĩnh lặng phản chiếu ánh đuốc hầm mộ
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera glide. Low-angle slow glide across black, mirror-still underground floodwaters covering the stone floor of an ancient subterranean imperial crypt. Ripples gently catching reflections of warm lantern flame against ancient damp limestone walls. Eerie stillness, cavernous acoustics visualised through subtle water motion. Ultra-smooth camera movement. Avoid readable text, human figures, corpses, blood.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ, thi thể, máu me, mặt người.

## ai_10.png — CH06: Không gian tẩm điện tráng lệ phủ bụi thời gian
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Interior of a grand subterranean imperial burial chamber, Ding Dongling style. Massive carved stone columns, gilded bronze roof rafters dulled by centuries of underground condensation, high vaulted ceiling. In the center, a massive vacant stone bier dais flanked by ornate weathered marble steps. Shafts of cold dust-filled air piercing through from an entrance arch. Haunting majestic desolation. Avoid readable text, Chinese characters, coffins, human remains, recognizable faces.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Thi thể, quan tài mở, chữ Hán, mặt người.

## ai_11.png — CH07: Thư phòng cổ vắng lặng bên rèm lụa trắng
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A solemn private study in a grand European-concession mansion in Tianjin, July 1928. Heavy dark mahogany desk, traditional white mourning silk drapery hung over French windows, an unlit porcelain lamp, an open telegraph leather portfolio without readable text. Gloomy rainy day lighting casting long cool grey reflections across parquet flooring. Somber, tense, aristocratic grief. Generous negative space on one side. Avoid readable text, letters, Chinese calligraphy, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ viết, mặt người, tang lễ quá đà.

## ai_12.png — CH08: Khối ngọc phát quang mờ ảo trong hộp gấm cổ
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual of the legendary luminous pearl. A polished, flawless spherical natural phosphorescent mineral orb (fluorite-like) resting inside an antique dark jadeite and silk-lined carved wooden box. In near-darkness, the sphere emits an ethereal, gentle soft cyan-green glow that illuminates the velvet folds around it. Elegant, mysterious, museum-grade macro still life. Avoid readable text, letters, numbers, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ, số, mặt người, hiệu ứng ma quái quá lố.

## vid_05.mp4 — CH08: Ánh sáng quét qua chuỗi ngọc trai và châu báu cổ
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera glide. Extremely smooth macro glide over antique loose natural sea pearls, carved emerald-green jadeite beads, and gold filigree ornaments scattered gently on dark raw silk. Raking warm spotlight slowly revealing rich antique luster and mineral patinas. Museum documentary quality, shallow depth of field. Avoid readable characters, coins with stamps, text, faces.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ khắc, mặt người.

## ai_13.png — CH09: Bàn trà đàm phán ngầm với phong bao mật và tách sứ
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual of high-level political bribery and backroom dealings in 1928 Republican China. An antique zitan tea table inside an opulent private reception room. Two fine celadon porcelain tea bowls with steam gently dissipating, an unmarked plain heavy brown leather document satchel, and an antique lacquered gift casket tightly closed. Low-key warm interior lamp light, discreet conspiratorial atmosphere. Avoid readable text, letters, stamps, money, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ, tiền mặt đọc được, mặt người.

## ai_14.png — CH10: Hành lang công đường vắng bóng người với hàng cột xám
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A long, cavernous, empty neoclassical corridor inside the Nationalist Government Military Commission headquarters in Nanjing, late 1928. Imposing grey stone columns, tall arched windows casting stark geometrical shadows across polished terrazzo floors. Dead quiet, bureaucratic silence, power concealed behind heavy closed oak doors. Cold slate and marble palette, dramatic vanishing point perspective. Avoid readable text, door plaques, banners with writing, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ trên biển phòng, mặt người.

## ai_15.png — CH11: Hộp gấm đen chạm hoa văn rồng bị cháy xém một góc
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual metaphor of the Nine Dragons Sword after the 1946 Dai Li plane crash. An antique rectangular imperial sword scabbard box made of scorched dark wood and charred brocade fabric resting on damp gravel amidst mountain mist. Faint metallic sheen of a twisted antique bronze dragon fitting visible near the burnt edge. Tragic, mysterious historical relic atmosphere. Low-key somber lighting, muted charcoal and tarnished bronze palette. Avoid readable text, letters, blood, modern airplane debris, recognizable faces.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Máu me, xác máy bay hiện đại, chữ, mặt người.

## vid_06.mp4 — CH11: Tàn tro bay chậm qua thanh kiếm cổ trong tủ kính mờ
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera drift. Slow macro drift across an antique Chinese steel straight sword displayed behind dark museum glass. Faint translucent reflections of smoke and drifting dust particles caught in a single vertical spotlight beam. The blade bears subtle traditional hamon folds and oxidized dragon engravings without readable text. Solemn historical documentary aesthetic. Ultra-smooth camera motion. Avoid readable text, modern display stands, faces.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ, mặt người.

## ai_16.png — CH13: Bậc đá rêu phong hoang phế trước cửa hầm mộ trống
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A poignant concluding landscape: an ancient carved stone threshold and weathered marble steps leading into the open, empty shadow of an imperial tomb chamber, overgrown with wild mountain grass and moss. Golden autumn late afternoon sunlight breaking through storm clouds, raking across cracked stone blocks and chisel marks. Solitary, melancholic, grand moral contemplation on transient ambition and greed. Beautiful vast composition, negative space. Avoid readable text, graffiti, modern barriers, tourists, recognizable faces.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ khắc hiện đại, khách du lịch, mặt người.
