# GH-411 (Codex): cửa sổ sốc 40 s cho Long MIM/CK/CL — port PR #407

Đọc issue #411 (nội dung chép dưới), `motion/long/opening_gate.py`, `motion/stier/build.py` (`hook_errors`, `retention_hook_lint`), `docs/pm/storytelling-guide.md` mục "Tiêu đề và mở đầu kiểu survival" + "Cửa sổ sốc", và PR #407 ở gốc repo: `../long_script_lint.py` (hàm/biến soc_40s, shock_window_s, OPEN_LOOP) + `../tests/test_long_script_lint.py` để tái dùng danh sách dấu hiệu.

## Việc
1. `motion/long/opening_gate.py`:
   - **O7 (cảnh báo, không chặn):** 40 giây đầu không có câu hỏi ("?"), câu móc hay nghịch lý (tái dùng danh sách dấu hiệu của #407). Dùng giây thật từ `timing.json` nếu có (output/long/<topic>/chNN/timing.json), không thì ước lượng như `estimated_lines`. Câu bắt đầu đúng giây 40 không tính.
   - **O8 (cảnh báo):** trong 40 giây đầu có < 3 "nhịp hình mạnh": cảnh type slam / quote / counter / question, hoặc cảnh có `vid`, hoặc photo có `tone` hoặc `move`.
   - In O7/O8 ở cùng chỗ in O1 (retention_findings / problems), ghi rõ là cảnh báo.
2. `motion/stier/build.py`: với spec `rules >= 3`, thêm cảnh báo (không lỗi) khi `lines[0]` > 9 từ.
3. Test mới trong `tests/` theo khuôn test #407: thiếu sốc, câu hỏi sớm, nghịch lý muộn (sau 40 s → cảnh báo), theo giây thật, O8 đủ/thiếu nhịp hình, Short câu 0 > 9 từ.
4. Chạy thử (chỉ đọc) trên `cl-dich-nhan-kiet`, `mim-binance-6-3-ty-20-phut`, `ck-c8-10-trieu-mua-duoc-gi` (data có trong worktree; timing thật nằm ở `D:\Tools\Youtube Creator v2ietneu-main\creator_v2\output\long\<topic>\` — nếu hàm cần output thì cho tham số root/out, không chép file vào repo) và 1 Long cũ trước 13/11 (vd `mata-hari`). Ghi kết quả vào báo cáo.

## Luật
- Chỉ sửa: `motion/long/opening_gate.py`, `motion/stier/build.py`, file test mới trong `tests/`. Không sửa file khác.
- Mọi CLI mới (nếu có) gọi `factory.console.utf8_console()`.
- **Ghi file bằng Python `open(..., 'w', encoding='utf-8')`. Không dùng PowerShell để ghi** (từng làm mất dấu tiếng Việt thành '?'). Sau khi ghi, kiểm bằng Python không có chuỗi `??` mới trong file đã sửa (`git diff | grep '??'`).
- Chạy `python -m pytest -q tests` toàn bộ: phải xanh.
- Không commit, không push, không render, không đăng, không đọc thư mục credentials.

## Báo cáo
`docs/pm/tickets/GH-411-report.md` (tiếng Việt có dấu, ghi bằng Python utf-8): thay đổi, số test, kết quả pytest, kết quả chạy thử 4 Long (O7/O8 in gì).
