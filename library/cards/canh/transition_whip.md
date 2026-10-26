---
{
  "id": "transition_whip",
  "ten": "Whip transition",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chuyen_canh",
    "nhanh"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 13,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/beebidao/status/2108567783789515051",
    "https://x.com/HimazinProducer/status/2111335698745966657"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Khung lia nhanh ngang/dọc, blur ngắn rồi dừng ở cảnh kế theo cùng hướng chuyển động. Mẫu [1](https://x.com/beebidao/status/2108567783789515051) minh họa lia từ góc rộng sang chi tiết cùng phòng; mẫu [2](https://x.com/HimazinProducer/status/2111335698745966657) cho thấy dùng một cú quét làm đổi góc nhìn.

## Khi nào dùng

Không hợp BUD trang nghiêm; FS chỉ thử giữa hai góc cùng phòng. Dạng Short. Không nên dùng khi blur/lia nhanh gây chóng mặt và khó seek.

## Cách dựng trong HyperFrames

Kỹ thuật transition_whip chưa có trong engine như một visual riêng. Dịch hai lớp cảnh theo GSAP easing cố định; bật blur ở khoảng t hữu hạn và tắt tại điểm cắt. Mọi trạng thái của transition_whip là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

blur/lia nhanh gây chóng mặt và khó seek.
