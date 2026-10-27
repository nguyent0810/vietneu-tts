---
{
  "id": "shadow_puppet",
  "ten": "Rối bóng",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "bud"
  ],
  "hop_ngach": [
    "minh_hoa",
    "ke_chuyen"
  ],
  "cam_ngach": [
    "fs"
  ],
  "so_muc": 21,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/x4b47x/status/2103019799614034026",
    "https://x.com/moreisdifferent/status/2108563710260170985"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 3
  },
  "cong": "cao"
}
---

## Mô tả

Silhouette phẳng chuyển động sau nền sáng như rối chiếu bóng, có khớp hoặc đạo cụ riêng. Mẫu [1](https://x.com/x4b47x/status/2103019799614034026) minh họa đưa hình bóng vào cảnh kể dụ ngôn; mẫu [2](https://x.com/moreisdifferent/status/2108563710260170985) cho thấy cử động khớp trên nền phẳng.

## Khi nào dùng

BUD: Short minh họa dụ ngôn đã kiểm văn bản. Dạng Short. Không nên dùng khi cách điệu thiếu trang nghiêm.

## Cách dựng trong HyperFrames

Kỹ thuật shadow_puppet chưa có trong engine như một visual riêng. Vẽ silhouette SVG theo pose keyframe; xoay nhóm quanh pivot cố định trên nền phẳng, không mô phỏng đèn. Mọi trạng thái của shadow_puppet là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

cách điệu thiếu trang nghiêm; khớp cứng hoặc nguồn tạo hình mơ hồ.
