---
{
  "id": "montage",
  "ten": "Montage nhiều cảnh",
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
  "so_muc": 107,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/hyperframes_oct/plan_o02.json",
    "output/cl_staging/hyperframes_oct/plan_o07.json",
    "output/cl_staging/hyperframes_sept/plan_d26.json",
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_bu_1006b.py"
  ],
  "vi_du": [
    "https://x.com/alexalbert__/status/2102466523164274839",
    "https://x.com/twoclipping/status/2102554209166000267"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/dossier.html",
    "hyperframes_short/compositions/dustbeam.html",
    "hyperframes_short/compositions/ember_long.html",
    "hyperframes_short/compositions/fs_v3.html",
    "hyperframes_short/compositions/hongchi.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Nhiều hình cắt nối thành chuỗi ngắn, mỗi khung bổ sung một mảnh bối cảnh; dossier và hongchi đổi ảnh theo phân đoạn.

## Khi nào dùng

Short chuỗi 3 cảnh làm bằng chứng/không khí; Long mở đầu chương hoặc tóm tắt. Không nên dùng: Một chi tiết cần giữ nguyên liên tục để người xem đọc.

## Cách dựng trong HyperFrames

Nhánh dựng cho montage nằm tại `hyperframes_short/compositions/dossier.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/hyperframes_oct/plan_o02.json:1`.

style `dossier`/`dustbeam`; đổi media theo nhịp cảnh, mỗi asset một khoảng thời gian.

## Rủi ro

Crop lệch giữa ảnh làm chủ thể nhảy; nhịp cắt không theo lời thành slideshow.
