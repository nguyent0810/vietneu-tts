# GH-170: hợp đồng đầu ra Long (builder ghi, consumer đọc)

Phạm vi: `motion/long/build_long.py` (render chương, final, cache TTS), `srt.py`, và các consumer. Short (`motion/stier`) ngoài phạm vi (#145). Không upload, không đổi lịch.

## 1. Nguyên tắc

1. **Công bố bằng một bước nguyên tử.** Builder ghi vào file tạm cùng thư mục (`.<tên>-<uuid>.<đuôi>`), kiểm hợp lệ, rồi mới `os.replace` sang tên cuối. Không bao giờ ghi thẳng vào tên cuối.
2. **Key / manifest chỉ ghi sau artifact.** Key bị xoá TRƯỚC khi thử ghi artifact; chỉ ghi lại sau khi `os.replace` artifact thành công. Crash ở đâu thì trạng thái còn lại là "không có key" = không cache hit.
3. **Một lượt final có manifest** `final.run.json`: `running` ghi trước khi đụng bất cứ thứ gì, `ok` chỉ ghi ở bước cuối, `failed` ghi khi bắt được lỗi. Tiến trình bị giết giữa chừng để lại `running`.
4. **Consumer fail closed.** Có manifest mà không phải `ok` (hoặc `ok` nhưng file không khớp) thì consumer từ chối, dù `final.mp4` cũ vẫn nằm đó.
5. **Lỗi khoá file trên Windows** (`PermissionError`/`OSError` ở `os.replace`) là lỗi rõ (`SystemExit` nêu file và nói bản cũ giữ nguyên), không im lặng, không công bố key.
6. Không xoá bản tốt vì một lượt thất bại. Chỉ xoá file tạm của chính lượt đó.

## 2. Artifact

### 2.1 Cache TTS: `output/long/<topic>/tts/<key>.wav`
- **Ghi:** `build_long.tts_line` (qua `tts`, `takes`). Key = `sha1(voice|text|take)[:16]`.
- **Đọc:** `speak` (tạo `voice.wav`), `do_takes`, `do_pick`/`stt_takes.py` (qua `takes.json`).
- **Cache hit** = file tồn tại VÀ `long_output.wav_complete` (header RIFF khớp kích thước thật, data > 0) VÀ giải mã được, không rỗng, hữu hạn. Không dựa mtime.
- **Công bố:** `sf.write` vào file tạm, kiểm lại (số mẫu = số mẫu engine trả về, đúng tần số, hữu hạn) rồi `os.replace`. Thất bại: file tạm bị xoá, không có `<key>.wav`.
- File cache cũ bị cắt dở (crash của code cũ) bị coi là miss và đọc lại. Cache đầy đủ cũ giữ nguyên byte, không đổi.
- `takes.json`, `picks.json`: ghi nguyên tử (consumer đọc JSON; file cắt dở sẽ báo lỗi thay vì dùng nhầm).

### 2.2 Render chương: `output/long/<topic>/<chNN>/silent.mp4` + `silent.key` (nháp: `draft.mp4` + `draft.key`)
- **Ghi:** `build_long.do_render`, trong `render_lock`.
- **Đọc:** `do_render` (cache hit), `_do_final_locked` (kiểm trước khi ghép), `srt.py` (độ dài chương; từ nay kiểm hợp lệ), `brand_sting.py`/`freeze_check.py` (chỉ soi, không đưa vào sản phẩm: chưa kiểm key, xem mục 6).
- **Hợp lệ** = `silent.mp4` là file có luồng hình, độ dài khớp `dur` trong `data.js` (±0,1 s) VÀ `silent.key` == `render_key()` hiện tại.
- **Cache hit** = hợp lệ (cả ba điều kiện), không chỉ "file + key tồn tại".
- **Một lượt render:** xoá key cũ → render vào file tạm → kiểm có hình + độ dài → `os.replace` video → ghi key (tạm + replace). Mọi nhánh lỗi (ffmpeg/renderer lỗi, file rỗng, sai độ dài, replace bị khoá, crash) để lại video cũ nguyên vẹn nhưng KHÔNG có key → lần sau không cache hit và `final`/`srt` từ chối chương này.
- `draft_av.mp4` (nháp có tiếng): ffmpeg ghi file tạm rồi replace, ffmpeg lỗi thì báo lỗi.

### 2.3 Final: `final.mp4`, `captions.vi.srt`, `final.commit`, `final.run.json`, (`qa_ok` do `scripts/qa_mark.py`)
- **Ghi:** `build_long.do_final` (cũng là cửa mà `make_video` của #159 phải gọi, không tự ghép), `srt.py --out`, `qa_mark.py` (qa_ok).
- **Đọc:** `publish_long.py` (preflight, đăng, đăng thủ công/đẩy vào kho), `qa_mark.py`, `qa_blank.py`, các chuỗi `run_chain` (`[ -f final.mp4 ]`), `factory/manual.py` (xuất gói, qua bản sao trong kho).
- **Manifest** `final.run.json`: `run_id`, `state` (`running|ok|failed`), `started_at`, `finished_at`, `error`, `final {size, sha256}`, `captions {size, sha256}`, `chapters {name: key}`.
- **Hợp lệ** (`long_output.final_problems(od)` rỗng) = manifest `ok` VÀ `final.mp4`, `captions.vi.srt` tồn tại với kích thước khớp manifest (publish kiểm cả sha256).
- **Không manifest = legacy:** final dựng trước GH-170 vẫn được chấp nhận (không thể chứng minh ngược). Vì mọi lượt `final` mới ghi `running` trước tiên, một lượt mới thất bại luôn để lại manifest không `ok`; chỉ lượt chưa từng chạy mới là legacy.
- **Một lượt final:** (1) cổng branch + soát ảnh/clip (từ chối trước khi bắt đầu thì chưa động manifest) → (2) manifest `running` → (3) cổng floor/craft/variety, kiểm từng chương hợp lệ (2.2) → (4) ghép vào `.final-<uuid>.mp4`, audio gate (`check_parts`, buzz, `check_final` trên file tạm) → (5) `srt.py --out` file tạm, kiểm không rỗng → (6) `os.replace` final, rồi captions → (7) `final.commit` (nguyên tử) → (8) manifest `ok` + sha256.
- **Thất bại ở bước 3 đến 7:** manifest `failed` với lý do; `final.mp4`/`captions.vi.srt`/`final.commit` cũ nằm nguyên (không xoá, không ghi đè), file tạm bị dọn. Consumer thấy manifest `failed` và dừng.
- **Giết tiến trình** giữa chừng: manifest `running`, consumer dừng.
- **Lỗi khoá ở bước 6/7:** `SystemExit` nêu file bị khoá, manifest `failed`.
- **Phục hồi:** chạy lại `final`. (Không có lệnh "đánh dấu bản cũ là ok" vì không được tin một final không do lượt ok tạo ra.)

### 2.4 Trung gian (không phải sản phẩm, không consumer ngoài build_long)
`concat.txt`, `concat_a.txt`, `<ch>/mixpad.wav`: ghi lại mỗi lượt final, nằm trong lượt có manifest. `<ch>/mix.wav`, `voice.wav`, `sfx.wav`, `data.js`: do `html`/`tts` ghi trực tiếp; xem mục 6.

## 3. Cache hit, tóm tắt

| Artifact | Cache hit khi |
|---|---|
| TTS wav | tồn tại + header nhất quán + giải mã được + không rỗng/hữu hạn |
| silent.mp4 | tồn tại + có hình + khớp `dur` data.js + `silent.key` == `render_key` hiện tại, và `--force` luôn bỏ qua |
| final | không có "cache hit": mỗi lượt `final` chạy lại; hợp lệ = manifest `ok` + file khớp |

## 4. Consumer phải làm gì

- `publish_long.py`: trước mọi đăng/đưa vào kho khi chưa có `video_id`, gọi `final_problems(od, full=True)`; có lỗi thì dừng, chưa upload gì.
- `scripts/qa_mark.py`: từ chối đánh dấu QA nếu `final_problems` có lỗi.
- `srt.py`: từ chối nếu chương không hợp lệ (2.2); ghi atomic.
- Chuỗi shell: kiểm `python motion/long/long_output.py check <topic>` (mã thoát 0 mới đi tiếp); `run_chain.py` cảnh báo chuỗi chỉ dựa `[ -f final.mp4 ]`.
- `make_video` (#159): chỉ gọi `build_long.do_final`/`do_render`, không đọc `final.mp4` nếu `final_problems` khác rỗng.

## 5. Giả định chưa xác minh

1. `os.replace` cùng thư mục là nguyên tử trên NTFS (đúng theo tài liệu Win32 `MoveFileEx` với `REPLACE_EXISTING`, chưa kiểm trên ổ/junction thật của máy sản xuất; `output/` là junction sang `Youtube_Creator_V2/`).
2. `os.replace` lên file đang mở (trình phát, antivirus quét) trên Windows ném `PermissionError`; chỉ giả lập bằng mock, chưa thử khoá thật.
3. `hyperframes render -o <tên-ẩn>.mp4` ghi đúng đường dẫn tạm đó (không tự đổi tên); tên tạm KHÔNG được tạo sẵn để tránh renderer từ chối ghi đè.
4. Tên tạm bắt đầu bằng dấu chấm không bị công cụ nào quét (`glob("*.mp4")` của pathlib vẫn khớp file ẩn). Đã tìm: không consumer nào glob `*.mp4`/`*.wav` trong thư mục chương/tts ngoài `freeze_check` (`ch*/silent.mp4`, không khớp tên tạm).
5. Mất điện/crash HĐH sau `os.replace` mà trước khi flush: không `fsync`, chưa đảm bảo bền vững.
6. libsndfile ghi header WAV ở lúc đóng file; header `data` bằng 0 hoặc dài hơn file được coi là dở (đúng với soundfile PCM_16 mặc định).

## 6. Ngoài phạm vi, cần lead quyết

- `voice.wav`, `mix.wav`, `sfx.wav`, `data.js` do `tts`/`html` ghi thẳng (đầu vào của render/final, chưa nguyên tử). `render_key` băm `data.js` nên đổi data.js làm key đổi; `mix.wav` cũ/dở có thể vào final. Nên làm ở ticket riêng.
- `brand_sting.py` ghi thẳng `silent.mp4`; `freeze_check.py` đọc `ch*/silent.mp4` không kiểm key (chỉ soi).
- Short (`motion/stier/build.py`, `enqueue_mim.py`, `enqueue_ck.py`, `upload_one.py`) cũng đọc `final.mp4` kiểu "tồn tại": thuộc #145.
- Final legacy không manifest vẫn được đăng (không thể chứng minh). Lead/chủ kênh có thể chọn chặn cả legacy; hiện chọn không chặn để khỏi gãy 19 final CK đang chờ.

## 7. Lỗ hổng của bản vá dở (trước khi làm theo hợp đồng)

1. `final.mp4` vẫn ghi thẳng bằng ffmpeg `-y` vào tên cuối: ffmpeg bị giết để lại file dở; lỗi `check_final` hay ngoại lệ thì `unlink` mất cả bản tốt cũ.
2. `__main__ final` xoá `final.mp4` cũ trước (mất bản tốt; ngược tiêu chí). `do_final` gọi trực tiếp (`make_video`) thì không xoá và không có trạng thái: lỗi phụ đề hoặc audio gate còn nguyên `final.mp4`, `captions.vi.srt`, `final.commit` cũ mà không dấu hiệu lượt mới thất bại, tức là fail open.
3. `srt.py` ghi `captions.vi.srt` thẳng; lỗi hoặc crash để final mới đi kèm SRT cũ/dở. Chạy lẻ `srt.py` không kiểm chương hợp lệ.
4. `final.commit` ghi không nguyên tử và không bị vô hiệu khi lượt mới thất bại.
5. Không consumer nào kiểm trạng thái: `publish_long.preflight` chỉ `exists()`, `qa_mark` băm file bất kỳ (và `qa_ok` mới có cũng không kiểm lượt).
6. `os.replace` bị khoá ném `PermissionError` thô; key được ghi sau video nhưng lỗi ở bước key để video mới + không key mà không báo rõ.
7. `draft_av.mp4` và `takes.json`/`picks.json` ghi thẳng; ffmpeg tạo `draft_av` không kiểm mã thoát.
8. TTS: kiểm hợp lệ file đã có chỉ là "không rỗng, tần số, hữu hạn" nên WAV bị cắt dở (header đúng, ít dữ liệu) vẫn được giải mã và dùng; file ghi tạm dùng `mkstemp` (tạo sẵn); import `factory.speak` đã bị chuyển lên đường cache-hit (rủi ro phụ thuộc môi trường).
9. File tạm mồ côi (kill -9) không bao giờ được dọn.
10. Test nằm ở `tests/` gốc repo thay vì `creator_v2/tests/`, nên không chạy cùng bộ test của creator_v2.

## 8. Bổ sung sau review độc lập

- **Hợp lệ của final có thêm điều kiện chương:** `final_problems` so `chapters` trong manifest với `silent.key` hiện tại của từng chương. Chương render lại hoặc đổi sau lượt final (key khác, hoặc key bị xoá) thì final bị coi là không hợp lệ. Chỉ so key đã ghi, không tính lại `render_key` (đắt, và phụ thuộc engine hiện tại).
- **Dọn file tạm:** `sweep_temps(dst)` khớp đúng mẫu `temp_path(dst)` (kể cả tạm-của-tạm `..`), áp dụng cho `silent.mp4`, `silent.key`, `draft_av.mp4`, `final.mp4`, `captions.vi.srt`, `final.run.json` và wav TTS, luôn trong lúc giữ khoá.
- **Chạy tay `srt.py` làm manifest lệch:** manifest ghi kích thước và sha256 của `captions.vi.srt`. Chạy tay `srt.py` (ghi đè phụ đề) làm file khác manifest nên consumer (publish đo sha256) sẽ từ chối; phải chạy lại `build_long.py <topic> final`. Đây là chủ ý: không có phụ đề "ngoài lượt".
- **Throughput:** `render_lock` (khoá cả máy) được giữ suốt `do_final` (ghép, đo audio, srt, sha256 file lớn). Trong lúc đó mọi render khác phải chờ. Chấp nhận để final không bị chen; nếu thành nút cổ chai thì tách phần băm sha256 ra ngoài khoá.
- **Consumer ngoài phạm vi, vẫn đọc `final.mp4` mà không qua manifest:** `scripts/qa_blank.py`, `scripts/freeze_check.py` (đọc `ch*/silent.mp4`), `scripts/cleanup_published.py`, các chuỗi shell chỉ kiểm `[ -f final.mp4 ]` (`run_chain` mới chỉ cảnh báo). Kết quả QA của chúng trên một final của lượt failed không có giá trị.
- **Ghi không nguyên tử còn lại:** `voice.wav`, `mix.wav`, `sfx.wav`, `data.js` (do `tts`/`html` ghi). Đề xuất ticket riêng.

## 9. Đo rủi ro render lại hàng loạt (chỉ đọc, 05/11/2026)

Phạm vi: mọi thư mục chương có `silent.mp4` trong output Long sản xuất (170 chương, 21 topic, bỏ thư mục `_*`). Không ghi gì.

| Phép kiểm | Kết quả |
|---|---|
| `_chapter_duration_ok` (dur trong `data.js` so với ffprobe, ngưỡng 0,1 s; luồng hình) | **0/170 trượt**: ngưỡng 0,1 s không quá chặt, không có data.js sai dạng |
| Chương có `silent.key` | 170/170 |
| `silent.key == render_key` hiện tại (tính với engine/composition của repo V2 cũ, là nơi các composition Long còn nằm) | **9/170 khớp, 161/170 lệch** |

Nguyên nhân lệch: không phải lỗi, đó là invalidation đúng của `render_key`. `casewide.js/css` sửa 28/10, `chart.js` 27/10 và các theme/engine khác sau khi phần lớn chương được render (22 đến 23/10); `ck-a2` còn có data.js/composition ghi lại sau lần render. Chỉ `mim-jobs-1985` (render 29/10) khớp 9/9. Một vài file engine (`beat2.*`, `bud-chiemnghiem.css`, `ck-bang-tra-ab.css`, `theme-bud.css`) chưa có trong `motion/hf/assets/engine` của repo mới, nên với Long dùng beat2 thì `render_key` hiện không tính được ở repo mới (báo "cần render lại").

Hệ quả cần lead quyết: **`final` mới từ chối các Long cũ này nếu chương đã render trước 28/10** (cần render lại 161 chương), trong khi `final` cũ chấp nhận. Với video chưa đăng và cần dựng lại final, `render` (không `--force`) sẽ render lại các chương lệch, đúng như trước GH-170; điều mới là `final` không còn ghép chương đã lệch. Không đề xuất đổi ngưỡng 0,1 s (không liên quan). Nếu muốn giữ khả năng dựng lại final cho video cũ mà không render lại, phải có lệnh tường minh kiểu `final --accept-existing-chapters` do chủ kênh duyệt (chưa làm).
