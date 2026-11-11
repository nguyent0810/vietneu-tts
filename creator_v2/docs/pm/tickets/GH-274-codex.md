# GH-274 + GH-275 + GH-280: Long MIM/CK/CL tự gắn chuyển động máy quay, mặc định cho Long mới, mức nhạc nền (Codex, lần 3)

Đọc issue #274, #275 và #280 (`gh issue view <số> --repo nguyent0810/vietneu-tts`).

## ĐỪNG DỪNG SỚM
Lần 2 bạn dừng sau 2 phút vì pytest lỗi quyền thư mục tạm. **Lỗi môi trường test không phải lý do để dừng.**
- Lead đã chạy bộ test gốc ngoài sandbox: **7 failed, 1133 passed, 20 skipped.** 7 test đỏ đều do thiếu module `vnlunar` (test_claims, test_lines, test_pillars), không liên quan việc này.
- Bạn **chỉ cần chạy các test mới và test liên quan**: `-k "cine or long_defaults or mix_level or long"`, với `--basetemp=tmp_pytest -p no:cacheprovider`. Lỗi quyền lúc dọn thư mục tạm thì cứ ghi lại vào báo cáo. Test mới nên tránh `tmp_path` khi có thể (dùng dữ liệu trong bộ nhớ). Lead sẽ chạy lại toàn bộ ngoài sandbox.
- **Phải triển khai đầy đủ cả ba việc.** Báo cáo "chưa hoàn tất" mà không có code tính là hỏng.

## Việc #280 (âm thanh), làm sau #274/#275
Chi tiết trong issue #280.
- Trong `build_long.py` (`mix_chapter`): tham số hoá mức trộn theo kênh. Mặc định cho Long mới: nhạc nền gain 0.17, nén theo giọng threshold 0.05, ratio 4; ambience +15 dB. Topic legacy giữ nguyên mức cũ.
- Nhạc tự to lên ở thẻ chương và ở khoảng lặng dài ≥ 1,2 giây.
- Thêm cổng đo mức nhạc nền so với giọng sau bước `mix`: nhỏ hơn giọng quá 18 dB thì chặn `final`.

## Môi trường
- **Worktree:** `D:\Tools\Youtube Creator v2\wt-cine`, nhánh `feat/274-long-cine-auto`. Chỉ sửa trong worktree này, không đụng `vietneu-main`.
- **Python:** `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- **Dữ liệu thật (chỉ đọc):** `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\data\long\mata-hari\`. Chạy thử thì chép sang `creator_v2/tmp_dry/` trong worktree.
- **Pytest:** chạy với `--basetemp=tmp_pytest -p no:cacheprovider` (thư mục trong worktree). Sandbox không ghi được vào Temp của user; 419 lỗi setup lần trước là do chuyện này, không phải do code.

## File ĐƯỢC SỬA (Lead cho phép đích danh, ngoại lệ luật AGENTS.md)
- `creator_v2/motion/hf/assets/engine/casewide.js`
- `creator_v2/motion/hf/assets/engine/casewide.css`
- `creator_v2/motion/long/scene_params.py`
- `creator_v2/motion/long/build_long.py`
- `creator_v2/motion/long/floor.py`
- `creator_v2/motion/long/cadence.py` (chỉ khi cần đếm thêm)
- `creator_v2/motion/long/README.md`
- File mới:
  - `creator_v2/motion/long/cine_auto.py`
  - `creator_v2/data/long/_legacy_topics.json`
  - `creator_v2/tests/test_cine_auto.py`
  - `creator_v2/tests/test_long_defaults.py`

Không sửa file nào khác.

## Việc #274 (đã chỉnh theo phát hiện của bạn)
1. **Engine:** cho `cam` (push_in, pull_out, dolly, pan, tilt_up) chạy được trên `print` và `split`, không chỉ `photo`/`pano`. Với `broll` (video) chỉ thêm push_in/pull_out thật chậm (scale ≤ 1.06), và tắt mặc định nếu clip đã có chuyển động mạnh: để trống, chỉ bật khi được gán.
2. **`cine_auto.py`:** gán tự động cho Long mới (spec có `"cine_auto": true`; Long mới bật mặc định theo #275).
   - **Phân bổ:**
     - khoảng 65% cảnh `photo`/`print`/`split` có `cam`;
     - khoảng 15% có `fx` (fog, mist_drift, god_rays, dust, embers, rain, candle_flicker, snow_ash), **theo bối cảnh**, ví dụ mưa hoặc nến chỉ khi lời đọc hay nhãn có từ liên quan, hoặc khi spec có `ambience` tương ứng;
     - `transition_in` xoay vòng.
   - **Ảnh rộng:** tỉ lệ ≥ 2:1 và đủ 2 điểm neo thì thành `pano`, trong sàn pano hiện có.
   - **Chống nhàm:**
     - không hai `cam` giống nhau liền nhau;
     - mỗi 2 phút có ít nhất 3 kiểu;
     - 120 giây đầu không đóng khung ảnh.
   - **Cảnh chữ** (`kinetic`, `slam`, `question`) đã có `bg`: thêm `cam` chậm (push_in hoặc pan nhẹ) cho nền, để nền không đứng yên. Không đổi độ tối.
   - **Cảnh ghi tay** `cam`, `fx`, `layout`, `transition_in` thì giữ nguyên. Tất định theo seed, không random.
3. `build_long.py html` gọi `cine_auto`, rồi in bảng phân bố: % `cam` theo kiểu, % `fx`, % `pano`, chuỗi lặp dài nhất.
4. `floor.py`: **cảnh báo** (chưa chặn) khi Long `cine_auto` có `cam` dưới 50% số ảnh.

## Việc #275
- `data/long/_legacy_topics.json`: liệt kê **mọi thư mục topic đang có** trong `data/long/` của bản sản xuất hôm nay. Topic cũ giữ nguyên hành vi.
- Topic **không có trong danh sách**, tức Long mới:
  - `build_long.py` tự điền mặc định khi spec thiếu: `opening_gate: true`, `cine_auto: true`, `idcards: true` (khoá cho #276, hiện chưa dùng), `voice2` (giọng câu trích theo kênh; đọc cách Mata Hari khai), `ambience`. Bảng mặc định theo kênh: CL theo bối cảnh, MIM nhẹ hoặc tắt, CK tắt.
  - Chặn `html`/`render` khi `opening_gate` bị tắt mà không có `--allow-opening`.
- README: bảng mặc định theo kênh.

## Kiểm (bắt buộc)
- Pytest toàn bộ (với cờ ở trên). Ghi số pass/fail **trước và sau**. Test mới phải xanh. Test đỏ có sẵn từ trước thì liệt kê, không sửa.
- Chạy khô `cine_auto` trên bản sao Mata Hari, bật `cine_auto`, in bảng trước/sau. Đạt khi:
  - ≥ 60% cảnh `photo`/`print`/`split` có `cam`;
  - không có `cam` lặp liền nhau;
  - ≥ 3 kiểu `cam` trong mỗi cửa sổ 2 phút.
- Chứng minh topic cũ (ví dụ `mata-hari`, nằm trong legacy) **không đổi** khi chạy `html` mà không bật cờ: test so data trước và sau.

## Báo cáo (TIẾNG VIỆT CÓ DẤU)
- Ghi `docs/pm/tickets/GH-274-report.md` **bằng Python**: `Path(...).write_text(text, encoding="utf-8")`. Không dùng PowerShell `>`/`Set-Content`. Lần trước báo cáo bị `?` thay chữ có dấu.
- Sau khi ghi, đọc lại file bằng Python và kiểm không có chuỗi `"?n"`, `"?c"`.
- Nội dung báo cáo:
  - diff tóm tắt theo file;
  - bảng Mata Hari trước/sau;
  - kết quả pytest trước/sau;
  - lệnh render thử 1 chương, để Lead chạy.

## Ràng buộc
Không render, không commit, không đăng.
