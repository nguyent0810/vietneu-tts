# 075b — bằng chứng thực thi

Worktree `output/worktrees/wt_ascript`, nhánh `docs/audio-script-unify`; không commit/push. Python dùng venv repo chính, gọi `../../../.venv/bin/python` khi cwd ở worktree. Chỉ đọc plan/audio manifest BUD/FS, không TTS/render, không thao tác kênh/lịch. Các test entrypoint render có mock chặn trước TTS theo fixture, không render sản phẩm.

## Test trước/sau
Lệnh tại worktree:
```sh
../../../.venv/bin/python -m pytest tests/ -q -k 'lint or retention or hook or script'
```
Trước thay: `198 passed, 6 skipped, 1033 deselected, 1 warning in 5.68s` — [log](pytest-before.txt).
Sau thay cuối: `228 passed, 6 skipped, 1033 deselected in 4.29s` — [log](pytest-after.txt).
Kiểm riêng guard và toàn bộ test075b:
```sh
../../../.venv/bin/python -m pytest tests/test_shortbuild_guards.py tests/test_audio_script_unify.py -q
```
`38 passed in 0.12s` — [log](pytest-guards.txt). Bộ yêu cầu chọn theo `-k` bỏ một số test tên guard; lượt riêng kiểm bổ sung những test đó. Test legacy kỳ vọng chặn văn phong đã đổi kỳ vọng nhưng vẫn giữ cờ/gợi ý; fixture chặn trướcTTS dùng lỗi khung thật hoặc cau_dai.

Task nhắc test đỏ có sẵn trên main `test_ruleset_has_approved_d_values`. Đã tìm cả tệp ignored trong `tests`/`creator_v2/tests` của worktree và repo chính: không có hàm này ở snapshot đang mở, nên **chưa tái lập, không tuyên bố đã sửa/đã thấy test đỏ**.

## Hai plan CLI trước/sau
Dựng bản lint/HBR trước thay từ `git show HEAD:long_script_lint.py` và `git show HEAD:hf_batch_render.py` vào `/tmp/075b_before/`; chỉ chạy CLI lint `--strict`, không chạy runner. Với mỗi plan:
```sh
PYTHONPATH=<worktree> ../../../.venv/bin/python /tmp/075b_before/long_script_lint.py <repo-chinh>/output/cl_staging/long/plan_<id>.json --strict
../../../.venv/bin/python long_script_lint.py <repo-chinh>/output/cl_staging/long/plan_<id>.json --strict
```
- `L_bud_axathe`: trước/sau `-- 0 lỗi, 3 cảnh báo, 7 gợi ý`; cả hai exit0.
- `L_fs_cmp_9091`: trước/sau `-- 0 lỗi, 3 cảnh báo, 2 gợi ý`; cả hai exit0.
[Receipt SHA256 và kết quả](lint-comparison.json), log từng lượt ở `<id>.before.txt`/`<id>.after.txt`; SHA plan giữ nguyên sau chạy. Mẫu này không có vi phạm mới nên số lỗi không giảm; fixture riêng chứng minh mức kiểm đổi, không bịa cải thiện từ mẫu0 lỗi.

## Kiểm tài liệu, phạm vi và phép đo
`git diff --check`: exit0, không output lỗi.
Grep bằng regex `≤\s*10\s*tiếng|3s/câu|3s mỗi câu|3 giây mỗi câu` trên `.claude/skills/**/*.md`, phân loại riêng dòng có `≤ 4 giây`:
`SKILL_GREP: 0 luật ép ≤10 tiếng/3s mỗi câu; 1 dòng ≤ 4 giây đều là cảnh tĩnh, kèm động8s`.
`CORE_DOC: 10 mục; 9 luật lõi; 1271 token cách trắng` (số tách khoảng trắng, không phải tiếng/phút).
Kiểm mọi link Markdown đường dẫn cục bộ trong doc sửa/mới: `DOC_LOCAL_LINKS: PASS`.
So AST từng hàm HBR với bảnHEAD: `IMAGE_GATES_UNCHANGED: pace_gate_issues, opening_gate, bare_lines, reveal_issues, pacing`. Không sửa `hf_qa`, `studio.py`, bộ kiểm độc lập hay composition.
Đo lại:
```sh
../../../.venv/bin/python docs/research/075b/measure.py ../../.. > /tmp/075b-rates-recheck.json
```
So JSON với `voice-rates.json`: `VOICE_RATES_REPLAY: 7 nhóm khớp receipt`. [Bảng tốc độ và giới hạn](../../script/voice-rates.md); không có mẫu Thục Đoan trong thư mục được quét.

## Mức kiểm và việc Lead cần quyết
[Ma trận](../../script/lint-matrix.md) có danh sách hạ mức và lý do; Long có7 mã LỖI, đường audio HBR/shortbuild có10 nhóm như lõi §9 (không gộp cổng hình/schema/render vào con số này). Hạ lookup/tuyển tập vì đoán nghĩa/chương/clock nháp, TRUU_TUONG vì từ điển không hiểu nghĩa, v2/tone/rào nguồn vì gu hoặc heuristic. Nhịp/CTA/rehook/payoff và hồ sơ nhân vật tiếp tục CB. Giữ override hỏng, câu dài, tên chi, integrity, nguồn BUD và cổng hình hiện có. Không thêm lint phỏng dựng BUD.

1. Lead điền `audio_script_rules.AUDIO_SCRIPT_FROM` bằng **ngày merge thật** (đangNone); `tts.pause_ctx`/row.pause_ctx đã bật LỖI ngay. Có test ngày trước/từ mốc, không chọn ngày17/11 thay ngày merge.
2. Code V2 stier chưa đổi: `creator_v2/AGENTS.md` mục “Không sửa code dùng chung” chỉ ngoại lệ ticket code ghi rõ tên file. Task gọi đích danh long lint + retention + hook nhưng chưa ghi các file `creator_v2/motion/stier/build.py`, `script_lint.py`. Đã chuyển văn bản/hồ sơ và ghi đủ mọi đường chặn cũ trong ma trận; cần Lead giao rõ hai file này nếu muốn áp mức CB xuyên V2. Không dùng tài liệu mới để tuyên bố preflight legacy đã đổi.
3. Bổ sung segments Thục Đoan cùng cấu hình mới khi sản xuất có audio; không cần chạyTTS trong task docs/code.

Danh sách file: [changed-files.txt](changed-files.txt). Phụ lục X01–X20 ở `docs/script/conflicts-075b.md`. Báo cáo bàn giao ngắn ở repo chính, không tạo/sửa plan sản xuất.
