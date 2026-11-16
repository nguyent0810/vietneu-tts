# GH-441 (Codex): Short MIM/CK/CL "kể cho tai nghe" — port PR #440

Đọc issue #441 (`gh issue view 441 --repo nguyent0810/vietneu-tts` hoặc nội dung chép dưới), PR #440 ở gốc repo (`../hf_batch_render.py` hàm `short_story_issues`, `../shortbuild/guards.py`, `../tests/test_shortbuild_guards.py`), `motion/stier/build.py` (preflight, `hook_errors`, `retention_hook_lint`), `motion/long/script_lines.py` (FLOW_SOURCE_TERMS / SOURCE_PATTERN), `motion/long/scenekit.py` (`label_pd`, #436).

Việc:
1. `motion/stier/build.py` (preflight + build): LỖI khi một dòng `lines` kết thúc bằng dấu phẩy (câu tách đôi).
2. Short truyện (spec `theme == "case"`, hoặc `story: true`, hoặc có `short_type`) và spec có `test_cell`: LỖI khi > 1 câu rào nguồn; spec khác chỉ CẢNH BÁO. Bộ từ rào: tái dùng từ script_lines.
3. Câu có `{pd}` ở cuối trong `lines` (bỏ dấu khỏi lời đọc trước TTS) → cảnh của câu đó hiện chip PHỎNG DỰNG (tái dùng cách nhãn của engine casefile hiện có, như nhãn MINH HỌA/illus); nếu không gắn được tự động thì cho khai `pd_scenes` như build_063 và guards kiểm.
4. Chỉ áp cho spec có `publish_at` ≥ 2026-11-29 hoặc không có `publish_at`; spec hẹn trước ngày đó bỏ qua (giống #440).
5. Test mới `tests/test_stier_ear.py` theo khuôn test #440.
6. Chạy preflight thử trên 3 spec CL mới nhất + `cl-hkv-survival-pilot` (chỉ đọc), ghi kết quả.

Luật: chỉ sửa `motion/stier/build.py`, file test mới, và (nếu cần) engine casefile để hiện chip. Ghi file bằng Python `open(..., 'w', encoding='utf-8')`, KHÔNG PowerShell; không có `??` mới trong diff. Chỉ chạy test liên quan + `tests/test_console.py`. Không render, không commit/push/đăng, không đọc credentials.
Báo cáo `docs/pm/tickets/GH-441-report.md` (tiếng Việt, Python utf-8).
