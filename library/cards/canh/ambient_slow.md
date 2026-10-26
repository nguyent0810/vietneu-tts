---
{
  "id": "ambient_slow",
  "ten": "Chuyển động chậm tĩnh tại",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "nen"
  ],
  "cam_ngach": [],
  "so_muc": 20,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/EvoLinkAi/status/2110762371920892095",
    "https://x.com/rubenssoto_ai/status/2110065587279798719"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 2
  },
  "cong": "thap"
}
---

## Mô tả

Cảnh gần tĩnh chỉ có một chuyển động nhỏ, chậm và lặp kín như rèm lay hoặc ánh sáng đổi. Mẫu [1](https://x.com/EvoLinkAi/status/2110762371920892095) minh họa giữ rèm lay nhẹ sau sơ đồ phòng; mẫu [2](https://x.com/rubenssoto_ai/status/2110065587279798719) cho thấy làm nền có nhịp thở thay vì cắt liên tục.

## Khi nào dùng

FS/BUD: Long mở đoạn giải thích không gian hoặc dẫn nhập yên tĩnh. Dạng Ca_hai. Không nên dùng khi loop lộ điểm nối hoặc chuyển động cạnh chữ làm giảm tương phản.

## Cách dựng trong HyperFrames

Kỹ thuật ambient_slow chưa có trong engine như một visual riêng. Tách nền/đối tượng thành lớp SVG/CSS; đặt keyframe đầu-cuối kín, pha là t modulo chu kỳ thay vì clock trình duyệt. Mọi trạng thái của ambient_slow là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

loop lộ điểm nối hoặc chuyển động cạnh chữ làm giảm tương phản.
