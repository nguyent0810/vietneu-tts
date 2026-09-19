codex
Tôi đã đối chiếu trực tiếp critique vòng 1 với nội dung v2. Có một lỗi đếm trong hồ sơ: critique vòng 1 thực tế chứa **10 finding riêng biệt** (3 High, 5 Medium, 2 Low), dù phần đầu và log ghi “9 issues”. Tôi review đủ cả 10 để không bỏ sót.

1. High — Xem nhẹ anomaly “views before publish”: **SỬA MỘT PHẦN**

Đã sửa tốt:

- Đưa anomaly lên ưu tiên cao nhất.
- Ghi nhận việc xác minh credentials/channel và query cô lập.
- Áp dụng nguyên tắc quarantine.
- Không còn lấy các hàng bất thường để diễn giải hiệu suất.

Riêng giả thuyết “Studio preview” được trình bày đúng mức độ: v2 gọi đây là “most plausible explanation, not proven”, nói rõ không thể xác nhận nếu thiếu audit log, và đánh giá confidence chỉ MEDIUM. Nó không bị trình bày như kết luận đã chứng minh.

Còn thiếu so với recommendation vòng 1:

- V2 không cung cấp hoặc dẫn tới raw request parameters và raw API responses đã lưu.
- Chưa xác minh `publishAt`, upload/schedule history hay trạng thái visibility trước public.
- Việc anomaly tái hiện qua query cô lập loại trừ bulk contamination, nhưng chưa đủ để khẳng định rộng rằng nó “not a script artifact”: cùng một logic request/transformation vẫn có thể tạo lỗi ở cả query bulk và isolated.
- Câu “credential/query-bug hypotheses are ruled out” hơi mạnh đối với `B_i31QRy670`: credential sai trong lần kiểm tra đầu đã được sửa, nhưng evidence thô của lần chạy đúng không có trong v2.
- “Further investigation is not pursued this cycle” chưa hoàn toàn đáp ứng yêu cầu P0 data-integrity investigation ban đầu.

2. High — “Engagement difference is real” chưa được chứng minh: **ĐÃ SỬA ĐỦ**

V2:

- Hiển thị đúng phép đối soát 10.62s và 9.42s.
- Rút lại kết luận về statistical reliability.
- Chỉ nói API trả về AVD/AVP khác nhau.
- Nêu rõ chưa biết denominator và cần documentation hoặc `engagedViews`.
- Hạ confidence xuống LOW.

3. High — Duration được diễn giải gần như nguyên nhân/confound: **ĐÃ SỬA ĐỦ**

V2 đã:

- Gọi duration là “potential design difference”.
- Nói rõ AVP vốn đã duration-normalized.
- Không quy phần chênh lệch cho duration với n=1 mỗi channel.
- Rút lại giải thích loop/rounding không có chứng cứ.
- Giữ discrepancy 24.81s ở trạng thái chưa giải thích.

4. Medium — Experiment A dùng metric/success criterion không phù hợp: **ĐÃ SỬA ĐỦ**

V2 đã tách:

- Retrieval correctness: 100% so với single-day control.
- Analytical usability: ngưỡng định trước `views ≥ 500`.

Đồng thời không còn đặt target tăng số video mà tooling không thể kiểm soát, và đã bổ sung quota, pagination, duplicates, partial responses cùng rollback condition.

5. Medium — Experiment D thiếu đặc tả, effort thấp và rollback sai phạm vi: **SỬA MỘT PHẦN**

Đã sửa:

- Effort tăng lên 3.
- Thừa nhận phạm vi nhiều generator.
- Bổ sung test missing/corrupt/stale sidecar, resume và registry persistence.
- Mở rộng rollback sang writer, reader và registry đã migrate một phần.

Còn thiếu:

- Chưa định nghĩa schema/version cụ thể.
- Chưa định nghĩa naming/mapping contract 1:1 giữa source segment và sidecar.
- Chưa quy định hành vi cụ thể khi missing/corrupt/stale.
- Chưa xử lý rõ collision và backward compatibility.
- “Rollback … must cover” mới là yêu cầu tổng quát, chưa phải kế hoạch rollback khả thi cho registry data đã migrate.

6. Medium — Experiment C thiếu sampling frame và rubric đo được: **SỬA MỘT PHẦN**

Đã bổ sung đúng các thành phần cần thiết: locked population, date range, stratification, checklist, hai lượt độc lập/adjudication, numerator/denominator và decision rules.

Tuy nhiên, các yếu tố quyết định vẫn để dưới dạng placeholder:

- “e.g. all … in a defined date range” chưa khóa date range thật.
- Chưa xác định population size hoặc sampling rule cụ thể.
- “above a set threshold” chưa đặt threshold.
- Chưa có rubric severity vận hành cụ thể ngoài zero-tolerance cho threat/deadline.

Vì vậy card đã có khung tốt nhưng chưa đủ executable hoặc reproducible.

7. Medium — Experiment B không phải experiment và không kiểm tra correctness: **ĐÃ SỬA ĐỦ**

V2 đã:

- Đổi tên thành reporting control.
- Yêu cầu AVD, AVP, duration và reconciliation.
- Bắt buộc warning khi không đối soát được.
- Không còn coi việc đặt hai số cạnh nhau là đủ.

“Reasonable tolerance” chưa được định lượng, nhưng không làm mất phần sửa cốt lõi; nên định nghĩa trước khi triển khai control.

8. Medium — Bảng Impact × Confidence × Effort thiếu justification/false precision: **SỬA MỘT PHẦN**

Đã sửa:

- Thêm anomaly/invariant vào bảng.
- Điều chỉnh effort/confidence.
- Có justification.
- Cảnh báo score chỉ là ordinal-derived và dùng judgment để phá hòa.

Còn vấn đề:

- Vẫn tính và hiển thị decimal score từ thang ordinal.
- Justification chưa thực sự theo từng cell; nhiều hàng chỉ có một câu tổng quát.
- E được gọi là “top priority” dù E có Impact 2, trong khi D có Impact 3; thứ tự chỉ có thể hiểu nếu ưu tiên theo score.
- Confidence của E là 3 với lý do “mechanism directly demonstrated”, trong khi §0 nói cơ chế preview chưa được chứng minh. Chỉ sự tồn tại/tái hiện của anomaly được chứng minh, không phải mechanism.

9. Low — §1.1/§1.5 overclaim về cơ chế availability: **ĐÃ SỬA ĐỦ**

V2 đã thu hẹp phát biểu xuống đúng phần được kiểm chứng:

- Day dimension theo PT.
- Bucket `2026-07-24` có 853 views cho video cụ thể.
- Không còn giải thích toàn bộ sibling videos bằng earliest-slot mechanism.
- Không còn nói “entire first-day activity”.

10. Low — “Experiment A helps accumulate” và non-recommendations không nhất quán: **ĐÃ SỬA ĐỦ**

V2 nói chính xác Experiment A chỉ retrieve/observe dữ liệu đã được xử lý, không tạo observation và không tăng tốc Analytics. Experiment E cũng được đặt làm prerequisite cho các phân tích sau.

Vấn đề mới trong v2:

- **Severity: Medium**
- **Evidence:** §0 gọi các hàng trước public là data-integrity anomaly và E tự động “excludes” chúng dựa trên public publish day. Nhưng chính giả thuyết của v2 cho rằng đây có thể là genuine pre-public preview views. Nếu vậy, hàng dữ liệu không nhất thiết sai; nó chỉ không phù hợp để đo public performance. Ngoài ra, cụm “video’s own viewable PT day” bị dùng gần như đồng nghĩa với public `publishedAt`, trong khi scheduled/private preview có thể làm video viewable sớm hơn đối với chủ kênh.
- **Recommendation:** Định nghĩa invariant là “row predates public-publish PT day” và quarantine khỏi public-performance analysis, không gọi nó là bằng chứng row không trustworthy hoặc data corruption. Lưu nguyên row trong raw data, kèm reason code và provenance.

- **Severity: Medium**
- **Evidence:** §0 nói anomaly “not a script artifact” và bảng nói E có Confidence 3 vì “mechanism directly demonstrated”. Isolated queries chỉ chứng minh hiện tượng tái hiện và giảm khả năng bulk contamination; chúng không chứng minh nguyên nhân, cũng chưa loại trừ shared request/transformation semantics nếu raw requests/responses chưa được lưu và kiểm tra.
- **Recommendation:** Đổi thành “reproduced outside the bulk query; bulk cross-contamination and the identified credential mismatch are unlikely explanations”. Trong bảng, mô tả confidence là cao đối với khả năng phát hiện violation, không phải đối với cơ chế gây anomaly.

- **Severity: Low**
- **Evidence:** Hồ sơ tự nhận có 9 issues nhưng critique và accept/reject log thực tế đánh số/miêu tả 10 finding: 3 High + 5 Medium + 2 Low.
- **Recommendation:** Sửa metadata, summary và references thành 10 issues để bảo đảm traceability.

