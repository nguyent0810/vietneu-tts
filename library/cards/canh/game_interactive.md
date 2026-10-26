---
{
  "id": "game_interactive",
  "ten": "Tương tác / trò chơi",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "quiz",
    "tuong_tac"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 126,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/ggsimm/status/2102882622053535814",
    "https://x.com/gandamu_ml/status/2102919394775220530"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
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

Màn hình có lựa chọn và phản hồi đúng/sai như quiz; video tuyến tính chỉ mô phỏng lựa chọn định sẵn. Mẫu [1](https://x.com/ggsimm/status/2102882622053535814) minh họa hiện lựa chọn phương vị dưới dạng quiz; mẫu [2](https://x.com/gandamu_ml/status/2102919394775220530) cho thấy đưa đáp án cố định sau thời gian chờ.

## Khi nào dùng

Không hợp FS/BUD tuyến tính, chỉ thử nghiệm quiz nhận diện phương vị. Dạng Short. Không nên dùng khi mô phỏng tương tác giả hứa chức năng không có.

## Cách dựng trong HyperFrames

Kỹ thuật game_interactive chưa có trong engine như một visual riêng. Dựng state lựa chọn định sẵn bằng HTML/SVG; tiến state theo t, không nhận input, random hay realtime. Mọi trạng thái của game_interactive là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

mô phỏng tương tác giả hứa chức năng không có; quiz làm nhẹ nội dung nghiêm.
