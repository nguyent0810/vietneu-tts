codex
Kết quả kiểm tra 7 điểm còn lại:

1. §0 raw evidence và mức claim: ĐẠT. Đã có raw isolated-query output, credential source, `publishAt`, `privacyStatus`, `uploadStatus`; đồng thời thừa nhận shared `_query()` vẫn có thể gây lỗi. Không còn claim rộng “not a script artifact” hay đã xác định mechanism.

2. Quarantine framing: ĐẠT. Invariant dựa trên “public publish PT day”; row được giữ nguyên, thêm `quarantine_reason`, chỉ loại khỏi public-performance analysis, không gọi là corrupt/invalid.

3. Bảng Impact × Confidence × Effort: ĐẠT. Confidence=3 của E được định nghĩa rõ là detection confidence, không phải mechanism confidence. Priority ordering theo Score cũng được nói rõ.

4. Experiment D: SỬA MỘT PHẦN.

- Schema/version, 1:1 mapping, missing/corrupt/stale behavior, backward compatibility, resume và rollback đã được mô tả cụ thể.
- Medium — collision contract vẫn tự mâu thuẫn.
- Evidence: [04_claude_diagnosis_v3.md:127](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/analytics_reviews/cycle2_2026-07-27/04_claude_diagnosis_v3.md:127>) nói sidecar “overwrites”, rồi gọi đó là cùng behavior với “`.txt` overwrite/numbered-suffix logic”. Overwrite và numbered suffix là hai behavior khác nhau; generator hiện cũng không đồng nhất—một số overwrite, một số tạo suffix.
- Recommendation: Quy định sidecar luôn được suy ra từ `out_path` thực tế sau khi generator đã giải quyết collision. Nếu `.txt` thành `_2_Short.txt`, sidecar phải là `_2_Short.meta.v1.json`; nếu `.txt` bị overwrite thì sidecar tương ứng mới được overwrite. Bổ sung test cho cả hai nhánh.

5. Experiment C: SỬA MỘT PHẦN.

- Population=8, full-population review và numeric threshold đã khóa.
- Medium — date range chưa được khóa bằng ngày thực.
- Evidence: [04_claude_diagnosis_v3.md:137](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/analytics_reviews/cycle2_2026-07-27/04_claude_diagnosis_v3.md:137>) chỉ ghi “as of this review” và “this cycle”, không nêu ngày bắt đầu/kết thúc hoặc điều kiện thời gian xác định được. Điều này chưa đáp ứng chính claim “locked an actual date range”.
- Recommendation: Ghi rõ date range bằng ngày ISO, hoặc định nghĩa snapshot có thể tái lập, chẳng hạn `created_at/uploaded_at từ YYYY-MM-DD đến YYYY-MM-DD, snapshot registry tại 2026-07-27T…+07:00`.

6. Số issue vòng 1: ĐẠT. Đã sửa thành 10; các số 9 còn lại chỉ nói “9 of 17 videos” và “9 generators”, không phải issue count.

Không phát hiện vấn đề mới ngoài hai điểm chưa hoàn tất thuộc chính Experiment D và C.
