# 14: S7 Script Quality Gate, nối xuyên suốt với generator zodiac

**Spec:** `../spec-2.md`, mục Script Quality Gate (S7). Quyết định: D52, D54, D84, D87, D88, D89, D91.

**What to build:** Một Short zodiac sau khi qua S1 đi tiếp qua S7, tại cùng điểm hội tụ, không có đường vào thứ hai. S7 chạy S8 (ticket 11) và các tín hiệu chẩn đoán bằng code (ticket 12), đọc Content invariant (ticket 13), rồi ghi một Quality record `layer: script` vào kho Quality record của Spec 1. Record có finding S8, `diagnostics` (không có trường điểm), fingerprint, và `rubric_version = "script-instrumentation-v0"`.

Kết quả theo từng trường hợp:
- S8 FAIL: Short không tới TTS hay upload.
- Invariant không đủ: Needs review với `SCR_INVARIANT_INCOMPLETE`.
- Ghi record thất bại: Short đó bị chặn (fail closed), batch vẫn chạy tiếp.

**Blocked by:** 02, 11, 12, 13

**Status:** ready-for-agent

- [ ] S7 được gọi ngay sau S1, tại cùng điểm hội tụ; không có đường vào thứ hai
- [ ] Record `layer: script` ghi vào đúng kho append-only theo Domain của Spec 1; không có store mới
- [ ] Record có finding S8, `diagnostics`, fingerprint, `rubric_version = "script-instrumentation-v0"`, và các version thật khác
- [ ] Gate status chỉ là FAIL khi có finding S8 thuộc loại chặn; chẩn đoán không bao giờ làm đổi Gate status
- [ ] S8 FAIL: Short không tới TTS hay upload
- [ ] Invariant không đủ: Needs review với `SCR_INVARIANT_INCOMPLETE`
- [ ] Outcome chưa map được: `INTERNAL_UNMAPPED` và Needs review
- [ ] Ghi record thất bại: Short bị chặn, batch không crash
- [ ] Test qua seam S7 chạy được trên Windows; test đi qua generator zodiac với agy/Codex giả lập
