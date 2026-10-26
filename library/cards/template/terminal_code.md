---
{
  "id": "terminal_code",
  "ten": "Terminal / cửa sổ mã",
  "loai": "template",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "ky_thuat",
    "code"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 110,
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
    "https://x.com/joaoli13/status/2102805376466891137",
    "https://x.com/kohya_tech/status/2102896431883497891"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 0
  },
  "cong": "thap"
}
---

## Mô tả

Cửa sổ terminal có prompt, lệnh và log hiện theo dòng, minh họa thao tác kỹ thuật. Mẫu [1](https://x.com/joaoli13/status/2102805376466891137) minh họa hiện lệnh kiểm tra metadata ảnh; mẫu [2](https://x.com/kohya_tech/status/2102896431883497891) cho thấy đưa log cố định vào cửa sổ terminal.

## Khi nào dùng

Không hợp FS/BUD; thử nghiệm giải thích cách kiểm tra file nguồn. Dạng Short. Không nên dùng khi log giả thành bằng chứng chạy thật.

## Cách dựng trong HyperFrames

Kỹ thuật terminal_code chưa có trong engine như một visual riêng. Dựng terminal bằng HTML/CSS và log tĩnh; hiện dòng theo mốc t, caret tính từ modulo thời gian. Mọi trạng thái của terminal_code là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

log giả thành bằng chứng chạy thật; font nhỏ/cú pháp sai khó kiểm.
