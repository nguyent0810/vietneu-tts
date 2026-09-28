# VieNeu Short Content

Hệ thống sinh nội dung Short/Long tiếng Việt cho các kênh YouTube, từ ý tưởng đến kịch bản đọc và audio TTS. Glossary này giữ ngôn ngữ chung giữa người làm nội dung và agent.

## Phân loại nội dung

**Domain** (`topic`):
Mảng nội dung gắn với một kênh và một giọng đọc: Phật giáo (BUD), Phong Thủy (FS), Hình Sự (CL).
_Avoid_: channel (khi ý là mảng nội dung), chủ đề

**Category** (`content category`):
Loại nội dung xét theo cách tạo và kiểm chứng: GROUNDED_DATA, EDUCATIONAL, INTERPRETATION, CREATIVE_ASTROLOGY, STORYTELLING, TRENDING. Độc lập với Domain.
_Avoid_: format, dạng

**Short**:
Video ngắn dọc, lời đọc khoảng 20–30 giây.

**Short độc lập** (`standalone Short`):
Short mà toàn bộ giá trị nằm trong chính nó, không gắn với một Long cụ thể.

**Short trích từ Long** (`extracted Short`):
Short được cắt và viết lại từ một đoạn của một Long cụ thể; giá trị vẫn phải nằm trong chính Short.
_Avoid_: clip, teaser

**Long**:
Video dài theo tập; BUD Short được trích từ Long.
_Avoid_: episode (khi ý là định dạng)

**Đoạn short** (`segment`):
Một đơn vị kịch bản trong file nhiều Short, đánh dấu bằng dòng `*** N`.

**Khoảng nghỉ** (`gap`):
Quãng lặng giữa hai chunk audio, phân loại theo ranh giới đoạn, câu hoặc dấu câu phụ.

**Kịch bản đọc** (`narration script`):
Văn bản cuối cùng được đưa vào TTS.
_Avoid_: script (khi không rõ tầng)

**Từ điển phát âm** (`pronunciation dictionary`):
Bảng ánh xạ từ/cụm từ sang cách đọc đúng cho TTS.

## Tầng chất lượng

**Content quality**:
Chất lượng của ý tưởng và mạch ý, trước khi xét câu chữ: Content hook, Payoff fidelity, Value, Accuracy, Structure, Safety, Originality, CTA.

**Script quality**:
Chất lượng của Kịch bản đọc như văn bản viết để nghe, độc lập giọng và engine: nội dung có được truyền đạt rõ, tự nhiên và giữ người xem không. Gồm Script hook, Nghe hiểu ngay, Mạch câu, Câu chốt, Tự nhiên, Tiết kiệm, Độ dài phù hợp; hard gate là Script fidelity và Toàn vẹn văn bản.

**Audio quality**:
Chất lượng những gì chỉ tồn tại khi đã đọc thành tiếng: ngữ điệu, phát âm, khoảng nghỉ thật, tốc độ thật, cảm xúc giọng.

**Phép thử viết lại** (`rewrite test`):
Cách phân tầng một lỗi: sửa được chỉ bằng viết lại câu chữ mà giữ nguyên claim, thứ tự ý và Payoff thì là lỗi Script; phải đổi ý, fact, thứ tự ý hoặc Payoff thì là lỗi Content.

**Content hook**:
Ý tưởng/điều tò mò mà video hứa hẹn ngay từ đầu. Thuộc Content quality.

**Script hook**:
Câu chữ mở đầu hiện thực hoá Content hook. Thuộc Script quality. Đo bằng Khoảng cách tới điểm móc, không bằng độ dài câu đầu.
_Avoid_: hook (khi không rõ tầng)

## Rubric và gate

**Base rubric**:
Bộ tiêu chí Content quality áp dụng cho mọi Short.

**Domain overlay**:
Phần bổ sung/điều chỉnh Base rubric theo Domain.

**Category overlay**:
Phần bổ sung/điều chỉnh Base rubric theo Category. Rubric hiệu lực = Base rubric → Domain overlay → Category overlay.

**Hard gate**:
Tiêu chí mà FAIL thì cả gate FAIL, không điểm nào khác bù được. Content: Accuracy, Safety. Script: Script fidelity, Toàn vẹn văn bản.

**Reason code**:
Mã lý do chuẩn hoá đi kèm mỗi FAIL, ví dụ `ACC_UNSOURCED_CLAIM`, `SAF_CR1_CERTAINTY`.

**Score anchor**:
Mô tả một mức điểm bằng danh sách điều kiện kiểm tra được, kèm ít nhất một case thật.
_Avoid_: label (như "yếu/tốt")

**Quality record**:
Bản ghi bền vững kết quả Content Quality Gate của một Short, gồm gate status, reason code, điểm, evidence và phiên bản rubric; được ghi cho mọi kết quả, không chỉ Short đã đăng.

**Gate status**:
Kết quả của Content Quality Gate cho một Short: PASS, FAIL, Source không đủ hoặc Needs review.

**Claim ledger**:
Danh sách từng claim sự thật trong script cùng nguồn đối chiếu và kết quả PASS/FAIL.

**CR-1**:
Luật Safety cấm khẳng định chắc chắn, gây sợ hoặc bán nỗi sợ về niềm tin, vận mệnh.

**Content Quality Gate**:
Cổng quyết định một Short có đủ Content quality để đi tiếp sang sản xuất audio hay không.

**Source không đủ** (`insufficient source`):
Kết quả khi chất liệu nguồn không đủ để tạo Short đạt Content Quality Gate mà không phải thêm thắt; là kết quả hợp lệ, không phải lỗi.
_Avoid_: fail (khi nguyên nhân là nguồn)

**Calibration**:
Việc đối chiếu điểm rubric đã lưu với số liệu sau khi đăng để điều chỉnh rubric.

**Baseline snapshot**:
Bản ghi trạng thái chất lượng và hiệu quả của các Short đã đăng trước khi thay đổi Quality Model; là mốc so sánh cho Quality Model v1 và các lần calibration sau.

**Evaluator**:
Cơ chế hoặc tác nhân chịu trách nhiệm đánh giá một tiêu chí: Deterministic/Code (luật hoặc dữ liệu xác định), LLM judge (ngữ nghĩa, định tính) hoặc Human sampling (người review một tỷ lệ mẫu để calibration evaluator khác).
_Avoid_: judge (khi ý là mọi loại người/máy chấm)

**Needs review** (`needs_review`):
Trạng thái yêu cầu con người xem xét trước khi Publish. Không đồng nghĩa với PASS và không tự chuyển thành Publish.

**False reject**:
Trường hợp Content Quality Gate đánh FAIL một Short thực tế đủ điều kiện PASS.

**False accept**:
Trường hợp Content Quality Gate đánh PASS một Short thực tế phải FAIL. False accept ở Accuracy hoặc Safety là lỗi nghiêm trọng.

## Content Quality Model

**Value promise**:
Cam kết giá trị mà một Short của một Domain phải mang lại cho người xem; là cơ sở để đánh giá Value.
- BUD: một góc nhìn áp dụng được vào đời sống hôm nay, giữ nguyên ý giáo lý.
- FS: một hướng dẫn cụ thể liên quan đến ngày, tuổi hoặc tháng, diễn đạt có hedge để người xem tự quyết.
- CL: giải trí có thông tin, giúp người xem hiểu một vụ án, tình tiết hoặc nguyên tắc pháp lý cụ thể.

**Curiosity trung thực** (`honest curiosity`):
Sự tò mò tạo ra từ một chi tiết thật, cụ thể và trả lời được bằng nội dung phía sau; không dựa trên khẳng định chắc chắn, nỗi sợ hay lời hứa gây hiểu lầm. Chỉ có giá trị khi Content hook được trả bằng Payoff tương ứng.
_Avoid_: clickbait

**Payoff fidelity**:
Mức độ Short trả đúng và đủ điều Content hook đã hứa. Thay cho "Curiosity" như một tiêu chí chấm riêng.
_Avoid_: curiosity score

**Takeaway**:
Điều người xem mang về từ một Short, phát biểu được bằng một câu.

**Fact thừa** (`unused fact`):
Thông tin đúng nhưng không phục vụ Takeaway, làm loãng Short.

**Hook formula**:
Khuôn chiến lược mở đầu dùng để sinh Content hook (hiện là A/B/C/D).
_Avoid_: hook strategy (khi ý là nhãn để so trùng)

**Payoff**:
Phần nội dung trả lời hoặc thực hiện lời hứa của Content hook, tương ứng với đúng loại lời hứa hoặc câu hỏi mà hook tạo ra. Một kết luận chung chung không được tính là Payoff.

**Catalog-level quality**:
Chất lượng xét trên danh mục Short cùng Domain trong một recent window, thay vì từng Short độc lập; dùng để phát hiện lặp Content hook, hook formula, takeaway, opening pattern và CTA.

**Backup pool**:
Kho Short đã vượt Content Quality Gate nhưng chưa đăng, dùng thay thế khi Short dự kiến đăng bị gate FAIL.

## Script Quality Model

**Khoảng cách tới điểm móc** (`time-to-hook`):
Số từ (quy ra giây theo tốc độ đọc) đứng trước chi tiết cụ thể tạo ra sự tò mò của Content hook.
_Avoid_: độ dài câu đầu (chỉ là số liệu chẩn đoán)

**Nghe hiểu ngay** (`listenability`):
Mức người nghe hiểu câu ở lần nghe đầu, không tua lại: mật độ số/tên/thuật ngữ, câu dài hoặc lồng, đại từ mơ hồ khi chỉ nghe.

**Mạch câu** (`sentence flow`):
Mỗi câu đẩy ý tiếp hoặc tạo lý do để nghe câu sau; chuyển ý có nối.

**Câu chốt** (`landing`):
Câu cuối chốt Payoff gọn, không lơi. Payoff có hay không là Payoff fidelity (Content); câu chốt lơi là Script.

**Tự nhiên** (`naturalness`):
Văn nói chứ không phải văn viết, không có cụm quen của AI, đúng register của Domain.

**Tiết kiệm** (`economy`):
Không lặp câu/ý, không câu độn, không lặp cùng một cách hedge.

**Script fidelity**:
Hard gate tầng Script: lời văn không tạo claim mới và không làm mạnh claim quá Claim ledger (Short trích từ Long: quá đoạn trích nguồn). Lỗi CR-1 không tính ở đây mà ở Safety.

**Toàn vẹn văn bản** (`text integrity`):
Hard gate tầng Script: không lặp câu, không câu cụt, không markup/ký hiệu sót vào lời đọc.

**Retention theo câu** (`per-sentence retention`):
Retention curve căn theo mốc thời gian từng câu sau khi đăng. Chỉ là bằng chứng calibration, không phải tiêu chí chấm trước khi đăng.

**Content invariant**:
Phần Content phải giữ nguyên khi chỉ viết lại Script: Content hook (chi tiết móc), Claim ledger, thứ tự ý, Payoff, và đoạn trích nguồn nếu Short trích từ Long. Đổi bất kỳ phần nào là đổi Content.

**Script rewrite**:
Viết lại chỉ câu chữ khi lỗi thuộc Script, giữ Content invariant; bản mới phải qua Script Quality Gate rồi chạy lại hard gate của Content Quality Gate.
_Avoid_: regenerate (dùng cho sinh lại cả Short khi lỗi Content)

**Tín hiệu chẩn đoán** (`diagnostic signal`):
Số đo do code tính (số từ câu đầu, mật độ số/tên, độ dài câu...) để hỗ trợ evaluator; không tự thành điểm.

**Chưa phân tầng** (`unattributed`):
Nhãn cho lỗi người chấm nghe thấy nhưng Phép thử viết lại không xác định được thuộc Script hay Audio.

**Opening pattern**:
Kiểu mở đầu trừu tượng theo cảm nhận người xem (vd câu hỏi tu từ "bạn có biết"), dùng cho Catalog-level; khác Hook formula là nhãn chiến lược nội bộ.

**Surface pattern**:
Mẫu câu chữ bề mặt lặp được giữa các Short (câu mở, câu chốt, cách hedge, câu CTA, signature phrase). Catalog-level đo độ tập trung của nó; cần đa dạng.

**Domain voice**:
Register, xưng hô, độ trang trọng, nhịp điển hình của Domain; cần đồng nhất, Catalog-level không đo.

**Tự đứng được** (`standalone`):
Short trích từ Long nghe hiểu được mà không cần tập Long: không còn tham chiếu kiểu "như đã nói", "câu chuyện trên" hay đại từ chỉ ngữ cảnh Long.

**Script provenance** (`script_provenance`):
Nguồn của text script dùng trong baseline, theo thứ bậc `exact` (registry `final_script`) → `revision` (Hub audioScript khớp revision lúc đăng) → `rendered` (`.srt`/manifest: lời đã đọc sau normalize) → `source_only` (đoạn trích nguồn, không phải script đã đăng) → `missing`; kèm `verified`/`unverified`. Phục vụ độ tin cậy dữ liệu, không phải tiêu chí chất lượng.
_Avoid_: coi `source_only` là final_script

**n theo tiêu chí**:
Số Short thực sự chấm được cho một tiêu chí; khác số Short thu thập vào baseline.

**Operational target**:
Mục tiêu vận hành của hệ thống, ví dụ 5 Short/ngày; không phải objective của Content Quality Model.
