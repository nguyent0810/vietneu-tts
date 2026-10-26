---
{
  "id": "venn_diagram",
  "ten": "Sơ đồ Venn",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_sanh",
    "phan_loai"
  ],
  "cam_ngach": [],
  "so_muc": 13,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/kantamk-61f410",
    "https://prompt-motion.com/samaote-5e2fc2"
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
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Hai hoặc ba vòng giao nhau với vùng riêng/chung có nhãn để so tập hợp khái niệm. Mẫu [1](https://prompt-motion.com/kantamk-61f410) minh họa so hai cách dịch thuật ngữ và vùng nghĩa chung; mẫu [2](https://prompt-motion.com/samaote-5e2fc2) cho thấy tô phần giao giữa hai vòng.

## Khi nào dùng

BUD: Short phân biệt hai cách dịch có phần nghĩa chung. Dạng Short. Không nên dùng khi diện tích không phải tỷ lệ nếu không chú thích.

## Cách dựng trong HyperFrames

Kỹ thuật venn_diagram chưa có trong engine như một visual riêng. Vẽ ellipse và vùng giao bằng SVG mask/path; reveal từng tập hợp theo thời gian. Mọi trạng thái của venn_diagram là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

diện tích không phải tỷ lệ nếu không chú thích; hơn ba nhóm rối.
