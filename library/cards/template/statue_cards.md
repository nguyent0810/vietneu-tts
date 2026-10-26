---
{
  "id": "statue_cards",
  "ten": "Thẻ tượng BUD",
  "loai": "template",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "bud"
  ],
  "hop_ngach": [
    "giai_thich",
    "van_hoa"
  ],
  "cam_ngach": [
    "fs"
  ],
  "so_muc": 0,
  "so_nguon": 0,
  "nguon": [],
  "bang_chung_dung": [
    "output/cl_staging/grok/build_budlookup.py",
    "output/cl_staging/grok/tools/lookup/renderer.py"
  ],
  "vi_du": [],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "../../../../../../../Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/output/cl_staging/grok/build_r1025.py"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Ảnh tượng BUD làm nền, chip tiêu đề nằm trên vùng tối và các thẻ lời hiện lần lượt; html_statue chọn ảnh/độ sáng theo id bài.

## Khi nào dùng

Short BUD có ảnh tượng và câu kinh đã kiểm nguồn. Không nên dùng: Không dùng cho FS; cũng tránh khi chữ phải phủ mặt hoặc thiếu credit ảnh.

## Cách dựng trong HyperFrames

Nhánh dựng cho statue cards nằm tại `output/cl_staging/grok/build_r1025.py:162`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_r1025.py:168`.

style `statue_cards`; gọi `html_statue(rid,t,dur)`, rid phải có trong `IMG`, `HEAD`, `ACCENT`, `CARDS`; pham_vi `bud`.

## Rủi ro

Ticket 45 ngày 21/10: thẻ chữ đè mặt tượng, tiêu đề rớt một chữ; kiểm crop và ảnh credit từ Commons metadata.
