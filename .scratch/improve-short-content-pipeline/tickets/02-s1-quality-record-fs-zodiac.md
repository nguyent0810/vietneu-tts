# 02: Content Quality Gate (S1) + kho Quality record, nối xuyên suốt với generator zodiac

**Spec:** `../spec.md` — Content Quality Gate, Kho Quality record. Quyết định: D40, D43, D44, D46, D47, D52, D53, D54.

**What to build:** Lập seam S1. Khi generator 12 con giáp chạy, dù kết quả là PASS, không fact-check nào PASS, dưới ngưỡng `hook_score` hiện hành, lỗi generate/judge hay verdict bị từ chối, outcome đều đi qua S1, được chuẩn hoá thành Gate decision (Gate status + reason codes) và ghi thành một dòng Quality record trong kho append-only của Domain Phong Thủy. Record giữ nguyên source outcome gốc bên cạnh Gate decision. Khi generator FAIL vẫn có record, dù không có file script nào được ghi. Không đổi ngưỡng hay rubric nào.

**Blocked by:** None (can start immediately)

**Status:** done (grok review OK)

- [x] S1 nhận source outcome, trả Gate decision; bảng ánh xạ nằm một chỗ duy nhất
- [x] Ánh xạ đủ các outcome của judge panel engine: pass, không fact-check PASS, dưới ngưỡng, lỗi generate/judge theo vòng, verdict bị từ chối, bypass (ở đây chỉ ghi nhận source outcome; hành vi bypass đầy đủ ở ticket 06)
- [x] Outcome không có trong bảng ánh xạ → reason code dành cho outcome chưa map + Gate status Needs review (không map ngầm)
- [x] Reason code là tập đóng có tiền tố nhóm (`ACC_`, `SAF_`, `STR_`, `JUDGE_`, `SRC_`, `BYPASS_`, và nhóm internal)
- [x] Quality record có tối thiểu: quality_record_id, created_at, schema version, domain, content_id/video_id, rubric_version = "legacy", generator_version, prompt_version, judge_model (giá trị thật), gate_status, reason_codes, source_outcome, evidence, bypass flag, mọi ứng viên kèm điểm/fact-check và nhãn Hook formula
- [x] Record FAIL đủ để gán nhãn mù sau này: script/ứng viên, fact set hoặc source excerpt, timestamp
- [x] Kho append-only, một file JSONL mỗi Domain, trong vùng output bị gitignore; lần chạy sau không ghi đè dòng cũ
- [x] Ghi record không dùng khoá chỉ có trên Unix; test S1 chạy được trên Windows
- [x] Ghi record thất bại → Short đó bị chặn khỏi Publish path; lỗi không làm crash cả batch
- [x] Generator zodiac gọi S1 cho mọi outcome, kể cả khi thoát vì FAIL
- [x] Test qua seam S1 cho từng loại outcome; test qua generator zodiac với agy/Codex giả lập ở cấp hàm gọi CLI
