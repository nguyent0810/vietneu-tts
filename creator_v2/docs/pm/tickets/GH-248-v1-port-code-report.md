# GH-248 — Báo cáo code: 3 cổng v1 (thumb, opening, script_lint)

- Nhánh: `feat/v1-gates` trong worktree `D:\Tools\Youtube Creator v2\wt-v1port\creator_v2` (từ `origin/main`, `9c5d14c`).
- Không commit, không push, không đăng, không đổi lịch. Không sửa checkout `vietneu-main`.
- Python: `vietneu-main\creator_v2\.venv\Scripts\python.exe`. pytest: `--basetemp=...\scratchpad\pyt -p no:cacheprovider`.

## File đã sửa

| File | Việc |
|---|---|
| `motion/long/thumb.py` | Cảnh báo khi mẫu không có `<img>`. Lỗi khi chữ < 44px trên khung 1280 (mẫu 1920×1080 thì ngưỡng 66px) hoặc chữ giao vùng badge góc dưới-phải (x > 1060/1280, y > 620/720). Render thêm `tN_tiny.jpg` 168×94. Giữ `--allow-thumb`, `--lint-only`. |
| `motion/long/opening_gate.py` | "1,2 tỷ" khớp "một tỷ hai"; "1,5 triệu" khớp "một triệu rưỡi" và "một triệu năm". O2b: chữ nền trống liên tục > 3,0s trong 0–40s là lỗi. O6: năm cụm meta trong 0–40s là lỗi. |
| `motion/stier/script_lint.py` | `short_retention()` cho theme `mim`, `ck`, `case` (CL). |
| `motion/stier/build.py` | `--preflight` gọi `short_retention`. `--allow-hook` bỏ qua cùng cổng hook cũ. |
| `tests/test_thumb_lint.py`, `tests/test_opening_gate.py`, `tests/test_script_lint_short.py` | Test mới. |

`git diff --stat` (chưa tính file test mới, chưa commit): 6 file, +490 / −5. `tests/test_script_lint_short.py` đang untracked.

## Diff tóm tắt

- **Thumb.** Luật cũ (số từ chữ lớn, cỡ `.big` sau FIT, ảnh phẳng) giữ nguyên. Luật mới nằm trong `lint_feed()`, gọi từ `lint()` nên `--lint-only` và lúc dựng đều in `THUMB LINT:`. Thiếu `<img>` chỉ là `CẢNH BÁO`, không làm mã thoát thành 1. Chữ đo theo `font-size` inline hoặc CSS; vị trí lấy `left/top/right/bottom`, `text-align`, `translateX(-50%)`. Vòng xuất ảnh thêm `scale=168:94` thành `tN_tiny.jpg`. Lần này không render, nên chưa có file `tN_tiny.jpg` thật.
- **Opening.** Bộ chuẩn hoá TTS vẫn đọc "1,2 tỷ" thành "một phẩy hai tỷ" và cách đó vẫn khớp. Thêm cách nói thường: số nguyên + đơn vị + một chữ số thập phân, và với `,5` thêm "rưỡi". Không nhận "một tỷ hai mươi" là 1,2. O2b gộp các cảnh `TEXT_TYPES` không `img`/`vid`/`bg` nếu dính nhau; đúng 3,0s thì qua, dài hơn thì lỗi. O6 soi từ có mốc < 40s.
- **Short.** Câu 1 hơn 14 từ là lỗi. Câu 2 chứa "là một" / "được gọi là" / "nghĩa là" là cảnh báo. Tiêu đề kết thúc bằng `?` mà không có số và không có tên riêng (viết tắt Latin như AI, tên Latin, chữ hoa giữa câu thường) là cảnh báo. Theme `bud` không đi qua hàm này. Spec không ghi `theme` được coi là `case` (CL), đúng mặc định của `themes.py`.

## Test

Trước khi sửa: **7 failed, 1115 passed, 20 skipped** (124,85s).

Sau khi sửa: **7 failed, 1129 passed, 20 skipped** (111,72s).

Thêm 14 test passed. Bảy lỗi không đổi, đều `ModuleNotFoundError: No module named 'vnlunar'`:

- `tests/test_claims.py`: `test_wrong_month_statistic_is_caught`, `test_correct_month_statistic_passes`, `test_statistic_about_another_month_is_rejected`, `test_god_count_statistic_is_verified`, `test_statistics_are_recounted_not_trusted`
- `tests/test_lines.py::test_lich_countdown_is_real`
- `tests/test_pillars.py::test_daily_kind_takes_over_when_fixed_topics_run_out`

`pytest tests -q -k "thumb or opening or script_lint or hook"`: **50 passed, 1106 deselected**.

## Ba lệnh kiểm

`opening_gate.py` và `thumb.py` lấy `ROOT` từ vị trí file (`Path(__file__)`), không từ cwd. Worktree là `origin/main`: không có `output/.../timing.json`, không có `motion/long/thumbs/ck-g2-bao-hiem-lien-ket_t1.html`, không có spec `mim-tr-agent-browser` và `cl-tr-calvin-fairbank-1851`. Những thứ đó nằm ở checkout sản xuất. Code worktree đọc data sản xuất qua `--root` (opening, build) hoặc gán `HERE`/`ROOT` (thumb, vì CLI chưa có `--root`).

### 1. `opening_gate.py ck-e4-bao-hiem-tien-gui`

Lệnh đúng dữ liệu đã render (code worktree, data + `timing.json` sản xuất):

```
python motion/long/opening_gate.py ck-e4-bao-hiem-tien-gui --root "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2"
```

```
OK
```

Mã thoát 0. Không còn dòng "1,2 Tỷ". Lời 0–6,6s là "Gửi một tỷ hai…", trước đây chỉ khớp "một phẩy hai tỷ" nên trượt. "350 Triệu" vẫn khớp "ba trăm năm mươi triệu". Không phát sinh O2b hay O6 trên timing này.

Cùng file, không `--root` (data worktree, không có `timing.json`, ước lượng): "một tỷ hai" rơi vào khoảng 36,7s, ngoài cửa 20s, nên dòng "1,2 Tỷ" vẫn in. Đó là vì lời trong bản `origin/main` nói số quá muộn, không phải vì còn lệch cách đọc. Kèm O2b 23,0s và luật cũ (chữ trống 23,0s, không có câu hỏi trong 45s đầu). Mã thoát 1.

### 2. `thumb.py ck-g2-bao-hiem-lien-ket t1 --lint-only`

Lệnh literal trong worktree không thấy mẫu HTML (file chỉ có ở checkout sản xuất), không in gì, mã thoát 0.

Chạy `lint()` của file worktree trên mẫu và `t1.jpg` sản xuất:

```
THUMB LINT: CẢNH BÁO ck-g2-bao-hiem-lien-ket_t1: chữ lớn 8 từ (> 7): nên rút gọn
THUMB LINT: CẢNH BÁO ck-g2-bao-hiem-lien-ket_t1: không có <img> chủ thể
THUMB LINT: LỖI ck-g2-bao-hiem-lien-ket_t1: chữ 'VÍ DỤ GIẢ ĐỊNH' cỡ 34px nhỏ hơn 44px khung 1280 (ngưỡng 66px trên khung 1920)
THUMB LINT: 1 thumbnail lỗi (ck-g2-bao-hiem-lien-ket_t1); sửa mẫu hoặc chạy lại với --allow-thumb nếu cố ý
```

Mã thoát 1. Cảnh báo thiếu ảnh không tự nó chặn; lỗi 34px thì chặn. `--allow-thumb` vẫn bỏ qua lỗi. Chưa dựng `t1_tiny.jpg` vì `--lint-only` không render.

### 3. `build.py --preflight mim-tr-agent-browser cl-tr-calvin-fairbank-1851`

Spec không có trong worktree. Code worktree, spec sản xuất:

```
python motion/stier/build.py --preflight mim-tr-agent-browser cl-tr-calvin-fairbank-1851 --root "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2"
```

```
mim-tr-agent-browser: OK — 109 từ, ước lượng 33.0s
cl-tr-calvin-fairbank-1851: OK — 114 từ, ước lượng 34.5s
```

Mã thoát 0. Câu 1 của hai bài đều dưới 14 từ, câu 2 không phải câu định nghĩa. Tiêu đề MIM có "AI" và kết thúc bằng hỏi nên không bị coi là câu hỏi trừu tượng; tiêu đề CL không kết thúc bằng `?` và có số 47. Không có dòng `CẢNH BÁO` mới.
