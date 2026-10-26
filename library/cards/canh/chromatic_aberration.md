---
{
  "id": "chromatic_aberration",
  "ten": "Lệch sắc màu",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "hieu_ung",
    "ky_thuat_hinh"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 24,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/GroundControl/status/2103678647777230877"
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
    "bud": 0
  },
  "cong": "thap"
}
---

## Mô tả

Viền đỏ/xanh lệch quanh cạnh tương phản, còn lớp chữ chính giữ nét để hiệu ứng không phủ toàn khung. Mẫu [1](https://x.com/twoclipping/status/2102554209166000267) minh họa tách viền màu quanh một cạnh ảnh; mẫu [2](https://x.com/GroundControl/status/2103678647777230877) cho thấy nhấn khoảnh khắc sai lệch quang học.

## Khi nào dùng

Không hợp FS/BUD; thử nghiệm giải thích lỗi ống kính. Dạng Short. Không nên dùng khi gây mỏi mắt, giảm rõ phụ đề, dễ thành glitch trang trí.

## Cách dựng trong HyperFrames

Kỹ thuật chromatic_aberration chưa có trong engine như một visual riêng. Tạo hai layer tint đỏ/cyan tiền dựng; animate clip/translate ngắn theo timeline t và giữ chữ ngoài effect. Mọi trạng thái của chromatic_aberration là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

gây mỏi mắt, giảm rõ phụ đề, dễ thành glitch trang trí.
