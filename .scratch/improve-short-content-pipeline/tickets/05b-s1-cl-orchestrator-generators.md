# 05b: Nối S1 vào CL orchestrator escalation + generator CL / storytelling / educational

**Spec:** `../spec.md` — Content Quality Gate (call site). Quyết định: D46.

**What to build:** Các outcome escalation của CL orchestrator (hiện chỉ nằm trong bộ nhớ; audit log không được ghi) và outcome của các generator criminal law, storytelling, educational, provenance đều đi qua S1 và có Quality record.

**Blocked by:** 05a

**Prerequisite vận hành:** 01

**Status:** ready-for-agent

- [ ] Mỗi loại escalation của orchestrator có reason code riêng và có record
- [ ] Generator criminal law, storytelling, educational, provenance gọi S1 cho mọi outcome, kể cả nơi hiện chỉ ghi file khi PASS
- [ ] Không còn outcome CL nào chỉ in ra màn hình mà không có record
- [ ] Test cho ít nhất một escalation và một FAIL mỗi generator
