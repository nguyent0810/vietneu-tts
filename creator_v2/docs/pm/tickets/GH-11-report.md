# Báo cáo điều tra GH-11 · Cách tạo `final.mp4` của `mim-macintosh-1984`

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/11

---

## 1. Kết luận

**Mức kết luận:** **Đã xác định được, kèm bằng chứng.**

- File `output/long/mim-macintosh-1984/final.mp4` (`2026-10-27 05:33:23`) được tạo bằng **đúng chuỗi lệnh chuẩn của `motion/long/build_long.py`** (`tts` → `html` → `render` → `final`), chạy 2 vòng liên tiếp vào rạng sáng `27/10/2026` (`04:50–05:17` và `05:20–05:33`), sau đó đăng qua `motion/long/publish_long.py` lúc `05:34:22`.
- **Không có hành vi lách cổng** (không sửa tạm `floor.py`/`build_long.py`, không ghép `ffmpeg` ngoài luồng, không render từ repo khác như `wt-studio` hay `vietneu-tts`).
- **Nguyên nhân `build_long.py` và `publish_long.py` không chặn `floor` vào sáng `27/10/2026`:**
  - Commit `e405989` (*"long: production floor so a new Long cannot be worse than the published ones"*, `2026-10-12 14:22:18 +0700`, tác giả `nguyent0810 <tung.hdv@gmail.com>`) được tạo trên nhánh của máy CL và merge vào `origin/main` (qua `308dc51` ngày `16/10` và PR #3 `a7dd500` ngày `19/10`).
  - Trong khi đó, thư mục làm việc hiện tại (`D:\Tools\Youtube Creator v2\Youtube_Creator_V2`, tác giả `nguyen-tung <nguyen-tung@web-life.co.jp>`) đứng trên nhánh local `feat/shorts-mix-standard` (tách khỏi nhánh gốc từ commit `eb34350` ngày `04/10/2026`). Do nhánh local này vô tình commit ~20 GB ảnh chụp render (`motion/hf/_snap_c3` và `_snap_gpu`) nên không push/pull được và **chưa từng merge `origin/main` trong suốt giai đoạn `15/10` đến sáng `28/10/2026`** (lịch sử gốc của nhánh này được giữ tại tag `backup/shorts-mix-local-2026-10-28`).
  - Tại thời điểm dựng `mim-macintosh-1984` (`27/10/2026 04:38–05:34`), `HEAD` của repo local đang ở commit `bc005c7` (`2026-10-23 08:26:35 +0700`), và các thay đổi local giai đoạn 16–28/10 sau đó được gom vào commit `8c76fcc` (`2026-10-28 11:32:22 +0700`).
  - Ở cả `bc005c7` lẫn `8c76fcc`:
    1. File `motion/long/floor.py` **chưa tồn tại** trong working tree (`git ls-tree bc005c7 motion/long/floor.py` và `git ls-tree 8c76fcc motion/long/floor.py` đều trống).
    2. `motion/long/build_long.py` (blob `568c299` tại `bc005c7`, `8966004` tại `8c76fcc`) **chưa có** `import floor`, **chưa có** `_refuse_floor()`, và lệnh `html` không in dòng `floor:`.
    3. `motion/long/publish_long.py` (blob `c30e1a9` tại `bc005c7` và `8c76fcc`) cũng **chưa có** `import floor`.
  - Đến `2026-10-28 11:32:58 +0700` (**hơn 30 giờ sau** khi `mim-macintosh-1984/final.mp4` được tạo), commit merge `2cc389d` (`Merge remote-tracking branch 'origin/main' into feat/shorts-mix-standard`, sau đó squash lên `main` thành `c6d3206` lúc `11:52:32 +0700`) mới đưa `motion/long/floor.py` và `_refuse_floor` từ `origin/main` vào thư mục làm việc này.

---

## 2. Dòng thời gian bằng chứng

### 2.1. Lịch sử Git & Reflog (`git log`, `git reflog`, `backup/shorts-mix-local-2026-10-28`)

| Mốc thời gian (`+0700`) | Commit / Tham chiếu | Bằng chứng |
|---|---|---|
| `2026-10-04 21:28:59` | `eb34350` | `git merge-base 8c76fcc e405989` — điểm chung cuối cùng giữa nhánh local `feat/shorts-mix-standard` và nhánh có `e405989` trước khi merge ngày `28/10`. |
| `2026-10-12 14:22:18` | `e405989` | Tạo `motion/long/floor.py` và thêm `_refuse_floor` vào `motion/long/build_long.py`, `motion/long/publish_long.py` trên nhánh `main` (`nguyent0810 <tung.hdv@gmail.com>`). |
| `2026-10-15 18:39:37` | `838b6b1` | Commit trên `feat/shorts-mix-standard` (`nguyen-tung <nguyen-tung@web-life.co.jp>`). Ngày `16/10`, phiên web `claude/audit-git-state-ok6tlu` (`308dc51`) merge `origin/main` + `838b6b1` trên remote rồi vào PR #3 (`a7dd500`, `19/10`), nhưng repo local không pull bản merge này về mà tiếp tục commit thẳng từ `838b6b1` (`4ffe7df` → `5650616` → … → `bc005c7` → `8c76fcc`). |
| `2026-10-23 08:26:35` | `bc005c7` | `HEAD@{2026-10-23 08:26:35 +0700}` trong `git reflog` — `HEAD` của repo local trong suốt ngày `26–27/10/2026`. `motion/long/build_long.py` ở blob `568c299`: `do_render` và `do_final` không gọi `_refuse_floor`. |
| `2026-10-28 11:32:22` | `8c76fcc` | `HEAD@{2026-10-28 11:32:22 +0700}`: gom toàn bộ công việc MIM/CK từ `16–28/10` trên nhánh local `feat/shorts-mix-standard`. Kiểm bằng `git ls-tree 8c76fcc motion/long/floor.py` xác nhận vẫn chưa có `floor.py`. |
| `2026-10-28 11:32:58` | `2cc389d` | `HEAD@{2026-10-28 11:32:58 +0700}` (`tag: backup/shorts-mix-local-2026-10-28`): merge `origin/main` (`65ecd81`) vào `feat/shorts-mix-standard`. `git diff 8c76fcc 2cc389d -- motion/long/` xác nhận chính commit merge này mới thêm `motion/long/floor.py` (94 dòng) và thêm `import floor` + `_refuse_floor` vào `build_long.py` (blob `8966004` → `9ec2f7d`) cùng `publish_long.py` (blob `c30e1a9` → `697a35c`). |
| `2026-10-28 11:52:32` | `c6d3206` | Squash nhánh `feat/shorts-mix-standard` (đã bỏ `_snap_*`) lên `main`. |

### 2.2. Dòng thời gian file và log của `mim-macintosh-1984` (ngày `27/10/2026`)

| Giờ (`mtime` 27/10/2026) | Đường dẫn file | Chi tiết bằng chứng |
|---|---|---|
| `04:31:26` – `04:37:26` | `data/long/mim-macintosh-1984/{facts,factcheck,script,ai_prompts}.md` | Các bước nghiên cứu (T6R), kịch bản (T6W1) và prompt ảnh AI (T6W2). |
| `04:38:10` – `04:38:20` | `output/long/mim-macintosh-1984/broll/*.mp4`, `index.json` | Tải 6 clip Pexels (`3592341`, `6803042`, `4962316`, `19205382`, `4450059`, `29542968`). |
| `04:39:49` – `04:44:29` | `output/long/mim-macintosh-1984/tts/*.wav`, `ch00..ch07/{voice.wav,timing.json}` | Chạy `build_long.py mim-macintosh-1984 tts` cho 8 chương (`ch00`..`ch07`) và tải ảnh Commons vào `img/`. |
| `04:45:09` – `04:45:12` | `output/long/mim-macintosh-1984/qa_clips.jpg` | Chạy `clip_sheet.py` ở cuối ticket `T6W2` (Codex dừng tại đây theo `T6W2-ket-qua.md`). |
| `04:50:04` – `04:50:25` | `output/long/mim-macintosh-1984/img/ai/ai_01..05.png`, `img/ai01..05.{jpg,json}` | Tạo và import 5 ảnh AI. |
| `04:50:31` | `output/long/mim-macintosh-1984/html.log` | **Vòng 1 `build_long.py mim-macintosh-1984 html`:** in đủ `ch00`..`ch07` và các dòng `! WARNING`, **không có dòng `  floor:`** ở cuối (chứng minh chạy bằng `build_long.py` bản trước merge `2cc389d`). |
| `05:00:30` – `05:17:02` | `output/long/mim-macintosh-1984/render.log`, `ch02,ch04,ch05,ch07/silent.{mp4,key}` | **Vòng 1 `build_long.py mim-macintosh-1984 render`:** in cảnh báo `diacritics_gallery.py render lab` rồi render đủ 8 chương `ch00`..`ch07` (`140s`–`214s`/chương). |
| `05:17:43` – `05:17:50` | `output/long/mim-macintosh-1984/final.log`, `qa_final_sheet.jpg` | **Vòng 1 `build_long.py mim-macintosh-1984 final`:** in `audio_lint: true peak -1.8 dBTP, -14.2 LUFS` và `final.mp4 10.80 phút`. Sau khi soi `qa_final_sheet.jpg`, phát hiện 2 lỗi (ảnh dọc của Jobs mất đầu và tiêu đề chương `"CHÍN MƯƠI K"`, ghi tại `docs/pm/tickets/2026-10-26-codex-pilot/00-THEO-DOI-LOI-CODEX.md` dòng 101). |
| `05:20:30` | `data/long/mim-macintosh-1984/{gen_scenes.py,spec.json,ch00..ch07.json}` | Sửa `gen_scenes.py` và sinh lại `spec.json`, `ch00.json`..`ch07.json`. |
| `05:20:42` – `05:20:47` | `output/long/mim-macintosh-1984/html2.log`, `ch00..ch07/{data.js,sfx.wav,mix.wav}` | **Vòng 2 `build_long.py mim-macintosh-1984 html`:** dựng lại `data.js` và âm thanh 8 chương; log kết thúc ở `ch07`, không có dòng `  floor:`. |
| `05:23:10` – `05:32:44` | `output/long/mim-macintosh-1984/render2.log`, `ch00,ch01,ch03,ch06/silent.{mp4,key}` | **Vòng 2 `build_long.py mim-macintosh-1984 render`:** render lại 4 chương có đổi hình (`ch00` `05:23:10`, `ch01` `05:26:44`, `ch03` `05:29:49`, `ch06` `05:32:44`); 4 chương `ch02, ch04, ch05, ch07` khớp `silent.key` nên in `không đổi, bỏ qua`. |
| `05:32:56` – `05:33:25` | `output/long/mim-macintosh-1984/{concat.txt,concat_a.txt,final.mp4,final2.log}`, `ch00..ch07/mixpad.wav` | **Vòng 2 `build_long.py mim-macintosh-1984 final`:** tạo `concat.txt` (`05:32:56`), `mixpad.wav` (`05:32:56–05:32:57`), `concat_a.txt` (`05:33:00`), ghép `final.mp4` (`05:33:23`, `115.796.374` bytes) và ghi `final2.log` (`05:33:25`). |
| `05:33:48` – `05:34:24` | `output/long/mim-macintosh-1984/{description.txt,captions.vi.srt,publish.log,pub/result.json}` | Chạy `describe.py`, `srt_long.py` và `publish_long.py` (lên lịch video `OH1RsQ9sSJg` cho `2026-11-30T13:00:00Z`). |

---

## 3. Đề xuất chốt chặn

Sự việc không xuất phát từ việc lách cổng trong code, mà từ **lệch nhánh Git kéo dài (branch drift)** giữa nhánh local `feat/shorts-mix-standard` và `origin/main` (do nhánh local bị kẹt các file `_snap_*` > 100 MB không push/pull được từ 15/10 đến 28/10). Để tránh lặp lại tình trạng chạy bản `build_long.py` / `publish_long.py` thiếu cổng mới trên `origin/main`:

1. **Kiểm tra đồng bộ với `origin/main` trước khi `render` (bản thật) / `final` / `publish`:**
   - Trong `scripts/long_gate.py` hoặc đầu `do_final` / `publish_long.py`, chạy kiểm tra đọc nhẹ `git merge-base --is-ancestor origin/main HEAD`. Nếu nhánh hiện tại chưa chứa `origin/main`, in cảnh báo rõ hoặc chặn `final`/`publish` để tránh dùng bộ cổng cũ.
2. **Chặn commit nhầm thư mục render/snapshot làm kẹt đồng bộ Git:**
   - Giữ quy tắc `.gitignore` cho `motion/hf/_snap_*/` và thêm kiểm tra kích thước file staged (ví dụ chặn file > 50 MB) để nhánh làm việc không bị kẹt push HTTP 500 dẫn tới tách rời khỏi `main` nhiều ngày.
3. **Ghi nhận metadata cổng khi xuất `final.mp4`:**
   - Cùng với `GH-12` (tách ngưỡng sàn nội dung theo kênh `CL` vs `MIM`/`CK` trong `floor.py`), có thể lưu kèm commit hash (`git rev-parse HEAD`) vào file dấu QA (`output/long/<topic>/qa_ok`) để `publish_long.py` biết chính xác `final.mp4` được dựng ở phiên bản cổng nào.
