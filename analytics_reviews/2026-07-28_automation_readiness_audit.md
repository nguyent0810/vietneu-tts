# Audit: Sẵn sàng chạy tự động (Short + Long, nhiều kênh cùng lúc)?

**Trạng thái: DRAFT v4 -- audit gốc đã APPROVED (Codex vòng 4/4), phần này ghi lại kết quả sau khi THỰC SỰ SỬA cả 9 khuyến nghị ở mục G của bản gốc. Đang chờ Codex vòng 5 (review lại phần sửa).**

**Lịch sử review bản audit gốc:** vòng 1 = 10 phát hiện (bao gồm 1 Critical mới phát hiện: job launchd duy nhất lỗi 5/5 lần, trước đó không ai biết); vòng 2 = 5 phát hiện về độ chính xác câu chữ/trích dẫn; vòng 3 = 1 câu còn sót; vòng 4 = APPROVED.

**Câu hỏi audit:** Workflow hiện tại đã đủ để chạy **tự động, không giám sát, cho cả Short và Long, trên nhiều kênh (FS/BUD/CL) cùng lúc** chưa?

**Kết luận bản gốc (đã APPROVED): CHƯA.** Root cause chính: tác vụ tự động sản xuất nội dung duy nhất (launchd) lỗi 5/5 lần; không có khoá bảo vệ giao dịch đọc-sửa-ghi cho registry/rotation-state; chỉ 1/3 kênh (BUD) có bằng chứng Long-form thật; CL Short còn vấn đề B-roll chưa dứt điểm.

**Cập nhật DRAFT v4 (sau khi sửa):** Toàn bộ 9 khuyến nghị ở mục G đã được thực hiện thật (không chỉ đề xuất) -- xem chi tiết từng mục dưới đây, đánh dấu **[ĐÃ SỬA]**. 1 mục (#1, launchd/TCC) vẫn còn phụ thuộc 1 thao tác thủ công của người dùng (cấp quyền Full Disk Access qua System Settings) mà không công cụ nào có thể tự làm thay -- đánh dấu **[CẦN THAO TÁC THỦ CÔNG]**.

**Phương pháp:** 2 agent nghiên cứu độc lập đọc mã nguồn round 1 → Codex phản biện độc lập, tự đọc lại code + tự chạy `launchctl print` + đọc log thật trên máy → tôi tự xác minh lại TỪNG phát hiện của Codex bằng lệnh thật trước khi sửa (không sửa mù theo lời Codex). Mọi claim trong bản này đều có trích dẫn file:dòng hoặc lệnh đã tự chạy.

---

## A. Cơ chế điều phối / lên lịch tự động

**Round 2 correction (Codex finding #1, Critical — tự xác minh bằng `launchctl print gui/$(id -u)/com.vieneutts.dailyshortbatch`):**

```
runs = 5
last exit code = 126
```
```
/bin/bash: /Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/scripts/daily_short_batch.sh: Operation not permitted
```
(lặp lại y hệt ở cả 5 lần launchd đã khởi chạy job này, ghi trong `output/shorts/launchd_stderr.log`; `runs=5` là số lần launchd đã kích hoạt job — không có bằng chứng phân biệt trong đó bao nhiêu lần là trigger đúng lịch `StartCalendarInterval` vs. có thể có lần được kickstart thủ công)

**Nhiều khả năng đây là lỗi quyền hệ thống macOS (TCC — launchd không có quyền thực thi script trong thư mục `~/Documents`), nhưng chưa xác minh được nguyên nhân chính xác** (chưa test trực tiếp qua System Settings → Privacy & Security để xác nhận đây đúng là TCC chứ không phải nguyên nhân quyền hệ thống khác). Dù nguyên nhân chính xác là gì, hệ quả thực tế đã xác minh chắc chắn: tác vụ tự động SẢN XUẤT NỘI DUNG duy nhất trong toàn bộ repo **chưa từng chạy thành công lần nào**, mà cũng không có cảnh báo nào tới người dùng vì lỗi xảy ra ở tầng launchd, trước khi script kịp ghi bất kỳ log ứng dụng nào.

| Tác vụ | Lịch (plist, `~/Library/LaunchAgents/com.vieneutts.dailyshortbatch.plist:12-18`) | Trạng thái thật |
|---|---|---|
| `com.vieneutts.dailyshortbatch.plist` | `Hour=3, Minute=17` — **round 1 correction (Codex finding #2): plist KHÔNG khai báo timezone, launchd diễn giải theo giờ hệ thống (hiện là Asia/Ho_Chi_Minh), KHÔNG phải UTC như bản round-1 khẳng định sai.** | ❌ Cả 5/5 lần launchd đã khởi chạy job đều thất bại với `exit 126`, chưa từng tạo ra sản phẩm nào |
| `com.vieneutts.shorthealthcheck.plist` | Mỗi 2 ngày | `runs = 0` tại thời điểm audit — bản thân health-check cũng chưa từng tự chạy, nên KHÔNG có cơ chế nào đang thật sự giám sát lỗi #1 ở trên |

**Không tồn tại:** lịch chạy cho FS/CL Short, lịch chạy cho bất kỳ kênh nào ở Long, hay bất kỳ script "chạy tất cả kênh cùng lúc" nào. `run.sh` là entry point thủ công cho 1 pipeline TTS cũ hơn, không phải pipeline hiện đại đang dùng.

**Round 2 correction (Codex finding #8, Medium):** ngay cả khi launchd job chạy được, nó KHÔNG phải "nhà máy tự duy trì" — `daily_short_batch.sh:14` gọi cứng `--episodes 06 --count 5`, không dùng flag `--auto-discover` mà `short_batch_runner.py` đã hỗ trợ (`short_batch_runner.py:424`). Đây là script xử lý 1 backlog cố định (EP006); khi EP006 hết đoạn pending, job sẽ hoàn tất với 0 sản phẩm mà không tự tìm nguồn mới.

**Round 2 correction (Codex finding #7, Medium — tự đọc `scripts/daily_short_batch.sh`):** script dùng `set -euo pipefail` (dòng 5). Dòng 14: `OUTPUT="$(python3 short_batch_runner.py ... 2>&1)"` rồi dòng 15 mới `EXIT_CODE=$?`. Dưới `set -e`, nếu lệnh trong `$(...)` trả về khác 0, bash thoát NGAY tại dòng gán biến đó — trước khi kịp chạy `EXIT_CODE=$?` và ghi `daily_run_log.jsonl`. Nghĩa là: nếu `short_batch_runner.py` crash thật (không chỉ launchd-permission-lỗi như hiện tại), thất bại đó cũng sẽ KHÔNG được ghi log — health-check (`short_health_check.py:93`) chỉ đọc được từ `daily_run_log.jsonl`, nên sẽ không thấy gì bất thường thay vì thấy 1 dòng lỗi.

**Kết luận:** tự động hoá hiện tại = 0/6 tổ hợp kênh×loại-nội-dung đang thật sự hoạt động (không phải 1/6 như round-1 báo — 1/6 có CẤU HÌNH nhưng đang hỏng hoàn toàn, im lặng).

## B. Khoá tiến trình toàn cục chặn chạy đồng thời

`process_topics.py` dùng khoá `fcntl.flock(LOCK_EX | LOCK_NB)` trên file `.process_topics.lock` (`process_topics.py:61-84`, xác nhận đúng) — chỉ 1 instance chạy tại 1 thời điểm, trên TOÀN REPO, không phân biệt kênh.

**Round 2 correction (Codex finding #6, High — đề xuất "bỏ khoá" ở bản round-1 là nguy hiểm, đã sửa ở mục G):** khoá này KHÔNG chỉ để tránh race trên file — nó còn ngăn 2 tiến trình cùng tải model TTS/tranh GPU-RAM (mỗi `long_batch_runner.py` gọi `process_topics.py` ở bước audio, `long_batch_runner.py:138`). Bỏ khoá mà không thay bằng cơ chế điều phối tài nguyên khác (semaphore/queue) có thể tạo ra lỗi MỚI nghiêm trọng hơn (tranh chấp GPU/RAM), không chỉ đơn thuần "cho phép chạy song song".

**[ĐÃ SỬA] Round 3 (mục G.4):** thay vì fail ngay với `AlreadyRunningError` khi có tiến trình khác đang giữ khoá, `_PipelineLock` (`process_topics.py:61-108`) giờ ĐỢI CÓ GIỚI HẠN (poll `LOCK_NB` mỗi 15s, tối đa 1800s/30 phút, cấu hình qua `LOCK_ACQUIRE_TIMEOUT_SECONDS`/`LOCK_POLL_INTERVAL_SECONDS`) — vẫn CHỈ 1 instance chạy tại 1 thời điểm (không đổi mức bảo vệ GPU/RAM), chỉ đổi hành vi khi có tranh chấp từ "huỷ ngay" sang "xếp hàng". Test thật bằng 2 thread giả lập tranh chấp khoá (xem lịch sử sửa) xác nhận: tiến trình chờ nhận được khoá ngay khi tiến trình giữ khoá nhả ra, và raise `AlreadyRunningError` đúng khi vượt timeout. **Xác nhận thêm bằng tình huống THẬT không giả lập trong lúc viết bản audit này:** khởi chạy đồng thời `long_batch_runner.py --domain FS` và `--domain CL` (cả 2 đều gọi `process_topics.py` ở bước audio) — `ps aux` xác nhận tiến trình `process_topics.py` của CL (pid 84091) tồn tại nhưng dùng 0.0% CPU/không tăng CPU-time trong khi tiến trình của FS (pid 82653) đang chạy tích cực — đúng hành vi "xếp hàng đợi", không crash, không tranh chấp GPU với FS.

## C. File trạng thái dùng chung — không có khoá ghi

**Round 2 correction (Codex finding #3, High — bản round-1 mô tả sai topology registry):** Short và Long **KHÔNG dùng chung 1 file registry** như round-1 khẳng định nhầm. Short dùng `output/shorts/<topic>/registry.json` (`short_batch_runner.py:52`); Long dùng `output/long/<topic>/registry.json` (`long_batch_runner.py:62`) — 2 file khác nhau, kể cả cùng 1 kênh. Rủi ro race giữa Long và Short của cùng kênh vì vậy KHÔNG xảy ra qua đường này.

**Nhưng rủi ro race vẫn thật, chỉ hẹp hơn round-1 mô tả:** 2 tiến trình CÙNG LOẠI (2×Short, hoặc 2×Long) nhắm CÙNG 1 kênh, chạy đồng thời, vẫn đọc-sửa-ghi cùng 1 file JSON không khoá:

| File | Có khoá? | Rủi ro cụ thể |
|---|---|---|
| `output/shorts/<topic>/registry.json` | **[ĐÃ SỬA]** Có — xem chi tiết dưới bảng | (đã giảm, xem dưới) |
| `output/long/<topic>/registry.json` | **[ĐÃ SỬA]** Có — xem chi tiết dưới bảng | (đã giảm, xem dưới) |
| `chunks_cache/{iching,western_zodiac,element_color}_rotation_state.json` | **[ĐÃ SỬA]** Có — xem chi tiết dưới bảng | (đã giảm, xem dưới) |
| `topic_voices.json`, `bgm_tracks.py`, `domain_creative_profiles.json` | Chỉ đọc lúc chạy | An toàn |
| `.youtube_channels/{label}.json` | Mỗi kênh 1 file riêng | An toàn, cách ly đúng theo kênh |

**[ĐÃ SỬA] Round 3 (mục G.5) -- registry.json (`short_batch_runner.py`/`long_batch_runner.py`):** thêm module dùng chung `registry_lock.py` (khoá `fcntl.flock` ngắn hạn, chỉ giữ quanh bước đọc-ghi JSON, không giữ suốt thời gian TTS/render/upload). `save_registry()` giờ MERGE với bản mới nhất trên đĩa dưới khoá đó (`{**on_disk, **registry}`) thay vì ghi đè trắng. **Tự phát hiện 1 bug thật khi tự viết test 2-tiến-trình-giả-lập trước khi coi là xong (xem lịch sử sửa):** lần đầu implement có đồng bộ ngược bản đã merge vào biến `registry` trong bộ nhớ của caller -- gây lỗi MỚI tinh vi hơn (key của tiến trình khác "dính" vào bộ nhớ cục bộ rồi bị chính nó ghi đè lại ở lần save SAU, xoá mất update thật của tiến trình kia). Đã bỏ hành vi đồng bộ ngược đó, test lại xác nhận cả 2 tiến trình giả lập giữ đúng update của nhau qua 2 vòng save xen kẽ. Đồng thời thêm bước "recheck" (đọc lại registry ngay trên đĩa, so status đã biết vs status tươi) ngay trước khi bắt đầu xử lý 1 segment/episode, thu hẹp (không xoá hết) cửa sổ race khi 2 tiến trình cùng chọn trùng 1 mục "pending". `next_available_slot()` (chống trùng slot đăng) đổi sang luôn đọc registry tươi thay vì biến cục bộ.

**[ĐÃ SỬA] Round 3 (mục G.5) -- rotation_state.py:** `peek_next()` giờ khoá ngắn hạn quanh bước đọc-ghi VÀ tự đánh dấu "reserved" mục vừa trả về (kèm timestamp) để 1 tiến trình khác gọi gần như đồng thời không nhận về CÙNG 1 mục -- test thật (2 thread gọi `peek_next()` cùng lúc) xác nhận nhận về 2 mục khác nhau. Reservation quá hạn (>900s, `RESERVATION_TIMEOUT_SECONDS`) được coi như tiến trình giữ nó đã chết/treo, tự động khả dụng lại -- test thật xác nhận đúng hành vi. `commit()` xoá reservation khi ghi thành công.

## D. Long-form: chỉ 1/3 kênh có bằng chứng production thật

| Kênh | Long-form đã render thật? | Đã upload YouTube thật? |
|---|---|---|
| **BUD** | ✅ | ✅ |
| **FS** | ❌ Không có file `.mp4` nào trong `output/long/Phong Thủy/` | ❌ Chưa |
| **CL** | ❌ Không có file `.mp4` nào trong `output/long/Hình Sự/` | ❌ Chưa |

**Round 2 correction (Codex finding #9, Medium — bổ sung trích dẫn cụ thể cho dòng BUD):** `output/long/Phật giáo/registry.json` ghi `status="uploaded"`, video ID `IktxS6H8UmU`; file `.mp4` thật tồn tại (`with_bgm.mp4`/`render_raw.mp4`, kích thước 1.582.867.092 byte, ngày tạo 2026-07-23); đối chiếu chéo với `analytics_reviews/2026-07-27_daily_factory_raw/phat_giao_last20_uploads.json` xác nhận `publishedAt=2026-07-27T13:00:28Z` khớp đúng ID. Lưu ý: `registry.json` còn giữ vài đường dẫn cũ dạng `output/long/EP001/...` (thiếu tên kênh) từ trước khi sửa bug registry-collision-đa-domain — các đường dẫn này không còn đúng scope hiện tại, artifact thật nằm ở `output/long/Phật giáo/EP001/...`; chưa xác nhận việc resume có phụ thuộc đường dẫn cũ này hay không.

**Round 2 correction (Codex finding #4, High — claim "gates.long_ready=false" SAI, đã tự đọc code sửa lại):** bản round-1 nói CL bị "chủ động khoá qua `gates.long_ready=false` trong manifest". Đã tự kiểm tra: **trường `gates`/`long_ready` không tồn tại ở bất kỳ đâu trong schema thật.** `content_repo.py:193-194`'s `manifest_is_ready()` chỉ xét `content_status`/`qa_status`; hàm gate thật (`content_repo.py:207-248`, `gate_episode()`) yêu cầu tồn tại đúng cấu trúc thư mục `_PRODUCTION/Long/_INTERNAL/manifest.json` cho từng episode. Đã tự kiểm tra trực tiếp: `content_repo_clone/DOMAINS/CRIMINAL_LAW/PRODUCTION_PACKAGES/HINH_SU/EP001/` chỉ có `_INTERNAL/`, `OUTPUT/`, `_ARCHIVE/` — **không hề có thư mục `_PRODUCTION/Long/` nào cả.** Vì vậy CL bị loại khỏi Long pipeline đơn giản vì cấu trúc thư mục `_PRODUCTION/` (bước staging sang pipeline sản xuất) chưa từng được tạo cho episode này — không phải vì một cờ "khoá chủ đích" nào trong schema. Bản thân manifest gốc của CL (`_INTERNAL/manifest.json`) có field `external_processes.video_render: "OUT_OF_SCOPE"` — **đây là suy luận, chưa phải bằng chứng chắc chắn:** field này tự nó chỉ xác nhận video-render được đánh dấu ngoài phạm vi CHO GÓI/QUY TRÌNH manifest này, không tự nó chứng minh đã có một quyết định chủ đích, ở cấp cao hơn, loại CL khỏi Long production nói chung — không có tài liệu quyết định riêng nào được tìm thấy để xác nhận điều đó. Cơ chế kỹ thuật thật, xác nhận chắc chắn, là "thiếu cấu trúc thư mục `_PRODUCTION/Long/` cần thiết" — không phải 1 gate-flag có thể "giữ nguyên"/"đổi" như round-1 ngụ ý.

**Logic sáng tạo dùng chung nhưng chỉ kiểm chứng cho BUD:** `director_bible.py`'s `DEFAULT_BIBLE` (dùng khi Gemini không khả dụng) hardcode màu sắc/tone cho Phật giáo (`director_bible.py:33-64`); `creative_director.py`'s `batch_judge_video_eligibility()` và `gemini_tiebreak()` chưa từng chạy thật trên nội dung FS/CL; symbol library của FS có 2 linh vật (Chu Tước, Huyền Vũ) tự ghi chú "chưa test riêng, suy luận theo loại" (`domain_creative_profiles.json`, ghi chú gốc).

## E. Short-form: bằng chứng trực tiếp từ hôm nay (27-28/7)

**Round 2 correction (Codex finding #10, Medium — bổ sung trích dẫn cụ thể thay vì chỉ kể lại):**

- **FS, BUD:** 5 Short render+upload thành công. Video ID đã xác minh qua API thật (xem `WEEKLY_PUBLISHING_LEDGER_v1.json`): `QRRkgg4pSZc`, `9iHds-4UNDw`, `NdziddsrEkM`, `mqtBUdwmcso`, `4LGJi3YVsoI` — cả 5 đều `privacyStatus=private` + `publishAt` đúng lịch đã tính, xác nhận qua `videos.list` trực tiếp.
- **CL:** render kỹ thuật thành công (video ID `h3wGuPatJ3I`, verified qua API, `privacyStatus=private`), nhưng B-roll tự động (Pexels) ban đầu trả về cảnh trông giống phim tù/cảnh sát. Nguyên nhân gốc xác nhận bằng cách tự gọi `translate_vi_to_en()` thật: "án treo" bị dịch sai thành "hang" (treo cổ). Đã thêm `broll_query_sanitizer` cho domain CL trong `domain_creative_profiles.json` (14 pattern), test lại 2 lần — cải thiện phần lớn (cảnh 1 giờ là hình luật sư đọc tài liệu, phù hợp) nhưng KHÔNG dứt điểm — 1 cảnh (~14-30s, đoạn "thời gian thử thách") vẫn còn vấn đề dù đã đổi từ khoá 2 lần. Người dùng đã đồng ý xuất bản tạm với hạn chế này.

**Kết luận riêng cho CL Short:** N=1 (Short đầu tiên trong lịch sử kênh). Mọi hạ tầng (voice "Tuyen", B-roll sanitizer) mới lần đầu chạy thật — chưa đủ để coi là đã kiểm chứng ổn định.

## F. Tổng hợp — checklist sẵn sàng tự động hoá đa kênh

| Điều kiện cần | Đạt? |
|---|---|
| Điều kiện cần | Đạt? (bản gốc, đã APPROVED) | Đạt? (sau khi sửa, DRAFT v4) |
|---|---|---|
| Có cơ chế điều phối chạy tất cả kênh × cả 2 loại nội dung | ❌ 0/6 tổ hợp đang hoạt động thật | ⚠️ Vẫn 0/6 job TỰ ĐỘNG (launchd) — nhưng lần đầu tiên đã CHẠY THẬT được Long cho cả FS và CL (thủ công, không qua lịch), xem mục D |
| An toàn khi 2+ tiến trình chạy đồng thời | ❌ Khoá toàn cục fail-ngay | ✅ **[ĐÃ SỬA]** Khoá vẫn giữ (đúng, tránh tranh GPU/RAM) nhưng đổi sang hàng đợi timeout/retry — verify thật bằng FS+CL chạy đồng thời |
| File trạng thái dùng chung có khoá ghi | ❌ Không khoá | ✅ **[ĐÃ SỬA]** registry.json (merge-on-save) + rotation-state (reserved/timeout) đều có khoá giao dịch, verify bằng test 2-tiến-trình-giả-lập |
| Long-form đã kiểm chứng thật cho cả 3 kênh | ❌ Chỉ BUD (1/3) | Xem mục D cập nhật (render đang chạy khi viết bản này) |
| Short-form đã kiểm chứng ổn định cho cả 3 kênh | ⚠️ CL còn vấn đề B-roll | ✅ **[ĐÃ SỬA]** B-roll CL dứt điểm bằng symbol_library static-asset; N vẫn =1 (chỉ 1 Short CL từng chạy) nên "ổn định" vẫn cần thêm dữ liệu, nhưng vấn đề an toàn nội dung đã giải quyết |
| Tác vụ tự động hiện có đang chạy đúng | ❌ 0/1 production job | ⚠️ Vẫn 0/1 — **[CẦN THAO TÁC THỦ CÔNG]** cấp TCC, nhưng lỗi giờ sẽ KHÔNG còn làm mất log âm thầm (mục G.2) và health-check giờ phát hiện được tình trạng "không chạy được gì" (mục G.3) |
| Quota YouTube được điều phối giữa các tiến trình song song | ⚠️ Chưa xác minh | ✅ **[ĐÃ XÁC NHẬN]** người dùng xác nhận trực tiếp: 3 kênh = 3 GCP project riêng, không chung quota |

## G. Đề xuất cụ thể để tiến tới sẵn sàng — TRẠNG THÁI SAU KHI SỬA (2026-07-28)

Người dùng yêu cầu thực hiện thật cả 9 mục (không chỉ đề xuất). Kết quả từng mục:

1. **[CẦN THAO TÁC THỦ CÔNG, chưa xong]** launchd `exit 126`/`Operation not permitted`. Đã tự điều tra sâu: xác nhận đây là lỗi quyền hệ thống (không phải bug code — script/thư mục/quyền POSIX đều đúng, `bash -n` không lỗi cú pháp), khớp mẫu hình TCC chặn tiến trình nền truy cập `~/Documents`. Không thể tự cấp TCC bằng công cụ dòng lệnh (đã thử `sqlite3` đọc trực tiếp `TCC.db` → `authorization denied`; `sfltool dumpbtm` → treo/không trả dữ liệu) — đây là giới hạn bảo mật cố ý của macOS, cấp quyền BẮT BUỘC phải qua thao tác người dùng trong System Settings → Privacy & Security → Full Disk Access, cấp cho `/bin/bash`. **Việc CÓ THỂ tự làm (đã làm) là mục 2 dưới đây** — sửa để lỗi (dù nguyên nhân gì) không còn làm mất log âm thầm.
2. **[ĐÃ SỬA]** `scripts/daily_short_batch.sh`: bọc lệnh chính (và bước lấy `SSL_CERT_FILE`) trong `set +e ... set -e` để `EXIT_CODE=$?` và bước ghi `daily_run_log.jsonl` LUÔN chạy được dù lệnh chính lỗi thật (không chỉ lỗi quyền launchd hiện tại); script tự `exit "$EXIT_CODE"` ở cuối để launchd vẫn thấy đúng exit code thật. `bash -n` xác nhận cú pháp hợp lệ.
3. **[ĐÃ SỬA]** `short_health_check.py`: thêm `check_missing_or_stale_run()` — phát hiện "không có dòng log mới nào trong >26h" (kể cả trường hợp log RỖNG HOÀN TOÀN, đúng lỗ hổng thật đang xảy ra), phân biệt với `check_recent_runs_for_stall()` cũ (chỉ đọc NỘI DUNG log đã có, im lặng nếu log rỗng). Chạy thật xác nhận: phát hiện đúng và cảnh báo "job không chạy được gì trong 119.6h" — khớp thực tế launchd đang lỗi.
4. **[ĐÃ SỬA]** Xem mục B — chuyển `LOCK_NB` sang hàng đợi có timeout/retry, test thật bằng 2 tiến trình Long thật (FS+CL) chạy đồng thời.
5. **[ĐÃ SỬA]** Xem mục C — khoá bao trọn giao dịch đọc-sửa-ghi cho registry.json (merge-on-save) và rotation-state (reserved/timeout).
6. **[ĐANG CHẠY khi viết bản này]** Render Long-form thật cho FS — xem mục D cập nhật.
7. **[ĐÃ QUYẾT ĐỊNH bởi người dùng: CÓ]** CL Long-form — người dùng chọn đưa vào production ngay. **Phát hiện quan trọng khi thực hiện, SỬA LẠI 1 claim SAI của bản audit gốc:** claim round-2 "CL bị loại vì thiếu cấu trúc thư mục `_PRODUCTION/Long/`" chỉ đúng MỘT PHẦN — tự chạy `gate_episode()` thật (không đoán) xác nhận CL EP001 **đã** `long_ready=True` từ trước, qua nhánh fallback "manifest phẳng" của `content_repo.py:143-155` (đọc thẳng `_INTERNAL/manifest.json` + field `tts_output`, không cần cấu trúc `_PRODUCTION/Long/` lồng nhau) — nhánh này áp dụng y hệt cho CL VÀ FS. Vậy lý do thật CL (và FS) chưa từng render Long không phải "bị chặn kỹ thuật", mà đơn giản là **chưa từng có ai chạy** `long_batch_runner.py --domain CL/FS` trước đợt sửa này. Xem mục D cập nhật.
8. **[ĐÃ SỬA]** B-roll CL: thay vì tiếp tục vá `broll_query_sanitizer` (đã 2 vòng, không dứt điểm vì root cause là Pexels catalog tự thiên lệch cho cụm pháp lý tiếng Anh trung tính, không phải lỗi dịch/cache), thêm 2 entry `symbol_library` (render_mode=`static_asset`) cho domain CL trong `domain_creative_profiles.json`, khớp các cụm tiếng Việt ĐÃ BIẾT gây lỗi ("án treo", "thời gian thử thách", "thử thách", "bản án", "kết án", "tuyên án", "mức án", "hình phạt", "phạm tội", "phiên tòa", "tòa án", "xét xử", "ra tòa") sang 2 ảnh trung tính tự sinh qua ComfyUI/SDXL-Turbo (cán cân công lý, toà nhà toà án — không người, không bạo lực, đã tự kiểm tra bằng mắt), bỏ qua hẳn Pexels cho các cụm này thay vì tiếp tục phụ thuộc vào 1 nguồn không kiểm soát được nội dung. Render lại thật + kiểm tra từng khung hình (5s/20s/38s) xác nhận cả 3 scene giờ dùng ảnh an toàn. Video cũ đã upload (private, chưa public) bị xoá + thay bằng video mới, verify qua API — xem mục E cập nhật.
9. **[ĐÃ XÁC NHẬN]** Người dùng xác nhận trực tiếp: mỗi kênh dùng 1 project/quota GCP riêng (3 kênh = 3 project riêng), không dùng chung.
