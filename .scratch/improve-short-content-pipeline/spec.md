# Spec: Instrumentation cho Content Quality Model (phần không phụ thuộc anchor)

**Status:** ready-for-agent
**Nguồn:** phiên grill 2026-09-28, xem `decisions.md` (D1–D51), `research.md`, `CONTEXT.md`.

## Problem Statement

Người vận hành các kênh Short (Phật giáo, Phong Thủy, Hình Sự) muốn biết một Short có đạt Content quality hay không, và muốn gate chất lượng dần được hiệu chỉnh theo dữ liệu thật. Hiện tại điều đó không làm được, vì hệ thống **vứt mất bằng chứng**:

- Khi generator hoặc judge đánh FAIL, không có gì được ghi lại. Generator thoát mà không ghi file, còn reject của CL chỉ in ra màn hình. Vì vậy không ai đo được gate đang chặn nhầm bao nhiêu (False Reject).
- Mỗi domain đi một đường khác nhau tới Publish, và runner tự diễn giải outcome theo từng domain. Không có một chỗ nào nói được: "Short này đã qua gate với Gate status gì, vì lý do gì".
- Registry chỉ giữ `hook_score` và script thắng. Ứng viên thua, fact-check, feedback của judge, chiến lược hook và phiên bản prompt đều bị vứt.
- Biến `SKIP_JUDGE_PANEL` mở một đường đi thẳng từ generator đến upload, ở mọi domain dùng chung engine, kể cả CL. Hành vi này trái với comment trong code và không có test.
- Judge có thể trả về một script do chính nó viết. Hàng rào duy nhất là word overlap ≥ 0.4, một chỉ số mơ hồ, không có test.
- Không có Baseline snapshot của các Short đã đăng. Retention curve và traffic source chưa từng được lấy về. Vì vậy mọi thay đổi rubric sau này sẽ không có mốc để so sánh.
- Con số "C4 chặn ~80%" dựa trên 5 tập, và chưa có công cụ nào đo C4 trên tập nhãn cấp câu đã commit.

## Solution

Xây phần **hạ tầng tạo dữ liệu** cho Content Quality Model trước khi viết anchor hay ngưỡng:

1. **Content Quality Gate (S1)**: điểm hội tụ duy nhất mà mọi outcome của mọi Domain phải đi qua trước Publish. S1 chuẩn hoá outcome thành Gate decision (Gate status + reason codes), đồng thời giữ nguyên source outcome gốc.
2. **Quality record**: mỗi quyết định của S1, dù PASS, FAIL, Needs review hay Source không đủ, được ghi vào một kho append-only riêng theo Domain, có identity và version để truy nguyên.
3. **Không còn bypass**: bật `SKIP_JUDGE_PANEL` ở bất kỳ Domain nào luôn cho ra Needs review, không bao giờ tự động Publish.
4. **Judge chỉ chọn, không viết**: judge trả `candidate_id`; code lấy nguyên văn ứng viên đó. Word overlap 0.4 bị bỏ.
5. **Đo C4 cấp câu**: công cụ chạy scorer C4 trên các tập golden/holdout đã commit và báo confusion matrix cấp câu, tách bạch với False Reject cấp Short.
6. **Baseline snapshot**: công cụ ghép dữ liệu registry, ledger, metrics, retention curve và traffic source thành một snapshot local cho các Short đã đăng.
7. **Lấy retention curve + traffic source** từ YouTube Analytics cho từng video, ghi vào baseline local.

Không có anchor, ngưỡng hay rubric mới nào trong spec này. Rubric version hiện hành được ghi nhận là "legacy" để phân biệt với Quality Model v1 sau này.

## User Stories

### Content Quality Gate và Quality record

1. Là người vận hành, tôi muốn mọi Short của mọi Domain đi qua cùng một Content Quality Gate trước Publish, để không Domain nào có đường tắt riêng.
2. Là người vận hành, tôi muốn một Short bị generator FS đánh FAIL vẫn có Quality record, để biết hôm nay có bao nhiêu Short bị chặn và vì sao.
3. Là người vận hành, tôi muốn khi không có ứng viên nào qua fact-check thì Gate status là FAIL với reason code tương ứng, để phân biệt với FAIL vì điểm thấp.
4. Là người vận hành, tôi muốn Short dưới ngưỡng `hook_score` hiện hành được ghi là Needs review kèm reason code, để không bị nhầm là PASS.
5. Là người vận hành, tôi muốn outcome FAIL của CL gate (sidecar, Phase A, C4) cũng tạo Quality record, để CL có dữ liệu False Reject như các Domain khác.
6. Là người vận hành, tôi muốn Short trích từ Long của BUD mà nguồn không đủ chất liệu được ghi là Source không đủ, không phải FAIL, để không trách nhầm generator.
7. Là người phân tích calibration, tôi muốn mỗi Quality record giữ nguyên source outcome gốc (nguồn, trạng thái gốc, lý do gốc) bên cạnh Gate decision đã chuẩn hoá, để biết generator thật sự trả gì và S1 đã chuyển nó thành gì.
8. Là người phân tích calibration, tôi muốn một Short FAIL vì nhiều lý do có đủ mọi reason code, để biết tiêu chí nào đang chặn nhiều nhất.
9. Là người phân tích calibration, tôi muốn mỗi Quality record có `quality_record_id` và `created_at` bất biến, để trích dẫn một quyết định cụ thể mà không bị nhầm.
10. Là người phân tích calibration, tôi muốn mỗi Quality record có rubric version, generator version, prompt version và judge model, để không trộn dữ liệu của các version khác nhau khi tính n ≥ 30.
11. Là người phân tích calibration, tôi muốn record lưu mọi ứng viên A/B/C/D kèm điểm, fact-check và nhãn Hook formula, không chỉ ứng viên thắng, để sau này đo Hook formula nào hiệu quả.
12. Là người gán nhãn, tôi muốn record FAIL lưu đủ script, source excerpt, case_id (nếu có) và timestamp, để tôi có thể chấm mù xem đó có phải False Reject không.
13. Là người vận hành, tôi muốn kho Quality record là append-only, để không lần chạy nào ghi đè bằng chứng của lần trước.
14. Là người vận hành, tôi muốn kho Quality record tách theo Domain, để xem nhanh tình trạng của một kênh.
15. Là người vận hành, tôi muốn registry chỉ giữ reference tới Quality record (nếu cần), để registry không trở thành một source of truth thứ hai.
16. Là người vận hành, tôi muốn runner không tự đặt `status` dựa trên logic riêng của từng topic mà dùng Gate decision của S1, để hành vi các Domain nhất quán.
17. Là người vận hành, tôi muốn Short có Gate status Needs review không bao giờ tự đi tới TTS, upload hay Publish khi chưa có người duyệt.
18. Là người vận hành, tôi muốn việc ghi Quality record không phụ thuộc cơ chế khoá chỉ có trên Unix, để chạy và test được trên Windows.
19. Là người vận hành, tôi muốn nếu việc ghi Quality record thất bại thì Short đó không được Publish (fail closed) nhưng batch vẫn chạy tiếp các Short khác, để không có Short nào được Publish mà thiếu bằng chứng.
19b. Là người phân tích, tôi muốn một outcome mới chưa được ánh xạ ra Needs review với reason code riêng cho outcome chưa map, để nó không bị nuốt vào một reason code sai.

### SKIP_JUDGE_PANEL

20. Là developer, tôi muốn vẫn bật được `SKIP_JUDGE_PANEL` để debug nhanh.
21. Là người vận hành, tôi muốn khi biến này bật, mọi Domain (BUD, FS, TRENDING, CL, storytelling, educational) đều cho Gate status Needs review với reason code `BYPASS_JUDGE`.
22. Là người vận hành, tôi muốn Short đi qua bypass không bao giờ ở trạng thái `scripted` và không bao giờ tự upload.
23. Là người phân tích, tôi muốn Quality record ghi rõ Short đã đi qua bypass, để loại chúng khỏi dữ liệu calibration.

### Judge chỉ chọn

24. Là người vận hành, tôi muốn judge chỉ trả `candidate_id` của ứng viên thắng, để script được Publish luôn là một ứng viên đã được fact-check, không phải văn bản judge tự viết.
25. Là người vận hành, tôi muốn verdict có `candidate_id` không tồn tại, thiếu, hoặc không hợp lệ bị từ chối, để một verdict hỏng không lọt thành PASS.
26. Là developer, tôi muốn word overlap 0.4 bị bỏ hẳn, để không còn hai cơ chế cùng chống một lỗi.
27. Là developer, tôi muốn verdict bị từ chối vẫn được ghi vào lịch sử vòng và Quality record, để biết judge hỏng bao nhiêu lần.

### Đo C4 cấp câu

28. Là người phân tích, tôi muốn chạy scorer C4 trên golden corpus và holdout v1/v2, để có confusion matrix cấp câu (chặn đúng, chặn nhầm, bỏ sót, cho qua đúng).
29. Là người phân tích, tôi muốn báo cáo C4 tách theo category và materiality của fixture, để biết loại câu nào bị chặn nhầm nhiều.
30. Là người phân tích, tôi muốn báo cáo C4 ghi rõ đây là **đo cấp câu**, không phải False Reject cấp Short, để không ai suy diễn sai đơn vị.
31. Là người phân tích, tôi muốn báo cáo lưu phiên bản scorer, judge model, corpus và commit, để so sánh các lần chạy.
32. Là developer, tôi muốn công cụ đo C4 nhận scorer như một tham số, để test được mà không gọi Codex thật.
33. Là người vận hành, tôi muốn chạy thật với Codex là một lệnh thủ công có báo cáo đầu ra, không nằm trong CI, vì nó tốn phí và không deterministic.

### Baseline snapshot

34. Là người phân tích, tôi muốn một Baseline snapshot của mọi Short đã đăng với domain, category, generator, script (nếu có), `hook_score` cũ, views, average view %, retention curve và traffic source.
35. Là người phân tích, tôi muốn snapshot ghi rõ trường nào thiếu và vì sao (script không có trong registry, video không có metrics…), để không nhầm "thiếu dữ liệu" với "giá trị 0".
36. Là người phân tích, tôi muốn snapshot tính được median và phân phối average view % theo Domain, không chỉ trung bình.
37. Là người phân tích, tôi muốn snapshot có cột cho số vi phạm CR-1 và vi phạm Safety đã biết (từ PR-5 và các audit), để làm mốc so sánh cho D20.
38. Là người phân tích, tôi muốn snapshot ghi publish/pass rate trong giai đoạn baseline nếu dữ liệu registry cho phép.
39. Là người vận hành, tôi muốn công cụ baseline đọc từ các file tôi copy từ máy production và export từ Hub, không tự kết nối Hub DB, vì credential do tôi giữ.
40. Là người vận hành, tôi muốn dữ liệu thô và snapshot nằm trong thư mục bị gitignore, để không vô tình commit metadata nội bộ.
41. Là người phân tích, tôi muốn snapshot có version và thời điểm tạo, để các lần calibration sau so với đúng mốc.
42. Là người gán nhãn, tôi muốn từ snapshot xuất được tập gán nhãn theo D37 (FS từ PR-5, BUD gồm hai video retention thấp, CL đã đăng), để bắt đầu gán nhãn.

### Retention curve + traffic source

43. Là người vận hành, tôi muốn lấy retention curve (tỷ lệ người xem theo vị trí trong video) cho từng Short đã đăng, để thấy người xem rời đi ở giây nào.
44. Là người vận hành, tôi muốn lấy phân bố traffic source cho từng Short, để kiểm soát biến nhiễu khi so sánh.
45. Là người vận hành, tôi muốn việc lấy dữ liệu dùng lại xác thực YouTube hiện có và tôn trọng các lỗi tạm thời như luồng sync hiện tại.
46. Là người vận hành, tôi muốn video không có dữ liệu retention (quá ít view) được ghi là thiếu, không làm hỏng cả lần chạy.
47. Là người vận hành, tôi muốn dữ liệu này ghi vào baseline local, không đẩy lên Hub trong phạm vi spec này.

## Implementation Decisions

### Module mới: Content Quality Gate (S1)

- Một module sâu với giao diện nhỏ: nhận một **source outcome** và trả về một **Gate decision**, đồng thời ghi Quality record.
- **Source outcome** là dữ liệu gốc do nơi phát sinh cung cấp: tên nguồn (vd FS generator, judge panel engine, BUD review, CL sidecar gate, CL Phase A, CL orchestrator), raw status, raw reason, script (nếu có), ứng viên và lịch sử vòng, fact set hoặc source excerpt, identity (domain, category, generator, content_id, video_id nếu đã có, case_id nếu CL, Short độc lập hay Short trích từ Long, Long nguồn), và các version.
- **Gate decision** gồm Gate status (PASS, FAIL, Needs review, Source không đủ), danh sách reason codes, evidence, bypass flag.
- Bảng ánh xạ source outcome → Gate decision nằm **một chỗ duy nhất** trong S1. Tối thiểu phủ: pass; không fact-check nào PASS; dưới ngưỡng `hook_score` hiện hành; lỗi generate/judge; verdict judge bị từ chối; bypass judge; CL sidecar fail; CL Phase A/C4 fail; CL escalation; nguồn không đủ.
- Reason code là tập đóng, có tiền tố theo nhóm (vd `ACC_`, `SAF_`, `STR_`, `JUDGE_`, `SRC_`, `BYPASS_`). Không đổi ngưỡng hiện hành, chỉ đặt tên cho kết quả đang có.
- Outcome chưa có trong bảng ánh xạ **không** được map ngầm vào reason code gần giống: S1 trả reason code dành riêng cho outcome chưa map (vd `INTERNAL_UNMAPPED`) và Gate status Needs review.
- Rubric version cho mọi record trong spec này là giá trị "legacy". Quality Model v1 sẽ có version riêng. Các version khác (generator, prompt, judge model) vẫn ghi giá trị thật, không dùng "legacy".
- Mọi nơi quyết định outcome trước Publish đều gọi S1: các generator FS (kể cả khi thoát vì FAIL), TRENDING (bước draft và bước publish), BUD review, và CL gate. Runner đọc Gate decision thay vì tự diễn giải theo topic. Việc nối các call site vào S1 là **prefactor**, làm trước các thay đổi hành vi khác.
- Nếu ghi Quality record thất bại thì Short đó bị chặn khỏi Publish path (fail closed). Batch không bắt buộc dừng: các Short khác vẫn tiếp tục.

### Kho Quality record

- Append-only, một file JSONL cho mỗi Domain, nằm trong vùng output bị gitignore. Không bao giờ sửa hay xoá dòng cũ; mỗi quyết định mới là một dòng mới.
- Identity tối thiểu của mỗi record: `quality_record_id`, `created_at`, `domain`, `content_id` / `video_id`, `rubric_version`, `generator_version`, `prompt_version`, `judge_model`, `gate_status`, `reason_codes`, `source_outcome`, `evidence`, `bypass`. Schema đầy đủ do ticket triển khai định ra; record phải có schema version.
- Không dùng khoá chỉ có trên Unix. Ghi append theo cách an toàn trên cả Windows và Linux.
- Registry có thể giữ `quality_record_id` làm reference. Registry không phải source of truth cho chất lượng.

### SKIP_JUDGE_PANEL

- Engine vẫn đọc biến, nhưng outcome khi bypass là một source outcome riêng (bypass). S1 ánh xạ nó thành Needs review + `BYPASS_JUDGE` cho mọi Domain.
- Không đường nào đưa Short có Gate status Needs review tới trạng thái `scripted` hay upload mà không có human approval.
- Comment sai trong engine (nói CL không đọc biến) phải được sửa cho khớp hành vi mới.

### Judge chỉ chọn

- Contract của judge đổi: verdict chứa `candidate_id` của ứng viên thắng, cùng fact-check, điểm và feedback. Không chứa script.
- Code lấy văn bản thắng bằng `candidate_id` từ danh sách ứng viên. Nếu `candidate_id` thiếu, không tồn tại, hoặc verdict sai cấu trúc thì verdict bị từ chối, vòng đó được ghi là lỗi judge.
- Bỏ word overlap 0.4. Giữ yêu cầu fact-check của ứng viên thắng phải PASS.
- Prompt judge hiện hành cập nhật cho contract mới. Đây là thay đổi contract, không phải thay đổi rubric.

### Đo C4 cấp câu

- Một module nhận danh sách fixture (từ golden, holdout v1, holdout v2) và một scorer, trả về kết quả từng fixture và confusion matrix cấp câu, chia theo corpus, category, materiality.
- Adapter bọc excerpt của fixture thành dạng đầu vào mà scorer C4 production cần.
- Một lệnh thủ công chạy với scorer thật (Codex), ghi báo cáo gồm scorer version, judge model, corpus, commit, thời điểm. Báo cáo ghi rõ đơn vị là câu.

### Baseline snapshot

- Một hàm thuần nhận: các registry theo Domain, publishing ledger, metrics theo video (export từ Hub hoặc từ luồng sync), retention curve, traffic source, danh sách vi phạm đã biết. Trả về các dòng snapshot cộng thống kê theo Domain (n, median, phân vị average view %).
- Một lệnh bao ngoài chỉ lo đọc file đầu vào từ thư mục baseline raw (gitignore) và ghi snapshot có version.
- Mỗi trường thiếu có lý do thiếu.
- Có bước xuất tập gán nhãn theo D37.

### Retention curve + traffic source

- Hai hàm lấy dữ liệu mới đặt cạnh hàm lấy báo cáo ngày trong luồng sync hiện có, dùng chung cách gọi API, xác thực và xử lý lỗi tạm thời.
- Retention curve: tỷ lệ người xem theo vị trí trong video, cho từng video. Traffic source: phân bố theo loại nguồn, cho từng video.
- Kết quả ghi vào baseline raw local. Không đổi payload ingest của Hub.

## Testing Decisions

- **Test tốt** chỉ kiểm tra hành vi bên ngoài qua seam: đưa vào đầu vào thật hoặc fixture, kiểm tra đầu ra hoặc record được ghi. Không kiểm tra hàm nội bộ, không mock subprocess. Giả lập agy/Codex ở cấp hàm gọi CLI như test hiện có.
- **Seam S1 (Content Quality Gate):** test bảng ánh xạ với từng loại source outcome đã liệt kê, gồm cả bypass ở mọi Domain và CL fail. Kiểm tra Gate decision, reason codes, source outcome được giữ nguyên, và record được append (không ghi đè). Kiểm tra fail closed khi không ghi được record. Chạy được trên Windows.
- **Seam S1 qua call site:** test cho mỗi đường vào (FS generator FAIL, engine bypass, BUD review, CL gate fail) rằng kết quả đi qua S1 và có record. Những test cần registry và runner (dùng khoá Unix) là nhóm CI/container test.
- **Seam S2 (kiểm tra verdict):** verdict hợp lệ lấy đúng văn bản ứng viên; verdict thiếu, sai hoặc lạ `candidate_id` bị từ chối; verdict có kèm script tự viết không làm thay đổi văn bản được chọn. Hàm thuần.
- **Seam S3 (đo C4):** với scorer giả, confusion matrix đúng theo từng corpus, category, materiality. Adapter dựng đầu vào đúng từ fixture thật trong repo.
- **Seam S4 (retention/traffic):** giả lập hàm gọi API YouTube giống test sync hiện có; kiểm tra parse, xử lý video thiếu dữ liệu, xử lý lỗi tạm thời.
- **Seam S5 (baseline):** fixture nhỏ cho registry, ledger, metrics, retention; kiểm tra phép ghép, lý do thiếu, thống kê theo Domain, xuất tập nhãn.
- **Prior art:** test generator trending và CL case generation (giả lập hàm gọi CLI); test verification của CL risk gate (giả lập Codex trả claims); test sync YouTube (giả lập hàm gọi API); test registry và runner CL gate (đổi đường dẫn registry, chặn TTS).
- **Môi trường:** S1–S5 không phụ thuộc khoá Unix và chạy được trên Windows. Nhóm test registry/runner chạy trên CI Ubuntu hoặc container. Hiện CI chỉ chạy cho push/PR vào `main`; ticket đầu tiên phải cho CI chạy trên branch này.

## Out of Scope

- Anchor 0–4, ngưỡng tối thiểu và rubric Content Quality Model v1 (chờ Baseline snapshot và tập nhãn).
- Payoff fidelity, Value, Structure, Originality, CTA dưới dạng tiêu chí chấm mới; claim ledger cho Accuracy; lexicon CR-1.
- Catalog-level quality, Backup pool, điều phối Hook formula.
- Sửa hay thay C4. Spec này chỉ đo C4 cấp câu.
- False Reject cấp Short (cần Quality record tích luỹ và người gán nhãn).
- Hub: schema, bảng retention/traffic, endpoint ingest, UI.
- Script Quality, Audio Quality, Pipeline Reliability (chờ các vòng grill sau).
- Long.
- Đưa ticket lên GitHub Issues.

## Further Notes

- Thứ tự tổng: Content decisions → spec này → tickets → implement instrumentation → baseline + labels → anchor/threshold calibration → Content Quality Model v1.
- Dữ liệu baseline cần người vận hành cung cấp: thư mục output của Short từ máy production, và export video + metrics theo ngày từ Hub. Retention curve và traffic source cần người vận hành chạy vì cần OAuth.
- D29 đã được sửa: không tồn tại tập "20 Short bị C4 chặn". Đo cấp câu (spec này) và đo cấp Short (sau này) được báo cáo riêng.
- Hạ tầng hiện tại có thiết kế theo máy Mac (thiết bị `mps`, đường dẫn tuyệt đối trong script shell). Việc này thuộc Pipeline Reliability, không xử lý ở đây, trừ khi chặn test của spec.
