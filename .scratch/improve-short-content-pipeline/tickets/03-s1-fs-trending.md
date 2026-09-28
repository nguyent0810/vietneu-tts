# 03: Nối S1 vào các generator Phong Thủy còn lại + TRENDING

**Spec:** `../spec.md` — Content Quality Gate (call site). Quyết định: D46.

**What to build:** Mọi generator FS (12 vị Thần, lịch hoàng đạo, 12 con giáp theo tháng, màu ngũ hành, vận ngũ hành, iching, western zodiac, educational và storytelling của FS) và TRENDING (bước draft và bước publish tái kiểm) đều đưa outcome qua S1 và có Quality record, giống generator zodiac ở ticket 02. Việc TRENDING luôn buộc người duyệt được thể hiện thành Gate status Needs review với reason code tương ứng, không phải logic riêng ngoài S1.

**Blocked by:** 02

**Status:** done (grok review OK)

- [x] Mỗi generator FS trong danh sách gọi S1 cho mọi outcome, kể cả khi không ghi file script
- [x] TRENDING: bước draft và bước publish đều tạo Quality record; publish tái kiểm FAIL có reason code riêng
- [x] Category và generator đúng trong record của từng generator
- [x] Test cho ít nhất một outcome PASS và một FAIL mỗi generator (agy/Codex giả lập)
