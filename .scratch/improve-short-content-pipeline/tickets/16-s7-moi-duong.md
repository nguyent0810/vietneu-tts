# 16: S7 cho mọi đường vào còn lại

**Spec:** `../spec-2.md`, mục Script Quality Gate (S7). Quyết định: D87.

**What to build:** Mọi Domain và mọi đường vào (các generator FS còn lại, TRENDING, BUD review, CL sidecar / Phase A / orchestrator, CL storytelling / educational) đều đi qua S7 ngay sau S1, và có Quality record `layer: script`. Không Short nào tới TTS mà không có quyết định của S7.

**Blocked by:** 14, 15, 03, 04, 05b

**Prerequisite vận hành:** 01

**Status:** ready-for-agent

- [ ] Mỗi đường vào có test khẳng định kết quả đi qua S7 và có record `layer: script`
- [ ] Runner không đưa Short tới TTS khi chưa có quyết định S7, hoặc khi S7 FAIL
- [ ] Short đi đường bypass judge vẫn qua S7; Gate status Needs review của S1 không bị S7 ghi đè thành PASS
- [ ] Test cần runner/registry thuộc nhóm CI/container
