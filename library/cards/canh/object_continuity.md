---
{
  "id": "object_continuity",
  "ten": "Vật thể lặp xuyên cảnh",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "lien_tuc",
    "so_sanh"
  ],
  "cam_ngach": [],
  "so_muc": 15,
  "so_nguon": 3,
  "nguon": [
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/anabology/status/2103534482930491441",
    "https://prompt-motion.com/ultimaxbt-bbebf5"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 0
  },
  "cong": "cao",
  "dang_thu": [
    {
      "kenh": "mimck",
      "video": "STEVE JOBS 1984: Macintosh biết nói bằng hình (Long)",
      "ngay_dang": "2026-11-30",
      "do_sau": "2026-12-07",
      "ghi": "áp thử 26/10, chưa có số xem"
    }
  ]
}
---

## Mô tả

Cùng một vật giữ vị trí tương ứng qua các cảnh để nối bối cảnh và duy trì điểm neo. Mẫu [1](https://x.com/anabology/status/2103534482930491441) minh họa giữ hình gương khi chuyển từ ảnh sang sơ đồ; mẫu [2](https://prompt-motion.com/ultimaxbt-bbebf5) cho thấy đưa một vật qua hai góc nhìn.

## Khi nào dùng

FS: Long theo cùng vật thể khi giải thích vị trí. Dạng Ca_hai. Không nên dùng khi anchor lệch làm biến dạng.

## Cách dựng trong HyperFrames

Kỹ thuật object_continuity chưa có trong engine như một visual riêng. Đặt anchor tương ứng thủ công trên các ảnh; tween transform/mask giữa cảnh bằng timeline cố định. Mọi trạng thái của object_continuity là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

**MIMCK 27/10:** lời đọc phải nhắc tới vật nối ở mỗi chương, nếu không cảnh vật nối lạc nghĩa. Bài Steve Jobs 1984 dùng con chuột một nút ở 8/8 chương, xoay vòng 2 ảnh Commons và 1 ảnh AI; không cần sửa engine.

## Rủi ro

anchor lệch làm biến dạng; không rõ nguồn ảnh khiến tưởng cùng vật thật.
