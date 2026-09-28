# 05a: Nối S1 vào CL sidecar gate + Phase A/C4

**Spec:** `../spec.md` — Content Quality Gate (call site). Quyết định: D29, D43, D46.

**What to build:** Mọi outcome của CL sidecar gate và Phase A (gồm C4 FAIL) đi qua S1 và có Quality record. Reject của C4 không còn chỉ in ra màn hình: record lưu script/draft, source excerpt, case_id, các câu bị chặn và timestamp, để sau này đo False Reject cấp Short.

**Blocked by:** 02

**Prerequisite vận hành:** 01

**Status:** ready-for-agent

- [ ] Sidecar gate PASS/FAIL đi qua S1; reason code riêng cho từng loại fail của sidecar
- [ ] Phase A C4 FAIL và storytelling C4 FAIL có record, với các câu bị chặn làm evidence
- [ ] Record CL có case_id và các hash đã review
- [ ] Không đổi logic chấm của C4
- [ ] Test với Codex giả lập trả claims bị chặn và không bị chặn
