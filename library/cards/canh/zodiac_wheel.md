---
{
  "id": "zodiac_wheel",
  "ten": "Vòng 12 chi",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "fs"
  ],
  "hop_ngach": [
    "tra_cuu",
    "van_hoa",
    "tam_linh"
  ],
  "cam_ngach": [],
  "so_muc": 2,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/longform.js",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/motion-library/SKILL.md"
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

12 chi đặt quanh vòng kiểu mặt đồng hồ, Tý ở đỉnh; legend bên cạnh nêu nhóm quan hệ theo từng bước.

## Khi nào dùng

Short giải một nhóm tam hợp/xung; Long đi lần lượt qua nhiều chi. Không nên dùng: Chỉ cần nêu một con giáp mà không có quan hệ vòng.

## Cách dựng trong HyperFrames

Nhánh dựng cho zodiac wheel nằm tại `hyperframes_short/compositions/longform.js:246`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/compositions/longform.js:302`.

visual type `wheel`; `title`, `focus`, `steps[{rel,chi,label}]`, biến thể `tilt|assemble|spin` (longform.js).

## Rủi ro

Thứ tự CHI gắn theo góc 30°; step.chi sai làm đường quan hệ nối nhầm nút.
