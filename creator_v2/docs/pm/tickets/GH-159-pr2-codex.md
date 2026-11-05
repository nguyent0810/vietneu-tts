# GH-159 · PR 2 (Codex): Long creator_v2 đọc bảng kênh từ hồ sơ `library/channels`

Issue: https://github.com/nguyent0810/vietneu-tts/issues/159.

Thiết kế đã được chủ kênh duyệt: `creator_v2/docs/pm/2026-11-05-thiet-ke-mot-workflow.md`, mục 5, dòng PR 2. PR 1 (#165) đã merge, nên `library/tools/channel_profile.py` cùng các file `mim.yaml`, `ck.yaml`, `cl.yaml` đã có trên main.

Bạn làm ở **gốc repo**, tức worktree này. Nhánh: `mimck/159-pr2-creator-doc-ho-so`.

**Hạn:** 90 phút.

## Mục tiêu
Bảng kênh hard-code trong code Long của creator_v2 chuyển sang đọc từ hồ sơ kênh. Bỏ việc spec thiếu kênh tự thành "CL".

**Đầu ra dựng phải giống hệt trước.** Không đổi giọng, theme, màu, ngưỡng, hay bất kỳ giá trị nào.

## Việc

### 1. `creator_v2/motion/long/build_long.py`
- **`_channels()` (dòng 106–116):** dựng bảng từ hồ sơ qua `channel_profile.load()`. Kết quả phải **bằng đúng** bảng cũ, theo từng khoá, cho `CL`, `MIM`, `CK`. Ánh xạ:

  | Khoá bảng cũ | Lấy từ hồ sơ |
  |---|---|
  | `voice` | `voice_profile.tham_so.dan` |
  | `quote` | `voice_profile.tham_so.trich` |
  | `ask` | `voice_profile.tham_so.hoi` (chỉ khi có) |
  | `theme` | `theme.long` (chỉ khi bảng cũ có khoá này) |
  | `brand` | `theme.brand` |
  | `accent` | `typography.mau_nhan` |
  | `pools` | `themes.THEMES[<tên>]["pools"]`, với `<tên>` là khoá mới `theme.pools` trong hồ sơ (MIM và CK đều là `"mim"`) |
  | `no_sa` | `anh.cam_sa` |
  | `voice_fx` | `getattr(themes, voice_profile.tham_so.fx)` |

- **Dữ liệu hồ sơ đang khác code thì sửa hồ sơ cho khớp code, không sửa code:**
  - `cl.yaml` có `theme.long = "case"`, nhưng bảng cũ của CL **không có** `theme`. Hiện `THEME["name"]` của CL là `""` (dòng 180). Bỏ `theme.long` khỏi `cl.yaml`, hoặc để `""`. Ghi rõ đã chọn cách nào.
  - `cl.yaml` có `typography.mau_nhan = "#e2402d"`, nhưng bảng cũ của CL không có `accent`; giá trị này chỉ là fallback ở dòng 1091. Hoặc không đưa `accent` vào bảng CL, hoặc chứng minh giá trị hiệu lực vẫn y hệt. Chọn cách nào để bảng **bằng đúng** bảng cũ.
  - Thêm `"pools": "mim"` vào `theme` của `mim.yaml` và `ck.yaml`.
- **Nhận biết kênh:**
  - Thay `spec.get("channel", "CL")` ở các dòng 178, 980, 1284, 1340, và mọi chỗ tương tự, bằng một kênh lấy **một lần** qua `channel_profile.resolve({"channel": spec.get("channel")})`. Đổi sang mã viết hoa `CL`/`MIM`/`CK` cho các hàm đang dùng dạng đó, ví dụ `floor.problems`.
  - Thiếu kênh thì **báo lỗi rõ**, không mặc định CL.
- **9 spec Long CL không có trường `channel`:** `bulger`, `capone`, `escobar`, `golden`, `kowloon`, `mafia`, `ripper`, `shanghai`, `yakuza` (`data/long/<topic>/spec.json`). Thêm `"channel": "CL"` vào mỗi file, giữ nguyên mọi khoá khác. Đây là thay đổi dữ liệu, không làm đổi đầu ra dựng.
  - Xong thì kiểm: mọi `data/long/*/spec.json` đều resolve được kênh.

### 2. `creator_v2/motion/variety.py:35`
`CHANNEL_THEME = {"MIM": "lab", "CK": "chart"}` → dựng từ hồ sơ: kênh nào có `theme.long` thì lấy giá trị đó. Kết quả phải bằng đúng dict cũ.

### 3. Không đụng trong PR này
- `motion/stier/themes.py`: Short tra theme theo tên theme, không theo kênh; làm ở PR sau.
- Ngưỡng `floor.py`.
- `factory/channels.py`.
- Engine JS.

### 4. Import
creator_v2 hiện không import gì từ `library/`. Thêm một helper nhỏ, ví dụ `creator_v2/motion/channel_table.py`, nạp `channel_profile` theo đường dẫn tương đối tới gốc repo.
- Không dựa vào biến môi trường hay đường dẫn tuyệt đối.
- Chạy được từ thư mục `creator_v2/`, đúng như các lệnh sản xuất hiện nay.

### 5. Test, trong `creator_v2/tests/`
- **Snapshot:** chép nguyên văn bảng `_channels()` cũ vào test, có chú thích ngày và commit gốc. Bảng mới phải `==` bảng cũ, với `themes` được import thật.
- `variety.CHANNEL_THEME` bằng dict cũ.
- Mọi `data/long/*/spec.json` resolve được kênh. Một spec giả thiếu `channel` phải ra `ValueError` hoặc `SystemExit`.
- Lệnh chạy:
  - `python -m pytest creator_v2/tests -q -p no:cacheprovider`;
  - `python -m pytest tests/test_channel_profile.py -q -p no:cacheprovider`.

  Test nào lỗi vì môi trường Windows sandbox (`PermissionError` thư mục tạm, `fcntl`) thì ghi tên vào báo cáo. Không tắt test.

## Được ghi
- `creator_v2/motion/long/build_long.py`, `creator_v2/motion/variety.py`, helper mới trong `creator_v2/motion/`.
- `library/channels/mim.yaml`, `ck.yaml`, `cl.yaml`: chỉ các chỉnh sửa nêu ở mục 1.
- 9 file `creator_v2/data/long/<topic>/spec.json`: chỉ thêm `channel`.
- Test mới trong `creator_v2/tests/`.
- Báo cáo: `creator_v2/docs/pm/tickets/GH-159-pr2-codex-report.md`.

**Không:**
- render, TTS;
- upload, đổi lịch;
- commit;
- đọc credentials.

## Báo cáo
- File đã đổi, kèm một dòng mô tả mỗi file.
- Kết quả pytest (dòng tổng) và danh sách test lỗi do môi trường.
- Cách đã xử lý `theme`/`accent` của CL.
- `git grep -n 'get("channel", "CL")'` sau khi sửa: phải còn 0 kết quả trong `creator_v2/motion/long/`.

Câu trả lời cuối: tối đa 3 dòng.
