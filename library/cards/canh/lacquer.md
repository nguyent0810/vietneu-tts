---
{
  "id": "lacquer",
  "ten": "Sơn mài",
  "loai": "canh",
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
  "so_muc": 24,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/build_F10.py",
    "output/cl_staging/long/build_F13.py",
    "output/cl_staging/long/build_F16.py",
    "output/cl_staging/long/build_F19.py",
    "output/cl_staging/long/build_F4.py"
  ],
  "vi_du": [
    "https://x.com/agentgamesbot/status/2103401820261355554",
    "https://x.com/mizugame_22/status/2104940371038109764"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/lacquer_long.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Mảng sơn bóng có viền sáng và nền tối, tạo cảm giác vật thể phủ sơn; lacquer_long giữ lớp highlight riêng.

## Khi nào dùng

Long về đồ vật/văn hóa cần bề mặt sơn mài. Không nên dùng: Nội dung hiện đại cần sắc thái trung tính hoặc bảng tra cứu.

## Cách dựng trong HyperFrames

Nhánh dựng cho lacquer nằm tại `hyperframes_short/compositions/lacquer_long.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_F10.py:1`.

composition `lacquer_long.html`; đặt ảnh chủ thể dưới lớp highlight.

## Rủi ro

Highlight dễ đọc như vết nứt; tương phản vàng trên nền đen cần thử frame.
