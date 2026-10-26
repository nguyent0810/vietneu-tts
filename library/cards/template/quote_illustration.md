---
{
  "id": "quote_illustration",
  "ten": "Trích dẫn minh họa",
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
  "so_muc": 0,
  "so_nguon": 0,
  "nguon": [],
  "bang_chung_dung": [
    "output/cl_staging/build_jataka_b1.py"
  ],
  "vi_du": [],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/jataka_engine.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Câu trích và hình minh họa chia hai vùng, tranh làm rõ ý chứ không phủ câu; jataka_engine dựng illustration scene.

## Khi nào dùng

Short lời dạy kèm một hành động; Long truyện có câu then chốt. Không nên dùng: Ảnh minh họa có thể khiến câu bị gán sai nguồn.

## Cách dựng trong HyperFrames

Nhánh dựng cho quote illustration nằm tại `hyperframes_short/compositions/jataka_engine.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_jataka_b1.py:1`.

visual type `illus` trong jataka_engine; tách illustration khỏi caption.

## Rủi ro

Hình diễn sai ngữ cảnh làm người xem tưởng là tư liệu; quote phải giữ nguyên văn.
