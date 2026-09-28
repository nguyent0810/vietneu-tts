# 06: SKIP_JUDGE_PANEL → Needs review + BYPASS_JUDGE ở mọi Domain

**Spec:** `../spec.md` — SKIP_JUDGE_PANEL. Quyết định: D19, D49.

**What to build:** `SKIP_JUDGE_PANEL` vẫn dùng được để debug, nhưng ở mọi Domain (BUD, FS, TRENDING, CL, storytelling, educational), Short đi qua bypass luôn có Gate status Needs review với reason code `BYPASS_JUDGE` và bypass flag trong Quality record; không bao giờ ở trạng thái `scripted`, không bao giờ tự upload/Publish.

**Blocked by:** 03, 04, 05b

**Prerequisite vận hành:** 01

**Status:** ready-for-agent

- [ ] Với biến bật: test cho từng Domain/đường vào cho ra Gate status Needs review, reason code `BYPASS_JUDGE`, bypass flag
- [ ] Short bypass không tới TTS/upload trong runner
- [ ] Comment sai trong engine (nói CL không đọc biến) được sửa
- [ ] Với biến tắt, hành vi không đổi
