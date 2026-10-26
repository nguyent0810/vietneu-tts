---
{
  "id": "wheel_spin",
  "ten": "Vòng xoay",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "fs"
  ],
  "hop_ngach": [
    "phan_loai",
    "do_hoa"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 15,
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
    "fs": 1,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Bánh xe sector quay quanh tâm rồi dừng ở nhãn được chọn trước; không cần bốc thăm thật. Mẫu [1](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/longform.js) minh họa xoay vòng nhóm hướng tới cung đang nói; mẫu [2](https://prompt-motion.com/ultimaxbt-bbebf5) cho thấy làm nổi sector sau khi dừng.

## Khi nào dùng

FS: Short chỉ dùng như ẩn dụ phân nhóm, không chọn kết quả bói. Dạng Short. Không nên dùng khi random giả như kết quả rút thật.

## Cách dựng trong HyperFrames

Kỹ thuật wheel_spin chưa có trong engine như một visual riêng. Khai báo sector và đích quay cố định; góc = easing(t) tới kết quả đã biết, không random. Mọi trạng thái của wheel_spin là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Phần hình học vòng có thể mở rộng từ visual `hyperframes_short/compositions/longform.js:2590`. Công vua.

## Rủi ro

random giả như kết quả rút thật; quay nhanh gây chóng mặt.
