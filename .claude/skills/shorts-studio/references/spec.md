# Spec JSON (một short)

```json
{
  "id": "fs_2027_sinhcon",              // duy nhất; job ở hyperframes_short/jobs/<id>/
  "channel": "fs",                      // sổ đa dạng: output/cl_staging/<channel>/studio_ledger.json
  "theme": "tet-poster",                // studio/themes/<theme>.json
  "kicker": "SINH CON NĂM 2027",        // nhãn mono góc trên
  "foot": "Kiến thức truyền thống · để tham khảo",
  "lines": ["Con sinh năm **2027** đều mệnh **Thiên Hà Thủy**.", "..."],   // **x** = từ nhấn (màu accent + phụ đề)
  "tts": true, "voice_series": "fs",    // hoặc "voice": {"wav": "...wav", "manifest": "...json (segments)"}
  "scenes": [ { "device": "hook_poster", "line": 0, "...": "..." }, { "device": "split", "line": 1, "seam": "zoom", "...": "..." } ],
  "loop": true,                         // móc quay lại ở 0,45s cuối (khung cuối ~ khung đầu)
  "seam": "curve",                      // ghi đè seam mặc định của theme
  "capGroup": 5,                        // số từ mỗi cụm phụ đề
  "tail": 1.4,                          // giây sau câu cuối
  "out": "output/cl_staging/fs/out/fs_2027_sinhcon.mp4",
  "credits": ["Ảnh: ... — Pexels (...)"]
}
```

## Cảnh
- `device` (bắt buộc), `line` = câu mà cảnh bắt đầu (cảnh kéo tới khi cảnh sau bắt đầu, -0,12s), `seam` (curve | side | zoom | inv | blur | hard),
  `ghost` = chữ nền mờ khổng lồ của cảnh (""= không).
- Trường riêng từng thiết bị: `references/devices.md`.

## Mốc thời gian (anchor)
Mọi khoá kết thúc bằng `at`/`At` và các mảng như `flips` nhận:
- `[câu, "từ"]` hoặc `[câu, "từ", lần]`: thời điểm từ đó được đọc (hf_align bám năng lượng âm thanh thật). So khớp tiền tố, bỏ dấu câu, giữ dấu tiếng Việt.
- `[câu, 0.5]`: tỉ lệ trong câu (số thực). `số` = giây tuyệt đối.
- Không thấy từ -> **build dừng** và báo câu/từ (không âm thầm rơi về đầu câu).

## Đầu ra của build
`jobs/<id>/index.html` (engine inline + phiên bản), `plan.json` (cửa sổ cảnh, cảnh báo đa dạng), `qa.json`, `qa_sheet.jpg`,
mp4 + `.render.json` (theme, engine, bgm, ghi nguồn) ở `out`.
