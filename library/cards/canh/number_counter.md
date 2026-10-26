---
{
  "id": "number_counter",
  "ten": "Số đếm tăng / count-up",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_lieu",
    "chi_so"
  ],
  "cam_ngach": [],
  "so_muc": 17,
  "so_nguon": 2,
  "nguon": [
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/studio/devices/number.js",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/studio/devices/table.js"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 0
  },
  "cong": "thap"
}
---

## Mô tả

Số trung tâm tăng tới giá trị đích theo easing; nhãn và đơn vị giữ con số trong ngữ cảnh. Mẫu [1](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/studio/devices/number.js) minh họa đếm tới số ngày trong khoảng có nguồn; mẫu [2](file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/studio/devices/table.js) cho thấy dừng ở tổng được xác nhận.

## Khi nào dùng

FS: Short hiện số ngày giữa hai mốc đã nêu. Dạng Short. Không nên dùng khi làm tròn thiếu đơn vị sai nghĩa.

## Cách dựng trong HyperFrames

Kỹ thuật number_counter chưa có trong engine như một visual riêng. Tính lerp(start,end,ease(t)) rồi format bằng đơn vị cố định; giữ số đầu/cuối và rounding tường minh. Mọi trạng thái của number_counter là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Phần nội suy số có thể lấy mẫu từ device `hyperframes_short/studio/devices/number.js:3`. Công thap.

## Rủi ro

làm tròn thiếu đơn vị sai nghĩa; count-up có thể giật gân hóa số nhỏ.
