---
{
  "id": "camera_zoom",
  "ten": "Zoom camera",
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
  "so_muc": 45,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2103273003555402193",
    "https://x.com/demonugc/status/2103526713208525162"
  ],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Ảnh phóng vào điểm được nhắc, giữ tâm nhìn theo tọa độ thay vì phóng giữa màn hình.

## Khi nào dùng

Short nhấn một chi tiết; Long phân tích hiện vật qua vài mức cận. Không nên dùng: Cần so hai vùng cách xa nhau trong một nhịp ngắn.

## Cách dựng trong HyperFrames

Nhánh dựng cho camera zoom nằm tại `hyperframes_short/compositions/longform.js:1441`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:703`.

visual type `doc`; move `{x,y,z}` chọn tâm và mức phóng, `d` là thời lượng tween.

## Rủi ro

Zoom lớn làm mất ngữ cảnh; tâm zoom đặt sai có thể cắt mất chi tiết.
