# Kế hoạch migration: đề xuất #327 + sửa nối dây cải thiện cũ

Ngày 13/11/2026. Chủ kênh đã duyệt các đề xuất trong `docs/pm/bud-fs-28d-2026-11-research.md` (PR #332) và đặt luật: **mỗi cải thiện phải gắn vào workflow đang chạy, không để dead code; khi migration thì kiểm luôn các cải thiện trước.**

Mỗi mục dưới đây ghi bốn thứ:
- **Gắn vào**: bước nào của workflow gọi tới (skill, builder, lint, runner, upload).
- **Thay gì**: phần cũ bị thay hoặc bị gỡ. Không viết thêm bản song song.
- **Bằng chứng chạy**: test hoặc cổng sẽ đỏ nếu bị bỏ qua.
- **PR**: nhóm PR thực hiện.

## Đường chạy hiện tại (để đối chiếu)

```
kịch bản (.txt) ──long_script_lint──▶ tools/long_plan_build.py ──▶ plan_L_*.json
   │                                        │ (phải qua save_plan_rows → wire_plan_row,
   │                                        │  style_suggest, layout_policy v2)
   ▼                                        ▼
hf_batch_render.py: lint → TTS → pacing() [pace gate, O1–O8] → render chương → mux → O9
   ▼
upload_long.py (hẹn giờ) ──▶ long-packaging: promise_check, ab_ledger, Video liên quan
```

## Phần A — Sửa nối dây cải thiện cũ (audit 13/11)

Audit đọc code các PR merge từ 20/10. Lead đã đối chiếu các điểm dưới đây với code và tất cả đều đúng.

| # | Vấn đề | Gắn vào / sửa | Thay gì | Bằng chứng chạy | PR |
|---|---|---|---|---|---|
| A1 | `tools/long_plan_build.py` (#320) ghi plan bằng `write_text` nên bỏ qua `save_plan_rows`/`wire_plan_row`. Plan dựng ra thiếu `layout_policy: v2`, không được `style_suggest` áp, `keep` không chép `layout_policy`. | Cuối `build`/`build_new` gọi `hf_batch_render.save_plan_rows(out, [plan], legacy=False)`. | Bỏ hai chỗ `write_text`. Sửa skill `long-video` dòng 92 và 115 cho đúng hàm thật. | Test mới: dựng fixture xong thì plan có `layout_policy: "v2"`, có wire giọng/âm, `bare_lines == []`. | M1 |
| A2 | Bản cũ `output/cl_staging/long/pilot_plan_build.py` (+ `.bak_1112`) trùng với tool mới. | Không cần gắn gì. | Chuyển vào Thùng rác. | `grep` không còn ai gọi bản cũ. | M1 |
| A3 | Bảng Mùi 2027 bị hardcode trong tool chung `long_plan_build.py:83`. | Chuyển sang dữ liệu plan hoặc file JSON riêng của pilot. | Gỡ khỏi tool. | Test: tool không chứa dữ liệu của một video cụ thể. | M1 |
| A4 (M8) | Script đăng thật và asset gate ở ngoài git. | Đã chuyển vào `tools/publish/` và `tools/long/`; skills, docs và test trỏ đường mới. | Bản trong `output/` Lead chuyển vào Thùng rác sau khi PR merge. | Test khói `--help`; test asset gate chạy từ bản trong git. | M8 |
| A5 | O9 chỉ chạy khi mp4 đã có từ lần trước, nên lần render đầu bỏ qua. | Sau khi mux xong mp4 lần này, runner gọi `opening_gate(row, segs, video_path=<mp4 mới>)`. Nếu O9 lỗi thì đánh dấu HỎNG nhưng **giữ** file để Lead xem. | Gỡ `opening_gate_issues/_warnings` nếu không còn ai gọi ngoài test. | Test: render giả có khung trống 0,5 s trong 40 s đầu thì runner báo HỎNG ngay lần đầu. | M2 |
| A6 | `hf_media_sheet.py` không hiểu `kind: local` nên báo "KHÔNG CÓ CLIP". Trong khi đó skill và bridge đều dùng `local`. | Thêm nhánh `local` (đọc file). | Thôi nạp thủ công như thợ 049 đã phải làm. | Test: plan có media `local` thì sheet ra đủ ảnh. | M2 |
| A7 | `agy_route.usable()` coi pool vắng là dùng được, nên vẫn chọn Argon (Mac không có Argon). Không skill nào gọi `agy_route.py`. `review_gate.sh` cố định Flash. | `review_gate.sh` lấy model qua `agy_route.py pick review`; pool vắng tính là không dùng được; dự phòng `claude-sonnet-4-6`. Skill `lead-dispatch` ghi bước này. | Gỡ model cố định trong `review_gate.sh`. Sửa dòng lỗi thời ở `docs/agents/agy-machine-c.md:79`. | Test: cache quota không có argon thì `pick` không trả argon. Gemini hết thì trả Claude. | M3 |
| A8 | `promise_check` (#297) chỉ chạy tay. | Gọi trong `upload_long.py` trước khi hẹn giờ: lỗi chặn, cảnh báo thì in ra. | Bỏ câu "chạy tay" trong skill. | Test: plan có lời hứa thumbnail không có trong kịch bản thì upload dừng. | M2 |
| A9 | `kinetic_suggest` (#294): `plan_enrich` có ghi nhưng không ai đọc. | Runner cảnh báo khi plan Long `layout_policy: v2` còn `kinetic_suggest` mà chưa có visual nào dùng preset. Không tự áp, vì style mới chỉ được opt-in theo luật 10/11. | Nếu đến 30/11 vẫn không ai dùng thì gỡ khoá này khỏi `plan_enrich`. | Test cảnh báo. | M3 |
| A10 | `test_lookup_flap.py` chỉ dò chuỗi trong mã nguồn. Không có lint bắt bảng `lookup` thiếu `find`. | Runner cảnh báo bảng tra năm sinh không có `find` (sẽ không có ô lật số). | Không gỡ test regex cũ. Thêm test dựng HTML thật bằng bridge. | Test mới dựng thật. | M3 |

## Phần B — Đề xuất #327 gắn vào workflow

| # | Đề xuất | Gắn vào | Thay gì | Bằng chứng chạy | PR |
|---|---|---|---|---|---|
| B1 | Cold open Long: nhân vật xuất hiện trong 5 giây đầu, cảnh đỉnh ở câu 1. | Skill `long-script` luật 1. `long_script_lint` thêm cảnh báo `NHAN_VAT_MUON` khi tên nhân vật (lấy từ `format: nhan_vat`/`kicker` hoặc tiêu đề) chưa xuất hiện trước khoảng 15 tiếng đọc đầu (khoảng 5 giây). | Viết lại luật 1 hiện có, không thêm luật mới. | Test lint. Lint đã chạy trước TTS trong runner, nên cảnh báo sẽ hiện ở mỗi lần render. | M4 |
| B2 | Dời câu nguồn ("dựa trên kinh...") xuống sau giây 90. | Skill `long-script` luật 2. Lint cảnh báo nếu câu nguồn nằm trong 60 giây đầu. Trên BUD, bỏ qua câu có tên kinh khi tên kinh chính là tiêu đề. | Sửa luật 2. | Test lint. | M4 |
| B3 | Khuôn "Long ngắn 5–8 phút" (suất pilot 1–2 bài/tuần/kênh). | `long-script/references/formats.md` thêm format `ngan` (ngân sách 925–1.500 tiếng, 4–6 chương, khuôn mở mục 4). `long_script_lint --format ngan` kiểm độ dài. `tools/long_plan_build.py --format ngan` để runner bỏ yêu cầu ≥30 phút cho format này. | Luật "Long ≥30 phút" giữ cho format khác. | Test lint và test builder. Runner không báo "quá ngắn" với `format: ngan`. | M4 |
| B4 | Bước ngoặt chính đặt ở 75–85% thời lượng. | Skill `long-script`, khuôn nhân vật. Lint gợi ý (không chặn) dựa trên `reward_at`, nếu plan có. | Nhập vào luật "phần thưởng 50%, cảnh mạnh 75%" đang có. | Test lint. | M4 |
| B5 | Thumbnail BUD: nhân vật cận mặt, 2–5 chữ. A/B chỉ đổi thumbnail. Ưu tiên video có AVP cao mà CTR thấp. | Skill `long-packaging`. `tools/long_packaging/ab_ledger.py` thêm lệnh `candidates` (đọc Studio CSV, lọc AVP ≥ 25% và CTR < trung vị kênh). | Không có thay thế. | Test `candidates` trên CSV mẫu. | M5 |
| B6 | Mẫu tiêu đề Search FS ("tuổi/năm sinh + 2027 + chủ đề"). | Skill `long-packaging`. `seo_check.py` gợi ý mẫu khi tiêu đề FS không chứa năm hoặc tuổi. | Không có thay thế. | Test `seo_check`. | M5 |
| B7 | Gắn "Video liên quan" từ Short sang Long: FS khi Short trên 100 nghìn lượt xem, BUD khi Short ≥ 1.000 lượt xem và AVP ≥ 100%. | `tools/long_packaging/related_map.py`: đọc CSV và danh sách Long, đề xuất cặp và ghi sổ `related_ledger.json`. Lead gửi chủ kênh bảng ghép, sau đó gắn trong Studio. Đo lại sau 14 ngày. | Thay việc ghép bằng tay như ngày 10/11. | Test ghép trên CSV mẫu. Sổ ghi ngày gắn để đo. | M5 |
| B8 | Short FS 10 giây kiểu bảng tra: câu mở "Bạn sinh năm bao nhiêu?", đủ 12 chi, "dừng hình", khung cuối ≥ 3 giây. Thử E6/E7. | Skill `shorts-lookup` §1/§2. Device bảng tra trong `studio.py`: thêm tuỳ chọn `opener=nam_sinh` và `loop=1`. QA `studio.py` kiểm khung cuối ≥ 3 giây. | Gộp vào dạng 1 đang có. | Test studio QA. | M6 |
| B9 | Chuỗi kinh chú: mỗi tập đặt tiêu đề độc lập, không dùng "Câu thứ N", tối đa 5 tập. Thêm dạng "dừng hình đọc theo" và gắn nhãn Đại thừa. | Skill `shorts-lookup` §7 và dạng 7. `studio.py` QA cảnh báo khi tiêu đề có dạng "Câu thứ N". | Không có thay thế. | Test QA. | M6 |
| B10 | Thử nghiệm E1–E12. | Sổ `output/cl_staging/experiments/` cùng `ab_ledger.py`. Skill `long-packaging` bước 7 thêm mốc đo 14 ngày. `review_due.py` nhắc đến hạn đo. | Không có thay thế. | `review_due.py` hiện việc khi tới mốc. | M5 |

## Thứ tự PR

| PR | Nội dung | Ưu tiên | Ai làm |
|---|---|---|---|
| M1 | A1–A3: builder qua `save_plan_rows`, gỡ bản trùng và dữ liệu hardcode | P0 | Codex + review gate |
| M2 | A4–A6, A8: đưa upload và asset gate vào git, O9 sau render, media sheet `local`, `promise_check` trong upload | P0/P1 | Codex + review gate |
| M3 | A7, A9, A10: agy_route và review_gate theo hạn mức, cảnh báo kinetic và lookup | P1 | Codex + review gate |
| M4 | B1–B4: luật kịch bản, lint, format Long ngắn | P1 | Lead viết luật; Codex viết lint và test |
| M5 | B5–B7, B10: packaging, A/B, Video liên quan, sổ thử nghiệm | P1 | Codex + Lead |
| M6 | B8–B9: Short FS 10 giây, chuỗi kinh chú | P2 | Codex + Lead |

Mỗi PR có mục **"Migration"** trong mô tả: nơi gọi, phần cũ đã gỡ, test chứng minh đường chạy dùng nó. Sau khi merge, Lead chạy lại một plan thật qua đúng đường chạy (dựng plan, gate, render một chương) để xác nhận.

## Không làm

- Không tự áp `kinetic_suggest` hay style mới vào plan, vì style mới chỉ được opt-in theo luật 10/11.
- Không sửa tiêu đề hoặc thumbnail của video đã hẹn giờ, trừ khi chủ kênh yêu cầu.
- Không gắn "Video liên quan" khi chủ kênh chưa xem bảng ghép.
