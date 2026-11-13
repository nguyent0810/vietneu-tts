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
- **DEAD**: không tài liệu, không nơi gọi, không dùng.

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

## 4. Chết hẳn (P2, PO quyết xoá hay giữ)
| # | Mục | Quy mô | Đề xuất |
|---|---|---|---|
| D1 | `layers`, visual `camera`, các khoá pan phụ (trục dọc, zoom/focus theo điểm dừng, `end_*`, `transition_out`, `focus_pull`) của 028c | Khoảng 600 dòng bridge + JS, 0 lần dùng | Đưa ra sau cờ showreel, hoặc xoá |
| D2 | Module: `hf_beatmap`, `hf_align_check`, `hf_long_retention`, `tools/subject_box.py` + `saliency_box.swift`, `library/opening_library/*`, `library/tools/image_request.py` + `prompt_builder.py` | 8 module, có test, 0 nơi gọi | Xoá. Riêng `opening_library` (#54/#82) cần PO xem có nối vào câu mở Long không. |
| D3 | Short: 7 khối registry (ink-bleed, shimmer, grain, particle, constellation, ui-3d-reveal, lens-flare, trong đó lens-flare đã bị cấm), style `hongchi`, `studio_ledger`, theme `archive` | 0 lần dùng | Xoá, sửa SKILL shorts-studio §5 |
| D4 | Thẻ thư viện | 421/438 thẻ có `dang_dung_o` rỗng, 273 thẻ là chữ chép tự động. `cards`/`knowledge`/`inventory` không có nơi gọi sản xuất | Đóng băng, lưu trữ thẻ chép tự động |
| D5 | Visual `region`/`profile` (bị khoá), `wind`/`clues`/`relic`/`eclipse`; media kind `asset` | 0 lần dùng gần đây | Xoá, hoặc đưa vào hồ sơ kênh |
| D6 | Ghi "mặc định" mà không phải mặc định: `wordts`, short v3 `anchor` | 0/273 | Hoặc làm mặc định thật, hoặc sửa lời trong skill |

## 5. Thứ tự PR đề xuất
1. **M7** (P0): R1 (cổng Short) và R2 (lịch trùng).
2. **M8** (P0): R3 (script sản xuất vào git, gộp với A4 của M2).
3. **M9** (P1): W1 (ticket 058) và W5.
4. **M10** (P1): W2 và W3 (chuyển động, cine), có test.
5. **M11** (P1): mục 3 (tài liệu), W4 (vòng thiết bị Short).
6. **M12** (P2): mục 4 (xoá), sau khi PO quyết từng dòng.

Mỗi PR có mục Migration (nơi gọi, phần gỡ, test chứng minh), theo luật "migration, không code chết" (13/11).
