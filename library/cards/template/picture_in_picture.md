---
{
  "id": "picture_in_picture",
  "ten": "Picture in picture",
  "loai": "template",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "anh_phu"
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
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/MustaphaFenzar/status/2102773737129156730",
    "https://x.com/oviniciuslana/status/2103086714772463953"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 1
  },
  "cong": "thap"
}
---

## Mô tả

Khung nhỏ nổi trên hình chính giữ đồng thời người nói, sơ đồ hoặc hình phụ. Mẫu [1](https://x.com/MustaphaFenzar/status/2102773737129156730) minh họa để sơ đồ nhỏ khi cảnh chính mô tả căn phòng; mẫu [2](https://x.com/oviniciuslana/status/2103086714772463953) cho thấy chèn bản đồ ở góc lúc đọc lời giải thích.

## Khi nào dùng

FS: Short giữ bản vẽ trong góc khi chỉ vị trí. Dạng Ca_hai. Không nên dùng khi khung phụ che phụ đề/mặt.

## Cách dựng trong HyperFrames

Kỹ thuật picture_in_picture chưa có trong engine như một visual riêng. Đặt hai media theo thời gian tuyệt đối, khung phụ neo trong safe-area; visibility/opacity đọc từ t. Mọi trạng thái của picture_in_picture là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

khung phụ che phụ đề/mặt; hai hình chuyển động tranh chú ý.
