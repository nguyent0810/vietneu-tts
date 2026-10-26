---
{
  "id": "pie_wheel",
  "ten": "Vòng / bánh xe phân loại",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "fs"
  ],
  "hop_ngach": [
    "phan_loai",
    "phuong_huong"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 22,
  "so_nguon": 2,
  "nguon": [
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/fs_v3.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban.html"
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
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Bánh xe chia sector có nhãn quanh tâm; mỗi sector biểu diễn nhóm hoặc hướng. Mẫu [1](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/fs_v3.html) minh họa nhấn từng cung trong vòng hướng; mẫu [2](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban.html) cho thấy đánh dấu nhóm đang nói.

## Khi nào dùng

FS: Short phân loại bốn nhóm hướng trước phần chi tiết. Dạng Ca_hai. Không nên dùng khi vòng đều ngụ ý tỷ lệ bằng nhau.

## Cách dựng trong HyperFrames

Kỹ thuật pie_wheel chưa có trong engine như một visual riêng. Tạo sector SVG từ danh sách/góc cố định; active index đổi theo beat, không random. Mọi trạng thái của pie_wheel là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Vòng sector có thể tái dùng cấu trúc SVG quanh visual `hyperframes_short/compositions/longform.js:2590`. Công vua.

## Rủi ro

vòng đều ngụ ý tỷ lệ bằng nhau; chữ nhỏ quanh tâm khó đọc.
