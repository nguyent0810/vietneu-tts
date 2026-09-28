# 04: Nối S1 vào BUD review + runner đọc Gate decision

**Spec:** `../spec.md` — Content Quality Gate (call site, runner). Quyết định: D12, D46, D47.

**What to build:** Short Phật giáo (Short trích từ Long) đi qua bước viết lại, rồi outcome qua S1 và có Quality record, gồm cả trường hợp Source không đủ. Runner không còn tự diễn giải outcome theo topic (nhánh BUD, nhánh "dùng thẳng" của topic khác): runner đọc Gate decision của S1 để quyết định Short có được đi tiếp tới TTS hay không. Registry chỉ giữ reference tới Quality record, không phải source of truth.

**Blocked by:** 02

**Prerequisite vận hành:** 01 (test runner/registry chạy trên CI hoặc container)

**Status:** ready-for-agent

- [ ] BUD review đưa outcome qua S1; record ghi là Short trích từ Long và ghi Long nguồn
- [ ] Nguồn yếu → Gate status Source không đủ, không phải FAIL
- [ ] Runner dùng Gate decision cho mọi topic; nhánh "dùng thẳng" không còn bỏ qua S1
- [ ] Short có Gate status khác PASS không tới TTS/upload
- [ ] Registry entry có reference tới quality_record_id
- [ ] Test runner qua xử lý một segment, với registry trỏ vào thư mục tạm và TTS bị chặn, cho PASS, Needs review và Source không đủ
