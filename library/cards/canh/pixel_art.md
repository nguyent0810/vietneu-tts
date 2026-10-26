---
{
  "id": "pixel_art",
  "ten": "Nghệ thuật pixel",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "do_hoa",
    "hoai_niem"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 128,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/majidmanzarpour/status/2102476258948927543",
    "https://x.com/Viggle_PINOC/status/2102861939072434495"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Lưới pixel vuông, palette ít và cạnh bậc thang tạo hình cố ý không khử răng cưa. Mẫu [1](https://x.com/majidmanzarpour/status/2102476258948927543) minh họa dùng sprite pixel để biểu diễn vật thể retro; mẫu [2](https://x.com/Viggle_PINOC/status/2102861939072434495) cho thấy đổi pose bằng frame sprite rời.

## Khi nào dùng

Không hợp FS/BUD trừ minh họa hoài niệm có chủ đích. Dạng Short. Không nên dùng khi nội dung nghiêm dễ bị game hóa.

## Cách dựng trong HyperFrames

Kỹ thuật pixel_art chưa có trong engine như một visual riêng. Lưu sprite sheet; chọn frame floor(t*fps) và scale nguyên lần với image-rendering pixelated. Mọi trạng thái của pixel_art là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

nội dung nghiêm dễ bị game hóa; scale lẻ làm pixel và chữ nhòe.
