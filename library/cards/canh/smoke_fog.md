---
{
  "id": "smoke_fog",
  "ten": "Khói / sương",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "khong_khi",
    "nen"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 40,
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
    "https://x.com/koldo2k/status/2103129343253778767",
    "https://x.com/agentgamesbot/status/2103401820261355554"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
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

Dải sương bán trong làm lùi nền; khói có đường viền mềm và che khuất một phần cảnh. Mẫu [1](https://x.com/koldo2k/status/2103129343253778767) minh họa đưa lớp sương vào cảnh thiên nhiên nguồn thật; mẫu [2](https://x.com/agentgamesbot/status/2103401820261355554) cho thấy tách nền xa và gần bằng haze.

## Khi nào dùng

Không hợp FS/BUD giải thích trực tiếp; chỉ thử trong cảnh thơ phù hợp. Dạng Ca_hai. Không nên dùng khi che bản đồ/chữ.

## Cách dựng trong HyperFrames

Kỹ thuật smoke_fog chưa có trong engine như một visual riêng. Dùng vài lớp PNG/SVG tiền vẽ; dịch theo biểu thức sin(t) với seed/pha khóa, không dùng particle realtime. Mọi trạng thái của smoke_fog là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

che bản đồ/chữ; hiệu ứng huyền bí dễ làm sai giọng FS.
