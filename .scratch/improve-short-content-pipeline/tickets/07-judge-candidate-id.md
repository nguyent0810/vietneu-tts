# 07: Judge chỉ trả candidate_id, bỏ word overlap 0.4

**Spec:** `../spec.md` — Judge chỉ chọn. Quyết định: D28 (đã sửa), D48, D56.

**What to build:** Judge chọn ứng viên thắng bằng `candidate_id`; script được dùng luôn là nguyên văn ứng viên đó. Verdict thiếu, sai hoặc lạ `candidate_id`, hoặc sai cấu trúc, bị từ chối và được ghi thành lỗi judge trong lịch sử vòng của engine (S1 ánh xạ lỗi này qua cơ chế chung của engine outcome, không cần ticket này chờ S1). Bỏ word overlap 0.4; giữ yêu cầu fact-check của ứng viên thắng phải PASS.

**Blocked by:** None (can start immediately)

**Status:** done (grok review OK)

- [x] Contract verdict: `candidate_id` + fact-check + điểm + feedback, không có script
- [x] Prompt judge hiện hành cập nhật theo contract mới (không đổi rubric)
- [x] Văn bản thắng lấy từ danh sách ứng viên bằng `candidate_id`
- [x] Verdict có kèm script tự viết không làm thay đổi văn bản được chọn
- [x] `candidate_id` thiếu / không tồn tại / verdict sai cấu trúc → verdict bị từ chối, ghi vào lịch sử vòng
- [x] Word overlap 0.4 bị xoá
- [x] Test thuần trên hàm kiểm tra verdict + test qua engine với Codex giả lập
