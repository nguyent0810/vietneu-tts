---
{
  "id": "texture_overlay",
  "ten": "Lớp phủ texture",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chat_lieu",
    "nen"
  ],
  "cam_ngach": [],
  "so_muc": 14,
  "so_nguon": 2,
  "nguon": [
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/components/grain-overlay.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/components/ink-bleed-reveal.html"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 2
  },
  "cong": "thap"
}
---

## Mô tả

Lớp giấy/hạt/mực bán trong phủ lên nền để thêm chất liệu mà không thay thông tin chính. Mẫu [1](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/components/grain-overlay.html) minh họa phủ hạt nhẹ lên trang chú giải; mẫu [2](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/components/ink-bleed-reveal.html) cho thấy đặt lớp mực dưới chữ chính.

## Khi nào dùng

BUD: Short dùng nền giấy nhẹ cho chú giải, tránh phủ lên kinh. Dạng Ca_hai. Không nên dùng khi làm giảm tương phản chữ.

## Cách dựng trong HyperFrames

Kỹ thuật texture_overlay chưa có trong engine như một visual riêng. Dùng asset texture cục bộ tĩnh và blend/opacity CSS; hạt không sinh lại giữa các frame. Mọi trạng thái của texture_overlay là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Lớp phủ có thể bắt đầu từ component `hyperframes_short/compositions/components/grain-overlay.html:1`. Công thap.

## Rủi ro

làm giảm tương phản chữ; blend mode khác nhau giữa GPU.
