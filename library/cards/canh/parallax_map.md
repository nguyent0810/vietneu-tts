---
{
  "id": "parallax_map",
  "ten": "Bản đồ có chiều sâu",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "fs"
  ],
  "hop_ngach": [
    "ban_do",
    "khong_gian"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 15,
  "so_nguon": 2,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/bonnyxen/status/2107843676135100870",
    "https://prompt-motion.com/ultimaxbt-bbebf5"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Các lớp địa hình/bản đồ lệch tốc độ khi lia, tạo chiều sâu giả nhưng giữ tọa độ cơ sở. Mẫu [1](https://x.com/bonnyxen/status/2107843676135100870) minh họa lia nền trong khi giữ nhãn địa điểm; mẫu [2](https://prompt-motion.com/ultimaxbt-bbebf5) cho thấy tách đường và địa hình thành lớp.

## Khi nào dùng

FS: Long theo tuyến từ cổng tới nhà trên sơ đồ. Dạng Ca_hai. Không nên dùng khi parallax làm nhãn lệch vị trí.

## Cách dựng trong HyperFrames

Kỹ thuật parallax_map chưa có trong engine như một visual riêng. Tách nền/đường/nhãn thành group; dịch camera các lớp theo hệ số cố định, nhưng khóa nhãn vào tọa độ bản đồ. Mọi trạng thái của parallax_map là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

parallax làm nhãn lệch vị trí; chuyển động nhiều gây chóng mặt.
