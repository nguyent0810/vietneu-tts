---
{
  "id": "split_text",
  "ten": "Tách chữ / ký tự",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chu",
    "thuat_ngu"
  ],
  "cam_ngach": [],
  "so_muc": 22,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2103835273813496100",
    "https://x.com/juancarlos17626/status/2108663864581558301"
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
  "cong": "vua"
}
---

## Mô tả

Từ/cụm tách thành ký tự, cột hoặc nửa rồi ghép lại để làm rõ cấu trúc chữ. Mẫu [1](https://x.com/twoclipping/status/2103835273813496100) minh họa tách thuật ngữ Pali khỏi phần dịch; mẫu [2](https://x.com/juancarlos17626/status/2108663864581558301) cho thấy đưa các mảnh chữ về đúng thứ tự.

## Khi nào dùng

BUD: Short giải nghĩa một thuật ngữ trong chú giải. Dạng Short. Không nên dùng khi cắt giữa dấu tiếng việt.

## Cách dựng trong HyperFrames

Kỹ thuật split_text chưa có trong engine như một visual riêng. Tạo span/SVG theo grapheme Unicode; tween transform về vị trí cuối theo GSAP time, không cắt UTF-16 tùy tiện. Mọi trạng thái của split_text là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

cắt giữa dấu tiếng Việt; hiệu ứng biến chữ kinh thành trò chơi.
