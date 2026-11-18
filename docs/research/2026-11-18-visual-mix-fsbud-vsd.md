# 080 — Tỷ lệ chữ/hình Long và Short BUD / FS / VSD

Ngày chốt kế hoạch Short: `2026-11-18`. Trạng thái: nghiên cứu để Lead review; không thay cổng, không render, không gọi YouTube, không commit/push.

## Kết quả chính và phạm vi chứng cứ

- Long BUD: 30 video, chữ 36.53% theo thời lượng gộp; trung bình từng video 35.22%. 27/30 vượt mốc 15.00%.

- Long FS: 36 video, chữ 22.42% theo thời lượng gộp; trung bình từng video 21.09%. 22/36 vượt mốc 15.00%.
- Short BUD: 20 mẫu có timing, chữ khác bảng 45.93%; bảng/khung tra cứu 0.00% thời lượng.
- Short FS: 20 mẫu có timing, chữ khác bảng 23.14%; bảng/khung tra cứu 56.73% thời lượng.
- Short VSD: 3 mẫu có timing, chữ khác bảng 57.16%; bảng/khung tra cứu 5.47% thời lượng.

FS bị pha trộn hai dạng khác nhau: nhóm bảng tra có chủ đích và nhóm kể/giải thích. Riêng nhóm không phải toàn video bảng tra có chữ 53.48%. Không dùng tỷ lệ gộp để kết luận short kể FS đã ít chữ.

**Thiếu mẫu VSD:** chỉ có 14 spec trong kho được giao, 3 job có cửa sổ timing. Thiếu 17 mẫu có timing so với mục tiêu 20; chưa đạt yêu cầu cỡ mẫu VSD. Các job này chưa có bằng chứng render `ok` ở đường dẫn output spec. Không gọi là 3 MP4 đã xác minh. Không tìm thấy Long VSD trong các plan Long được giao.

**Nguồn số liệu:** [JSON đo đầy đủ](2026-11-18-visual-mix-fsbud-vsd.json). Mỗi dòng bảng bên dưới truy bằng `long.records[id]` hoặc `short.records[id]` (tra phần tử có `id` tương ứng); có đường dẫn plan, manifest/timing, cảnh `t0/t1`, metric, bằng chứng render và SHA-256 đầu vào. Tổng kênh: `*.summary`; nhóm kể: `short.summary_non_lookup_videos`; ngưỡng đề xuất: `proposed_policy_not_applied`; danh mục engine: `engine_catalogs`. JSON đồng hành `.checks.json` và `recorded_verification` lưu kết quả lệnh kiểm.

Đã thử đúng `gh issue view 467 --repo nguyent0810/vietneu-tts`, nhận `HTTP 401: Requires authentication`. Bản tham chiếu cục bộ đọc đủ mục đề xuất và các câu hỏi: [`creator_v2/docs/pm/2026-11-17-chuan-hinh-anh-5-kenh.md`](../../creator_v2/docs/pm/2026-11-17-chuan-hinh-anh-5-kenh.md). Chưa xác minh được các sửa đổi/comment mới trên issue trực tiếp. Bản cục bộ còn viết ngân sách theo số cảnh; mã 076/079 hiện đã tính theo giây. Đề nghị sửa tài liệu khi Lead duyệt.

## Cách đo và giới hạn

Long gọi nguyên trạng `hf_batch_render.visual_mix_scenes(row, segments)` rồi `tools.visual_mix.measure(scenes)`. Adapter dùng `_shot_plan`, áp visual và `cuts`, gộp cảnh giữ, tính cả khoảng nghỉ đến đầu cảnh kế. Không thay hàm production; không dùng timing ước tính. Manifest phải khớp số dòng và lời đọc sau xử lý markup, hoa/thường, dấu câu và normalizer số/viết tắt cục bộ đang dùng bởi TTS. Có manifest chưa đủ: phải có sidecar render `ok` hoặc MP4 cục bộ. Đây là tái dựng cấu trúc từ **plan hiện tại + timing thật**, không phải phân loại pixel của MP4. Khớp lời đọc cũng chưa chứng minh plan hình chưa từng được sửa sau render.

Chữ chuẩn lõi là `TEXT_KINDS`, với quy tắc full-screen riêng: `kinetic/slam/quote/question` vẫn tính chữ khi có nền ảnh trang trí; từ khoá phủ trên cảnh ảnh đúng vai trò media không tính. Thẻ chương, bảng tra, `ledger` và các đồ hoạ dữ liệu hiện không tính. Giữ nguyên định nghĩa này để so hai engine. **Điểm mù cần Lead quyết:** Long có `visual.type=studio` thì adapter hiện trả `kind=studio`, không phân biệt `quote`, `stamp`, `list_build` với sơ đồ. `nested_studio_devices` trong JSON ghi lại device để không che vấn đề; chưa đưa chúng vào tử số chuẩn. `stat`, `stamp`, các style mộc bản nhiều chữ cũng không mặc nhiên nằm trong tử số này. Vì vậy số chuẩn không phải phần trăm pixel chữ toàn video.

Ảnh khác nhau/phút = số ref ảnh tĩnh khác nhau trong từng video chia số phút adapter; khi gộp kênh, cộng số ref theo từng video, không khử trùng xuyên video. `max_repeat` theo cặp ref + style; crop/layout/camera không tạo ảnh mới. Đây là **ref được adapter nhận diện**, không phải đối chiếu byte ảnh: query stock chưa resolve, ảnh nằm trong visual `museum/doc/photo/studio` hoặc alias chưa được adapter xuất có thể bị bỏ sót. Chỉ số thấp, đặc biệt giá trị không có ref ở Short BUD/FS, **không chứng minh video không có ảnh hoặc không lặp ảnh**. Không dùng số này để chặn video trong nghiên cứu này.

`uploaded.json` đang lưu ID video, không có ngày xuất bản xác thực. Cột ngày đăng để trống; ngày kế hoạch được ghi riêng. Long lấy tất cả video đã có bằng chứng render, kể cả ngày kế hoạch ở tương lai. Short BUD/FS chọn từ ngày kế hoạch gần nhất không vượt ngày chốt, thử lần lượt đến đủ cỡ mẫu đo được; bỏ qua lỗi và ghi lý do. Không coi ID trong sổ upload là đã phát công khai. VSD thiếu trường ngày nên không xác lập được thứ tự xuất bản; dùng tất cả job đo được. Mẫu này có thiên lệch về dạng có adapter/timing, không đại diện mọi short mới nhất.

Short legacy có manifest dùng cùng adapter HBR để giữ hợp đồng thời gian; Short toàn bảng dùng thời lượng render và vai trò template, không giả tạo các lần cắt nội bộ. Short custom HTML chỉ có thời lượng render không đủ để suy tỷ lệ chữ, được loại có lý do. Short Studio dùng `jobs/<id>/plan.json` đã có `windows/devices`, gồm cả đoạn loop cuối; kiểm số cảnh, thứ tự device, cửa sổ liên tục và dương. Không có cache thì không lấy độ dài câu để thay thế. Timeline TTS legacy có thể thiếu đuôi so với MP4: số chênh ghi `tail_unmeasured_s`. Không kiểm pixel, không chọn ảnh/clip mới, không dựng composition hay tờ ảnh trong task nghiên cứu này.

### Định nghĩa chữ và bảng ở Short Studio

| Nhóm | Device và ý nghĩa |
|---|---|
| Chữ trọng tâm | `hook_poster`, `hook_slam`, `myth_strike`, `window`, `stamp`, `source_card`, `quote`, `close`, `list_build`. Ảnh trong hook là một dải phụ; vẫn tính chữ trọng tâm. `quote/close/source_card` không vì thêm trường `img` mà thành cảnh ảnh: phải xét code build có sử dụng nó. |
| Bảng/so sánh có chủ đích | `ledger`, `split`, `month_sheet`, `thiep_cuoi`; template FS `yeartable`, `daytable`, `decade_grid`… Theo dõi ngân sách tra cứu riêng. `board` cũng có thể là bảng quan hệ có chủ đích ở creator_v2; **Studio hiện không đăng ký device board**. Không suy một bảng đúng nội dung chỉ từ nhãn. |
| Đồ hoạ/hình | `pan_tour` là ảnh + camera; `time_spine`, `wheel`, `cycle_draw`, `count_ring`, `bars`, `unit_grid`, `calendar` là đồ hoạ dữ liệu/quy trình. Chữ nhãn không tự biến toàn cảnh thành chữ lấp chỗ. |

Báo hai tỷ lệ: chữ khác bảng và phần tra cứu. Tổng hai tỷ lệ là mức khung mang nội dung chữ/bảng chủ đạo theo phân loại này. “Chữ khác bảng” không đồng nghĩa “vô ích”: trích dẫn đúng mục đích vẫn có thể cần thiết. Các bảng tra phải có dữ liệu/cấu trúc để người xem tự tìm, không được đổi tên một thẻ chữ thành bảng để lách ngân sách.

## Long — trung bình theo kênh

| Kênh | n | Tổng phút | Chữ theo giây gộp | TB từng video | Chữ theo cảnh gộp | Ref ảnh/phút | Lặp max |
|---|---:|---:|---:|---:|---:|---:|---:|
| BUD | 30 | 873.16 | 36.53% | 35.22% | 42.59% | 0.66 | 6 |
| FS | 36 | 985.90 | 22.42% | 21.09% | 29.21% | 0.39 | 3 |
| VSD | 0 | — | — | — | — | — | — |

Theo giây gộp = tổng giây chữ / tổng giây; TB từng video = trung bình tỷ lệ của từng video. Theo cảnh cũng gộp tử số/mẫu số. Không tráo các định nghĩa khi so con số cũ ở #467 vốn đếm cảnh.

### Mỗi Long một dòng

Phân bố: `loại % thời lượng (số cảnh)`, chỉ lấy các loại đứng đầu đã lưu trong `metrics.top6`. Ngày đăng “—” do không có ngày trong sổ; kế hoạch không phải ngày đăng.

| Kênh | ID | Ngày đăng | Ngày kế hoạch | Phút | Chữ/giây | Chữ/cảnh | Ref ảnh/phút | Lặp max | Phân bố loại cảnh |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| BUD | `L_bud_01` | — | 2026-10-02 | 6.17 | 8.58% | 16.67% | 0.00 | 0 | stock 87.37% (25); chữ khoá 8.58% (6); chương 4.06% (5) |
| BUD | `L_bud_02` | — | 2026-10-04 | 6.15 | 1.56% | 3.03% | 0.00 | 0 | stock 94.13% (27); chương 4.31% (5); chữ khoá 1.56% (1) |
| BUD | `L_bud_03` | — | 2026-10-07 | 4.43 | 21.20% | 15.91% | 0.00 | 0 | stock 55.37% (27); quote 10.91% (5); list 10.29% (2); map 10.29% (1); chương 6.98% (7); compare 4.04% (1) |
| BUD | `L_bud_04` | — | 2026-10-09 | 4.20 | 21.94% | 21.95% | 0.00 | 0 | stock 58.37% (22); list 10.72% (2); illus 9.40% (3); word 7.24% (5); chương 4.96% (5); quote 3.98% (2) |
| BUD | `L_bud_05` | — | 2026-10-10 | 30.64 | 54.81% | 68.70% | 0.00 | 0 | chữ khoá 34.45% (115); stock 14.57% (22); quote 12.56% (25); doc 9.15% (14); shadow 4.82% (5); list 4.05% (6) |
| BUD | `L_bud_06` | — | 2026-10-13 | 30.40 | 61.43% | 72.77% | 0.00 | 0 | chữ khoá 32.31% (96); list 13.59% (12); quote 12.11% (23); ledger 10.62% (10); stock 8.24% (12); museum 7.93% (5) |
| BUD | `L_bud_07` | — | 2026-10-17 | 30.13 | 62.22% | 70.24% | 0.00 | 0 | chữ khoá 31.77% (82); list 20.20% (18); ledger 13.72% (9); quote 9.02% (15); stock 7.62% (9); annot 4.10% (3) |
| BUD | `L_bud_08` | — | 2026-10-20 | 30.15 | 36.39% | 48.57% | 0.00 | 0 | quote 12.36% (15); word 11.14% (19); chữ khoá 9.34% (26); relic 7.35% (6); shadow 6.50% (5); compare 6.29% (5) |
| BUD | `L_bud_09` | — | 2026-10-24 | 30.12 | 25.03% | 36.51% | 0.00 | 0 | ledger 17.59% (11); quote 12.04% (18); dialog 8.51% (7); compare 8.00% (8); word 7.25% (14); relic 7.22% (7) |
| BUD | `L_bud_10` | — | 2026-10-27 | 30.02 | 42.48% | 44.63% | 0.00 | 0 | word 20.24% (27); quote 16.57% (14); ledger 10.88% (8); compare 6.94% (6); illus 6.70% (9); shadow 6.49% (4) |
| BUD | `L_bud_11` | — | 2026-10-31 | 30.02 | 42.52% | 42.98% | 0.00 | 0 | quote 18.99% (18); word 16.18% (18); ledger 13.12% (10); compare 8.68% (7); stamp 7.12% (7); chữ khoá 6.91% (15) |
| BUD | `L_bud_12` | — | 2026-11-03 | 30.11 | 40.93% | 44.44% | 0.00 | 0 | word 17.76% (21); quote 16.89% (21); compare 14.09% (13); ledger 12.66% (8); dialog 8.34% (6); chữ khoá 5.94% (13) |
| BUD | `L_bud_13` | — | 2026-11-07 | 30.09 | 40.65% | 44.26% | 0.00 | 0 | quote 19.82% (23); word 15.55% (19); compare 13.08% (10); ledger 12.31% (8); timeline 7.32% (5); chương 5.90% (26) |
| BUD | `L_bud_14` | — | 2026-11-10 | 30.65 | 29.56% | 28.40% | 1.08 | 1 | stock 19.71% (30); tư liệu 19.32% (33); quote 16.77% (28); ledger 5.64% (6); chương 5.50% (26); word 5.33% (9) |
| BUD | `L_bud_15` | — | 2026-12-19 | 30.47 | 48.27% | 40.54% | 0.69 | 1 | quote 27.62% (30); stock 17.93% (24); tư liệu 13.70% (21); chữ khoá 11.13% (16); word 6.28% (10); ledger 5.67% (5) |
| BUD | `L_bud_16` | — | 2026-11-17 | 30.51 | 44.72% | 40.61% | 0.56 | 1 | chữ khoá 19.62% (31); stock 17.24% (28); quote 15.89% (19); tư liệu 10.39% (17); ledger 7.21% (7); word 6.32% (13) |
| BUD | `L_bud_17` | — | 2026-11-21 | 29.44 | 44.14% | 40.15% | 0.48 | 1 | stock 18.33% (25); quote 15.95% (16); chữ khoá 12.15% (18); tư liệu 11.08% (14); word 10.64% (15); ledger 9.78% (9) |
| BUD | `L_bud_18` | — | 2026-11-24 | 29.90 | 35.40% | 31.47% | 0.40 | 1 | stock 30.95% (40); quote 13.85% (14); word 12.26% (18); tư liệu 7.57% (12); compare 6.94% (8); ledger 5.63% (5) |
| BUD | `L_bud_19` | — | 2026-11-28 | 28.91 | 46.97% | 47.85% | 0.80 | 1 | chữ khoá 20.90% (38); stock 19.39% (29); quote 17.54% (24); tư liệu 16.83% (23); word 7.05% (14); chương 4.00% (17) |
| BUD | `L_bud_20` | — | 2026-12-01 | 30.26 | 56.75% | 53.04% | 0.00 | 0 | stock 30.17% (52); chữ khoá 25.39% (54); quote 23.14% (26); chương 4.34% (20); word 3.91% (10); list 3.77% (5) |
| BUD | `L_bud_21` | — | 2026-12-05 | 29.47 | 50.54% | 49.40% | 0.03 | 1 | stock 34.41% (51); chữ khoá 30.13% (55); quote 14.53% (15); ledger 5.44% (3); chương 4.78% (23); word 3.62% (8) |
| BUD | `L_bud_22` | — | 2026-12-08 | 30.21 | 24.88% | 28.18% | 0.93 | 1 | stock 41.05% (59); tư liệu 19.74% (28); word 8.22% (23); quote 6.00% (12); chữ khoá 5.40% (10); list 5.26% (6) |
| BUD | `L_bud_23` | — | 2026-12-12 | 30.18 | 39.20% | 39.41% | 0.83 | 1 | stock 28.95% (39); tư liệu 16.41% (25); chữ khoá 16.20% (31); quote 8.35% (12); word 7.67% (16); list 6.44% (7) |
| BUD | `L_bud_24` | — | 2026-12-15 | 30.14 | 29.85% | 29.71% | 1.13 | 1 | stock 27.86% (43); tư liệu 26.34% (34); chữ khoá 13.90% (26); word 5.65% (13); chương 5.41% (30); list 4.92% (5) |
| BUD | `L_bud_25` | — | 2026-11-14 | 32.97 | 44.58% | 55.39% | 0.18 | 3 | stock 43.26% (58); chữ khoá 29.37% (80); quote 7.76% (14); tư liệu 6.95% (11); word 4.81% (14); list 2.64% (5) |
| BUD | `L_bud_26` | — | 2026-11-19 | 31.18 | 24.62% | 35.68% | 2.31 | 6 | ảnh AI 55.02% (76); chữ khoá 14.47% (44); tư liệu 13.41% (21); quote 4.52% (11); list 3.38% (5); chương 2.63% (14) |
| BUD | `L_bud_tt01` | — | 2026-10-18 | 56.54 | 13.85% | 29.57% | 0.85 | 1 | tư liệu 32.73% (73); stock 29.96% (67); studio 22.68% (83); chữ khoá 12.19% (86); ask 1.26% (9); chương 0.78% (8) |
| BUD | `L_bud_tt02` | — | 2026-10-22 | 46.65 | 21.12% | 41.08% | 0.69 | 2 | tư liệu 27.51% (53); studio 26.16% (65); stock 24.51% (51); chữ khoá 19.78% (115); ask 1.10% (6); chương 0.69% (6) |
| BUD | `L_bud_tt03` | — | 2026-10-29 | 50.75 | 26.85% | 42.76% | 2.46 | 2 | tư liệu 46.20% (149); chữ khoá 25.19% (188); studio 24.46% (101); ask 1.66% (10); map 1.37% (4); chương 1.12% (11) |
| BUD | `L_bud_tt04` | — | 2026-11-05 | 32.32 | 15.43% | 29.46% | 2.51 | 2 | tư liệu 49.40% (83); stock 26.11% (45); chữ khoá 14.00% (63); studio 8.20% (34); ask 1.43% (8); chương 0.86% (8) |
| FS | `L_fs_01` | — | 2026-10-03 | 7.60 | 13.14% | 23.26% | 0.00 | 0 | stock 82.53% (25); chữ khoá 13.14% (10); chương 4.34% (8) |
| FS | `L_fs_02` | — | 2026-10-04 | 5.84 | 1.52% | 2.63% | 0.00 | 0 | stock 93.11% (30); chương 5.37% (7); chữ khoá 1.52% (1) |
| FS | `L_fs_03` | — | 2026-10-05 | 5.99 | 15.92% | 6.90% | 0.00 | 0 | stock 33.60% (16); elements 26.02% (1); list 15.92% (2); wheel 12.47% (2); years 6.70% (1); chương 5.28% (7) |
| FS | `L_fs_04` | — | 2026-10-07 | 5.42 | 14.66% | 6.06% | 0.00 | 0 | stock 34.00% (16); elements 20.52% (1); list 14.66% (2); wheel 11.92% (2); chương 6.14% (8); compare 4.58% (1) |
| FS | `L_fs_05` | — | 2026-10-09 | 5.05 | 11.08% | 8.57% | 0.00 | 0 | stock 42.67% (19); elements 20.89% (1); wheel 10.20% (2); list 6.98% (1); chương 6.03% (7); quote 4.10% (2) |
| FS | `L_fs_06` | — | 2026-10-02 | 35.14 | 14.74% | 28.38% | 0.00 | 0 | elements 36.69% (13); wheel 16.43% (26); years 14.86% (14); stock 9.30% (29); list 7.24% (13); chữ khoá 6.76% (26) |
| FS | `L_fs_07` | — | 2026-10-10 | 30.06 | 29.14% | 43.21% | 0.00 | 0 | ledger 37.65% (31); chữ khoá 16.98% (52); stock 11.29% (15); museum 10.60% (24); list 9.87% (13); chương 2.72% (12) |
| FS | `L_fs_08` | — | 2026-10-15 | 30.13 | 31.09% | 46.23% | 0.00 | 0 | lookup 36.47% (15); ledger 17.87% (9); list 15.96% (11); chữ khoá 14.60% (36); chương 3.70% (17); relic 2.24% (2) |
| FS | `L_fs_09` | — | 2026-10-17 | 30.01 | 22.44% | 37.21% | 0.00 | 0 | bagua 19.24% (14); chữ khoá 15.56% (36); ledger 14.26% (14); dialog 7.75% (5); compare 7.12% (6); lookup 6.89% (4) |
| FS | `L_fs_10` | — | 2026-10-22 | 30.03 | 15.80% | 20.66% | 0.00 | 0 | ledger 22.02% (19); word 14.25% (21); lookup 9.01% (8); dialog 8.95% (7); chiwheel 8.33% (7); relic 7.23% (6) |
| FS | `L_fs_11` | — | 2026-10-24 | 30.20 | 14.54% | 19.09% | 0.00 | 0 | ledger 27.25% (18); word 13.63% (19); lookup 9.46% (8); compare 9.05% (8); stamp 7.01% (6); chiwheel 6.92% (5) |
| FS | `L_fs_12` | — | 2026-10-29 | 30.01 | 18.17% | 22.41% | 0.00 | 0 | compare 18.54% (14); word 16.63% (22); ledger 16.11% (10); bagua 11.39% (10); stamp 9.18% (11); chương 5.28% (24) |
| FS | `L_fs_13` | — | 2026-10-31 | 31.03 | 11.74% | 15.65% | 0.00 | 0 | ledger 32.32% (20); compare 13.51% (10); bagua 12.89% (13); word 10.24% (15); stamp 7.33% (11); chương 5.75% (26) |
| FS | `L_fs_14` | — | 2026-11-05 | 30.04 | 15.40% | 22.12% | 0.00 | 0 | ledger 29.29% (20); compare 13.04% (9); word 10.93% (16); timeline 9.45% (6); chiwheel 6.02% (5); lookup 5.94% (7) |
| FS | `L_fs_15` | — | 2026-11-07 | 30.13 | 15.46% | 16.35% | 1.06 | 1 | tư liệu 20.04% (32); ledger 18.18% (16); stock 17.54% (29); word 11.16% (18); compare 9.05% (9); chương 6.41% (30) |
| FS | `L_fs_16` | — | 2026-12-17 | 31.06 | 14.16% | 14.37% | 0.84 | 1 | stock 23.50% (40); ledger 18.15% (18); tư liệu 16.31% (26); chữ khoá 10.65% (17); compare 6.44% (7); chương 5.95% (30) |
| FS | `L_fs_17` | — | 2026-11-14 | 30.48 | 28.22% | 29.19% | 0.72 | 1 | chữ khoá 15.94% (27); ledger 14.16% (12); stock 14.13% (22); tư liệu 12.63% (22); word 8.82% (15); compare 7.75% (7) |
| FS | `L_fs_18` | — | 2026-11-19 | 30.50 | 30.17% | 29.61% | 0.85 | 1 | chữ khoá 19.84% (29); tư liệu 19.14% (26); stock 14.35% (22); ledger 13.98% (11); word 8.69% (14); compare 6.76% (7) |
| FS | `L_fs_19` | — | 2026-11-21 | 30.50 | 33.72% | 31.51% | 0.62 | 1 | chữ khoá 20.72% (28); stock 17.38% (22); ledger 13.47% (11); tư liệu 12.72% (19); word 11.11% (16); compare 6.73% (9) |
| FS | `L_fs_20` | — | 2026-11-26 | 28.95 | 24.90% | 27.42% | 0.76 | 1 | stock 28.88% (44); chữ khoá 14.82% (32); tư liệu 10.69% (22); ledger 7.96% (8); word 6.61% (14); chương 5.97% (24) |
| FS | `L_fs_21` | — | 2026-11-28 | 28.54 | 37.49% | 39.64% | 0.04 | 1 | stock 46.08% (47); chữ khoá 32.65% (60); chương 6.55% (25); list 3.30% (4); stamp 3.15% (22); ledger 2.18% (3) |
| FS | `L_fs_22` | — | 2026-12-03 | 29.43 | 31.54% | 37.13% | 0.03 | 1 | stock 42.48% (56); chữ khoá 29.15% (57); ledger 12.85% (12); chương 6.34% (25); stamp 2.82% (5); compare 1.96% (3) |
| FS | `L_fs_23` | — | 2026-12-05 | 30.02 | 23.36% | 25.00% | 0.87 | 1 | stock 37.90% (57); tư liệu 15.11% (26); list 9.17% (11); doc 8.37% (13); word 7.08% (20); chữ khoá 6.83% (15) |
| FS | `L_fs_24` | — | 2026-12-10 | 30.13 | 22.98% | 23.03% | 1.83 | 1 | tư liệu 35.92% (55); stock 18.74% (30); list 8.73% (8); word 7.00% (18); chương 5.64% (27); chữ khoá 5.56% (12) |
| FS | `L_fs_25` | — | 2026-12-12 | 30.13 | 33.94% | 30.34% | 1.39 | 1 | stock 27.52% (41); tư liệu 24.51% (42); chữ khoá 11.50% (25); list 10.77% (8); word 7.62% (17); chương 5.65% (29) |
| FS | `L_fs_26` | — | 2026-11-12 | 32.54 | 43.03% | 48.90% | 0.31 | 3 | stock 34.95% (47); chữ khoá 30.76% (66); tư liệu 13.65% (19); quote 5.12% (7); word 4.93% (12); chương 2.80% (14) |
| FS | `L_fs_27` | — | 2026-11-24 | 29.76 | 54.04% | 68.22% | 1.01 | 2 | chữ khoá 43.27% (121); ảnh AI 15.92% (21); tư liệu 14.17% (16); timeline 5.07% (4); quote 4.29% (12); chương 3.44% (14) |
| FS | `L_fs_t10_mao` | — | 2026-11-06 | 30.22 | 6.99% | 15.60% | 0.00 | 0 | studio 52.88% (80); stock 27.72% (83); ledger 5.80% (8); chữ khoá 4.25% (19); chiwheel 4.02% (6); ask 2.74% (15) |
| FS | `L_fs_t10_ngaytot` | — | 2026-11-05 | 29.24 | 12.43% | 19.23% | 0.21 | 1 | stock 27.19% (76); studio 24.79% (34); compare 14.45% (23); ledger 11.59% (13); list 6.80% (9); chữ khoá 3.75% (19) |
| FS | `L_fs_t10_top3` | — | 2026-11-04 | 31.01 | 11.64% | 12.71% | 0.19 | 1 | stock 35.43% (110); studio 23.72% (48); ledger 9.24% (11); compare 8.93% (14); list 8.57% (12); chiwheel 3.42% (4) |
| FS | `L_fs_tv01` | — | 2026-10-16 | 33.28 | 31.89% | 52.65% | 0.30 | 1 | studio 34.65% (45); chữ khoá 31.79% (118); stock 9.33% (16); ledger 7.95% (8); tư liệu 7.92% (15); chương 3.09% (15) |
| FS | `L_fs_tv02` | — | 2026-10-20 | 35.93 | 28.97% | 51.57% | 0.42 | 1 | studio 33.34% (44); chữ khoá 28.58% (113); tư liệu 11.77% (22); ledger 10.82% (9); stock 4.82% (10); lookup 3.89% (3) |
| FS | `L_fs_tv03` | — | 2026-10-27 | 36.87 | 30.67% | 53.06% | 0.57 | 2 | chữ khoá 30.32% (129); studio 25.13% (38); tư liệu 24.60% (37); stock 10.44% (16); ledger 3.05% (5); chương 2.68% (14) |
| FS | `L_fs_tv04` | — | 2026-11-03 | 31.33 | 10.21% | 21.39% | 0.41 | 1 | stock 46.75% (81); studio 32.21% (40); chữ khoá 9.97% (39); tư liệu 7.72% (14); chiwheel 1.26% (2); chương 1.16% (9) |
| FS | `L_fs_tv05` | — | 2026-11-10 | 28.91 | 1.94% | 3.45% | 0.00 | 0 | stock 61.00% (137); studio 30.25% (41); chương 3.90% (13); chiwheel 2.49% (4); chữ khoá 1.15% (4); ask 0.80% (3) |
| FS | `L_fs_tv06` | — | 2026-11-17 | 30.40 | 2.28% | 4.39% | 0.00 | 0 | stock 56.98% (147); studio 33.42% (53); chương 3.79% (13); chiwheel 2.37% (4); chữ khoá 1.25% (5); bagua 1.16% (1) |

Long không đo được:

- `L_bud_tt05` — no existing segment manifest (`output/cl_staging/long/plan_long_tt5.json`).

- `L_fs_01b` — no existing segment manifest (`output/cl_staging/long/plan_long_w40.json`).

## Short — mẫu đo và trường hợp bị loại

| Kênh | n đo | Chữ theo giây gộp | TB từng video | Chữ theo cảnh | Tra cứu theo giây | Chữ + tra cứu |
|---|---:|---:|---:|---:|---:|---:|
| BUD | 20 | 45.93% | 46.40% | 50.00% | 0.00% | 45.93% |
| FS | 20 | 23.14% | 18.70% | 43.64% | 56.73% | 79.87% |
| VSD | 3 | 57.16% | 57.83% | 65.22% | 5.47% | 62.63% |

| Kênh | ID | Ngày kế hoạch | Giây adapter | Chữ khác bảng | Bảng tra | Cơ sở thời gian |
|---|---|---|---:|---:|---:|---|
| BUD | `b45_e` | 2026-11-15 | 28.10 | 39.43% | 0.00% | TTS segments |
| BUD | `b45_d` | 2026-11-15 | 30.18 | 67.40% | 0.00% | TTS segments |
| BUD | `b45_c` | 2026-11-15 | 31.36 | 42.41% | 0.00% | TTS segments |
| BUD | `b45_b` | 2026-11-15 | 29.12 | 39.22% | 0.00% | TTS segments |
| BUD | `b45_a` | 2026-11-15 | 26.36 | 41.20% | 0.00% | TTS segments |
| BUD | `rp27_b23` | 2026-11-14 | 26.04 | 35.64% | 0.00% | TTS segments |
| BUD | `b44_e` | 2026-11-14 | 28.56 | 49.51% | 0.00% | TTS segments |
| BUD | `rp27_b22` | 2026-11-14 | 27.16 | 52.87% | 0.00% | TTS segments |
| BUD | `b44_d` | 2026-11-14 | 28.32 | 47.46% | 0.00% | TTS segments |
| BUD | `b44_c` | 2026-11-14 | 28.20 | 26.52% | 0.00% | TTS segments |
| BUD | `b44_b` | 2026-11-14 | 26.70 | 44.12% | 0.00% | TTS segments |
| BUD | `b44_a` | 2026-11-14 | 28.00 | 27.79% | 0.00% | TTS segments |
| BUD | `b43_j` | 2026-11-13 | 15.12 | 47.35% | 0.00% | TTS segments |
| BUD | `rp27_b21` | 2026-11-13 | 21.02 | 72.41% | 0.00% | TTS segments |
| BUD | `b43_i` | 2026-11-13 | 18.16 | 80.07% | 0.00% | TTS segments |
| BUD | `b43_h` | 2026-11-13 | 17.52 | 16.89% | 0.00% | TTS segments |
| BUD | `b43_g` | 2026-11-13 | 15.76 | 43.65% | 0.00% | TTS segments |
| BUD | `rp27_b20` | 2026-11-13 | 20.96 | 54.39% | 0.00% | TTS segments |
| BUD | `b43_f` | 2026-11-13 | 15.96 | 44.61% | 0.00% | TTS segments |
| BUD | `rp27_b19` | 2026-11-12 | 21.36 | 55.06% | 0.00% | TTS segments |
| FS | `fsr47_05` | 2026-11-18 | 27.00 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `hd_20261119` | 2026-11-18 | 15.42 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `nt_lamnha_2027_01` | 2026-11-18 | 9.00 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `fs_007_18_2` | 2026-11-18 | 24.80 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `nt_lamnha_2026_12` | 2026-11-18 | 9.00 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `nt_cuoi_2027_h1` | 2026-11-18 | 9.00 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `fs_007_18_1` | 2026-11-18 | 24.37 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `fsr47_04` | 2026-11-17 | 27.00 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `f41_d` | 2026-11-17 | 26.94 | 65.63% | 0.00% | TTS segments |
| FS | `hd_20261118` | 2026-11-17 | 14.98 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `f41_c` | 2026-11-17 | 26.88 | 42.63% | 0.00% | TTS segments |
| FS | `f41_b` | 2026-11-17 | 25.52 | 49.92% | 0.00% | TTS segments |
| FS | `fsr47_03` | 2026-11-17 | 27.00 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `f41_a` | 2026-11-17 | 29.24 | 60.60% | 0.00% | TTS segments |
| FS | `fsr47_02` | 2026-11-16 | 26.57 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `f40_d` | 2026-11-16 | 28.04 | 66.33% | 0.00% | TTS segments |
| FS | `hd_20261117` | 2026-11-16 | 15.36 | 0.00% | 100.00% | render duration; whole lookup template |
| FS | `f40_c` | 2026-11-16 | 28.26 | 48.90% | 0.00% | TTS segments |
| FS | `f40_b` | 2026-11-16 | 28.66 | 40.06% | 0.00% | TTS segments |
| FS | `fsr47_01` | 2026-11-16 | 24.23 | 0.00% | 100.00% | render duration; whole lookup template |
| VSD | `vsd_l2_vanmieu` | không có | 53.00 | 50.91% | 0.00% | Studio cached windows |
| VSD | `vsd_l2_haivan` | không có | 44.52 | 55.80% | 16.98% | Studio cached windows |
| VSD | `vsd_l2_coloa` | không có | 40.66 | 66.80% | 0.00% | Studio cached windows |

Các dòng loại khi đi từ gần nhất về trước, gồm spec VSD chưa có timing; không nội suy hay coi là chữ bằng không:

| Kênh | ID | Lý do không đo |
|---|---|---|
| BUD | `bud137d_a3` | ValueError: no ok render sidecar |
| BUD | `bud138g_t8` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `budr47_03` | HyperFramesError: câu 1: vừa có ảnh vừa nằm trong sơ đồ của câu 1 |
| BUD | `bud138g_t7` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud137d_k3` | ValueError: no ok render sidecar |
| BUD | `bud137d_k2` | ValueError: no ok render sidecar |
| BUD | `bud138g_t6` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `budr47_02` | HyperFramesError: câu 1: vừa có ảnh vừa nằm trong sơ đồ của câu 1 |
| BUD | `bud138g_t5` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud137d_a2` | ValueError: no ok render sidecar |
| BUD | `budr47_01` | HyperFramesError: câu 1: vừa có ảnh vừa nằm trong sơ đồ của câu 1 |
| BUD | `bud137d_a1` | ValueError: no ok render sidecar |
| BUD | `bud138g_t4` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud138g_t3` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud137d_k1` | ValueError: no ok render sidecar |
| BUD | `bud_tn1_06s` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud_tn1_05s` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud_tn1_02s` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud138g_t2` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud_tn1_06q` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| BUD | `bud_tn1_02q` | ValueError: custom HTML/render duration only; no scene timing adapter, cannot infer text share from style |
| FS | `fs_d2_18_1` | ValueError: no ok render sidecar |
| FS | `fs_ret_1117` | ValueError: no ok render sidecar |
| FS | `fs_ret_1116` | ValueError: no ok render sidecar |
| VSD | `vsd_l2_binhngo` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_xuanhuong` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_thanglong` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_taysontet` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_sondoong` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_namquoc` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_kieu` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_hoangthanh` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_dalat` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_cuulong` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |
| VSD | `vsd_l1_bachdang` | ValueError: Studio spec exists but no cached job windows; no duration estimate substituted |

ID trùng khác nội dung: `hd_20261111` trong `output/cl_staging/fs/plan_hd_week_2026-11-05.json`, `output/cl_staging/fs/plan_hd_week_2026-11-11.json`. Loại mọi bản, không tự chọn một bản. Xem `plan_conflicts`.

## So khả năng hai engine

Đối chiếu source đăng ký trong `engine_catalogs`, không chỉ tên trong tài liệu. Có file sao chép trong thư mục composition chưa chứng minh casewide sử dụng được nó.

| Engine gốc: longform + Studio | creator_v2: casewide + lab + chart |
|---|---|
| FS có `hexagram`, `luoshu`, `bagua`, `compass`, `chiwheel`, `napam`, `cuudieu`, `eclipse`, `years/lookup`; BUD có `breath`, `shadow`, `wind`, `relic`. Có sẵn ngữ nghĩa phù hợp kênh. | Chưa thấy đăng ký tương đương trực tiếp trong casewide. Có generic `map`, `board`, `org`, `calendar`, `ledger`; muốn dùng các dạng FS/BUD phải viết adapter/chuyển schema, không tự đổi tên cảnh. |
| `region/profile` phục vụ địa hình/mặt cắt; media có `pan.stops`, `cuts` theo từ trong cùng câu, camera theo file. | Có `pano`, `map`, `broll` và bộ camera/transition; không cùng schema `media`/`visuals`/`until` của bridge. Cả hai có hình giữ bằng chuyển động, không bắt buộc thêm chữ khi câu dài. |
| Bộ style #258: `woodcut`, `papercut`, `oneline`, `film16`, `blueprint`, `pencil`, gọi qua HF_LONG. Đây là khả năng triển khai gốc; có giới hạn số cảnh và không xếp liền nhau. | Casewide không đăng ký các tên style đó. `idcardV2` có biến thể blueprint và `sketch/print/paper` có họ thẩm mỹ gần, nhưng không đồng nghĩa đã hỗ trợ API #258. File style được chép cạnh composition vẫn cần nạp/wire adapter. |
| Studio có `month_sheet`, `thiep_cuoi`, `time_spine`, `cycle_draw`, `count_ring`, `wheel`, `unit_grid`, khung tra cứu và hold cuối. `split` là hai vùng chữ/số. | Có `split` hai ảnh; `file/evidence/source/print/book`, `org`, `pizzini`, `memorial`, `saint`, `seismo`; không coi split hai engine là cùng cách dựng. |
| Có `pie`, `stat`, `ledger` và đồ hoạ cơ bản; chưa có đăng ký trực tiếp các device tài chính/công nghệ bên phải trong các source gốc đã đọc. | Chart có `candles`, `race`, `breadth`, `basket`, `waterfall`, `heat`, `stack`; lab có `nn`, `chat`, `go`, `chess`, `qr`, `barcode`, `captcha`, `keyboard`, `flap`, `punch`, `guess`. Đây là kho thay chữ cho MIM/CK và một phần VSD, cần chọn theo nghĩa. |

Không port toàn engine trong task này. Ưu tiên bảng tra/quan hệ/timeline/địa hình cho FS/VSD, ảnh/tư liệu/đồ vật và đồ hoạ có nghĩa cho BUD; không áp cảnh điều tra hoặc mô hình tài chính chỉ để đủ loại cảnh. Giữ quy tắc nguồn và hình BUD/FS khi chọn tài sản, nhất là không dùng hình AI làm chứng cứ lịch sử.

## Các xung đột với cổng và cách dung hoà

| Chỗ hiện tại | Xung đột/không xung đột | Phương án để Lead duyệt, chưa sửa mã |
|---|---|---|
| `visual_mix` — ngân sách toàn Long | Ngân sách chữ theo thời lượng tương thích ý định của PO. Bản đề xuất cục bộ còn ghi theo số cảnh nên khác hợp đồng hiện hành. | Giữ giây làm chuẩn, cảnh là thông tin bổ sung. Thiếu hình: ưu tiên tư liệu/clip, camera/pano, đồ hoạ dữ liệu, bản đồ/quy trình và bảng đúng mục đích trước chữ. |
| `pace_gate_issues` — cửa sổ mở đầu | Cửa sổ đầu còn giới hạn cảnh tĩnh/động và chữ trần; giảm tỷ lệ chữ không tự đạt nhịp cắt. | Giữ ngoại lệ nhịp mở đầu như đề xuất #467. Dùng `cuts` theo từ của 079/task liên quan #482 và `pan.stops`, đổi hình/camera trong lời dài. Tách shot không tạo ảnh khác nhau mới nếu vẫn cùng ref. Không gọi camera toàn cảnh là đã có cut. |
| `opening_gate` | Đòi hình ở đầu, giới hạn chữ trần và đủ ảnh khác nhau trong cửa sổ đầu. Có ảnh nền nhưng visual toàn màn hình vẫn có thể bị O1 chặn. O3 còn nhánh O3b xét sơ đồ nhưng cần Lead xét ý nghĩa, không mặc định mọi sơ đồ là ảnh thật. | Chuẩn bị media đầu tiên, thêm shot tư liệu hợp nội dung, dùng overlay đúng loại. Không lấp các nhịp thiếu bằng text. Giữ O1/O2/O3; pano cùng file không thoả số ảnh khác nhau. |
| `pacing` và ADR nhịp hình | Ngoài cửa sổ đầu vẫn có chặn cảnh giữ dài, cần `slow_hold`; giới hạn một loại sơ đồ cũng còn. Vì vậy “không độ dài cảnh cứng” chưa phải hành vi hiện tại. | Ticket sau cần tách đứng yên khỏi camera/video đang diễn tiến, cho phép hold có lý do; tạm dùng `slow_hold` theo đúng cổng hiện có. Không tắt pacing hay chia chữ để qua cổng. |
| `hook_lint` | Chỉ cờ `KHUNG_DAU_TRONG` chặn; từ ngữ hook là gợi ý. Hình, figure, sơ đồ cụ thể hoặc bảng có năm/chi có thể thoả khung đầu; không đo ngân sách cả video. | Giữ độc lập kiểm nội dung hook. Dùng thông tin cụ thể/bảng tra có nghĩa; không coi qua lint là qua tỷ lệ chữ hay bằng chứng ảnh đã xuất hiện. |
| Studio cổng đầu #253 | Kiểm luma, khung đầu và thời điểm chữ hook; mặc định cảnh báo, strict-hook mới chặn. Whitelist có `split`, `board`, `counter` không chứng minh chúng có ảnh hay tồn tại trong Studio. | Giữ hook hiện sớm và ảnh sáng. Thêm dải ảnh vào hook không đổi phân loại text trọng tâm. Bảng FS vẫn được xét đúng mục đích, không đổi cổng hay miễn tự động vì tỷ lệ chữ thấp. |
| Long FS `tra_cuu` | Luật là **bảng tóm tắt xuất hiện sớm**, không phải trần thời lượng cho mỗi bảng. Xem `docs/script/profiles/fs-lookup.md` và skill long-script. | Trả bảng trong mốc đầu đã quy định; tách chỉ số lookup khỏi filler, không giấu bảng chính đến cuối để đạt tỷ lệ chữ. Bảng có thể giữ khi còn thông tin, nhưng phải tuân cổng nhịp đầu hoặc được Lead duyệt thay đổi riêng. |
| Style #258 | Không thể thay mọi cảnh chữ bằng mộc bản để lách ngân sách. Kiểu trang trí không tự sinh tư liệu mới. | Giữ giới hạn style hiện có. Theo dõi ref gốc riêng; ảnh khác style có identity lặp riêng nhưng vẫn là cùng file trong unique-images. |

Các mốc hiện hữu đã đối chiếu source (cũng lưu `proposed_policy_not_applied.gates`): mở đầu 40s / 8 ảnh; nhịp 120s đầu, tĩnh 4s / động 8s, chữ trần 1.5s; hook ≤0.8s, luma ≥50; bảng Long tra cứu trước 45s; cảnh giữ cũ 25s; style tối đa 3 cảnh. Đây là mô tả hợp đồng đọc được, không phải kết quả chạy gate trên từng video.

## Ngưỡng đề xuất và module chung #159

| Phạm vi | Đề nghị | Căn cứ và giới hạn |
|---|---|---|
| Long BUD/FS | Giữ cảnh báo >12.00%, review/chặn theo policy hiện tại >15.00%; ngoại lệ có lý do do Lead xét. | Hiện BUD 36.53%, FS 22.42%; có khoảng cải thiện lớn. Không nâng trần để hợp thức hoá mẫu cũ. Lộ trình giảm bằng media/đồ hoạ có nghĩa; đánh dấu legacy đúng hợp đồng hiện tại. |
| Long VSD | Cùng mục tiêu 15.00%; chưa áp kết luận thực nghiệm riêng kênh. | Chưa có Long để đo. Dùng đây làm mục tiêu biên tập đề xuất, không nhận là tối ưu đã chứng minh. |
| Short kể BUD/FS | Thí điểm mục tiêu ≤30.00%, >30.00% cảnh báo, >40.00% bắt buộc Lead review thủ công; chưa sửa cổng tự động. | Mẫu BUD 45.93%, FS không bảng 53.48%. Áp trần Long ngay sẽ đụng toàn bộ nhóm kể đo được. Mốc này là bước giảm đề xuất, không phải tối ưu suy ra từ retention. |
| Short kể VSD | Cùng mốc thí điểm 30.00%/40.00%; chỉ cảnh báo trước khi đủ 20 mẫu. | Mới có 3 timeline, chữ 57.16%; chưa đủ để ban hành chặn. |
| Short bảng tra FS, bảng BUD/VSD có chủ đích | Lookup có thể tới 100.00% khi chính bảng là sản phẩm; filler ngoài bảng mục tiêu ≤15.00%; giữ khung cuối ≥3s theo skill, vẫn kiểm đọc được/overflow/contrast. | FS có các template toàn bảng; cấm chữ lấp chỗ không nên cấm chức năng tự tra. Phải lưu nhãn mục đích và dữ liệu bảng, không miễn cho mọi device có tên board/split/ledger. |

Short trích lời ngắn cần Lead quyết lane riêng: câu kinh là nội dung chính, tỷ lệ chữ không có cùng ý nghĩa với truyện nhiều cảnh. Không tự cấp ngoại lệ “mọi quote đều hợp lệ”. Kiểm nguồn, bố cục hình và giá trị cho người xem trước; mẫu hiện tại không đủ chứng minh nên chọn trần riêng nào.

Giữ mốc ảnh của Long như cảnh báo chẩn đoán: 4 ref/phút; lặp >4 cảnh báo, >6 review/chặn đúng policy hiện tại. Chưa dùng mật độ ảnh này để kết luận thiếu hình ở video nhiều sơ đồ/clip hoặc ref chưa resolve. Không quy đổi crop/camera thành ảnh mới để đạt ngân sách.

**#159: nên hợp nhất hợp đồng và báo cáo; lõi đã gần chung.** `creator_v2/motion/long/floor.py` đã import `tools.visual_mix`, cùng với HBR dùng `measure/issues/format_table`; không cần viết lại một bộ tính ngân sách nữa. Còn khác adapter thời gian, ref ảnh, taxonomy và cách xác định legacy/new. Studio chưa có adapter mix production; script của task này chỉ là đo nghiên cứu. Bước tiếp theo nên chuẩn hoá schema cảnh có vai trò `text/media/graphic/lookup`, unwrap device lồng `studio`, ảnh nằm trong visual và alias nhiều panel, giữ cả loại renderer lẫn loại nội dung; xuất chung bảng giây/cảnh/lookup/độ tin cậy ref. Gate riêng vẫn giữ nguồn, hook, nhịp đầu và bố cục. Không merge renderer hay sửa `tools/visual_mix.py`, HBR, Studio, hook_lint trong ticket này.

## Kiểm thử và khả năng chạy lại

Từ worktree `output/worktrees/wt_mix`:

```sh
.venv/bin/python tools/visual_mix_audit.py --long --short --out docs/research/2026-11-18-visual-mix-fsbud-vsd.json
.venv/bin/python -m pytest tests/test_visual_mix_audit.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m pytest -q test_*.py
```

Script tự tìm dữ liệu production ở thư mục cha vì worktree không có `output/cl_staging`; có thể chỉ định `--data-root`. Chỉ đọc các plan/manifests/job cache/sổ upload nêu trong JSON và code tham chiếu. Output có hash đầu vào/mã để nhận ra dữ liệu thay đổi giữa các lần đo. Không gọi entrypoint render, không ffprobe, không tải media, không sửa dữ liệu production. Các test nhỏ kiểm phân loại bảng/chữ, nền ảnh trang trí, thời lượng không đều, loop, cache lỗi, device lạ, chuẩn hoá lời và ID trùng.


`.venv/bin/python -m pytest tests/test_visual_mix_audit.py -q` (worktree):

```text
16 passed in 0.05s
```

`.venv/bin/python -m pytest tests/ -q` (worktree):

```text
9 failed, 1343 passed, 28 skipped, 3 warnings in 69.94s (0:01:09)
```

`.venv/bin/python -m pytest -q test_*.py` (worktree):

```text
1324 passed, 40 skipped in 70.12s (0:01:10)
```

Script đo kết thúc exit 0. Bộ `tests/` trả exit 1: các kiểm E2E contrast/overflow gặp `npm error code EPERM` tại cache ngoài workspace; các kiểm scenes không khởi động được trình duyệt. Các test gốc trả exit 0. Chưa tuyên bố toàn bộ bộ kiểm đạt. Tên từng test lỗi và thông báo nằm trong [JSON kết quả kiểm](2026-11-18-visual-mix-fsbud-vsd.checks.json); đây là kết quả test đã chạy, không phải audit tự chạy lại tests.

Không có composition mới hoặc sửa layout, nên không nhận “tiền kiểm hình đạt”, không chạy render/đăng/kiểm ảnh như một bài sản xuất. Các lỗi môi trường test không bị đổi thành pass; không sửa mã ngoài phạm vi.

## Lead cần quyết

- Duyệt ngưỡng/lane Short, nhất là bảng tra và trích lời ngắn; duyệt kế hoạch bổ sung timing/mẫu VSD.
- Xác nhận cập nhật mới trên issue #467 so với bản cục bộ; thống nhất giây thay vì số cảnh.
- Mở ticket adapter riêng để xử lý Studio lồng và danh tính ảnh trước khi dùng các chỉ số ảnh làm cổng.
- Quyết định sửa giới hạn cảnh ngoài cửa sổ đầu trong ticket sau; nghiên cứu này giữ nguyên toàn bộ cổng.
- Chạy lại các test cần npm/Chromium ở môi trường có quyền phù hợp; không cần sửa logic QA để làm xanh báo cáo này.

## Bản nháp comment cho #467 (Lead tự đăng)

Đã bổ sung đo FS/BUD/VSD trong docs/research/2026-11-18-visual-mix-fsbud-vsd.md và JSON kèm hash nguồn. Long đo bằng adapter visual_mix_scenes + measure với segments thật: BUD 30 video, chữ 36.53% thời lượng; FS 36 video, 22.42%. Chưa có Long VSD.

Short đủ 20 mẫu BUD và 20 FS: chữ khác bảng 45.93%/23.14%; riêng FS không bảng là 53.48%. VSD chỉ 14 spec, 3 job có timing: 57.16%, chưa đủ mẫu hoặc xác minh MP4. Bảng tra phải theo dõi riêng, không xem là chữ lấp chỗ.

Đề nghị Long giữ mốc 15.00% theo giây. Short kể thí điểm mục tiêu 30.00%, vượt 40.00% Lead review; bảng đúng mục đích được ngân sách riêng. Cần giữ ngoại lệ nhịp mở đầu, dùng cuts/pan thay chữ; giới hạn cảnh dài hiện vẫn còn nên muốn bỏ phải ticket riêng.

Lõi tools.visual_mix đã dùng chung hai nhánh; còn thiếu chuẩn hoá adapter Studio lồng, danh tính ảnh và lane. Chỉ số ảnh hiện là ref nhận diện được, không phải đầy đủ ảnh thật. Chưa đổi cổng, render hay đăng comment.
