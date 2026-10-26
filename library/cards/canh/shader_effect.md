---
{
  "id": "shader_effect",
  "ten": "Hiệu ứng shader",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "hieu_ung",
    "do_hoa"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 229,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/alexalbert__/status/2102466523164274839",
    "https://x.com/Michaelzsguo/status/2102592355165782312"
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
  "cong": "cao"
}
---

## Mô tả

Công thức màu/ánh sáng tác động theo pixel lên ảnh, như méo sóng hoặc viền sáng. Mẫu [1](https://x.com/alexalbert__/status/2102466523164274839) minh họa làm biến dạng ảnh như minh họa quang học; mẫu [2](https://x.com/Michaelzsguo/status/2102592355165782312) cho thấy đổi cường độ ánh sáng trên vật thể.

## Khi nào dùng

Không hợp FS/BUD khi biến dạng tư liệu. Dạng Ca_hai. Không nên dùng khi webgl/filter nặng headless.

## Cách dựng trong HyperFrames

Kỹ thuật shader_effect chưa có trong engine như một visual riêng. Ưu tiên bake các mốc shader thành ảnh rồi crossfade theo t; nếu dùng SVG filter thì tham số phải cố định. Mọi trạng thái của shader_effect là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

WebGL/filter nặng headless; sai màu ảnh nguồn hoặc tăng VRAM.
