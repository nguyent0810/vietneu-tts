---
{
  "id": "mask_reveal",
  "ten": "Reveal bằng mask",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "reveal",
    "anh_tu_lieu"
  ],
  "cam_ngach": [],
  "so_muc": 25,
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
    "https://x.com/brainextends/status/2103801834930606193",
    "https://x.com/iamtanzil_/status/2103820321673675031"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 1
  },
  "cong": "vua"
}
---

## Mô tả

Mask hình học che ảnh rồi mở theo wipe, đường tròn hoặc mép tùy chỉnh. Mẫu [1](https://x.com/brainextends/status/2103801834930606193) minh họa mở vùng chú giải trên sơ đồ; mẫu [2](https://x.com/iamtanzil_/status/2103820321673675031) cho thấy quét mask qua ảnh đã crop.

## Khi nào dùng

FS: Short tiết lộ chi tiết trên bản vẽ sau câu hỏi. Dạng Ca_hai. Không nên dùng khi mép raster răng cưa.

## Cách dựng trong HyperFrames

Kỹ thuật mask_reveal chưa có trong engine như một visual riêng. Ảnh tĩnh cộng clipPath/polygon SVG; mọi đỉnh mask tính từ progress t. Mọi trạng thái của mask_reveal là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

mép raster răng cưa; che nguồn quá lâu tạo nhịp bí hiểm.
