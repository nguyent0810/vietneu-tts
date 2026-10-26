---
{
  "id": "end_card",
  "ten": "Thẻ kết",
  "loai": "template",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "tra_cuu",
    "van_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 30,
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
    "https://x.com/JustinPerea/status/2102893186330841502",
    "https://x.com/wallacex227/status/2103245000989659422"
  ],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [
    "endcard"
  ],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Thẻ kết giữ một lời nhắc hoặc tên kênh trên nền ít chi tiết; visual endcard có vùng title và CTA riêng.

## Khi nào dùng

Short chốt một ý và lời mời theo dõi; Long kết chương có câu đọng lại. Không nên dùng: Kết luận còn chưa được nêu hoặc CTA lấn át nội dung.

## Cách dựng trong HyperFrames

Nhánh dựng cho end card nằm tại `hyperframes_short/compositions/longform.js:1387`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:703`.

visual type `endcard`; truyền `title`, `cta` ngắn và thời điểm vào; dùng ở cuối timeline.

## Rủi ro

CTA dài tràn safe area; animation chưa kết sẽ để frame cuối ở trạng thái nửa hiện.
