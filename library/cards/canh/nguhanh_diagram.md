---
{
  "id": "nguhanh_diagram",
  "ten": "Sơ đồ ngũ hành",
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
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Năm nút Mộc–Hỏa–Thổ–Kim–Thủy nằm trên vòng; cung sinh đi quanh vòng còn tương khắc là dây cung xuyên tâm.

## Khi nào dùng

Short giải thích một quan hệ ngũ hành; Long khi dẫn từng bước theo lời. Không nên dùng: Chỉ cần nêu năm tên mà không diễn giải quan hệ.

## Cách dựng trong HyperFrames

Nhánh dựng cho nguhanh diagram nằm tại `hyperframes_short/compositions/longform.js:356`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/compositions/longform.js:388`.

visual type `elements`; truyền `year.element`, `year.label`, `steps[{kind,from,to}]` với kind `sinh|khac|hoa`.

## Rủi ro

Nhầm chiều tương sinh/đặt sai `from`, `to` sẽ đảo kiến thức; nhãn năm có thể đè nút.
