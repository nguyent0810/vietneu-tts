---
{
  "id": "long_video_6_render_soat",
  "ten": "6. Render + soát",
  "loai": "khuon",
  "dinh_dang": [],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    ".claude/skills/long-video/SKILL.md:120"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "``` .venv/bin/python hf_batch_render.py output/cl_staging/long --only <id> --quality looks ``` - Mặc định KHÔNG chạy QA tự động (người dùng tự review video, ưu tiên render nhanh). Chỉ thêm `HF_QA=1` khi viết cảnh/style mới hoặc người dùng yêu cầu. - Độ to đầu ra (ticket 68, 24/10/2026): trộn → đo → tăng tới đích → limiter đỉnh thật −1 dBTP → đo lại. Long −16 LUFS, Short −14 LUFS (`hyperframes_bridge.LOUD_TARGET`). Nhạc nén theo giọng `\"duck_db\"` (mặc định 6), đỉnh tiếng động `\"sfx_peak\"` mặc định .25 (−12 dB so giọng). Bài dễ lấn giọng (`hf_music.MASKS_VOICE`) không vào Long. - Nhạc nền tự đặt dưới giọng 21 dB, xoay pool track; video dài tự render luồng (`HF_CAPTURE_PARALLEL_STREAM`) — không",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/long-video/SKILL.md:120`. ``` .venv/bin/python hf_batch_render.py output/cl_staging/long --only <id> --quality looks ``` - Mặc định KHÔNG chạy QA tự động (người dùng tự review video, ưu tiên render nhanh). Chỉ thêm `HF_QA=1` khi viết cảnh/style mới hoặc người dùng yêu cầu. - Độ to đầu ra (ticket 68, 24/10/2026): trộn → đo → tăng tới đích → limiter đỉnh thật −1 dBTP → đo lại. Long −16 LUFS, Short −14 LUFS (`hyperframes_bridge.LOUD_TARGET`). Nhạc nén theo giọng `"duck_db"` (mặc định 6), đỉnh tiếng động.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
