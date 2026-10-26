---
{
  "id": "explainer_general",
  "ten": "Dạng giải thích tổng quát",
  "loai": "kich_ban",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "huong_dan"
  ],
  "cam_ngach": [],
  "so_muc": 161,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/deedydas/status/2102787937482252537",
    "https://x.com/joaoli13/status/2102805376466891137"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Nội dung chia thành nhịp câu hỏi, cơ chế minh họa và hệ quả, mỗi nhịp dùng một hình chứng minh. Mẫu [1](https://x.com/deedydas/status/2102787937482252537) minh họa đặt câu hỏi rồi mở sơ đồ lời giải; mẫu [2](https://x.com/joaoli13/status/2102805376466891137) cho thấy chốt hệ quả sau ví dụ cụ thể.

## Khi nào dùng

FS: Short giải thích lỗi đặt gương, nguyên nhân và cách kiểm tra. Dạng Ca_hai. Không nên dùng khi cấu trúc dễ thành công thức.

## Cách dựng trong HyperFrames

Kỹ thuật explainer_general chưa có trong engine như một visual riêng. Chia lời thành beat có start/end tuyệt đối; mỗi beat dựng SVG/HTML riêng và lấy state từ timeline. Mọi trạng thái của explainer_general là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

cấu trúc dễ thành công thức; không trình bày quan niệm như nhân quả khoa học.
