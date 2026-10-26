---
{
  "id": "0013_retro_sau_moi_dot",
  "ten": "Viết retro sau mỗi đợt đăng; mỗi bài học thành một luật, lỗi lặp lại thành một đoạn code kiểm",
  "loai": "luat",
  "dinh_dang": [],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    "docs/adr/0013-retro-sau-moi-dot.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (19/10/2026, bổ sung 21/10). Ngày 19/10, chủ kênh yêu cầu tự nhìn lại sau mỗi đợt đăng. Ghi nhận chung chung không làm đổi hành vi, nên cần một khuôn bắt buộc. Ngày 21/10 ta mượn ý vòng tự cải thiện \"đề xuất – thử – ghép\" của Harness², nhưng không cài framework đó. Khuôn retro: - File `output/cl_staging/retro/<ngày>_<đợt>.md` có 2 phần: \"làm tốt\", và bảng \"Lỗi | Hậu quả | Đã đổi thành\". - Mỗi lỗi ghi một dòng vào `grok/improve/defects.jsonl`: khâu, ai bắt được, có lọt qua bước tự kiểm không, luật nào đã sửa. - Lỗi lặp lại từ 2 lần trở lên thì viết **check bằng code** trước, rồi mới thêm luật chữ. - Thứ Hai: đếm lỗi theo khâu, gộp hoặc bỏ luật thừa.",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0013-retro-sau-moi-dot.md:1`. Trạng thái: đã chấp nhận (19/10/2026, bổ sung 21/10). Ngày 19/10, chủ kênh yêu cầu tự nhìn lại sau mỗi đợt đăng. Ghi nhận chung chung không làm đổi hành vi, nên cần một khuôn bắt buộc. Ngày 21/10 ta mượn ý vòng tự cải thiện "đề xuất – thử – ghép" của Harness², nhưng không cài framework đó. Khuôn retro: - File `output/cl_staging/retro/<ngày>_<đợt>.md` có 2 phần: "làm tốt", và bảng "Lỗi | Hậu quả | Đã đổi thành". - Mỗi lỗi ghi một dòng vào `grok/improve/defects.jsonl`: khâu, ai.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
