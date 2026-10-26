---
{
  "id": "lower_third",
  "ten": "Lower third / dải tên",
  "loai": "template",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "dan_nguon",
    "ten_nguoi"
  ],
  "cam_ngach": [],
  "so_muc": 20,
  "so_nguon": 2,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/alexwtlf/status/2103713416367981005",
    "https://x.com/Michaelzsguo/status/2105105890936233985"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 2
  },
  "cong": "thap"
}
---

## Mô tả

Dải chữ ở mép dưới nêu tên, vai trò hoặc địa điểm trong khi hình chính tiếp tục. Mẫu [1](https://x.com/alexwtlf/status/2103713416367981005) minh họa ghi tên người dịch dưới đoạn trích; mẫu [2](https://x.com/Michaelzsguo/status/2105105890936233985) cho thấy nêu địa danh khi bản đồ vẫn hiện.

## Khi nào dùng

BUD: Short ghi nguồn bản dịch và tên người dịch. Dạng Short. Không nên dùng khi dễ đè caption hoặc mặt người.

## Cách dựng trong HyperFrames

Kỹ thuật lower_third chưa có trong engine như một visual riêng. Dựng dải bằng HTML/CSS ở safe area; opacity/translate GSAP có start/end cố định, tránh vùng caption. Mọi trạng thái của lower_third là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

dễ đè caption hoặc mặt người; tên dài bị cắt làm sai nguồn.
