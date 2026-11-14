# Story-driven Long-form: portfolio assessment (2026-11-14)

Phạm vi: đọc repo và dữ liệu đã lưu; không gọi API, không sửa lịch hay đưa ý tưởng vào production. FACT / HYPOTHESIS / RECOMMENDATION đánh dấu từng nhận định. Mọi điểm là đánh giá tương đối theo rubric, không dự báo viral.

## 1. Portfolio assessment

| Kênh | FACT: baseline và định vị | HYPOTHESIS về storytelling | RECOMMENDATION / fit |
|---|---|---|---|
| BUD | Nghiên cứu #327: Long 28 ngày 2.824 views, AVD 7:06, CTR 3,35%; trung vị AVP Long 22,7%. Truyện Tiền Thân tt04 AVP 31,8%; Ngoài Đời Thật Tây Du Ký 30,1%. | Cảnh nhân vật cụ thể sớm có thể cải thiện mở đầu, nhưng kết quả khác độ dài/chủ đề; chưa có retention đủ của các Long mới để quy kết. | Dùng có chọn lọc cho truyện có nguồn và khuôn nhân vật. Không đổi toàn bộ kênh sang survival. Pipeline TTS, ảnh minh họa, motion hiện có tái dùng được; nghiên cứu nguồn và kiểm tôn giáo làm chi phí tăng. Giữ định dạng, thử tối đa hai pilot sau duyệt. |
| FS | #327: Long 28 ngày 10.234 views, AVD 5:01, CTR 6,9%; Shorts 3,79 triệu views. Có 12 plan `L_fs_t11_*` và plan `L_fs_2027_12tuoi`; tiêu đề/độ dài/lịch phát không đủ trường trong plan đã đọc. | Câu chuyện theo một hồ sơ tuổi/tháng có thể gắn tiến trình với nhu cầu tra cứu, nhưng 12 tuổi/tuổi cụ thể và lời dự báo có nguy cơ lặp hoặc bị hiểu là khẳng định. | Chỉ dùng khung “một lựa chọn, các mốc theo tháng” bên trong cấu trúc tra cứu; bảng và câu trả lời xuất hiện sớm. Số lịch phải sinh `fs_calendar`; gắn “theo tử vi truyền thống, mang tính tham khảo”, không hứa tiền. Tái dùng bảng/motion, chi phí kiểm số và kiểm lời tăng. |
| MIM | FACT: định vị AI/công nghệ và chiến lược documentary 45 ngày: 10–15 phút mặc định, motion/slide/giọng tổng hợp; Long trước đây CTR 0,8–4,2%, 8–145 views ở các mẫu trong báo cáo 26/10. | Nhân vật thật + bước ngoặt công nghệ phù hợp định vị hơn survival giả lập; hình 2D có thể giải thích cơ chế nhưng không thay bằng chứng. | Đề xuất chủ kênh cân nhắc storytelling nhân vật trong documentary (Shannon/Lee Sedol đã có Short, không lặp lại như thử nghiệm mới). Không thiết kế thử nghiệm. Duy trì motion pipeline; chi phí fact-check tăng vừa. |
| CK | FACT: định vị dữ liệu giải câu hỏi tiền bạc; Long mẫu 28 ngày có CTR 0,7–2,5%, 10–82 views theo báo cáo 26/10. Chiến lược ghi nguồn, giai đoạn, phương pháp, giả định. | Hành trình quyết định tiền có fit nếu mỗi bước gắn dữ liệu thật; “sinh tồn” hoặc kết cục tài chính kịch tính có thể gợi hứa lợi nhuận. | Chỉ mượn tiến trình lựa chọn-hệ quả cho backtest có giả định công khai; không dựng nhân vật giả như bằng chứng. Pipeline biểu đồ tái dùng, thêm công xác minh. Không thiết kế thử nghiệm. |
| CL | FACT: định vị true crime. 26/10: 104,9k views/28 ngày, 941 giờ, CTR 3,4%; Khun Sa 5.865 views, CTR 3,8%, AVD 10:13; Bến Thượng Hải 3.068 views, CTR 3,6%. Narcos AVD 19:15/66% nhưng 610 impressions. | Storytelling có fit cao khi diễn tiến dựa trên hồ sơ; mô hình survival hư cấu dễ làm sai lệch vụ án. | Giữ documentary theo chứng cứ và timeline; không dựng xung đột/cảnh giả. Dùng đồ họa timeline/địa điểm, ghi rõ khoảng trống chứng cứ. Tư liệu hóa làm chi phí cao; CL chủ kênh tự quyết. |

### Bằng chứng đã có và các thử nghiệm cũ phải phân biệt

- FACT — BUD: Truyện Tiền Thân short hoạt hình 0/7 đạt nền (sổ thất bại); video dài tt04 có AVP 31,8%, nhưng không chứng minh được causal uplift. Khuôn Ngoài Đời Thật có kết quả hỗn hợp: Tây Du Ký 586 views / 30,1% AVP; Trần Nhân Tông 304 / 28,1%; một số video khác có retention tốt nhưng impressions thấp. Không đề xuất lại y nguyên.
- FACT — FS: tử vi theo năm sinh và bảng 2027 thắng ở Short; Long “tử vi trọn đời” đã thuộc nhóm format rộng được thử trước và yếu. Tháng 11 âm có 12 plan Long đã hiện diện, hẹn 28/11–09/12 theo brief, nên không gọi “kể chuyện tuổi theo tháng” là format chưa thử.
- FACT — FS: kế hoạch 28 ngày cho thấy format Long có nhu cầu nhưng sample nhỏ và CTR/retention theo từng Long không đầy đủ. “Short → Long” BUD chưa đo; FS tổng 325 lượt theo #327.
- FACT — MIM/CK: đã có chiến lược documentary 45 ngày và quyết định giữ lịch; thí nghiệm cũ dạng người/năm/bước ngoặt, con số tiền × thời gian đã được triển khai. Đề xuất ở handoff chỉ là hướng cân nhắc, không mở lịch.
- FACT — CL: “Ngoài Đời Thật” và documentary lịch sử/true crime đã chạy; không coi format đó là ý tưởng mới.

## 2. Ý tưởng và chấm điểm (0–5)

Trọng số: audience fit 25%, storytelling 20%, evidence 20%, feasibility 15%, originality 10%, experiment value 10%. Điểm tổng = tổng điểm thành phần × trọng số; làm tròn 2 chữ số.

| Hạng | Kênh / ý tưởng (định hướng, chưa phải kế hoạch sản xuất) | Audience | Story | Evidence | Feasible | Original | Exp. | Tổng | Quyết định |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | BUD — một truyện tiền thân có nguồn, mở ngay tại lựa chọn cuối; kể “điều nguồn nói / phần minh họa” riêng | 5 | 5 | 4 | 3 | 3 | 5 | 4.30 | Top pilot đề xuất |
| 2 | FS — một hồ sơ tuổi trong tháng 11 âm, tiến trình theo mốc; câu trả tra cứu xuất hiện sớm | 5 | 4 | 4 | 4 | 2 | 4 | 4.05 | Top pilot đề xuất; đã có lịch t11 cần đối chiếu, không trùng 12 bài |
| 3 | CL — timeline một vụ án có hồ sơ xác minh, dựng quyết định điều tra thành các bước | 5 | 5 | 4 | 2 | 2 | 3 | 3.90 | Handoff chủ kênh; rủi ro nguồn/nhạy cảm cao |
| 4 | BUD — chân dung một nhân vật trong kinh/chú giải, chọn một quyết định có hậu quả; tránh lặp khung Ngoài Đời Thật | 4 | 5 | 3 | 3 | 4 | 4 | 3.85 | Top pilot đề xuất sau kiểm nguồn |
| 5 | MIM — một người và một quyết định làm thay đổi sản phẩm công nghệ; documentary 10–15 phút | 4 | 4 | 3 | 4 | 3 | 3 | 3.60 | Handoff chủ kênh; không thử nghiệm |
| 6 | CK — mô phỏng một quyết định tài chính qua các giai đoạn với bộ dữ liệu công khai, gắn giả định | 4 | 4 | 3 | 3 | 3 | 3 | 3.45 | Handoff chủ kênh; không thử nghiệm |
| 7 | FS — “một ngày cần chọn” trong năm sinh: giải thích cách tra bảng, diễn biến là ví dụ minh họa | 4 | 3 | 3 | 4 | 3 | 3 | 3.40 | Không chọn: gần format lịch/ngày tốt đã chạy |

FACT — Điểm là nhận định cấu trúc, không phải số đo hiệu suất. Không chọn “survival 100 ngày” cho các kênh vì không có evidence riêng và có thể làm lệch niche. Các ý tưởng 4–7 bị loại khỏi top pilot do lặp format cũ, thẩm quyền kênh hoặc rủi ro nguồn cao hơn.

Hạng xếp theo tổng điểm giảm dần. Nếu bằng điểm, ưu tiên lần lượt Audience, Evidence, Feasible, Originality cao hơn; nếu vẫn bằng, xếp theo tên kênh rồi tên ý tưởng. Mỗi ý tưởng nhận hạng liên tục; không dùng hạng đồng hạng làm nhảy số.

### Chi tiết ý tưởng

#### BUD-01 — Truyện tiền thân: lựa chọn cuối
- **Tiêu đề đề xuất:** “Một lựa chọn cuối cùng trong truyện Tiền Thân: điều bản kinh kể” (chốt theo nguồn đã duyệt).
- **Hook 30 giây:** Nêu nhân vật và lựa chọn có thật trong nguồn; đặt câu hỏi về hậu quả, không thêm cảnh ngoài văn bản.
- **Nhân vật/góc nhìn:** Nhân vật trong truyện; người dẫn phân biệt kinh điển, chú giải/truyền thuyết và minh họa.
- **Xung đột:** Lựa chọn của nhân vật và hệ quả được nguồn ghi lại.
- **Tiến trình:** Bối cảnh có nguồn → biến cố → lựa chọn → hệ quả → đối chiếu lớp nguồn.
- **Cao trào:** Hệ quả trực tiếp của lựa chọn theo nguyên văn nguồn.
- **Lý do xem tiếp:** Người xem chờ câu trả lời cho lựa chọn và biết đâu là kinh, đâu là diễn giải.
- **Thời lượng / độ khó:** 12–15 phút / cao (nghiên cứu và kiểm lớp nguồn).
- **Tái dùng asset:** Cao; khung nhân vật, nền và motion có thể dùng lại, thay asset theo từng tích truyện.
- **Dữ liệu hỗ trợ:** TT04 AVP 31,8%; Tây Du Ký 30,1%; BUD median AVP 22,7% (#327). Tín hiệu mô tả, chưa chứng minh quan hệ nhân quả.
- **Rủi ro lệch niche/lặp:** Nhầm kinh với chú giải/truyền thuyết hoặc lặp khuôn Ngoài Đời Thật; kiểm từng chi tiết bằng nguồn.

#### FS-01 — Một hồ sơ tuổi/tháng, câu trả sớm
- **Tiêu đề đề xuất:** “Tháng 11 âm: một hồ sơ tuổi và các mốc cần lưu ý” (chọn tuổi/chủ đề sau khi đối chiếu lịch).
- **Hook 30 giây:** Nêu câu hỏi tra cứu cụ thể, trả lời/bảng chính trước, rồi mở câu hỏi về diễn tiến theo mốc.
- **Nhân vật/góc nhìn:** Một hồ sơ tuổi làm ví dụ; lời dẫn theo tử vi truyền thống, mang tính tham khảo.
- **Xung đột:** Nhu cầu có câu trả lời nhanh gặp diễn tiến nhiều mốc cần giải thích.
- **Tiến trình:** Câu trả lời/bảng → giải thích mốc → diễn giải → nhắc giới hạn tham khảo.
- **Cao trào:** Tổng hợp mốc cuối và trả lời câu hỏi mở đầu.
- **Lý do xem tiếp:** Khán giả chờ cách các mốc ghép thành một câu trả lời rõ ràng.
- **Thời lượng / độ khó:** 8–12 phút / trung bình; kiểm trùng lịch và sinh số bằng `fs_calendar`.
- **Tái dùng asset:** Cao; bảng/motion và khung theo tháng có thể dùng lại sau cập nhật.
- **Dữ liệu hỗ trợ:** FS Long #327: 10.234 views/28 ngày, AVD 5:01, CTR 6,9%; retention riêng format UNKNOWN (lấy: Studio → Analytics → video ID → Giữ chân người xem, export CSV).
- **Rủi ro lệch niche/lặp:** Gần 12 plan `L_fs_t11_*` đã hẹn; chỉ đề xuất sau xác nhận không trùng, không trình bày suy đoán như sự thật.

#### BUD-02 — Một nhân vật, ba lớp nguồn
- **Tiêu đề đề xuất:** “Culapanthaka: một lựa chọn qua kinh điển, chú giải và truyền thuyết” (chỉ dùng lớp có nguồn đối chiếu).
- **Hook 30 giây:** Nêu lựa chọn trung tâm và báo trước ba lớp tư liệu sẽ được tách rõ.
- **Nhân vật/góc nhìn:** Một nhân vật trong nguồn; người dẫn chỉ ra nguồn của từng chi tiết.
- **Xung đột:** Một lựa chọn có hậu quả, trong khi các lớp tư liệu kể/giải thích khác nhau.
- **Tiến trình:** Giới thiệu nguồn → lựa chọn → hệ quả theo từng lớp → đối chiếu điều chắc chắn và chưa chắc.
- **Cao trào:** Khoảnh khắc cho thấy khác biệt giữa văn bản kinh và phần diễn giải đời sau.
- **Lý do xem tiếp:** Người xem muốn biết chi tiết thuộc nguồn nào và kết luận nào có thể rút ra.
- **Thời lượng / độ khó:** 12–15 phút / cao (kiểm nguồn và biên tập phân lớp).
- **Tái dùng asset:** Cao; nhân vật, sơ đồ nguồn và motion có thể dùng cho nội dung kế tiếp.
- **Dữ liệu hỗ trợ:** Plan `L_bud_culapanthaka` đã có, outcome UNKNOWN (lấy: Studio → Analytics → video ID → Giữ chân người xem và Phạm vi tiếp cận, export CSV); format Ngoài Đời Thật có AVP 28,1–30,1% (#327).
- **Rủi ro lệch niche/lặp:** Nguy cơ gán lời/việc ngoài kinh hoặc lặp chân dung nhân vật; PO đã gộp vào BUD-01, không chạy riêng.

#### Các ý tưởng còn lại — hook và thời lượng
- **FS — “một ngày cần chọn”:** Hook: mở bằng câu hỏi tra ngày, chỉ cách đọc bảng rồi đưa diễn biến minh họa. Thời lượng: 8–10 phút.
- **MIM — Lee Sedol và quyết định trước bước ngoặt AI cờ vây:** Hook: mở bằng lựa chọn trước ván đấu và câu hỏi nó nói gì về tương tác người-máy. Thời lượng: 10–15 phút.
- **CK — Backtest 100 triệu từ đỉnh 2018:** Hook: nêu vốn giả định và phương pháp công khai, hỏi kết quả thay đổi ra sao theo từng mốc. Thời lượng: 10–15 phút.
- **CL — Timeline một vụ án có hồ sơ:** Hook: nêu mốc đã xác minh và câu hỏi điều tra nào dẫn tới bước kế tiếp. Thời lượng: 12–18 phút.

## 3. Top 3 experiments — đề xuất chờ duyệt, chỉ BUD/FS

Các mốc 48h / 7d / 28d tính từ lúc phát hành nếu được chủ kênh duyệt. CONTINUE / ITERATE / STOP dùng so sánh với video cùng kênh, cùng format/độ dài và cohort thời gian; ngưỡng chưa thể điền trị tuyệt đối vì baseline Long đủ sạch chưa có. Trước mỗi pilot, Lead lấy Studio CSV/Analytics gồm impressions, CTR theo nguồn, retention 30s/60s, AVD, watch hours, chi phí sản xuất. Không quyết định bằng views tuyệt đối.

### EXP-064-BUD-01 — Cold open từ cảnh lựa chọn có thật
- HYPOTHESIS: mở bằng cảnh/biến cố có nguyên văn trong nguồn và nêu nhân vật ngay 5 giây đầu sẽ cải thiện retention 30s so với video BUD truyện có cùng độ dài, mà không tăng tỷ lệ lỗi nguồn.
- FACT comparator: `L_bud_tt04` (AVP 31,8%, 177 views/28 ngày theo #327); comparator phụ `L_bud_22` Tây Du Ký (586 views, AVP 30,1%; retention tại 54s 56% theo issue, source report #327). Kích thước sample nhỏ/không tương đồng format.
- Baseline thật: #327 BUD Long median AVP 22,7%; CTR kênh 3,35%, AVD 7:06. Retention 30s của comparator mới: UNKNOWN (lấy: Studio → Analytics → video ID → Giữ chân người xem, export CSV).
- Thiết kế: một tập truyện có nguồn đã duyệt; giữ thời lượng/packaging/pipeline gần comparator; không thêm thời tiết, hành động hay lời thoại ngoài nguồn; phân biệt kinh/chú giải/truyền thuyết/hư cấu minh họa.
- Đánh giá: 48h CTR/impressions và retention 30s; 7d retention 60s, AVD, watch hours; 28d hiệu suất cuối và phút sản xuất.
- CONTINUE: retention 30s và AVD không thấp hơn baseline cùng format, CTR không giảm rõ rệt, fact-check sạch, chi phí trong mức Lead duyệt. ITERATE: retention đầu cải thiện nhưng CTR/AVD không hoặc ngược lại; sửa một biến ở lượt sau. STOP: retention đầu thấp hơn comparator và không có cải thiện tới 7d, hoặc lỗi nguồn/khung nhãn.

### EXP-064-FS-01 — Tiến trình một tuổi/tháng, câu trả sớm
- HYPOTHESIS: kể theo một câu hỏi tra cứu cụ thể, trả bảng/câu trả lời trước rồi dùng tiến trình thời gian để giữ mạch sẽ tăng AVD so với Long tra cứu rộng, trong khi CTR không suy giảm.
- FACT comparator: `L_fs_2027_12tuoi` plan tồn tại nhưng outcome chưa có trong nguồn; #327 ghi Long FS 28 ngày 10.234 views / AVD 5:01 / CTR 6,9%. Short 2027 thắng mạnh, nhưng không chứng minh Long.
- Baseline thật: số kênh ở trên; baseline retention riêng Long và impressions theo format: UNKNOWN (lấy: Studio → Analytics → video ID → Giữ chân người xem và Phạm vi tiếp cận, export CSV; hoặc Browsentic chế độ nâng cao). Không đối chiếu trùng 12 plan tháng 11 âm (L_fs_t11_*), đang hẹn 28/11–09/12 theo brief.
- Thiết kế: chỉ chọn một chủ đề không trùng lịch đã hẹn; một câu hỏi tìm kiếm, bảng/câu trả trong 45 giây; các diễn biến là cách diễn giải tử vi truyền thống, tham khảo. Mọi số sinh bằng `fs_calendar`; không hứa tiền hay kết quả chắc chắn.
- Đánh giá 48h/7d/28d như trên; thêm CTR Search/Browse/Suggested, watch hours và chi phí kiểm dữ liệu.
- CONTINUE: CTR không dưới nền 6,9% sau đủ impressions theo đánh giá Lead, AVD/retention tăng so với comparator cùng loại, không có lỗi số/lời hứa. ITERATE: CTR tốt nhưng retention tụt sau bảng hoặc ngược lại. STOP: cả CTR và AVD yếu hơn baseline sau 7d/28d hoặc phát hiện dự báo nói như sự thật.

### EXP-064-BUD-02 — Nhân vật kinh điển, tách ba lớp nguồn
- HYPOTHESIS: một hành trình nhân vật được kể bằng “kinh điển / chú giải hoặc truyền thuyết / minh họa” rõ ràng sẽ cải thiện watch time mà vẫn giữ niềm tin người xem.
- FACT comparator: `L_bud_culapanthaka` plan nhân vật đã có; outcome UNKNOWN. BUD có 2.824 Long views / 28 ngày, AVD 7:06; format Ngoài Đời Thật có AVP 28,1–30,1% ở các ví dụ ghi trong #327.
- Baseline thật: retention theo giây/CTR/chi phí của plan Culapanthaka UNKNOWN (lấy: Studio → Analytics → video ID → Giữ chân người xem và Phạm vi tiếp cận, export CSV; chi phí lấy từ báo cáo sản xuất) trước khi pilot.
- Thiết kế và mốc: một nhân vật, một lựa chọn, không mượn chi tiết ngoài nguồn; 48h, 7d, 28d đo như BUD-01.
- CONTINUE: watch hours và retention không thấp hơn nhân vật comparator, không nhập nhằng lớp nguồn. ITERATE: retention tốt nhưng người xem hiểu nhầm chú giải là kinh thì sửa lời dẫn. STOP: phát sinh gán lời/việc cho Đức Phật ngoài kinh hoặc kết quả tổng thể thấp hơn baseline.

## 4. Evidence & uncertainty

- FACT: nguồn BUD/FS chính là `docs/pm/bud-fs-28d-2026-11-research.md`, #327 migration, plan files, scoreboard `plan_replace_w47.md`; MIM/CK/CL dựa trên ba báo cáo PM trong brief và creator_v2 rules/ledgers.
- UNKNOWN — CTR, impressions, retention theo từng Long cho nhiều video; mức ảnh hưởng CAO với ngưỡng continue/stop. Lấy: Studio → Analytics → video ID → Phạm vi tiếp cận (impressions/CTR) và Giữ chân người xem (retention), export CSV tại 48h/7d/28d; hoặc Browsentic chế độ nâng cao, kèm nguồn traffic.
- UNKNOWN — outcome của plan FS t11 và `L_fs_2027_12tuoi`, lịch/độ dài trong uploaded ledger: mức ảnh hưởng CAO để loại trùng lịch; xác minh plan/upload list trong worktree sản xuất trước khi duyệt.
- UNKNOWN — production cost theo từng kênh: ảnh hưởng VỪA; ghi phút script, tìm nguồn, tạo ảnh, dựng.
- UNKNOWN — Short→Long BUD theo từng video; ảnh hưởng THẤP tới pilot storytelling, CAO nếu chọn KPI chuyển đổi.
- FACT: scoreboard Short 14/11 cho thấy BUD median views 647, stay 27,7%, AVP 84,23%; FS dữ liệu gần kỳ có 61/64 Short thắng và median 12k theo `plan_replace_w47.md`. Đây là bối cảnh Short, không dùng làm baseline Long.

## 5. Risks

- BUD: nhầm kinh với chú giải/truyền thuyết; chi tiết ngoài nguồn; hứa phước. Cổng: fact pack, đối chiếu nguồn, nhãn minh họa rõ; không gán chi tiết cho Đức Phật ngoài kinh, không hứa phước.
- FS: biến diễn giải thành tiên đoán chắc chắn, gõ tay lịch/số; lặp 12 Long tháng 11 âm. Cổng: `fs_calendar`, rà kế hoạch hiện hữu, khung “theo truyền thống / tham khảo”, không hứa tiền.
- MIM: người kể chuyện lấn át chứng cứ; cần nguồn về người/sự kiện và liên hệ công nghệ hiện tại.
- CK: mô phỏng bị xem như dự đoán lợi nhuận; nêu giả định, nguồn, giai đoạn và giới hạn.
- CL: sai sự kiện, nhầm nghi can/thủ phạm, tái dựng thiếu căn cứ; chỉ kể điều có hồ sơ xác minh.
- Toàn portfolio: sample nhỏ, phân phối/impressions khác nhau, độ dài không đồng nhất; không tuyên bố quan hệ nhân quả từ một video.

## Quyết định PO 14/11
- **EXP-064-BUD-01: DUYỆT làm pilot số 1**, gộp phần phân lớp nguồn của BUD-02 (một Long kể chuyện 12–15 phút). Plan.md phải được PO duyệt trước khi viết lời (ticket 066).
- EXP-064-BUD-02: gộp vào BUD-01, không chạy riêng.
- **EXP-064-FS-01: HOÃN.** 12 Long ngắn `L_fs_t11_*` (28/11–09/12) đã dùng phần hợp nhất của công thức (nhân vật mở đầu, lựa chọn → hậu quả); chờ số d7 (khoảng giữa tháng 12) để không lẫn biến.
- MIM, CK, CL: bàn giao chủ kênh (`docs/pm/handoff/2026-11-story-longform-mim-ck-cl.md`).

## 6. Approval requests

1. Chủ BUD duyệt hoặc từ chối tối đa hai ý tưởng BUD-01/BUD-02, kịch bản và chi phí trước production.
2. Chủ FS duyệt ý tưởng FS-01 sau khi Lead xác nhận không trùng nội dung/lịch `L_fs_t11_*` và số liệu từ `fs_calendar`.
3. Lead xác nhận comparator, xuất baseline Studio CSV, và ngưỡng tương đối trước khi thử; các ngưỡng tuyệt đối còn UNKNOWN.
4. Chủ MIM, CK, CL tự quyết các đề xuất handoff; Lead BUD/FS không thử nghiệm các kênh đó.
5. Không thay đổi lịch, tiêu đề, thumbnail/video đã hẹn trong tài liệu này.
