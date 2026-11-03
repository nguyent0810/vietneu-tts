# EXTRACTION_LOG (claude-sonnet, prompt fs-extract-0.2)

Tổng thời gian wall-clock: ~6 phút 5 giây (đọc schema/nguồn gộp chung). Ước tính theo chủ đề: tt05_temiya ~1,5 phút; vsd_fansipan ~1 phút; ck_bybit_2025 ~1,5 phút; f19_hue_phong_thuy ~1 phút; fs_short_ngay_tot_cuoi ~1 phút. Spans được kiểm bằng script tìm chuỗi con nguyên văn trong snapshot (0 span lỗi ở cả 5 store). Không ghi trạng thái xác minh.

## Nguồn không dùng được
- vsd_fansipan_s2 (viettimes), f19_hue_phong_thuy_s3 (tienphong), fs_short_ngay_tot_cuoi_s2 (tienphong): snapshot là byte nén/rác (hàng nghìn ký tự U+FFFD), không đọc được -> bỏ khỏi `sources`, không trích. tt05_temiya_s3 (sacred-texts): blocked 403, bỏ qua.
- Hệ quả: Fansipan chỉ còn 1 nguồn (Viet Nam News); f19 mất bài Tiền Phong (minh đường thuỷ tụ, hai cồn...); FS mất bài Tiền Phong về ngày 5/14/23.

## Theo chủ đề
### tt05_temiya — 20 facts
Predicates: other (14), performed, held_role, named, related_to, stated, part_of. Facts truyện đều kind=legend, modality=legendary, according_to_edition=tt05_temiya_s1; 2 fact về bộ Mahānipāta (Wikipedia s2) là assertion.
Muốn mà không có span: không (Sunanda là người đánh xe, không bị gán nhầm vào slot "giả câm"). Cowell edition ghi ở sources.edition là nhãn của snapshot ancient-buddhist-texts.net (bản dịch Cowell + chú thích), vì snapshot không tự khẳng định số tập; cần người kiểm.
Thiếu từ vựng: `was_tested_by`, `suffered_in`, `advised`, `ordered_burial_of`, `identified_in_jataka_as` (tiền thân đối chiếu), `told_at`, `had_wives`, `lifted`, `feared_rebirth_in_hell`.

### vsd_fansipan — 14 facts
Predicates: other (9), stated (2), located_in (2), measured_as (1).
Chỉ có MỘT fact đo: 3.147,3 m (2019). Giá trị 1909 (3.143 m) KHÔNG có trong snapshot s1 (chỉ nói "cao hơn 4 m so với số đo của người Pháp 1909"); không tạo fact vì không có span -> không có cặp comparable_group đầy đủ. Đã có fact chênh lệch 4 m (predicate other, cùng comparable_group `fansipan_height`), KHÔNG dùng `changed`. Hai giải thích (công nghệ kém chính xác / dãy núi nâng 23 cm mỗi năm) là attributed + hypothesized + hedge possible.
Thiếu từ vựng: `measurement_difference`, `measured_height_with_method`, `possible_explanation_of_difference`, `is_highest_peak_of`, `distance_from`.

### ck_bybit_2025 — 22 facts
Predicates: compromised (6), attributed_to_actor (6), other (4), lost_asset (3), occurred_on, caused, stated.
Tách đúng: compromised.subject = hạ tầng Safe{Wallet}/máy Developer1/JS trên S3; Bybit chỉ là subject của lost_asset; hạ tầng Bybit có 2 fact compromised với negated=true (attributed Bybit). attributed_to_actor đều có attributed_to: FBI (DPRK; "TraderTraitor" theo IC3; "TradeTraitor ... Lazarus group ... UNC4899" theo Sygnia), Bybit (Lazarus Group), Mandiant, CryptoSlate. Giữ nguyên tên nhóm theo từng nguồn (entity tradertraitor, lazarus, dprk tách riêng; quan hệ "also known as" là fact riêng attributed FBI qua Sygnia).
Dị bản số tiền: 1,5 tỷ USD (FBI) vs 1,4 tỷ USD (CryptoSlate) -> kind=variant, variant_group=bybit_loss_usd; thêm 400.000+ ETH (Sygnia). Số 1,4 tỷ của CryptoSlate là "hack" chứ không nói thẳng "mất", đã ghi nhận trong statement.
Thiếu từ vựng: `executed_via`, `activation_condition_targets`, `malicious_code_removed_after`, `also_known_as`; cần predicate cho "trích dẫn đơn vị pháp y xác nhận" và `negated compromised` có thể cần cờ riêng. Không có từ cho "bị trộm" cấp event (stolen_from).
Muốn mà chưa làm: quyết định số ETH cụ thể (~401.000) — snapshot chỉ ghi "over 400,000 ETH" nên dùng approx; Hasu "they" mơ hồ (đã ghi rõ trong statement).

### f19_hue_phong_thuy — 19 facts
Predicates: other (14), built (2), located_in, measured_as, named.
Các diễn giải phong thủy đều kind=attributed (attributed_to là bài/tác phẩm: Tiền Phong qua citation, Arndt, Đại Nam nhất thống chí, bài Wikipedia tương ứng) — không có assertion thuần cho diễn giải. Chỉ mô tả địa lý/niên đại (105 m, 1804, 1805–1832, hướng đông nam) là assertion.
Muốn mà không có span: "minh đường thuỷ tụ", sông Hương làm minh đường, các chi tiết Tiền Phong (snapshot s3 hỏng); Kim Long/Vauban không cần. Số hiệu UNESCO 678 nằm rời rạc trong infobox (không có span liền) nên bỏ.
Thiếu từ vựng: `feng_shui_symbolizes`, `feng_shui_front_screen_of`, `oriented_to_face`, `symbol_of`, `designated_unesco_world_heritage`, `flanked_by`, `renamed_in_reign_of`, `chose_as_front_altar`. Nên có predicate chung `fengshui_interpretation(subject, object)` hoặc `symbolizes`.
Lưu ý: facts có attributed_to = tác phẩm (type work) chứ không phải người.

### fs_short_ngay_tot_cuoi — 19 facts
Predicates: rule_traditional (9), other (7), stated (2), measured_as (1).
Luật truyền thống kind=tradition với condition.applies_when: Tam Nương lunar_day in [3,7,13,18,22,27] (3 nguồn: Hoàng Hà, Chợ Giá, Saigoneer — event_type khác nhau), Nguyệt kỵ lunar_day in [5,14,23] (Chợ Giá), tháng cô hồn lunar_month=7, năm Kim Lâu của cô dâu, giờ hoàng đạo, ngày hoàng đạo. XUNG ĐỘT NGUỒN: Chợ Giá định nghĩa Nguyệt kỵ = 5/14/23; Hoàng Hà Mobile nói Nguyệt Kỵ là tên gọi khác (phương Tây) của chính ngày Tam Nương -> hai fact kind=tradition cùng variant_group `nguyet_ky_definition` (lưu ý: schema chỉ bắt buộc variant_group với kind=variant; ở đây gắn thêm vào tradition).
Nguồn gốc Tam Nương: 3 fact kind=variant (Ngọc Hoàng/Saigoneer, Ngọc Hoàng/Hoàng Hà, truyền thuyết Trung Hoa) cùng variant_group `tam_nuong_origin`, modality legendary, according_to_edition = source tương ứng; 1 legend (tên ba nàng); 1 attributed giả thuyết khoa học (hedge possible).
Muốn mà không có span: ngày 5/14/23 "xấu" theo Tiền Phong (s2 hỏng); quy tắc "cưới trước 3–5 tháng" (làn ngaytot) không có trong 3 snapshot còn đọc được; số tháng cụ thể cho từng tuổi (Kim Lâu theo tuổi) không có.
Thiếu từ vựng: `rule_traditional` dùng được nhưng nên có trường object chuẩn; `computes_wedding_days_with`, `rated_best_wedding_day`, `proposed_scientific_explanation`, `origin_myth`, `named_in_tam_nuong_story`. Gợi ý thêm field `applies_when.field` chuẩn hoá (lunar_day, lunar_month, event_type, hour_type, day_type, bride_year_kim_lau) vào vocabulary.

## Vấn đề chung
- `predicates.json` thiếu: quan hệ chỉ dẫn/giả thuyết nguyên nhân (possible_explanation), `origin_myth`, `symbolizes`, `renamed`, `advised`, nên có predicate tổng quát cho "mô tả phương pháp đo".
- Schema: `evidence.span` có "[6.2]", "{6.30}" (chú thích số trang trong Cowell) — span khớp nguyên văn nhưng validator cần không chuẩn hoá bỏ chúng.
- `attributed_to` trong schema là entity_id; mình dùng entity type `work`/`org`/`group`, không chỉ person.
- `snapshot_path` copy nguyên từ sources_index (tương đối so với pilot/sources/).
