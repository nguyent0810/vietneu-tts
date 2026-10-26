---
{
  "id": "browser_mockup",
  "ten": "Khung trình duyệt / website",
  "loai": "template",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "bang_chung",
    "web"
  ],
  "cam_ngach": [],
  "so_muc": 75,
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
    "https://x.com/deedydas/status/2102787937482252537",
    "https://x.com/thallisribeiro/status/2103107359727829318"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Khung trình duyệt có tab/thanh địa chỉ bao quanh snapshot trang web, tạo ngữ cảnh nguồn số. Mẫu [1](https://x.com/deedydas/status/2102787937482252537) minh họa đóng khung ảnh chụp trang nguồn trong trình duyệt; mẫu [2](https://x.com/thallisribeiro/status/2103107359727829318) cho thấy cuộn tới đoạn trích trên trang đã lưu.

## Khi nào dùng

BUD: Short dẫn tới bản dịch kinh có URL kiểm tra được. Dạng Short. Không nên dùng khi giao diện giả bị hiểu là trang thật.

## Cách dựng trong HyperFrames

Kỹ thuật browser_mockup chưa có trong engine như một visual riêng. Dựng chrome trình duyệt bằng HTML/CSS và chèn snapshot cục bộ; cuộn bằng transform tính từ t, không fetch web. Mọi trạng thái của browser_mockup là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

giao diện giả bị hiểu là trang thật; chữ screenshot nhỏ khó đọc.
