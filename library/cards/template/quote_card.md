---
{
  "id": "quote_card",
  "ten": "Thẻ trích dẫn",
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
  "so_muc": 17,
  "so_nguon": 2,
  "nguon": [
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "hyperframes_short/compositions/_game_bud_loiday01.html",
    "hyperframes_short/compositions/_game_bud_loiday02.html",
    "hyperframes_short/compositions/_r_bud_a2_01.html",
    "hyperframes_short/compositions/_tb_bud_t1_01.html",
    "hyperframes_short/compositions/_tb_bud_t1_02.html"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/studio/devices/quote.js",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/longform.js"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/studio/devices/quote.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Câu trích đứng trong thẻ riêng với tên nguồn và khoảng trắng; device quote dùng nội dung ngắn thay banner tràn khung.

## Khi nào dùng

Short một câu trích có xuất xứ; Long đặt trích dẫn giữa phần giải thích. Không nên dùng: Không xác định được nguyên văn hoặc người nói.

## Cách dựng trong HyperFrames

Nhánh dựng cho quote card nằm tại `hyperframes_short/studio/devices/quote.js:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:658`.

device `quote`; truyền quote, attribution và thời lượng giữ.

## Rủi ro

Dấu câu/nguồn sai làm thay đổi ý; câu dài cần xuống dòng có chủ đích.
