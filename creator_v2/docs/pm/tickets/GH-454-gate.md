# GH-454 — Cổng "cửa sổ sốc 3 giây" cho Short MIM/CK/CL

## Bối cảnh
Chủ kênh duyệt 15/11 và 17/11: Short MIM/CK/CL dồn bi kịch / nghịch lý / sốc vào 3 giây đầu
(`docs/pm/storytelling-guide.md`, mục "Tiêu đề và mở đầu kiểu survival", dòng "Short: ...").
Hiện `motion/stier/script_lint.py::short_retention()` (gọi từ `motion/stier/build.py --preflight`, bỏ qua bằng `--allow-hook`)
chỉ chặn câu 1 > 14 từ.

## Việc (code + test)
Mở rộng `short_retention(spec)` cho theme `mim`, `ck`, `case`:

Áp dụng mức LỖI khi spec có `publish_at` >= `2026-12-01` (đợt mới); spec cũ hơn hoặc thiếu `publish_at` thì cùng các luật đó chỉ là CẢNH BÁO (không làm hỏng Short cũ khi build lại).

1. `spec["hook_kind"]` bắt buộc, thuộc {"bi_kich", "nghich_ly", "dong_ho"}.
2. Câu 1 (`lines[0]`) ≤ 9 từ (đếm bằng `words()` sẵn có).
3. Câu hỏi hậu quả trước giây 3: trong các từ đọc ở 3 giây đầu (ước lượng 3,3 từ/giây như preflight đang dùng, tức ~10 từ đầu của lines nối lại) phải có một câu kết thúc bằng "?" HOẶC có từ hỏi ("vì sao", "tại sao", "sao", "làm sao", "điều gì", "chuyện gì", "ai", "bao nhiêu", "thế nào"). Nếu đo thật bằng timing có sẵn trong build thì càng tốt, nhưng preflight không có audio nên dùng ước lượng.
4. Cảnh mở đầu (cảnh phủ thời điểm 0) không được là chữ trần: phải có ảnh/clip/hình nền (dùng đúng định nghĩa "chữ trần" mà build.py/mix lint đang dùng; tìm trong `motion/stier/build.py`). Không có logo/kicker kênh làm cảnh đầu.
5. Tiêu đề ≤ 60 ký tự.

Giữ nguyên các luật cũ. Thông báo lỗi tiếng Việt ngắn, có tên luật.

## Test
Thêm vào `tests/test_script_lint_short.py`: mỗi luật một ca đạt + một ca hỏng; ca spec cũ (publish_at 2026-11-20) chỉ ra cảnh báo. Chạy `python -m pytest tests/test_script_lint_short.py tests/test_stier_hook_gate.py tests/test_stier_preflight_schema.py -q` phải xanh, và `python -m pytest -q -x tests` không đỏ thêm.

## Môi trường
Bạn đang chạy TRONG worktree riêng `D:\Tools\Youtube Creator v2\wt-454` (nhánh `lead/454-short-hook-gate`, tách từ origin/main). Mọi đường dẫn ở trên tính từ `D:\Tools\Youtube Creator v2\wt-454\creator_v2`. Chạy pytest trong thư mục đó. Không đụng checkout `vietneu-main`.

## File được ghi
Trong worktree: chỉ `motion/stier/script_lint.py`, `motion/stier/build.py` (nếu cần nối), `tests/test_script_lint_short.py`, và báo cáo.
Ghi file tiếng Việt bằng Python `encoding="utf-8"`; kiểm diff không có '?' thay chữ có dấu.
Không commit, không render, không gọi mạng.

## Báo cáo
`docs/pm/tickets/GH-454-gate.report.md` trong worktree này (UTF-8): tóm tắt thay đổi, lệnh test và kết quả (dán dòng cuối pytest).
