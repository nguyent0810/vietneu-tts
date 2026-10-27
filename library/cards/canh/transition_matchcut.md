---
{
  "id": "transition_matchcut",
  "ten": "Match cut",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chuyen_canh",
    "lien_tuc"
  ],
  "cam_ngach": [],
  "so_muc": 17,
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
    "https://x.com/MadMax_Series/status/2108577475752054868"
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
  "cong": "vua"
}
---

## Mô tả

Cảnh mới giữ hình dáng/vị trí gần cảnh trước rồi đổi chủ thể, tạo cầu nối thị giác. Mẫu [1](https://x.com/twoclipping/status/2102554209166000267) minh họa chuyển từ vòng la bàn sang vòng sơ đồ; mẫu [2](https://x.com/MadMax_Series/status/2108577475752054868) cho thấy giữ điểm neo khi đổi bối cảnh.

## Khi nào dùng

FS: Short nối hai sơ đồ có cùng hướng. Dạng Ca_hai. Không nên dùng khi anchor lệch gây giật.

## Cách dựng trong HyperFrames

Kỹ thuật transition_matchcut chưa có trong engine như một visual riêng. Đặt anchor tương ứng thủ công cho hai cảnh; nội suy transform/opacity trong khoảng chuyển cố định. Mọi trạng thái của transition_matchcut là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

anchor lệch gây giật; dễ ngụ ý hai khái niệm là một.
