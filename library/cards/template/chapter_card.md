---
{
  "id": "chapter_card",
  "ten": "Thẻ chương",
  "loai": "template",
  "dinh_dang": [
    "long"
  ],
  "pham_vi": [
    "bud"
  ],
  "hop_ngach": [
    "cau_truc",
    "dan_nhap"
  ],
  "cam_ngach": [
    "fs"
  ],
  "so_muc": 27,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/monya_for_io/status/2104554735382778328",
    "https://x.com/Michaelzsguo/status/2105105890936233985"
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
    "bud": 2
  },
  "cong": "thap"
}
---

## Mô tả

Thẻ mở chương có số thứ tự, tiêu đề ngắn và dấu hiệu thị giác phân biệt đoạn mới. Mẫu [1](https://x.com/monya_for_io/status/2104554735382778328) minh họa đánh dấu chương giải nghĩa thuật ngữ; mẫu [2](https://x.com/Michaelzsguo/status/2105105890936233985) cho thấy hiện tiêu đề trước nội dung dài.

## Khi nào dùng

BUD: Long chuyển chương sau một đoạn giảng. Dạng Long. Không nên dùng khi quá nhiều title card làm đứt mạch.

## Cách dựng trong HyperFrames

Kỹ thuật chapter_card chưa có trong engine như một visual riêng. Dựng card HTML/SVG từ số chương và tiêu đề; vào/ra opacity/translate tại mốc chapter cố định. Mọi trạng thái của chapter_card là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Cấu trúc chương hiện có để đối chiếu nằm ở `hyperframes_short/compositions/longform.js:180`. Công thap.

## Rủi ro

quá nhiều title card làm đứt mạch; tiêu đề không khớp cấu trúc nội dung.
