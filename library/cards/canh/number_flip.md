---
{
  "id": "number_flip",
  "ten": "Số lật",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_lieu",
    "typography"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 11,
  "so_nguon": 2,
  "nguon": [
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/shorts-studio/references/devices.md",
    "https://prompt-motion.com/kantamk-61f410"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Chữ số lật qua trục ngang kiểu bảng cơ học, có thể đổi từng hàng riêng. Mẫu [1](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/shorts-studio/references/devices.md) minh họa lật chữ số tới mốc năm; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy đổi hàng chục và đơn vị theo nhịp.

## Khi nào dùng

Không hợp FS/BUD nếu con số không phải mốc đáng chú ý. Dạng Short. Không nên dùng khi font/perspective méo chữ.

## Cách dựng trong HyperFrames

Kỹ thuật number_flip chưa có trong engine như một visual riêng. Tách glyph thành hai mặt CSS 3D, góc lật tính từ chữ số tại t; fallback crossfade glyph SVG nếu headless méo. Mọi trạng thái của number_flip là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

font/perspective méo chữ; bộ đếm giả bị hiểu thành số liệu thật.
