---
{
  "id": "typewriter",
  "ten": "Chữ đánh máy",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chu",
    "dan_giai"
  ],
  "cam_ngach": [],
  "so_muc": 14,
  "so_nguon": 2,
  "nguon": [
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/ultimaxbt-bbebf5",
    "https://prompt-motion.com/kantamk-61f410"
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
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Ký tự hiện lần lượt theo tốc độ đều, dấu câu tạo nhịp dừng và caret có thể chớp theo thời gian. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa gõ câu dẫn chú giải ngắn; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy dừng caret ở dấu câu.

## Khi nào dùng

BUD: Short giới thiệu một thuật ngữ trước khi giải nghĩa. Dạng Short. Không nên dùng khi cắt giữa grapheme tiếng việt.

## Cách dựng trong HyperFrames

Kỹ thuật typewriter chưa có trong engine như một visual riêng. Tách chuỗi theo grapheme; số ký tự hiện = f(t), caret nhấp theo modulo t thay vì clock thật. Mọi trạng thái của typewriter là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

cắt giữa grapheme tiếng Việt; typing làm kinh văn trông như chat.
