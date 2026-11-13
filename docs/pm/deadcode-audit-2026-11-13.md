# Audit code chết bộ dựng video — 13/11/2026

Người yêu cầu: PO ("audit toàn bộ bộ dựng video để không còn deadcode tương tự panorama").
Phương pháp: 3 agent đọc độc lập, Lead kiểm chứng ngẫu nhiên bằng `git grep` (khớp).
- **Engine Long** (`hyperframes_bridge.py`, `hf_batch_render.py`, `longform.js`, các picker): 45 plan, 24 plan từ 20/10.
- **Module và công cụ**: 65 module, 41 module có nơi gọi.
- **Bộ dựng Short**: 273 dòng plan Short từ 20/10.

Phân loại:
- **LIVE**: đang chạy (tự động, hoặc có tài liệu và có dùng).
- **UNDOC**: đang dùng nhưng không skill nào ghi.
- **DOC-ONLY**: có tài liệu nhưng không ai dùng.
- **DEAD**: không tài liệu, không nơi gọi, không dùng. Lưu ý: thư viện chung chưa dùng KHÔNG phải DEAD (xem mục 4).

Bổ sung cho `docs/pm/327-migration-plan.md` (hàng A1–A10).

## 1. Rủi ro sản xuất (P0)
| # | Phát hiện | Bằng chứng | Đề xuất |
|---|---|---|---|
| R1 | Short đang **bỏ qua cổng công thức v2/v3** | 273/273 dòng Short từ 20/10 dựng bằng 32 builder `output/cl_staging/grok/build_*.py` (gitignore), dùng `shortbuild/`. Không builder nào gọi `short_v2_issues`, `short_tone_issues`, `hook_errors`, `zodiac_naming_errors`. Có 83 dòng hẹn từ 14/11. | `shortbuild.guards.validate` gọi đủ các cổng. Builder đang dùng chuyển vào `builders/short/`. Soát lại các dòng hẹn từ 14/11. |
| R2 | Hai bản lịch hoàng đạo lệch nhau | `tools/hoangdao_daily.py` và `fs_calendar/hoangdao_daily.py` khác 30 dòng. `build_004` dùng bản `tools/`. | Xoá bản `tools/`, trỏ về `fs_calendar`. |
| R3 | Script sản xuất nằm ngoài git | `upload_long.py`, `asset_gate.py`, `thumb_cb.py`, `playlist_apply.py`, `worker_status.py`, `pano_stitch.py`, `pano_prep.py`, `review_due.py`, `upload_bud.py`, `upload_fs.py` | Mở rộng A4: đưa vào `tools/`. Test hiện đang bị skip (`test_asset_gate_chapter_dup`, `test_cine_still_fx`, `test_pano_pan`, `test_worker_status`) sẽ chạy thật. |

## 2. Đã làm mà không nối vào mặc định (P1, nối vào)
| # | Tính năng | Hiện trạng | Đề xuất |
|---|---|---|---|
| W1 | Panorama `pan` (028/028b) | UNDOC. Chỉ P1–P3 và 3 Long `t11` (Lead dùng tay 13/11) có dùng. | Ticket 058: thêm skill, `pano_stitch` vào `tools/`, runner nhắc Long mới chưa có cảnh toàn cảnh. Cân nhắc cho `assign_layouts_v2` tự pan ảnh ≥ 2:1. |
| W2 | Preset chuyển động (`motion_picker`: slow_zoom, push_detail, parallax, reveal…) | DEAD trên thực tế: tính cho mọi Long mới nhưng chỉ ghi vào `scene_decision`. Ảnh do người gắn sau thì không chạy picker. | Chạy `motion_picker` trên các dòng media ảnh ở bước lưu hoặc render, khi ảnh chưa có `preset`/`cine`. Nếu không thì xoá MOTION_PRESETS cùng `copy_motion`. |
| W3 | Bảng màu và hiệu ứng cine chưa từng được chọn (rain, fog, embers, petals, snow_ash; grade cold/night; chuyển cảnh whip, flash_white, match_dissolve) | DEAD | Đưa vào `_LAYOUT_FX_BUD_FS` theo ngữ cảnh (mùa đông thì cold, đêm thì night), hoặc bỏ khỏi danh sách. |
| W4 | Thiết bị Studio đã chứng minh trên Long nhưng Short chưa dùng: split, myth_strike, count_ring, unit_grid, stamp | DOC-ONLY (Short) | Đưa vào vòng luân phiên của builder Short qua `shortbuild` (BUD: hiểu lầm có nguồn; FS: con số, dấu son). |
| W5 | `clips` do `long_plan_build` ghi | Bridge và runner không đọc; `asset_gate` chặn cho tới khi đổi tay sang media | Builder đổi `clips` thành media, hoặc runner tự đổi. |

## 3. Đang dùng mà thiếu tài liệu (P1, ghi vào skill)
- **Long:** visual `overlay`, `lookup`, `chiwheel`, `dialog`, `teaser`, `bagua`, `scroll`, `stamp`; media kind `openverse`, `museum`; đủ danh sách giá trị cine (fx, grade, transition, `depth`).
- **Short:** style `yeartable` (78 dòng), `statue_cards` (42), `daytable` (29), `ai_cards` (14); vòng theme navy/red/jade/amber/ivory và mould A/B; thiết bị `pan_tour` (82 cảnh trong Long).
- **Đường dẫn trong skill đã cũ:** `tuvi_year.py`, `hoangdao_indep_check.py`, `scoreboard/hook_lint.py` trỏ vào `output/`, trong khi đã có bản trong git.

## 4. Thư viện chung và code chết: phân biệt (PO chốt 13/11)
**Thư viện chung** gồm cảnh, khối hiệu ứng, năng lực camera làm sẵn để mở rộng kênh. Thư viện được phép chưa dùng: theo luật ngày 26/10, thư viện chỉ áp vào ô thử nghiệm và dạng đang thua.
**Code chết** là công cụ hoặc đường code không có vai trò trong quy trình, cũng không phải kho dự trữ.
Vấn đề của thư viện hiện nay không phải ở chỗ tồn tại, mà là không có đường ra: catalog thiếu, hồ sơ kênh không trỏ tới, không có gì canh hỏng.

| # | Mục | Loại | Xử lý |
|---|---|---|---|
| L1 | Cảnh `wind`, `clues`, `relic`, `eclipse`, `hexagram`, `luoshu`, `compass`, `cuudieu`, `annot`, `pie`, `napam`, `museum` (catalog `dat`) | Thư viện | Gắn vào hồ sơ kênh hợp (BUD: relic, eclipse; FS: wind, compass, luoshu, cuudieu, napam…). Bộ chọn chỉ lấy khi plan là ô thử nghiệm hoặc dạng thua. |
| L2 | `region`, `profile` (catalog `khoa`) | Thư viện khoá | Giữ khoá. Mở khi kênh Văn Sử Địa chạy. |
| L3 | Panorama `pan`, camera/layers 028c (máy bám nhân vật) | Thư viện năng lực | Thêm vào catalog (trạng thái, kênh, ví dụ JSON). Camera/layers để `thu` cho tới khi có pilot. |
| L4 | 7 khối registry Short (ink-bleed, shimmer, grain, particle, constellation, ui-3d-reveal) | Thư viện | Thêm vào catalog có trạng thái. Sửa SKILL shorts-studio §5: "trong kho, chưa nối builder". |
| L5 | Style `hongchi`, theme `archive`, kind `asset` | Thư viện | Thêm vào catalog có trạng thái. |
| L6 | 438 thẻ thư viện | Thư viện tri thức | Giữ thẻ có nội dung thật; lưu trữ 273 thẻ chép tự động; ghi `dang_dung_o` khi dùng. |
| X1 | `lens-flare` | Bị cấm (quy_uoc.md) | Xoá |
| X2 | `hf_beatmap`, `hf_align_check` | Công cụ, không phải thư viện; đã có công cụ khác chạy thật (`hf_asr_check`) | Xoá |
| X3 | `studio_ledger` (đường code chưa từng tạo file) | Code chết | Xoá |
| X4 | Chữ "mặc định" cho `wordts`, `anchor` | Tài liệu sai | Sửa thành "tuỳ chọn", không đổi Short đang thắng |

Nối vào quy trình (công cụ có ích, chưa có nơi gọi):
- `hf_long_retention` vào tổng kết thứ Hai (`hf_brief`): đo pilot Long ngắn.
- `prompt_builder` + `image_request` vào `ai_image_batch`: tra kho trước, rồi sinh prompt theo hồ sơ kênh.
- `subject_box` vào M10 (preset chuyển động).
- `opening_library` làm gợi ý trong `long_script_lint` (PO 05/11: chỉ gợi ý, không tự chạy).

Để thư viện "sống":
- **Catalog đủ:** mọi món thư viện có trạng thái `dat` / `thu` / `khoa`, kênh được dùng, ví dụ.
- **Canh hỏng:** một test showreel mỗi tuần render khung đại diện của mọi món `dat`, món nào vỡ thì báo.
- **Báo cáo món nằm im:** tổng kết thứ Hai liệt kê món 30 ngày chưa dùng, để Lead đưa vào pilot kế tiếp.

## 5. Thứ tự PR đề xuất
1. **M7** (P0): R1 (cổng Short) và R2 (lịch trùng).
2. **M8** (P0): R3 (script sản xuất vào git, gộp với A4 của M2).
3. **M9** (P1): W1 (ticket 058) và W5.
4. **M10** (P1): W2 và W3 (chuyển động, cine), có test.
5. **M11** (P1): mục 3 (tài liệu), W4 (vòng thiết bị Short).
6. **M12** (P2): mục 4, gồm thư viện có đường ra (catalog, hồ sơ kênh, test canh hỏng, báo cáo món nằm im), xoá X1–X3 và sửa X4. Nối 4 công cụ ở M10/M11.

Mỗi PR có mục Migration (nơi gọi, phần gỡ, test chứng minh), theo luật "migration, không code chết" (13/11).

- Skill long-video §5 ghi `"bgm"` ghim một bài và `"bgm_rotate": false` tắt đổi bài; code (hf_batch_render.long_pool) đọc `"bgm_pin": true`, không có `bgm_rotate`. Sửa skill (Lead phát hiện 13/11 khi ghim nhạc cho L_fs_t11_*).
- Kho nhạc FS chỉ còn 8 bài dùng được cho Long (2 bài lấn giọng). Series 12 tuổi cần thêm bài (incompetech CC BY theo §5).
