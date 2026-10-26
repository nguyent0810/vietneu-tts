---
{
  "id": "social_post",
  "ten": "Bài đăng mạng xã hội",
  "loai": "template",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "trich_dan",
    "web"
  ],
  "cam_ngach": [],
  "so_muc": 15,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/redpersongpt/status/2103807094554284430",
    "https://x.com/anabology/status/2103534482930491441"
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
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Bài đăng hiển thị tài khoản, thời gian, nội dung và phản hồi như card feed để trích lời. Mẫu [1](https://x.com/redpersongpt/status/2103807094554284430) minh họa đặt phát ngôn công khai trong card có tên tài khoản; mẫu [2](https://x.com/anabology/status/2103534482930491441) cho thấy highlight câu gốc trong snapshot.

## Khi nào dùng

BUD: Short trích phát ngôn của tổ chức có link nguồn. Dạng Short. Không nên dùng khi dễ giả mạo/bỏ ngữ cảnh.

## Cách dựng trong HyperFrames

Kỹ thuật social_post chưa có trong engine như một visual riêng. Dựng HTML/CSS từ snapshot đã lưu, che dữ liệu thừa; highlight text node theo thời điểm t. Mọi trạng thái của social_post là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

dễ giả mạo/bỏ ngữ cảnh; avatar và ngày phải khớp nguồn.
