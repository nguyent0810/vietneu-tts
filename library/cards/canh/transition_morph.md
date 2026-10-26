---
{
  "id": "transition_morph",
  "ten": "Chuyển cảnh morph",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chuyen_canh",
    "do_hoa"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 44,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2103273003555402193",
    "https://x.com/ajith_io/status/2103449416325890146"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 0
  },
  "cong": "cao"
}
---

## Mô tả

Đường bao A biến dần thành B qua các điểm tương ứng thay vì cắt cảnh trực tiếp. Mẫu [1](https://x.com/twoclipping/status/2103273003555402193) minh họa biến hình ký hiệu trung tính giữa hai trạng thái; mẫu [2](https://x.com/ajith_io/status/2103449416325890146) cho thấy nội suy path giữa hai đồ hình.

## Khi nào dùng

Không hợp BUD với biểu tượng linh thiêng; thử hình sơ đồ trung tính. Dạng Ca_hai. Không nên dùng khi ghép điểm path sai làm tan méo, ngụ ý quan hệ biến đổi.

## Cách dựng trong HyperFrames

Kỹ thuật transition_morph chưa có trong engine như một visual riêng. Chuẩn hóa hai SVG path cùng topology hoặc bake shape trung gian; morph progress đọc trực tiếp từ t. Mọi trạng thái của transition_morph là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

ghép điểm path sai làm tan méo, ngụ ý quan hệ biến đổi.
