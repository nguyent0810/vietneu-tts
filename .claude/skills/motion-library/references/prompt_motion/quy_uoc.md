# Quy ước dùng mẫu motion cho FS và BUD

Rút từ 234 mẫu prompt-motion.com (phân loại 25/10/2026, xem `catalog.md`) và đối chiếu với kho cảnh đang có
(`../../SKILL.md`, `shorts-studio/references/devices.md`). Mục đích: khi viết plan hay cần cảnh mới, tra đúng một chỗ
để biết dùng loại cảnh nào, spec ra sao, tránh gì.

## 0. Cách tra khi viết plan

1. Đọc câu kịch bản, xác định **dạng** (mục 2). Mỗi dạng có câu kịch bản điển hình đi kèm.
2. Dạng đã có engine: viết `visuals` / `media` / thiết bị Studio theo spec mẫu của dạng đó.
3. Dạng còn ghi `MỚI`: không tự chế trong plan. Dùng cảnh thay thế ghi ở dạng đó, rồi xếp cảnh mới vào hàng đợi (mục 3).
   Khi viết cảnh mới, giao thợ bằng `prompt_mau.md` và làm theo skill `motion-scene-dev`.
4. Trước khi render cả video: soát khung tĩnh theo luật 10 ở mục 1.

## 1. Luật chung (mọi dạng, mọi kênh)

Mỗi luật ghi mẫu nguồn để mở xem khi cần.

1. **Một cảnh, một ý.** Long: cứ 3–5 giây có một thứ mới trên màn hình. Hook short: đổi ý mỗi 1,5–2 giây.
   "Ba khoảnh khắc thật đắt hơn mười hoạt cảnh tầm thường." (daniel-haida-8691d4, ik-builds-b8bdcf)
2. **Chuyển động bám lời, không bám nhạc.** Mốc `at`/`word` lấy từ hf_align. Cue sheet theo cụm, chỗ nghỉ, chỗ nhấn
   của lời đọc. (gdgtify-287ddf)
3. **Chuyển cảnh có lý do.** Không crossfade, không blur-in. Ưu tiên vật dùng chung giữa hai cảnh (chấm, đường kẻ, khung ảnh,
   khối màu tràn mang chữ sang cảnh sau). Không có vật chung thì cắt cứng, đặt sớm hai khung trước nhịp.
   (ultimaxbt-2ddf1e, notdwd-7de38a)
4. **Danh sách cấm chung:** hạt bung (particle burst), lens flare, glow neon, tách RGB, rung camera, easing nảy tưng,
   sàn lưới, nền nháy, vòng sóng xung kích, chữ hay khung ở bốn góc kiểu HUD giả, khung tô sau chữ (giống bôi đen),
   gradient tím hồng, glassmorphism, xoay 3D vô cớ, thuật ngữ dựng phim hiện trên màn, "bất cứ thứ gì trông như template".
   (twoclipping-6dd14e, daniel-haida-8691d4, blog "make AI motion graphics look less AI")
5. **Mọi khung là hàm thuần của thời gian.** Không `Math.random`, `Date`, timer, CSS transition. Lò xo dùng nghiệm đóng; giá trị
   đổi đích nhiều lần = tổng một lò xo cho mỗi lần đổi. Không `Math.floor` trên chuyển động (render được nửa khung).
   Chữ đang gõ = phần đã gõ tới thời điểm t. (twoclipping-221cab, rossaxbt-94583b; khớp `motion-scene-dev`)
6. **Easing và nhịp.** Mặc định `cubic-bezier(0.16, 1, 0.3, 1)`, vượt đích dưới 2 %. Vật lắng xuống dùng giảm chấn tới hạn.
   Các phần tử vào lệch nhịp nhau. Không bao giờ hai chuyển động camera cùng lúc. (daniel-haida-8691d4, antonio-kodheli-490109)
7. **Thời lượng tối thiểu.** Mọi xuất hiện kéo ít nhất 0,3 s (0,05 s trông như bật tắt). Ý chính đứng yên tuyệt đối ít nhất
   400 ms. Khung cuối của video đứng đủ lâu để đọc. Short `loop`: khung cuối khớp khung đầu (gồm cả hướng chuyển động).
   (rossaxbt-3085b7, gdgtify-287ddf, ultimaxbt-bbebf5)
8. **Không bịa trên màn hình.** Năm, ngày, tuổi, sao hạn tính bằng code. Lời kinh nguyên văn, có số kinh. Không khẩu hiệu
   diễn ý, không con số "cho đẹp". (ik-builds-b8bdcf, antonio-kodheli-490109; khớp luật kênh)
9. **Màu và chất.** Một màu nhấn duy nhất mỗi cảnh. FS: nền xanh đen, chữ kem, nhấn vàng; đỏ son chỉ cho cảnh báo / dấu.
   BUD: nâu ấm, vàng nghệ, kem; không neon, không nhịp gắt. Chữ phải có vai trò trong bố cục, không chỉ là nhãn.
10. **Soát trước render.** Render 4–8 khung tĩnh (hoặc một khung mỗi nhịp) để duyệt bố cục trước khi render cả cảnh. Quét
    "bật một khung" bằng chênh lệch khung (gấp 3 lần khung lân cận). Kiểm dấu tiếng Việt ở mọi chữ. Người soát cuối không
    phải người vừa dựng. (notdwd-7de38a, twoclipping-221cab, antonio-kodheli-490109)
11. **Bẫy kỹ thuật đã được người khác dính** (bổ sung cho bảng bẫy của `motion-scene-dev`):
    - không đặt `opacity`/`filter` lên phần tử `preserve-3d` (dẹt hình, lộ hai mặt), fade lớp bọc ngoài (áp cho `card3d`);
    - không đặt `will-change` lên thứ bị camera scale (chữ mờ);
    - khối màu tràn khung phải vượt quá góc xa nhất và kéo khoảng 0,35 s, nhanh hơn trông như chớp;
    - con để `visibility: visible` sẽ lộ dưới cha đang ẩn, dùng `inherit`;
    - nhoè quá nặng xoá mất hình, giảm tới khi còn đọc được; chữ đứng yên luôn nét, chỉ chuyển động nhanh mới nhoè;
    - zoom của cảnh sau bắt đầu đúng mức cảnh trước kết thúc, không nhảy về 1.0;
    - font viết tay phổ biến (Caveat…) thiếu dấu tiếng Việt: dùng Charm hoặc font đã có trong WORDTS_FONTS.
12. **Bản dọc là bố cục lại**, không cắt từ bản ngang.

## 2. Mười hai dạng cảnh

Ký hiệu: ✅ engine có sẵn · 🟡 có cảnh gần đúng, dùng tạm · `MỚI` cần viết (xem mục 3).

### D1. Dòng thời gian nhân vật, triều đại ✅
- **Câu kịch bản điển hình:** "Năm 1491, ông sinh ở làng Trung Am…", "Bốn mươi năm sau…", các mốc đời nhân vật Ngoài Đời Thật,
  đời Đức Phật, lịch sử một công trình.
- **Kênh:** FS và BUD, Long; short dùng bản dọc.
- **Engine:** Long `timeline` (mốc ngang), `years` (thẻ năm, mark vòng vẽ tay); short Studio `time_spine` (trục dọc).
  ```json
  "visuals": {"14": {"type": "timeline", "title": "ĐỜI TRẠNG TRÌNH",
    "items": [{"yr": "1491", "label": "Sinh ở Trung Am", "at": 14, "word": "sinh"},
              {"yr": "1535", "label": "Đỗ Trạng nguyên", "at": 16, "word": "đỗ"},
              {"yr": "1542", "label": "Cáo quan về quê", "at": 18, "word": "cáo", "now": true}]}}
  ```
- **Mẫu tham khảo:** triglyceee-bd5b08 (thẻ năm lớn, màu phẳng theo phe, nhân vật hình nộm không mặt),
  kloss-xyz-fe0c31 (mỗi mốc một kiểu đồ hoạ, bộ đếm năm), buildfastwithai-53234e (nền giấy, con dấu, sợi chỉ nối mốc).
- **Nhịp:** mỗi mốc 2–4 s, tối đa 5 mốc một cảnh (luật liệt kê ≤ 3 khi đọc; mốc thứ 4–5 chỉ hiện chữ).
- **Cấm:** năm chưa soát nguồn; hạt "công nghệ" (đổi sang bụi vàng / khói hương).

### D2. Quy trình từng bước, bày vật 🟡 (`MỚI: step_assemble`)
- **Câu điển hình:** "Đầu tiên đặt bát hương ở giữa…", "Mâm ngũ quả gồm…", "Ba bước dâng hương…".
- **Kênh:** FS (bàn thờ, mâm cúng, vật phẩm phong thủy), BUD (lễ Phật giản dị).
- **Dùng tạm:** short `list_build` (mục tích lũy, mục cũ mờ), Long `list` biến thể `stack`; ảnh từng món bằng `media` layout `pinned`.
- **Cảnh mới `step_assemble`:** khung trống (bàn thờ / mâm) → từng vật bay vào đúng chỗ, nhãn tên + ý nghĩa + vị trí hiện khi vật chạm chỗ,
  thanh bước N nút sáng dần. Mẫu: ror-fly-9950f1 (thanh bước, thẻ liều lượng), sarut0bisasuke-cefa43 (từ rỗng đến đầy).
- **Cấm:** bịa lễ, bịa vị trí đặt; BUD tuyệt đối không hình rượu bia.

### D3. Giải thích khái niệm cho người chưa biết gì ✅
- **Câu điển hình:** "Thiên can là gì?", "Ngũ hành tương sinh thế nào?", "Tứ diệu đế gồm…".
- **Engine:** `wheel` (12 chi, quan hệ xung/hợp), `elements` (ngũ hành), short `cycle_draw` (vòng sinh/khắc), `compare` (hai vế),
  `list` / `list_build`; Long thêm `illus` mở ý.
- **Khuôn kể (mượn yunn260414-60d996):** khái niệm → ví dụ đời thường → từng thuật ngữ → tổng kết bằng một hình đã thấy từ đầu.
  Một sơ đồ đi suốt, mỗi câu thêm một nét, không đổi sơ đồ giữa chừng.
- **Chú ý luật kịch bản Long:** không đặt chương định nghĩa trước câu trả lời đầu tiên (`long-script` luật 3); định nghĩa ≤ 2 câu.

### D4. Ngày, tháng, giờ ✅
- **Câu điển hình:** "Thứ Năm 22/10 là ngày Tam Nương", "Tháng 10 âm có những ngày…", "Giờ Tý từ 23 giờ…".
- **Engine:** short `calendar` (lịch bloc lật + dấu son), `month_sheet` (tờ tháng, vòng khoanh), `ledger`; Long `clock` (12 canh giờ);
  `word` fx `slam` cho chữ công bố ngày.
- **Mẫu:** tankazunori0914-0fc886 (chữ gõ dần, thanh chọn 7 ô, chữ to trên nền lặp chữ mờ, thẻ dữ liệu cuối).
- **Cấm:** ngày giờ không sinh bằng code; lịch hoàng đạo trễ thì huỷ chứ không dời (luật kênh).

### D5. Con số, tỉ lệ ✅
- **Câu điển hình:** "31 năm sinh phạm Hoang Ốc", "3 trên 12 tuổi…", "cõng cha mẹ trăm năm".
- **Engine:** `stat` (Long), `count_ring`, `bars`, `unit_grid` (k trên N), `ledger` (bảng tra).
- **Luật đã có:** năm sinh dùng `word` không dùng `stat` (stat in "1.990"); số ≥ 5 chữ số hoặc đơn vị dài đưa vào `label`.
- **Mẫu:** viktoroddy-98c1d8 (số odometer lăn trên đường tăng trưởng), nolkeeg-bf062e (mỗi màn một số lớn + nhãn nghiêng + thanh tiến độ).
- **Cấm:** số liệu không có nguồn; bộ đếm chạy quá đích rồi lùi lại (overshoot trên số).

### D6. Trích kinh, dẫn nguồn ✅
- **Câu điển hình:** lời Phật nguyên văn, kệ Pháp Cú, câu Sấm, ca dao phong thủy.
- **Engine:** `quote` (biến thể `page`, `kinetic`, `glass`, `type` máy chữ) + `source`; short `quote` mode `karaoke` (từng chữ theo mốc thật),
  `source_card` (dẫn nguồn trước phán định, cụm `[[sáng]]`).
- **Mẫu:** samaote-5e2fc2 (chữ hiện theo từng tiếng khi tụng), henkvaness-0e06af (cặp thẻ trích tối/sáng, từ tô màu).
- **Nhịp:** tụng kinh / kệ: chữ to, chậm, không nảy; giữ câu đọc được trọn trước khi chuyển.
- **Cấm:** cắt ghép lời kinh cho vừa hình; trích không số kinh.

### D7. Ảnh và tư liệu 🟡 (`MỚI: paint_over`, `out_of_frame`)
- **Câu điển hình:** "Bức chân dung duy nhất còn lại…", "Trên bản đồ cổ, sông chảy…", "Tranh Đông Hồ vẽ…".
- **Engine:** `doc` (lia trên trang sách quét), `photo` (ảnh in + vòng khoanh đỏ), layout `depth` (2.5D), `card3d`, `pinned`, `full`.
- **Cảnh mới `paint_over`:** nét SVG vàng (FS) hoặc vòng sáng mảnh (BUD) tự vẽ đè lên tranh khắc / tranh cổ theo lời: long mạch, hướng nhà,
  đường đi của nhân vật. Mẫu: lexnlin-038035 (vẽ đè lên tranh khắc), ik-builds-b8bdcf (ghi chú marker tự vẽ nét).
- **Cảnh mới `out_of_frame`:** chủ thể (đã tách lớp như `depth`) bước ra ngoài khung tranh khi vào chương. Mẫu: pankajkumar-dev-0bee87.
- **Cấm:** ảnh không rõ quyền dùng; tranh khắc phương Tây thay cho tư liệu Á Đông; tách lớp làm méo mặt Đức Phật.

### D8. Chữ theo nghĩa ✅ (`MỚI: word_architecture` — chỉ khi đã giải bài toán dấu)
- **Câu điển hình:** một khái niệm mạnh ("vô thường", "buông"), phá ngộ nhận ("KHÔNG PHẢI X · Y"), câu hook.
- **Engine:** `word` với `fx` theo nghĩa (dissolve, rays, split, crack, ripple, wave, flicker, grow, slam) và chuyển động
  (sync, flip, wipe, zoom, breathe); short `hook_slam`, `myth_strike`, `window` (chữ khổng lồ làm cửa sổ), `stamp` (dấu son).
- **Mẫu:** gizakdag-cf4ae6 (vòng chữ rối rồi lắng, kết "breathe" — hợp BUD), gdgtify-287ddf (chữ làm kết cấu: từ khoá là dầm, cột, sàn),
  rneayan-474bcf (chất in lệch bản, gần Đông Hồ — dùng `grain-overlay` + `ink-bleed-reveal`).
- **Cấm:** biến dạng glyph khi chữ có dấu chưa được kiểm (đã từng cắt dấu chữ hoa ở thẻ chữ khoá); chữ đè lên mặt người.

### D9. Tái hiện không lộ mặt 🟡 (`MỚI: shadow_theatre`, `tranh_song`)
- **Câu điển hình:** cảnh trong truyện Tiền Thân, giai thoại nhân vật, cold open "một đêm năm 1535…".
- **Dùng tạm:** ảnh AI bóng lưng / dáng xa theo bảng nhân vật (ADR 0004), `illus`, layout `depth`.
- **Cảnh mới `shadow_theatre` (ưu tiên số 1):** rối bóng giấy cắt sau màn sáng ấm, đèn dầu rung nhẹ, nhân vật chỉ là bóng
  (dáng Việt / Ấn cổ: áo dài, nón, cà sa), cảnh đổi bằng tấm giấy trượt. Mẫu: x4b47x-9cc84f (BUD 3, FS 2).
- **Cảnh mới `tranh_song`:** tranh minh hoạ / tranh Đông Hồ sống dậy: tách lớp, khớp xoay nhẹ, hơi thở, nền trôi. Mẫu: abderrahmen-g-9e8ed0.
- **Mẫu không lời:** kamstudiolabs-0b0824 (phim câm, âm thanh kể nửa câu chuyện) cho cold open, nhưng ≤ 10 s vì khán giả nghe giảng.
- **Cấm:** hoạt hình hoá Đức Phật / chư tăng kiểu đáng yêu; bóng dáng phương Tây; thêm tình tiết không có trong nguồn.

### D10. Cảnh thở, không khí, mở chương 🟡 (`MỚI: season_window`, `life_stages`, `song_trang`)
- **Câu điển hình:** câu chuyển chương, câu kết lặng, "rồi mùa đông lại tới…".
- **Engine:** `illus` (road, sunrise, lotus, moon, house), không khí tự động (bụi vàng, cánh hoa, vệt sáng sang chương).
- **Cảnh mới:** `season_window` — khung cửa gỗ Việt đứng yên, bốn mùa trôi ngoài cửa (lúa, sen, đào mai), chén trà trên bàn
  (mẫu itsolelehmann-e47532, hợp vô thường BUD và tứ quý FS); `life_stages` — một bóng người không mặt đi qua các tuổi rồi lặp
  (loicrambo-ad6830, hợp sinh lão bệnh tử BUD và mở đầu Tử vi trọn đời FS); `song_trang` — mặt nước phản chiếu trăng tính theo t
  (demitiyageekzen-7770ad, đổi sang Khuê Văn Các / Ngọ Môn / chùa bên sông).
- **Cấm:** kiến trúc Trung Hoa thay cho Việt; hạt và vệt sáng dày đặc (luật 4).

### D11. Chuyển cảnh và nhận diện kênh 🟡 (`MỚI: thread_dot`, `assemble_reveal`, `flood_contract`)
- **Engine hiện có:** thẻ chương (zoom, slam, split, roll, depth, ink), chuyển cảnh (push, pushup, zoom, wipe, iris, blurfade), `endcard` shader.
- **Cảnh mới:** `assemble_reveal` — vạch quẻ (FS) / cánh sen (BUD) tụ lại thành biểu tượng rồi lộ tên kênh, cho intro và thẻ kết
  (tdinh-me-815acb); `thread_dot` — một hạt vàng xuyên mọi cảnh của short: dấu chữ → điểm trên vòng 12 chi → ô năm sinh → thẻ kết
  (ultimaxbt-bbebf5, chỉ FS; BUD nếu dùng thì chậm); `flood_contract` — khối màu tràn khung mang chữ sang cảnh sau (ultimaxbt-2ddf1e).
- **Xem lại:** `blurfade` gần với crossfade đang bị cấm ở luật 3 (mục 4).

### D12. Hook short dọc ✅ (`MỚI: ring_escape` cho FS)
- **Engine:** `hook_poster`, `hook_slam`, `myth_strike`, `window`, `split`; câu hỏi lặng `ask` + `silence`.
- **Mẫu:** kantamk-61f410 (câu hỏi cố định ở đỉnh + bộ đếm; 12 vòng = 12 chi, "tuổi bạn thoát ở vòng mấy?"), apoorvjain25-d24184
  (chữ đơn rất to đóng xuống, kết một câu lật), gizakdag-cf4ae6 (BUD).
- **Luật short v2/v3 vẫn giữ:** câu 1 tình huống cụ thể có neo, câu 2 lật bằng chi tiết bất ngờ, 27–32 giây.
- **Cấm:** kết quả "thoát vòng" ngụ ý dự báo vận hạn; nhịp game cho BUD.

## 3. Hàng đợi cảnh MỚI (ưu tiên)

| Ưu tiên | Cảnh | Dạng | Kênh | Mẫu | Khó | Vì sao |
|---|---|---|---|---|---|---|
| 1 | `shadow_theatre` | D9 | BUD, FS | x4b47x-9cc84f | vừa | Mẫu hợp nhất cả thư viện (BUD 3). Kể truyện không lộ mặt, giảm phụ thuộc ảnh AI có mặt |
| 1 | `paint_over` | D7 | FS, BUD | lexnlin-038035, ik-builds-b8bdcf | vừa | Khuôn nhân vật Ngoài Đời Thật dựa nhiều vào tranh cổ; vẽ đè biến ảnh tĩnh thành lời giải thích |
| 2 | `step_assemble` | D2 | FS | ror-fly-9950f1 | vừa | Bàn thờ, mâm cúng, vật phẩm là chủ đề FS chạy đều |
| 2 | `assemble_reveal` | D11 | FS, BUD | tdinh-me-815acb | vừa | Intro / thẻ kết nhận diện kênh, dùng ở mọi Long |
| 2 | `out_of_frame` | D7 | FS, BUD | pankajkumar-dev-0bee87 | vừa | Dựa trên tách lớp `depth` đã có |
| 2 | `season_window` | D10 | BUD, FS | itsolelehmann-e47532 | vừa | Cảnh thở giữa chương, ít rủi ro nội dung |
| 3 | `tranh_song` | D9 | FS, BUD | abderrahmen-g-9e8ed0 | khó | Tranh Đông Hồ sống dậy cho cold open |
| 3 | `life_stages` | D10 | BUD, FS | loicrambo-ad6830 | khó | Sinh lão bệnh tử; mở đầu Tử vi trọn đời |
| 3 | `thread_dot` | D11 | FS | ultimaxbt-bbebf5 | vừa | Vật dẫn xuyên short bảng tra |
| 3 | `ring_escape` | D12 | FS | kantamk-61f410 | vừa | Hook 12 chi; mô phỏng vật lý tính sẵn |
| 3 | `song_trang` | D10 | FS, BUD | demitiyageekzen-7770ad | khó | Nền đêm cho đêm nghe 90 phút, bí ẩn Huế |
| 4 | `word_architecture` | D8 | BUD | gdgtify-287ddf | khó | Chỉ làm sau khi giải được biến dạng chữ có dấu |
| 4 | `marker_note` | D7 | FS | ik-builds-b8bdcf | dễ | Cần font viết tay có dấu |

Mỗi cảnh mới: viết theo `motion-scene-dev`, thử bằng showreel + hf_qa, giao thợ bằng `prompt_mau.md`, thêm vào bảng ở `../../SKILL.md` khi xong.

## 4. Đối chiếu engine hiện có với danh sách cấm (đề xuất, chưa sửa)

| Thành phần đang có | Vướng luật | Đề xuất |
|---|---|---|
| Chuyển cảnh `blurfade` (longform.js) | luật 3: crossfade / blur-in | Bỏ khỏi bộ chọn tự động, giữ cho trường hợp ép bằng spec |
| Chùm hạt bung ở thẻ chương (`lf-burst`) | luật 4: particle burst | Thay bằng vệt sáng mảnh hoặc bỏ; đo trước/sau trên đường giữ chân |
| Khối registry `lens-flare.html` | luật 4: lens flare | Không dùng trong cảnh mới |
| Layout `card3d` | luật 11: opacity trên `preserve-3d` | Kiểm cách fade hiện tại; nếu fade thẳng phần tử 3D thì chuyển sang lớp bọc |
| Không khí hạt bụi vàng / cánh hoa | luật 4 (nếu dày) | Giữ nhưng thưa; không thêm hạt vào cảnh mới |

Sửa các mục trên là việc riêng: cần render so sánh và soát giữ chân, không gộp vào thay đổi tài liệu.

## 5. Giới hạn của thư viện

- Chấm điểm dựa trên tiêu đề, thẻ, prompt và mô tả; **chưa xem video**. 165/234 mẫu là prompt một câu, phần kỹ thuật suy theo tiêu đề.
  Trước khi viết một cảnh MỚI, mở link mẫu xem video gốc.
- Video và prompt thuộc người tạo (link ở mỗi mục). Chỉ mượn kỹ thuật, không chép thiết kế, không tải video về kho kênh.
- Một số mục chỉ có lệnh `npx skills add …`: không cài khi chưa đọc mã và chưa được duyệt.
- Cập nhật khi trang có mẫu mới: `python3 cap_nhat.py` (lấy lại dữ liệu thô), phân loại phần mới theo cùng khoá, chạy `build_catalog.py`.
