---
{
  "id": "pie_chart",
  "ten": "Biểu đồ tròn",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "du_lieu",
    "ti_le"
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
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/longform.js",
    "https://prompt-motion.com/ultimaxbt-bbebf5"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 1
  },
  "cong": "vua"
}
---

## Mô tả

Hình tròn chia lát theo tỷ trọng với tổng 100%, lát và nhãn làm rõ cơ cấu. Mẫu [1](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/longform.js) minh họa chia lát theo tỷ lệ dữ liệu đã xác nhận; mẫu [2](https://prompt-motion.com/ultimaxbt-bbebf5) cho thấy tô lát đang được giải thích.

## Khi nào dùng

FS: Short minh họa cơ cấu nhóm hướng từ bộ số liệu có mẫu số. Dạng Short. Không nên dùng khi lát nhỏ khó so sánh.

## Cách dựng trong HyperFrames

Kỹ thuật pie_chart chưa có trong engine như một visual riêng. Tính cung SVG từ tổng số đã kiểm; lần lượt highlight sector qua GSAP timeline, không phát sinh dữ liệu lúc render. Mọi trạng thái của pie_chart là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Có thể mở rộng cấu trúc lát SVG quanh visual đang có ở `hyperframes_short/compositions/longform.js:2667`. Công vua.

## Rủi ro

lát nhỏ khó so sánh; tổng sai hoặc 3D làm méo cảm nhận.
