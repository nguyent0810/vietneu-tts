---
{
  "id": "word_highlight",
  "ten": "Tô sáng từ đang đọc",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "tra_cuu",
    "van_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 24,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_fs_tables_1013.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/grok/build_fs2027.py",
    "output/cl_staging/grok/build_r1026.py",
    "output/cl_staging/grok/build_r1027.py"
  ],
  "vi_du": [
    "https://x.com/hahazwei/status/2104809910152425483",
    "https://x.com/leploutos/status/2106728230707159472"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/review_yeartable.html",
    "hyperframes_short/studio/core.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Một từ trong câu đổi màu đúng mốc voice, phần còn lại giữ nguyên; review_yeartable đọc từ `word`/`at`.

## Khi nào dùng

Short nhấn tên hạn/khái niệm; Long nhấn thuật ngữ có timing chính xác. Không nên dùng: Từ đang đổi nghĩa theo ngữ cảnh hoặc đoạn thoại dồn từ.

## Cách dựng trong HyperFrames

Nhánh dựng cho word highlight nằm tại `hyperframes_short/compositions/longform.js:1083`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/studio/core.js:1`.

visual type `word`; chỉ rõ `word`, `at`, `color` và thời lượng nhấn theo câu.

## Rủi ro

Timing word sai làm màu nhấn chạy trước tiếng; clip cắt dấu tiếng Việt từng có ở 3/10.
