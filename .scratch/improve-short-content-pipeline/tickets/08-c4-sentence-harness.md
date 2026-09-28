# 08: Harness đo C4 cấp câu + báo cáo chạy thủ công

**Spec:** `../spec.md` — Đo C4 cấp câu. Quyết định: D29, D43.

**What to build:** Một công cụ chạy scorer C4 trên golden corpus và holdout v1/v2 đã commit, cho confusion matrix **cấp câu** (chặn đúng, chặn nhầm, bỏ sót, cho qua đúng) theo corpus, category, materiality. Test dùng scorer giả. Chạy thật với Codex là một lệnh thủ công, ghi báo cáo có scorer version, judge model, corpus, commit, thời điểm, và ghi rõ đơn vị đo là câu, không phải False Reject cấp Short.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Nạp đủ 3 corpus; báo lỗi rõ nếu fixture sai cấu trúc
- [ ] Adapter bọc excerpt của fixture thành đầu vào mà scorer C4 production cần
- [ ] Confusion matrix đúng với scorer giả, chia theo corpus, category, materiality
- [ ] Lệnh thủ công chạy scorer thật, ghi báo cáo có version/commit/thời điểm và nhãn "đơn vị: câu"
- [ ] Không chạy scorer thật trong CI
