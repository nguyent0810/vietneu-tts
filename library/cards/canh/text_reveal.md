---
{
  "id": "text_reveal",
  "ten": "Reveal chữ",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chu",
    "reveal"
  ],
  "cam_ngach": [],
  "so_muc": 24,
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
    "https://x.com/brainextends/status/2103801834930606193",
    "https://x.com/TawohAwa/status/2104896325255037196"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 3
  },
  "cong": "thap"
}
---

## Mô tả

Dòng chữ mở bằng mask/wipe/opacity để nhấn câu kết luận theo nhịp thoại. Mẫu [1](https://x.com/brainextends/status/2103801834930606193) minh họa hiện cụm giải nghĩa sau câu trích; mẫu [2](https://x.com/TawohAwa/status/2104896325255037196) cho thấy mở từng từ khóa theo thời điểm.

## Khi nào dùng

BUD: Short lần lượt hiện cụm giải nghĩa sau khi đọc trích đoạn. Dạng Short. Không nên dùng khi mask cắt dấu hoặc lệch caption.

## Cách dựng trong HyperFrames

Kỹ thuật text_reveal chưa có trong engine như một visual riêng. Dùng clipPath hoặc span với mốc reveal tuyệt đối; progress mỗi glyph là hàm t và giữ state cuối ổn định. Mọi trạng thái của text_reveal là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

mask cắt dấu hoặc lệch caption; chữ ra nhanh khó đọc.
