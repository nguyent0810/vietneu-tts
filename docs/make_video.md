# make_video.py: cửa dựng chung (#159 PR 3)

```
python make_video.py <long|short> <spec | thư mục plan> [--only id] [--channel X] [--slot ISO] [--dry-run]
```

Kênh là dữ liệu: `library/channels/<kênh>.yaml` khoá `dung.<long|short>.engine` chọn renderer. Kênh nhận diện từ `channel`/`kenh` của spec (plan row: `series`), rồi `--channel`, rồi tiền tố slug. Không có mặc định.

| engine | renderer | cwd | ghi chú |
|---|---|---|---|
| casewide (Long MIM/CK) | `motion/long/build_long.py <topic> tts, html, render, final` | `creator_v2/` | spec phải là `creator_v2/data/long/<topic>/spec.json`; sau `final` kiểm `final_problems` (manifest `final.run.json`, sha256), không `ok` thì thoát 1 |
| casefile (Short MIM/CK/CL) | `motion/stier/build.py <slug> --preflight`, rồi `build.py <slug> [--slot ISO]` | `creator_v2/` | preflight lỗi thì không render; spec nằm ở `data/stier/specs/` |
| hf_batch (BUD/FS) | `hf_batch_render.py <thư mục plan> --only <id>` | gốc repo | `--only` bắt buộc, id phải khớp chính xác một row, `lane` khớp loại, `series` khớp kênh |
| studio (VSD Short) | `studio.py build <spec> --render --qa --strict` | gốc repo | spec cần `channel`, `theme` |

- Bước nào thoát khác 0 thì dừng và `make_video` trả đúng mã đó.
- `--dry-run` in kênh, theme, cwd, lệnh; không chạy gì.
- `make_video` không upload. Giọng, media, cổng và đường dẫn output vẫn do renderer cũ quyết định.

## Phạm vi và chuẩn bị trước

- Long creator_v2: `make_video` chỉ chạy **bốn bước cuối** `tts, html, render, final`. Không viết kịch bản, không tìm ảnh/clip, không chạy `takes`/`pick`.
- Việc phải làm trước (make_video kiểm và **chặn ngay, trước TTS**, in lý do; `--dry-run` cũng liệt kê và thoát 1):
  - soát clip: `python motion/long/clip_sheet.py <topic>`, mở tờ soát, rồi `--ok`; soát ảnh: `img_sheet.py` tương tự (dấu `qa_clips.ok`, `qa_imgs.ok` phải khớp cảnh hiện tại);
  - nếu đã có `output/long/<topic>/tts/takes.json` thì phải chạy `build_long.py <topic> pick` (tạo `picks.json`) trước. Chưa chạy `takes` thì `tts` dùng take 0 và không cần `pick`.
- Các cổng khác (floor, lint HTML, nhánh git, variety) vẫn do `build_long.py` chặn ở bước của nó; lỗi sẽ lan ra thành mã thoát khác 0.
- hf_batch: plan phải có `script` thật (rỗng/placeholder bị từ chối vì renderer bỏ qua mà vẫn thoát 0). Nếu `out/<id>.mp4` đã có (và không phải video theo chương), make_video từ chối; truyền `--allow-existing` khi chủ động giữ bản cũ. Sau khi chạy, mp4 phải tồn tại và mới hơn lúc bắt đầu.
- Short creator_v2: `spec.theme` phải bằng `theme.short` của hồ sơ, hoặc nằm trong `theme.short_allowed` (khoá tuỳ chọn của hồ sơ).
- Studio `--qa --strict` thoát khác 0 khi QA lint/check không đạt (sửa trong `studio.py`; không `--strict` thì như cũ).
