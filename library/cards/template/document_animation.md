---
{
  "id": "document_animation",
  "ten": "Tài liệu / báo chí động",
  "loai": "template",
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
  "so_muc": 16,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "output/cl_staging/hyperframes_oct/plan_o02.json",
    "output/cl_staging/hyperframes_oct/plan_o07.json",
    "output/cl_staging/hyperframes_sept/plan_d26.json"
  ],
  "vi_du": [
    "https://prompt-motion.com/ultimaxbt-bbebf5",
    "https://prompt-motion.com/kantamk-61f410"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/dossier.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Trang tài liệu trượt/phóng vào vùng đang đọc, phần tag tách khỏi ảnh; dossier giữ cảm giác giấy hồ sơ.

## Khi nào dùng

Long phân tích một tư liệu theo đoạn; Short trích một trang có nguồn. Không nên dùng: Không có tài liệu thật để minh họa hoặc trang có chữ quá nhỏ.

## Cách dựng trong HyperFrames

Nhánh dựng cho document animation nằm tại `hyperframes_short/compositions/dossier.html:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/compositions/longform.js:1441`.

visual type `doc`; `src,w,h,tone,moves[{x,y,z,d}]`, tùy chọn `tag` và `tag_at`.

## Rủi ro

Zoom crop có thể cắt chú thích nguồn; giấy giả cần ghi rõ là minh họa.
