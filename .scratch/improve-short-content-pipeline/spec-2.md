# Spec 2: Instrumentation cho Script Quality Model (phần không phụ thuộc anchor)

**Status:** ready-for-agent (duyệt 2026-09-28, D88–D91)
**Nguồn:** grill Script Quality 2026-09-28, xem `decisions.md` (D57–D91), `research.md` (mục "Seam cho Script Quality"), `CONTEXT.md`.
**Phụ thuộc Spec 1:** dùng chung Content Quality Gate (S1) và kho Quality record.

## Problem Statement

Người vận hành muốn biết cách viết để đọc của một Short có truyền đạt nội dung rõ, tự nhiên và giữ người xem hay không. Muốn vậy, Script quality phải được tách khỏi Content quality và đo được theo dữ liệu thật. Hiện tại không làm được, vì:

- Content và Script được sinh chung trong một lần gọi writer. Ngoài CL provenance, không có Content invariant tách riêng (Content hook, Claim ledger, thứ tự ý, Payoff). Fact của FS mất sau khi sinh. Đoạn trích gốc của BUD không được lưu sau review. Vì vậy không thể sửa riêng câu chữ mà vẫn biết Content có bị đổi hay không.
- Không có kiểm tra bằng code nào cho lặp câu, markup hay ký hiệu sót vào lời đọc, hay câu cụt. Một script E2E đã lặp một câu ba lần. Các luật lặp câu và listening-load chỉ nằm trong prompt.
- Tín hiệu Script hook duy nhất là luật "câu đầu >20 từ thì điểm bị ép xuống 7". Luật này đo độ dài câu đầu, không đo khoảng cách tới điểm móc.
- Không có lịch sử opening nào theo Domain, nên không đo được việc lặp công thức mở đầu (3/5 hook của CL dùng cùng một công thức câu hỏi).
- Không có dữ liệu nào gắn nhận định về Script với bằng chứng, nên sau này không calibration được.

## Solution

Xây phần **hạ tầng tạo dữ liệu** cho Script Quality Model. Spec này không viết anchor, không đặt ngưỡng, và không chấm điểm:

1. **Content invariant (S6):** sidecar đặt cạnh script. Nguồn claim do code ghi. Content hook, thứ tự ý và Payoff do LLM trích, có evidence; riêng CL provenance lấy deterministic từ `StoryPlan`.
2. **Script Quality Gate (S7):** gọi tại cùng điểm hội tụ với S1 và ghi Quality record `layer: script`.
3. **Toàn vẹn văn bản (S8):** kiểm tra deterministic trên text sẽ thật sự được đọc. Đây là gate duy nhất có quyền chặn trong spec này.
4. **Script fidelity shadow (S9):** LLM so script với nguồn claim và ghi finding có evidence. Không chặn.
5. **Tín hiệu chẩn đoán (S10):** khoảng cách tới điểm móc, mật độ số và tên, độ dài. Chỉ ghi, không tính thành điểm.
6. **Script rewrite contract (S11):** từ finding của S8 sinh một bản viết lại, rồi chạy deterministic invariant guard. Không có retry loop.
7. **Opening pattern + concentration signal (S12/S13):** chỉ advisory, ghi vào Quality record.

## User Stories

### Content invariant

1. Là người phân tích, tôi muốn mỗi Short có Content invariant lưu cạnh script, để biết một bản viết lại có giữ nguyên Content hay không.
2. Là người phân tích, tôi muốn nguồn claim (fact FS, fact pack CL, đoạn trích BUD và TRENDING) do code ghi, không do LLM tóm tắt, để tham chiếu fidelity không bị sai lệch.
3. Là người vận hành BUD, tôi muốn đoạn trích gốc được lưu trước khi review viết lại, để sau này kiểm được Script fidelity.
4. Là người phân tích, tôi muốn Content hook, thứ tự ý và Payoff do LLM trích được đánh dấu là `derived` và kèm span evidence, để không nhầm chúng với dữ liệu gốc.
5. Là người vận hành CL, tôi muốn Short đi đường provenance lấy thứ tự ý và vai trò HOOK/BEAT/REVEAL/PAYOFF thẳng từ `StoryPlan`, không qua LLM.
6. Là người vận hành, tôi muốn trường nào của invariant bị thiếu thì có lý do thiếu, và invariant không đủ thì Short không được Script rewrite mà chuyển sang Needs review.

### Script Quality Gate và Toàn vẹn văn bản

7. Là người vận hành, tôi muốn mọi Short, ở mọi Domain và mọi đường vào, đi qua Script Quality Gate ngay sau Content Quality Gate và trước TTS.
8. Là người vận hành, tôi muốn Toàn vẹn văn bản được kiểm trên text sau khi đã bỏ `**` và emotion tag đúng như bước render làm, để kiểm đúng thứ sẽ được đọc lên.
9. Là người vận hành, tôi muốn câu lặp (nguyên văn và sau khi chuẩn hoá) bị chặn, kèm evidence là các câu lặp.
10. Là người vận hành, tôi muốn markup hoặc ký hiệu còn sót (dấu sao lẻ, ngoặc vuông, `#`, `*** N`, nhãn "Phương án", mảnh JSON, URL) bị chặn, kèm evidence.
11. Là người vận hành, tôi muốn câu cuối không có dấu kết câu được ghi là finding câu cụt kèm evidence, nhưng không chặn, vì script có thể cố ý kết bằng `…` hoặc câu hỏi.
12. Là người vận hành, tôi muốn Short FAIL Toàn vẹn văn bản không tới TTS hay upload.
13. Là người phân tích, tôi muốn mỗi quyết định của Script gate được ghi thành Quality record `layer: script`, có reason code thuộc tập đóng, evidence và version.
14. Là người vận hành, tôi muốn ghi record thất bại thì Short đó bị chặn (fail closed) mà không làm dừng cả batch, giống S1.

### Script fidelity shadow

15. Là người phân tích, tôi muốn LLM so script với nguồn claim của invariant và ghi finding (claim mới, claim bị làm mạnh, trích dẫn sai nguyên văn, thuật ngữ giáo lý bị thay lệch nghĩa), mỗi finding kèm evidence.
16. Là người vận hành, tôi muốn finding shadow không bao giờ đổi Gate status hay chặn Publish.
17. Là người phân tích, tôi muốn evaluator là model khác model writer, và kết quả "không chắc" được ghi đúng là không chắc.
18. Là người phân tích, tôi muốn Short không có nguồn claim được ghi `Source không đủ` cho fidelity, không bị bỏ qua lặng lẽ.
19. Là người vận hành, tôi muốn lỗi CR-1 không bị ghi lại lần nữa ở tầng Script.

### Tín hiệu chẩn đoán

20. Là người phân tích, tôi muốn có Khoảng cách tới điểm móc: LLM đánh dấu span chi tiết móc, code đếm số từ đứng trước và quy ra giây theo 170 và 200 từ/phút.
21. Là người phân tích, tôi muốn có mật độ số, tên và thuật ngữ theo từng câu, độ dài từng câu, số câu, tổng số từ và số từ câu đầu.
22. Là người vận hành, tôi muốn mọi tín hiệu chẩn đoán chỉ được ghi lại, không thành điểm và không chặn. Luật ép điểm 7 hiện có của engine giữ nguyên.

### Script rewrite contract

23. Là người vận hành, tôi muốn một finding của Toàn vẹn văn bản được chuyển thành rewrite contract (câu bị chỉ ra, loại lỗi, Content invariant phải giữ), để writer chỉ sửa đúng câu đó.
24. Là người vận hành, tôi muốn bản viết lại đi qua deterministic invariant guard: tập token claim (số, can chi, tên, thuật ngữ có trong nguồn) phải giữ nguyên, và không có token số mới.
25. Là người vận hành, tôi muốn bản viết lại vi phạm guard được ghi là đổi Content và chuyển về Content gate, không được coi là Script rewrite.
26. Là người vận hành, tôi muốn bản viết lại qua guard phải đi lại Script gate và hard gate của Content gate trước khi dùng.
27. Là người phân tích, tôi muốn phép so sánh invariant bằng LLM chạy shadow và được ghi lại.
28. Là người vận hành, tôi muốn spec này chỉ có một lần viết lại cho mỗi finding. Nếu lần đó thất bại, Short vào Needs review. Không có retry loop.

### Opening pattern và Catalog

29. Là người phân tích, tôi muốn mỗi Short qua Script gate có fingerprint N từ đầu đã chuẩn hoá (do code tính) và một mô tả Opening pattern tự do kèm evidence (do LLM viết), ghi vào Quality record.
30. Là người phân tích, tôi muốn concentration signal được tính từ các Quality record PASS gần nhất của cùng Domain và ghi lại dưới dạng advisory.
31. Là người vận hành, tôi muốn Catalog signal không có quyền FAIL, không có ngưỡng, không whitelist hay blacklist, và không được đưa vào prompt của writer.

## Implementation Decisions

### Content invariant (S6)

- Là một sidecar JSON có schema version, đặt cạnh file script staged, theo mẫu sidecar provenance của CL.
- Các trường:
  - `claim_source` (loại nguồn cùng dữ liệu gốc);
  - `source_excerpt` (khi có);
  - `content_hook`, `idea_order`, `payoff` (mỗi trường có `derived_by`: `code`, `story_plan` hoặc `llm`, kèm span evidence);
  - `missing` (tên trường và lý do);
  - các version.
- Nơi ghi:
  - Generator FS và TRENDING ghi `facts` / `extract_facts` đã dùng.
  - Runner ghi đoạn trích BUD trước bước review.
  - CL provenance lấy từ fact pack và `StoryPlan`.
  - CL legacy và case pipeline ghi excerpt hoặc `CoreFact` mà chúng có.
- Phần LLM trích chạy sau khi có script thắng.
- Không đổi cách generator viết script. Không tách thành Content Plan rồi mới tới Script.

### Script Quality Gate (S7)

- Module sâu, giao diện nhỏ: nhận script, Content invariant và identity; trả về Script gate decision; ghi Quality record `layer: script`.
- Được gọi tại cùng điểm hội tụ runner dùng cho S1. Không tạo đường vào thứ hai.
- Gate status có thể có: PASS, FAIL (chỉ do S8), Needs review, Source không đủ.
- Reason code dùng tiền tố mới `SCR_` trong tập đóng của D54 (vd `SCR_REPEATED_SENTENCE`, `SCR_LEFTOVER_MARKUP`, `SCR_TRUNCATED`, `SCR_INVARIANT_INCOMPLETE`). Outcome chưa map được ghi `INTERNAL_UNMAPPED` và Needs review.
- `rubric_version` của record Script là `"script-instrumentation-v0"`, tách khỏi `"legacy"` của Content. Các version khác ghi giá trị thật.

### Script evaluator (một lần gọi)

- Một lần gọi LLM cho mỗi Short trả về các phần tách riêng: trích invariant (Content hook, thứ tự ý, Payoff), finding Script fidelity shadow, span chi tiết móc, mô tả Opening pattern. Mỗi phần có evidence riêng; không có điểm tổng.

### Toàn vẹn văn bản (S8)

- Hàm thuần trên text đã qua đúng các bước strip của bước render. Dùng lại chính hàm strip, không viết bản sao.
- Kiểm: câu lặp nguyên văn và sau khi chuẩn hoá (hạ chữ, bỏ dấu câu); ký hiệu hoặc markup còn sót; câu cuối không có dấu kết câu.
- Đầu ra là danh sách finding `{loại, câu/span, vị trí, chặn}`. Loại chặn: câu lặp, markup/ký hiệu sót. Loại không chặn: câu cuối thiếu dấu kết. Có ít nhất một finding chặn thì FAIL.

### Script fidelity shadow (S9)

- Evaluator LLM khác model writer. Đầu vào là script và `claim_source` / `source_excerpt`.
- Đầu ra là danh sách finding `{loại, span script, span nguồn nếu có, độ chắc}`.
- Được ghi vào Quality record với cờ `shadow: true`. Không bao giờ ảnh hưởng Gate status.
- Không có nguồn claim thì ghi `Source không đủ` cho fidelity.

### Tín hiệu chẩn đoán (S10)

- Phần code là hàm thuần. Phần LLM chỉ đánh dấu span chi tiết móc và không chấm.
- Được ghi vào Quality record dưới khóa `diagnostics`. Không có trường điểm.

### Script rewrite contract (S11)

- **Contract:** `{finding, câu cần sửa, invariant}` được đưa cho writer; kết quả là `candidate_rewritten_script`. Theo mẫu "chỉ sửa câu bị chỉ ra" của review Long BUD.
- **Deterministic invariant guard:** là hàm thuần. Nó so tập token claim của bản trước và bản sau với nguồn claim. Mẫu này đã có ở guard số của CL.
- **Kết quả:** qua guard thì chạy lại S7 và hard gate của S1. Vi phạm guard thì ghi đổi Content và về Content gate. Viết lại thất bại thì Needs review.
- **Không có trong spec này:** retry count, feedback loop, tối ưu rewrite.

### Opening pattern và concentration (S12/S13)

- **Fingerprint:** N từ đầu đã chuẩn hoá. N là tham số cấu hình và chỉ dùng để đo.
- **Mô tả Opening pattern:** LLM viết mô tả tự do kèm span evidence. Chưa có taxonomy.
- **Concentration:** đọc các Quality record PASS của Domain trong window theo số lượng. Tính tỷ trọng theo fingerprint; mô tả tự do được giữ để chuẩn hoá sau khi có baseline. Kích thước window là tham số, không phải ngưỡng.
- **Lưu trữ:** không store mới, không dùng khoá chỉ có trên Unix.

## Testing Decisions

- Theo nguyên tắc của Spec 1: chỉ test hành vi bên ngoài qua seam. Giả lập agy/Codex ở cấp hàm gọi CLI.
- **S6:** fixture cho từng đường (FS facts, BUD excerpt, CL StoryPlan, TRENDING, CL legacy). Kiểm tra `derived_by`, evidence, và lý do thiếu. Kiểm tra invariant không đủ thì không được rewrite.
- **S8:** case thật cho lặp câu ba lần (script E2E round 6 nếu lấy lại được, không thì dùng fixture tương đương), `**` lẻ, emotion tag hợp lệ bị strip và không bị tính là lỗi, câu cụt, và script sạch. Hàm thuần, chạy trên Windows.
- **S7:** mỗi đường vào đi qua gate và có record `layer: script`. FAIL S8 không tới TTS. Ghi record lỗi thì fail closed. Test cần runner và registry thuộc nhóm CI/container.
- **S9:** evaluator giả trả finding. Kiểm tra Gate status không đổi, cờ `shadow`, và `Source không đủ`.
- **S10:** tính đúng khoảng cách tới điểm móc với span giả, mật độ và độ dài. Không có trường điểm.
- **S11:** guard bắt token số mới, tên bị đổi, can chi bị bỏ. Bản viết lại hợp lệ đi lại S7 và S1. Lần viết lại thất bại thì Needs review.
- **S12/S13:** fingerprint ổn định. Concentration đúng trên tập record fixture. Không có đường nào từ signal tới Gate status hay prompt writer.

## Out of Scope

- Anchor 0–4, threshold, rubric Script Quality v1.
- Dùng điểm Script làm publish gate. Chấm S-b, S-c, S-d, S-e, S-f.
- Script fidelity làm hard gate chặn thật.
- Catalog concentration threshold, taxonomy Opening pattern, feedback "tránh pattern" cho writer.
- Retry loop, retry count, feedback loop đầy đủ, tối ưu rewrite.
- Refactor generator thành Content Plan → Script.
- Sửa luật ép điểm 7 của engine.
- Audio Quality, TTS engine, emotion tag, từ điển phát âm, pause marker, Pipeline Reliability, Long.
- Đưa ticket lên GitHub Issues.

## Further Notes

- **Thứ tự:** Spec 2 → tickets → implementation tạo dữ liệu (Spec 1 + Spec 2) → baseline + labels → anchor/threshold cho cả Content và Script. Không viết anchor trước baseline.
- **Phụ thuộc:** S6, S8, S10 và guard của S11 là hàm thuần, làm độc lập. S7, S9, S12 và S13 ghi Quality record nên bị chặn bởi ticket 02 của Spec 1.
- **Lý do chạy shadow:** C4 là một LLM gate chưa đo và đã chặn 4/5 tập, cả 4 được đánh giá là chặn nhầm. Script fidelity chỉ được lên gate thật sau khi đo trên tập đã gán nhãn.
