# Danh sách AI Prompts cho đề tài Mata Hari ngoài đời thật (slug: mata-hari, kênh CL)

Được tạo theo yêu cầu Ticket GH-228, quy chuẩn docs/codex/long-rules.md, brief docs/pm/tickets/GH-228-matahari-research-agy.md.
Các prompt phục vụ Nhóm B (Tái dựng bối cảnh) và Nhóm C (Minh họa khái niệm).

Quy tắc bắt buộc (theo tiền lệ Hòa Thân và brief GH-228):
- Tuyệt đối không vẽ khuôn mặt nhận diện được của nhân vật lịch sử (Margaretha Zelle / Mata Hari, Georges Ladoux, Vadim Maslov, Pierre Bouchardon, Jean Hallaure, Robert Nivelle...). Người chỉ là bóng, quay lưng hoặc ở xa trong sương mù.
- Tuyệt đối không vẽ chữ, số, ấn triện, dấu mộc, mật mã hay văn bản giả.
- Tuyệt đối không dựng cảnh xử bắn, không vẽ cảnh hành hình, không máu me hay mô tả chi tiết cái chết.
- Khung hình chuẩn: 16:9 (1920x1080).
- Phong cách: Cinematic historical editorial, photoreal lighting with subtle film grain, muted early 20th-century Belle Époque & World War I European aesthetic.
- Các prompt video (vid_NN.mp4) dùng cho công cụ tạo video Flow (chuyển động chậm, camera drift tĩnh, không giật hình).
- Đã tra cứu kho tài sản dùng chung (python ../library/tools/assets.py find, tag cl/hinh_su): kho có 10 tài sản (ai_29, ai_57, ai_45, ai_18, ai_04, ai_10, ai_26 và vid_11..vid_15 thuộc lô 198). Với Mata Hari (bối cảnh châu Âu đầu thế kỷ 20), các prompt dưới đây được thiết kế chuyên biệt để đảm bảo tính xác thực lịch sử và chất lượng thẩm mỹ.

---

## ai_01.png — CH00: Pháo đài Vincennes trong màn sương sớm tháng 10 năm 1917
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Exterior perimeter wall and stone moat of the ancient fortress Château de Vincennes outside Paris at twilight before dawn in October 1917. Cold autumn morning mist swirling across the muddy firing range clearing. Barren leafless oak trees silhouetted against a pale grey overcast sky. Seen from very far behind at a distance, a formation of French World War I soldiers in dark blue greatcoats and Adrian helmets standing motionless in formation, faces completely obscured by distance and atmospheric fog. No execution scene, no violence, no weapons aimed, no readable text, no logos. Solemn, chilly, haunting historic atmosphere.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Mặt người, cảnh xử bắn, máu me, chữ viết.

## vid_01.mp4 — CH00: Thành lũy Vincennes trong màn sương sớm
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow continuous camera drift. A smooth horizontal camera glide along the massive grey limestone fortress walls and dry moat of Château de Vincennes during early dawn in autumn. Thin wisps of morning mist drifting silently across weathered medieval stone masonry and damp grass. Desolate, quiet, atmospheric historical mood. Avoid text, readable letters, people, modern structures.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Người, chữ, chi tiết hiện đại.

## ai_02.png — CH01: Hồ sơ mật tình báo và con dấu sáp niêm phong
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual metaphor of declassified military secrets. A stack of aged vintage World War I intelligence dossier folders tied with faded ribbon on a dark weathered oak desk. A blank vintage wax seal ribbon lying beside an antique brass magnifying glass. Low-key dramatic chiaroscuro lighting from a green-shaded brass desk lamp, casting long diagonal shadows. Rich paper textures, dust motes in the light beam, generous negative space on one side for text layout. Avoid readable text, letters, numbers, stamps, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ, số, mặt người.

## ai_03.png — CH02: Dinh thự thuộc địa đảo Java cuối thế kỷ 19
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A wide colonial Indische-style plantation veranda in Java (Dutch East Indies) circa 1898 during a tropical late afternoon downpour. Polished dark teak floorboards reflecting raindrops, white wooden colonial pillars, rattan plantation armchairs. Dense tropical palm fronds, banana leaves, and banyan trees visible through the heavy misty rain outside. A solitary woman in a long Victorian white linen dress seen from far behind looking out into the storm, face never visible. Melancholy, isolated colonial atmosphere, muted tropical palette. Avoid readable text, logos, recognizable faces.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Mặt người, chữ viết.

## vid_02.mp4 — CH02: Mưa nhiệt đới trên tán cọ đảo Java
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera drift. Slow cinematic macro glide across lush wet palm fronds and colonial wooden shutters in Java during a tropical rainstorm. Gentle water droplets dripping from lush leaves, soft ambient grey-green lighting, tranquil and melancholic mood. Avoid text, people, modern objects.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Người, chữ, chi tiết hiện đại.

## ai_04.png — CH03: Khán phòng nhà hát salon Paris năm 1905
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Interior of an opulent Belle Époque private salon and museum gallery in Paris circa 1905, dimly lit by hundreds of flickering beeswax candles and brass lanterns. Sumptuous crimson velvet drapes, gilded stucco mouldings, antique Persian rugs, and an imposing bronze statue of an Asian deity emerging from the shadows in the background. Soft haze of frankincense in the air. Mysterious, exotic, aristocratic ambiance, deep shadows with warm golden glow. Avoid readable text, signs, logos, recognizable faces, people.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Mặt người, chữ viết.

## ai_05.png — CH04: Sân ga xe lửa châu Âu mùa đông năm 1914
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A grand European railway terminal in Paris or The Hague during a freezing foggy night in late 1914, just after the outbreak of World War I. Heavy clouds of white steam billowing from a black vintage steam locomotive onto damp iron platform tracks. Distant silhouettes of travelers wrapped in heavy overcoats with vintage leather suitcases hurrying through the fog, seen only from far behind with no visible faces. Cold industrial architecture, dim yellow sodium lanterns, foreboding wartime atmosphere. Avoid readable text, train numbers, signs, logos, recognizable faces.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Mặt người, chữ trên bảng hiệu.

## vid_03.mp4 — CH04: Hơi nước đầu máy xe lửa trên đường ray đêm
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow continuous camera glide. Smooth tracking shot low to the ground gliding along vintage European railway tracks enveloped in billowing steam and cold evening mist under vintage cast-iron arches. Moody, cinematic, noir wartime aesthetic. Avoid text, legible signs, faces.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Người, chữ.

## ai_06.png — CH05: Lọ mực vô hình và bút chấm trên bàn đêm
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual metaphor of covert espionage. An amber glass medicine bottle with a plain cork stopper, a vintage metal dip pen with brass nib, and a blank piece of aged parchment paper lying on a dark walnut tabletop in a modest hotel room. A single candle burning low, casting warm circular illumination and long shadows across the textured wood. Quiet, secretive, tense atmosphere. Avoid readable text, handwriting, labels with writing, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Chữ viết trên giấy, nhãn chữ trên lọ, mặt người.

## ai_07.png — CH06: Văn phòng Deuxième Bureau tại Paris 1916
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Interior of a French military intelligence office (Deuxième Bureau) in Paris during World War I, circa 1916. An empty dark mahogany executive desk holding blank paper stacks, an antique brass desk clock, and a vintage black candlestick telephone. On the wood-paneled wall hangs a large abstract tactical map of Western Europe. Soft overcast daylight streaming through high French casement windows overlooking Parisian zinc rooftops. Austere, bureaucratic, tense military authority. Avoid readable text, map lettering, logos, recognizable faces, people.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Mặt người, chữ đọc được trên bản đồ.

## vid_04.mp4 — CH06: Ánh sáng cửa sổ văn phòng quân báo Paris
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow subtle camera drift. Slow atmospheric camera drift across a dark wood-paneled French wartime office towards French balcony windows, revealing overcast Parisian rooftops under autumn skies. Subtle dust motes floating in muted window light. Calm, stately, cinematic pacing. Avoid text, people.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Người, chữ.

## ai_08.png — CH07: Bệnh viện dã chiến Mặt trận phía Đông Thế chiến I
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A quiet recovery ward in a military convalescent hospital during World War I, autumn 1916. Rows of simple iron-framed cots with pristine white linens, large arched windows with sheer white curtains billowing gently in a cool breeze. Soft golden late-afternoon sunlight casting long peaceful shadows across worn wooden floorboards. Somber, tender, poignant atmosphere. Avoid blood, wounds, medical gore, readable text, medical signs, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Máu me, vết thương, mặt người, chữ viết.

## ai_09.png — CH08: Cột thu phát vô tuyến Madrid trong đêm
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Rooftops of historic central Madrid at midnight in late 1916. An early radio telegraph antenna mast with intricate copper wire rigging standing against a dramatic cloudy twilight sky. In the far distance, faint warm amber city lights glow among terracotta tiled roofs and baroque church domes. Silent invisible radio waves traveling through the night air. Mysterious, shadowy, suspenseful telecommunications espionage mood. Avoid readable text, letters, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Mặt người, chữ viết.

## ai_10.png — CH09: Cửa phòng khách sạn Elysée Palace mở hé
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A luxurious Haussmannian hotel corridor inside the Elysée Palace Hotel in Paris on a winter morning in February 1917. Deep red patterned runner carpet stretching along cream-colored walls with classical gilded wainscoting. The white paneled door to Room 131 stands slightly ajar, revealing a sliver of an unmade bed and an antique leather traveling trunk on the wooden floor inside. Dramatic corridor lighting, tense, abrupt aftermath of an unexpected arrest. Avoid readable numbers on doors, text, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Số phòng, chữ, mặt người.

## ai_11.png — CH10: Vành móng ngựa tòa án quân sự Paris 1917
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. An austere French military courtroom (Troisième Conseil de guerre) in Paris during July 1917. An empty dark carved oak witness dock in the foreground under harsh direct window light. High dark paneled judges bench in the background, rows of empty wooden spectators benches. Solemn, suffocating judicial atmosphere, heavy dust motes illuminated by beams of summer sunlight. Avoid readable text, courtroom seals, coat of arms with lettering, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ, ấn triện, mặt người.

## vid_05.mp4 — CH10: Hạt bụi lơ lửng trong phòng xử án vắng lặng
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow continuous camera drift. A slow, haunting camera float through an empty historic wooden military courtroom, focusing on dust motes swirling gracefully in a stark shaft of daylight across dark polished oak railings. Heavy, tense courtroom atmosphere. Avoid text, people.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: C (Minh họa khái niệm)
- Cấm: Người, chữ.

## ai_12.png — CH11: Chiến hào Mặt trận Chemin des Dames hoang tàn
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A desolate, silent Western Front battlefield trench at Chemin des Dames in 1917, shrouded in dense grey morning mist. Muddy duckboard pathways, rusted rolls of concertina barbed wire, shattered sandbags, and splintered wooden revetments under a heavy, overcast leaden sky. Bleak, solemn anti-war landscape, monumental stillness. Avoid blood, corpses, violence, active combat, readable text, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Thi thể, máu me, mặt người, chữ viết.

## ai_13.png — CH11: Hàng mũ sắt Adrian phủ sương lạnh
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. Conceptual visual metaphor of sacrifice and mutiny in World War I. A long row of French Horizon Blue Adrian helmets resting abandoned on a muddy trench parapet in thick autumn fog. Wet metal surfaces with fine dew beads reflecting the pale grey sky, weathered canvas chin straps. Quiet, poignant, symbolic memorial atmosphere. Avoid readable text, regiment numbers, blood, corpses, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Số trung đoàn, máu me, thi thể, mặt người.

## ai_14.png — CH12: Chiếc áo choàng nhung xanh trong buồng giam trống
- Prompt (tiếng Anh): cinematic historical editorial still, painterly-photoreal with subtle film grain, full-bleed 16:9. Conceptual visual metaphor of dignity and departure. Inside a sparse historic stone prison cell at Saint-Lazare Prison in Paris during early dawn. A single deep peacock-blue velvet coat with delicate faux-fur trim draped gracefully over the back of an austere wooden chair. Soft cold morning light filtering through high narrow barred iron window, touching the rich fabric texture and bare stone walls. Poignant, quiet, dignified, peaceful melancholy. Avoid blood, violence, execution paraphernalia, readable text, logos, recognizable faces, human figures.
- Khung: 16:9, 1920x1080
- Nhóm: C (Minh họa khái niệm)
- Cấm: Cảnh hành quyết, máu me, mặt người, chữ viết.

## ai_15.png — CH13: Kho lưu trữ giải mật thế kỷ 21
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. An expansive modern national archive storage facility in France or the UK, housing historical declassified wartime records. Soaring aisles of precision steel shelves holding uniform grey acid-free archive boxes with clean minimalist barcode tabs. Symmetrical perspective, pristine museum preservation lighting, deep vanishing point. Reverent, objective, modern documentary authority. Avoid readable text, letters, logos, watermarks, recognizable faces, people.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ đọc được, mặt người.

## vid_06.mp4 — CH13: Bụi thời gian và hồ sơ lưu trữ thế kỷ
- Prompt (tiếng Anh): cinematic historical video, 16:9, slow continuous camera glide. Smooth macro camera tracking shot gliding past rows of vintage historical document folders and archival drawer labels in a warm quiet archive library. Cinematic shallow depth of field, gentle golden lighting. Avoid readable text, faces.
- Định dạng: 16:9, MP4, slow motion / subtle camera drift
- Nhóm: C (Minh họa khái niệm)
- Cấm: Người, chữ.

## ai_16.png — CH13: Tượng đồng ven dòng kênh Leeuwarden lúc hoàng hôn
- Prompt (tiếng Anh): cinematic historical editorial still, photoreal with subtle film grain, full-bleed 16:9. A picturesque urban canal in the historic center of Leeuwarden (Friesland, Netherlands) at golden hour sunset. A delicate bronze statue of an elegant dancer silhouette standing gracefully near the water edge, reflected on the calm rippling canal surface. Traditional Dutch gabled brick canal houses, quaint stone bridge, warm amber and violet twilight sky. Serene, nostalgic, timeless poetic homecoming. Avoid readable text, modern signage, logos, recognizable faces, close-up human figures.
- Khung: 16:9, 1920x1080
- Nhóm: B (Tái dựng bối cảnh)
- Cấm: Chữ trên bảng hiệu, mặt người.
