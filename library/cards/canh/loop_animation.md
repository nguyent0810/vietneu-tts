---
{
  "id": "loop_animation",
  "ten": "Loop animation",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "nen",
    "lap_lai"
  ],
  "cam_ngach": [],
  "so_muc": 23,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/majidmanzarpour/status/2102476258948927543",
    "https://x.com/koldo2k/status/2103129343253778767"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
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

Một hành động ngắn khép lại đúng pose ban đầu và lặp với chu kỳ đều. Mẫu [1](https://x.com/majidmanzarpour/status/2102476258948927543) minh họa lặp một nhịp gợn nền; mẫu [2](https://x.com/koldo2k/status/2103129343253778767) cho thấy quay icon về pose đầu.

## Khi nào dùng

BUD: Short chỉ dùng vòng sáng rất nhẹ sau lời dẫn. Dạng Ca_hai. Không nên dùng khi điểm nối giật.

## Cách dựng trong HyperFrames

Kỹ thuật loop_animation chưa có trong engine như một visual riêng. Đặt một chu kỳ có pose đầu/cuối trùng; tính pha từ t modulo chu kỳ để mọi seek tái lập. Mọi trạng thái của loop_animation là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

điểm nối giật; chuyển động liền mạch gây phân tâm khi tụng niệm.
