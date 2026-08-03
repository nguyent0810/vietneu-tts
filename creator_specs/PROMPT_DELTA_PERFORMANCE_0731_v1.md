# Prompt Delta — Performance Audit 30-31/07 v1 — 3 đề xuất từ phân tích hiệu năng thực tế

**Nguồn:** phân tích video thật 30-31/07 (3 kênh, `channel_perf_fresh.json`) + `perf_findings_draft.md` v3 (Codex-approved 4 vòng, dữ liệu tới 27/07) + audit thủ công script FS Long EP001. Quy trình: 3 vòng Codex adversarial review (`codex_perf_hyp_review1/2/3_out.txt`) — round 1 bắt 21 lỗi (kể cả 1 lỗi factual của Claude: nhầm domain EP001 là BUD trong khi là FS), round 2 bắt tiếp 2 HIGH + nhiều MEDIUM (chủ yếu về Delta #3 quá rộng + lỗ hổng semantic), round 3 bị TREO sau 42 phút (không giống hành vi bình thường của round 1-2, vốn chỉ mất vài phút) — đã dừng, không chờ thêm, tự quyết định thận trọng dựa trên kết luận round 2.

**Trạng thái tổng thể: CHỈ Delta #3 (phạm vi đã thu hẹp) được áp dụng. Delta #1 và #2 là THIẾT KẾ THỬ NGHIỆM, CHƯA triển khai vào pipeline.** Đây không phải thất bại của quá trình audit — sau 2 vòng phản biện nghiêm túc, phần lớn giả thuyết nền (đặc biệt Pattern A dựa trên video n=2/n=5 view) không đạt ngưỡng bằng chứng đủ mạnh để biện minh cho 1 rule bắt buộc trong pipeline. Chi tiết đầy đủ từng giả thuyết/điều kiện bác bỏ: xem `perf_hypotheses_v3.md` trong scratchpad (không copy lại toàn bộ ở đây để tránh trùng lặp).

---

## Delta #3 — Giảm lặp disclaimer ở Long-form (ĐÃ ÁP DỤNG, phạm vi hẹp)

**Bằng chứng:** script FS Long EP001 (`content_repo_clone/DOMAINS/FENG_SHUI/PRODUCTION_PACKAGES/TU_VI_PHONG_THUY/EP001/OUTPUT/03_AUDIO_SCRIPT_TTS.txt`) lặp cam kết "không tính lá số cho bạn" gần nguyên văn 3 lần (dòng 17, 67, và khối 71-89 dài ~19 dòng thuần rào chắn, không nhân vật/kịch tính).

**Đã làm:**
1. Sửa THỦ CÔNG file script gốc của EP001 (xem diff bên dưới) — đây là bản ghi lưu trữ/tham khảo, **KHÔNG làm thay đổi video đã publish** (`video_id: GxbJ7acsjlA`, đã `status: uploaded`, publish_at 2026-07-30 — video thật trên YouTube giữ nguyên, không re-render).
2. Đề xuất quy trình LINT-CÓ-NGƯỜI-DUYỆT cho Long-form TƯƠNG LAI (chưa code hoá, ghi lại đây làm spec): khi duyệt script Long mới, liệt kê các câu có cùng `boundary_intent` (nhóm theo Ý NGHĨA ranh giới/cam kết đang phát biểu — vd "không luận giải cá nhân" — KHÔNG khớp chuỗi ký tự nguyên văn, để tránh model né rule bằng cách diễn đạt lại), gắn cờ nếu >2 câu cùng `boundary_intent`, đưa cho người biên tập quyết định giữ/gộp. KHÔNG tự động xoá/rewrite bằng máy. Phạm vi CHỈ áp cho loại cam kết "không luận giải cá nhân" (loại duy nhất có bằng chứng cụ thể từ EP001), không mở rộng thành rule chung cho "mọi cam kết nội dung" (Codex round 2 chỉ ra 1 audit không đủ để tổng quát hoá).

## Delta #1 — "Initial payoff" rubric cho short_judge_panel_engine.py (THIẾT KẾ, CHƯA triển khai)

Nhắm vào Pattern B (BUD: 2 video views cao/retention thấp — "Đoán Ai Nợ Ai Từ Kiếp Trước" 881v/31.34%, "Hai vị vua, hai lời nguyện" 774v/24.93%). Schema output đầy đủ (chống game, có `not_applicable` cho cold-open hợp lệ) đã thiết kế trong `perf_hypotheses_v3.md`. **Chưa áp dụng** vì: (a) giả thuyết B1 (payoff latency) chưa được audit trực tiếp trên 2 transcript thật, (b) cần chạy thử trên mẫu nhỏ + đo agreement giữa nhiều lần chấm trước khi tin cậy.

## Delta #2 — Concrete-anchor cho category triết lý/trừu tượng (THIẾT KẾ A/B, CHƯA chạy)

Nhắm vào Pattern A (FS phân tán). **Bị hạ từ "rule bắt buộc" xuống "thiết kế A/B trên giấy"** vì 2 video bằng chứng chỉ có n=2 và n=5 views — không đủ để áp rule toàn category (Codex round 1 HIGH #4: overfitting vào nhiễu). Thiết kế A/B đầy đủ (random assignment, metric, ngưỡng, stopping rule) trong `perf_hypotheses_v3.md`. **Chưa chạy.**

---

## Diff áp dụng cho EP001 (Delta #3)

`content_repo_clone/DOMAINS/FENG_SHUI/PRODUCTION_PACKAGES/TU_VI_PHONG_THUY/EP001/OUTPUT/03_AUDIO_SCRIPT_TTS.txt`:
- Dòng 9: câu trả lời "không ai cả" đổi thành câu giữ curiosity gap thay vì đóng ngay.
- Dòng 17: rút cam kết đầy đủ xuống 1 câu tease ngắn, dời cam kết đầy đủ tới sau đoạn kể lại nhân vật thứ hai (gần dòng 91 cũ).
- Dòng 67: bỏ, không lặp lại cam kết lần 2.
- Khối 71-89 (~19 dòng): gộp thành 1 đoạn ngắn duy nhất mang đầy đủ cam kết, đặt đúng vị trí có bối cảnh/stakes cao nhất.
- Đoạn lừa đảo (dòng 91-101 cũ): viết lại dùng "người thứ hai" làm nhân vật xuyên suốt thay vì liệt kê trừu tượng.
- Đoạn Loan Đầu/Lý Khí (dòng 45-51 cũ): thêm ví dụ hình ảnh cụ thể (2 thầy, 1 căn nhà).

*(Áp dụng trực tiếp vào file, xem lịch sử git commit này để đối chiếu bản trước/sau.)*
