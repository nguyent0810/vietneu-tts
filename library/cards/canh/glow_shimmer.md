---
{
  "id": "glow_shimmer",
  "ten": "Phát sáng / shimmer",
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
  "so_muc": 124,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "hyperframes_short/compositions/_tb_fs_nx01.html",
    "hyperframes_short/compositions/_tb_fs_nx02.html",
    "hyperframes_short/compositions/_tb_fs_nx03.html",
    "output/cl_staging/grok/build_bud_1023.py",
    "output/cl_staging/grok/build_bud_t.py"
  ],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/ishuagra02/status/2102920408743678129"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/components/text-shimmer.html",
    "hyperframes_short/compositions/lightfield.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Vệt sáng chạy qua chữ rồi tắt; bản FS yeartable từng để shimmer đứng lại đè cột cuối.

## Khi nào dùng

Short nhấn một nhãn/giá trị; Long tối đa một lượt quét theo lời đọc. Không nên dùng: Bảng dày nhiều cột hay nền sáng khó giữ tương phản.

## Cách dựng trong HyperFrames

Nhánh dựng cho glow shimmer nằm tại `hyperframes_short/compositions/review_yeartable.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_fs2027.py:1`.

style `review_yeartable`; hẹn shimmer theo số hàng, kết thúc trước 85% tổng thời lượng.

## Rủi ro

Vệt phải về opacity 0 trước frame cuối; 23/10 shimmer kẹt ở cột Thái Tuế.
